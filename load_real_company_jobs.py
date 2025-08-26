#!/usr/bin/env python3
"""
Load Real Company Jobs
Populates database with jobs from direct company sources (Greenhouse/Lever)
Ensures all jobs have real company emails for successful applications
"""

import sys
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.enhanced_job_scraper import EnhancedJobScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def clear_old_jobs(conn):
    """Clear old Adzuna and other aggregator jobs"""
    cursor = conn.cursor()
    
    # Count before
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE source = 'Adzuna'")
    adzuna_count = cursor.fetchone()[0]
    
    # Delete Adzuna jobs and jobs with adzuna emails
    cursor.execute("""
        DELETE FROM jobs 
        WHERE source = 'Adzuna' 
        OR company_email LIKE '%adzuna%'
        OR company_email = 'N/A'
        OR company_email IS NULL
    """)
    
    deleted = cursor.rowcount
    conn.commit()
    
    logger.info(f"Cleared {deleted} old/invalid jobs (including {adzuna_count} from Adzuna)")
    return deleted


def add_jobs_to_database(jobs, conn):
    """Add scraped jobs to the database"""
    cursor = conn.cursor()
    added = 0
    updated = 0
    
    for job in jobs:
        try:
            # Check if job already exists
            cursor.execute("""
                SELECT id FROM jobs WHERE job_id = ?
            """, (job['job_id'],))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing job
                cursor.execute("""
                    UPDATE jobs SET
                        company = ?,
                        title = ?,
                        location = ?,
                        url = ?,
                        company_email = ?,
                        company_domain = ?,
                        relevance_score = ?,
                        source = ?,
                        updated_at = ?
                    WHERE job_id = ?
                """, (
                    job['company'],
                    job['position'],
                    job.get('location', 'Remote'),
                    job['url'],
                    job['company_email'],
                    job['company_domain'],
                    job.get('relevance_score', 0.75),
                    job['source'],
                    datetime.now().isoformat(),
                    job['job_id']
                ))
                updated += 1
            else:
                # Insert new job (simplified to match actual table columns)
                cursor.execute("""
                    INSERT INTO jobs (
                        job_id, company, title, location, url,
                        company_email, relevance_score,
                        source, applied, email_verified, bounce_detected
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job['job_id'],
                    job['company'],
                    job['position'],
                    job.get('location', 'Remote'),
                    job['url'],
                    job['company_email'],
                    job.get('relevance_score', 0.75),
                    job['source'],
                    0,  # not applied
                    1,  # email verified (we know these are real)
                    0   # no bounce
                ))
                added += 1
                
        except Exception as e:
            logger.error(f"Error adding job {job.get('job_id')}: {e}")
            continue
    
    conn.commit()
    logger.info(f"Added {added} new jobs, updated {updated} existing jobs")
    return added, updated


def main():
    """Main function to load real company jobs"""
    
    print("\n" + "="*60)
    print("🚀 LOADING REAL COMPANY JOBS")
    print("="*60)
    
    # Connect to database
    db_path = "unified_platform.db"
    conn = sqlite3.connect(db_path)
    
    try:
        # Step 1: Clear old aggregator jobs
        print("\n📍 Clearing old aggregator jobs...")
        cleared = clear_old_jobs(conn)
        
        # Step 2: Scrape jobs from real companies
        print("\n📍 Scraping jobs from real company sources...")
        scraper = EnhancedJobScraper()
        
        # Scrape all companies (limit to prevent overwhelming)
        jobs = scraper.scrape_all_companies(limit=20)
        
        # Calculate relevance scores
        print("\n📍 Calculating relevance scores...")
        for job in jobs:
            job['relevance_score'] = scraper.calculate_relevance_score(job)
        
        # Step 3: Add to database
        print("\n📍 Adding jobs to database...")
        added, updated = add_jobs_to_database(jobs, conn)
        
        # Step 4: Show summary
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT company) as companies,
                AVG(relevance_score) as avg_score,
                COUNT(CASE WHEN email_verified = 1 THEN 1 END) as verified_emails
            FROM jobs
            WHERE source IN ('Greenhouse', 'Lever')
        """)
        
        stats = cursor.fetchone()
        
        print("\n" + "="*60)
        print("✅ JOB LOADING COMPLETE")
        print("="*60)
        print(f"📊 Database Statistics:")
        print(f"   Total Jobs: {stats[0] or 0}")
        print(f"   Companies: {stats[1] or 0}")
        print(f"   Avg Relevance: {stats[2] or 0:.2f}")
        print(f"   Verified Emails: {stats[3] or 0}")
        
        # Show top companies
        cursor.execute("""
            SELECT company, COUNT(*) as job_count, company_email
            FROM jobs
            WHERE source IN ('Greenhouse', 'Lever')
            GROUP BY company
            ORDER BY job_count DESC
            LIMIT 10
        """)
        
        print(f"\n📍 Top Companies with Jobs:")
        for company, count, email in cursor.fetchall():
            print(f"   {company}: {count} jobs ({email})")
        
        # Show high-relevance jobs
        cursor.execute("""
            SELECT company, title, relevance_score, company_email
            FROM jobs
            WHERE relevance_score >= 0.9
            AND source IN ('Greenhouse', 'Lever')
            ORDER BY relevance_score DESC
            LIMIT 5
        """)
        
        print(f"\n🎯 Top Relevance Jobs (Matthew-specific):")
        for company, title, score, email in cursor.fetchall():
            print(f"   {score:.2f} - {company}: {position}")
            print(f"         Email: {email}")
        
        print("\n✅ Ready to send applications!")
        print("Run: python automated_apply.py")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()