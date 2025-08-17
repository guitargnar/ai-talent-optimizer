#!/usr/bin/env python3
"""
Guided Application System
Interactive application process with approval for each job
Ensures compliance through human oversight and control
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import logging
from typing import Optional, Dict, List

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.application import ApplicationService
from src.services.email_service import EmailService
from src.services.content import ContentGenerator
from src.services.resume import ResumeService
from src.models.database import DatabaseManager, Job
from src.config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class GuidedApplicationWorkflow:
    """Interactive application workflow with approvals"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.app_service = ApplicationService(self.db)
        self.email_service = EmailService()
        self.content_gen = ContentGenerator()
        self.resume_service = ResumeService()
        
        # Track session stats
        self.session_stats = {
            'reviewed': 0,
            'approved': 0,
            'skipped': 0,
            'edited': 0,
            'sent': 0,
            'failed': 0
        }
        
        # Safety limits
        self.MAX_PER_SESSION = 10
        self.MIN_DELAY_SECONDS = 30
        
    def get_next_job(self) -> Optional[Job]:
        """Get next high-priority job to apply to"""
        session = self.db.get_session()
        
        try:
            job = session.query(Job).filter(
                Job.applied == False,
                Job.relevance_score >= 0.65,
                Job.company_email != None,
                Job.company_email != 'N/A',
                ~Job.company_email.contains('adzuna'),
                ~Job.company_email.contains('indeed'),
                Job.source.in_(['Greenhouse', 'Lever'])
            ).order_by(
                Job.relevance_score.desc()
            ).first()
            
            return job
            
        finally:
            session.close()
    
    def display_job_details(self, job: Job) -> None:
        """Display comprehensive job details"""
        
        print("\n" + "="*70)
        print(f"🎯 JOB OPPORTUNITY #{self.session_stats['reviewed'] + 1}")
        print("="*70)
        
        print(f"\n🏢 COMPANY: {job.company}")
        print(f"💼 POSITION: {job.position}")
        print(f"📍 LOCATION: {job.location or 'Remote'}")
        print(f"⭐ RELEVANCE SCORE: {job.relevance_score:.2%}")
        print(f"🔗 JOB URL: {job.url[:60]}..." if job.url else "🔗 JOB URL: N/A")
        
        print(f"\n📧 APPLICATION DETAILS:")
        print(f"   Will send to: {job.company_email}")
        print(f"   From: {settings.email.address}")
        
        # Show why this job matches
        print(f"\n🎯 WHY THIS MATCHES YOU:")
        if job.relevance_score >= 0.9:
            print("   ✅ Excellent match - AI/ML role at top company")
        elif job.relevance_score >= 0.8:
            print("   ✅ Strong match - Senior role with relevant tech")
        elif job.relevance_score >= 0.7:
            print("   ✅ Good match - Aligns with your experience")
        else:
            print("   ⚠️ Potential match - Worth considering")
    
    def generate_email_content(self, job: Job) -> Dict:
        """Generate personalized email content"""
        
        # Try to use personalized email composer first
        try:
            from src.services.email_composer import EmailComposer
            composer = EmailComposer()
            email_content = composer.compose_email(job.__dict__)
            return {
                'subject': email_content['subject'],
                'body': email_content['body']
            }
        except Exception as e:
            # Fallback to basic content generator
            cover_letter = self.content_gen.generate_cover_letter(job)
            
            # Generate subject
            subject_templates = [
                f"Application for {job.position} - Matthew Scott",
                f"{job.position} Role - 10 Years Healthcare AI Experience",
                f"Re: {job.position} at {job.company}",
                f"Matthew Scott - {job.position} Application",
                f"Interested in {job.position} Position at {job.company}"
            ]
            
            # Pick best subject
            if 'AI' in job.position or 'ML' in job.position:
                subject = subject_templates[1]
            elif 'Senior' in job.position or 'Staff' in job.position:
                subject = subject_templates[1]
            else:
                subject = subject_templates[0]
            
            return {
                'subject': subject,
                'body': cover_letter
            }
    
    def preview_email(self, job: Job, content: Dict) -> None:
        """Display email preview"""
        
        print("\n" + "-"*70)
        print("📧 EMAIL PREVIEW:")
        print("-"*70)
        print(f"Subject: {content['subject']}")
        print(f"\n{content['body']}")
        print("-"*70)
        
        # Show resume info
        resume_path = self.resume_service.get_resume_for_job(job)
        if resume_path and Path(resume_path).exists():
            print(f"\n📎 Attachment: {Path(resume_path).name}")
        else:
            print(f"\n⚠️ Resume not found")
    
    def get_user_decision(self) -> str:
        """Get user's decision on application"""
        
        print("\n" + "="*70)
        print("📋 WHAT WOULD YOU LIKE TO DO?")
        print("="*70)
        print("1. ✅ SEND - Send this application as shown")
        print("2. ⏭️ SKIP - Skip this job, move to next")
        print("3. ✏️ EDIT - Edit the email content")
        print("4. 💾 SAVE - Save for later review")
        print("5. ❌ STOP - End this session")
        
        while True:
            choice = input("\nYour choice (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            print("Please enter 1, 2, 3, 4, or 5")
    
    def send_application(self, job: Job, content: Dict) -> bool:
        """Send the application with safety checks"""
        
        # Final confirmation
        print("\n⚠️ FINAL CONFIRMATION")
        print(f"   Send to: {job.company_email}")
        print(f"   Company: {job.company}")
        print(f"   Position: {job.position}")
        
        confirm = input("\nConfirm send? (yes/no): ").lower()
        if confirm != 'yes':
            print("❌ Cancelled")
            return False
        
        print("\n📤 Sending application...")
        
        # Get resume path
        resume_path = self.resume_service.get_resume_for_job(job)
        
        # Send via email service
        success = self.email_service.send_application(
            to_email=job.company_email,
            subject=content['subject'],
            body=content['body'],
            resume_path=resume_path
        )
        
        if success:
            # Mark as applied in database
            session = self.db.get_session()
            try:
                db_job = session.query(Job).filter_by(id=job.id).first()
                if db_job:
                    db_job.applied = True
                    db_job.applied_date = datetime.now()
                    db_job.application_method = 'email'
                    db_job.status = 'applied'
                    session.commit()
            finally:
                session.close()
            
            print("✅ Application sent successfully!")
            self.session_stats['sent'] += 1
            return True
        else:
            print("❌ Failed to send application")
            self.session_stats['failed'] += 1
            return False
    
    def edit_content(self, content: Dict) -> Dict:
        """Allow user to edit email content"""
        
        print("\n✏️ EDIT MODE")
        print("Current subject: " + content['subject'])
        new_subject = input("New subject (or press Enter to keep): ").strip()
        if new_subject:
            content['subject'] = new_subject
        
        print("\nWould you like to edit the body? (y/n): ", end="")
        if input().lower() == 'y':
            print("\nPaste new body (end with '###' on a new line):")
            lines = []
            while True:
                line = input()
                if line == '###':
                    break
                lines.append(line)
            content['body'] = '\n'.join(lines)
        
        self.session_stats['edited'] += 1
        return content
    
    def run_workflow(self) -> None:
        """Run the guided application workflow"""
        
        print("\n" + "="*70)
        print("🚀 GUIDED JOB APPLICATION WORKFLOW")
        print("="*70)
        print("\n📋 How this works:")
        print("1. You'll review each job opportunity")
        print("2. See the exact email that will be sent")
        print("3. Approve, skip, or edit each application")
        print("4. Applications are sent only with your approval")
        print(f"\n⚠️ Safety limits: Max {self.MAX_PER_SESSION} per session")
        
        # Check email configuration
        if not settings.email.is_configured:
            print("\n❌ Email not configured! Run: python setup_email_smtp.py")
            return
        
        print(f"\n✅ Email configured: {settings.email.address}")
        
        # Main workflow loop
        while self.session_stats['sent'] < self.MAX_PER_SESSION:
            # Get next job
            job = self.get_next_job()
            if not job:
                print("\n✅ No more eligible jobs to review")
                break
            
            self.session_stats['reviewed'] += 1
            
            # Display job details
            self.display_job_details(job)
            
            # Generate email content
            content = self.generate_email_content(job)
            
            # Preview email
            self.preview_email(job, content)
            
            # Get user decision
            decision = self.get_user_decision()
            
            if decision == '1':  # Send
                if self.send_application(job, content):
                    self.session_stats['approved'] += 1
                    # Rate limiting
                    print(f"\n⏱️ Waiting {self.MIN_DELAY_SECONDS} seconds before next...")
                    time.sleep(self.MIN_DELAY_SECONDS)
                    
            elif decision == '2':  # Skip
                print("⏭️ Skipped")
                self.session_stats['skipped'] += 1
                
            elif decision == '3':  # Edit
                content = self.edit_content(content)
                self.preview_email(job, content)
                if input("\nSend edited version? (yes/no): ").lower() == 'yes':
                    if self.send_application(job, content):
                        self.session_stats['approved'] += 1
                        time.sleep(self.MIN_DELAY_SECONDS)
                        
            elif decision == '4':  # Save
                # TODO: Implement save for later
                print("💾 Saved for later (feature coming soon)")
                
            elif decision == '5':  # Stop
                print("🛑 Stopping session...")
                break
            
            # Check if limit reached
            if self.session_stats['sent'] >= self.MAX_PER_SESSION:
                print(f"\n⚠️ Session limit reached ({self.MAX_PER_SESSION} applications)")
                break
        
        # Show session summary
        self.show_summary()
    
    def show_summary(self) -> None:
        """Display session summary"""
        
        print("\n" + "="*70)
        print("📊 SESSION SUMMARY")
        print("="*70)
        print(f"\n📋 Applications Reviewed: {self.session_stats['reviewed']}")
        print(f"✅ Sent Successfully: {self.session_stats['sent']}")
        print(f"⏭️ Skipped: {self.session_stats['skipped']}")
        print(f"✏️ Edited: {self.session_stats['edited']}")
        print(f"❌ Failed: {self.session_stats['failed']}")
        
        if self.session_stats['sent'] > 0:
            print(f"\n🎯 Success Rate: {self.session_stats['sent']}/{self.session_stats['approved']}")
            print(f"\n📧 Check your sent folder for confirmations")
            print(f"📊 Track responses with: python main.py status")
        
        print("\n✅ Session complete!")


def main():
    """Main entry point"""
    workflow = GuidedApplicationWorkflow()
    
    try:
        workflow.run_workflow()
    except KeyboardInterrupt:
        print("\n\n⚠️ Session interrupted by user")
        workflow.show_summary()
    except Exception as e:
        logger.error(f"Error in workflow: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()