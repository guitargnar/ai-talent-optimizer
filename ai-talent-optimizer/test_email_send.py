#!/usr/bin/env python3
"""Test email sending directly"""

from bcc_email_tracker import BCCEmailTracker
import time

print("🧪 Testing email send functionality...")

tracker = BCCEmailTracker()
print("✅ BCCEmailTracker initialized")

# Test sending a simple email
test_email = {
    'to': 'test@example.com',
    'subject': 'Test Email - Please Ignore',
    'body': 'This is a test email to debug the application system.'
}

print(f"\n📧 Attempting to send test email to: {test_email['to']}")
print("⏱️  Starting timer...")

start_time = time.time()
try:
    success, tracking_id = tracker.send_tracked_email(
        to_email=test_email['to'],
        subject=test_email['subject'],
        body=test_email['body'],
        email_type='applications',
        track_in_db=False  # Don't track in DB for test
    )
    
    elapsed = time.time() - start_time
    print(f"\n✅ Email send completed in {elapsed:.2f} seconds")
    print(f"Success: {success}")
    print(f"Tracking ID: {tracking_id}")
    
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n❌ Email send failed after {elapsed:.2f} seconds")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()