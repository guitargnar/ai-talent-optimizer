"""
Core application service for managing job applications.
Handles the complete application lifecycle.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import time

from ..models.database import DatabaseManager, Job, Application, Response
from ..config.settings import settings
from .email_service import EmailService
from .resume import ResumeService
from .content import ContentGenerator

logger = logging.getLogger(__name__)


class ApplicationService:
    """Main service for managing job applications."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize application service."""
        self.db = db_manager or DatabaseManager()
        self.email_service = EmailService()
        self.resume_service = ResumeService()
        self.content_generator = ContentGenerator()
        
        # Track daily limits
        self.daily_applications = 0
        self.last_reset = datetime.now().date()
    
    def apply_to_job(self, job_id: int, method: str = "auto") -> Tuple[bool, str]:
        """
        Apply to a job with specified method.
        
        Args:
            job_id: Database ID of the job
            method: Application method (auto, email, web_form)
            
        Returns:
            Tuple of (success, message)
        """
        session = self.db.get_session()
        
        try:
            # Check daily limit
            if not self._check_daily_limit():
                return False, f"Daily limit reached ({settings.application.max_applications_per_day})"
            
            # Get job details
            job = session.query(Job).filter_by(id=job_id).first()
            if not job:
                return False, f"Job {job_id} not found"
            
            if job.applied:
                return False, f"Already applied to {job.company} - {job.position}"
            
            # Determine application method
            if method == "auto":
                method = self._determine_best_method(job)
            
            # Apply based on method
            if method == "email":
                success, message = self._apply_via_email(job, session)
            elif method == "web_form":
                success, message = self._apply_via_web_form(job, session)
            else:
                return False, f"Unknown application method: {method}"
            
            if success:
                # Update job status
                job.applied = True
                job.applied_date = datetime.now()
                job.application_method = method
                job.status = 'applied'
                
                # Create application record
                application = Application(
                    job_id=job.id,
                    sent_date=datetime.now(),
                    resume_version=self.resume_service.get_current_version(),
                    email_sent=(method == "email"),
                    delivery_status="sent"
                )
                session.add(application)
                
                # Commit changes
                session.commit()
                
                # Update daily counter
                self.daily_applications += 1
                
                logger.info(f"Applied to {job.company} - {job.position} via {method}")
                return True, f"Successfully applied to {job.company}"
            else:
                return False, message
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error applying to job {job_id}: {e}")
            return False, f"Error: {str(e)}"
        finally:
            session.close()
    
    def _apply_via_email(self, job: Job, session) -> Tuple[bool, str]:
        """Apply to job via email."""
        logger.info(f"Attempting to apply to {job.company} via email: {job.company_email}")
        
        # Check email configuration
        if not settings.email.is_configured:
            logger.error("Email not configured in settings")
            return False, "Email not configured"
        
        # Verify email address
        if not job.company_email:
            logger.warning(f"No company email available for {job.company}")
            return False, "No company email available"
        
        # Skip job board emails
        if 'adzuna.com' in job.company_email or 'indeed.com' in job.company_email:
            logger.warning(f"Skipping job board email: {job.company_email}")
            return False, "Job board email - need real company email"
        
        if job.bounce_detected:
            logger.warning(f"Email {job.company_email} has bounced previously")
            return False, f"Email {job.company_email} has bounced previously"
        
        # Generate application content
        cover_letter = self.content_generator.generate_cover_letter(job)
        resume_path = self.resume_service.get_resume_for_job(job)
        
        # Send email
        subject = f"Application for {job.position} at {job.company}"
        success = self.email_service.send_application(
            to_email=job.company_email,
            subject=subject,
            body=cover_letter,
            resume_path=resume_path
        )
        
        if success:
            return True, "Email sent successfully"
        else:
            return False, "Failed to send email"
    
    def _apply_via_web_form(self, job: Job, session) -> Tuple[bool, str]:
        """Apply to job via web form."""
        # For now, just mark as needing manual application
        job.notes = "Manual application required via web form"
        return False, f"Please apply manually at: {job.url}"
    
    def _determine_best_method(self, job: Job) -> str:
        """Determine the best application method for a job."""
        # If we have a verified email and no bounces, use email
        if job.company_email and job.email_verified and not job.bounce_detected:
            return "email"
        
        # If we have a URL, suggest web form
        if job.url:
            return "web_form"
        
        # Default to email if we have any email
        if job.company_email:
            return "email"
        
        return "web_form"
    
    def _check_daily_limit(self) -> bool:
        """Check if daily application limit has been reached."""
        # Reset counter if new day
        today = datetime.now().date()
        if today > self.last_reset:
            self.daily_applications = 0
            self.last_reset = today
        
        return self.daily_applications < settings.application.max_applications_per_day
    
    def batch_apply(self, count: int = 10, min_score: float = None) -> Dict[str, int]:
        """
        Apply to multiple jobs in batch.
        
        Args:
            count: Number of jobs to apply to
            min_score: Minimum relevance score (default from settings)
            
        Returns:
            Dictionary with results
        """
        min_score = min_score or settings.application.min_relevance_score
        session = self.db.get_session()
        
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        try:
            # Get eligible jobs
            jobs = session.query(Job).filter(
                Job.applied == False,
                Job.relevance_score >= min_score,
                Job.bounce_detected == False
            ).order_by(Job.relevance_score.desc()).limit(count).all()
            
            logger.info(f"Found {len(jobs)} eligible jobs to apply to")
            logger.info(f"Min score filter: {min_score}")
            
            # Log details about each job
            for idx, job in enumerate(jobs, 1):
                logger.info(f"Job {idx}: {job.company} - {job.position}")
                logger.info(f"  Score: {job.relevance_score}, Email: {job.company_email}")
            
            for job in jobs:
                logger.info(f"\nProcessing: {job.company} - {job.position}")
                logger.info(f"  Email: {job.company_email}")
                logger.info(f"  Score: {job.relevance_score}")
                
                # Check daily limit
                if not self._check_daily_limit():
                    logger.info("Daily limit reached, stopping batch")
                    break
                
                # Apply to job
                success, message = self.apply_to_job(job.id)
                
                if success:
                    results['success'] += 1
                    logger.info(f"✅ Successfully applied to {job.company}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{job.company}: {message}")
                    logger.warning(f"❌ Failed to apply to {job.company}: {message}")
                
                # Rate limiting
                time.sleep(settings.email.delay_seconds)
            
            logger.info(f"\nBatch complete: {results['success']} sent, {results['failed']} failed")
            return results
            
        finally:
            session.close()
    
    def send_follow_up(self, job_id: int) -> Tuple[bool, str]:
        """
        Send follow-up email for a job application.
        
        Args:
            job_id: Database ID of the job
            
        Returns:
            Tuple of (success, message)
        """
        session = self.db.get_session()
        
        try:
            job = session.query(Job).filter_by(id=job_id).first()
            if not job:
                return False, f"Job {job_id} not found"
            
            if not job.applied:
                return False, "Haven't applied to this job yet"
            
            # Get application record
            application = session.query(Application).filter_by(job_id=job_id).first()
            if not application:
                return False, "Application record not found"
            
            # Check if enough time has passed
            days_since = (datetime.now() - application.sent_date).days
            if days_since < 7:
                return False, f"Too soon for follow-up ({days_since} days)"
            
            # Generate follow-up content
            follow_up = self.content_generator.generate_follow_up(job, days_since)
            
            # Send follow-up
            subject = f"Re: Application for {job.position} at {job.company}"
            success = self.email_service.send_email(
                to_email=job.company_email,
                subject=subject,
                body=follow_up
            )
            
            if success:
                # Update tracking
                application.follow_up_count += 1
                application.last_follow_up = datetime.now()
                application.next_follow_up = datetime.now() + timedelta(days=7)
                session.commit()
                
                return True, "Follow-up sent successfully"
            else:
                return False, "Failed to send follow-up"
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error sending follow-up for job {job_id}: {e}")
            return False, f"Error: {str(e)}"
        finally:
            session.close()
    
    def get_application_stats(self) -> Dict:
        """Get application statistics."""
        session = self.db.get_session()
        
        try:
            total_jobs = session.query(Job).count()
            applied = session.query(Job).filter_by(applied=True).count()
            responses = session.query(Response).count()
            interviews = session.query(Response).filter_by(
                response_type='interview_request'
            ).count()
            
            # Calculate rates
            response_rate = (responses / applied * 100) if applied > 0 else 0
            interview_rate = (interviews / applied * 100) if applied > 0 else 0
            
            return {
                'total_jobs': total_jobs,
                'applications_sent': applied,
                'responses_received': responses,
                'interviews_scheduled': interviews,
                'response_rate': round(response_rate, 1),
                'interview_rate': round(interview_rate, 1),
                'daily_limit': settings.application.max_applications_per_day,
                'daily_sent': self.daily_applications
            }
            
        finally:
            session.close()