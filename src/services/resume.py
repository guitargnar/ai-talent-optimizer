"""
Resume service for managing and selecting appropriate resumes.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict
import hashlib

from ..config.settings import settings

logger = logging.getLogger(__name__)


class ResumeService:
    """Service for managing resume versions and selection."""
    
    def __init__(self):
        """Initialize resume service."""
        self.resumes_dir = settings.resumes_dir
        self.default_resume = settings.application.resume_path
        
        # Cache available resumes
        self._scan_resumes()
    
    def _scan_resumes(self):
        """Scan for available resume files."""
        self.available_resumes = {}
        
        if self.resumes_dir.exists():
            for resume_file in self.resumes_dir.glob("*.pdf"):
                # Categorize by filename patterns
                name = resume_file.stem.lower()
                
                if 'executive' in name or 'leadership' in name:
                    category = 'executive'
                elif 'technical' in name or 'engineer' in name:
                    category = 'technical'
                elif 'ml' in name or 'ai' in name or 'machine' in name:
                    category = 'ai_ml'
                elif 'master' in name or 'general' in name:
                    category = 'general'
                else:
                    category = 'other'
                
                self.available_resumes[category] = str(resume_file)
        
        logger.info(f"Found {len(self.available_resumes)} resume categories")
    
    def get_resume_for_job(self, job) -> str:
        """
        Select the most appropriate resume for a job.
        
        Args:
            job: Job object with position and description
            
        Returns:
            Path to selected resume file
        """
        # PRIORITY: Always use 2025 resume if available
        # This is the most up-to-date resume with Mirador project
        for resume_path in self.resumes_dir.glob("*2025*.pdf"):
            logger.info(f"Using 2025 resume: {resume_path.name}")
            return str(resume_path)
        
        # Fallback to category-based selection only if 2025 resume not found
        position_lower = job.position.lower() if job.position else ""
        description_lower = job.description.lower() if job.description else ""
        
        # Check for executive roles
        if any(term in position_lower for term in ['director', 'vp', 'chief', 'head of', 'principal']):
            if 'executive' in self.available_resumes:
                return self.available_resumes['executive']
        
        # Check for AI/ML roles
        if any(term in position_lower + description_lower for term in 
               ['machine learning', 'ml engineer', 'ai', 'artificial intelligence', 'deep learning']):
            if 'ai_ml' in self.available_resumes:
                return self.available_resumes['ai_ml']
        
        # Check for technical roles
        if any(term in position_lower for term in ['engineer', 'developer', 'architect']):
            if 'technical' in self.available_resumes:
                return self.available_resumes['technical']
        
        # Default to general or master resume
        if 'general' in self.available_resumes:
            return self.available_resumes['general']
        
        # Fall back to default
        return self.default_resume
    
    def get_current_version(self) -> str:
        """
        Get version identifier for current resume.
        
        Returns:
            Version string (hash of file content)
        """
        try:
            if Path(self.default_resume).exists():
                with open(self.default_resume, 'rb') as f:
                    content = f.read()
                    return hashlib.md5(content).hexdigest()[:8]
            return "unknown"
        except Exception as e:
            logger.error(f"Error getting resume version: {e}")
            return "error"
    
    def list_resumes(self) -> List[Dict[str, str]]:
        """
        List all available resumes.
        
        Returns:
            List of resume information dictionaries
        """
        resumes = []
        
        for category, path in self.available_resumes.items():
            file_path = Path(path)
            if file_path.exists():
                resumes.append({
                    'category': category,
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size': f"{file_path.stat().st_size / 1024:.1f} KB"
                })
        
        return resumes
    
    def validate_resume(self, resume_path: str) -> bool:
        """
        Validate that a resume file exists and is readable.
        
        Args:
            resume_path: Path to resume file
            
        Returns:
            True if valid
        """
        try:
            path = Path(resume_path)
            return path.exists() and path.suffix == '.pdf' and path.stat().st_size > 0
        except Exception:
            return False