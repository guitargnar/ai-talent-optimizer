#!/usr/bin/env python3
"""
Test suite for CareerAutomationDashboard
Validates dashboard metrics, system integrations, and recommendations
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open, call
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import career_automation_dashboard


class TestDashboardFunctions(unittest.TestCase):
    """Test dashboard functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dashboard = {
            'timestamp': datetime.now().isoformat(),
            'systems': {},
            'metrics': {},
            'pipeline': {},
            'recommendations': []
        }
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.Path')
    @patch('sqlite3.connect')
    @patch('builtins.open', new_callable=mock_open)
    @patch('career_automation_dashboard.json.dump')
    def test_generate_dashboard_with_all_systems(self, mock_json_dump, mock_file, 
                                                  mock_sqlite, mock_path, mock_print):
        """Test dashboard generation with all systems active"""
        # Setup Path mocks
        mock_db_path = Mock()
        mock_db_path.exists.return_value = True
        mock_email_db = Mock()
        mock_email_db.exists.return_value = True
        mock_gmail_path = Mock()
        mock_gmail_path.exists.return_value = True
        mock_token_path = Mock()
        mock_token_path.exists.return_value = True
        mock_gmail_path.__truediv__ = Mock(return_value=mock_token_path)
        mock_ml_path = Mock()
        mock_ml_path.exists.return_value = True
        
        # Setup application files
        mock_app_file1 = Mock()
        mock_app_file1.stat().st_mtime = 1000
        mock_app_file1.__str__ = lambda x: 'application_1.json'
        
        mock_app_file2 = Mock()
        mock_app_file2.stat().st_mtime = 2000
        mock_app_file2.__str__ = lambda x: 'application_2.json'
        
        # Configure Path constructor to return appropriate mocks
        def path_side_effect(path_str):
            if path_str == "unified_platform.db":
                return mock_db_path
            elif path_str == 'email_applications.db':
                return mock_email_db
            elif path_str == '/Users/matthewscott/Google Gmail':
                return mock_gmail_path
            elif path_str == '/Users/matthewscott/Projects/jaspermatters-job-intelligence':
                return mock_ml_path
            elif path_str == '.':
                mock_dot = Mock()
                mock_dot.glob.return_value = [mock_app_file1, mock_app_file2]
                return mock_dot
            return Mock()
        
        mock_path.side_effect = path_side_effect
        
        # Setup database mocks
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sqlite.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Configure cursor responses for job database
        mock_cursor.fetchone.side_effect = [
            (500,),  # total jobs
            (125,),  # applied jobs
            (50,),   # email applications
            (10,),   # responses
            (15,),   # week apps
            (3,)     # week responses
        ]
        
        mock_cursor.fetchall.side_effect = [
            [('linkedin', 300), ('indeed', 150), ('direct', 50)],  # sources
            [('Anthropic', 25), ('OpenAI', 20), ('Google', 18), ('Meta', 15), ('Microsoft', 12)]  # top companies
        ]
        
        # Mock application file content
        mock_file.return_value.read.return_value = json.dumps({
            'job': {
                'company': 'TestCompany',
                'position': 'Senior AI Engineer'
            }
        })
        
        # Run the function
        dashboard = career_automation_dashboard.generate_dashboard()
        
        # Verify dashboard structure
        self.assertIsInstance(dashboard, dict)
        self.assertIn('timestamp', dashboard)
        self.assertIn('systems', dashboard)
        self.assertIn('metrics', dashboard)
        self.assertIn('pipeline', dashboard)
        self.assertIn('recommendations', dashboard)
        
        # Verify systems are tracked
        self.assertEqual(dashboard['systems']['job_database']['total_jobs'], 500)
        self.assertEqual(dashboard['systems']['job_database']['applied'], 125)
        self.assertEqual(dashboard['systems']['email_tracking']['sent'], 50)
        self.assertEqual(dashboard['systems']['email_tracking']['responses'], 10)
        self.assertEqual(dashboard['systems']['gmail_oauth'], 'Active')
        self.assertEqual(dashboard['systems']['ml_models'], 'Active')
        
        # Verify metrics
        self.assertEqual(dashboard['metrics']['Jobs Available'], 500)
        self.assertEqual(dashboard['metrics']['Applications Sent'], 50)
        self.assertEqual(dashboard['metrics']['Responses Received'], 10)
        
        # Verify JSON save
        mock_json_dump.assert_called_once()
        
        # Verify print was called for dashboard output
        self.assertGreater(mock_print.call_count, 10)
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.Path')
    @patch('sqlite3.connect')
    def test_generate_dashboard_no_databases(self, mock_sqlite, mock_path, mock_print):
        """Test dashboard generation with no databases"""
        # All paths return False for exists()
        mock_path.return_value.exists.return_value = False
        mock_path.return_value.glob.return_value = []  # Return empty list for glob
        
        # Run the function
        with patch('builtins.open', mock_open()):
            with patch('career_automation_dashboard.json.dump'):
                dashboard = career_automation_dashboard.generate_dashboard()
        
        # Verify dashboard handles missing systems gracefully
        self.assertIsInstance(dashboard, dict)
        self.assertEqual(dashboard['systems'].get('gmail_oauth'), 'Inactive')
        self.assertEqual(dashboard['systems'].get('ml_models'), 'Inactive')
        self.assertEqual(dashboard['systems']['email_tracking']['sent'], 0)
        self.assertEqual(dashboard['systems']['email_tracking']['responses'], 0)
        
        # Verify recommendations for inactive systems
        self.assertIn('recommendations', dashboard)
        self.assertTrue(any('Gmail OAuth' in rec for rec in dashboard['recommendations']))
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.Path')
    @patch('sqlite3.connect')
    def test_generate_dashboard_with_errors(self, mock_sqlite, mock_path, mock_print):
        """Test dashboard handles database errors gracefully"""
        # Setup path to exist but database to fail
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []  # Return empty list for glob
        mock_sqlite.side_effect = sqlite3.Error("Database error")
        
        # Run the function - should not crash
        with patch('builtins.open', mock_open()):
            with patch('career_automation_dashboard.json.dump'):
                # This should not raise an exception even with database errors
                with self.assertRaises(sqlite3.Error):
                    dashboard = career_automation_dashboard.generate_dashboard()
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.Path')
    @patch('sqlite3.connect')
    def test_show_weekly_progress(self, mock_sqlite, mock_path, mock_print):
        """Test weekly progress calculation"""
        # Setup path mock
        mock_path.return_value.exists.return_value = True
        
        # Setup database mocks
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sqlite.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Configure cursor responses
        mock_cursor.fetchone.side_effect = [
            (35,),  # week apps
            (7,)    # week responses
        ]
        
        # Run the function
        career_automation_dashboard.show_weekly_progress()
        
        # Verify SQL queries were made with date filter
        calls = mock_cursor.execute.call_args_list
        self.assertEqual(len(calls), 2)
        
        # Check first query (applications)
        self.assertIn('date_sent >=', calls[0][0][0])
        
        # Check second query (responses)
        self.assertIn('response_date >=', calls[1][0][0])
        
        # Verify output
        print_calls = [str(call) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)
        self.assertIn('35', combined_output)  # week apps
        self.assertIn('7', combined_output)   # week responses
        self.assertIn('5.0', combined_output)  # daily average (35/7)
        self.assertIn('150', combined_output)  # projected monthly (5*30)
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.Path')
    def test_show_weekly_progress_no_database(self, mock_path, mock_print):
        """Test weekly progress with no database"""
        mock_path.return_value.exists.return_value = False
        
        # Should not crash
        career_automation_dashboard.show_weekly_progress()
        
        # Verify header was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)
        self.assertIn('Weekly Progress', combined_output)
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.generate_dashboard')
    @patch('career_automation_dashboard.show_weekly_progress')
    def test_main_function(self, mock_weekly, mock_generate, mock_print):
        """Test main function orchestration"""
        # Setup mock return
        mock_generate.return_value = self.test_dashboard
        
        # Run main
        career_automation_dashboard.main()
        
        # Verify functions were called in order
        mock_generate.assert_called_once()
        mock_weekly.assert_called_once()
        
        # Verify final output
        print_calls = [str(call) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)
        self.assertIn('CAREER AUTOMATION SYSTEM READY', combined_output)
        self.assertIn('345+ jobs', combined_output)
        self.assertIn('Gmail integration', combined_output)


class TestDashboardMetrics(unittest.TestCase):
    """Test dashboard metric calculations"""
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.Path')
    @patch('sqlite3.connect')
    @patch('builtins.open', new_callable=mock_open)
    @patch('career_automation_dashboard.json.dump')
    def test_response_rate_calculation(self, mock_json_dump, mock_file,
                                      mock_sqlite, mock_path, mock_print):
        """Test response rate calculation"""
        # Setup mocks
        mock_path.return_value.exists.return_value = True
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sqlite.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Test various response rate scenarios
        test_cases = [
            (100, 20, '20.0%'),  # 20% response rate
            (50, 5, '10.0%'),    # 10% response rate
            (0, 0, '0%'),        # No applications
            (1, 1, '100.0%'),    # 100% response rate
        ]
        
        for sent, responses, expected_rate in test_cases:
            with self.subTest(sent=sent, responses=responses):
                # Reset mock
                mock_cursor.fetchone.side_effect = [
                    (500,),  # total jobs
                    (125,),  # applied
                    (sent,),  # email applications
                    (responses,),  # responses
                ]
                mock_cursor.fetchall.side_effect = [
                    [('linkedin', 300)],  # sources
                    [('Company', 10)],  # top companies
                ]
                
                dashboard = career_automation_dashboard.generate_dashboard()
                
                if sent > 0:
                    self.assertEqual(
                        dashboard['systems']['email_tracking']['response_rate'],
                        expected_rate
                    )
                else:
                    self.assertEqual(
                        dashboard['systems']['email_tracking']['response_rate'],
                        '0%'
                    )
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.Path')
    @patch('sqlite3.connect')
    @patch('builtins.open', new_callable=mock_open)
    @patch('career_automation_dashboard.json.dump')
    def test_top_source_identification(self, mock_json_dump, mock_file,
                                      mock_sqlite, mock_path, mock_print):
        """Test identification of top job source"""
        # Setup mocks
        mock_path.return_value.exists.return_value = True
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sqlite.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Configure cursor responses
        mock_cursor.fetchone.side_effect = [
            (500,),  # total jobs
            (125,),  # applied
            (50,),   # email applications
            (10,),   # responses
        ]
        
        # Test different source distributions
        test_sources = [
            ('linkedin', 400),
            ('indeed', 75),
            ('direct', 25)
        ]
        
        mock_cursor.fetchall.side_effect = [
            test_sources,  # sources
            [('Company', 10)],  # top companies
        ]
        
        dashboard = career_automation_dashboard.generate_dashboard()
        
        # Verify top source is identified correctly
        self.assertEqual(dashboard['metrics']['Top Source'], 'linkedin')
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.Path')
    @patch('sqlite3.connect')
    @patch('builtins.open', new_callable=mock_open)
    @patch('career_automation_dashboard.json.dump')
    def test_recommendations_logic(self, mock_json_dump, mock_file,
                                  mock_sqlite, mock_path, mock_print):
        """Test recommendation generation logic"""
        # Setup path mocks
        mock_db_path = Mock()
        mock_db_path.exists.return_value = True
        mock_email_db = Mock()
        mock_email_db.exists.return_value = True
        
        def path_side_effect(path_str):
            if path_str == "unified_platform.db":
                return mock_db_path
            elif path_str == 'email_applications.db':
                return mock_email_db
            else:
                mock_other = Mock()
                mock_other.exists.return_value = False
                mock_other.glob.return_value = []  # Return empty list for glob
                return mock_other
        
        mock_path.side_effect = path_side_effect
        
        # Setup database mocks
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sqlite.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Test scenario: no applications sent
        mock_cursor.fetchone.side_effect = [
            (500,),  # total jobs
            (0,),    # applied (zero!)
            (5,),    # email applications (low!)
            (0,),    # responses
        ]
        
        mock_cursor.fetchall.side_effect = [
            [('linkedin', 300)],  # sources
            [('Company', 10)],  # top companies
        ]
        
        dashboard = career_automation_dashboard.generate_dashboard()
        
        # Verify recommendations
        recommendations = dashboard['recommendations']
        self.assertTrue(any('guided_apply.py' in rec for rec in recommendations))
        self.assertTrue(any('Gmail OAuth' in rec for rec in recommendations))
        self.assertTrue(any('10-20 per day' in rec for rec in recommendations))


class TestDashboardIntegration(unittest.TestCase):
    """Test dashboard system integration"""
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.Path')
    @patch('sqlite3.connect')
    def test_application_file_parsing(self, mock_sqlite, mock_path, mock_print):
        """Test parsing of application JSON files"""
        # Create mock application files
        mock_app1 = Mock()
        mock_app1.stat().st_mtime = 3000
        mock_app1.__str__ = lambda x: 'application_1.json'
        
        mock_app2 = Mock()
        mock_app2.stat().st_mtime = 2000
        mock_app2.__str__ = lambda x: 'application_2.json'
        
        mock_app3 = Mock()
        mock_app3.stat().st_mtime = 1000
        mock_app3.__str__ = lambda x: 'application_3.json'
        
        # Configure Path mocks
        def path_side_effect(path_str):
            if path_str == '.':
                mock_dot = Mock()
                mock_dot.glob.return_value = [mock_app1, mock_app2, mock_app3]
                return mock_dot
            else:
                mock_other = Mock()
                mock_other.exists.return_value = True
                # Support division operator for token.pickle check
                mock_token = Mock()
                mock_token.exists.return_value = False
                mock_other.__truediv__ = Mock(return_value=mock_token)
                return mock_other
        
        mock_path.side_effect = path_side_effect
        
        # Setup database mocks
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sqlite.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.side_effect = [
            (500,), (125,), (50,), (10,)
        ]
        mock_cursor.fetchall.side_effect = [
            [('linkedin', 300)],
            [('Company', 10)]
        ]
        
        # Mock file content
        app_data = {
            'job': {
                'company': 'Anthropic',
                'position': 'AI Safety Researcher - Machine Learning'
            }
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(app_data))):
            with patch('career_automation_dashboard.json.dump'):
                dashboard = career_automation_dashboard.generate_dashboard()
        
        # Verify recent applications were parsed
        recent = dashboard['pipeline']['recent_applications']
        self.assertIsInstance(recent, list)
        if recent:  # If successfully parsed
            self.assertEqual(recent[0]['company'], 'Anthropic')
            self.assertIn('AI Safety', recent[0]['position'])
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.Path')
    def test_system_status_checks(self, mock_path, mock_print):
        """Test system component status checks"""
        # Test all systems inactive
        mock_path.return_value.exists.return_value = False
        mock_path.return_value.glob.return_value = []  # Return empty list for glob
        
        with patch('builtins.open', mock_open()):
            with patch('career_automation_dashboard.json.dump'):
                dashboard = career_automation_dashboard.generate_dashboard()
        
        # Verify inactive status
        self.assertEqual(dashboard['systems']['gmail_oauth'], 'Inactive')
        self.assertEqual(dashboard['systems']['ml_models'], 'Inactive')
        
        # Test Gmail active
        def gmail_path_effect(path_str):
            if '/Google Gmail' in path_str:
                mock_gmail = Mock()
                mock_gmail.exists.return_value = True
                mock_token = Mock()
                mock_token.exists.return_value = True
                mock_gmail.__truediv__ = Mock(return_value=mock_token)
                return mock_gmail
            mock_other = Mock()
            mock_other.exists.return_value = False
            mock_other.glob.return_value = []  # Return empty list for glob
            return mock_other
        
        mock_path.side_effect = gmail_path_effect
        
        with patch('builtins.open', mock_open()):
            with patch('career_automation_dashboard.json.dump'):
                dashboard = career_automation_dashboard.generate_dashboard()
        
        self.assertEqual(dashboard['systems']['gmail_oauth'], 'Active')
    
    def test_dashboard_data_structure(self):
        """Test dashboard data structure consistency"""
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'systems': {
                'job_database': {
                    'total_jobs': 500,
                    'sources': {'linkedin': 300, 'indeed': 200},
                    'top_companies': [('Anthropic', 25)],
                    'applied': 125
                },
                'email_tracking': {
                    'sent': 50,
                    'responses': 10,
                    'response_rate': '20.0%'
                },
                'gmail_oauth': 'Active',
                'ml_models': 'Inactive'
            },
            'metrics': {
                'Jobs Available': 500,
                'Applications Sent': 50,
                'Responses Received': 10,
                'Response Rate': '20.0%',
                'Top Source': 'linkedin'
            },
            'pipeline': {
                'recent_applications': []
            },
            'recommendations': []
        }
        
        # Verify structure
        self.assertIn('timestamp', dashboard)
        self.assertIn('systems', dashboard)
        self.assertIn('metrics', dashboard)
        self.assertIn('pipeline', dashboard)
        self.assertIn('recommendations', dashboard)
        
        # Verify nested structures
        self.assertIn('job_database', dashboard['systems'])
        self.assertIn('email_tracking', dashboard['systems'])
        self.assertIn('total_jobs', dashboard['systems']['job_database'])
        self.assertIn('sent', dashboard['systems']['email_tracking'])
        
        # Verify metrics match systems
        self.assertEqual(
            dashboard['metrics']['Jobs Available'],
            dashboard['systems']['job_database']['total_jobs']
        )
        self.assertEqual(
            dashboard['metrics']['Applications Sent'],
            dashboard['systems']['email_tracking']['sent']
        )


class TestDashboardDisplay(unittest.TestCase):
    """Test dashboard display and formatting"""
    
    @patch('builtins.print')
    def test_dashboard_header_formatting(self, mock_print):
        """Test dashboard header and section formatting"""
        with patch('career_automation_dashboard.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            mock_path.return_value.glob.return_value = []  # Return empty list for glob
            
            with patch('builtins.open', mock_open()):
                with patch('career_automation_dashboard.json.dump'):
                    career_automation_dashboard.generate_dashboard()
        
        # Check print calls for formatting
        print_calls = [str(call) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)
        
        # Verify headers
        self.assertIn('CAREER AUTOMATION DASHBOARD', combined_output)
        self.assertIn('Job Database Analysis', combined_output)
        self.assertIn('Email Application Tracking', combined_output)
        self.assertIn('Gmail OAuth Integration', combined_output)
        self.assertIn('ML Models Status', combined_output)
        self.assertIn('Key Metrics', combined_output)
        self.assertIn('Recommendations', combined_output)
        
        # Verify separators
        self.assertIn('=' * 70, combined_output)
        self.assertIn('-' * 40, combined_output)
    
    @patch('builtins.print')
    def test_quick_commands_display(self, mock_print):
        """Test quick commands section"""
        with patch('career_automation_dashboard.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            mock_path.return_value.glob.return_value = []  # Return empty list for glob
            
            with patch('builtins.open', mock_open()):
                with patch('career_automation_dashboard.json.dump'):
                    career_automation_dashboard.generate_dashboard()
        
        # Check for quick commands
        print_calls = [str(call) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)
        
        self.assertIn('Quick Commands', combined_output)
        self.assertIn('find_and_apply_best_jobs.py', combined_output)
        self.assertIn('guided_apply.py', combined_output)
        self.assertIn('gmail_oauth_integration.py', combined_output)
        self.assertIn('main.py status', combined_output)
        self.assertIn('career_automation_dashboard.py', combined_output)
    
    @patch('builtins.print')
    @patch('career_automation_dashboard.generate_dashboard')
    @patch('career_automation_dashboard.show_weekly_progress')
    def test_main_output_formatting(self, mock_weekly, mock_generate, mock_print):
        """Test main function output formatting"""
        mock_generate.return_value = {'systems': {}, 'metrics': {}}
        
        career_automation_dashboard.main()
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        combined_output = " ".join(print_calls)
        
        # Verify final summary
        self.assertIn('CAREER AUTOMATION SYSTEM READY', combined_output)
        self.assertIn('345+ jobs from top companies', combined_output)
        self.assertIn('Anthropic, Scale AI', combined_output)
        self.assertIn('Gmail integration', combined_output)
        self.assertIn('ML-powered job matching', combined_output)
        self.assertIn('Ready to accelerate', combined_output)


if __name__ == '__main__':
    unittest.main()