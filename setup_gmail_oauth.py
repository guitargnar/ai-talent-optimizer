#!/usr/bin/env python3
"""
Setup Gmail OAuth with App Password
This script helps configure Gmail integration for job application tracking
"""

import os
import json
import base64
from datetime import datetime

def setup_gmail_app_password():
    """Configure Gmail with app password for job tracking"""
    
    print("🔐 Gmail App Password Setup for Job Application Tracking")
    print("="*60)
    
    # Get user email
    email = input("Enter your Gmail address: ").strip()
    
    # App password (user should paste the one they just generated)
    print("\nPaste your 16-character app password (spaces will be removed automatically)")
    app_password = input("App password: ").strip().replace(" ", "")
    
    if len(app_password) != 16:
        print("❌ Error: App password should be exactly 16 characters (excluding spaces)")
        return False
    
    # Create credentials file
    credentials = {
        "email": email,
        "app_password": app_password,
        "created_at": datetime.now().isoformat(),
        "purpose": "AI Job Application Tracking",
        "monitored_companies": [
            "openai", "anthropic", "google", "meta", "apple",
            "cohere", "scale", "inflection", "character", "adept",
            "microsoft", "amazon", "nvidia", "huggingface", "mistral",
            "stability", "databricks", "palantir", "tesla", "netflix"
        ]
    }
    
    # Save credentials securely
    credentials_dir = os.path.expanduser("~/.gmail_job_tracker")
    os.makedirs(credentials_dir, exist_ok=True)
    
    credentials_file = os.path.join(credentials_dir, "credentials.json")
    
    # Set restrictive permissions before writing
    if not os.path.exists(credentials_file):
        open(credentials_file, 'a').close()
    os.chmod(credentials_file, 0o600)  # Read/write for owner only
    
    with open(credentials_file, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"\n✅ Credentials saved to: {credentials_file}")
    
    # Create quick test script
    test_script = """#!/usr/bin/env python3
import imaplib
import json
import os

# Load credentials
with open(os.path.expanduser('~/.gmail_job_tracker/credentials.json'), 'r') as f:
    creds = json.load(f)

# Test connection
try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(creds['email'], creds['app_password'])
    mail.select('inbox')
    
    # Search for job-related emails
    result, data = mail.search(None, 'UNSEEN', 'OR', 
        'FROM', '"noreply"', 
        'FROM', '"careers"'
    )
    
    email_ids = data[0].split()
    print(f"✅ Connection successful!")
    print(f"📧 Found {len(email_ids)} unread job-related emails")
    
    mail.logout()
except Exception as e:
    print(f"❌ Connection failed: {e}")
"""
    
    test_file = "test_gmail_connection.py"
    with open(test_file, 'w') as f:
        f.write(test_script)
    os.chmod(test_file, 0o755)
    
    print(f"\n📝 Test script created: {test_file}")
    print("\nTo test your Gmail connection, run:")
    print(f"  python {test_file}")
    
    # Update gmail_oauth_integration.py to use app password
    update_integration = input("\nUpdate gmail_oauth_integration.py to use app password? (y/n): ")
    
    if update_integration.lower() == 'y':
        update_gmail_integration_file(email, app_password)
    
    print("\n🎉 Gmail setup complete!")
    print("\nNext steps:")
    print("1. Run the test script to verify connection")
    print("2. Run gmail_oauth_integration.py to start monitoring responses")
    print("3. The system will automatically track responses from monitored companies")
    
    return True

def update_gmail_integration_file(email, app_password):
    """Update the gmail_oauth_integration.py file to use app password"""
    
    integration_update = f'''#!/usr/bin/env python3
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
            search_criteria = f'(FROM "{{company}}")'
            
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
                        'email_id': email_id.decode() if isinstance(email_id, bytes) else email_id
                    })
                    
            except Exception as e:
                print(f"Error searching {{company}}: {{e}}")
        
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
        report_file = f"gmail_response_report_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\\n📊 Gmail Response Report")
        print(f"{{'='*40}}")
        print(f"Total Responses: {{report['total_responses']}}")
        print(f"Interview Requests: {{report['interview_requests']}}")
        print(f"Next Steps: {{report['next_steps']}}")
        print(f"Rejections: {{report['rejections']}}")
        print(f"Auto-acknowledgments: {{report['auto_acknowledgments']}}")
        print(f"\\nReport saved to: {{report_file}}")
        
        self.mail.logout()
        return report

if __name__ == "__main__":
    print("🔍 Gmail Job Response Monitor")
    print("Using app password authentication")
    
    monitor = GmailAppPasswordIntegration()
    monitor.generate_report()
'''
    
    # Save updated integration file
    integration_file = "gmail_app_password_integration.py"
    with open(integration_file, 'w') as f:
        f.write(integration_update)
    os.chmod(integration_file, 0o755)
    
    print(f"\n✅ Created new integration file: {integration_file}")

if __name__ == "__main__":
    setup_gmail_app_password()