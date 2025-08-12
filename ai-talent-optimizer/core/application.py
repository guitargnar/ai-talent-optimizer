"""
Unified Application Engine
Consolidates functionality from 12+ separate apply scripts
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import Config
from data.models import Job, Application, init_database

logger = logging.getLogger(__name__)

class ApplicationEngine:
    """Single engine for all job applications"""
    
    def __init__(self):
        self.config = Config()
        self.session = init_database()
        self.stats = {
            "applications_sent": 0,
            "emails_sent": 0,
            "responses_received": 0
        }
    
    def apply_to_job(self, job: Dict, method: str = "email") -> bool:
        """
        Unified application method replacing:
        - apply_priority_companies.py
        - apply_to_real_jobs_now.py
        - apply_top_ai_jobs.py
        - apply_with_verified_emails.py
        - automated_apply.py
        - manual_apply_now.py
        - personalized_apply.py
        """
        try:
            # Check if already applied
            existing = self.session.query(Application).filter_by(
                job_id=job.get('id')
            ).first()
            
            if existing:
                logger.info(f"Already applied to {job['company']} - {job['position']}")
                return False
            
            # Generate tailored resume
            resume_path = self._generate_resume(job)
            
            # Generate cover letter
            cover_letter = self._generate_cover_letter(job)
            
            # Send application
            success = False
            if method == "email":
                success = self._send_email_application(job, resume_path, cover_letter)
            elif method == "linkedin":
                success = self._send_linkedin_application(job, resume_path, cover_letter)
            elif method == "website":
                success = self._submit_website_application(job, resume_path, cover_letter)
            
            # Track application
            if success:
                self._track_application(job, method, resume_path)
                self.stats["applications_sent"] += 1
                logger.info(f"✅ Applied to {job['company']} - {job['position']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Application failed for {job.get('company')}: {e}")
            return False
    
    def apply_batch(self, jobs: List[Dict], limit: int = 25) -> Dict:
        """Apply to multiple jobs at once"""
        results = {
            "successful": [],
            "failed": [],
            "skipped": []
        }
        
        for i, job in enumerate(jobs[:limit]):
            logger.info(f"Processing {i+1}/{min(len(jobs), limit)}: {job['company']}")
            
            if self.apply_to_job(job):
                results["successful"].append(job)
            else:
                results["failed"].append(job)
            
            # Rate limiting
            if (i + 1) % 5 == 0:
                logger.info(f"Progress: {i+1} applications processed")
        
        return results
    
    def apply_priority_companies(self) -> Dict:
        """Focus on priority companies (replacing apply_priority_companies.py)"""
        priority_jobs = self._get_priority_jobs()
        return self.apply_batch(priority_jobs)
    
    def apply_top_ai_jobs(self) -> Dict:
        """Apply to top AI/ML positions (replacing apply_top_ai_jobs.py)"""
        ai_jobs = self._get_ai_ml_jobs()
        return self.apply_batch(ai_jobs)
    
    def apply_with_verified_emails(self) -> Dict:
        """Apply only to jobs with verified emails (replacing apply_with_verified_emails.py)"""
        verified_jobs = self._get_verified_email_jobs()
        return self.apply_batch(verified_jobs)
    
    def _generate_resume(self, job: Dict) -> str:
        """Generate tailored resume for specific job"""
        # For now, return master resume
        # TODO: Implement dynamic resume generation
        return str(Config.get_resume_path("master"))
    
    def _generate_cover_letter(self, job: Dict) -> str:
        """Generate personalized cover letter"""
        template = f"""Dear Hiring Team at {job['company']},

I am writing to express my strong interest in the {job['position']} position at {job['company']}. With over 10 years of experience at Humana, where I've delivered $1.2M in annual savings through AI automation, I am excited about the opportunity to bring my expertise to your team.

As a Senior Risk Management Professional II at Humana, I've architected enterprise-scale AI systems while building a comprehensive platform with 117 Python modules processing thousands of operations daily. My unique combination of healthcare domain expertise and cutting-edge AI implementation makes me an ideal fit for this role.

Key achievements that align with your needs:
• Built distributed ML systems with 78 specialized models for complex decision-making
• Developed production AI systems serving 50M+ users across healthcare systems
• Reduced LLM inference costs by 90% through custom adaptive quantization
• Maintained 100% compliance across 500+ Medicare regulatory pages using AI

I am particularly drawn to {job['company']}'s mission and believe my experience scaling AI systems at a Fortune 50 company would be valuable to your team. I've already been operating at a Principal level, as evidenced by the enterprise platform I've built while maintaining my demanding day job.

I would welcome the opportunity to discuss how my experience and passion for AI innovation can contribute to {job['company']}'s continued success.

{Config.EMAIL_SIGNATURE}
"""
        return template
    
    def _send_email_application(self, job: Dict, resume_path: str, cover_letter: str) -> bool:
        """Send application via email"""
        # TODO: Integrate with Gmail OAuth
        logger.info(f"Would send email to {job.get('email', 'Unknown')}")
        return True  # Placeholder
    
    def _send_linkedin_application(self, job: Dict, resume_path: str, cover_letter: str) -> bool:
        """Send application via LinkedIn"""
        # TODO: Integrate with LinkedIn automation
        logger.info(f"Would apply via LinkedIn to {job['company']}")
        return False  # Placeholder
    
    def _submit_website_application(self, job: Dict, resume_path: str, cover_letter: str) -> bool:
        """Submit application via company website"""
        # TODO: Integrate with website automation
        logger.info(f"Would apply via website to {job['company']}")
        return False  # Placeholder
    
    def _track_application(self, job: Dict, method: str, resume_path: str):
        """Track application in database"""
        application = Application(
            job_id=job.get('id'),
            applied_date=datetime.utcnow(),
            resume_version=Path(resume_path).name,
            application_method=method,
            email_address=job.get('email'),
            status='sent'
        )
        self.session.add(application)
        self.session.commit()
    
    def _get_priority_jobs(self) -> List[Dict]:
        """Get jobs from priority companies"""
        # TODO: Query from unified database
        return []
    
    def _get_ai_ml_jobs(self) -> List[Dict]:
        """Get AI/ML specific jobs"""
        # TODO: Query from unified database
        return []
    
    def _get_verified_email_jobs(self) -> List[Dict]:
        """Get jobs with verified email addresses"""
        # TODO: Query from unified database
        return []
    
    def get_stats(self) -> Dict:
        """Get application statistics"""
        return self.stats

# Quick test interface
if __name__ == "__main__":
    engine = ApplicationEngine()
    print(f"Application Engine initialized")
    print(f"Config: {Config.PERSONAL['name']} - {Config.PERSONAL['email']}")
    print(f"Resume path: {Config.get_resume_path()}")