#!/usr/bin/env python3
"""Debug automated application system"""

import sqlite3
import json
import traceback

# Check config
try:
    with open('unified_config.json', 'r') as f:
        config = json.load(f)
    print("✅ Config loaded successfully")
    print(f"  min_relevance_score: {config.get('min_relevance_score', 'NOT FOUND')}")
except Exception as e:
    print(f"❌ Config load failed: {e}")

# Check database
try:
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    
    # Count total jobs
    cursor.execute("SELECT COUNT(*) FROM job_discoveries")
    total_jobs = cursor.fetchone()[0]
    print(f"\n✅ Database connected: {total_jobs} total jobs")
    
    # Count unapplied jobs
    cursor.execute("SELECT COUNT(*) FROM job_discoveries WHERE applied = 0")
    unapplied = cursor.fetchone()[0]
    print(f"  📋 Unapplied jobs: {unapplied}")
    
    # Count by score
    min_score = config.get('min_relevance_score', 0.3)
    cursor.execute("SELECT COUNT(*) FROM job_discoveries WHERE applied = 0 AND relevance_score >= ?", (min_score,))
    eligible = cursor.fetchone()[0]
    print(f"  🎯 Jobs with score >= {min_score}: {eligible}")
    
    # Show top 5 eligible jobs
    cursor.execute("""
        SELECT company, position, relevance_score 
        FROM job_discoveries 
        WHERE applied = 0 AND relevance_score >= ?
        ORDER BY relevance_score DESC
        LIMIT 5
    """, (min_score,))
    
    print(f"\n📊 Top 5 eligible jobs:")
    for i, (company, position, score) in enumerate(cursor.fetchall(), 1):
        print(f"  {i}. {company} - {position} (Score: {score})")
    
    conn.close()
except Exception as e:
    print(f"❌ Database error: {e}")
    traceback.print_exc()

# Try importing modules
print("\n🔍 Checking imports...")
try:
    from email_application_tracker import EmailApplicationTracker
    print("✅ EmailApplicationTracker imported")
except Exception as e:
    print(f"❌ EmailApplicationTracker import failed: {e}")

try:
    from bcc_email_tracker import BCCEmailTracker
    print("✅ BCCEmailTracker imported")
except Exception as e:
    print(f"❌ BCCEmailTracker import failed: {e}")

try:
    from ats_ai_optimizer import ATSAIOptimizer
    print("✅ ATSAIOptimizer imported")
except Exception as e:
    print(f"❌ ATSAIOptimizer import failed: {e}")

try:
    from resume_pdf_generator import ResumePDFGenerator
    print("✅ ResumePDFGenerator imported")
except Exception as e:
    print(f"❌ ResumePDFGenerator import failed: {e}")

try:
    from improved_application_templates import ImprovedApplicationTemplates
    print("✅ ImprovedApplicationTemplates imported")
except Exception as e:
    print(f"❌ ImprovedApplicationTemplates import failed: {e}")

# Try initializing the system
print("\n🚀 Trying to initialize AutomatedApplicationSystem...")
try:
    from automated_apply import AutomatedApplicationSystem
    system = AutomatedApplicationSystem()
    print("✅ System initialized successfully")
    
    # Try getting jobs
    print("\n📋 Getting unapplied jobs...")
    jobs = system.get_unapplied_jobs(limit=3)
    print(f"✅ Found {len(jobs)} jobs")
    
except Exception as e:
    print(f"❌ System initialization failed: {e}")
    traceback.print_exc()