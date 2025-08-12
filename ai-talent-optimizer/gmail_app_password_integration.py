#!/usr/bin/env python3
"""
Gmail Integration using App Password
Monitors job application responses and updates tracking
"""

import imaplib
import email
from email.header import decode_header
import json
import os
from datetime import datetime
import re

class GmailAppPasswordIntegration:
    def __init__(self):
        # Load credentials
        creds_file = os.path.expanduser('~/.gmail_job_tracker/credentials.json')
        with open(creds_file, 'r') as f:
            self.creds = json.load(f)
        
        self.email = self.creds['email']
        self.password = self.creds['app_password']
        self.monitored_companies = self.creds.get('monitored_companies', [])
        
    def connect(self):
        """Connect to Gmail using IMAP"""
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(self.email, self.password)
        self.mail.select('inbox')
        
    def search_job_responses(self, days_back=7):
        """Search for job application responses"""
        responses = []
        
        # Search for emails from monitored companies
        for company in self.monitored_companies:
            search_criteria = f'(FROM "{company}")'
            
            try:
                result, data = self.mail.search(None, search_criteria)
                email_ids = data[0].split()
                
                for email_id in email_ids[-10:]:  # Check last 10 emails
                    result, msg_data = self.mail.fetch(email_id, '(RFC822)')
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extract email details
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()
                    
                    from_email = msg.get("From")
                    date = msg.get("Date")
                    
                    # Classify response type
                    response_type = self.classify_response(subject, msg)
                    
                    responses.append({
                        'company': company,
                        'subject': subject,
                        'from': from_email,
                        'date': date,
                        'type': response_type,
                        'email_id': email_id.decode()
                    })
                    
            except Exception as e:
                print(f"Error searching {company}: {e}")
        
        return responses
    
    def classify_response(self, subject, msg):
        """Classify the type of response"""
        subject_lower = subject.lower()
        
        # Check for interview requests
        interview_keywords = ['interview', 'meeting', 'call', 'chat', 'conversation']
        if any(keyword in subject_lower for keyword in interview_keywords):
            return 'interview_request'
        
        # Check for rejections
        rejection_keywords = ['unfortunately', 'not moving forward', 'other candidates']
        if any(keyword in subject_lower for keyword in rejection_keywords):
            return 'rejection'
        
        # Check for next steps
        next_steps_keywords = ['next steps', 'assessment', 'test', 'exercise']
        if any(keyword in subject_lower for keyword in next_steps_keywords):
            return 'next_steps'
        
        # Auto-acknowledgment
        if 'received' in subject_lower or 'thank you for applying' in subject_lower:
            return 'auto_acknowledgment'
        
        return 'other'
    
    def generate_report(self):
        """Generate response tracking report"""
        self.connect()
        responses = self.search_job_responses()
        
        report = {
            'total_responses': len(responses),
            'interview_requests': sum(1 for r in responses if r['type'] == 'interview_request'),
            'rejections': sum(1 for r in responses if r['type'] == 'rejection'),
            'next_steps': sum(1 for r in responses if r['type'] == 'next_steps'),
            'auto_acknowledgments': sum(1 for r in responses if r['type'] == 'auto_acknowledgment'),
            'responses': responses
        }
        
        # Save report
        report_file = f"gmail_response_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Gmail Response Report")
        print(f"{'='*40}")
        print(f"Total Responses: {report['total_responses']}")
        print(f"Interview Requests: {report['interview_requests']}")
        print(f"Next Steps: {report['next_steps']}")
        print(f"Rejections: {report['rejections']}")
        print(f"Auto-acknowledgments: {report['auto_acknowledgments']}")
        print(f"\nReport saved to: {report_file}")
        
        self.mail.logout()
        return report

if __name__ == "__main__":
    print("🔍 Gmail Job Response Monitor")
    print("Using app password authentication")
    
    monitor = GmailAppPasswordIntegration()
    monitor.generate_report()