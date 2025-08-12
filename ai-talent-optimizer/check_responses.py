#!/usr/bin/env python3
"""
Response Checker - Monitors email replies to job applications
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import List, Dict, Tuple

# Import email functionality
from gmail_app_password_integration import GmailJobResponseChecker

class ResponseChecker:
    """Checks for responses to job applications"""
    
    def __init__(self):
        self.db_path = "UNIFIED_AI_JOBS.db"
        self.tracking_log_path = "data/bcc_tracking_log.json"
        self.response_log_path = "data/response_tracking.json"
        
        # Ensure response tracking column exists
        self._ensure_response_column()
        
    def _ensure_response_column(self):
        """Add response tracking column if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                ALTER TABLE job_discoveries 
                ADD COLUMN response_received INTEGER DEFAULT 0
            """)
            cursor.execute("""
                ALTER TABLE job_discoveries 
                ADD COLUMN response_date TEXT
            """)
            cursor.execute("""
                ALTER TABLE job_discoveries 
                ADD COLUMN response_type TEXT
            """)
            conn.commit()
        except sqlite3.OperationalError:
            # Columns already exist
            pass
        
        conn.close()
        
    def load_sent_emails(self) -> Dict:
        """Load BCC tracking log"""
        if not Path(self.tracking_log_path).exists():
            return {}
            
        with open(self.tracking_log_path, 'r') as f:
            data = json.load(f)
            
        return data.get('sent_emails', {})
        
    def check_for_responses(self, days_back: int = 7) -> List[Dict]:
        """Check Gmail for responses to sent applications"""
        responses = []
        
        print(f"🔍 Searching for responses from last {days_back} days...")
        
        try:
            # Use the existing Gmail integration
            gmail_checker = GmailJobResponseChecker()
            gmail_checker.connect()
            
            # Search for job responses
            gmail_responses = gmail_checker.search_job_responses(days_back=days_back)
            
            # Convert to our format
            for msg_type, messages in gmail_responses.items():
                for msg in messages:
                    response_info = {
                        'from': msg.get('From', ''),
                        'subject': msg.get('Subject', ''),
                        'date': msg.get('Date', ''),
                        'type': msg_type,  # 'positive', 'rejection', or 'neutral'
                        'company': self._extract_company(msg, {}),
                        'snippet': str(msg)[:200]
                    }
                    responses.append(response_info)
                    
            print(f"✅ Found {len(responses)} responses")
            
        except Exception as e:
            print(f"❌ Error checking responses: {e}")
            
        return responses
        
    def _analyze_response(self, message: Dict, sent_emails: Dict) -> Dict:
        """Analyze if email is a job application response"""
        
        # Extract sender info
        from_email = message.get('from', '').lower()
        subject = message.get('subject', '').lower()
        body = message.get('body', '').lower()
        
        # Common response indicators
        positive_keywords = [
            'interview', 'schedule', 'call', 'meet', 'zoom', 
            'next step', 'interested', 'opportunity', 'discuss'
        ]
        
        negative_keywords = [
            'unfortunately', 'not selected', 'other candidates',
            'not a fit', 'decided to move', 'position filled'
        ]
        
        auto_reply_keywords = [
            'auto-reply', 'automatic reply', 'out of office',
            'received your', 'thank you for applying'
        ]
        
        # Determine response type
        response_type = None
        
        if any(keyword in subject + body for keyword in positive_keywords):
            response_type = 'positive'
        elif any(keyword in subject + body for keyword in negative_keywords):
            response_type = 'rejection'
        elif any(keyword in subject + body for keyword in auto_reply_keywords):
            response_type = 'auto_reply'
        else:
            # Check if from a company we applied to
            for email_id, sent_info in sent_emails.items():
                company = sent_info.get('company', '').lower()
                if company in from_email or company in subject:
                    response_type = 'neutral'
                    break
                    
        if response_type:
            return {
                'from': message.get('from'),
                'subject': message.get('subject'),
                'date': message.get('date'),
                'type': response_type,
                'company': self._extract_company(message, sent_emails),
                'snippet': message.get('snippet', '')[:200]
            }
            
        return None
        
    def _extract_company(self, message: Dict, sent_emails: Dict) -> str:
        """Try to extract company name from response"""
        from_email = message.get('from', '').lower()
        
        # Check against sent emails
        for email_id, sent_info in sent_emails.items():
            company = sent_info.get('company', '')
            if company.lower() in from_email:
                return company
                
        # Extract domain from email
        match = re.search(r'@([^.]+)\.', from_email)
        if match:
            return match.group(1).title()
            
        return 'Unknown'
        
    def update_database(self, responses: List[Dict]):
        """Update database with response information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for response in responses:
            company = response['company']
            response_type = response['type']
            response_date = response['date']
            
            # Update the job record
            cursor.execute("""
                UPDATE job_discoveries 
                SET response_received = 1,
                    response_date = ?,
                    response_type = ?
                WHERE company = ? 
                AND applied = 1
            """, (response_date, response_type, company))
            
        conn.commit()
        rows_updated = conn.total_changes
        conn.close()
        
        print(f"💾 Updated {rows_updated} job records with responses")
        
    def save_response_log(self, responses: List[Dict]):
        """Save response tracking log"""
        log_data = {
            'last_check': datetime.now().isoformat(),
            'responses': responses
        }
        
        # Merge with existing log
        if Path(self.response_log_path).exists():
            with open(self.response_log_path, 'r') as f:
                existing = json.load(f)
                # Append new responses
                existing_responses = existing.get('responses', [])
                for new_response in responses:
                    # Check if not duplicate
                    if not any(r['from'] == new_response['from'] and 
                              r['date'] == new_response['date'] 
                              for r in existing_responses):
                        existing_responses.append(new_response)
                log_data['responses'] = existing_responses
                
        # Save updated log
        Path(self.response_log_path).parent.mkdir(exist_ok=True)
        with open(self.response_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
            
    def generate_report(self, responses: List[Dict]):
        """Generate response report"""
        if not responses:
            print("\n📭 No responses found")
            return
            
        print("\n📬 Response Summary:")
        print("=" * 60)
        
        # Count by type
        by_type = {}
        for r in responses:
            r_type = r['type']
            by_type[r_type] = by_type.get(r_type, 0) + 1
            
        print(f"Total responses: {len(responses)}")
        for r_type, count in by_type.items():
            emoji = {
                'positive': '🎉',
                'rejection': '❌',
                'auto_reply': '🤖',
                'neutral': '📧'
            }.get(r_type, '📧')
            print(f"  {emoji} {r_type.title()}: {count}")
            
        # Show positive responses
        positive = [r for r in responses if r['type'] == 'positive']
        if positive:
            print("\n🎯 Interview Opportunities:")
            for r in positive:
                print(f"  • {r['company']} - {r['subject']}")
                print(f"    {r['snippet']}")
                
        # Calculate response rate
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM job_discoveries WHERE applied=1")
        total_applied = cursor.fetchone()[0]
        conn.close()
        
        if total_applied > 0:
            response_rate = (len(responses) / total_applied) * 100
            print(f"\n📊 Response Rate: {response_rate:.1f}% ({len(responses)}/{total_applied})")
            
    def run(self):
        """Main response checking process"""
        print("📧 Checking for job application responses...")
        
        # Check for responses
        responses = self.check_for_responses(days_back=7)
        
        if responses:
            # Update database
            self.update_database(responses)
            
            # Save log
            self.save_response_log(responses)
            
        # Generate report
        self.generate_report(responses)
        
        print("\n✅ Response check complete!")


if __name__ == "__main__":
    checker = ResponseChecker()
    checker.run()