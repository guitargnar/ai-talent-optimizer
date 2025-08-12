#!/usr/bin/env python3
"""
Test Email Automation Configuration
Verify that email sending is properly configured
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_configuration():
    """Test if email configuration is working"""
    print("📧 Testing Email Automation Configuration")
    print("=" * 60)
    
    # Get credentials from environment
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_APP_PASSWORD')
    email_name = os.getenv('EMAIL_NAME', 'Matthew David Scott')
    
    # Check if credentials exist
    print("\n1️⃣ Checking Credentials:")
    if email_address:
        print(f"✅ Email Address: {email_address}")
    else:
        print("❌ EMAIL_ADDRESS not found in .env")
        return False
        
    if email_password:
        print(f"✅ App Password: {'*' * 12} (hidden)")
    else:
        print("❌ EMAIL_APP_PASSWORD not found in .env")
        return False
    
    print(f"✅ Email Name: {email_name}")
    
    # Test SMTP connection
    print("\n2️⃣ Testing SMTP Connection:")
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            print("✅ Connected to Gmail SMTP server")
            
            # Try to login
            server.login(email_address, email_password)
            print("✅ Successfully authenticated with Gmail")
            
            # Create test message
            print("\n3️⃣ Creating Test Message:")
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Career Automation Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            message["From"] = f"{email_name} <{email_address}>"
            message["To"] = email_address  # Send to self
            
            # Create message body
            text = f"""
Career Automation Email Test

This is a test email from your career automation system.

Test Details:
- Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Email System: Gmail SMTP
- Status: Working ✅

Your Contact Information:
- Email: matthewdscott7@gmail.com
- Phone: (502) 345-0525
- LinkedIn: linkedin.com/in/mscott77

If you received this email, your automation is configured correctly!

Best regards,
Matthew Scott
"""
            
            html = f"""
<html>
  <body>
    <h2>Career Automation Email Test</h2>
    <p>This is a test email from your career automation system.</p>
    
    <h3>Test Details:</h3>
    <ul>
      <li><strong>Date/Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
      <li><strong>Email System:</strong> Gmail SMTP</li>
      <li><strong>Status:</strong> Working ✅</li>
    </ul>
    
    <h3>Your Contact Information:</h3>
    <ul>
      <li><strong>Email:</strong> matthewdscott7@gmail.com</li>
      <li><strong>Phone:</strong> (502) 345-0525</li>
      <li><strong>LinkedIn:</strong> <a href="https://linkedin.com/in/mscott77">linkedin.com/in/mscott77</a></li>
    </ul>
    
    <p>If you received this email, your automation is configured correctly!</p>
    
    <p>Best regards,<br>
    Matthew Scott</p>
  </body>
</html>
"""
            
            # Add parts
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send test email
            print("\n4️⃣ Sending Test Email:")
            user_confirm = input("Send test email to yourself? (y/n): ")
            if user_confirm.lower() == 'y':
                server.send_message(message)
                print(f"✅ Test email sent to {email_address}")
                print("\n📬 Check your inbox for the test email!")
            else:
                print("⏭️  Skipped sending test email")
            
        print("\n✅ Email automation is properly configured!")
        print("\n💡 You can now use email automation for:")
        print("   - Automated follow-ups")
        print("   - Application confirmations")
        print("   - Interview scheduling")
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure 2-Factor Authentication is enabled on your Google account")
        print("2. Generate an app-specific password at: https://myaccount.google.com/apppasswords")
        print("3. Update EMAIL_APP_PASSWORD in your .env file")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_email_configuration()