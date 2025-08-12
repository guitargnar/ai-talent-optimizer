#!/usr/bin/env python3
"""
Add Job from User Input - Easy way to add jobs you find manually
"""

import sqlite3
from datetime import datetime
import re

def parse_salary(salary_text):
    """Parse salary from various formats"""
    # Look for numbers with K
    if not salary_text or salary_text.lower() in ['not listed', 'competitive', 'negotiable']:
        return 400000, 500000  # Default for principal roles
    
    # Extract numbers
    numbers = re.findall(r'(\d+)k?', salary_text.lower().replace(',', ''))
    if len(numbers) >= 2:
        min_sal = int(numbers[0]) * (1000 if 'k' in salary_text.lower() else 1)
        max_sal = int(numbers[1]) * (1000 if 'k' in salary_text.lower() else 1)
        return min_sal, max_sal
    elif len(numbers) == 1:
        base = int(numbers[0]) * (1000 if 'k' in salary_text.lower() else 1)
        return int(base * 0.9), int(base * 1.1)  # +/- 10%
    
    return 400000, 500000  # Default

def add_single_job():
    """Add a single job interactively"""
    print("\n📝 ADD A NEW $400K+ JOB OPPORTUNITY")
    print("="*60)
    
    # Collect information
    company = input("Company name: ").strip()
    position = input("Position title: ").strip()
    url = input("Application URL (or 'skip'): ").strip()
    if url.lower() == 'skip':
        url = f"https://careers.{company.lower().replace(' ', '')}.com"
    
    location = input("Location (e.g., 'Remote', 'SF/Remote'): ").strip()
    salary = input("Salary range (e.g., '400K-500K' or 'not listed'): ").strip()
    
    min_sal, max_sal = parse_salary(salary)
    
    notes = input("Any notes (or press Enter to skip): ").strip()
    
    # Priority
    print("\nPriority level:")
    print("1. URGENT (perfect fit)")
    print("2. HIGH (great opportunity)")
    print("3. MEDIUM (worth applying)")
    priority_choice = input("Select (1-3): ").strip()
    priority_map = {'1': 'URGENT', '2': 'HIGH', '3': 'MEDIUM'}
    priority = priority_map.get(priority_choice, 'MEDIUM')
    
    # Add to database
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("""
        SELECT id FROM principal_jobs 
        WHERE company = ? AND position = ?
    """, (company, position))
    
    if cursor.fetchone():
        print(f"\n⚠️  Job already exists: {company} - {position}")
        update = input("Update it with new information? (yes/no): ").strip()
        if update.lower() == 'yes':
            cursor.execute("""
                UPDATE principal_jobs 
                SET url = ?, min_salary = ?, max_salary = ?, location = ?, notes = ?
                WHERE company = ? AND position = ?
            """, (url, min_sal, max_sal, location, f"Priority: {priority}. {notes}", 
                  company, position))
            print("✅ Job updated!")
    else:
        cursor.execute("""
            INSERT INTO principal_jobs 
            (company, position, url, min_salary, max_salary, location, 
             remote, healthcare_focused, ai_focused, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company,
            position,
            url,
            min_sal,
            max_sal,
            location,
            1 if 'remote' in location.lower() else 0,
            1 if any(h in company.lower() for h in ['health', 'medical', 'bio', 'pharma']) else 0,
            1 if 'ml' in position.lower() or 'machine learning' in position.lower() or 'ai' in position.lower() else 0,
            f"Priority: {priority}. Added manually. {notes}"
        ))
        print(f"✅ Added: {company} - {position} (${min_sal:,}-${max_sal:,})")
    
    conn.commit()
    conn.close()

def add_bulk_jobs():
    """Add multiple jobs from paste"""
    print("\n📋 BULK ADD JOBS")
    print("="*60)
    print("Paste job listings in this format:")
    print("Company | Position | URL | Location | Salary")
    print("Example:")
    print("Stripe | Principal ML Engineer | https://stripe.com/jobs/123 | Remote | 400K-500K")
    print("\nPaste your jobs below (type 'DONE' on a new line when finished):")
    
    jobs = []
    while True:
        line = input()
        if line.strip().upper() == 'DONE':
            break
        if '|' in line:
            jobs.append(line.strip())
    
    if not jobs:
        print("No jobs to add")
        return
    
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    
    added = 0
    for job_line in jobs:
        parts = [p.strip() for p in job_line.split('|')]
        if len(parts) >= 2:
            company = parts[0]
            position = parts[1]
            url = parts[2] if len(parts) > 2 and parts[2] else f"https://careers.{company.lower().replace(' ', '')}.com"
            location = parts[3] if len(parts) > 3 else "Remote"
            salary = parts[4] if len(parts) > 4 else "400K+"
            
            min_sal, max_sal = parse_salary(salary)
            
            # Check if exists
            cursor.execute("""
                SELECT id FROM principal_jobs 
                WHERE company = ? AND position = ?
            """, (company, position))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO principal_jobs 
                    (company, position, url, min_salary, max_salary, location, 
                     remote, healthcare_focused, ai_focused, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company,
                    position,
                    url,
                    min_sal,
                    max_sal,
                    location,
                    1 if 'remote' in location.lower() else 0,
                    1 if any(h in company.lower() for h in ['health', 'medical', 'bio', 'pharma']) else 0,
                    1,  # Assume all are AI/ML focused
                    "Added via bulk import"
                ))
                added += 1
                print(f"✅ Added: {company} - {position}")
            else:
                print(f"⏭️  Skipped (exists): {company} - {position}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Added {added} new jobs to database")

def quick_add_from_url():
    """Quick add just from URL - we'll fetch details"""
    print("\n🔗 QUICK ADD FROM URL")
    print("="*60)
    
    url = input("Paste job URL: ").strip()
    
    # Parse company from URL
    company = "Unknown"
    if 'greenhouse.io' in url:
        # Extract company from greenhouse URL
        parts = url.split('/')
        for i, part in enumerate(parts):
            if part == 'boards.greenhouse.io' and i+1 < len(parts):
                company = parts[i+1].replace('-', ' ').title()
    elif 'lever.co' in url:
        parts = url.split('/')
        for i, part in enumerate(parts):
            if part == 'jobs.lever.co' and i+1 < len(parts):
                company = parts[i+1].replace('-', ' ').title()
    elif 'ashbyhq.com' in url:
        parts = url.split('/')
        for i, part in enumerate(parts):
            if part == 'jobs.ashbyhq.com' and i+1 < len(parts):
                company = parts[i+1].replace('-', ' ').title()
    else:
        company = input("Company name: ").strip()
    
    position = input("Position title: ").strip()
    location = input("Location (default: Remote): ").strip() or "Remote"
    salary = input("Salary (default: 400K-500K): ").strip() or "400K-500K"
    
    min_sal, max_sal = parse_salary(salary)
    
    # Add to database
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO principal_jobs 
        (company, position, url, min_salary, max_salary, location, 
         remote, healthcare_focused, ai_focused, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company,
        position,
        url,
        min_sal,
        max_sal,
        location,
        1 if 'remote' in location.lower() else 0,
        0,
        1,
        f"Added from URL. Priority: HIGH"
    ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added: {company} - {position}")
    print(f"   URL: {url}")
    print(f"   Salary: ${min_sal:,}-${max_sal:,}")

def view_recent_jobs():
    """View recently added jobs"""
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT company, position, min_salary, max_salary, url, 
               datetime(discovered_at) as added_date
        FROM principal_jobs 
        ORDER BY discovered_at DESC 
        LIMIT 10
    """)
    
    jobs = cursor.fetchall()
    conn.close()
    
    if jobs:
        print("\n📋 RECENTLY ADDED JOBS:")
        print("="*60)
        for company, position, min_sal, max_sal, url, added in jobs:
            print(f"\n{company} - {position}")
            print(f"  💰 ${min_sal:,}-${max_sal:,}")
            print(f"  🔗 {url[:50]}...")
            if added:
                print(f"  📅 Added: {added}")
    else:
        print("\n❌ No jobs in database")

def main():
    """Main menu"""
    while True:
        print("\n" + "="*60)
        print("🎯 JOB ADDITION TOOL")
        print("="*60)
        print("1. Add single job (detailed)")
        print("2. Bulk add jobs (paste multiple)")
        print("3. Quick add from URL")
        print("4. View recent jobs")
        print("5. Generate applications for new jobs")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            add_single_job()
        elif choice == '2':
            add_bulk_jobs()
        elif choice == '3':
            quick_add_from_url()
        elif choice == '4':
            view_recent_jobs()
        elif choice == '5':
            print("\n🚀 Generating applications...")
            import subprocess
            subprocess.run(["python3", "apply_to_real_jobs_now.py"])
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()