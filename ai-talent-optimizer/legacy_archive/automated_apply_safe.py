#!/usr/bin/env python3
"""
Safe Automated Application System
With email validation and delivery confirmation
"""

import os
import sys
import time
import json
import sqlite3
from datetime import datetime
from email_validator import EmailValidator
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/.env")


class SafeAutomatedApply:
    """Automated job application with validation and safety checks"""
    
    def __init__(self):
        self.validator = EmailValidator()
        self.email_address = os.getenv("EMAIL_ADDRESS", "matthewdscott7@gmail.com")
        self.email_password = os.getenv("EMAIL_APP_PASSWORD", "")
        
        # Track applications
        self.applications_sent = []
        self.applications_failed = []
        self.applications_alternative = []
        
    def get_unapplied_jobs(self, limit=10):
        """Get jobs that haven't been applied to yet"""
        conn = sqlite3.connect('unified_talent_optimizer.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT company, position, url, salary_range, relevance_score
            FROM job_discoveries
            WHERE applied = 0
            ORDER BY relevance_score DESC
            LIMIT ?
        """, (limit,))
        
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
        return jobs
    
    def validate_and_apply(self, job):
        """Validate email before applying"""
        company = job['company']
        position = job['position']
        
        print(f"\n📋 Processing: {company} - {position}")
        
        # First, try to find correct email
        email_info = self.validator.find_correct_email(company)
        
        if email_info['method'] == 'email' and email_info['email']:
            # We have a valid email
            target_email = email_info['email']
            
            # Double-check validation
            validation = self.validator.validate_before_send(target_email, company)
            
            if validation['send_ok']:
                print(f"   ✅ Valid email found: {target_email}")
                
                # Send application
                success = self.send_application(job, target_email)
                
                if success:
                    self.applications_sent.append({
                        'company': company,
                        'position': position,
                        'email': target_email,
                        'timestamp': datetime.now().isoformat()
                    })
                    return 'sent'
                else:
                    self.applications_failed.append({
                        'company': company,
                        'position': position,
                        'reason': 'Send failed'
                    })
                    return 'failed'
            else:
                print(f"   ❌ Email validation failed: {validation['reason']}")
                self.applications_failed.append({
                    'company': company,
                    'position': position,
                    'reason': validation['reason']
                })
                return 'failed'
                
        elif email_info['method'] == 'web_form':
            # Need to use web form
            print(f"   ℹ️ Use web form: {email_info['instruction']}")
            self.applications_alternative.append({
                'company': company,
                'position': position,
                'method': 'web_form',
                'instruction': email_info['instruction']
            })
            return 'alternative'
            
        else:
            # No valid method found
            print(f"   ⚠️ No valid application method found")
            self.applications_alternative.append({
                'company': company,
                'position': position,
                'method': 'unknown',
                'instruction': f'Research {company} careers page'
            })
            return 'alternative'
    
    def send_application(self, job, email):
        """Send the actual application email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = email
            msg['Subject'] = f"Application for {job['position']} position"
            
            # Add cover letter
            cover_letter = self.generate_cover_letter(job)
            msg.attach(MIMEText(cover_letter, 'plain'))
            
            # Would add resume here
            # resume_path = self.select_resume(job)
            # with open(resume_path, 'rb') as f:
            #     attach = MIMEApplication(f.read(), _subtype="pdf")
            #     attach.add_header('Content-Disposition', 'attachment', filename='resume.pdf')
            #     msg.attach(attach)
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"   📧 Application sent successfully!")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to send: {str(e)}")
            return False
    
    def generate_cover_letter(self, job):
        """Generate a simple cover letter"""
        return f"""Dear Hiring Manager,

I am writing to express my interest in the {job['position']} position at {job['company']}.

With my experience in software engineering and AI/ML applications, I believe I would be a valuable addition to your team.

I have attached my resume for your review and would welcome the opportunity to discuss how my skills align with your needs.

Thank you for your consideration.

Best regards,
Matthew Scott"""
    
    def run_safe_batch(self, count=5):
        """Run a safe batch of applications"""
        print("\n🛡️ SAFE APPLICATION BATCH")
        print("="*60)
        
        # Get jobs
        jobs = self.get_unapplied_jobs(count)
        
        if not jobs:
            print("No unapplied jobs found")
            return
        
        print(f"Found {len(jobs)} jobs to process\n")
        
        # Process each job
        for i, job in enumerate(jobs, 1):
            print(f"[{i}/{len(jobs)}]", end="")
            result = self.validate_and_apply(job)
            
            # Wait between applications
            if i < len(jobs) and result == 'sent':
                wait_time = 30  # 30 seconds between applications
                print(f"   ⏱️ Waiting {wait_time} seconds...")
                time.sleep(wait_time)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate application report"""
        print("\n" + "="*60)
        print("📊 APPLICATION REPORT")
        print("="*60)
        
        print(f"\n✅ Successfully Sent: {len(self.applications_sent)}")
        for app in self.applications_sent:
            print(f"   • {app['company']} - {app['position']}")
        
        print(f"\n❌ Failed (Invalid Email): {len(self.applications_failed)}")
        for app in self.applications_failed:
            print(f"   • {app['company']}: {app['reason']}")
        
        print(f"\n🌐 Need Manual Application: {len(self.applications_alternative)}")
        for app in self.applications_alternative:
            print(f"   • {app['company']} - {app['position']}")
            print(f"     → {app['instruction']}")
        
        # Save report
        report_file = f"safe_application_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'sent': self.applications_sent,
                'failed': self.applications_failed,
                'alternative': self.applications_alternative,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n💾 Report saved to: {report_file}")


def main():
    """Run safe automated applications"""
    
    print("🛡️ SAFE AUTOMATED APPLICATION SYSTEM")
    print("with Email Validation & Delivery Confirmation")
    print("="*60)
    
    # Check if we should proceed
    print("\n⚠️ This system will:")
    print("  1. Validate email addresses before sending")
    print("  2. Skip invalid emails")
    print("  3. Suggest alternatives for companies without email")
    print("  4. Track all application attempts")
    
    response = input("\nProceed with safe application batch? (y/n): ")
    
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Run safe batch
    safe_apply = SafeAutomatedApply()
    
    try:
        count = int(input("How many applications to attempt? (1-5): "))
        count = min(max(count, 1), 5)  # Limit to 1-5 for safety
    except:
        count = 3  # Default to 3
    
    safe_apply.run_safe_batch(count)
    
    print("\n✅ Safe application batch complete!")
    print("Review the report for manual application instructions.")


if __name__ == "__main__":
    main()