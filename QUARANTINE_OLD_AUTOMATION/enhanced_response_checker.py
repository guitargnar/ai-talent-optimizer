#!/usr/bin/env python3
"""
⚠️ DEPRECATED - DO NOT USE - Has 100% false positive rate
Enhanced Response Checker - Comprehensive email response tracking with database integration
Combines the best of existing systems with new tracking capabilities

WARNING: This checker incorrectly identifies non-job emails as responses.
USE INSTEAD: accurate_response_checker.py for real response tracking
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
from typing import List, Dict, Tuple
from dotenv import load_dotenv

class EnhancedResponseChecker:
    """Advanced response tracking with pattern analysis"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.db_path = "UNIFIED_AI_JOBS.db"
        self.response_log_path = "data/response_tracking.json"
        self.metrics_path = "data/response_metrics.json"
        
        # Gmail configuration - check multiple possible env var names
        self.email_address = os.getenv('EMAIL_ADDRESS') or os.getenv('GMAIL_ADDRESS', 'matthewdscott7@gmail.com')
        self.app_password = os.getenv('EMAIL_APP_PASSWORD') or os.getenv('GMAIL_APP_PASSWORD', '')
        
        # Response patterns
        self.positive_patterns = [
            r'interview', r'schedule.*call', r'next.*step', r'meet.*team',
            r'availability', r'assessment', r'coding.*challenge', r'technical.*round'
        ]
        
        self.rejection_patterns = [
            r'not.*moving.*forward', r'other.*candidate', r'not.*fit',
            r'decided.*not', r'position.*filled', r'pursuing.*other'
        ]
        
        # Ensure database has proper columns
        self._ensure_database_schema()
        
    def _ensure_database_schema(self):
        """Add response tracking columns to database if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if columns exist and add if missing
        cursor.execute("PRAGMA table_info(job_discoveries)")
        columns = [col[1] for col in cursor.fetchall()]
        
        new_columns = [
            ("response_received", "INTEGER DEFAULT 0"),
            ("response_date", "TEXT"),
            ("response_type", "TEXT"),  # positive, negative, neutral
            ("interview_scheduled", "INTEGER DEFAULT 0"),
            ("rejection_reason", "TEXT"),
            ("follow_up_sent", "INTEGER DEFAULT 0"),
            ("follow_up_date", "TEXT"),
            ("resume_version", "TEXT"),
            ("response_time_days", "INTEGER")
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE job_discoveries ADD COLUMN {col_name} {col_type}")
                    print(f"✅ Added column: {col_name}")
                except sqlite3.OperationalError:
                    pass  # Column already exists
        
        conn.commit()
        conn.close()
    
    def connect_to_gmail(self):
        """Connect to Gmail using IMAP"""
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.email_address, self.app_password)
            return mail
        except Exception as e:
            print(f"❌ Failed to connect to Gmail: {e}")
            print("Make sure GMAIL_APP_PASSWORD is set in your .env file")
            return None
    
    def check_for_responses(self, days_back=7):
        """Check for job application responses in the last N days"""
        mail = self.connect_to_gmail()
        if not mail:
            return []
        
        responses = []
        
        try:
            mail.select('inbox')
            
            # Search for emails from the last N days
            date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            
            # Search for potential job responses
            search_criteria = f'(SINCE {date})'
            _, messages = mail.search(None, search_criteria)
            
            for msg_id in messages[0].split():
                _, msg_data = mail.fetch(msg_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Extract email details
                        subject = self._decode_header(msg['Subject'])
                        from_addr = self._decode_header(msg['From'])
                        date_str = msg['Date']
                        
                        # Check if this is a job-related response
                        if self._is_job_response(subject, from_addr):
                            # Get email body
                            body = self._get_email_body(msg)
                            
                            # Analyze response type
                            response_type = self._analyze_response_type(subject, body)
                            
                            # Extract company name
                            company = self._extract_company(from_addr, subject)
                            
                            responses.append({
                                'subject': subject,
                                'from': from_addr,
                                'date': date_str,
                                'company': company,
                                'type': response_type,
                                'body_preview': body[:500] if body else ''
                            })
            
            mail.logout()
            
        except Exception as e:
            print(f"❌ Error checking emails: {e}")
        
        return responses
    
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
    
    def _is_job_response(self, subject, from_addr):
        """Determine if email is likely a job application response"""
        job_keywords = [
            'application', 'position', 'role', 'opportunity', 'interview',
            'candidate', 'resume', 'cv', 'hiring', 'recruitment', 'job',
            're:', 'follow', 'next step', 'assessment', 'thank you for'
        ]
        
        text = f"{subject} {from_addr}".lower()
        return any(keyword in text for keyword in job_keywords)
    
    def _analyze_response_type(self, subject, body):
        """Analyze if response is positive, negative, or neutral"""
        text = f"{subject} {body}".lower()
        
        # Check for positive indicators
        positive_score = sum(1 for pattern in self.positive_patterns 
                            if re.search(pattern, text, re.IGNORECASE))
        
        # Check for negative indicators
        negative_score = sum(1 for pattern in self.rejection_patterns 
                           if re.search(pattern, text, re.IGNORECASE))
        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_company(self, from_addr, subject):
        """Extract company name from email"""
        # Try to extract from email domain
        if '@' in from_addr:
            domain = from_addr.split('@')[1].split('>')[0]
            company = domain.split('.')[0]
            
            # Clean up common patterns
            company = company.replace('mail', '').replace('careers', '')
            company = company.replace('recruiting', '').replace('jobs', '')
            
            return company.capitalize()
        
        return 'Unknown'
    
    def update_database_with_responses(self, responses):
        """Update database with response information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for response in responses:
            company = response['company']
            response_type = response['type']
            
            # First find the most recent application for this company
            cursor.execute("""
                SELECT id FROM job_discoveries 
                WHERE company LIKE ? 
                AND applied = 1
                AND response_received = 0
                ORDER BY COALESCE(application_date, applied_date) DESC
                LIMIT 1
            """, (f'%{company}%',))
            
            result = cursor.fetchone()
            if result:
                job_id = result[0]
                
                # Update that specific job
                cursor.execute("""
                    UPDATE job_discoveries 
                    SET response_received = 1,
                        response_date = ?,
                        response_type = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), response_type, job_id))
                
                # If positive response, mark interview_scheduled
                if response_type == 'positive':
                    cursor.execute("""
                        UPDATE job_discoveries 
                        SET interview_scheduled = 1
                        WHERE id = ?
                    """, (job_id,))
        
        conn.commit()
        conn.close()
    
    def calculate_response_metrics(self):
        """Calculate and display response rate metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get metrics
        cursor.execute("SELECT COUNT(*) FROM job_discoveries WHERE applied = 1")
        total_applied = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM job_discoveries WHERE response_received = 1")
        total_responses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM job_discoveries WHERE response_type = 'positive'")
        positive_responses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM job_discoveries WHERE interview_scheduled = 1")
        interviews = cursor.fetchone()[0]
        
        # Calculate response time
        cursor.execute("""
            SELECT AVG(JULIANDAY(response_date) - JULIANDAY(date_applied))
            FROM job_discoveries 
            WHERE response_received = 1 AND response_date IS NOT NULL
        """)
        avg_response_time = cursor.fetchone()[0] or 0
        
        # Get best performing resume versions
        cursor.execute("""
            SELECT resume_version, COUNT(*) as responses, 
                   SUM(CASE WHEN response_type = 'positive' THEN 1 ELSE 0 END) as positive
            FROM job_discoveries 
            WHERE response_received = 1 AND resume_version IS NOT NULL
            GROUP BY resume_version
        """)
        resume_performance = cursor.fetchall()
        
        conn.close()
        
        # Calculate rates
        response_rate = (total_responses / total_applied * 100) if total_applied > 0 else 0
        interview_rate = (interviews / total_applied * 100) if total_applied > 0 else 0
        positive_rate = (positive_responses / total_responses * 100) if total_responses > 0 else 0
        
        metrics = {
            'total_applied': total_applied,
            'total_responses': total_responses,
            'response_rate': response_rate,
            'positive_responses': positive_responses,
            'positive_rate': positive_rate,
            'interviews_scheduled': interviews,
            'interview_rate': interview_rate,
            'avg_response_time_days': round(avg_response_time, 1),
            'resume_performance': resume_performance,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save metrics
        with open(self.metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    
    def display_dashboard(self):
        """Display a comprehensive response tracking dashboard"""
        print("\n" + "="*60)
        print("📊 ENHANCED RESPONSE TRACKING DASHBOARD")
        print("="*60)
        
        # Check for new responses
        print("\n🔍 Checking for new responses...")
        responses = self.check_for_responses(days_back=7)
        
        if responses:
            print(f"\n✅ Found {len(responses)} potential responses:")
            for resp in responses[:5]:  # Show first 5
                emoji = "🎉" if resp['type'] == 'positive' else "❌" if resp['type'] == 'negative' else "📧"
                print(f"  {emoji} {resp['company']}: {resp['subject'][:50]}...")
            
            # Update database
            self.update_database_with_responses(responses)
            print(f"\n✅ Updated database with {len(responses)} responses")
        else:
            print("  No new responses found")
        
        # Calculate metrics
        metrics = self.calculate_response_metrics()
        
        print("\n📈 RESPONSE METRICS:")
        print(f"  Total Applications: {metrics['total_applied']}")
        print(f"  Total Responses: {metrics['total_responses']}")
        print(f"  Response Rate: {metrics['response_rate']:.1f}%")
        print(f"  Positive Responses: {metrics['positive_responses']}")
        print(f"  Interview Rate: {metrics['interview_rate']:.1f}%")
        print(f"  Avg Response Time: {metrics['avg_response_time_days']} days")
        
        if metrics['resume_performance']:
            print("\n📄 RESUME VERSION PERFORMANCE:")
            for version, responses, positive in metrics['resume_performance']:
                success_rate = (positive/responses * 100) if responses > 0 else 0
                print(f"  {version}: {responses} responses, {success_rate:.0f}% positive")
        
        print("\n" + "="*60)
        print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

def main():
    """Main execution function"""
    checker = EnhancedResponseChecker()
    
    # Check if we have Gmail credentials
    if not checker.app_password:
        print("⚠️  Gmail App Password not found in .env file")
        print("Please check your .env file has EMAIL_APP_PASSWORD set")
        print("Location: /Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/.env")
        return
    
    # Run the dashboard
    checker.display_dashboard()
    
    # Show actionable insights
    metrics = checker.calculate_response_metrics()
    
    if metrics['response_rate'] < 5:
        print("\n💡 INSIGHTS:")
        print("  - Response rate below 5% - consider A/B testing different resume versions")
        print("  - Try applying earlier in the day (9-11 AM)")
        print("  - Focus on smaller companies (< 1000 employees)")
    
    if metrics['avg_response_time_days'] > 5:
        print("\n⏰ FOLLOW-UP NEEDED:")
        print("  - Average response time is > 5 days")
        print("  - Consider sending follow-ups for applications > 7 days old")
        print("  - Run: python3 send_followup_email.py")

if __name__ == "__main__":
    main()