#!/usr/bin/env python3
"""
Accurate Response Checker - Eliminates false positives from job response tracking
Only counts REAL interview requests and legitimate job application responses
"""

import sqlite3
import json
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from pathlib import Path
import re
import os
from typing import List, Dict, Tuple, Set
from dotenv import load_dotenv

class AccurateResponseChecker:
    """Strict response tracking that eliminates false positives"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.db_path = "unified_platform.db"
        self.verified_responses_path = "data/verified_responses.json"
        self.false_positives_path = "data/false_positives.json"
        
        # Gmail configuration
        self.email_address = os.getenv('EMAIL_ADDRESS', 'matthewdscott7@gmail.com')
        self.app_password = os.getenv('EMAIL_APP_PASSWORD', '')
        
        # STRICT interview request patterns - must be explicit
        self.interview_patterns = [
            r'schedule.*(?:call|interview|meeting|chat).*(?:with|speak)',
            r'(?:would|we\'d).*like.*(?:interview|meet|speak|chat).*you',
            r'availability.*(?:interview|call|discussion|meeting)',
            r'next.*(?:interview|round|stage).*(?:process|recruitment)',
            r'hiring manager.*(?:meet|speak|interview)',
            r'(?:phone|video|technical|onsite).*interview',
            r'interview.*(?:scheduled|invite|invitation)',
            r'please.*(?:select|choose|provide).*(?:time|slot|availability)',
            r'calendly.*link.*interview',
            r'zoom.*meeting.*interview'
        ]
        
        # Definite false positive patterns
        self.false_positive_patterns = [
            r'api.*(?:access|request|proposal)',
            r'model.*(?:access|granted|approved)',
            r'payment.*(?:method|update|billing)',
            r'newsletter',
            r'product.*(?:announcement|update|launch)',
            r'blog.*post',
            r'webinar',
            r'demo.*(?:request|scheduled)',
            r'support.*ticket',
            r'password.*reset',
            r'verify.*email',
            r'unsubscribe',
            r'promotional',
            r'realtime.*api',  # OpenAI product announcements
            r'llama.*access',  # HuggingFace model access
            r'gpu.*scheduler', # Your old proposal to OpenAI
        ]
        
        # Auto-reply indicators
        self.auto_reply_patterns = [
            r'auto.*(?:reply|response|generated)',
            r'do.*not.*reply',
            r'noreply@',
            r'no-reply@',
            r'automatic.*(?:reply|response)',
            r'received.*your.*(?:application|submission)',
            r'thank.*you.*for.*applying',
            r'we.*have.*received',
            r'application.*(?:received|submitted|confirmed)',
            r'confirmation.*number',
            r'reference.*number'
        ]
        
        # Track companies we've actually applied to
        self.applied_companies = self._get_applied_companies()
        
    def _get_applied_companies(self) -> Set[str]:
        """Get list of companies we've actually applied to"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT LOWER(company_name) 
            FROM applications
        """)
        
        companies = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        return companies
    
    def connect_to_gmail(self):
        """Connect to Gmail using IMAP"""
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.email_address, self.app_password)
            return mail
        except Exception as e:
            print(f"❌ Failed to connect to Gmail: {e}")
            return None
    
    def _decode_header(self, header_value):
        """Decode email header"""
        if not header_value:
            return ""
        
        decoded_parts = decode_header(header_value)
        result = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                result += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                result += str(part)
        return result
    
    def _get_email_body(self, msg):
        """Extract email body text"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())
        
        return body
    
    def _is_from_applied_company(self, from_addr: str, subject: str) -> bool:
        """Check if email is from a company we actually applied to"""
        email_text = f"{from_addr} {subject}".lower()
        
        # Check if any applied company name appears in the email
        for company in self.applied_companies:
            if company in email_text:
                return True
        
        # Also check common recruiting domains
        recruiting_domains = ['greenhouse.io', 'lever.co', 'workday.com', 'taleo.net', 'breezy.hr']
        for domain in recruiting_domains:
            if domain in from_addr.lower():
                return True
        
        return False
    
    def _is_false_positive(self, subject: str, body: str, from_addr: str) -> bool:
        """Strictly identify false positives"""
        text = f"{subject} {body} {from_addr}".lower()
        
        # Check false positive patterns
        for pattern in self.false_positive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check if it's an auto-reply
        for pattern in self.auto_reply_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check specific known false positives
        if "proposal" in subject.lower() and "scheduler" in subject.lower():
            return True  # Your OpenAI proposal
        
        if "llama" in text and "access" in text:
            return True  # HuggingFace model access
        
        if "payment method" in text or "billing" in text:
            return True  # Billing notifications
        
        return False
    
    def _is_real_interview_request(self, subject: str, body: str) -> bool:
        """Strictly verify if this is a REAL interview request"""
        text = f"{subject} {body}".lower()
        
        # Must match at least one strict interview pattern
        for pattern in self.interview_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Double-check it's not a false positive
                if not self._is_false_positive(subject, body, ""):
                    return True
        
        return False
    
    def check_for_real_responses(self, days_back=7):
        """Check for REAL job application responses only"""
        mail = self.connect_to_gmail()
        if not mail:
            return []
        
        verified_responses = []
        false_positives = []
        
        try:
            mail.select('inbox')
            
            # Search for emails from the last N days
            date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            search_criteria = f'(SINCE {date})'
            _, messages = mail.search(None, search_criteria)
            
            for msg_id in messages[0].split():
                _, msg_data = mail.fetch(msg_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Extract details
                        subject = self._decode_header(msg['Subject'])
                        from_addr = self._decode_header(msg['From'])
                        date_str = msg['Date']
                        body = self._get_email_body(msg)
                        
                        # Skip if definitely a false positive
                        if self._is_false_positive(subject, body, from_addr):
                            false_positives.append({
                                'subject': subject,
                                'from': from_addr,
                                'reason': 'Known false positive pattern'
                            })
                            continue
                        
                        # Only process if from a company we applied to
                        if not self._is_from_applied_company(from_addr, subject):
                            continue
                        
                        # Classify the response
                        response_type = 'unknown'
                        confidence = 0
                        
                        if self._is_real_interview_request(subject, body):
                            response_type = 'interview_request'
                            confidence = 95
                        elif any(word in body.lower() for word in ['rejected', 'not moving forward', 'other candidates']):
                            response_type = 'rejection'
                            confidence = 90
                        elif any(word in body.lower() for word in ['received your application', 'thank you for applying']):
                            response_type = 'auto_reply'
                            confidence = 85
                        
                        # Only add if we're confident it's job-related
                        if confidence > 80:
                            verified_responses.append({
                                'subject': subject,
                                'from': from_addr,
                                'date': date_str,
                                'type': response_type,
                                'confidence': confidence,
                                'body_preview': body[:200] if body else ''
                            })
            
            mail.logout()
            
        except Exception as e:
            print(f"❌ Error checking emails: {e}")
        
        # Save results
        with open(self.verified_responses_path, 'w') as f:
            json.dump(verified_responses, f, indent=2)
        
        with open(self.false_positives_path, 'w') as f:
            json.dump(false_positives, f, indent=2)
        
        return verified_responses
    
    def verify_bcc_functionality(self):
        """Verify if BCC tracking is actually working"""
        print("\n🔍 VERIFYING BCC EMAIL FUNCTIONALITY:")
        
        # Check if BCC aliases work
        bcc_test_addresses = [
            'matthewdscott7+jobapps@gmail.com',
            'matthewdscott7+applications@gmail.com',
            'matthewdscott7+followups@gmail.com'
        ]
        
        print("\n📧 BCC Addresses Being Used:")
        for addr in bcc_test_addresses:
            print(f"  • {addr}")
        
        print("\n⚠️  IMPORTANT: Gmail '+' aliases should automatically route to your main inbox")
        print("  These addresses don't need separate setup, they're automatic aliases")
        
        # Check if we can find BCC'd emails
        mail = self.connect_to_gmail()
        if mail:
            try:
                mail.select('inbox')
                
                # Search for emails TO the BCC addresses
                bcc_found = False
                for bcc_addr in bcc_test_addresses:
                    search_query = f'(TO "{bcc_addr}")'
                    _, messages = mail.search(None, search_query)
                    
                    if messages[0]:
                        count = len(messages[0].split())
                        if count > 0:
                            print(f"\n✅ Found {count} emails BCC'd to {bcc_addr}")
                            bcc_found = True
                
                if not bcc_found:
                    print("\n⚠️  No BCC'd emails found - the BCC system may not be working")
                    print("  Or applications may not have been sent with BCC yet")
                
                mail.logout()
                
            except Exception as e:
                print(f"\n❌ Error checking BCC: {e}")
    
    def display_accurate_dashboard(self):
        """Display only verified, accurate response metrics"""
        print("\n" + "="*70)
        print("🎯 ACCURATE RESPONSE TRACKING DASHBOARD")
        print("="*70)
        
        # Check for real responses
        print("\n🔍 Checking for VERIFIED job application responses...")
        responses = self.check_for_real_responses(days_back=14)
        
        # Categorize responses
        interviews = [r for r in responses if r['type'] == 'interview_request']
        rejections = [r for r in responses if r['type'] == 'rejection']
        auto_replies = [r for r in responses if r['type'] == 'auto_reply']
        
        print(f"\n✅ VERIFIED RESPONSES (Last 14 Days):")
        print(f"  • Real Interview Requests: {len(interviews)}")
        print(f"  • Rejections: {len(rejections)}")
        print(f"  • Auto-replies: {len(auto_replies)}")
        
        if interviews:
            print(f"\n🎉 REAL INTERVIEW REQUESTS:")
            for interview in interviews:
                print(f"  • {interview['from'][:50]}")
                print(f"    Subject: {interview['subject'][:60]}...")
                print(f"    Confidence: {interview['confidence']}%")
        else:
            print(f"\n📝 No verified interview requests found")
            print("  This is based on STRICT criteria - only explicit interview invitations count")
        
        # Load false positives
        if Path(self.false_positives_path).exists():
            with open(self.false_positives_path, 'r') as f:
                false_positives = json.load(f)
                
            if false_positives:
                print(f"\n❌ FALSE POSITIVES FILTERED OUT: {len(false_positives)}")
                for fp in false_positives[:3]:
                    print(f"  • {fp['subject'][:60]}... ({fp['reason']})")
        
        # Calculate accurate metrics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied = 1")
        total_applied = cursor.fetchone()[0]
        
        conn.close()
        
        # Calculate REAL rates
        real_response_rate = ((len(interviews) + len(rejections)) / total_applied * 100) if total_applied > 0 else 0
        interview_rate = (len(interviews) / total_applied * 100) if total_applied > 0 else 0
        
        print(f"\n📊 ACCURATE METRICS:")
        print(f"  Total Applications: {total_applied}")
        print(f"  Real Response Rate: {real_response_rate:.1f}%")
        print(f"  Interview Request Rate: {interview_rate:.1f}%")
        
        # Verify BCC
        self.verify_bcc_functionality()
        
        print("\n" + "="*70)
        print(f"Accurate report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

def main():
    """Main execution"""
    checker = AccurateResponseChecker()
    
    # Run accurate dashboard
    checker.display_accurate_dashboard()
    
    print("\n💡 KEY DIFFERENCES FROM OLD SYSTEM:")
    print("  • Only counts emails from companies you actually applied to")
    print("  • Filters out API responses, model access, billing emails")
    print("  • Requires explicit interview language (not just 'next steps')")
    print("  • Identifies and reports false positives")
    print("  • Verifies BCC email functionality")

if __name__ == "__main__":
    main()