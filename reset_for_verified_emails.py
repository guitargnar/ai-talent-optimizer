#!/usr/bin/env python3
"""
Reset for Verified Emails - Allow re-application to companies with verified emails
Since all previous applications bounced, we can safely re-apply with correct emails
"""

import sqlite3
from datetime import datetime

def reset_verified_companies():
    """Reset companies with verified emails for re-application"""
    conn = sqlite3.connect("unified_platform.db")
    cursor = conn.cursor()
    
    # Get companies with verified emails that were marked as applied
    cursor.execute("""
        SELECT company, verified_email, relevance_score 
        FROM jobs 
        WHERE verified_email IS NOT NULL 
        AND verified_email != ''
        AND applied = 1
        ORDER BY relevance_score DESC
    """)
    
    companies = cursor.fetchall()
    
    print("🔄 RESETTING COMPANIES WITH VERIFIED EMAILS")
    print("="*60)
    print(f"\nFound {len(companies)} companies with verified emails:")
    
    for company, email, score in companies:
        print(f"  • {company}: {email} (Score: {score:.2f})")
    
    if companies:
        print(f"\n⚠️  These applications previously bounced (100% bounce rate)")
        print(f"✅ Now we have REAL emails, so we can re-apply!")
        
        # Auto-confirm if running in non-interactive mode
        import sys
        if not sys.stdin.isatty():
            confirm = 'yes'
            print("\n✅ Auto-confirming reset (non-interactive mode)")
        else:
            confirm = input("\nReset these for re-application? (yes/no): ")
        
        if confirm.lower() == 'yes':
            # Reset the applied status for companies with verified emails
            cursor.execute("""
                UPDATE jobs 
                SET applied = 0,
                    application_invalid = 0,
                    bounce_detected = 0,
                    response_received = 0,
                    applied_date = NULL
                WHERE verified_email IS NOT NULL 
                AND verified_email != ''
                AND applied = 1
            """)
            
            reset_count = cursor.rowcount
            conn.commit()
            
            print(f"\n✅ Reset {reset_count} job entries for re-application!")
            print(f"\n🚀 You can now apply to these companies with REAL emails:")
            print(f"   python3 automated_apply.py --batch 5")
        else:
            print("Reset cancelled")
    else:
        print("\nNo companies with verified emails found")
    
    conn.close()

if __name__ == "__main__":
    reset_verified_companies()