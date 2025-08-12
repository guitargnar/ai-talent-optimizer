#!/usr/bin/env python3
"""
Personalized Application System
Replaces generic applications with memorable, specific ones
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import time
import random

from bcc_email_tracker import BCCEmailTracker
from differentiation_engine import DifferentiationEngine
from unique_cover_letters import UniqueCoverLetterGenerator
from resume_pdf_generator import ResumePDFGenerator

class PersonalizedApplicationSystem:
    """Send memorable applications that stand out"""
    
    def __init__(self):
        self.db_path = "UNIFIED_AI_JOBS.db"
        self.bcc_tracker = BCCEmailTracker()
        self.differentiation = DifferentiationEngine()
        self.letter_generator = UniqueCoverLetterGenerator()
        
        # Load config
        with open('unified_config.json', 'r') as f:
            self.config = json.load(f)
        
        # Resume paths
        self.resume_versions = {
            'technical': Path("resumes/technical_deep_dive.pdf"),
            'executive': Path("resumes/executive_leadership.pdf"),
            'healthcare': Path("resumes/matthew_scott_healthcare_ai.pdf"),
            'default': Path("resumes/matthew_scott_ai_ml_resume.pdf")
        }
    
    def get_high_value_jobs(self, limit=10):
        """Get high-value jobs worth personalizing"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Focus on high-value companies and roles
        query = """
        SELECT * FROM job_discoveries 
        WHERE applied = 0 
        AND relevance_score >= 0.5
        AND (
            company LIKE '%OpenAI%' OR 
            company LIKE '%Anthropic%' OR 
            company LIKE '%Google%' OR 
            company LIKE '%Meta%' OR 
            company LIKE '%Apple%' OR
            company LIKE '%Microsoft%' OR
            position LIKE '%Senior%' OR
            position LIKE '%Staff%' OR
            position LIKE '%Principal%' OR
            position LIKE '%Lead%'
        )
        ORDER BY relevance_score DESC, salary_range DESC
        LIMIT ?
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (limit,))
        jobs = cursor.fetchall()
        conn.close()
        
        return [dict(job) for job in jobs]
    
    def create_personalized_application(self, job):
        """Create a completely personalized application"""
        print(f"\n🎯 Creating personalized application for {job['company']} - {job['position']}")
        
        # Generate differentiated email content
        memorable_content = self.differentiation.create_memorable_email(job)
        
        # Alternative: Use unique cover letter generator
        unique_letter = self.letter_generator.create_unique_cover_letter(
            job['company'], 
            job['position'],
            job.get('description', '')
        )
        
        # Choose best approach based on company
        if job['company'].lower() in ['openai', 'anthropic', 'google deepmind']:
            # Use differentiation engine for top companies
            subject = memorable_content['subject']
            body = memorable_content['body']
            print("  ✓ Using differentiation engine for top-tier company")
        else:
            # Use unique letter generator for others
            subject = f"{job['position']} - ML Leader with {random.choice(['$1.2M Impact', '50M+ Scale', '10K Lives Saved'])}"
            body = unique_letter
            print("  ✓ Using unique letter generator")
        
        # Select best resume
        resume_path = self._select_personalized_resume(job)
        
        return {
            'subject': subject,
            'body': body,
            'resume': resume_path,
            'personalization_notes': memorable_content.get('memorable_elements', [])
        }
    
    def _select_personalized_resume(self, job):
        """Select the most appropriate resume version"""
        position = job['position'].lower()
        company = job['company'].lower()
        
        if 'health' in company or 'medical' in position or 'clinical' in position:
            resume_type = 'healthcare'
        elif any(word in position for word in ['director', 'vp', 'head', 'principal']):
            resume_type = 'executive'
        elif any(word in position for word in ['infrastructure', 'platform', 'architect']):
            resume_type = 'technical'
        else:
            resume_type = 'default'
        
        resume_path = self.resume_versions.get(resume_type, self.resume_versions['default'])
        
        if resume_path.exists():
            print(f"  ✓ Selected {resume_type} resume variant")
            return str(resume_path)
        else:
            print(f"  ! {resume_type} resume not found, using default")
            return str(self.resume_versions['default'])
    
    def send_personalized_application(self, job):
        """Send a personalized application"""
        # Create personalized content
        application = self.create_personalized_application(job)
        
        # Determine email address
        careers_email = job.get('apply_url', '')
        if '@' not in careers_email:
            company_name = job['company'].lower().replace(' ', '').replace("'", "")
            careers_email = f"careers@{company_name}.com"
        
        print(f"\n📧 Sending personalized application to {careers_email}")
        
        # Send via BCC tracker
        success, tracking_id = self.bcc_tracker.send_tracked_email(
            to_email=careers_email,
            subject=application['subject'],
            body=application['body'],
            email_type='applications',
            attachments=[application['resume']] if application['resume'] else None
        )
        
        if success:
            self._mark_applied(job['id'])
            print(f"  ✅ Sent successfully! Tracking ID: {tracking_id}")
            
            # Log personalization elements
            print(f"\n  📝 What makes this application unique:")
            for element in application['personalization_notes']:
                print(f"     • {element}")
            
            return True
        else:
            print(f"  ❌ Failed to send")
            return False
    
    def _mark_applied(self, job_id):
        """Mark job as applied in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE job_discoveries 
            SET applied = 1, 
                applied_date = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), job_id))
        
        conn.commit()
        conn.close()
    
    def run_personalized_batch(self, max_applications=5):
        """Run a batch of personalized applications"""
        print("🚀 Personalized Application Campaign")
        print("=" * 60)
        
        # Get high-value jobs
        jobs = self.get_high_value_jobs(limit=max_applications)
        
        if not jobs:
            print("No high-value jobs found. Consider lowering criteria.")
            return
        
        print(f"\n📋 Found {len(jobs)} high-value opportunities:")
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job['company']} - {job['position']} (Score: {job['relevance_score']})")
        
        input("\nPress Enter to start sending personalized applications...")
        
        sent_count = 0
        for job in jobs:
            if self.send_personalized_application(job):
                sent_count += 1
                
                # Rate limiting
                wait_time = random.randint(60, 180)
                print(f"\n⏱️  Waiting {wait_time} seconds (appears more human)...")
                time.sleep(wait_time)
        
        print(f"\n✅ Sent {sent_count} personalized applications!")
        print("Each one unique, memorable, and specific to the role.")


def main():
    """Run personalized applications"""
    import sys
    
    system = PersonalizedApplicationSystem()
    
    if '--demo' in sys.argv:
        # Demo mode - show what would be sent
        jobs = system.get_high_value_jobs(3)
        for job in jobs:
            app = system.create_personalized_application(job)
            print(f"\n{'='*60}")
            print(f"TO: {job['company']} - {job['position']}")
            print(f"SUBJECT: {app['subject']}")
            print(f"\nBODY PREVIEW:")
            print(app['body'][:500] + "...")
            print(f"\nRESUME: {app['resume']}")
    
    elif '--batch' in sys.argv:
        batch_size = 5
        if len(sys.argv) > 2:
            batch_size = int(sys.argv[2])
        system.run_personalized_batch(batch_size)
    
    else:
        print("Personalized Application System")
        print("\nUsage:")
        print("  python personalized_apply.py --demo     # See examples")
        print("  python personalized_apply.py --batch 3  # Send 3 personalized applications")


if __name__ == "__main__":
    main()