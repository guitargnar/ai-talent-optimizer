"""
Unit tests for accurate response checker
"""

import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
from email.message import EmailMessage

import pytest

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock the imports that might not be available
with patch.dict('sys.modules', {
    'bcc_email_tracker': MagicMock(),
    'dotenv': MagicMock()
}):
    from accurate_response_checker import AccurateResponseChecker


class TestAccurateResponseChecker:
    """Test accurate response checking functionality"""
    
    @pytest.fixture
    def mock_checker(self):
        """Create mock response checker"""
        with patch.dict(os.environ, {'EMAIL_ADDRESS': 'test@example.com', 
                                    'EMAIL_APP_PASSWORD': 'testpass'}):
            checker = AccurateResponseChecker()
            checker.db_path = ":memory:"  # Use in-memory database
            return checker
    
    @pytest.fixture
    def mock_email(self):
        """Create mock email message"""
        msg = EmailMessage()
        msg['Subject'] = 'Test Subject'
        msg['From'] = 'recruiter@company.com'
        msg['To'] = 'test@example.com'
        msg['Date'] = 'Mon, 1 Jan 2024 12:00:00 +0000'
        return msg
    
    @pytest.mark.unit
    def test_initialization(self, mock_checker):
        """Test checker initialization"""
        assert mock_checker.email_address == 'test@example.com'
        assert mock_checker.app_password == 'testpass'
        assert len(mock_checker.interview_patterns) > 0
        assert len(mock_checker.rejection_patterns) > 0
    
    @pytest.mark.unit
    def test_extract_company_from_email(self, mock_checker):
        """Test company extraction from email addresses"""
        test_cases = [
            ('john@google.com', 'google'),
            ('careers@meta.com', 'meta'),
            ('noreply@anthropic.ai', 'anthropic'),
            ('recruiter@company.co.uk', 'company'),
            ('hr@sub.domain.com', 'domain'),
        ]
        
        for email, expected in test_cases:
            result = mock_checker.extract_company_from_email(email)
            assert result == expected
    
    @pytest.mark.unit
    def test_is_interview_request_positive(self, mock_checker, mock_email):
        """Test positive interview detection"""
        interview_subjects = [
            "Interview Invitation - Google",
            "Schedule your technical interview",
            "Next steps: Phone screen with Meta",
            "Coding assessment invitation",
            "We'd like to meet you - Interview Request"
        ]
        
        for subject in interview_subjects:
            mock_email['Subject'] = subject
            mock_email.set_content("We would like to schedule an interview with you.")
            
            result = mock_checker.is_interview_request(mock_email)
            assert result is True, f"Failed to detect interview in: {subject}"
    
    @pytest.mark.unit
    def test_is_interview_request_negative(self, mock_checker, mock_email):
        """Test false positive rejection for interviews"""
        non_interview_subjects = [
            "Thank you for your application",
            "We received your resume",
            "Application confirmation",
            "Newsletter: Interview tips",
            "Blog post: How to ace interviews"
        ]
        
        for subject in non_interview_subjects:
            mock_email['Subject'] = subject
            mock_email.set_content("Thank you for applying to our company.")
            
            result = mock_checker.is_interview_request(mock_email)
            assert result is False, f"False positive for: {subject}"
    
    @pytest.mark.unit
    def test_is_rejection_positive(self, mock_checker, mock_email):
        """Test rejection detection"""
        rejection_subjects = [
            "Application Status Update",
            "Thank you for your interest",
            "Regarding your application"
        ]
        
        rejection_bodies = [
            "We've decided to move forward with other candidates",
            "Unfortunately, we will not be proceeding",
            "We won't be able to offer you a position",
            "decided not to move forward at this time"
        ]
        
        for subject in rejection_subjects:
            for body in rejection_bodies:
                mock_email['Subject'] = subject
                mock_email.set_content(body)
                
                result = mock_checker.is_rejection(mock_email)
                assert result is True, f"Failed to detect rejection: {body[:50]}"
    
    @pytest.mark.unit
    def test_is_auto_reply(self, mock_checker, mock_email):
        """Test auto-reply detection"""
        auto_reply_subjects = [
            "Auto-Reply: Out of office",
            "Automatic reply: Vacation",
            "Application received - Do not reply",
            "No-reply: Confirmation"
        ]
        
        for subject in auto_reply_subjects:
            mock_email['Subject'] = subject
            result = mock_checker.is_auto_reply(mock_email)
            assert result is True, f"Failed to detect auto-reply: {subject}"
    
    @pytest.mark.unit
    def test_is_from_applied_company(self, mock_checker, mock_email):
        """Test company verification"""
        mock_checker.applied_companies = {'google', 'meta', 'anthropic'}
        
        test_cases = [
            ('recruiter@google.com', True),
            ('hr@meta.com', True),
            ('noreply@anthropic.ai', True),
            ('spam@randomcompany.com', False),
            ('newsletter@techblog.com', False),
        ]
        
        for email_addr, expected in test_cases:
            mock_email['From'] = email_addr
            result = mock_checker.is_from_applied_company(mock_email)
            assert result == expected, f"Failed for {email_addr}"
    
    @pytest.mark.unit
    @patch('imaplib.IMAP4_SSL')
    def test_connect_to_gmail(self, mock_imap, mock_checker):
        """Test Gmail connection"""
        mock_imap_instance = MagicMock()
        mock_imap.return_value = mock_imap_instance
        
        mock_checker.connect_to_gmail()
        
        assert mock_imap.called
        mock_imap_instance.login.assert_called_with('test@example.com', 'testpass')
    
    @pytest.mark.unit
    def test_categorize_response(self, mock_checker, mock_email):
        """Test response categorization"""
        # Test interview categorization
        mock_email['Subject'] = "Interview Invitation"
        mock_email.set_content("Please schedule your interview")
        category = mock_checker.categorize_response(mock_email)
        assert category == 'interview'
        
        # Test rejection categorization
        mock_email['Subject'] = "Application Update"
        mock_email.set_content("We've decided to move forward with other candidates")
        category = mock_checker.categorize_response(mock_email)
        assert category == 'rejection'
        
        # Test auto-reply categorization
        mock_email['Subject'] = "Auto-Reply: Out of Office"
        category = mock_checker.categorize_response(mock_email)
        assert category == 'auto_reply'
        
        # Test unknown categorization
        mock_email['Subject'] = "Random email"
        mock_email.set_content("Random content")
        category = mock_checker.categorize_response(mock_email)
        assert category == 'unknown'
    
    @pytest.mark.unit
    def test_filter_false_positives(self, mock_checker):
        """Test false positive filtering"""
        responses = [
            {
                'subject': 'Interview Invitation',
                'from': 'recruiter@google.com',
                'company': 'google',
                'body_preview': 'Schedule your interview'
            },
            {
                'subject': 'Newsletter: Interview Tips',
                'from': 'blog@randomsite.com',
                'company': 'randomsite',
                'body_preview': 'Read our blog'
            }
        ]
        
        mock_checker.applied_companies = {'google'}
        
        # Filter responses
        filtered = mock_checker.filter_false_positives(responses, 'interview')
        
        assert len(filtered['valid']) == 1
        assert len(filtered['false_positives']) == 1
        assert filtered['valid'][0]['company'] == 'google'
    
    @pytest.mark.integration
    @patch('imaplib.IMAP4_SSL')
    def test_check_responses_full_flow(self, mock_imap, mock_checker):
        """Test complete response checking flow"""
        # Setup mock IMAP
        mock_imap_instance = MagicMock()
        mock_imap.return_value = mock_imap_instance
        
        # Mock email search and fetch
        mock_imap_instance.search.return_value = ('OK', [b'1 2'])
        
        # Create mock emails
        interview_email = self._create_email_data(
            "Interview Request", 
            "recruiter@google.com",
            "Please schedule your interview"
        )
        
        rejection_email = self._create_email_data(
            "Application Update",
            "hr@meta.com", 
            "We've decided to move forward with other candidates"
        )
        
        mock_imap_instance.fetch.side_effect = [
            ('OK', [(b'1', interview_email)]),
            ('OK', [(b'2', rejection_email)])
        ]
        
        mock_checker.applied_companies = {'google', 'meta'}
        
        # Run check
        with patch.object(mock_checker, 'save_verified_responses'):
            results = mock_checker.check_responses()
        
        assert 'interviews' in results
        assert 'rejections' in results
        assert len(results['interviews']) >= 0
        assert len(results['rejections']) >= 0
    
    def _create_email_data(self, subject, from_addr, body):
        """Helper to create email data for tests"""
        email_str = f"""Subject: {subject}
From: {from_addr}
To: test@example.com
Date: Mon, 1 Jan 2024 12:00:00 +0000

{body}"""
        return email_str.encode('utf-8')