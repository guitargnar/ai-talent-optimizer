#!/usr/bin/env python3
"""
Email Validation System
Prevents sending applications to non-existent email addresses
"""

import re
import socket
import smtplib
import dns.resolver
from typing import Tuple, Dict, Optional
import json
from datetime import datetime


class EmailValidator:
    """Validate email addresses before sending applications"""
    
    def __init__(self):
        # Known good email patterns for companies
        self.known_patterns = {
            'default_attempts': [
                'careers@{company}.com',
                'jobs@{company}.com',
                'recruiting@{company}.com',
                'talent@{company}.com',
                'hr@{company}.com',
                'hiring@{company}.com',
                'recruitment@{company}.com'
            ],
            
            # Company-specific known good emails
            'verified_emails': {
                'openai': 'Use web form at careers.openai.com',
                'anthropic': 'Use web form at anthropic.com/careers',
                'google': 'Use careers.google.com',
                'meta': 'Use metacareers.com',
                'apple': 'Use jobs.apple.com',
                'microsoft': 'Use careers.microsoft.com',
                'amazon': 'Use amazon.jobs',
                'netflix': 'Use jobs.netflix.com',
                'stripe': 'Use stripe.com/jobs',
                'databricks': 'Use databricks.com/company/careers',
                'snowflake': 'Use careers.snowflake.com',
                'pinecone': 'Use pinecone.io/careers',
                'cohere': 'Use cohere.ai/careers',
                'huggingface': 'Use huggingface.co/join-us'
            }
        }
        
        # Cache for validated emails
        self.validation_cache = {}
        self.load_cache()
    
    def load_cache(self):
        """Load previously validated emails"""
        try:
            with open('validated_emails_cache.json', 'r') as f:
                self.validation_cache = json.load(f)
        except:
            self.validation_cache = {}
    
    def save_cache(self):
        """Save validated emails cache"""
        with open('validated_emails_cache.json', 'w') as f:
            json.dump(self.validation_cache, f, indent=2)
    
    def validate_email_format(self, email: str) -> bool:
        """Check if email format is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def check_domain_exists(self, domain: str) -> bool:
        """Check if domain has MX records"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return len(mx_records) > 0
        except:
            return False
    
    def verify_email_address(self, email: str) -> Tuple[bool, str]:
        """
        Verify if email address is likely to exist
        Returns (is_valid, reason)
        """
        
        # Check cache first
        if email in self.validation_cache:
            cached = self.validation_cache[email]
            return cached['valid'], cached['reason']
        
        # Check format
        if not self.validate_email_format(email):
            result = (False, "Invalid email format")
            self.cache_result(email, result)
            return result
        
        domain = email.split('@')[1]
        
        # Check if domain exists
        if not self.check_domain_exists(domain):
            result = (False, f"Domain {domain} does not exist or has no mail server")
            self.cache_result(email, result)
            return result
        
        # Try SMTP verification (may not always work)
        try:
            # Connect to mail server
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_host = str(mx_records[0].exchange)
            
            server = smtplib.SMTP(timeout=10)
            server.set_debuglevel(0)
            server.connect(mx_host)
            server.helo('gmail.com')  # Identify ourselves
            
            # Try to verify
            code, message = server.verify(email)
            server.quit()
            
            if code == 250:
                result = (True, "Email verified via SMTP")
            else:
                result = (False, f"SMTP verification failed: {message}")
                
        except Exception as e:
            # SMTP verification often fails due to security, but domain exists
            result = (True, f"Domain exists (SMTP check skipped: {str(e)[:50]})")
        
        self.cache_result(email, result)
        return result
    
    def cache_result(self, email: str, result: Tuple[bool, str]):
        """Cache validation result"""
        self.validation_cache[email] = {
            'valid': result[0],
            'reason': result[1],
            'checked_at': datetime.now().isoformat()
        }
        self.save_cache()
    
    def find_correct_email(self, company: str, job_url: str = None) -> Dict:
        """
        Find the correct application email for a company
        Returns dict with email or alternative application method
        """
        
        company_lower = company.lower().replace(' ', '').replace(',', '').replace('.', '')
        
        # Check known companies first
        for known_company, instruction in self.known_patterns['verified_emails'].items():
            if known_company in company_lower:
                return {
                    'method': 'web_form',
                    'instruction': instruction,
                    'email': None
                }
        
        # Try common patterns
        valid_emails = []
        for pattern in self.known_patterns['default_attempts']:
            test_email = pattern.replace('{company}', company_lower)
            is_valid, reason = self.verify_email_address(test_email)
            
            if is_valid:
                valid_emails.append(test_email)
        
        if valid_emails:
            return {
                'method': 'email',
                'email': valid_emails[0],  # Use first valid email
                'alternatives': valid_emails[1:] if len(valid_emails) > 1 else []
            }
        
        # No valid email found
        return {
            'method': 'unknown',
            'instruction': f'Apply directly at {company} website or through job board',
            'email': None
        }
    
    def validate_before_send(self, email: str, company: str) -> Dict:
        """
        Final validation before sending application
        Returns dict with send_ok and instructions
        """
        
        # First check if email is valid
        is_valid, reason = self.verify_email_address(email)
        
        if is_valid:
            return {
                'send_ok': True,
                'email': email,
                'message': f'Email {email} validated successfully'
            }
        
        # Email invalid, find alternative
        alternative = self.find_correct_email(company)
        
        return {
            'send_ok': False,
            'email': None,
            'reason': reason,
            'alternative': alternative,
            'message': f'Email {email} is invalid. {alternative.get("instruction", "Find alternative method.")}'
        }
    
    def get_validation_report(self) -> str:
        """Generate report of all validated emails"""
        valid = [e for e, data in self.validation_cache.items() if data['valid']]
        invalid = [e for e, data in self.validation_cache.items() if not data['valid']]
        
        report = f"""
EMAIL VALIDATION REPORT
=======================
Total Checked: {len(self.validation_cache)}
Valid: {len(valid)}
Invalid: {len(invalid)}

INVALID EMAILS:
"""
        for email in invalid:
            report += f"  ❌ {email}: {self.validation_cache[email]['reason']}\n"
        
        report += "\nVALID EMAILS:\n"
        for email in valid[:10]:  # Show first 10
            report += f"  ✅ {email}\n"
        
        return report


def main():
    """Test the email validator"""
    print("📧 Email Validation System")
    print("="*60)
    
    validator = EmailValidator()
    
    # Test known problematic emails
    test_emails = [
        ('careers@openai.com', 'OpenAI'),
        ('careers@anthropic.com', 'Anthropic'),
        ('careers@pinecone.com', 'Pinecone'),
        ('careers@snowflake.com', 'Snowflake'),
        ('careers@google.com', 'Google'),
        ('jobs@meta.com', 'Meta'),
        ('careers@stripe.com', 'Stripe')
    ]
    
    print("\n🔍 Testing Known Problematic Emails:")
    print("-"*60)
    
    for email, company in test_emails:
        result = validator.validate_before_send(email, company)
        
        if result['send_ok']:
            print(f"✅ {email}: Valid")
        else:
            print(f"❌ {email}: {result['reason']}")
            if result.get('alternative'):
                print(f"   Alternative: {result['alternative'].get('instruction', 'Check company website')}")
    
    print("\n" + validator.get_validation_report())
    
    # Save cache
    validator.save_cache()
    print("\n💾 Validation cache saved to validated_emails_cache.json")


if __name__ == "__main__":
    main()