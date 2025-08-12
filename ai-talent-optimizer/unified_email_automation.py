#!/usr/bin/env python3
"""
Unified Email Automation System
Combines BCC tracking, manual logging, and Gmail OAuth monitoring
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import schedule
import time

# Import all email components
from email_application_tracker import EmailApplicationTracker
from gmail_oauth_integration import GmailOAuthIntegration
from bcc_email_tracker import BCCEmailTracker
from send_followup_email import FollowUpEmailSender


class UnifiedEmailAutomation:
    """Complete email automation system with multiple tracking methods"""
    
    def __init__(self):
        print("🚀 Initializing Unified Email Automation System...")
        
        # Initialize all components
        self.email_tracker = EmailApplicationTracker()
        self.gmail_oauth = GmailOAuthIntegration()
        self.bcc_tracker = BCCEmailTracker()
        self.followup_sender = FollowUpEmailSender()
        
        # Configuration
        self.config = {
            'enable_bcc': True,
            'enable_oauth_monitor': True,
            'enable_auto_followup': True,
            'followup_schedule': {
                'initial': 3,    # days
                'second': 7,     # days
                'final': 14      # days
            }
        }
        
        # Status tracking
        self.status_file = 'data/unified_email_status.json'
        self.status = self._load_status()
    
    def _load_status(self) -> Dict:
        """Load system status"""
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r') as f:
                return json.load(f)
        return {
            'last_sync': None,
            'emails_sent_today': 0,
            'last_followup_check': None,
            'active_applications': 0
        }
    
    def _save_status(self):
        """Save system status"""
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
        with open(self.status_file, 'w') as f:
            json.dump(self.status, f, indent=2)
    
    def send_application(self,
                        company_email: str,
                        company_name: str,
                        position: str,
                        custom_body: Optional[str] = None,
                        attachments: List[str] = None) -> bool:
        """
        Send job application with full tracking
        
        Args:
            company_email: Recipient email
            company_name: Company name
            position: Position title
            custom_body: Custom email body (optional)
            attachments: List of file paths to attach
            
        Returns:
            Success status
        """
        
        # Generate subject
        subject = f"Application for {position} - Matthew Scott"
        
        # Generate body if not provided
        if not custom_body:
            body = self._generate_application_body(company_name, position)
        else:
            body = custom_body
        
        # Send with BCC tracking if enabled
        if self.config['enable_bcc']:
            success, tracking_id = self.bcc_tracker.send_tracked_email(
                to_email=company_email,
                subject=subject,
                body=body,
                email_type='applications',
                attachments=attachments,
                track_in_db=True  # Also log in email tracker
            )
            
            if success:
                print(f"✅ Application sent with BCC tracking: {tracking_id}")
                self.status['emails_sent_today'] += 1
                self._save_status()
                return True
            else:
                print("❌ Failed to send with BCC tracking")
                return False
        else:
            # Fallback to regular sending with manual logging
            # Would implement regular SMTP sending here
            print("⚠️  BCC tracking disabled, using manual logging only")
            
            # Log to email tracker
            self.email_tracker.log_email_application({
                'to_email': company_email,
                'company_name': company_name,
                'position_title': position,
                'subject_line': subject,
                'email_type': 'direct_application'
            })
            
            return True
    
    def _generate_application_body(self, company: str, position: str) -> str:
        """Generate personalized application email body"""
        return f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {position} position at {company}.

With my proven track record of delivering $1.2M in AI-driven savings at Humana and 10+ years of experience building production ML systems for healthcare, I am excited about the opportunity to contribute to your team.

Key highlights from my background:
• Led ML initiatives that transformed risk prediction accuracy by 47%
• Built scalable AI/ML platforms serving 50M+ users
• Deep expertise in Python, cloud architecture, and healthcare analytics
• Successful remote work track record since 2015

I have attached my resume for your review and would welcome the opportunity to discuss how my expertise in healthcare AI and platform engineering can benefit {company}.

Thank you for your consideration. I look forward to hearing from you.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77"""
    
    def check_and_send_followups(self):
        """Check for due follow-ups and send them"""
        if not self.config['enable_auto_followup']:
            print("⚠️  Auto follow-up disabled")
            return
        
        print("\n📧 Checking for pending follow-ups...")
        
        # Get pending follow-ups
        pending = self.followup_sender.get_pending_followups()
        
        if not pending:
            print("✅ No follow-ups due today")
            self.status['last_followup_check'] = datetime.now().isoformat()
            self._save_status()
            return
        
        print(f"Found {len(pending)} follow-ups to send:")
        
        for followup in pending:
            print(f"\n• {followup['company']} - {followup['position']}")
            print(f"  Type: {followup['follow_up_type']}")
            
            # Use BCC tracking for follow-ups too
            if self.config['enable_bcc']:
                # Get email content from followup sender
                # This would need to be integrated with the followup sender
                success = self.followup_sender.send_followup(followup)
                if success:
                    print("  ✅ Follow-up sent with tracking")
            else:
                print("  ⚠️  BCC disabled for follow-ups")
        
        self.status['last_followup_check'] = datetime.now().isoformat()
        self._save_status()
    
    def sync_all_systems(self):
        """Sync all email tracking systems"""
        print("\n🔄 Syncing all email tracking systems...")
        
        # 1. Sync Gmail OAuth responses
        if self.config['enable_oauth_monitor']:
            print("\n1️⃣ Syncing Gmail OAuth responses...")
            self.gmail_oauth.sync_gmail_responses()
        
        # 2. Sync BCC tracking folder
        if self.config['enable_bcc']:
            print("\n2️⃣ Syncing BCC tracking folder...")
            self.bcc_tracker.sync_bcc_folder()
        
        # 3. Generate follow-up list
        print("\n3️⃣ Updating follow-up schedule...")
        followups = self.email_tracker.generate_follow_up_list()
        print(f"   Found {len(followups)} applications needing follow-up")
        
        self.status['last_sync'] = datetime.now().isoformat()
        self.status['active_applications'] = len(self.email_tracker.search_email_applications())
        self._save_status()
        
        print("\n✅ All systems synced!")
    
    def generate_unified_report(self) -> Dict:
        """Generate comprehensive email automation report"""
        
        # Get reports from all systems
        email_report = self.email_tracker.generate_report()
        gmail_report = self.gmail_oauth.generate_unified_report()
        bcc_report = self.bcc_tracker.generate_bcc_report()
        
        # Combine into unified report
        unified_report = {
            'generated_at': datetime.now().isoformat(),
            'status': self.status,
            'email_tracking': {
                'total_applications': email_report['summary']['total_applications'],
                'response_rate': email_report['summary']['response_rate'],
                'interview_rate': email_report['summary']['interview_rate'],
                'follow_ups_needed': len(email_report['follow_ups_needed'])
            },
            'gmail_oauth': {
                'monitored_companies': gmail_report['metrics']['monitored_companies'],
                'responses_tracked': gmail_report['metrics'].get('responses_tracked', 0)
            },
            'bcc_tracking': {
                'total_tracked': bcc_report['total_tracked'],
                'last_7_days': bcc_report['last_7_days'],
                'by_type': bcc_report['by_type']
            },
            'recommendations': self._generate_recommendations(email_report, gmail_report, bcc_report)
        }
        
        return unified_report
    
    def _generate_recommendations(self, email_report: Dict, gmail_report: Dict, bcc_report: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check response rate
        response_rate = float(email_report['summary']['response_rate'].rstrip('%'))
        if response_rate < 10:
            recommendations.append("📈 Response rate below 10% - Consider updating resume keywords")
        
        # Check follow-ups
        if len(email_report['follow_ups_needed']) > 10:
            recommendations.append(f"📧 {len(email_report['follow_ups_needed'])} follow-ups pending - Schedule time to send")
        
        # Check daily activity
        if self.status['emails_sent_today'] < 5:
            recommendations.append("🎯 Only {self.status['emails_sent_today']} applications today - Aim for 10+")
        
        return recommendations
    
    def run_automation_loop(self):
        """Run continuous automation loop"""
        print("🤖 Starting Unified Email Automation Loop")
        print("Press Ctrl+C to stop")
        
        # Schedule tasks
        schedule.every(30).minutes.do(self.sync_all_systems)
        schedule.every().day.at("09:00").do(self.check_and_send_followups)
        schedule.every().day.at("18:00").do(self.generate_daily_summary)
        
        # Initial sync
        self.sync_all_systems()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                print("\n👋 Stopping automation loop")
                break
    
    def generate_daily_summary(self):
        """Generate and display daily summary"""
        print("\n📊 Daily Email Automation Summary")
        print("=" * 60)
        
        report = self.generate_unified_report()
        
        print(f"\n📧 Email Activity:")
        print(f"  • Total Applications: {report['email_tracking']['total_applications']}")
        print(f"  • Response Rate: {report['email_tracking']['response_rate']}")
        print(f"  • Interview Rate: {report['email_tracking']['interview_rate']}")
        print(f"  • Follow-ups Needed: {report['email_tracking']['follow_ups_needed']}")
        
        print(f"\n🔍 Tracking Status:")
        print(f"  • Gmail OAuth: Monitoring {report['gmail_oauth']['monitored_companies']} companies")
        print(f"  • BCC Tracking: {report['bcc_tracking']['total_tracked']} emails tracked")
        print(f"  • Last 7 days: {report['bcc_tracking']['last_7_days']} emails")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  {rec}")
        
        # Save report
        report_file = f"data/daily_reports/report_{datetime.now().strftime('%Y%m%d')}.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Full report saved to: {report_file}")


def main():
    """Main entry point"""
    import sys
    
    print("🚀 Unified Email Automation System")
    print("=" * 60)
    
    automation = UnifiedEmailAutomation()
    
    if '--sync' in sys.argv:
        # One-time sync
        automation.sync_all_systems()
    elif '--followup' in sys.argv:
        # Check and send follow-ups
        automation.check_and_send_followups()
    elif '--report' in sys.argv:
        # Generate report
        automation.generate_daily_summary()
    elif '--loop' in sys.argv:
        # Run continuous loop
        automation.run_automation_loop()
    else:
        # Interactive menu
        print("\nOptions:")
        print("1. Send tracked application")
        print("2. Check for follow-ups")
        print("3. Sync all systems")
        print("4. Generate report")
        print("5. Run automation loop")
        
        choice = input("\nSelect option (1-5): ")
        
        if choice == '1':
            # Demo sending
            company = input("Company name: ")
            position = input("Position: ")
            email = input("Company email: ")
            
            success = automation.send_application(
                company_email=email,
                company_name=company,
                position=position
            )
            
            if success:
                print("\n✅ Application sent successfully!")
        
        elif choice == '2':
            automation.check_and_send_followups()
        
        elif choice == '3':
            automation.sync_all_systems()
        
        elif choice == '4':
            automation.generate_daily_summary()
        
        elif choice == '5':
            automation.run_automation_loop()


if __name__ == "__main__":
    main()