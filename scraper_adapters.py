#!/usr/bin/env python3
"""
Adapter classes to normalize different job scraper interfaces
"""

import sys
import time
import random
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Add career-automation path
sys.path.append('/Users/matthewscott/SURVIVE/career-automation/real-tracker/career-automation/interview-prep')

logger = logging.getLogger(__name__)

class JobScraperAdapter:
    """Base adapter class for normalizing job scrapers"""
    
    @staticmethod
    def normalize_job(job: Dict, source: str) -> Dict:
        """Normalize job object to standard format"""
        
        # Handle different field names
        position = job.get('position') or job.get('title') or 'Unknown Position'
        company = job.get('company') or 'Unknown Company'
        
        # Handle salary
        salary_range = "0-0"
        if 'salary_range' in job:
            salary_range = job['salary_range']
        elif 'salary_min' in job and 'salary_max' in job:
            min_sal = int(job.get('salary_min', 0) or 0)
            max_sal = int(job.get('salary_max', 0) or 0)
            if min_sal > 0 or max_sal > 0:
                salary_range = f"{min_sal}-{max_sal}"
        elif 'salary' in job and job['salary']:
            # Try to parse string salary
            salary_str = str(job['salary'])
            if '-' in salary_str:
                salary_range = salary_str
            elif '$' in salary_str:
                # Extract numbers from salary string
                import re
                numbers = re.findall(r'\d+', salary_str.replace(',', ''))
                if numbers:
                    if len(numbers) >= 2:
                        salary_range = f"{numbers[0]}000-{numbers[1]}000"
                    else:
                        salary_range = f"{numbers[0]}000-{int(numbers[0])*1.2}000"
        
        # Build normalized job
        normalized = {
            'job_id': job.get('job_id') or f"{company}_{position}_{datetime.now().timestamp()}",
            'source': source,
            'company': company,
            'position': position,
            'description': job.get('description', '')[:2000],  # Limit description length
            'location': job.get('location', 'Not specified'),
            'remote_option': job.get('remote_option', 'Unknown'),
            'salary_range': salary_range,
            'url': job.get('url', ''),
            'posted_date': job.get('posted_date') or datetime.now().isoformat(),
            'relevance_score': job.get('match_score', 50) / 100.0  # Convert to 0-1 scale
        }
        
        # Add optional fields if present
        if 'requirements' in job:
            normalized['requirements'] = job['requirements']
        if 'technologies' in job:
            normalized['technologies'] = job['technologies']
            
        return normalized


class FreeJobScraperAdapter:
    """Adapter for FreeJobScraper"""
    
    def __init__(self):
        self.scraper = None
        self.initialized = False
        
    def initialize(self):
        """Lazy initialization of scraper"""
        if not self.initialized:
            try:
                from free_job_scraper import FreeJobScraper
                self.scraper = FreeJobScraper()
                self.initialized = True
                logger.info("FreeJobScraper initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize FreeJobScraper: {e}")
                
    def search_ai_jobs(self, max_jobs: int = 20) -> List[Dict]:
        """Search for AI/ML jobs using free sources"""
        self.initialize()
        if not self.scraper:
            return []
            
        all_jobs = []
        
        try:
            # Search with AI/ML keywords
            ai_keywords = [
                "artificial intelligence",
                "machine learning",
                "deep learning",
                "AI engineer",
                "ML engineer",
                "data scientist",
                "neural network",
                "LLM",
                "NLP"
            ]
            
            jobs = self.scraper.search_all_free_sources(keywords=ai_keywords)
            
            # Normalize each job
            for job in jobs[:max_jobs]:
                normalized = JobScraperAdapter.normalize_job(job, 'free_api')
                all_jobs.append(normalized)
                
            logger.info(f"FreeJobScraper found {len(all_jobs)} AI/ML jobs")
            
        except Exception as e:
            logger.error(f"FreeJobScraper search failed: {e}")
            
        return all_jobs


class MultiSourceScraperAdapter:
    """Adapter for MultiSourceJobScraper"""
    
    def __init__(self):
        self.scraper = None
        self.initialized = False
        
    def initialize(self):
        """Lazy initialization of scraper"""
        if not self.initialized:
            try:
                from multi_source_job_scraper import MultiSourceJobScraper
                self.scraper = MultiSourceJobScraper()
                self.initialized = True
                logger.info("MultiSourceJobScraper initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize MultiSourceJobScraper: {e}")
                
    def search_ai_jobs(self, max_jobs: int = 20) -> List[Dict]:
        """Search for AI/ML jobs using multiple sources"""
        self.initialize()
        if not self.scraper:
            return []
            
        all_jobs = []
        
        try:
            # MultiSourceJobScraper expects keywords parameter
            ai_keywords = [
                "AI", "ML", "artificial intelligence",
                "machine learning", "deep learning"
            ]
            
            jobs = self.scraper.search_all_sources(keywords=ai_keywords)
            
            # Normalize each job
            for job in jobs[:max_jobs]:
                normalized = JobScraperAdapter.normalize_job(job, 'multi_source')
                all_jobs.append(normalized)
                
            logger.info(f"MultiSourceJobScraper found {len(all_jobs)} AI/ML jobs")
            
        except Exception as e:
            logger.error(f"MultiSourceJobScraper search failed: {e}")
            
        return all_jobs


class EnhancedJobScraperAdapter:
    """Adapter for EnhancedJobScraper (Selenium-based)"""
    
    def __init__(self):
        self.scraper = None
        self.initialized = False
        
    def initialize(self):
        """Lazy initialization of scraper"""
        if not self.initialized:
            try:
                from enhanced_automation.enhanced_job_scraper import EnhancedJobScraper
                self.scraper = EnhancedJobScraper(headless=True)
                self.initialized = True
                logger.info("EnhancedJobScraper initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EnhancedJobScraper: {e}")
                
    def scrape_job_urls(self, urls: List[str]) -> List[Dict]:
        """Scrape specific job URLs"""
        self.initialize()
        if not self.scraper:
            return []
            
        all_jobs = []
        
        try:
            for url in urls:
                try:
                    job_data = self.scraper.scrape_job(url)
                    
                    # Convert to our normalized format
                    normalized = {
                        'job_id': f"scraped_{datetime.now().timestamp()}",
                        'source': 'selenium_scrape',
                        'company': job_data.get('company', 'Unknown'),
                        'position': job_data.get('title', 'Unknown Position'),
                        'description': job_data.get('description', ''),
                        'location': job_data.get('location', 'Not specified'),
                        'remote_option': 'Unknown',
                        'salary_range': job_data.get('salary', '0-0'),
                        'url': url,
                        'posted_date': job_data.get('scraped_at', datetime.now().isoformat()),
                        'relevance_score': 0.7  # Default relevance
                    }
                    
                    all_jobs.append(normalized)
                    
                    # Anti-detection delay
                    time.sleep(random.uniform(3, 7))
                    
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {e}")
                    continue
                    
            logger.info(f"EnhancedJobScraper scraped {len(all_jobs)} jobs")
            
        except Exception as e:
            logger.error(f"EnhancedJobScraper failed: {e}")
        finally:
            if self.scraper and hasattr(self.scraper, 'close_driver'):
                self.scraper.close_driver()
                
        return all_jobs
    
    def search_company_pages(self, companies: List[tuple]) -> List[Dict]:
        """Search specific company career pages"""
        all_jobs = []
        
        # For now, return placeholder data
        # In production, would scrape actual company pages
        for company_name, career_url in companies:
            job = {
                'job_id': f"{company_name.lower()}_ai_2025",
                'source': 'company_page',
                'company': company_name,
                'position': 'AI/ML Engineer',
                'description': f"Join {company_name}'s AI team",
                'location': 'Various',
                'remote_option': 'Hybrid',
                'salary_range': '250000-500000',
                'url': career_url,
                'posted_date': datetime.now().isoformat(),
                'relevance_score': 0.8
            }
            all_jobs.append(job)
            
        return all_jobs


class UnifiedJobScraper:
    """Unified interface for all job scrapers"""
    
    def __init__(self):
        self.adapters = {
            'free': FreeJobScraperAdapter(),
            'multi': MultiSourceScraperAdapter(),
            'enhanced': EnhancedJobScraperAdapter()
        }
        
    def search_all_sources(self, max_jobs_per_source: int = 10) -> List[Dict]:
        """Search all available sources for AI/ML jobs"""
        all_jobs = []
        
        # Try free sources first (most reliable)
        logger.info("🔍 Searching free API sources...")
        free_jobs = self.adapters['free'].search_ai_jobs(max_jobs_per_source)
        all_jobs.extend(free_jobs)
        
        # Try multi-source scraper
        logger.info("🔍 Searching multiple sources...")
        multi_jobs = self.adapters['multi'].search_ai_jobs(max_jobs_per_source)
        all_jobs.extend(multi_jobs)
        
        # Try company pages (using enhanced scraper)
        logger.info("🔍 Checking target company pages...")
        target_companies = [
            ('OpenAI', 'https://openai.com/careers'),
            ('Anthropic', 'https://www.anthropic.com/careers'),
            ('Google DeepMind', 'https://www.deepmind.com/careers'),
            ('Meta AI', 'https://ai.facebook.com/join-us/'),
            ('Cohere', 'https://cohere.com/careers')
        ]
        company_jobs = self.adapters['enhanced'].search_company_pages(target_companies[:3])
        all_jobs.extend(company_jobs)
        
        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = f"{job['company']}_{job['position']}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
                
        logger.info(f"✅ Total unique AI/ML jobs found: {len(unique_jobs)}")
        return unique_jobs
        
    def close_all(self):
        """Clean up any resources"""
        for adapter in self.adapters.values():
            if hasattr(adapter, 'scraper') and adapter.scraper:
                if hasattr(adapter.scraper, 'close_driver'):
                    adapter.scraper.close_driver()


def test_adapters():
    """Test the adapter system"""
    print("🧪 Testing Job Scraper Adapters")
    print("="*60)
    
    scraper = UnifiedJobScraper()
    
    try:
        jobs = scraper.search_all_sources(max_jobs_per_source=5)
        
        print(f"\n✅ Found {len(jobs)} total jobs")
        
        # Display first few jobs
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job['position']} at {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Salary: ${job['salary_range']}")
            print(f"   Source: {job['source']}")
            print(f"   Score: {job['relevance_score']:.2f}")
            
    finally:
        scraper.close_all()
        
    print("\n✅ Adapter test complete!")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_adapters()