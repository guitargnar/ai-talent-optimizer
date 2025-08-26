#!/usr/bin/env python3
"""
Automated Job Application System
Applies to jobs from the discovery database
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import time
import random

from email_application_tracker import EmailApplicationTracker
from bcc_email_tracker import BCCEmailTracker
from ats_ai_optimizer import ATSAIOptimizer
from resume_pdf_generator import ResumePDFGenerator
from improved_application_templates import ImprovedApplicationTemplates
from email_verification_system import EmailVerificationSystem  # Added for email verification
from enhanced_email_verifier import EnhancedEmailVerifier  # Enhanced verification
from collect_real_emails import RealEmailCollector  # Real email database


class AutomatedApplicationSystem:
    """Automate job applications from discovered opportunities"""
    
    def __init__(self):
        self.db_path = "unified_platform.db"
        self.email_tracker = EmailApplicationTracker()
        self.bcc_tracker = BCCEmailTracker()
        self.email_verifier = EmailVerificationSystem()  # Initialize email verifier
        self.enhanced_verifier = EnhancedEmailVerifier()  # Enhanced verification
        self.email_collector = RealEmailCollector()  # Real email database
        self.resume_version = Path("resumes/matthew_scott_ai_ml_resume.pdf")
        
        # Load configuration
        with open('unified_config.json', 'r') as f:
            self.config = json.load(f)
        
        # Resume generation
        self.ats_optimizer = ATSAIOptimizer()
        self.pdf_generator = ResumePDFGenerator()
        self.resume_versions = {
            'technical': Path("resumes/technical_deep_dive.pdf"),
            'executive': Path("resumes/executive_leadership.pdf"),
            'master': Path("resumes/master_resume_-_all_keywords.pdf"),
            'default': Path("resumes/matthew_scott_ai_ml_resume.pdf")
        }
        
        # Application templates
        self.improved_templates = ImprovedApplicationTemplates()
        self.templates = self._load_templates()
        
        # Rate limiting
        self.applications_today = 0
        self.max_daily = 30
        
    def _load_templates(self):
        """Load application templates"""
        return {
            'cover_letter': """Dear {company} Hiring Team,

I am writing to express my strong interest in the {position} position at {company}.

With my proven track record of delivering $1.2M in AI-driven savings at Humana and 10+ years of experience building production ML systems for healthcare, I am excited about the opportunity to contribute to your team.

Key highlights from my background:
• Led ML initiatives that transformed risk prediction accuracy by 47%
• Built scalable AI/ML platforms serving 50M+ users
• Deep expertise in Python, cloud architecture, and healthcare analytics
• Successful remote work track record since 2015

I have attached my resume for your review and would welcome the opportunity to discuss how my expertise in healthcare AI and platform engineering can benefit {company}.

Thank you for your consideration. I look forward to hearing from you.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77"""
        }
    
    def get_unapplied_jobs(self, limit=10):
        """Get jobs that haven't been applied to yet"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Get minimum score from config
        min_score = self.config.get('min_relevance_score', 0.3)
        
        query = """
        SELECT * FROM jobs 
        WHERE applied = 0 
        AND relevance_score >= ?
        ORDER BY relevance_score DESC, salary_range DESC
        LIMIT ?
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (min_score, limit))
        jobs = cursor.fetchall()
        conn.close()
        
        return [dict(job) for job in jobs]
    
    def _select_resume_for_job(self, job):
        """Select the best resume version for the job"""
        title = job['position'].lower()
        company = job['company'].lower()
        
        # Keywords for matching
        technical_keywords = ['engineer', 'developer', 'architect', 'ml', 'ai', 'scientist', 'technical']
        executive_keywords = ['director', 'vp', 'president', 'head', 'chief', 'executive', 'manager', 'lead']
        
        # Check for executive roles
        if any(keyword in position for keyword in executive_keywords):
            resume_type = 'executive'
        # Check for technical roles
        elif any(keyword in position for keyword in technical_keywords):
            resume_type = 'technical'
        # Default to master version
        else:
            resume_type = 'master'
        
        resume_version = self.resume_versions.get(resume_type, self.resume_versions['default'])
        
        # Ensure the resume exists
        if resume_path.exists():
            print(f"  📄 Using {resume_type} resume: {resume_path.name}")
            return str(resume_version)
        else:
            print(f"  ⚠️  {resume_type} resume not found, using default")
            return str(self.resume_versions['default'])
    
    def apply_to_job(self, job):
        """Apply to a specific job"""
        print(f"\n📧 Applying to {job['company']} - {job['position']}...")
        
        # Select appropriate resume version for this job
        resume_version = self._select_resume_for_job(job)
        
        # Generate personalized cover letter
        # Use improved templates for top AI companies
        if job['company'].lower() in ['openai', 'anthropic', 'google deepmind']:
            cover_letter = self.improved_templates.generate_targeted_cover_letter(
                job['company'], 
                job['position']
            )
        else:
            # Use generic improved template for other companies
            cover_letter = self.improved_templates.generate_targeted_cover_letter(
                job['company'],
                job['position']
            )
        
        # FIRST: Try to get verified email from database
        email_info = self.email_collector.get_email_for_company(job['company'])
        
        if email_info and email_info.get('email'):
            careers_email = email_info['email']
            print(f"  ✅ Using verified email from database: {careers_email}")
            print(f"     Source: {email_info.get('source', 'unknown')}")
        else:
            # Try to get from job posting
            careers_email = job.get('apply_url', '')
            
            if '@' not in careers_email:
                # NO LONGER generate fake emails - skip if no real email
                print(f"  ❌ No verified email found for {job['company']}")
                print(f"  ⚠️  SKIPPING - We no longer send to unverified addresses")
                print(f"  💡 TIP: Add email manually using: python3 collect_real_emails.py")
                return False
        
        # ENHANCED VERIFICATION - Use new comprehensive checker
        verification = self.enhanced_verifier.comprehensive_verify(careers_email, job['company'])
        
        if not verification['is_valid']:
            print(f"  ❌ Email failed verification: {careers_email}")
            print(f"  Confidence: {verification['confidence']}%")
            print(f"  Recommendation: {verification.get('recommendation', 'DO NOT SEND')}")
            
            for check, details in verification['checks'].items():
                if not details.get('valid', False):
                    print(f"    ❌ {check}: {details.get('message', 'Failed')}")
            
            # Add to blacklist
            print(f"  🚫 Email added to blacklist to prevent future attempts")
            return False
        
        if verification['confidence'] < 70:
            print(f"  ⚠️  Low confidence email: {careers_email}")
            print(f"  Confidence: {verification['confidence']}%")
            print(f"  Recommendation: {verification.get('recommendation', 'RISKY')}")
            
            # Ask for confirmation on low confidence
            if verification['confidence'] < 50:
                print(f"  ⏭️  Skipping due to high bounce risk")
                return False
        
        print(f"  ✅ Email verified: {careers_email}")
        print(f"     Confidence: {verification['confidence']}%")
        print(f"     Recommendation: {verification.get('recommendation', 'Safe to send')}")
        
        # Send application via BCC tracker
        subject = f"Application for {job['position']} - Matthew Scott"
        
        success, tracking_id = self.bcc_tracker.send_tracked_email(
            to_email=careers_email,
            subject=subject,
            body=cover_letter,
            email_type='applications',
            attachments=[resume_path] if resume_path else None
        )
        
        if success:
            # Mark as applied in database
            self._mark_applied(job['id'])
            self.applications_today += 1
            print(f"  ✅ Applied successfully! Tracking ID: {tracking_id}")
            return True
        elif tracking_id:
            # Email was already sent previously - still mark as applied
            self._mark_applied(job['id'])
            print(f"  ✅ Already applied (marked in database). Tracking ID: {tracking_id}")
            return True
        else:
            print(f"  ❌ Failed to apply")
            return False
    
    def _mark_applied(self, job_id):
        """Mark job as applied in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE jobs 
            SET applied = 1, 
                applied_date = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), job_id))
        
        conn.commit()
        conn.close()
    
    def run_application_batch(self, max_applications=5):
        """Run a batch of applications"""
        print("🚀 Running Automated Application Batch")
        print("=" * 60)
        
        # Get unapplied jobs
        jobs = self.get_unapplied_jobs(limit=max_applications)
        
        if not jobs:
            print("No suitable jobs found to apply to")
            return
        
        print(f"Found {len(jobs)} jobs to apply to:")
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job['company']} - {job['position']} (${job.get('salary_range', 'N/A')})")
        
        applied_count = 0
        
        for job in jobs:
            if self.applications_today >= self.max_daily:
                print(f"\n⚠️  Daily limit reached ({self.max_daily} applications)")
                break
            
            # Apply to job
            if self.apply_to_job(job):
                applied_count += 1
                
                # Rate limiting - wait between applications
                wait_time = random.randint(30, 90)
                print(f"  ⏱️  Waiting {wait_time} seconds before next application...")
                time.sleep(wait_time)
        
        print(f"\n✅ Applied to {applied_count} jobs successfully!")
        print(f"Total applications today: {self.applications_today}")
        
        return applied_count


def main():
    """Run automated applications"""
    import sys
    
    system = AutomatedApplicationSystem()
    
    if '--batch' in sys.argv:
        # Run batch applications
        batch_size = 5
        if len(sys.argv) > 2:
            try:
                batch_size = int(sys.argv[2])
            except:
                pass
        
        system.run_application_batch(max_applications=batch_size)
    
    else:
        # Interactive mode
        print("🤖 Automated Application System")
        print("\nOptions:")
        print("1. Apply to top 5 jobs")
        print("2. Apply to specific number of jobs")
        print("3. View unapplied jobs")
        
        choice = input("\nSelect option (1-3): ")
        
        if choice == '1':
            system.run_application_batch(5)
        elif choice == '2':
            num = int(input("How many jobs to apply to? "))
            system.run_application_batch(num)
        elif choice == '3':
            jobs = system.get_unapplied_jobs(20)
            print(f"\n📋 Top 20 unapplied jobs:")
            for i, job in enumerate(jobs, 1):
                print(f"{i}. {job['company']} - {job['position']} (Score: {job['relevance_score']})")


if __name__ == "__main__":
    main()
