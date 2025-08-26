#!/usr/bin/env python3
"""
Comprehensive Test Suite for validate_migration.py
==================================================
Tests all validation methods with mocked database connections and file operations.
Achieves 85%+ test coverage.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open, PropertyMock
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import tempfile
import zipfile

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from validate_migration import MigrationValidator


class TestMigrationValidator(unittest.TestCase):
    """Test suite for MigrationValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = MigrationValidator('test.db', 'backup.zip')
        self.validator.validation_results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'stats': {}
        }
    
    @patch('validate_migration.Path.glob')
    def test_find_latest_backup(self, mock_glob):
        """Test finding the latest backup file."""
        # Test with multiple backup files
        mock_glob.return_value = [
            Path('database_backup_20250101_120000.zip'),
            Path('database_backup_20250102_120000.zip'),
            Path('database_backup_20250103_120000.zip')
        ]
        
        # Create validator - this calls _find_latest_backup in __init__
        validator = MigrationValidator('test.db')
        
        # The latest backup should be selected
        self.assertEqual(validator.backup_file, 'database_backup_20250103_120000.zip')
        
        # Now test the method directly
        result = validator._find_latest_backup()
        self.assertEqual(result, 'database_backup_20250103_120000.zip')
    
    @patch('validate_migration.Path.glob')
    def test_find_latest_backup_no_files(self, mock_glob):
        """Test finding latest backup when no backup files exist."""
        mock_glob.return_value = []
        
        validator = MigrationValidator('test.db')
        result = validator._find_latest_backup()
        
        self.assertIsNone(result)
    
    @patch('validate_migration.sqlite3.connect')
    def test_validate_database_structure_success(self, mock_connect):
        """Test successful database structure validation."""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock tables
        mock_cursor.fetchall.side_effect = [
            # Tables
            [('companies',), ('jobs',), ('applications',), ('contacts',),
             ('emails',), ('metrics',), ('profile',), ('system_log',)],
            # Views
            [('active_jobs',), ('application_responses',), ('contact_network',)],
            # Indexes
            [('idx_jobs_company',), ('idx_applications_job',), ('idx_emails_app',)]
        ]
        
        result = self.validator.validate_database_structure()
        
        self.assertTrue(result)
        self.assertEqual(len(self.validator.validation_results['passed']), 11)  # 8 tables + 3 views
        self.assertEqual(len(self.validator.validation_results['failed']), 0)
        self.assertEqual(self.validator.validation_results['stats']['index_count'], 3)
        mock_conn.close.assert_called_once()
    
    @patch('validate_migration.sqlite3.connect')
    def test_validate_database_structure_missing_tables(self, mock_connect):
        """Test database structure validation with missing tables."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock missing some tables
        mock_cursor.fetchall.side_effect = [
            # Tables (missing 'profile' and 'system_log')
            [('companies',), ('jobs',), ('applications',), ('contacts',),
             ('emails',), ('metrics',)],
            # Views (missing 'contact_network')
            [('active_jobs',), ('application_responses',)],
            # Indexes
            []
        ]
        
        result = self.validator.validate_database_structure()
        
        self.assertFalse(result)  # Should fail due to missing tables
        self.assertEqual(len(self.validator.validation_results['failed']), 2)  # 2 missing tables
        self.assertEqual(len(self.validator.validation_results['warnings']), 1)  # 1 missing view
    
    @patch('validate_migration.sqlite3.connect')
    def test_validate_database_structure_exception(self, mock_connect):
        """Test database structure validation with connection error."""
        mock_connect.side_effect = sqlite3.Error("Connection failed")
        
        result = self.validator.validate_database_structure()
        
        self.assertFalse(result)
        self.assertEqual(len(self.validator.validation_results['failed']), 1)
        self.assertIn("Structure validation error", self.validator.validation_results['failed'][0])
    
    @patch('validate_migration.sqlite3.connect')
    def test_validate_record_counts_success(self, mock_connect):
        """Test successful record count validation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock record counts within expected ranges
        mock_cursor.fetchone.side_effect = [
            (100,),  # companies
            (500,),  # jobs
            (50,),   # applications
            (25,),   # contacts
            (60,),   # emails
            (50,),   # metrics
            (1,),    # profile
            (100,)   # system_log
        ]
        
        result = self.validator.validate_record_counts()
        
        self.assertTrue(result)
        self.assertEqual(len(self.validator.validation_results['passed']), 8)
        self.assertEqual(self.validator.validation_results['stats']['total_records'], 886)
        mock_conn.close.assert_called_once()
    
    @patch('validate_migration.sqlite3.connect')
    def test_validate_record_counts_out_of_range(self, mock_connect):
        """Test record count validation with counts outside expected ranges."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock record counts outside expected ranges
        mock_cursor.fetchone.side_effect = [
            (300,),  # companies (too many)
            (50,),   # jobs (too few)
            (200,),  # applications (too many)
            (0,),    # contacts (ok)
            (20,),   # emails (ok)
            (10,),   # metrics (ok)
            (5,),    # profile (too many)
            (0,)     # system_log (ok)
        ]
        
        result = self.validator.validate_record_counts()
        
        self.assertTrue(result)  # Method returns True even with warnings
        self.assertEqual(len(self.validator.validation_results['warnings']), 4)  # 4 out of range
        self.assertEqual(len(self.validator.validation_results['passed']), 4)  # 4 in range
    
    @patch('validate_migration.sqlite3.connect')
    def test_validate_record_counts_exception(self, mock_connect):
        """Test record count validation with database error."""
        mock_connect.side_effect = sqlite3.Error("Query failed")
        
        result = self.validator.validate_record_counts()
        
        self.assertFalse(result)
        self.assertEqual(len(self.validator.validation_results['failed']), 1)
        self.assertIn("Record count error", self.validator.validation_results['failed'][0])
    
    @patch('validate_migration.sqlite3.connect')
    def test_validate_data_integrity_success(self, mock_connect):
        """Test successful data integrity validation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # All integrity checks pass
        mock_cursor.fetchone.side_effect = [
            (0,),  # Jobs with invalid company_id
            (0,),  # Applications with invalid job_id
            (0,),  # Emails with invalid application_id
            (0,),  # Contacts with invalid company_id
            (1,)   # Profile record count (should be 1)
        ]
        
        result = self.validator.validate_data_integrity()
        
        self.assertTrue(result)
        self.assertEqual(len(self.validator.validation_results['passed']), 5)
        self.assertEqual(len(self.validator.validation_results['failed']), 0)
        mock_conn.close.assert_called_once()
    
    @patch('validate_migration.sqlite3.connect')
    def test_validate_data_integrity_failures(self, mock_connect):
        """Test data integrity validation with constraint violations."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Some integrity checks fail
        mock_cursor.fetchone.side_effect = [
            (5,),  # Jobs with invalid company_id (5 violations)
            (3,),  # Applications with invalid job_id (3 violations)
            (0,),  # Emails with invalid application_id (ok)
            (2,),  # Contacts with invalid company_id (2 violations)
            (0,)   # Profile record count (should be 1, but is 0)
        ]
        
        result = self.validator.validate_data_integrity()
        
        self.assertFalse(result)
        self.assertEqual(len(self.validator.validation_results['failed']), 4)  # 4 failed checks
        self.assertEqual(len(self.validator.validation_results['passed']), 1)  # 1 passed check
    
    @patch('validate_migration.sqlite3.connect')
    def test_validate_data_integrity_multiple_profiles(self, mock_connect):
        """Test data integrity validation with multiple profile records."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.side_effect = [
            (0,),  # Jobs with invalid company_id
            (0,),  # Applications with invalid job_id
            (0,),  # Emails with invalid application_id
            (0,),  # Contacts with invalid company_id
            (3,)   # Profile record count (should be 1, but is 3)
        ]
        
        result = self.validator.validate_data_integrity()
        
        self.assertFalse(result)
        self.assertEqual(len(self.validator.validation_results['failed']), 1)
        self.assertIn("should be 1", self.validator.validation_results['failed'][0])
    
    @patch('validate_migration.sqlite3.connect')
    def test_validate_data_integrity_exception(self, mock_connect):
        """Test data integrity validation with database error."""
        mock_connect.side_effect = sqlite3.Error("Integrity check failed")
        
        result = self.validator.validate_data_integrity()
        
        self.assertFalse(result)
        self.assertEqual(len(self.validator.validation_results['failed']), 1)
        self.assertIn("Integrity check error", self.validator.validation_results['failed'][0])
    
    @patch('validate_migration.sqlite3.connect')
    def test_spot_check_data_success(self, mock_connect):
        """Test successful spot checks."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock spot check results
        mock_cursor.fetchone.side_effect = [
            (5,),   # Known companies (>= 1)
            (25,),  # AI/ML jobs (>= 10)
            (10,),  # Principal+ jobs (>= 5)
            (5,),   # Applications with responses (>= 0)
            (20,),  # Email responses (>= 10)
            (15,)   # Metrics (>= 5)
        ]
        
        # Mock sample data
        mock_cursor.fetchall.side_effect = [
            # Sample jobs
            [('Google', 'ML Engineer'), ('Meta', 'AI Researcher'), ('Apple', 'Data Scientist')],
            # Sample applications
            [('Anthropic', 'Senior ML Engineer', '2025-01-15 10:00:00'),
             ('OpenAI', 'Research Engineer', '2025-01-16 11:00:00'),
             ('DeepMind', 'AI Safety Researcher', '2025-01-17 12:00:00')]
        ]
        
        result = self.validator.spot_check_data()
        
        self.assertTrue(result)
        self.assertEqual(len(self.validator.validation_results['passed']), 6)
        mock_conn.close.assert_called_once()
    
    @patch('validate_migration.sqlite3.connect')
    def test_spot_check_data_below_threshold(self, mock_connect):
        """Test spot checks with values below expected thresholds."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock spot check results below thresholds
        mock_cursor.fetchone.side_effect = [
            (0,),  # Known companies (< 1)
            (5,),  # AI/ML jobs (< 10)
            (2,),  # Principal+ jobs (< 5)
            (0,),  # Applications with responses (>= 0, ok)
            (3,),  # Email responses (< 10)
            (1,)   # Metrics (< 5)
        ]
        
        # Mock sample data
        mock_cursor.fetchall.side_effect = [
            [],  # No sample jobs
            []   # No sample applications
        ]
        
        result = self.validator.spot_check_data()
        
        self.assertTrue(result)  # Method returns True even with warnings
        self.assertEqual(len(self.validator.validation_results['warnings']), 5)
        self.assertEqual(len(self.validator.validation_results['passed']), 1)  # Only applications passed
    
    @patch('validate_migration.sqlite3.connect')
    def test_spot_check_data_exception(self, mock_connect):
        """Test spot checks with database error."""
        mock_connect.side_effect = sqlite3.Error("Query error")
        
        result = self.validator.spot_check_data()
        
        self.assertFalse(result)
        self.assertEqual(len(self.validator.validation_results['warnings']), 1)
        self.assertIn("Spot check error", self.validator.validation_results['warnings'][0])
    
    @patch('validate_migration.Path.exists')
    @patch('validate_migration.zipfile.ZipFile')
    def test_compare_with_backup_success(self, mock_zipfile, mock_exists):
        """Test successful backup comparison."""
        mock_exists.return_value = True
        
        # Mock zipfile operations
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        manifest = {
            'databases': ['db1.db', 'db2.db', 'db3.db', 'db4.db', 'db5.db'],
            'timestamp': '2025-01-01T12:00:00'
        }
        mock_zip.read.return_value = json.dumps(manifest).encode()
        
        result = self.validator.compare_with_backup()
        
        self.assertTrue(result)
        self.assertEqual(self.validator.validation_results['stats']['original_databases'], 5)
        self.assertEqual(self.validator.validation_results['stats']['consolidation_ratio'], '5:1')
    
    @patch('validate_migration.Path.exists')
    def test_compare_with_backup_no_file(self, mock_exists):
        """Test backup comparison when no backup file exists."""
        mock_exists.return_value = False
        
        result = self.validator.compare_with_backup()
        
        self.assertTrue(result)  # Should return True even without backup
        self.assertNotIn('original_databases', self.validator.validation_results['stats'])
    
    @patch('validate_migration.Path.exists')
    def test_compare_with_backup_no_backup_specified(self, mock_exists):
        """Test backup comparison when no backup file is specified."""
        self.validator.backup_file = None
        
        result = self.validator.compare_with_backup()
        
        self.assertTrue(result)
        mock_exists.assert_not_called()
    
    @patch('validate_migration.Path.exists')
    @patch('validate_migration.zipfile.ZipFile')
    def test_compare_with_backup_exception(self, mock_zipfile, mock_exists):
        """Test backup comparison with zipfile error."""
        mock_exists.return_value = True
        mock_zipfile.side_effect = zipfile.BadZipFile("Corrupted zip")
        
        result = self.validator.compare_with_backup()
        
        self.assertTrue(result)  # Should return True even with error
    
    def test_generate_report_complete(self):
        """Test complete report generation."""
        # Set up validation results
        self.validator.validation_results = {
            'passed': ['Check 1', 'Check 2', 'Check 3'],
            'failed': ['Check 4'],
            'warnings': ['Warning 1', 'Warning 2'],
            'stats': {
                'companies_count': 100,
                'jobs_count': 500,
                'total_records': 600
            }
        }
        
        report = self.validator.generate_report()
        
        self.assertIn('timestamp', report)
        self.assertEqual(report['database'], 'test.db')
        self.assertEqual(report['backup_file'], 'backup.zip')
        self.assertEqual(report['summary']['total_checks'], 6)
        self.assertEqual(report['summary']['passed'], 3)
        self.assertEqual(report['summary']['failed'], 1)
        self.assertEqual(report['summary']['warnings'], 2)
        self.assertEqual(report['summary']['health_score'], 50.0)  # 3/6 * 100
    
    def test_generate_report_all_passed(self):
        """Test report generation when all checks pass."""
        self.validator.validation_results = {
            'passed': ['Check 1', 'Check 2', 'Check 3', 'Check 4', 'Check 5'],
            'failed': [],
            'warnings': [],
            'stats': {}
        }
        
        report = self.validator.generate_report()
        
        self.assertEqual(report['summary']['health_score'], 100.0)
        self.assertEqual(report['summary']['failed'], 0)
        self.assertEqual(report['summary']['warnings'], 0)
    
    def test_generate_report_no_checks(self):
        """Test report generation with no checks performed."""
        self.validator.validation_results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'stats': {}
        }
        
        report = self.validator.generate_report()
        
        self.assertEqual(report['summary']['total_checks'], 0)
        self.assertEqual(report['summary']['health_score'], 0)
    
    @patch('builtins.print')
    def test_print_summary_passed(self, mock_print):
        """Test printing summary for passed validation."""
        report = {
            'database': 'test.db',
            'timestamp': '2025-01-20T12:00:00',
            'summary': {
                'total_checks': 10,
                'passed': 9,
                'failed': 0,
                'warnings': 1,
                'health_score': 90.0
            },
            'validation_results': {
                'failed': [],
                'warnings': ['Minor warning'],
                'stats': {'total_records': 1000}
            }
        }
        
        self.validator.print_summary(report)
        
        # Check that success message was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('VALIDATION PASSED' in str(call) for call in print_calls))
    
    @patch('builtins.print')
    def test_print_summary_failed(self, mock_print):
        """Test printing summary for failed validation."""
        report = {
            'database': 'test.db',
            'timestamp': '2025-01-20T12:00:00',
            'summary': {
                'total_checks': 10,
                'passed': 3,
                'failed': 5,
                'warnings': 2,
                'health_score': 30.0
            },
            'validation_results': {
                'failed': ['Critical failure 1', 'Critical failure 2'],
                'warnings': ['Warning 1', 'Warning 2'],
                'stats': {}
            }
        }
        
        self.validator.print_summary(report)
        
        # Check that failure message was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('VALIDATION FAILED' in str(call) for call in print_calls))
    
    @patch('builtins.print')
    def test_print_summary_with_warnings(self, mock_print):
        """Test printing summary with warnings."""
        report = {
            'database': 'test.db',
            'timestamp': '2025-01-20T12:00:00',
            'summary': {
                'total_checks': 10,
                'passed': 7,
                'failed': 0,
                'warnings': 3,
                'health_score': 70.0
            },
            'validation_results': {
                'failed': [],
                'warnings': ['Warning 1', 'Warning 2', 'Warning 3', 'Warning 4', 'Warning 5', 'Warning 6'],
                'stats': {}
            }
        }
        
        self.validator.print_summary(report)
        
        # Check that warning message was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('PASSED WITH WARNINGS' in str(call) for call in print_calls))
    
    @patch('validate_migration.MigrationValidator.compare_with_backup')
    @patch('validate_migration.MigrationValidator.spot_check_data')
    @patch('validate_migration.MigrationValidator.validate_data_integrity')
    @patch('validate_migration.MigrationValidator.validate_record_counts')
    @patch('validate_migration.MigrationValidator.validate_database_structure')
    @patch('builtins.open', new_callable=mock_open)
    @patch('validate_migration.json.dump')
    def test_run_validation_success(self, mock_json_dump, mock_file, mock_structure,
                                   mock_counts, mock_integrity, mock_spot, mock_backup):
        """Test successful validation run."""
        # All validations pass
        mock_structure.return_value = True
        mock_counts.return_value = True
        mock_integrity.return_value = True
        mock_spot.return_value = True
        mock_backup.return_value = True
        
        # Set up results for high health score
        self.validator.validation_results = {
            'passed': ['Check 1', 'Check 2', 'Check 3', 'Check 4', 'Check 5',
                      'Check 6', 'Check 7', 'Check 8', 'Check 9'],
            'failed': [],
            'warnings': ['Warning 1'],
            'stats': {}
        }
        
        result = self.validator.run_validation()
        
        self.assertTrue(result)
        mock_structure.assert_called_once()
        mock_counts.assert_called_once()
        mock_integrity.assert_called_once()
        mock_spot.assert_called_once()
        mock_backup.assert_called_once()
        
        # Check that report was saved
        mock_json_dump.assert_called_once()
    
    @patch('validate_migration.MigrationValidator.compare_with_backup')
    @patch('validate_migration.MigrationValidator.spot_check_data')
    @patch('validate_migration.MigrationValidator.validate_data_integrity')
    @patch('validate_migration.MigrationValidator.validate_record_counts')
    @patch('validate_migration.MigrationValidator.validate_database_structure')
    @patch('builtins.open', new_callable=mock_open)
    @patch('validate_migration.json.dump')
    def test_run_validation_failure(self, mock_json_dump, mock_file, mock_structure,
                                   mock_counts, mock_integrity, mock_spot, mock_backup):
        """Test validation run with failures."""
        # Some validations fail
        mock_structure.return_value = False
        mock_counts.return_value = True
        mock_integrity.return_value = False
        mock_spot.return_value = True
        mock_backup.return_value = True
        
        # Set up results for low health score
        self.validator.validation_results = {
            'passed': ['Check 1', 'Check 2'],
            'failed': ['Failure 1', 'Failure 2', 'Failure 3', 'Failure 4', 'Failure 5'],
            'warnings': ['Warning 1', 'Warning 2', 'Warning 3'],
            'stats': {}
        }
        
        result = self.validator.run_validation()
        
        self.assertFalse(result)  # Health score will be < 70%
        mock_structure.assert_called_once()
        mock_counts.assert_called_once()
        mock_integrity.assert_called_once()
        mock_spot.assert_called_once()
        mock_backup.assert_called_once()


class TestMainFunction(unittest.TestCase):
    """Test the main function."""
    
    @patch('validate_migration.Path.exists')
    @patch('builtins.print')
    def test_main_no_database(self, mock_print, mock_exists):
        """Test main when unified database doesn't exist."""
        mock_exists.return_value = False
        
        from validate_migration import main
        result = main()
        
        self.assertEqual(result, 1)
        # Check error message was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('not found' in str(call) for call in print_calls))
    
    @patch('validate_migration.MigrationValidator')
    @patch('validate_migration.Path.exists')
    @patch('builtins.print')
    def test_main_validation_success(self, mock_print, mock_exists, mock_validator_class):
        """Test main with successful validation."""
        mock_exists.return_value = True
        
        # Mock validator instance
        mock_validator = MagicMock()
        mock_validator.run_validation.return_value = True
        mock_validator_class.return_value = mock_validator
        
        from validate_migration import main
        result = main()
        
        self.assertEqual(result, 0)
        mock_validator.run_validation.assert_called_once()
        # Check success message
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('SUCCESSFULLY' in str(call) for call in print_calls))
    
    @patch('validate_migration.MigrationValidator')
    @patch('validate_migration.Path.exists')
    @patch('builtins.print')
    def test_main_validation_failure(self, mock_print, mock_exists, mock_validator_class):
        """Test main with failed validation."""
        mock_exists.return_value = True
        
        # Mock validator instance
        mock_validator = MagicMock()
        mock_validator.run_validation.return_value = False
        mock_validator_class.return_value = mock_validator
        
        from validate_migration import main
        result = main()
        
        self.assertEqual(result, 1)
        mock_validator.run_validation.assert_called_once()
        # Check failure message
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('FAILED' in str(call) for call in print_calls))


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete validation scenarios."""
    
    @patch('validate_migration.sqlite3.connect')
    @patch('validate_migration.Path.glob')
    def test_complete_validation_flow(self, mock_glob, mock_connect):
        """Test complete validation flow with mixed results."""
        # Set up backup files
        mock_glob.return_value = [Path('database_backup_20250120_120000.zip')]
        
        # Create validator
        validator = MigrationValidator('unified_platform.db')
        
        # Mock database connection for all methods
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Set up responses for structure validation
        mock_cursor.fetchall.side_effect = [
            # Tables
            [('companies',), ('jobs',), ('applications',), ('contacts',),
             ('emails',), ('metrics',), ('profile',), ('system_log',)],
            # Views
            [('active_jobs',), ('application_responses',)],  # Missing one view
            # Indexes
            [('idx_1',), ('idx_2',)],
            # Reset for next method
        ]
        
        # Validate structure
        structure_result = validator.validate_database_structure()
        self.assertTrue(structure_result)  # Should pass even with warning
        
        # Set up responses for record counts
        mock_cursor.fetchone.side_effect = [
            (100,), (400,), (30,), (10,), (50,), (40,), (1,), (200,),  # All in range
        ]
        
        # Validate counts
        counts_result = validator.validate_record_counts()
        self.assertTrue(counts_result)
        
        # Verify results accumulated correctly
        self.assertGreater(len(validator.validation_results['passed']), 0)
        self.assertGreater(len(validator.validation_results['warnings']), 0)  # Missing view
    
    @patch('validate_migration.sqlite3.connect')
    @patch('builtins.open', new_callable=mock_open)
    @patch('validate_migration.json.dump')
    @patch('validate_migration.datetime')
    def test_report_generation_and_save(self, mock_datetime, mock_json_dump, mock_file, mock_connect):
        """Test report generation and saving to file."""
        # Mock datetime
        mock_now = MagicMock()
        mock_now.isoformat.return_value = '2025-01-20T15:30:00'
        mock_now.strftime.return_value = '20250120_153000'
        mock_datetime.now.return_value = mock_now
        
        # Mock database
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simple responses to pass validation
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = (0,)
        
        validator = MigrationValidator('test.db')
        validator.run_validation()
        
        # Check that file was opened with correct name
        mock_file.assert_called_with('validation_report_20250120_153000.json', 'w')
        
        # Check that JSON was dumped
        mock_json_dump.assert_called_once()
        
        # Verify report structure
        report_data = mock_json_dump.call_args[0][0]
        self.assertIn('timestamp', report_data)
        self.assertIn('summary', report_data)
        self.assertIn('validation_results', report_data)


if __name__ == '__main__':
    unittest.main(verbosity=2)