#!/usr/bin/env python3
"""
Email Application Tracker - Track job applications sent via email
Integrates with Universal Tracker system
"""

import os
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
import re


class EmailApplicationTracker:
    """Track and manage job applications sent via email"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Email applications log
        self.email_log = self.data_dir / "email_applications_log.csv"
        self.email_json = self.data_dir / "email_applications.json"
        
        # Common email patterns for job applications
        self.email_patterns = {
            'recruiter_domains': [
                '@greenhouse.io', '@lever.co', '@workday.com',
                '@taleo.net', '@jobvite.com', '@smartrecruiters.com'
            ],
            'common_subjects': [
                'application', 'applying for', 'interest in',
                'resume for', 'candidate for', 're:'
            ],
            'hr_emails': [
                'careers@', 'jobs@', 'hr@', 'recruiting@',
                'talent@', 'hiring@', 'recruitment@'
            ]
        }
        
        self.initialize_tracking()
    
    def initialize_tracking(self):
        """Initialize email tracking CSV"""
        if not self.email_log.exists():
            headers = [
                'email_id',
                'date_sent',
                'time_sent',
                'to_email',
                'company_name',
                'position_title',
                'subject_line',
                'email_type',  # direct_application, recruiter_response, follow_up
                'attachments',
                'resume_version',
                'cover_letter_included',
                'portfolio_link',
                'response_received',
                'response_date',
                'interview_scheduled',
                'notes',
                'universal_tracker_id'
            ]
            
            with open(self.email_log, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def extract_company_from_email(self, email_address):
        """Extract company name from email address"""
        # Remove common prefixes
        email_lower = email_address.lower()
        for prefix in self.email_patterns['hr_emails']:
            email_lower = email_lower.replace(prefix, '')
        
        # Extract domain
        domain = email_lower.split('@')[-1]
        company = domain.split('.')[0]
        
        # Clean up common suffixes
        company = company.replace('-careers', '').replace('careers', '')
        company = company.replace('-jobs', '').replace('jobs', '')
        company = company.replace('hiring', '').replace('recruit', '')
        
        return company.title()
    
    def parse_email_subject(self, subject):
        """Extract position from email subject"""
        # Common patterns
        patterns = [
            r'(?:applying for|application for|interest in)\s+(.+?)(?:\s+position|\s+role)?',
            r'(.+?)\s+(?:position|role|opportunity)',
            r're:\s+(.+)',
            r'resume for\s+(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return subject
    
    def log_email_application(self, email_data):
        """Log an email application"""
        # Generate unique ID
        email_id = f"EMAIL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract company if not provided
        if not email_data.get('company_name'):
            email_data['company_name'] = self.extract_company_from_email(
                email_data.get('to_email', '')
            )
        
        # Extract position if not provided
        if not email_data.get('position_title'):
            email_data['position_title'] = self.parse_email_subject(
                email_data.get('subject_line', '')
            )
        
        # Prepare row data
        row = [
            email_id,
            email_data.get('date_sent', datetime.now().strftime('%Y-%m-%d')),
            email_data.get('time_sent', datetime.now().strftime('%H:%M:%S')),
            email_data.get('to_email', ''),
            email_data.get('company_name', ''),
            email_data.get('position_title', ''),
            email_data.get('subject_line', ''),
            email_data.get('email_type', 'direct_application'),
            email_data.get('attachments', 'resume.pdf'),
            email_data.get('resume_version', 'standard'),
            email_data.get('cover_letter_included', 'yes'),
            email_data.get('portfolio_link', 'https://matthewscott.ai'),
            email_data.get('response_received', 'no'),
            email_data.get('response_date', ''),
            email_data.get('interview_scheduled', 'no'),
            email_data.get('notes', ''),
            email_data.get('universal_tracker_id', '')
        ]
        
        # Write to CSV
        with open(self.email_log, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        # Also save to JSON for easy access
        self.update_json_log(email_id, email_data)
        
        return email_id
    
    def update_json_log(self, email_id, email_data):
        """Update JSON log for easy searching"""
        if self.email_json.exists():
            with open(self.email_json, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        
        data[email_id] = {
            **email_data,
            'email_id': email_id,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.email_json, 'w') as f:
            json.dump(data, f, indent=2)
    
    def search_email_applications(self, search_term=None, date_range=None):
        """Search email applications"""
        applications = []
        
        with open(self.email_log, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Filter by search term
                if search_term:
                    search_lower = search_term.lower()
                    if not any(search_lower in str(v).lower() for v in row.values()):
                        continue
                
                # Filter by date range
                if date_range:
                    app_date = datetime.strptime(row['date_sent'], '%Y-%m-%d')
                    if not (date_range['start'] <= app_date <= date_range['end']):
                        continue
                
                applications.append(row)
        
        return applications
    
    def generate_follow_up_list(self, days_ago=3):
        """Generate list of applications needing follow-up"""
        cutoff_date = datetime.now() - timedelta(days=days_ago)
        follow_ups = []
        
        applications = self.search_email_applications()
        
        for app in applications:
            # Skip if already received response
            if app['response_received'].lower() == 'yes':
                continue
            
            # Check if it's time for follow-up
            app_date = datetime.strptime(app['date_sent'], '%Y-%m-%d')
            if app_date <= cutoff_date:
                follow_ups.append({
                    'company': app['company_name'],
                    'position': app['position_title'],
                    'email': app['to_email'],
                    'days_since': (datetime.now() - app_date).days,
                    'original_date': app['date_sent']
                })
        
        return follow_ups
    
    def import_gmail_data(self, gmail_export_file):
        """Import data from Gmail export (CSV format)"""
        imported = 0
        
        with open(gmail_export_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map Gmail fields to our format
                email_data = {
                    'to_email': row.get('To', ''),
                    'subject_line': row.get('Subject', ''),
                    'date_sent': row.get('Date', '').split(' ')[0],
                    'time_sent': row.get('Date', '').split(' ')[1] if ' ' in row.get('Date', '') else '',
                    'email_type': 'direct_application'
                }
                
                # Only import if it looks like a job application
                if any(keyword in email_data['subject_line'].lower() 
                       for keyword in self.email_patterns['common_subjects']):
                    self.log_email_application(email_data)
                    imported += 1
        
        return imported
    
    def generate_report(self):
        """Generate summary report of email applications"""
        applications = self.search_email_applications()
        
        # Calculate statistics
        total = len(applications)
        responses = sum(1 for app in applications if app['response_received'].lower() == 'yes')
        interviews = sum(1 for app in applications if app['interview_scheduled'].lower() == 'yes')
        
        # Group by company
        by_company = {}
        for app in applications:
            company = app['company_name']
            if company not in by_company:
                by_company[company] = []
            by_company[company].append(app)
        
        # Generate report
        report = {
            'summary': {
                'total_applications': total,
                'responses_received': responses,
                'response_rate': f"{(responses/total*100):.1f}%" if total > 0 else "0%",
                'interviews_scheduled': interviews,
                'interview_rate': f"{(interviews/total*100):.1f}%" if total > 0 else "0%",
                'unique_companies': len(by_company)
            },
            'by_company': {
                company: {
                    'count': len(apps),
                    'positions': list(set(app['position_title'] for app in apps)),
                    'last_contact': max(app['date_sent'] for app in apps)
                }
                for company, apps in by_company.items()
            },
            'follow_ups_needed': self.generate_follow_up_list()
        }
        
        return report


def main():
    """Demo usage of email application tracker"""
    tracker = EmailApplicationTracker()
    
    print("📧 Email Application Tracker\n")
    
    # Example: Log a new email application
    example_application = {
        'to_email': 'careers@openai.com',
        'company_name': 'OpenAI',
        'position_title': 'AI Research Engineer',
        'subject_line': 'Application for AI Research Engineer - Matthew Scott',
        'attachments': 'resume_ai_optimized.pdf, portfolio_link.txt',
        'cover_letter_included': 'yes',
        'notes': 'Emphasized consciousness research experience'
    }
    
    # Log the application
    email_id = tracker.log_email_application(example_application)
    print(f"✅ Logged application: {email_id}")
    
    # Generate report
    report = tracker.generate_report()
    
    print("\n📊 Email Application Summary:")
    print(f"Total Applications: {report['summary']['total_applications']}")
    print(f"Response Rate: {report['summary']['response_rate']}")
    print(f"Interview Rate: {report['summary']['interview_rate']}")
    
    # Show follow-ups needed
    if report['follow_ups_needed']:
        print(f"\n⏰ Follow-ups Needed ({len(report['follow_ups_needed'])}):")
        for follow_up in report['follow_ups_needed'][:5]:
            print(f"  • {follow_up['company']} - {follow_up['position']} ({follow_up['days_since']} days ago)")
    
    print("\n💡 To import Gmail data:")
    print("1. Export your sent emails as CSV from Gmail")
    print("2. Run: tracker.import_gmail_data('gmail_export.csv')")
    
    print("\n🔍 To search applications:")
    print("results = tracker.search_email_applications('AI Research')")


if __name__ == "__main__":
    main()