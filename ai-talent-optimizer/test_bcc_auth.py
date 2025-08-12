#!/usr/bin/env python3
"""Test BCC authentication"""

from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Check credentials
email = os.getenv('EMAIL_ADDRESS')
password = os.getenv('EMAIL_APP_PASSWORD')

print(f"Email: {email}")
print(f"Password: {'*' * len(password) if password else 'NOT FOUND'} ({len(password) if password else 0} chars)")

# Test with simple SMTP
import smtplib
import ssl

try:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email, password)
        print("✅ Authentication successful!")
except Exception as e:
    print(f"❌ Authentication failed: {e}")