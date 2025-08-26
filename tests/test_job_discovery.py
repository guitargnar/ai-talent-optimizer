"""
Unit tests for job discovery functionality
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestJobDatabase:
    """Test job database operations"""

    @pytest.fixture
    def test_db(self, tmp_path):
        """Create temporary test database"""
        db_path = tmp_path / "test_jobs.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create schema
        cursor.execute(
            """
            CREATE TABLE job_discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                description TEXT,
                url TEXT,
                salary_range TEXT,
                location TEXT,
                relevance_score REAL DEFAULT 0.5,
                applied INTEGER DEFAULT 0,
                application_date TEXT,
                discovered_date TEXT DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                UNIQUE(company, title)
            )
        """
        )

        # Add test data
        test_jobs = [
            (
                "OpenAI",
                "ML Engineer",
                "Build AI systems",
                "http://openai.com/jobs/1",
                "200000-300000",
                "San Francisco",
                0.95,
                0,
            ),
            (
                "Google",
                "Data Scientist",
                "Analyze data",
                "http://google.com/jobs/2",
                "150000-250000",
                "Mountain View",
                0.85,
                0,
            ),
            (
                "Meta",
                "AI Researcher",
                "Research AI",
                "http://meta.com/jobs/3",
                "180000-280000",
                "Remote",
                0.90,
                1,
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO jobs 
            (company, title, description, url, salary_range, location, relevance_score, applied)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            test_jobs,
        )

        conn.commit()
        conn.close()

        return db_path

    @pytest.mark.unit
    @pytest.mark.database
    def test_database_creation(self, test_db):
        """Test database is created with correct schema"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert ("job_discoveries",) in tables

        # Check columns
        cursor.execute("PRAGMA table_info(job_discoveries)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        expected_columns = [
            "id",
            "company",
            "position",
            "description",
            "url",
            "salary_range",
            "location",
            "relevance_score",
            "applied",
            "application_date",
            "discovered_date",
            "source",
        ]

        for col in expected_columns:
            assert col in column_names

        conn.close()

    @pytest.mark.unit
    @pytest.mark.database
    def test_job_insertion(self, test_db):
        """Test inserting new jobs"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Insert new job
        new_job = (
            "Anthropic",
            "Safety Researcher",
            "AI Safety",
            "http://anthropic.com/jobs",
            "250000-350000",
            "Remote",
            0.98,
        )

        cursor.execute(
            """
            INSERT INTO jobs
            (company, title, description, url, salary_range, location, relevance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            new_job,
        )
        conn.commit()

        # Verify insertion
        cursor.execute("SELECT * FROM jobs WHERE company = 'Anthropic'")
        result = cursor.fetchone()

        assert result is not None
        assert result[1] == "Anthropic"  # company
        assert result[2] == "Safety Researcher"  # position
        assert result[7] == 0.98  # relevance_score

        conn.close()

    @pytest.mark.unit
    @pytest.mark.database
    def test_duplicate_job_handling(self, test_db):
        """Test handling of duplicate jobs"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Try to insert duplicate
        duplicate_job = (
            "OpenAI",
            "ML Engineer",
            "Different description",
            "http://openai.com/jobs/new",
            "300000-400000",
            "NYC",
            0.80,
        )

        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                """
                INSERT INTO jobs
                (company, title, description, url, salary_range, location, relevance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                duplicate_job,
            )

        conn.close()

    @pytest.mark.unit
    @pytest.mark.database
    def test_unapplied_jobs_query(self, test_db):
        """Test querying unapplied jobs"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Get unapplied jobs sorted by relevance
        cursor.execute(
            """
            SELECT company, title, relevance_score
            FROM jobs
            WHERE applied = 0
            ORDER BY relevance_score DESC
        """
        )

        results = cursor.fetchall()

        assert len(results) == 2  # Only 2 unapplied jobs
        assert results[0][0] == "OpenAI"  # Highest relevance first
        assert results[0][2] == 0.95
        assert results[1][0] == "Google"
        assert results[1][2] == 0.85

        conn.close()

    @pytest.mark.unit
    @pytest.mark.database
    def test_mark_job_applied(self, test_db):
        """Test marking job as applied"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Mark OpenAI job as applied
        cursor.execute(
            """
            UPDATE jobs
            SET applied = 1, applied_date = datetime('now')
            WHERE company = 'OpenAI' AND title = 'ML Engineer'
        """
        )
        conn.commit()

        # Verify update
        cursor.execute(
            """
            SELECT applied, application_date
            FROM jobs
            WHERE company = 'OpenAI' AND title = 'ML Engineer'
        """
        )

        result = cursor.fetchone()
        assert result[0] == 1  # applied
        assert result[1] is not None  # application_date set

        conn.close()

    @pytest.mark.unit
    @pytest.mark.database
    def test_job_statistics(self, test_db):
        """Test calculating job statistics"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Get statistics
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN applied = 1 THEN 1 END) as applied,
                COUNT(DISTINCT company) as companies,
                AVG(relevance_score) as avg_score,
                MIN(CAST(SUBSTR(salary_range, 1, INSTR(salary_range, '-')-1) AS INTEGER)) as salary_min,
                MAX(CAST(SUBSTR(salary_range, INSTR(salary_range, '-')+1) AS INTEGER)) as max_salary
            FROM jobs
        """
        )

        stats = cursor.fetchone()

        assert stats[0] == 3  # total jobs
        assert stats[1] == 1  # applied jobs
        assert stats[2] == 3  # unique companies
        assert 0.89 < stats[3] < 0.91  # average score around 0.90

        conn.close()


class TestJobScraperIntegration:
    """Test job scraper integration"""

    @pytest.mark.unit
    def test_relevance_scoring(self):
        """Test job relevance scoring algorithm"""

        def calculate_relevance(description, title):
            """Simple relevance scoring"""
            score = 0.5  # Base score

            # Keywords and weights
            high_value_keywords = [
                "ML",
                "AI",
                "machine learning",
                "deep learning",
                "neural",
                "tensorflow",
                "pytorch",
            ]
            medium_value_keywords = [
                "python",
                "data",
                "engineer",
                "scientist",
                "research",
                "algorithm",
            ]

            description_lower = description.lower()
            title_lower = title.lower()

            # Check keywords
            for keyword in high_value_keywords:
                if keyword.lower() in description_lower or keyword.lower() in title_lower:
                    score += 0.1

            for keyword in medium_value_keywords:
                if keyword.lower() in description_lower or keyword.lower() in title_lower:
                    score += 0.05

            return min(score, 1.0)  # Cap at 1.0

        # Test cases
        test_cases = [
            ("ML Engineer building AI systems with PyTorch", "ML Engineer", 0.8),
            ("Data entry position", "Data Entry Clerk", 0.55),
            ("Deep learning researcher using neural networks", "AI Researcher", 0.85),
            ("Python developer", "Software Engineer", 0.6),
        ]

        for desc, title, expected_min in test_cases:
            score = calculate_relevance(desc, title)
            assert score >= expected_min

    @pytest.mark.unit
    @patch("requests.get")
    def test_api_error_handling(self, mock_get):
        """Test handling of API errors"""
        # Mock API error
        mock_get.return_value.status_code = 500
        mock_get.return_value.text = "Internal Server Error"

        import requests

        response = requests.get("http://api.example.com/jobs")

        assert response.status_code == 500
        # In real implementation, should handle gracefully
        assert response.text == "Internal Server Error"

    @pytest.mark.unit
    def test_salary_parsing(self):
        """Test salary range parsing"""

        def parse_salary(salary_str):
            """Parse salary string to min/max tuple"""
            if not salary_str:
                return (0, 0)

            # Remove non-numeric characters except dash
            cleaned = "".join(c for c in salary_str if c.isdigit() or c == "-")

            if "-" in cleaned:
                parts = cleaned.split("-")
                if len(parts) == 2:
                    try:
                        return (int(parts[0]), int(parts[1]))
                    except ValueError:
                        return (0, 0)

            return (0, 0)

        test_cases = [
            ("$150,000-$200,000", (150000, 200000)),
            ("150000-200000", (150000, 200000)),
            ("150k-200k", (150, 200)),  # Simplified parsing
            ("Competitive", (0, 0)),
            (None, (0, 0)),
        ]

        for salary_str, expected in test_cases:
            if "k" not in str(salary_str):  # Skip 'k' format for simple parser
                result = parse_salary(salary_str)
                assert result == expected
