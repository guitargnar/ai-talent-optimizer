#!/usr/bin/env python3
"""
Link existing Gmail OAuth credentials to unified system
"""

import os
import json
import shutil
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly']

def setup_gmail_oauth():
    """Link existing Gmail OAuth and create token if needed"""
    
    # Paths
    existing_creds = Path.home() / ".gmail_job_tracker" / "credentials.json"
    existing_token = Path.home() / ".gmail_job_tracker" / "token.json"
    
    local_creds = Path("credentials.json")
    local_token = Path("token.json")
    
    print("🔗 Linking Gmail OAuth credentials...")
    
    # Link credentials.json
    if existing_creds.exists():
        if not local_creds.exists():
            # Create symlink
            local_creds.symlink_to(existing_creds)
            print(f"✅ Linked credentials.json from {existing_creds}")
        else:
            print(f"✅ credentials.json already exists locally")
    else:
        print(f"❌ No credentials found at {existing_creds}")
        return False
    
    # Check for existing token
    creds = None
    if existing_token.exists():
        # Copy token (don't symlink - it gets updated)
        shutil.copy2(existing_token, local_token)
        print(f"✅ Copied existing token.json")
        creds = Credentials.from_authorized_user_file(str(local_token), SCOPES)
    elif local_token.exists():
        creds = Credentials.from_authorized_user_file(str(local_token), SCOPES)
        print(f"✅ Using existing local token.json")
    
    # Check if token needs refresh
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            print("✅ Refreshed expired token")
        except Exception as e:
            print(f"⚠️ Could not refresh token: {e}")
            creds = None
    
    # If no valid creds, need to authorize
    if not creds or not creds.valid:
        print("\n🔐 Need to authorize Gmail access...")
        print("This will open a browser window for authorization")
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(local_creds), SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ Authorization successful!")
        except Exception as e:
            print(f"❌ Authorization failed: {e}")
            print("\nTo manually authorize:")
            print("1. Go to: https://console.cloud.google.com/apis/credentials")
            print("2. Create OAuth 2.0 credentials")
            print("3. Download and save as credentials.json")
            return False
    
    # Save the token
    if creds:
        with open(local_token, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ Saved token.json")
        
        # Also update the original location
        with open(existing_token, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ Updated token in {existing_token}")
    
    # Test the connection
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        print(f"\n✅ Gmail API connected! Found {len(labels)} labels")
        return True
    except Exception as e:
        print(f"❌ Gmail API test failed: {e}")
        return False

if __name__ == "__main__":
    try:
        import google.auth
        setup_gmail_oauth()
    except ImportError:
        print("❌ Google API libraries not installed")
        print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        print("\nThen run this script again.")