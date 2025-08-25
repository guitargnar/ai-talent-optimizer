#!/usr/bin/env python3
"""
Priority Application Launcher - Apply to top companies NOW
Focuses on highest priority opportunities from tracker
"""

import webbrowser
import time
from datetime import datetime
from pathlib import Path
import json

def apply_to_priority_companies():
    """Apply to highest priority companies immediately"""
    
    print("\n" + "="*60)
    print("🚀 PRIORITY APPLICATION LAUNCHER")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Priority companies with direct application links
    priority_companies = [
        {
            "company": "Tempus AI",
            "priority": "URGENT",
            "positions": "59 open positions",
            "url": "https://www.tempus.com/careers/",
            "linkedin_search": "https://www.linkedin.com/jobs/search/?keywords=tempus%20AI%20machine%20learning&location=United%20States",
            "notes": "Healthcare AI leader, $8.1B valuation",
            "resume": "resumes/matthew_scott_healthcare_tech_resume.pdf"
        },
        {
            "company": "DeepMind London",
            "priority": "URGENT",
            "positions": "Senior ML Engineer",
            "url": "https://www.deepmind.com/careers",
            "linkedin_search": "https://www.linkedin.com/jobs/search/?keywords=deepmind&location=London",
            "notes": "UK visa sponsorship available",
            "resume": "resumes/european/DeepMind_Senior_Machine_Learning_Engineer.txt"
        },
        {
            "company": "Anthropic",
            "priority": "URGENT",
            "positions": "ML Safety roles",
            "url": "https://www.anthropic.com/careers",
            "linkedin_search": "https://www.linkedin.com/jobs/search/?keywords=anthropic&f_AL=true",
            "notes": "AI safety focus, Claude creators",
            "resume": "resumes/matthew_scott_ai_ml_engineer_resume.pdf"
        },
        {
            "company": "Spotify Stockholm",
            "priority": "HIGH",
            "positions": "Principal ML Platform",
            "url": "https://www.lifeatspotify.com/jobs",
            "linkedin_search": "https://www.linkedin.com/jobs/search/?keywords=spotify%20machine%20learning&location=Stockholm",
            "notes": "Sweden visa sponsorship, SEK 900K-1.3M",
            "resume": "resumes/european/Spotify_Principal_Engineer_-_ML_Platform.txt"
        },
        {
            "company": "Scale AI",
            "priority": "HIGH",
            "positions": "Multiple ML roles",
            "url": "https://scale.com/careers",
            "linkedin_search": "https://www.linkedin.com/jobs/search/?keywords=scale%20AI&f_AL=true",
            "notes": "Fast growing, $7.3B valuation",
            "resume": "resumes/matthew_scott_ai_ml_engineer_resume.pdf"
        },
        {
            "company": "Cohere",
            "priority": "HIGH",
            "positions": "LLM Engineers",
            "url": "https://cohere.com/careers",
            "linkedin_search": "https://www.linkedin.com/jobs/search/?keywords=cohere&f_AL=true",
            "notes": "Enterprise LLMs, Toronto/SF",
            "resume": "resumes/matthew_scott_ai_ml_engineer_resume.pdf"
        }
    ]
    
    # High-value key points to emphasize
    key_points = """
    🎯 KEY POINTS TO EMPHASIZE IN EVERY APPLICATION:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    1. IMMEDIATE AVAILABILITY - No notice period required
    2. 10+ YEARS EXPERIENCE - Enterprise ML systems
    3. TECHNICAL EXPERTISE - Python, TensorFlow, PyTorch
    4. OPEN SOURCE PROJECTS - Mirador, FretForge, FinanceForge
    5. FULL-STACK CAPABLE - Can build complete systems
    6. RELOCATION READY - For international opportunities
    
    COVER LETTER OPENER:
    "I'm immediately available and excited to bring my 10+ years 
    of ML expertise building production AI systems at enterprise scale."
    """
    
    print(key_points)
    print("\n" + "="*60)
    print("PRIORITY APPLICATIONS")
    print("="*60)
    
    for i, company in enumerate(priority_companies, 1):
        print(f"\n{i}. {company['company']} [{company['priority']}]")
        print(f"   📍 Positions: {company['positions']}")
        print(f"   💡 Notes: {company['notes']}")
        print(f"   📄 Resume: {Path(company['resume']).name}")
        print(f"   🔗 Careers: {company['url']}")
    
    print("\n" + "="*60)
    print("APPLICATION STEPS")
    print("="*60)
    
    steps = """
    1. SELECT a company number (1-6) to open both:
       - Company careers page
       - LinkedIn job search (filtered for Easy Apply)
    
    2. APPLY directly on company site first
    
    3. THEN check LinkedIn for Easy Apply options
    
    4. USE the specified resume for each company
    
    5. TRACK in master CSV after applying
    """
    
    print(steps)
    
    # Interactive selection
    while True:
        choice = input(f"\nEnter company number (1-{len(priority_companies)}), 'all' to open all, or 'q' to quit: ")
        
        if choice.lower() == 'q':
            break
        elif choice.lower() == 'all':
            print("\n🚀 Opening all priority companies...")
            for company in priority_companies:
                print(f"   Opening {company['company']}...")
                webbrowser.open(company['url'])
                time.sleep(1)
                webbrowser.open(company['linkedin_search'])
                time.sleep(1)
            break
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(priority_companies):
                    company = priority_companies[idx]
                    
                    print(f"\n🎯 Opening {company['company']} application pages...")
                    print(f"📄 Use resume: {company['resume']}")
                    
                    # Open careers page
                    webbrowser.open(company['url'])
                    time.sleep(2)
                    
                    # Open LinkedIn search
                    print(f"🔗 Opening LinkedIn search for {company['company']}...")
                    webbrowser.open(company['linkedin_search'])
                    
                    # Show quick application template
                    print(f"\n📝 QUICK APPLICATION TEMPLATE FOR {company['company'].upper()}:")
                    print("-" * 40)
                    
                    template = f"""
Subject: Principal ML Engineer - Immediate Availability

Dear {company['company']} Hiring Team,

I'm immediately available and excited to bring my 10+ years of ML expertise 
building production systems at enterprise scale.

Why I'm perfect for {company['company']}:
• Expert in Python, TensorFlow, PyTorch, and scikit-learn
• Built production ML systems handling large-scale data
• Strong software engineering and DevOps practices
• {company['notes']}

I can start immediately and am excited to discuss how my experience 
can contribute to {company['company']}'s mission.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77
                    """
                    
                    print(template)
                    print("-" * 40)
                    
                    # Log application
                    log_application(company)
                    
                else:
                    print("❌ Invalid number")
            except ValueError:
                print("❌ Please enter a number")
    
    print("\n✨ Good luck with your priority applications!")
    print("📊 Remember to update MASTER_TRACKER_400K.csv after applying")


def log_application(company):
    """Log that we initiated an application"""
    log_file = Path("application_log.json")
    
    # Load existing log
    if log_file.exists():
        with open(log_file, 'r') as f:
            log = json.load(f)
    else:
        log = {"applications": []}
    
    # Add new entry
    log["applications"].append({
        "company": company["company"],
        "timestamp": datetime.now().isoformat(),
        "priority": company["priority"],
        "method": "direct_and_linkedin"
    })
    
    # Save log
    with open(log_file, 'w') as f:
        json.dump(log, f, indent=2)
    
    print(f"✅ Application logged for {company['company']}")


def check_linkedin_easy_apply():
    """Quick check for LinkedIn Easy Apply setup"""
    config_path = Path("linkedin_config.json")
    
    if not config_path.exists():
        print("\n⚠️ LinkedIn automation not configured")
        print("Run: python3 quick_linkedin_apply.py to set up")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    if not config.get('linkedin_email'):
        print("\n⚠️ LinkedIn credentials not set")
        print("Update linkedin_config.json with your credentials")
        return False
    
    print("\n✅ LinkedIn Easy Apply is configured and ready")
    return True


if __name__ == "__main__":
    # Check LinkedIn setup
    check_linkedin_easy_apply()
    
    # Launch priority applications
    apply_to_priority_companies()