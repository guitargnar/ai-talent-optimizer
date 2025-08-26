#!/usr/bin/env python3
"""
Quick Email Setup - One-command setup for verified email system
Imports known emails and shows current status
"""

import sys
from collect_real_emails import RealEmailCollector
from enhanced_email_verifier import EnhancedEmailVerifier
import sqlite3

def main():
    print("🚀 QUICK EMAIL SETUP")
    print("="*60)
    
    # Step 1: Import known emails
    print("\n📧 Step 1: Importing known company emails...")
    collector = RealEmailCollector()
    imported = collector.import_known_emails()
    print(f"✅ Imported {imported} verified emails")
    
    # Step 2: Update database
    print("\n🔄 Step 2: Updating database with verified emails...")
    updated = collector.update_database_with_emails()
    print(f"✅ Updated {updated} companies with verified emails")
    
    # Step 3: Show current status
    print("\n📊 Step 3: Current Email Status")
    print("-"*40)
    
    # Get statistics
    conn = sqlite3.connect("unified_platform.db")
    cursor = conn.cursor()
    
    # Count companies with verified emails
    cursor.execute("""
        SELECT COUNT(DISTINCT company) 
        FROM jobs 
        WHERE verified_email IS NOT NULL AND verified_email != ''
    """)
    companies_with_email = cursor.fetchone()[0]
    
    # Get high-value companies with emails
    cursor.execute("""
        SELECT company, verified_email, relevance_score
        FROM jobs
        WHERE verified_email IS NOT NULL 
        AND verified_email != ''
        AND relevance_score >= 0.65
        ORDER BY relevance_score DESC
        LIMIT 10
    """)
    high_value_ready = cursor.fetchall()
    
    # Get companies still needing emails
    cursor.execute("""
        SELECT DISTINCT company, MAX(relevance_score) as score
        FROM jobs
        WHERE (verified_email IS NULL OR verified_email = '')
        AND relevance_score >= 0.65
        GROUP BY company
        ORDER BY score DESC
        LIMIT 10
    """)
    need_emails = cursor.fetchall()
    
    conn.close()
    
    print(f"\n✅ READY TO APPLY:")
    print(f"  Companies with verified emails: {companies_with_email}")
    
    if high_value_ready:
        print(f"\n🎯 HIGH-VALUE COMPANIES READY (with emails):")
        for company, email, score in high_value_ready[:5]:
            print(f"  • {company}: {email} (Score: {score:.2f})")
    
    if need_emails:
        print(f"\n⚠️ HIGH-VALUE COMPANIES NEEDING EMAILS:")
        for company, score in need_emails[:5]:
            print(f"  • {company} (Score: {score:.2f})")
        
        print(f"\n💡 To add emails for these companies:")
        print(f"  python3 collect_real_emails.py")
        print(f"  Select option 2 to add manually")
    
    # Show sample of known emails
    print(f"\n📧 SAMPLE VERIFIED EMAILS IN DATABASE:")
    sample_emails = list(collector.known_company_emails.items())[:10]
    for company, email in sample_emails:
        print(f"  {company}: {email}")
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("\n🚀 NEXT STEPS:")
    print("  1. Apply to companies with verified emails:")
    print("     python3 automated_apply.py --batch 5")
    print("\n  2. Add more emails manually:")
    print("     python3 collect_real_emails.py")
    print("\n  3. Check email verification status:")
    print("     python3 enhanced_email_verifier.py")
    print("\n⚠️ IMPORTANT: System will now ONLY send to verified emails!")
    print("No more bounces! 🎯")

if __name__ == "__main__":
    main()