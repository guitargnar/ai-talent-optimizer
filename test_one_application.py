#!/usr/bin/env python3
"""Test sending one real application"""

from automated_apply import AutomatedApplicationSystem
import sqlite3

# Get one job to test with
conn = sqlite3.connect("unified_platform.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT * FROM jobs 
    WHERE applied = 0 AND company = 'OpenAI'
    LIMIT 1
""")
job = cursor.fetchone()
conn.close()

if job:
    print(f"Testing with job: {job['company']} - {job['position']}")
    
    # Create system
    system = AutomatedApplicationSystem()
    
    # Debug the email setup
    print(f"\nEmail setup:")
    print(f"Primary email: {system.bcc_tracker.primary_email}")
    print(f"Password loaded: {'Yes' if system.bcc_tracker.email_password else 'No'}")
    print(f"Password length: {len(system.bcc_tracker.email_password) if system.bcc_tracker.email_password else 0}")
    
    # Try to apply
    print("\nAttempting to apply...")
    success = system.apply_to_job(dict(job))
    
    if success:
        print("✅ Application sent successfully!")
    else:
        print("❌ Application failed")
else:
    print("No jobs found to test with")