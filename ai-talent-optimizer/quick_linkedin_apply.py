#!/usr/bin/env python3
"""
Quick LinkedIn Easy Apply - Simplified interface for fast job applications
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Import the automation components
from linkedin_easy_apply_automation import LinkedInEasyApplyBot
from linkedin_job_processor import LinkedInJobProcessor


def quick_setup():
    """Quick setup wizard for first-time users"""
    config_path = Path('linkedin_config.json')
    
    if not config_path.exists():
        print("\n🚀 QUICK SETUP WIZARD")
        print("=" * 50)
        
        email = input("LinkedIn email: ")
        password = input("LinkedIn password: ")
        phone = input("Phone number (e.g., (502) 345-0525): ")
        resume_path = input("Full path to resume PDF: ")
        
        config = {
            "linkedin_email": email,
            "linkedin_password": password,
            "profile": {
                "phone": phone,
                "email": email,
                "linkedin_url": "linkedin.com/in/mscott77",
                "current_company": "Humana",
                "years_experience": "10",
                "degree": "Self-Directed Learning",
                "school": "Independent Study",
                "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "AI"]
            },
            "resume_path": resume_path,
            "auto_submit": False,
            "max_applications_per_day": 50
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration saved!")
        return True
    
    return False


def apply_to_single_job(job_url: str, auto_submit: bool = False):
    """Apply to a single LinkedIn job"""
    print(f"\n🎯 Applying to: {job_url}")
    
    # Update auto_submit setting
    config_path = Path('linkedin_config.json')
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        config['auto_submit'] = auto_submit
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    # Initialize and run bot
    bot = LinkedInEasyApplyBot(headless=False)
    
    try:
        bot.setup_driver()
        
        if bot.login_to_linkedin():
            success = bot.apply_to_job(job_url)
            
            if success:
                print("✅ Application submitted successfully!")
            else:
                print("⚠️ Application prepared (review required)")
        else:
            print("❌ Login failed - check credentials")
            
    finally:
        bot.cleanup()


def apply_to_job_list():
    """Apply to jobs from linkedin_job_urls.txt"""
    processor = LinkedInJobProcessor()
    
    # Load URLs from file
    urls = processor.load_urls_from_file()
    
    if not urls:
        print("\n⚠️ No URLs found in linkedin_job_urls.txt")
        print("Add LinkedIn job URLs (one per line) to linkedin_job_urls.txt")
        return
    
    print(f"\n📋 Found {len(urls)} job URLs")
    
    # Ask for confirmation
    response = input("Apply to all jobs? (y/n): ")
    if response.lower() == 'y':
        # Ask about auto-submit
        auto = input("Auto-submit applications? (y/n): ")
        auto_submit = auto.lower() == 'y'
        
        # Process URLs
        processor.process_urls_batch(urls, auto_submit=auto_submit, max_applications=10)
        
        # Show report
        print("\n" + processor.generate_report())


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("🚀 LINKEDIN EASY APPLY - QUICK START")
    print("=" * 60)
    
    # Check for first-time setup
    if not Path('linkedin_config.json').exists():
        quick_setup()
    
    # Menu
    print("\nChoose an option:")
    print("1. Apply to single job (paste URL)")
    print("2. Apply to job list (from file)")
    print("3. Setup/Update configuration")
    print("4. View application report")
    print("5. Exit")
    
    choice = input("\nEnter choice (1-5): ")
    
    if choice == '1':
        # Single job application
        job_url = input("Paste LinkedIn job URL: ").strip()
        if job_url:
            auto = input("Auto-submit? (y/n): ")
            apply_to_single_job(job_url, auto_submit=(auto.lower() == 'y'))
    
    elif choice == '2':
        # Batch application
        apply_to_job_list()
    
    elif choice == '3':
        # Setup wizard
        quick_setup()
        print("\n✅ Configuration updated!")
    
    elif choice == '4':
        # View report
        processor = LinkedInJobProcessor()
        print("\n" + processor.generate_report())
    
    elif choice == '5':
        print("Goodbye! 👋")
        sys.exit(0)
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Direct URL provided
        job_url = sys.argv[1]
        if job_url.startswith('http'):
            apply_to_single_job(job_url, auto_submit=False)
        else:
            print(f"Invalid URL: {job_url}")
    else:
        # Interactive menu
        main()