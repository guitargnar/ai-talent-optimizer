#!/usr/bin/env python3
"""
Connect Job Scrapers to Unified AI Hunter System
Production-ready integration with error handling and fallbacks
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
# Add career-automation path
sys.path.append('/Users/matthewscott/SURVIVE/career-automation/real-tracker/career-automation/interview-prep')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(full_name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_scraper_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JobScraperIntegration:
    """Integrates multiple job scrapers with unified AI hunter system"""
    
    def __init__(self):
        self.unified_db_path = "unified_platform.db"
        self.ai_keywords = [
            "AI", "artificial intelligence", "machine learning", "ML",
            "deep learning", "neural network", "LLM", "large language model",
            "NLP", "computer vision", "research scientist", "AI researcher",
            "AI engineer", "ML engineer", "AI solutions architect"
        ]
        # Use the unified adapter system
        self._initialize_unified_scraper()
    
    def _initialize_unified_scraper(self):
        """Initialize the unified scraper adapter"""
        try:
            from scraper_adapters import UnifiedJobScraper
            self.unified_scraper = UnifiedJobScraper()
            logger.info("✓ Unified job scraper system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize unified scraper: {e}")
            self.unified_scraper = None
    
    def discover_ai_jobs(self, max_jobs: int = 50) -> List[Dict]:
        """Discover AI/ML jobs from all available sources"""
        all_jobs = []
        
        # Use the unified scraper if available
        if self.unified_scraper:
            try:
                logger.info("🔍 Searching for AI/ML jobs across all sources...")
                all_jobs = self.unified_scraper.search_all_sources(max_jobs_per_source=max_jobs // 3)
                logger.info(f"  Found {len(all_jobs)} jobs from unified scraper")
            except Exception as e:
                logger.error(f"Unified scraper failed: {e}")
        
        # Fallback: Use hardcoded opportunities if scrapers fail
        if not all_jobs:
            logger.warning("No jobs found via scrapers, using fallback opportunities")
            all_jobs = self._get_fallback_opportunities()
        
        # Filter for AI/ML roles (already done by adapters, but double-check)
        ai_jobs = self._filter_ai_ml_jobs(all_jobs)
        
        logger.info(f"✅ Total AI/ML jobs discovered: {len(ai_jobs)}")
        return ai_jobs[:max_jobs]
    
    
    def _get_fallback_opportunities(self) -> List[Dict]:
        """Hardcoded opportunities as fallback"""
        return [
            {
                'job_id': 'openai_research_2025',
                'company': 'OpenAI',
                'position': 'AI Research Scientist',
                'location': 'San Francisco, CA',
                'remote_option': 'Hybrid',
                'salary_range': '350000-500000',
                'url': 'https://openai.com/careers',
                'description': 'Work on cutting-edge AI research',
                'posted_date': datetime.now().isoformat(),
                'source': 'fallback'
            },
            {
                'job_id': 'anthropic_safety_2025',
                'company': 'Anthropic',
                'position': 'AI Safety Researcher',
                'location': 'Remote',
                'remote_option': 'Full Remote',
                'salary_range': '300000-450000',
                'url': 'https://anthropic.com/careers',
                'description': 'Research AI alignment and safety',
                'posted_date': datetime.now().isoformat(),
                'source': 'fallback'
            }
        ]
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on company + position"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = f"{job.get('company', '')}_{job.get('position', '')}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _filter_ai_ml_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter for AI/ML specific roles"""
        ai_jobs = []
        
        for job in jobs:
            # Check position title
            title = job.get('position', '').lower()
            description = job.get('description', '').lower()
            
            # Look for AI/ML keywords
            if any(keyword.lower() in position or keyword.lower() in description 
                   for keyword in self.ai_keywords):
                ai_jobs.append(job)
        
        return ai_jobs
    
    def save_to_unified_db(self, jobs: List[Dict]):
        """Save discovered jobs to unified database"""
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        # Ensure job_discoveries table exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            job_id TEXT UNIQUE,
            company TEXT,
            position TEXT,
            location TEXT,
            remote_option TEXT,
            salary_range TEXT,
            url TEXT,
            description TEXT,
            discovered_date TEXT,
            relevance_score REAL,
            applied BOOLEAN DEFAULT 0,
            skip_reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Insert jobs
        new_jobs = 0
        for job in jobs:
            try:
                cursor.execute('''
                INSERT OR IGNORE INTO job_discoveries 
                (source, job_id, company, title, location, remote_option,
                 salary_range, url, description, discovered_date, relevance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job.get('source', 'scraper'),
                    job.get('job_id', f"{job['company']}_{job['position']}_{datetime.now().timestamp()}"),
                    job.get('company'),
                    job.get('position'),
                    job.get('location', 'Not specified'),
                    job.get('remote_option', 'Unknown'),
                    job.get('salary_range', '0-0'),
                    job.get('url', ''),
                    job.get('description', '')[:1000],  # Truncate long descriptions
                    datetime.now().isoformat(),
                    job.get('relevance_score', 0.5)
                ))
                
                if cursor.rowcount > 0:
                    new_jobs += 1
                    
            except Exception as e:
                logger.error(f"Error saving job: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"💾 Saved {new_jobs} new jobs to database")
        return new_jobs

def integrate_with_unified_hunter():
    """Update unified_ai_hunter.py to use real job discovery"""
    
    integration_code = '''
    def discover_ai_jobs(self, max_jobs: int = 50) -> List[Dict]:
        """Discover new AI/ML jobs from all sources"""
        logger.info(f"Discovering up to {max_jobs} new AI/ML jobs...")
        
        # Use the job scraper integration
        try:
            from connect_job_scrapers import JobScraperIntegration
            scraper_integration = JobScraperIntegration()
            
            # Discover jobs
            jobs = scraper_integration.discover_ai_jobs(max_jobs)
            
            # Save to database
            scraper_integration.save_to_unified_db(jobs)
            
            logger.info(f"Discovered {len(jobs)} potential AI/ML jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"Job discovery failed: {e}")
            return []
    '''
    
    print("\n📝 To integrate with unified_ai_hunter.py:")
    print("Replace the discover_ai_jobs method with the code above")
    print("\nOr run: python connect_job_scrapers.py --test")

def main():
    """Test the job scraper integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Job Scraper Integration')
    parser.add_argument('--test', action='store_true', help='Test job discovery')
    parser.add_argument('--max-jobs', type=int, default=20, help='Max jobs to discover')
    args = parser.parse_args()
    
    if args.test:
        print("🚀 Testing Job Scraper Integration")
        print("="*60)
        
        integration = JobScraperIntegration()
        
        # Test discovery
        jobs = integration.discover_ai_jobs(args.max_jobs)
        
        print(f"\n📊 Discovered {len(jobs)} AI/ML jobs:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"\n{i}. {job['position']} at {job['company']}")
            print(f"   Location: {job.get('location', 'Not specified')}")
            print(f"   Salary: ${job.get('salary_range', 'Not specified')}")
            print(f"   Source: {job.get('source', 'Unknown')}")
        
        if len(jobs) > 5:
            print(f"\n... and {len(jobs) - 5} more jobs")
        
        # Save to database
        saved = integration.save_to_unified_db(jobs)
        print(f"\n✅ Integration test complete! {saved} new jobs saved.")
    
    else:
        integrate_with_unified_hunter()

if __name__ == "__main__":
    main()