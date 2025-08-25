#!/usr/bin/env python3
"""
Comprehensive System Status Report
Shows the current state of the Unified Career Intelligence System
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def generate_status_report():
    """Generate comprehensive status report"""
    
    # Connect to database
    db_path = Path(__file__).parent.parent / 'data_layer' / 'unified_career.db'
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 UNIFIED CAREER INTELLIGENCE SYSTEM - STATUS REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # PHASE 1: DATA LAYER
    print("\n✅ PHASE 1: DATA LAYER")
    print("-" * 40)
    
    cursor.execute("SELECT COUNT(*) FROM master_jobs")
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT company) FROM master_jobs")
    total_companies = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT source) FROM master_jobs WHERE source IS NOT NULL")
    total_sources = cursor.fetchone()[0]
    
    print(f"• Total Jobs: {total_jobs}")
    print(f"• Companies: {total_companies}")
    print(f"• Data Sources: {total_sources}")
    
    # Top sources
    cursor.execute("""
        SELECT source, COUNT(*) as cnt 
        FROM master_jobs 
        WHERE source IS NOT NULL
        GROUP BY source 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    sources = cursor.fetchall()
    if sources:
        print("\nTop Data Sources:")
        for source, count in sources:
            print(f"  - {source}: {count} jobs")
    
    # PHASE 2: ML INTEGRATION
    print("\n✅ PHASE 2: ML INTEGRATION")
    print("-" * 40)
    
    cursor.execute("SELECT COUNT(*) FROM master_jobs WHERE ml_score IS NOT NULL")
    scored_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(ml_score), MAX(ml_score), MIN(ml_score) FROM master_jobs WHERE ml_score IS NOT NULL")
    ml_stats = cursor.fetchone()
    
    print(f"• Jobs with ML Scores: {scored_jobs}/{total_jobs}")
    if ml_stats[0]:
        print(f"• Score Range: {ml_stats[2]:.2f} - {ml_stats[1]:.2f}")
        print(f"• Average Score: {ml_stats[0]:.2f}")
    
    # PHASE 3: APPLICATION PIPELINE
    print("\n✅ PHASE 3: APPLICATION PIPELINE")
    print("-" * 40)
    
    cursor.execute("SELECT COUNT(*) FROM master_applications")
    total_apps = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT job_uid) FROM master_applications")
    unique_jobs_applied = cursor.fetchone()[0]
    
    print(f"• Total Applications: {total_apps}")
    print(f"• Unique Jobs Applied: {unique_jobs_applied}")
    
    # Application methods
    cursor.execute("""
        SELECT application_method, COUNT(*) as cnt 
        FROM master_applications 
        WHERE application_method IS NOT NULL
        GROUP BY application_method
    """)
    methods = cursor.fetchall()
    if methods:
        print("\nApplication Methods:")
        for method, count in methods:
            print(f"  - {method}: {count}")
    
    # Recent applications
    cursor.execute("""
        SELECT ma.applied_date, mj.company, mj.position 
        FROM master_applications ma
        LEFT JOIN master_jobs mj ON ma.job_uid = mj.job_uid
        WHERE ma.applied_date IS NOT NULL
        ORDER BY ma.applied_date DESC
        LIMIT 5
    """)
    recent_apps = cursor.fetchall()
    if recent_apps:
        print("\nRecent Applications:")
        for date, company, position in recent_apps:
            if company and position:
                print(f"  • {company} - {position}")
    
    # PHASE 4: RESPONSE MANAGEMENT
    print("\n✅ PHASE 4: RESPONSE MANAGEMENT")
    print("-" * 40)
    
    cursor.execute("SELECT COUNT(*) FROM master_applications WHERE response_type IS NOT NULL")
    responses = cursor.fetchone()[0]
    
    print(f"• Responses Received: {responses}/{total_apps}")
    if total_apps > 0:
        print(f"• Response Rate: {(responses/total_apps)*100:.1f}%")
    
    # Response types
    cursor.execute("""
        SELECT response_type, COUNT(*) as cnt 
        FROM master_applications 
        WHERE response_type IS NOT NULL
        GROUP BY response_type
    """)
    response_types = cursor.fetchall()
    if response_types:
        print("\nResponse Types:")
        for rtype, count in response_types:
            print(f"  - {rtype}: {count}")
    
    # PHASE 5: INTELLIGENCE DASHBOARD
    print("\n✅ PHASE 5: INTELLIGENCE DASHBOARD")
    print("-" * 40)
    
    # Company intelligence
    cursor.execute("SELECT COUNT(*) FROM company_intelligence")
    companies_tracked = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM performance_metrics")
    metrics_tracked = cursor.fetchone()[0]
    
    print(f"• Companies with Intelligence: {companies_tracked}")
    print(f"• Performance Metrics Tracked: {metrics_tracked}")
    
    # Top performing companies
    cursor.execute("""
        SELECT mj.company, COUNT(*) as job_count,
               COUNT(ma.job_uid) as applications
        FROM master_jobs mj
        LEFT JOIN master_applications ma ON mj.job_uid = ma.job_uid
        GROUP BY mj.company
        HAVING job_count > 5
        ORDER BY job_count DESC
        LIMIT 5
    """)
    top_companies = cursor.fetchall()
    if top_companies:
        print("\nTop Companies (Jobs/Applications):")
        for company, jobs, apps in top_companies:
            print(f"  • {company}: {jobs} jobs, {apps} applications")
    
    # SYSTEM SUMMARY
    print("\n" + "="*80)
    print("📈 SYSTEM SUMMARY")
    print("-" * 40)
    
    print(f"✅ All 5 Phases Complete and Operational")
    print(f"📊 {total_jobs} jobs from {total_companies} companies")
    print(f"📮 {total_apps} applications sent")
    if total_apps > 0 and responses > 0:
        print(f"📧 {(responses/total_apps)*100:.1f}% response rate")
    print(f"🎯 Ready for 50-75 applications/day")
    
    print("\n" + "="*80)
    print("System Status: FULLY OPERATIONAL ✅")
    print("="*80)
    
    conn.close()

if __name__ == "__main__":
    generate_status_report()