#!/usr/bin/env python3
"""
Email Tester - Verify SMTP configuration and delivery
Tests email sending to verify configuration before any applications
"""

import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import time

class EmailTester:
    def __init__(self):
        """Initialize with credentials from .env"""
        load_dotenv()
        self.email = os.getenv('EMAIL_ADDRESS', '').strip()
        self.password = os.getenv('EMAIL_APP_PASSWORD', '').strip()
        
        if not self.email or not self.password:
            raise ValueError("EMAIL_ADDRESS and EMAIL_APP_PASSWORD must be set in .env file")
        
        print(f"✅ Loaded credentials for: {self.email}")
        print(f"✅ App password: {'*' * 12} (hidden)")
    
    def test_smtp_connection(self):
        """Test basic SMTP connection"""
        print("\n🔍 Testing SMTP Connection...")
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            print("✅ Connected to Gmail SMTP server")
            
            server.login(self.email, self.password)
            print("✅ Authentication successful")
            
            server.quit()
            print("✅ SMTP connection test passed")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            print("   Check your app password in .env file")
            return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def send_test_email(self, to_email=None):
        """Send a test email to verify delivery"""
        if to_email is None:
            to_email = self.email  # Send to self by default
        
        print(f"\n📧 Sending test email to: {to_email}")
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = f"Email Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            body = f"""
This is a test email from your AI Talent Optimizer system.

Test Details:
- Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- From: {self.email}
- To: {to_email}
- Purpose: Verify email delivery is working

If you received this email, your SMTP configuration is working correctly!

Next steps:
1. Check if this email went to spam
2. Reply to confirm receipt
3. We can proceed with fixing the application system
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email, self.password)
            
            text = msg.as_string()
            server.sendmail(self.email, to_email, text)
            server.quit()
            
            print("✅ Email sent successfully!")
            print("📬 Check your inbox (and spam folder)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def test_bcc(self):
        """Test BCC functionality"""
        print("\n🔍 Testing BCC functionality...")
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = self.email
            msg['Subject'] = f"BCC Test - {datetime.now().strftime('%H:%M:%S')}"
            
            # BCC address (won't appear in headers)
            bcc_email = f"{self.email.split('@')[0]}+bcctest@gmail.com"
            
            body = f"""
BCC Test Email

This email is sent to: {self.email}
With BCC to: {bcc_email}

If you receive this at both addresses, BCC is working.
Gmail '+' aliases should automatically route to your main inbox.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send to both To and BCC
            recipients = [self.email, bcc_email]
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email, self.password)
            server.sendmail(self.email, recipients, msg.as_string())
            server.quit()
            
            print(f"✅ BCC test sent")
            print(f"   To: {self.email}")
            print(f"   BCC: {bcc_email}")
            print("📬 Check if you received both copies")
            return True
            
        except Exception as e:
            print(f"❌ BCC test failed: {e}")
            return False
    
    def diagnose_issues(self):
        """Run full diagnostic suite"""
        print("=" * 60)
        print("🏥 EMAIL SYSTEM DIAGNOSTICS")
        print("=" * 60)
        
        results = {
            'credentials_loaded': False,
            'smtp_connection': False,
            'email_delivery': False,
            'bcc_working': False
        }
        
        # Check credentials
        results['credentials_loaded'] = bool(self.email and self.password)
        
        # Test SMTP
        if results['credentials_loaded']:
            results['smtp_connection'] = self.test_smtp_connection()
        
        # Test email delivery
        if results['smtp_connection']:
            results['email_delivery'] = self.send_test_email()
            time.sleep(2)  # Brief pause between tests
            results['bcc_working'] = self.test_bcc()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC RESULTS")
        print("=" * 60)
        
        for test, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test:20} : {status}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if not results['credentials_loaded']:
            print("1. Check .env file has EMAIL_ADDRESS and EMAIL_APP_PASSWORD")
            print("2. Generate app password at: https://myaccount.google.com/apppasswords")
        elif not results['smtp_connection']:
            print("1. Verify app password is correct (not your regular password)")
            print("2. Check 2-factor authentication is enabled")
            print("3. Ensure 'Less secure app access' is handled via app password")
        elif not results['email_delivery']:
            print("1. Check spam filters")
            print("2. Verify email address is correct")
            print("3. Check Gmail sending limits (500/day)")
        else:
            print("✅ Email system is working! You can send applications.")
        
        return all(results.values())

def main():
    """Run email tests"""
    print("🚀 AI TALENT OPTIMIZER - EMAIL TESTER")
    print("=" * 60)
    
    try:
        tester = EmailTester()
        
        # Run diagnostics
        all_tests_passed = tester.diagnose_issues()
        
        if all_tests_passed:
            print("\n🎉 SUCCESS: Email system is fully operational!")
            print("You can now send job applications.")
        else:
            print("\n⚠️  WARNING: Email system has issues that need fixing.")
            print("Fix the issues above before sending applications.")
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("Fix this error before proceeding.")
        return 1
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    exit(main())