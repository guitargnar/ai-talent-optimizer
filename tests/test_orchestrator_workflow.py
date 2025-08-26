#!/usr/bin/env python3
"""
Comprehensive unit and integration tests for orchestrator.py
Targeting 85% test coverage with human-in-the-loop workflow validation
"""

import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, call, mock_open, PropertyMock
import os
import sys
import json

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import (
    StrategicCareerOrchestrator,
    WebFormAutomator, 
    LinkedInResearcher,
    generate_content_with_ollama
)


class TestFutureIntegrations:
    """Test future integration stubs"""
    
    @pytest.mark.unit
    def test_web_form_automator_init(self):
        """Test WebFormAutomator initialization"""
        automator = WebFormAutomator()
        assert automator.browser is None
        assert automator.page is None
    
    @pytest.mark.unit
    def test_apply_via_greenhouse(self):
        """Test Greenhouse application stub"""
        automator = WebFormAutomator()
        result = automator.apply_via_greenhouse("https://test.greenhouse.io/job/123")
        assert result is False  # Currently returns False as not implemented
    
    @pytest.mark.unit
    def test_apply_via_lever(self):
        """Test Lever application stub"""
        automator = WebFormAutomator()
        result = automator.apply_via_lever("https://test.lever.co/job/456")
        assert result is False
    
    @pytest.mark.unit
    def test_screenshot_confirmation(self):
        """Test screenshot confirmation stub"""
        automator = WebFormAutomator()
        result = automator.screenshot_confirmation()
        assert result == "confirmation_screenshot.png"
    
    @pytest.mark.unit
    def test_linkedin_researcher_init(self):
        """Test LinkedInResearcher initialization"""
        researcher = LinkedInResearcher()
        assert researcher.session is None
    
    @pytest.mark.unit
    def test_find_hiring_manager(self):
        """Test finding hiring manager"""
        researcher = LinkedInResearcher()
        result = researcher.find_hiring_manager("Google", "Software Engineer")
        assert result['name'] == 'Unknown'
        assert result['title'] == 'Hiring Manager'
        assert result['profile_url'] is None
    
    @pytest.mark.unit
    def test_find_team_members(self):
        """Test finding team members"""
        researcher = LinkedInResearcher()
        result = researcher.find_team_members("Meta", "Engineering")
        assert result == []
    
    @pytest.mark.unit
    def test_get_company_insights(self):
        """Test getting company insights"""
        researcher = LinkedInResearcher()
        result = researcher.get_company_insights("Amazon")
        assert result['recent_news'] == []
        assert result['employee_count'] == 0
        assert result['growth_rate'] == 'Unknown'
    
    @pytest.mark.unit
    def test_generate_content_with_ollama(self):
        """Test Ollama content generation stub"""
        company_info = {'name': 'Anthropic', 'focus': 'AI Safety'}
        job_description = "ML Engineer role focusing on safety"
        
        result = generate_content_with_ollama(company_info, job_description)
        assert result['cover_letter'] == 'Generated content would go here'
        assert result['key_points'] == []
        assert result['personalization_score'] == 0.95


class TestOrchestratorInitialization:
    """Test orchestrator initialization and setup"""
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_init_basic(self, mock_researcher, mock_dynamic, mock_quality, mock_connect):
        """Test basic initialization"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        
        assert orchestrator.db_path == "unified_platform.db"
        assert mock_quality.called
        assert mock_dynamic.called
        assert mock_researcher.called
        assert orchestrator.session_stats['discovered'] == 0
        assert orchestrator.session_stats['staged'] == 0
        assert orchestrator.session_stats['reviewed'] == 0
        assert orchestrator.session_stats['sent'] == 0
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    def test_upgrade_database_schema(self, mock_connect):
        """Test database schema upgrade"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock the table info check
        mock_cursor.fetchone.return_value = (0,)  # Column doesn't exist
        
        orchestrator = StrategicCareerOrchestrator()
        
        # Verify CREATE TABLE was called
        create_calls = [str(call) for call in mock_cursor.execute.call_args_list]
        assert any('CREATE TABLE IF NOT EXISTS applications' in str(call) for call in create_calls)
        assert mock_conn.commit.called
        assert mock_conn.close.called


class TestDiscoveryWorkflow:
    """Test job discovery and staging workflow"""
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_discover_and_stage_jobs_success(self, mock_researcher, mock_dynamic, mock_quality, mock_connect):
        """Test successful job discovery and staging"""
        # Setup mocks
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        
        # Mock discovered jobs
        discovered_jobs = [
            {
                'company_name': 'Google',
                'job_title': 'ML Engineer',
                'db_id': 1
            },
            {
                'company_name': 'Meta',
                'job_title': 'Data Scientist',
                'db_id': 2
            }
        ]
        
        orchestrator.dynamic_system.discover_new_jobs_online.return_value = discovered_jobs
        orchestrator.company_researcher.find_and_verify_email.return_value = "careers@google.com"
        orchestrator.dynamic_system.update_database_with_discoveries.return_value = discovered_jobs
        
        # Mock research and content generation
        orchestrator.quality_system.research_company.return_value = {'key_points': ['Innovation']}
        orchestrator.quality_system.generate_personalized_email.return_value = (
            "Application for ML Engineer", 
            "Dear Google, I am interested..."
        )
        orchestrator.quality_system.select_resume.return_value = "resume_ml.pdf"
        
        # Execute discovery
        orchestrator.discover_and_stage_jobs("ML Engineer")
        
        # Verify calls
        assert orchestrator.dynamic_system.discover_new_jobs_online.called
        assert orchestrator.company_researcher.find_and_verify_email.called
        assert orchestrator.dynamic_system.update_database_with_discoveries.called
        assert orchestrator.session_stats['discovered'] == 2
        assert orchestrator.session_stats['staged'] == 2
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_discover_no_jobs_found(self, mock_researcher, mock_dynamic, mock_quality, mock_connect):
        """Test when no jobs are discovered"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.dynamic_system.discover_new_jobs_online.return_value = []
        
        orchestrator.discover_and_stage_jobs("Unicorn Trainer")
        
        assert orchestrator.session_stats['discovered'] == 0
        assert orchestrator.session_stats['staged'] == 0
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_stage_application_with_verified_email(self, mock_researcher, mock_dynamic, mock_quality, mock_connect):
        """Test staging application with verified email"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        
        # Setup job with verified email
        job = {
            'company_name': 'Anthropic',
            'job_title': 'AI Safety Researcher',
            'db_id': 1,
            'email': 'careers@anthropic.com',
            'email_verified': True
        }
        
        orchestrator.quality_system.research_company.return_value = {
            'key_points': ['AI Safety', 'Constitutional AI']
        }
        orchestrator.quality_system.generate_personalized_email.return_value = (
            "AI Safety Researcher Application",
            "Dear Anthropic, Your work on AI safety..."
        )
        orchestrator.quality_system.select_resume.return_value = "resume_ai.pdf"
        
        orchestrator._stage_application(job)
        
        # Verify database insert
        assert mock_cursor.execute.called
        insert_call = str(mock_cursor.execute.call_args[0][0])
        assert "INSERT INTO applications" in insert_call
        assert mock_conn.commit.called
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_stage_application_portal_only(self, mock_researcher, mock_dynamic, mock_quality, mock_connect):
        """Test staging application for portal-only companies"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        
        # Setup job with no email
        job = {
            'company_name': 'Netflix',
            'job_title': 'Senior Engineer',
            'db_id': 3
        }
        
        # Mock no email found
        orchestrator.company_researcher.find_and_verify_email.return_value = None
        
        orchestrator.quality_system.research_company.return_value = {}
        orchestrator.quality_system.generate_personalized_email.return_value = (
            "Cover Letter",
            "Dear Netflix..."
        )
        orchestrator.quality_system.select_resume.return_value = "resume.pdf"
        
        orchestrator._stage_application(job)
        
        # Verify NULL email was stored
        insert_args = mock_cursor.execute.call_args[0][1]
        assert insert_args[3] is None  # email_to should be None


class TestReviewWorkflow:
    """Test review and approval workflow"""
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_get_pending_applications(self, mock_researcher, mock_dynamic, mock_quality, mock_connect):
        """Test fetching pending applications"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock pending applications
        mock_cursor.fetchall.return_value = [
            (1, 'Google', 'ML Engineer', 'careers@google.com', 'Application', 'Body', 'resume.pdf', 0.95, 1),
            (2, 'Meta', 'Data Scientist', 'jobs@meta.com', 'Application', 'Body', 'resume.pdf', 0.90, 2)
        ]
        
        orchestrator = StrategicCareerOrchestrator()
        pending = orchestrator._get_pending_applications()
        
        assert len(pending) == 2
        assert pending[0][1] == 'Google'
        assert pending[1][1] == 'Meta'
    
    @pytest.mark.unit
    @patch('builtins.input', side_effect=['a', 'q'])  # Approve first, then quit
    @patch('orchestrator.sqlite3.connect')
    @patch('smtplib.SMTP')
    @patch('pathlib.Path.exists')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_review_approve_workflow(self, mock_researcher, mock_dynamic, mock_quality, 
                                    mock_path_exists, mock_smtp, mock_connect, mock_input):
        """Test review workflow with approval"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock path exists for resume
        mock_path_exists.return_value = True
        
        # Mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Mock pending application
        mock_cursor.fetchall.return_value = [
            (1, 'Google', 'ML Engineer', 'careers@google.com', 'Application', 'Body', 'resume.pdf', 0.95, 1)
        ]
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.quality_system.email = "test@gmail.com"
        orchestrator.quality_system.password = "password"
        
        orchestrator.review_pending_applications()
        
        # Verify email was sent
        assert mock_server.send_message.called
        assert orchestrator.session_stats['sent'] == 1
        assert orchestrator.session_stats['reviewed'] == 1
    
    @pytest.mark.unit
    @patch('builtins.input', return_value='s')  # Skip
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_review_skip_workflow(self, mock_researcher, mock_dynamic, mock_quality, mock_connect, mock_input):
        """Test review workflow with skip"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock pending application
        mock_cursor.fetchall.return_value = [
            (1, 'Google', 'ML Engineer', 'careers@google.com', 'Application', 'Body', 'resume.pdf', 0.95, 1)
        ]
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.review_pending_applications()
        
        assert orchestrator.session_stats['sent'] == 0
        assert orchestrator.session_stats['reviewed'] == 1
    
    @pytest.mark.unit
    @patch('builtins.input', return_value='d')  # Delete
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_review_delete_workflow(self, mock_researcher, mock_dynamic, mock_quality, mock_connect, mock_input):
        """Test review workflow with delete"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock pending application
        mock_cursor.fetchall.return_value = [
            (1, 'Google', 'ML Engineer', 'careers@google.com', 'Application', 'Body', 'resume.pdf', 0.95, 1)
        ]
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.review_pending_applications()
        
        # Verify delete was called
        update_calls = [str(call) for call in mock_cursor.execute.call_args_list]
        assert any("UPDATE applications" in str(call) and "status = 'deleted'" in str(call) for call in update_calls)
        assert orchestrator.session_stats['reviewed'] == 1
    
    @pytest.mark.unit
    @patch('builtins.input', side_effect=['p'])  # Proceed with web app
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_review_portal_application(self, mock_researcher, mock_dynamic, mock_quality, mock_connect, mock_input):
        """Test review workflow for portal-only applications"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock portal-only application (email_to is None)
        mock_cursor.fetchall.return_value = [
            (1, 'Netflix', 'Senior Engineer', None, 'Cover Letter', 'Body', 'resume.pdf', 0.92, 1)
        ]
        
        orchestrator = StrategicCareerOrchestrator()
        
        with patch('builtins.input', side_effect=['p', '']):  # Proceed, then Enter
            orchestrator.review_pending_applications()
        
        # Verify portal application was processed
        assert orchestrator.session_stats['sent'] == 1
        assert orchestrator.session_stats['reviewed'] == 1
    
    @pytest.mark.unit
    @patch('builtins.input', side_effect=['x', 'a'])  # Invalid, then approve
    @patch('orchestrator.sqlite3.connect')
    @patch('smtplib.SMTP')
    @patch('pathlib.Path.exists')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_review_invalid_input_handling(self, mock_researcher, mock_dynamic, mock_quality,
                                          mock_path_exists, mock_smtp, mock_connect, mock_input):
        """Test handling of invalid input during review"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        mock_path_exists.return_value = True
        mock_smtp.return_value.__enter__.return_value = MagicMock()
        
        # Mock pending application
        mock_cursor.fetchall.return_value = [
            (1, 'Google', 'ML Engineer', 'careers@google.com', 'Application', 'Body', 'resume.pdf', 0.95, 1)
        ]
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.quality_system.email = "test@gmail.com"
        orchestrator.quality_system.password = "password"
        
        orchestrator.review_pending_applications()
        
        # Should still process after invalid input
        assert orchestrator.session_stats['reviewed'] == 1


class TestStatusDashboard:
    """Test status dashboard functionality"""
    
    @pytest.mark.unit
    @patch('orchestrator.subprocess.run')
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_show_status_dashboard(self, mock_researcher, mock_dynamic, mock_quality, mock_connect, mock_subprocess):
        """Test status dashboard display"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock subprocess for metrics dashboard
        mock_subprocess.return_value = MagicMock(stdout="Metrics output", stderr="")
        
        # Mock database counts
        mock_cursor.fetchone.return_value = (5, 10, 2)  # pending, sent, deleted
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.session_stats = {
            'discovered': 15,
            'staged': 12,
            'reviewed': 8,
            'sent': 6
        }
        
        # Should not raise exception
        orchestrator.show_status_dashboard()
        
        assert mock_subprocess.called
        assert mock_cursor.execute.called
    
    @pytest.mark.unit
    @patch('orchestrator.subprocess.run', side_effect=Exception("Failed"))
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_show_status_dashboard_error_handling(self, mock_researcher, mock_dynamic, mock_quality, 
                                                  mock_connect, mock_subprocess):
        """Test status dashboard error handling"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        mock_cursor.fetchone.return_value = (0, 0, 0)
        
        orchestrator = StrategicCareerOrchestrator()
        
        # Should handle subprocess error gracefully
        orchestrator.show_status_dashboard()
        
        assert mock_cursor.execute.called


class TestMainMenu:
    """Test main menu and interactive dashboard"""
    
    @pytest.mark.unit
    @patch('builtins.input', side_effect=['q'])  # Quit immediately
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_run_interactive_dashboard_quit(self, mock_researcher, mock_dynamic, mock_quality, mock_connect, mock_input):
        """Test quitting from main menu"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.run_interactive_dashboard()
        
        # Should exit cleanly
        assert True
    
    @pytest.mark.unit
    @patch('builtins.input', side_effect=['d', 'ML Engineer', 'q'])  # Discover, then quit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_run_interactive_dashboard_discover(self, mock_researcher, mock_dynamic, mock_quality, 
                                               mock_connect, mock_input):
        """Test discover option from main menu"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.dynamic_system.discover_new_jobs_online.return_value = []
        
        orchestrator.run_interactive_dashboard()
        
        orchestrator.dynamic_system.discover_new_jobs_online.assert_called_with("ML Engineer")
    
    @pytest.mark.unit
    @patch('builtins.input', side_effect=['r', 'q'])  # Review, then quit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_run_interactive_dashboard_review(self, mock_researcher, mock_dynamic, mock_quality, 
                                             mock_connect, mock_input):
        """Test review option from main menu"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # No pending applications
        mock_cursor.fetchall.return_value = []
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.run_interactive_dashboard()
        
        assert mock_cursor.execute.called
    
    @pytest.mark.unit
    @patch('builtins.input', side_effect=['s', 'q'])  # Status, then quit
    @patch('orchestrator.subprocess.run')
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_run_interactive_dashboard_status(self, mock_researcher, mock_dynamic, mock_quality, 
                                             mock_connect, mock_subprocess, mock_input):
        """Test status option from main menu"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        mock_subprocess.return_value = MagicMock(stdout="Status", stderr="")
        mock_cursor.fetchone.return_value = (0, 0, 0)
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.run_interactive_dashboard()
        
        assert mock_subprocess.called
    
    @pytest.mark.unit
    @patch('builtins.input', side_effect=['a', '', 'q'])  # Advanced, Enter, quit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_run_interactive_dashboard_advanced(self, mock_researcher, mock_dynamic, mock_quality, 
                                               mock_connect, mock_input):
        """Test advanced menu option"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.run_interactive_dashboard()
        
        # Should show advanced menu and return
        assert True
    
    @pytest.mark.unit
    @patch('builtins.input', side_effect=['x', 'q'])  # Invalid, then quit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_run_interactive_dashboard_invalid(self, mock_researcher, mock_dynamic, mock_quality, 
                                              mock_connect, mock_input):
        """Test invalid option handling"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.run_interactive_dashboard()
        
        # Should handle invalid input and continue
        assert True


class TestEmailSending:
    """Test email sending functionality"""
    
    @pytest.mark.unit
    @patch('smtplib.SMTP')
    @patch('pathlib.Path.exists')
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_send_staged_application_success(self, mock_researcher, mock_dynamic, mock_quality, 
                                            mock_connect, mock_path_exists, mock_smtp):
        """Test successful email sending"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        mock_path_exists.return_value = True
        
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.quality_system.email = "test@gmail.com"
        orchestrator.quality_system.password = "password"
        
        app_data = (
            1, 'Google', 'ML Engineer', 'careers@google.com',
            'Application', 'Body', 'resume.pdf', 0.95, 1
        )
        
        result = orchestrator._send_staged_application(1, app_data)
        
        assert result is True
        assert mock_server.send_message.called
        assert mock_cursor.execute.called
        assert mock_conn.commit.called
    
    @pytest.mark.unit
    @patch('smtplib.SMTP', side_effect=Exception("SMTP Error"))
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_send_staged_application_failure(self, mock_researcher, mock_dynamic, mock_quality, 
                                            mock_connect, mock_smtp):
        """Test email sending failure"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.quality_system.email = "test@gmail.com"
        orchestrator.quality_system.password = "password"
        
        app_data = (
            1, 'Google', 'ML Engineer', 'careers@google.com',
            'Application', 'Body', 'resume.pdf', 0.95, 1
        )
        
        result = orchestrator._send_staged_application(1, app_data)
        
        assert result is False


class TestPortalApplications:
    """Test web portal application functionality"""
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_get_portal_url_known_company(self, mock_researcher, mock_dynamic, mock_quality, mock_connect):
        """Test getting portal URL for known company"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        
        url = orchestrator._get_portal_url('Anthropic', None)
        assert url == 'https://job-boards.greenhouse.io/anthropic'
        
        url = orchestrator._get_portal_url('Google', None)
        assert url == 'https://careers.google.com'
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_get_portal_url_from_database(self, mock_researcher, mock_dynamic, mock_quality, mock_connect):
        """Test getting portal URL from database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock URL from database
        mock_cursor.fetchone.return_value = ('https://custom.portal.com',)
        
        orchestrator = StrategicCareerOrchestrator()
        
        url = orchestrator._get_portal_url('Unknown Company', 123)
        assert url == 'https://custom.portal.com'
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_get_portal_url_fallback(self, mock_researcher, mock_dynamic, mock_quality, mock_connect):
        """Test portal URL fallback generation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # No URL in database
        mock_cursor.fetchone.return_value = None
        
        orchestrator = StrategicCareerOrchestrator()
        
        url = orchestrator._get_portal_url('Random Startup', 456)
        assert url == 'https://careers.randomstartup.com'
    
    @pytest.mark.unit
    @patch('builtins.input', return_value='')  # Press Enter
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_proceed_with_web_application_manual(self, mock_researcher, mock_dynamic, mock_quality, 
                                                mock_connect, mock_input):
        """Test manual web application process"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        
        result = orchestrator._proceed_with_web_application(
            1, 'Netflix', 'Senior Engineer', 'https://jobs.netflix.com'
        )
        
        assert result is True
        assert mock_cursor.execute.called
        assert mock_conn.commit.called


class TestStatisticsTracking:
    """Test statistics and metrics tracking"""
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_session_stats_initialization(self, mock_researcher, mock_dynamic, mock_quality, mock_connect):
        """Test session statistics initialization"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        
        assert orchestrator.session_stats['discovered'] == 0
        assert orchestrator.session_stats['staged'] == 0
        assert orchestrator.session_stats['reviewed'] == 0
        assert orchestrator.session_stats['sent'] == 0
    
    @pytest.mark.unit
    @patch('orchestrator.sqlite3.connect')
    @patch('orchestrator.QualityFirstApplicationSystem')
    @patch('orchestrator.DynamicJobApplicationSystem')
    @patch('orchestrator.CompanyResearcher')
    def test_session_summary_display(self, mock_researcher, mock_dynamic, mock_quality, mock_connect):
        """Test session summary display"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        orchestrator = StrategicCareerOrchestrator()
        orchestrator.session_stats = {
            'discovered': 10,
            'staged': 8,
            'reviewed': 5,
            'sent': 3
        }
        
        # Should not raise exception
        orchestrator._show_session_summary()


class TestMainFunction:
    """Test main entry point"""
    
    @pytest.mark.unit
    @patch('orchestrator.StrategicCareerOrchestrator')
    def test_main_normal_execution(self, mock_orchestrator_class):
        """Test normal main execution"""
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        from orchestrator import main
        main()
        
        assert mock_orchestrator.run_interactive_dashboard.called
    
    @pytest.mark.unit
    @patch('orchestrator.StrategicCareerOrchestrator')
    def test_main_keyboard_interrupt(self, mock_orchestrator_class):
        """Test main with keyboard interrupt"""
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.run_interactive_dashboard.side_effect = KeyboardInterrupt()
        
        from orchestrator import main
        main()
        
        assert mock_orchestrator._show_session_summary.called
    
    @pytest.mark.unit
    @patch('orchestrator.StrategicCareerOrchestrator')
    def test_main_exception_handling(self, mock_orchestrator_class):
        """Test main with exception"""
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.run_interactive_dashboard.side_effect = Exception("Test error")
        
        from orchestrator import main
        main()
        
        # Should handle exception gracefully
        assert True


class TestIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.mark.integration
    def test_complete_discovery_to_send_workflow(self):
        """Test complete workflow from discovery to sending"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            with patch('orchestrator.StrategicCareerOrchestrator.db_path', str(db_path)):
                with patch('orchestrator.QualityFirstApplicationSystem') as mock_quality:
                    with patch('orchestrator.DynamicJobApplicationSystem') as mock_dynamic:
                        with patch('orchestrator.CompanyResearcher') as mock_researcher:
                            with patch('orchestrator.smtplib.SMTP') as mock_smtp:
                                with patch('builtins.input', side_effect=['d', 'ML Engineer', 'r', 'a', 'q']):
                                    
                                    # Setup mocks
                                    mock_quality_instance = MagicMock()
                                    mock_quality_instance.email = "test@gmail.com"
                                    mock_quality_instance.password = "password"
                                    mock_quality_instance.research_company.return_value = {}
                                    mock_quality_instance.generate_personalized_email.return_value = ("Subject", "Body")
                                    mock_quality_instance.select_resume.return_value = "resume.pdf"
                                    mock_quality.return_value = mock_quality_instance
                                    
                                    mock_dynamic_instance = MagicMock()
                                    mock_dynamic_instance.discover_new_jobs_online.return_value = [
                                        {'company_name': 'Test Co', 'job_title': 'ML Engineer', 'db_id': 1}
                                    ]
                                    mock_dynamic_instance.update_database_with_discoveries.return_value = [
                                        {'company_name': 'Test Co', 'job_title': 'ML Engineer', 'db_id': 1}
                                    ]
                                    mock_dynamic.return_value = mock_dynamic_instance
                                    
                                    mock_researcher_instance = MagicMock()
                                    mock_researcher_instance.find_and_verify_email.return_value = "careers@test.com"
                                    mock_researcher.return_value = mock_researcher_instance
                                    
                                    mock_smtp_instance = MagicMock()
                                    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
                                    
                                    # Create database
                                    conn = sqlite3.connect(str(db_path))
                                    cursor = conn.cursor()
                                    cursor.execute("""
                                        CREATE TABLE applications (
                                            id INTEGER PRIMARY KEY,
                                            company TEXT,
                                            position TEXT,
                                            email_to TEXT,
                                            email_subject TEXT,
                                            email_body TEXT,
                                            resume_version TEXT,
                                            status TEXT,
                                            created_date TEXT,
                                            personalization_score REAL,
                                            job_id INTEGER
                                        )
                                    """)
                                    cursor.execute("""
                                        CREATE TABLE jobs (
                                            id INTEGER PRIMARY KEY,
                                            company TEXT,
                                            title TEXT,
                                            applied INTEGER,
                                            applied_date TEXT,
                                            application_status TEXT
                                        )
                                    """)
                                    conn.commit()
                                    conn.close()
                                    
                                    # Run orchestrator
                                    from orchestrator import main
                                    main()
                                    
                                    # Verify workflow completed
                                    assert mock_dynamic_instance.discover_new_jobs_online.called
                                    assert mock_researcher_instance.find_and_verify_email.called
                                    
    @pytest.mark.integration
    def test_portal_only_workflow(self):
        """Test workflow for portal-only applications"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            # Create test database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE applications (
                    id INTEGER PRIMARY KEY,
                    company TEXT,
                    position TEXT,
                    email_to TEXT,
                    email_subject TEXT,
                    email_body TEXT,
                    resume_version TEXT,
                    status TEXT DEFAULT 'pending_review',
                    created_date TEXT,
                    personalization_score REAL,
                    job_id INTEGER,
                    notes TEXT,
                    sent_date TEXT,
                    reviewed_date TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY,
                    company TEXT,
                    title TEXT,
                    url TEXT,
                    applied INTEGER DEFAULT 0,
                    applied_date TEXT,
                    application_status TEXT,
                    method TEXT
                )
            """)
            
            # Insert portal-only application
            cursor.execute("""
                INSERT INTO applications (company, position, email_to, email_subject, 
                                        email_body, resume_version, personalization_score, job_id)
                VALUES ('Netflix', 'Senior Engineer', NULL, 'Cover Letter', 
                       'Dear Netflix...', 'resume.pdf', 0.90, 1)
            """)
            conn.commit()
            conn.close()
            
            with patch('orchestrator.sqlite3.connect') as mock_connect:
                mock_connect.return_value = sqlite3.connect(str(db_path))
                
                with patch('orchestrator.QualityFirstApplicationSystem'):
                    with patch('orchestrator.DynamicJobApplicationSystem'):
                        with patch('orchestrator.CompanyResearcher'):
                            with patch('builtins.input', side_effect=['r', 'p', '', 'q']):
                                
                                orchestrator = StrategicCareerOrchestrator()
                                orchestrator.db_path = str(db_path)
                                orchestrator.review_pending_applications()
                                
                                # Verify portal application was processed
                                conn = sqlite3.connect(str(db_path))
                                cursor = conn.cursor()
                                cursor.execute("SELECT status FROM applications WHERE id = 1")
                                status = cursor.fetchone()[0]
                                conn.close()
                                
                                assert status == 'applied_via_portal'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])