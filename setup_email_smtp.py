#!/usr/bin/env python3
"""
SMTP Email Configuration Setup and Test
Helps configure and test email credentials for job applications
"""

import os
import sys
import smtplib
import getpass
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv, set_key

# Load existing .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


def test_gmail_connection(email, password):
    """Test Gmail SMTP connection"""
    try:
        print(f"\n📧 Testing Gmail SMTP connection...")
        print(f"   Email: {email}")
        print(f"   Server: smtp.gmail.com:587")
        
        # Create SMTP connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        
        print("✅ Successfully connected to Gmail SMTP!")
        
        # Send test email to yourself
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = email
        msg['Subject'] = "Test: AI Talent Optimizer Email Setup Successful"
        
        body = """
        🎉 Congratulations! Your email is configured correctly.
        
        The AI Talent Optimizer can now send job applications on your behalf.
        
        Next steps:
        1. Run: python automated_apply.py
        2. Monitor applications in the database
        3. Check your sent folder for confirmation
        
        Good luck with your job search!
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Test email sent successfully! Check your inbox.")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed!")
        print("\n🔐 Gmail App Password Required:")
        print("   1. Go to: https://myaccount.google.com/apppasswords")
        print("   2. Sign in to your Google account")
        print("   3. Select 'Mail' as the app")
        print("   4. Select your device type")
        print("   5. Click 'Generate'")
        print("   6. Copy the 16-character password (no spaces)")
        print("\n   Note: You need 2-factor authentication enabled")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def setup_outlook_connection(email, password):
    """Test Outlook/Hotmail SMTP connection"""
    try:
        print(f"\n📧 Testing Outlook SMTP connection...")
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        server.login(email, password)
        server.quit()
        print("✅ Successfully connected to Outlook SMTP!")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def update_env_file(email, password, provider='gmail'):
    """Update .env file with credentials"""
    
    # Determine SMTP settings based on provider
    if provider == 'gmail':
        smtp_server = 'smtp.gmail.com'
        smtp_port = '587'
    elif provider == 'outlook':
        smtp_server = 'smtp-mail.outlook.com'
        smtp_port = '587'
    else:
        smtp_server = input("Enter SMTP server: ")
        smtp_port = input("Enter SMTP port: ")
    
    # Update .env file
    set_key(env_path, 'EMAIL_ADDRESS', email)
    set_key(env_path, 'EMAIL_APP_PASSWORD', password)
    set_key(env_path, 'SMTP_SERVER', smtp_server)
    set_key(env_path, 'SMTP_PORT', smtp_port)
    
    print(f"\n✅ Updated .env file with credentials")


def main():
    """Main setup function"""
    
    print("\n" + "="*60)
    print("🔧 SMTP EMAIL CONFIGURATION SETUP")
    print("="*60)
    
    # Check current configuration
    current_email = os.getenv('EMAIL_ADDRESS', '')
    current_password = os.getenv('EMAIL_APP_PASSWORD', '')
    
    if current_email and current_password:
        print(f"\n📍 Current configuration found:")
        print(f"   Email: {current_email}")
        print(f"   Password: {'*' * len(current_password[:4])}...")
        
        test_current = input("\nTest current configuration? (y/n): ").lower()
        if test_current == 'y':
            if test_gmail_connection(current_email, current_password):
                print("\n✅ Current configuration works! You're all set.")
                return
            else:
                print("\n⚠️ Current configuration failed. Let's update it.")
    
    # Setup new configuration
    print("\n📝 Email Provider Setup")
    print("1. Gmail (recommended)")
    print("2. Outlook/Hotmail")
    print("3. Other")
    
    choice = input("\nSelect provider (1-3): ")
    
    if choice == '1':
        provider = 'gmail'
        print("\n📱 Gmail Setup Instructions:")
        print("1. Enable 2-factor authentication on your Google account")
        print("2. Generate an app-specific password:")
        print("   - Go to: https://myaccount.google.com/apppasswords")
        print("   - Select 'Mail' and your device")
        print("   - Copy the 16-character password\n")
        
    elif choice == '2':
        provider = 'outlook'
        print("\n📱 Outlook Setup Instructions:")
        print("1. Enable 2-factor authentication")
        print("2. Generate an app password:")
        print("   - Go to: https://account.microsoft.com/security")
        print("   - Click 'Advanced security options'")
        print("   - Under 'App passwords', create a new one\n")
    else:
        provider = 'other'
    
    # Get credentials
    email = input("Enter your email address: ").strip()
    if not email:
        email = current_email or 'matthewdscott7@gmail.com'
        print(f"Using: {email}")
    
    password = getpass.getpass("Enter your app password (hidden): ").strip()
    if not password and current_password:
        use_current = input("Use current password? (y/n): ").lower()
        if use_current == 'y':
            password = current_password
    
    # Test connection
    if provider == 'gmail':
        success = test_gmail_connection(email, password)
    elif provider == 'outlook':
        success = setup_outlook_connection(email, password)
    else:
        print("⚠️ Manual configuration required for other providers")
        success = True
    
    if success:
        # Update .env file
        save = input("\nSave these credentials to .env? (y/n): ").lower()
        if save == 'y':
            update_env_file(email, password, provider)
            
            print("\n" + "="*60)
            print("✅ EMAIL SETUP COMPLETE!")
            print("="*60)
            print("\n🎯 Next Steps:")
            print("1. Run: python load_real_company_jobs.py  # Get latest jobs")
            print("2. Run: python automated_apply.py        # Send applications")
            print("3. Check: python main.py status          # Monitor progress")
            
            # Test if we can import and use the email service
            print("\n🔍 Testing email service integration...")
            try:
                sys.path.insert(0, str(Path(__file__).parent))
                from src.services.email_service import EmailService
                
                # Reload settings to get new credentials
                from importlib import reload
                from src.config import settings as settings_module
                reload(settings_module)
                
                service = EmailService()
                print("✅ Email service ready to use!")
                
            except Exception as e:
                print(f"⚠️ Email service test failed: {e}")
                print("   You may need to restart your Python session")
    else:
        print("\n❌ Setup failed. Please check your credentials and try again.")
        print("\nTroubleshooting:")
        print("- Make sure you're using an app password, not your regular password")
        print("- Ensure 2-factor authentication is enabled")
        print("- Check that 'Less secure app access' is not needed (use app passwords instead)")


if __name__ == "__main__":
    main()