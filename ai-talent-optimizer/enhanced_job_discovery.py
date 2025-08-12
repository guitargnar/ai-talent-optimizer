#!/usr/bin/env python3
"""
Enhanced Job Discovery - Finds MORE AI/ML jobs from multiple sources
"""

import sys
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict

# Add path to existing scrapers
sys.path.append('/Users/matthewscott/SURVIVE/career-automation/real-tracker/career-automation/interview-prep')

# Import all available scrapers
from free_job_scraper import FreeJobScraper
from scraper_adapters import JobScraperAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedJobDiscovery:
    """Discovers AI/ML jobs from multiple sources"""
    
    def __init__(self):
        self.db_path = "UNIFIED_AI_JOBS.db"
        self.scraper = FreeJobScraper()
        self.adapter = JobScraperAdapter()
        
    def calculate_relevance_score(self, job: Dict) -> float:
        """Calculate relevance based on keywords and requirements"""
        score = 0.0
        
        # High-value keywords (from config)
        high_value_keywords = [
            'AI', 'ML', 'machine learning', 'deep learning', 'LLM', 
            'computer vision', 'NLP', 'data science', 'python',
            'tensorflow', 'pytorch', 'remote', 'senior', 'staff', 'principal',
            'GPT', 'transformer', 'neural', 'artificial intelligence'
        ]
        
        # Negative keywords
        negative_keywords = [
            'junior', 'intern', 'entry level', 'clearance required',
            'on-site only', 'no remote', 'contract', 'part-time',
            'unpaid', 'volunteer', 'student'
        ]
        
        # Check title and description
        text = f"{job.get('position', '')} {job.get('description', '')}".lower()
        
        # Positive scoring
        for keyword in high_value_keywords:
            if keyword.lower() in text:
                score += 0.1
                
        # Boost for senior roles
        if any(word in text for word in ['senior', 'staff', 'principal', 'lead', 'director']):
            score += 0.2
            
        # Boost for remote
        if 'remote' in text or job.get('remote_option') == 'Remote':
            score += 0.15
            
        # Negative scoring
        for keyword in negative_keywords:
            if keyword.lower() in text:
                score -= 0.2
                
        # Salary boost
        try:
            salary_range = job.get('salary_range', '0-0')
            min_salary = int(salary_range.split('-')[0])
            if min_salary > 150000:
                score += 0.2
            elif min_salary > 120000:
                score += 0.1
        except:
            pass
            
        # Cap between 0 and 1
        return max(0.0, min(1.0, score))
        
    def discover_jobs(self, max_jobs: int = 100) -> List[Dict]:
        """Discover jobs from all sources"""
        all_jobs = []
        
        logger.info("🔍 Starting enhanced job discovery...")
        
        # Search all free sources
        try:
            logger.info("Searching Adzuna, RemoteOK, Remotive...")
            # Define keywords for AI/ML jobs
            keywords = [
                "machine learning engineer remote",
                "ML engineer remote", 
                "AI engineer remote",
                "data scientist remote",
                "senior ML engineer",
                "staff ML engineer",
                "principal ML engineer",
                "AI researcher remote",
                "LLM engineer remote",
                "computer vision engineer remote"
            ]
            jobs = self.scraper.search_all_free_sources(keywords=keywords)
            
            for job in jobs:
                # Normalize the job data
                normalized = self.adapter.normalize_job(job, job.get('source', 'Unknown'))
                
                # Calculate better relevance score
                normalized['relevance_score'] = self.calculate_relevance_score(normalized)
                
                # Only include relevant jobs
                if normalized['relevance_score'] >= 0.3:
                    all_jobs.append(normalized)
                    
            logger.info(f"✅ Found {len(all_jobs)} relevant jobs")
            
        except Exception as e:
            logger.error(f"❌ Error discovering jobs: {e}")
            
        return all_jobs
        
    def save_to_database(self, jobs: List[Dict]):
        """Save discovered jobs to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        
        for job in jobs:
            try:
                # Check if job already exists
                cursor.execute("""
                    SELECT 1 FROM job_discoveries 
                    WHERE company = ? AND position = ?
                """, (job['company'], job['position']))
                
                if cursor.fetchone():
                    continue
                    
                # Insert new job (using existing schema)
                cursor.execute("""
                    INSERT INTO job_discoveries (
                        job_id, source, company, position, description,
                        location, remote_option, salary_range, url,
                        discovered_date, relevance_score, applied
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    job['job_id'],
                    job['source'],
                    job['company'],
                    job['position'],
                    job.get('description', '')[:2000],  # Limit description length
                    job.get('location', ''),
                    job.get('remote_option', ''),
                    job.get('salary_range', '0-0'),
                    job.get('url', ''),
                    datetime.now().isoformat(),
                    job['relevance_score']
                ))
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving job {job.get('company')}: {e}")
                
        conn.commit()
        conn.close()
        
        logger.info(f"💾 Saved {saved_count} new jobs to database")
        return saved_count
        
    def run(self):
        """Main discovery process"""
        # Discover jobs
        jobs = self.discover_jobs(max_jobs=100)
        
        if not jobs:
            logger.warning("No new jobs found")
            return 0
            
        # Save to database
        saved = self.save_to_database(jobs)
        
        # Show summary
        logger.info("\n📊 Discovery Summary:")
        logger.info(f"  • Total jobs found: {len(jobs)}")
        logger.info(f"  • New jobs saved: {saved}")
        logger.info(f"  • Average relevance: {sum(j['relevance_score'] for j in jobs)/len(jobs):.2f}")
        
        # Show top 5
        top_jobs = sorted(jobs, key=lambda x: x['relevance_score'], reverse=True)[:5]
        logger.info("\n🎯 Top opportunities:")
        for job in top_jobs:
            logger.info(f"  • {job['company']} - {job['position']} (score: {job['relevance_score']:.2f})")
            
        return saved


if __name__ == "__main__":
    discovery = EnhancedJobDiscovery()
    discovery.run()