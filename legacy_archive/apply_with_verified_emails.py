#!/usr/bin/env python3
"""
Apply with Verified Emails - Simplified application sender for verified emails only
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import time
import os

from bcc_email_tracker import BCCEmailTracker
from improved_application_templates import ImprovedApplicationTemplates

class VerifiedEmailApplicator:
    """Apply only to companies with verified emails"""
    
    def __init__(self):
        self.db_path = "unified_platform.db"
        self.bcc_tracker = BCCEmailTracker()
        self.templates = ImprovedApplicationTemplates()
        
        # Resume paths
        self.resume_paths = {
            'default': Path("resumes/matthew_scott_ai_ml_resume.pdf"),
            'technical': Path("resumes/technical_deep_dive.pdf"),
            'executive': Path("resumes/executive_leadership.pdf")
        }
    
    def get_verified_jobs(self, limit=5):
        """Get jobs with verified emails"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM jobs 
            WHERE applied = 0 
            AND verified_email IS NOT NULL 
            AND verified_email != ''
            AND relevance_score >= 0.3
            ORDER BY relevance_score DESC
            LIMIT ?
        """, (limit,))
        
        jobs = cursor.fetchall()
        conn.close()
        
        return [dict(job) for job in jobs]
    
    def select_resume(self, title):
        """Select appropriate resume for position"""
        position_lower = position.lower()
        
        if any(word in position_lower for word in ['director', 'vp', 'head', 'chief', 'executive']):
            resume_type = 'executive'
        elif any(word in position_lower for word in ['engineer', 'developer', 'scientist', 'ml', 'ai']):
            resume_type = 'technical'
        else:
            resume_type = 'default'
        
        resume_version = self.resume_paths.get(resume_type, self.resume_paths['default'])
        
        if resume_path.exists():
            print(f"  📄 Using {resume_type} resume")
            return str(resume_version)
        else:
            print(f"  📄 Using default resume")
            return str(self.resume_paths['default'])
    
    def apply_to_job(self, job):
        """Apply to a single job with verified email"""
        print(f"\n{'='*60}")
        print(f"📧 Applying to {job['company']}")
        print(f"  Position: {job['position']}")
        print(f"  Email: {job['verified_email']}")
        print(f"  Score: {job['relevance_score']:.2f}")
        
        # Select resume
        resume_version = self.select_resume(job['position'])
        
        # Generate cover letter
        print(f"  📝 Generating personalized cover letter...")
        cover_letter = self.templates.generate_targeted_cover_letter(
            job['company'], 
            job['position']
        )
        
        # Prepare email
        subject = f"Application for {job['position']} - Matthew Scott"
        
        # Send via BCC tracker
        print(f"  📤 Sending application...")
        success, tracking_id = self.bcc_tracker.send_tracked_email(
            to_email=job['verified_email'],
            subject=subject,
            body=cover_letter,
            email_type='applications',
            attachments=[resume_path] if Path(resume_version).exists() else None
        )
        
        if success:
            # Mark as applied
            self.mark_applied(job['id'], job['verified_email'])
            print(f"  ✅ SUCCESS! Tracking ID: {tracking_id}")
            return True
        else:
            print(f"  ❌ Failed to send")
            return False
    
    def mark_applied(self, job_id, email_used):
        """Mark job as applied in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE jobs 
            SET applied = 1,
                applied_date = ?,
                actual_email_used = ?,
                email_verified = 1,
                email_confidence = 100
            WHERE id = ?
        """, (datetime.now().isoformat(), email_used, job_id))
        
        conn.commit()
        conn.close()
    
    def run_batch(self, max_applications=3):
        """Run batch of applications"""
        print("\n🚀 VERIFIED EMAIL APPLICATION BATCH")
        print("="*60)
        
        # Get jobs with verified emails
        jobs = self.get_verified_jobs(max_applications)
        
        if not jobs:
            print("❌ No jobs found with verified emails")
            print("\n💡 Add more verified emails:")
            print("   python3 collect_real_emails.py")
            return 0
        
        print(f"\n✅ Found {len(jobs)} jobs with verified emails:")
        for job in jobs:
            print(f"  • {job['company']} - {job['position']}")
        
        applied = 0
        failed = 0
        
        for i, job in enumerate(jobs, 1):
            print(f"\n[{i}/{len(jobs)}] Processing...")
            
            if self.apply_to_job(job):
                applied += 1
                # Wait between applications
                if i < len(jobs):
                    wait = 30
                    print(f"\n⏱️  Waiting {wait} seconds before next application...")
                    time.sleep(wait)
            else:
                failed += 1
        
        print("\n" + "="*60)
        print("📊 BATCH COMPLETE:")
        print(f"  ✅ Successful: {applied}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📧 All used VERIFIED emails - no bounces expected!")
        
        return applied


def main():
    """Main execution"""
    import sys
    
    applicator = VerifiedEmailApplicator()
    
    # Check for batch size argument
    batch_size = 3
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
        except:
            pass
    
    print(f"📧 Applying to up to {batch_size} companies with verified emails")
    print("⚠️  Only companies with REAL, VERIFIED emails will be contacted")
    
    applied = applicator.run_batch(batch_size)
    
    if applied > 0:
        print(f"\n✅ Successfully applied to {applied} companies!")
        print("📈 These should NOT bounce - we used verified emails")
        print("\n🔍 Check for responses in 3-7 days:")
        print("   python3 accurate_response_checker.py")
    else:
        print("\n⚠️  No applications sent")
        print("Consider adding more verified emails for high-value companies")


if __name__ == "__main__":
    main()