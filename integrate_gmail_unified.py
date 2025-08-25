#!/usr/bin/env python3
"""
Integrate Gmail monitoring with Unified AI Hunter system
Improves response classification and connects to unified database
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from gmail_app_password_integration import GmailAppPasswordIntegration

class ImprovedGmailIntegration(GmailAppPasswordIntegration):
    """Enhanced Gmail integration with better classification"""
    
    def __init__(self):
        super().__init__()
        self.unified_db_path = "UNIFIED_AI_JOBS.db"
        
    def classify_response(self, subject, msg):
        """Improved response classification"""
        subject_lower = subject.lower()
        
        # Get email body for better classification
        body = self._get_email_body(msg).lower() if hasattr(self, '_get_email_body') else ""
        
        # Model access grants are not interviews
        if 'access granted' in subject_lower or 'model access' in subject_lower:
            return 'other'
        
        # Real interview indicators
        interview_strong = [
            'schedule', 'calendar', 'availability', 'zoom', 'teams',
            'technical interview', 'phone screen', 'hiring manager',
            'recruiter', 'would you be available'
        ]
        if any(indicator in subject_lower or indicator in body for indicator in interview_strong):
            return 'interview_request'
        
        # Weaker interview signals
        interview_weak = ['interview', 'meeting', 'call', 'chat', 'conversation']
        interview_context = ['position', 'role', 'opportunity', 'application']
        
        if any(weak in subject_lower for weak in interview_weak):
            if any(context in subject_lower or context in body for context in interview_context):
                return 'interview_request'
        
        # Clear rejections
        rejection_keywords = [
            'unfortunately', 'not moving forward', 'other candidates',
            'not selected', 'decided to proceed', 'not a match',
            'pursue other', 'position has been filled'
        ]
        if any(keyword in subject_lower or keyword in body for keyword in rejection_keywords):
            return 'rejection'
        
        # Next steps (assessments, tests)
        next_steps_keywords = [
            'next steps', 'assessment', 'test', 'exercise',
            'coding challenge', 'take-home', 'complete the following'
        ]
        if any(keyword in subject_lower or keyword in body for keyword in next_steps_keywords):
            return 'next_steps'
        
        # Auto-acknowledgments
        acknowledgment_keywords = [
            'received your application', 'thank you for applying',
            'application has been received', 'confirm receipt',
            'successfully submitted'
        ]
        if any(keyword in subject_lower or keyword in body for keyword in acknowledgment_keywords):
            return 'auto_acknowledgment'
        
        return 'other'
    
    def _get_email_body(self, msg):
        """Extract email body text"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode()
            except:
                pass
        
        return body[:1000]  # First 1000 chars for classification
    
    def sync_with_unified_db(self, responses):
        """Sync Gmail responses with unified database"""
        if not os.path.exists(self.unified_db_path):
            print(f"Warning: Unified database not found at {self.unified_db_path}")
            return
        
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        # Create response tracking table if not exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gmail_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT UNIQUE,
            company TEXT,
            subject TEXT,
            from_email TEXT,
            received_date TEXT,
            response_type TEXT,
            processed_date TEXT DEFAULT CURRENT_TIMESTAMP,
            linked_application_id INTEGER
        )
        ''')
        
        # Insert new responses
        new_responses = 0
        for response in responses:
            try:
                cursor.execute('''
                INSERT OR IGNORE INTO gmail_responses 
                (email_id, company, subject, from_email, received_date, response_type)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    response['email_id'],
                    response['company'],
                    response['subject'],
                    response['from'],
                    response['date'],
                    response['type']
                ))
                
                if cursor.rowcount > 0:
                    new_responses += 1
                    
                    # Try to link to application
                    if response['type'] in ['interview_request', 'next_steps', 'rejection']:
                        cursor.execute('''
                        UPDATE unified_applications 
                        SET status = ?, response_date = ?, response_type = ?
                        WHERE company = ? AND response_date IS NULL
                        ORDER BY applied_date DESC
                        LIMIT 1
                        ''', (
                            'responded',
                            response['date'],
                            response['type'],
                            response['company']
                        ))
                        
            except Exception as e:
                print(f"Error processing response: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Synced {new_responses} new responses to unified database")
        
    def generate_actionable_report(self):
        """Generate report with actionable insights"""
        self.connect()
        responses = self.search_job_responses()
        
        # Separate by response type
        interviews = [r for r in responses if r['type'] == 'interview_request']
        next_steps = [r for r in responses if r['type'] == 'next_steps']
        rejections = [r for r in responses if r['type'] == 'rejection']
        
        print("\n🎯 ACTIONABLE ITEMS")
        print("="*50)
        
        if interviews:
            print(f"\n🎉 INTERVIEW REQUESTS ({len(interviews)}):")
            for interview in interviews:
                print(f"  • {interview['company'].upper()}: {interview['subject'][:60]}...")
                print(f"    From: {interview['from']}")
                print(f"    Date: {interview['date']}")
                print(f"    ACTION: Reply within 24 hours with availability\n")
        
        if next_steps:
            print(f"\n📋 NEXT STEPS REQUIRED ({len(next_steps)}):")
            for step in next_steps:
                print(f"  • {step['company'].upper()}: {step['subject'][:60]}...")
                print(f"    Date: {step['date']}")
                print(f"    ACTION: Complete assessment/test ASAP\n")
        
        if not interviews and not next_steps:
            print("\n⏳ No immediate actions required")
            print("Continue with daily application routine")
        
        # Sync with unified database
        self.sync_with_unified_db(responses)
        
        # Save detailed report
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_responses': len(responses),
            'interview_requests': len(interviews),
            'next_steps': len(next_steps),
            'rejections': len(rejections),
            'auto_acknowledgments': sum(1 for r in responses if r['type'] == 'auto_acknowledgment'),
            'actionable_items': {
                'interviews': interviews,
                'next_steps': next_steps
            },
            'all_responses': responses
        }
        
        report_file = f"gmail_actionable_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        self.mail.logout()
        return report

def main():
    """Run improved Gmail integration"""
    print("🚀 Enhanced Gmail Job Response Monitor")
    print("="*50)
    
    monitor = ImprovedGmailIntegration()
    report = monitor.generate_actionable_report()
    
    print("\n📊 SUMMARY STATISTICS")
    print("="*50)
    print(f"Total Emails Scanned: {report['total_responses']}")
    print(f"Interview Requests: {report['interview_requests']}")
    print(f"Next Steps: {report['next_steps']}")
    print(f"Rejections: {report['rejections']}")
    print(f"Auto-acknowledgments: {report['auto_acknowledgments']}")
    
    # Integration status
    if os.path.exists("UNIFIED_AI_JOBS.db"):
        print("\n✅ Unified database integration: ACTIVE")
    else:
        print("\n⚠️  Unified database not found - run consolidate_systems.py first")

if __name__ == "__main__":
    main()