#!/usr/bin/env python3
"""
Email Tracking Integration - Connect email applications with universal tracker
Run this to sync your email applications with the main tracking system
"""

import os
import csv
import json
from datetime import datetime
from pathlib import Path

# Import our trackers
from email_application_tracker import EmailApplicationTracker
from gmail_application_finder import GmailApplicationFinder


def integrate_with_universal_tracker():
    """
    Integration guide for connecting email applications with your universal tracker
    """
    
    print("📧 Email Application Integration Guide\n")
    print("=" * 60)
    
    # Initialize components
    email_tracker = EmailApplicationTracker()
    gmail_finder = GmailApplicationFinder()
    
    print("🔍 Step 1: Find Your Email Applications\n")
    print("Run these searches in Gmail (copy/paste each one):\n")
    
    # Get search queries
    queries = gmail_finder.generate_gmail_search_queries(30)  # Last 30 days
    for i, query in enumerate(queries[:5], 1):
        print(f"{i}. {query}")
    
    print("\n📝 Step 2: Log Each Application Found\n")
    print("For each email found, create an entry like this:\n")
    
    # Example entry
    example = {
        "date_sent": "2025-08-01",
        "to_email": "careers@anthropic.com",
        "company_name": "Anthropic",
        "position_title": "AI Safety Research Engineer",
        "subject_line": "Application for AI Safety Research Engineer - Matthew Scott",
        "attachments": "resume_ai_consciousness.pdf, cover_letter.pdf",
        "notes": "Emphasized consciousness research alignment with AI safety"
    }
    
    print(json.dumps(example, indent=2))
    
    print("\n📊 Step 3: Generate Universal Tracker Update\n")
    
    # Create sample CSV update format
    universal_tracker_format = """
# Add these columns to your universal tracker CSV:
- email_sent_date
- email_recipient
- email_subject
- direct_application (yes/no)
- gmail_thread_id (if available)
    """
    
    print(universal_tracker_format)
    
    print("\n🔗 Step 4: Link with Career Automation System\n")
    
    integration_code = """
# In your career automation system, add this to track email applications:

def log_email_application(company, position, email, date_sent):
    # Log to email tracker
    from ai_talent_optimizer.email_application_tracker import EmailApplicationTracker
    tracker = EmailApplicationTracker()
    
    email_data = {
        'to_email': email,
        'company_name': company,
        'position_title': position,
        'date_sent': date_sent,
        'email_type': 'direct_application',
        'resume_version': 'ai_optimized'
    }
    
    email_id = tracker.log_email_application(email_data)
    
    # Also update universal tracker
    # ... your existing universal tracker code ...
    
    return email_id
    """
    
    print(integration_code)
    
    print("\n📈 Step 5: Track Response Rates\n")
    
    # Generate response tracking template
    response_template = {
        "email_applications": {
            "total_sent": 0,
            "responses_received": 0,
            "interviews_scheduled": 0,
            "response_rate": "0%",
            "average_response_time": "0 days"
        },
        "by_company_type": {
            "big_tech": {"sent": 0, "responses": 0},
            "ai_startups": {"sent": 0, "responses": 0},
            "enterprise": {"sent": 0, "responses": 0},
            "healthcare_ai": {"sent": 0, "responses": 0}
        }
    }
    
    # Save tracking template
    with open('email_response_tracking.json', 'w') as f:
        json.dump(response_template, f, indent=2)
    
    print("Created: email_response_tracking.json")
    
    print("\n⚡ Quick Commands:\n")
    
    commands = [
        "# Log a new email application:",
        "python -c \"from email_application_tracker import EmailApplicationTracker; " +
        "t = EmailApplicationTracker(); " +
        "t.log_email_application({'to_email': 'careers@company.com', 'company_name': 'Company', 'position_title': 'Role'})\"",
        "",
        "# Check applications needing follow-up:",
        "python -c \"from email_application_tracker import EmailApplicationTracker; " +
        "t = EmailApplicationTracker(); " +
        "print([f'{f[\"company\"]} ({f[\"days_since\"]} days)' for f in t.generate_follow_up_list()])\"",
        "",
        "# Generate report:",
        "python -c \"from email_application_tracker import EmailApplicationTracker; " +
        "t = EmailApplicationTracker(); " +
        "r = t.generate_report(); " +
        "print(f'Total: {r[\"summary\"][\"total_applications\"]}, Response Rate: {r[\"summary\"][\"response_rate\"]}')\"",
    ]
    
    for cmd in commands:
        print(cmd)
    
    print("\n✅ Integration Complete!\n")
    print("Your email applications can now be tracked alongside your automated applications.")
    print("This gives you a complete view of ALL your job search activities.")


def sync_with_career_automation():
    """
    Create sync file for career automation system
    """
    
    # Create sync configuration
    sync_config = {
        "email_tracker_path": str(Path(__file__).parent),
        "universal_tracker_path": "../SURVIVE/career-automation/real-tracker/career-automation/interview-prep/data",
        "sync_fields": [
            "company_name",
            "position_title", 
            "date_applied",
            "email_sent",
            "follow_up_status"
        ],
        "sync_frequency": "daily",
        "last_sync": datetime.now().isoformat()
    }
    
    with open('tracker_sync_config.json', 'w') as f:
        json.dump(sync_config, f, indent=2)
    
    print("📁 Created: tracker_sync_config.json")
    print("This file helps sync email applications with your main tracker.")


def create_daily_workflow():
    """
    Create a daily workflow for managing all applications
    """
    
    workflow = """
# 📅 Daily Job Application Workflow

## Morning (9:00 AM)
1. Run Gmail searches for yesterday's email applications
2. Log any direct email applications in email_application_tracker
3. Run career automation for 30 new applications
4. Check AI Talent Optimizer for profile view increases

## Afternoon (2:00 PM)  
1. Send follow-ups for applications 3+ days old
2. Update response tracking for any replies received
3. Run career automation for 25 more applications
4. Post LinkedIn content (if scheduled)

## Evening (6:00 PM)
1. Review daily metrics:
   - Total applications sent (automated + email)
   - Response rate
   - Profile views
   - New connections
2. Update universal tracker with all activities
3. Plan tomorrow's targets

## Weekly (Fridays)
1. Generate comprehensive report
2. Analyze response rates by channel
3. Adjust strategy based on results
4. Update AI Talent Optimizer settings
"""
    
    with open('daily_workflow.md', 'w') as f:
        f.write(workflow)
    
    print("\n📋 Created: daily_workflow.md")
    print("Follow this workflow to maximize your job search effectiveness!")


def main():
    """Run the integration setup"""
    
    print("🚀 Setting Up Email Application Tracking Integration\n")
    
    # Run integration steps
    integrate_with_universal_tracker()
    
    print("\n" + "=" * 60 + "\n")
    
    # Create sync configuration
    sync_with_career_automation()
    
    print("\n" + "=" * 60 + "\n")
    
    # Create workflow
    create_daily_workflow()
    
    print("\n" + "=" * 60 + "\n")
    
    print("🎯 Your Integrated Job Search Stack:")
    print("1. AI Talent Optimizer → Get discovered by AI recruiters")
    print("2. Career Automation → Apply to 50+ jobs daily automatically")  
    print("3. Email Tracker → Track direct applications & responses")
    print("4. Universal Tracker → Single source of truth for everything")
    
    print("\n💪 You now have the most comprehensive job search system possible!")
    print("Combining AI optimization, automation, and detailed tracking.")


if __name__ == "__main__":
    main()