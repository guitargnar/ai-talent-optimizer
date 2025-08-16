"""
Models package for AI Talent Optimizer.
"""

from .database import Job, Application, Response, Contact, EmailTemplate, DatabaseManager

__all__ = [
    'Job',
    'Application', 
    'Response',
    'Contact',
    'EmailTemplate',
    'DatabaseManager',
]