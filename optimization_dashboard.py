#!/usr/bin/env python3
"""
Optimization Dashboard - Shows all metrics and optimization opportunities
Combines response tracking, A/B testing, and follow-up insights
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

from accurate_response_checker import AccurateResponseChecker  # Using accurate checker to eliminate false positives
from ab_testing_system import ABTestingSystem
from smart_followup_system import SmartFollowUpSystem

def display_optimization_dashboard():
    """Display comprehensive optimization dashboard"""
    
    print("\n" + "="*70)
    print("🚀 AI JOB HUNTER OPTIMIZATION DASHBOARD")
    print("="*70)
    
    # Database stats
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    
    # Get current metrics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_jobs,
            SUM(CASE WHEN applied = 1 THEN 1 ELSE 0 END) as applied,
            SUM(CASE WHEN response_received = 1 THEN 1 ELSE 0 END) as responses,
            SUM(CASE WHEN interview_scheduled = 1 THEN 1 ELSE 0 END) as interviews,
            SUM(CASE WHEN relevance_score >= 0.65 AND applied = 0 THEN 1 ELSE 0 END) as high_value_pending
        FROM job_discoveries
    """)
    
    stats = cursor.fetchone()
    
    print("\n📊 CURRENT PERFORMANCE:")
    print(f"  Total Jobs in Database: {stats[0]}")
    print(f"  Applications Sent: {stats[1]}")
    print(f"  Responses Received: {stats[2]}")
    print(f"  Interviews Scheduled: {stats[3]}")
    print(f"  High-Value Pending: {stats[4]}")
    
    # Calculate rates
    if stats[1] > 0:
        response_rate = (stats[2] / stats[1]) * 100
        interview_rate = (stats[3] / stats[1]) * 100
        print(f"\n  📈 Response Rate: {response_rate:.1f}%")
        print(f"  📈 Interview Rate: {interview_rate:.1f}%")
    
    # Get today's activity
    today = datetime.now().date().isoformat()
    cursor.execute("""
        SELECT COUNT(*) FROM job_discoveries 
        WHERE DATE(COALESCE(application_date, applied_date)) = ?
    """, (today,))
    
    today_apps = cursor.fetchone()[0]
    print(f"\n  📅 Today's Applications: {today_apps}")
    
    # Get jobs needing follow-up
    three_days_ago = (datetime.now() - timedelta(days=3)).isoformat()
    cursor.execute("""
        SELECT COUNT(*) FROM job_discoveries
        WHERE applied = 1
        AND response_received = 0
        AND follow_up_sent = 0
        AND COALESCE(application_date, applied_date) <= ?
    """, (three_days_ago,))
    
    followup_needed = cursor.fetchone()[0]
    
    if followup_needed > 0:
        print(f"\n  ⏰ FOLLOW-UPS NEEDED: {followup_needed} jobs (3+ days old)")
    
    conn.close()
    
    # A/B Testing Insights
    print("\n" + "-"*70)
    print("🧪 A/B TESTING INSIGHTS:")
    
    ab_system = ABTestingSystem()
    performance = ab_system.calculate_performance()
    
    if performance['resume_versions']:
        print("\n  Resume Version Performance:")
        for version, metrics in performance['resume_versions'].items():
            if metrics['applications'] > 0:
                print(f"    • {version}: {metrics['applications']} sent, "
                      f"{metrics['response_rate']}% response rate")
    
    if performance['best_combination']:
        print(f"\n  🏆 Best Performer: {performance['best_combination']['resume']}")
    
    if performance['recommendations']:
        print("\n  💡 Recommendations:")
        for rec in performance['recommendations']:
            print(f"    • {rec}")
    
    # Quick Actions
    print("\n" + "-"*70)
    print("⚡ QUICK ACTIONS TO BOOST PERFORMANCE:")
    
    actions = []
    
    # Check application rate
    if today_apps < 20:
        actions.append(f"Send {20 - today_apps} more applications today (target: 20/day)")
        actions.append("Run: python3 automated_apply.py --batch 10")
    
    # Check follow-ups
    if followup_needed > 0:
        actions.append(f"Send follow-ups to {followup_needed} jobs")
        actions.append("Run: python3 smart_followup_system.py")
    
    # Check response tracking
    if stats[1] > 20 and stats[2] == 0:
        actions.append("Set up Gmail response tracking")
        actions.append("Run: export GMAIL_APP_PASSWORD='your-app-password'")
        actions.append("Then: python3 enhanced_response_checker.py")
    
    # Check high-value opportunities
    if stats[4] > 0:
        actions.append(f"Apply to {stats[4]} high-value opportunities (0.65+ score)")
        actions.append("Run: python3 personalized_apply.py")
    
    if actions:
        for i, action in enumerate(actions, 1):
            print(f"\n  {i}. {action}")
    else:
        print("\n  ✅ All systems optimal!")
    
    # Priority Companies
    print("\n" + "-"*70)
    print("🎯 MANUAL PRIORITY TARGETS:")
    print("  1. Abridge - $550M funding, CEO contacted")
    print("  2. Tempus AI - 59 open positions")
    print("  3. Oscar Health - GenAI implementation")
    
    # Success Prediction
    print("\n" + "-"*70)
    print("📈 PROJECTED OUTCOMES (Based on Current Metrics):")
    
    if stats[1] > 0:
        # Project based on current rates
        weekly_apps = today_apps * 7
        projected_responses = int(weekly_apps * (response_rate / 100))
        projected_interviews = int(weekly_apps * (interview_rate / 100))
        
        print(f"  Next Week ({weekly_apps} applications):")
        print(f"    • Expected Responses: {projected_responses}")
        print(f"    • Expected Interviews: {projected_interviews}")
    
    print("\n" + "="*70)
    print(f"Dashboard generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

def main():
    """Main execution"""
    display_optimization_dashboard()
    
    print("💡 TIP: Run this dashboard daily to track optimization progress")
    print("📚 For detailed analysis, use:")
    print("   • python3 enhanced_response_checker.py - Response patterns")
    print("   • python3 ab_testing_system.py - A/B test results")
    print("   • python3 smart_followup_system.py --analyze - Follow-up effectiveness")

if __name__ == "__main__":
    main()