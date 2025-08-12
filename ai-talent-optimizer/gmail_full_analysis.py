#!/usr/bin/env python3
"""
Gmail Full Analysis - Source of Truth for Job Applications
Analyzes ALL sent and received emails to determine true application status
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import pickle
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from typing import Dict, List, Tuple

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailApplicationAnalyzer:
    def __init__(self):
        self.service = None
        self.sent_applications = []
        self.received_responses = []
        self.bounced_emails = []
        self.company_status = defaultdict(dict)
        
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        token_path = 'token.pickle'
        
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Try multiple credential file locations
                cred_files = [
                    'credentials.json',
                    '/Users/matthewscott/Google Gmail/credentials.json',
                    '/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/credentials.json'
                ]
                
                flow = None
                for cred_file in cred_files:
                    if os.path.exists(cred_file):
                        flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
                        break
                
                if not flow:
                    print("❌ No credentials.json found. Please set up Gmail OAuth.")
                    return False
                    
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    def search_sent_applications(self):
        """Find all sent job applications"""
        print("\n📤 Searching SENT folder for job applications...")
        
        # Search queries for job applications
        queries = [
            'in:sent subject:(application OR resume OR "cover letter" OR position OR role OR engineer)',
            'in:sent to:(careers OR jobs OR recruiting OR hr OR talent)',
            'in:sent "attached resume"',
            'in:sent "I am writing to express"',
            'in:sent "I am excited to apply"'
        ]
        
        all_messages = set()
        
        for query in queries:
            try:
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=500
                ).execute()
                
                messages = results.get('messages', [])
                for msg in messages:
                    all_messages.add(msg['id'])
                    
            except Exception as e:
                print(f"Error with query '{query}': {e}")
        
        print(f"Found {len(all_messages)} potential job application emails")
        
        # Analyze each message
        for msg_id in all_messages:
            self._analyze_sent_message(msg_id)
        
        return len(self.sent_applications)
    
    def _analyze_sent_message(self, msg_id):
        """Analyze a sent message"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extract key information
            subject = ''
            to_email = ''
            date_sent = ''
            bcc = ''
            
            for header in headers:
                name = header['name'].lower()
                value = header['value']
                
                if name == 'subject':
                    subject = value
                elif name == 'to':
                    to_email = value
                elif name == 'date':
                    date_sent = value
                elif name == 'bcc':
                    bcc = value
            
            # Check if it's a job application
            if self._is_job_application(subject, to_email):
                company = self._extract_company_from_email(to_email)
                
                app_data = {
                    'company': company,
                    'to_email': to_email,
                    'subject': subject,
                    'date_sent': date_sent,
                    'bcc': bcc,
                    'message_id': msg_id
                }
                
                self.sent_applications.append(app_data)
                self.company_status[company]['sent'] = True
                self.company_status[company]['sent_date'] = date_sent
                self.company_status[company]['email_used'] = to_email
                
        except Exception as e:
            print(f"Error analyzing message {msg_id}: {e}")
    
    def search_received_responses(self):
        """Find all received responses to job applications"""
        print("\n📥 Searching INBOX for responses...")
        
        # Search for responses
        queries = [
            'subject:("thank you for applying" OR "application received" OR "we received your application")',
            'subject:(interview OR "next steps" OR "phone screen" OR "technical assessment")',
            'subject:("unfortunately" OR "we regret" OR "not moving forward" OR "other candidates")',
            'from:(careers OR jobs OR recruiting OR noreply OR donotreply)',
            '"Your application for"',
            '"We have received your application"'
        ]
        
        all_responses = set()
        
        for query in queries:
            try:
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=500
                ).execute()
                
                messages = results.get('messages', [])
                for msg in messages:
                    all_responses.add(msg['id'])
                    
            except Exception as e:
                print(f"Error with query '{query}': {e}")
        
        print(f"Found {len(all_responses)} potential response emails")
        
        # Analyze each response
        for msg_id in all_responses:
            self._analyze_received_message(msg_id)
        
        return len(self.received_responses)
    
    def _analyze_received_message(self, msg_id):
        """Analyze a received message"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extract key information
            subject = ''
            from_email = ''
            date_received = ''
            
            for header in headers:
                name = header['name'].lower()
                value = header['value']
                
                if name == 'subject':
                    subject = value
                elif name == 'from':
                    from_email = value
                elif name == 'date':
                    date_received = value
            
            # Get message body
            body = self._extract_body(message['payload'])
            
            # Categorize response
            response_type = self._categorize_response(subject, body)
            
            if response_type:
                company = self._extract_company_from_email(from_email)
                
                response_data = {
                    'company': company,
                    'from_email': from_email,
                    'subject': subject,
                    'date_received': date_received,
                    'type': response_type,
                    'body_preview': body[:200] if body else '',
                    'message_id': msg_id
                }
                
                self.received_responses.append(response_data)
                self.company_status[company]['response_received'] = True
                self.company_status[company]['response_type'] = response_type
                self.company_status[company]['response_date'] = date_received
                
        except Exception as e:
            print(f"Error analyzing response {msg_id}: {e}")
    
    def search_bounced_emails(self):
        """Find bounced emails"""
        print("\n❌ Searching for bounced emails...")
        
        queries = [
            'from:(mailer-daemon OR postmaster) subject:(undeliverable OR "delivery failed" OR "returned mail")',
            '"550 5.1.1"',  # User unknown
            '"mailbox unavailable"',
            '"address rejected"'
        ]
        
        for query in queries:
            try:
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=100
                ).execute()
                
                messages = results.get('messages', [])
                
                for msg in messages:
                    self._analyze_bounce(msg['id'])
                    
            except Exception as e:
                print(f"Error searching bounces: {e}")
        
        return len(self.bounced_emails)
    
    def _analyze_bounce(self, msg_id):
        """Analyze a bounce message"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id
            ).execute()
            
            body = self._extract_body(message['payload'])
            
            # Extract the failed email address
            email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
            emails = re.findall(email_pattern, body)
            
            for email in emails:
                if email not in ['matthewdscott7@gmail.com', 'mailer-daemon@googlemail.com']:
                    self.bounced_emails.append(email)
                    company = self._extract_company_from_email(email)
                    self.company_status[company]['bounced'] = True
                    
        except Exception as e:
            print(f"Error analyzing bounce: {e}")
    
    def _is_job_application(self, subject, to_email):
        """Check if email is likely a job application"""
        # Keywords in subject
        subject_keywords = ['application', 'resume', 'position', 'role', 'engineer', 
                          'developer', 'interest', 'opportunity']
        
        # Common job email patterns
        email_patterns = ['careers@', 'jobs@', 'recruiting@', 'hr@', 'talent@', 
                         'hiring@', 'opportunities@']
        
        subject_lower = subject.lower()
        to_lower = to_email.lower()
        
        # Check subject
        has_keyword = any(kw in subject_lower for kw in subject_keywords)
        
        # Check email pattern
        has_pattern = any(pattern in to_lower for pattern in email_patterns)
        
        return has_keyword or has_pattern
    
    def _extract_company_from_email(self, email):
        """Extract company name from email address"""
        # Extract domain
        match = re.search(r'@([\w\.-]+)', email)
        if match:
            domain = match.group(1)
            # Remove common suffixes
            company = domain.replace('.com', '').replace('.io', '').replace('.ai', '')
            company = company.replace('-', ' ').replace('_', ' ')
            return company.title()
        return 'Unknown'
    
    def _extract_body(self, payload):
        """Extract email body from payload"""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
        elif payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            
        return body
    
    def _categorize_response(self, subject, body):
        """Categorize the type of response"""
        text = (subject + ' ' + body).lower()
        
        # Interview invitation
        if any(word in text for word in ['interview', 'phone screen', 'technical assessment', 
                                         'next steps', 'schedule a call', 'meet with']):
            return 'INTERVIEW_INVITATION'
        
        # Rejection
        if any(phrase in text for phrase in ['unfortunately', 'we regret', 'not moving forward',
                                            'other candidates', 'not selected', 'unable to offer']):
            return 'REJECTION'
        
        # Automated acknowledgment
        if any(phrase in text for phrase in ['thank you for applying', 'application received',
                                            'we have received', 'application has been submitted']):
            return 'ACKNOWLEDGMENT'
        
        # Request for information
        if any(phrase in text for phrase in ['please provide', 'could you send', 
                                            'additional information']):
            return 'INFO_REQUEST'
        
        return None
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "="*60)
        print("📊 GMAIL ANALYSIS REPORT - SOURCE OF TRUTH")
        print("="*60)
        
        print(f"\n📤 SENT APPLICATIONS: {len(self.sent_applications)}")
        print("-"*40)
        
        # Show recent sent applications
        recent_sent = sorted(self.sent_applications, 
                           key=lambda x: x['date_sent'], 
                           reverse=True)[:10]
        
        for app in recent_sent:
            print(f"  • {app['company']}: {app['to_email']}")
            print(f"    Subject: {app['subject'][:50]}...")
            print(f"    Date: {app['date_sent']}")
            if app['bcc']:
                print(f"    BCC: {app['bcc']}")
            print()
        
        print(f"\n📥 RESPONSES RECEIVED: {len(self.received_responses)}")
        print("-"*40)
        
        # Categorize responses
        response_types = defaultdict(list)
        for resp in self.received_responses:
            response_types[resp['type']].append(resp)
        
        for resp_type, responses in response_types.items():
            print(f"\n  {resp_type}: {len(responses)}")
            for resp in responses[:5]:
                print(f"    • {resp['company']}: {resp['subject'][:50]}...")
        
        print(f"\n❌ BOUNCED EMAILS: {len(set(self.bounced_emails))}")
        print("-"*40)
        for email in set(self.bounced_emails)[:10]:
            print(f"  • {email}")
        
        print("\n📈 RESPONSE RATE ANALYSIS")
        print("-"*40)
        
        # Calculate metrics
        companies_applied = len(set(app['company'] for app in self.sent_applications))
        companies_responded = len(set(resp['company'] for resp in self.received_responses))
        
        if companies_applied > 0:
            response_rate = (companies_responded / companies_applied) * 100
            print(f"  • Companies Applied To: {companies_applied}")
            print(f"  • Companies Responded: {companies_responded}")
            print(f"  • Response Rate: {response_rate:.1f}%")
        
        # Interview rate
        interviews = [r for r in self.received_responses if r['type'] == 'INTERVIEW_INVITATION']
        if companies_applied > 0:
            interview_rate = (len(interviews) / companies_applied) * 100
            print(f"  • Interview Invitations: {len(interviews)}")
            print(f"  • Interview Rate: {interview_rate:.1f}%")
        
        print("\n🎯 COMPANIES NEEDING FOLLOW-UP")
        print("-"*40)
        
        # Find companies with no response
        no_response = []
        for company, status in self.company_status.items():
            if status.get('sent') and not status.get('response_received'):
                no_response.append(company)
        
        for company in no_response[:10]:
            print(f"  • {company}")
        
        # Save results to JSON
        results = {
            'analysis_date': datetime.now().isoformat(),
            'sent_count': len(self.sent_applications),
            'response_count': len(self.received_responses),
            'bounce_count': len(set(self.bounced_emails)),
            'companies_applied': companies_applied,
            'companies_responded': companies_responded,
            'interview_count': len(interviews),
            'response_rate': response_rate if companies_applied > 0 else 0,
            'sent_applications': self.sent_applications[:20],  # Sample
            'received_responses': self.received_responses[:20],  # Sample
            'bounced_emails': list(set(self.bounced_emails))
        }
        
        with open('gmail_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n✅ Full results saved to gmail_analysis_results.json")
        
        return results

def main():
    analyzer = GmailApplicationAnalyzer()
    
    print("🔍 Starting Gmail Analysis...")
    print("This will analyze your actual sent/received emails")
    print("-"*60)
    
    if not analyzer.authenticate():
        print("❌ Failed to authenticate with Gmail")
        return
    
    print("✅ Gmail authenticated successfully")
    
    # Analyze sent applications
    sent_count = analyzer.search_sent_applications()
    print(f"✅ Found {sent_count} sent applications")
    
    # Analyze received responses
    response_count = analyzer.search_received_responses()
    print(f"✅ Found {response_count} responses")
    
    # Check for bounces
    bounce_count = analyzer.search_bounced_emails()
    print(f"✅ Found {bounce_count} bounced emails")
    
    # Generate report
    results = analyzer.generate_report()
    
    # Update database with findings
    print("\n🔄 Updating database with findings...")
    update_database_with_results(results)
    
    print("\n✅ Analysis complete!")

def update_database_with_results(results):
    """Update the job tracking database with Gmail findings"""
    try:
        conn = sqlite3.connect('UNIFIED_AI_JOBS.db')
        cursor = conn.cursor()
        
        # Update response status for companies that responded
        for response in results.get('received_responses', []):
            company = response['company']
            response_type = response['type']
            
            if response_type == 'INTERVIEW_INVITATION':
                cursor.execute("""
                    UPDATE job_discoveries 
                    SET response_received = 1, 
                        interview_scheduled = 1,
                        notes = 'Interview invitation received via Gmail'
                    WHERE company LIKE ?
                """, (f'%{company}%',))
            elif response_type in ['REJECTION', 'ACKNOWLEDGMENT']:
                cursor.execute("""
                    UPDATE job_discoveries 
                    SET response_received = 1,
                        notes = ?
                    WHERE company LIKE ?
                """, (f'{response_type} received via Gmail', f'%{company}%',))
        
        conn.commit()
        print(f"✅ Updated {cursor.rowcount} database records")
        
    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()