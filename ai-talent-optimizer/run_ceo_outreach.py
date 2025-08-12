#!/usr/bin/env python3
"""
CEO Outreach Campaign Runner
Comprehensive system to land $450K+ positions through direct CEO/CTO contact

This script orchestrates the complete CEO outreach campaign targeting:
- Genesis AI ($480K)
- Inworld AI ($475K) 
- Adyen ($465K)
- Lime ($465K)
- Thumbtack ($450K)

Total potential value: $2.34M annually
"""

import sys
from pathlib import Path
import logging
from datetime import datetime
import argparse

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from core.ceo_outreach_engine import CEOOutreachEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ceo_outreach.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CEOOutreachCampaign:
    """Complete CEO outreach campaign orchestrator"""
    
    def __init__(self):
        """Initialize the campaign"""
        self.engine = CEOOutreachEngine()
        self.campaign_start = datetime.now()
        
        print("🎯 CEO OUTREACH CAMPAIGN - LANDING $450K+ POSITIONS")
        print("=" * 60)
        print("Target Companies:")
        print("• Genesis AI - Principal ML Research Engineer ($480K)")
        print("• Inworld AI - Staff/Principal ML Engineer ($475K)")
        print("• Adyen - Staff Engineer ML ($465K)")
        print("• Lime - Principal ML Engineer ($465K)") 
        print("• Thumbtack - Principal ML Infrastructure ($450K)")
        print(f"\n💰 Total Potential Annual Value: $2.34M")
        print(f"📅 Campaign Started: {self.campaign_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def run_full_campaign(self):
        """Execute the complete CEO outreach campaign"""
        try:
            # Phase 1: Research CEO contacts
            print("\n🔍 PHASE 1: CEO CONTACT RESEARCH")
            print("-" * 40)
            contacts = self.engine.research_all_targets()
            print(f"✅ Research Complete: {len(contacts)} decision-makers identified")
            
            if len(contacts) == 0:
                print("⚠️  No contacts found. Check internet connection and retry.")
                return False
            
            # Phase 2: Send initial outreach
            print("\n📧 PHASE 2: INITIAL CEO OUTREACH") 
            print("-" * 40)
            outreach_results = self.engine.send_ceo_outreach(limit=5, priority_threshold=50)
            
            sent_count = len(outreach_results['sent'])
            failed_count = len(outreach_results['failed'])
            
            print(f"✅ Outreach Sent: {sent_count} CEOs")
            print(f"❌ Failed: {failed_count} CEOs")
            
            if outreach_results['sent']:
                print("📤 Messages sent to:")
                for company in outreach_results['sent']:
                    print(f"   • {company}")
            
            if outreach_results['failed']:
                print("⚠️ Failed to send to:")
                for company in outreach_results['failed']:
                    print(f"   • {company}")
            
            # Phase 3: Schedule follow-ups for existing contacts
            print("\n📮 PHASE 3: FOLLOW-UP MANAGEMENT")
            print("-" * 40)
            follow_ups = self.engine.schedule_follow_ups()
            print(f"✅ Follow-ups Scheduled: {len(follow_ups)}")
            
            # Phase 4: Generate comprehensive report
            print("\n📊 PHASE 4: CAMPAIGN REPORT")
            print("-" * 40)
            report = self.engine.generate_outreach_report()
            print(report)
            
            # Save report to file
            self._save_campaign_report(report)
            
            # Campaign summary
            self._print_campaign_summary(contacts, outreach_results, follow_ups)
            
            return True
            
        except Exception as e:
            logger.error(f"Campaign failed: {e}")
            print(f"\n❌ Campaign Error: {e}")
            return False
    
    def run_research_only(self):
        """Run CEO research phase only"""
        print("\n🔍 CEO RESEARCH PHASE")
        print("-" * 30)
        
        contacts = self.engine.research_all_targets()
        
        print(f"\n✅ Research Results: {len(contacts)} contacts discovered")
        
        if contacts:
            print("\n📋 Contact Summary:")
            for contact in contacts:
                confidence = "🔵 High" if contact.confidence_level > 0.7 else "🟡 Medium" if contact.confidence_level > 0.4 else "🔴 Low"
                print(f"   • {contact.company}: {contact.name or 'TBD'} - {confidence}")
        
        # Generate research report
        report = self.engine.generate_outreach_report()
        print(f"\n{report}")
        
        return contacts
    
    def run_outreach_only(self, limit=5):
        """Send outreach to existing researched contacts"""
        print(f"\n📧 CEO OUTREACH PHASE (Limit: {limit})")
        print("-" * 30)
        
        results = self.engine.send_ceo_outreach(limit=limit)
        
        sent_count = len(results['sent'])
        print(f"✅ Outreach sent to {sent_count} CEOs")
        
        if results['sent']:
            print("📤 Companies contacted:")
            for company in results['sent']:
                print(f"   • {company}")
        
        if results['failed']:
            print("❌ Failed to contact:")
            for company in results['failed']:
                print(f"   • {company}")
        
        return results
    
    def run_follow_up(self):
        """Send follow-up messages only"""
        print("\n📮 FOLLOW-UP PHASE")
        print("-" * 20)
        
        follow_ups = self.engine.schedule_follow_ups()
        
        print(f"✅ Follow-ups sent: {len(follow_ups)}")
        
        if follow_ups:
            print("📮 Follow-up messages sent to:")
            for contact in follow_ups:
                print(f"   • {contact['company']}: {contact['name']}")
        
        return follow_ups
    
    def generate_report(self):
        """Generate current campaign status report"""
        print("\n📊 CAMPAIGN STATUS REPORT")
        print("-" * 30)
        
        report = self.engine.generate_outreach_report()
        print(report)
        
        # Save to file
        self._save_campaign_report(report)
        
        return report
    
    def _save_campaign_report(self, report):
        """Save campaign report to file"""
        report_dir = Path('output/ceo_outreach/reports')
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'campaign_report_{timestamp}.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📁 Report saved: {report_file}")
    
    def _print_campaign_summary(self, contacts, outreach_results, follow_ups):
        """Print final campaign summary"""
        campaign_duration = datetime.now() - self.campaign_start
        
        print(f"\n🏆 CAMPAIGN SUMMARY")
        print("=" * 50)
        print(f"📅 Duration: {campaign_duration}")
        print(f"🔍 Contacts Researched: {len(contacts)}")
        print(f"📧 Initial Outreach Sent: {len(outreach_results['sent'])}")
        print(f"📮 Follow-ups Sent: {len(follow_ups)}")
        print(f"🎯 Total Outreach Messages: {len(outreach_results['sent']) + len(follow_ups)}")
        print(f"💰 Potential Value Targeted: $2.34M annually")
        
        print(f"\n📈 SUCCESS METRICS TO TRACK:")
        print("• Response rate from CEOs (target: 20%+)")
        print("• Meeting conversion (target: 50% of responses)")
        print("• Interview conversion (target: 50% of meetings)")
        print("• Offer conversion (target: 25% of interviews)")
        
        print(f"\n🚀 NEXT STEPS:")
        print("1. Monitor email responses daily")
        print("2. Follow up with non-responders after 5-7 days")
        print("3. Schedule meetings with interested CEOs")
        print("4. Prepare technical deep-dive materials")
        print("5. Track all interactions in CRM system")
        
        stats = self.engine.get_stats()
        if stats['contacted'] > 0:
            print(f"\n📊 CURRENT PIPELINE:")
            print(f"• Total contacts: {stats['total_contacts']}")
            print(f"• Contacted: {stats['contacted']}")
            print(f"• Response rate: TBD (check email)")
            print(f"• Pipeline value: {stats['total_potential_salary']}")


def main():
    """Main execution with command-line arguments"""
    parser = argparse.ArgumentParser(description='CEO Outreach Campaign for $450K+ Positions')
    parser.add_argument('--mode', choices=['full', 'research', 'outreach', 'followup', 'report'], 
                       default='full', help='Campaign mode to run')
    parser.add_argument('--limit', type=int, default=5, 
                       help='Number of outreach emails to send (default: 5)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run without actually sending emails')
    
    args = parser.parse_args()
    
    # Initialize campaign
    campaign = CEOOutreachCampaign()
    
    # Execute based on mode
    if args.mode == 'full':
        print("🚀 Running FULL CEO Outreach Campaign")
        success = campaign.run_full_campaign()
        if success:
            print("\n✅ Campaign completed successfully!")
            print("📧 Check your email for responses over the next 48-72 hours")
            print("🔄 Run with --mode followup after 5 days for follow-ups")
        else:
            print("\n❌ Campaign encountered issues - check logs")
            
    elif args.mode == 'research':
        print("🔍 Running CEO Research Phase Only")
        contacts = campaign.run_research_only()
        print(f"\n✅ Research complete - {len(contacts)} contacts found")
        print("📧 Run with --mode outreach to send messages")
        
    elif args.mode == 'outreach':
        print("📧 Running CEO Outreach Phase Only")
        results = campaign.run_outreach_only(limit=args.limit)
        print(f"\n✅ Outreach sent to {len(results['sent'])} CEOs")
        print("📮 Run with --mode followup after 5-7 days")
        
    elif args.mode == 'followup':
        print("📮 Running Follow-up Phase Only")
        follow_ups = campaign.run_follow_up()
        print(f"\n✅ Follow-ups sent to {len(follow_ups)} contacts")
        
    elif args.mode == 'report':
        print("📊 Generating Campaign Report")
        report = campaign.generate_report()
        
    print(f"\n📝 Campaign log saved to: ceo_outreach.log")
    print("🔍 Detailed outreach records in: output/ceo_outreach/")


if __name__ == "__main__":
    main()