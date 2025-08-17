#!/usr/bin/env python3
"""
Send Batch Applications
Safely send multiple applications with the corrected resume
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.application import ApplicationService
from src.models.database import DatabaseManager, Job
from src.config.settings import settings

def send_batch_applications(max_count: int = 5):
    """Send batch of applications with safety controls"""
    
    print("\n" + "="*70)
    print("🚀 SENDING BATCH APPLICATIONS")
    print("="*70)
    
    # Check email configuration
    if not settings.email.is_configured:
        print("\n❌ Email not configured!")
        return False
    
    print(f"✅ Email configured: {settings.email.address}")
    print(f"📋 Will send up to {max_count} applications")
    
    # Get eligible jobs
    db = DatabaseManager()
    session = db.get_session()
    app_service = ApplicationService(db)
    
    sent_count = 0
    failed_count = 0
    
    try:
        # Get top unapplied jobs
        jobs = session.query(Job).filter(
            Job.applied == False,
            Job.relevance_score >= 0.8,  # High quality only
            Job.company_email != None,
            Job.company_email != 'N/A',
            ~Job.company_email.contains('adzuna'),
            ~Job.company_email.contains('indeed'),
            Job.source.in_(['Greenhouse', 'Lever'])
        ).order_by(
            Job.relevance_score.desc()
        ).limit(max_count).all()
        
        if not jobs:
            print("\n❌ No eligible jobs found")
            return False
        
        print(f"\n📊 Found {len(jobs)} eligible positions")
        
        for i, job in enumerate(jobs, 1):
            print(f"\n[{i}/{len(jobs)}] {job.company} - {job.position}")
            print(f"   Score: {job.relevance_score:.0%} | Email: {job.company_email}")
            
            # Send application
            print("   📤 Sending...")
            success, message = app_service.apply_to_job(job.id)
            
            if success:
                print(f"   ✅ Sent successfully!")
                sent_count += 1
            else:
                print(f"   ❌ Failed: {message}")
                failed_count += 1
            
            # Rate limiting
            if i < len(jobs):
                print(f"   ⏳ Waiting 30 seconds...")
                time.sleep(30)
        
        print("\n" + "="*70)
        print("📊 BATCH COMPLETE")
        print("="*70)
        print(f"✅ Sent: {sent_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📧 Total applications sent today: {sent_count}")
        
        if sent_count > 0:
            print("\n🎯 Next steps:")
            print("1. Check your Gmail sent folder")
            print("2. Monitor for responses")
            print("3. Run 'python main.py status' to track")
        
        return sent_count > 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        session.close()


if __name__ == "__main__":
    print("\n⚠️ This will send REAL job applications!")
    print("Using the corrected, accurate resume.")
    
    # Get count
    try:
        count = int(input("\nHow many to send? (1-10): ") or "3")
        count = min(max(count, 1), 10)
    except:
        count = 3
    
    confirm = input(f"\nSend {count} applications? (yes/no): ").lower()
    if confirm == 'yes':
        success = send_batch_applications(count)
        if success:
            print("\n🎉 Batch applications sent successfully!")
    else:
        print("\n✅ Cancelled. No applications sent.")