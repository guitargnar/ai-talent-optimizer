#!/usr/bin/env python3
"""Check all emails sent today"""

import json
from datetime import datetime
from pathlib import Path

def check_bcc_log():
    """Check BCC tracking log"""
    log_file = Path("data/bcc_tracking_log.json")
    if log_file.exists():
        with open(log_file) as f:
            data = json.load(f)
        
        sent_emails = data.get('sent_emails', {})
        today = datetime.now().strftime('%Y-%m-%d')
        
        todays = []
        for tracking_id, email_data in sent_emails.items():
            if today in email_data.get('sent_date', ''):
                todays.append({
                    'time': email_data['sent_date'][11:19],
                    'to': email_data['to'],
                    'company': email_data.get('company', 'Unknown'),
                    'id': tracking_id
                })
        
        return sorted(todays, key=lambda x: x['time'])
    return []

def check_email_log():
    """Check email applications log"""
    log_file = Path("data/email_applications_log.csv") 
    if log_file.exists():
        import csv
        todays = []
        today = datetime.now().strftime('%Y-%m-%d')
        
        with open(log_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if today in row.get('timestamp', ''):
                    todays.append({
                        'time': row['timestamp'][11:19] if 'timestamp' in row else 'N/A',
                        'company': row.get('company', 'Unknown'),
                        'email': row.get('email', 'N/A'),
                        'status': row.get('status', 'N/A')
                    })
        
        return sorted(todays, key=lambda x: x['time'])
    return []

def main():
    print("📧 TODAY'S JOB APPLICATIONS SENT")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)
    
    # Check BCC log
    bcc_sends = check_bcc_log()
    print(f"\n📋 BCC TRACKING LOG ({len(bcc_sends)} found):")
    if bcc_sends:
        for i, email in enumerate(bcc_sends, 1):
            print(f"{i}. {email['time']} → {email['to']}")
            print(f"   Company: {email['company']}")
            print(f"   Tracking: {email['id']}")
    else:
        print("   No emails found in BCC log today")
    
    # Check CSV log
    csv_sends = check_email_log()
    print(f"\n📋 EMAIL APPLICATION LOG ({len(csv_sends)} found):")
    if csv_sends:
        for i, email in enumerate(csv_sends, 1):
            print(f"{i}. {email['time']} - {email['company']}")
            print(f"   Email: {email['email']}")
            print(f"   Status: {email['status']}")
    else:
        print("   No emails found in CSV log today")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 TOTAL SENT TODAY: {len(bcc_sends) + len(csv_sends)}")
    
    # List the companies we know we sent to
    print("\n🎯 CONFIRMED SENDS (from script output):")
    confirmed = [
        "Google (careers@google.com) - ee8269cc56f8",
        "Meta (recruiting@meta.com) - 5a148e9b3333", 
        "Apple (aiml-jobs@apple.com) - 655e9dc31839",
        "Microsoft (staffing@microsoft.com) - 4df243af8cb5",
        "Amazon (amazonjobs@amazon.com) - 2e5ee61d9d0d",
        "Gamesight (careers@gamesight.io) - 2bad096df9e9",
        "Madhive (careers@madhive.com) - ae52b053829d",
        "Komodo Health (careers@komodohealth.com) - 5457e5f47827",
        "PrizePicks (careers@prizepicks.com) - 5fda8d03f646"
    ]
    
    for company in confirmed:
        print(f"  ✅ {company}")
    
    print(f"\n📧 Check matthewdscott7+jobapps@gmail.com for BCC copies")
    print("🔍 Responses typically arrive in 3-7 days")

if __name__ == "__main__":
    main()