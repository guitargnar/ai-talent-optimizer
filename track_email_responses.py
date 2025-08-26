#!/usr/bin/env python3
"""
Email Response Tracker with Penalty System
Monitors all job-related emails and updates company penalties
"""

import sqlite3
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys

sys.path.append('/Users/matthewscott/Google Gmail')
sys.path.append('.')

from linkedin_job_scraper import LinkedInJobScraper

class EmailResponseTracker:
    """Tracks email responses and updates penalty system"""
    
    def __init__(self):
        self.scraper = LinkedInJobScraper()
        self.db_path = Path("unified_platform.db")
        self.gmail_path = Path('/Users/matthewscott/Google Gmail')
        
        # Company name patterns to detect in emails
        self.company_patterns = {
            'anthropic': 'Anthropic',
            'scale ai': 'Scale AI',
            'scale.ai': 'Scale AI',
            'scale.com': 'Scale AI',
            'meta': 'Meta',
            'facebook': 'Meta',
            'microsoft': 'Microsoft',
            'apple': 'Apple',
            'tesla': 'Tesla',
            'google': 'Google',
            'amazon': 'Amazon',
            'netflix': 'Netflix',
            'stripe': 'Stripe',
            'plaid': 'Plaid',
            'figma': 'Figma',
            'atlassian': 'Atlassian'
        }
        
        # Response type patterns
        self.response_patterns = {
            'rejection': [
                r'unfortunately',
                r'not moving forward',
                r'other candidates',
                r'not a match',
                r'decided to proceed',
                r'wish you success'
            ],
            'interview': [
                r'schedule.*interview',
                r'phone screen',
                r'technical interview',
                r'meet with',
                r'available for a call',
                r'discuss.*opportunity'
            ],
            'auto_reply': [
                r'received your application',
                r'thank you for applying',
                r'reviewing your application',
                r'auto-reply',
                r'do not reply'
            ]
        }
    
    def detect_company(self, email_content: str) -> Optional[str]:
        """Detect company from email content"""
        email_lower = email_content.lower()
        
        for pattern, company in self.company_patterns.items():
            if pattern in email_lower:
                return company
        
        return None
    
    def classify_response(self, email_content: str) -> str:
        """Classify the type of response"""
        email_lower = email_content.lower()
        
        for response_type, patterns in self.response_patterns.items():
            for pattern in patterns:
                if re.search(pattern, email_lower):
                    return response_type
        
        return 'unknown'
    
    def process_incoming_email(self, email_data: Dict):
        """Process an incoming email and update tracking"""
        
        # Detect company
        company = self.detect_company(
            f"{email_data.get('from', '')} {email_data.get('subject', '')} {email_data.get('body', '')}"
        )
        
        if not company:
            print(f"ℹ️ Could not detect company from email")
            return
        
        # Classify response
        response_type = self.classify_response(email_data.get('body', ''))
        
        # Track the email
        self.scraper.track_email({
            'direction': 'incoming',
            'email_from': email_data.get('from'),
            'email_to': email_data.get('to'),
            'subject': email_data.get('subject'),
            'body_preview': email_data.get('body', '')[:500],
            'company': company,
            'is_job_related': True,
            'requires_action': response_type == 'interview',
            'gmail_message_id': email_data.get('message_id')
        })
        
        # Update application tracking
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find most recent application to this company
        cursor.execute("""
        UPDATE applications
        SET response_received = 1,
            response_date = CURRENT_TIMESTAMP,
            response_type = ?
        WHERE rowid = (
            SELECT rowid FROM applications
            WHERE company = ?
            AND response_received = 0
            ORDER BY application_date DESC
            LIMIT 1
        )
        """, (response_type, company))
        
        # Update penalty system based on response
        if response_type == 'rejection':
            cursor.execute("""
            UPDATE company_penalties
            SET rejection_count = rejection_count + 1,
                penalty_score = penalty_score + 10,
                cooldown_days = 30,
                can_apply_after = datetime('now', '+30 days')
            WHERE company = ?
            """, (company,))
            print(f"❌ Rejection from {company} - 30 day cooldown applied")
            
        elif response_type == 'interview':
            cursor.execute("""
            UPDATE company_penalties
            SET penalty_score = MAX(penalty_score - 5, 0)
            WHERE company = ?
            """, (company,))
            print(f"✅ Interview request from {company}!")
            
        elif response_type == 'auto_reply':
            print(f"📧 Auto-acknowledgment from {company}")
        
        conn.commit()
        conn.close()
    
    def process_outgoing_email(self, email_data: Dict):
        """Track outgoing application email"""
        
        # Detect company from recipient
        company = self.detect_company(email_data.get('to', ''))
        
        if company:
            self.scraper.track_email({
                'direction': 'outgoing',
                'email_from': email_data.get('from'),
                'email_to': email_data.get('to'),
                'subject': email_data.get('subject'),
                'body_preview': email_data.get('body', '')[:500],
                'company': company,
                'is_job_related': True,
                'gmail_message_id': email_data.get('message_id')
            })
            print(f"📤 Tracked outgoing email to {company}")
    
    def check_for_no_responses(self):
        """Check for applications with no response and update penalties"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find applications older than 14 days with no response
        cursor.execute("""
        SELECT company, COUNT(*) as count
        FROM applications
        WHERE response_received = 0
        AND julianday('now') - julianday(applied_date) > 14
        GROUP BY company
        """)
        
        no_responses = cursor.fetchall()
        
        for company, count in no_responses:
            # Update penalty for no response
            cursor.execute("""
            UPDATE company_penalties
            SET no_response_count = ?,
                penalty_score = penalty_score + 2,
                cooldown_days = MIN(cooldown_days + 7, 30)
            WHERE company = ?
            """, (count, company))
            
            print(f"⏰ No response from {company} ({count} applications) - penalty increased")
        
        conn.commit()
        conn.close()
    
    def get_email_summary(self) -> Dict:
        """Get summary of email tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total emails tracked
        cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN direction = 'incoming' THEN 1 ELSE 0 END) as incoming,
            SUM(CASE WHEN direction = 'outgoing' THEN 1 ELSE 0 END) as outgoing
        FROM emails
        """)
        email_stats = cursor.fetchone()
        
        # Response statistics
        cursor.execute("""
        SELECT 
            response_type,
            COUNT(*) as count
        FROM applications
        WHERE response_received = 1
        GROUP BY response_type
        """)
        response_types = cursor.fetchall()
        
        # Companies with penalties
        cursor.execute("""
        SELECT company, penalty_score, cooldown_days, can_apply_after
        FROM company_penalties
        WHERE penalty_score > 0
        ORDER BY penalty_score DESC
        LIMIT 5
        """)
        penalties = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_emails': email_stats[0] or 0,
            'incoming': email_stats[1] or 0,
            'outgoing': email_stats[2] or 0,
            'response_types': dict(response_types) if response_types else {},
            'companies_with_penalties': penalties
        }
    
    def simulate_responses(self):
        """Simulate some email responses for testing"""
        print("\n🧪 Simulating email responses for testing...")
        
        test_emails = [
            {
                'from': 'recruiting@meta.com',
                'to': 'matthewdscott7@gmail.com',
                'subject': 'Thank you for your application',
                'body': 'We received your application for the ML Engineer position and are reviewing it.',
                'message_id': f'test_meta_{datetime.now().timestamp()}'
            },
            {
                'from': 'careers@microsoft.com',
                'to': 'matthewdscott7@gmail.com',
                'subject': 'Interview Request - Senior ML Engineer',
                'body': 'We would like to schedule an interview for the Azure AI position. Please let us know your availability.',
                'message_id': f'test_msft_{datetime.now().timestamp()}'
            },
            {
                'from': 'noreply@apple.com',
                'to': 'matthewdscott7@gmail.com',
                'subject': 'Application Update',
                'body': 'Unfortunately, we have decided to proceed with other candidates at this time.',
                'message_id': f'test_apple_{datetime.now().timestamp()}'
            }
        ]
        
        for email in test_emails:
            self.process_incoming_email(email)


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("📧 EMAIL RESPONSE TRACKER WITH PENALTY SYSTEM")
    print("=" * 60)
    
    tracker = EmailResponseTracker()
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--simulate':
        tracker.simulate_responses()
    
    # Check for no responses
    tracker.check_for_no_responses()
    
    # Get summary
    summary = tracker.get_email_summary()
    
    print("\n📊 Email Tracking Summary:")
    print(f"Total Emails: {summary['total_emails']}")
    print(f"  • Incoming: {summary['incoming']}")
    print(f"  • Outgoing: {summary['outgoing']}")
    
    if summary['response_types']:
        print("\n📨 Response Types:")
        for response_type, count in summary['response_types'].items():
            print(f"  • {response_type.title()}: {count}")
    
    if summary['companies_with_penalties']:
        print("\n⚠️ Companies with Penalties:")
        for company, score, cooldown, can_apply in summary['companies_with_penalties']:
            if can_apply:
                can_apply_date = datetime.fromisoformat(can_apply)
                days_left = (can_apply_date - datetime.now()).days
                print(f"  • {company}: Score {score:.1f}, {cooldown}d cooldown, {days_left}d remaining")
            else:
                print(f"  • {company}: Score {score:.1f}, {cooldown}d cooldown")
    
    print("\n✨ Email tracking complete!")
    print("\nNext steps:")
    print("1. Monitor: python3 track_email_responses.py")
    print("2. Apply: python3 apply_to_linkedin_jobs.py")
    print("3. Dashboard: python3 career_automation_dashboard.py")

if __name__ == "__main__":
    main()