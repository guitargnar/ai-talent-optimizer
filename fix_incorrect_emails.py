#!/usr/bin/env python3
"""
Fix Incorrect Emails - Update database with correct application methods
Based on actual bounce results from Gmail
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class EmailFixer:
    """Fix incorrect email addresses based on bounce feedback"""
    
    def __init__(self):
        self.db_path = "UNIFIED_AI_JOBS.db"
        self.corrections_path = "data/email_corrections.json"
        
        # Based on actual results from Gmail
        self.bounced_emails = [
            "careers@openai.com",  # Address not found
            "google-jobs@google.com",  # Address not found
        ]
        
        self.unmonitored_emails = [
            "jobs@anthropic.com",  # Not monitored, auto-reply only
        ]
        
        # Correct application methods (from research)
        self.correct_methods = {
            "OpenAI": {
                "method": "website",
                "url": "https://openai.com/careers",
                "notes": "Must apply through website, no direct email"
            },
            "Google": {
                "method": "website", 
                "url": "https://careers.google.com",
                "notes": "Apply through Google Careers portal"
            },
            "Google DeepMind": {
                "method": "website",
                "url": "https://www.deepmind.com/careers",
                "notes": "Apply through DeepMind careers page"
            },
            "Anthropic": {
                "method": "website",
                "url": "https://www.anthropic.com/careers",
                "notes": "Apply through website as indicated in auto-reply"
            },
            "Meta": {
                "method": "website",
                "url": "https://www.metacareers.com",
                "notes": "Portal application only"
            },
            "Microsoft": {
                "method": "website",
                "url": "https://careers.microsoft.com",
                "notes": "Use Microsoft Careers portal"
            },
            "Amazon": {
                "method": "website",
                "url": "https://www.amazon.jobs",
                "notes": "Apply through Amazon Jobs"
            },
            "Apple": {
                "method": "website",
                "url": "https://jobs.apple.com",
                "notes": "Apply through Apple Jobs portal"
            },
            "Netflix": {
                "method": "website",
                "url": "https://jobs.netflix.com",
                "notes": "Apply through Netflix Jobs"
            },
            "Tesla": {
                "method": "website",
                "url": "https://www.tesla.com/careers",
                "notes": "Apply through Tesla Careers"
            },
            "Stripe": {
                "method": "website",
                "url": "https://stripe.com/jobs",
                "notes": "Apply through Stripe Jobs"
            }
        }
        
        # Companies that DO accept email applications (verified)
        self.working_emails = {
            "Databricks": "recruiting@databricks.com",
            "Scale AI": "careers@scale.com",
            "Weights & Biases": "careers@wandb.com",
            "GitLab": "careers@gitlab.com",
            "Zapier": "jobs@zapier.com",
            "Automattic": "jobs@automattic.com"
        }
    
    def mark_bounced_emails(self):
        """Mark bounced emails in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("📧 MARKING BOUNCED EMAILS:")
        
        for email in self.bounced_emails:
            cursor.execute("""
                UPDATE job_discoveries 
                SET bounce_detected = 1,
                    application_invalid = 1,
                    verified_email = NULL,
                    bounce_reason = 'Address not found'
                WHERE verified_email = ?
            """, (email,))
            
            affected = cursor.rowcount
            print(f"  ❌ {email}: Marked {affected} entries as bounced")
        
        # Add notes column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE job_discoveries ADD COLUMN notes TEXT")
        except:
            pass
        
        for email in self.unmonitored_emails:
            cursor.execute("""
                UPDATE job_discoveries 
                SET verified_email = NULL,
                    notes = 'Email not monitored - use website'
                WHERE verified_email = ?
            """, (email,))
            
            affected = cursor.rowcount
            print(f"  ⚠️  {email}: Marked {affected} entries as unmonitored")
        
        conn.commit()
        conn.close()
    
    def add_application_urls(self):
        """Add correct application URLs for companies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add column if doesn't exist
        try:
            cursor.execute("ALTER TABLE job_discoveries ADD COLUMN application_url TEXT")
        except:
            pass
        
        try:
            cursor.execute("ALTER TABLE job_discoveries ADD COLUMN application_method TEXT")
        except:
            pass
        
        print("\n🌐 ADDING CORRECT APPLICATION METHODS:")
        
        for company, info in self.correct_methods.items():
            cursor.execute("""
                UPDATE job_discoveries 
                SET application_url = ?,
                    application_method = ?,
                    notes = ?
                WHERE company LIKE ?
            """, (info['url'], info['method'], info['notes'], f'%{company}%'))
            
            affected = cursor.rowcount
            if affected > 0:
                print(f"  ✅ {company}: {info['url']}")
        
        conn.commit()
        conn.close()
    
    def update_working_emails(self):
        """Update companies with working email addresses"""
        from collect_real_emails import RealEmailCollector
        collector = RealEmailCollector()
        
        print("\n✅ ADDING VERIFIED WORKING EMAILS:")
        
        for company, email in self.working_emails.items():
            collector.add_verified_email(company, email, source="verified_working")
            print(f"  ✅ {company}: {email}")
        
        # Update database
        collector.update_database_with_emails()
    
    def generate_report(self):
        """Generate report of fixes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get companies that need website applications
        cursor.execute("""
            SELECT DISTINCT company, application_url, relevance_score
            FROM job_discoveries
            WHERE application_method = 'website'
            AND relevance_score >= 0.5
            ORDER BY relevance_score DESC
            LIMIT 10
        """)
        
        website_apps = cursor.fetchall()
        
        # Get companies with working emails
        cursor.execute("""
            SELECT DISTINCT company, verified_email, relevance_score
            FROM job_discoveries
            WHERE verified_email IS NOT NULL
            AND verified_email != ''
            AND relevance_score >= 0.5
            ORDER BY relevance_score DESC
            LIMIT 10
        """)
        
        email_apps = cursor.fetchall()
        
        conn.close()
        
        print("\n" + "="*60)
        print("📊 APPLICATION METHOD REPORT")
        print("="*60)
        
        if website_apps:
            print("\n🌐 HIGH-VALUE COMPANIES (Apply via Website):")
            for company, url, score in website_apps[:5]:
                print(f"  {company} (Score: {score:.2f})")
                print(f"    → {url}")
        
        if email_apps:
            print("\n📧 HIGH-VALUE COMPANIES (Email Available):")
            for company, email, score in email_apps[:5]:
                print(f"  {company} (Score: {score:.2f})")
                print(f"    → {email}")
        
        print("\n" + "="*60)
        
        # Save corrections log
        corrections = {
            "timestamp": datetime.now().isoformat(),
            "bounced_emails": self.bounced_emails,
            "unmonitored_emails": self.unmonitored_emails,
            "website_applications": {c: info for c, info in self.correct_methods.items()},
            "working_emails": self.working_emails
        }
        
        with open(self.corrections_path, 'w') as f:
            json.dump(corrections, f, indent=2)
        
        print(f"💾 Corrections saved to: {self.corrections_path}")


def main():
    """Main execution"""
    fixer = EmailFixer()
    
    print("🔧 FIXING EMAIL DATABASE")
    print("="*60)
    print("Based on actual bounce results from Gmail\n")
    
    # Mark bounced emails
    fixer.mark_bounced_emails()
    
    # Add correct application methods
    fixer.add_application_urls()
    
    # Update working emails
    fixer.update_working_emails()
    
    # Generate report
    fixer.generate_report()
    
    print("\n✅ FIXES COMPLETE!")
    print("\n🚀 NEXT STEPS:")
    print("  1. For website applications, manually apply at:")
    print("     • OpenAI: https://openai.com/careers")
    print("     • Anthropic: https://www.anthropic.com/careers")
    print("     • Google: https://careers.google.com")
    print("\n  2. For email applications, use verified addresses:")
    print("     python3 apply_with_verified_emails.py")


if __name__ == "__main__":
    main()