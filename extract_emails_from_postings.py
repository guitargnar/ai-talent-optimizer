#!/usr/bin/env python3
"""
Extract Emails from Job Postings - Find real contact emails in job descriptions
Helps manually collect verified email addresses from actual job postings
"""

import re
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class JobPostingEmailExtractor:
    """Extract real email addresses from job posting descriptions"""
    
    def __init__(self):
        self.db_path = "unified_platform.db"
        self.extracted_emails_path = "data/extracted_emails.json"
        self.job_board_patterns_path = "data/job_board_patterns.json"
        
        # Load existing data
        self.extracted_emails = self._load_json(self.extracted_emails_path, {})
        
        # Email extraction patterns
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Standard email
            r'(?:contact|email|apply|send|submit).*?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}).*?(?:resume|cv|application)',
        ]
        
        # Patterns to identify application instructions
        self.application_patterns = [
            r'(?:apply|submit|send).*?(?:to|at|via).*?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            r'(?:email|contact).*?(?:us|recruiter|hr).*?(?:at|to).*?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            r'(?:interested|questions).*?(?:contact|email).*?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        ]
        
        # URL patterns for application forms
        self.url_patterns = [
            r'(?:apply|application).*?(https?://[^\s]+)',
            r'(https?://[^\s]*(?:careers|jobs|apply|recruiting)[^\s]*)',
            r'(?:visit|go to).*?(https?://[^\s]+).*?(?:apply|submit)',
        ]
        
        # Known job board domains to filter out
        self.job_board_domains = [
            'indeed.com', 'linkedin.com', 'glassdoor.com', 'monster.com',
            'ziprecruiter.com', 'dice.com', 'careerbuilder.com', 'simplyhired.com',
            'angel.co', 'wellfound.com', 'hired.com', 'triplebyte.com'
        ]
    
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
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extract all email addresses from text"""
        emails = set()
        
        for pattern in self.email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    email = match[0] if match[0] else match[-1]
                else:
                    email = match
                
                # Clean and validate
                email = email.lower().strip()
                if self._is_valid_job_email(email):
                    emails.add(email)
        
        return list(emails)
    
    def _is_valid_job_email(self, email: str) -> bool:
        """Check if email is likely for job applications"""
        # Filter out common non-job emails
        invalid_patterns = [
            'noreply', 'donotreply', 'no-reply', 'do-not-reply',
            'unsubscribe', 'privacy', 'support', 'info@',
            'admin@', 'webmaster@', 'postmaster@', 'abuse@'
        ]
        
        email_lower = email.lower()
        
        # Check if it's from a job board (we want company emails)
        for domain in self.job_board_domains:
            if domain in email_lower:
                return False
        
        # Check for invalid patterns
        for pattern in invalid_patterns:
            if pattern in email_lower:
                return False
        
        # Prefer emails with job-related keywords
        good_patterns = [
            'career', 'job', 'recruit', 'talent', 'hiring',
            'hr', 'people', 'apply', 'employment', 'opportunity'
        ]
        
        # Give preference to emails with good patterns
        for pattern in good_patterns:
            if pattern in email_lower:
                return True
        
        # Accept other emails if they look valid
        return '@' in email and '.' in email.split('@')[1]
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract application URLs from text"""
        urls = set()
        
        for pattern in self.url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    url = match[0] if match[0] else match[-1]
                else:
                    url = match
                
                # Clean URL
                url = url.strip()
                
                # Filter out job board URLs
                is_job_board = any(domain in url for domain in self.job_board_domains)
                if not is_job_board:
                    urls.add(url)
        
        return list(urls)
    
    def scan_job_descriptions(self, limit: int = 50) -> Dict:
        """Scan job descriptions for contact information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get jobs without verified emails
        cursor.execute("""
            SELECT id, company, title, description, job_url
            FROM jobs
            WHERE description IS NOT NULL
            AND (verified_email IS NULL OR verified_email = '')
            ORDER BY relevance_score DESC
            LIMIT ?
        """, (limit,))
        
        jobs = cursor.fetchall()
        conn.close()
        
        results = {
            'total_scanned': len(jobs),
            'emails_found': {},
            'urls_found': {},
            'companies_with_contact': []
        }
        
        for job_id, company, title, description, job_url in jobs:
            if not description:
                continue
            
            # Combine description and job_url for scanning
            full_text = f"{description} {job_url or ''}"
            
            # Extract emails
            emails = self.extract_emails_from_text(full_text)
            if emails:
                if company not in results['emails_found']:
                    results['emails_found'][company] = []
                results['emails_found'][company].extend(emails)
                results['companies_with_contact'].append(company)
            
            # Extract URLs
            urls = self.extract_urls_from_text(full_text)
            if urls:
                if company not in results['urls_found']:
                    results['urls_found'][company] = []
                results['urls_found'][company].extend(urls)
        
        # Remove duplicates
        for company in results['emails_found']:
            results['emails_found'][company] = list(set(results['emails_found'][company]))
        
        for company in results['urls_found']:
            results['urls_found'][company] = list(set(results['urls_found'][company]))
        
        return results
    
    def save_extracted_emails(self, emails_dict: Dict):
        """Save extracted emails to database"""
        from collect_real_emails import RealEmailCollector
        collector = RealEmailCollector()
        
        saved_count = 0
        for company, emails in emails_dict.items():
            for email in emails:
                # Add to verified emails
                if collector.add_verified_email(company, email, source="job_posting"):
                    saved_count += 1
                    print(f"  ✅ Saved: {company} -> {email}")
        
        return saved_count
    
    def interactive_review(self, results: Dict):
        """Interactively review and save extracted emails"""
        print(f"\n📧 EXTRACTED CONTACT INFORMATION:")
        print(f"  Scanned: {results['total_scanned']} job descriptions")
        print(f"  Companies with emails: {len(results['emails_found'])}")
        print(f"  Companies with URLs: {len(results['urls_found'])}")
        
        if results['emails_found']:
            print(f"\n✅ EMAILS FOUND:")
            for company, emails in list(results['emails_found'].items())[:10]:
                print(f"\n  {company}:")
                for email in emails:
                    print(f"    • {email}")
                    save = input("    Save this email? (y/n/skip all): ")
                    
                    if save.lower() == 'y':
                        from collect_real_emails import RealEmailCollector
                        collector = RealEmailCollector()
                        collector.add_verified_email(company, email, source="job_posting")
                        print("    ✅ Saved!")
                    elif save.lower() == 'skip all':
                        return
        
        if results['urls_found']:
            print(f"\n🌐 APPLICATION URLS FOUND:")
            for company, urls in list(results['urls_found'].items())[:5]:
                print(f"\n  {company}:")
                for url in urls[:2]:  # Show max 2 URLs per company
                    print(f"    • {url}")
    
    def generate_manual_research_list(self) -> str:
        """Generate list of companies needing manual email research"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get high-value companies without emails
        cursor.execute("""
            SELECT DISTINCT company, MAX(relevance_score) as score
            FROM jobs
            WHERE applied = 0
            AND relevance_score >= 0.5
            AND (verified_email IS NULL OR verified_email = '')
            GROUP BY company
            ORDER BY score DESC
            LIMIT 30
        """)
        
        companies = cursor.fetchall()
        conn.close()
        
        research_data = {
            'generated': datetime.now().isoformat(),
            'companies': [],
            'research_instructions': [
                "For each company:",
                "1. Google: '[company] careers contact email'",
                "2. Visit: [company].com/careers or /jobs",
                "3. LinkedIn: Search for '[company] recruiter' or 'talent acquisition'",
                "4. Check recent job postings on Indeed/LinkedIn for contact info",
                "5. Use Hunter.io or RocketReach for email discovery"
            ]
        }
        
        for company, score in companies:
            research_data['companies'].append({
                'name': company,
                'relevance_score': round(score, 2),
                'search_queries': [
                    f"{company} careers email",
                    f"{company} recruiting contact",
                    f"{company} jobs apply email",
                    f"site:{company.lower().replace(' ', '')}.com careers"
                ]
            })
        
        # Save to file
        output_path = "data/manual_email_research.json"
        self._save_json(output_path, research_data)
        
        print(f"\n📋 MANUAL RESEARCH LIST GENERATED:")
        print(f"  File: {output_path}")
        print(f"  Companies: {len(companies)}")
        print(f"\n  Top 10 to research:")
        for company, score in companies[:10]:
            print(f"    • {company} (Score: {score:.2f})")
        
        return output_path


def main():
    """Main execution"""
    extractor = JobPostingEmailExtractor()
    
    print("📧 Email Extractor from Job Postings")
    print("\nOptions:")
    print("1. Scan job descriptions for emails")
    print("2. Generate manual research list")
    print("3. Interactive email review")
    print("4. Auto-save all found emails")
    
    choice = input("\nSelect option (1-4): ")
    
    if choice == '1':
        print("\n🔍 Scanning job descriptions...")
        results = extractor.scan_job_descriptions(limit=100)
        
        if results['emails_found']:
            print(f"\n✅ Found emails for {len(results['emails_found'])} companies!")
            extractor.interactive_review(results)
        else:
            print("\n❌ No emails found in job descriptions")
            print("  Most companies don't include email in postings")
            print("  Try option 2 for manual research list")
    
    elif choice == '2':
        path = extractor.generate_manual_research_list()
        print(f"\n💡 Next steps:")
        print(f"  1. Open {path}")
        print(f"  2. Research each company using provided queries")
        print(f"  3. Add found emails: python3 collect_real_emails.py")
    
    elif choice == '3':
        print("\n🔍 Scanning for review...")
        results = extractor.scan_job_descriptions(limit=50)
        extractor.interactive_review(results)
    
    elif choice == '4':
        print("\n🔍 Auto-scanning and saving...")
        results = extractor.scan_job_descriptions(limit=100)
        
        if results['emails_found']:
            saved = extractor.save_extracted_emails(results['emails_found'])
            print(f"\n✅ Saved {saved} email addresses")
        else:
            print("\n❌ No emails found to save")


if __name__ == "__main__":
    main()