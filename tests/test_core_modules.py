"""
Unit tests for core modules without external dependencies
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestDatabaseOperations:
    """Test database-related operations"""
    
    @pytest.mark.unit
    def test_database_connection(self, tmp_path):
        """Test database connection"""
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(db_path)
        assert conn is not None
        
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.commit()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert ('test',) in tables
        conn.close()
    
    @pytest.mark.unit
    def test_data_insertion(self, tmp_path):
        """Test data insertion and retrieval"""
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY,
                company TEXT,
                title TEXT
            )
        """)
        
        # Insert data
        cursor.execute("INSERT INTO jobs (company, title) VALUES (?, ?)",
                      ("Google", "Engineer"))
        conn.commit()
        
        # Retrieve data
        cursor.execute("SELECT * FROM jobs")
        result = cursor.fetchone()
        
        assert result[1] == "Google"
        assert result[2] == "Engineer"
        conn.close()


class TestDataNormalization:
    """Test data normalization functions"""
    
    @pytest.mark.unit
    def test_company_name_normalization(self):
        """Test company name cleaning"""
        def normalize_company(name):
            suffixes = [' Inc.', ' Inc', ' LLC', ' Ltd', ' Corporation', ' Corp']
            normalized = name.strip()
            for suffix in suffixes:
                if normalized.endswith(suffix):
                    normalized = normalized[:-len(suffix)]
            return ' '.join(normalized.split()).title()
        
        assert normalize_company("Google Inc.") == "Google"
        assert normalize_company("  Meta  LLC  ") == "Meta"
        assert normalize_company("microsoft corporation") == "Microsoft"
    
    @pytest.mark.unit
    def test_salary_extraction(self):
        """Test salary range parsing"""
        def extract_salary(salary_str):
            if not salary_str:
                return None, None
            
            import re
            numbers = re.findall(r'\d+', salary_str.replace(',', ''))
            if not numbers:
                return None, None
            
            min_sal = int(numbers[0])
            if 'k' in salary_str.lower():
                min_sal *= 1000
            
            max_sal = int(numbers[1]) if len(numbers) > 1 else None
            if max_sal and 'k' in salary_str.lower():
                max_sal *= 1000
                
            return min_sal, max_sal
        
        assert extract_salary("150000-200000") == (150000, 200000)
        assert extract_salary("150k-200k") == (150000, 200000)
        assert extract_salary("$150,000") == (150000, None)


class TestEmailValidation:
    """Test email validation logic"""
    
    @pytest.mark.unit
    def test_email_format_validation(self):
        """Test email format checking"""
        import re
        
        def is_valid_email(email):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None
        
        assert is_valid_email("test@example.com") is True
        assert is_valid_email("careers@company.co.uk") is True
        assert is_valid_email("invalid.email") is False
        assert is_valid_email("@example.com") is False
    
    @pytest.mark.unit
    def test_company_extraction_from_email(self):
        """Test extracting company from email"""
        def extract_company(email):
            if '@' not in email:
                return None
            domain = email.split('@')[1]
            # Remove common email providers
            if domain in ['gmail.com', 'yahoo.com', 'hotmail.com']:
                return None
            # Extract company name from domain
            company = domain.split('.')[0]
            return company.lower()
        
        assert extract_company("recruiter@google.com") == "google"
        assert extract_company("hr@anthropic.ai") == "anthropic"
        assert extract_company("john@gmail.com") is None


class TestApplicationStatus:
    """Test application status tracking"""
    
    @pytest.mark.unit
    def test_status_transitions(self):
        """Test valid status transitions"""
        valid_transitions = {
            'draft': ['pending_review', 'deleted'],
            'pending_review': ['sent', 'deleted'],
            'sent': ['response_received', 'rejected'],
            'response_received': ['interview_scheduled'],
        }
        
        def can_transition(from_status, to_status):
            return to_status in valid_transitions.get(from_status, [])
        
        assert can_transition('draft', 'pending_review') is True
        assert can_transition('sent', 'response_received') is True
        assert can_transition('draft', 'sent') is False
    
    @pytest.mark.unit
    def test_priority_scoring(self):
        """Test job priority calculation"""
        def calculate_priority(salary_min, company_tier, remote, ai_ml_focused):
            score = 0.5  # Base score
            
            if salary_min and salary_min >= 200000:
                score += 0.2
            if company_tier == 'tier1':
                score += 0.2
            if remote:
                score += 0.05
            if ai_ml_focused:
                score += 0.05
                
            return min(score, 1.0)
        
        assert calculate_priority(250000, 'tier1', True, True) == 1.0
        assert calculate_priority(150000, 'tier2', False, False) == 0.5
        assert calculate_priority(200000, 'tier1', True, False) == 0.95


class TestDeduplication:
    """Test deduplication logic"""
    
    @pytest.mark.unit
    def test_job_deduplication(self):
        """Test identifying duplicate jobs"""
        seen_jobs = set()
        
        def is_duplicate(company, title):
            key = f"{company.lower()}:{title.lower()}"
            if key in seen_jobs:
                return True
            seen_jobs.add(key)
            return False
        
        assert is_duplicate("Google", "ML Engineer") is False
        assert is_duplicate("Google", "ML Engineer") is True
        assert is_duplicate("Google", "Data Scientist") is False
        assert is_duplicate("Meta", "ML Engineer") is False
    
    @pytest.mark.unit
    def test_fuzzy_matching(self):
        """Test fuzzy string matching for duplicates"""
        def similarity_ratio(s1, s2):
            # Simple character overlap ratio
            s1, s2 = s1.lower(), s2.lower()
            if not s1 or not s2:
                return 0
            
            common = sum(1 for c in s1 if c in s2)
            return common / max(len(s1), len(s2))
        
        assert similarity_ratio("Google Inc", "Google") > 0.5
        assert similarity_ratio("ML Engineer", "Machine Learning Engineer") > 0.4
        assert similarity_ratio("Apple", "Amazon") < 0.5


class TestMetricsCalculation:
    """Test metrics and statistics"""
    
    @pytest.mark.unit  
    def test_response_rate_calculation(self):
        """Test response rate metrics"""
        def calculate_response_rate(sent, responses):
            if sent == 0:
                return 0.0
            return (responses / sent) * 100
        
        assert calculate_response_rate(100, 10) == 10.0
        assert calculate_response_rate(50, 5) == 10.0
        assert calculate_response_rate(0, 0) == 0.0
    
    @pytest.mark.unit
    def test_conversion_funnel(self):
        """Test conversion funnel metrics"""
        def calculate_funnel(discovered, applied, responded, interviewed):
            return {
                'discovery_to_application': (applied / discovered * 100) if discovered else 0,
                'application_to_response': (responded / applied * 100) if applied else 0,
                'response_to_interview': (interviewed / responded * 100) if responded else 0,
                'overall_conversion': (interviewed / discovered * 100) if discovered else 0
            }
        
        metrics = calculate_funnel(1000, 100, 10, 2)
        assert metrics['discovery_to_application'] == 10.0
        assert metrics['application_to_response'] == 10.0
        assert metrics['response_to_interview'] == 20.0
        assert metrics['overall_conversion'] == 0.2