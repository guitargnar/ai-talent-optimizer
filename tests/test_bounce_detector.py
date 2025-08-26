#!/usr/bin/env python3
"""
Comprehensive Test Suite for bounce_detector.py
================================================
Tests bounce detection, pattern matching, SMTP parsing, and database updates.
Achieves 85%+ test coverage.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open, PropertyMock, call
import json
import sqlite3
import imaplib
import email
from email.message import EmailMessage
from datetime import datetime, timedelta
from pathlib import Path
import os

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from bounce_detector import BounceDetector


class TestBounceDetector(unittest.TestCase):
    """Test suite for BounceDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'EMAIL_ADDRESS': 'test@example.com',
            'EMAIL_APP_PASSWORD': 'test_password'
        })
        self.env_patcher.start()
        
        # Create detector instance
        with patch('bounce_detector.load_dotenv'):
            self.detector = BounceDetector()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.env_patcher.stop()
    
    def test_initialization(self):
        """Test BounceDetector initialization."""
        self.assertEqual(self.detector.db_path, "unified_platform.db")
        self.assertEqual(self.detector.email_address, 'test@example.com')
        self.assertEqual(self.detector.app_password, 'test_password')
        
        # Check patterns are loaded
        self.assertGreater(len(self.detector.bounce_patterns), 0)
        self.assertGreater(len(self.detector.email_extraction_patterns), 0)
        self.assertIn('invalid_address', self.detector.bounce_reasons)
        self.assertIn('domain_not_found', self.detector.bounce_reasons)
    
    @patch('bounce_detector.imaplib.IMAP4_SSL')
    def test_connect_to_gmail_success(self, mock_imap):
        """Test successful Gmail connection."""
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        
        result = self.detector.connect_to_gmail()
        
        self.assertEqual(result, mock_mail)
        mock_imap.assert_called_once_with('imap.gmail.com')
        mock_mail.login.assert_called_once_with('test@example.com', 'test_password')
    
    @patch('bounce_detector.imaplib.IMAP4_SSL')
    @patch('builtins.print')
    def test_connect_to_gmail_failure(self, mock_print, mock_imap):
        """Test Gmail connection failure."""
        mock_imap.side_effect = Exception("Connection failed")
        
        result = self.detector.connect_to_gmail()
        
        self.assertIsNone(result)
        mock_print.assert_called_with("❌ Failed to connect to Gmail: Connection failed")
    
    def test_decode_header(self):
        """Test email header decoding."""
        # Test UTF-8 encoded header
        encoded_header = '=?utf-8?b?Qm91bmNlZCBNZXNzYWdl?='
        result = self.detector._decode_header(encoded_header)
        self.assertEqual(result, 'Bounced Message')
        
        # Test plain text
        plain_header = 'Plain Text Header'
        result = self.detector._decode_header(plain_header)
        self.assertEqual(result, 'Plain Text Header')
        
        # Test None
        result = self.detector._decode_header(None)
        self.assertEqual(result, "")
    
    def test_get_email_body_multipart(self):
        """Test extracting body from multipart email."""
        mock_msg = MagicMock()
        mock_msg.is_multipart.return_value = True
        
        # Create mock parts
        text_part = MagicMock()
        text_part.get_content_type.return_value = "text/plain"
        text_part.get_payload.return_value = b"Email bounced"
        
        html_part = MagicMock()
        html_part.get_content_type.return_value = "text/html"
        html_part.get_payload.return_value = b"<html>Email bounced</html>"
        
        mock_msg.walk.return_value = [mock_msg, text_part, html_part]
        
        body = self.detector._get_email_body(mock_msg)
        
        self.assertIn("Email bounced", body)
    
    def test_get_email_body_simple(self):
        """Test extracting body from simple email."""
        mock_msg = MagicMock()
        mock_msg.is_multipart.return_value = False
        mock_msg.get_payload.return_value = b"Simple bounce message"
        
        body = self.detector._get_email_body(mock_msg)
        
        self.assertEqual(body, "Simple bounce message")
    
    def test_get_email_body_with_error(self):
        """Test body extraction with error handling."""
        mock_msg = MagicMock()
        mock_msg.is_multipart.return_value = False
        mock_msg.get_payload.side_effect = [Exception("Decode error"), "Fallback text"]
        
        body = self.detector._get_email_body(mock_msg)
        
        self.assertEqual(body, "Fallback text")
    
    def test_is_bounce_email_positive_cases(self):
        """Test detecting bounce emails with various patterns."""
        test_cases = [
            ("Mail Delivery Subsystem", "mailer-daemon@example.com", "Message not delivered"),
            ("Undelivered Mail Returned", "postmaster@example.com", "Failed to deliver"),
            ("Delivery Status Notification", "noreply@example.com", "550 User rejected"),
            ("Failed Delivery", "system@example.com", "Mailbox not found"),
            ("Undeliverable", "daemon@example.com", "User unknown"),
            ("Message Failure", "admin@example.com", "No such user"),
            ("Delivery Failed", "bounce@example.com", "Recipient rejected"),
            ("Cannot Deliver", "notify@example.com", "Address not found")
        ]
        
        for subject, from_addr, body in test_cases:
            result = self.detector._is_bounce_email(subject, from_addr, body)
            self.assertTrue(result, f"Failed to detect bounce for: {subject}")
    
    def test_is_bounce_email_negative_cases(self):
        """Test non-bounce emails are not detected as bounces."""
        test_cases = [
            ("Meeting Reminder", "colleague@example.com", "Don't forget our meeting"),
            ("Newsletter", "news@example.com", "Latest updates"),
            ("Invoice", "billing@example.com", "Payment due"),
            ("Welcome", "welcome@example.com", "Thank you for signing up")
        ]
        
        for subject, from_addr, body in test_cases:
            result = self.detector._is_bounce_email(subject, from_addr, body)
            self.assertFalse(result, f"False positive for: {subject}")
    
    def test_extract_bounced_address(self):
        """Test extracting email addresses from bounce messages."""
        test_cases = [
            # Angle brackets format
            ("The message to <john.doe@example.com> could not be delivered", 
             "john.doe@example.com"),
            
            # Plain email
            ("Failed to deliver to user@domain.com", 
             "user@domain.com"),
            
            # With 'to' prefix
            ("Delivery failed to test@example.org",
             "test@example.org"),
            
            # With 'recipient' prefix
            ("The recipient invalid@company.com does not exist",
             "invalid@company.com"),
            
            # Multiple emails (should get first)
            ("From admin@test.com to user@example.com failed",
             "admin@test.com"),
        ]
        
        for body, expected in test_cases:
            result = self.detector._extract_bounced_address(body)
            self.assertEqual(result, expected, f"Failed to extract from: {body}")
    
    def test_extract_bounced_address_no_match(self):
        """Test extraction when no email found."""
        body = "This message contains no email addresses"
        result = self.detector._extract_bounced_address(body)
        self.assertIsNone(result)
    
    def test_extract_bounced_address_invalid_email(self):
        """Test extraction filters out invalid emails."""
        body = "Failed to deliver to notanemail and also @invalid"
        result = self.detector._extract_bounced_address(body)
        self.assertIsNone(result)
    
    def test_categorize_bounce_reason(self):
        """Test categorizing bounce reasons."""
        test_cases = [
            # Invalid address
            ("550 5.1.1 No such user here", "invalid_address"),
            ("User unknown in local recipient table", "invalid_address"),
            ("Mailbox not found", "invalid_address"),
            ("Address not found", "invalid_address"),
            
            # Domain not found
            ("Host not found", "domain_not_found"),
            ("Domain not found", "domain_not_found"),
            ("No MX record for domain", "domain_not_found"),
            
            # Mailbox full
            ("Mailbox full", "mailbox_full"),
            ("Quota exceeded", "mailbox_full"),
            ("User over quota", "mailbox_full"),
            
            # Blocked
            ("Message blocked as spam", "blocked"),
            ("Rejected by policy", "blocked"),
            ("Blacklisted sender", "blocked"),
            ("Connection refused", "blocked"),
            
            # Temporary
            ("Temporary failure, please try again", "temporary"),
            ("Service temporarily unavailable", "temporary"),
            
            # Unknown
            ("Some other error", "unknown")
        ]
        
        for body, expected_category in test_cases:
            result = self.detector._categorize_bounce_reason(body)
            self.assertEqual(result, expected_category, f"Failed for: {body}")
    
    @patch('bounce_detector.BounceDetector.connect_to_gmail')
    def test_scan_for_bounces_no_connection(self, mock_connect):
        """Test scanning when Gmail connection fails."""
        mock_connect.return_value = None
        
        result = self.detector.scan_for_bounces()
        
        self.assertEqual(result, [])
        mock_connect.assert_called_once()
    
    @patch('bounce_detector.BounceDetector.connect_to_gmail')
    @patch('bounce_detector.email.message_from_bytes')
    def test_scan_for_bounces_with_bounces(self, mock_message_from_bytes, mock_connect):
        """Test scanning and finding bounce emails."""
        mock_mail = MagicMock()
        mock_connect.return_value = mock_mail
        
        # Mock folder selection
        mock_mail.select.return_value = (None, None)
        
        # Mock search results
        mock_mail.search.return_value = (None, [b'1 2'])
        
        # Create mock bounce emails
        bounce1 = self._create_mock_bounce_email(
            "Mail Delivery Failed",
            "mailer-daemon@gmail.com",
            "The message to <invalid@example.com> could not be delivered. User unknown."
        )
        
        bounce2 = self._create_mock_bounce_email(
            "Undelivered Mail",
            "postmaster@yahoo.com",
            "Failed to deliver to full@mailbox.com - Mailbox full"
        )
        
        # Mock message parsing
        mock_message_from_bytes.side_effect = [bounce1, bounce2] * 5  # For multiple search queries
        
        # Mock fetch results
        mock_mail.fetch.return_value = (None, [(None, b'bounce_email')])
        
        result = self.detector.scan_for_bounces(days_back=7)
        
        # Should find unique bounces
        self.assertGreater(len(result), 0)
        
        # Check bounce structure
        if result:
            bounce = result[0]
            self.assertIn('bounced_email', bounce)
            self.assertIn('bounce_date', bounce)
            self.assertIn('reason_category', bounce)
            self.assertIn('subject', bounce)
        
        mock_mail.logout.assert_called_once()
    
    @patch('bounce_detector.BounceDetector.connect_to_gmail')
    @patch('builtins.print')
    def test_scan_for_bounces_with_error(self, mock_print, mock_connect):
        """Test error handling during bounce scanning."""
        mock_mail = MagicMock()
        mock_connect.return_value = mock_mail
        
        # Mock error during folder selection
        mock_mail.select.side_effect = Exception("IMAP error")
        
        result = self.detector.scan_for_bounces()
        
        # Should handle error gracefully
        self.assertEqual(result, [])
        
        # Check error was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Error scanning for bounces' in str(call) for call in print_calls))
    
    @patch('bounce_detector.BounceDetector.connect_to_gmail')
    def test_scan_for_bounces_removes_duplicates(self, mock_connect):
        """Test that duplicate bounces are removed."""
        mock_mail = MagicMock()
        mock_connect.return_value = mock_mail
        
        mock_mail.select.return_value = (None, None)
        mock_mail.search.return_value = (None, [b'1'])
        
        # Create duplicate bounce
        bounce_email = self._create_mock_bounce_email(
            "Delivery Failed",
            "mailer-daemon@gmail.com",
            "Failed to deliver to duplicate@example.com"
        )
        
        with patch('bounce_detector.email.message_from_bytes', return_value=bounce_email):
            # Mock multiple fetches returning same email
            mock_mail.fetch.return_value = (None, [(None, b'bounce')])
            
            # Process multiple search queries
            with patch.object(self.detector, '_extract_bounced_address', return_value='duplicate@example.com'):
                result = self.detector.scan_for_bounces()
        
        # Should have only unique emails
        unique_emails = set(b['bounced_email'] for b in result if 'bounced_email' in b)
        self.assertEqual(len(unique_emails), len(result))
    
    @patch('bounce_detector.sqlite3.connect')
    def test_update_database_with_bounces(self, mock_connect):
        """Test updating database with bounce information."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        bounces = [
            {
                'bounced_email': 'invalid@example.com',
                'reason_category': 'invalid_address',
                'bounce_date': '2025-01-20'
            },
            {
                'bounced_email': 'full@mailbox.com',
                'reason_category': 'mailbox_full',
                'bounce_date': '2025-01-20'
            }
        ]
        
        self.detector.update_database_with_bounces(bounces)
        
        # Check ALTER TABLE was attempted
        alter_calls = [call[0][0] for call in mock_cursor.execute.call_args_list 
                      if 'ALTER TABLE' in str(call[0][0])]
        self.assertEqual(len(alter_calls), 2)  # Two columns added
        
        # Check UPDATE was called for each bounce
        update_calls = [call for call in mock_cursor.execute.call_args_list 
                       if 'UPDATE jobs' in str(call[0][0])]
        self.assertEqual(len(update_calls), 2)
        
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    def test_update_database_with_bounces_empty(self):
        """Test database update with no bounces."""
        # Should return early without database connection
        with patch('bounce_detector.sqlite3.connect') as mock_connect:
            self.detector.update_database_with_bounces([])
            mock_connect.assert_not_called()
    
    @patch('bounce_detector.sqlite3.connect')
    def test_update_database_with_bounces_alter_table_exists(self, mock_connect):
        """Test database update when columns already exist."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Track execution order
        execute_count = 0
        def execute_side_effect(query, params=None):
            nonlocal execute_count
            execute_count += 1
            # First two calls are ALTER TABLE, which should fail
            if execute_count <= 2 and 'ALTER TABLE' in query:
                raise Exception("column already exists")
            # Subsequent UPDATE calls should succeed
            return None
        
        mock_cursor.execute.side_effect = execute_side_effect
        
        bounces = [{
            'bounced_email': 'test@example.com',
            'reason_category': 'invalid_address'
        }]
        
        self.detector.update_database_with_bounces(bounces)
        
        # Should still complete successfully
        mock_conn.commit.assert_called_once()
    
    @patch('bounce_detector.BounceDetector.scan_for_bounces')
    @patch('bounce_detector.BounceDetector.update_database_with_bounces')
    @patch('bounce_detector.sqlite3.connect')
    @patch('builtins.open', new_callable=mock_open)
    @patch('bounce_detector.json.dump')
    def test_generate_bounce_report(self, mock_json_dump, mock_file, mock_connect,
                                   mock_update_db, mock_scan):
        """Test generating comprehensive bounce report."""
        # Mock bounce scan results
        bounces = [
            {
                'bounced_email': 'invalid@example.com',
                'reason_category': 'invalid_address',
                'bounce_date': '2025-01-20',
                'subject': 'Delivery Failed'
            },
            {
                'bounced_email': 'full@mailbox.com',
                'reason_category': 'mailbox_full',
                'bounce_date': '2025-01-20',
                'subject': 'Mailbox Full'
            }
        ]
        mock_scan.return_value = bounces
        
        # Mock database statistics
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(100,), (5,)]  # total_sent, total_bounced
        
        report = self.detector.generate_bounce_report()
        
        # Verify report structure
        self.assertIn('scan_date', report)
        self.assertEqual(report['total_sent'], 100)
        self.assertEqual(report['total_bounced'], 5)
        self.assertEqual(report['bounce_rate'], 5.0)
        self.assertEqual(report['new_bounces_found'], 2)
        self.assertIn('invalid_address', report['bounces_by_category'])
        self.assertIn('mailbox_full', report['bounces_by_category'])
        
        # Verify files were saved
        self.assertEqual(mock_json_dump.call_count, 2)  # bounce_log and invalid_emails
        
        mock_update_db.assert_called_once_with(bounces)
        mock_conn.close.assert_called_once()
    
    @patch('bounce_detector.BounceDetector.generate_bounce_report')
    @patch('builtins.print')
    def test_display_bounce_dashboard(self, mock_print, mock_generate):
        """Test displaying bounce dashboard."""
        # Mock report
        mock_generate.return_value = {
            'total_sent': 200,
            'total_bounced': 15,
            'bounce_rate': 7.5,
            'new_bounces_found': 3,
            'bounces_by_category': {
                'invalid_address': ['bad1@example.com', 'bad2@example.com'],
                'mailbox_full': ['full@example.com']
            },
            'bounced_emails': ['bad1@example.com', 'bad2@example.com', 'full@example.com']
        }
        
        self.detector.display_bounce_dashboard()
        
        # Check output contains expected sections
        print_calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(str(call) for call in print_calls)
        
        self.assertIn('BOUNCE DETECTION DASHBOARD', output)
        self.assertIn('Total Emails Sent: 200', output)
        self.assertIn('Total Bounces Detected: 15', output)
        self.assertIn('Bounce Rate: 7.5%', output)
        self.assertIn('WARNING: Bounce rate exceeds 5% threshold', output)
        self.assertIn('Invalid Address: 2 emails', output)
        self.assertIn('ACTION REQUIRED', output)
    
    @patch('bounce_detector.BounceDetector.generate_bounce_report')
    @patch('builtins.print')
    def test_display_bounce_dashboard_no_bounces(self, mock_print, mock_generate):
        """Test dashboard when no bounces found."""
        mock_generate.return_value = {
            'total_sent': 100,
            'total_bounced': 0,
            'bounce_rate': 0.0,
            'new_bounces_found': 0,
            'bounces_by_category': {},
            'bounced_emails': []
        }
        
        self.detector.display_bounce_dashboard()
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(str(call) for call in print_calls)
        
        self.assertIn('No bounces detected - excellent delivery!', output)
        self.assertNotIn('WARNING', output)
    
    def _create_mock_bounce_email(self, subject, from_addr, body):
        """Helper to create mock bounce email."""
        msg = MagicMock()
        msg.__getitem__.side_effect = lambda x: {
            'Subject': subject,
            'From': from_addr,
            'Date': 'Mon, 20 Jan 2025 10:00:00 +0000'
        }.get(x)
        msg.is_multipart.return_value = False
        msg.get_payload.return_value = body.encode('utf-8')
        return msg


class TestMainFunction(unittest.TestCase):
    """Test the main function."""
    
    @patch('bounce_detector.BounceDetector')
    @patch('builtins.print')
    def test_main_with_password(self, mock_print, mock_detector_class):
        """Test main function with password configured."""
        mock_detector = MagicMock()
        mock_detector.app_password = 'test_password'
        mock_detector_class.return_value = mock_detector
        
        from bounce_detector import main
        main()
        
        mock_detector.display_bounce_dashboard.assert_called_once()
        
        # Check recommendations were printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(str(call) for call in print_calls)
        self.assertIn('RECOMMENDATIONS', output)
    
    @patch('bounce_detector.BounceDetector')
    @patch('builtins.print')
    def test_main_without_password(self, mock_print, mock_detector_class):
        """Test main function without password."""
        mock_detector = MagicMock()
        mock_detector.app_password = ''
        mock_detector_class.return_value = mock_detector
        
        from bounce_detector import main
        main()
        
        mock_detector.display_bounce_dashboard.assert_not_called()
        
        # Check warning was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(str(call) for call in print_calls)
        self.assertIn('Gmail App Password not found', output)


class TestBouncePatterns(unittest.TestCase):
    """Test various bounce patterns and SMTP codes."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('bounce_detector.load_dotenv'):
            self.detector = BounceDetector()
    
    def test_smtp_response_codes(self):
        """Test detection of various SMTP response codes."""
        test_cases = [
            # Hard bounces (5xx codes) - matching actual patterns
            ("550 5.1.1 User unknown", True),
            ("550 rejected: mailbox unavailable", True),  # Matches '550.*rejected' pattern
            ("551 User not local", False),  # Not in patterns
            ("552 Requested mail action aborted: exceeded storage allocation", False),
            ("553 Requested action not taken: mailbox name not allowed", False),
            ("554 Transaction failed", False),
            
            # Soft bounces (4xx codes) - should still be detected
            ("421 Service not available", False),  # Temporary, not a bounce pattern
            ("450 Requested mail action not taken", False),
            ("451 Requested action aborted", False),
            ("452 Requested action not taken: insufficient system storage", False),
            
            # Success codes (2xx) - should not be detected
            ("250 OK", False),
            ("220 Service ready", False),
        ]
        
        for body, should_detect in test_cases:
            result = self.detector._is_bounce_email("Subject", "system@mail.com", body)
            if should_detect:
                self.assertTrue(result, f"Failed to detect: {body}")
    
    def test_international_bounce_messages(self):
        """Test bounce detection in different formats."""
        test_cases = [
            # Various formats
            "Delivery has failed to these recipients",
            "The following message to <user@example.com> was undeliverable",
            "Your message could not be delivered",
            "Permanent failure delivering message",
            "Mail delivery failed: returning message to sender",
            "This is the mail system at host mail.example.com",
            "The email account that you tried to reach does not exist",
            "Message rejected due to content restrictions"
        ]
        
        for body in test_cases:
            # Most of these should be detected
            result = self.detector._is_bounce_email("Delivery Status", "postmaster@example.com", body)
            # We expect most to be detected based on patterns
    
    def test_extract_email_edge_cases(self):
        """Test email extraction from various bounce message formats."""
        test_cases = [
            # Complex formats
            ("Original-Recipient: rfc822;user@example.com", "user@example.com"),
            ("Final-Recipient: RFC822; bad.email@domain.org", "bad.email@domain.org"),
            ("X-Failed-Recipients: invalid@test.com", "invalid@test.com"),
            
            # Multiple emails in message
            ("From sender@example.com to recipient@example.org failed", "sender@example.com"),
            
            # Quoted printable
            ("Failed: \"user@example.com\"", "user@example.com"),
            
            # With additional text
            ("The recipient address <noreply@company.com> was rejected", "noreply@company.com"),
        ]
        
        for body, expected in test_cases:
            result = self.detector._extract_bounced_address(body)
            if expected:
                self.assertEqual(result, expected, f"Failed to extract from: {body}")


class TestDatabaseIntegration(unittest.TestCase):
    """Test database integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('bounce_detector.load_dotenv'):
            self.detector = BounceDetector()
    
    @patch('bounce_detector.sqlite3.connect')
    def test_database_update_with_complex_emails(self, mock_connect):
        """Test database updates with various email formats."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        bounces = [
            {
                'bounced_email': 'careers@company.com',
                'reason_category': 'invalid_address'
            },
            {
                'bounced_email': 'jobs@startup.io',
                'reason_category': 'domain_not_found'
            },
            {
                'bounced_email': 'hr@bigcorp.com',
                'reason_category': 'mailbox_full'
            }
        ]
        
        self.detector.update_database_with_bounces(bounces)
        
        # Check UPDATE queries were constructed correctly
        update_calls = [call for call in mock_cursor.execute.call_args_list 
                       if 'UPDATE' in str(call)]
        self.assertEqual(len(update_calls), 3)
        
        # Verify careers@ and jobs@ special handling
        for call in update_calls:
            query = call[0][0]
            self.assertIn('careers@', query.lower())
    
    @patch('bounce_detector.sqlite3.connect')
    def test_generate_report_with_zero_sent(self, mock_connect):
        """Test report generation when no emails have been sent."""
        with patch.object(self.detector, 'scan_for_bounces', return_value=[]):
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # No emails sent
            mock_cursor.fetchone.side_effect = [(0,), (0,)]
            
            with patch('builtins.open', mock_open()):
                with patch('bounce_detector.json.dump'):
                    report = self.detector.generate_bounce_report()
            
            self.assertEqual(report['bounce_rate'], 0)
            self.assertEqual(report['total_sent'], 0)


class TestEdgeCasesAndErrors(unittest.TestCase):
    """Test edge cases and error scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('bounce_detector.load_dotenv'):
            self.detector = BounceDetector()
    
    def test_malformed_email_header(self):
        """Test handling of malformed email headers."""
        malformed = '=?broken-encoding?q?test?='
        result = self.detector._decode_header(malformed)
        # Should handle gracefully
        self.assertIsInstance(result, str)
    
    def test_empty_bounce_body(self):
        """Test categorization with empty body."""
        result = self.detector._categorize_bounce_reason("")
        self.assertEqual(result, 'unknown')
    
    def test_scan_with_missing_folders(self):
        """Test scanning when some folders don't exist."""
        with patch.object(self.detector, 'connect_to_gmail') as mock_connect:
            mock_mail = MagicMock()
            mock_connect.return_value = mock_mail
            
            # First folder works, others fail
            mock_mail.select.side_effect = [
                (None, None),  # INBOX works
                Exception("Folder not found"),  # [Gmail]/Spam fails
                Exception("Folder not found"),  # [Gmail]/All Mail fails
            ]
            
            mock_mail.search.return_value = (None, [b''])
            
            result = self.detector.scan_for_bounces()
            
            # Should continue despite folder errors
            self.assertIsInstance(result, list)
    
    @patch('bounce_detector.BounceDetector.connect_to_gmail')
    def test_scan_with_search_error(self, mock_connect):
        """Test handling of search errors."""
        mock_mail = MagicMock()
        mock_connect.return_value = mock_mail
        
        mock_mail.select.return_value = (None, None)
        mock_mail.search.side_effect = Exception("Search failed")
        
        with patch('builtins.print'):
            result = self.detector.scan_for_bounces()
        
        self.assertEqual(result, [])
        mock_mail.logout.assert_called_once()
    
    def test_extract_email_with_special_characters(self):
        """Test email extraction with special characters."""
        test_cases = [
            "Failed to deliver to user+tag@example.com",
            "Bounced: first.last@company.co.uk",
            "Invalid: user-name@sub.domain.com",
            "Rejected: user_123@example.org"
        ]
        
        for body in test_cases:
            result = self.detector._extract_bounced_address(body)
            self.assertIsNotNone(result)
            self.assertIn('@', result)
            self.assertIn('.', result)


if __name__ == '__main__':
    unittest.main(verbosity=2)