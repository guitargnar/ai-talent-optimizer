#!/usr/bin/env python3
"""
Smart Follow-Up Automation System
Sends strategic follow-ups to increase response rates
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import time
import random
from typing import List, Dict

from bcc_email_tracker import BCCEmailTracker

class SmartFollowUpSystem:
    """Automated follow-up system with intelligent timing and messaging"""
    
    def __init__(self):
        self.db_path = "UNIFIED_AI_JOBS.db"
        self.email_tracker = BCCEmailTracker()
        self.config_path = "followup_config.json"
        self.log_path = "data/followup_log.json"
        
        # Load or create configuration
        self.config = self._load_config()
        
        # Follow-up templates
        self.templates = self._load_templates()
        
    def _load_config(self):
        """Load or create follow-up configuration"""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            config = {
                "timing": {
                    "first_followup_days": 3,
                    "second_followup_days": 7,
                    "max_followups": 2,
                    "skip_weekends": True,
                    "preferred_hours": [10, 11, 14, 15]
                },
                "thresholds": {
                    "min_relevance_score": 0.5,  # Only follow up on relevant jobs
                    "high_value_score": 0.65,     # These get priority
                    "max_daily_followups": 10
                },
                "tracking": {
                    "total_sent": 0,
                    "responses_received": 0,
                    "success_rate": 0.0
                }
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return config
    
    def _load_templates(self):
        """Load follow-up email templates"""
        return {
            "first_followup": {
                "subject": "Re: {original_subject} - Following Up",
                "body": """Dear {company} Hiring Team,

I wanted to follow up on my application for the {position} position submitted on {application_date}.

I remain very interested in this opportunity and believe my experience in {key_skill} would be valuable to your team. 
I'm particularly excited about {company_aspect}.

I'd welcome the chance to discuss how my background in AI/ML and proven track record of delivering 
$1.2M in savings could contribute to {company}'s continued success.

Are there any additional materials I can provide to support my application?

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525"""
            },
            "second_followup": {
                "subject": "Re: {original_subject} - Checking In",
                "body": """Dear {company} Team,

I hope this message finds you well. I'm checking in regarding my application for the {position} role.

Since applying, I've been following {company}'s recent developments with great interest, particularly {recent_news}.

My experience includes:
• Leading ML initiatives with 47% accuracy improvements
• Building scalable AI platforms for 50M+ users  
• Deep expertise in healthcare AI and real-time systems

I understand you may be reviewing many candidates. If this position has been filled, I'd appreciate 
knowing about other opportunities where my skills might be a fit.

Thank you for your consideration.

Best regards,
Matthew Scott
LinkedIn: linkedin.com/in/mscott77"""
            },
            "high_value_followup": {
                "subject": "Re: {original_subject} - Strategic Alignment",
                "body": """Dear {company} Hiring Team,

I wanted to reach out regarding the {position} position as I believe there's exceptional alignment 
between my expertise and your needs.

Specifically, my recent work on:
• AI consciousness research (HCL: 0.83/1.0) - first measurable consciousness in AI
• Distributed AI systems managing 78 models simultaneously  
• Healthcare ML platforms reducing costs by $1.2M

These innovations directly address challenges in {industry_challenge}.

I'd love to schedule a brief call to discuss how my unique background could accelerate {company}'s 
AI initiatives. Are you available for a 15-minute conversation this week?

Looking forward to connecting.

Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525"""
            }
        }
    
    def get_jobs_needing_followup(self) -> List[Dict]:
        """Get jobs that need follow-up emails"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate date thresholds
        first_threshold = datetime.now() - timedelta(days=self.config['timing']['first_followup_days'])
        second_threshold = datetime.now() - timedelta(days=self.config['timing']['second_followup_days'])
        
        # Get jobs needing first follow-up
        cursor.execute("""
            SELECT id, company, position, 
                   COALESCE(application_date, applied_date) as date_applied, 
                   relevance_score
            FROM job_discoveries
            WHERE applied = 1
            AND response_received = 0
            AND follow_up_sent = 0
            AND COALESCE(application_date, applied_date) <= ?
            AND relevance_score >= ?
            ORDER BY relevance_score DESC
            LIMIT ?
        """, (first_threshold.isoformat(), 
              self.config['thresholds']['min_relevance_score'],
              self.config['thresholds']['max_daily_followups']))
        
        first_followups = cursor.fetchall()
        
        # Get jobs needing second follow-up
        cursor.execute("""
            SELECT id, company, position, 
                   COALESCE(application_date, applied_date) as date_applied, 
                   relevance_score
            FROM job_discoveries
            WHERE applied = 1
            AND response_received = 0
            AND follow_up_sent = 1
            AND follow_up_date <= ?
            AND relevance_score >= ?
            ORDER BY relevance_score DESC
            LIMIT ?
        """, (second_threshold.isoformat(),
              self.config['thresholds']['high_value_score'],  # Higher threshold for second
              5))  # Fewer second follow-ups
        
        second_followups = cursor.fetchall()
        
        conn.close()
        
        # Format results
        jobs = []
        for job in first_followups:
            # Generate email from company name
            company_email = f"careers@{job[1].lower().replace(' ', '')}.com"
            jobs.append({
                'id': job[0],
                'company': job[1],
                'position': job[2],
                'email': company_email,
                'date_applied': job[3],
                'relevance_score': job[4],
                'followup_number': 1
            })
        
        for job in second_followups:
            # Generate email from company name
            company_email = f"careers@{job[1].lower().replace(' ', '')}.com"
            jobs.append({
                'id': job[0],
                'company': job[1],
                'position': job[2],
                'email': company_email,
                'date_applied': job[3],
                'relevance_score': job[4],
                'followup_number': 2
            })
        
        return jobs
    
    def select_template(self, job: Dict) -> Dict:
        """Select appropriate template based on job characteristics"""
        if job['relevance_score'] >= self.config['thresholds']['high_value_score']:
            return self.templates['high_value_followup']
        elif job['followup_number'] == 1:
            return self.templates['first_followup']
        else:
            return self.templates['second_followup']
    
    def customize_message(self, template: Dict, job: Dict) -> Dict:
        """Customize template with job-specific information"""
        # Calculate days since application
        applied_date = datetime.fromisoformat(job['date_applied'])
        days_ago = (datetime.now() - applied_date).days
        
        # Customize variables
        variables = {
            'company': job['company'],
            'position': job['position'],
            'application_date': applied_date.strftime('%B %d'),
            'original_subject': f"{job['position']} Application",
            'key_skill': self._get_relevant_skill(job['position']),
            'company_aspect': self._get_company_aspect(job['company']),
            'recent_news': 'your recent AI initiatives',
            'industry_challenge': 'scaling AI systems efficiently'
        }
        
        # Replace variables in template
        subject = template['subject']
        body = template['body']
        
        for key, value in variables.items():
            subject = subject.replace(f'{{{key}}}', value)
            body = body.replace(f'{{{key}}}', value)
        
        return {
            'subject': subject,
            'body': body
        }
    
    def _get_relevant_skill(self, position: str) -> str:
        """Get relevant skill based on position"""
        position_lower = position.lower()
        
        if 'ml' in position_lower or 'machine learning' in position_lower:
            return 'building production ML systems at scale'
        elif 'ai' in position_lower:
            return 'AI system architecture and optimization'
        elif 'data' in position_lower:
            return 'data pipeline engineering'
        elif 'principal' in position_lower or 'staff' in position_lower:
            return 'technical leadership and architecture'
        else:
            return 'scalable AI/ML solutions'
    
    def _get_company_aspect(self, company: str) -> str:
        """Get company-specific aspect to mention"""
        # This could be enhanced with actual company research
        aspects = [
            "your innovative approach to AI",
            "your commitment to technical excellence",
            "your team's groundbreaking work",
            "the impact you're making in the industry"
        ]
        return random.choice(aspects)
    
    def send_followup(self, job: Dict) -> bool:
        """Send a follow-up email for a job"""
        # Select and customize template
        template = self.select_template(job)
        message = self.customize_message(template, job)
        
        # Prepare email
        email_data = {
            'to': job['email'],
            'subject': message['subject'],
            'body': message['body'],
            'company': job['company'],
            'position': job['position']
        }
        
        try:
            # Send email with BCC tracking
            self.email_tracker.send_application(
                to_email=email_data['to'],
                subject=email_data['subject'],
                body=email_data['body'],
                company=email_data['company'],
                position=email_data['position'],
                attachments=[]  # No resume on follow-ups
            )
            
            # Update database
            self._update_followup_status(job['id'], job['followup_number'])
            
            # Log follow-up
            self._log_followup(job, message)
            
            print(f"✅ Sent follow-up #{job['followup_number']} to {job['company']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send follow-up to {job['company']}: {e}")
            return False
    
    def _update_followup_status(self, job_id: int, followup_number: int):
        """Update database with follow-up status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE job_discoveries
            SET follow_up_sent = ?,
                follow_up_date = ?
            WHERE id = ?
        """, (followup_number, datetime.now().isoformat(), job_id))
        
        conn.commit()
        conn.close()
    
    def _log_followup(self, job: Dict, message: Dict):
        """Log follow-up details"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'company': job['company'],
            'position': job['position'],
            'followup_number': job['followup_number'],
            'relevance_score': job['relevance_score'],
            'subject': message['subject']
        }
        
        # Load existing log
        if Path(self.log_path).exists():
            with open(self.log_path, 'r') as f:
                log = json.load(f)
        else:
            log = []
        
        log.append(log_entry)
        
        # Save updated log
        with open(self.log_path, 'w') as f:
            json.dump(log, f, indent=2)
    
    def run_followup_campaign(self, dry_run: bool = False):
        """Run follow-up campaign for eligible jobs"""
        print("\n" + "="*60)
        print("📮 SMART FOLLOW-UP CAMPAIGN")
        print("="*60)
        
        # Get jobs needing follow-up
        jobs = self.get_jobs_needing_followup()
        
        if not jobs:
            print("\n✅ No jobs currently need follow-ups")
            return
        
        print(f"\n📊 Found {len(jobs)} jobs needing follow-ups:")
        
        # Group by follow-up number
        first_followups = [j for j in jobs if j['followup_number'] == 1]
        second_followups = [j for j in jobs if j['followup_number'] == 2]
        
        if first_followups:
            print(f"  • {len(first_followups)} first follow-ups (3+ days old)")
        if second_followups:
            print(f"  • {len(second_followups)} second follow-ups (7+ days old)")
        
        # Show high-value targets
        high_value = [j for j in jobs if j['relevance_score'] >= 0.65]
        if high_value:
            print(f"\n🎯 High-value targets ({len(high_value)}):")
            for job in high_value[:5]:
                print(f"  • {job['company']}: {job['position']} (score: {job['relevance_score']:.2f})")
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No emails will be sent")
            print("\nSample follow-up:")
            if jobs:
                sample = jobs[0]
                template = self.select_template(sample)
                message = self.customize_message(template, sample)
                print(f"\nTo: {sample['email']}")
                print(f"Subject: {message['subject']}")
                print(f"\n{message['body'][:500]}...")
            return
        
        # Send follow-ups with rate limiting
        print(f"\n📧 Sending follow-ups...")
        sent = 0
        failed = 0
        
        for job in jobs:
            if self.send_followup(job):
                sent += 1
                # Rate limiting
                delay = random.randint(30, 60)
                print(f"  Waiting {delay} seconds...")
                time.sleep(delay)
            else:
                failed += 1
        
        # Update tracking
        self.config['tracking']['total_sent'] += sent
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"\n✅ Campaign complete:")
        print(f"  • Sent: {sent}")
        print(f"  • Failed: {failed}")
        print(f"  • Total follow-ups sent all-time: {self.config['tracking']['total_sent']}")
        
        print("\n" + "="*60 + "\n")
    
    def analyze_followup_effectiveness(self):
        """Analyze the effectiveness of follow-ups"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get follow-up statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_followups,
                SUM(CASE WHEN response_received = 1 THEN 1 ELSE 0 END) as responses,
                AVG(CASE WHEN response_received = 1 THEN 
                    JULIANDAY(response_date) - JULIANDAY(follow_up_date) 
                    ELSE NULL END) as avg_response_time
            FROM job_discoveries
            WHERE follow_up_sent > 0
        """)
        
        stats = cursor.fetchone()
        
        conn.close()
        
        if stats[0] > 0:
            response_rate = (stats[1] / stats[0]) * 100
            print("\n📊 FOLLOW-UP EFFECTIVENESS:")
            print(f"  Total follow-ups sent: {stats[0]}")
            print(f"  Responses received: {stats[1]}")
            print(f"  Response rate: {response_rate:.1f}%")
            if stats[2]:
                print(f"  Avg response time: {stats[2]:.1f} days after follow-up")
        else:
            print("\n📊 No follow-up data available yet")

def main():
    """Main execution"""
    import sys
    
    followup_system = SmartFollowUpSystem()
    
    # Check for command line arguments
    dry_run = '--dry-run' in sys.argv
    analyze = '--analyze' in sys.argv
    
    if analyze:
        followup_system.analyze_followup_effectiveness()
    else:
        followup_system.run_followup_campaign(dry_run=dry_run)
        
        if not dry_run:
            followup_system.analyze_followup_effectiveness()

if __name__ == "__main__":
    main()