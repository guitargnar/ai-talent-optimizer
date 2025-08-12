"""
AI Talent Optimizer - Core Business Logic
Unified engine for job discovery, applications, and outreach
"""

from .job_discovery import JobDiscovery
from .application import ApplicationEngine
from .resume_engine import ResumeEngine
from .email_engine import EmailEngine

__all__ = [
    'JobDiscovery',
    'ApplicationEngine', 
    'ResumeEngine',
    'EmailEngine'
]

__version__ = '2.0.0'