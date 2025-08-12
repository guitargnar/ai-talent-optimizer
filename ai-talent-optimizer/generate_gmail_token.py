#!/usr/bin/env python3
"""
Gmail Token Generator
Creates token.json for Gmail API access
"""

import os
import json
import tempfile
import subprocess
from pathlib import Path

def create_oauth_credentials():
    """Create temporary OAuth credentials for token generation"""
    
    # This is a placeholder OAuth2 client configuration
    # In production, you would download this from Google Cloud Console
    oauth_config = {
        "installed": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "project_id": "ai-talent-optimizer",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    gmail_dir = Path.home() / ".gmail_job_tracker"
    gmail_dir.mkdir(exist_ok=True)
    
    oauth_file = gmail_dir / "oauth_credentials.json"
    
    print("🔐 Gmail OAuth2 Token Generation Setup")
    print("=" * 50)
    print()
    print("To generate a Gmail token.json file, you need OAuth2 credentials.")
    print()
    print("📋 STEP-BY-STEP INSTRUCTIONS:")
    print()
    print("1. 🌐 Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print()
    print("2. 📁 Create or select a project:")
    print("   - Click 'Select a project' or 'New Project'")
    print("   - Name: 'AI Talent Optimizer' (or similar)")
    print()
    print("3. 🔌 Enable Gmail API:")
    print("   - Go to 'APIs & Services' → 'Library'")
    print("   - Search for 'Gmail API'")
    print("   - Click 'Enable'")
    print()
    print("4. 🔑 Create OAuth2 Credentials:")
    print("   - Go to 'APIs & Services' → 'Credentials'")
    print("   - Click '+ Create Credentials'")
    print("   - Select 'OAuth 2.0 Client IDs'")
    print("   - Application type: 'Desktop application'")
    print("   - Name: 'AI Talent Optimizer'")
    print("   - Click 'Create'")
    print()
    print("5. 💾 Download JSON:")
    print("   - Click the download button (⬇️) next to your client")
    print("   - Save the file as 'client_secret.json'")
    print()
    
    if oauth_file.exists():
        print(f"✅ Found existing OAuth file: {oauth_file}")
        return True
    
    print("🤔 Do you have the client_secret.json file downloaded? (y/n): ", end="")
    response = input().strip().lower()
    
    if response == 'y':
        print("📁 Enter the full path to your client_secret.json file: ", end="")
        json_path = input().strip()
        
        if os.path.exists(json_path):
            # Copy to our location
            import shutil
            shutil.copy2(json_path, oauth_file)
            os.chmod(oauth_file, 0o600)
            print(f"✅ OAuth credentials saved to: {oauth_file}")
            return True
        else:
            print(f"❌ File not found: {json_path}")
            return False
    else:
        print("\n📝 Creating example OAuth credentials file...")
        print(f"   Location: {oauth_file}")
        print()
        print("⚠️  You MUST replace these with real credentials:")
        
        with open(oauth_file, 'w') as f:
            json.dump(oauth_config, f, indent=2)
        os.chmod(oauth_file, 0o600)
        
        print()
        print("🔴 IMPORTANT: This is a template file!")
        print("   You must replace YOUR_CLIENT_ID and YOUR_CLIENT_SECRET")
        print("   with your actual values from Google Cloud Console.")
        print()
        print("📝 Edit this file and run the script again:")
        print(f"   nano {oauth_file}")
        
        return False

def generate_token_with_oauth():
    """Generate token.json using OAuth2 flow"""
    
    print("\n🎫 Generating Gmail Token")
    print("=" * 30)
    
    gmail_dir = Path.home() / ".gmail_job_tracker"
    oauth_file = gmail_dir / "oauth_credentials.json"
    token_file = gmail_dir / "token.json"
    
    if not oauth_file.exists():
        print("❌ OAuth credentials not found.")
        return False
    
    # Check if we have valid credentials
    try:
        with open(oauth_file, 'r') as f:
            oauth_data = json.load(f)
        
        client_id = oauth_data['installed']['client_id']
        client_secret = oauth_data['installed']['client_secret']
        
        if 'YOUR_CLIENT_ID' in client_id or 'YOUR_CLIENT_SECRET' in client_secret:
            print("❌ OAuth credentials still contain placeholder values.")
            print("   Please edit the file and replace with real values:")
            print(f"   nano {oauth_file}")
            return False
            
    except Exception as e:
        print(f"❌ Error reading OAuth credentials: {e}")
        return False
    
    # Try to generate token using the OAuth2 flow
    try:
        print("🌐 Starting OAuth2 authorization flow...")
        print()
        print("This will:")
        print("1. Open a browser window")
        print("2. Ask you to sign in to Gmail")
        print("3. Request permission to send emails")
        print("4. Generate token.json file")
        print()
        print("Press Enter to continue or Ctrl+C to cancel...", end="")
        input()
        
        # Use the setup script we created earlier
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.compose'
        ]
        
        flow = InstalledAppFlow.from_client_secrets_file(str(oauth_file), SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save token
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        os.chmod(token_file, 0o600)
        
        print(f"\n✅ Token generated successfully!")
        print(f"   Saved to: {token_file}")
        
        # Test the token
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Token validated for: {profile['emailAddress']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing required libraries: {e}")
        print("\nInstall with: pip install google-auth google-auth-oauthlib google-api-python-client")
        return False
    except Exception as e:
        print(f"❌ Token generation failed: {e}")
        return False

def create_simple_token():
    """Create a simple token file for testing (not recommended for production)"""
    
    print("\n⚠️  FALLBACK: Creating Simple Token")
    print("=" * 40)
    print()
    print("This creates a basic token structure for testing.")
    print("For production use, you need real OAuth2 tokens.")
    print()
    
    gmail_dir = Path.home() / ".gmail_job_tracker"
    token_file = gmail_dir / "token.json"
    
    # Simple token structure (will not work for actual API calls)
    simple_token = {
        "token": "fake_access_token",
        "refresh_token": "fake_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "scopes": [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.readonly"
        ],
        "expiry": "2025-12-31T23:59:59Z",
        "note": "This is a placeholder token. Replace with real OAuth2 token."
    }
    
    with open(token_file, 'w') as f:
        json.dump(simple_token, f, indent=2)
    os.chmod(token_file, 0o600)
    
    print(f"✅ Simple token created: {token_file}")
    print("⚠️  This will NOT work for actual Gmail API calls!")
    print("   Use it only to test the token file structure.")
    
    return True

def main():
    """Main token generation flow"""
    
    print("🚀 Gmail Token Generator")
    print("=" * 40)
    print()
    print("This script helps you generate the token.json file needed")
    print("for Gmail API access in the AI Talent Optimizer.")
    print()
    
    # Check if token already exists
    gmail_dir = Path.home() / ".gmail_job_tracker"
    token_file = gmail_dir / "token.json"
    
    if token_file.exists():
        print(f"✅ Token already exists: {token_file}")
        print()
        print("🤔 Do you want to regenerate it? (y/n): ", end="")
        if input().strip().lower() != 'y':
            print("✅ Using existing token.")
            return True
    
    # Step 1: Create OAuth credentials
    print("\n🔑 Step 1: OAuth2 Credentials")
    print("-" * 35)
    if not create_oauth_credentials():
        print("\n⚠️  OAuth credentials setup incomplete.")
        print("🤔 Create a simple token for testing instead? (y/n): ", end="")
        if input().strip().lower() == 'y':
            return create_simple_token()
        else:
            print("❌ Cannot proceed without OAuth credentials.")
            return False
    
    # Step 2: Generate token
    print("\n🎫 Step 2: Token Generation")
    print("-" * 30)
    
    success = generate_token_with_oauth()
    
    if not success:
        print("\n⚠️  OAuth token generation failed.")
        print("🤔 Create a simple token for testing instead? (y/n): ", end="")
        if input().strip().lower() == 'y':
            return create_simple_token()
        else:
            return False
    
    print("\n🎉 SUCCESS!")
    print("=" * 20)
    print("✅ Gmail token.json has been created!")
    print("✅ You can now send emails via Gmail API!")
    print(f"✅ Token location: {token_file}")
    print()
    print("🚀 Next Steps:")
    print("   1. Test with: python unified_email_engine.py")
    print("   2. Send applications with the AI Talent Optimizer")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Token generation interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()