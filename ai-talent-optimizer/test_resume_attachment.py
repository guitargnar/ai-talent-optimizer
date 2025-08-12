#!/usr/bin/env python3
"""Test resume attachment functionality"""

import sqlite3
from automated_apply import AutomatedApplicationSystem

# Get one unapplied job
conn = sqlite3.connect('unified_talent_optimizer.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Find a technical role to test
cursor.execute("""
    SELECT * FROM job_discoveries 
    WHERE applied = 0 
    AND (position LIKE '%Engineer%' OR position LIKE '%Scientist%')
    LIMIT 1
""")
job = cursor.fetchone()
conn.close()

if job:
    print(f"🧪 Testing resume attachment for: {job['company']} - {job['position']}")
    
    # Create system
    system = AutomatedApplicationSystem()
    
    # Test resume selection
    print("\n1️⃣ Testing resume selection:")
    resume_path = system._select_resume_for_job(dict(job))
    print(f"Selected: {resume_path}")
    
    # Test if file exists
    from pathlib import Path
    if Path(resume_path).exists():
        print(f"✅ Resume file exists: {Path(resume_path).stat().st_size:,} bytes")
    else:
        print("❌ Resume file not found!")
        exit(1)
    
    # Send test automatically
    print(f"\n2️⃣ Sending test application to {job['company']}...")
    
    if True:
        result = system.apply_to_job(dict(job))
        if result:
            print("\n✅ Application sent with resume!")
            
            # Check BCC log to verify attachment
            import json
            with open('data/bcc_tracking_log.json', 'r') as f:
                log = json.load(f)
            
            # Find latest entry
            latest = max(log['sent_emails'].items(), 
                        key=lambda x: x[1]['sent_date'])
            
            print(f"\n📋 Latest email details:")
            print(f"  To: {latest[1]['to']}")
            print(f"  Attachments: {latest[1]['attachments']}")
        else:
            print("\n❌ Application failed")
else:
    print("No suitable jobs found for testing")