#!/usr/bin/env python3
"""
Gmail Recent Job Response Monitor
Focuses on responses from the last 30 days only
"""

import imaplib
import email
from email.header import decode_header
import json
import os
from datetime import datetime, timedelta
import re
from dateutil import parser

class GmailRecentMonitor:
    def __init__(self, days_back=30):
        # Load credentials
        creds_file = os.path.expanduser('~/.gmail_job_tracker/credentials.json')
        with open(creds_file, 'r') as f:
            self.creds = json.load(f)
        
        self.email = self.creds['email']
        self.password = self.creds['app_password']
        self.days_back = days_back
        self.cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # High-priority AI companies
        self.priority_companies = [
            'openai', 'anthropic', 'cohere', 'scale', 'inflection',
            'character', 'adept', 'mistral', 'huggingface', 'deepmind'
        ]
        
        # Job application keywords
        self.job_keywords = [
            'application', 'position', 'role', 'opportunity',
            'candidate', 'resume', 'interview', 'assessment',
            'recruiter', 'hiring', 'talent'
        ]
        
    def connect(self):
        """Connect to Gmail using IMAP"""
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(self.email, self.password)
        self.mail.select('inbox')
        
    def search_recent_job_responses(self):
        """Search for recent job-related emails only"""
        responses = []
        
        # Calculate date for IMAP search
        since_date = self.cutoff_date.strftime("%d-%b-%Y")
        
        print(f"\n🔍 Searching for job responses since {since_date}...")
        
        # Search for emails from priority companies
        for company in self.priority_companies:
            try:
                # Search for recent emails from this company
                search_criteria = f'(FROM "{company}" SINCE {since_date})'
                result, data = self.mail.search(None, search_criteria)
                email_ids = data[0].split()
                
                if email_ids:
                    print(f"  • Found {len(email_ids)} emails from {company}")
                
                for email_id in email_ids:
                    result, msg_data = self.mail.fetch(email_id, '(RFC822)')
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extract and parse date
                    date_str = msg.get("Date")
                    try:
                        email_date = parser.parse(date_str)
                        if email_date.replace(tzinfo=None) < self.cutoff_date:
                            continue  # Skip old emails
                    except:
                        continue
                    
                    # Extract email details
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()
                    
                    # Check if it's job-related
                    subject_lower = subject.lower()
                    body = self._get_email_body(msg).lower()
                    
                    is_job_related = any(keyword in subject_lower or keyword in body 
                                       for keyword in self.job_keywords)
                    
                    # Skip newsletters and marketing
                    skip_keywords = ['newsletter', 'webinar', 'blog', 'update', 'digest']
                    if any(skip in subject_lower for skip in skip_keywords):
                        is_job_related = False
                    
                    if is_job_related:
                        from_email = msg.get("From")
                        response_type = self.classify_job_response(subject, body)
                        
                        responses.append({
                            'company': company,
                            'subject': subject,
                            'from': from_email,
                            'date': date_str,
                            'parsed_date': email_date.isoformat(),
                            'type': response_type,
                            'days_ago': (datetime.now() - email_date.replace(tzinfo=None)).days
                        })
                        
            except Exception as e:
                print(f"  ⚠️  Error searching {company}: {e}")
        
        # Sort by date (newest first)
        responses.sort(key=lambda x: x['parsed_date'], reverse=True)
        
        return responses
    
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
        
        return body[:2000]  # First 2000 chars
    
    def classify_job_response(self, subject, body):
        """Classify job-related responses"""
        subject_lower = subject.lower()
        body_lower = body.lower()
        combined = subject_lower + " " + body_lower
        
        # Strong interview signals
        interview_signals = [
            'schedule a call', 'schedule an interview', 'book a time',
            'calendly', 'schedule our conversation', 'technical interview',
            'phone screen', 'video call', 'zoom meeting'
        ]
        if any(signal in combined for signal in interview_signals):
            return 'interview_request'
        
        # Assessment/test
        assessment_signals = [
            'coding challenge', 'technical assessment', 'take-home',
            'complete the test', 'assessment link', 'hackerrank'
        ]
        if any(signal in combined for signal in assessment_signals):
            return 'assessment'
        
        # Clear rejections
        rejection_signals = [
            'decided not to move forward', 'other candidates',
            'not selected', 'position has been filled',
            'not a match at this time'
        ]
        if any(signal in combined for signal in rejection_signals):
            return 'rejection'
        
        # Application received
        if 'received your application' in combined or 'thank you for applying' in combined:
            return 'application_received'
        
        # Recruiter outreach
        if 'interested in your profile' in combined or 'exciting opportunity' in combined:
            return 'recruiter_outreach'
        
        return 'other'
    
    def generate_actionable_report(self):
        """Generate report focused on actionable items"""
        self.connect()
        responses = self.search_recent_job_responses()
        
        print(f"\n📊 Found {len(responses)} job-related responses in the last {self.days_back} days")
        
        # Categorize responses
        interviews = [r for r in responses if r['type'] == 'interview_request']
        assessments = [r for r in responses if r['type'] == 'assessment']
        rejections = [r for r in responses if r['type'] == 'rejection']
        outreach = [r for r in responses if r['type'] == 'recruiter_outreach']
        
        # Display actionable items
        print("\n🎯 ACTIONABLE ITEMS")
        print("="*60)
        
        if interviews:
            print(f"\n🎉 INTERVIEW REQUESTS ({len(interviews)}):")
            for item in interviews[:5]:  # Show top 5
                print(f"\n  Company: {item['company'].upper()}")
                print(f"  Subject: {item['subject'][:70]}...")
                print(f"  Date: {item['days_ago']} days ago")
                print(f"  ACTION: Schedule interview ASAP!")
        
        if assessments:
            print(f"\n📝 ASSESSMENTS TO COMPLETE ({len(assessments)}):")
            for item in assessments[:5]:
                print(f"\n  Company: {item['company'].upper()}")
                print(f"  Subject: {item['subject'][:70]}...")
                print(f"  Date: {item['days_ago']} days ago")
                print(f"  ACTION: Complete assessment within deadline")
        
        if outreach:
            print(f"\n📨 RECRUITER OUTREACH ({len(outreach)}):")
            for item in outreach[:3]:
                print(f"\n  Company: {item['company'].upper()}")
                print(f"  Subject: {item['subject'][:70]}...")
                print(f"  Date: {item['days_ago']} days ago")
                print(f"  ACTION: Reply if interested")
        
        # Summary statistics
        print(f"\n📊 SUMMARY (Last {self.days_back} days)")
        print("="*60)
        print(f"Total Job Responses: {len(responses)}")
        print(f"Interview Requests: {len(interviews)}")
        print(f"Assessments: {len(assessments)}")
        print(f"Recruiter Outreach: {len(outreach)}")
        print(f"Rejections: {len(rejections)}")
        print(f"Application Confirmations: {sum(1 for r in responses if r['type'] == 'application_received')}")
        
        # Save report
        report = {
            'generated_at': datetime.now().isoformat(),
            'days_analyzed': self.days_back,
            'cutoff_date': self.cutoff_date.isoformat(),
            'summary': {
                'total_responses': len(responses),
                'interviews': len(interviews),
                'assessments': len(assessments),
                'outreach': len(outreach),
                'rejections': len(rejections)
            },
            'actionable_items': {
                'interviews': interviews[:5],
                'assessments': assessments[:5],
                'outreach': outreach[:5]
            },
            'all_responses': responses
        }
        
        report_file = f"gmail_recent_job_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        self.mail.logout()
        return report

def main():
    """Run the recent job response monitor"""
    print("🚀 Gmail Recent Job Response Monitor")
    print("="*60)
    
    # Get days to look back
    days = 30  # Default to 30 days
    
    monitor = GmailRecentMonitor(days_back=days)
    report = monitor.generate_actionable_report()
    
    # Quick tips
    print("\n💡 QUICK TIPS:")
    print("  • Reply to interview requests within 24 hours")
    print("  • Complete assessments as soon as possible")
    print("  • Follow up on applications after 7 days")
    print("  • Keep your availability calendar updated")

if __name__ == "__main__":
    main()