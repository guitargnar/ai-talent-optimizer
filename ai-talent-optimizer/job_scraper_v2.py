#!/usr/bin/env python3
"""
Job Scraper V2 - Real Jobs from Real Sources
Focuses on verified job boards and company career pages
"""

import requests
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from urllib.parse import urlparse
import time

class RealJobScraper:
    def __init__(self):
        """Initialize the job scraper with real sources"""
        self.db_path = "REAL_JOBS.db"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Initialize database
        self._init_database()
        
        # Target companies with verified career pages
        self.target_companies = {
            'Temporal Technologies': {
                'careers_url': 'https://job-boards.greenhouse.io/temporaltechnologies',
                'api_url': 'https://boards-api.greenhouse.io/v1/boards/temporaltechnologies/jobs',
                'email_pattern': 'careers@temporal.io'
            },
            'Zocdoc': {
                'careers_url': 'https://www.zocdoc.com/careers',
                'email_pattern': 'careers@zocdoc.com'
            },
            'Doximity': {
                'careers_url': 'https://workat.doximity.com',
                'email_pattern': 'careers@doximity.com'
            },
            'Garner Health': {
                'careers_url': 'https://boards.greenhouse.io/garnerhealth',
                'api_url': 'https://boards-api.greenhouse.io/v1/boards/garnerhealth/jobs',
                'email_pattern': 'careers@garnerhealth.com'
            },
            'Red Canary': {
                'careers_url': 'https://jobs.lever.co/redcanary',
                'email_pattern': 'careers@redcanary.com'
            }
        }
    
    def _init_database(self):
        """Create database for real jobs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                location TEXT,
                remote BOOLEAN DEFAULT 0,
                salary_min INTEGER,
                salary_max INTEGER,
                url TEXT UNIQUE NOT NULL,
                email TEXT,
                email_verified BOOLEAN DEFAULT 0,
                description TEXT,
                requirements TEXT,
                posted_date TEXT,
                scraped_date TEXT DEFAULT CURRENT_TIMESTAMP,
                applied BOOLEAN DEFAULT 0,
                applied_date TEXT,
                response_received BOOLEAN DEFAULT 0,
                response_date TEXT,
                source TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def scrape_greenhouse_api(self, company_name: str, api_url: str) -> List[Dict]:
        """Scrape jobs from Greenhouse API"""
        jobs = []
        print(f"\n🔍 Fetching {company_name} jobs from Greenhouse...")
        
        try:
            response = self.session.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for job in data.get('jobs', []):
                    # Filter for engineering roles
                    title = job.get('title', '').lower()
                    if any(keyword in title for keyword in ['engineer', 'developer', 'architect', 'technical']):
                        job_data = {
                            'company': company_name,
                            'position': job.get('title'),
                            'location': job.get('location', {}).get('name', 'Remote'),
                            'remote': 'remote' in job.get('location', {}).get('name', '').lower(),
                            'url': job.get('absolute_url'),
                            'description': '',  # Would need to fetch individual job page
                            'posted_date': job.get('updated_at', ''),
                            'source': 'greenhouse_api'
                        }
                        
                        # Check for senior/staff/principal roles
                        if any(level in title for level in ['senior', 'staff', 'principal', 'lead', 'manager', 'director']):
                            job_data['priority'] = True
                            
                        jobs.append(job_data)
                        print(f"  ✅ Found: {job_data['position']}")
                
                print(f"  Total: {len(jobs)} engineering jobs found")
            else:
                print(f"  ❌ Failed to fetch: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        return jobs
    
    def scrape_lever_jobs(self, company_name: str, lever_url: str) -> List[Dict]:
        """Scrape jobs from Lever.co"""
        jobs = []
        print(f"\n🔍 Fetching {company_name} jobs from Lever...")
        
        try:
            # Lever has a JSON API
            api_url = lever_url.replace('jobs.lever.co', 'api.lever.co/v0/postings')
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for job in data:
                    title = job.get('text', '').lower()
                    if any(keyword in title for keyword in ['engineer', 'developer', 'architect', 'technical']):
                        job_data = {
                            'company': company_name,
                            'position': job.get('text'),
                            'location': job.get('location', 'Remote'),
                            'remote': 'remote' in job.get('workplaceType', '').lower(),
                            'url': job.get('hostedUrl'),
                            'description': job.get('description', ''),
                            'posted_date': job.get('createdAt'),
                            'source': 'lever_api'
                        }
                        
                        if any(level in title for level in ['senior', 'staff', 'principal', 'lead', 'manager', 'director']):
                            job_data['priority'] = True
                            
                        jobs.append(job_data)
                        print(f"  ✅ Found: {job_data['position']}")
                
                print(f"  Total: {len(jobs)} engineering jobs found")
            else:
                print(f"  ❌ Failed to fetch: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        return jobs
    
    def extract_salary(self, text: str) -> tuple:
        """Extract salary range from text"""
        salary_min, salary_max = None, None
        
        # Look for salary patterns like $150,000 - $200,000 or $150K-$200K
        patterns = [
            r'\$(\d+),?(\d+)k?\s*[-–]\s*\$(\d+),?(\d+)k?',
            r'\$(\d+)k\s*[-–]\s*\$(\d+)k',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower().replace(',', ''))
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    try:
                        if 'k' in text.lower():
                            salary_min = int(groups[0]) * 1000
                            salary_max = int(groups[-1]) * 1000
                        else:
                            salary_min = int(''.join(groups[:2]))
                            salary_max = int(''.join(groups[-2:]))
                        break
                    except:
                        pass
        
        return salary_min, salary_max
    
    def save_jobs(self, jobs: List[Dict]):
        """Save jobs to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for job in jobs:
            try:
                # Extract salary if present
                if 'description' in job:
                    salary_min, salary_max = self.extract_salary(job.get('description', ''))
                    job['salary_min'] = salary_min
                    job['salary_max'] = salary_max
                
                # Set email from company pattern
                company = job.get('company', '')
                for target_company, info in self.target_companies.items():
                    if target_company.lower() in company.lower():
                        job['email'] = info.get('email_pattern', '')
                        break
                
                cursor.execute("""
                    INSERT OR IGNORE INTO jobs (
                        company, position, location, remote, salary_min, salary_max,
                        url, email, description, requirements, posted_date, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.get('company'),
                    job.get('position'),
                    job.get('location'),
                    job.get('remote', False),
                    job.get('salary_min'),
                    job.get('salary_max'),
                    job.get('url'),
                    job.get('email'),
                    job.get('description', ''),
                    job.get('requirements', ''),
                    job.get('posted_date'),
                    job.get('source')
                ))
                
                if cursor.rowcount > 0:
                    saved_count += 1
                    
            except Exception as e:
                print(f"    ⚠️ Error saving job: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n💾 Saved {saved_count} new jobs to database")
        return saved_count
    
    def scrape_all(self):
        """Scrape all configured sources"""
        print("=" * 60)
        print("🚀 REAL JOB SCRAPER V2")
        print("=" * 60)
        
        all_jobs = []
        
        # Scrape each company
        for company, info in self.target_companies.items():
            if 'api_url' in info:
                if 'greenhouse' in info['api_url']:
                    jobs = self.scrape_greenhouse_api(company, info['api_url'])
                    all_jobs.extend(jobs)
            elif 'lever' in info.get('careers_url', ''):
                jobs = self.scrape_lever_jobs(company, info['careers_url'])
                all_jobs.extend(jobs)
            
            time.sleep(1)  # Be respectful with rate limiting
        
        # Save all jobs
        if all_jobs:
            self.save_jobs(all_jobs)
        
        # Show summary
        self.show_summary()
        
        return all_jobs
    
    def show_summary(self):
        """Show database summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE remote = 1")
        remote_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE salary_min >= 150000")
        high_salary_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied = 0")
        not_applied = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT company, COUNT(*) as count 
            FROM jobs 
            GROUP BY company 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_companies = cursor.fetchall()
        
        print("\n" + "=" * 60)
        print("📊 DATABASE SUMMARY")
        print("=" * 60)
        print(f"Total Jobs: {total_jobs}")
        print(f"Remote Jobs: {remote_jobs}")
        print(f"High Salary (>$150K): {high_salary_jobs}")
        print(f"Not Yet Applied: {not_applied}")
        
        print("\n🏢 Top Companies:")
        for company, count in top_companies:
            print(f"  • {company}: {count} jobs")
        
        # Show some specific high-value targets
        cursor.execute("""
            SELECT company, position, salary_min, salary_max, url
            FROM jobs
            WHERE applied = 0
            AND (
                position LIKE '%Principal%' 
                OR position LIKE '%Staff%'
                OR position LIKE '%Senior Manager%'
                OR position LIKE '%Director%'
            )
            ORDER BY salary_max DESC NULLS LAST
            LIMIT 5
        """)
        high_value_jobs = cursor.fetchall()
        
        if high_value_jobs:
            print("\n🎯 HIGH-VALUE TARGETS (Not Applied):")
            for job in high_value_jobs:
                company, position, sal_min, sal_max, url = job
                salary = f"${sal_min/1000:.0f}K-${sal_max/1000:.0f}K" if sal_min else "Not listed"
                print(f"  • {company}: {position}")
                print(f"    Salary: {salary}")
                print(f"    URL: {url[:50]}...")
        
        conn.close()

def main():
    """Run the job scraper"""
    scraper = RealJobScraper()
    
    # Scrape all configured sources
    jobs = scraper.scrape_all()
    
    print(f"\n✅ Scraping complete! Found {len(jobs)} total jobs")
    print(f"📁 Jobs saved to: REAL_JOBS.db")
    print(f"\n💡 Next step: Review jobs and prepare applications")

if __name__ == "__main__":
    main()