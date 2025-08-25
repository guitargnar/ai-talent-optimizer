#!/usr/bin/env python3
"""
Bounce Detector - Identifies and tracks bounced emails
Searches Gmail for delivery failures and updates database
"""

import imaplib
import email
from email.header import decode_header
import sqlite3
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv

class BounceDetector:
    """Detect and track email bounces to improve delivery"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.db_path = "UNIFIED_AI_JOBS.db"
        self.bounce_log_path = "data/bounce_log.json"
        self.invalid_emails_path = "data/invalid_emails.json"
        
        # Gmail configuration
        self.email_address = os.getenv('EMAIL_ADDRESS', 'matthewdscott7@gmail.com')
        self.app_password = os.getenv('EMAIL_APP_PASSWORD', '')
        
        # Bounce detection patterns
        self.bounce_patterns = [
            r'Mail Delivery Subsystem',
            r'Mail Delivery System',
            r'Undelivered Mail Returned',
            r'Delivery Status Notification',
            r'Failed to deliver',
            r'Undeliverable',
            r'Message not delivered',
            r'Delivery failed',
            r'could not be delivered',
            r'permanent failure',
            r'550.*rejected',
            r'mailbox.*not.*found',
            r'user.*unknown',
            r'no such user',
            r'recipient.*rejected',
            r'address.*not.*found'
        ]
        
        # Extract email from bounce patterns
        self.email_extraction_patterns = [
            r'<([^>]+@[^>]+)>',  # Extract from <email@domain.com>
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Standard email
            r'to\s+([^\s]+@[^\s]+)',  # "to email@domain.com"
            r'recipient\s+([^\s]+@[^\s]+)',  # "recipient email@domain.com"
        ]
        
        # Bounce reason categories
        self.bounce_reasons = {
            'invalid_address': ['no such user', 'user unknown', 'mailbox not found', 'address not found'],
            'domain_not_found': ['host not found', 'domain not found', 'no mx record'],
            'mailbox_full': ['mailbox full', 'quota exceeded', 'over quota'],
            'blocked': ['blocked', 'rejected', 'spam', 'blacklisted', 'refused'],
            'temporary': ['temporary failure', 'try again', 'temporarily unavailable']
        }
    
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
                content_type = part.get_content_type()
                if content_type in ["text/plain", "text/html"]:
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())
        
        return body
    
    def _is_bounce_email(self, subject: str, from_addr: str, body: str) -> bool:
        """Check if email is a bounce notification"""
        text = f"{subject} {from_addr} {body}".lower()
        
        for pattern in self.bounce_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_bounced_address(self, body: str) -> str:
        """Extract the email address that bounced"""
        for pattern in self.email_extraction_patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                email_addr = match.group(1)
                # Clean up the email
                email_addr = email_addr.strip().lower()
                # Verify it looks like an email
                if '@' in email_addr and '.' in email_addr:
                    return email_addr
        
        return None
    
    def _categorize_bounce_reason(self, body: str) -> str:
        """Categorize the bounce reason"""
        body_lower = body.lower()
        
        for category, keywords in self.bounce_reasons.items():
            for keyword in keywords:
                if keyword in body_lower:
                    return category
        
        return 'unknown'
    
    def scan_for_bounces(self, days_back: int = 14) -> List[Dict]:
        """Scan Gmail for bounce notifications"""
        mail = self.connect_to_gmail()
        if not mail:
            return []
        
        bounces = []
        
        try:
            # Search in both inbox and spam
            for folder in ['INBOX', '[Gmail]/Spam', '[Gmail]/All Mail']:
                try:
                    mail.select(folder)
                except:
                    continue  # Skip if folder doesn't exist
                
                # Search for potential bounces
                date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
                
                # Search for bounce indicators
                search_queries = [
                    f'(FROM "mailer-daemon" SINCE {date})',
                    f'(FROM "postmaster" SINCE {date})',
                    f'(SUBJECT "Undelivered" SINCE {date})',
                    f'(SUBJECT "Delivery Status" SINCE {date})',
                    f'(SUBJECT "Failed" SINCE {date})'
                ]
                
                for query in search_queries:
                    try:
                        _, messages = mail.search(None, query)
                        
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
                                    
                                    # Check if it's really a bounce
                                    if self._is_bounce_email(subject, from_addr, body):
                                        # Extract bounced email address
                                        bounced_email = self._extract_bounced_address(body)
                                        
                                        if bounced_email:
                                            # Categorize reason
                                            reason = self._categorize_bounce_reason(body)
                                            
                                            bounces.append({
                                                'bounced_email': bounced_email,
                                                'bounce_date': date_str,
                                                'reason_category': reason,
                                                'subject': subject,
                                                'folder': folder,
                                                'body_preview': body[:500] if body else ''
                                            })
                    except Exception as e:
                        print(f"Error searching with query {query}: {e}")
                        continue
            
            mail.logout()
            
        except Exception as e:
            print(f"❌ Error scanning for bounces: {e}")
        
        # Remove duplicates
        unique_bounces = []
        seen_emails = set()
        for bounce in bounces:
            if bounce['bounced_email'] not in seen_emails:
                unique_bounces.append(bounce)
                seen_emails.add(bounce['bounced_email'])
        
        return unique_bounces
    
    def update_database_with_bounces(self, bounces: List[Dict]):
        """Update database to mark bounced emails"""
        if not bounces:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First ensure columns exist
        try:
            cursor.execute("ALTER TABLE job_discoveries ADD COLUMN bounce_detected INTEGER DEFAULT 0")
        except:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE job_discoveries ADD COLUMN bounce_reason TEXT")
        except:
            pass  # Column already exists
        
        # Update bounced emails
        for bounce in bounces:
            email_addr = bounce['bounced_email']
            reason = bounce['reason_category']
            
            # Find applications sent to this email
            cursor.execute("""
                UPDATE job_discoveries 
                SET bounce_detected = 1,
                    bounce_reason = ?
                WHERE applied = 1
                AND (
                    LOWER(company) || '@' IN (SELECT LOWER(?) WHERE ? LIKE '%' || LOWER(company) || '%')
                    OR ? LIKE '%careers@%'
                    OR ? LIKE '%jobs@%'
                )
            """, (reason, email_addr, email_addr, email_addr, email_addr))
        
        conn.commit()
        conn.close()
    
    def generate_bounce_report(self) -> Dict:
        """Generate comprehensive bounce report"""
        # Scan for bounces
        bounces = self.scan_for_bounces()
        
        # Update database
        if bounces:
            self.update_database_with_bounces(bounces)
        
        # Categorize bounces
        categories = {}
        for bounce in bounces:
            category = bounce['reason_category']
            if category not in categories:
                categories[category] = []
            categories[category].append(bounce['bounced_email'])
        
        # Get statistics from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM job_discoveries WHERE applied = 1")
        total_sent = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM job_discoveries WHERE bounce_detected = 1")
        total_bounced = cursor.fetchone()[0]
        
        conn.close()
        
        # Calculate bounce rate
        bounce_rate = (total_bounced / total_sent * 100) if total_sent > 0 else 0
        
        report = {
            'scan_date': datetime.now().isoformat(),
            'total_sent': total_sent,
            'total_bounced': total_bounced,
            'bounce_rate': bounce_rate,
            'new_bounces_found': len(bounces),
            'bounces_by_category': categories,
            'bounced_emails': [b['bounced_email'] for b in bounces]
        }
        
        # Save report
        with open(self.bounce_log_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save invalid emails list
        with open(self.invalid_emails_path, 'w') as f:
            json.dump({'invalid_emails': list(set(b['bounced_email'] for b in bounces))}, f, indent=2)
        
        return report
    
    def display_bounce_dashboard(self):
        """Display bounce detection dashboard"""
        print("\n" + "="*70)
        print("📧 BOUNCE DETECTION DASHBOARD")
        print("="*70)
        
        print("\n🔍 Scanning for bounced emails...")
        
        # Generate report
        report = self.generate_bounce_report()
        
        print(f"\n📊 BOUNCE STATISTICS:")
        print(f"  Total Emails Sent: {report['total_sent']}")
        print(f"  Total Bounces Detected: {report['total_bounced']}")
        print(f"  Bounce Rate: {report['bounce_rate']:.1f}%")
        print(f"  New Bounces Found: {report['new_bounces_found']}")
        
        if report['bounce_rate'] > 5:
            print(f"\n⚠️  WARNING: Bounce rate exceeds 5% threshold!")
        
        if report['bounces_by_category']:
            print(f"\n❌ BOUNCE CATEGORIES:")
            for category, emails in report['bounces_by_category'].items():
                print(f"  {category.replace('_', ' ').title()}: {len(emails)} emails")
                for email_addr in emails[:3]:  # Show first 3
                    print(f"    • {email_addr}")
        
        if report['bounced_emails']:
            print(f"\n📝 ACTION REQUIRED:")
            print(f"  • Remove {len(report['bounced_emails'])} invalid emails from future sends")
            print(f"  • Verify email addresses before sending")
            print(f"  • Consider using company websites instead of direct email")
            
            # Save to file for reference
            print(f"\n💾 Invalid emails saved to: {self.invalid_emails_path}")
        else:
            print(f"\n✅ No bounces detected - excellent delivery!")
        
        print("\n" + "="*70)
        print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

def main():
    """Main execution"""
    detector = BounceDetector()
    
    # Check if Gmail credentials exist
    if not detector.app_password:
        print("⚠️  Gmail App Password not found in .env file")
        print("Location: /Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/.env")
        return
    
    # Run bounce detection
    detector.display_bounce_dashboard()
    
    print("\n💡 RECOMMENDATIONS:")
    print("  1. Run this daily to catch bounces quickly")
    print("  2. Remove bounced emails from your sending list")
    print("  3. Verify new emails before adding to campaigns")
    print("  4. Use company websites when email bounces")

if __name__ == "__main__":
    main()