"""
Email service for sending applications and communications.
Handles SMTP, deliverability, and bounce detection.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Optional, List
import time

from ..config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for handling all email operations."""
    
    def __init__(self):
        """Initialize email service."""
        self.smtp_server = settings.email.smtp_server
        self.smtp_port = settings.email.smtp_port
        self.email_address = settings.email.address
        self.app_password = settings.email.app_password
        
        # Track sent emails for rate limiting
        self.emails_sent_today = 0
        self.last_send_time = None
    
    def send_application(
        self,
        to_email: str,
        subject: str,
        body: str,
        resume_path: Optional[str] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send job application email with optional resume attachment.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (HTML or plain text)
            resume_path: Path to resume file to attach
            bcc: List of BCC addresses for tracking
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Check configuration
            if not self._is_configured():
                logger.error("Email service not configured")
                return False
            
            # Check daily limit
            if self.emails_sent_today >= settings.email.max_per_day:
                logger.warning(f"Daily email limit reached ({settings.email.max_per_day})")
                return False
            
            # Rate limiting
            self._apply_rate_limit()
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add BCC for tracking
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            elif settings.email.address:
                # Always BCC self for tracking
                msg['Bcc'] = f"{self.email_address.split('@')[0]}+sent@gmail.com"
            
            # Add body
            msg.attach(MIMEText(body, 'html' if '<html>' in body else 'plain'))
            
            # Attach resume if provided
            if resume_path and Path(resume_path).exists():
                with open(resume_path, 'rb') as f:
                    attachment = MIMEApplication(f.read(), _subtype='pdf')
                    attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=Path(resume_path).name
                    )
                    msg.attach(attachment)
            
            # Send email
            success = self._send_smtp(msg, to_email)
            
            if success:
                self.emails_sent_today += 1
                self.last_send_time = time.time()
                logger.info(f"Email sent to {to_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> bool:
        """
        Send simple email without attachments.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            
        Returns:
            True if sent successfully
        """
        return self.send_application(to_email, subject, body)
    
    def _send_smtp(self, msg: MIMEMultipart, to_email: str) -> bool:
        """Send email via SMTP."""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.app_password)
                
                # Get all recipients (To + Bcc)
                recipients = [to_email]
                if msg.get('Bcc'):
                    recipients.extend(msg['Bcc'].split(', '))
                
                server.send_message(msg, to_addrs=recipients)
                return True
                
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed - check credentials")
            return False
        except smtplib.SMTPRecipientsRefused:
            logger.error(f"Recipient refused: {to_email}")
            return False
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False
    
    def _is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.email_address and self.app_password)
    
    def _apply_rate_limit(self):
        """Apply rate limiting between emails."""
        if self.last_send_time:
            elapsed = time.time() - self.last_send_time
            if elapsed < settings.email.delay_seconds:
                sleep_time = settings.email.delay_seconds - elapsed
                logger.debug(f"Rate limiting: sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
    
    def verify_email(self, email: str) -> bool:
        """
        Verify if an email address is valid and deliverable.
        
        Args:
            email: Email address to verify
            
        Returns:
            True if email appears valid
        """
        # Basic validation
        if not email or '@' not in email:
            return False
        
        # Check for known bounce patterns
        bounce_domains = ['noreply', 'no-reply', 'donotreply']
        if any(pattern in email.lower() for pattern in bounce_domains):
            return False
        
        # TODO: Implement more sophisticated verification
        # - DNS MX record check
        # - SMTP verification
        # - Disposable email detection
        
        return True
    
    def check_bounces(self) -> List[str]:
        """
        Check for bounced emails via IMAP.
        
        Returns:
            List of bounced email addresses
        """
        # TODO: Implement IMAP bounce checking
        # This would connect to Gmail via IMAP and scan for bounce messages
        
        return []