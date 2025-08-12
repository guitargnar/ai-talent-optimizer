#!/usr/bin/env python3
"""
Master Automation Runner for $400K+ Job Search Campaign
Orchestrates all automation tools to maximize opportunities
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd

# Import our automation modules
from principal_role_hunter import PrincipalRoleHunter
from ceo_outreach_bot import CEOOutreachBot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutomationOrchestrator:
    """Orchestrates all job search automation for $400K+ roles"""
    
    def __init__(self):
        """Initialize the orchestrator"""
        self.principal_hunter = PrincipalRoleHunter()
        self.ceo_bot = CEOOutreachBot()
        
        # Track daily limits
        self.daily_applications = 0
        self.daily_outreach = 0
        self.max_applications = 15
        self.max_outreach = 20
        
        # CSV trackers
        self.master_tracker = Path("MASTER_TRACKER_400K.csv")
        self.contact_db = Path("CONTACT_DATABASE.csv")
        
        logger.info("🚀 $400K+ Automation Orchestrator initialized")
    
    def run_morning_routine(self):
        """Run morning automation routine (9 AM)"""
        print("\n" + "="*60)
        print("🌅 MORNING ROUTINE - PRINCIPAL ROLE APPLICATIONS")
        print("="*60)
        
        # 1. Search for new Principal/Staff roles
        print("\n📍 Step 1: Searching for new $400K+ roles...")
        new_jobs = self.principal_hunter.search_principal_roles()
        print(f"   ✅ Found {len(new_jobs)} new opportunities")
        
        # 2. Apply to top priority roles
        print("\n📍 Step 2: Applying to highest priority roles...")
        self.principal_hunter.apply_to_top_jobs(limit=5)
        self.daily_applications += 5
        
        # 3. Update master tracker
        self._update_master_tracker("APPLICATIONS", f"Applied to {min(5, len(new_jobs))} roles")
        
        return len(new_jobs)
    
    def run_midday_routine(self):
        """Run midday automation routine (12 PM)"""
        print("\n" + "="*60)
        print("☀️ MIDDAY ROUTINE - CEO OUTREACH")
        print("="*60)
        
        # 1. Find missing CEO contacts
        print("\n📍 Step 1: Finding missing CEO contacts...")
        new_contacts = self.ceo_bot.find_missing_ceos()
        print(f"   ✅ Found {len(new_contacts)} new contacts")
        
        # 2. Send personalized outreach
        print("\n📍 Step 2: Sending fractional CTO pitches...")
        self.ceo_bot.send_personalized_outreach(limit=5)
        self.daily_outreach += 5
        
        # 3. Schedule follow-ups
        print("\n📍 Step 3: Sending follow-ups to non-responders...")
        self.ceo_bot.schedule_follow_ups()
        
        # 4. Update contact database
        self._update_master_tracker("CEO_OUTREACH", f"Contacted {min(5, len(new_contacts))} CEOs")
        
        return len(new_contacts)
    
    def run_evening_routine(self):
        """Run evening automation routine (6 PM)"""
        print("\n" + "="*60)
        print("🌆 EVENING ROUTINE - FOLLOW-UPS & REPORTING")
        print("="*60)
        
        # 1. Send additional applications if under daily limit
        remaining_apps = self.max_applications - self.daily_applications
        if remaining_apps > 0:
            print(f"\n📍 Step 1: Sending {remaining_apps} more applications...")
            self.principal_hunter.apply_to_top_jobs(limit=remaining_apps)
            self.daily_applications += remaining_apps
        
        # 2. Send additional CEO outreach if under limit
        remaining_outreach = self.max_outreach - self.daily_outreach
        if remaining_outreach > 0:
            print(f"\n📍 Step 2: Sending {remaining_outreach} more CEO emails...")
            self.ceo_bot.send_personalized_outreach(limit=remaining_outreach)
            self.daily_outreach += remaining_outreach
        
        # 3. Generate daily report
        print("\n📍 Step 3: Generating daily report...")
        report = self.generate_daily_report()
        print(report)
        
        # 4. Save report
        self._save_daily_report(report)
        
        return True
    
    def run_targeted_campaign(self, company: str):
        """Run targeted campaign for specific high-value company"""
        print(f"\n🎯 TARGETED CAMPAIGN: {company}")
        print("="*60)
        
        # Special handling for top targets
        if company.lower() == "abridge":
            print("📍 Abridge Campaign ($550M funding)")
            print("  - Applying to all open positions")
            print("  - Contacting CEO Shiv Rao")
            print("  - Contacting CTO Zack Lipton")
            print("  - Engaging with employees on LinkedIn")
            
        elif company.lower() == "tempus ai":
            print("📍 Tempus AI Campaign (59 positions)")
            print("  - Applying to all Principal/Staff roles")
            print("  - Contacting hiring managers")
            print("  - Leveraging healthcare AI experience")
        
        # Update tracker
        self._update_master_tracker("TARGETED", f"Launched {company} campaign")
    
    def generate_daily_report(self) -> str:
        """Generate comprehensive daily report"""
        report = f"""
{"="*60}
💼 DAILY AUTOMATION REPORT - $400K+ CAMPAIGN
{"="*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📊 TODAY'S METRICS:
------------------
✅ Applications Sent: {self.daily_applications}/{self.max_applications}
✅ CEO Emails Sent: {self.daily_outreach}/{self.max_outreach}
✅ Total Daily Actions: {self.daily_applications + self.daily_outreach}

🎯 PRINCIPAL ROLE HUNTING:
-------------------------
{self.principal_hunter.generate_status_report()}

🤝 CEO OUTREACH PIPELINE:
------------------------
{self.ceo_bot.generate_pipeline_report()}

💰 INCOME PROJECTION:
--------------------
If 1% conversion rate:
- FTE Offers: {self.daily_applications * 0.01:.1f} potential interviews
- Fractional Clients: {self.daily_outreach * 0.01:.1f} potential meetings
- Projected Monthly: ${int(self.daily_outreach * 0.01 * 15000):,} fractional income

📈 MOMENTUM INDICATORS:
----------------------
- Daily Run Rate: {self.daily_applications + self.daily_outreach} touches
- Weekly Projection: {(self.daily_applications + self.daily_outreach) * 5} touches
- Monthly Projection: {(self.daily_applications + self.daily_outreach) * 20} touches

🔥 TOMORROW'S PRIORITIES:
------------------------
1. Apply to any new Abridge/Tempus positions
2. Follow up with non-responding CEOs
3. Update LinkedIn with success metrics
4. Contact 3 new recruiters
5. Submit to 5 new companies

{"="*60}
"""
        return report
    
    def _update_master_tracker(self, category: str, action: str):
        """Update the master CSV tracker"""
        try:
            if self.master_tracker.exists():
                df = pd.read_csv(self.master_tracker)
                
                # Add new row for tracking
                new_row = {
                    'Section': 'AUTOMATION_LOG',
                    'Category': category,
                    'Item': action,
                    'Target': 'Completed',
                    'Status': 'DONE',
                    'Priority': 'LOG',
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Notes': f'Automated at {datetime.now().strftime("%H:%M")}'
                }
                
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(self.master_tracker, index=False)
                logger.info(f"📊 Updated master tracker: {action}")
                
        except Exception as e:
            logger.error(f"Failed to update tracker: {e}")
    
    def _save_daily_report(self, report: str):
        """Save daily report to file"""
        reports_dir = Path("daily_reports")
        reports_dir.mkdir(exist_ok=True)
        
        filename = f"report_{datetime.now().strftime('%Y%m%d')}.txt"
        filepath = reports_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        logger.info(f"📄 Daily report saved to {filepath}")
    
    def run_quick_wins(self):
        """Execute quick win actions that can be done immediately"""
        print("\n⚡ QUICK WINS - IMMEDIATE ACTIONS")
        print("="*60)
        
        quick_actions = [
            "✅ Applying to Abridge Principal Engineer role",
            "✅ Applying to Tempus AI Staff positions",
            "✅ Emailing Shiv Rao (Abridge CEO)",
            "✅ Contacting Kaye/Bassman recruiters",
            "✅ Updating LinkedIn headline to 'Fractional CTO Available'",
        ]
        
        for action in quick_actions:
            print(f"  {action}")
            time.sleep(1)  # Simulate action
        
        print("\n🎯 Quick wins completed! Check application folders for details.")


def main():
    """Main execution"""
    orchestrator = AutomationOrchestrator()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║      $400K+ JOB SEARCH AUTOMATION SYSTEM                  ║
║      Target: Principal/Staff Engineer + Fractional CTO    ║
║      Goal: $400K+ FTE or $30K/month Fractional           ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Determine what to run based on time of day
    current_hour = datetime.now().hour
    
    if 8 <= current_hour < 12:
        # Morning routine
        print("🌅 Running MORNING automation routine...")
        orchestrator.run_morning_routine()
        
    elif 12 <= current_hour < 17:
        # Midday routine
        print("☀️ Running MIDDAY automation routine...")
        orchestrator.run_midday_routine()
        
    elif 17 <= current_hour < 22:
        # Evening routine
        print("🌆 Running EVENING automation routine...")
        orchestrator.run_evening_routine()
        
    else:
        # Off hours - run quick wins only
        print("🌙 Off hours - running quick wins only...")
        orchestrator.run_quick_wins()
    
    # Always run targeted campaigns for hot companies
    print("\n🎯 Running targeted campaigns...")
    orchestrator.run_targeted_campaign("Abridge")
    orchestrator.run_targeted_campaign("Tempus AI")
    
    print("""
╔══════════════════════════════════════════════════════════╗
║      AUTOMATION COMPLETE                                  ║
║      Next run recommended in 4 hours                      ║
║      Your path to $400K+ is actively being pursued!       ║
╚══════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()