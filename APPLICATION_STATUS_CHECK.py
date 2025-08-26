#!/usr/bin/env python3
"""
Application Status Check - Emergency Verification
Confirms resume configuration and shows how applications are being sent
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import settings
from src.services.resume import ResumeService
from src.services.email_service import EmailService

def check_application_status():
    """Check how applications are being sent"""
    
    print("\n" + "="*80)
    print("🚨 APPLICATION STATUS CHECK - POST-TERMINATION")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Termination: Monday, August 19, 2025")
    print(f"Days Since: {(datetime.now() - datetime(2025, 8, 19)).days}")
    
    # 1. Resume Configuration
    print("\n📄 RESUME CONFIGURATION:")
    print("-" * 40)
    
    resume_service = ResumeService()
    configured_resume = settings.application.resume_path
    
    if Path(configured_resume).exists():
        size = Path(configured_resume).stat().st_size
        print(f"✅ Using: {Path(configured_resume).name}")
        print(f"   Size: {size:,} bytes")
        print(f"   Path: {configured_resume}")
        
        # Verify it's the 2025 resume
        if "2025" in configured_resume:
            print("   ⭐ CORRECT - This is your latest resume with Mirador project!")
        else:
            print("   ⚠️ WARNING - Not using 2025 resume!")
    else:
        print(f"❌ Resume not found at: {configured_resume}")
    
    # 2. Email Configuration
    print("\n✉️ EMAIL CONFIGURATION:")
    print("-" * 40)
    
    if settings.email.is_configured:
        print(f"✅ Email configured: {settings.email.address}")
        print(f"   SMTP: {settings.email.smtp_server}:{settings.email.smtp_port}")
        print(f"   Max per day: {settings.email.max_per_day}")
    else:
        print("❌ Email not configured!")
    
    # 3. Database Status
    print("\n💾 DATABASE STATUS:")
    print("-" * 40)
    
    db_path = Path(settings.database.path)
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count jobs
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active = 1")
        active_jobs = cursor.fetchone()[0]
        
        # Count applications
        cursor.execute("SELECT COUNT(*) FROM applications")
        total_apps = cursor.fetchone()[0]
        
        # Recent applications
        cursor.execute("""
            SELECT COUNT(*) FROM applications 
            WHERE date(discovered_date) >= date('now', '-7 days')
        """)
        recent_apps = cursor.fetchone()[0]
        
        print(f"📊 Active jobs: {active_jobs}")
        print(f"✉️ Total applications: {total_apps}")
        print(f"📅 Last 7 days: {recent_apps}")
        
        # Check if applications are using the correct resume
        cursor.execute("""
            SELECT resume_version, COUNT(*) 
            FROM applications 
            WHERE resume_path IS NOT NULL 
            GROUP BY resume_path
            ORDER BY COUNT(*) DESC
            LIMIT 5
        """)
        
        resume_usage = cursor.fetchall()
        if resume_usage:
            print("\n📋 Resume Usage in Applications:")
            for resume_version, count in resume_usage:
                resume_name = Path(resume_version).name if resume_path else "Unknown"
                if "2025" in str(resume_version):
                    print(f"   ⭐ {resume_name}: {count} applications")
                else:
                    print(f"   ⚠️ {resume_name}: {count} applications (outdated)")
        
        conn.close()
    else:
        print(f"❌ Database not found at: {db_path}")
    
    # 4. Application Pipeline Status
    print("\n🚀 APPLICATION PIPELINE:")
    print("-" * 40)
    
    print(f"✓ Max applications per day: {settings.application.max_applications_per_day}")
    print(f"✓ Min relevance score: {settings.application.min_relevance_score}")
    print(f"✓ Auto apply: {settings.application.auto_apply}")
    print(f"✓ Email delay: {settings.email.delay_seconds} seconds")
    
    # 5. Emergency Actions
    print("\n" + "="*80)
    print("🎯 IMMEDIATE ACTIONS REQUIRED:")
    print("="*80)
    
    actions_needed = []
    
    if not Path(configured_resume).exists() or "2025" not in configured_resume:
        actions_needed.append("FIX RESUME: Copy Matthew_Scott_2025_Professional_Resume.pdf to resumes/")
    
    if total_apps < 50:
        actions_needed.append("SEND APPLICATIONS: Run guided_apply.py to start sending")
    
    if recent_apps < 10:
        actions_needed.append("INCREASE VOLUME: Target 50 applications per day")
    
    if not settings.email.is_configured:
        actions_needed.append("CONFIGURE EMAIL: Set EMAIL_ADDRESS and EMAIL_APP_PASSWORD in .env")
    
    if actions_needed:
        for i, action in enumerate(actions_needed, 1):
            print(f"{i}. {action}")
    else:
        print("✅ System is properly configured and ready!")
    
    # 6. Commands to Run
    print("\n📝 COMMANDS TO RUN:")
    print("-" * 40)
    print("# Send applications with approval")
    print("python3 guided_apply.py")
    print()
    print("# Check for responses")
    print("python3 check_responses.py")
    print()
    print("# View system status")
    print("python3 main.py status")
    print()
    print("# Emergency batch send (use carefully)")
    print("python3 send_batch_applications.py --limit 50")
    
    print("\n" + "="*80)
    print("✅ Status check complete")
    print("="*80)

if __name__ == "__main__":
    check_application_status()