#!/usr/bin/env python3
"""
Apply to European Jobs - Quick application sender
Sends applications to the European companies we've identified
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import webbrowser

def main():
    """Show European jobs and provide quick apply links"""
    
    print("\n" + "="*60)
    print("🇪🇺 EUROPEAN JOB APPLICATION LAUNCHER")
    print("="*60)
    
    # Get jobs from database
    db_path = Path('data/european_jobs.db')
    if not db_path.exists():
        print("❌ No European jobs database found. Run fetch_european_jobs_now.py first")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT company, position, location, salary_range, url, resume_path
    FROM european_jobs
    WHERE resume_generated = 1
    ORDER BY 
        CASE 
            WHEN salary_range LIKE '%£%' THEN 1  -- UK first
            WHEN salary_range LIKE '%€%' THEN 2  -- EU second
            ELSE 3
        END
    """)
    
    jobs = cursor.fetchall()
    conn.close()
    
    if not jobs:
        print("❌ No jobs with resumes found")
        return
    
    print(f"\n📋 Found {len(jobs)} European positions with tailored resumes")
    print("-" * 60)
    
    # Display jobs
    for i, (company, position, location, salary, url, resume_path) in enumerate(jobs, 1):
        print(f"\n{i}. {company}")
        print(f"   📍 {location}")
        print(f"   💼 {position}")
        print(f"   💰 {salary}")
        print(f"   📄 Resume: {Path(resume_path).name if resume_path else 'Not generated'}")
        print(f"   🔗 {url}")
    
    print("\n" + "="*60)
    print("📝 APPLICATION INSTRUCTIONS")
    print("="*60)
    
    print("""
1. SELECT A JOB NUMBER to open the careers page
2. COPY YOUR RESUME from resumes/european/
3. APPLY DIRECTLY on the company website
4. USE THESE KEY POINTS in your application:
   
   ✅ 10 years at Humana (Fortune 50)
   ✅ $1.2M annual savings through ML automation
   ✅ 7 specialized LLMs in production
   ✅ Available for immediate relocation
   ✅ Eligible for work visa sponsorship
    """)
    
    # Interactive selection
    while True:
        choice = input("\nEnter job number (1-{}) to open, 'all' for all links, or 'q' to quit: ".format(len(jobs)))
        
        if choice.lower() == 'q':
            break
        elif choice.lower() == 'all':
            print("\n🚀 Opening all career pages...")
            for company, position, location, salary, url, resume_path in jobs:
                if url and url != 'https://example.com':
                    print(f"   Opening {company}...")
                    webbrowser.open(url)
            break
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(jobs):
                    company, position, location, salary, url, resume_path = jobs[idx]
                    
                    print(f"\n🎯 Opening {company} careers page...")
                    print(f"📄 Your resume is at: {resume_path}")
                    
                    if url and url != 'https://example.com':
                        webbrowser.open(url)
                    else:
                        print(f"⚠️  No URL available, search for: {company} careers {position}")
                    
                    # Show resume snippet
                    if resume_path and Path(resume_path).exists():
                        print("\n📋 RESUME PREVIEW (first 20 lines):")
                        print("-" * 40)
                        with open(resume_path, 'r') as f:
                            lines = f.readlines()[:20]
                            for line in lines:
                                print(line.rstrip())
                        print("-" * 40)
                else:
                    print("❌ Invalid number")
            except ValueError:
                print("❌ Please enter a number")
    
    print("\n✨ Good luck with your applications!")
    print("💡 TIP: Follow up in 3-5 days if no response")


if __name__ == "__main__":
    main()