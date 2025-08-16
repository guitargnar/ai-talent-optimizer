#!/usr/bin/env python3
"""
Simple Apply - Clean, manual application system
No automation tricks, just send real applications to real jobs
"""

import sqlite3
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from dotenv import load_dotenv
import json

class SimpleApplicationSender:
    def __init__(self):
        """Initialize with clean configuration"""
        load_dotenv()
        self.email = os.getenv('EMAIL_ADDRESS')
        self.password = os.getenv('EMAIL_APP_PASSWORD')
        self.db_path = "REAL_JOBS.db"
        self.tracking_db = "APPLICATION_TRACKING.db"
        
        # Your real information
        self.my_info = {
            'name': 'Matthew Scott',
            'email': 'matthewdscott7@gmail.com',
            'phone': '(502) 345-0525',
            'linkedin': 'linkedin.com/in/mscott77',
            'github': 'github.com/guitargnar',
            'current_role': 'Senior Risk Management Professional II at Humana',
            'years_experience': '10+ years',
            'key_achievement': '$1.2M annual savings through AI automation'
        }
        
        # Resume path
        self.resume_path = Path("resumes/matthew_scott_ai_ml_resume.pdf")
        if not self.resume_path.exists():
            print(f"⚠️ Resume not found at {self.resume_path}")
            self.resume_path = None
        
        # Initialize tracking database
        self._init_tracking_db()
    
    def _init_tracking_db(self):
        """Create simple tracking database"""
        conn = sqlite3.connect(self.tracking_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                email_to TEXT NOT NULL,
                email_sent BOOLEAN DEFAULT 0,
                sent_date TEXT,
                cover_letter TEXT,
                response_received BOOLEAN DEFAULT 0,
                response_date TEXT,
                response_type TEXT,
                notes TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_available_jobs(self, limit=10):
        """Get jobs we haven't applied to yet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, company, position, location, remote, 
                   salary_min, salary_max, url, email
            FROM jobs
            WHERE applied = 0
            AND email IS NOT NULL
            AND email != ''
            ORDER BY 
                CASE 
                    WHEN position LIKE '%Principal%' THEN 1
                    WHEN position LIKE '%Staff%' THEN 2
                    WHEN position LIKE '%Senior Manager%' THEN 3
                    WHEN position LIKE '%Senior%' THEN 4
                    ELSE 5
                END,
                salary_max DESC NULLS LAST
            LIMIT ?
        """, (limit,))
        
        jobs = cursor.fetchall()
        conn.close()
        
        return jobs
    
    def generate_cover_letter(self, company, position):
        """Generate simple, effective cover letter"""
        cover_letter = f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {position} position at {company}.

With over 10 years of experience at Humana, where I currently serve as a Senior Risk Management Professional II, I have successfully delivered $1.2M in annual savings through AI automation while maintaining 99.9% system uptime. My work has directly improved Medicare Stars ratings by 8%, impacting over $50M in CMS bonus payments.

What makes me uniquely qualified for this role:

• Deep Healthcare Domain Expertise: A decade at a Fortune 50 healthcare company gives me intimate knowledge of compliance, regulatory requirements, and the unique challenges of healthcare technology.

• Proven AI/ML Implementation: I've architected and deployed production AI systems processing over 1M predictions daily with sub-100ms latency, demonstrating both technical depth and operational excellence.

• Business Impact Focus: Every system I build is measured by business outcomes - cost savings, compliance rates, and user satisfaction - not just technical metrics.

I am particularly drawn to {company}'s mission and believe my combination of technical expertise and healthcare domain knowledge would be valuable to your team.

I would welcome the opportunity to discuss how my experience building scalable, compliant AI systems could contribute to {company}'s continued success.

Best regards,
Matthew Scott
{self.my_info['phone']}
{self.my_info['email']}
{self.my_info['linkedin']}
"""
        return cover_letter
    
    def send_application(self, job_id, company, position, to_email):
        """Send a single application with tracking"""
        print(f"\n📧 Sending application to {company} for {position}")
        print(f"   To: {to_email}")
        
        # Generate cover letter
        cover_letter = self.generate_cover_letter(company, position)
        
        # Track in database first
        track_conn = sqlite3.connect(self.tracking_db)
        track_cursor = track_conn.cursor()
        
        track_cursor.execute("""
            INSERT INTO applications (company, position, email_to, cover_letter)
            VALUES (?, ?, ?, ?)
        """, (company, position, to_email, cover_letter))
        
        tracking_id = track_cursor.lastrowid
        track_conn.commit()
        
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = f"Application for {position} - Matthew Scott"
            
            # Add BCC for tracking
            bcc_email = f"{self.email.split('@')[0]}+jobapps@gmail.com"
            
            # Attach cover letter
            msg.attach(MIMEText(cover_letter, 'plain'))
            
            # Attach resume if available
            if self.resume_path and self.resume_path.exists():
                with open(self.resume_path, 'rb') as f:
                    attach = MIMEApplication(f.read(), _subtype="pdf")
                    attach.add_header('Content-Disposition', 'attachment', 
                                    filename='Matthew_Scott_Resume.pdf')
                    msg.attach(attach)
                print("   ✅ Resume attached")
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email, self.password)
            
            # Send to both recipient and BCC
            recipients = [to_email, bcc_email]
            server.sendmail(self.email, recipients, msg.as_string())
            server.quit()
            
            # Update tracking
            track_cursor.execute("""
                UPDATE applications 
                SET email_sent = 1, sent_date = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), tracking_id))
            
            # Update job as applied
            job_conn = sqlite3.connect(self.db_path)
            job_cursor = job_conn.cursor()
            job_cursor.execute("""
                UPDATE jobs 
                SET applied = 1, applied_date = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), job_id))
            job_conn.commit()
            job_conn.close()
            
            print("   ✅ Application sent successfully!")
            print(f"   📋 Tracking ID: {tracking_id}")
            print(f"   📬 BCC copy sent to: {bcc_email}")
            
            track_conn.commit()
            track_conn.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to send: {e}")
            
            # Update tracking with failure
            track_cursor.execute("""
                UPDATE applications 
                SET notes = ?
                WHERE id = ?
            """, (f"Failed: {str(e)}", tracking_id))
            track_conn.commit()
            track_conn.close()
            return False
    
    def show_status(self):
        """Show application status"""
        conn = sqlite3.connect(self.tracking_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(email_sent) as sent,
                   SUM(response_received) as responses
            FROM applications
        """)
        
        stats = cursor.fetchone()
        
        print("\n" + "=" * 60)
        print("📊 APPLICATION STATUS")
        print("=" * 60)
        print(f"Total Applications: {stats[0]}")
        print(f"Successfully Sent: {stats[1] or 0}")
        print(f"Responses Received: {stats[2] or 0}")
        
        # Show recent applications
        cursor.execute("""
            SELECT company, position, sent_date, response_received
            FROM applications
            WHERE email_sent = 1
            ORDER BY sent_date DESC
            LIMIT 5
        """)
        
        recent = cursor.fetchall()
        if recent:
            print("\n📅 Recent Applications:")
            for app in recent:
                response = "✅ Response" if app[3] else "⏳ Waiting"
                print(f"  • {app[0]}: {app[1]}")
                print(f"    Sent: {app[2][:10]} | Status: {response}")
        
        conn.close()

def main():
    """Run the simple application system"""
    print("=" * 60)
    print("🚀 SIMPLE JOB APPLICATION SYSTEM")
    print("=" * 60)
    
    sender = SimpleApplicationSender()
    
    # Show current status
    sender.show_status()
    
    # Get available jobs
    print("\n🔍 Finding jobs to apply to...")
    jobs = sender.get_available_jobs(limit=5)
    
    if not jobs:
        print("❌ No jobs with email addresses found")
        print("💡 Run job_scraper_v2.py to get more jobs")
        return
    
    print(f"\n📋 Found {len(jobs)} jobs to apply to:")
    for i, job in enumerate(jobs, 1):
        job_id, company, position, location, remote, sal_min, sal_max, url, email = job
        remote_str = "Remote" if remote else location
        salary = f"${sal_min/1000:.0f}K-${sal_max/1000:.0f}K" if sal_min else "Not listed"
        
        print(f"\n{i}. {company}: {position}")
        print(f"   Location: {remote_str}")
        print(f"   Salary: {salary}")
        print(f"   Email: {email}")
    
    # Ask user to confirm
    print("\n" + "-" * 60)
    response = input("Send applications to these 5 jobs? (y/n): ").strip().lower()
    
    if response == 'y':
        success_count = 0
        for job in jobs:
            job_id, company, position, _, _, _, _, _, email = job
            if sender.send_application(job_id, company, position, email):
                success_count += 1
        
        print("\n" + "=" * 60)
        print(f"✅ COMPLETE: Sent {success_count} applications")
        print("=" * 60)
    else:
        print("❌ Cancelled - no applications sent")

if __name__ == "__main__":
    main()