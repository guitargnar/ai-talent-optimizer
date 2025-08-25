#!/usr/bin/env python3
"""
Integrated Automation System
Combines all components with proper error handling
"""

import os
import sys
import time
import json
import sqlite3
from datetime import datetime

# Add path for imports
sys.path.insert(0, "/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer")

from email_validator import EmailValidator
from resume_selector import select_resume_for_job
from db_config import get_db_connection
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

load_dotenv("/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/.env")


class IntegratedAutomation:
    """Fully integrated automation system"""
    
    def __init__(self):
        self.validator = EmailValidator()
        self.email_address = os.getenv("EMAIL_ADDRESS", "matthewdscott7@gmail.com")
        self.email_password = os.getenv("EMAIL_APP_PASSWORD", "")
        self.applied_count = 0
        self.failed_count = 0
        
    def apply_to_job(self, job):
        """Apply to a single job with full validation"""
        
        company = job['company']
        position = job['position']
        
        print(f"\n📋 {company} - {position}")
        
        # Step 1: Find correct email
        email_info = self.validator.find_correct_email(company)
        
        if email_info['method'] == 'web_form':
            print(f"   ℹ️ Use web form: {email_info['instruction']}")
            self.log_application(job, method='web_form', instruction=email_info['instruction'])
            return False
            
        elif email_info['method'] == 'email' and email_info['email']:
            target_email = email_info['email']
            
            # Step 2: Validate email
            validation = self.validator.validate_before_send(target_email, company)
            
            if not validation['send_ok']:
                print(f"   ❌ Invalid email: {validation['reason']}")
                self.failed_count += 1
                return False
            
            # Step 3: Select resume
            resume_path = select_resume_for_job(job)
            if not resume_path:
                print("   ❌ No resume available")
                return False
            
            # Step 4: Generate cover letter
            cover_letter = self.generate_cover_letter(job)
            
            # Step 5: Send application
            success = self.send_application(job, target_email, resume_path, cover_letter)
            
            if success:
                self.applied_count += 1
                self.log_application(job, method='email', email=target_email, status='sent')
                return True
            else:
                self.failed_count += 1
                return False
        
        else:
            print(f"   ⚠️ No application method found")
            return False
    
    def send_application(self, job, email, resume_path, cover_letter):
        """Send application email with resume"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = email
            msg['Bcc'] = f"{self.email_address.split('@')[0]}+jobapps@gmail.com"
            msg['Subject'] = f"Application for {job['position']} at {job['company']}"
            
            # Add cover letter
            msg.attach(MIMEText(cover_letter, 'plain'))
            
            # Add resume
            with open(resume_path, 'rb') as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', 
                                filename=os.path.basename(resume_path))
                msg.attach(attach)
            
            # Send
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"   ✅ Sent to {email}")
            return True
            
        except Exception as e:
            print(f"   ❌ Send failed: {str(e)[:50]}")
            return False
    
    def generate_cover_letter(self, job):
        """Generate personalized cover letter"""
        # This would integrate with your AI system
        # For now, using template
        return f"""Dear Hiring Team at {job['company']},

I am writing to express my strong interest in the {job['position']} position at {job['company']}.

With extensive experience in software engineering and AI/ML applications, including projects like:
• Reflexia Model Manager - LLM deployment with adaptive quantization
• FinanceForge - Financial optimization achieving $1,097/year savings
• Guitar Consciousness - ML-based personalized learning system

I am confident I can contribute significantly to your team's success.

I have attached my resume for your review and would welcome the opportunity to discuss how my skills and experience align with your needs.

Thank you for your consideration.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
"""
    
    def log_application(self, job, **kwargs):
        """Log application attempt to database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update job as applied
        cursor.execute("""
            UPDATE job_discoveries 
            SET applied = 1, 
                application_date = ?,
                application_method = ?,
                email_used = ?
            WHERE company = ? AND position = ?
        """, (
            datetime.now().isoformat(),
            kwargs.get('method', 'unknown'),
            kwargs.get('email', ''),
            job['company'],
            job['position']
        ))
        
        conn.commit()
        conn.close()
    
    def run_batch(self, count=3):
        """Run a batch of applications"""
        print("\n🚀 INTEGRATED AUTOMATION BATCH")
        print("="*60)
        
        # Get unapplied jobs
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT company, position, url, salary_range, relevance_score
            FROM job_discoveries
            WHERE applied = 0
            ORDER BY relevance_score DESC
            LIMIT ?
        """, (count,))
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'company': row[0],
                'position': row[1],
                'url': row[2],
                'salary': row[3],
                'score': row[4]
            })
        
        conn.close()
        
        if not jobs:
            print("No unapplied jobs found")
            return
        
        print(f"\nProcessing {len(jobs)} jobs...")
        
        for i, job in enumerate(jobs, 1):
            print(f"\n[{i}/{len(jobs)}]", end="")
            self.apply_to_job(job)
            
            if i < len(jobs):
                time.sleep(30)  # Wait between applications
        
        print(f"\n\n📊 RESULTS")
        print(f"   ✅ Sent: {self.applied_count}")
        print(f"   ❌ Failed: {self.failed_count}")


def main():
    automation = IntegratedAutomation()
    automation.run_batch(3)


if __name__ == "__main__":
    main()
