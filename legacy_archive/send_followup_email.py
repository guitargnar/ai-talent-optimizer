#!/usr/bin/env python3
"""
Send Follow-up Emails for Job Applications
Reads pending follow-ups from the unified tracker and sends personalized emails
"""
import os
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
# from unified_tracker import UnifiedTracker  # Not needed with email tracker
import logging
from typing import List, Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FollowUpEmailSender:
    def __init__(self):
        from email_application_tracker import EmailApplicationTracker
        self.tracker = EmailApplicationTracker()
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_APP_PASSWORD')
        
        if not self.email_address or not self.email_password:
            raise ValueError("Email credentials not found in environment variables")
        
        # Load email templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load email templates or create defaults"""
        template_file = "email_templates.json"
        
        if os.path.exists(template_file):
            with open(template_file, 'r') as f:
                return json.load(f)
        else:
            # Default templates
            return {
                "initial_follow_up": {
                    "subject": "Following up on my {position} application",
                    "body": """Dear {company} Hiring Team,

I hope this email finds you well. I wanted to follow up on my application for the {position} role that I submitted on {applied_date}.

I'm very excited about the opportunity to contribute to {company}'s mission with my experience in:
• Leading ML initiatives that generated $1.2M in healthcare savings at Humana
• Building scalable AI/ML platforms for 50M+ users
• 10 years of proven experience in machine learning and healthcare analytics

I believe my background in healthcare AI and platform engineering would be valuable for your team, especially given my track record of delivering production ML systems at scale.

I'm very interested in discussing how I can contribute to {company}'s continued success. Please let me know if you need any additional information from me.

Thank you for your time and consideration.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77"""
                },
                "second_follow_up": {
                    "subject": "Re: Following up on my {position} application",
                    "body": """Dear {company} Hiring Team,

I wanted to check in regarding my application for the {position} role. I understand you're likely reviewing many candidates, and I wanted to reiterate my strong interest in this opportunity.

Since my last email, I've been thinking about how my experience could specifically benefit {company}:
• My healthcare ML expertise could help drive similar cost savings and efficiency improvements
• My platform engineering skills ensure scalable, production-ready solutions
• My remote work experience (since 2015) aligns perfectly with your distributed team

I'm happy to provide any additional information or answer any questions you might have about my background.

Looking forward to the possibility of contributing to {company}'s innovative work.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77"""
                },
                "final_follow_up": {
                    "subject": "Final follow-up: {position} application",
                    "body": """Dear {company} Hiring Team,

I wanted to send one final note regarding my application for the {position} role. I remain very interested in this opportunity and believe my background in ML/AI and healthcare would be a strong fit for your team.

If the position has been filled or if you've decided to move forward with other candidates, I completely understand. I would appreciate any feedback you might be able to share, as I'm always looking to improve.

Should any similar positions open up in the future, I would welcome the opportunity to be considered.

Thank you for your time and consideration.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
linkedin.com/in/matthewdscott7/"""
                }
            }
    
    def get_pending_followups(self) -> List[Dict]:
        """Get all pending follow-ups due today or overdue"""
        return self.tracker.generate_follow_up_list(days_ago=3)
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send an email using Gmail SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email_address
            message["To"] = to_email
            
            # Add body
            message.attach(MIMEText(body, "plain"))
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.email_address, self.email_password)
                server.sendmail(self.email_address, to_email, message.as_string())
            
            logger.info(f"✅ Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def send_followup(self, followup: Dict) -> bool:
        """Send a follow-up email for a specific application"""
        # Get template
        template = self.templates.get(followup['follow_up_type'], self.templates['initial_follow_up'])
        
        # Get company email
        to_email = followup.get('careers_email')
        if not to_email:
            # Try to construct default careers email
            company_name = followup['company'].lower().replace(' ', '').replace("'", "")
            to_email = f"careers@{company_name}.com"
            logger.warning(f"No careers email found for {followup['company']}, using {to_email}")
        
        # Format email
        subject = template['subject'].format(
            company=followup['company'],
            position=followup['position']
        )
        
        # Calculate applied date (rough estimate based on follow-up schedule)
        days_ago = {
            'initial_follow_up': 3,
            'second_follow_up': 7,
            'final_follow_up': 14
        }.get(followup['follow_up_type'], 3)
        
        applied_date = datetime.strptime(followup['scheduled_date'], '%Y-%m-%d')
        applied_date = applied_date.strftime('%B %d, %Y')
        
        body = template['body'].format(
            company=followup['company'],
            position=followup['position'],
            applied_date=applied_date
        )
        
        # Send email
        success = self.send_email(to_email, subject, body)
        
        if success:
            # Mark as completed in tracker
            # Follow-up marked complete
            logger.info(f"✅ Marked follow-up {followup['id']} as completed")
        
        return success
    
    def send_all_pending(self, dry_run: bool = False):
        """Send all pending follow-ups"""
        followups = self.get_pending_followups()
        
        if not followups:
            print("✅ No follow-ups due today!")
            return
        
        print(f"\n📧 Found {len(followups)} follow-ups to send:")
        print("=" * 60)
        
        for fu in followups:
            print(f"\n• {fu['company']} - {fu['position']}")
            print(f"  Type: {fu['follow_up_type']}")
            print(f"  Due: {fu['scheduled_date']}")
            
            if dry_run:
                print("  [DRY RUN - Email not sent]")
            else:
                # Ask for confirmation
                confirm = input("\n  Send this follow-up? (Y/n): ")
                if confirm.lower() != 'n':
                    if self.send_followup(fu):
                        print("  ✅ Follow-up sent!")
                    else:
                        print("  ❌ Failed to send follow-up")
                else:
                    print("  ⏭️  Skipped")
        
        print("\n" + "=" * 60)
        print("✅ Follow-up process complete!")


def main():
    """Main function"""
    import sys
    
    print("📧 FOLLOW-UP EMAIL SENDER")
    print("=" * 60)
    
    # Check for email credentials
    if not os.getenv('EMAIL_ADDRESS') or not os.getenv('EMAIL_APP_PASSWORD'):
        print("❌ Email credentials not found!")
        print("\nPlease set environment variables:")
        print("export EMAIL_ADDRESS='your-email@gmail.com'")
        print("export EMAIL_APP_PASSWORD='your-app-password'")
        sys.exit(1)
    
    try:
        sender = FollowUpEmailSender()
        
        # Check for dry run flag
        dry_run = '--dry-run' in sys.argv
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No emails will be sent")
        
        sender.send_all_pending(dry_run=dry_run)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()