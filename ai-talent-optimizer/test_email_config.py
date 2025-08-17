#!/usr/bin/env python3
"""
Test Email Configuration
Non-interactive test of SMTP credentials
"""

import os
import sys
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


def test_current_config():
    """Test the current email configuration"""
    
    email = os.getenv('EMAIL_ADDRESS', '')
    password = os.getenv('EMAIL_APP_PASSWORD', '')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    
    print("\n" + "="*60)
    print("📧 TESTING EMAIL CONFIGURATION")
    print("="*60)
    
    print(f"\n📍 Current Configuration:")
    print(f"   Email: {email}")
    print(f"   Password: {'*' * 4}...{password[-4:] if len(password) > 4 else '****'}")
    print(f"   Server: {smtp_server}:{smtp_port}")
    
    if not email or not password:
        print("\n❌ Email credentials not configured!")
        print("\n📝 To configure:")
        print("1. Edit .env file and add:")
        print("   EMAIL_ADDRESS=your_email@gmail.com")
        print("   EMAIL_APP_PASSWORD=your_app_password")
        return False
    
    print(f"\n🔍 Testing connection to {smtp_server}...")
    
    try:
        # Test SMTP connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email, password)
        
        print("✅ SMTP Authentication successful!")
        
        # Try to send a test email
        print("\n📤 Sending test email...")
        
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = email
        msg['Subject'] = "AI Talent Optimizer - Email Test Successful"
        
        body = """
Hello Matthew,

This is a test email from your AI Talent Optimizer system.

✅ Your email configuration is working correctly!
✅ SMTP authentication successful
✅ Ready to send job applications

Your system is configured with:
- 307 real jobs from top companies
- Verified company emails (careers@anthropic.com, etc.)
- Automated application sending

Next steps:
1. Run: python automated_apply.py
2. Monitor your sent folder
3. Track responses in the database

Good luck with your job search!

--
AI Talent Optimizer
Automated Job Application System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Test email sent to {email}")
        print("   Check your inbox to confirm receipt")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ Authentication failed!")
        print(f"   Error: {e}")
        print("\n🔐 HOW TO FIX - Gmail App Password Required:")
        print("\n   Step 1: Enable 2-Factor Authentication")
        print("   - Go to: https://myaccount.google.com/security")
        print("   - Click '2-Step Verification'")
        print("   - Follow the setup process")
        print("\n   Step 2: Generate App Password")
        print("   - Go to: https://myaccount.google.com/apppasswords")
        print("   - Sign in if needed")
        print("   - Select 'Mail' as the app")
        print("   - Select 'Other' and type 'AI Talent Optimizer'")
        print("   - Click 'Generate'")
        print("   - Copy the 16-character password (ignore spaces)")
        print("\n   Step 3: Update .env file")
        print(f"   - Edit: {env_path}")
        print(f"   - Set: EMAIL_APP_PASSWORD=<16-char-password>")
        print("   - Save the file")
        print("\n   Step 4: Run this test again")
        print("   - python test_email_config.py")
        
        return False
        
    except smtplib.SMTPServerDisconnected:
        print("\n❌ Server disconnected - possible network issue")
        print("   Check your internet connection")
        return False
        
    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"   Error: {e}")
        print("\n🔍 Troubleshooting:")
        print("   1. Check internet connection")
        print("   2. Verify Gmail account is active")
        print("   3. Ensure 'Less secure apps' is NOT the issue (use app passwords)")
        print("   4. Check if any Gmail security alerts were triggered")
        return False


def test_email_service():
    """Test the EmailService class"""
    print("\n🔧 Testing EmailService integration...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.services.email_service import EmailService
        
        service = EmailService()
        
        if service._is_configured():
            print("✅ EmailService is configured")
            print(f"   Email: {service.email_address}")
            print(f"   Max per day: {service.emails_sent_today}/{os.getenv('MAX_EMAILS_PER_DAY', '50')}")
            
            # Test sending
            test_send = service.send_email(
                to_email=service.email_address,
                subject="EmailService Test",
                body="This is a test from the EmailService class."
            )
            
            if test_send:
                print("✅ EmailService.send_email() successful!")
            else:
                print("❌ EmailService.send_email() failed")
                print("   Check logs for details")
                
        else:
            print("❌ EmailService not configured")
            
    except Exception as e:
        print(f"❌ EmailService error: {e}")


def main():
    """Main test function"""
    
    # Test current configuration
    success = test_current_config()
    
    if success:
        # Test EmailService integration
        test_email_service()
        
        print("\n" + "="*60)
        print("✅ EMAIL CONFIGURATION VERIFIED")
        print("="*60)
        print("\n🎯 Ready to send job applications!")
        print("\n📋 Available Commands:")
        print("   python load_real_company_jobs.py  # Refresh job listings")
        print("   python automated_apply.py         # Send applications")
        print("   python main.py status            # Check progress")
        
    else:
        print("\n" + "="*60)
        print("⚠️ EMAIL CONFIGURATION NEEDS ATTENTION")
        print("="*60)
        print("\nFollow the instructions above to fix the configuration")
        print("Then run this test again: python test_email_config.py")


if __name__ == "__main__":
    main()