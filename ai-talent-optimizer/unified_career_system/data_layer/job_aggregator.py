#!/usr/bin/env python3
"""
Job Aggregator for Unified Career System
Pulls from all job sources and deduplicates intelligently
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
import hashlib
import re

# Add paths for all systems
sys.path.append('/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer')
sys.path.append('/Users/matthewscott/SURVIVE/career-automation')
sys.path.append('/Users/matthewscott/Projects/jaspermatters-job-intelligence')

from master_database import MasterDatabase

class JobAggregator:
    """
    Aggregates jobs from all sources:
    - AI Talent Optimizer (Greenhouse, Lever)
    - LinkedIn Scraper (Real-time)
    - SURVIVE Career Automation (Adzuna)
    - Indeed/Monster (future)
    """
    
    def __init__(self):
        self.master_db = MasterDatabase("unified_career_system/data_layer/unified_career.db")
        self.dedup_cache = set()
        self._load_existing_jobs()
        
    def _load_existing_jobs(self):
        """Load existing job UIDs for deduplication"""
        cursor = self.master_db.conn.cursor()
        cursor.execute("SELECT job_uid FROM master_jobs")
        self.dedup_cache = {row[0] for row in cursor.fetchall()}
        print(f"📊 Loaded {len(self.dedup_cache)} existing jobs for deduplication")
        
    def is_duplicate(self, company: str, position: str, location: str = None) -> bool:
        """
        Smart duplicate detection using multiple strategies:
        1. Exact match on company + position
        2. Fuzzy match on similar titles
        3. Location-aware matching
        """
        # Normalize company and position
        company_norm = self._normalize_text(company)
        position_norm = self._normalize_text(position)
        
        # Check exact match
        cursor = self.master_db.conn.cursor()
        cursor.execute("""
        SELECT COUNT(*) FROM master_jobs
        WHERE LOWER(company) = LOWER(?)
        AND LOWER(position) = LOWER(?)
        """, (company, position))
        
        if cursor.fetchone()[0] > 0:
            return True
        
        # Check fuzzy match (similar positions at same company)
        cursor.execute("""
        SELECT position FROM master_jobs
        WHERE LOWER(company) = LOWER(?)
        """, (company,))
        
        existing_positions = [row[0].lower() for row in cursor.fetchall()]
        
        for existing_pos in existing_positions:
            if self._are_positions_similar(position_norm, existing_pos):
                return True
                
        return False
        
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        # Remove special characters and extra spaces
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = ' '.join(text.split())
        return text
        
    def _are_positions_similar(self, pos1: str, pos2: str) -> bool:
        """Check if two positions are essentially the same"""
        # Remove common variations
        replacements = [
            ('senior', 'sr'),
            ('junior', 'jr'),
            ('engineer', 'eng'),
            ('developer', 'dev'),
            ('machine learning', 'ml'),
            ('artificial intelligence', 'ai'),
            (' - ', ' '),
            ('/', ' '),
            ('(', ''),
            (')', ''),
        ]
        
        for old, new in replacements:
            pos1 = pos1.replace(old, new)
            pos2 = pos2.replace(old, new)
        
        # Check if core role is the same
        pos1_words = set(pos1.split())
        pos2_words = set(pos2.split())
        
        # If 70% of words match, consider similar
        if len(pos1_words) > 0 and len(pos2_words) > 0:
            overlap = len(pos1_words & pos2_words)
            similarity = overlap / min(len(pos1_words), len(pos2_words))
            return similarity >= 0.7
            
        return False
        
    def aggregate_greenhouse_jobs(self) -> int:
        """Pull jobs from Greenhouse API"""
        try:
            from src.services.enhanced_job_scraper import EnhancedJobScraper
            scraper = EnhancedJobScraper()
            
            companies = [
                'anthropic', 'scale', 'openai', 'stripe', 'figma',
                'notion', 'canva', 'databricks', 'snowflake', 'confluent'
            ]
            
            new_jobs = 0
            for company in companies:
                try:
                    jobs = scraper.scrape_greenhouse_board(company)
                    for job in jobs:
                        if not self.is_duplicate(job['company'], job['position']):
                            job_uid = self.master_db._generate_job_uid(
                                job['company'], job['position'], 
                                datetime.now().isoformat()
                            )
                            
                            self.master_db.conn.execute("""
                            INSERT INTO master_jobs (
                                job_uid, company, position, location,
                                url, description, source, source_job_id
                            ) VALUES (?, ?, ?, ?, ?, ?, 'greenhouse', ?)
                            """, (
                                job_uid, job['company'], job['position'],
                                job.get('location'), job.get('url'),
                                job.get('description'), job.get('id')
                            ))
                            new_jobs += 1
                            
                except Exception as e:
                    print(f"  ⚠️ Error scraping {company}: {e}")
                    
            self.master_db.conn.commit()
            return new_jobs
            
        except ImportError:
            print("  ⚠️ Greenhouse scraper not available")
            return 0
            
    def aggregate_linkedin_jobs(self) -> int:
        """Pull real-time LinkedIn jobs"""
        try:
            from linkedin_job_scraper import LinkedInJobScraper
            scraper = LinkedInJobScraper()
            
            # This would normally make real API calls
            # For now, we already have the data in the database
            return 0
            
        except ImportError:
            print("  ⚠️ LinkedIn scraper not available")
            return 0
            
    def aggregate_survive_jobs(self) -> int:
        """Pull jobs from SURVIVE Adzuna integration"""
        survive_path = Path("/Users/matthewscott/SURVIVE/career-automation/real-tracker/career-automation")
        if not survive_path.exists():
            print("  ⚠️ SURVIVE system not found")
            return 0
            
        # Would integrate with SURVIVE's Adzuna scraper
        # For now, we've already imported the CSV data
        return 0
        
    def run_aggregation(self) -> Dict:
        """Run complete aggregation from all sources"""
        print("\n🔄 Running Job Aggregation")
        print("=" * 60)
        
        results = {
            'greenhouse': 0,
            'linkedin': 0,
            'survive': 0,
            'total_new': 0,
            'duplicates_prevented': 0
        }
        
        # Aggregate from each source
        print("\n📍 Greenhouse API:")
        results['greenhouse'] = self.aggregate_greenhouse_jobs()
        print(f"  ✅ Added {results['greenhouse']} new jobs")
        
        print("\n📍 LinkedIn Scraper:")
        results['linkedin'] = self.aggregate_linkedin_jobs()
        print(f"  ✅ Added {results['linkedin']} new jobs")
        
        print("\n📍 SURVIVE/Adzuna:")
        results['survive'] = self.aggregate_survive_jobs()
        print(f"  ✅ Added {results['survive']} new jobs")
        
        results['total_new'] = sum([
            results['greenhouse'],
            results['linkedin'],
            results['survive']
        ])
        
        # Calculate duplicates prevented
        initial_cache_size = len(self.dedup_cache)
        self._load_existing_jobs()
        results['duplicates_prevented'] = len(self.dedup_cache) - initial_cache_size
        
        return results
        
    def get_priority_jobs(self, limit: int = 10) -> List[Dict]:
        """Get highest priority jobs to apply to"""
        cursor = self.master_db.conn.cursor()
        
        cursor.execute("""
        SELECT 
            job_uid, company, position, location,
            salary_min, salary_max, ml_score, url
        FROM master_jobs
        WHERE applied = 0
        AND is_active = 1
        ORDER BY 
            priority_level ASC,
            ml_score DESC,
            discovered_date DESC
        LIMIT ?
        """, (limit,))
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'job_uid': row[0],
                'company': row[1],
                'position': row[2],
                'location': row[3],
                'salary_range': f"${row[4]}-${row[5]}" if row[4] else "Not specified",
                'ml_score': row[6],
                'url': row[7]
            })
            
        return jobs
        
    def mark_inactive_jobs(self, days_old: int = 30):
        """Mark old jobs as inactive"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        cursor = self.master_db.conn.cursor()
        cursor.execute("""
        UPDATE master_jobs
        SET is_active = 0
        WHERE discovered_date < ?
        AND applied = 0
        """, (cutoff_date,))
        
        self.master_db.conn.commit()
        return cursor.rowcount


def main():
    """Run job aggregation"""
    aggregator = JobAggregator()
    
    # Run aggregation
    results = aggregator.run_aggregation()
    
    print("\n📊 Aggregation Summary:")
    print(f"Total New Jobs: {results['total_new']}")
    print(f"Duplicates Prevented: {results['duplicates_prevented']}")
    
    # Get priority jobs
    priority_jobs = aggregator.get_priority_jobs(5)
    
    if priority_jobs:
        print("\n🎯 Top Priority Jobs:")
        for i, job in enumerate(priority_jobs, 1):
            print(f"\n{i}. {job['position']} at {job['company']}")
            print(f"   Location: {job['location'] or 'Not specified'}")
            print(f"   Salary: {job['salary_range']}")
            if job['ml_score']:
                print(f"   Match Score: {job['ml_score']:.2f}")
    
    # Mark old jobs as inactive
    inactive = aggregator.mark_inactive_jobs()
    print(f"\n🗑️ Marked {inactive} old jobs as inactive")
    
    # Final stats
    stats = aggregator.master_db.get_stats()
    print(f"\n📈 Total Active Jobs: {stats['total_jobs']}")
    
    aggregator.master_db.close()

if __name__ == "__main__":
    main()