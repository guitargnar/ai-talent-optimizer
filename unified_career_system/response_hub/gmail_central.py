#!/usr/bin/env python3
"""
Centralized Gmail Management Hub for Unified Career System
Unifies all email operations across integrated systems
"""

import os
import sys
import json
import sqlite3
import base64
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
import re
from dataclasses import dataclass
from enum import Enum

# Gmail API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Add paths for integrated systems
sys.path.append(str(Path(__file__).parent.parent.parent))
from unified_career_system.data_layer.master_database import MasterDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailType(Enum):
    """Email classification types"""
    REJECTION = "rejection"
    INTERVIEW_REQUEST = "interview_request"
    OFFER = "offer"
    AUTO_REPLY = "auto_reply"
    FOLLOW_UP_NEEDED = "follow_up_needed"
    INFORMATION_REQUEST = "information_request"
    UNKNOWN = "unknown"


@dataclass
class EmailMessage:
    """Structured email message"""
    message_id: str
    thread_id: str
    from_email: str
    from_name: str
    to_email: str
    subject: str
    body: str
    received_date: datetime
    labels: List[str]
    is_job_related: bool = False
    company: Optional[str] = None
    email_type: Optional[EmailType] = None
    sentiment_score: Optional[float] = None
    action_required: bool = False
    attachments: List[str] = None


@dataclass
class EmailAction:
    """Action to take based on email"""
    action_type: str  # schedule_interview, send_follow_up, update_application
    priority: str  # high, medium, low
    deadline: Optional[datetime] = None
    details: Dict = None


class GmailCentral:
    """
    Centralized Gmail management hub
    
    Features:
    - Unified OAuth authentication
    - Multi-account support
    - Email classification with ML
    - Response tracking across all systems
    - Automated follow-up scheduling
    - Interview coordination
    """
    
    # Gmail API scope
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.send',
              'https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, db_path: str = "unified_platform.db",
                 credentials_path: str = None):
        """
        Initialize Gmail Central Hub
        
        Args:
            db_path: Path to unified database
            credentials_path: Path to Gmail credentials.json
        """
        self.db_path = db_path
        self.master_db = MasterDatabase(db_path)
        
        # Gmail service
        self.service = None
        self.credentials_path = credentials_path or self._find_credentials()
        self.token_path = Path.home() / '.gmail_token.pickle'
        
        # Email patterns for classification
        self._init_classification_patterns()
        
        # Company detection patterns
        self._init_company_patterns()
        
        # Cache for processed emails
        self.processed_cache = set()
        self._load_processed_cache()
        
        # Initialize Gmail service
        self._init_gmail_service()
        
        logger.info("Initialized GmailCentral hub")
        
    def _find_credentials(self) -> str:
        """Find Gmail credentials file"""
        possible_paths = [
            Path.home() / 'credentials.json',
            Path.home() / '.credentials' / 'gmail_credentials.json',
            Path('/Users/matthewscott/Google Gmail/credentials.json'),
            Path('credentials.json')
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
                
        logger.warning("Gmail credentials not found. Manual setup required.")
        return None
        
    def _init_gmail_service(self):
        """Initialize Gmail API service"""
        if not self.credentials_path:
            logger.warning("No credentials path set. Gmail service not initialized.")
            return
            
        creds = None
        
        # Load token if it exists
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
                
        # If there are no (valid) credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if Path(self.credentials_path).exists():
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                else:
                    logger.error(f"Credentials file not found: {self.credentials_path}")
                    return
                    
            # Save credentials for next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
                
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {e}")
            
    def _init_classification_patterns(self):
        """Initialize email classification patterns"""
        self.classification_patterns = {
            EmailType.REJECTION: [
                r'unfortunately',
                r'not moving forward',
                r'other candidates',
                r'not a match',
                r'decided to proceed with',
                r'wish you (all the )?best',
                r'not selected',
                r'unable to offer',
                r'position has been filled'
            ],
            EmailType.INTERVIEW_REQUEST: [
                r'schedule.*interview',
                r'phone screen',
                r'technical interview',
                r'meet with',
                r'available for a (call|chat|conversation)',
                r'discuss.*opportunity',
                r'next steps',
                r'coding challenge',
                r'assessment'
            ],
            EmailType.OFFER: [
                r'offer letter',
                r'pleased to offer',
                r'job offer',
                r'compensation package',
                r'salary.*benefits',
                r'start date',
                r'welcome to the team'
            ],
            EmailType.AUTO_REPLY: [
                r'received your application',
                r'thank you for applying',
                r'reviewing your application',
                r'auto(-)?reply',
                r'do not reply',
                r'confirmation of.*application',
                r'successfully submitted'
            ],
            EmailType.INFORMATION_REQUEST: [
                r'additional information',
                r'please provide',
                r'could you (send|share)',
                r'need.*documents',
                r'references',
                r'portfolio',
                r'work samples'
            ]
        }
        
    def _init_company_patterns(self):
        """Initialize company detection patterns"""
        self.company_patterns = {
            # Top tech companies
            'anthropic': 'Anthropic',
            'openai': 'OpenAI',
            'scale ai': 'Scale AI',
            'scale.ai': 'Scale AI',
            'meta': 'Meta',
            'facebook': 'Meta',
            'google': 'Google',
            'microsoft': 'Microsoft',
            'apple': 'Apple',
            'amazon': 'Amazon',
            'netflix': 'Netflix',
            
            # Startups and mid-size
            'stripe': 'Stripe',
            'plaid': 'Plaid',
            'figma': 'Figma',
            'notion': 'Notion',
            'canva': 'Canva',
            'databricks': 'Databricks',
            'snowflake': 'Snowflake',
            'confluent': 'Confluent',
            'hashicorp': 'HashiCorp',
            'datadog': 'Datadog',
            
            # Healthcare tech
            'tempus': 'Tempus',
            'flatiron': 'Flatiron Health',
            'oscar': 'Oscar Health',
            'cedar': 'Cedar',
            'zocdoc': 'Zocdoc'
        }
        
    def _load_processed_cache(self):
        """Load cache of already processed emails"""
        cursor = self.master_db.conn.cursor()
        cursor.execute("""
        SELECT gmail_message_id FROM emails
        WHERE processed = 1
        """)
        
        for row in cursor.fetchall():
            if row[0]:
                self.processed_cache.add(row[0])
                
        logger.info(f"Loaded {len(self.processed_cache)} processed emails to cache")
        
    def fetch_recent_emails(self, days_back: int = 7,
                           max_results: int = 100) -> List[EmailMessage]:
        """
        Fetch recent emails from Gmail
        
        Args:
            days_back: Number of days to look back
            max_results: Maximum emails to fetch
            
        Returns:
            List of email messages
        """
        if not self.service:
            logger.warning("Gmail service not initialized")
            return []
            
        try:
            # Build query for job-related emails
            after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            query = f'after:{after_date} (subject:application OR subject:interview OR subject:offer OR from:careers OR from:recruiting OR from:jobs)'
            
            # Get message list
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No recent job-related emails found")
                return []
                
            # Fetch full message details
            email_messages = []
            for msg in messages:
                if msg['id'] in self.processed_cache:
                    continue
                    
                try:
                    # Get message details
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id']
                    ).execute()
                    
                    # Parse message
                    email_msg = self._parse_email_message(message)
                    if email_msg:
                        email_messages.append(email_msg)
                        
                except Exception as e:
                    logger.error(f"Error fetching message {msg['id']}: {e}")
                    
            logger.info(f"Fetched {len(email_messages)} new job-related emails")
            return email_messages
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return []
            
    def _parse_email_message(self, message: Dict) -> Optional[EmailMessage]:
        """Parse Gmail message into EmailMessage object"""
        try:
            msg_id = message['id']
            thread_id = message['threadId']
            labels = message.get('labelIds', [])
            
            # Parse headers
            headers = {h['name']: h['value'] 
                      for h in message['payload'].get('headers', [])}
            
            from_header = headers.get('From', '')
            from_match = re.match(r'(.+?)\s*<(.+?)>', from_header)
            
            if from_match:
                from_name = from_match.group(1).strip('"')
                from_email = from_match.group(2)
            else:
                from_name = ''
                from_email = from_header
                
            # Get email body
            body = self._extract_body(message['payload'])
            
            # Create EmailMessage
            email_msg = EmailMessage(
                message_id=msg_id,
                thread_id=thread_id,
                from_email=from_email,
                from_name=from_name,
                to_email=headers.get('To', ''),
                subject=headers.get('Subject', ''),
                body=body,
                received_date=datetime.fromtimestamp(
                    int(message['internalDate']) / 1000
                ),
                labels=labels
            )
            
            # Detect company
            email_msg.company = self._detect_company(email_msg)
            
            # Classify email
            email_msg.email_type = self._classify_email(email_msg)
            
            # Check if job-related
            email_msg.is_job_related = self._is_job_related(email_msg)
            
            # Determine if action required
            email_msg.action_required = self._check_action_required(email_msg)
            
            return email_msg
            
        except Exception as e:
            logger.error(f"Error parsing email message: {e}")
            return None
            
    def _extract_body(self, payload: Dict) -> str:
        """Extract body text from email payload"""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif 'parts' in part:
                    body += self._extract_body(part)
        elif payload['body'].get('data'):
            body = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8', errors='ignore')
            
        return body
        
    def _detect_company(self, email: EmailMessage) -> Optional[str]:
        """Detect company from email content"""
        # Check email domain
        domain = email.from_email.split('@')[-1].lower()
        
        # Check known patterns in domain
        for pattern, company in self.company_patterns.items():
            if pattern in domain:
                return company
                
        # Check subject and body
        search_text = f"{email.subject} {email.body}".lower()
        
        for pattern, company in self.company_patterns.items():
            if pattern in search_text:
                return company
                
        return None
        
    def _classify_email(self, email: EmailMessage) -> EmailType:
        """Classify email type using patterns"""
        search_text = f"{email.subject} {email.body}".lower()
        
        # Check each classification pattern
        for email_type, patterns in self.classification_patterns.items():
            for pattern in patterns:
                if re.search(pattern, search_text, re.IGNORECASE):
                    return email_type
                    
        return EmailType.UNKNOWN
        
    def _is_job_related(self, email: EmailMessage) -> bool:
        """Determine if email is job-related"""
        # Check if company detected
        if email.company:
            return True
            
        # Check for job-related keywords
        job_keywords = [
            'application', 'interview', 'position', 'opportunity',
            'role', 'job', 'candidate', 'resume', 'offer', 'hiring'
        ]
        
        search_text = f"{email.subject} {email.body}".lower()
        
        return any(keyword in search_text for keyword in job_keywords)
        
    def _check_action_required(self, email: EmailMessage) -> bool:
        """Check if email requires action"""
        if email.email_type in [
            EmailType.INTERVIEW_REQUEST,
            EmailType.INFORMATION_REQUEST,
            EmailType.OFFER
        ]:
            return True
            
        # Check for action keywords
        action_keywords = [
            'please respond', 'let us know', 'confirm', 'reply',
            'action required', 'urgent', 'deadline', 'asap'
        ]
        
        search_text = f"{email.subject} {email.body}".lower()
        
        return any(keyword in search_text for keyword in action_keywords)
        
    def process_emails(self, emails: List[EmailMessage]) -> Dict:
        """
        Process emails and update database
        
        Args:
            emails: List of email messages to process
            
        Returns:
            Processing results
        """
        results = {
            'total': len(emails),
            'processed': 0,
            'job_related': 0,
            'actions_created': 0,
            'applications_updated': 0,
            'errors': 0
        }
        
        for email in emails:
            try:
                if not email.is_job_related:
                    continue
                    
                results['job_related'] += 1
                
                # Record email in database
                self._record_email(email)
                
                # Update application if matched
                if email.company:
                    updated = self._update_application_status(email)
                    if updated:
                        results['applications_updated'] += 1
                        
                # Create action if required
                if email.action_required:
                    action = self._create_action(email)
                    if action:
                        results['actions_created'] += 1
                        
                # Mark as processed
                self.processed_cache.add(email.message_id)
                results['processed'] += 1
                
            except Exception as e:
                logger.error(f"Error processing email {email.message_id}: {e}")
                results['errors'] += 1
                
        return results
        
    def _record_email(self, email: EmailMessage):
        """Record email in database"""
        cursor = self.master_db.conn.cursor()
        
        # Generate email UID
        email_uid = email.message_id[:16]
        
        # Determine direction
        direction = 'incoming'  # Most job emails are incoming
        
        # Find related job/application
        job_uid = None
        application_uid = None
        
        if email.company:
            # Try to match to recent application
            cursor.execute("""
            SELECT j.job_uid, a.application_uid
            FROM applications a
            JOIN master_jobs j ON a.job_uid = j.job_uid
            WHERE LOWER(j.company) = LOWER(?)
            ORDER BY a.applied_date DESC
            LIMIT 1
            """, (email.company,))
            
            result = cursor.fetchone()
            if result:
                job_uid = result[0]
                application_uid = result[1]
                
        # Insert email record
        cursor.execute("""
        INSERT OR IGNORE INTO email_tracking (
            email_uid, direction, email_from, email_to,
            subject, body, is_job_related, company,
            job_uid, application_uid, sentiment, urgency,
            action_required, action_type, gmail_message_id,
            thread_id, received_date, processed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email_uid, direction, email.from_email, email.to_email,
            email.subject, email.body[:5000], email.is_job_related,
            email.company, job_uid, application_uid,
            email.sentiment_score, 
            'high' if email.action_required else 'low',
            email.action_required,
            email.email_type.value if email.email_type else None,
            email.message_id, email.thread_id,
            email.received_date, True
        ))
        
        self.master_db.conn.commit()
        
    def _update_application_status(self, email: EmailMessage) -> bool:
        """Update application status based on email"""
        if not email.company:
            return False
            
        cursor = self.master_db.conn.cursor()
        
        # Map email type to application outcome
        outcome_map = {
            EmailType.REJECTION: 'rejected',
            EmailType.INTERVIEW_REQUEST: 'interview',
            EmailType.OFFER: 'offer',
            EmailType.AUTO_REPLY: 'pending'
        }
        
        outcome = outcome_map.get(email.email_type)
        
        if outcome and outcome != 'pending':
            # Update most recent application for this company
            cursor.execute("""
            UPDATE applications
            SET response_received = 1,
                response_date = ?,
                response_type = ?,
                outcome = ?
            WHERE application_uid = (
                SELECT a.application_uid
                FROM applications a
                JOIN master_jobs j ON a.job_uid = j.job_uid
                WHERE LOWER(j.company) = LOWER(?)
                AND a.response_received = 0
                ORDER BY a.applied_date DESC
                LIMIT 1
            )
            """, (
                email.received_date,
                email.email_type.value,
                outcome,
                email.company
            ))
            
            if cursor.rowcount > 0:
                self.master_db.conn.commit()
                logger.info(f"Updated application status for {email.company}: {outcome}")
                return True
                
        return False
        
    def _create_action(self, email: EmailMessage) -> Optional[EmailAction]:
        """Create action based on email"""
        if not email.action_required:
            return None
            
        action = None
        
        if email.email_type == EmailType.INTERVIEW_REQUEST:
            action = EmailAction(
                action_type='schedule_interview',
                priority='high',
                deadline=email.received_date + timedelta(days=2),
                details={
                    'company': email.company,
                    'email_id': email.message_id,
                    'thread_id': email.thread_id
                }
            )
            
        elif email.email_type == EmailType.INFORMATION_REQUEST:
            action = EmailAction(
                action_type='provide_information',
                priority='medium',
                deadline=email.received_date + timedelta(days=3),
                details={
                    'company': email.company,
                    'request': 'Check email for details'
                }
            )
            
        elif email.email_type == EmailType.OFFER:
            action = EmailAction(
                action_type='review_offer',
                priority='high',
                deadline=email.received_date + timedelta(days=5),
                details={
                    'company': email.company,
                    'requires_response': True
                }
            )
            
        if action:
            # Store action in database or task queue
            logger.info(f"Created action: {action.action_type} for {email.company}")
            
        return action
        
    def send_follow_up(self, company: str, application_uid: str,
                       template: str = 'standard') -> bool:
        """
        Send follow-up email for an application
        
        Args:
            company: Company name
            application_uid: Application unique ID
            template: Follow-up template to use
            
        Returns:
            Success status
        """
        if not self.service:
            logger.warning("Gmail service not initialized")
            return False
            
        try:
            # Get application details
            cursor = self.master_db.conn.cursor()
            cursor.execute("""
            SELECT j.title, a.applied_date
            FROM applications a
            JOIN master_jobs j ON a.job_uid = j.job_uid
            WHERE a.application_uid = ?
            """, (application_uid,))
            
            result = cursor.fetchone()
            if not result:
                logger.error(f"Application {application_uid} not found")
                return False
                
            title = result[0]
            applied_date = datetime.fromisoformat(result[1])
            
            # Generate follow-up email
            subject = f"Following up on {position} application - Matthew Scott"
            
            if template == 'standard':
                body = f"""Dear {company} Hiring Team,

I hope this email finds you well. I wanted to follow up on my application for the {position} title, 
which I submitted on {applied_date.strftime('%B %d, %Y')}.

I remain very interested in this opportunity and would love to discuss how my experience in ML engineering 
and production systems can contribute to {company}'s success.

I'm happy to provide any additional information you might need.

Thank you for your time and consideration.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
"""
            else:
                # Other templates can be added here
                body = self._generate_custom_follow_up(company, title, applied_date)
                
            # Create message
            message = {
                'raw': base64.urlsafe_b64encode(
                    f"To: careers@{company.lower().replace(' ', '')}.com\n"
                    f"Subject: {subject}\n\n{body}".encode()
                ).decode()
            }
            
            # Send email
            sent = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            logger.info(f"Follow-up sent to {company} for position {position}")
            
            # Record follow-up
            cursor.execute("""
            UPDATE applications
            SET follow_ups_sent = follow_ups_sent + 1,
                last_follow_up = CURRENT_TIMESTAMP
            WHERE application_uid = ?
            """, (application_uid,))
            
            self.master_db.conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send follow-up: {e}")
            return False
            
    def _generate_custom_follow_up(self, company: str, position: str,
                                  applied_date: datetime) -> str:
        """Generate custom follow-up based on company and time elapsed"""
        days_elapsed = (datetime.now() - applied_date).days
        
        if days_elapsed < 7:
            urgency = "I understand you're likely reviewing many applications"
        elif days_elapsed < 14:
            urgency = "I wanted to check on the status of my application"
        else:
            urgency = "I remain enthusiastic about this opportunity"
            
        return f"""Dear {company} Hiring Team,

{urgency} for the {position} position.

With my 10+ years of experience building production ML systems and achieving measurable 
business impact (including $1.2M annual savings through ML optimization), I'm confident 
I can make significant contributions to your team.

I'd welcome the opportunity to discuss how my background aligns with your needs.

Looking forward to hearing from you.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
LinkedIn: linkedin.com/in/mscott77
"""
        
    def get_email_stats(self) -> Dict:
        """Get email statistics"""
        cursor = self.master_db.conn.cursor()
        
        stats = {}
        
        # Total emails
        cursor.execute("SELECT COUNT(*) FROM emails")
        stats['total_emails'] = cursor.fetchone()[0]
        
        # Job-related emails
        cursor.execute("SELECT COUNT(*) FROM emails WHERE is_job_related = 1")
        stats['job_related'] = cursor.fetchone()[0]
        
        # By direction
        cursor.execute("""
        SELECT direction, COUNT(*)
        FROM emails
        GROUP BY direction
        """)
        stats['by_direction'] = dict(cursor.fetchall())
        
        # By type
        cursor.execute("""
        SELECT action_type, COUNT(*)
        FROM emails
        WHERE action_type IS NOT NULL
        GROUP BY action_type
        """)
        stats['by_type'] = dict(cursor.fetchall())
        
        # Actions required
        cursor.execute("SELECT COUNT(*) FROM emails WHERE action_required = 1")
        stats['actions_required'] = cursor.fetchone()[0]
        
        # Response rate
        cursor.execute("""
        SELECT 
            COUNT(CASE WHEN response_received = 1 THEN 1 END) * 100.0 / COUNT(*)
        FROM applications
        WHERE applied_date > date('now', '-30 days')
        """)
        stats['response_rate_30d'] = cursor.fetchone()[0] or 0
        
        return stats


def main():
    """Test Gmail Central Hub"""
    hub = GmailCentral()
    
    print("📧 Gmail Central Hub v1.0")
    print("=" * 60)
    
    # Get email statistics
    stats = hub.get_email_stats()
    print("\n📊 Email Statistics:")
    print(f"  • Total emails tracked: {stats['total_emails']}")
    print(f"  • Job-related: {stats['job_related']}")
    print(f"  • Actions required: {stats['actions_required']}")
    print(f"  • 30-day response rate: {stats['response_rate_30d']:.1f}%")
    
    # Fetch recent emails
    print("\n🔍 Fetching recent emails...")
    emails = hub.fetch_recent_emails(days_back=7, max_results=20)
    
    if emails:
        print(f"Found {len(emails)} new job-related emails")
        
        # Process emails
        print("\n⚙️ Processing emails...")
        results = hub.process_emails(emails)
        
        print(f"\n✅ Processing Results:")
        print(f"  • Processed: {results['processed']}/{results['total']}")
        print(f"  • Applications updated: {results['applications_updated']}")
        print(f"  • Actions created: {results['actions_created']}")
        
        # Show sample emails
        print("\n📬 Recent Job Emails:")
        for email in emails[:5]:
            print(f"\n  From: {email.from_name or email.from_email}")
            print(f"  Company: {email.company or 'Unknown'}")
            print(f"  Subject: {email.subject}")
            print(f"  Type: {email.email_type.value if email.email_type else 'Unknown'}")
            print(f"  Action Required: {'Yes' if email.action_required else 'No'}")
    else:
        print("No new job-related emails found")
        
    print("\n✨ Gmail Central Hub test complete!")


if __name__ == "__main__":
    main()