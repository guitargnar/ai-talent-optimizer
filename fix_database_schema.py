#!/usr/bin/env python3
"""
Fix database schema to support job discoveries
"""

import sqlite3
import os

def fix_database_schema():
    """Add missing columns to job_discoveries table"""
    
    db_path = "unified_platform.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get current schema
    cursor.execute("PRAGMA table_info(job_discoveries)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    print("📊 Current columns:", existing_columns)
    
    # Add missing columns
    columns_to_add = [
        ("location", "TEXT"),
        ("remote_option", "TEXT"),
        ("salary_range", "TEXT"),
        ("url", "TEXT"),
        ("description", "TEXT")
    ]
    
    added = 0
    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE job_discoveries ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name}")
                added += 1
            except sqlite3.OperationalError as e:
                print(f"⚠️  Could not add {column_name}: {e}")
    
    conn.commit()
    
    # Verify changes
    cursor.execute("PRAGMA table_info(job_discoveries)")
    new_columns = [row[1] for row in cursor.fetchall()]
    print(f"\n📊 Updated columns: {new_columns}")
    
    conn.close()
    
    print(f"\n✅ Database schema fixed! Added {added} columns.")
    return True

if __name__ == "__main__":
    fix_database_schema()