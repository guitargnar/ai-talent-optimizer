#!/usr/bin/env python3
"""Apply to top AI jobs NOW"""

import sqlite3
import time
from automated_apply import AutomatedApplicationSystem

# Get top AI jobs
conn = sqlite3.connect("unified_platform.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Find best AI jobs
cursor.execute("""
    SELECT * FROM jobs 
    WHERE applied = 0 
    AND (
        position LIKE '%AI%' OR 
        position LIKE '%ML%' OR 
        position LIKE '%Machine Learning%' OR
        position LIKE '%Principal%' OR
        position LIKE '%Staff%' OR
        company IN ('OpenAI', 'Anthropic', 'Google', 'Meta', 'Apple', 'Microsoft')
    )
    ORDER BY 
        CASE 
            WHEN company IN ('OpenAI', 'Anthropic', 'Google', 'Meta') THEN 1
            WHEN position LIKE '%Principal%' THEN 2
            WHEN position LIKE '%Staff%' THEN 3
            ELSE 4
        END,
        relevance_score DESC
    LIMIT 5
""")
jobs = cursor.fetchall()

if jobs:
    print(f"\n🎯 Found {len(jobs)} high-value AI jobs")
    
    # Create system
    system = AutomatedApplicationSystem()
    
    success_count = 0
    
    for job in jobs:
        print(f"\n{'='*60}")
        print(f"🏢 {job['company']} - {job['position']}")
        print(f"   Score: {job['relevance_score']}")
        print(f"   Location: {job['location'] or 'Remote'}")
        
        print(f"\n🚀 Applying...")
        result = system.apply_to_job(dict(job))
        
        if result:
            print("✅ SENT!")
            success_count += 1
            # Mark as applied
            cursor.execute("""
                UPDATE jobs 
                SET applied = 1, applied_date = datetime('now') 
                WHERE id = ?
            """, (job['id'],))
            conn.commit()
            
            # Wait between applications
            if success_count < len(jobs):
                print("⏳ Waiting 60 seconds...")
                time.sleep(60)
        else:
            print("❌ Failed - check logs")
    
    print(f"\n{'='*60}")
    print(f"✅ SUMMARY: {success_count}/{len(jobs)} applications sent successfully!")
else:
    print("❌ No AI jobs found")

conn.close()