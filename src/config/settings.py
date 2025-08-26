"""
Centralized configuration management for AI Talent Optimizer.
All settings are loaded from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    path: str = os.getenv('DATABASE_PATH', './data/unified_jobs.db')
    backup_path: str = os.getenv('BACKUP_PATH', './backups')
    pool_size: int = int(os.getenv('DB_POOL_SIZE', '5'))
    echo: bool = os.getenv('DB_ECHO', 'False').lower() == 'true'


@dataclass
class EmailConfig:
    """Email configuration settings."""
    address: str = os.getenv('EMAIL_ADDRESS', '')
    app_password: str = os.getenv('EMAIL_APP_PASSWORD', '')
    smtp_server: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port: int = int(os.getenv('SMTP_PORT', '587'))
    delay_seconds: int = int(os.getenv('EMAIL_DELAY_SECONDS', '5'))
    max_per_day: int = int(os.getenv('MAX_EMAILS_PER_DAY', '50'))
    
    @property
    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return bool(self.address and self.app_password)


@dataclass
class APIConfig:
    """External API configuration."""
    adzuna_app_id: str = os.getenv('ADZUNA_APP_ID', '')
    adzuna_app_key: str = os.getenv('ADZUNA_APP_KEY', '')
    openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
    github_token: Optional[str] = os.getenv('GITHUB_TOKEN')
    linkedin_cookie: Optional[str] = os.getenv('LINKEDIN_COOKIE')


@dataclass
class ApplicationConfig:
    """Application behavior configuration."""
    debug_mode: bool = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    max_applications_per_day: int = int(os.getenv('MAX_APPLICATIONS_PER_DAY', '20'))
    auto_apply: bool = os.getenv('AUTO_APPLY', 'False').lower() == 'true'
    min_relevance_score: float = float(os.getenv('MIN_RELEVANCE_SCORE', '0.65'))
    resume_path: str = os.getenv('RESUME_PATH', './resumes/matthew_scott_professional_resume.pdf')
    
    # Retry configuration
    max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
    retry_delay: int = int(os.getenv('RETRY_DELAY', '60'))
    
    # Rate limiting
    rate_limit_per_minute: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '10'))


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = os.getenv('LOG_LEVEL', 'INFO')
    file_path: str = os.getenv('LOG_FILE', './logs/application.log')
    format: str = os.getenv('LOG_FORMAT', 
                            '%(asctime)s - %(full_name)s - %(levelname)s - %(message)s')
    max_bytes: int = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))


class Settings:
    """Main settings class combining all configuration."""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.email = EmailConfig()
        self.api = APIConfig()
        self.application = ApplicationConfig()
        self.logging = LoggingConfig()
        
        # Paths
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / 'data'
        self.logs_dir = self.project_root / 'logs'
        self.output_dir = self.project_root / 'output'
        self.resumes_dir = self.project_root / 'resumes'
        
        # Create directories if they don't exist
        for directory in [self.data_dir, self.logs_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.email.is_configured:
            errors.append("Email configuration missing (EMAIL_ADDRESS, EMAIL_APP_PASSWORD)")
        
        if not self.api.adzuna_app_id or not self.api.adzuna_app_key:
            errors.append("Adzuna API credentials missing")
        
        if not Path(self.application.resume_version).exists():
            errors.append(f"Resume file not found: {self.application.resume_path}")
        
        return errors
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary for logging/debugging."""
        return {
            'database': {
                'path': self.database.path,
                'backup_path': self.database.backup_path
            },
            'email': {
                'configured': self.email.is_configured,
                'address': self.email.address if self.email.address else 'NOT SET'
            },
            'application': {
                'debug_mode': self.application.debug_mode,
                'max_per_day': self.application.max_applications_per_day,
                'min_score': self.application.min_relevance_score
            }
        }


# Global settings instance
settings = Settings()