"""
Unit tests for database migration functionality
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from migrate_data import DatabaseMigrator


class TestDatabaseMigrator:
    """Test database migration functionality"""
    
    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for test databases"""
        return tmp_path
    
    @pytest.fixture
    def test_migrator(self, temp_dir):
        """Create test migrator instance"""
        migrator = DatabaseMigrator(target_db=str(temp_dir / "test_unified.db"))
        migrator.source_databases = []  # Start with empty list
        return migrator
    
    @pytest.fixture
    def sample_source_db(self, temp_dir):
        """Create sample source database"""
        db_path = temp_dir / "source.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create sample tables
        cursor.execute("""
            CREATE TABLE companies (
                id INTEGER PRIMARY KEY,
                name TEXT,
                industry TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY,
                company TEXT,
                title TEXT,
                salary INTEGER
            )
        """)
        
        # Insert sample data
        cursor.execute("INSERT INTO companies VALUES (1, 'Google', 'Tech')")
        cursor.execute("INSERT INTO companies VALUES (2, 'Meta', 'Tech')")
        cursor.execute("INSERT INTO jobs VALUES (1, 'Google', 'Engineer', 150000)")
        cursor.execute("INSERT INTO jobs VALUES (2, 'Meta', 'Scientist', 180000)")
        
        conn.commit()
        conn.close()
        return str(db_path)
    
    @pytest.mark.unit
    def test_migrator_initialization(self, test_migrator):
        """Test migrator initialization"""
        assert test_migrator.target_db.endswith("test_unified.db")
        assert test_migrator.dedup_stats == {'total': 0, 'unique': 0, 'duplicates': 0}
        assert isinstance(test_migrator.migration_log, dict)
    
    @pytest.mark.unit
    def test_normalize_company_name(self, test_migrator):
        """Test company name normalization"""
        test_cases = [
            ("Google Inc.", "Google"),
            ("Meta LLC", "Meta"),
            ("openai", "Openai"),
            ("  Anthropic  ", "Anthropic"),
            ("Microsoft Corporation", "Microsoft"),
            ("amazon.com Inc", "Amazon.Com"),
        ]
        
        for input_name, expected in test_cases:
            result = test_migrator.normalize_company_name(input_name)
            assert result == expected
    
    @pytest.mark.unit
    def test_normalize_job_title(self, test_migrator):
        """Test job title normalization"""
        test_cases = [
            ("Senior ML Engineer", "Senior ML Engineer"),
            ("sr. engineer", "Senior Engineer"),
            ("lead data scientist", "Lead Data Scientist"),
            ("  Machine Learning  ", "Machine Learning"),
            ("VP of Engineering", "VP Engineering"),
        ]
        
        for input_title, expected in test_cases:
            result = test_migrator.normalize_job_title(input_title)
            assert result == expected
    
    @pytest.mark.unit
    def test_extract_salary_range(self, test_migrator):
        """Test salary range extraction"""
        test_cases = [
            ("150000-200000", (150000, 200000)),
            ("$150,000 - $200,000", (150000, 200000)),
            ("150k-200k", (150000, 200000)),
            ("400K+", (400000, None)),
            ("Not specified", (None, None)),
            (None, (None, None)),
        ]
        
        for input_range, expected in test_cases:
            result = test_migrator.extract_salary_range(input_range)
            assert result == expected
    
    @pytest.mark.unit
    def test_create_unified_database(self, test_migrator, temp_dir):
        """Test unified database creation"""
        test_migrator.target_db = str(temp_dir / "unified.db")
        test_migrator.create_unified_database()
        
        # Verify database was created
        assert Path(test_migrator.target_db).exists()
        
        # Verify tables were created
        conn = sqlite3.connect(test_migrator.target_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['companies', 'jobs', 'applications', 'contacts', 
                         'emails', 'metrics', 'profile', 'system_log']
        
        for table in expected_tables:
            assert table in tables
        
        conn.close()
    
    @pytest.mark.unit
    def test_migrate_companies(self, test_migrator, sample_source_db, temp_dir):
        """Test company migration"""
        test_migrator.target_db = str(temp_dir / "unified.db")
        test_migrator.create_unified_database()
        
        # Mock source database info
        source_conn = sqlite3.connect(sample_source_db)
        target_conn = sqlite3.connect(test_migrator.target_db)
        
        # Migrate companies
        count = test_migrator.migrate_companies(source_conn, target_conn, 
                                                Path(sample_source_db).name)
        
        assert count == 2
        
        # Verify migrated data
        cursor = target_conn.cursor()
        cursor.execute("SELECT name FROM companies ORDER BY name")
        companies = [row[0] for row in cursor.fetchall()]
        
        assert companies == ['Google', 'Meta']
        
        source_conn.close()
        target_conn.close()
    
    @pytest.mark.unit
    def test_deduplication(self, test_migrator):
        """Test deduplication logic"""
        test_migrator.company_map = {}
        
        # First company should be added
        result1 = test_migrator.is_duplicate_company("Google", test_migrator.company_map)
        assert result1 is False
        test_migrator.company_map["google"] = 1
        
        # Duplicate should be detected
        result2 = test_migrator.is_duplicate_company("Google Inc", test_migrator.company_map)
        assert result2 is True
        
        # Different company should not be duplicate
        result3 = test_migrator.is_duplicate_company("Meta", test_migrator.company_map)
        assert result3 is False
    
    @pytest.mark.unit  
    def test_backup_creation(self, test_migrator, sample_source_db, temp_dir):
        """Test backup creation"""
        test_migrator.backup_dir = str(temp_dir / "backup")
        test_migrator.source_databases = [sample_source_db]
        
        # Create backup
        with patch('zipfile.ZipFile') as mock_zip:
            mock_zip_instance = MagicMock()
            mock_zip.return_value.__enter__.return_value = mock_zip_instance
            
            test_migrator.create_backup()
            
            # Verify backup was attempted
            assert mock_zip.called
    
    @pytest.mark.unit
    def test_migration_summary(self, test_migrator):
        """Test migration summary generation"""
        test_migrator.migration_log = {
            'source.db': {
                'companies': 10,
                'jobs': 50,
                'applications': 5
            }
        }
        
        test_migrator.dedup_stats = {
            'total': 65,
            'unique': 45,
            'duplicates': 20
        }
        
        summary = test_migrator.generate_summary()
        
        assert summary['total_records_processed'] == 65
        assert summary['unique_records_migrated'] == 45
        assert summary['duplicates_removed'] == 20
        assert summary['deduplication_rate'] == pytest.approx(30.77, rel=0.01)
    
    @pytest.mark.unit
    def test_error_handling(self, test_migrator, temp_dir):
        """Test error handling during migration"""
        # Test with non-existent database
        bad_db_path = str(temp_dir / "nonexistent.db")
        test_migrator.source_databases = [bad_db_path]
        
        # Should handle missing database gracefully
        result = test_migrator.run_migration()
        assert result is True  # Migration completes even with missing DBs
    
    @pytest.mark.integration
    def test_full_migration_flow(self, test_migrator, sample_source_db, temp_dir):
        """Test complete migration flow"""
        test_migrator.target_db = str(temp_dir / "final_unified.db")
        test_migrator.source_databases = [sample_source_db]
        
        # Run full migration
        result = test_migrator.run_migration()
        assert result is True
        
        # Verify target database exists
        assert Path(test_migrator.target_db).exists()
        
        # Verify data was migrated
        conn = sqlite3.connect(test_migrator.target_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM companies")
        company_count = cursor.fetchone()[0]
        assert company_count > 0
        
        conn.close()


class TestMigrationHelpers:
    """Test helper functions"""
    
    @pytest.mark.unit
    def test_is_duplicate_company():
        """Test duplicate company detection"""
        migrator = DatabaseMigrator()
        seen = {}
        
        # Add first company
        assert migrator.is_duplicate_company("Google", seen) is False
        seen["google"] = 1
        
        # Check duplicate
        assert migrator.is_duplicate_company("Google Inc", seen) is True
        assert migrator.is_duplicate_company("GOOGLE", seen) is True
        
        # Check different company
        assert migrator.is_duplicate_company("Anthropic", seen) is False
    
    @pytest.mark.unit
    def test_generate_unique_id():
        """Test unique ID generation"""
        migrator = DatabaseMigrator()
        
        id1 = migrator.generate_job_id("Google", "Engineer", "source.db")
        id2 = migrator.generate_job_id("Google", "Engineer", "source.db")
        id3 = migrator.generate_job_id("Meta", "Engineer", "source.db")
        
        # Same inputs should generate same ID
        assert id1 == id2
        
        # Different inputs should generate different ID
        assert id1 != id3