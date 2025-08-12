#!/usr/bin/env python3
import imaplib
import json
import os

# Load credentials
with open(os.path.expanduser('~/.gmail_job_tracker/credentials.json'), 'r') as f:
    creds = json.load(f)

# Test connection
try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(creds['email'], creds['app_password'])
    mail.select('inbox')
    
    # Search for job-related emails
    result, data = mail.search(None, 'UNSEEN', 'OR', 
        'FROM', '"noreply"', 
        'FROM', '"careers"'
    )
    
    email_ids = data[0].split()
    print(f"✅ Connection successful!")
    print(f"📧 Found {len(email_ids)} unread job-related emails")
    
    mail.logout()
except Exception as e:
    print(f"❌ Connection failed: {e}")
