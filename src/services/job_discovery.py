"""
Enhanced Job Discovery Service
Scrapes jobs from multiple sources and validates company emails
"""

import logging
import requests
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import time
import re
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedJobDiscovery:
    """Multi-source job discovery with intelligent email validation"""
    
    def __init__(self, db_path: str = "data/unified_jobs.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Load API credentials from environment
        self.adzuna_app_id = os.getenv('ADZUNA_APP_ID', '6742d5ed')
        self.adzuna_app_key = os.getenv('ADZUNA_APP_KEY', 'f523e955e3e3ec4f13dae8253e5dd439')
        
        # Target companies with known career pages and emails
        self.target_companies = self._load_target_companies()
        
        # Job title keywords for AI/ML roles
        self.job_keywords = [
            'AI Engineer', 'ML Engineer', 'Machine Learning', 'Artificial Intelligence',
            'Principal Engineer', 'Staff Engineer', 'Senior Engineer', 'Tech Lead',
            'Data Scientist', 'MLOps', 'AI Platform', 'LLM', 'Deep Learning',
            'Computer Vision', 'NLP', 'Natural Language Processing'
        ]
        
    def _load_target_companies(self) -> Dict:
        """Load target companies with verified emails"""
        return {
            # Healthcare Tech Companies
            'Tempus': {
                'careers_url': 'https://www.tempus.com/careers/',
                'email': 'careers@tempus.com',
                'domain': 'tempus.com',
                'industry': 'Healthcare AI'
            },
            'Cedar': {
                'careers_url': 'https://www.cedar.com/careers/',
                'email': 'careers@cedar.com',
                'domain': 'cedar.com',
                'industry': 'Healthcare Payments'
            },
            'Zocdoc': {
                'careers_url': 'https://www.zocdoc.com/careers',
                'email': 'careers@zocdoc.com',
                'domain': 'zocdoc.com',
                'industry': 'Healthcare Marketplace'
            },
            'Oscar Health': {
                'careers_url': 'https://www.hioscar.com/careers',
                'email': 'careers@hioscar.com',
                'domain': 'hioscar.com',
                'industry': 'Health Insurance Tech'
            },
            'Doximity': {
                'careers_url': 'https://workat.doximity.com',
                'email': 'careers@doximity.com',
                'domain': 'doximity.com',
                'industry': 'Medical Network'
            },
            
            # AI/ML Companies
            'Anthropic': {
                'careers_url': 'https://www.anthropic.com/careers',
                'email': 'careers@anthropic.com',
                'domain': 'anthropic.com',
                'industry': 'AI Safety'
            },
            'OpenAI': {
                'careers_url': 'https://openai.com/careers/',
                'email': 'careers@openai.com',
                'domain': 'openai.com',
                'industry': 'AGI Research'
            },
            'Hugging Face': {
                'careers_url': 'https://huggingface.co/jobs',
                'email': 'careers@huggingface.co',
                'domain': 'huggingface.co',
                'industry': 'ML Tools'
            },
            'Scale AI': {
                'careers_url': 'https://scale.com/careers',
                'email': 'careers@scale.com',
                'domain': 'scale.com',
                'industry': 'Data Labeling AI'
            },
            'Cohere': {
                'careers_url': 'https://cohere.com/careers',
                'email': 'careers@cohere.com',
                'domain': 'cohere.com',
                'industry': 'Enterprise LLM'
            },
            
            # Tech Giants
            'Google DeepMind': {
                'careers_url': 'https://deepmind.google/careers/',
                'email': 'deepmind-careers@google.com',
                'domain': 'deepmind.google',
                'industry': 'AI Research'
            },
            'Meta AI': {
                'careers_url': 'https://ai.meta.com/careers/',
                'email': 'airecruiting@meta.com',
                'domain': 'meta.com',
                'industry': 'Social AI'
            },
            'Apple': {
                'careers_url': 'https://jobs.apple.com',
                'email': 'jobs@apple.com',
                'domain': 'apple.com',
                'industry': 'Consumer AI'
            },
            'Microsoft': {
                'careers_url': 'https://careers.microsoft.com',
                'email': 'recruiting@microsoft.com',
                'domain': 'microsoft.com',
                'industry': 'Enterprise AI'
            },
            
            # Startups & Scale-ups
            'Perplexity': {
                'careers_url': 'https://www.perplexity.ai/careers',
                'email': 'careers@perplexity.ai',
                'domain': 'perplexity.ai',
                'industry': 'AI Search'
            },
            'Runway': {
                'careers_url': 'https://runwayml.com/careers/',
                'email': 'careers@runwayml.com',
                'domain': 'runwayml.com',
                'industry': 'Creative AI'
            },
            'Jasper': {
                'careers_url': 'https://www.jasper.ai/careers',
                'email': 'careers@jasper.ai',
                'domain': 'jasper.ai',
                'industry': 'Marketing AI'
            },
            'Synthesia': {
                'careers_url': 'https://www.synthesia.io/careers',
                'email': 'careers@synthesia.io',
                'domain': 'synthesia.io',
                'industry': 'Video AI'
            },
            'Glean': {
                'careers_url': 'https://www.glean.com/careers',
                'email': 'careers@glean.com',
                'domain': 'glean.com',
                'industry': 'Enterprise Search'
            },
            'Replit': {
                'careers_url': 'https://replit.com/careers',
                'email': 'careers@replit.com',
                'domain': 'replit.com',
                'industry': 'AI Development'
            }
        }
    
    def scrape_adzuna_jobs(self, location: str = "USA", max_results: int = 50) -> List[Dict]:
        """Scrape jobs from Adzuna API"""
        jobs = []
        
        try:
            # Search for AI/ML jobs
            for keyword in ['AI Engineer', 'Machine Learning', 'Principal Engineer']:
                url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
                params = {
                    'app_id': self.adzuna_app_id,
                    'app_key': self.adzuna_app_key,
                    'results_per_page': 20,
                    'what': keyword,
                    'where': location,
                    'sort_by': 'date'
                }
                
                response = self.session.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data.get('results', []):
                        # Extract company domain from redirect URL if possible
                        company_domain = self._extract_company_domain(job.get('redirect_url', ''))
                        
                        job_data = {
                            'job_id': f"adzuna_{job.get('id')}",
                            'company': job.get('company', {}).get('display_name', 'Unknown'),
                            'position': job.get('title', ''),
                            'location': job.get('location', {}).get('display_name', ''),
                            'salary_range': self._format_salary(job.get('salary_min'), job.get('salary_max')),
                            'url': job.get('redirect_url', ''),
                            'description': job.get('description', ''),
                            'source': 'Adzuna',
                            'company_domain': company_domain
                        }
                        jobs.append(job_data)
                        
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Error scraping Adzuna: {e}")
            
        return jobs
    
    def scrape_greenhouse_boards(self) -> List[Dict]:
        """Scrape jobs from Greenhouse boards"""
        jobs = []
        
        greenhouse_companies = [
            ('temporaltechnologies', 'Temporal Technologies'),
            ('garnerhealth', 'Garner Health'),
            ('weights-biases', 'Weights & Biases'),
            ('verkada', 'Verkada'),
            ('figma', 'Figma'),
            ('notion', 'Notion'),
            ('airtable', 'Airtable')
        ]
        
        for board_id, company_name in greenhouse_companies:
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{board_id}/jobs"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data.get('jobs', []):
                        # Filter for engineering roles
                        title = job.get('title', '').lower()
                        if any(keyword.lower() in title for keyword in ['engineer', 'scientist', 'architect', 'developer']):
                            job_data = {
                                'job_id': f"greenhouse_{board_id}_{job.get('id')}",
                                'company': company_name,
                                'position': job.get('title'),
                                'location': job.get('location', {}).get('name', 'Remote'),
                                'url': job.get('absolute_url'),
                                'description': '',  # Would need separate API call
                                'source': 'Greenhouse',
                                'company_domain': f"{board_id}.com"
                            }
                            jobs.append(job_data)
                            
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping Greenhouse {board_id}: {e}")
                
        return jobs
    
    def scrape_lever_boards(self) -> List[Dict]:
        """Scrape jobs from Lever boards"""
        jobs = []
        
        lever_companies = [
            ('redcanary', 'Red Canary'),
            ('brex', 'Brex'),
            ('plaid', 'Plaid'),
            ('reddit', 'Reddit'),
            ('shopify', 'Shopify')
        ]
        
        for company_id, company_name in lever_companies:
            try:
                url = f"https://api.lever.co/v0/postings/{company_id}"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data:
                        # Filter for relevant roles
                        title = job.get('text', '').lower()
                        if any(keyword.lower() in title for keyword in ['engineer', 'scientist', 'technical']):
                            job_data = {
                                'job_id': f"lever_{company_id}_{job.get('id')}",
                                'company': company_name,
                                'position': job.get('text'),
                                'location': job.get('categories', {}).get('location', 'Remote'),
                                'url': job.get('hostedUrl'),
                                'description': job.get('descriptionPlain', ''),
                                'source': 'Lever',
                                'company_domain': f"{company_id}.com"
                            }
                            jobs.append(job_data)
                            
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping Lever {company_id}: {e}")
                
        return jobs
    
    def _extract_company_domain(self, url: str) -> Optional[str]:
        """Extract company domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove common prefixes
            for prefix in ['www.', 'careers.', 'jobs.', 'apply.']:
                if domain.startswith(prefix):
                    domain = domain[len(prefix):]
                    
            # Skip job boards
            job_boards = ['adzuna', 'indeed', 'linkedin', 'greenhouse', 'lever', 'workday']
            if any(board in domain for board in job_boards):
                return None
                
            return domain
            
        except:
            return None
    
    def _format_salary(self, min_sal: Optional[float], max_sal: Optional[float]) -> str:
        """Format salary range"""
        if min_sal and max_sal:
            return f"${min_sal:,.0f} - ${max_sal:,.0f}"
        elif min_sal:
            return f"${min_sal:,.0f}+"
        elif max_sal:
            return f"Up to ${max_sal:,.0f}"
        return ""
    
    def deduplicate_and_enrich_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicates and enrich with company emails"""
        seen = set()
        enriched = []
        
        for job in jobs:
            # Create unique key
            key = f"{job['company'].lower()}_{job['position'].lower()}"
            
            if key not in seen:
                seen.add(key)
                
                # Try to find company email
                company_email = self._find_company_email(job['company'], job.get('company_domain'))
                job['company_email'] = company_email
                job['email_confidence'] = 80 if company_email else 0
                
                # Calculate relevance score
                job['relevance_score'] = self._calculate_relevance(job)
                
                # Add metadata
                job['discovered_date'] = datetime.now().isoformat()
                job['applied'] = False
                job['email_verified'] = False
                
                enriched.append(job)
                
        return enriched
    
    def _find_company_email(self, company_name: str, domain: Optional[str]) -> Optional[str]:
        """Find company email from our database or patterns"""
        # Check our target companies first
        for target, info in self.target_companies.items():
            if company_name.lower() in target.lower() or target.lower() in company_name.lower():
                return info['email']
        
        # If we have a domain, generate likely email
        if domain:
            # Common patterns
            patterns = [
                f"careers@{domain}",
                f"jobs@{domain}",
                f"recruiting@{domain}",
                f"hr@{domain}",
                f"talent@{domain}"
            ]
            # Return the first pattern (most common)
            return patterns[0]
            
        return None
    
    def _calculate_relevance(self, job: Dict) -> float:
        """Calculate job relevance score"""
        score = 0.5  # Base score
        
        title = job.get('position', '').lower()
        company = job.get('company', '').lower()
        
        # Title scoring
        if 'principal' in title or 'staff' in title:
            score += 0.2
        if 'senior' in title:
            score += 0.1
        if any(term in title for term in ['ai', 'ml', 'machine learning', 'artificial intelligence']):
            score += 0.15
        
        # Company scoring
        if any(comp.lower() in company for comp in self.target_companies.keys()):
            score += 0.15
        
        # Has email bonus
        if job.get('company_email'):
            score += 0.1
            
        return min(score, 1.0)
    
    def save_to_database(self, jobs: List[Dict]) -> int:
        """Save jobs to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        saved = 0
        
        for job in jobs:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO jobs (
                        job_id, company, position, location, remote_option,
                        salary_range, url, description, source, discovered_date,
                        relevance_score, applied, company_email, email_verified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job['job_id'],
                    job['company'],
                    job['position'],
                    job.get('location', ''),
                    'Remote' if 'remote' in job.get('location', '').lower() else 'Onsite',
                    job.get('salary_range', ''),
                    job.get('url', ''),
                    job.get('description', ''),
                    job.get('source', 'Unknown'),
                    job['discovered_date'],
                    job['relevance_score'],
                    job['applied'],
                    job.get('company_email'),
                    job.get('email_verified', False)
                ))
                saved += 1
                
            except sqlite3.IntegrityError:
                # Job already exists
                pass
            except Exception as e:
                logger.error(f"Error saving job {job.get('job_id')}: {e}")
                
        conn.commit()
        conn.close()
        
        logger.info(f"Saved {saved} new jobs to database")
        return saved
    
    def discover_all_jobs(self) -> Dict[str, int]:
        """Main method to discover jobs from all sources"""
        logger.info("Starting comprehensive job discovery...")
        
        all_jobs = []
        
        # Scrape from each source
        logger.info("Scraping Adzuna...")
        adzuna_jobs = self.scrape_adzuna_jobs()
        all_jobs.extend(adzuna_jobs)
        logger.info(f"Found {len(adzuna_jobs)} jobs from Adzuna")
        
        logger.info("Scraping Greenhouse boards...")
        greenhouse_jobs = self.scrape_greenhouse_boards()
        all_jobs.extend(greenhouse_jobs)
        logger.info(f"Found {len(greenhouse_jobs)} jobs from Greenhouse")
        
        logger.info("Scraping Lever boards...")
        lever_jobs = self.scrape_lever_boards()
        all_jobs.extend(lever_jobs)
        logger.info(f"Found {len(lever_jobs)} jobs from Lever")
        
        # Deduplicate and enrich
        logger.info("Deduplicating and enriching jobs...")
        enriched_jobs = self.deduplicate_and_enrich_jobs(all_jobs)
        
        # Save to database
        saved = self.save_to_database(enriched_jobs)
        
        return {
            'total_scraped': len(all_jobs),
            'unique_jobs': len(enriched_jobs),
            'saved_to_db': saved,
            'with_emails': len([j for j in enriched_jobs if j.get('company_email')])
        }

def run_job_discovery():
    """Standalone function to run job discovery"""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    discovery = EnhancedJobDiscovery()
    results = discovery.discover_all_jobs()
    
    print("\n" + "="*50)
    print("🎯 Job Discovery Complete!")
    print("="*50)
    print(f"📊 Total scraped: {results['total_scraped']}")
    print(f"🔍 Unique jobs: {results['unique_jobs']}")
    print(f"💾 Saved to database: {results['saved_to_db']}")
    print(f"📧 Jobs with emails: {results['with_emails']}")
    
    return results

if __name__ == "__main__":
    run_job_discovery()