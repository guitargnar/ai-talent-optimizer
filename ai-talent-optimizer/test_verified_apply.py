#!/usr/bin/env python3
"""
Test Verified Apply - Simple test of applying with verified emails
"""

import sqlite3

def test_verified_applications():
    """Test which companies can be applied to with verified emails"""
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    
    print("🔍 TESTING VERIFIED EMAIL APPLICATIONS")
    print("="*60)
    
    # Get unapplied jobs with verified emails
    cursor.execute("""
        SELECT company, position, relevance_score, verified_email 
        FROM job_discoveries 
        WHERE applied = 0 
        AND verified_email IS NOT NULL 
        AND verified_email != ''
        AND relevance_score >= 0.3
        ORDER BY relevance_score DESC
        LIMIT 10
    """)
    
    jobs = cursor.fetchall()
    
    if jobs:
        print(f"\n✅ Found {len(jobs)} jobs ready to apply with verified emails:")
        for company, position, score, email in jobs:
            print(f"\n  Company: {company}")
            print(f"  Position: {position}")
            print(f"  Score: {score:.2f}")
            print(f"  Verified Email: {email}")
            print(f"  Status: READY TO SEND ✅")
    else:
        print("\n❌ No jobs found with verified emails")
        
        # Check why
        cursor.execute("""
            SELECT COUNT(*) FROM job_discoveries WHERE applied = 0
        """)
        unapplied = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM job_discoveries 
            WHERE verified_email IS NOT NULL AND verified_email != ''
        """)
        with_email = cursor.fetchone()[0]
        
        print(f"\n📊 Debug Info:")
        print(f"  Total unapplied jobs: {unapplied}")
        print(f"  Jobs with verified emails: {with_email}")
        
        # Show what we have
        cursor.execute("""
            SELECT company, applied, verified_email 
            FROM job_discoveries 
            WHERE relevance_score >= 0.5
            ORDER BY relevance_score DESC
            LIMIT 5
        """)
        
        print(f"\n  Sample high-value jobs:")
        for company, applied, email in cursor.fetchall():
            status = "Applied" if applied else "Not Applied"
            email_status = email if email else "No Email"
            print(f"    {company}: {status}, Email: {email_status}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("💡 RECOMMENDATIONS:")
    
    if jobs:
        print("  ✅ Ready to apply! Run:")
        print("     python3 automated_apply.py --batch 3")
    else:
        print("  1. Add more verified emails:")
        print("     python3 collect_real_emails.py")
        print("  2. Reset previously applied companies:")
        print("     python3 reset_for_verified_emails.py")

if __name__ == "__main__":
    test_verified_applications()