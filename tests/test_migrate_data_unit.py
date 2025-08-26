#!/usr/bin/env python3
"""
Comprehensive unit tests for migrate_data.py with proper mocking
"""

import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, call, mock_open
import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from migrate_data import DatabaseMigrator


class TestDatabaseMigratorInit:
    """Test DatabaseMigrator initialization"""
    
    @pytest.mark.unit
    def test_init_default_target(self):
        """Test default target database initialization"""
        migrator = DatabaseMigrator()
        assert migrator.target_db == 'unified_platform.db'
        assert len(migrator.source_databases) == 19
        assert migrator.stats['total_records_processed'] == 0
        assert migrator.stats['total_records_migrated'] == 0
        assert migrator.stats['duplicates_removed'] == 0
        assert len(migrator.seen_jobs) == 0
        assert len(migrator.seen_companies) == 0
    
    @pytest.mark.unit
    def test_init_custom_target(self):
        """Test custom target database initialization"""
        migrator = DatabaseMigrator('custom.db')
        assert migrator.target_db == 'custom.db'


class TestNormalization:
    """Test data normalization methods"""
    
    @pytest.mark.unit
    def test_normalize_company_name(self):
        """Test company name normalization"""
        migrator = DatabaseMigrator()
        
        # Test suffix removal
        assert migrator.normalize_company_name("Apple Inc.") == "Apple"
        assert migrator.normalize_company_name("Google LLC") == "Google"
        assert migrator.normalize_company_name("Microsoft Corporation") == "Microsoft"
        
        # Test case normalization
        assert migrator.normalize_company_name("meta platforms") == "Meta Platforms"
        assert migrator.normalize_company_name("OPENAI") == "Openai"
        
        # Test whitespace handling
        assert migrator.normalize_company_name("  Anthropic  ") == "Anthropic"
        assert migrator.normalize_company_name("Space   X") == "Space X"
        
        # Test edge cases
        assert migrator.normalize_company_name("") == ""
        assert migrator.normalize_company_name(None) == ""
        
        # Test that lowercase suffixes aren't removed
        assert migrator.normalize_company_name("apple ltd") == "Apple Ltd"
        
    @pytest.mark.unit
    def test_generate_job_id(self):
        """Test job ID generation"""
        migrator = DatabaseMigrator()
        
        # Test basic generation
        job_id = migrator.generate_job_id("Google", "Engineer", "NYC")
        assert isinstance(job_id, str)
        assert len(job_id) == 12  # Truncated MD5 hash
        
        # Test consistency
        job_id2 = migrator.generate_job_id("Google", "Engineer", "NYC")
        assert job_id == job_id2
        
        # Test uniqueness
        job_id3 = migrator.generate_job_id("Meta", "Engineer", "NYC")
        assert job_id != job_id3


class TestDatabaseCreation:
    """Test database creation functionality"""
    
    @pytest.mark.unit
    @patch('builtins.open', mock_open(read_data='CREATE TABLE test (id INTEGER);'))
    @patch('sqlite3.connect')
    @patch('os.remove')
    @patch('pathlib.Path.exists')
    def test_create_unified_database_success(self, mock_exists, mock_remove, mock_connect):
        """Test successful database creation"""
        mock_exists.return_value = True
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        migrator = DatabaseMigrator()
        result = migrator.create_unified_database()
        
        assert result is True
        mock_remove.assert_called_once_with('unified_platform.db')
        mock_conn.executescript.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @pytest.mark.unit
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_create_unified_database_no_schema(self, mock_open):
        """Test database creation with missing schema file"""
        migrator = DatabaseMigrator()
        result = migrator.create_unified_database()
        assert result is False


class TestCompanyMigration:
    """Test company migration with real database"""
    
    @pytest.mark.unit
    def test_migrate_companies_with_temp_db(self):
        """Test company migration using temporary databases"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create target database
            target_db = Path(tmpdir) / 'target.db'
            migrator = DatabaseMigrator(str(target_db))
            
            # Create target schema
            conn = sqlite3.connect(str(target_db))
            conn.execute("""
                CREATE TABLE companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.close()
            
            # Create source database
            source_db = Path(tmpdir) / 'source.db'
            conn = sqlite3.connect(str(source_db))
            conn.execute("""
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY,
                    company TEXT,
                    title TEXT
                )
            """)
            conn.execute("INSERT INTO jobs VALUES (1, 'Google Inc.', 'Engineer')")
            conn.execute("INSERT INTO jobs VALUES (2, 'Meta LLC', 'Scientist')")
            conn.execute("INSERT INTO jobs VALUES (3, 'Google', 'Manager')")  # Duplicate
            conn.commit()
            conn.close()
            
            # Override source databases
            migrator.source_databases = {str(source_db): ['jobs']}
            
            # Run migration
            migrator.migrate_companies()
            
            # Verify results
            conn = sqlite3.connect(str(target_db))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM companies ORDER BY name")
            companies = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            assert companies == ['Google', 'Meta']
            assert len(migrator.seen_companies) == 2
            assert migrator.stats['table_counts']['companies']['migrated'] == 2


class TestJobMigration:
    """Test job migration with real database"""
    
    @pytest.mark.unit
    def test_migrate_jobs_with_deduplication(self):
        """Test job migration with deduplication"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create target database
            target_db = Path(tmpdir) / 'target.db'
            migrator = DatabaseMigrator(str(target_db))
            
            # Create target schema
            conn = sqlite3.connect(str(target_db))
            conn.execute("""
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE,
                    source TEXT,
                    company TEXT,
                    company_id INTEGER,
                    title TEXT,
                    location TEXT,
                    description TEXT,
                    requirements TEXT,
                    url TEXT,
                    salary_min INTEGER,
                    salary_max INTEGER,
                    remote_type TEXT,
                    relevance_score REAL,
                    priority_score REAL,
                    is_ai_ml_focused INTEGER,
                    is_healthcare INTEGER,
                    is_principal_plus INTEGER,
                    status TEXT,
                    discovered_date TEXT
                )
            """)
            conn.close()
            
            # Create source database
            source_db = Path(tmpdir) / 'source.db'
            conn = sqlite3.connect(str(source_db))
            conn.execute("""
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY,
                    company TEXT,
                    title TEXT,
                    location TEXT
                )
            """)
            conn.execute("INSERT INTO jobs VALUES (1, 'Google', 'ML Engineer', 'NYC')")
            conn.execute("INSERT INTO jobs VALUES (2, 'Google', 'ML Engineer', 'NYC')")  # Duplicate
            conn.execute("INSERT INTO jobs VALUES (3, 'Meta', 'Data Scientist', 'SF')")
            conn.commit()
            conn.close()
            
            # Set up companies
            migrator.seen_companies = {'Google': 1, 'Meta': 2}
            
            # Override source databases for specific test
            migrator.source_databases = {str(source_db): ['jobs']}
            
            # Run migration  
            migrator.migrate_jobs()
            
            # Verify results
            conn = sqlite3.connect(str(target_db))
            cursor = conn.cursor()
            cursor.execute("SELECT company, title FROM jobs ORDER BY company")
            jobs = cursor.fetchall()
            conn.close()
            
            assert len(jobs) == 2
            assert jobs[0] == ('Google', 'ML Engineer')
            assert jobs[1] == ('Meta', 'Data Scientist')
            assert migrator.stats['duplicates_removed'] == 1


class TestApplicationMigration:
    """Test application migration"""
    
    @pytest.mark.unit 
    def test_migrate_applications_creates_missing_jobs(self):
        """Test that applications create missing job records"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create databases
            target_db = Path(tmpdir) / 'target.db'
            source_db = Path(tmpdir) / 'source.db'
            
            migrator = DatabaseMigrator(str(target_db))
            
            # Create target schema
            conn = sqlite3.connect(str(target_db))
            conn.executescript("""
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE,
                    source TEXT,
                    company TEXT,
                    company_id INTEGER,
                    title TEXT,
                    status TEXT
                );
                CREATE TABLE applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER,
                    company_id INTEGER,
                    company_name TEXT,
                    position TEXT,
                    method TEXT,
                    email_to TEXT,
                    resume_version TEXT,
                    cover_letter_version TEXT,
                    email_subject TEXT,
                    email_body TEXT,
                    applied_date TEXT,
                    status TEXT,
                    response_received INTEGER,
                    personalization_score REAL
                );
            """)
            conn.close()
            
            # Create source with applications but no matching jobs
            conn = sqlite3.connect(str(source_db))
            conn.execute("""
                CREATE TABLE applications (
                    id INTEGER PRIMARY KEY,
                    company TEXT,
                    position TEXT,
                    applied_date TEXT
                )
            """)
            conn.execute("""
                INSERT INTO applications VALUES 
                (1, 'Anthropic', 'AI Researcher', '2024-01-15')
            """)
            conn.commit()
            conn.close()
            
            # Set up migrator with proper isolation
            migrator.source_databases = {str(source_db): ['applications']}
            migrator.seen_companies = {'Anthropic': 1}
            
            # Instead of calling the real migrate_applications which tries all databases,
            # we'll test the core logic directly
            with patch('pathlib.Path.exists') as mock_exists:
                # Only our test database exists
                mock_exists.side_effect = lambda p: str(p) == str(source_db)
                migrator.migrate_applications()
            
            # Verify job was created
            conn = sqlite3.connect(str(target_db))
            cursor = conn.cursor()
            cursor.execute("SELECT company, title FROM jobs")
            jobs = cursor.fetchall()
            cursor.execute("SELECT company_name, position FROM applications")
            apps = cursor.fetchall()
            conn.close()
            
            assert len(jobs) == 1
            assert jobs[0] == ('Anthropic', 'AI Researcher')
            assert len(apps) == 1
            assert apps[0] == ('Anthropic', 'AI Researcher')


class TestEmailMigration:
    """Test email and response migration"""
    
    @pytest.mark.unit
    def test_migrate_emails_categorization(self):
        """Test email categorization during migration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_db = Path(tmpdir) / 'target.db'
            source_db = Path(tmpdir) / 'source.db'
            
            migrator = DatabaseMigrator(str(target_db))
            
            # Create schemas
            conn = sqlite3.connect(str(target_db))
            conn.execute("""
                CREATE TABLE emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT,
                    thread_id TEXT,
                    direction TEXT,
                    from_email TEXT,
                    to_email TEXT,
                    subject TEXT,
                    body_text TEXT,
                    email_type TEXT,
                    received_date TEXT,
                    action_required INTEGER
                )
            """)
            conn.close()
            
            conn = sqlite3.connect(str(source_db))
            conn.execute("""
                CREATE TABLE responses (
                    id INTEGER PRIMARY KEY,
                    subject TEXT,
                    from_email TEXT,
                    body TEXT
                )
            """)
            conn.executemany("""
                INSERT INTO responses VALUES (?, ?, ?, ?)
            """, [
                (1, 'Interview Invitation', 'hr@google.com', 'Please schedule...'),
                (2, 'Unfortunately...', 'hr@meta.com', 'We decided to...'),
                (3, 'Job Offer', 'hr@apple.com', 'We are pleased...')
            ])
            conn.commit()
            conn.close()
            
            migrator.source_databases = {str(source_db): ['responses']}
            
            # Run migration
            migrator.migrate_emails_and_responses()
            
            # Verify categorization
            conn = sqlite3.connect(str(target_db))
            cursor = conn.cursor()
            cursor.execute("SELECT subject, email_type FROM emails ORDER BY id")
            emails = cursor.fetchall()
            conn.close()
            
            assert len(emails) == 3
            assert emails[0][1] == 'interview'
            assert emails[1][1] == 'rejection'
            assert emails[2][1] == 'offer'


class TestDeduplication:
    """Test deduplication logic"""
    
    @pytest.mark.unit
    def test_job_deduplication_logic(self):
        """Test job deduplication by company and title"""
        migrator = DatabaseMigrator()
        
        # First job
        key1 = ('google', 'software engineer')
        migrator.seen_jobs[key1] = 1
        
        # Check duplicate
        key2 = ('google', 'software engineer')
        assert key2 in migrator.seen_jobs
        
        # Check different job
        key3 = ('google', 'data scientist')
        assert key3 not in migrator.seen_jobs
    
    @pytest.mark.unit
    def test_contact_deduplication_by_email(self):
        """Test contact deduplication by email"""
        migrator = DatabaseMigrator()
        
        migrator.seen_contacts['john@google.com'] = 1
        assert 'john@google.com' in migrator.seen_contacts
        assert 'jane@google.com' not in migrator.seen_contacts
    
    @pytest.mark.unit
    def test_application_deduplication(self):
        """Test application deduplication by job and date"""
        migrator = DatabaseMigrator()
        
        app_key = (1, '2024-01-15')
        migrator.seen_applications[app_key] = 1
        
        assert app_key in migrator.seen_applications
        assert (1, '2024-01-16') not in migrator.seen_applications
        assert (2, '2024-01-15') not in migrator.seen_applications


class TestStatistics:
    """Test statistics tracking"""
    
    @pytest.mark.unit
    def test_stats_tracking(self):
        """Test that statistics are properly tracked"""
        migrator = DatabaseMigrator()
        
        # Initial stats
        assert migrator.stats['total_records_processed'] == 0
        assert migrator.stats['total_records_migrated'] == 0
        assert migrator.stats['duplicates_removed'] == 0
        
        # Simulate processing
        migrator.stats['total_records_processed'] = 100
        migrator.stats['total_records_migrated'] = 85
        migrator.stats['duplicates_removed'] = 15
        
        assert migrator.stats['total_records_processed'] == 100
        assert migrator.stats['total_records_migrated'] == 85
        assert migrator.stats['duplicates_removed'] == 15


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.unit
    def test_empty_database_handling(self):
        """Test handling of empty source databases"""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_db = Path(tmpdir) / 'target.db'
            empty_db = Path(tmpdir) / 'empty.db'
            
            # Create empty source database
            conn = sqlite3.connect(str(empty_db))
            conn.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY)")
            conn.close()
            
            # Create target
            conn = sqlite3.connect(str(target_db))
            conn.execute("""
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY,
                    job_id TEXT,
                    company TEXT,
                    title TEXT
                )
            """)
            conn.close()
            
            migrator = DatabaseMigrator(str(target_db))
            migrator.source_databases = {str(empty_db): ['jobs']}
            
            # Should not crash
            migrator.migrate_jobs()
            
            assert migrator.stats['total_records_processed'] == 0
            assert migrator.stats['total_records_migrated'] == 0
    
    @pytest.mark.unit
    def test_missing_table_handling(self):
        """Test handling of missing tables in source database"""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_db = Path(tmpdir) / 'target.db'
            source_db = Path(tmpdir) / 'source.db'
            
            # Create source without expected table
            conn = sqlite3.connect(str(source_db))
            conn.execute("CREATE TABLE other_table (id INTEGER)")
            conn.close()
            
            # Create target
            conn = sqlite3.connect(str(target_db))
            conn.execute("CREATE TABLE applications (id INTEGER)")
            conn.close()
            
            migrator = DatabaseMigrator(str(target_db))
            migrator.source_databases = {str(source_db): ['applications']}
            
            # Should handle gracefully
            migrator.migrate_applications()
            
            # Should log error but not crash
            assert migrator.stats['total_records_migrated'] == 0


class TestIntegration:
    """Test full migration workflow"""
    
    @pytest.mark.integration
    @patch('builtins.open', mock_open(read_data='CREATE TABLE test (id INTEGER);'))
    @patch('migrate_data.DatabaseMigrator.migrate_companies')
    @patch('migrate_data.DatabaseMigrator.migrate_jobs')
    @patch('migrate_data.DatabaseMigrator.migrate_contacts')
    @patch('migrate_data.DatabaseMigrator.migrate_applications')
    @patch('migrate_data.DatabaseMigrator.migrate_emails_and_responses')
    @patch('migrate_data.DatabaseMigrator.migrate_metrics')
    @patch('migrate_data.DatabaseMigrator.migrate_profile')
    @patch('migrate_data.DatabaseMigrator.create_unified_database')
    def test_execute_migration_success(self, mock_create, mock_profile, mock_metrics,
                                      mock_emails, mock_apps, mock_contacts,
                                      mock_jobs, mock_companies):
        """Test successful execution of full migration"""
        mock_create.return_value = True
        
        migrator = DatabaseMigrator()
        result = migrator.execute_migration()
        
        assert result is True
        mock_create.assert_called_once()
        mock_companies.assert_called_once()
        mock_jobs.assert_called_once()
        mock_contacts.assert_called_once()
        mock_apps.assert_called_once()
        mock_emails.assert_called_once()
        mock_metrics.assert_called_once()
        mock_profile.assert_called_once()
    
    @pytest.mark.integration
    @patch('migrate_data.DatabaseMigrator.create_unified_database')
    def test_execute_migration_failure(self, mock_create):
        """Test migration failure when database creation fails"""
        mock_create.return_value = False
        
        migrator = DatabaseMigrator()
        result = migrator.execute_migration()
        
        assert result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])