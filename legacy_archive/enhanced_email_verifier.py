#!/usr/bin/env python3
"""
Enhanced Email Verifier - Comprehensive validation before sending
Prevents bounces by verifying emails are real and deliverable
"""

import re
import socket
import smtplib
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import requests

class EnhancedEmailVerifier:
    """Advanced email verification to prevent bounces"""
    
    def __init__(self):
        self.verified_emails_path = "data/verified_emails.json"
        self.blacklist_path = "data/email_blacklist.json"
        self.company_emails_path = "data/company_emails.json"
        
        # Load existing data
        self.verified_emails = self._load_json(self.verified_emails_path, {})
        self.blacklist = self._load_json(self.blacklist_path, [])
        self.company_emails = self._load_json(self.company_emails_path, {})
        
        # Common invalid patterns
        self.invalid_patterns = [
            r'^careers@.*\.com$',  # Generic careers@ often doesn't exist
            r'^jobs@.*\.com$',     # Generic jobs@ often doesn't exist
            r'^hr@.*\.com$',       # Generic hr@ often doesn't exist
            r'^info@.*\.com$',     # Generic info@ rarely for jobs
            r'^admin@.*\.com$',    # Generic admin@ not for jobs
            r'^noreply@',          # No-reply addresses
            r'^donotreply@',       # Do-not-reply addresses
            r'^mailto:',           # Malformed with mailto: prefix
        ]
        
        # Known good email patterns for specific companies
        self.known_good_patterns = {
            'google': ['@google.com', 'recruiting@google.com'],
            'meta': ['@meta.com', 'recruiting@fb.com', '@facebook.com'],
            'amazon': ['@amazon.jobs', '@amazon.com'],
            'microsoft': ['@microsoft.com'],
            'apple': ['@apple.com'],
            'netflix': ['@netflix.com'],
            'uber': ['@uber.com'],
            'airbnb': ['@airbnb.com'],
            'stripe': ['@stripe.com'],
            'openai': ['@openai.com'],
            'anthropic': ['@anthropic.com'],
        }
        
        # Valid email formats that are more likely to work
        self.preferred_patterns = [
            r'recruiting@',
            r'talent@',
            r'hiring@',
            r'recruitment@',
            r'people@',
            r'apply@',
            r'[a-z]+\.recruiting@',  # company.recruiting@
            r'[a-z]+-careers@',      # company-careers@
        ]
    
    def _load_json(self, path: str, default):
        """Load JSON file or return default"""
        if Path(path).exists():
            with open(path, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, path: str, data):
        """Save data to JSON file"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def verify_email_format(self, email: str) -> Tuple[bool, str]:
        """Check if email format is valid"""
        # Basic regex for email format
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        # Check against invalid patterns
        for invalid_pattern in self.invalid_patterns:
            if re.match(invalid_pattern, email.lower()):
                return False, f"Generic/invalid pattern: {invalid_pattern}"
        
        return True, "Format valid"
    
    def check_domain_exists(self, email: str) -> Tuple[bool, str]:
        """Check if domain has MX records"""
        try:
            import dns.resolver
            domain = email.split('@')[1]
            
            # Check MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            if mx_records:
                return True, f"Domain has {len(mx_records)} MX records"
            
            return False, "No MX records found"
            
        except ImportError:
            # DNS library not available, try basic socket check
            try:
                domain = email.split('@')[1]
                socket.gethostbyname(domain)
                return True, "Domain exists (basic check)"
            except:
                return False, "Domain lookup failed"
        except Exception as e:
            # Any DNS errors
            if 'NXDOMAIN' in str(e):
                return False, "Domain does not exist"
            elif 'NoAnswer' in str(e):
                return False, "No MX records for domain"
            else:
                return False, f"DNS lookup failed: {str(e)}"
    
    def smtp_verify(self, email: str) -> Tuple[bool, str]:
        """Try SMTP verification (limited effectiveness)"""
        try:
            import dns.resolver
            domain = email.split('@')[1]
            
            # Get MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_host = str(mx_records[0].exchange)
            
            # Connect to SMTP server
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_host)
            server.helo('gmail.com')  # Identify as Gmail
            
            # Try VRFY command (often disabled)
            code, message = server.verify(email)
            server.quit()
            
            if code == 250:
                return True, "SMTP verification successful"
            else:
                return False, f"SMTP verification failed: {message}"
                
        except ImportError:
            # DNS library not available
            return None, "SMTP verification requires dnspython library"
        except Exception as e:
            # SMTP verification often fails due to security
            return None, f"SMTP verification unavailable: {str(e)}"
    
    def check_against_blacklist(self, email: str) -> Tuple[bool, str]:
        """Check if email is blacklisted"""
        if email.lower() in [e.lower() for e in self.blacklist]:
            return False, "Email is blacklisted (known bounce)"
        return True, "Not blacklisted"
    
    def check_known_good_pattern(self, email: str, company: str = None) -> Tuple[bool, str]:
        """Check if email matches known good patterns"""
        email_lower = email.lower()
        
        # Check company-specific patterns
        if company:
            company_lower = company.lower()
            if company_lower in self.known_good_patterns:
                for pattern in self.known_good_patterns[company_lower]:
                    if pattern in email_lower:
                        return True, f"Matches known pattern for {company}"
        
        # Check preferred patterns
        for pattern in self.preferred_patterns:
            if re.search(pattern, email_lower):
                return True, f"Matches preferred pattern: {pattern}"
        
        return None, "No known pattern match"
    
    def comprehensive_verify(self, email: str, company: str = None) -> Dict:
        """Perform comprehensive email verification"""
        result = {
            'email': email,
            'is_valid': True,
            'confidence': 0,
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if already verified
        if email in self.verified_emails:
            cached = self.verified_emails[email]
            if cached.get('is_valid'):
                return cached
        
        # 1. Format validation (40% weight)
        format_valid, format_msg = self.verify_email_format(email)
        result['checks']['format'] = {'valid': format_valid, 'message': format_msg}
        if format_valid:
            result['confidence'] += 40
        else:
            result['is_valid'] = False
            self.blacklist.append(email)
            self._save_json(self.blacklist_path, self.blacklist)
            return result
        
        # 2. Blacklist check (immediate fail)
        blacklist_ok, blacklist_msg = self.check_against_blacklist(email)
        result['checks']['blacklist'] = {'valid': blacklist_ok, 'message': blacklist_msg}
        if not blacklist_ok:
            result['is_valid'] = False
            result['confidence'] = 0
            return result
        
        # 3. Domain existence (30% weight)
        domain_exists, domain_msg = self.check_domain_exists(email)
        result['checks']['domain'] = {'valid': domain_exists, 'message': domain_msg}
        if domain_exists:
            result['confidence'] += 30
        else:
            result['is_valid'] = False
            self.blacklist.append(email)
            self._save_json(self.blacklist_path, self.blacklist)
            return result
        
        # 4. Known pattern matching (20% weight)
        pattern_match, pattern_msg = self.check_known_good_pattern(email, company)
        result['checks']['pattern'] = {'valid': pattern_match, 'message': pattern_msg}
        if pattern_match:
            result['confidence'] += 20
        elif pattern_match is False:
            result['confidence'] -= 10
        
        # 5. SMTP verification (10% weight if successful)
        smtp_valid, smtp_msg = self.smtp_verify(email)
        result['checks']['smtp'] = {'valid': smtp_valid, 'message': smtp_msg}
        if smtp_valid:
            result['confidence'] += 10
        elif smtp_valid is False:
            result['confidence'] -= 20
        
        # Final determination
        if result['confidence'] < 50:
            result['is_valid'] = False
            result['recommendation'] = "DO NOT SEND - High bounce risk"
        elif result['confidence'] < 70:
            result['recommendation'] = "CAUTION - Moderate bounce risk"
        else:
            result['recommendation'] = "SAFE TO SEND - Low bounce risk"
        
        # Cache the result
        self.verified_emails[email] = result
        self._save_json(self.verified_emails_path, self.verified_emails)
        
        return result
    
    def add_verified_email(self, company: str, email: str, source: str = "manual"):
        """Manually add a verified email"""
        if company not in self.company_emails:
            self.company_emails[company] = []
        
        email_entry = {
            'email': email,
            'source': source,
            'added': datetime.now().isoformat(),
            'verified': True
        }
        
        self.company_emails[company].append(email_entry)
        self._save_json(self.company_emails_path, self.company_emails)
        
        # Also add to verified list
        self.verified_emails[email] = {
            'email': email,
            'is_valid': True,
            'confidence': 100,
            'source': source,
            'company': company
        }
        self._save_json(self.verified_emails_path, self.verified_emails)
    
    def get_company_email(self, company: str) -> Optional[str]:
        """Get verified email for a company"""
        if company in self.company_emails:
            emails = self.company_emails[company]
            # Return most recently verified email
            for email_entry in reversed(emails):
                if email_entry.get('verified'):
                    return email_entry['email']
        return None
    
    def verify_batch(self, emails: List[str]) -> Dict:
        """Verify a batch of emails"""
        results = {
            'total': len(emails),
            'valid': 0,
            'invalid': 0,
            'uncertain': 0,
            'details': []
        }
        
        for email in emails:
            verification = self.comprehensive_verify(email)
            results['details'].append(verification)
            
            if verification['is_valid']:
                if verification['confidence'] >= 70:
                    results['valid'] += 1
                else:
                    results['uncertain'] += 1
            else:
                results['invalid'] += 1
        
        return results
    
    def display_verification_report(self):
        """Display comprehensive verification report"""
        print("\n" + "="*70)
        print("📧 EMAIL VERIFICATION REPORT")
        print("="*70)
        
        print(f"\n📊 STATISTICS:")
        print(f"  Verified Emails: {len(self.verified_emails)}")
        print(f"  Blacklisted: {len(self.blacklist)}")
        print(f"  Company Emails: {len(self.company_emails)}")
        
        # Show high-confidence emails
        high_confidence = [e for e, v in self.verified_emails.items() 
                          if v.get('confidence', 0) >= 80]
        if high_confidence:
            print(f"\n✅ HIGH CONFIDENCE EMAILS ({len(high_confidence)}):")
            for email in high_confidence[:5]:
                print(f"  • {email}")
        
        # Show blacklisted emails
        if self.blacklist:
            print(f"\n❌ BLACKLISTED EMAILS ({len(self.blacklist)}):")
            for email in self.blacklist[:5]:
                print(f"  • {email}")
        
        # Show company emails
        if self.company_emails:
            print(f"\n🏢 COMPANY EMAILS:")
            for company, emails in list(self.company_emails.items())[:5]:
                if emails:
                    print(f"  {company}: {emails[0]['email']}")
        
        print("\n" + "="*70)


def main():
    """Main execution"""
    verifier = EnhancedEmailVerifier()
    
    print("🔍 Enhanced Email Verifier")
    print("\nOptions:")
    print("1. Verify single email")
    print("2. Verify batch from database")
    print("3. Add verified email manually")
    print("4. View verification report")
    print("5. Test common patterns")
    
    choice = input("\nSelect option (1-5): ")
    
    if choice == '1':
        email = input("Enter email to verify: ")
        company = input("Enter company name (optional): ")
        
        result = verifier.comprehensive_verify(email, company if company else None)
        
        print(f"\n📧 Verification Results for: {email}")
        print(f"  Valid: {'✅' if result['is_valid'] else '❌'}")
        print(f"  Confidence: {result['confidence']}%")
        print(f"  Recommendation: {result.get('recommendation', 'Unknown')}")
        
        print("\n  Checks:")
        for check, details in result['checks'].items():
            status = '✅' if details.get('valid') else '❌' if details.get('valid') is False else '⚠️'
            print(f"    {status} {check}: {details.get('message', 'N/A')}")
    
    elif choice == '2':
        # Load emails from database
        import sqlite3
        conn = sqlite3.connect("unified_platform.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT company 
            FROM jobs 
            WHERE applied = 1
            LIMIT 10
        """)
        
        companies = cursor.fetchall()
        emails = []
        
        for company in companies:
            # Try to construct email
            company = company[0].lower().replace(' ', '').replace("'", "")
            test_email = f"careers@{company_name}.com"
            emails.append(test_email)
        
        conn.close()
        
        print(f"\n🔍 Verifying {len(emails)} emails...")
        results = verifier.verify_batch(emails)
        
        print(f"\n📊 Batch Results:")
        print(f"  Valid: {results['valid']}")
        print(f"  Invalid: {results['invalid']}")
        print(f"  Uncertain: {results['uncertain']}")
        
        print("\n  Invalid emails:")
        for detail in results['details']:
            if not detail['is_valid']:
                print(f"    ❌ {detail['email']}")
    
    elif choice == '3':
        company = input("Company name: ")
        email = input("Verified email address: ")
        source = input("Source (e.g., website, linkedin): ")
        
        verifier.add_verified_email(company, email, source)
        print(f"✅ Added verified email for {company}")
    
    elif choice == '4':
        verifier.display_verification_report()
    
    elif choice == '5':
        test_emails = [
            "careers@google.com",
            "recruiting@meta.com",
            "jobs@randomcompany.com",
            "hr@startup.com",
            "john.doe@company.com",
            "apply@openai.com",
            "mailto:test@example.com",
            "noreply@company.com"
        ]
        
        print("\n🧪 Testing common patterns:")
        for email in test_emails:
            result = verifier.comprehensive_verify(email)
            status = '✅' if result['is_valid'] else '❌'
            print(f"  {status} {email}: {result['confidence']}% confidence")


if __name__ == "__main__":
    main()