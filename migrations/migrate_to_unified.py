#!/usr/bin/env python3
"""
Migration script to consolidate multiple databases into unified schema.
Preserves all existing data while eliminating duplicates.
"""

import sqlite3
from pathlib import Path
import sys
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.database import DatabaseManager, Job, Application, Response

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class DataMigrator:
    """Migrate data from old databases to new unified schema."""
    
    def __init__(self):
        """Initialize migrator."""
        self.new_db = DatabaseManager("sqlite:///data/unified_jobs.db")
        self.migrated_jobs = set()
        self.stats = {
            'jobs_migrated': 0,
            'applications_migrated': 0,
            'duplicates_skipped': 0,
            'errors': 0
        }
    
    def migrate_all(self):
        """Run complete migration."""
        logger.info("Starting data migration to unified database")
        logger.info("=" * 60)
        
        # Find all database files
        db_files = [
            "unified_platform.db",
            "unified_platform.db",
            "unified_platform.db",
            "unified_platform.db",
            "unified_platform.db",
            "unified_platform.db",
            "unified_platform.db"
        ]
        
        for db_file in db_files:
            if Path(db_file).exists():
                logger.info(f"\nMigrating from {db_file}...")
                self.migrate_database(db_file)
            else:
                logger.info(f"Skipping {db_file} (not found)")
        
        # Show final statistics
        logger.info("\n" + "=" * 60)
        logger.info("Migration Complete!")
        logger.info(f"  Jobs migrated: {self.stats['jobs_migrated']}")
        logger.info(f"  Applications migrated: {self.stats['applications_migrated']}")
        logger.info(f"  Duplicates skipped: {self.stats['duplicates_skipped']}")
        logger.info(f"  Errors: {self.stats['errors']}")
    
    def migrate_database(self, db_path: str):
        """Migrate data from a single database."""
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Migrate job-related tables
            if 'job_discoveries' in tables:
                self.migrate_job_discoveries(cursor)
            elif 'jobs' in tables:
                self.migrate_jobs_table(cursor)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error migrating {db_path}: {e}")
            self.stats['errors'] += 1
    
    def migrate_job_discoveries(self, cursor):
        """Migrate FROM jobs table format."""
        cursor.execute("SELECT * FROM jobs")
        rows = cursor.fetchall()
        
        session = self.new_db.get_session()
        
        for row in rows:
            try:
                # Create unique job ID
                job_id = f"{row['company']}_{row['position']}".replace(' ', '_').lower()
                
                # Skip if already migrated
                if job_id in self.migrated_jobs:
                    self.stats['duplicates_skipped'] += 1
                    continue
                
                # Check if job exists
                existing = session.query(Job).filter_by(job_id=job_id).first()
                if existing:
                    # Update existing job
                    self._update_job(existing, row)
                else:
                    # Create new job
                    job = Job(
                        job_id=job_id,
                        company=row['company'],
                        title=row['position'],
                        location=row.get('location'),
                        remote_option=row.get('remote_option'),
                        salary_range=row.get('salary_range'),
                        url=row.get('url') or row.get('application_url'),
                        description=row.get('description'),
                        source=row.get('source', 'legacy'),
                        discovered_date=self._parse_date(row.get('discovered_date')),
                        relevance_score=float(row.get('relevance_score', 0)),
                        applied=bool(row.get('applied', 0)),
                        applied_date=self._parse_date(row.get('applied_date')),
                        method=row.get('application_method'),
                        company_email=row.get('actual_email_used') or row.get('verified_email'),
                        email_verified=bool(row.get('email_verified', 0)),
                        bounce_detected=bool(row.get('bounce_detected', 0)),
                        bounce_reason=row.get('bounce_reason'),
                        skip_reason=row.get('skip_reason'),
                        notes=row.get('notes')
                    )
                    
                    # Set status based on flags
                    if row.get('interview_scheduled'):
                        job.status = 'interview'
                    elif row.get('response_received'):
                        job.status = 'responded'
                    elif row.get('applied'):
                        job.status = 'applied'
                    else:
                        job.status = 'discovered'
                    
                    session.add(job)
                    self.stats['jobs_migrated'] += 1
                
                # Add to migrated set
                self.migrated_jobs.add(job_id)
                
                # Create application record if applied
                if row.get('applied'):
                    self._migrate_application(session, job_id, row)
                
            except Exception as e:
                logger.error(f"Error migrating job: {e}")
                self.stats['errors'] += 1
                continue
        
        session.commit()
        session.close()
    
    def migrate_jobs_table(self, cursor):
        """Migrate from generic jobs table format."""
        cursor.execute("SELECT * FROM jobs")
        rows = cursor.fetchall()
        
        session = self.new_db.get_session()
        
        for row in rows:
            try:
                # Use existing job_id or create one
                job_id = row.get('job_id') or f"{row['company']}_{row['title']}".replace(' ', '_').lower()
                
                if job_id in self.migrated_jobs:
                    self.stats['duplicates_skipped'] += 1
                    continue
                
                job = Job(
                    job_id=job_id,
                    company=row.get('company'),
                    title=row.get('title') or row.get('position'),
                    location=row.get('location'),
                    url=row.get('url'),
                    description=row.get('description'),
                    source=row.get('source', 'legacy'),
                    discovered_date=datetime.now(),
                    relevance_score=0.5,  # Default score
                    applied=False,
                    status='discovered'
                )
                
                session.add(job)
                self.migrated_jobs.add(job_id)
                self.stats['jobs_migrated'] += 1
                
            except Exception as e:
                logger.error(f"Error migrating job: {e}")
                self.stats['errors'] += 1
        
        session.commit()
        session.close()
    
    def _migrate_application(self, session, job_id: str, row):
        """Create application record from row data."""
        try:
            # Get the job from new database
            job = session.query(Job).filter_by(job_id=job_id).first()
            if not job:
                return
            
            # Check if application already exists
            existing = session.query(Application).filter_by(job_id=job.id).first()
            if existing:
                return
            
            application = Application(
                job_id=job.id,
                sent_date=self._parse_date(row.get('applied_date')) or datetime.now(),
                resume_version=row.get('resume_version', 'unknown'),
                status=bool(row.get('applied')),
                follow_up_count=int(row.get('follow_up_sent', 0)),
                last_follow_up=self._parse_date(row.get('follow_up_date'))
            )
            
            session.add(application)
            self.stats['applications_migrated'] += 1
            
        except Exception as e:
            logger.error(f"Error migrating application: {e}")
    
    def _update_job(self, job, row):
        """Update existing job with new data."""
        # Only update if new data is better
        if row.get('description') and not job.description:
            job.description = row['description']
        
        if row.get('salary_range') and not job.salary_range:
            job.salary_range = row['salary_range']
        
        if row.get('actual_email_used') and not job.company_email:
            job.company_email = row['actual_email_used']
        
        # Update status if more advanced
        if row.get('applied') and not job.applied:
            job.applied = True
            job.applied_date = self._parse_date(row.get('applied_date'))
    
    def _parse_date(self, date_str):
        """Parse date string to datetime object."""
        if not date_str:
            return None
        
        try:
            # Try common formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except:
            return None


def main():
    """Run migration."""
    # Create data directory if needed
    Path('data').mkdir(exist_ok=True)
    
    # Backup existing unified database if it exists
    unified_db = Path("unified_platform.db")
    if unified_db.exists():
        backup_path = f"data/unified_jobs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy(unified_db, backup_path)
        logger.info(f"Backed up existing database to {backup_path}")
    
    # Run migration
    migrator = DataMigrator()
    migrator.migrate_all()


if __name__ == '__main__':
    main()