#!/usr/bin/env python3
"""Direct test of email sending"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment
load_dotenv()

email = os.getenv('EMAIL_ADDRESS')
password = os.getenv('EMAIL_APP_PASSWORD')

print(f"Testing with:")
print(f"Email: {email}")
print(f"Password: {'*' * len(password)} ({len(password)} chars)")

# Create message
msg = MIMEMultipart()
msg['From'] = email
msg['To'] = email
msg['Subject'] = "TEST: AI Job Hunter Working"
msg['Bcc'] = 'matthewdscott7+jobapps@gmail.com'

body = "This is a test from your AI Job Hunter automation system. If you receive this, everything is working!"
msg.attach(MIMEText(body, 'plain'))

# Send
try:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        print("\nConnecting to Gmail...")
        server.login(email, password)
        print("Logged in successfully!")
        
        print("Sending test email...")
        server.send_message(msg)
        print("✅ Test email sent! Check your inbox.")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure 2-factor authentication is enabled")
    print("2. Generate a new app password at:")
    print("   https://myaccount.google.com/apppasswords")
    print("3. Update .env with the new password")