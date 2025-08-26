#!/usr/bin/env python3
"""
Master Database for Unified Career Intelligence System
Combines all job sources into a single source of truth
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

class MasterDatabase:
    """
    Unified database combining:
    - AI Talent Optimizer (345+ jobs)
    - SURVIVE Career Automation (1,601+ applications)
    - LinkedIn Scraper (real-time jobs)
    - Jaspermatters Intelligence (ML-analyzed jobs)
    """
    
    def __init__(self, db_path: str = "unified_platform.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        
    def _init_schema(self):
        """Create unified schema for all job sources"""
        cursor = self.conn.cursor()
        
        # Master jobs table - combines all sources
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_uid TEXT UNIQUE NOT NULL,  -- Universal unique ID
            
            -- Core job information
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            department TEXT,
            level TEXT,  -- Entry, Mid, Senior, Staff, Principal
            
            -- Location details
            location TEXT,
            remote_type TEXT,  -- Remote, Hybrid, On-site
            timezone TEXT,
            
            -- Compensation
            salary_min INTEGER,
            salary_max INTEGER,
            salary_currency TEXT DEFAULT 'USD',
            equity_offered BOOLEAN DEFAULT 0,
            
            -- Job details
            description TEXT,
            requirements TEXT,
            nice_to_have TEXT,
            benefits TEXT,
            
            -- URLs and sources
            url TEXT,
            source TEXT NOT NULL,  -- greenhouse, lever, linkedin, indeed, etc.
            source_job_id TEXT,
            careers_page TEXT,
            
            -- Dates
            posted_date DATETIME,
            discovered_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_date DATETIME,
            
            -- ML Analysis
            ml_score FLOAT,  -- Overall match score
            salary_predicted INTEGER,  -- ML predicted salary
            vector_embedding BLOB,  -- Stored embeddings
            cluster_id INTEGER,  -- Job cluster
            keywords_extracted TEXT,  -- JSON array
            
            -- Application status
            applied BOOLEAN DEFAULT 0,
            applied_date DATETIME,
            application_method TEXT,  -- email, website, linkedin
            application_id TEXT,
            
            -- Company intelligence
            company_size TEXT,
            company_industry TEXT,
            company_stage TEXT,  -- Startup, Growth, Enterprise
            glassdoor_rating FLOAT,
            
            -- Metadata
            is_active BOOLEAN DEFAULT 1,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            quality_score FLOAT,  -- Job posting quality
            priority_level INTEGER DEFAULT 3  -- 1-5, 1 being highest
        )
        """)
        
        # Master applications table - tracks all applications
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_uid TEXT UNIQUE NOT NULL,
            job_uid TEXT NOT NULL,
            
            -- Application details
            applied_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            application_method TEXT,  -- email, portal, linkedin, api
            resume_version TEXT,
            cover_letter_version TEXT,
            
            -- Submission details
            submitted_to_email TEXT,
            submitted_to_portal TEXT,
            confirmation_number TEXT,
            
            -- Documents
            resume_content TEXT,
            cover_letter_content TEXT,
            portfolio_links TEXT,  -- JSON array
            
            -- Response tracking
            response_received BOOLEAN DEFAULT 0,
            response_date DATETIME,
            response_type TEXT,  -- rejection, interview, offer, ghost
            response_content TEXT,
            
            -- Interview tracking
            interview_scheduled BOOLEAN DEFAULT 0,
            interview_dates TEXT,  -- JSON array
            interview_rounds INTEGER DEFAULT 0,
            interview_notes TEXT,
            
            -- Outcome
            outcome TEXT,  -- pending, rejected, withdrawn, offer, accepted
            offer_amount INTEGER,
            rejection_reason TEXT,
            
            -- Analytics
            days_to_response INTEGER,
            follow_ups_sent INTEGER DEFAULT 0,
            last_follow_up DATETIME,
            
            -- Source system
            source_system TEXT,  -- ai-talent-optimizer, survive, manual
            original_id TEXT,  -- ID in source system
            
            FOREIGN KEY (job_uid) REFERENCES master_jobs(job_uid)
        )
        """)
        
        # Company intelligence table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT UNIQUE NOT NULL,
            
            -- Company details
            website TEXT,
            linkedin_url TEXT,
            careers_page TEXT,
            
            -- Size and stage
            employee_count INTEGER,
            funding_stage TEXT,
            total_funding INTEGER,
            valuation INTEGER,
            
            -- Culture and benefits
            glassdoor_rating FLOAT,
            culture_score FLOAT,
            benefits_score FLOAT,
            work_life_balance FLOAT,
            
            -- Hiring intelligence
            hiring_velocity TEXT,  -- slow, moderate, fast
            typical_process TEXT,
            average_response_days INTEGER,
            interview_difficulty TEXT,
            
            -- Key people
            recruiters TEXT,  -- JSON array
            hiring_managers TEXT,  -- JSON array
            executives TEXT,  -- JSON array
            
            -- Application history
            total_applications INTEGER DEFAULT 0,
            total_responses INTEGER DEFAULT 0,
            total_interviews INTEGER DEFAULT 0,
            total_offers INTEGER DEFAULT 0,
            
            -- Penalty system
            penalty_score FLOAT DEFAULT 0,
            cooldown_until DATETIME,
            max_applications INTEGER DEFAULT 3,
            
            -- Notes
            notes TEXT,
            tags TEXT,  -- JSON array
            
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Email tracking table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_uid TEXT UNIQUE NOT NULL,
            
            -- Email details
            direction TEXT NOT NULL,  -- incoming, outgoing
            email_from TEXT,
            email_to TEXT,
            cc TEXT,
            bcc TEXT,
            
            -- Content
            subject TEXT,
            body TEXT,
            attachments TEXT,  -- JSON array
            
            -- Classification
            is_job_related BOOLEAN DEFAULT 0,
            company TEXT,
            job_uid TEXT,
            application_uid TEXT,
            
            -- Response analysis
            sentiment FLOAT,  -- -1 to 1
            urgency TEXT,  -- low, medium, high
            action_required BOOLEAN DEFAULT 0,
            action_type TEXT,  -- schedule_interview, provide_info, etc.
            
            -- Tracking
            gmail_message_id TEXT,
            thread_id TEXT,
            sent_date DATETIME,
            received_date DATETIME,
            read_date DATETIME,
            
            -- Status
            processed BOOLEAN DEFAULT 0,
            archived BOOLEAN DEFAULT 0,
            starred BOOLEAN DEFAULT 0,
            
            FOREIGN KEY (job_uid) REFERENCES master_jobs(job_uid),
            FOREIGN KEY (application_uid) REFERENCES master_applications(application_uid)
        )
        """)
        
        # Performance metrics table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_date DATE DEFAULT CURRENT_DATE,
            
            -- Daily metrics
            jobs_discovered INTEGER DEFAULT 0,
            applications_sent INTEGER DEFAULT 0,
            responses_received INTEGER DEFAULT 0,
            interviews_scheduled INTEGER DEFAULT 0,
            
            -- Quality metrics
            average_match_score FLOAT,
            average_response_time FLOAT,
            response_rate FLOAT,
            interview_rate FLOAT,
            
            -- System performance
            automation_success_rate FLOAT,
            email_delivery_rate FLOAT,
            scraping_success_rate FLOAT,
            ml_accuracy FLOAT,
            
            -- Cumulative metrics
            total_jobs_in_db INTEGER,
            total_applications INTEGER,
            total_responses INTEGER,
            total_interviews INTEGER,
            total_offers INTEGER
        )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON master_jobs(company)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_applied ON master_jobs(applied)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_score ON master_jobs(ml_score DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_apps_job ON master_applications(job_uid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_apps_response ON master_applications(response_received)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_company ON email_tracking(company)")
        
        self.conn.commit()
        
    def import_ai_talent_optimizer_jobs(self, db_path: str):
        """Import jobs from AI Talent Optimizer database"""
        source_conn = sqlite3.connect(db_path)
        cursor = source_conn.cursor()
        
        # Import from unified_jobs table
        cursor.execute("""
        SELECT job_id, company, title, location, remote_option,
               salary_range, url, description, source, discovered_date,
               relevance_score, applied, applied_date, company_email
        FROM jobs
        """)
        
        jobs = cursor.fetchall()
        imported = 0
        
        for job in jobs:
            job_uid = self._generate_job_uid(job[1], job[2], job[9])
            
            try:
                self.conn.execute("""
                INSERT INTO jobs (
                    job_uid, company, title, location, remote_type,
                    url, description, source, discovered_date,
                    ml_score, applied, applied_date, source_job_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_uid, job[1], job[2], job[3], job[4],
                    job[6], job[7], job[8] or 'ai-talent-optimizer', job[9],
                    job[10], job[11], job[12], job[0]
                ))
                imported += 1
            except sqlite3.IntegrityError:
                # Job already exists
                pass
                
        source_conn.close()
        self.conn.commit()
        return imported
        
    def import_survive_applications(self, csv_path: str):
        """Import applications from SURVIVE CSV tracker"""
        import csv
        
        imported = 0
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Generate job UID
                job_uid = self._generate_job_uid(
                    row.get('Company', ''),
                    row.get('Position', ''),
                    row.get('Date Applied', '')
                )
                
                # Insert job if not exists
                self.conn.execute("""
                INSERT OR IGNORE INTO master_jobs (
                    job_uid, company, title, location,
                    url, applied, applied_date, source
                ) VALUES (?, ?, ?, ?, ?, 1, ?, 'survive')
                """, (
                    job_uid,
                    row.get('Company', ''),
                    row.get('Position', ''),
                    row.get('Location', ''),
                    row.get('URL', ''),
                    row.get('Date Applied', ''),
                ))
                
                # Insert application
                app_uid = self._generate_app_uid(job_uid, row.get('Date Applied', ''))
                
                try:
                    self.conn.execute("""
                    INSERT INTO applications (
                        application_uid, job_uid, applied_date,
                        method, source_system
                    ) VALUES (?, ?, ?, ?, 'survive')
                    """, (
                        app_uid, job_uid, row.get('Date Applied', ''),
                        row.get('Method', 'unknown')
                    ))
                    imported += 1
                except sqlite3.IntegrityError:
                    pass
                    
        self.conn.commit()
        return imported
        
    def import_linkedin_jobs(self, db_path: str):
        """Import jobs from LinkedIn scraper database"""
        source_conn = sqlite3.connect(db_path)
        cursor = source_conn.cursor()
        
        cursor.execute("""
        SELECT job_id, company, title, location, remote_option,
               posted_date, hours_ago, url, description, salary_range,
               applied, applied_date
        FROM jobs
        """)
        
        jobs = cursor.fetchall()
        imported = 0
        
        for job in jobs:
            job_uid = self._generate_job_uid(job[1], job[2], job[5])
            
            try:
                self.conn.execute("""
                INSERT INTO jobs (
                    job_uid, company, title, location, remote_type,
                    posted_date, url, description, source,
                    applied, applied_date, source_job_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'linkedin', ?, ?, ?)
                """, (
                    job_uid, job[1], job[2], job[3], job[4],
                    job[5], job[7], job[8],
                    job[10], job[11], job[0]
                ))
                imported += 1
            except sqlite3.IntegrityError:
                pass
                
        source_conn.close()
        self.conn.commit()
        return imported
        
    def _generate_job_uid(self, company: str, position: str, date: str) -> str:
        """Generate unique job identifier"""
        content = f"{company}_{position}_{date}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
        
    def _generate_app_uid(self, job_uid: str, date: str) -> str:
        """Generate unique application identifier"""
        content = f"{job_uid}_{date}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
        
    def get_stats(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total jobs
        cursor.execute("SELECT COUNT(*) FROM jobs")
        stats['total_jobs'] = cursor.fetchone()[0]
        
        # Jobs by source
        cursor.execute("""
        SELECT source, COUNT(*) 
        FROM jobs 
        GROUP BY source
        """)
        stats['jobs_by_source'] = dict(cursor.fetchall())
        
        # Applications
        cursor.execute("SELECT COUNT(*) FROM applications")
        stats['total_applications'] = cursor.fetchone()[0]
        
        # Response rate
        cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN response_received = 1 THEN 1 ELSE 0 END) as responses
        FROM applications
        """)
        result = cursor.fetchone()
        if result[0] > 0:
            stats['response_rate'] = f"{(result[1]/result[0]*100):.1f}%"
        else:
            stats['response_rate'] = "0%"
            
        # Top companies
        cursor.execute("""
        SELECT company, COUNT(*) as count
        FROM jobs
        GROUP BY company
        ORDER BY count DESC
        LIMIT 10
        """)
        stats['top_companies'] = cursor.fetchall()
        
        return stats
        
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Initialize and populate master database"""
    print("🚀 Initializing Master Database for Unified Career System")
    print("=" * 60)
    
    db = MasterDatabase("unified_platform.db")
    
    # Import from AI Talent Optimizer
    if Path("unified_platform.db").exists():
        imported = db.import_ai_talent_optimizer_jobs("unified_platform.db")
        print(f"✅ Imported {imported} jobs from AI Talent Optimizer")
    
    # Import from LinkedIn scraper
    if Path("unified_platform.db").exists():
        imported = db.import_linkedin_jobs("unified_platform.db")
        print(f"✅ Imported {imported} jobs from LinkedIn scraper")
    
    # Import from SURVIVE (if CSV exists)
    survive_csv = Path("/Users/matthewscott/SURVIVE/career-automation/real-tracker/UPDATED_REAL_JOB_TRACKER_JULY_2025.csv")
    if survive_csv.exists():
        imported = db.import_survive_applications(str(survive_csv))
        print(f"✅ Imported {imported} applications from SURVIVE tracker")
    
    # Show statistics
    stats = db.get_stats()
    print("\n📊 Master Database Statistics:")
    print(f"Total Jobs: {stats['total_jobs']}")
    print(f"Total Applications: {stats['total_applications']}")
    print(f"Response Rate: {stats['response_rate']}")
    
    print("\n📍 Jobs by Source:")
    for source, count in stats['jobs_by_source'].items():
        print(f"  • {source}: {count}")
    
    if stats['top_companies']:
        print("\n🏢 Top Companies:")
        for company, count in stats['top_companies'][:5]:
            print(f"  • {company}: {count} jobs")
    
    db.close()
    print("\n✨ Master database initialized successfully!")
    
if __name__ == "__main__":
    main()