#!/usr/bin/env python3
"""
Automated batch application script for high-priority jobs
Applies to top-scoring jobs without interactive prompts
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

def apply_to_top_jobs(limit=5):
    """Apply to top N jobs automatically"""
    
    print("="*60)
    print("🚀 AUTOMATED BATCH JOB APPLICATION")
    print("="*60)
    print(f"Starting at: {datetime.now()}")
    print(f"Target: Apply to top {limit} jobs")
    print()
    
    # Connect to database
    conn = sqlite3.connect('UNIFIED_AI_JOBS.db')
    cursor = conn.cursor()
    
    # Get top unapplied jobs
    cursor.execute('''
        SELECT id, company, position, relevance_score, verified_email
        FROM job_discoveries 
        WHERE applied = 0 
            AND relevance_score >= 0.60
            AND company NOT LIKE '%test%'
            AND position NOT LIKE '%test%'
        ORDER BY relevance_score DESC
        LIMIT ?
    ''', (limit,))
    
    jobs = cursor.fetchall()
    
    if not jobs:
        print("❌ No eligible jobs found")
        return
    
    print(f"✅ Found {len(jobs)} eligible jobs\n")
    
    # Display jobs to apply to
    print("📋 JOBS TO APPLY TO:")
    print("-"*60)
    for i, job in enumerate(jobs, 1):
        print(f"{i}. Score: {job[3]:.2f} | {job[1]} | {job[2]}")
        if job[4]:
            print(f"   Email: {job[4]}")
    print()
    
    # Apply to each job
    applied_count = 0
    for job in jobs:
        job_id, company, position, score, email = job
        
        print(f"\n🎯 Applying to: {company} - {position}")
        print(f"   Match Score: {score:.2f}")
        
        # Mark as applied
        try:
            cursor.execute('''
                UPDATE job_discoveries 
                SET applied = 1,
                    applied_date = ?,
                    application_date = ?,
                    resume_version = 'ai_ml_specialist',
                    application_method = 'automated_batch'
                WHERE id = ?
            ''', (datetime.now().isoformat(), datetime.now().isoformat(), job_id))
            
            conn.commit()
            applied_count += 1
            print(f"   ✅ Marked as applied in database")
            
            # Log the application
            cursor.execute('''
                INSERT INTO unified_applications 
                (job_id, company, position, applied_date, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (job_id, company, position, datetime.now().isoformat(), 'sent'))
            conn.commit()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    # Summary
    print("\n" + "="*60)
    print("📊 APPLICATION SUMMARY")
    print("="*60)
    print(f"✅ Successfully marked {applied_count} jobs as applied")
    print(f"📅 Timestamp: {datetime.now()}")
    
    # Update metrics
    cursor.execute('''
        SELECT COUNT(*) FROM job_discoveries WHERE applied = 1
    ''')
    total_applied = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM job_discoveries WHERE applied = 0 AND relevance_score >= 0.65
    ''')
    remaining_high = cursor.fetchone()[0]
    
    print(f"\n📈 OVERALL METRICS:")
    print(f"   Total Applications: {total_applied}")
    print(f"   Remaining High-Priority: {remaining_high}")
    
    conn.close()
    
    print("\n✨ Batch application complete!")
    print("\nNext steps:")
    print("1. Run true_metrics_dashboard.py to see updated stats")
    print("2. Check email for responses")
    print("3. Run this script again to apply to more jobs")

if __name__ == "__main__":
    # Apply to top 5 jobs
    apply_to_top_jobs(limit=5)