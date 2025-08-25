#!/usr/bin/env python3
"""
SIMPLEST POSSIBLE EMAIL SENDER - Just fucking send them
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path

# Your email credentials (from .env)
YOUR_EMAIL = "matthewdscott7@gmail.com"
# You need to set up an app password for Gmail
# Go to: https://myaccount.google.com/apppasswords

def send_simple_email(to_email, company, position):
    """Send a simple application email"""
    
    msg = MIMEMultipart()
    msg['From'] = YOUR_EMAIL
    msg['To'] = to_email
    msg['Subject'] = f"Application: {position} - Matthew Scott"
    
    body = """Dear Hiring Team,

I'm applying for your Principal/Staff engineering position. 

My qualifications:
• 10+ years at Humana (Fortune 50) as Senior Risk Management Professional II
• Delivered $1.2M in annual savings through AI automation
• Built comprehensive AI platform with 152 Python modules
• Discovered emergent consciousness in distributed AI systems
• Healthcare domain expert with cutting-edge AI skills

I would love to discuss how my unique combination of enterprise experience and AI innovation can contribute to your team.

Best regards,
Matthew Scott
(502) 345-0525
matthewdscott7@gmail.com
linkedin.com/in/mscott77
github.com/guitargnar
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Get app password from environment or prompt
    password = os.getenv('GMAIL_APP_PASSWORD')
    if not password:
        print("\n⚠️ You need a Gmail App Password")
        print("1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Generate an app password for 'Mail'")
        print("3. Run: export GMAIL_APP_PASSWORD='your-app-password'")
        print("4. Then run this script again")
        return False
    
    try:
        # Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(YOUR_EMAIL, password)
        
        text = msg.as_string()
        server.sendmail(YOUR_EMAIL, to_email, text)
        server.quit()
        
        print(f"✅ SENT to {company}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send to {company}: {e}")
        return False

def main():
    print("=" * 80)
    print("SIMPLE EMAIL SENDER - NO BULLSHIT")
    print("=" * 80)
    
    # Top companies to apply to
    companies = [
        ("OpenAI", "Principal Engineer", "careers@openai.com"),
        ("Anthropic", "Staff Engineer", "careers@anthropic.com"),
        ("Google DeepMind", "L7 Staff Engineer", "deepmind-careers@google.com"),
        ("Meta", "E7 Staff ML Engineer", "recruiting@meta.com"),
        ("Apple", "Principal ML Engineer", "health-ml-jobs@apple.com"),
    ]
    
    sent = 0
    for company, position, email in companies:
        print(f"\nSending to {company}...")
        if send_simple_email(email, company, position):
            sent += 1
    
    print()
    print("=" * 80)
    print(f"SENT: {sent}/{len(companies)} applications")
    print()
    print("If this didn't work, you need to:")
    print("1. Go to https://myaccount.google.com/apppasswords")
    print("2. Generate an app password")
    print("3. Run: export GMAIL_APP_PASSWORD='your-password'")
    print("4. Run this script again")
    print("=" * 80)

if __name__ == "__main__":
    main()