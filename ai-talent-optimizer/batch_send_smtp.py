#!/usr/bin/env python3
"""Batch send using SMTP - bypasses OAuth issues"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import time
import json
from datetime import datetime
import hashlib

# Priority companies
COMPANIES = [
    ("Stripe", "recruiting@stripe.com", "Principal ML Engineer"),
    ("Uber", "recruiting@uber.com", "Staff AI Engineer"),
    ("Airbnb", "careers@airbnb.com", "Staff Software Engineer"),
    ("LinkedIn", "staffing@linkedin.com", "Principal Engineer"),
    ("Spotify", "careers@spotify.com", "Staff Backend Engineer"),
    ("Square", "jobs@squareup.com", "Principal Software Engineer"),
    ("Databricks", "careers@databricks.com", "Staff ML Platform Engineer"),
    ("Salesforce", "careers@salesforce.com", "Principal Architect"),
    ("Adobe", "careers@adobe.com", "Principal ML Scientist"),
    ("PayPal", "recruiting@paypal.com", "Principal AI Engineer"),
]

def load_credentials():
    """Load email credentials from .env"""
    env_path = "/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/.env"
    creds = {}
    
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    creds[key] = val.strip('"').strip("'")
    
    return creds.get('EMAIL_ADDRESS'), creds.get('EMAIL_APP_PASSWORD')

def send_application(company, email, position, smtp_server, from_email):
    """Send single application"""
    tracking_id = hashlib.md5(f"{company}{datetime.now()}".encode()).hexdigest()[:12]
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = email
    msg['Bcc'] = "matthewdscott7+jobapps@gmail.com"
    msg['Subject'] = f"{position} Application - Matthew Scott"
    
    body = f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {position} role at {company}.

With 10+ years at Fortune 50 Humana, I've delivered transformative results:
• $1.2M+ annual savings through AI automation
• Built platform with 117 Python modules processing 1M+ records daily
• Maintained zero critical defects across 1,000+ deployments
• Architected AI orchestration system managing 89 specialized models

My unique value proposition combines deep enterprise healthcare experience with cutting-edge AI implementation skills, making me ideally suited to drive innovation at {company}.

I'm particularly excited about {company}'s technical challenges and believe my proven track record of scaling AI systems would add immediate value to your team.

Resume attached. Available for immediate discussion.

Best regards,
Matthew Scott
(502) 345-0525
matthewdscott7@gmail.com
linkedin.com/in/mscott77
github.com/guitargnar"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach resume
    resume_path = "/Users/matthewscott/AI-ML-Portfolio/MATTHEW_SCOTT_RESUME_2025.pdf"
    if os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="MATTHEW_SCOTT_RESUME_2025.pdf"')
            msg.attach(part)
    
    # Send
    smtp_server.send_message(msg)
    
    # Track in BCC log
    log_file = "/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/data/bcc_tracking_log.json"
    if os.path.exists(log_file):
        with open(log_file) as f:
            data = json.load(f)
    else:
        data = {"sent_emails": {}}
    
    data["sent_emails"][tracking_id] = {
        "to": email,
        "company": company,
        "position": position,
        "sent_date": datetime.now().isoformat(),
        "subject": msg['Subject']
    }
    
    with open(log_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return tracking_id

def main():
    print("🚀 BATCH SMTP SENDER")
    print("=" * 50)
    
    email, password = load_credentials()
    if not email or not password:
        print("❌ No credentials found in .env")
        return
    
    print(f"📧 Using: {email}")
    print(f"📎 Resume: MATTHEW_SCOTT_RESUME_2025.pdf")
    print("=" * 50)
    
    # Connect to SMTP
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        print("✅ SMTP connected\n")
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return
    
    sent = 0
    for company, company_email, position in COMPANIES:
        print(f"📧 [{sent + 1}/{len(COMPANIES)}] {company}")
        print(f"   Position: {position}")
        
        try:
            tracking = send_application(company, company_email, position, server, email)
            print(f"   ✅ SENT! Tracking: {tracking}")
            sent += 1
            
            if sent < len(COMPANIES):
                print(f"   ⏱️  Waiting 15 seconds...")
                time.sleep(15)
                
        except Exception as e:
            print(f"   ❌ Failed: {str(e)[:50]}")
    
    server.quit()
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {sent}/{len(COMPANIES)} sent")
    print(f"📧 Total applications: {sent + 20}")
    print("📬 Check matthewdscott7+jobapps@gmail.com for copies")

if __name__ == "__main__":
    main()