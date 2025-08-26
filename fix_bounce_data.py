#!/usr/bin/env python3
"""
Fix Bounce Data - Reset incorrect bounce detections
Only mark as bounced if we actually sent an email to that address
"""

import sqlite3
from datetime import datetime

def fix_bounce_data():
    """Reset bounce data to accurate state"""
    conn = sqlite3.connect("unified_platform.db")
    cursor = conn.cursor()
    
    print("🔧 FIXING BOUNCE DATA")
    print("=" * 60)
    
    # First, check current state
    cursor.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN applied = 1 THEN 1 ELSE 0 END) as applied,
               SUM(CASE WHEN bounce_detected = 1 THEN 1 ELSE 0 END) as bounced
        FROM jobs
    """)
    total, applied, bounced = cursor.fetchone()
    print(f"\n📊 BEFORE FIX:")
    print(f"  Total jobs: {total}")
    print(f"  Applied: {applied}")
    print(f"  Marked as bounced: {bounced}")
    print(f"  Incorrect bounce rate: {bounced}/{applied} = {bounced/applied*100:.1f}%")
    
    # Reset all bounce flags where we haven't actually applied
    cursor.execute("""
        UPDATE jobs
        SET bounce_detected = 0,
            bounce_reason = NULL
        WHERE applied = 0
    """)
    rows_fixed = cursor.rowcount
    print(f"\n✅ Reset {rows_fixed} false bounce detections (jobs not applied to)")
    
    # Reset bounces where no email was actually used
    cursor.execute("""
        UPDATE jobs
        SET bounce_detected = 0,
            bounce_reason = NULL
        WHERE actual_email_used IS NULL OR actual_email_used = ''
    """)
    rows_fixed2 = cursor.rowcount
    print(f"✅ Reset {rows_fixed2} bounces with no email address")
    
    # Get list of actually bounced emails (only from applied jobs)
    cursor.execute("""
        SELECT company, actual_email_used, bounce_reason
        FROM jobs
        WHERE applied = 1 
        AND bounce_detected = 1
        AND actual_email_used IS NOT NULL
        AND actual_email_used != ''
    """)
    real_bounces = cursor.fetchall()
    
    print(f"\n📧 REAL BOUNCES (from actual applications):")
    if real_bounces:
        for company, email, reason in real_bounces[:10]:
            print(f"  • {company}: {email} ({reason})")
        if len(real_bounces) > 10:
            print(f"  ... and {len(real_bounces) - 10} more")
    else:
        print("  No real bounces found!")
    
    # Check final state
    cursor.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN applied = 1 THEN 1 ELSE 0 END) as applied,
               SUM(CASE WHEN bounce_detected = 1 THEN 1 ELSE 0 END) as bounced
        FROM jobs
    """)
    total, applied, bounced = cursor.fetchone()
    
    print(f"\n📊 AFTER FIX:")
    print(f"  Total jobs: {total}")
    print(f"  Applied: {applied}")
    print(f"  Actually bounced: {bounced}")
    print(f"  Real bounce rate: {bounced}/{applied} = {bounced/applied*100:.1f}%" if applied > 0 else "  No applications sent")
    
    # Get jobs ready to apply to (high score, not applied, not bounced)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM jobs
        WHERE applied = 0
        AND relevance_score >= 0.65
        AND (bounce_detected = 0 OR bounce_detected IS NULL)
    """)
    ready_to_apply = cursor.fetchone()[0]
    
    print(f"\n🎯 READY TO APPLY:")
    print(f"  {ready_to_apply} high-value jobs available")
    print(f"  Command: python3 automated_apply.py --batch 10")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ BOUNCE DATA FIXED!")
    print("\nNext steps:")
    print("1. Run: python3 email_verification_system.py  # Verify emails first")
    print("2. Run: python3 automated_apply.py --batch 10  # Send applications")
    print("3. Run: python3 true_metrics_dashboard.py     # Check real metrics")

if __name__ == "__main__":
    fix_bounce_data()