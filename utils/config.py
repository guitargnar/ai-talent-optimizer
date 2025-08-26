"""
Centralized Configuration Management
Single source of truth for all settings
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Unified configuration manager"""
    
    # Core Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "output"
    RESUMES_DIR = BASE_DIR / "resumes"
    TEMPLATES_DIR = BASE_DIR / "templates"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Database
    DATABASE_PATH = BASE_DIR / "unified_platform.db"
    
    # Gmail OAuth (link to existing)
    GMAIL_CREDS_DIR = Path.home() / ".gmail_job_tracker"
    GMAIL_CREDENTIALS = GMAIL_CREDS_DIR / "credentials.json"
    GMAIL_TOKEN = GMAIL_CREDS_DIR / "token.json"
    
    # Personal Information (VERIFIED)
    PERSONAL = {
        "name": "Matthew Scott",
        "email": "matthewdscott7@gmail.com",
        "phone": "502-345-0525",  # Fixed phone number
        "linkedin": "linkedin.com/in/mscott77",
        "github": "github.com/guitargnar",
        "instagram": "@guitargnar",
        "location": "Louisville, KY",
        "current_title": "Senior Risk Management Professional II",
        "current_company": "Humana Inc.",
        "years_at_humana": 10,
        "total_experience": 10
    }
    
    # Application Settings
    DAILY_APPLICATION_TARGET = 25
    MIN_SALARY = 400000
    PREFERRED_LOCATIONS = ["Remote", "Louisville, KY", "San Francisco, CA", "New York, NY"]
    
    # Priority Companies (AI/ML Focus)
    PRIORITY_COMPANIES = [
        "Anthropic", "OpenAI", "Google DeepMind", "Meta AI", 
        "Microsoft", "Apple", "Amazon", "NVIDIA", "Tesla",
        "Scale AI", "Cohere", "Stability AI", "Hugging Face",
        "Databricks", "Snowflake", "Palantir", "DataRobot"
    ]
    
    # Job Title Keywords
    TARGET_TITLES = [
        "Principal Engineer", "Staff Engineer", "Principal AI Engineer",
        "Staff ML Engineer", "AI Architect", "ML Architect",
        "Director of AI", "VP Engineering", "Distinguished Engineer",
        "Senior Staff Engineer", "Principal Applied Scientist"
    ]
    
    # Email Templates
    EMAIL_SIGNATURE = """
Best regards,

Matthew Scott
Senior AI/ML Engineer | Production Systems Architect
📧 matthewdscott7@gmail.com | 📱 502-345-0525
🔗 linkedin.com/in/mscott77 | 💻 github.com/guitargnar
📍 Louisville, KY | Open to Remote
"""
    
    # API Keys (from environment)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(full_name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def load_env(cls):
        """Load environment variables from .env file"""
        env_file = cls.BASE_DIR / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    @classmethod
    def get_resume_path(cls, version="master"):
        """Get path to specific resume version"""
        if version == "master":
            return cls.RESUMES_DIR / "matthew_scott_ai_ml_resume.pdf"
        return cls.RESUMES_DIR / f"{version}.pdf"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for dir_path in [cls.DATA_DIR, cls.OUTPUT_DIR, cls.RESUMES_DIR, 
                         cls.TEMPLATES_DIR, cls.LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            "personal": cls.PERSONAL,
            "paths": {
                "base": str(cls.BASE_DIR),
                "database": str(cls.DATABASE_PATH),
                "resumes": str(cls.RESUMES_DIR)
            },
            "settings": {
                "daily_target": cls.DAILY_APPLICATION_TARGET,
                "min_salary": cls.MIN_SALARY,
                "locations": cls.PREFERRED_LOCATIONS
            }
        }

# Initialize on import
Config.load_env()
Config.ensure_directories()