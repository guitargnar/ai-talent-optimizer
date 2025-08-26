#!/usr/bin/env python3
"""
Project Ascent - Master Campaign Sequence Runner
Orchestrates the $400K+ job search campaign
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
from pathlib import Path

from intelligent_message_generator import IntelligentMessageGenerator
from campaign_assets.campaign_config import (
    TIER_1_TARGETS,
    TIER_2_TARGETS,
    TIER_3_TARGETS,
    CAMPAIGN_TARGETS,
    SUCCESS_METRICS
)

class CampaignSequenceRunner:
    """Master orchestrator for Project Ascent campaign"""
    
    def __init__(self, dry_run: bool = True):
        """
        Initialize campaign runner
        
        Args:
            dry_run: If True, generates messages but doesn't send (default: True for safety)
        """
        self.dry_run = dry_run
        self.message_generator = IntelligentMessageGenerator()
        self.db_path = "unified_platform.db"
        self._init_database()
        
        # Campaign state
        self.today_messages = []
        self.pending_approval = []
        
        print(f"🚀 PROJECT ASCENT CAMPAIGN RUNNER INITIALIZED")
        print(f"Mode: {'DRY RUN (No messages will be sent)' if dry_run else 'LIVE MODE'}")
        print("=" * 80)
    
    def _init_database(self):
        """Initialize campaign tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                target_name TEXT,
                company TEXT,
                tier TEXT,
                message_type TEXT,
                subject TEXT,
                status TEXT,
                response_received INTEGER DEFAULT 0,
                interview_scheduled INTEGER DEFAULT 0,
                notes TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                date TEXT PRIMARY KEY,
                messages_sent INTEGER,
                responses_received INTEGER,
                interviews_scheduled INTEGER,
                applications_submitted INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    def identify_high_value_targets(self, count: int = 5) -> List[Dict]:
        """
        Identify today's high-value targets across tiers
        
        Args:
            count: Number of targets to identify
            
        Returns:
            List of target dictionaries
        """
        targets = []
        
        # Prioritize Tier 1 (Humana VPs)
        tier_1_count = min(2, count)
        for target in TIER_1_TARGETS[:tier_1_count]:
            target["tier"] = "tier_1"
            targets.append(target)
        
        # Add Tier 2 (Healthcare AI)
        tier_2_count = min(2, count - len(targets))
        for target in TIER_2_TARGETS[:tier_2_count]:
            target["tier"] = "tier_2"
            targets.append(target)
        
        # Fill remaining with Tier 3
        tier_3_count = count - len(targets)
        for target in TIER_3_TARGETS[:tier_3_count]:
            target["tier"] = "tier_3"
            targets.append(target)
        
        print(f"📋 Identified {len(targets)} high-value targets for today:")
        for i, target in enumerate(targets, 1):
            print(f"   {i}. {target.get('name', 'Contact')} at {target['company']} (Tier: {target['tier'][-1]})")
        
        return targets
    
    def generate_personalized_messages(self, targets: List[Dict]) -> List[Dict]:
        """
        Generate personalized messages for identified targets
        
        Args:
            targets: List of target dictionaries
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        print(f"\n✍️  Generating personalized messages...")
        
        for target in targets:
            subject, body = self.message_generator.generate_message(
                target.get("name", "Hiring Manager"),
                target["company"],
                target["tier"],
                target.get("title"),
                target
            )
            
            messages.append({
                "target": target,
                "subject": subject,
                "body": body,
                "tier": target["tier"],
                "generated_at": datetime.now().isoformat()
            })
            
            print(f"   ✅ Generated message for {target.get('name', 'Contact')} at {target['company']}")
        
        self.today_messages = messages
        return messages
    
    def present_for_approval(self, messages: List[Dict]) -> List[Dict]:
        """
        Present generated messages for user approval
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            List of approved messages
        """
        approved = []
        
        print("\n" + "=" * 80)
        print("📨 MESSAGES READY FOR REVIEW")
        print("=" * 80)
        
        for i, msg in enumerate(messages, 1):
            target = msg["target"]
            print(f"\nMESSAGE {i}/{len(messages)}")
            print("-" * 40)
            print(f"To: {target.get('name', 'Contact')} at {target['company']}")
            print(f"Title: {target.get('title', 'N/A')}")
            print(f"Tier: {msg['tier']}")
            print(f"\nSubject: {msg['subject']}")
            print(f"\nMessage Body:")
            print("-" * 40)
            print(msg['body'])
            print("-" * 40)
            
            if self.dry_run:
                print("✅ DRY RUN MODE: Message prepared but not sent")
                approved.append(msg)
            else:
                response = input("\nApprove this message? (y/n/edit): ").strip().lower()
                
                if response == 'y':
                    approved.append(msg)
                    print("✅ Message approved")
                elif response == 'edit':
                    # Allow editing (simplified for now)
                    print("📝 Edit functionality coming soon. Message skipped for now.")
                else:
                    print("❌ Message rejected")
        
        self.pending_approval = approved
        return approved
    
    def execute_outreach(self, approved_messages: List[Dict]) -> Dict:
        """
        Execute the outreach campaign (send messages)
        
        Args:
            approved_messages: List of approved message dictionaries
            
        Returns:
            Execution summary
        """
        summary = {
            "total_approved": len(approved_messages),
            "sent": 0,
            "failed": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.dry_run:
            print(f"\n🔒 DRY RUN: Would send {len(approved_messages)} messages")
            summary["sent"] = len(approved_messages)
            summary["note"] = "Dry run - no messages actually sent"
            
            # Log to database even in dry run
            self._log_outreach(approved_messages, "dry_run")
        else:
            print(f"\n📤 Sending {len(approved_messages)} approved messages...")
            
            for msg in approved_messages:
                # In production, this would integrate with email/LinkedIn APIs
                # For now, we simulate sending
                success = self._send_message(msg)
                
                if success:
                    summary["sent"] += 1
                    self._log_outreach([msg], "sent")
                    print(f"   ✅ Sent to {msg['target'].get('name', 'Contact')}")
                else:
                    summary["failed"] += 1
                    self._log_outreach([msg], "failed")
                    print(f"   ❌ Failed to send to {msg['target'].get('name', 'Contact')}")
        
        return summary
    
    # DECOMMISSIONED: Strategic Pivot to Human-Centric Approach [2025-08-12]
    # Automated sending disabled due to 0% response rate over 223 days
    def _send_message(self, message: Dict) -> bool:
        """
        [DECOMMISSIONED] Send a single message - NOW DISABLED
        
        This function has been intentionally disabled as part of Project Ascent 2.0.
        The automated approach failed completely (0% response rate) and was damaging
        the professional brand. Senior roles require human touch and trust-building.
        
        Args:
            message: Message dictionary
            
        Returns:
            False - always fails now to prevent automated sending
        """
        print("⚠️ DECOMMISSIONED: Automated sending is disabled")
        print("📝 Use manual, personalized outreach with intelligence dossiers instead")
        print(f"   Target: {message.get('target', {}).get('name', 'Unknown')}")
        print(f"   Company: {message.get('target', {}).get('company', 'Unknown')}")
        print("   Action: Copy message and send manually after personalizing")
        return False  # Always return False to prevent sending
    
    def _log_outreach(self, messages: List[Dict], status: str):
        """Log outreach attempts to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for msg in messages:
            target = msg["target"]
            cursor.execute("""
                INSERT INTO outreach_log 
                (timestamp, target_name, company, tier, message_type, subject, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                target.get("name", "Unknown"),
                target["company"],
                msg["tier"],
                "initial_outreach",
                msg["subject"],
                status,
                f"Generated at {msg['generated_at']}"
            ))
        
        # Update daily metrics
        today = datetime.now().date().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO campaign_metrics 
            (date, messages_sent, responses_received, interviews_scheduled, applications_submitted)
            VALUES (?, 
                COALESCE((SELECT messages_sent FROM metrics WHERE date = ?), 0) + ?,
                COALESCE((SELECT responses_received FROM metrics WHERE date = ?), 0),
                COALESCE((SELECT interviews_scheduled FROM metrics WHERE date = ?), 0),
                COALESCE((SELECT applications_submitted FROM metrics WHERE date = ?), 0)
            )
        """, (today, today, len(messages), today, today, today))
        
        conn.commit()
        conn.close()
    
    def generate_daily_report(self) -> str:
        """Generate daily campaign report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get today's metrics
        today = datetime.now().date().isoformat()
        cursor.execute("""
            SELECT * FROM metrics WHERE date = ?
        """, (today,))
        
        today_metrics = cursor.fetchone()
        
        # Get overall campaign stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_outreach,
                SUM(response_received) as total_responses,
                SUM(interview_scheduled) as total_interviews
            FROM outreach_log
        """)
        
        overall_stats = cursor.fetchone()
        
        conn.close()
        
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║                  PROJECT ASCENT - DAILY REPORT                 ║
║                      {datetime.now().strftime('%Y-%m-%d %H:%M')}                      ║
╚════════════════════════════════════════════════════════════════╝

📊 TODAY'S ACTIVITY ({today})
─────────────────────────────────
Messages Sent:        {today_metrics[1] if today_metrics else 0}
Responses Received:   {today_metrics[2] if today_metrics else 0}
Interviews Scheduled: {today_metrics[3] if today_metrics else 0}
Applications:         {today_metrics[4] if today_metrics else 0}

📈 CAMPAIGN TOTALS
─────────────────────────────────
Total Outreach:       {overall_stats[0] if overall_stats else 0}
Total Responses:      {overall_stats[1] if overall_stats else 0}
Total Interviews:     {overall_stats[2] if overall_stats else 0}

🎯 KEY METRICS
─────────────────────────────────
Response Rate:        {(overall_stats[1]/overall_stats[0]*100 if overall_stats[0] > 0 else 0):.1f}%
Interview Rate:       {(overall_stats[2]/overall_stats[0]*100 if overall_stats[0] > 0 else 0):.1f}%
Target Salary:        $400,000+
Campaign Day:         {(datetime.now() - datetime(2025, 1, 1)).days}

💡 NEXT ACTIONS
─────────────────────────────────
1. Review and respond to any new messages
2. Follow up on messages sent 3-7 days ago
3. Update LinkedIn with recent achievements
4. Apply to 5 new positions
5. Schedule tomorrow's outreach targets

🚀 Keep pushing forward! Every message brings you closer to $400K+
"""
        
        return report
    
    def run_daily_sequence(self):
        """Run the complete daily campaign sequence"""
        
        print("\n🎯 Starting Project Ascent Daily Campaign Sequence\n")
        
        # Step 1: Identify targets
        targets = self.identify_high_value_targets(count=5)
        
        # Step 2: Generate messages
        messages = self.generate_personalized_messages(targets)
        
        # Step 3: Present for approval
        approved = self.present_for_approval(messages)
        
        # Step 4: Execute outreach
        summary = self.execute_outreach(approved)
        
        # Step 5: Generate report
        report = self.generate_daily_report()
        print(report)
        
        # Save report to file
        report_path = f"campaign_reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        os.makedirs("campaign_reports", exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {report_path}")
        
        return summary


def main():
    """Main entry point for campaign runner"""
    
    # Check for command line arguments
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        dry_run = False
        print("⚠️  WARNING: Running in LIVE MODE - messages will be sent!")
        confirm = input("Are you sure you want to continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("Aborting...")
            return
    
    # Initialize and run campaign
    runner = CampaignSequenceRunner(dry_run=dry_run)
    summary = runner.run_daily_sequence()
    
    print("\n✅ Campaign sequence complete!")
    print(f"Summary: {json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    main()