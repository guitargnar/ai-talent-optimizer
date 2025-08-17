#!/usr/bin/env python3
"""
Manual Email Test - Direct SMTP Testing
Tests email with explicit credentials for debugging
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def test_gmail_manually():
    """Test Gmail with manual password entry"""
    
    print("\n" + "="*60)
    print("🔧 MANUAL GMAIL SMTP TEST")
    print("="*60)
    
    # Hardcoded values for testing
    email = "matthewdscott7@gmail.com"
    
    print(f"\n📧 Testing with: {email}")
    print("\n🔐 App Password Instructions:")
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Generate new app password for 'Mail'")
    print("3. Copy the 16-character password")
    print("4. Enter it below (spaces OK, will be removed)")
    
    # Get password interactively
    password = input("\nEnter app password: ").strip().replace(' ', '')
    
    print(f"\n🔍 Testing with {len(password)}-character password...")
    print(f"   First 4 chars: {password[:4] if len(password) >= 4 else 'N/A'}")
    print(f"   Last 4 chars: {password[-4:] if len(password) >= 4 else 'N/A'}")
    
    try:
        # Connect to Gmail
        print("\n📡 Connecting to smtp.gmail.com:587...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        
        print("🔒 Starting TLS encryption...")
        server.starttls()
        
        print(f"🔐 Logging in as {email}...")
        server.login(email, password)
        
        print("✅ LOGIN SUCCESSFUL!")
        
        # Send test email
        print("\n📤 Sending test email...")
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = email
        msg['Subject'] = "SUCCESS: AI Talent Optimizer Email Working!"
        
        body = """
Your email is now configured correctly!

Password that worked: [First 4: """ + password[:4] + """] ... [Last 4: """ + password[-4:] + """]
Length: """ + str(len(password)) + """ characters

Save this password in your .env file:
EMAIL_APP_PASSWORD=""" + password + """

Your system is ready to send job applications to:
- Anthropic (careers@anthropic.com)
- Scale AI (careers@scale.com)
- And 307+ other jobs!

Run: python automated_apply.py
"""
        
        msg.attach(MIMEText(body, 'plain'))
        server.send_message(msg)
        server.quit()
        
        print("✅ Test email sent! Check your inbox.")
        print("\n📝 To save this password:")
        print(f"   Edit: .env")
        print(f"   Set: EMAIL_APP_PASSWORD={password}")
        
        # Offer to save
        save = input("\nSave this password to .env? (y/n): ").lower()
        if save == 'y':
            from dotenv import set_key
            from pathlib import Path
            env_path = Path(__file__).parent / '.env'
            set_key(env_path, 'EMAIL_APP_PASSWORD', password)
            print("✅ Password saved to .env!")
            print("\n🎯 You're ready to send applications!")
            print("   Run: python automated_apply.py")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ Authentication failed!")
        print(f"   Error: {e}")
        print("\n🔍 Common issues:")
        print("1. Wrong password - try generating a new one")
        print("2. 2FA not enabled - enable it first")
        print("3. Security block - check Gmail for alerts")
        print("4. Typo in password - try again")
        
    except smtplib.SMTPServerDisconnected:
        print("\n❌ Server disconnected")
        print("   Check your internet connection")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"   Type: {type(e).__name__}")
    
    return False


def test_with_different_passwords():
    """Test with password variations"""
    
    email = "matthewdscott7@gmail.com"
    base_password = "qvjrafdkgvragbf"
    
    variations = [
        base_password,  # As stored
        base_password + "b",  # With