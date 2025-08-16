#!/usr/bin/env python3
"""Apply to top AI job immediately"""

import sqlite3
from automated_apply import AutomatedApplicationSystem

# Get the best AI job
conn = sqlite3.connect('unified_talent_optimizer.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Find best AI job
cursor.execute("""
    SELECT * FROM job_discoveries 
    WHERE applied = 0 
    AND (position LIKE '%AI%' OR position LIKE '%ML%' OR company LIKE '%AI%')
    ORDER BY relevance_score DESC
    LIMIT 1
""")
job = cursor.fetchone()

if job:
    print(f"\n🎯 Found AI Job: {job['company']} - {job['position']}")
    print(f"   Score: {job['relevance_score']}")
    print(f"   URL: {job['url']}")
    
    # Create system
    print("\n📧 Initializing application system...")
    system = AutomatedApplicationSystem()
    
    # Apply
    print(f"\n🚀 Applying to {job['company']}...")
    result = system.apply_to_job(dict(job))
    
    if result:
        print("\n✅ APPLICATION SENT SUCCESSFULLY!")
        # Mark as applied
        cursor.execute("UPDATE job_discoveries SET applied = 1, applied_date = datetime('now') WHERE id = ?", (job['id'],))
        conn.commit()
    else:
        print("\n❌ Application failed - check logs")
else:
    print("❌ No AI jobs found")

conn.close()