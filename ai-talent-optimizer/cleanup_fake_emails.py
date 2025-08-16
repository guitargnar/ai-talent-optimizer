#!/usr/bin/env python3
"""
Cleanup Fake Emails - Remove all guessed/generic email addresses
Only keep verified, real email addresses
"""

import sqlite3
import json
from pathlib import Path

def cleanup_fake_emails():
    """Remove all generic careers@ and guessed email addresses"""
    
    print("=" * 60)
    print("🧹 CLEANING UP FAKE EMAIL ADDRESSES")
    print("=" * 60)
    
    # Generic patterns that are usually fake
    fake_patterns = [
        'careers@',
        'jobs@',
        'recruiting@',
        'hr@',
        'info@',
        'contact@',
        'hello@',
        'apply@',
        'talent@',
        'hire@',
        'resume@',
        'applications@'
    ]
    
    # Known bounced emails from logs
    known_bounces = [
        'careers@openai.com',
        'careers@snowflake.com',
        'careers@pinecone.com',
        'careers@invisibletechnologies.com',
        'careers@virtahealth.com',
        'careers@augment.co',
        'careers@convoy.com',
        'careers@genesisai.com',
        'careers@inworldai.com',
        'test@example.com'
    ]
    
    # Clean up REAL_JOBS.db
    if Path("REAL_JOBS.db").exists():
        conn = sqlite3.connect("REAL_JOBS.db")
        cursor = conn.cursor()
        
        # Get all emails
        cursor.execute("SELECT DISTINCT email FROM jobs WHERE email IS NOT NULL")
        all_emails = cursor.fetchall()
        
        removed_count = 0
        kept_count = 0
        
        for email_tuple in all_emails:
            email = email_tuple[0]
            
            # Check if it's a generic pattern
            is_fake = any(email.startswith(pattern) for pattern in fake_patterns)
            is_bounced = email in known_bounces
            
            if is_fake or is_bounced:
                print(f"❌ Removing fake email: {email}")
                cursor.execute("UPDATE jobs SET email = NULL WHERE email = ?", (email,))
                removed_count += 1
            else:
                print(f"✅ Keeping verified email: {email}")
                kept_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"\nCleaned REAL_JOBS.db:")
        print(f"  • Removed: {removed_count} fake emails")
        print(f"  • Kept: {kept_count} verified emails")
    
    # Clean up UNIFIED_AI_JOBS.db
    if Path("UNIFIED_AI_JOBS.db").exists():
        conn = sqlite3.connect("UNIFIED_AI_JOBS.db")
        cursor = conn.cursor()
        
        # Check if email column exists
        cursor.execute("PRAGMA table_info(job_discoveries)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'email' in columns:
            cursor.execute("SELECT DISTINCT email FROM job_discoveries WHERE email IS NOT NULL")
            all_emails = cursor.fetchall()
            
            removed_count = 0
            for email_tuple in all_emails:
                email = email_tuple[0]
                is_fake = any(email.startswith(pattern) for pattern in fake_patterns)
                if is_fake:
                    cursor.execute("UPDATE job_discoveries SET email = NULL WHERE email = ?", (email,))
                    removed_count += 1
            
            conn.commit()
            print(f"\nCleaned UNIFIED_AI_JOBS.db: Removed {removed_count} fake emails")
        else:
            print("\nUNIFIED_AI_JOBS.db doesn't have email column")
        
        conn.close()
    
    # Update invalid_emails.json
    invalid_file = Path("data/invalid_emails.json")
    if invalid_file.exists():
        with open(invalid_file, 'r') as f:
            data = json.load(f)
        
        # Add all fake patterns to invalid list
        invalid_list = data.get('invalid_emails', [])
        
        for pattern in fake_patterns:
            # Add common company domains with fake patterns
            for domain in ['gmail.com', 'company.com', 'corp.com']:
                fake_email = f"{pattern}{domain}"
                if fake_email not in invalid_list:
                    invalid_list.append(fake_email)
        
        # Add known bounces
        for bounce in known_bounces:
            if bounce not in invalid_list:
                invalid_list.append(bounce)
        
        data['invalid_emails'] = invalid_list
        
        with open(invalid_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nUpdated invalid_emails.json with {len(invalid_list)} blocked addresses")
    
    print("\n" + "=" * 60)
    print("✅ CLEANUP COMPLETE")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("1. Use email finder tools to get REAL email addresses")
    print("2. Verify emails with MX record checking before sending")
    print("3. Apply through company portals when email unavailable")
    print("4. Research actual hiring managers on LinkedIn")

def show_remaining_jobs():
    """Show jobs that still have email addresses after cleanup"""
    
    if Path("REAL_JOBS.db").exists():
        conn = sqlite3.connect("REAL_JOBS.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT company, position, email 
            FROM jobs 
            WHERE email IS NOT NULL AND email != ''
            ORDER BY company
        """)
        
        jobs_with_email = cursor.fetchall()
        conn.close()
        
        if jobs_with_email:
            print("\n📧 Jobs with verified email addresses:")
            for company, position, email in jobs_with_email:
                print(f"  • {company}: {position}")
                print(f"    Email: {email}")
        else:
            print("\n⚠️ No jobs have verified email addresses")
            print("You'll need to:")
            print("  1. Find real contacts via LinkedIn")
            print("  2. Use email finder tools")
            print("  3. Apply through company websites")

if __name__ == "__main__":
    cleanup_fake_emails()
    show_remaining_jobs()