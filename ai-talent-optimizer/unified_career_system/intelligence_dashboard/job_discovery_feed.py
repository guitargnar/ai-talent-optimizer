#!/usr/bin/env python3
"""
Real-time Job Discovery Feed
Continuously discovers and prioritizes new opportunities
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import time
import threading
from queue import Queue
import requests

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from unified_career_system.data_layer.master_database import MasterDatabase
from unified_career_system.data_layer.job_aggregator import JobAggregator
from unified_career_system.ml_engine.job_matcher import JobMatcher

class JobDiscoveryFeed:
    """Real-time job discovery and prioritization"""
    
    def __init__(self):
        self.db = MasterDatabase()
        self.aggregator = JobAggregator()
        self.matcher = JobMatcher()
        
        # Discovery configuration
        self.sources = {
            'greenhouse': {
                'enabled': True,
                'frequency': 3600,  # 1 hour
                'last_check': None,
                'priority': 1
            },
            'lever': {
                'enabled': True,
                'frequency': 3600,
                'last_check': None,
                'priority': 2
            },
            'linkedin': {
                'enabled': True,
                'frequency': 1800,  # 30 minutes
                'last_check': None,
                'priority': 3
            },
            'indeed': {
                'enabled': False,  # Future
                'frequency': 7200,
                'last_check': None,
                'priority': 4
            }
        }
        
        # Real-time feed
        self.job_queue = Queue()
        self.discovery_thread = None
        self.running = False
        
    def start_discovery(self):
        """Start continuous job discovery"""
        if self.running:
            print("Discovery already running")
            return
        
        self.running = True
        self.discovery_thread = threading.Thread(target=self._discovery_loop)
        self.discovery_thread.daemon = True
        self.discovery_thread.start()
        print("🔍 Job discovery started")
    
    def stop_discovery(self):
        """Stop job discovery"""
        self.running = False
        if self.discovery_thread:
            self.discovery_thread.join(timeout=5)
        print("Discovery stopped")
    
    def _discovery_loop(self):
        """Main discovery loop"""
        while self.running:
            for source, config in self.sources.items():
                if not config['enabled']:
                    continue
                
                # Check if it's time to run this source
                if config['last_check']:
                    time_since = (datetime.now() - config['last_check']).seconds
                    if time_since < config['frequency']:
                        continue
                
                # Discover jobs from this source
                try:
                    self._discover_from_source(source)
                    config['last_check'] = datetime.now()
                except Exception as e:
                    print(f"Error discovering from {source}: {e}")
            
            # Sleep before next check
            time.sleep(60)  # Check every minute
    
    def _discover_from_source(self, source: str):
        """Discover jobs from a specific source"""
        print(f"\n🔍 Discovering from {source}...")
        
        if source == 'greenhouse':
            jobs = self._discover_greenhouse()
        elif source == 'lever':
            jobs = self._discover_lever()
        elif source == 'linkedin':
            jobs = self._discover_linkedin()
        else:
            return
        
        # Process discovered jobs
        new_count = 0
        for job in jobs:
            if self._is_new_job(job):
                self._process_new_job(job)
                new_count += 1
        
        if new_count > 0:
            print(f"  ✅ Found {new_count} new jobs from {source}")
    
    def _discover_greenhouse(self) -> List[Dict]:
        """Discover jobs from Greenhouse boards"""
        jobs = []
        
        # Top companies using Greenhouse
        companies = [
            ('anthropic', 'https://jobs.lever.co/anthropic'),
            ('openai', 'https://openai.com/careers'),
            ('scale', 'https://scale.com/careers'),
            ('databricks', 'https://databricks.com/company/careers'),
            ('stripe', 'https://stripe.com/jobs')
        ]
        
        for company, url in companies:
            try:
                # Simulate API call (would be real in production)
                # For now, create sample jobs
                if company == 'anthropic':
                    jobs.extend([
                        {
                            'title': 'ML Infrastructure Engineer',
                            'company': 'Anthropic',
                            'location': 'San Francisco, CA',
                            'source': 'greenhouse',
                            'url': f'{url}/ml-infrastructure',
                            'discovered_at': datetime.now().isoformat(),
                            'description': 'Build ML infrastructure for Claude',
                            'requirements': ['Python', 'PyTorch', 'Distributed Systems']
                        },
                        {
                            'title': 'Senior ML Engineer - Safety',
                            'company': 'Anthropic',
                            'location': 'Remote',
                            'source': 'greenhouse',
                            'url': f'{url}/ml-safety',
                            'discovered_at': datetime.now().isoformat(),
                            'description': 'Work on AI safety and alignment',
                            'requirements': ['ML', 'Research', 'Python']
                        }
                    ])
            except Exception as e:
                print(f"Error discovering from {company}: {e}")
        
        return jobs
    
    def _discover_lever(self) -> List[Dict]:
        """Discover jobs from Lever boards"""
        jobs = []
        
        # Companies using Lever
        companies = [
            ('figma', 'https://jobs.lever.co/figma'),
            ('plaid', 'https://jobs.lever.co/plaid'),
            ('netflix', 'https://jobs.lever.co/netflix')
        ]
        
        for company, url in companies:
            try:
                # Simulate discovery
                if company == 'figma':
                    jobs.append({
                        'title': 'ML Engineer - Design Intelligence',
                        'company': 'Figma',
                        'location': 'San Francisco, CA',
                        'source': 'lever',
                        'url': f'{url}/ml-design',
                        'discovered_at': datetime.now().isoformat(),
                        'description': 'Build ML for design tools',
                        'requirements': ['ML', 'Computer Vision', 'Python']
                    })
            except Exception as e:
                print(f"Error discovering from {company}: {e}")
        
        return jobs
    
    def _discover_linkedin(self) -> List[Dict]:
        """Discover jobs from LinkedIn"""
        jobs = []
        
        # Simulate LinkedIn discovery
        # In production, would use selenium or LinkedIn API
        sample_jobs = [
            {
                'title': 'Staff ML Engineer',
                'company': 'Meta',
                'location': 'Menlo Park, CA',
                'source': 'linkedin',
                'url': 'https://linkedin.com/jobs/view/12345',
                'discovered_at': datetime.now().isoformat(),
                'description': 'Work on recommendation systems',
                'posted': '2 hours ago'
            },
            {
                'title': 'ML Platform Engineer',
                'company': 'Apple',
                'location': 'Cupertino, CA',
                'source': 'linkedin',
                'url': 'https://linkedin.com/jobs/view/12346',
                'discovered_at': datetime.now().isoformat(),
                'description': 'Build ML infrastructure for Siri',
                'posted': '5 hours ago'
            }
        ]
        
        # Only return "recent" jobs
        for job in sample_jobs:
            if 'hour' in job.get('posted', ''):
                jobs.append(job)
        
        return jobs
    
    def _is_new_job(self, job: Dict) -> bool:
        """Check if job is new"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check by URL first
        if job.get('url'):
            cursor.execute(
                "SELECT 1 FROM master_jobs WHERE url = ?",
                (job['url'],)
            )
            if cursor.fetchone():
                conn.close()
                return False
        
        # Check by company + title (fuzzy)
        cursor.execute("""
            SELECT 1 FROM master_jobs 
            WHERE company = ? 
            AND title LIKE ?
        """, (job['company'], f"%{job['title'][:20]}%"))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is None
    
    def _process_new_job(self, job: Dict):
        """Process a newly discovered job"""
        # Add to aggregator for deduplication and scoring
        jobs_added = self.aggregator.aggregate_jobs([job])
        
        if jobs_added > 0:
            # Add to real-time queue
            self.job_queue.put(job)
            
            # Calculate priority
            priority = self._calculate_priority(job)
            
            # Notify if high priority
            if priority == 'URGENT':
                self._send_notification(job)
    
    def _calculate_priority(self, job: Dict) -> str:
        """Calculate job priority"""
        # Score the job
        matches = self.matcher.find_best_matches(limit=100)
        
        # Find this job in matches
        for match in matches:
            if match.get('title') == job['title'] and match.get('company') == job['company']:
                score = match.get('final_score', 0)
                
                if score > 0.85:
                    return 'URGENT'
                elif score > 0.7:
                    return 'HIGH'
                elif score > 0.5:
                    return 'MEDIUM'
                else:
                    return 'LOW'
        
        return 'UNKNOWN'
    
    def _send_notification(self, job: Dict):
        """Send notification for high-priority job"""
        print(f"\n🔥 HIGH PRIORITY JOB DISCOVERED!")
        print(f"   {job['company']} - {job['title']}")
        print(f"   Location: {job.get('location', 'Not specified')}")
        print(f"   Posted: {job.get('posted', 'Recently')}")
        print(f"   Action: Apply within 24 hours\n")
    
    def get_live_feed(self, limit: int = 20) -> List[Dict]:
        """Get live job feed with enrichment"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get most recent jobs
        cursor.execute("""
            SELECT 
                j.*,
                c.response_rate,
                c.interview_rate,
                c.avg_response_days,
                julianday('now') - julianday(j.discovered_at) as days_old,
                CASE 
                    WHEN julianday('now') - julianday(j.discovered_at) < 0.25 THEN '🔥 HOT'
                    WHEN julianday('now') - julianday(j.discovered_at) < 1 THEN '✨ NEW'
                    WHEN julianday('now') - julianday(j.discovered_at) < 3 THEN '📍 RECENT'
                    ELSE '📌 ACTIVE'
                END as freshness_badge
            FROM master_jobs j
            LEFT JOIN company_intelligence c ON j.company = c.company_name
            WHERE j.status = 'active'
            ORDER BY j.discovered_at DESC
            LIMIT ?
        """, (limit,))
        
        jobs = []
        for row in cursor.fetchall():
            job = dict(zip([col[0] for col in cursor.description], row))
            
            # Add insights
            job['insights'] = self._generate_insights(job)
            
            # Add application strategy
            job['strategy'] = self._generate_strategy(job)
            
            jobs.append(job)
        
        conn.close()
        return jobs
    
    def _generate_insights(self, job: Dict) -> List[str]:
        """Generate insights for a job"""
        insights = []
        
        # Company insights
        if job.get('response_rate'):
            if job['response_rate'] > 20:
                insights.append(f"📊 High response rate: {job['response_rate']:.1f}%")
            elif job['response_rate'] < 5:
                insights.append(f"⚠️ Low response rate: {job['response_rate']:.1f}%")
        
        # Timing insights
        if job.get('days_old'):
            if job['days_old'] < 1:
                insights.append("⏰ Apply immediately - very fresh posting")
            elif job['days_old'] > 14:
                insights.append("📅 Posted 2+ weeks ago - may be filled")
        
        # ML score insights
        if job.get('ml_score'):
            if job['ml_score'] > 0.8:
                insights.append(f"🎯 Excellent match: {job['ml_score']:.1%}")
            elif job['ml_score'] > 0.6:
                insights.append(f"✅ Good match: {job['ml_score']:.1%}")
        
        # Location insights
        if 'remote' in job.get('location', '').lower():
            insights.append("🌍 Remote position available")
        
        return insights
    
    def _generate_strategy(self, job: Dict) -> Dict:
        """Generate application strategy"""
        strategy = {
            'timing': 'standard',
            'channel': 'email',
            'priority': 'medium',
            'notes': []
        }
        
        # Timing strategy
        if job.get('days_old', 0) < 1:
            strategy['timing'] = 'immediate'
            strategy['notes'].append("Apply within 24 hours")
        elif job.get('days_old', 0) > 7:
            strategy['timing'] = 'low_priority'
            strategy['notes'].append("May already be in process")
        
        # Channel strategy
        if job.get('company') in ['Anthropic', 'OpenAI', 'DeepMind']:
            strategy['channel'] = 'portal'
            strategy['notes'].append("Use company portal for best results")
        
        # Priority based on ML score
        if job.get('ml_score', 0) > 0.8:
            strategy['priority'] = 'high'
            strategy['notes'].append("Highly qualified - customize heavily")
        elif job.get('ml_score', 0) > 0.6:
            strategy['priority'] = 'medium'
            strategy['notes'].append("Good fit - standard customization")
        else:
            strategy['priority'] = 'low'
            strategy['notes'].append("Stretch role - emphasize potential")
        
        return strategy
    
    def display_live_feed(self):
        """Display the live job feed"""
        print("\n" + "="*80)
        print("🔍 LIVE JOB DISCOVERY FEED")
        print("="*80)
        
        jobs = self.get_live_feed(10)
        
        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job.get('freshness_badge', '')} {job['company']} - {job['title']}")
            print(f"   📍 {job.get('location', 'Not specified')}")
            print(f"   🔗 {job.get('source', 'unknown').upper()}")
            
            if job.get('ml_score'):
                score_bar = "█" * int(job['ml_score'] * 10) + "░" * (10 - int(job['ml_score'] * 10))
                print(f"   📊 Match: [{score_bar}] {job['ml_score']:.1%}")
            
            # Show insights
            if job['insights']:
                print(f"   💡 Insights:")
                for insight in job['insights']:
                    print(f"      • {insight}")
            
            # Show strategy
            if job['strategy']['notes']:
                print(f"   📋 Strategy: {', '.join(job['strategy']['notes'])}")
            
            print("-" * 40)
        
        # Summary stats
        print(f"\n📈 FEED STATISTICS")
        print(f"   • Jobs shown: {len(jobs)}")
        print(f"   • High priority: {sum(1 for j in jobs if j.get('ml_score', 0) > 0.8)}")
        print(f"   • New today: {sum(1 for j in jobs if j.get('days_old', 0) < 1)}")
        
        print("\n" + "="*80)

def main():
    """Run the job discovery feed"""
    feed = JobDiscoveryFeed()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--live':
        # Start continuous discovery
        feed.start_discovery()
        
        print("Job discovery running in background...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Display live feed every 30 seconds
                feed.display_live_feed()
                time.sleep(30)
        except KeyboardInterrupt:
            feed.stop_discovery()
            print("\nDiscovery stopped.")
    else:
        # One-time display
        feed.display_live_feed()

if __name__ == "__main__":
    main()