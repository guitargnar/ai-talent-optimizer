#!/usr/bin/env python3
"""
LIVE TEST - Greenhouse Automation with Real Job Posting
Testing with mthree Junior Software Engineer position
"""

from web_form_automator import WebFormAutomator
from pathlib import Path
from datetime import datetime

def run_live_test(dry_run=True):
    """
    Execute live test with real Greenhouse job posting
    
    Target: mthree Junior Software Engineer
    URL: https://job-boards.greenhouse.io/mthreerecruitingportal/jobs/4406180006
    """
    
    print("="*60)
    print("🚀 LIVE GREENHOUSE AUTOMATION TEST")
    print("="*60)
    print(f"Mode: {'DRY RUN - Screenshot Only' if dry_run else '⚠️  LIVE SUBMISSION'}")
    print("="*60)
    
    # Real job posting URL
    job_url = "https://job-boards.greenhouse.io/mthreerecruitingportal/jobs/4406180006"
    company = "mthree"
    role = "Junior Software Engineer"
    
    print(f"\n🎯 Target Position:")
    print(f"   Company: {company}")
    print(f"   Role: {role}")
    print(f"   URL: {job_url}")
    
    # Professional cover letter for this specific role
    cover_letter = """Dear mthree Hiring Team,

I am writing to express my strong interest in the Junior Software Engineer position at mthree. Your comprehensive training program and focus on developing new graduates aligns perfectly with my career goals and technical background.

As a software engineer with 10+ years of Python experience, I bring:

• Extensive experience building production systems, including a 274-module AI platform
• Strong foundation in software development processes, source control, and agile methodologies
• Proven ability to work in global team environments
• Active open source contributor with a portfolio on GitHub (github.com/guitargnar)
• Healthcare technology experience from 10 years at Humana

What particularly excites me about mthree is your 4-8 week training academy and commitment to continuous learning. Having invested heavily in my own development (including $250/month for Claude Code), I deeply value organizations that prioritize skill growth and mentorship.

My recent work includes building an AI Talent Optimizer platform that demonstrates my ability to create sophisticated automation systems while maintaining code quality and safety standards. This aligns well with your focus on building complex applications in team environments.

I am eager to bring my technical skills and passion for continuous improvement to the mthree team. The opportunity to work with other motivated graduates while contributing to meaningful projects is exactly what I'm seeking in my next role.

Thank you for considering my application. I look forward to discussing how I can contribute to mthree's success.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
LinkedIn: linkedin.com/in/mscott77
GitHub: github.com/guitargnar"""

    # Initialize automator
    automator = WebFormAutomator(dry_run=dry_run)
    
    print("\n📋 Application Details:")
    print(f"   Applicant: {automator.user_info['first_name']} {automator.user_info['last_name']}")
    print(f"   Email: {automator.user_info['email']}")
    print(f"   Phone: {automator.user_info['phone']}")
    print(f"   Resume: resumes/base_resume.pdf")
    
    # Check resume exists
    resume_path = "resumes/base_resume.pdf"
    if Path(resume_path).exists():
        print(f"   ✅ Resume found: {Path(resume_path).absolute()}")
    else:
        print(f"   ⚠️  Resume not found - will need manual upload")
    
    print("\n" + "="*60)
    print("🤖 STARTING AUTOMATION")
    print("="*60)
    
    try:
        # Execute the automation
        success, message = automator.apply_via_greenhouse(
            job_url=job_url,
            cover_letter=cover_letter,
            resume_path=resume_path
        )
        
        print("\n" + "="*60)
        print("📊 AUTOMATION RESULT")
        print("="*60)
        print(f"Status: {'SUCCESS' if success else 'FAILED'}")
        print(f"Message: {message}")
        
        if success and dry_run:
            print("\n✅ DRY RUN COMPLETE - Application NOT Submitted")
            print("\n📸 Screenshot captured for review")
            print("   Please review the screenshot to verify:")
            print("   • All form fields are correctly filled")
            print("   • Cover letter is properly formatted")
            print("   • Resume attachment is indicated")
            print("\n⚠️  To submit for real, run with dry_run=False")
            
            # Create timestamp for screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/greenhouse_review_{timestamp}.png"
            print(f"\n📁 Screenshot location: {screenshot_path}")
            
        elif success and not dry_run:
            print("\n🎉 LIVE SUBMISSION COMPLETE!")
            print("   Your application has been submitted to mthree")
            print("   Check your email for confirmation")
            
            # Log the submission
            with open("live_submissions.log", "a") as f:
                f.write(f"{datetime.now().isoformat()} | {company} | {role} | {job_url} | SUCCESS\n")
            
    except Exception as e:
        print(f"\n❌ Error during automation: {str(e)}")
        return False
    
    return success

def main():
    """Main execution"""
    
    # Ensure screenshots directory exists
    Path("screenshots").mkdir(exist_ok=True)
    
    print("🔐 SAFETY CHECK")
    print("="*60)
    print("This script will attempt to fill out a REAL job application")
    print("Current mode: DRY RUN (screenshot only)")
    print("="*60)
    
    # First run - always dry run for safety
    print("\n📋 Phase 1: DRY RUN TEST")
    success = run_live_test(dry_run=True)
    
    if success:
        print("\n" + "="*60)
        print("✅ DRY RUN SUCCESSFUL")
        print("="*60)
        print("\nNext steps:")
        print("1. Review the screenshot in screenshots/ directory")
        print("2. Verify all fields are correctly populated")
        print("3. If everything looks good, uncomment the live submission below")
        
        # LIVE SUBMISSION - UNCOMMENT ONLY AFTER REVIEWING SCREENSHOT
        # print("\n⚠️  PREPARING FOR LIVE SUBMISSION...")
        # response = input("Type 'SUBMIT' to proceed with real submission: ")
        # if response == "SUBMIT":
        #     print("\n📋 Phase 2: LIVE SUBMISSION")
        #     run_live_test(dry_run=False)
        # else:
        #     print("Live submission cancelled")

if __name__ == "__main__":
    main()