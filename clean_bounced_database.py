#!/usr/bin/env python3
"""
Clean Bounced Database - Mark invalid applications and reset for fresh start
Analyzes bounce data and prepares database for verified email sending
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class DatabaseCleaner:
    """Clean and reset database after bounce crisis"""
    
    def __init__(self):
        self.db_path = "unified_platform.db"
        self.bounce_log_path = "data/bounce_log.json"
        self.invalid_emails_path = "data/invalid_emails.json"
        self.cleanup_log_path = "data/database_cleanup_log.json"
        
        # Load bounce data
        self.bounce_data = self._load_json(self.bounce_log_path, {})
        self.invalid_emails = self._load_json(self.invalid_emails_path, {}).get('invalid_emails', [])
    
    def _load_json(self, path: str, default):
        """Load JSON file or return default"""
        if Path(path).exists():
            with open(path, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, path: str, data):
        """Save data to JSON file"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def analyze_damage(self) -> Dict:
        """Analyze the extent of the bounce problem"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied = 1")
        total_applied = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE bounce_detected = 1")
        total_bounced = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE response_received = 1")
        total_responses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE interview_scheduled = 1")
        total_interviews = cursor.fetchone()[0]
        
        # Get list of bounced companies
        cursor.execute("""
            SELECT company, title, applied_date 
            FROM jobs 
            WHERE bounce_detected = 1
            ORDER BY applied_date DESC
        """)
        bounced_applications = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_applied': total_applied,
            'total_bounced': total_bounced,
            'bounce_rate': (total_bounced / total_applied * 100) if total_applied > 0 else 0,
            'false_responses': total_responses,  # These are likely false positives
            'false_interviews': total_interviews,  # These are likely false positives
            'bounced_applications': bounced_applications[:10],  # Show first 10
            'invalid_email_count': len(self.invalid_emails)
        }
    
    def mark_bounced_as_invalid(self) -> int:
        """Mark all bounced applications as invalid"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add columns if they don't exist
        try:
            cursor.execute("ALTER TABLE job_discoveries ADD COLUMN application_invalid INTEGER DEFAULT 0")
        except:
            pass
        
        try:
            cursor.execute("ALTER TABLE job_discoveries ADD COLUMN cleanup_date TEXT")
        except:
            pass
        
        # Mark bounced as invalid
        cursor.execute("""
            UPDATE jobs 
            SET application_invalid = 1,
                cleanup_date = ?
            WHERE bounce_detected = 1
        """, (datetime.now().isoformat(),))
        
        bounced_marked = cursor.rowcount
        
        # Also mark applications to known invalid emails
        for email in self.invalid_emails:
            # Try to find applications that might have used this email
            cursor.execute("""
                UPDATE jobs 
                SET application_invalid = 1,
                    bounce_detected = 1,
                    cleanup_date = ?
                WHERE applied = 1
                AND (actual_email_used = ? OR actual_email_used IS NULL)
            """, (datetime.now().isoformat(), email))
        
        conn.commit()
        conn.close()
        
        return bounced_marked
    
    def reset_false_positives(self) -> Dict:
        """Reset false positive response tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count false positives before reset
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE response_received = 1")
        false_responses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE interview_scheduled = 1")
        false_interviews = cursor.fetchone()[0]
        
        # Reset false positive fields
        cursor.execute("""
            UPDATE jobs 
            SET response_received = 0,
                response_date = NULL,
                response_type = NULL,
                interview_scheduled = 0
            WHERE response_received = 1
        """)
        
        responses_reset = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return {
            'false_responses_cleared': false_responses,
            'false_interviews_cleared': false_interviews,
            'records_reset': responses_reset
        }
    
    def mark_for_reapplication(self) -> int:
        """Mark high-value bounced applications for re-sending with correct emails"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add column if doesn't exist
        try:
            cursor.execute("ALTER TABLE job_discoveries ADD COLUMN needs_reapplication INTEGER DEFAULT 0")
        except:
            pass
        
        # Mark high-value bounced applications for re-application
        cursor.execute("""
            UPDATE jobs 
            SET needs_reapplication = 1
            WHERE application_invalid = 1
            AND relevance_score >= 0.5
        """)
        
        marked = cursor.rowcount
        
        # Get list of companies to re-apply to
        cursor.execute("""
            SELECT company, title, relevance_score 
            FROM jobs 
            WHERE needs_reapplication = 1
            ORDER BY relevance_score DESC
            LIMIT 20
        """)
        
        reapply_list = cursor.fetchall()
        
        conn.commit()
        conn.close()
        
        print(f"\n🔄 TOP COMPANIES TO RE-APPLY (with correct emails):")
        for company, title, score in reapply_list:
            print(f"  • {company} - {position} (Score: {score:.2f})")
        
        return marked
    
    def create_cleanup_report(self) -> Dict:
        """Create comprehensive cleanup report"""
        damage = self.analyze_damage()
        
        report = {
            'cleanup_date': datetime.now().isoformat(),
            'damage_assessment': damage,
            'cleanup_actions': {
                'bounced_marked': 0,
                'false_positives_reset': {},
                'marked_for_reapplication': 0
            },
            'recommendations': []
        }
        
        # Perform cleanup
        report['cleanup_actions']['bounced_marked'] = self.mark_bounced_as_invalid()
        report['cleanup_actions']['false_positives_reset'] = self.reset_false_positives()
        report['cleanup_actions']['marked_for_reapplication'] = self.mark_for_reapplication()
        
        # Add recommendations
        if damage['bounce_rate'] > 50:
            report['recommendations'].append("CRITICAL: Over 50% bounce rate - email system was fundamentally broken")
        
        report['recommendations'].extend([
            "1. Import known company emails: python3 collect_real_emails.py",
            "2. Manually research emails for high-value companies",
            "3. Only send to verified emails going forward",
            "4. Use web application forms when email unavailable",
            "5. Monitor bounce rate daily - should be <5%"
        ])
        
        # Save report
        self._save_json(self.cleanup_log_path, report)
        
        return report
    
    def display_cleanup_summary(self):
        """Display cleanup summary dashboard"""
        print("\n" + "="*70)
        print("🧹 DATABASE CLEANUP REPORT")
        print("="*70)
        
        # Get damage assessment
        damage = self.analyze_damage()
        
        print(f"\n📊 DAMAGE ASSESSMENT:")
        print(f"  Total Applications Sent: {damage['total_applied']}")
        print(f"  Total Bounced: {damage['total_bounced']}")
        print(f"  Bounce Rate: {damage['bounce_rate']:.1f}%")
        print(f"  False 'Responses': {damage['false_responses']}")
        print(f"  False 'Interviews': {damage['false_interviews']}")
        print(f"  Invalid Emails Found: {damage['invalid_email_count']}")
        
        if damage['bounce_rate'] == 100:
            print(f"\n🚨 CRITICAL: 100% bounce rate - NO emails were delivered!")
        
        # Perform cleanup
        print(f"\n🔧 PERFORMING CLEANUP...")
        report = self.create_cleanup_report()
        
        print(f"\n✅ CLEANUP COMPLETED:")
        print(f"  Bounced Applications Marked Invalid: {report['cleanup_actions']['bounced_marked']}")
        print(f"  False Positives Reset: {report['cleanup_actions']['false_positives_reset']['false_responses_cleared']}")
        print(f"  Marked for Re-application: {report['cleanup_actions']['marked_for_reapplication']}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        
        print(f"\n📄 Cleanup report saved to: {self.cleanup_log_path}")
        print("\n" + "="*70)
        
        # Show database state after cleanup
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM jobs 
            WHERE applied = 1 AND application_invalid = 0
        """)
        valid_applications = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM jobs 
            WHERE applied = 0 AND relevance_score >= 0.5
        """)
        pending_high_value = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\n📈 DATABASE STATE AFTER CLEANUP:")
        print(f"  Valid Applications Remaining: {valid_applications}")
        print(f"  High-Value Jobs Pending: {pending_high_value}")
        print(f"  Ready for fresh start with verified emails!")
        print("="*70 + "\n")


def main():
    """Main execution"""
    cleaner = DatabaseCleaner()
    
    print("🧹 Database Cleanup Tool")
    print("\n⚠️  This will:")
    print("  1. Mark all bounced emails as invalid")
    print("  2. Reset false positive responses")
    print("  3. Prepare database for verified email sending")
    
    confirm = input("\nProceed with cleanup? (yes/no): ")
    
    if confirm.lower() == 'yes':
        cleaner.display_cleanup_summary()
        
        print("\n✅ NEXT STEPS:")
        print("  1. Import known emails: python3 collect_real_emails.py")
        print("  2. Verify emails: python3 enhanced_email_verifier.py")
        print("  3. Send to verified addresses only: python3 automated_apply.py")
    else:
        print("Cleanup cancelled")


if __name__ == "__main__":
    main()