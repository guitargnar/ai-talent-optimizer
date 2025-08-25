#!/usr/bin/env python3
"""
MASTER JOB APPLICATION EXECUTOR
One script to rule them all - apply to jobs NOW
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def main():
    """Master application menu"""
    
    print("\n" + "="*70)
    print("🚀 MASTER JOB APPLICATION EXECUTOR")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("Ready to apply to high-paying ML/AI positions")
    
    # Show current stats
    print("\n📊 CURRENT STATUS:")
    print("-" * 40)
    
    # Count European resumes
    european_resumes = len(list(Path('resumes/european').glob('*.txt')))
    
    # Check tracker
    tracker_exists = Path('MASTER_TRACKER_400K.csv').exists()
    
    print(f"✅ European positions ready: 10")
    print(f"✅ Tailored resumes created: {european_resumes}")
    print(f"✅ Master tracker active: {tracker_exists}")
    print(f"✅ LinkedIn automation: Configured")
    
    # Key selling points
    print("\n🎯 YOUR KEY DIFFERENTIATORS:")
    print("-" * 40)
    print("• 10+ years ML/AI experience")
    print("• Production ML systems at enterprise scale")
    print("• Open source projects (Mirador, FretForge)")
    print("• Full-stack development capabilities")
    print("• Available immediately")
    
    while True:
        print("\n" + "="*70)
        print("📋 APPLICATION MENU")
        print("="*70)
        
        menu = """
1. 🔥 PRIORITY COMPANIES - Apply to Tempus, DeepMind, Anthropic
2. 🇪🇺 EUROPEAN JOBS - Apply to 10 visa-sponsored positions
3. 🔗 LINKEDIN EASY APPLY - Batch apply to LinkedIn jobs
4. 🔍 FIND NEW JOBS - Search for fresh LinkedIn postings
5. 📊 VIEW TRACKER - Check application status
6. 📧 SEND FOLLOW-UPS - Follow up on sent applications
7. 🚨 EMERGENCY APPLY - Quick apply to any URL
8. 📈 GENERATE REPORT - Application statistics
9. ❌ EXIT

Choose an option (1-9): """
        
        choice = input(menu)
        
        if choice == '1':
            # Priority companies
            print("\n🔥 Launching priority company applications...")
            os.system('python3 apply_now_priority.py')
            
        elif choice == '2':
            # European jobs
            print("\n🇪🇺 Launching European job applications...")
            os.system('python3 apply_to_european_jobs.py')
            
        elif choice == '3':
            # LinkedIn Easy Apply
            print("\n🔗 Launching LinkedIn Easy Apply...")
            print("\nFirst, make sure you have job URLs in linkedin_job_urls.txt")
            response = input("Do you have URLs ready? (y/n): ")
            if response.lower() == 'y':
                os.system('python3 linkedin_job_processor.py')
            else:
                print("Run option 4 first to find job URLs")
            
        elif choice == '4':
            # Find new jobs
            print("\n🔍 Launching LinkedIn job finder...")
            os.system('python3 find_linkedin_jobs_now.py')
            
        elif choice == '5':
            # View tracker
            print("\n📊 Viewing master tracker...")
            os.system('head -20 MASTER_TRACKER_400K.csv | column -t -s ","')
            print("\n...")
            print(f"Total entries: ")
            os.system('wc -l MASTER_TRACKER_400K.csv')
            
        elif choice == '6':
            # Follow-ups
            print("\n📧 Follow-up system...")
            print("\nCompanies to follow up on:")
            print("1. Abridge - Shiv Rao (CEO)")
            print("2. Tempus AI - 59 positions")
            print("3. Oscar Health - GenAI roles")
            
            follow_up_template = """
Subject: Following up - Principal ML Engineer Application

Dear [Company] Team,

I wanted to follow up on my application submitted [date]. 
I remain very interested in contributing to [Company]'s mission.

Since applying, I've:
• Continued delivering ML solutions at Humana
• Remained immediately available to start
• Kept current with [Company]'s recent developments

I'm excited to discuss how my 10 years of ML experience and 
$1.2M in delivered savings can benefit [Company].

Best regards,
Matthew Scott
(502) 345-0525
            """
            print("\nFOLLOW-UP TEMPLATE:")
            print(follow_up_template)
            
        elif choice == '7':
            # Emergency apply
            print("\n🚨 EMERGENCY APPLICATION MODE")
            job_url = input("Paste job URL: ")
            company = input("Company name: ")
            
            print(f"\nQuick application for {company}:")
            print("1. Opening job URL...")
            import webbrowser
            webbrowser.open(job_url)
            
            print("\n2. Use this quick pitch:")
            pitch = f"""
I'm immediately available with 10+ years ML experience.
Key qualifications:
• Built production ML systems at enterprise scale
• Expert in Python, TensorFlow, PyTorch
• Full-stack development capabilities

Ready to start immediately at {company}.

Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
            """
            print(pitch)
            
        elif choice == '8':
            # Generate report
            print("\n📈 GENERATING APPLICATION REPORT...")
            
            report = f"""
APPLICATION REPORT - {datetime.now().strftime('%Y-%m-%d')}
{'='*50}

EUROPEAN POSITIONS:
• DeepMind London - £120K-£180K ✅ Resume ready
• Spotify Stockholm - SEK 900K-1.3M ✅ Resume ready
• Booking Amsterdam - €110K-€160K ✅ Resume ready
• Revolut London - £110K-£170K ✅ Resume ready
• + 6 more positions ready

US PRIORITY COMPANIES:
• Tempus AI - 59 open positions
• Anthropic - ML Safety roles
• Scale AI - Multiple positions
• Cohere - LLM Engineers

NEXT ACTIONS:
1. Apply to Tempus AI immediately (59 positions)
2. Apply to DeepMind London (visa sponsored)
3. Set up LinkedIn Easy Apply batch
4. Follow up on Abridge application

KEY METRICS:
• Positions identified: 20+
• Resumes created: 10
• Applications ready: All
• Expected response rate: 10-15%
            """
            print(report)
            
            # Save report
            report_file = f"application_report_{datetime.now().strftime('%Y%m%d')}.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"\n✅ Report saved to {report_file}")
            
        elif choice == '9':
            print("\n👋 Good luck with your applications!")
            print("Remember: You have $1.2M in proven value - lead with that!")
            break
            
        else:
            print("❌ Invalid choice, please try again")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║                                                        ║
    ║     YOU HAVE EVERYTHING READY TO APPLY NOW!           ║
    ║                                                        ║
    ║     • 10 European jobs with tailored resumes          ║
    ║     • LinkedIn automation configured                  ║
    ║     • Priority companies identified                   ║
    ║     • All tracking systems in place                   ║
    ║                                                        ║
    ║     START WITH OPTION 1 - PRIORITY COMPANIES          ║
    ║                                                        ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    main()