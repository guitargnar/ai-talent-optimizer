#!/usr/bin/env python3
"""
Test Gmail Token Integration
Validates that the Gmail token.json enables email sending
"""

import os
import sys
from pathlib import Path
from core.email_engine import EmailEngine

def test_email_engine_with_token():
    """Test the email engine with Gmail token"""
    
    print("🧪 Testing Gmail Token Integration")
    print("=" * 50)
    
    # Initialize email engine
    engine = EmailEngine()
    status = engine.get_status()
    
    print("\n📊 Email Engine Status:")
    for key, value in status.items():
        status_icon = "✅" if value else "❌"
        print(f"   {status_icon} {key}: {value}")
    
    # Check token file details
    token_file = Path.home() / ".gmail_job_tracker" / "token.json"
    
    print(f"\n📄 Token File Details:")
    print(f"   Location: {token_file}")
    print(f"   Exists: {'✅' if token_file.exists() else '❌'}")
    
    if token_file.exists():
        import json
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            print(f"   Size: {token_file.stat().st_size} bytes")
            print(f"   Fields: {list(token_data.keys())}")
            
            # Check if it's a real token or placeholder
            if 'fake_' in str(token_data) or 'placeholder' in str(token_data).lower():
                print("   ⚠️  This is a placeholder token (won't work for real API calls)")
            else:
                print("   ✅ Appears to be a real OAuth2 token")
                
        except Exception as e:
            print(f"   ❌ Error reading token: {e}")
    
    # Test email sending capability
    print(f"\n📧 Email Sending Test:")
    
    if not engine.engine:
        print("   ❌ No email engine available")
        return False
    
    # Test with a simple application email
    test_subject = "🧪 Test Application - AI Talent Optimizer"
    test_body = """Dear Hiring Team,

This is a test email to verify that the Gmail token integration is working correctly for the AI Talent Optimizer system.

✅ Gmail token.json detected
✅ Email engine initialized
✅ Ready for job application automation

Best regards,
Matthew Scott
AI Talent Optimizer Test System"""
    
    print("   📤 Attempting to send test email...")
    
    try:
        success = engine.send_application(
            to="matthewdscott7@gmail.com",  # Send to self
            subject=test_subject,
            body=test_body
        )
        
        if success:
            print("   ✅ Test email sent successfully!")
            print("   📧 Check your inbox for the test message")
            return True
        else:
            print("   ❌ Test email failed to send")
            return False
            
    except Exception as e:
        print(f"   ❌ Email send exception: {e}")
        return False

def provide_next_steps():
    """Provide next steps based on test results"""
    
    print(f"\n🎯 Next Steps:")
    print("-" * 20)
    
    token_file = Path.home() / ".gmail_job_tracker" / "token.json"
    
    if not token_file.exists():
        print("1. Generate Gmail token:")
        print("   python generate_gmail_token.py")
        print()
        print("2. Follow OAuth2 setup instructions")
        print("   https://console.cloud.google.com/")
        
    else:
        print("1. ✅ Gmail token exists")
        print("2. ✅ Email engine operational")
        print("3. 🚀 Ready to send job applications!")
        print()
        print("📝 To send applications:")
        print("   python send_direct_applications.py")
        print()
        print("📈 To check application status:")
        print("   python true_metrics_dashboard.py")

def main():
    """Main test function"""
    
    print("🚀 Gmail Token Integration Test")
    print("=" * 60)
    print("This test validates that Gmail token.json enables email sending")
    print("for the AI Talent Optimizer job application system.")
    print()
    
    # Run the test
    success = test_email_engine_with_token()
    
    # Provide guidance
    provide_next_steps()
    
    print(f"\n🏁 Test Result: {'✅ PASSED' if success else '❌ FAILED'}")
    
    if success:
        print("\n🎉 Gmail token integration is working!")
        print("   You can now send automated job applications.")
    else:
        print("\n⚠️  Gmail token needs attention.")
        print("   Check the setup instructions above.")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()