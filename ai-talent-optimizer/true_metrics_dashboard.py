#!/usr/bin/env python3
"""
True Metrics Dashboard - Shows only verified, accurate job search metrics
No false positives, only real responses and validated data
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Import accurate tracking systems only
from accurate_response_checker import AccurateResponseChecker
from bounce_detector import BounceDetector
from email_verification_system import EmailVerificationSystem
from ab_testing_system import ABTestingSystem
from smart_followup_system import SmartFollowUpSystem

class TrueMetricsDashboard:
    """Display only verified, accurate metrics - no false positives"""
    
    def __init__(self):
        self.db_path = "UNIFIED_AI_JOBS.db"
        
        # Use only accurate checkers
        self.response_checker = AccurateResponseChecker()
        self.bounce_detector = BounceDetector()
        self.email_verifier = EmailVerificationSystem()
        self.ab_testing = ABTestingSystem()
        self.followup_system = SmartFollowUpSystem()
        
        # Paths for verified data
        self.verified_responses_path = "data/verified_responses.json"
        self.bounce_log_path = "data/bounce_log.json"
        self.invalid_emails_path = "data/invalid_emails.json"
    
    def get_true_metrics(self) -> Dict:
        """Get only verified, accurate metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get basic counts
        cursor.execute("SELECT COUNT(*) FROM job_discoveries")
        total_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM job_discoveries WHERE applied = 1")
        total_applied = cursor.fetchone()[0]
        
        # Get verified email metrics
        cursor.execute("""
            SELECT COUNT(*) FROM job_discoveries 
            WHERE applied = 1 AND email_verified = 1
        """)
        verified_emails = cursor.fetchone()[0]
        
        # Get bounce metrics
        cursor.execute("""
            SELECT COUNT(*) FROM job_discoveries 
            WHERE applied = 1 AND bounce_detected = 1
        """)
        bounced = cursor.fetchone()[0]
        
        # Get today's applications
        today = datetime.now().date().isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM job_discoveries 
            WHERE DATE(COALESCE(application_date, applied_date)) = ?
        """, (today,))
        today_applied = cursor.fetchone()[0]
        
        # Get high-value pending
        cursor.execute("""
            SELECT COUNT(*) FROM job_discoveries 
            WHERE applied = 0 AND relevance_score >= 0.65
        """)
        high_value_pending = cursor.fetchone()[0]
        
        # Get follow-up metrics
        cursor.execute("""
            SELECT COUNT(*) FROM job_discoveries 
            WHERE applied = 1 AND follow_up_sent > 0
        """)
        followups_sent = cursor.fetchone()[0]
        
        conn.close()
        
        # Load verified responses (from accurate checker)
        verified_responses = []
        if Path(self.verified_responses_path).exists():
            with open(self.verified_responses_path, 'r') as f:
                verified_responses = json.load(f)
        
        # Count real responses by type
        interviews = len([r for r in verified_responses if r.get('type') == 'interview_request'])
        rejections = len([r for r in verified_responses if r.get('type') == 'rejection'])
        auto_replies = len([r for r in verified_responses if r.get('type') == 'auto_reply'])
        
        # Calculate TRUE rates
        true_response_rate = ((interviews + rejections) / total_applied * 100) if total_applied > 0 else 0
        interview_rate = (interviews / total_applied * 100) if total_applied > 0 else 0
        bounce_rate = (bounced / total_applied * 100) if total_applied > 0 else 0
        email_verification_rate = (verified_emails / total_applied * 100) if total_applied > 0 else 0
        
        return {
            'total_jobs': total_jobs,
            'total_applied': total_applied,
            'today_applied': today_applied,
            'high_value_pending': high_value_pending,
            'real_interviews': interviews,
            'real_rejections': rejections,
            'auto_replies': auto_replies,
            'true_response_rate': true_response_rate,
            'interview_rate': interview_rate,
            'bounce_rate': bounce_rate,
            'bounced_count': bounced,
            'verified_emails': verified_emails,
            'email_verification_rate': email_verification_rate,
            'followups_sent': followups_sent
        }
    
    def get_email_health_status(self) -> Dict:
        """Get email system health metrics"""
        # Load bounce log
        bounce_data = {}
        if Path(self.bounce_log_path).exists():
            with open(self.bounce_log_path, 'r') as f:
                bounce_data = json.load(f)
        
        # Load invalid emails
        invalid_emails = []
        if Path(self.invalid_emails_path).exists():
            with open(self.invalid_emails_path, 'r') as f:
                data = json.load(f)
                invalid_emails = data.get('invalid_emails', [])
        
        return {
            'total_bounced': bounce_data.get('total_bounced', 0),
            'bounce_rate': bounce_data.get('bounce_rate', 0),
            'invalid_email_count': len(invalid_emails),
            'bounces_by_category': bounce_data.get('bounces_by_category', {})
        }
    
    def get_priority_actions(self, metrics: Dict) -> List[Dict]:
        """Generate priority actions based on true metrics"""
        actions = []
        
        # Check application rate
        if metrics['today_applied'] < 20:
            actions.append({
                'priority': 'HIGH',
                'action': f"Send {20 - metrics['today_applied']} more applications today",
                'command': 'python3 automated_apply.py --batch 10'
            })
        
        # Check bounce rate
        if metrics['bounce_rate'] > 5:
            actions.append({
                'priority': 'CRITICAL',
                'action': f"Bounce rate is {metrics['bounce_rate']:.1f}% - verify emails before sending",
                'command': 'python3 email_verification_system.py'
            })
        
        # Check for high-value opportunities
        if metrics['high_value_pending'] > 0:
            actions.append({
                'priority': 'HIGH',
                'action': f"Apply to {metrics['high_value_pending']} high-value jobs (0.65+ score)",
                'command': 'python3 personalized_apply.py'
            })
        
        # Check response rate
        if metrics['true_response_rate'] == 0 and metrics['total_applied'] > 20:
            actions.append({
                'priority': 'MEDIUM',
                'action': "No responses yet - consider A/B testing different approaches",
                'command': 'python3 ab_testing_system.py'
            })
        
        # Check for follow-ups needed
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        three_days_ago = (datetime.now() - timedelta(days=3)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM job_discoveries 
            WHERE applied = 1 
            AND response_received = 0 
            AND follow_up_sent = 0
            AND COALESCE(application_date, applied_date) <= ?
        """, (three_days_ago,))
        
        followup_needed = cursor.fetchone()[0]
        conn.close()
        
        if followup_needed > 0:
            actions.append({
                'priority': 'MEDIUM',
                'action': f"Send follow-ups to {followup_needed} applications (3+ days old)",
                'command': 'python3 smart_followup_system.py'
            })
        
        return actions
    
    def display_dashboard(self):
        """Display the true metrics dashboard"""
        print("\n" + "="*80)
        print("🎯 TRUE METRICS DASHBOARD - No False Positives")
        print("="*80)
        
        # Get metrics
        metrics = self.get_true_metrics()
        email_health = self.get_email_health_status()
        
        # Display core metrics
        print("\n📊 VERIFIED APPLICATION METRICS:")
        print(f"  Total Jobs in Database: {metrics['total_jobs']}")
        print(f"  Total Applications Sent: {metrics['total_applied']}")
        print(f"  Today's Applications: {metrics['today_applied']}")
        print(f"  High-Value Pending: {metrics['high_value_pending']}")
        
        print("\n✅ REAL RESPONSE METRICS (Strictly Verified):")
        print(f"  Real Interview Requests: {metrics['real_interviews']}")
        print(f"  Confirmed Rejections: {metrics['real_rejections']}")
        print(f"  Auto-replies: {metrics['auto_replies']}")
        print(f"  TRUE Response Rate: {metrics['true_response_rate']:.1f}%")
        print(f"  Interview Rate: {metrics['interview_rate']:.1f}%")
        
        print("\n📧 EMAIL DELIVERY HEALTH:")
        print(f"  Emails Verified Before Sending: {metrics['verified_emails']} ({metrics['email_verification_rate']:.1f}%)")
        print(f"  Bounced Emails Detected: {metrics['bounced_count']}")
        print(f"  Bounce Rate: {metrics['bounce_rate']:.1f}%")
        
        if metrics['bounce_rate'] > 5:
            print(f"  ⚠️  WARNING: High bounce rate detected!")
        
        if email_health['bounces_by_category']:
            print("\n  Bounce Categories:")
            for category, emails in email_health['bounces_by_category'].items():
                print(f"    • {category.replace('_', ' ').title()}: {len(emails)}")
        
        print("\n📈 ENGAGEMENT METRICS:")
        print(f"  Follow-ups Sent: {metrics['followups_sent']}")
        
        # Get priority actions
        actions = self.get_priority_actions(metrics)
        
        if actions:
            print("\n⚡ PRIORITY ACTIONS:")
            for action in sorted(actions, key=lambda x: ['CRITICAL', 'HIGH', 'MEDIUM'].index(x['priority'])):
                emoji = "🚨" if action['priority'] == 'CRITICAL' else "⚠️" if action['priority'] == 'HIGH' else "📝"
                print(f"\n  {emoji} [{action['priority']}] {action['action']}")
                print(f"     Command: {action['command']}")
        else:
            print("\n✅ All systems optimal - no urgent actions needed")
        
        # Reality check
        print("\n🔍 REALITY CHECK:")
        if metrics['real_interviews'] == 0:
            print("  • No real interview requests received yet")
            print("  • This is based on STRICT verification - only explicit invitations count")
        else:
            print(f"  • You have {metrics['real_interviews']} REAL interview opportunities!")
        
        if metrics['bounce_rate'] > 0:
            print(f"  • {metrics['bounced_count']} emails have bounced - remove these addresses")
        
        print("\n" + "-"*80)
        print("📝 DATA SOURCES:")
        print("  • Response data: accurate_response_checker.py (no false positives)")
        print("  • Bounce data: bounce_detector.py")
        print("  • Email verification: email_verification_system.py")
        
        print("\n" + "="*80)
        print(f"Dashboard generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("This dashboard shows ONLY verified data - no assumptions or false positives")
        print("="*80 + "\n")

def main():
    """Main execution"""
    dashboard = TrueMetricsDashboard()
    dashboard.display_dashboard()
    
    print("\n💡 DAILY WORKFLOW:")
    print("  1. Run this dashboard first: python3 true_metrics_dashboard.py")
    print("  2. Check for bounces: python3 bounce_detector.py")
    print("  3. Verify responses: python3 accurate_response_checker.py")
    print("  4. Send verified applications: python3 automated_apply.py")
    print("\n⚠️  Never use enhanced_response_checker.py - it has 100% false positives")

if __name__ == "__main__":
    main()