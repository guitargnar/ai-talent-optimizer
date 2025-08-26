#!/usr/bin/env python3
"""Test a single application"""

import sqlite3
from automated_apply import AutomatedApplicationSystem

# Get one unapplied job
conn = sqlite3.connect("unified_platform.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT * FROM jobs 
    WHERE applied = 0 AND relevance_score >= 0.65
    LIMIT 1
""")
job = cursor.fetchone()
conn.close()

if job:
    print(f"Testing with: {job['company']} - {job['position']}")
    
    # Create system
    system = AutomatedApplicationSystem()
    
    # Apply to single job
    result = system.apply_to_job(dict(job))
    
    if result:
        print("✅ Application process completed!")
    else:
        print("❌ Application failed")
else:
    print("No unapplied jobs found")