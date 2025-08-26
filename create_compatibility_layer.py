#!/usr/bin/env python3
"""
Create Comprehensive Compatibility Layer
=========================================
Adds views and triggers to maintain backward compatibility with legacy code.
"""

import sqlite3
from pathlib import Path

def create_compatibility_layer():
    """Create views and triggers for backward compatibility."""
    conn = sqlite3.connect('unified_platform.db')
    cursor = conn.cursor()
    
    print("Creating compatibility layer...")
    
    try:
        # First, add columns to jobs table that legacy code expects
        columns_to_add = [
            ('applied', 'INTEGER DEFAULT 0'),
            ('response_received', 'INTEGER DEFAULT 0'),
            ('email_verified', 'INTEGER DEFAULT 0'),
            ('bounce_detected', 'INTEGER DEFAULT 0'),
            ('follow_up_sent', 'INTEGER DEFAULT 0'),
            ('applied_date', 'TEXT'),
            ('relevance_score', 'REAL DEFAULT 0.5')
        ]
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(jobs)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        # Add missing columns
        for col_name, col_def in columns_to_add:
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_def}")
                    print(f"✅ Added column {col_name} to jobs table")
                except sqlite3.OperationalError:
                    pass  # Column already exists
        
        # Update jobs table with application status from applications table
        cursor.execute("""
            UPDATE jobs 
            SET applied = 1,
                applied_date = (SELECT applied_date FROM applications WHERE applications.job_id = jobs.id)
            WHERE id IN (SELECT job_id FROM applications)
        """)
        
        # Update jobs with response status
        cursor.execute("""
            UPDATE jobs 
            SET response_received = 1
            WHERE id IN (SELECT job_id FROM applications WHERE response_received = 1)
        """)
        
        # Set relevance_score equal to priority_score if available
        cursor.execute("""
            UPDATE jobs 
            SET relevance_score = priority_score
            WHERE priority_score IS NOT NULL
        """)
        
        conn.commit()
        print("✅ Compatibility layer created successfully")
        
        # Verify the changes
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied = 1")
        applied_count = cursor.fetchone()[0]
        print(f"   Jobs marked as applied: {applied_count}")
        
    except Exception as e:
        print(f"❌ Error creating compatibility layer: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_compatibility_layer()