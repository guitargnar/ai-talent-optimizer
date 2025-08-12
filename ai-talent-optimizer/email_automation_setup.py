#!/usr/bin/env python3
"""
Email Automation Setup - Gmail SMTP Configuration
Automate follow-ups and application tracking
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Optional
import schedule
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_gmail_automation():
    """Complete Gmail setup guide"""
    
    print("📧 EMAIL AUTOMATION SETUP GUIDE")
    print("=" * 60)
    
    print("\n🔐 STEP 1: Enable 2-Factor Authentication")
    print("-" * 40)
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Click on '2-Step Verification'")
    print("3. Follow the setup process")
    print("4. Keep your phone handy for verification")
    
    print("\n🔑 STEP 2: Generate App Password")
    print("-" * 40)
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Select app: 'Mail'")
    print("3. Select device: 'Other' → Name it 'Career Automation'")
    print("4. Copy the 16-character password")
    print("5. Save it securely (you won't see it again!)")
    
    print("\n📝 STEP 3: Create .env File")
    print("-" * 40)
    print("Add these to your .env file:\n")
    
    env_template = """# Email Configuration
EMAIL_ADDRESS=matthewdscott7@gmail.com
EMAIL_APP_PASSWORD=your-16-char-app-password
EMAIL_NAME=Matthew David Scott

# Optional: Backup email
BACKUP_EMAIL=your.backup@email.com

# Email Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
"""
    
    print(env_template)
    
    print("\n✅ STEP 4: Test Configuration")
    print("-" * 40)
    print("Run: python email_automation_setup.py --test")
    
    print("\n🚀 STEP 5: Start Using")
    print("-" * 40)
    print("The email automation system will:")
    print("- Send application confirmations")
    print("- Schedule follow-ups (3, 7, 14 days)")
    print("- Track email status")
    print("- Never spam (max 3 follow-ups)")


class EmailAutomation:
    def __init__(self):
        self.email = os.getenv('EMAIL_ADDRESS', 'matthewdscott7@gmail.com')
        self.password = os.getenv('EMAIL_APP_PASSWORD')
        self.name = os.getenv('EMAIL_NAME', 'Matthew David Scott')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # Track sent emails
        self.sent_emails = self._load_sent_history()
        
    def _load_sent_history(self) -> Dict:
        """Load history of sent emails"""
        if os.path.exists('email_history.json'):
            with open('email_history.json', 'r') as f:
                return json.load(f)
        return {}
    
    def _save_sent_history(self):
        """Save email history"""
        with open('email_history.json', 'w') as f:
            json.dump(self.sent_emails, f, indent=2)
    
    def test_connection(self) -> bool:
        """Test Gmail SMTP connection"""
        if not self.password:
            print("❌ Email app password not found in .env file")
            return False
            
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                print(f"✅ Successfully connected to Gmail as {self.email}")
                return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\nTroubleshooting:")
            print("1. Verify 2-factor authentication is enabled")
            print("2. Check app password is correct (16 characters, no spaces)")
            print("3. Ensure 'Less secure app access' is OFF (we use app passwords)")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   html_body: Optional[str] = None, attachments: List[str] = None) -> bool:
        """Send email with optional HTML and attachments"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.name} <{self.email}>"
            message['To'] = to_email
            message['Subject'] = subject
            
            # Add text version
            message.attach(MIMEText(body, 'plain'))
            
            # Add HTML version if provided
            if html_body:
                message.attach(MIMEText(html_body, 'html'))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        self._attach_file(message, file_path)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                server.send_message(message)
            
            # Track sent email
            self._track_email(to_email, subject)
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
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
    
    def _track_email(self, to_email: str, subject: str):
        """Track sent emails to prevent spam"""
        key = f"{to_email}_{subject[:30]}"
        if key not in self.sent_emails:
            self.sent_emails[key] = []
        
        self.sent_emails[key].append({
            'sent_at': datetime.now().isoformat(),
            'to': to_email,
            'subject': subject
        })
        
        self._save_sent_history()
    
    def send_application_confirmation(self, company: str, position: str, 
                                    contact_email: Optional[str] = None) -> bool:
        """Send confirmation after applying"""
        subject = f"Application Submitted: {position} at {company}"
        
        body = f"""Dear Hiring Team at {company},

I wanted to confirm that I have submitted my application for the {position} position through your careers portal.

I am very excited about this opportunity and believe my experience delivering $1.2M in AI-driven savings at Humana makes me an excellent fit for your team.

Key highlights from my application:
• 10+ years of healthcare technology experience
• Proven ML/AI implementation with measurable business impact
• Strong Python and production deployment expertise
• Successful remote work track record

I am available for interviews at your convenience and look forward to discussing how I can contribute to {company}'s continued success.

Thank you for considering my application.

Best regards,
{self.name}
{self.email}
502-345-5252
linkedin.com/in/mscott77"""
        
        # Send to contact email if provided, otherwise save as draft
        if contact_email:
            return self.send_email(contact_email, subject, body)
        else:
            # Save as template
            with open(f'email_template_{company}_{datetime.now().strftime("%Y%m%d")}.txt', 'w') as f:
                f.write(f"To: [Hiring Manager Email]\n")
                f.write(f"Subject: {subject}\n\n")
                f.write(body)
            logger.info(f"Email template saved for {company}")
            return True
    
    def schedule_follow_up(self, company: str, position: str, 
                          applied_date: datetime, follow_up_number: int = 1) -> str:
        """Generate follow-up email content"""
        
        days_since = (datetime.now() - applied_date).days
        
        if follow_up_number == 1:  # 3-day follow-up
            subject = f"Following Up: {position} Application - {self.name}"
            body = f"""Dear Hiring Team,

I wanted to follow up on my application for the {position} role submitted on {applied_date.strftime('%B %d')}.

I remain very interested in contributing my ML expertise and proven track record of delivering enterprise-scale AI solutions to {company}.

Since applying, I've been researching {company}'s recent initiatives and am particularly excited about [specific project/news]. My experience with [relevant skill] would allow me to make an immediate impact.

I'm available for an interview at your convenience and would be happy to provide any additional information needed.

Best regards,
{self.name}"""
        
        elif follow_up_number == 2:  # 7-day follow-up
            subject = f"Continued Interest: {position} at {company}"
            body = f"""Dear Hiring Team,

I hope this message finds you well. I'm writing to reiterate my strong interest in the {position} position.

With my background in building production ML systems that delivered $1.2M in savings at Humana, I'm confident I can bring similar value to {company}.

I understand you may be reviewing many applications. If there's any additional information that would be helpful in evaluating my candidacy, please let me know.

Looking forward to the opportunity to discuss this role.

Best regards,
{self.name}"""
        
        else:  # 14-day final follow-up
            subject = f"Final Follow-Up: {position} Application"
            body = f"""Dear Hiring Team,

I wanted to send a final note regarding my application for the {position} role.

While I understand you may have many qualified candidates, I remain highly interested in this opportunity. My unique combination of healthcare AI expertise and proven business impact makes me particularly well-suited for this position.

If the position has been filled, I would appreciate knowing so I can focus my search elsewhere. However, if you're still in the selection process, I'm very much available and eager to contribute to {company}'s success.

Thank you for your time and consideration.

Best regards,
{self.name}"""
        
        return subject, body
    
    def create_email_templates(self):
        """Create all email templates"""
        templates = {
            'application_confirmation': {
                'subject': 'Application Submitted: {position} at {company}',
                'body': self.send_application_confirmation('{{company}}', '{{position}}')
            },
            'thank_you_post_interview': {
                'subject': 'Thank You - {position} Interview',
                'body': """Dear {interviewer_name},

Thank you for taking the time to discuss the {position} role with me today. I enjoyed our conversation about {specific_topic} and am even more excited about the opportunity to contribute to {company}.

Your insights about {company_initiative} particularly resonated with me, as they align closely with my experience {relevant_experience}.

I look forward to the next steps in the process and the opportunity to join your team.

Best regards,
{self.name}"""
            },
            'networking_outreach': {
                'subject': 'Connecting from {source} - ML/AI Professional',
                'body': """Hi {name},

I came across your profile while researching {company}'s impressive work in {area}. As someone with 10+ years in healthcare AI who recently delivered $1.2M in savings through ML automation, I'm very interested in learning more about your team's approach to {specific_topic}.

Would you be open to a brief 15-minute call to discuss {company}'s ML initiatives? I'd be happy to share insights from my experience building production AI systems in regulated environments.

Best regards,
{self.name}
LinkedIn: linkedin.com/in/mscott77"""
            }
        }
        
        # Save templates
        with open('email_templates.json', 'w') as f:
            json.dump(templates, f, indent=2)
        
        logger.info("Email templates created in email_templates.json")
        return templates
    
    def get_pending_follow_ups(self, applications: List[Dict]) -> List[Dict]:
        """Get list of follow-ups due"""
        pending = []
        now = datetime.now()
        
        for app in applications:
            if 'applied_date' not in app:
                continue
                
            applied = datetime.fromisoformat(app['applied_date'])
            days_since = (now - applied).days
            
            # Check if follow-up is due
            if days_since >= 3 and not app.get('follow_up_1_sent'):
                pending.append({
                    'company': app['company'],
                    'position': app['position'],
                    'follow_up_number': 1,
                    'applied_date': applied
                })
            elif days_since >= 7 and not app.get('follow_up_2_sent'):
                pending.append({
                    'company': app['company'],
                    'position': app['position'],
                    'follow_up_number': 2,
                    'applied_date': applied
                })
            elif days_since >= 14 and not app.get('follow_up_3_sent'):
                pending.append({
                    'company': app['company'],
                    'position': app['position'],
                    'follow_up_number': 3,
                    'applied_date': applied
                })
        
        return pending


def test_email_system():
    """Test the email automation system"""
    from dotenv import load_dotenv
    load_dotenv()
    
    automation = EmailAutomation()
    
    print("\n🧪 Testing Email System")
    print("-" * 40)
    
    # Test connection
    if automation.test_connection():
        print("\n✅ Connection successful!")
        
        # Create templates
        print("\n📝 Creating email templates...")
        automation.create_email_templates()
        
        # Test sending
        test_email = input("\nEnter email for test (or press Enter to skip): ")
        if test_email:
            success = automation.send_email(
                test_email,
                "Test: Career Automation System",
                "This is a test email from your career automation system.\n\nIf you received this, your email automation is working correctly!",
                html_body="<h2>Test Email</h2><p>Your career automation email system is <b>working correctly</b>!</p>"
            )
            
            if success:
                print(f"✅ Test email sent to {test_email}")
            else:
                print("❌ Failed to send test email")
    else:
        print("\n❌ Connection failed. Please check your setup.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_email_system()
    else:
        setup_gmail_automation()
        print("\n💡 To test your setup, run:")
        print("   python email_automation_setup.py --test")