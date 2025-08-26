"""
Unit tests for orchestrator module
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, call

import pytest

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestOrchestrator:
    """Test orchestrator functionality"""
    
    @pytest.fixture
    def mock_db(self, tmp_path):
        """Create mock database"""
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create minimal schema
        cursor.execute("""
            CREATE TABLE applications (
                id INTEGER PRIMARY KEY,
                company_name TEXT,
                position TEXT,
                status TEXT,
                applied_date TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY,
                company TEXT,
                title TEXT,
                priority_score REAL
            )
        """)
        
        conn.commit()
        conn.close()
        return str(db_path)
    
    @pytest.mark.unit
    @patch('orchestrator.JobDiscoveryEngine')
    @patch('orchestrator.ContentGenerator')
    @patch('orchestrator.ApplicationReviewer')
    def test_orchestrator_init(self, mock_reviewer, mock_generator, mock_discovery):
        """Test orchestrator initialization"""
        from orchestrator import StrategicOrchestrator
        
        with patch('orchestrator.Path.exists', return_value=True):
            orchestrator = StrategicOrchestrator()
            
            assert orchestrator.db_path == "unified_platform.db"
            assert mock_discovery.called
            assert mock_generator.called
            assert mock_reviewer.called
    
    @pytest.mark.unit
    def test_discover_jobs(self, mock_db):
        """Test job discovery"""
        from orchestrator import StrategicOrchestrator
        
        with patch('orchestrator.Path.exists', return_value=True):
            with patch.object(StrategicOrchestrator, '__init__', return_value=None):
                orchestrator = StrategicOrchestrator()
                orchestrator.db_path = mock_db
                orchestrator.discovery = Mock()
                
                # Mock discovery results
                orchestrator.discovery.search_jobs.return_value = [
                    {
                        'company': 'Google',
                        'title': 'ML Engineer',
                        'url': 'http://google.com/jobs/1',
                        'salary_min': 150000
                    },
                    {
                        'company': 'Meta',
                        'title': 'Data Scientist',
                        'url': 'http://meta.com/jobs/2',
                        'salary_min': 180000
                    }
                ]
                
                # Run discovery
                jobs = orchestrator.discover_phase("ML Engineer", limit=2)
                
                assert len(jobs) == 2
                assert jobs[0]['company'] == 'Google'
                assert orchestrator.discovery.search_jobs.called
    
    @pytest.mark.unit
    def test_generate_content(self):
        """Test content generation"""
        from orchestrator import ContentGenerator
        
        generator = ContentGenerator()
        
        job = {
            'company': 'Anthropic',
            'title': 'AI Safety Researcher',
            'description': 'Research AI safety'
        }
        
        with patch.object(generator, 'personalize_for_company') as mock_personalize:
            mock_personalize.return_value = {
                'cover_letter': 'Dear Anthropic...',
                'resume_variant': 'ai_ml',
                'personalization_score': 0.95
            }
            
            content = generator.generate_for_job(job)
            
            assert 'cover_letter' in content
            assert content['personalization_score'] == 0.95
            assert mock_personalize.called
    
    @pytest.mark.unit
    def test_stage_application(self, mock_db):
        """Test application staging"""
        from orchestrator import StrategicOrchestrator
        
        with patch('orchestrator.Path.exists', return_value=True):
            with patch.object(StrategicOrchestrator, '__init__', return_value=None):
                orchestrator = StrategicOrchestrator()
                orchestrator.db_path = mock_db
                
                application = {
                    'company': 'OpenAI',
                    'position': 'Research Scientist',
                    'cover_letter': 'Dear OpenAI...',
                    'status': 'pending_review'
                }
                
                # Stage application
                orchestrator.stage_application(application)
                
                # Verify it was added to database
                conn = sqlite3.connect(mock_db)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM applications WHERE company_name = 'OpenAI'")
                result = cursor.fetchone()
                
                assert result is not None
                assert result[1] == 'OpenAI'
                assert result[2] == 'Research Scientist'
                conn.close()
    
    @pytest.mark.unit
    @patch('builtins.input', return_value='y')
    def test_review_approval(self, mock_input):
        """Test application review and approval"""
        from orchestrator import ApplicationReviewer
        
        reviewer = ApplicationReviewer()
        
        application = {
            'company': 'DeepMind',
            'position': 'ML Researcher',
            'cover_letter': 'Dear DeepMind...',
            'personalization_score': 0.92
        }
        
        # Test approval
        approved = reviewer.review_application(application)
        assert approved is True
        assert mock_input.called
    
    @pytest.mark.unit
    @patch('builtins.input', return_value='n')
    def test_review_rejection(self, mock_input):
        """Test application rejection"""
        from orchestrator import ApplicationReviewer
        
        reviewer = ApplicationReviewer()
        
        application = {
            'company': 'Company X',
            'position': 'Role Y',
            'personalization_score': 0.60
        }
        
        # Test rejection
        approved = reviewer.review_application(application)
        assert approved is False
    
    @pytest.mark.unit
    @patch('orchestrator.BCCEmailTracker')
    def test_send_application(self, mock_tracker):
        """Test sending approved application"""
        from orchestrator import StrategicOrchestrator
        
        with patch('orchestrator.Path.exists', return_value=True):
            with patch.object(StrategicOrchestrator, '__init__', return_value=None):
                orchestrator = StrategicOrchestrator()
                orchestrator.email_tracker = mock_tracker.return_value
                
                application = {
                    'company': 'Stripe',
                    'position': 'Backend Engineer',
                    'email': 'careers@stripe.com',
                    'cover_letter': 'Dear Stripe...',
                    'resume_path': '/path/to/resume.pdf'
                }
                
                # Send application
                orchestrator.send_application(application)
                
                # Verify email was sent
                assert orchestrator.email_tracker.send_application.called
                call_args = orchestrator.email_tracker.send_application.call_args
                assert 'careers@stripe.com' in str(call_args)
    
    @pytest.mark.unit
    def test_metrics_tracking(self, mock_db):
        """Test metrics collection"""
        from orchestrator import StrategicOrchestrator
        
        with patch('orchestrator.Path.exists', return_value=True):
            with patch.object(StrategicOrchestrator, '__init__', return_value=None):
                orchestrator = StrategicOrchestrator()
                orchestrator.db_path = mock_db
                
                # Add test data
                conn = sqlite3.connect(mock_db)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO applications 
                    (company_name, position, status, applied_date)
                    VALUES (?, ?, ?, ?)
                """, ('Google', 'Engineer', 'sent', datetime.now().isoformat()))
                conn.commit()
                conn.close()
                
                # Get metrics
                metrics = orchestrator.get_metrics()
                
                assert 'total_staged' in metrics
                assert 'total_sent' in metrics
                assert metrics['total_sent'] == 1
    
    @pytest.mark.integration
    @patch('orchestrator.JobDiscoveryEngine')
    @patch('orchestrator.ContentGenerator')
    @patch('orchestrator.BCCEmailTracker')
    @patch('builtins.input', side_effect=['y', 'n', 'q'])
    def test_full_workflow(self, mock_input, mock_email, mock_content, mock_discovery, mock_db):
        """Test complete orchestration workflow"""
        from orchestrator import StrategicOrchestrator
        
        with patch('orchestrator.Path.exists', return_value=True):
            orchestrator = StrategicOrchestrator()
            orchestrator.db_path = mock_db
            
            # Mock discovery
            orchestrator.discovery.search_jobs.return_value = [
                {'company': 'Apple', 'title': 'iOS Developer'}
            ]
            
            # Mock content generation
            orchestrator.generator.generate_for_job.return_value = {
                'cover_letter': 'Dear Apple...',
                'resume_variant': 'mobile'
            }
            
            # Run orchestration
            orchestrator.run("iOS Developer", auto_mode=False)
            
            # Verify workflow executed
            assert orchestrator.discovery.search_jobs.called
            assert orchestrator.generator.generate_for_job.called