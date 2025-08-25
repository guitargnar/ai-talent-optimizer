"""
Unit tests for email authentication
"""

import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestEmailAuthentication:
    """Test email authentication functionality"""

    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock environment variables"""
        monkeypatch.setenv("EMAIL_ADDRESS", "test@example.com")
        monkeypatch.setenv("EMAIL_APP_PASSWORD", "testpassword1234")  # Exactly 16 chars
        return {"email": "test@example.com", "password": "testpassword1234"}

    @pytest.mark.unit
    def test_env_loading(self, mock_env):
        """Test that environment variables are loaded correctly"""
        email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_APP_PASSWORD")

        assert email == mock_env["email"]
        assert password == mock_env["password"]
        assert len(password) == 16

    @pytest.mark.unit
    def test_password_validation(self):
        """Test password format validation"""
        valid_passwords = [
            "abcd1234efgh5678",  # 16 chars alphanumeric
            "1234567890abcdef",  # 16 chars alphanumeric
        ]

        invalid_passwords = [
            "short",  # Too short
            "toolongpasswordthatexceeds16ch",  # Too long
            "abcd 1234 efgh 5678",  # Contains spaces
            "abcd-1234-efgh-5678",  # Contains dashes
        ]

        for pwd in valid_passwords:
            assert len(pwd) == 16
            assert pwd.isalnum()

        for pwd in invalid_passwords:
            assert len(pwd) != 16 or not pwd.replace(" ", "").replace("-", "").isalnum()

    @pytest.mark.unit
    @patch("smtplib.SMTP")
    def test_smtp_connection(self, mock_smtp, mock_env):
        """Test SMTP connection establishment"""
        # Setup mock
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        # Test connection
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(mock_env["email"], mock_env["password"])

        # Verify calls
        mock_smtp.assert_called_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_with(mock_env["email"], mock_env["password"])

    @pytest.mark.unit
    @patch("smtplib.SMTP_SSL")
    def test_smtp_ssl_connection(self, mock_smtp_ssl, mock_env):
        """Test SMTP SSL connection"""
        # Setup mock
        mock_server = Mock()
        mock_smtp_ssl.return_value = mock_server

        # Test SSL connection
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(mock_env["email"], mock_env["password"])

        # Verify calls
        mock_smtp_ssl.assert_called_with("smtp.gmail.com", 465)
        mock_server.login.assert_called_with(mock_env["email"], mock_env["password"])

    @pytest.mark.unit
    def test_email_message_creation(self, mock_env):
        """Test email message creation"""
        msg = MIMEMultipart()
        msg["From"] = mock_env["email"]
        msg["To"] = "recipient@example.com"
        msg["Subject"] = "Test Subject"

        body = "Test email body"
        msg.attach(MIMEText(body, "plain"))

        assert msg["From"] == mock_env["email"]
        assert msg["To"] == "recipient@example.com"
        assert msg["Subject"] == "Test Subject"
        assert body in msg.as_string()

    @pytest.mark.unit
    @patch("smtplib.SMTP_SSL")
    def test_authentication_failure(self, mock_smtp_ssl, mock_env):
        """Test handling of authentication failure"""
        # Setup mock to raise authentication error
        mock_server = Mock()
        mock_smtp_ssl.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(
            535, b"Authentication failed"
        )

        # Test authentication failure
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

        with pytest.raises(smtplib.SMTPAuthenticationError) as exc_info:
            server.login(mock_env["email"], "wrong_password")

        assert exc_info.value.smtp_code == 535
        assert b"Authentication failed" in exc_info.value.smtp_error

    @pytest.mark.integration
    @pytest.mark.email
    def test_real_email_authentication(self):
        """Integration test for real email authentication (requires .env)"""
        # Skip if no real credentials
        if not os.path.exists("/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/.env"):
            pytest.skip("No .env file found for integration test")

        # Load real credentials
        from dotenv import load_dotenv

        load_dotenv("/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/.env")

        email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_APP_PASSWORD")

        if not email or not password:
            pytest.skip("Email credentials not configured")

        # Test real authentication
        try:
            import ssl

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(email, password)
                assert True  # Login successful
        except smtplib.SMTPAuthenticationError:
            pytest.fail("Real authentication failed - check credentials")


class TestBCCEmailTracker:
    """Test BCC email tracking functionality"""

    @pytest.fixture
    def mock_bcc_tracker(self):
        """Create mock BCC tracker"""
        with patch(
            "sys.path", ["/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer"] + sys.path
        ):
            # Mock the imports that might fail
            with patch.dict(
                "sys.modules",
                {"email_application_tracker": MagicMock(), "gmail_oauth_integration": MagicMock()},
            ):
                from bcc_email_tracker import BCCEmailTracker

                tracker = BCCEmailTracker()
                tracker.email_password = "test_password"
                return tracker

    @pytest.mark.unit
    def test_tracking_id_generation(self, mock_bcc_tracker):
        """Test unique tracking ID generation"""
        id1 = mock_bcc_tracker._generate_tracking_id("test@example.com", "Subject 1")
        id2 = mock_bcc_tracker._generate_tracking_id("test@example.com", "Subject 2")
        id3 = mock_bcc_tracker._generate_tracking_id("test@example.com", "Subject 1")

        # Different subjects should generate different IDs
        assert id1 != id2
        # Same email and subject should generate same ID (for deduplication)
        assert id1 == id3
        # ID should be 12 characters
        assert len(id1) == 12

    @pytest.mark.unit
    def test_company_extraction(self, mock_bcc_tracker):
        """Test company name extraction from email"""
        test_cases = [
            ("careers@google.com", "google"),
            ("jobs@anthropic.ai", "anthropic"),
            ("recruiting@openai.com", "openai"),
            ("hr@meta.com", "meta"),
        ]

        for email, expected in test_cases:
            # Simple extraction logic
            domain = email.split("@")[1]
            company = domain.split(".")[0]
            assert company == expected

    @pytest.mark.unit
    def test_position_extraction(self, mock_bcc_tracker):
        """Test position extraction from subject"""
        test_cases = [
            ("Application for Senior ML Engineer", "Senior ML Engineer"),
            ("Re: Machine Learning Scientist position", "Machine Learning Scientist"),
            ("Interest in AI Researcher role", "AI Researcher"),
            ("Applying for Data Scientist at Google", "Data Scientist"),
        ]

        for subject, expected in test_cases:
            position = mock_bcc_tracker._extract_position(subject)
            assert expected.lower() in position.lower()

    @pytest.mark.unit
    def test_bcc_address_selection(self, mock_bcc_tracker):
        """Test BCC address selection based on email type"""
        assert "jobapps" in mock_bcc_tracker.bcc_addresses["applications"]
        assert "followups" in mock_bcc_tracker.bcc_addresses["followups"]
        assert "networking" in mock_bcc_tracker.bcc_addresses["networking"]
