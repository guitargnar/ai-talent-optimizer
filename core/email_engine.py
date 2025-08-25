"""
Email Engine
Consolidated email handling with Gmail token support
"""

from typing import List, Dict, Tuple
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class EmailEngine:
    """Unified email operations with Gmail token support"""
    
    def __init__(self):
        self.gmail_configured = False
        self.token_file = Path.home() / ".gmail_job_tracker" / "token.json"
        self.smtp_available = self._check_smtp_config()
        self.gmail_api_available = self._check_gmail_token()
        
        # Initialize the best available method
        self._initialize_email_method()
    
    def _check_smtp_config(self) -> bool:
        """Check if SMTP configuration is available"""
        email = os.getenv('EMAIL_ADDRESS')
        password = os.getenv('EMAIL_APP_PASSWORD')
        return bool(email and password)
    
    def _check_gmail_token(self) -> bool:
        """Check if Gmail token.json exists and is valid"""
        if not self.token_file.exists():
            logger.info("Gmail token.json not found")
            return False
        
        try:
            import json
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            
            # Check for required fields
            required_fields = ['token', 'client_id']
            if any(field in str(token_data) for field in required_fields):
                logger.info("Gmail token.json found")
                return True
            
        except Exception as e:
            logger.warning(f"Invalid Gmail token.json: {e}")
        
        return False
    
    def _initialize_email_method(self):
        """Initialize the best available email method"""
        if self.gmail_api_available:
            try:
                from unified_email_engine import UnifiedEmailEngine
                self.engine = UnifiedEmailEngine(prefer_gmail_api=True)
                self.gmail_configured = True
                logger.info("Gmail API method initialized")
                return
            except Exception as e:
                logger.warning(f"Gmail API initialization failed: {e}")
        
        if self.smtp_available:
            try:
                from unified_email_engine import UnifiedEmailEngine
                self.engine = UnifiedEmailEngine(prefer_gmail_api=False)
                self.gmail_configured = True
                logger.info("SMTP method initialized")
                return
            except Exception as e:
                logger.error(f"SMTP initialization failed: {e}")
        
        logger.error("No email method available")
        self.engine = None
    
    def send_application(self, to: str, subject: str, body: str, attachments: List[str] = None) -> bool:
        """Send job application email"""
        if not self.engine:
            logger.error("No email engine available")
            return False
        
        try:
            success, result = self.engine.send_email(
                to_email=to,
                subject=subject,
                body=body,
                attachments=attachments or [],
                email_type='application'
            )
            
            if success:
                logger.info(f"Email sent to {to} with result: {result}")
            else:
                logger.error(f"Email send failed: {result}")
            
            return success
            
        except Exception as e:
            logger.error(f"Email send exception: {e}")
            return False
    
    def check_responses(self) -> List[Dict]:
        """Check for new responses"""
        # TODO: Implement response checking via Gmail API
        if self.gmail_api_available:
            logger.info("Checking responses via Gmail API (not yet implemented)")
        
        return []
    
    def get_status(self) -> Dict:
        """Get email engine status"""
        return {
            'gmail_configured': self.gmail_configured,
            'smtp_available': self.smtp_available,
            'gmail_api_available': self.gmail_api_available,
            'token_exists': self.token_file.exists(),
            'engine_available': self.engine is not None
        }