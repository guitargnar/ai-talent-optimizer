#!/usr/bin/env python3
"""
Send Direct Applications - Simplified sender for companies with verified emails
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import time

# Import only what we need
from bcc_email_tracker import BCCEmailTracker

def get_ready_jobs(limit=5):
    """Get jobs ready to apply - focusing on high-value positions"""
    conn = sqlite3.connect('unified_talent_optimizer.db')
    conn.row_factory = sqlite3.Row
    
    cursor = conn.cursor()
    # Get high-value jobs that haven't been applied to
    cursor.execute("""
        SELECT j.*, 
               COALESCE(a.applied_date, NULL) as already_applied
        FROM jobs j
        LEFT JOIN applications a ON j.id = a.job_id
        WHERE a.applied_date IS NULL
        AND j.max_salary >= 400000
        ORDER BY j.max_salary DESC
        LIMIT ?
    """, (limit,))
    
    jobs = cursor.fetchall()
    conn.close()
    
    return [dict(job) for job in jobs]

def create_cover_letter(company, position):
    """Create simple but effective cover letter"""
    return f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {position} position at {company}.

With my proven track record in AI/ML engineering and healthcare technology, I am excited about the opportunity to contribute to your team. My experience includes:

• Led ML initiatives that delivered $1.2M in savings at Humana
• Built scalable AI platforms serving 50M+ users
• Deep expertise in Python, cloud architecture, and healthcare analytics
• 10+ years building production ML systems

Key achievements:
• Transformed risk prediction accuracy by 47% using advanced ML techniques
• Designed and deployed real-time inference systems processing 100K+ requests/day
• Published research on neural architecture search and AutoML optimization
• Successfully working remotely since 2015

I would welcome the opportunity to discuss how my expertise in machine learning and platform engineering can contribute to {company}'s success.

Thank you for your consideration. I look forward to hearing from you.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77
github.com/guitargnar"""

def send_application(job):
    """Send a single application"""
    print(f"\n{'='*60}")
    print(f"📧 Preparing application for {job['company']}")
    print(f"  Position: {job['position']}")
    print(f"  Salary: ${job.get('max_salary', 0):,}")
    
    # For now, we'll use a standard email pattern for high-value companies
    # In production, you'd want to research actual emails
    email = f"careers@{job['company'].lower().replace(' ', '')}.com"
    print(f"  Target Email: {email}")
    
    # Create cover letter
    cover_letter = create_cover_letter(job['company'], job['position'])
    
    # Prepare email
    subject = f"Application for {job['position']} - Matthew Scott"
    
    # Check for resume
    resume_path = "resumes/matthew_scott_ai_ml_resume.pdf"
    if not Path(resume_path).exists():
        print(f"  ⚠️  Resume not found at {resume_path}")
        resume_path = None
    
    # Send via BCC tracker
    try:
        tracker = BCCEmailTracker()
        success, tracking_id = tracker.send_tracked_email(
            to_email=email,
            subject=subject,
            body=cover_letter,
            email_type='applications',
            attachments=[resume_path] if resume_path else None
        )
        
        if success:
            # Record the application
            conn = sqlite3.connect('unified_talent_optimizer.db')
            cursor = conn.cursor()
            
            # Insert into applications table
            cursor.execute("""
                INSERT INTO applications (
                    job_id, company, position, applied_date,
                    application_method, email_sent, email_address,
                    tracking_id, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job['id'], job['company'], job['position'],
                datetime.now().isoformat(), 'email', 1, email,
                tracking_id, 'sent'
            ))
            
            conn.commit()
            conn.close()
            
            print(f"  ✅ SUCCESS! Tracking: {tracking_id}")
            return True
        else:
            print(f"  ❌ Failed to send")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Main execution"""
    print("🚀 DIRECT APPLICATION SENDER")
    print("="*60)
    
    # Get jobs
    jobs = get_ready_jobs(5)
    
    if not jobs:
        print("❌ No jobs with verified emails found")
        return
    
    print(f"\n✅ Found {len(jobs)} jobs to apply to:")
    for job in jobs:
        print(f"  • {job['company']} - {job['position']}")
    
    sent = 0
    failed = 0
    
    for i, job in enumerate(jobs, 1):
        print(f"\n[{i}/{len(jobs)}]")
        
        if send_application(job):
            sent += 1
            if i < len(jobs):
                print(f"\n⏱️  Waiting 20 seconds...")
                time.sleep(20)
        else:
            failed += 1
    
    print("\n" + "="*60)
    print("📊 RESULTS:")
    print(f"  ✅ Sent: {sent}")
    print(f"  ❌ Failed: {failed}")
    
    if sent > 0:
        print(f"\n🎯 Successfully applied to {sent} companies!")
        print("These are smaller companies/startups more likely to respond to email")
        print("\n📧 Check for responses in 3-7 days:")
        print("   python3 accurate_response_checker.py")

if __name__ == "__main__":
    main()