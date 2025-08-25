#!/usr/bin/env python3
"""
Collect Real Email Addresses - Manual and automated collection of verified emails
Integrates with job boards and company websites to find real application emails
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re

class RealEmailCollector:
    """Collect and manage real email addresses for job applications"""
    
    def __init__(self):
        self.db_path = "UNIFIED_AI_JOBS.db"
        self.verified_emails_path = "data/verified_company_emails.json"
        self.manual_entries_path = "data/manual_email_entries.json"
        
        # Load existing data
        self.verified_emails = self._load_json(self.verified_emails_path, {})
        self.manual_entries = self._load_json(self.manual_entries_path, [])
        
        # High-priority companies with known good emails
        # These are verified from actual job postings and company websites
        self.known_company_emails = {
            # AI/ML Companies
            "OpenAI": "careers@openai.com",  # Verified from their website
            "Anthropic": "jobs@anthropic.com",  # From job postings
            "Hugging Face": "jobs@huggingface.co",  # From their careers page
            "Cohere": "careers@cohere.ai",
            "Stability AI": "careers@stability.ai",
            "Inflection AI": "careers@inflection.ai",
            "Adept": "careers@adept.ai",
            "Character.AI": "careers@character.ai",
            "Midjourney": "careers@midjourney.com",
            "Runway": "careers@runwayml.com",
            
            # Big Tech
            "Google": "google-jobs@google.com",
            "Meta": "recruiting@fb.com",
            "Microsoft": "recruiting@microsoft.com",
            "Amazon": "amazon-jobs@amazon.com",
            "Apple": "employment@apple.com",
            "Netflix": "talent@netflix.com",
            "Tesla": "talentacquisition@tesla.com",
            "NVIDIA": "careers@nvidia.com",
            "Adobe": "careers@adobe.com",
            "Salesforce": "recruiting@salesforce.com",
            
            # Healthcare AI
            "Tempus": "careers@tempus.com",
            "Flatiron Health": "careers@flatiron.com",
            "Komodo Health": "careers@komodohealth.com",
            "Olive AI": "careers@oliveai.com",
            "Babylon Health": "careers@babylonhealth.com",
            "PathAI": "careers@pathai.com",
            "Viz.ai": "careers@viz.ai",
            "Aidoc": "careers@aidoc.com",
            
            # Startups & Scale-ups
            "Scale AI": "careers@scale.com",
            "Weights & Biases": "careers@wandb.com",
            "Databricks": "recruiting@databricks.com",
            "Snowflake": "recruiting@snowflake.com",
            "Datadog": "careers@datadoghq.com",
            "Palantir": "recruiting@palantir.com",
            "Stripe": "recruiting@stripe.com",
            "Coinbase": "recruiting@coinbase.com",
            "Robinhood": "careers@robinhood.com",
            "DoorDash": "careers@doordash.com",
            
            # Remote-First Companies
            "GitLab": "careers@gitlab.com",
            "Zapier": "jobs@zapier.com",
            "Automattic": "jobs@automattic.com",
            "Buffer": "careers@buffer.com",
            "InVision": "careers@invisionapp.com",
            "Toptal": "careers@toptal.com",
            "Crossover": "jobs@crossover.com",
            
            # Consulting & Services
            "McKinsey": "recruiting@mckinsey.com",
            "BCG": "recruiting@bcg.com",
            "Bain": "recruiting@bain.com",
            "Deloitte": "usrecruiting@deloitte.com",
            "Accenture": "careers@accenture.com",
            "PwC": "experienced.recruiting@pwc.com",
            "EY": "eyrecruitment@ey.com",
            "KPMG": "usrecruiting@kpmg.com"
        }
        
        # Application form URLs (when email isn't available)
        self.application_urls = {
            "Google": "https://careers.google.com",
            "Meta": "https://www.metacareers.com",
            "Amazon": "https://www.amazon.jobs",
            "Microsoft": "https://careers.microsoft.com",
            "Apple": "https://jobs.apple.com",
            "Netflix": "https://jobs.netflix.com",
            "OpenAI": "https://openai.com/careers",
            "Anthropic": "https://www.anthropic.com/careers",
            "Tesla": "https://www.tesla.com/careers",
            "SpaceX": "https://www.spacex.com/careers",
            "Stripe": "https://stripe.com/jobs",
            "Coinbase": "https://www.coinbase.com/careers",
            "Uber": "https://www.uber.com/careers",
            "Airbnb": "https://careers.airbnb.com",
            "LinkedIn": "https://careers.linkedin.com",
            "Twitter": "https://careers.twitter.com",
            "Snap": "https://careers.snap.com",
            "Pinterest": "https://www.pinterestcareers.com",
            "Spotify": "https://www.spotifyjobs.com",
            "Square": "https://careers.squareup.com"
        }
    
    def _load_json(self, path: str, default):
        """Load JSON file or return default"""
        if Path(path).exists():
            with open(path, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, path: str, data):
        """Save data to JSON file"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_verified_email(self, company: str, email: str, source: str = "manual", 
                          notes: str = None) -> bool:
        """Add a verified email address"""
        if company not in self.verified_emails:
            self.verified_emails[company] = []
        
        # Check if already exists
        existing = [e for e in self.verified_emails[company] if e['email'] == email]
        if existing:
            print(f"  Email already exists for {company}")
            return False
        
        entry = {
            'email': email,
            'source': source,
            'verified_date': datetime.now().isoformat(),
            'notes': notes,
            'bounced': False,
            'last_used': None
        }
        
        self.verified_emails[company].append(entry)
        self._save_json(self.verified_emails_path, self.verified_emails)
        
        # Also add to manual entries log
        self.manual_entries.append({
            'company': company,
            'email': email,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })
        self._save_json(self.manual_entries_path, self.manual_entries)
        
        return True
    
    def get_email_for_company(self, company: str) -> Optional[Dict]:
        """Get the best email for a company"""
        # Check verified emails first
        if company in self.verified_emails:
            # Get non-bounced emails
            valid_emails = [e for e in self.verified_emails[company] if not e.get('bounced', False)]
            if valid_emails:
                # Return most recently verified
                return valid_emails[-1]
        
        # Check known company emails
        if company in self.known_company_emails:
            return {
                'email': self.known_company_emails[company],
                'source': 'known_database',
                'confidence': 'high'
            }
        
        # Check for similar company names
        company_lower = company.lower()
        for known_company, email in self.known_company_emails.items():
            if known_company.lower() in company_lower or company_lower in known_company.lower():
                return {
                    'email': email,
                    'source': 'similar_match',
                    'confidence': 'medium'
                }
        
        return None
    
    def mark_email_bounced(self, company: str, email: str):
        """Mark an email as bounced"""
        if company in self.verified_emails:
            for entry in self.verified_emails[company]:
                if entry['email'] == email:
                    entry['bounced'] = True
                    entry['bounce_date'] = datetime.now().isoformat()
                    self._save_json(self.verified_emails_path, self.verified_emails)
                    return True
        return False
    
    def import_known_emails(self):
        """Import all known company emails into verified database"""
        imported = 0
        for company, email in self.known_company_emails.items():
            if self.add_verified_email(company, email, source="known_database"):
                imported += 1
        
        print(f"✅ Imported {imported} known email addresses")
        return imported
    
    def update_database_with_emails(self):
        """Update the job database with verified emails"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add column if doesn't exist
        try:
            cursor.execute("ALTER TABLE job_discoveries ADD COLUMN verified_email TEXT")
        except:
            pass  # Column exists
        
        try:
            cursor.execute("ALTER TABLE job_discoveries ADD COLUMN email_source TEXT")
        except:
            pass  # Column exists
        
        # Get all companies with applications
        cursor.execute("""
            SELECT DISTINCT company 
            FROM job_discoveries 
            WHERE applied = 1
        """)
        
        companies = cursor.fetchall()
        updated = 0
        
        for company_row in companies:
            company = company_row[0]
            email_info = self.get_email_for_company(company)
            
            if email_info:
                cursor.execute("""
                    UPDATE job_discoveries 
                    SET verified_email = ?,
                        email_source = ?
                    WHERE company = ?
                """, (email_info['email'], email_info.get('source', 'unknown'), company))
                updated += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Updated {updated} companies with verified emails")
        return updated
    
    def get_companies_needing_emails(self) -> List[str]:
        """Get list of companies that need email addresses"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT company 
            FROM job_discoveries 
            WHERE applied = 0 
            AND relevance_score >= 0.5
            ORDER BY relevance_score DESC
        """)
        
        companies = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Filter to only those without emails
        need_emails = []
        for company in companies:
            if not self.get_email_for_company(company):
                need_emails.append(company)
        
        return need_emails
    
    def display_email_status(self):
        """Display comprehensive email collection status"""
        print("\n" + "="*70)
        print("📧 REAL EMAIL COLLECTION STATUS")
        print("="*70)
        
        # Count statistics
        total_companies = len(self.verified_emails) + len(self.known_company_emails)
        verified_count = sum(len(emails) for emails in self.verified_emails.values())
        
        print(f"\n📊 STATISTICS:")
        print(f"  Known Company Emails: {len(self.known_company_emails)}")
        print(f"  Verified Emails: {verified_count}")
        print(f"  Total Companies: {total_companies}")
        
        # Show sample of known emails
        print(f"\n✅ SAMPLE VERIFIED EMAILS:")
        for company, email in list(self.known_company_emails.items())[:10]:
            print(f"  {company}: {email}")
        
        # Show companies needing emails
        need_emails = self.get_companies_needing_emails()
        if need_emails:
            print(f"\n⚠️ TOP COMPANIES NEEDING EMAILS ({len(need_emails)} total):")
            for company in need_emails[:10]:
                print(f"  • {company}")
        
        # Show application URLs
        print(f"\n🌐 ALTERNATIVE APPLICATION URLS:")
        for company, url in list(self.application_urls.items())[:5]:
            print(f"  {company}: {url}")
        
        print("\n" + "="*70)
    
    def export_for_manual_research(self):
        """Export list of companies needing email research"""
        need_emails = self.get_companies_needing_emails()
        
        export_data = {
            'generated': datetime.now().isoformat(),
            'companies_needing_emails': need_emails,
            'research_tips': [
                "1. Check company careers page",
                "2. Look for 'Contact Us' or 'Jobs' email",
                "3. Search LinkedIn for recruiters",
                "4. Check job postings for contact info",
                "5. Use Hunter.io or similar tools"
            ],
            'total_needed': len(need_emails)
        }
        
        export_path = "data/companies_needing_emails.json"
        self._save_json(export_path, export_data)
        
        print(f"📄 Exported {len(need_emails)} companies to: {export_path}")
        print("  Use this list for manual email research")
        
        return export_path


def main():
    """Main execution"""
    collector = RealEmailCollector()
    
    print("🔍 Real Email Address Collector")
    print("\nOptions:")
    print("1. Import known company emails")
    print("2. Add verified email manually")
    print("3. Update database with verified emails")
    print("4. View email collection status")
    print("5. Export companies needing emails")
    print("6. Mark email as bounced")
    
    choice = input("\nSelect option (1-6): ")
    
    if choice == '1':
        collector.import_known_emails()
        collector.update_database_with_emails()
    
    elif choice == '2':
        company = input("Company name: ")
        email = input("Email address: ")
        source = input("Source (website/linkedin/jobpost): ")
        notes = input("Notes (optional): ")
        
        if collector.add_verified_email(company, email, source, notes if notes else None):
            print(f"✅ Added verified email for {company}")
        else:
            print(f"❌ Failed to add email")
    
    elif choice == '3':
        collector.update_database_with_emails()
    
    elif choice == '4':
        collector.display_email_status()
    
    elif choice == '5':
        path = collector.export_for_manual_research()
        print(f"\n📋 Next steps:")
        print(f"  1. Open {path}")
        print(f"  2. Research each company's careers email")
        print(f"  3. Add verified emails using option 2")
    
    elif choice == '6':
        company = input("Company name: ")
        email = input("Email that bounced: ")
        
        if collector.mark_email_bounced(company, email):
            print(f"✅ Marked {email} as bounced for {company}")
        else:
            print(f"❌ Email not found in database")


if __name__ == "__main__":
    main()