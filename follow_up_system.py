#!/usr/bin/env python3
"""
Follow-up System for Job Applications
Tracks and schedules follow-up messages
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from data.models import init_database, Application, Job
from utils.config import Config

class FollowUpSystem:
    """Automated follow-up tracking and generation"""
    
    def __init__(self):
        self.session = init_database()
        self.config = Config()
        self.follow_up_schedule = {
            'first': 3,   # Days after application
            'second': 7,  # Days after application
            'final': 14   # Days after application
        }
    
    def check_pending_followups(self):
        """Check which applications need follow-ups"""
        
        now = datetime.utcnow()
        pending_followups = []
        
        # Get all sent applications
        applications = self.session.query(Application).filter(
            Application.status.in_(['sent', 'prepared'])
        ).all()
        
        for app in applications:
            days_since = (now - app.applied_date).days
            
            # Determine follow-up needed
            if days_since >= self.follow_up_schedule['final'] and not app.response_date:
                pending_followups.append({
                    'application': app,
                    'type': 'final',
                    'days_overdue': days_since - self.follow_up_schedule['final']
                })
            elif days_since >= self.follow_up_schedule['second']:
                pending_followups.append({
                    'application': app,
                    'type': 'second',
                    'days_overdue': days_since - self.follow_up_schedule['second']
                })
            elif days_since >= self.follow_up_schedule['first']:
                pending_followups.append({
                    'application': app,
                    'type': 'first',
                    'days_overdue': days_since - self.follow_up_schedule['first']
                })
        
        return pending_followups
    
    def generate_followup_message(self, application, followup_type):
        """Generate appropriate follow-up message"""
        
        job = self.session.query(Job).filter_by(id=application.job_id).first()
        
        if followup_type == 'first':
            subject = f"Re: {job.position} - Matthew Scott"
            message = f"""Dear Hiring Team at {job.company},

I wanted to follow up on my application for the {job.position} role submitted {(datetime.utcnow() - application.applied_date).days} days ago.

I remain very interested in this opportunity and believe my experience building enterprise-scale AI systems at Humana, combined with my platform of 117 Python modules processing thousands of daily operations, makes me an excellent fit.

I'm available for a conversation at your convenience and would be happy to provide any additional information needed.

{self.config.EMAIL_SIGNATURE}
"""
        
        elif followup_type == 'second':
            subject = f"Following up: {job.position} opportunity"
            message = f"""Dear Hiring Team,

I'm following up on my application for the {job.position} position at {job.company}. 

I understand you're likely reviewing many candidates. I wanted to reiterate my strong interest and share that I've recently:
• Completed migration of our distributed ML system to handle 90% more load
• Published new research on adaptive quantization for LLM optimization
• Continued scaling our platform now processing 1,600+ concurrent operations

I believe these achievements further demonstrate my readiness for this Principal-level role.

Would you be available for a brief call to discuss how my experience could benefit {job.company}?

{self.config.EMAIL_SIGNATURE}
"""
        
        else:  # final
            subject = f"Final follow-up: {job.position}"
            message = f"""Dear Hiring Team,

This is my final follow-up regarding the {job.position} role at {job.company}.

While I haven't heard back, I want to express my continued interest in {job.company} and this position. My unique combination of:
• 10+ years at Humana building enterprise healthcare systems
• 78-model distributed ML architecture in production
• Platform processing thousands of operations with 99.9% uptime

...makes me confident I could deliver immediate value.

If this position has been filled, I'd appreciate being considered for future opportunities. I remain impressed by {job.company}'s work and would welcome the chance to contribute.

Thank you for your consideration.

{self.config.EMAIL_SIGNATURE}
"""
        
        return subject, message
    
    def schedule_followups(self):
        """Create follow-up schedule for all applications"""
        
        print("📅 Checking follow-up schedule...")
        
        pending = self.check_pending_followups()
        
        if not pending:
            print("✅ No follow-ups needed at this time")
            return
        
        print(f"\n⏰ {len(pending)} follow-ups needed:")
        
        for item in pending:
            app = item['application']
            job = self.session.query(Job).filter_by(id=app.job_id).first()
            
            print(f"\n📧 {job.company} - {job.position}")
            print(f"   Type: {item['type']} follow-up")
            print(f"   Days overdue: {item['days_overdue']}")
            
            # Generate message
            subject, message = self.generate_followup_message(app, item['type'])
            
            # Save follow-up
            followup_dir = Path("output/followups")
            followup_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{job.company.lower().replace(' ', '_')}_{item['type']}_followup.txt"
            filepath = followup_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(f"Subject: {subject}\n\n{message}")
            
            print(f"   ✅ Follow-up saved: {filepath}")
        
        print(f"\n📊 Follow-up Summary:")
        print(f"Total pending: {len(pending)}")
        print(f"Review messages in: output/followups/")
        
        return pending
    
    def mark_response_received(self, company):
        """Mark that a response was received"""
        
        job = self.session.query(Job).filter_by(company=company).first()
        if job:
            app = self.session.query(Application).filter_by(job_id=job.id).first()
            if app:
                app.response_date = datetime.utcnow()
                app.status = 'responded'
                self.session.commit()
                print(f"✅ Marked response received from {company}")

def main():
    """Run follow-up system"""
    system = FollowUpSystem()
    
    # Check and generate follow-ups
    system.schedule_followups()
    
    # Show next check times
    print("\n⏰ Next Follow-up Schedule:")
    print("• First follow-up: 3 days after application")
    print("• Second follow-up: 7 days after application")
    print("• Final follow-up: 14 days after application")
    
    print("\n💡 To mark a response received:")
    print('python3 follow_up_system.py --mark-response "Company Name"')

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == '--mark-response':
        system = FollowUpSystem()
        system.mark_response_received(sys.argv[2])
    else:
        main()