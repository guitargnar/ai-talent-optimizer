#!/usr/bin/env python3
"""
Complete Gmail OAuth2 Setup for Email Sending
This creates the token.json needed for Gmail API email sending
"""

import os
import json
import sys
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64

# Gmail API scopes for sending and reading
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose'
]

class GmailOAuth2Setup:
    """Complete Gmail OAuth2 setup and token generation"""
    
    def __init__(self):
        self.creds_dir = Path.home() / ".gmail_job_tracker"
        self.oauth_creds_file = self.creds_dir / "oauth_credentials.json"
        self.token_file = self.creds_dir / "token.json"
        self.creds_dir.mkdir(exist_ok=True)
    
    def create_oauth_credentials(self):
        """Create OAuth2 credentials.json for Gmail API"""
        print("🔐 Creating Gmail OAuth2 Credentials")
        print("=" * 50)
        print()
        print("You need to create OAuth2 credentials in Google Cloud Console:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Gmail API:")
        print("   - Go to APIs & Services → Library")
        print("   - Search 'Gmail API' and enable it")
        print("4. Create OAuth2 credentials:")
        print("   - Go to APIs & Services → Credentials")
        print("   - Click 'Create Credentials' → OAuth 2.0 Client IDs")
        print("   - Application type: Desktop application")
        print("   - Name: AI Talent Optimizer")
        print("   - Download the JSON file")
        print()
        
        # Check if user has credentials
        if self.oauth_creds_file.exists():
            print(f"✅ OAuth credentials already exist at: {self.oauth_creds_file}")
            return True
        
        print("🤔 Do you have the OAuth2 credentials JSON file? (y/n): ", end="")
        has_creds = input().lower().strip()
        
        if has_creds == 'y':
            print("📁 Enter the full path to your downloaded credentials JSON: ", end="")
            creds_path = input().strip()
            
            if os.path.exists(creds_path):
                # Copy to our location
                import shutil
                shutil.copy2(creds_path, self.oauth_creds_file)
                os.chmod(self.oauth_creds_file, 0o600)
                print(f"✅ Credentials saved to: {self.oauth_creds_file}")
                return True
            else:
                print(f"❌ File not found: {creds_path}")
                return False
        else:
            print("❌ Please create OAuth2 credentials first and run this script again.")
            return False
    
    def generate_token(self):
        """Generate OAuth2 token.json"""
        print("\n🎫 Generating OAuth2 Token")
        print("=" * 30)
        
        if not self.oauth_creds_file.exists():
            print("❌ OAuth credentials not found. Run create_oauth_credentials() first.")
            return False
        
        creds = None
        
        # Check for existing token
        if self.token_file.exists():
            print("📄 Found existing token, checking validity...")
            creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
        
        # Refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully!")
            except Exception as e:
                print(f"⚠️ Token refresh failed: {e}")
                creds = None
        
        # Generate new token if needed
        if not creds or not creds.valid:
            print("🌐 Starting OAuth2 authorization flow...")
            print("This will open a browser window for Gmail authorization.")
            print("Please:")
            print("1. Sign in to your Gmail account")
            print("2. Grant the requested permissions")
            print("3. Return to this script")
            print()
            print("Press Enter to continue...", end="")
            input()
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.oauth_creds_file), SCOPES
                )
                creds = flow.run_local_server(port=0)
                print("✅ Authorization successful!")
            except Exception as e:
                print(f"❌ Authorization failed: {e}")
                return False
        
        # Save the token
        if creds:
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
            os.chmod(self.token_file, 0o600)
            print(f"✅ Token saved to: {self.token_file}")
            return True
        
        return False
    
    def test_gmail_api(self):
        """Test Gmail API with generated token"""
        print("\n🧪 Testing Gmail API Connection")
        print("=" * 35)
        
        if not self.token_file.exists():
            print("❌ Token not found. Generate token first.")
            return False
        
        try:
            creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
            service = build('gmail', 'v1', credentials=creds)
            
            # Test API access
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            print(f"✅ Gmail API connected! Found {len(labels)} labels")
            
            # Get user profile
            profile = service.users().getProfile(userId='me').execute()
            print(f"✅ Email: {profile['emailAddress']}")
            print(f"✅ Messages: {profile['messagesTotal']:,}")
            
            return True, service
            
        except Exception as e:
            print(f"❌ Gmail API test failed: {e}")
            return False, None
    
    def send_test_email(self, service):
        """Send a test email via Gmail API"""
        print("\n📧 Testing Email Send via Gmail API")
        print("=" * 40)
        
        try:
            # Create test message
            message = MIMEMultipart()
            message['to'] = 'matthewdscott7@gmail.com'  # Send to self
            message['subject'] = '🧪 Gmail API Test - AI Talent Optimizer'
            
            body = """This is a test email sent via Gmail API from the AI Talent Optimizer system.

✅ Gmail OAuth2 token is working
✅ Gmail API connection successful
✅ Email sending capability confirmed

Time: """ + str(os.popen('date').read().strip()) + """

This email confirms that automated email sending is now functional for job applications.

-- 
AI Talent Optimizer System
Matthew Scott
"""
            
            message.attach(MIMEText(body, 'plain'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message
            send_result = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"✅ Test email sent successfully!")
            print(f"📧 Message ID: {send_result['id']}")
            print(f"📧 Thread ID: {send_result['threadId']}")
            print(f"📧 Sent to: matthewdscott7@gmail.com")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send test email: {e}")
            return False

def main():
    """Main setup flow"""
    print("🚀 Gmail OAuth2 Complete Setup")
    print("=" * 50)
    print("This script will:")
    print("1. Set up OAuth2 credentials for Gmail API")
    print("2. Generate token.json for email sending")
    print("3. Test Gmail API connection and email sending")
    print("4. Create a unified email engine")
    print()
    
    setup = GmailOAuth2Setup()
    
    # Step 1: Create OAuth credentials
    if not setup.create_oauth_credentials():
        print("\n❌ OAuth credentials setup failed. Exiting.")
        return False
    
    # Step 2: Generate token
    if not setup.generate_token():
        print("\n❌ Token generation failed. Exiting.")
        return False
    
    # Step 3: Test Gmail API
    success, service = setup.test_gmail_api()
    if not success:
        print("\n❌ Gmail API test failed. Exiting.")
        return False
    
    # Step 4: Send test email
    if setup.send_test_email(service):
        print("\n🎉 Complete Success!")
        print("=" * 30)
        print("✅ OAuth2 credentials created")
        print("✅ Token.json generated")
        print("✅ Gmail API connection verified")
        print("✅ Email sending tested and working")
        print()
        print("📁 Files created:")
        print(f"   - {setup.oauth_creds_file}")
        print(f"   - {setup.token_file}")
        print()
        print("🚀 You can now send emails via Gmail API!")
        print("   Use the GmailAPIEngine class for sending applications.")
        
        return True
    else:
        print("\n⚠️ Email test failed, but token was created.")
        print("You may need to check Gmail API quotas or permissions.")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()