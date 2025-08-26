#!/usr/bin/env python3
"""
Reset Failed Applications - Reset companies where emails bounced so we can try different methods
"""

import sqlite3

def reset_bounced_applications():
    """Reset applications that bounced so we can try again with correct methods"""
    conn = sqlite3.connect("unified_platform.db")
    cursor = conn.cursor()
    
    print("🔄 RESETTING BOUNCED APPLICATIONS")
    print("="*60)
    
    # Reset applications that bounced (except the ones we just successfully sent)
    cursor.execute("""
        UPDATE jobs
        SET applied = 0,
            application_invalid = 0,
            applied_date = NULL
        WHERE (bounce_detected = 1 OR application_invalid = 1)
        AND company NOT IN ('OpenAI', 'Anthropic', 'Google DeepMind')
    """)
    
    reset_count = cursor.rowcount
    
    # Also reset companies without any email
    cursor.execute("""
        UPDATE jobs
        SET applied = 0,
            application_invalid = 0
        WHERE applied = 1
        AND (verified_email IS NULL OR verified_email = '')
        AND (actual_email_used IS NULL OR actual_email_used = '')
    """)
    
    no_email_reset = cursor.rowcount
    
    conn.commit()
    
    # Get stats on what's available now
    cursor.execute("""
        SELECT COUNT(*) FROM jobs WHERE applied = 0
    """)
    available = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT company, title, relevance_score
        FROM jobs
        WHERE applied = 0
        AND relevance_score >= 0.5
        ORDER BY relevance_score DESC
        LIMIT 10
    """)
    
    top_jobs = cursor.fetchall()
    
    conn.close()
    
    print(f"\n✅ Reset {reset_count} bounced applications")
    print(f"✅ Reset {no_email_reset} applications with no email")
    print(f"\n📊 Total available jobs now: {available}")
    
    if top_jobs:
        print(f"\n🎯 TOP AVAILABLE JOBS:")
        for company, title, score in top_jobs:
            print(f"  • {company} - {position} (Score: {score:.2f})")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    reset_bounced_applications()