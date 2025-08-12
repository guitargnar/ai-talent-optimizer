#!/usr/bin/env python3
"""Send a test application to verify everything works"""

from bcc_email_tracker import BCCEmailTracker
import sys

def test_application():
    """Send a test application"""
    
    tracker = BCCEmailTracker()
    
    # Test data
    test_job = {
        'company': 'Test Company',
        'position': 'Test Position',
        'email': 'test@example.com'  # This won't actually send
    }
    
    # Test cover letter
    cover_letter = f"""Dear {test_job['company']} Hiring Team,

This is a test application to verify the email system is working correctly.

Best regards,
Matthew Scott"""
    
    print(f"📧 Testing email system...")
    print(f"From: {tracker.primary_email}")
    print(f"App Password: {'*' * 16} (loaded from .env)")
    print(f"BCC: {tracker.bcc_addresses['applications']}")
    
    # Ask for confirmation
    confirm = input("\nSend test email to yourself? (y/n): ")
    
    if confirm.lower() == 'y':
        # Send to self as test
        success, tracking_id = tracker.send_tracked_email(
            to_email=tracker.primary_email,  # Send to self
            subject=f"TEST: Application for {test_job['position']}",
            body=cover_letter,
            email_type='applications'
        )
        
        if success:
            print(f"\n✅ Test email sent successfully!")
            print(f"Tracking ID: {tracking_id}")
            print(f"Check your inbox for the test email")
        else:
            print(f"\n❌ Test failed")
    else:
        print("Test cancelled")

if __name__ == "__main__":
    test_application()