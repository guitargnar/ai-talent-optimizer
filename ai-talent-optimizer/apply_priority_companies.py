#!/usr/bin/env python3
"""Apply to priority companies from MASTER_TRACKER_400K.csv"""

import csv
import time
from datetime import datetime

# Read priority companies
priority_companies = []
with open('MASTER_TRACKER_400K.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Category'] in ['Abridge', 'Tempus AI', 'Oscar Health', 'Medium'] and row['Status'] == 'TODO':
            priority_companies.append({
                'company': row['Category'],
                'url': row['Email/LinkedIn'],
                'notes': row['Notes'],
                'value': row['Value/Comp']
            })

print(f"\n🎯 PRIORITY TARGETS ({len(priority_companies)} companies):")
for company in priority_companies:
    print(f"   - {company['company']} ({company['value']})")
    print(f"     {company['notes']}")

# Manual application instructions
print("\n📋 MANUAL APPLICATION STEPS:")
print("="*60)

print("\n1️⃣ ABRIDGE (Shiv Rao already contacted)")
print("   - Go to: https://abridge.com/careers")
print("   - Apply to Principal Engineer role")
print("   - Reference Shiv Rao contact in cover letter")
print("   - Use personalized_apply.py for this one")

print("\n2️⃣ TEMPUS AI (59 open positions!)")
print("   - Go to: https://tempus.com/careers")
print("   - Filter for: Engineering, AI/ML, Principal/Staff")
print("   - Apply to top 3 matches")

print("\n3️⃣ OSCAR HEALTH (GenAI focus)")
print("   - Go to: https://oscarlabs.com/careers")
print("   - Look for: AI/ML, Engineering Leadership")
print("   - Emphasize healthcare experience")

print("\n4️⃣ MEDIUM (VP Engineering)")
print("   - Go to: https://medium.com/jobs")
print("   - Apply to VP Engineering role")
print("   - Reports directly to CEO")

print("\n🚀 AUTOMATION COMMAND:")
print("python3 personalized_apply.py --company Abridge --position 'Principal Engineer'")

# Update tracker
print("\n📊 Updating MASTER_TRACKER_400K.csv...")
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

# Read current CSV
rows = []
with open('MASTER_TRACKER_400K.csv', 'r') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

# Add manual application note
new_row = {
    'Section': 'MANUAL_ACTION',
    'Category': 'Priority Applications',
    'Item': 'Manual applications initiated',
    'Target': 'IN_PROGRESS',
    'Status': 'ACTIVE',
    'Priority': 'URGENT',
    'Value/Comp': '$400K+',
    'Contact': 'Self',
    'Email/LinkedIn': '',
    'Notes': f'Started manual applications at {timestamp}',
    'Date': datetime.now().strftime("%Y-%m-%d"),
    'Follow-Up': ''
}
rows.append(new_row)

# Write back
with open('MASTER_TRACKER_400K.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("✅ Tracker updated!")