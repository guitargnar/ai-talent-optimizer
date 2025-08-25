#!/usr/bin/env python3
"""
Test email configuration to verify SMTP credentials work
"""

import smtplib
import os
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_config():
    """Test if email credentials are working"""
    
    # Load .env
    env_path = Path(__file__).parent / ".env"
    config = {}
    
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    config[key] = val.strip('"').strip("'")
    
    email = config.get('EMAIL_ADDRESS')
    password = config.get('EMAIL_APP_PASSWORD')
    
    if not email or not password:
        print("❌ Email credentials not found in .env")
        return False
    
    print(f"✅ Found email: {email}")
    print(f"✅ Found password: {'*' * len(password)}")
    
    # Test SMTP connection
    try:
        print("\n📧 Testing SMTP connection...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email, password)
            print("✅ SMTP authentication successful!")
            
            # Send test email to self
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = email
            msg['Subject'] = "Test from AI Talent Optimizer v2.0"
            
            body = """This is a test email from your AI Talent Optimizer v2.0.
            
If you receive this, your email configuration is working correctly!

Platform Status:
- Quality-first applications: ENABLED
- Human-in-the-loop: ACTIVE
- Personalization engine: READY
            
This test was sent to verify SMTP credentials."""
            
            msg.attach(MIMEText(body, 'plain'))
            
            server.send_message(msg)
            print("✅ Test email sent successfully to your inbox!")
            print(f"   Check {email} for the test message")
            
            return True
            
    except Exception as e:
        print(f"❌ SMTP error: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("EMAIL CONFIGURATION TEST")
    print("="*60)
    
    if test_email_config():
        print("\n✅ Email system is ready for quality applications!")
    else:
        print("\n❌ Email configuration needs attention")
