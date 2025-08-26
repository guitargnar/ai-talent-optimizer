#!/usr/bin/env python3
"""
Comprehensive unit tests for migrate_data.py targeting 85% coverage
"""

import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, call, mock_open
import os
import sys
import logging

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from migrate_data import DatabaseMigrator


class TestInitAndBasics:
    """Test initialization and basic methods"""
    
    @pytest.mark.unit
    def test_init(self):
        """Test initialization"""
        migrator = DatabaseMigrator()
        assert migrator.target_db == 'unified_platform.db'
        assert len(migrator.source_databases) == 19
        assert migrator.stats['total_records_processed'] == 0
        
        # Custom target
        migrator2 = DatabaseMigrator('custom.db')
        assert migrator2.target_db == 'custom.db'
    
    @pytest.mark.unit
    def test_normalize_company_name(self):
        """Test company name normalization"""
        migrator = DatabaseMigrator()
        
        # Test various cases
        assert migrator.normalize_company_name("Apple Inc.") == "Apple"
        assert migrator.normalize_company_name("Google LLC") == "Google"
        assert migrator.normalize_company_name("Microsoft Corporation") == "Microsoft"
        assert migrator.normalize_company_name("Meta, LLC") == "Meta,"  # Comma suffix not in list
        assert migrator.normalize_company_name("  OpenAI  ") == "Openai"
        assert migrator.normalize_company_name("") == ""
        assert migrator.normalize_company_name(None) == ""
        assert migrator.normalize_company_name("Company Ltd") == "Company"
        assert migrator.normalize_company_name("Company Limited") == "Company"
        assert migrator.normalize_company_name("Company Corp") == "Company"
    
    @pytest.mark.unit
    def test_generate_job_id(self):
        """Test job ID generation"""
        migrator = DatabaseMigrator()
        
        job_id = migrator.generate_job_id("Google", "Engineer", "NYC")
        assert isinstance(job_id, str)
        assert len(job_id) == 12
        
        # Test consistency
        job_id2 = migrator.generate_job_id("Google", "Engineer", "NYC")
        assert job_id == job_id2
        
        # Test different input
        job_id3 = migrator.generate_job_id("Meta", "Engineer", "NYC")
        assert job_id != job_id3


class TestDatabaseCreation:
    """Test database creation"""
    
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
    @patch('builtins.open', mock_open(read_data='CREATE TABLE test (id INTEGER);'))
    @patch('sqlite3.connect')
    @patch('pathlib.Path.exists')
    def test_create_unified_database_new(self, mock_exists, mock_connect):
        """Test database creation when it doesn't exist"""
        mock_exists.return_value = False
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        migrator = DatabaseMigrator()
        result = migrator.create_unified_database()
        
        assert result is True
        mock_conn.executescript.assert_called_once()
    
    @pytest.mark.unit
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_create_unified_database_no_schema(self, mock_open):
        """Test database creation with missing schema file"""
        migrator = DatabaseMigrator()
        result = migrator.create_unified_database()
        assert result is False


class TestCompanyMigration:
    """Test company migration"""
    
    @pytest.mark.unit
    @patch('sqlite3.connect')
    @patch('pathlib.Path.exists')
    def test_migrate_companies_success(self, mock_exists, mock_connect):
        """Test successful company migration"""
        migrator = DatabaseMigrator()
        
        # Only one source database exists
        mock_exists.side_effect = lambda self: 'ai_talent_optimizer.db' in str(self) if self else False
        
        # Setup mocks
        mock_target_conn = MagicMock()
        mock_target_cursor = MagicMock()
        mock_target_conn.cursor.return_value = mock_target_cursor
        mock_target_cursor.lastrowid = 1
        
        mock_source_conn = MagicMock()
        mock_source_cursor = MagicMock()
        mock_source_conn.cursor.return_value = mock_source_cursor
        
        # Mock PRAGMA table_info and SELECT results
        mock_source_cursor.fetchall.side_effect = [
            [('id',), ('company_name',)],  # PRAGMA table_info
            [('Google',), ('Meta',)]  # SELECT DISTINCT
        ]
        
        mock_connect.side_effect = [mock_target_conn, mock_source_conn]
        
        migrator.migrate_companies()
        
        assert mock_target_cursor.execute.called
        assert len(migrator.seen_companies) > 0
    
    @pytest.mark.unit
    @patch('sqlite3.connect')
    @patch('pathlib.Path.exists')
    def test_migrate_companies_no_sources(self, mock_exists, mock_connect):
        """Test company migration with no source databases"""
        migrator = DatabaseMigrator()
        mock_exists.return_value = False
        
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        migrator.migrate_companies()
        
        # Should only connect to target
        assert mock_connect.call_count == 1


class TestJobMigration:
    """Test job migration"""
    
    @pytest.mark.unit
    @patch('sqlite3.connect')
    @patch('pathlib.Path.exists')
    def test_migrate_jobs_success(self, mock_exists, mock_connect):
        """Test successful job migration"""
        migrator = DatabaseMigrator()
        migrator.seen_companies = {'Google': 1}
        
        # Only ai_talent_optimizer.db exists
        mock_exists.side_effect = lambda self: 'ai_talent_optimizer.db' in str(self) if self else False
        
        mock_target_conn = MagicMock()
        mock_target_cursor = MagicMock()
        mock_target_conn.cursor.return_value = mock_target_cursor
        mock_target_cursor.lastrowid = 1
        
        mock_source_conn = MagicMock()
        mock_source_cursor = MagicMock()
        mock_source_conn.cursor.return_value = mock_source_cursor
        mock_source_cursor.description = [('company',), ('title',), ('location',)]
        mock_source_cursor.fetchall.return_value = [
            ('Google', 'Engineer', 'NYC', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        ]
        
        mock_connect.side_effect = [mock_target_conn, mock_source_conn]
        
        migrator.migrate_jobs()
        
        assert mock_target_cursor.execute.called
        assert len(migrator.seen_jobs) > 0
    
    @pytest.mark.unit
    @patch('sqlite3.connect')
    @patch('pathlib.Path.exists')
    def test_migrate_jobs_with_duplicates(self, mock_exists, mock_connect):
        """Test job migration with duplicate detection"""
        migrator = DatabaseMigrator()
        migrator.seen_companies = {'Google': 1}
        
        mock_exists.side_effect = lambda self: 'ai_talent_optimizer.db' in str(self) if self else False
        
        mock_target_conn = MagicMock()
        mock_target_cursor = MagicMock()
        mock_target_conn.cursor.return_value = mock_target_cursor
        
        mock_source_conn = MagicMock()
        mock_source_cursor = MagicMock()
        mock_source_conn.cursor.return_value = mock_source_cursor
        mock_source_cursor.description = [('company',), ('title',)]
        mock_source_cursor.fetchall.return_value = [
            ('Google', 'Engineer'),
            ('Google', 'Engineer'),  # Duplicate
            ('Meta', 'Scientist')
        ]
        
        mock_connect.side_effect = [mock_target_conn, mock_source_conn]
        
        migrator.migrate_jobs()
        
        assert migrator.stats['duplicates_removed'] > 0


class TestContactMigration:
    """Test contact migration"""
    
    @pytest.mark.unit
    @patch('sqlite3.connect')
    @patch('pathlib.Path.exists')
    def test_migrate_contacts_success(self, mock_exists, mock_connect):
        """Test successful contact migration"""
        migrator = DatabaseMigrator()
        migrator.seen_companies = {'Google': 1}
        
        mock_exists.side_effect = lambda self: 'ai_talent_optimizer.db' in str(self) if self else False
        
        mock_target_conn = MagicMock()
        mock_target_cursor = MagicMock()
        mock_target_conn.cursor.return_value = mock_target_cursor
        mock_target_cursor.lastrowid = 1
        
        mock_source_conn = MagicMock()
        mock_source_cursor = MagicMock()
        mock_source_conn.cursor.return_value = mock_source_cursor
        mock_source_cursor.description = [('email',), ('name',), ('company',), ('title',)]
        mock_source_cursor.fetchall.return_value = [
            ('john@google.com', 'John Doe', 'Google', 'CEO')
        ]
        
        mock_connect.side_effect = [mock_target_conn, mock_source_conn]
        
        migrator.migrate_contacts()
        
        assert mock_target_cursor.execute.called
        assert len(migrator.seen_contacts) > 0


class TestApplicationMigration:
    """Test application migration"""
    
    @pytest.mark.unit
    @patch('sqlite3.connect')
    @patch('pathlib.Path.exists')
    def test_migrate_applications_success(self, mock_exists, mock_connect):
        """Test successful application migration"""
        migrator = DatabaseMigrator()
        migrator.seen_companies = {'Google': 1}
        migrator.seen_jobs = {('google', 'engineer'): 1}
        
        mock_exists.side_effect = lambda self: 'ai_talent_optimizer.db' in str(self) if self else False
        
        mock_target_conn = MagicMock()
        mock_target_cursor = MagicMock()
        mock_target_conn.cursor.return_value = mock_target_cursor
        mock_target_cursor.lastrowid = 1
        
        mock_source_conn = MagicMock()
        mock_source_cursor = MagicMock()
        mock_source_conn.cursor.return_value = mock_source_cursor
        mock_source_cursor.fetchone.return_value = (1,)  # Table exists
        mock_source_cursor.description = [('company',), ('position',), ('applied_date',)]
        mock_source_cursor.fetchall.return_value = [
            ('Google', 'Engineer', '2024-01-01')
        ]
        
        mock_connect.side_effect = [mock_target_conn, mock_source_conn]
        
        migrator.migrate_applications()
        
        assert mock_target_cursor.execute.called
        assert len(migrator.seen_applications) > 0
    
    @pytest.mark.unit
    @patch('sqlite3.connect')
    @patch('pathlib.Path.exists')
    def test_migrate_applications_missing_table(self, mock_exists, mock_connect):
        """Test application migration with missing table"""
        migrator = DatabaseMigrator()
        
        mock_exists.side_effect = lambda self: 'ai_talent_optimizer.db' in str(self) if self else False
        
        mock_target_conn = MagicMock()
        mock_source_conn = MagicMock()
        mock_source_cursor = MagicMock()
        mock_source_conn.cursor.return_value = mock_source_cursor
        mock_source_cursor.fetchone.return_value = (0,)  # Table doesn't exist
        
        mock_connect.side_effect = [mock_target_conn, mock_source_conn]
        
        migrator.migrate_applications()
        
        # Should handle gracefully
        assert migrator.stats['total_records_migrated'] == 0


class TestEmailMigration:
    """Test email migration"""
    
    @pytest.mark.unit
    @patch('sqlite3.connect')
    @patch('pathlib.Path.exists')
    def test_migrate_emails_success(self, mock_exists, mock_connect):
        """Test successful email migration"""
        migrator = DatabaseMigrator()
        
        mock_exists.side_effect = lambda self: 'ai_talent_optimizer.db' in str(self) if self else False
        
        mock_target_conn = MagicMock()
        mock_target_cursor = MagicMock()
        mock_target_conn.cursor.return_value = mock_target_cursor
        
        mock_source_conn = MagicMock()
        mock_source_cursor = MagicMock()
        mock_source_conn.cursor.return_value = mock_source_cursor
        mock_source_cursor.fetchone.return_value = (1,)  # Table exists
        mock_source_cursor.description = [('subject',), ('from_email',), ('body',)]
        mock_source_cursor.fetchall.return_value = [
            ('Interview Request', 'hr@google.com', 'Please schedule...'),
            ('Unfortunately', 'hr@meta.com', 'We decided...'),
            ('Job Offer', 'hr@apple.com', 'Congratulations!')
        ]
        
        mock_connect.side_effect = [mock_target_conn, mock_source_conn]
        
        migrator.migrate_emails_and_responses()
        
        assert mock_target_cursor.execute.called
        assert migrator.stats['table_counts']['emails']['migrated'] > 0


class TestMetricsMigration:
    """Test metrics migration"""
    
    @pytest.mark.unit
    @patch('sqlite3.connect')
    @patch('pathlib.Path.exists')
    def test_migrate_metrics_success(self, mock_exists, mock_connect):
        """Test successful metrics migration"""
        migrator = DatabaseMigrator()
        
        mock_exists.side_effect = lambda self: 'unified_talent_optimizer.db' in str(self) if self else False
        
        mock_target_conn = MagicMock()
        mock_target_cursor = MagicMock()
        mock_target_conn.cursor.return_value = mock_target_cursor
        
        mock_source_conn = MagicMock()
        mock_source_cursor = MagicMock()
        mock_source_conn.cursor.return_value = mock_source_cursor
        mock_source_cursor.fetchone.return_value = (1,)  # Table exists
        mock_source_cursor.description = [('metric_name',), ('value',)]
        mock_source_cursor.fetchall.return_value = [
            ('applications_sent', 100)
        ]
        
        mock_connect.side_effect = [mock_target_conn, mock_source_conn]
        
        migrator.migrate_metrics()
        
        assert mock_target_cursor.execute.called


class TestProfileMigration:
    """Test profile migration"""
    
    @pytest.mark.unit
    @patch('sqlite3.connect')
    @patch('pathlib.Path.exists')
    def test_migrate_profile_success(self, mock_exists, mock_connect):
        """Test successful profile migration"""
        migrator = DatabaseMigrator()
        
        mock_exists.side_effect = lambda self: 'unified_talent_optimizer.db' in str(self) if self else False
        
        mock_target_conn = MagicMock()
        mock_target_cursor = MagicMock()
        mock_target_conn.cursor.return_value = mock_target_cursor
        
        mock_source_conn = MagicMock()
        mock_source_cursor = MagicMock()
        mock_source_conn.cursor.return_value = mock_source_cursor
        mock_source_cursor.fetchone.side_effect = [
            (1,),  # Table exists
            ('Matthew Scott', 'Senior Engineer', 15, 'Principal', 400000, 600000)  # Profile data
        ]
        mock_source_cursor.description = [
            ('name',), ('current_title',), ('years_experience',),
            ('career_level',), ('target_salary_min',), ('target_salary_max',)
        ]
        
        mock_connect.side_effect = [mock_target_conn, mock_source_conn]
        
        migrator.migrate_profile()
        
        assert mock_target_cursor.execute.called


class TestSummaryAndExecution:
    """Test summary and execution methods"""
    
    @pytest.mark.unit
    @patch('builtins.print')
    def test_print_summary(self, mock_print):
        """Test summary printing"""
        migrator = DatabaseMigrator()
        migrator.stats['total_records_processed'] = 1000
        migrator.stats['total_records_migrated'] = 950
        migrator.stats['duplicates_removed'] = 50
        migrator.stats['table_counts']['jobs']['migrated'] = 500
        migrator.stats['errors'] = ['Error 1', 'Error 2']
        
        migrator.print_summary()
        
        # Check that print was called multiple times
        assert mock_print.call_count > 5
    
    @pytest.mark.unit
    @patch('migrate_data.DatabaseMigrator.create_unified_database')
    @patch('migrate_data.DatabaseMigrator.migrate_companies')
    @patch('migrate_data.DatabaseMigrator.migrate_jobs')
    @patch('migrate_data.DatabaseMigrator.migrate_contacts')
    @patch('migrate_data.DatabaseMigrator.migrate_applications')
    @patch('migrate_data.DatabaseMigrator.migrate_emails_and_responses')
    @patch('migrate_data.DatabaseMigrator.migrate_metrics')
    @patch('migrate_data.DatabaseMigrator.migrate_profile')
    @patch('migrate_data.DatabaseMigrator.print_summary')
    def test_execute_migration_success(self, mock_summary, mock_profile, mock_metrics,
                                      mock_emails, mock_apps, mock_contacts,
                                      mock_jobs, mock_companies, mock_create):
        """Test successful migration execution"""
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
        mock_summary.assert_called_once()
    
    @pytest.mark.unit
    @patch('migrate_data.DatabaseMigrator.create_unified_database')
    def test_execute_migration_failure(self, mock_create):
        """Test migration failure"""
        mock_create.return_value = False
        
        migrator = DatabaseMigrator()
        result = migrator.execute_migration()
        
        assert result is False
    
    @pytest.mark.unit
    @patch('migrate_data.DatabaseMigrator.create_unified_database')
    @patch('migrate_data.DatabaseMigrator.migrate_companies')
    def test_execute_migration_exception(self, mock_companies, mock_create):
        """Test migration with exception"""
        mock_create.return_value = True
        mock_companies.side_effect = Exception("Test error")
        
        migrator = DatabaseMigrator()
        result = migrator.execute_migration()
        
        assert result is False


class TestMain:
    """Test main function"""
    
    @pytest.mark.unit
    @patch('sys.exit')
    @patch('builtins.print')
    @patch('migrate_data.DatabaseMigrator.execute_migration')
    def test_main_success(self, mock_execute, mock_print, mock_exit):
        """Test main function with successful migration"""
        mock_execute.return_value = True
        
        from migrate_data import main
        main()
        
        mock_execute.assert_called_once()
        mock_exit.assert_called_with(0)
    
    @pytest.mark.unit
    @patch('sys.exit')
    @patch('builtins.print')
    @patch('migrate_data.DatabaseMigrator.execute_migration')
    def test_main_failure(self, mock_execute, mock_print, mock_exit):
        """Test main function with failed migration"""
        mock_execute.return_value = False
        
        from migrate_data import main
        main()
        
        mock_execute.assert_called_once()
        mock_exit.assert_called_with(1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])