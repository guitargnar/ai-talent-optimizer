#!/usr/bin/env python3
"""
Send First Application
Sends a single application to test the system
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.application import ApplicationService
from src.services.email_service import EmailService
from src.models.database import DatabaseManager, Job
from src.config.settings import settings

def send_first_application():
    """Send the first application to Anthropic"""
    
    print("\n" + "="*70)
    print("🚀 SENDING FIRST JOB APPLICATION")
    print("="*70)
    
    # Check email configuration
    if not settings.email.is_configured:
        print("\n❌ Email not configured!")
        print("Please run: python setup_email_smtp.py")
        return False
    
    print(f"\n✅ Email configured: {settings.email.address}")
    
    # Get the top Anthropic job
    db = DatabaseManager()
    session = db.get_session()
    
    try:
        # Get first unapplied Anthropic job
        job = session.query(Job).filter(
            Job.applied == False,
            Job.company == 'Anthropic',
            Job.relevance_score >= 0.9
        ).first()
        
        if not job:
            print("\n❌ No eligible Anthropic jobs found")
            return False
        
        print(f"\n📋 JOB DETAILS:")
        print(f"   Company: {job.company}")
        print(f"   Position: {job.position}")
        print(f"   Email to: {job.company_email}")
        print(f"   Relevance: {job.relevance_score:.0%}")
        
        # Confirm before sending
        print("\n⚠️ READY TO SEND APPLICATION")
        print("This will send a real email to Anthropic!")
        
        confirm = input("\nProceed? (yes/no): ").lower()
        if confirm != 'yes':
            print("❌ Cancelled")
            return False
        
        print("\n📤 Sending application...")
        
        # Send via application service
        app_service = ApplicationService(db)
        success, message = app_service.apply_to_job(job.id)
        
        if success:
            print(f"\n✅ SUCCESS! {message}")
            print("\n📧 Application sent to careers@anthropic.com")
            print("📁 Check your Gmail sent folder for confirmation")
            print("\n🎯 Next steps:")
            print("1. Monitor your email for responses")
            print("2. Run 'python main.py status' to track")
            print("3. Use 'python guided_apply.py' for more applications")
            return True
        else:
            print(f"\n❌ Failed: {message}")
            
            # Provide troubleshooting
            if "Email not configured" in message:
                print("\n🔧 Fix: Run 'python test_email_config.py'")
            elif "Job board email" in message:
                print("\n🔧 This job has a job board email, trying next...")
                # Try another job
                next_job = session.query(Job).filter(
                    Job.applied == False,
                    Job.company != 'Anthropic',  # Try different company
                    Job.relevance_score >= 0.8,
                    ~Job.company_email.contains('adzuna')
                ).first()
                
                if next_job:
                    print(f"\n🔄 Trying: {next_job.company} - {next_job.position}")
                    success, message = app_service.apply_to_job(next_job.id)
                    if success:
                        print(f"✅ SUCCESS! Sent to {next_job.company}")
                        return True
            
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        session.close()


if __name__ == "__main__":
    print("\n⚠️ This will send a REAL job application email!")
    print("Make sure you're ready to apply to Anthropic.")
    
    ready = input("\nAre you ready to send your first application? (yes/no): ").lower()
    if ready == 'yes':
        success = send_first_application()
        if success:
            print("\n🎉 Congratulations on sending your first application!")
    else:
        print("\n✅ No problem! Run this when you're ready.")
        print("You can also preview first with: python preview_applications.py")