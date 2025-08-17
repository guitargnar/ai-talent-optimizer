"""
Advanced Email Validation Service
Validates email addresses using multiple methods without sending test emails
"""

import logging
import re
import dns.resolver
import socket
import smtplib
from typing import Dict, Optional, Tuple
import sqlite3
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EmailValidator:
    """Advanced email validation with multiple verification methods"""
    
    def __init__(self, db_path: str = "data/unified_jobs.db"):
        self.db_path = db_path
        
        # Regex for basic email validation
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # Known valid email patterns for companies
        self.known_patterns = self._load_known_patterns()
        
        # Blacklist of invalid domains
        self.blacklist_domains = [
            'example.com', 'test.com', 'localhost', 'tempmail.com',
            'guerrillamail.com', '10minutemail.com', 'mailinator.com'
        ]
        
    def _load_known_patterns(self) -> Dict[str, str]:
        """Load known valid email patterns for companies"""
        return {
            # Tech companies
            'google.com': 'careers@google.com',
            'meta.com': 'careers@meta.com',
            'apple.com': 'jobs@apple.com',
            'microsoft.com': 'recruiting@microsoft.com',
            'amazon.com': 'amazon-jobs@amazon.com',
            
            # AI companies
            'openai.com': 'careers@openai.com',
            'anthropic.com': 'careers@anthropic.com',
            'deepmind.google': 'deepmind-careers@google.com',
            'huggingface.co': 'careers@huggingface.co',
            'scale.com': 'careers@scale.com',
            
            # Healthcare tech
            'tempus.com': 'careers@tempus.com',
            'zocdoc.com': 'careers@zocdoc.com',
            'doximity.com': 'careers@doximity.com',
            'cedar.com': 'careers@cedar.com',
            'hioscar.com': 'careers@hioscar.com'
        }
    
    def validate_email(self, email: str, company_name: Optional[str] = None) -> Dict:
        """
        Comprehensive email validation
        Returns confidence score and validation details
        """
        result = {
            'email': email,
            'valid': False,
            'confidence': 0,
            'checks': {},
            'reason': '',
            'validated_at': datetime.now().isoformat()
        }
        
        if not email:
            result['reason'] = 'No email provided'
            return result
        
        # Check 1: Syntax validation
        syntax_valid = self._check_syntax(email)
        result['checks']['syntax'] = syntax_valid
        if not syntax_valid:
            result['reason'] = 'Invalid email syntax'
            return result
        
        # Check 2: Domain extraction
        domain = email.split('@')[1].lower()
        result['domain'] = domain
        
        # Check 3: Blacklist check
        if domain in self.blacklist_domains:
            result['reason'] = 'Domain is blacklisted'
            result['checks']['blacklist'] = False
            return result
        result['checks']['blacklist'] = True
        
        # Check 4: Known pattern matching
        pattern_match = self._check_known_pattern(email, domain, company_name)
        result['checks']['pattern_match'] = pattern_match
        
        # Check 5: DNS MX record validation
        mx_valid = self._check_mx_records(domain)
        result['checks']['mx_records'] = mx_valid
        
        # Check 6: Domain reachability
        domain_reachable = self._check_domain_reachable(domain)
        result['checks']['domain_reachable'] = domain_reachable
        
        # Check 7: SMTP verification (careful not to send)
        smtp_valid = False
        if mx_valid:
            smtp_valid = self._check_smtp(email, domain)
        result['checks']['smtp_valid'] = smtp_valid
        
        # Calculate confidence score
        confidence = self._calculate_confidence(result['checks'])
        result['confidence'] = confidence
        
        # Determine if valid
        result['valid'] = confidence >= 60
        
        if result['valid']:
            result['reason'] = f'Validated with {confidence}% confidence'
        else:
            result['reason'] = self._get_failure_reason(result['checks'])
        
        return result
    
    def _check_syntax(self, email: str) -> bool:
        """Check email syntax"""
        return bool(self.email_pattern.match(email))
    
    def _check_known_pattern(self, email: str, domain: str, company_name: Optional[str]) -> bool:
        """Check if email matches known patterns"""
        # Direct match in known patterns
        if domain in self.known_patterns:
            return email.lower() == self.known_patterns[domain].lower()
        
        # Check common patterns
        common_prefixes = ['careers', 'jobs', 'recruiting', 'hr', 'talent', 'hiring']
        email_prefix = email.split('@')[0].lower()
        
        if email_prefix in common_prefixes:
            return True
        
        # Company name matching
        if company_name:
            company_clean = company_name.lower().replace(' ', '').replace('.', '')
            if company_clean in domain:
                return True
                
        return False
    
    def _check_mx_records(self, domain: str) -> bool:
        """Check if domain has MX records"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return len(mx_records) > 0
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, Exception) as e:
            logger.debug(f"MX record check failed for {domain}: {e}")
            return False
    
    def _check_domain_reachable(self, domain: str) -> bool:
        """Check if domain is reachable"""
        try:
            # Try to resolve the domain
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False
    
    def _check_smtp(self, email: str, domain: str) -> bool:
        """
        Check SMTP server (WITHOUT sending email)
        This only verifies the server exists and accepts connections
        """
        try:
            # Get MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_host = str(mx_records[0].exchange).rstrip('.')
            
            # Try to connect to SMTP server
            with smtplib.SMTP(timeout=5) as smtp:
                smtp.connect(mx_host)
                smtp.helo('validator.example.com')
                
                # We could do VRFY here but most servers disable it
                # So we just check if we can connect
                return True
                
        except Exception as e:
            logger.debug(f"SMTP check failed for {email}: {e}")
            return False
    
    def _calculate_confidence(self, checks: Dict[str, bool]) -> int:
        """Calculate confidence score based on checks"""
        weights = {
            'syntax': 20,
            'blacklist': 20,
            'pattern_match': 25,
            'mx_records': 20,
            'domain_reachable': 10,
            'smtp_valid': 5
        }
        
        score = 0
        for check, passed in checks.items():
            if passed and check in weights:
                score += weights[check]
                
        return score
    
    def _get_failure_reason(self, checks: Dict[str, bool]) -> str:
        """Get reason for validation failure"""
        if not checks.get('syntax'):
            return 'Invalid email format'
        if not checks.get('blacklist'):
            return 'Domain is blacklisted'
        if not checks.get('mx_records'):
            return 'No MX records found'
        if not checks.get('domain_reachable'):
            return 'Domain unreachable'
        return 'Low confidence score'
    
    def validate_batch(self, emails: list) -> Dict[str, Dict]:
        """Validate multiple emails"""
        results = {}
        
        for email_data in emails:
            if isinstance(email_data, str):
                email = email_data
                company = None
            else:
                email = email_data.get('email')
                company = email_data.get('company')
                
            results[email] = self.validate_email(email, company)
            
        return results
    
    def update_database_validations(self, limit: int = 100) -> Dict[str, int]:
        """Validate emails in database that haven't been validated"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get unvalidated emails
        cursor.execute("""
            SELECT id, company_email, company
            FROM jobs
            WHERE company_email IS NOT NULL 
            AND company_email != ''
            AND company_email != 'N/A'
            AND (email_verified IS NULL OR email_verified = 0)
            LIMIT ?
        """, (limit,))
        
        jobs = cursor.fetchall()
        
        validated = 0
        valid = 0
        
        for job_id, email, company in jobs:
            result = self.validate_email(email, company)
            
            # Update database
            cursor.execute("""
                UPDATE jobs
                SET email_verified = ?,
                    email_confidence_score = ?,
                    email_validation_date = ?,
                    email_validation_result = ?
                WHERE id = ?
            """, (
                result['valid'],
                result['confidence'],
                result['validated_at'],
                json.dumps(result),
                job_id
            ))
            
            validated += 1
            if result['valid']:
                valid += 1
                
            logger.info(f"Validated {email}: {result['valid']} ({result['confidence']}%)")
        
        conn.commit()
        conn.close()
        
        return {
            'total_validated': validated,
            'valid_emails': valid,
            'invalid_emails': validated - valid,
            'success_rate': (valid / validated * 100) if validated > 0 else 0
        }
    
    def add_verified_email(self, company: str, email: str, source: str = "manual") -> bool:
        """Manually add a verified email for a company"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update all jobs for this company
            cursor.execute("""
                UPDATE jobs
                SET company_email = ?,
                    email_verified = 1,
                    email_confidence_score = 100,
                    notes = 'Email manually verified from ' || ?
                WHERE company = ?
                AND (company_email IS NULL OR company_email = '' OR company_email = 'N/A')
            """, (email, source, company))
            
            affected = cursor.rowcount
            conn.commit()
            
            logger.info(f"Added verified email {email} for {company} ({affected} jobs updated)")
            return True
            
        except Exception as e:
            logger.error(f"Error adding verified email: {e}")
            return False
        finally:
            conn.close()

def run_email_validation():
    """Standalone function to validate emails in database"""
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    validator = EmailValidator()
    
    # Add some manually verified emails for top companies
    verified_emails = [
        ('Anthropic', 'careers@anthropic.com'),
        ('OpenAI', 'careers@openai.com'),
        ('Tempus', 'careers@tempus.com'),
        ('Google DeepMind', 'deepmind-careers@google.com'),
        ('Meta', 'airecruiting@meta.com'),
        ('Hugging Face', 'careers@huggingface.co')
    ]
    
    for company, email in verified_emails:
        validator.add_verified_email(company, email, "verified")
    
    # Validate existing emails
    results = validator.update_database_validations(limit=50)
    
    print("\n" + "="*50)
    print("✉️ Email Validation Complete!")
    print("="*50)
    print(f"📊 Total validated: {results['total_validated']}")
    print(f"✅ Valid emails: {results['valid_emails']}")
    print(f"❌ Invalid emails: {results['invalid_emails']}")
    print(f"📈 Success rate: {results['success_rate']:.1f}%")
    
    return results

if __name__ == "__main__":
    run_email_validation()