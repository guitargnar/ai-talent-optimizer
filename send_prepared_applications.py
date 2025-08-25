#!/usr/bin/env python3
"""
Send Prepared Applications Non-Interactively
Sends the applications that were prepared by find_and_apply_best_jobs.py
"""

import json
import smtplib
import os
import time
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

# Load environment
load_dotenv()

def send_application_email(app_data, credentials):
    """Send a single application email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = credentials['email']
        msg['To'] = app_data['to_email']
        msg['Subject'] = app_data['subject']
        
        # Add body
        body = app_data['cover_letter']
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach resume if exists
        resume_path = Path(app_data['resume_path'])
        if resume_path.exists():
            with open(resume_path, 'rb') as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', 
                                filename='matthew_scott_ai_ml_resume.pdf')
                msg.attach(attach)
            print(f"   ✅ Resume attached")
        else:
            # Try alternate paths
            alt_paths = [
                Path('/Users/matthewscott/Desktop/MATTHEW_SCOTT_ULTIMATE_FINAL_2025.pdf'),
                Path('/Users/matthewscott/Desktop/Matthew_Scott_AI_Resume_FINAL.pdf'),
                Path('/Users/matthewscott/Desktop/Matthew_Scott_2025_Professional_Resume.pdf')
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    with open(alt_path, 'rb') as f:
                        attach = MIMEApplication(f.read(), _subtype="pdf")
                        attach.add_header('Content-Disposition', 'attachment',
                                        filename='matthew_scott_ai_ml_resume.pdf')
                        msg.attach(attach)
                    print(f"   ✅ Resume attached from: {alt_path.name}")
                    break
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(credentials['email'], credentials['password'])
        
        text = msg.as_string()
        server.sendmail(credentials['email'], app_data['to_email'], text)
        server.quit()
        
        print(f"   ✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to send: {e}")
        return False

def log_application(app_data, success):
    """Log the application to tracking file"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'company': app_data['job']['company'],
        'position': app_data['job']['position'],
        'email': app_data['to_email'],
        'status': 'sent' if success else 'failed',
        'job_id': app_data['job'].get('job_id', 'unknown')
    }
    
    log_file = Path('sent_applications_log.json')
    if log_file.exists():
        with open(log_file) as f:
            logs = json.load(f)
    else:
        logs = []
    
    logs.append(log_entry)
    
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)

def main():
    """Send all prepared applications"""
    print("\n" + "=" * 60)
    print("📮 SENDING PREPARED APPLICATIONS")
    print("=" * 60)
    
    # Load credentials
    email = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_APP_PASSWORD')
    
    if not email or not password:
        print("❌ Email credentials not configured in .env")
        return
    
    credentials = {'email': email, 'password': password}
    print(f"✅ Using email: {email}")
    
    # Find application files
    app_files = sorted(Path('.').glob('application_*.json'), 
                      key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not app_files:
        print("❌ No prepared applications found")
        print("   Run: python3 find_and_apply_best_jobs.py --auto")
        return
    
    print(f"\n📁 Found {len(app_files)} prepared applications")
    
    # Process each application
    sent_count = 0
    failed_count = 0
    
    for i, app_file in enumerate(app_files[:5], 1):  # Limit to 5 for safety
        print(f"\n{i}. Processing: {app_file.name}")
        
        try:
            with open(app_file) as f:
                app_data = json.load(f)
            
            company = app_data['job']['company']
            position = app_data['job']['position']
            
            print(f"   Company: {company}")
            print(f"   Position: {position[:50]}...")
            print(f"   To: {app_data['to_email']}")
            
            # Send the application
            success = send_application_email(app_data, credentials)
            
            if success:
                sent_count += 1
                log_application(app_data, True)
                
                # Archive the application file
                archive_dir = Path('sent_applications')
                archive_dir.mkdir(exist_ok=True)
                app_file.rename(archive_dir / app_file.name)
                print(f"   📁 Archived to sent_applications/")
            else:
                failed_count += 1
                log_application(app_data, False)
            
            # Rate limiting
            if i < len(app_files[:5]):
                print("   ⏳ Waiting 5 seconds...")
                time.sleep(5)
                
        except Exception as e:
            print(f"   ❌ Error processing file: {e}")
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Sent: {sent_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📁 Remaining: {len(app_files) - sent_count - failed_count}")
    
    if sent_count > 0:
        print("\n✨ Applications sent successfully!")
        print("\n📋 Next Steps:")
        print("1. Check your sent folder to confirm")
        print("2. Monitor responses with: python3 gmail_oauth_integration.py")
        print("3. Track status with: python3 career_automation_dashboard.py")
        print("4. Responses typically arrive in 3-7 days")
    
    # Update email tracker database
    if sent_count > 0:
        try:
            from email_application_tracker import EmailApplicationTracker
            tracker = EmailApplicationTracker()
            
            log_file = Path('sent_applications_log.json')
            with open(log_file) as f:
                logs = json.load(f)
            
            for log in logs[-sent_count:]:
                if log['status'] == 'sent':
                    tracker.log_email_application(
                        company=log['company'],
                        position=log['position'],
                        email_used=credentials['email'],
                        recipient_email=log['email']
                    )
            
            print(f"\n✅ Updated email application tracker database")
        except Exception as e:
            print(f"\n⚠️ Could not update tracker: {e}")

if __name__ == "__main__":
    main()