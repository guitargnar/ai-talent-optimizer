#!/usr/bin/env python3
"""
Simple test dashboard to verify database connectivity
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_database():
    """Test database connectivity and show basic stats"""
    
    # Connect to database
    db_path = Path(__file__).parent.parent / 'data_layer' / 'unified_career.db'
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return
    
    print(f"✅ Database found at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("🚀 UNIFIED CAREER SYSTEM - DATABASE TEST")
    print("="*80)
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n📊 Tables found: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Count jobs
    try:
        cursor.execute("SELECT COUNT(*) FROM master_jobs")
        job_count = cursor.fetchone()[0]
        print(f"\n📋 Jobs in database: {job_count}")
        
        # Show sample jobs
        cursor.execute("SELECT company, position FROM master_jobs LIMIT 5")
        jobs = cursor.fetchall()
        if jobs:
            print("\nSample jobs:")
            for company, position in jobs:
                print(f"  • {company} - {position}")
    except Exception as e:
        print(f"  ⚠️ Error reading jobs: {e}")
    
    # Count applications
    try:
        cursor.execute("SELECT COUNT(*) FROM master_applications")
        app_count = cursor.fetchone()[0]
        print(f"\n📮 Applications tracked: {app_count}")
    except Exception as e:
        print(f"  ⚠️ Error reading applications: {e}")
    
    # Count companies
    try:
        cursor.execute("SELECT COUNT(DISTINCT company) FROM master_jobs")
        company_count = cursor.fetchone()[0]
        print(f"\n🏢 Companies: {company_count}")
        
        # Top companies
        cursor.execute("""
            SELECT company, COUNT(*) as cnt 
            FROM master_jobs 
            GROUP BY company 
            ORDER BY cnt DESC 
            LIMIT 5
        """)
        top_companies = cursor.fetchall()
        if top_companies:
            print("\nTop companies by job count:")
            for company, count in top_companies:
                print(f"  • {company}: {count} jobs")
    except Exception as e:
        print(f"  ⚠️ Error reading companies: {e}")
    
    print("\n" + "="*80)
    print("✅ Database test complete!")
    print("="*80)
    
    conn.close()

if __name__ == "__main__":
    test_database()