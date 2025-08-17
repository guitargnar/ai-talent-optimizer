#!/usr/bin/env python3
"""
Secure Password Update
Updates app password without exposing it in code
"""

import os
import sys
import smtplib
import getpass
from pathlib import Path
from dotenv import set_key, load_dotenv

env_path = Path(__file__).parent / '.env'


def update_and_test():
    """Securely update and test password"""
    
    print("\n" + "="*60)
    print("🔐 SECURE PASSWORD UPDATE FOR AI TALENT OPTIMIZER")
    print("="*60)
    
    print("\n✅ I can see you just created a new app password!")
    print("   Name: 'AI Talent Optimizer'")
    print("   Created: 9:15 AM")
    
    print("\n📝 Please enter the 16-character password Google showed you")
    print("   (spaces will be removed automatically)")
    
    # Get password securely (hidden input)
    password = getpass.getpass("\nEnter new app password: ").strip().replace(' ', '')
    
    if len(password) != 16:
        print(f"\n⚠️ Password should be 16 characters (got {len(password)})")
        print("   Make sure you copied the entire password")
        return False
    
    print(f"\n🔍 Testing password (****...{password[-4:]})")
    
    email = "matthewdscott7@gmail.com"
    
    try:
        # Test connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.quit()
        
        print("✅ Authentication successful!")
        
        # Update .env file
        print("\n📝 Updating .env file...")
        set_key(env_path, 'EMAIL_APP_PASSWORD', password)
        
        print("✅ Password saved securely!")
        
        # Final test with EmailService
        print("\n🔧 Testing EmailService...")
        load_dotenv(env_path, override=True)
        
        sys.path.insert(0, str(Path(__file__).parent))
        from src.services.email_service import EmailService
        
        service = EmailService()
        if service._is_configured():
            print("✅ EmailService configured and ready!")
            
            print("\n" + "="*60)
            print("🎉 SUCCESS! Email is now configured!")
            print("="*60)
            print("\n📋 You can now:")
            print("1. Send applications: python automated_apply.py")
            print("2. Check status: python main.py status")
            print("\n🎯 You have 307 jobs ready to apply to:")
            print("   - Anthropic (105 positions)")
            print("   - Scale AI (59 positions)")
            print("   - Plus many more!")
            
            return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ Authentication failed")
        print("   Please check the password and try again")
        print("   Make sure you copied from the 'AI Talent Optimizer' app password")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    return False


if __name__ == "__main__":
    # Check if password provided as argument
    if len(sys.argv) > 1:
        # Quick mode - password provided
        password = ''.join(sys.argv[1:]).replace(' ', '')
        
        if len(password) == 16:
            print(f"🔐 Testing password ending in ...{password[-4:]}")
            
            # Quick test
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login("matthewdscott7@gmail.com", password)
                server.quit()
                
                # Save to .env
                set_key(env_path, 'EMAIL_APP_PASSWORD', password)
                print("✅ Password updated and verified!")
                print("🎯 Run: python automated_apply.py")
                
            except:
                print("❌ Authentication failed")
        else:
            print(f"❌ Password must be 16 characters (got {len(password)})")
    else:
        # Interactive mode
        update_and_test()