#!/usr/bin/env python3
"""
AI Talent Optimizer - Database Consolidation Script
==================================================

Consolidates 7 databases (356+ records) into 1 unified authoritative source.
This script safely migrates all data while preserving relationships and avoiding duplicates.
"""

import sqlite3
import os
import shutil
import json
import logging
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseConsolidator:
    def __init__(self):
        self.source_databases = [
            "unified_platform.db",
            "unified_platform.db", 
            "unified_platform.db",
            "unified_platform.db",
            "unified_platform.db",
            "unified_platform.db",
            "unified_platform.db"
        ]
        
        self.target_db = "unified_platform.db"
        self.backup_dir = f'database_backups_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        self.migration_log = []
        
    def consolidate_all(self):
        """Main consolidation process."""
        logger.info("Starting database consolidation process...")
        
        # Phase 1: Preparation
        self._create_backups()
        self._create_unified_database()
        
        # Phase 2: Data Migration
        self._migrate_profile_data()
        self._migrate_job_data()
        self._migrate_application_data()
        self._migrate_response_data()
        self._migrate_contact_data()
        self._migrate_metrics_data()
        
        # Phase 3: Validation
        validation_results = self._validate_migration()
        
        # Phase 4: Generate Report
        self._generate_migration_report(validation_results)
        
        logger.info("Database consolidation complete!")
        return validation_results
    
    def _create_backups(self):
        """Create backups of all existing databases."""
        logger.info("Creating backups of existing databases...")
        
        os.makedirs(self.backup_dir, exist_ok=True)
        
        for db_file in self.source_databases:
            if os.path.exists(db_file):
                backup_path = os.path.join(self.backup_dir, db_file)
                shutil.copy2(db_file, backup_path)
                logger.info(f"Backed up {db_file} to {backup_path}")
            else:
                logger.warning(f"Source database not found: {db_file}")
    
    def _create_unified_database(self):
        """Create the new unified database with proper schema."""
        logger.info(f"Creating unified database: {self.target_db}")
        
        if os.path.exists(self.target_db):
            os.remove(self.target_db)
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        # Create tables with unified schema
        self._create_jobs_table(cursor)
        self._create_applications_table(cursor)
        self._create_responses_table(cursor)
        self._create_profile_table(cursor)
        self._create_contacts_table(cursor)
        self._create_metrics_table(cursor)
        
        # Create indexes for performance
        self._create_indexes(cursor)
        
        conn.commit()
        conn.close()
        
        logger.info("Unified database schema created successfully")
    
    def _create_jobs_table(self, cursor):
        """Create unified jobs table."""
        cursor.execute('''
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                location TEXT,
                remote BOOLEAN DEFAULT 0,
                min_salary INTEGER,
                max_salary INTEGER,
                salary_range TEXT,
                description TEXT,
                requirements TEXT,
                url TEXT,
                source TEXT,
                discovered_date TIMESTAMP,
                relevance_score REAL,
                priority_score REAL,
                healthcare_focused BOOLEAN DEFAULT 0,
                ai_focused BOOLEAN DEFAULT 1,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(company, title)
            )
        ''')
        
    def _create_applications_table(self, cursor):
        """Create unified applications table."""
        cursor.execute('''
            CREATE TABLE applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                applied_date TIMESTAMP,
                application_method TEXT,
                resume_version TEXT,
                cover_letter_version TEXT,
                email_sent BOOLEAN DEFAULT 0,
                email_address TEXT,
                status TEXT DEFAULT 'sent',
                ats_score REAL,
                tracking_id TEXT,
                notes TEXT,
                response_received BOOLEAN DEFAULT 0,
                response_date TIMESTAMP,
                response_type TEXT,
                interview_scheduled BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        ''')
    
    def _create_responses_table(self, cursor):
        """Create unified responses table."""
        cursor.execute('''
            CREATE TABLE responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                company TEXT,
                email_id TEXT UNIQUE,
                from_email TEXT,
                subject TEXT,
                received_date TIMESTAMP,
                response_type TEXT,
                email_content TEXT,
                action_required BOOLEAN DEFAULT 0,
                action_taken TEXT,
                interview_scheduled BOOLEAN DEFAULT 0,
                processed_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
    
    def _create_profile_table(self, cursor):
        """Create unified profile table."""
        cursor.execute('''
            CREATE TABLE profile (
                id INTEGER PRIMARY KEY,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                linkedin TEXT,
                github TEXT,
                location TEXT,
                years_experience INTEGER,
                current_focus TEXT,
                target_salary_min INTEGER DEFAULT 400000,
                total_applications INTEGER DEFAULT 0,
                total_responses INTEGER DEFAULT 0,
                total_interviews INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _create_contacts_table(self, cursor):
        """Create unified contacts table."""
        cursor.execute('''
            CREATE TABLE contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                name TEXT,
                title TEXT,
                email TEXT,
                linkedin TEXT,
                phone TEXT,
                contacted BOOLEAN DEFAULT 0,
                contacted_at TIMESTAMP,
                response_received BOOLEAN DEFAULT 0,
                meeting_scheduled BOOLEAN DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _create_metrics_table(self, cursor):
        """Create unified metrics table."""
        cursor.execute('''
            CREATE TABLE metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT UNIQUE,
                metric_value TEXT,
                verification_method TEXT,
                verified_at TIMESTAMP,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _create_indexes(self, cursor):
        """Create performance indexes."""
        indexes = [
            "CREATE INDEX idx_jobs_company ON jobs(company)",
            "CREATE INDEX idx_jobs_position ON jobs(title)",
            "CREATE INDEX idx_jobs_salary ON jobs(salary_min, salary_max)",
            "CREATE INDEX idx_applications_company ON applications(company)",
            "CREATE INDEX idx_applications_date ON applications(applied_date)",
            "CREATE INDEX idx_responses_date ON responses(received_date)",
            "CREATE INDEX idx_responses_type ON responses(response_type)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def _migrate_job_data(self):
        """Migrate all job data from source databases."""
        logger.info("Migrating job data...")
        
        target_conn = sqlite3.connect(self.target_db)
        target_cursor = target_conn.cursor()
        
        jobs_migrated = 0
        
        # Migrate from UNIFIED_AI_JOBS.db - job_discoveries table
        if os.path.exists("unified_platform.db"):
            source_conn = sqlite3.connect("unified_platform.db")
            source_cursor = source_conn.cursor()
            
            source_cursor.execute('''
                SELECT DISTINCT company, title, location, 
                       CASE WHEN remote_option='Yes' THEN 1 ELSE 0 END as remote_type,
                       CASE WHEN salary_range LIKE '%-%' THEN 
                           CAST(SUBSTR(salary_range, 1, INSTR(salary_range, '-')-1) AS INTEGER)
                       ELSE NULL END as min_sal,
                       CASE WHEN salary_range LIKE '%-%' THEN 
                           CAST(SUBSTR(salary_range, INSTR(salary_range, '-')+1) AS INTEGER)
                       ELSE NULL END as max_sal,
                       salary_range, description, url, source, discovered_date,
                       relevance_score, job_id, created_at
                FROM jobs 
                WHERE company IS NOT NULL AND position IS NOT NULL
            ''')
            
            for row in source_cursor.fetchall():
                try:
                    # Create unique job_id if missing
                    job_id = row[11] if row[11] else f"{row[0]}_{row[1]}_{hash(f'{row[0]}{row[1]}') % 10000}"
                    
                    target_cursor.execute('''
                        INSERT OR IGNORE INTO jobs (
                            job_id, company, title, location, remote_type, 
                            salary_min, salary_max, salary_range, description, 
                            url, source, discovered_date, relevance_score, discovered_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (job_id, row[0], row[1], row[2], row[3], row[4], row[5], 
                          row[6], row[7], row[8], row[9], row[10], row[11], row[12]))
                    
                    if target_cursor.rowcount > 0:
                        jobs_migrated += 1
                        
                except Exception as e:
                    logger.warning(f"Error migrating job {row[0]} - {row[1]}: {e}")
            
            source_conn.close()
        
        # Migrate from principal_jobs_400k.db
        if os.path.exists("unified_platform.db"):
            source_conn = sqlite3.connect("unified_platform.db")
            source_cursor = source_conn.cursor()
            
            source_cursor.execute('SELECT * FROM jobs')
            for row in source_cursor.fetchall():
                job_id = f"principal_{row[1]}_{row[2]}_{row[0]}"
                
                try:
                    target_cursor.execute('''
                        INSERT OR IGNORE INTO jobs (
                            job_id, company, title, url, salary_min, salary_max,
                            location, remote_type, healthcare_focused, ai_focused,
                            discovered_date, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'high_priority')
                    ''', (job_id, row[1], row[2], row[3], row[4], row[5], 
                          row[6], row[7], row[8], row[9], row[10]))
                    
                    if target_cursor.rowcount > 0:
                        jobs_migrated += 1
                        
                except Exception as e:
                    logger.warning(f"Error migrating principal job {row[1]} - {row[2]}: {e}")
            
            source_conn.close()
        
        # Migrate from other databases with job data
        for db_file in ["unified_platform.db", "unified_platform.db"]:
            if os.path.exists(db_file):
                jobs_migrated += self._migrate_jobs_from_db(db_file, target_cursor)
        
        target_conn.commit()
        target_conn.close()
        
        self.migration_log.append(f"Migrated {jobs_migrated} unique jobs")
        logger.info(f"Migrated {jobs_migrated} unique jobs")
    
    def _migrate_jobs_from_db(self, db_file, target_cursor):
        """Helper to migrate jobs from a specific database."""
        migrated = 0
        
        try:
            source_conn = sqlite3.connect(db_file)
            source_cursor = source_conn.cursor()
            
            if db_file == "unified_platform.db":
                source_cursor.execute('''
                    SELECT DISTINCT company, title, description, url, 
                           salary_range, location, relevance_score, discovered_date, source
                    FROM jobs
                    WHERE company IS NOT NULL AND position IS NOT NULL
                ''')
                
                for row in source_cursor.fetchall():
                    job_id = f"jobapp_{row[0]}_{row[1]}_{hash(f'{row[0]}{row[1]}') % 10000}"
                    
                    try:
                        target_cursor.execute('''
                            INSERT OR IGNORE INTO jobs (
                                job_id, company, title, description, url,
                                salary_range, location, relevance_score, 
                                discovered_date, source
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (job_id, row[0], row[1], row[2], row[3], 
                              row[4], row[5], row[6], row[7], row[8]))
                        
                        if target_cursor.rowcount > 0:
                            migrated += 1
                            
                    except Exception as e:
                        logger.warning(f"Error migrating job from {db_file}: {e}")
            
            elif db_file == "unified_platform.db":
                source_cursor.execute('SELECT * FROM jobs')
                for row in source_cursor.fetchall():
                    job_id = f"ai_opt_{row[1]}_{row[2]}_{row[0]}"
                    
                    try:
                        target_cursor.execute('''
                            INSERT OR IGNORE INTO jobs (
                                job_id, company, title, location, remote_type,
                                salary_min, salary_max, description, requirements,
                                source, source_url, discovered_date, priority_score, status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (job_id, row[1], row[2], row[3], row[4], 
                              row[5], row[6], row[7], row[8], row[9], 
                              row[10], row[12], row[13], row[14]))
                        
                        if target_cursor.rowcount > 0:
                            migrated += 1
                            
                    except Exception as e:
                        logger.warning(f"Error migrating job from {db_file}: {e}")
            
            source_conn.close()
            
        except Exception as e:
            logger.error(f"Error accessing {db_file}: {e}")
        
        return migrated
    
    def _migrate_application_data(self):
        """Migrate all application data."""
        logger.info("Migrating application data...")
        
        target_conn = sqlite3.connect(self.target_db)
        target_cursor = target_conn.cursor()
        
        apps_migrated = 0
        
        # Migrate from principal_jobs_400k.db (applications that were marked as applied)
        if os.path.exists("unified_platform.db"):
            source_conn = sqlite3.connect("unified_platform.db")
            source_cursor = source_conn.cursor()
            
            source_cursor.execute('''
                SELECT company, title, applied_at, response_received, offer_received, notes
                FROM jobs 
                WHERE applied = 1
            ''')
            
            for row in source_cursor.fetchall():
                try:
                    # Find matching job
                    target_cursor.execute('''
                        SELECT id FROM jobs WHERE company = ? AND title = ?
                    ''', (row[0], row[1]))
                    
                    job_result = target_cursor.fetchone()
                    job_id = job_result[0] if job_result else None
                    
                    target_cursor.execute('''
                        INSERT OR IGNORE INTO applications (
                            job_id, company, title, applied_date, 
                            response_received, status, notes
                        ) VALUES (?, ?, ?, ?, ?, 'sent', ?)
                    ''', (job_id, row[0], row[1], row[2], row[3], row[5]))
                    
                    if target_cursor.rowcount > 0:
                        apps_migrated += 1
                        
                except Exception as e:
                    logger.warning(f"Error migrating application {row[0]} - {row[1]}: {e}")
            
            source_conn.close()
        
        # Migrate from ai_talent_optimizer.db
        if os.path.exists("unified_platform.db"):
            source_conn = sqlite3.connect("unified_platform.db")
            source_cursor = source_conn.cursor()
            
            source_cursor.execute('SELECT * FROM applications')
            for row in source_cursor.fetchall():
                try:
                    target_cursor.execute('''
                        INSERT OR IGNORE INTO applications (
                            job_id, applied_date, resume_version, cover_letter_version,
                            status, email_address, method, status,
                            response_date, notes, ats_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (row[1], row[2], row[3], row[4], row[5], row[6], 
                          row[7], row[8], row[9], row[10], row[11]))
                    
                    if target_cursor.rowcount > 0:
                        apps_migrated += 1
                        
                except Exception as e:
                    logger.warning(f"Error migrating application from ai_talent_optimizer: {e}")
            
            source_conn.close()
        
        target_conn.commit()
        target_conn.close()
        
        self.migration_log.append(f"Migrated {apps_migrated} applications")
        logger.info(f"Migrated {apps_migrated} applications")
    
    def _migrate_response_data(self):
        """Migrate all response data."""
        logger.info("Migrating response data...")
        
        target_conn = sqlite3.connect(self.target_db)
        target_cursor = target_conn.cursor()
        
        responses_migrated = 0
        
        # Migrate from UNIFIED_AI_JOBS.db - gmail_responses
        if os.path.exists("unified_platform.db"):
            source_conn = sqlite3.connect("unified_platform.db")
            source_cursor = source_conn.cursor()
            
            source_cursor.execute('SELECT * FROM emails')
            for row in source_cursor.fetchall():
                try:
                    target_cursor.execute('''
                        INSERT OR IGNORE INTO responses (
                            email_id, company, subject, from_email, 
                            received_date, response_type, processed_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
                    
                    if target_cursor.rowcount > 0:
                        responses_migrated += 1
                        
                except Exception as e:
                    logger.warning(f"Error migrating response: {e}")
            
            source_conn.close()
        
        target_conn.commit()
        target_conn.close()
        
        self.migration_log.append(f"Migrated {responses_migrated} responses")
        logger.info(f"Migrated {responses_migrated} responses")
    
    def _migrate_profile_data(self):
        """Migrate profile data."""
        logger.info("Migrating profile data...")
        
        target_conn = sqlite3.connect(self.target_db)
        target_cursor = target_conn.cursor()
        
        # Migrate from your_profile.db
        if os.path.exists("unified_platform.db"):
            source_conn = sqlite3.connect("unified_platform.db")
            source_cursor = source_conn.cursor()
            
            # Get main profile data
            source_cursor.execute('SELECT * FROM profile LIMIT 1')
            profile_row = source_cursor.fetchone()
            
            if profile_row:
                try:
                    target_cursor.execute('''
                        INSERT INTO profile (
                            full_name, email, phone, linkedin, github, 
                            location, years_experience, current_focus, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', profile_row[1:])
                    
                    self.migration_log.append("Migrated profile data")
                    
                except Exception as e:
                    logger.error(f"Error migrating profile: {e}")
            
            source_conn.close()
        
        # Also check ai_talent_optimizer.db for profile data
        if os.path.exists("unified_platform.db"):
            source_conn = sqlite3.connect("unified_platform.db")
            source_cursor = source_conn.cursor()
            
            source_cursor.execute('SELECT * FROM profile LIMIT 1')
            profile_row = source_cursor.fetchone()
            
            if profile_row:
                # Update profile if it exists, or insert if no profile yet
                try:
                    target_cursor.execute('''
                        INSERT OR REPLACE INTO profile (
                            id, full_name, email, phone, linkedin, github,
                            location, years_experience, target_salary_min,
                            total_applications, total_responses, total_interviews, updated_at
                        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (profile_row[1], profile_row[2], profile_row[3], 
                          profile_row[4], profile_row[5], profile_row[7], 
                          profile_row[12], profile_row[13], profile_row[14], 
                          profile_row[15], profile_row[16], datetime.now()))
                    
                except Exception as e:
                    logger.warning(f"Error updating profile from ai_talent_optimizer: {e}")
            
            source_conn.close()
        
        target_conn.commit()
        target_conn.close()
        
        logger.info("Profile data migrated")
    
    def _migrate_contact_data(self):
        """Migrate contact data."""
        logger.info("Migrating contact data...")
        
        target_conn = sqlite3.connect(self.target_db)
        target_cursor = target_conn.cursor()
        
        # CEO outreach database is empty, but we'll handle it for completeness
        if os.path.exists("unified_platform.db"):
            source_conn = sqlite3.connect("unified_platform.db")
            source_cursor = source_conn.cursor()
            
            try:
                source_cursor.execute('SELECT * FROM contacts')
                for row in source_cursor.fetchall():
                    target_cursor.execute('''
                        INSERT INTO contacts (
                            company, full_name, title, email, linkedin, phone,
                            contacted, contacted_at, response_received, notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (row[1], row[2], row[3], row[4], row[5], row[6],
                          row[11], row[12], row[13], row[18]))
                
            except Exception as e:
                logger.warning(f"Error migrating contacts: {e}")
            
            source_conn.close()
        
        target_conn.commit()
        target_conn.close()
        
        logger.info("Contact data migrated")
    
    def _migrate_metrics_data(self):
        """Migrate metrics data."""
        logger.info("Migrating metrics data...")
        
        target_conn = sqlite3.connect(self.target_db)
        target_cursor = target_conn.cursor()
        
        metrics_migrated = 0
        
        if os.path.exists("unified_platform.db"):
            source_conn = sqlite3.connect("unified_platform.db")
            source_cursor = source_conn.cursor()
            
            source_cursor.execute('SELECT * FROM metrics')
            for row in source_cursor.fetchall():
                try:
                    target_cursor.execute('''
                        INSERT OR IGNORE INTO metrics (
                            metric_name, metric_value, verification_method,
                            verified_at, expires_at
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (row[0], row[1], row[2], row[4], row[5]))
                    
                    if target_cursor.rowcount > 0:
                        metrics_migrated += 1
                        
                except Exception as e:
                    logger.warning(f"Error migrating metric {row[0]}: {e}")
            
            source_conn.close()
        
        # Also migrate platform metrics from your_profile.db
        if os.path.exists("unified_platform.db"):
            source_conn = sqlite3.connect("unified_platform.db")
            source_cursor = source_conn.cursor()
            
            source_cursor.execute('SELECT * FROM metrics')
            for row in source_cursor.fetchall():
                try:
                    target_cursor.execute('''
                        INSERT OR IGNORE INTO metrics (
                            metric_name, metric_value, verification_method, verified_at
                        ) VALUES (?, ?, 'manual_verification', ?)
                    ''', (row[0], row[1], row[3]))
                    
                    if target_cursor.rowcount > 0:
                        metrics_migrated += 1
                        
                except Exception as e:
                    logger.warning(f"Error migrating platform metric {row[0]}: {e}")
            
            source_conn.close()
        
        target_conn.commit()
        target_conn.close()
        
        self.migration_log.append(f"Migrated {metrics_migrated} metrics")
        logger.info(f"Migrated {metrics_migrated} metrics")
    
    def _validate_migration(self):
        """Validate that migration was successful."""
        logger.info("Validating migration...")
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        validation = {
            "jobs": cursor.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],
            "applications": cursor.execute("SELECT COUNT(*) FROM applications").fetchone()[0],
            "responses": cursor.execute("SELECT COUNT(*) FROM emails").fetchone()[0],
            "profile": cursor.execute("SELECT COUNT(*) FROM profile").fetchone()[0],
            "contacts": cursor.execute("SELECT COUNT(*) FROM contacts").fetchone()[0],
            "metrics": cursor.execute("SELECT COUNT(*) FROM metrics").fetchone()[0],
            "total_unified": 0
        }
        
        validation["total_unified"] = sum(validation.values()) - validation["profile"]
        
        # Check for duplicates
        cursor.execute('''
            SELECT company, title, COUNT(*) as cnt 
            FROM jobs 
            GROUP BY company, position 
            HAVING COUNT(*) > 1
        ''')
        
        duplicates = cursor.fetchall()
        validation["duplicate_jobs"] = len(duplicates)
        
        # Check foreign key relationships
        cursor.execute('''
            SELECT COUNT(*) 
            FROM applications a 
            LEFT JOIN jobs j ON a.job_id = j.id 
            WHERE a.job_id IS NOT NULL AND j.id IS NULL
        ''')
        
        validation["orphaned_applications"] = cursor.fetchone()[0]
        
        conn.close()
        
        return validation
    
    def _generate_migration_report(self, validation_results):
        """Generate final migration report."""
        report = {
            "migration_timestamp": datetime.now().isoformat(),
            "source_databases": self.source_databases,
            "target_database": self.target_db,
            "backup_directory": self.backup_dir,
            "migration_log": self.migration_log,
            "validation_results": validation_results,
            "success": validation_results["duplicate_jobs"] == 0 and validation_results["orphaned_applications"] == 0
        }
        
        with open('database_migration_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Migration report saved to: database_migration_report.json")
        
        return report

def main():
    """Run the database consolidation."""
    consolidator = DatabaseConsolidator()
    
    try:
        validation_results = consolidator.consolidate_all()
        
        print("\n=== DATABASE CONSOLIDATION COMPLETE ===")
        print(f"Target Database: {consolidator.target_db}")
        print(f"Backup Directory: {consolidator.backup_dir}")
        print("\nRecord Counts in Unified Database:")
        print(f"  Jobs: {validation_results['jobs']}")
        print(f"  Applications: {validation_results['applications']}")
        print(f"  Responses: {validation_results['responses']}")
        print(f"  Profile: {validation_results['profile']}")
        print(f"  Contacts: {validation_results['contacts']}")
        print(f"  Metrics: {validation_results['metrics']}")
        print(f"  TOTAL: {validation_results['total_unified']}")
        
        print("\nData Quality:")
        print(f"  Duplicate Jobs: {validation_results['duplicate_jobs']}")
        print(f"  Orphaned Applications: {validation_results['orphaned_applications']}")
        
        if validation_results['duplicate_jobs'] == 0 and validation_results['orphaned_applications'] == 0:
            print("\n✅ MIGRATION SUCCESSFUL - No data integrity issues detected")
        else:
            print("\n⚠️  MIGRATION COMPLETED WITH WARNINGS - Check migration report")
        
        print(f"\nDetailed report saved to: database_migration_report.json")
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return None

if __name__ == "__main__":
    main()