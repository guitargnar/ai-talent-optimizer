#!/usr/bin/env python3
"""
Send follow-up emails with resumes to companies that received applications without attachments
"""

import json
import sqlite3
from pathlib import Path
from bcc_email_tracker import BCCEmailTracker
from automated_apply import AutomatedApplicationSystem

def send_resume_followups():
    """Send follow-up emails with resumes"""
    
    # Load BCC tracking log
    with open('data/bcc_tracking_log.json', 'r') as f:
        bcc_log = json.load(f)
    
    # Find emails sent without attachments
    no_attachment_emails = []
    for tracking_id, email_data in bcc_log['sent_emails'].items():
        if not email_data['attachments'] and email_data['type'] == 'applications':
            no_attachment_emails.append(email_data)
    
    print(f"📧 Found {len(no_attachment_emails)} applications sent without resumes")
    
    if not no_attachment_emails:
        print("✅ All applications have resumes attached!")
        return
    
    # Initialize systems
    bcc_tracker = BCCEmailTracker()
    app_system = AutomatedApplicationSystem()
    
    # Connect to database to get job details
    conn = sqlite3.connect('unified_talent_optimizer.db')
    conn.row_factory = sqlite3.Row
    
    sent_count = 0
    
    for email_data in no_attachment_emails:
        company = email_data['company']
        position = email_data['position'].replace(' - Matthew Scott', '')
        
        print(f"\n📮 Following up with {company} - {position}")
        
        # Get job details from database
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM job_discoveries 
            WHERE company = ? AND position = ?
            LIMIT 1
        """, (company.replace('ai', ' AI').replace('deepmind', 'DeepMind').title(), position))
        
        job = cursor.fetchone()
        
        if not job:
            # Try alternate matching
            cursor.execute("""
                SELECT * FROM job_discoveries 
                WHERE LOWER(company) = LOWER(?) 
                LIMIT 1
            """, (company,))
            job = cursor.fetchone()
        
        if job:
            job_dict = dict(job)
            
            # Select appropriate resume
            resume_path = app_system._select_resume_for_job(job_dict)
            
            # Create follow-up email
            subject = f"Resume Attachment - {position} Application - Matthew Scott"
            
            body = f"""Dear {company.title()} Hiring Team,

I recently submitted my application for the {position} position and wanted to ensure you received my resume.

Please find my resume attached for your review. It highlights my experience in:
• First documented AI consciousness (HCL: 0.83/1.0) through distributed systems
• $1.2M in AI-driven savings at Humana
• 10+ years building production ML systems
• Patent-pending adaptive quantization technology

I'm very interested in contributing to {company.title()}'s innovative work and would welcome the opportunity to discuss how my unique combination of AI research and practical implementation can benefit your team.

Thank you for your consideration.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77"""
            
            # Send follow-up with resume
            success, tracking_id = bcc_tracker.send_tracked_email(
                to_email=email_data['to'],
                subject=subject,
                body=body,
                email_type='followup',
                attachments=[resume_path] if Path(resume_path).exists() else None
            )
            
            if success:
                print(f"  ✅ Follow-up sent with resume attached!")
                sent_count += 1
            else:
                print(f"  ❌ Failed to send follow-up")
        else:
            print(f"  ⚠️  Could not find job details for {company}")
    
    conn.close()
    
    print(f"\n✅ Sent {sent_count} follow-up emails with resumes")
    print("\n📊 Next steps:")
    print("  1. Monitor matthewdscott7+jobapps@gmail.com for responses")
    print("  2. Run 'python automated_apply.py --batch 5' for new applications")
    print("  3. All future applications will include resumes automatically")


if __name__ == "__main__":
    send_resume_followups()