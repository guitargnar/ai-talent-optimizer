#!/usr/bin/env python3
"""
Enterprise Security Wrapper for Ollama Models
Addresses CVE vulnerabilities and adds enterprise-grade security
Author: Matthew Scott
"""

import os
import json
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from functools import wraps
import asyncio
import aiohttp
from flask import Flask, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import jwt
import redis
from cryptography.fernet import Fernet
import requests
from prometheus_client import Counter, Histogram, generate_latest
import re
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Security Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24
OLLAMA_BASE_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///audit_log.db')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app, origins=os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(','))

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=REDIS_URL,
    default_limits=["1000 per hour", "100 per minute"]
)

# Initialize Redis for caching
redis_client = redis.from_url(REDIS_URL)

# Initialize encryption
cipher_suite = Fernet(ENCRYPTION_KEY)

# Initialize database for audit logging
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(full_name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('secure_ollama.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Prometheus metrics
request_count = Counter('ollama_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('ollama_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
model_usage = Counter('ollama_model_usage', 'Model usage count', ['model'])
security_events = Counter('security_events_total', 'Security events', ['event_type'])

# Database Models
class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100))
    client_ip = Column(String(45))
    model = Column(String(100))
    prompt_hash = Column(String(64))
    response_hash = Column(String(64))
    tokens_used = Column(Integer)
    duration_ms = Column(Integer)
    status = Column(String(20))
    error_message = Column(Text, nullable=True)

Base.metadata.create_all(engine)

# Security Decorators
@dataclass
class SecurityContext:
    user_id: str
    client_ip: str
    roles: List[str]
    rate_limit: int
    models_allowed: List[str]

def require_auth(f):
    """Require valid JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            security_events.labels(event_type='invalid_auth').inc()
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.replace('Bearer ', '')
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            g.security_context = SecurityContext(
                user_id=payload['user_id'],
                client_ip=get_remote_address(),
                roles=payload.get('roles', ['user']),
                rate_limit=payload.get('rate_limit', 100),
                models_allowed=payload.get('models_allowed', [])
            )
        except jwt.ExpiredSignatureError:
            security_events.labels(event_type='expired_token').inc()
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError as e:
            security_events.labels(event_type='invalid_token').inc()
            logger.warning(f"Invalid token from {get_remote_address()}: {e}")
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def validate_input(f):
    """Validate and sanitize input"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate prompt
        prompt = data.get('prompt', '')
        if not prompt or len(prompt) > 10000:
            return jsonify({'error': 'Invalid prompt length'}), 400
        
        # Check for injection attempts
        injection_patterns = [
            r'<script',
            r'javascript:',
            r'on\w+\s*=',
            r'__proto__',
            r'constructor\s*\(',
            r'eval\s*\(',
            r'Function\s*\('
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                security_events.labels(event_type='injection_attempt').inc()
                logger.warning(f"Injection attempt from {g.security_context.client_ip}: {pattern}")
                return jsonify({'error': 'Invalid content detected'}), 400
        
        # Validate model name
        model = data.get('model', '')
        if not re.match(r'^[a-zA-Z0-9_\-\.:]+$', model):
            return jsonify({'error': 'Invalid model name'}), 400
        
        # Check model authorization
        if g.security_context.models_allowed and model not in g.security_context.models_allowed:
            security_events.labels(event_type='unauthorized_model').inc()
            return jsonify({'error': f'Access denied to model: {model}'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Utility Functions
def hash_content(content: str) -> str:
    """Generate SHA256 hash of content"""
    return hashlib.sha256(content.encode()).hexdigest()

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data"""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

async def call_ollama_model(model: str, prompt: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Securely call Ollama model with timeout and error handling"""
    start_time = datetime.utcnow()
    
    # Default options for security
    default_options = {
        'temperature': 0.7,
        'max_tokens': 2000,
        'timeout': 30,
        'stop': ['<script', 'javascript:', '__proto__']
    }
    
    if options:
        default_options.update(options)
    
    # Prepare request
    payload = {
        'model': model,
        'prompt': prompt,
        'stream': False,
        'options': default_options
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=default_options['timeout'])
            ) as response:
                if response.status != 200:
                    raise Exception(f"Ollama returned status {response.status}")
                
                result = await response.json()
                
                # Calculate metrics
                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                # Log successful call
                audit_log = AuditLog(
                    user_id=g.security_context.user_id,
                    client_ip=g.security_context.client_ip,
                    model=model,
                    prompt_hash=hash_content(prompt),
                    response_hash=hash_content(result.get('response', '')),
                    tokens_used=result.get('total_tokens', 0),
                    duration_ms=duration_ms,
                    status='success'
                )
                
                session = Session()
                session.add(audit_log)
                session.commit()
                session.close()
                
                # Update metrics
                model_usage.labels(model=model).inc()
                
                return {
                    'success': True,
                    'response': result.get('response', ''),
                    'model': model,
                    'tokens_used': result.get('total_tokens', 0),
                    'duration_ms': duration_ms
                }
                
    except asyncio.TimeoutError:
        security_events.labels(event_type='timeout').inc()
        logger.error(f"Timeout calling model {model}")
        return {'success': False, 'error': 'Request timeout'}
    except Exception as e:
        security_events.labels(event_type='model_error').inc()
        logger.error(f"Error calling model {model}: {e}")
        return {'success': False, 'error': 'Model error occurred'}

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/auth/token', methods=['POST'])
@limiter.limit("5 per minute")
def generate_token():
    """Generate JWT token for authenticated users"""
    data = request.get_json()
    
    # In production, validate against user database
    api_key = data.get('api_key', '')
    client_id = data.get('client_id', '')
    
    # Simplified validation (implement proper authentication)
    if not api_key or not client_id:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate token
    payload = {
        'user_id': client_id,
        'roles': ['user'],
        'rate_limit': 100,
        'models_allowed': [],  # Empty = all models
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return jsonify({
        'token': token,
        'expires_in': JWT_EXPIRATION_HOURS * 3600
    })

@app.route('/api/generate', methods=['POST'])
@require_auth
@validate_input
@limiter.limit("100 per hour")
async def generate():
    """Secure endpoint for model generation"""
    data = request.get_json()
    model = data.get('model')
    prompt = data.get('prompt')
    options = data.get('options', {})
    
    # Check cache
    cache_key = f"ollama:{model}:{hash_content(prompt)}"
    cached_response = redis_client.get(cache_key)
    
    if cached_response:
        logger.info(f"Cache hit for model {model}")
        return jsonify(json.loads(cached_response))
    
    # Call model
    result = await call_ollama_model(model, prompt, options)
    
    if result['success']:
        # Cache successful responses for 1 hour
        redis_client.setex(cache_key, 3600, json.dumps(result))
        request_count.labels(method='POST', endpoint='/api/generate', status='success').inc()
    else:
        request_count.labels(method='POST', endpoint='/api/generate', status='error').inc()
    
    return jsonify(result)

@app.route('/api/models', methods=['GET'])
@require_auth
def list_models():
    """List available models"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        models = response.json().get('models', [])
        
        # Filter based on user permissions
        if g.security_context.models_allowed:
            models = [m for m in models if m['name'] in g.security_context.models_allowed]
        
        return jsonify({'models': models})
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return jsonify({'error': 'Failed to list models'}), 500

@app.route('/api/audit', methods=['GET'])
@require_auth
def get_audit_logs():
    """Get audit logs (admin only)"""
    if 'admin' not in g.security_context.roles:
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get query parameters
    limit = min(int(request.args.get('limit', 100)), 1000)
    offset = int(request.args.get('offset', 0))
    
    session = Session()
    logs = session.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).limit(limit).offset(offset).all()
    
    result = [{
        'timestamp': log.timestamp.isoformat(),
        'user_id': log.user_id,
        'model': log.model,
        'tokens_used': log.tokens_used,
        'duration_ms': log.duration_ms,
        'status': log.status
    } for log in logs]
    
    session.close()
    
    return jsonify({'logs': result})

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Error Handlers
@app.errorhandler(429)
def rate_limit_exceeded(e):
    security_events.labels(event_type='rate_limit').inc()
    return jsonify({'error': 'Rate limit exceeded'}), 429

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

# Main execution
if __name__ == '__main__':
    logger.info("Starting Secure Ollama Wrapper")
    logger.info(f"Ollama backend: {OLLAMA_BASE_URL}")
    logger.info(f"Database: {DATABASE_URL}")
    logger.info(f"Redis: {REDIS_URL}")
    
    # Run with production WSGI server in production
    # gunicorn -w 4 -k uvicorn.workers.UvicornWorker secure_ollama_wrapper:app
    app.run(host='0.0.0.0', port=5000, debug=False)