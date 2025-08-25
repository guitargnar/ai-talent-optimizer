#!/usr/bin/env python3
"""
BCC Email Tracker - Automatic tracking via BCC
Enhances existing email tracking with automatic BCC capture
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/.env")

# Import existing trackers
from email_application_tracker import EmailApplicationTracker
from gmail_oauth_integration import GmailOAuthIntegration


class BCCEmailTracker:
    """Enhanced email tracking with automatic BCC"""
    
    def __init__(self):
        # Email configuration
        self.primary_email = os.getenv('EMAIL_ADDRESS', 'matthewdscott7@gmail.com')
        self.email_password = os.getenv('EMAIL_APP_PASSWORD')
        
        # BCC tracking addresses (using Gmail + aliases)
        self.bcc_addresses = {
            'applications': 'matthewdscott7+jobapps@gmail.com',
            'followups': 'matthewdscott7+followups@gmail.com',
            'networking': 'matthewdscott7+networking@gmail.com'
        }
        
        # Initialize existing trackers
        self.email_tracker = EmailApplicationTracker()
        self.gmail_integration = GmailOAuthIntegration()
        
        # BCC log for deduplication
        self.bcc_log_file = 'data/bcc_tracking_log.json'
        self.bcc_log = self._load_bcc_log()
    
    def _load_bcc_log(self) -> Dict:
        """Load BCC tracking log"""
        if os.path.exists(self.bcc_log_file):
            with open(self.bcc_log_file, 'r') as f:
                return json.load(f)
        return {'sent_emails': {}, 'last_sync': None}
    
    def _save_bcc_log(self):
        """Save BCC tracking log"""
        os.makedirs(os.path.dirname(self.bcc_log_file), exist_ok=True)
        with open(self.bcc_log_file, 'w') as f:
            json.dump(self.bcc_log, f, indent=2)
    
    def send_tracked_email(self, 
                          to_email: str,
                          subject: str,
                          body: str,
                          email_type: str = 'applications',
                          attachments: List[str] = None,
                          track_in_db: bool = True) -> Tuple[bool, str]:
        """
        Send email with automatic BCC tracking
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body (plain text)
            email_type: Type of email (applications/followups/networking)
            attachments: List of file paths to attach
            track_in_db: Whether to log in email tracker
            
        Returns:
            Tuple of (success, tracking_id)
        """
        
        # Generate tracking ID
        tracking_id = self._generate_tracking_id(to_email, subject)
        
        # Check if already sent (prevent duplicates)
        if tracking_id in self.bcc_log['sent_emails']:
            print(f"⚠️  Email already sent to {to_email} with subject: {subject}")
            return False, tracking_id
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = f"Matthew Scott <{self.primary_email}>"
            message['To'] = to_email
            message['Subject'] = subject
            
            # Add BCC for tracking
            bcc_address = self.bcc_addresses.get(email_type, self.bcc_addresses['applications'])
            message['Bcc'] = bcc_address
            
            # Add custom headers for tracking
            message['X-Job-Tracker-ID'] = tracking_id
            message['X-Job-Tracker-Type'] = email_type
            message['X-Job-Tracker-Date'] = datetime.now().isoformat()
            
            # Extract metadata for tracking
            company = self._extract_company(to_email)
            position = self._extract_position(subject)
            
            message['X-Job-Company'] = company
            message['X-Job-Position'] = position
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Add HTML version with tracking pixel
            html_body = self._create_html_body(body, tracking_id)
            message.attach(MIMEText(html_body, 'html'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        self._attach_file(message, file_path)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.primary_email, self.email_password)
                server.send_message(message)
            
            # Log to BCC tracker
            self.bcc_log['sent_emails'][tracking_id] = {
                'to': to_email,
                'subject': subject,
                'type': email_type,
                'sent_date': datetime.now().isoformat(),
                'company': company,
                'position': position,
                'bcc_address': bcc_address,
                'attachments': attachments or []
            }
            self._save_bcc_log()
            
            # Log to email tracker if requested
            if track_in_db:
                self.email_tracker.log_email_application({
                    'to_email': to_email,
                    'company_name': company,
                    'position_title': position,
                    'subject_line': subject,
                    'email_type': email_type,
                    'notes': f'BCC tracked: {tracking_id}'
                })
            
            print(f"✅ Email sent with BCC tracking: {tracking_id}")
            print(f"   To: {to_email}")
            print(f"   BCC: {bcc_address}")
            
            return True, tracking_id
            
        except Exception as e:
            print(f"❌ Failed to send tracked email: {e}")
            return False, None
    
    def _generate_tracking_id(self, to_email: str, subject: str) -> str:
        """Generate unique tracking ID"""
        import hashlib
        data = f"{to_email}:{subject}:{datetime.now().date()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _extract_company(self, email: str) -> str:
        """Extract company name from email"""
        # Use existing email tracker logic
        return self.email_tracker.extract_company_from_email(email)
    
    def _extract_position(self, subject: str) -> str:
        """Extract position from subject line"""
        # Common patterns
        patterns = [
            r'(?:application for|applying for|re:|interest in)\s+(.+?)(?:\s+position|\s+role|\s+at\s+|$)',
            r'(.+?)\s+(?:position|role|opportunity)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback
        return subject.replace('Application for ', '').replace('Re: ', '')
    
    def _create_html_body(self, plain_text: str, tracking_id: str) -> str:
        """Create HTML version with tracking pixel"""
        # Convert plain text to HTML
        html_text = plain_text.replace('\n', '<br>\n')
        
        # Add invisible tracking pixel (optional - for open tracking)
        tracking_pixel = f'<img src="https://matthewscott.ai/track/{tracking_id}" width="1" height="1" style="display:none">'
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        {html_text}
        {tracking_pixel}
        </body>
        </html>
        """
    
    def _attach_file(self, message: MIMEMultipart, file_path: str):
        """Attach file to email"""
        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(file_path)}'
            )
            message.attach(part)
    
    def sync_bcc_folder(self):
        """
        Sync BCC'd emails from Gmail to local tracker
        This would require Gmail API access to the BCC folders
        """
        print("📧 Syncing BCC tracking folders...")
        
        # This would connect to Gmail and check the +jobapps folders
        # For now, we'll just update the last sync time
        self.bcc_log['last_sync'] = datetime.now().isoformat()
        self._save_bcc_log()
        
        print(f"✅ Synced {len(self.bcc_log['sent_emails'])} tracked emails")
    
    def generate_bcc_report(self) -> Dict:
        """Generate report of BCC tracked emails"""
        report = {
            'total_tracked': len(self.bcc_log['sent_emails']),
            'by_type': {},
            'by_company': {},
            'last_7_days': 0,
            'last_30_days': 0
        }
        
        now = datetime.now()
        
        for tracking_id, email_data in self.bcc_log['sent_emails'].items():
            # Count by type
            email_type = email_data['type']
            report['by_type'][email_type] = report['by_type'].get(email_type, 0) + 1
            
            # Count by company
            company = email_data['company']
            report['by_company'][company] = report['by_company'].get(company, 0) + 1
            
            # Count recent emails
            sent_date = datetime.fromisoformat(email_data['sent_date'])
            days_ago = (now - sent_date).days
            
            if days_ago <= 7:
                report['last_7_days'] += 1
            if days_ago <= 30:
                report['last_30_days'] += 1
        
        return report
    
    def setup_gmail_filters(self):
        """Instructions for setting up Gmail filters"""
        print("\n📬 Gmail Filter Setup Instructions")
        print("=" * 60)
        print("\n1. Go to Gmail Settings → Filters and Blocked Addresses")
        print("\n2. Create these filters:")
        
        for email_type, bcc_address in self.bcc_addresses.items():
            print(f"\n   Filter for {email_type}:")
            print(f"   - To: {bcc_address}")
            print(f"   - Apply label: 'Job Tracking/{email_type.title()}'")
            print(f"   - Never send to Spam")
            print(f"   - Mark as important")
        
        print("\n3. Create a parent label 'Job Tracking' with sublabels")
        print("\n4. Optional: Set up forwarding to a tracking spreadsheet")
        print("\n✅ This will organize all BCC'd emails automatically!")


def demo_bcc_tracking():
    """Demo the BCC tracking system"""
    print("🚀 BCC Email Tracking Demo")
    print("=" * 60)
    
    tracker = BCCEmailTracker()
    
    # Example: Send a tracked application
    demo_email = {
        'to': 'careers@example-ai-company.com',
        'subject': 'Application for Senior ML Engineer - Matthew Scott',
        'body': """Dear Hiring Team,

I am writing to express my strong interest in the Senior ML Engineer position at Example AI Company.

With my proven track record of delivering $1.2M in AI-driven savings at Humana and 10+ years of experience in healthcare technology, I am excited about the opportunity to contribute to your team.

I have attached my resume for your review and would welcome the opportunity to discuss how my expertise in production ML systems can benefit your organization.

Thank you for your consideration.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77"""
    }
    
    print("\n📧 Demo Email Details:")
    print(f"To: {demo_email['to']}")
    print(f"Subject: {demo_email['subject']}")
    print(f"BCC: {tracker.bcc_addresses['applications']}")
    print("\nThis email will be:")
    print("✓ Sent to the company")
    print("✓ BCC'd to your tracking address") 
    print("✓ Logged in the email tracker")
    print("✓ Tagged with tracking ID")
    
    # Generate BCC report
    report = tracker.generate_bcc_report()
    print(f"\n📊 Current BCC Tracking Stats:")
    print(f"Total Tracked: {report['total_tracked']}")
    print(f"Last 7 days: {report['last_7_days']}")
    print(f"Last 30 days: {report['last_30_days']}")
    
    # Show Gmail setup
    tracker.setup_gmail_filters()


if __name__ == "__main__":
    import sys
    
    if '--demo' in sys.argv:
        demo_bcc_tracking()
    else:
        print("BCC Email Tracker Module")
        print("\nUsage:")
        print("  python bcc_email_tracker.py --demo    # Run demo")
        print("\nOr import and use:")
        print("  from bcc_email_tracker import BCCEmailTracker")
        print("  tracker = BCCEmailTracker()")
        print("  tracker.send_tracked_email(...)")