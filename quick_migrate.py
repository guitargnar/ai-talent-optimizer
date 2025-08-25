#!/usr/bin/env python3
"""
Quick migration to import existing job data.
"""

import sqlite3
from pathlib import Path

def quick_migrate():
    """Quick and dirty migration to get data into new system."""
    
    # Connect to old database
    old_db = sqlite3.connect('UNIFIED_AI_JOBS.db')
    old_cursor = old_db.cursor()
    
    # Connect to new database  
    new_db = sqlite3.connect('data/unified_jobs.db')
    new_cursor = new_db.cursor()
    
    # Create simplified table if needed
    new_cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE,
            company TEXT,
            position TEXT,
            location TEXT,
            remote_option TEXT,
            salary_range TEXT,
            url TEXT,
            description TEXT,
            source TEXT,
            discovered_date TEXT,
            relevance_score REAL,
            applied INTEGER DEFAULT 0,
            applied_date TEXT,
            application_method TEXT,
            company_email TEXT,
            email_verified INTEGER DEFAULT 0,
            bounce_detected INTEGER DEFAULT 0,
            bounce_reason TEXT,
            status TEXT DEFAULT 'discovered',
            skip_reason TEXT,
            notes TEXT
        )
    ''')
    
    # Get data from old database
    old_cursor.execute('SELECT * FROM job_discoveries')
    columns = [description[0] for description in old_cursor.description]
    
    migrated = 0
    for row in old_cursor.fetchall():
        # Create dict from row
        data = dict(zip(columns, row))
        
        # Generate unique job_id
        job_id = f"{data['company']}_{data['position']}".replace(' ', '_').lower()[:100]
        
        try:
            # Insert into new database
            new_cursor.execute('''
                INSERT OR IGNORE INTO jobs (
                    job_id, company, position, location, remote_option,
                    salary_range, url, description, source, discovered_date,
                    relevance_score, applied, applied_date, company_email,
                    email_verified, bounce_detected, bounce_reason, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id,
                data['company'],
                data['position'],
                data.get('location'),
                data.get('remote_option'),
                data.get('salary_range'),
                data.get('url') or data.get('application_url'),
                data.get('description'),
                data.get('source', 'legacy'),
                data.get('discovered_date'),
                data.get('relevance_score', 0.5),
                data.get('applied', 0),
                data.get('applied_date'),
                data.get('actual_email_used') or data.get('verified_email'),
                data.get('email_verified', 0),
                data.get('bounce_detected', 0),
                data.get('bounce_reason'),
                data.get('notes')
            ))
            
            if new_cursor.rowcount > 0:
                migrated += 1
                
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    new_db.commit()
    
    print(f"\n✅ Migrated {migrated} jobs successfully!")
    
    # Show stats
    new_cursor.execute('SELECT COUNT(*) FROM jobs')
    total = new_cursor.fetchone()[0]
    
    new_cursor.execute('SELECT COUNT(*) FROM jobs WHERE applied = 1')
    applied = new_cursor.fetchone()[0]
    
    print(f"📊 Database now contains:")
    print(f"  • Total jobs: {total}")
    print(f"  • Applications sent: {applied}")
    
    old_db.close()
    new_db.close()

if __name__ == '__main__':
    Path('data').mkdir(exist_ok=True)
    quick_migrate()