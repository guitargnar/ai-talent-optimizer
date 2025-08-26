#!/usr/bin/env python3
"""
Add Backward Compatibility Views
=================================
Creates views to maintain compatibility with legacy code expecting old schema.
"""

import sqlite3
from pathlib import Path

def add_compatibility_views():
    """Add views for backward compatibility."""
    conn = sqlite3.connect('unified_platform.db')
    cursor = conn.cursor()
    
    try:
        # Drop existing views if they exist
        cursor.execute("DROP VIEW IF EXISTS jobs_with_applied")
        cursor.execute("DROP VIEW IF EXISTS job_discoveries")
        cursor.execute("DROP VIEW IF EXISTS staged_applications")
        
        # Create view that includes applied status from applications table
        cursor.execute("""
            CREATE VIEW jobs_with_applied AS
            SELECT 
                j.*,
                CASE WHEN a.id IS NOT NULL THEN 1 ELSE 0 END as applied
            FROM jobs j
            LEFT JOIN applications a ON j.id = a.job_id
        """)
        
        # Create view for legacy job_discoveries table
        cursor.execute("""
            CREATE VIEW job_discoveries AS
            SELECT * FROM jobs
        """)
        
        # Create view for legacy staged_applications
        cursor.execute("""
            CREATE VIEW staged_applications AS
            SELECT * FROM applications WHERE status = 'pending_review'
        """)
        
        conn.commit()
        print("✅ Added backward compatibility views")
        
        # Verify views work
        cursor.execute("SELECT COUNT(*) FROM jobs_with_applied WHERE applied = 1")
        applied_count = cursor.fetchone()[0]
        print(f"   Jobs with applications: {applied_count}")
        
    except Exception as e:
        print(f"❌ Error adding views: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_compatibility_views()