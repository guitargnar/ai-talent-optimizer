#!/usr/bin/env python3
"""
Complete migration of all job databases to unified system
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from data.models import init_database, Job, Application, Contact, Profile

def migrate_all_databases():
    """Complete migration from all legacy databases"""
    
    session = init_database()
    stats = {
        "jobs_migrated": 0,
        "high_value_jobs": 0,
        "contacts_migrated": 0
    }
    
    print("🔄 Starting comprehensive database migration...")
    
    # 1. Migrate principal_jobs_400k.db (high-value jobs)
    if Path("principal_jobs_400k.db").exists():
        print("\n📊 Migrating principal_jobs_400k.db...")
        conn = sqlite3.connect('unified_talent_optimizer.db')
        cursor = conn.cursor()
        
        # Get all unapplied high-value jobs
        cursor.execute("""
            SELECT company, position, location, min_salary, max_salary, applied
            FROM principal_jobs 
            WHERE applied = 0 AND max_salary >= 400000
            ORDER BY max_salary DESC
            LIMIT 100
        """)
        
        for row in cursor.fetchall():
            try:
                # Check if job already exists
                existing = session.query(Job).filter_by(
                    company=row[0],
                    position=row[1]
                ).first()
                
                if not existing:
                    job = Job(
                        company=row[0],
                        position=row[1],
                        location=row[2] if row[2] else "Remote",
                        min_salary=row[3],
                        max_salary=row[4],
                        source="principal_jobs",
                        priority_score=float(row[4]) / 100000 if row[4] else 0,
                        status='new'
                    )
                    session.add(job)
                    stats["jobs_migrated"] += 1
                    
                    if row[4] and row[4] >= 450000:
                        stats["high_value_jobs"] += 1
                        print(f"  💰 Added: {row[0]} - {row[1]} (${row[4]:,})")
                        
            except Exception as e:
                print(f"  ⚠️ Error migrating job: {e}")
                continue
        
        conn.close()
        session.commit()
    
    # 2. Migrate UNIFIED_AI_JOBS.db
    if Path("UNIFIED_AI_JOBS.db").exists():
        print("\n📊 Migrating UNIFIED_AI_JOBS.db...")
        conn = sqlite3.connect('unified_talent_optimizer.db')
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if ('unified_jobs',) in tables:
            cursor.execute("""
                SELECT company, title, location, min_salary, max_salary,
                       job_type, remote, url, is_applied
                FROM unified_jobs
                WHERE is_applied = 0 OR is_applied IS NULL
                LIMIT 50
            """)
            
            for row in cursor.fetchall():
                try:
                    existing = session.query(Job).filter_by(
                        company=row[0],
                        position=row[1]
                    ).first()
                    
                    if not existing:
                        job = Job(
                            company=row[0],
                            position=row[1],
                            location=row[2],
                            min_salary=row[3],
                            max_salary=row[4],
                            remote=row[6] if len(row) > 6 else False,
                            source_url=row[7] if len(row) > 7 else None,
                            source="unified_ai",
                            status='new'
                        )
                        session.add(job)
                        stats["jobs_migrated"] += 1
                        
                except Exception as e:
                    print(f"  ⚠️ Error: {e}")
                    continue
        
        conn.close()
        session.commit()
    
    # 3. Migrate CEO contacts from ceo_outreach.db
    if Path("ceo_outreach.db").exists():
        print("\n📊 Migrating ceo_outreach.db...")
        conn = sqlite3.connect('unified_talent_optimizer.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if ('ceo_contacts',) in tables:
            cursor.execute("SELECT * FROM ceo_contacts")
            for row in cursor.fetchall():
                try:
                    contact = Contact(
                        company=row[1] if len(row) > 1 else "Unknown",
                        name=row[2] if len(row) > 2 else None,
                        title="CEO",
                        email=row[3] if len(row) > 3 else None
                    )
                    session.add(contact)
                    stats["contacts_migrated"] += 1
                except Exception as e:
                    print(f"  ⚠️ Error: {e}")
                    continue
        
        conn.close()
        session.commit()
    
    # Print summary
    print("\n" + "="*50)
    print("✅ Migration Complete!")
    print("="*50)
    print(f"Total jobs migrated: {stats['jobs_migrated']}")
    print(f"High-value jobs ($450K+): {stats['high_value_jobs']}")
    print(f"CEO contacts migrated: {stats['contacts_migrated']}")
    
    # Show top opportunities
    print("\n🎯 Top 5 Opportunities in Database:")
    top_jobs = session.query(Job).filter(
        Job.max_salary >= 400000
    ).order_by(Job.max_salary.desc()).limit(5).all()
    
    for i, job in enumerate(top_jobs, 1):
        print(f"{i}. {job.company} - {job.position}")
        print(f"   💰 ${job.max_salary:,} | 📍 {job.location}")
    
    return stats

if __name__ == "__main__":
    migrate_all_databases()