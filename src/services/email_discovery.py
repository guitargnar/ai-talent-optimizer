"""
Email Discovery Service
Automatically finds and validates company email addresses for job applications
"""

import re
import logging
from typing import Optional, List, Dict
from urllib.parse import urlparse
import sqlite3
import json
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class EmailDiscoveryService:
    """Service to discover and validate email addresses for companies"""
    
    def __init__(self, db_path: str = "unified_platform.db"):
        self.db_path = db_path
        
        # Load company data from JSON
        self.company_data = self._load_company_data()
        
        self.common_patterns = [
            "careers@{domain}",
            "jobs@{domain}",
            "hr@{domain}",
            "recruiting@{domain}",
            "talent@{domain}",
            "hiring@{domain}",
            "recruitment@{domain}",
            "apply@{domain}",
            "people@{domain}",
            "team@{domain}",
            "info@{domain}",
            "contact@{domain}"
        ]
    
    def _load_company_data(self) -> Dict:
        """Load company domains and verified emails from JSON"""
        json_path = Path(__file__).parent.parent.parent / 'data' / 'company_emails.json'
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load company data: {e}")
            return {'company_domains': {}, 'verified_emails': {}}
    
    def get_company_domain(self, company_name: str) -> Optional[str]:
        """Get domain for a company from our mapping"""
        # Direct match
        if company_name in self.company_data['company_domains']:
            return self.company_data['company_domains'][company_name]
        
        # Case-insensitive match
        for company, domain in self.company_data['company_domains'].items():
            if company.lower() == company_name.lower():
                return domain
        
        return None
    
    def get_verified_email(self, company_name: str) -> Optional[str]:
        """Get verified email for a company"""
        # Direct match
        if company_name in self.company_data['verified_emails']:
            return self.company_data['verified_emails'][company_name]
        
        # Case-insensitive match
        for company, email in self.company_data['verified_emails'].items():
            if company.lower() == company_name.lower():
                return email
        
        return None
        
    def extract_domain_from_url(self, url: str) -> Optional[str]:
        """Extract domain from company website or job URL"""
        try:
            if not url:
                return None
                
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
                
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
                
            # Skip job boards (expanded list)
            job_boards = ['greenhouse.io', 'lever.co', 'workday.com', 'linkedin.com', 
                         'indeed.com', 'angel.co', 'wellfound.com', 'ziprecruiter.com',
                         'adzuna.com', 'glassdoor.com', 'monster.com', 'careerbuilder.com',
                         'dice.com', 'simplyhired.com', 'remotive.com', 'remoteok.com',
                         'weworkremotely.com']
            if any(board in domain for board in job_boards):
                logger.debug(f"Skipping job board domain: {domain}")
                return None
                
            return domain
        except Exception as e:
            logger.error(f"Error extracting domain from {url}: {e}")
            return None
    
    def generate_email_candidates(self, company_name: str, domain: str = None) -> List[str]:
        """Generate potential email addresses for a company"""
        candidates = []
        
        if domain:
            # Use domain-based patterns
            for pattern in self.common_patterns:
                candidates.append(pattern.format(domain=domain))
        else:
            # Try to guess domain from company name
            cleaned_name = company_name.lower()
            # Remove common suffixes
            for suffix in [' inc', ' llc', ' corp', ' ltd', ' limited', ' co', ' company']:
                cleaned_name = cleaned_name.replace(suffix, '')
            
            # Create potential domains
            potential_domains = [
                f"{cleaned_name.replace(' ', '')}.com",
                f"{cleaned_name.replace(' ', '-')}.com",
                f"{cleaned_name.split()[0]}.com" if ' ' in cleaned_name else f"{cleaned_name}.com"
            ]
            
            for domain in potential_domains:
                for pattern in self.common_patterns[:6]:  # Use top patterns only
                    candidates.append(pattern.format(domain=domain))
                    
        return candidates
    
    def verify_email_syntax(self, email: str) -> bool:
        """Basic email syntax validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def discover_email_for_job(self, job_id: int) -> Optional[str]:
        """Discover email for a specific job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get job details
            cursor.execute("""
                SELECT company, url, url as company_website
                FROM jobs
                WHERE id = ?
            """, (job_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
                
            company, job_url, company_website = result
            
            # Try to extract domain
            domain = None
            if company_website:
                domain = self.extract_domain_from_url(company_website)
            if not domain and job_url:
                domain = self.extract_domain_from_url(job_url)
                
            # Generate candidates
            candidates = self.generate_email_candidates(company, domain)
            
            # Return the most likely candidate
            if candidates:
                # Prefer careers@ or jobs@ if available
                for preferred in ['careers@', 'jobs@', 'hr@']:
                    for candidate in candidates:
                        if candidate.startswith(preferred):
                            return candidate
                return candidates[0]
                
        except Exception as e:
            logger.error(f"Error discovering email for job {job_id}: {e}")
        finally:
            conn.close()
            
        return None
    
    def bulk_discover_emails(self, limit: int = 100) -> Dict[int, str]:
        """Discover emails for multiple jobs without emails"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        discovered = {}
        
        try:
            # Find jobs without emails
            cursor.execute("""
                SELECT id, company, url, url as company_website
                FROM jobs
                WHERE (company_email IS NULL OR company_email = 'N/A' OR company_email = '')
                AND applied = 0
                LIMIT ?
            """, (limit,))
            
            jobs = cursor.fetchall()
            logger.info(f"Found {len(jobs)} jobs needing email discovery")
            
            for job_id, company, job_url, company_website in jobs:
                # First check for verified email
                verified_email = self.get_verified_email(company)
                if verified_email:
                    discovered[job_id] = verified_email
                    cursor.execute("""
                        UPDATE jobs
                        SET company_email = ?,
                            discovered_date = ?
                        WHERE id = ?
                    """, (verified_email, datetime.now().isoformat(), job_id))
                    logger.info(f"Using verified email for {company_name}: {verified_email}")
                    continue
                
                # Try to get domain from our mapping
                domain = self.get_company_domain(company)
                
                # If no domain from mapping, try to extract from URL (but skip job boards)
                if not domain and company_website:
                    extracted = self.extract_domain_from_url(company_website)
                    if extracted and 'adzuna' not in extracted:  # Extra check
                        domain = extracted
                
                # Skip if we only have job board URLs
                if not domain and job_url and 'adzuna.com' in job_url:
                    logger.debug(f"Skipping {company_name} - only has Adzuna URL")
                    continue
                    
                # Generate candidates if we have a domain
                if domain:
                    candidates = self.generate_email_candidates(company, domain)
                else:
                    # Try generating from company name as last resort
                    candidates = self.generate_email_candidates(company, None)
                
                if candidates:
                    email = candidates[0]  # Use most likely candidate
                    discovered[job_id] = email
                    
                    # Update database
                    cursor.execute("""
                        UPDATE jobs
                        SET company_email = ?,
                            discovered_date = ?
                        WHERE id = ?
                    """, (email, datetime.now().isoformat(), job_id))
                    
                    logger.info(f"Discovered email for {company_name}: {email}")
                    
            conn.commit()
            logger.info(f"Successfully discovered {len(discovered)} email addresses")
            
        except Exception as e:
            logger.error(f"Error in bulk email discovery: {e}")
            conn.rollback()
        finally:
            conn.close()
            
        return discovered
    
    def add_company_website(self, job_id: int, website: str) -> bool:
        """Add company website to improve email discovery"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE jobs
                SET company_website = ?,
                    updated_at = ?
                WHERE id = ?
            """, (website, datetime.now().isoformat(), job_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error adding company website: {e}")
            return False
        finally:
            conn.close()

def fix_missing_emails():
    """Quick function to fix missing emails in the database"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    logging.basicConfig(level=logging.INFO)
    
    service = EmailDiscoveryService()
    discovered = service.bulk_discover_emails(limit=20)
    
    print(f"\n✅ Email Discovery Complete!")
    print(f"Discovered {len(discovered)} email addresses")
    
    if discovered:
        print("\nSample discoveries:")
        for job_id, email in list(discovered.items())[:5]:
            print(f"  Job #{job_id}: {email}")
    
    return discovered

if __name__ == "__main__":
    fix_missing_emails()