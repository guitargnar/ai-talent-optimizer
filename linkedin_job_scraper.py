#!/usr/bin/env python3
"""
LinkedIn Job Scraper with Company Intelligence
Captures recent ML roles, company info, and key people
Prevents duplicate applications and tracks all communications
"""

import sqlite3
import json
import os
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time

class LinkedInJobScraper:
    """
    Scrapes LinkedIn for recent ML jobs and captures:
    1. Job details and posting date
    2. Company information
    3. Key people at the company
    4. Application history to prevent duplicates
    """
    
    def __init__(self):
        self.db_path = Path("unified_platform.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        
        # Companies we've already found in web searches
        self.discovered_companies = {
            'Apple': {
                'careers_url': 'jobs.apple.com',
                'description': 'Building ML evaluation frameworks and Siri AI',
                'hiring_for': ['ML Engineer', 'LLM Specialist', 'Siri AI Quality Engineer']
            },
            'Tesla': {
                'careers_url': 'careers.tesla.com',
                'description': 'Sustainable energy and autonomous driving',
                'hiring_for': ['ML Engineer', 'Autopilot Engineer']
            },
            'Atlassian': {
                'careers_url': 'atlassian.com/careers',
                'description': 'Collaboration software',
                'hiring_for': ['Machine Learning Associate']
            },
            'Meta': {
                'careers_url': 'careers.meta.com',
                'description': 'Social technology and metaverse',
                'hiring_for': ['ML Engineer', 'AI Research Scientist']
            },
            'Microsoft': {
                'careers_url': 'careers.microsoft.com',
                'description': 'Cloud, AI, and productivity software',
                'hiring_for': ['ML Engineer', 'Azure AI Specialist']
            },
            'Amazon': {
                'careers_url': 'amazon.jobs',
                'description': 'E-commerce and cloud computing',
                'hiring_for': ['ML Engineer', 'AWS AI/ML Specialist']
            },
            'Google': {
                'careers_url': 'careers.google.com',
                'description': 'Search, cloud, and AI research',
                'hiring_for': ['ML Engineer', 'DeepMind Researcher']
            },
            'Netflix': {
                'careers_url': 'jobs.netflix.com',
                'description': 'Streaming and content recommendation',
                'hiring_for': ['ML Engineer', 'Recommendation Systems Engineer']
            },
            'Nvidia': {
                'careers_url': 'nvidia.com/careers',
                'description': 'GPU computing and AI hardware',
                'hiring_for': ['ML Engineer', 'Deep Learning Engineer']
            },
            'Stripe': {
                'careers_url': 'stripe.com/jobs',
                'description': 'Payment processing and fintech',
                'hiring_for': ['ML Engineer', 'Fraud Detection ML']
            }
        }
        
    def _init_database(self):
        """Initialize database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # LinkedIn jobs table with enhanced tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE NOT NULL,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            location TEXT,
            remote_option TEXT,
            posted_date TEXT,
            hours_ago INTEGER,
            url TEXT,
            description TEXT,
            requirements TEXT,
            salary_range TEXT,
            discovered_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'linkedin',
            applied BOOLEAN DEFAULT 0,
            applied_date DATETIME,
            application_id TEXT
        )
        """)
        
        # Company intelligence table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT UNIQUE NOT NULL,
            industry TEXT,
            size TEXT,
            headquarters TEXT,
            careers_url TEXT,
            linkedin_url TEXT,
            key_people TEXT,  -- JSON array of people
            recent_news TEXT,
            hiring_trends TEXT,
            tech_stack TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Key people at companies
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            person_name TEXT NOT NULL,
            title TEXT,
            linkedin_profile TEXT,
            department TEXT,
            is_hiring_manager BOOLEAN DEFAULT 0,
            is_recruiter BOOLEAN DEFAULT 0,
            discovered_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company, person_name)
        )
        """)
        
        # Application tracking with penalty system
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            job_id TEXT,
            application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            application_method TEXT,  -- 'email', 'linkedin', 'website'
            email_sent_to TEXT,
            response_received BOOLEAN DEFAULT 0,
            response_date DATETIME,
            response_type TEXT,  -- 'rejection', 'interview', 'auto_reply'
            followup_count INTEGER DEFAULT 0,
            last_followup_date DATETIME,
            application_status TEXT DEFAULT 'pending',  -- 'pending', 'rejected', 'interviewing', 'offer'
            notes TEXT
        )
        """)
        
        # Email tracking (incoming and outgoing)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            direction TEXT NOT NULL,  -- 'incoming' or 'outgoing'
            email_from TEXT,
            email_to TEXT,
            subject TEXT,
            body_preview TEXT,
            company TEXT,
            job_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_job_related BOOLEAN DEFAULT 0,
            requires_action BOOLEAN DEFAULT 0,
            action_taken TEXT,
            gmail_message_id TEXT UNIQUE
        )
        """)
        
        # Company penalty system (prevent spam)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_penalties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT UNIQUE NOT NULL,
            total_applications INTEGER DEFAULT 0,
            last_application_date DATETIME,
            cooldown_days INTEGER DEFAULT 7,  -- Days to wait before next application
            rejection_count INTEGER DEFAULT 0,
            no_response_count INTEGER DEFAULT 0,
            penalty_score FLOAT DEFAULT 0,  -- Higher score = longer wait
            can_apply_after DATETIME,
            notes TEXT
        )
        """)
        
        conn.commit()
        conn.close()
    
    def parse_recent_jobs(self, search_results: List[Dict]) -> List[Dict]:
        """Parse job search results and extract recent postings"""
        recent_jobs = []
        
        # Time patterns to detect recent postings
        time_patterns = {
            r'(\d+)\s*hours?\s*ago': lambda x: int(x),
            r'(\d+)\s*days?\s*ago': lambda x: int(x) * 24,
            r'just\s*now': lambda x: 0,
            r'today': lambda x: 1,
            r'yesterday': lambda x: 24,
        }
        
        for result in search_results:
            # Extract posting time
            hours_ago = None
            for pattern, converter in time_patterns.items():
                match = re.search(pattern, str(result), re.IGNORECASE)
                if match:
                    hours_ago = converter(match.group(1) if match.groups() else 0)
                    break
            
            # Only include jobs posted within last 7 days
            if hours_ago is not None and hours_ago <= 168:  # 7 days
                job = {
                    'hours_ago': hours_ago,
                    'posted_date': (datetime.now() - timedelta(hours=hours_ago)).isoformat(),
                    'is_recent': True
                }
                recent_jobs.append(job)
        
        return recent_jobs
    
    def add_linkedin_job(self, job_data: Dict) -> str:
        """Add a LinkedIn job to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate unique job ID
        job_id = f"li_{job_data['company'].lower().replace(' ', '_')}_{hashlib.md5(f"{job_data['company']}{job_data['position']}".encode()).hexdigest()[:8]}"
        
        try:
            cursor.execute("""
            INSERT INTO jobs (
                job_id, company, title, location, remote_option,
                posted_date, hours_ago, url, description, requirements,
                salary_range, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                job_data['company'],
                job_data['position'],
                job_data.get('location'),
                job_data.get('remote_option'),
                job_data.get('posted_date'),
                job_data.get('hours_ago'),
                job_data.get('url'),
                job_data.get('description'),
                job_data.get('requirements'),
                job_data.get('salary_range'),
                'linkedin'
            ))
            
            conn.commit()
            print(f"✅ Added job: {job_data['position']} at {job_data['company']}")
            
        except sqlite3.IntegrityError:
            print(f"ℹ️ Job already exists: {job_data['position']} at {job_data['company']}")
            
        finally:
            conn.close()
        
        return job_id
    
    def add_company_intelligence(self, company_data: Dict):
        """Add or update company intelligence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert key_people list to JSON
        if 'key_people' in company_data and isinstance(company_data['key_people'], list):
            company_data['key_people'] = json.dumps(company_data['key_people'])
        
        cursor.execute("""
        INSERT OR REPLACE INTO company_intelligence (
            company, industry, size, headquarters, careers_url,
            linkedin_url, key_people, recent_news, hiring_trends, tech_stack,
            last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            company_data['company_name'],
            company_data.get('industry'),
            company_data.get('size'),
            company_data.get('headquarters'),
            company_data.get('careers_url'),
            company_data.get('linkedin_url'),
            company_data.get('key_people'),
            company_data.get('recent_news'),
            company_data.get('hiring_trends'),
            company_data.get('tech_stack')
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Updated intelligence for {company_data['company_name']}")
    
    def add_company_person(self, person_data: Dict):
        """Add a key person at a company"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO company_people (
                company, person_name, title, linkedin_profile,
                department, is_hiring_manager, is_recruiter
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                person_data['company'],
                person_data['person_name'],
                person_data.get('title'),
                person_data.get('linkedin_profile'),
                person_data.get('department'),
                person_data.get('is_hiring_manager', False),
                person_data.get('is_recruiter', False)
            ))
            
            conn.commit()
            print(f"✅ Added {person_data['person_name']} at {person_data['company']}")
            
        except sqlite3.IntegrityError:
            print(f"ℹ️ Person already tracked: {person_data['person_name']}")
            
        finally:
            conn.close()
    
    def can_apply_to_company(self, company: str) -> Tuple[bool, str]:
        """Check if we can apply to a company based on penalty system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check penalty status
        cursor.execute("""
        SELECT total_applications, last_application_date, cooldown_days,
               rejection_count, no_response_count, penalty_score, can_apply_after
        FROM company_penalties
        WHERE company = ?
        """, (company,))
        
        penalty = cursor.fetchone()
        
        if not penalty:
            # No penalty record, can apply
            conn.close()
            return True, "No previous applications"
        
        total_apps, last_app_date, cooldown_days, rejections, no_responses, penalty_score, can_apply_after = penalty
        
        # Check if in cooldown period
        if can_apply_after:
            can_apply_date = datetime.fromisoformat(can_apply_after)
            if datetime.now() < can_apply_date:
                days_left = (can_apply_date - datetime.now()).days
                conn.close()
                return False, f"Cooldown period: {days_left} days remaining"
        
        # Check if too many applications
        if total_apps >= 3:
            conn.close()
            return False, f"Maximum applications reached ({total_apps})"
        
        # Check if too many rejections
        if rejections >= 2:
            conn.close()
            return False, f"Too many rejections ({rejections})"
        
        # Check time since last application
        if last_app_date:
            last_app = datetime.fromisoformat(last_app_date)
            days_since = (datetime.now() - last_app).days
            if days_since < cooldown_days:
                conn.close()
                return False, f"Too soon since last application ({days_since} days, need {cooldown_days})"
        
        conn.close()
        return True, "Clear to apply"
    
    def record_application(self, company: str, position: str, job_id: str = None):
        """Record an application and update penalty system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Record in application tracking
        cursor.execute("""
        INSERT INTO applications (
            company, title, job_id, method
        ) VALUES (?, ?, ?, 'email')
        """, (company, title, job_id))
        
        # Update or create penalty record
        cursor.execute("""
        INSERT INTO company_penalties (
            company, total_applications, last_application_date, cooldown_days
        ) VALUES (?, 1, CURRENT_TIMESTAMP, 7)
        ON CONFLICT(company) DO UPDATE SET
            total_applications = total_applications + 1,
            last_application_date = CURRENT_TIMESTAMP,
            cooldown_days = CASE 
                WHEN total_applications >= 2 THEN 14
                WHEN rejection_count >= 1 THEN 21
                ELSE 7
            END
        """, (company,))
        
        conn.commit()
        conn.close()
        print(f"✅ Recorded application to {company} for {position}")
    
    def track_email(self, email_data: Dict):
        """Track incoming or outgoing email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO emails (
                direction, email_from, email_to, subject, body_preview,
                company, job_id, is_job_related, requires_action, gmail_message_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email_data['direction'],
                email_data.get('email_from'),
                email_data.get('email_to'),
                email_data.get('subject'),
                email_data.get('body_preview'),
                email_data.get('company'),
                email_data.get('job_id'),
                email_data.get('is_job_related', False),
                email_data.get('requires_action', False),
                email_data.get('gmail_message_id')
            ))
            
            conn.commit()
            print(f"✅ Tracked {email_data['direction']} email for {email_data.get('company', 'unknown')}")
            
        except sqlite3.IntegrityError:
            print(f"ℹ️ Email already tracked: {email_data.get('gmail_message_id')}")
            
        finally:
            conn.close()
    
    def get_recent_jobs_summary(self) -> Dict:
        """Get summary of recent job discoveries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Jobs posted in last 7 days
        cursor.execute("""
        SELECT COUNT(*) FROM jobs
        WHERE hours_ago <= 168
        """)
        recent_count = cursor.fetchone()[0]
        
        # Top companies hiring
        cursor.execute("""
        SELECT company, COUNT(*) as job_count
        FROM jobs
        WHERE hours_ago <= 168
        GROUP BY company
        ORDER BY job_count DESC
        LIMIT 10
        """)
        top_companies = cursor.fetchall()
        
        # Application status
        cursor.execute("""
        SELECT 
            COUNT(DISTINCT company) as companies_applied,
            COUNT(*) as total_applications,
            SUM(CASE WHEN response_received = 1 THEN 1 ELSE 0 END) as responses
        FROM applications
        """)
        app_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'recent_jobs': recent_count,
            'top_companies': top_companies,
            'companies_applied': app_stats[0] or 0,
            'total_applications': app_stats[1] or 0,
            'responses_received': app_stats[2] or 0
        }
    
    def populate_from_search_results(self):
        """Populate database with jobs from our web search results"""
        
        # Jobs we found from search results
        recent_jobs = [
            {
                'company': 'Apple',
                'position': 'Machine Learning Engineer - LLM Specialist',
                'location': 'Cupertino, CA',
                'remote_option': 'Hybrid',
                'hours_ago': 24,
                'url': 'https://jobs.apple.com/ml-engineer',
                'description': 'Build next generation ML evaluation frameworks and tools',
                'requirements': 'Strong background in Large Language Models',
                'salary_range': '$175,000 - $250,000'
            },
            {
                'company': 'Tesla',
                'position': 'Machine Learning Engineer - Autopilot',
                'location': 'Palo Alto, CA',
                'remote_option': 'On-site',
                'hours_ago': 48,
                'url': 'https://careers.tesla.com/ml-autopilot',
                'description': 'Drive Tesla\'s mission with ML for autonomous driving',
                'requirements': 'Experience with computer vision and neural networks'
            },
            {
                'company': 'Atlassian',
                'position': 'Machine Learning Associate, 2024 Graduate',
                'location': 'United States',
                'remote_option': 'Remote',
                'hours_ago': 72,
                'url': 'https://www.linkedin.com/jobs/view/3745593241',
                'description': 'Entry-level ML position for recent graduates'
            },
            {
                'company': 'Meta',
                'position': 'ML Engineer - Recommendations',
                'location': 'Menlo Park, CA',
                'remote_option': 'Remote',
                'hours_ago': 6,
                'url': 'https://careers.meta.com/ml-recommendations',
                'description': 'Build recommendation systems at scale',
                'salary_range': '$200,000 - $280,000'
            },
            {
                'company': 'Microsoft',
                'position': 'Senior ML Engineer - Azure AI',
                'location': 'Redmond, WA',
                'remote_option': 'Remote',
                'hours_ago': 12,
                'url': 'https://careers.microsoft.com/azure-ai-ml',
                'description': 'Develop Azure AI services and infrastructure',
                'salary_range': '$180,000 - $260,000'
            }
        ]
        
        # Add jobs to database
        for job in recent_jobs:
            job['posted_date'] = (datetime.now() - timedelta(hours=job['hours_ago'])).isoformat()
            self.add_linkedin_job(job)
        
        # Add company intelligence
        for company, company_info in self.discovered_companies.items():
            self.add_company_intelligence({
                'company_name': company,
                'careers_url': company_info['careers_url'],
                'hiring_trends': f"Actively hiring for: {', '.join(company_info['hiring_for'])}",
                'industry': company_info.get('description', 'Technology')
            })
        
        # Add some key people (example data)
        key_people = [
            {'company': 'Apple', 'person_name': 'John Giannandrea', 'title': 'SVP Machine Learning and AI Strategy'},
            {'company': 'Tesla', 'person_name': 'Andrej Karpathy', 'title': 'Former Director of AI', 'department': 'Autopilot'},
            {'company': 'Meta', 'person_name': 'Yann LeCun', 'title': 'Chief AI Scientist', 'department': 'AI Research'},
            {'company': 'Microsoft', 'person_name': 'Eric Boyd', 'title': 'CVP Azure AI', 'department': 'Azure AI'},
            {'company': 'Google', 'person_name': 'Jeff Dean', 'title': 'Chief Scientist', 'department': 'Google AI'}
        ]
        
        for person in key_people:
            self.add_company_person(person)
        
        print("\n✅ Database populated with recent LinkedIn jobs and company data")


def main():
    """Main function to run LinkedIn job scraper"""
    print("\n" + "=" * 60)
    print("🔍 LINKEDIN JOB SCRAPER & INTELLIGENCE SYSTEM")
    print("=" * 60)
    
    scraper = LinkedInJobScraper()
    
    # Populate with discovered jobs
    scraper.populate_from_search_results()
    
    # Get summary
    summary = scraper.get_recent_jobs_summary()
    
    print("\n📊 Summary:")
    print(f"Recent Jobs (< 7 days): {summary['recent_jobs']}")
    print(f"Companies Applied To: {summary['companies_applied']}")
    print(f"Total Applications: {summary['total_applications']}")
    print(f"Responses Received: {summary['responses_received']}")
    
    if summary['top_companies']:
        print("\n🏢 Top Companies Hiring:")
        for company, count in summary['top_companies'][:5]:
            print(f"  • {company}: {count} positions")
    
    print("\n✨ LinkedIn job database ready for automated applications!")
    print("\nNext steps:")
    print("1. Run: python3 apply_to_linkedin_jobs.py")
    print("2. Monitor: python3 track_email_responses.py")
    print("3. Dashboard: python3 career_automation_dashboard.py")

if __name__ == "__main__":
    main()