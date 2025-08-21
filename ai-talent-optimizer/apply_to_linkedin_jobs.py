#!/usr/bin/env python3
"""
Apply to LinkedIn Jobs with Duplicate Prevention
Uses penalty system to avoid spamming companies
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import sys

sys.path.append('.')
from linkedin_job_scraper import LinkedInJobScraper

class LinkedInApplicationManager:
    """Manages applications to LinkedIn jobs with smart duplicate prevention"""
    
    def __init__(self):
        self.scraper = LinkedInJobScraper()
        self.db_path = Path('data/linkedin_jobs.db')
        self.sent_log = Path('sent_applications_log.json')
        
    def get_eligible_jobs(self) -> List[Dict]:
        """Get jobs we can apply to (respecting penalties)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent jobs that haven't been applied to
        cursor.execute("""
        SELECT job_id, company, position, location, remote_option,
               hours_ago, url, description, salary_range
        FROM linkedin_jobs
        WHERE applied = 0
        AND hours_ago <= 168  -- Within 7 days
        ORDER BY hours_ago ASC
        """)
        
        jobs = []
        for row in cursor.fetchall():
            job = {
                'job_id': row[0],
                'company': row[1],
                'position': row[2],
                'location': row[3],
                'remote_option': row[4],
                'hours_ago': row[5],
                'url': row[6],
                'description': row[7],
                'salary_range': row[8]
            }
            
            # Check if we can apply to this company
            can_apply, reason = self.scraper.can_apply_to_company(job['company'])
            job['can_apply'] = can_apply
            job['apply_status'] = reason
            
            jobs.append(job)
        
        conn.close()
        return jobs
    
    def check_previous_applications(self, company: str) -> Dict:
        """Check history with a company"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get application history
        cursor.execute("""
        SELECT COUNT(*) as total,
               MAX(application_date) as last_date,
               SUM(CASE WHEN response_received = 1 THEN 1 ELSE 0 END) as responses,
               SUM(CASE WHEN response_type = 'rejection' THEN 1 ELSE 0 END) as rejections
        FROM application_tracking
        WHERE company = ?
        """, (company,))
        
        history = cursor.fetchone()
        
        # Get positions applied to
        cursor.execute("""
        SELECT position, application_date, response_type
        FROM application_tracking
        WHERE company = ?
        ORDER BY application_date DESC
        """, (company,))
        
        positions = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_applications': history[0] or 0,
            'last_application': history[1],
            'responses': history[2] or 0,
            'rejections': history[3] or 0,
            'positions': positions
        }
    
    def create_smart_cover_letter(self, job: Dict, history: Dict) -> str:
        """Create cover letter that acknowledges previous applications if any"""
        
        # Check if we've applied before
        if history['total_applications'] > 0:
            # Reference previous interest
            opening = f"""Dear Hiring Team at {job['company']},

I remain deeply interested in contributing to {job['company']}'s mission and am excited to see the {job['position']} role. Having previously expressed interest in joining your team, I've continued to follow {job['company']}'s impressive progress and believe my enhanced skills and recent accomplishments make me an even stronger candidate now."""
        else:
            # First application to this company
            opening = f"""Dear Hiring Team at {job['company']},

I am writing to express my strong interest in the {job['position']} position. Your company's innovative work in AI/ML has caught my attention, and I'm excited about the opportunity to contribute to your team's success."""
        
        # Rest of the letter
        cover_letter = f"""{opening}

Since my last application, I've achieved significant milestones:

• **Enhanced ML Platform**: Expanded my Job Intelligence Platform to process 1000+ jobs daily with 92% accuracy, demonstrating production-ready ML engineering skills directly applicable to {job['company']}'s scale.

• **Advanced Integration**: Built a comprehensive career automation system integrating multiple data sources, OAuth authentication, and intelligent matching algorithms - skills valuable for {job['company']}'s complex systems.

• **Real-World Impact**: My work at Humana continues to save $1.2M annually through ML-driven automation, showing my ability to deliver measurable business value.

My technical expertise aligns perfectly with the {job['position']} role:
- Deep proficiency in TensorFlow, PyTorch, and modern ML frameworks
- Production deployment of LLMs and neural architectures
- Proven ability to scale ML systems handling millions of data points

I would welcome the opportunity to discuss how my experience and recent accomplishments can contribute to {job['company']}'s continued innovation.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77
github.com/guitargnar
"""
        
        return cover_letter
    
    def apply_to_job(self, job: Dict) -> bool:
        """Apply to a specific job with all checks"""
        
        # Final check if we can apply
        can_apply, reason = self.scraper.can_apply_to_company(job['company'])
        if not can_apply:
            print(f"❌ Cannot apply to {job['company']}: {reason}")
            return False
        
        # Get application history
        history = self.check_previous_applications(job['company'])
        
        # Create tailored cover letter
        cover_letter = self.create_smart_cover_letter(job, history)
        
        # Prepare application package
        app_data = {
            'job': job,
            'cover_letter': cover_letter,
            'resume_path': '/Users/matthewscott/Desktop/MATTHEW_SCOTT_AI_ML_ENGINEER_2025.pdf',
            'subject': f"Application for {job['position']} - Matthew Scott",
            'to_email': f"careers@{job['company'].lower().replace(' ', '')}.com",
            'application_history': history
        }
        
        # Save application
        filename = f"application_{job['company'].replace(' ', '_')}_{job['job_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(app_data, f, indent=2)
        
        # Record application in database
        self.scraper.record_application(job['company'], job['position'], job['job_id'])
        
        # Mark job as applied
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE linkedin_jobs
        SET applied = 1, applied_date = CURRENT_TIMESTAMP
        WHERE job_id = ?
        """, (job['job_id'],))
        conn.commit()
        conn.close()
        
        print(f"✅ Prepared application for {job['position']} at {job['company']}")
        print(f"   Previous applications: {history['total_applications']}")
        print(f"   Saved to: {filename}")
        
        return True
    
    def smart_apply_batch(self, limit: int = 5):
        """Intelligently apply to jobs respecting all constraints"""
        print("\n🤖 Smart Application Process")
        print("=" * 60)
        
        # Get eligible jobs
        jobs = self.get_eligible_jobs()
        eligible = [j for j in jobs if j['can_apply']]
        
        print(f"Found {len(jobs)} recent jobs")
        print(f"Eligible to apply: {len(eligible)}")
        
        if not eligible:
            print("\n❌ No eligible jobs to apply to currently")
            print("\nReasons for ineligibility:")
            ineligible = [j for j in jobs if not j['can_apply']]
            companies_seen = set()
            for job in ineligible[:5]:
                if job['company'] not in companies_seen:
                    print(f"  • {job['company']}: {job['apply_status']}")
                    companies_seen.add(job['company'])
            return
        
        # Apply to eligible jobs
        applications_sent = 0
        for job in eligible[:limit]:
            print(f"\n{applications_sent + 1}. {job['position']} at {job['company']}")
            print(f"   Posted: {job['hours_ago']} hours ago")
            print(f"   Location: {job.get('location', 'Not specified')}")
            
            if self.apply_to_job(job):
                applications_sent += 1
            
            if applications_sent >= limit:
                break
        
        print(f"\n✅ Prepared {applications_sent} applications")
        print("\nTo send: python3 send_prepared_applications.py")


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("🎯 LINKEDIN JOB APPLICATION MANAGER")
    print("=" * 60)
    
    manager = LinkedInApplicationManager()
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        # Just check eligible jobs
        jobs = manager.get_eligible_jobs()
        
        print("\n📋 Job Application Status:")
        print("-" * 40)
        
        can_apply = [j for j in jobs if j['can_apply']]
        cannot_apply = [j for j in jobs if not j['can_apply']]
        
        if can_apply:
            print(f"\n✅ Can Apply ({len(can_apply)} jobs):")
            for job in can_apply[:5]:
                print(f"  • {job['company']}: {job['position']}")
                print(f"    Posted {job['hours_ago']}h ago | {job['apply_status']}")
        
        if cannot_apply:
            print(f"\n❌ Cannot Apply ({len(cannot_apply)} jobs):")
            companies_seen = set()
            for job in cannot_apply[:5]:
                if job['company'] not in companies_seen:
                    print(f"  • {job['company']}: {job['apply_status']}")
                    companies_seen.add(job['company'])
    else:
        # Apply to jobs
        manager.smart_apply_batch(limit=3)
    
    print("\n✨ LinkedIn application manager complete!")

if __name__ == "__main__":
    main()