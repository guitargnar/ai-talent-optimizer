#!/usr/bin/env python3
"""
Quick Setup for Email Automation System
Run this to configure everything needed for email tracking
"""

import os
import sys
from pathlib import Path

def setup_email_automation():
    print("🚀 Email Automation Setup")
    print("=" * 60)
    
    # Check for .env file
    if not Path('.env').exists():
        print("\n⚠️  No .env file found!")
        print("\nCreating .env template...")
        
        env_template = """# Email Configuration
EMAIL_ADDRESS=matthewdscott7@gmail.com
EMAIL_APP_PASSWORD=your-16-char-app-password
EMAIL_NAME=Matthew David Scott

# Optional
BACKUP_EMAIL=your.backup@email.com
"""
        
        with open('.env', 'w') as f:
            f.write(env_template)
        
        print("✅ Created .env template")
        print("\n⚠️  IMPORTANT: Add your Gmail app password to .env")
        print("\nTo get app password:")
        print("1. Enable 2FA at: https://myaccount.google.com/security")
        print("2. Generate app password at: https://myaccount.google.com/apppasswords")
        return False
    
    # Test email configuration
    print("\n🧪 Testing email configuration...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        email = os.getenv('EMAIL_ADDRESS')
        password = os.getenv('EMAIL_APP_PASSWORD')
        
        if not password or password == 'your-16-char-app-password':
            print("❌ Email app password not configured in .env")
            return False
        
        print(f"✅ Email: {email}")
        print("✅ App password: ******* (hidden)")
        
        # Test imports
        print("\n📦 Checking dependencies...")
        try:
            import smtplib
            import ssl
            from email.mime.text import MIMEText
            print("✅ Email libraries available")
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            return False
        
        print("\n✅ Email automation ready to use!")
        print("\nQuick start commands:")
        print("  python unified_email_automation.py --report   # Generate report")
        print("  python unified_email_automation.py --sync     # Sync all systems")
        print("  python unified_email_automation.py --loop     # Run automation")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

if __name__ == "__main__":
    if setup_email_automation():
        sys.exit(0)
    else:
        sys.exit(1)
