#!/usr/bin/env python3
"""
Database Migration and Consolidation Tool
==========================================
Migrates data from 19 fragmented databases into a single unified platform database.
Includes intelligent deduplication and schema mapping.
"""

import sqlite3
import json
import hashlib
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self, target_db: str = 'unified_platform.db'):
        self.target_db = target_db
        self.source_databases = {
            'ai_talent_optimizer.db': ['jobs', 'applications', 'contacts', 'profiles', 'responses'],
            'APPLICATION_TRACKING.db': ['applications'],
            'campaign_tracking.db': ['campaign_metrics', 'outreach_log'],
            'career_automation.db': ['applications', 'job_opportunities'],
            'ceo_outreach.db': ['ceo_contacts'],
            'COMPANY_RESEARCH.db': ['company_research', 'key_contacts'],
            'data/applications.db': [],  # Empty database
            'data/european_jobs.db': ['european_jobs'],
            'data/linkedin_jobs.db': ['linkedin_jobs', 'application_tracking', 'company_intelligence', 'company_people', 'email_tracking'],
            'data/unified_jobs.db': ['jobs', 'applications', 'contacts', 'responses'],
            'job_applications.db': ['job_discoveries', 'application_tracking'],
            'principal_jobs_400k.db': ['principal_jobs'],
            'QUALITY_APPLICATIONS.db': ['quality_applications'],
            'REAL_JOBS.db': ['jobs'],
            'UNIFIED_AI_JOBS.db': ['job_discoveries', 'unified_applications', 'staged_applications', 'gmail_responses'],
            'unified_career.db': ['master_jobs', 'master_applications', 'company_intelligence'],
            'unified_talent_optimizer.db': ['jobs', 'applications', 'contacts', 'responses', 'metrics', 'profile'],
            'verified_metrics.db': ['verified_metrics', 'verification_log'],
            'your_profile.db': ['professional_identity', 'technical_skills', 'major_projects', 'work_experience']
        }
        
        self.stats = {
            'total_records_processed': 0,
            'total_records_migrated': 0,
            'duplicates_removed': 0,
            'errors': [],
            'table_counts': defaultdict(lambda: {'source': 0, 'migrated': 0})
        }
        
        # Deduplication tracking
        self.seen_jobs = {}  # Key: (company, title) -> job_id
        self.seen_companies = {}  # Key: normalized_name -> company_id
        self.seen_contacts = {}  # Key: (email or full_name) -> contact_id
        self.seen_applications = {}  # Key: (job_id, applied_date) -> application_id
        
    def create_unified_database(self) -> bool:
        """Create the unified database using the schema script."""
        logger.info("Creating unified database...")
        
        try:
            # Remove existing database if it exists
            if Path(self.target_db).exists():
                os.remove(self.target_db)
                logger.info(f"Removed existing {self.target_db}")
            
            # Create new database with schema
            with open('create_unified_schema.sql', 'r') as f:
                schema_sql = f.read()
            
            conn = sqlite3.connect(self.target_db)
            conn.executescript(schema_sql)
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Created unified database: {self.target_db}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create unified database: {e}")
            return False
    
    def normalize_company_name(self, company: str) -> str:
        """Normalize company name for deduplication."""
        if not company:
            return ""
        
        # Remove common suffixes
        suffixes = [' Inc.', ' Inc', ' LLC', ' Ltd', ' Limited', ' Corp', ' Corporation', 
                   ', Inc.', ', Inc', ', LLC', ', Ltd', ', Limited']
        normalized = company.strip()
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
        
        # Convert to title case and remove extra spaces
        normalized = ' '.join(normalized.split()).title()
        return normalized
    
    def generate_job_id(self, company: str, title: str, location: str = "") -> str:
        """Generate a unique job ID."""
        content = f"{company}_{title}_{location}".lower()
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def migrate_companies(self) -> None:
        """Migrate and deduplicate company data."""
        logger.info("\n" + "="*60)
        logger.info("MIGRATING COMPANIES")
        logger.info("="*60)
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        companies_found = set()
        
        # Extract companies from jobs and contacts across all databases
        for db_path, tables in self.source_databases.items():
            if not Path(db_path).exists():
                continue
            
            try:
                source_conn = sqlite3.connect(db_path)
                source_cursor = source_conn.cursor()
                
                # Look for company data in various tables
                for table in tables:
                    if 'job' in table.lower() or 'company' in table.lower():
                        try:
                            # Get column names
                            source_cursor.execute(f"PRAGMA table_info({table})")
                            columns = [col[1] for col in source_cursor.fetchall()]
                            
                            # Find company column
                            company_col = None
                            for col in columns:
                                if 'company' in col.lower():
                                    company_col = col
                                    break
                            
                            if company_col:
                                source_cursor.execute(f"SELECT DISTINCT {company_col} FROM {table} WHERE {company_col} IS NOT NULL")
                                for row in source_cursor.fetchall():
                                    if row[0]:
                                        companies_found.add(row[0])
                        except Exception as e:
                            logger.debug(f"Could not extract companies from {db_path}/{table}: {e}")
                
                source_conn.close()
                
            except Exception as e:
                logger.error(f"Error processing {db_path} for companies: {e}")
        
        # Insert unique companies
        for company_name in companies_found:
            normalized_name = self.normalize_company_name(company_name)
            
            if normalized_name and normalized_name not in self.seen_companies:
                try:
                    cursor.execute("""
                        INSERT INTO companies (name, created_at)
                        VALUES (?, CURRENT_TIMESTAMP)
                    """, (normalized_name,))
                    
                    company_id = cursor.lastrowid
                    self.seen_companies[normalized_name] = company_id
                    self.stats['table_counts']['companies']['migrated'] += 1
                    
                except sqlite3.IntegrityError:
                    # Company already exists
                    pass
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Migrated {self.stats['table_counts']['companies']['migrated']} unique companies")
    
    def migrate_jobs(self) -> None:
        """Migrate and deduplicate job data."""
        logger.info("\n" + "="*60)
        logger.info("MIGRATING JOBS")
        logger.info("="*60)
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        job_tables = [
            ('ai_talent_optimizer.db', 'jobs'),
            ('data/unified_jobs.db', 'jobs'),
            ('REAL_JOBS.db', 'jobs'),
            ('unified_talent_optimizer.db', 'jobs'),
            ('job_applications.db', 'job_discoveries'),
            ('UNIFIED_AI_JOBS.db', 'job_discoveries'),
            ('principal_jobs_400k.db', 'principal_jobs'),
            ('data/european_jobs.db', 'european_jobs'),
            ('data/linkedin_jobs.db', 'linkedin_jobs'),
        ]
        
        for db_path, table_name in job_tables:
            if not Path(db_path).exists():
                logger.warning(f"Database not found: {db_path}")
                continue
            
            logger.info(f"Processing {db_path}/{table_name}...")
            
            try:
                source_conn = sqlite3.connect(db_path)
                source_cursor = source_conn.cursor()
                
                # Get all records from source table
                source_cursor.execute(f"SELECT * FROM {table_name}")
                columns = [description[0] for description in source_cursor.description]
                rows = source_cursor.fetchall()
                
                for row in rows:
                    record = dict(zip(columns, row))
                    self.stats['total_records_processed'] += 1
                    
                    # Extract key fields with fallbacks
                    company = record.get('company') or record.get('company_name') or 'Unknown'
                    title = record.get('title') or record.get('position') or record.get('job_title') or 'Unknown'
                    location = record.get('location') or record.get('city') or ''
                    
                    # Normalize company name
                    company_normalized = self.normalize_company_name(company)
                    
                    # Check for duplicate
                    dedup_key = (company_normalized.lower(), title.lower())
                    if dedup_key in self.seen_jobs:
                        self.stats['duplicates_removed'] += 1
                        continue
                    
                    # Get company_id
                    company_id = self.seen_companies.get(company_normalized)
                    
                    # Generate unique job_id
                    job_id = self.generate_job_id(company, title, location)
                    
                    # Map fields to new schema
                    try:
                        cursor.execute("""
                            INSERT INTO jobs (
                                job_id, source, company, company_id, title,
                                location, description, requirements, url,
                                salary_min, salary_max, remote_type,
                                relevance_score, priority_score,
                                is_ai_ml_focused, is_healthcare, is_principal_plus,
                                status, discovered_date
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            job_id,
                            db_path.replace('.db', ''),
                            company,
                            company_id,
                            title,
                            location,
                            record.get('description', ''),
                            record.get('requirements', ''),
                            record.get('url') or record.get('link', ''),
                            record.get('salary_min') or record.get('min_salary'),
                            record.get('salary_max') or record.get('max_salary'),
                            record.get('remote_type') or record.get('remote', ''),
                            record.get('relevance_score', 0.0),
                            record.get('priority_score', 0.0),
                            1 if 'ai' in title.lower() or 'ml' in title.lower() or 'machine learning' in title.lower() else 0,
                            1 if 'health' in company.lower() or 'medical' in company.lower() else 0,
                            1 if 'principal' in title.lower() or 'staff' in title.lower() or 'director' in title.lower() else 0,
                            record.get('status', 'new'),
                            record.get('discovered_date') or record.get('created_at') or datetime.now().isoformat()
                        ))
                        
                        new_job_id = cursor.lastrowid
                        self.seen_jobs[dedup_key] = new_job_id
                        self.stats['table_counts']['jobs']['migrated'] += 1
                        self.stats['total_records_migrated'] += 1
                        
                    except sqlite3.IntegrityError as e:
                        logger.debug(f"Duplicate job_id {job_id}: {e}")
                        self.stats['duplicates_removed'] += 1
                    
                source_conn.close()
                
            except Exception as e:
                logger.error(f"Error migrating from {db_path}/{table_name}: {e}")
                self.stats['errors'].append(f"{db_path}/{table_name}: {str(e)}")
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Migrated {self.stats['table_counts']['jobs']['migrated']} unique jobs")
    
    def migrate_contacts(self) -> None:
        """Migrate and deduplicate contact data."""
        logger.info("\n" + "="*60)
        logger.info("MIGRATING CONTACTS")
        logger.info("="*60)
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        contact_tables = [
            ('ai_talent_optimizer.db', 'contacts'),
            ('ceo_outreach.db', 'ceo_contacts'),
            ('COMPANY_RESEARCH.db', 'key_contacts'),
            ('data/unified_jobs.db', 'contacts'),
            ('unified_talent_optimizer.db', 'contacts'),
            ('data/linkedin_jobs.db', 'company_people'),
        ]
        
        for db_path, table_name in contact_tables:
            if not Path(db_path).exists():
                continue
            
            logger.info(f"Processing {db_path}/{table_name}...")
            
            try:
                source_conn = sqlite3.connect(db_path)
                source_cursor = source_conn.cursor()
                
                source_cursor.execute(f"SELECT * FROM {table_name}")
                columns = [description[0] for description in source_cursor.description]
                rows = source_cursor.fetchall()
                
                for row in rows:
                    record = dict(zip(columns, row))
                    self.stats['total_records_processed'] += 1
                    
                    # Extract key fields
                    email = record.get('email', '')
                    full_name = record.get('name') or record.get('full_name') or ''
                    
                    # Check for duplicate
                    dedup_key = email if email else full_name
                    if not dedup_key or dedup_key in self.seen_contacts:
                        if dedup_key:
                            self.stats['duplicates_removed'] += 1
                        continue
                    
                    # Get company_id if company is specified
                    company_name = record.get('company', '')
                    company_id = None
                    if company_name:
                        normalized_company = self.normalize_company_name(company_name)
                        company_id = self.seen_companies.get(normalized_company)
                    
                    # Determine contact type
                    title = (record.get('title') or '').lower()
                    contact_type = 'employee'
                    if 'ceo' in title or 'chief executive' in title:
                        contact_type = 'ceo'
                    elif 'cto' in title or 'chief technology' in title:
                        contact_type = 'cto'
                    elif 'recruiter' in title or 'talent' in title:
                        contact_type = 'recruiter'
                    elif 'manager' in title and ('hiring' in title or 'engineering' in title):
                        contact_type = 'hiring_manager'
                    
                    try:
                        cursor.execute("""
                            INSERT INTO contacts (
                                company_id, full_name, first_name, last_name,
                                title, email, linkedin_url, phone,
                                contact_type, contacted, contacted_date,
                                response_received, notes, priority_score
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            company_id,
                            full_name,
                            record.get('first_name', ''),
                            record.get('last_name', ''),
                            record.get('title', ''),
                            email,
                            record.get('linkedin') or record.get('linkedin_url', ''),
                            record.get('phone', ''),
                            contact_type,
                            record.get('contacted', 0),
                            record.get('contacted_date'),
                            record.get('response_received', 0),
                            record.get('notes', ''),
                            record.get('priority_score', 0.0)
                        ))
                        
                        contact_id = cursor.lastrowid
                        self.seen_contacts[dedup_key] = contact_id
                        self.stats['table_counts']['contacts']['migrated'] += 1
                        self.stats['total_records_migrated'] += 1
                        
                    except sqlite3.IntegrityError as e:
                        logger.debug(f"Error inserting contact: {e}")
                
                source_conn.close()
                
            except Exception as e:
                logger.error(f"Error migrating from {db_path}/{table_name}: {e}")
                self.stats['errors'].append(f"{db_path}/{table_name}: {str(e)}")
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Migrated {self.stats['table_counts']['contacts']['migrated']} unique contacts")
    
    def migrate_applications(self) -> None:
        """Migrate and deduplicate application data."""
        logger.info("\n" + "="*60)
        logger.info("MIGRATING APPLICATIONS")
        logger.info("="*60)
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        application_tables = [
            ('ai_talent_optimizer.db', 'applications'),
            ('APPLICATION_TRACKING.db', 'applications'),
            ('career_automation.db', 'applications'),
            ('data/unified_jobs.db', 'applications'),
            ('unified_talent_optimizer.db', 'applications'),
            ('UNIFIED_AI_JOBS.db', 'unified_applications'),
            ('UNIFIED_AI_JOBS.db', 'staged_applications'),
            ('QUALITY_APPLICATIONS.db', 'quality_applications'),
            ('data/linkedin_jobs.db', 'application_tracking'),
        ]
        
        for db_path, table_name in application_tables:
            if not Path(db_path).exists():
                continue
            
            logger.info(f"Processing {db_path}/{table_name}...")
            
            try:
                source_conn = sqlite3.connect(db_path)
                source_cursor = source_conn.cursor()
                
                # Check if table exists
                source_cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if source_cursor.fetchone()[0] == 0:
                    logger.warning(f"Table {table_name} not found in {db_path}")
                    source_conn.close()
                    continue
                
                source_cursor.execute(f"SELECT * FROM {table_name}")
                columns = [description[0] for description in source_cursor.description]
                rows = source_cursor.fetchall()
                
                for row in rows:
                    record = dict(zip(columns, row))
                    self.stats['total_records_processed'] += 1
                    
                    # Extract key fields
                    company = record.get('company') or record.get('company_name') or 'Unknown'
                    position = record.get('position') or record.get('role') or record.get('job_title') or 'Unknown'
                    applied_date = record.get('applied_date') or record.get('application_date') or datetime.now().isoformat()
                    
                    # Find matching job
                    company_normalized = self.normalize_company_name(company)
                    job_key = (company_normalized.lower(), position.lower())
                    job_id = self.seen_jobs.get(job_key)
                    
                    if not job_id:
                        # Create a minimal job record if not found
                        job_id_str = self.generate_job_id(company, position)
                        company_id = self.seen_companies.get(company_normalized)
                        
                        try:
                            cursor.execute("""
                                INSERT INTO jobs (job_id, source, company, company_id, title, status)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (job_id_str, 'legacy_application', company, company_id, position, 'applied'))
                            job_id = cursor.lastrowid
                            self.seen_jobs[job_key] = job_id
                        except sqlite3.IntegrityError:
                            continue
                    
                    # Check for duplicate application
                    app_key = (job_id, applied_date[:10])  # Use date only for dedup
                    if app_key in self.seen_applications:
                        self.stats['duplicates_removed'] += 1
                        continue
                    
                    # Get company_id
                    company_id = self.seen_companies.get(company_normalized)
                    
                    try:
                        cursor.execute("""
                            INSERT INTO applications (
                                job_id, company_id, company_name, position,
                                method, email_to, resume_version, cover_letter_version,
                                email_subject, email_body, applied_date,
                                status, response_received, personalization_score
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            job_id,
                            company_id,
                            company,
                            position,
                            record.get('application_method') or record.get('method', 'email'),
                            record.get('email_to', ''),
                            record.get('resume_version') or record.get('resume_path', 'default'),
                            record.get('cover_letter_version', ''),
                            record.get('email_subject', ''),
                            record.get('email_body', ''),
                            applied_date,
                            record.get('status', 'sent'),
                            record.get('response_received', 0),
                            record.get('personalization_score', 0.0)
                        ))
                        
                        app_id = cursor.lastrowid
                        self.seen_applications[app_key] = app_id
                        self.stats['table_counts']['applications']['migrated'] += 1
                        self.stats['total_records_migrated'] += 1
                        
                    except sqlite3.IntegrityError as e:
                        logger.debug(f"Error inserting application: {e}")
                
                source_conn.close()
                
            except Exception as e:
                logger.error(f"Error migrating from {db_path}/{table_name}: {e}")
                self.stats['errors'].append(f"{db_path}/{table_name}: {str(e)}")
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Migrated {self.stats['table_counts']['applications']['migrated']} unique applications")
    
    def migrate_emails_and_responses(self) -> None:
        """Migrate email and response data."""
        logger.info("\n" + "="*60)
        logger.info("MIGRATING EMAILS AND RESPONSES")
        logger.info("="*60)
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        response_tables = [
            ('ai_talent_optimizer.db', 'responses'),
            ('data/unified_jobs.db', 'responses'),
            ('unified_talent_optimizer.db', 'responses'),
            ('UNIFIED_AI_JOBS.db', 'gmail_responses'),
            ('data/linkedin_jobs.db', 'email_tracking'),
        ]
        
        for db_path, table_name in response_tables:
            if not Path(db_path).exists():
                continue
            
            logger.info(f"Processing {db_path}/{table_name}...")
            
            try:
                source_conn = sqlite3.connect(db_path)
                source_cursor = source_conn.cursor()
                
                # Check if table exists
                source_cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if source_cursor.fetchone()[0] == 0:
                    logger.warning(f"Table {table_name} not found in {db_path}")
                    source_conn.close()
                    continue
                
                source_cursor.execute(f"SELECT * FROM {table_name}")
                columns = [description[0] for description in source_cursor.description]
                rows = source_cursor.fetchall()
                
                for row in rows:
                    record = dict(zip(columns, row))
                    self.stats['total_records_processed'] += 1
                    
                    # Determine email type
                    email_type = 'response'
                    subject = (record.get('subject') or '').lower()
                    if 'interview' in subject:
                        email_type = 'interview'
                    elif 'reject' in subject or 'unfortunately' in subject:
                        email_type = 'rejection'
                    elif 'offer' in subject:
                        email_type = 'offer'
                    
                    try:
                        cursor.execute("""
                            INSERT INTO emails (
                                message_id, thread_id, direction,
                                from_email, to_email, subject, body_text,
                                email_type, received_date, action_required
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            record.get('message_id') or record.get('email_id', ''),
                            record.get('thread_id', ''),
                            'received',
                            record.get('from_email') or record.get('sender', ''),
                            record.get('to_email') or record.get('recipient', ''),
                            record.get('subject', ''),
                            record.get('body') or record.get('email_content') or record.get('content', ''),
                            email_type,
                            record.get('received_date') or record.get('date') or datetime.now().isoformat(),
                            record.get('action_required', 0)
                        ))
                        
                        self.stats['table_counts']['emails']['migrated'] += 1
                        self.stats['total_records_migrated'] += 1
                        
                    except sqlite3.IntegrityError as e:
                        logger.debug(f"Duplicate email: {e}")
                
                source_conn.close()
                
            except Exception as e:
                logger.error(f"Error migrating from {db_path}/{table_name}: {e}")
                self.stats['errors'].append(f"{db_path}/{table_name}: {str(e)}")
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Migrated {self.stats['table_counts']['emails']['migrated']} email records")
    
    def migrate_metrics(self) -> None:
        """Migrate metrics data."""
        logger.info("\n" + "="*60)
        logger.info("MIGRATING METRICS")
        logger.info("="*60)
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        metrics_tables = [
            ('unified_talent_optimizer.db', 'metrics'),
            ('unified_talent_optimizer.db', 'platform_metrics'),
            ('verified_metrics.db', 'verified_metrics'),
            ('campaign_tracking.db', 'campaign_metrics'),
            ('your_profile.db', 'platform_metrics'),
        ]
        
        for db_path, table_name in metrics_tables:
            if not Path(db_path).exists():
                continue
            
            logger.info(f"Processing {db_path}/{table_name}...")
            
            try:
                source_conn = sqlite3.connect(db_path)
                source_cursor = source_conn.cursor()
                
                # Check if table exists
                source_cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if source_cursor.fetchone()[0] == 0:
                    source_conn.close()
                    continue
                
                source_cursor.execute(f"SELECT * FROM {table_name}")
                columns = [description[0] for description in source_cursor.description]
                rows = source_cursor.fetchall()
                
                for row in rows:
                    record = dict(zip(columns, row))
                    self.stats['total_records_processed'] += 1
                    
                    try:
                        cursor.execute("""
                            INSERT INTO metrics (
                                metric_name, metric_category, metric_value,
                                metric_unit, date, is_verified
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            record.get('metric_name') or record.get('name', 'unknown'),
                            record.get('category', 'system'),
                            record.get('metric_value') or record.get('value', 0),
                            record.get('unit', ''),
                            record.get('date') or record.get('created_at') or datetime.now().isoformat(),
                            record.get('verified', 0)
                        ))
                        
                        self.stats['table_counts']['metrics']['migrated'] += 1
                        self.stats['total_records_migrated'] += 1
                        
                    except Exception as e:
                        logger.debug(f"Error inserting metric: {e}")
                
                source_conn.close()
                
            except Exception as e:
                logger.error(f"Error migrating from {db_path}/{table_name}: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Migrated {self.stats['table_counts']['metrics']['migrated']} metrics")
    
    def migrate_profile(self) -> None:
        """Migrate profile data (single record)."""
        logger.info("\n" + "="*60)
        logger.info("MIGRATING PROFILE")
        logger.info("="*60)
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        # The profile table already has a default record from schema creation
        # Update it with any additional data from source databases
        
        profile_sources = [
            ('unified_talent_optimizer.db', 'profile'),
            ('your_profile.db', 'professional_identity'),
            ('ai_talent_optimizer.db', 'profiles'),
        ]
        
        profile_data = {}
        
        for db_path, table_name in profile_sources:
            if not Path(db_path).exists():
                continue
            
            try:
                source_conn = sqlite3.connect(db_path)
                source_cursor = source_conn.cursor()
                
                # Check if table exists
                source_cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if source_cursor.fetchone()[0] == 0:
                    source_conn.close()
                    continue
                
                source_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                columns = [description[0] for description in source_cursor.description]
                row = source_cursor.fetchone()
                
                if row:
                    record = dict(zip(columns, row))
                    # Merge data, preferring non-null values
                    for key, value in record.items():
                        if value and (key not in profile_data or not profile_data[key]):
                            profile_data[key] = value
                
                source_conn.close()
                
            except Exception as e:
                logger.error(f"Error reading profile from {db_path}: {e}")
        
        # Update the profile record with merged data
        if profile_data:
            try:
                cursor.execute("""
                    UPDATE profile SET
                        current_title = COALESCE(?, current_title),
                        years_experience = COALESCE(?, years_experience),
                        career_level = COALESCE(?, career_level),
                        target_salary_min = COALESCE(?, target_salary_min),
                        target_salary_max = COALESCE(?, target_salary_max),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                """, (
                    profile_data.get('current_title'),
                    profile_data.get('years_experience'),
                    profile_data.get('career_level'),
                    profile_data.get('target_salary_min'),
                    profile_data.get('target_salary_max')
                ))
                
                self.stats['table_counts']['profile']['migrated'] = 1
                logger.info(f"✅ Updated profile record")
                
            except Exception as e:
                logger.error(f"Error updating profile: {e}")
        
        conn.commit()
        conn.close()
    
    def print_summary(self) -> None:
        """Print migration summary."""
        print("\n" + "="*70)
        print("MIGRATION SUMMARY")
        print("="*70)
        print(f"Total records processed: {self.stats['total_records_processed']:,}")
        print(f"Total records migrated: {self.stats['total_records_migrated']:,}")
        print(f"Duplicates removed: {self.stats['duplicates_removed']:,}")
        print(f"Success rate: {(self.stats['total_records_migrated'] / max(self.stats['total_records_processed'], 1)) * 100:.1f}%")
        
        print("\nTable Migration Counts:")
        for table, counts in self.stats['table_counts'].items():
            if counts['migrated'] > 0:
                print(f"  {table}: {counts['migrated']:,} records")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:
                print(f"  - {error}")
        
        print("\n✅ Migration completed successfully!")
        print(f"   Unified database: {self.target_db}")
        print(f"   Log file: migration_{datetime.now().strftime('%Y%m%d')}*.log")
    
    def execute_migration(self) -> bool:
        """Execute the complete migration process."""
        logger.info("="*70)
        logger.info("DATABASE MIGRATION STARTED")
        logger.info(f"Target: {self.target_db}")
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        try:
            # Step 1: Create unified database
            if not self.create_unified_database():
                return False
            
            # Step 2: Migrate companies first (referenced by other tables)
            self.migrate_companies()
            
            # Step 3: Migrate jobs
            self.migrate_jobs()
            
            # Step 4: Migrate contacts
            self.migrate_contacts()
            
            # Step 5: Migrate applications
            self.migrate_applications()
            
            # Step 6: Migrate emails and responses
            self.migrate_emails_and_responses()
            
            # Step 7: Migrate metrics
            self.migrate_metrics()
            
            # Step 8: Migrate profile
            self.migrate_profile()
            
            # Print summary
            self.print_summary()
            
            logger.info(f"Migration completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False


def main():
    """Main execution function."""
    migrator = DatabaseMigrator()
    
    print("🚀 Starting database migration...")
    print("   This will consolidate 19 databases into unified_platform.db")
    print()
    
    success = migrator.execute_migration()
    
    if success:
        print("\n✅ MIGRATION COMPLETED SUCCESSFULLY")
        return 0
    else:
        print("\n❌ MIGRATION FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())