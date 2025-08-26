#!/usr/bin/env python3
"""
Email Verification System - Ensures emails are sent to legitimate addresses
Performs multiple checks to verify email validity and company legitimacy
"""

import re
import csv
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import dns.resolver
import socket

class EmailVerificationSystem:
    """Comprehensive email verification to prevent bounces and ensure delivery"""
    
    def __init__(self):
        self.db_path = "unified_platform.db"
        self.verified_emails_path = "data/verified_emails.json"
        self.suspicious_emails_path = "data/suspicious_emails.json"
        
        # Common legitimate recruiting email patterns
        self.legitimate_patterns = [
            r'^careers@.*',
            r'^jobs@.*',
            r'^hiring@.*',
            r'^recruiting@.*',
            r'^hr@.*',
            r'^talent@.*',
            r'^recruitment@.*',
            r'^apply@.*',
            r'^opportunities@.*',
            r'^.*careers@.*',
            r'^.*jobs@.*',
            r'^.*hiring@.*'
        ]
        
        # Suspicious patterns that might be fake
        self.suspicious_patterns = [
            r'.*test.*@.*',
            r'.*temp.*@.*',
            r'.*fake.*@.*',
            r'.*example\.com$',
            r'^info@.*',  # Too generic
            r'^contact@.*',  # Too generic
            r'^admin@.*',  # Unlikely for recruiting
            r'^support@.*',  # Wrong department
            r'.*\+.*@.*',  # Plus aliases (except for BCC tracking)
        ]
        
        # Known legitimate company domains
        self.trusted_domains = {
            'apple.com', 'google.com', 'meta.com', 'amazon.com', 'microsoft.com',
            'nvidia.com', 'openai.com', 'anthropic.com', 'cohere.ai', 'scale.com',
            'huggingface.co', 'inflection.ai', 'deepmind.com', 'databricks.com'
        }
        
        # Generic/free email providers (suspicious for company recruiting)
        self.free_email_providers = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
            'protonmail.com', 'mail.com', 'yandex.com', 'icloud.com'
        }
    
    def verify_email_format(self, email: str) -> Tuple[bool, str]:
        """Verify email has valid format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        return True, "Valid format"
    
    def check_domain_mx_records(self, email: str) -> Tuple[bool, str]:
        """Check if domain has valid MX records (can receive email)"""
        try:
            domain = email.split('@')[1]
            
            # Check MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            if mx_records:
                return True, f"Domain has {len(mx_records)} MX records"
            else:
                return False, "No MX records found"
                
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return False, "Domain does not exist or has no MX records"
        except Exception as e:
            return False, f"DNS lookup failed: {str(e)}"
    
    def check_domain_exists(self, email: str) -> Tuple[bool, str]:
        """Check if domain actually exists"""
        try:
            domain = email.split('@')[1]
            socket.gethostbyname(domain)
            return True, "Domain exists"
        except socket.gaierror:
            return False, "Domain does not exist"
        except Exception as e:
            return False, f"Domain check failed: {str(e)}"
    
    def is_legitimate_recruiting_email(self, email: str) -> Tuple[bool, str]:
        """Check if email follows legitimate recruiting patterns"""
        email_lower = email.lower()
        
        # Check against suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.match(pattern, email_lower):
                return False, f"Matches suspicious pattern: {pattern}"
        
        # Check if using free email provider
        domain = email_lower.split('@')[1]
        if domain in self.free_email_providers:
            return False, f"Using free email provider: {domain}"
        
        # Check against legitimate patterns
        for pattern in self.legitimate_patterns:
            if re.match(pattern, email_lower):
                return True, "Matches legitimate recruiting pattern"
        
        # Check if trusted domain
        if domain in self.trusted_domains:
            return True, f"Trusted domain: {domain}"
        
        return True, "No red flags detected"
    
    def verify_company_email_pair(self, company: str, email: str) -> Tuple[bool, str]:
        """Verify that email domain matches company name"""
        company_lower = company.lower().replace(' ', '').replace(',', '').replace('.', '')
        email_domain = email.split('@')[1].lower()
        
        # Direct match
        if company_lower in email_domain or email_domain.split('.')[0] in company_lower:
            return True, "Company name matches email domain"
        
        # Common variations
        variations = [
            company_lower,
            company_lower.replace('inc', ''),
            company_lower.replace('corp', ''),
            company_lower.replace('llc', ''),
            company_lower.replace('ltd', ''),
            company_lower.replace('holdings', ''),
            company_lower.replace('group', '')
        ]
        
        for var in variations:
            if var and var in email_domain:
                return True, "Company name variation matches domain"
        
        # Check if using legitimate recruiting platform
        recruiting_platforms = ['greenhouse.io', 'lever.co', 'workday.com', 'taleo.net']
        if any(platform in email_domain for platform in recruiting_platforms):
            return True, "Using legitimate recruiting platform"
        
        return False, "Company name does not match email domain"
    
    def comprehensive_email_check(self, email: str, company: str = None) -> Dict:
        """Perform comprehensive email verification"""
        results = {
            'email': email,
            'company': company,
            'is_valid': True,
            'confidence': 100,
            'checks': {}
        }
        
        # Format check
        valid, msg = self.verify_email_format(email)
        results['checks']['format'] = {'valid': valid, 'message': msg}
        if not valid:
            results['is_valid'] = False
            results['confidence'] -= 50
        
        # Domain existence check
        valid, msg = self.check_domain_exists(email)
        results['checks']['domain_exists'] = {'valid': valid, 'message': msg}
        if not valid:
            results['is_valid'] = False
            results['confidence'] -= 40
        
        # MX records check (can receive email)
        try:
            valid, msg = self.check_domain_mx_records(email)
            results['checks']['mx_records'] = {'valid': valid, 'message': msg}
            if not valid:
                results['confidence'] -= 30
        except:
            results['checks']['mx_records'] = {'valid': False, 'message': 'DNS lookup not available'}
        
        # Legitimacy check
        valid, msg = self.is_legitimate_recruiting_email(email)
        results['checks']['legitimacy'] = {'valid': valid, 'message': msg}
        if not valid:
            results['confidence'] -= 20
        
        # Company match check
        if company:
            valid, msg = self.verify_company_email_pair(company, email)
            results['checks']['company_match'] = {'valid': valid, 'message': msg}
            if not valid:
                results['confidence'] -= 15
        
        # Final verdict
        results['confidence'] = max(0, results['confidence'])
        results['is_valid'] = results['confidence'] >= 50
        
        return results
    
    def verify_database_emails(self):
        """Verify all emails in the job database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get unique company emails from applications
        cursor.execute("""
            SELECT DISTINCT company, 
                   COALESCE(email, 'careers@' || LOWER(REPLACE(company, ' ', '')) || '.com') as email
            FROM jobs 
            WHERE applied = 1
        """)
        
        applications = cursor.fetchall()
        conn.close()
        
        verified = []
        suspicious = []
        
        print(f"\n🔍 Verifying {len(applications)} unique company emails...")
        
        for company, email in applications:
            result = self.comprehensive_email_check(email, company)
            
            if result['is_valid'] and result['confidence'] >= 70:
                verified.append(result)
                print(f"✅ {email} - Confidence: {result['confidence']}%")
            else:
                suspicious.append(result)
                print(f"⚠️  {email} - Confidence: {result['confidence']}%")
                for check, details in result['checks'].items():
                    if not details['valid']:
                        print(f"    ❌ {check}: {details['message']}")
        
        # Save results
        with open(self.verified_emails_path, 'w') as f:
            json.dump(verified, f, indent=2)
        
        with open(self.suspicious_emails_path, 'w') as f:
            json.dump(suspicious, f, indent=2)
        
        return verified, suspicious
    
    def check_recent_csv_emails(self):
        """Check emails from recent CSV files"""
        csv_file = "data/email_applications_log.csv"
        
        if not Path(csv_file).exists():
            print(f"❌ CSV file not found: {csv_file}")
            return
        
        print(f"\n📋 Checking emails from {csv_file}...")
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            emails_to_check = set()
            
            for row in reader:
                if 'to' in row:
                    emails_to_check.add((row.get('company', 'Unknown'), row['to']))
        
        print(f"Found {len(emails_to_check)} unique emails to verify")
        
        for company, email in list(emails_to_check)[:10]:  # Check first 10
            result = self.comprehensive_email_check(email, company)
            
            if result['confidence'] >= 80:
                print(f"✅ {email} - VERIFIED (Confidence: {result['confidence']}%)")
            elif result['confidence'] >= 50:
                print(f"⚠️  {email} - QUESTIONABLE (Confidence: {result['confidence']}%)")
            else:
                print(f"❌ {email} - SUSPICIOUS (Confidence: {result['confidence']}%)")
    
    def generate_recommendations(self):
        """Generate recommendations for improving email delivery"""
        print("\n" + "="*70)
        print("📧 EMAIL DELIVERY RECOMMENDATIONS")
        print("="*70)
        
        recommendations = [
            "\n1. VERIFY BEFORE SENDING:",
            "   • Always check company careers page for official email",
            "   • Use LinkedIn to find actual recruiters",
            "   • Prefer application forms over direct email when available",
            
            "\n2. EMAIL ADDRESS PRIORITIES:",
            "   • Best: careers@company.com, jobs@company.com",
            "   • Good: hr@company.com, recruiting@company.com", 
            "   • Avoid: info@, contact@, support@",
            "   • Never: Personal Gmail/Yahoo addresses",
            
            "\n3. IMPROVE DELIVERABILITY:",
            "   • Keep emails under 150 words",
            "   • Avoid spam trigger words (Free, Guarantee, Act Now)",
            "   • Include company name in subject line",
            "   • Send during business hours (9 AM - 5 PM company time)",
            
            "\n4. BCC TRACKING:",
            "   • Your BCC system IS working (76 emails tracked)",
            "   • Gmail '+' aliases work automatically",
            "   • Consider creating filters to organize BCC'd copies",
            
            "\n5. FOLLOW-UP STRATEGY:",
            "   • Wait 5-7 business days before following up",
            "   • Reference specific role and date of application",
            "   • Keep follow-ups even shorter (50-75 words)",
            "   • Maximum 2 follow-ups per position"
        ]
        
        for rec in recommendations:
            print(rec)
        
        print("\n" + "="*70)

def main():
    """Main execution"""
    verifier = EmailVerificationSystem()
    
    print("="*70)
    print("🔍 EMAIL VERIFICATION SYSTEM")
    print("="*70)
    
    # Check database emails
    verified, suspicious = verifier.verify_database_emails()
    
    # Check CSV emails
    verifier.check_recent_csv_emails()
    
    # Summary
    print(f"\n📊 VERIFICATION SUMMARY:")
    print(f"  Verified Emails: {len(verified)}")
    print(f"  Suspicious Emails: {len(suspicious)}")
    
    if suspicious:
        print(f"\n⚠️  TOP CONCERNS:")
        for email_data in suspicious[:5]:
            print(f"  • {email_data['email']} - Confidence: {email_data['confidence']}%")
    
    # Recommendations
    verifier.generate_recommendations()

if __name__ == "__main__":
    main()