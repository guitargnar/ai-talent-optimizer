#!/usr/bin/env python3
"""
Unified Email Engine
Supports both SMTP (App Password) and Gmail API (OAuth2) methods
"""

import os
import json
import base64
import smtplib
import ssl
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Gmail API imports (optional)
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False

# Load environment variables
load_dotenv()

class UnifiedEmailEngine:
    """Unified email engine supporting SMTP and Gmail API methods"""
    
    def __init__(self, prefer_gmail_api: bool = True):
        """
        Initialize unified email engine
        
        Args:
            prefer_gmail_api: Whether to prefer Gmail API over SMTP when both available
        """
        self.prefer_gmail_api = prefer_gmail_api
        self.gmail_dir = Path.home() / ".gmail_job_tracker"
        
        # SMTP configuration
        self.smtp_email = os.getenv('EMAIL_ADDRESS', 'matthewdscott7@gmail.com')
        self.smtp_password = os.getenv('EMAIL_APP_PASSWORD')
        
        # Gmail API configuration
        self.oauth_creds_file = self.gmail_dir / "oauth_credentials.json"
        self.token_file = self.gmail_dir / "token.json"
        
        # Determine available methods
        self.smtp_available = bool(self.smtp_email and self.smtp_password)
        self.gmail_api_available = GMAIL_API_AVAILABLE and self.token_file.exists()
        
        # Select method
        if prefer_gmail_api and self.gmail_api_available:
            self.method = "gmail_api"
        elif self.smtp_available:
            self.method = "smtp"
        else:
            self.method = None
        
        self.gmail_service = None
        
        print(f"🔧 Email Engine Initialized")
        print(f"   SMTP Available: {self.smtp_available}")
        print(f"   Gmail API Available: {self.gmail_api_available}")
        print(f"   Selected Method: {self.method}")
    
    def _initialize_gmail_api(self):
        """Initialize Gmail API service"""
        if not self.gmail_api_available:
            return False
        
        try:
            creds = Credentials.from_authorized_user_file(str(self.token_file))
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            return True
        except Exception as e:
            print(f"⚠️ Failed to initialize Gmail API: {e}")
            return False
    
    def send_email(self, 
                   to_email: str,
                   subject: str,
                   body: str,
                   attachments: List[str] = None,
                   email_type: str = 'application') -> Tuple[bool, str]:
        """
        Send email using the best available method
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body (plain text)
            attachments: List of file paths to attach
            email_type: Type of email (for tracking)
            
        Returns:
            Tuple of (success, message_id/error)
        """
        if not self.method:
            return False, "No email method available"
        
        if self.method == "gmail_api":
            return self._send_via_gmail_api(to_email, subject, body, attachments)
        elif self.method == "smtp":
            return self._send_via_smtp(to_email, subject, body, attachments, email_type)
        else:
            return False, "Invalid email method"
    
    def _send_via_gmail_api(self, 
                           to_email: str, 
                           subject: str, 
                           body: str, 
                           attachments: List[str]) -> Tuple[bool, str]:
        """Send email via Gmail API"""
        try:
            if not self.gmail_service:
                if not self._initialize_gmail_api():
                    return False, "Gmail API initialization failed"
            
            # Create message
            message = MIMEMultipart()
            message['to'] = to_email
            message['from'] = self.smtp_email
            message['subject'] = subject
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Add HTML version for better formatting
            html_body = body.replace('\n', '<br>\n')
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            {html_body}
            </body>
            </html>
            """
            message.attach(MIMEText(html_message, 'html'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        self._attach_file(message, file_path)
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_result = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            message_id = send_result['id']
            print(f"✅ Email sent via Gmail API")
            print(f"   To: {to_email}")
            print(f"   Message ID: {message_id}")
            
            return True, message_id
            
        except Exception as e:
            error_msg = f"Gmail API send failed: {e}"
            print(f"❌ {error_msg}")
            
            # Fallback to SMTP if available
            if self.smtp_available:
                print("🔄 Falling back to SMTP...")
                return self._send_via_smtp(to_email, subject, body, attachments, 'application')
            
            return False, error_msg
    
    def _send_via_smtp(self, 
                      to_email: str, 
                      subject: str, 
                      body: str, 
                      attachments: List[str],
                      email_type: str) -> Tuple[bool, str]:
        """Send email via SMTP with App Password"""
        try:
            # Create message
            message = MIMEMultipart()
            message['From'] = f"Matthew Scott <{self.smtp_email}>"
            message['To'] = to_email
            message['Subject'] = subject
            
            # Add BCC for tracking
            bcc_addresses = {
                'application': 'matthewdscott7+jobapps@gmail.com',
                'followup': 'matthewdscott7+followups@gmail.com',
                'networking': 'matthewdscott7+networking@gmail.com'
            }
            bcc_address = bcc_addresses.get(email_type, bcc_addresses['application'])
            message['Bcc'] = bcc_address
            
            # Add tracking headers
            tracking_id = self._generate_tracking_id(to_email, subject)
            message['X-Job-Tracker-ID'] = tracking_id
            message['X-Job-Tracker-Type'] = email_type
            message['X-Job-Tracker-Date'] = datetime.now().isoformat()
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Add HTML version
            html_body = body.replace('\n', '<br>\n')
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            {html_body}
            </body>
            </html>
            """
            message.attach(MIMEText(html_message, 'html'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        self._attach_file(message, file_path)
            
            # Send via SMTP
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(message)
            
            print(f"✅ Email sent via SMTP")
            print(f"   To: {to_email}")
            print(f"   BCC: {bcc_address}")
            print(f"   Tracking ID: {tracking_id}")
            
            return True, tracking_id
            
        except Exception as e:
            error_msg = f"SMTP send failed: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def _attach_file(self, message: MIMEMultipart, file_path: str):
        """Attach file to email message"""
        try:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(file_path)}'
                )
                message.attach(part)
            print(f"   📎 Attached: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"   ⚠️ Failed to attach {file_path}: {e}")
    
    def _generate_tracking_id(self, to_email: str, subject: str) -> str:
        """Generate unique tracking ID"""
        import hashlib
        data = f"{to_email}:{subject}:{datetime.now().date()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def get_status(self) -> Dict:
        """Get detailed status of email engine"""
        status = {
            'smtp_available': self.smtp_available,
            'gmail_api_available': self.gmail_api_available,
            'selected_method': self.method,
            'smtp_config': {
                'email': self.smtp_email,
                'password_configured': bool(self.smtp_password)
            },
            'gmail_api_config': {
                'oauth_credentials': self.oauth_creds_file.exists(),
                'token_file': self.token_file.exists(),
                'libraries_available': GMAIL_API_AVAILABLE
            }
        }
        return status
    
    def test_connection(self) -> bool:
        """Test email connection"""
        print("\n🧪 Testing Email Connection")
        print("=" * 35)
        
        if self.method == "gmail_api":
            return self._test_gmail_api()
        elif self.method == "smtp":
            return self._test_smtp()
        else:
            print("❌ No email method available")
            return False
    
    def _test_gmail_api(self) -> bool:
        """Test Gmail API connection"""
        try:
            if not self.gmail_service:
                if not self._initialize_gmail_api():
                    return False
            
            # Test API access
            results = self.gmail_service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            print(f"✅ Gmail API connection successful! Found {len(labels)} labels")
            
            # Get user profile
            profile = self.gmail_service.users().getProfile(userId='me').execute()
            print(f"✅ Email: {profile['emailAddress']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Gmail API test failed: {e}")
            return False
    
    def _test_smtp(self) -> bool:
        """Test SMTP connection"""
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.smtp_email, self.smtp_password)
                print(f"✅ SMTP connection successful!")
                print(f"✅ Email: {self.smtp_email}")
                return True
                
        except Exception as e:
            print(f"❌ SMTP test failed: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """Send a test email"""
        test_subject = "🧪 Unified Email Engine Test"
        test_body = f"""This is a test email from the Unified Email Engine.

Method Used: {self.method}
Timestamp: {datetime.now()}

This confirms that automated email sending is working for the AI Talent Optimizer system.

✅ Email engine operational
✅ Ready for job application sending

--
AI Talent Optimizer
Matthew Scott
"""
        
        success, result = self.send_email(
            to_email=self.smtp_email,  # Send to self
            subject=test_subject,
            body=test_body,
            email_type='test'
        )
        
        if success:
            print(f"✅ Test email sent successfully! Result: {result}")
        else:
            print(f"❌ Test email failed: {result}")
        
        return success

def main():
    """Test the unified email engine"""
    print("🚀 Unified Email Engine Test")
    print("=" * 50)
    
    # Test both methods
    for prefer_api in [True, False]:
        method_name = "Gmail API" if prefer_api else "SMTP"
        print(f"\n📧 Testing with {method_name} preference...")
        
        engine = UnifiedEmailEngine(prefer_gmail_api=prefer_api)
        status = engine.get_status()
        
        print(f"\n📊 Engine Status:")
        for key, value in status.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for subkey, subvalue in value.items():
                    print(f"     {subkey}: {subvalue}")
            else:
                print(f"   {key}: {value}")
        
        if engine.method:
            engine.test_connection()
            
            # Ask if user wants to send test email
            print(f"\n🤔 Send test email via {engine.method.upper()}? (y/n): ", end="")
            if input().lower().strip() == 'y':
                engine.send_test_email()
        
        print("\n" + "="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()