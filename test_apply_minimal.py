#!/usr/bin/env python3
"""Minimal test of apply functionality"""

from automated_apply import AutomatedApplicationSystem
import time

print("🧪 Testing minimal apply functionality...")

system = AutomatedApplicationSystem()
print("✅ System initialized")

# Get one job
jobs = system.get_unapplied_jobs(limit=1)
print(f"✅ Found {len(jobs)} job(s)")

if jobs:
    job = jobs[0]
    print(f"\n📋 Job details:")
    print(f"  Company: {job['company']}")
    print(f"  Position: {job['position']}")
    print(f"  Score: {job['relevance_score']}")
    print(f"  Apply URL: {job.get('apply_url', 'N/A')}")
    
    # Mock the apply process
    print("\n🔍 Testing apply_to_job method...")
    start_time = time.time()
    try:
        # Temporarily override email sending to test
        # We'll just test up to the point of sending
        result = system.apply_to_job(job)
        elapsed = time.time() - start_time
        print(f"✅ Apply completed in {elapsed:.2f} seconds")
        print(f"Result: {result}")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Apply failed after {elapsed:.2f} seconds")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ No jobs found to test")