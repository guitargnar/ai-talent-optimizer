#!/usr/bin/env python3
"""
Preview Job Applications
Shows exactly what will be sent before actually sending
Ensures compliance with usage policies through transparency
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Optional

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.content import ContentGenerator
from src.services.resume import ResumeService
from src.models.database import DatabaseManager, Job

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class ApplicationPreview:
    """Preview applications before sending"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.content_gen = ContentGenerator()
        self.resume_service = ResumeService()
        
    def get_top_opportunities(self, count: int = 10) -> List[Job]:
        """Get top job opportunities to preview"""
        session = self.db.get_session()
        
        try:
            jobs = session.query(Job).filter(
                Job.applied == False,
                Job.relevance_score >= 0.65,
                Job.company_email != None,
                Job.company_email != 'N/A',
                ~Job.company_email.contains('adzuna'),
                ~Job.company_email.contains('indeed'),
                Job.source.in_(['Greenhouse', 'Lever'])
            ).order_by(
                Job.relevance_score.desc()
            ).limit(count).all()
            
            return jobs
            
        finally:
            session.close()
    
    def generate_application_content(self, job: Job) -> Dict:
        """Generate application content for a job"""
        
        # Try to use personalized email composer first
        try:
            from src.services.email_composer import EmailComposer
            composer = EmailComposer()
            email_content = composer.compose_email(job.__dict__)
            cover_letter = email_content['body']
            subject = email_content['subject']
        except:
            # Fallback to basic content generator
            cover_letter = self.content_gen.generate_cover_letter(job)
            subject = self._generate_subject(job)
        
        # Determine best resume variant
        resume_path = self.resume_service.get_resume_for_job(job)
        
        return {
            'job_id': job.id,
            'company': job.company,
            'position': job.position,
            'email_to': job.company_email,
            'subject': subject,
            'body': cover_letter,
            'resume': resume_path,
            'relevance_score': job.relevance_score,
            'job_url': job.url
        }
    
    def _generate_subject(self, job: Job) -> str:
        """Generate email subject line"""
        templates = [
            f"Application for {job.position} - Matthew Scott",
            f"{job.position} Role - 10 Years Healthcare AI Experience",
            f"Re: {job.position} at {job.company}",
            f"Interested in {job.position} Position",
            f"{job.position} - Matthew Scott (Humana AI Engineer)"
        ]
        
        # Pick appropriate template
        if 'Senior' in job.position or 'Staff' in job.position or 'Principal' in job.position:
            return templates[1]  # Emphasize experience
        elif 'AI' in job.position or 'ML' in job.position:
            return templates[4]  # Emphasize AI background
        else:
            return templates[0]  # Default professional
    
    def preview_application(self, job: Job) -> None:
        """Display preview of an application"""
        
        content = self.generate_application_content(job)
        
        print("\n" + "="*70)
        print(f"📋 APPLICATION PREVIEW #{job.id}")
        print("="*70)
        
        print(f"\n🏢 Company: {job.company}")
        print(f"💼 Position: {job.position}")
        print(f"📍 Location: {job.location}")
        print(f"🔗 Job URL: {job.url[:50]}..." if job.url else "🔗 Job URL: N/A")
        print(f"⭐ Relevance Score: {job.relevance_score:.2%}")
        
        print(f"\n📧 EMAIL DETAILS:")
        print(f"To: {content['email_to']}")
        print(f"From: matthewdscott7@gmail.com")
        print(f"Subject: {content['subject']}")
        
        print(f"\n📄 EMAIL BODY:")
        print("-" * 70)
        print(content['body'])
        print("-" * 70)
        
        print(f"\n📎 ATTACHMENT:")
        if content['resume'] and Path(content['resume']).exists():
            print(f"✅ Resume: {Path(content['resume']).name}")
            print(f"   Size: {Path(content['resume']).stat().st_size / 1024:.1f} KB")
        else:
            print(f"⚠️ Resume not found: {content['resume']}")
        
        print("\n" + "="*70)
    
    def preview_batch(self, count: int = 5) -> List[Dict]:
        """Preview multiple applications"""
        
        jobs = self.get_top_opportunities(count)
        
        if not jobs:
            print("\n❌ No eligible jobs found to preview")
            return []
        
        print(f"\n" + "="*70)
        print(f"🎯 TOP {len(jobs)} JOB OPPORTUNITIES")
        print("="*70)
        
        applications = []
        
        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job.company} - {job.position}")
            print(f"   Score: {job.relevance_score:.2%} | Email: {job.company_email}")
            applications.append(self.generate_application_content(job))
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total opportunities: {len(jobs)}")
        print(f"   Average relevance: {sum(j.relevance_score for j in jobs)/len(jobs):.2%}")
        print(f"   Top company: {jobs[0].company if jobs else 'N/A'}")
        
        # Group by company
        companies = {}
        for job in jobs:
            if job.company not in companies:
                companies[job.company] = []
            companies[job.company].append(job.position)
        
        print(f"\n🏢 BY COMPANY:")
        for company, positions in companies.items():
            print(f"   {company}: {len(positions)} position(s)")
            for pos in positions[:3]:  # Show first 3
                print(f"      - {pos}")
        
        return applications


def main():
    """Main preview function"""
    
    print("\n" + "="*70)
    print("🔍 JOB APPLICATION PREVIEW SYSTEM")
    print("="*70)
    print("\nThis system shows you exactly what will be sent")
    print("You maintain full control over every application")
    
    previewer = ApplicationPreview()
    
    # Get preview count
    try:
        count = int(input("\nHow many applications to preview? (1-10): ") or "5")
        count = min(max(count, 1), 10)  # Limit between 1-10
    except:
        count = 5
    
    # Preview applications
    applications = previewer.preview_batch(count)
    
    if not applications:
        return
    
    # Show detailed preview option
    print("\n" + "-"*70)
    show_details = input("\nShow detailed preview for each? (y/n): ").lower()
    
    if show_details == 'y':
        jobs = previewer.get_top_opportunities(count)
        for i, job in enumerate(jobs, 1):
            previewer.preview_application(job)
            
            if i < len(jobs):
                cont = input(f"\nContinue to next? ({i}/{len(jobs)}) (y/n): ").lower()
                if cont != 'y':
                    break
    
    print("\n" + "="*70)
    print("✅ PREVIEW COMPLETE")
    print("="*70)
    print("\n📋 Next Steps:")
    print("1. Review the applications above")
    print("2. Run 'python guided_apply.py' to send with approval")
    print("3. Or edit templates in src/services/email_composer.py")
    print("\n⚠️ Remember:")
    print("- Each application is personalized")
    print("- Daily limit is 10-20 applications")
    print("- All emails go to official careers@ addresses")
    print("- You approve each one before sending")


if __name__ == "__main__":
    main()