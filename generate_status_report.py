#!/usr/bin/env python3
"""Generate a status report of job applications"""

import sqlite3
from datetime import datetime
from bcc_email_tracker import BCCEmailTracker

def generate_report():
    """Generate comprehensive status report"""
    
    # Connect to database
    conn = sqlite3.connect("unified_platform.db")
    conn.row_factory = sqlite3.Row
    
    print("📊 AI Job Hunter Status Report")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Overall stats
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM jobs")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as applied FROM jobs WHERE applied = 1")
    applied = cursor.fetchone()['applied']
    
    cursor.execute("SELECT COUNT(*) as pending FROM jobs WHERE applied = 0")
    pending = cursor.fetchone()['pending']
    
    print("📈 Overall Statistics:")
    print(f"  • Total jobs discovered: {total}")
    print(f"  • Applications sent: {applied}")
    print(f"  • Pending applications: {pending}")
    print(f"  • Application rate: {applied/total*100:.1f}%")
    print()
    
    # Applied jobs
    print("✅ Recent Applications:")
    cursor.execute("""
        SELECT company, title, applied_date, salary_range 
        FROM jobs 
        WHERE applied = 1 
        ORDER BY applied_date DESC 
        LIMIT 10
    """)
    for job in cursor.fetchall():
        date = datetime.fromisoformat(job['applied_date']).strftime('%Y-%m-%d %H:%M')
        print(f"  • {job['company']} - {job['position']}")
        print(f"    Applied: {date}, Salary: ${job['salary_range'] or 'Not specified'}")
    print()
    
    # High-value pending
    print("🎯 High-Value Pending Applications:")
    cursor.execute("""
        SELECT company, title, relevance_score, salary_range 
        FROM jobs 
        WHERE applied = 0 AND relevance_score >= 0.65
        ORDER BY relevance_score DESC, salary_range DESC
        LIMIT 10
    """)
    for job in cursor.fetchall():
        print(f"  • {job['company']} - {job['position']}")
        print(f"    Score: {job['relevance_score']}, Salary: ${job['salary_range'] or 'Not specified'}")
    print()
    
    # BCC tracking report
    print("📧 Email Tracking Report:")
    tracker = BCCEmailTracker()
    bcc_report = tracker.generate_bcc_report()
    print(f"  • Total tracked emails: {bcc_report['total_tracked']}")
    print(f"  • Last 7 days: {bcc_report['last_7_days']}")
    print(f"  • Last 30 days: {bcc_report['last_30_days']}")
    
    if bcc_report['by_company']:
        print("\n  Top companies contacted:")
        for company, count in sorted(bcc_report['by_company'].items(), 
                                   key=lambda x: x[1], reverse=True)[:5]:
            print(f"    - {company}: {count} email(s)")
    
    conn.close()
    
    print("\n✨ Next Steps:")
    print("  1. Run 'python automated_apply.py --batch 5' to apply to more jobs")
    print("  2. Check matthewdscott7+jobapps@gmail.com for responses")
    print("  3. Run 'python send_followup_email.py' to send follow-ups")
    
if __name__ == "__main__":
    generate_report()