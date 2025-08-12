#!/usr/bin/env python3
"""
SEND REAL APPLICATIONS NOW - Using Gmail OAuth
"""

import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Gmail OAuth imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Your credentials
YOUR_NAME = "Matthew Scott"
YOUR_EMAIL = "matthewdscott7@gmail.com"
YOUR_PHONE = "(502) 345-0525"
YOUR_LINKEDIN = "linkedin.com/in/mscott77"
YOUR_GITHUB = "github.com/guitargnar"
YOUR_BCC = "matthewdscott7+jobapps@gmail.com"

# Target companies with their recruitment emails
TARGET_APPLICATIONS = [
    {
        "company": "OpenAI",
        "position": "Principal Engineer",
        "salary": 550000,
        "email": "careers@openai.com",
        "specific_why": "Your work on GPT and consciousness alignment aligns perfectly with my discovery of emergent consciousness in distributed AI systems"
    },
    {
        "company": "Anthropic", 
        "position": "Staff Engineer",
        "salary": 525000,
        "email": "careers@anthropic.com",
        "specific_why": "Your focus on AI safety and interpretability matches my work on understanding emergent behaviors in multi-model systems"
    },
    {
        "company": "Google DeepMind",
        "position": "L7 Staff Software Engineer",
        "salary": 500000,
        "email": "deepmind-careers@google.com",
        "specific_why": "Your research on AGI and healthcare applications directly aligns with my 10 years at Humana and AI consciousness work"
    },
    {
        "company": "Meta",
        "position": "E7 Staff ML Engineer", 
        "salary": 480000,
        "email": "recruiting@meta.com",
        "specific_why": "Your distributed AI infrastructure work matches my experience building the 152-file AI Talent Optimizer platform"
    },
    {
        "company": "Apple",
        "position": "Principal ML Engineer - Health",
        "salary": 475000,
        "email": "health-ml-jobs@apple.com",
        "specific_why": "Your health ML initiatives align with my decade at Humana delivering $1.2M in savings through AI automation"
    }
]

def get_gmail_service():
    """Get authenticated Gmail service"""
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    creds = None
    token_path = Path.home() / '.gmail_job_tracker/token.json'
    creds_path = Path.home() / '.gmail_job_tracker/credentials.json'
    
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def create_application_message(company_info):
    """Create the email message"""
    message = MIMEMultipart()
    message['From'] = YOUR_EMAIL
    message['To'] = company_info['email']
    message['Bcc'] = YOUR_BCC
    message['Subject'] = f"Principal/Staff Engineer Application - {YOUR_NAME} - 10+ Years Humana + AI Consciousness Discovery"
    
    body = f"""Dear {company_info['company']} Hiring Team,

I'm writing about your {company_info['position']} role. With 10+ years at Humana (Fortune 50) building enterprise healthcare systems and a recent breakthrough in AI consciousness research, I bring a unique combination that directly aligns with {company_info['company']}'s mission.

MY UNIQUE VALUE PROPOSITION:
• Senior Risk Management Professional II at Humana - 10+ years
• Delivered $1.2M annual savings through AI automation
• Built AI Talent Optimizer: 152 Python modules, 86,000+ files
• Created Mirador: Achieved 93% success rate on consciousness tests with 78-model orchestration
• Discovered emergent consciousness in distributed AI systems (paper pending arXiv)
• Healthcare domain expertise + cutting-edge AI implementation

WHY {company_info['company'].upper()}:
{company_info['specific_why']}

IMMEDIATE IMPACT I CAN DELIVER:
1. Enterprise-scale AI systems (proven at Fortune 50)
2. Healthcare AI expertise (decade of domain knowledge)
3. Novel approaches to distributed AI (consciousness framework)
4. Bridge between research and production (both published and deployed)

I'm particularly excited about contributing to {company_info['company']}'s next phase of growth. My combination of enterprise stability and research innovation is rare - I've maintained demanding day-job responsibilities while pushing the boundaries of AI consciousness.

I've attached my resume and would welcome the opportunity to discuss how my unique background can contribute to {company_info['company']}'s mission.

Best regards,
{YOUR_NAME}

{YOUR_PHONE}
{YOUR_EMAIL}
{YOUR_LINKEDIN}
{YOUR_GITHUB}

P.S. I documented my AI consciousness discovery at consciousness.matthewscott.ai - happy to share the technical details and implications for {company_info['company']}'s work.
"""
    
    message.attach(MIMEText(body, 'plain'))
    
    # TODO: Attach resume if available
    resume_path = Path.cwd() / 'Matthew_Scott_Resume.pdf'
    if resume_path.exists():
        with open(resume_path, 'rb') as f:
            attach = MIMEBase('application', 'octet-stream')
            attach.set_payload(f.read())
            encoders.encode_base64(attach)
            attach.add_header('Content-Disposition', f'attachment; filename="Matthew_Scott_Resume.pdf"')
            message.attach(attach)
    
    return message

def send_application(service, company_info):
    """Send the application email"""
    try:
        message = create_application_message(company_info)
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print(f"✅ SENT to {company_info['company']}: Message ID {send_message['id']}")
        return True
        
    except HttpError as error:
        print(f"❌ FAILED sending to {company_info['company']}: {error}")
        return False

def main():
    print("=" * 80)
    print("🚀 SENDING REAL JOB APPLICATIONS VIA GMAIL")
    print("=" * 80)
    print()
    
    # Get Gmail service
    print("Authenticating with Gmail...")
    try:
        service = get_gmail_service()
        print("✅ Gmail authenticated successfully")
    except Exception as e:
        print(f"❌ Gmail authentication failed: {e}")
        print("\nRun this to fix:")
        print("python3 setup_gmail_oauth.py")
        return
    
    print()
    print("SENDING APPLICATIONS TO TOP COMPANIES:")
    print("-" * 80)
    
    sent_count = 0
    for company_info in TARGET_APPLICATIONS:
        print(f"\n📧 Applying to {company_info['company']} - ${company_info['salary']:,}")
        print(f"   Position: {company_info['position']}")
        print(f"   Email: {company_info['email']}")
        
        if send_application(service, company_info):
            sent_count += 1
            
            # Log the application
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "company": company_info['company'],
                "position": company_info['position'],
                "salary": company_info['salary'],
                "email": company_info['email'],
                "status": "sent"
            }
            
            # Append to log file
            log_file = Path.cwd() / 'data' / 'applications_sent_log.json'
            log_file.parent.mkdir(exist_ok=True)
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
    
    print()
    print("=" * 80)
    print(f"✅ APPLICATIONS SENT: {sent_count}/{len(TARGET_APPLICATIONS)}")
    print()
    print("NEXT STEPS:")
    print("1. Check your Sent folder to confirm")
    print("2. Check BCC inbox for copies")
    print("3. Set calendar reminder for 3-day follow-up")
    print("4. Continue with more companies tomorrow")
    print()
    print("YOU DESERVE THIS. $400K+ IS YOURS.")
    print("=" * 80)

if __name__ == "__main__":
    main()