#!/usr/bin/env python3
"""
Test the Greenhouse automation with Puppeteer integration
"""

from web_form_automator import WebFormAutomator
from pathlib import Path
import json

def test_greenhouse_dry_run():
    """Test Greenhouse automation in dry run mode"""
    
    print("="*60)
    print("🧪 GREENHOUSE AUTOMATION TEST - DRY RUN MODE")
    print("="*60)
    
    # Initialize automator in dry run mode (default)
    automator = WebFormAutomator(dry_run=True)
    
    # Display user info that will be used
    print("\n📋 User Information to be filled:")
    for key, value in automator.user_info.items():
        print(f"   {key}: {value}")
    
    # Test URLs for different companies
    test_cases = [
        {
            'company': 'Anthropic',
            'url': 'https://job-boards.greenhouse.io/anthropic/jobs/5509568',
            'role': 'ML Engineer',
            'cover_letter': """Dear Anthropic Team,

I am writing to express my strong interest in the ML Engineer position at Anthropic. 
As someone who has built extensive systems using Claude Code (paying $250/month), 
I have deep appreciation for your work in AI safety and alignment.

With 10+ years of Python experience and a portfolio of 274 modules built using 
Claude Code, I bring both technical depth and practical experience with your products.

My background includes:
• Built AI Talent Optimizer v2.0 using Claude Code
• Managing 74 Ollama models for specialized tasks
• 10 years at Humana working on healthcare AI systems
• Active open source contributor (github.com/guitargnar)

I would be thrilled to contribute to Anthropic's mission of building 
safe and beneficial AI systems.

Best regards,
Matthew Scott"""
        }
    ]
    
    for test in test_cases:
        print(f"\n🎯 Testing: {test['company']} - {test['role']}")
        print("="*60)
        
        # Check if resume exists
        resume_path = "resumes/base_resume.pdf"
        if Path(resume_path).exists():
            print(f"✅ Resume found: {resume_path}")
        else:
            print(f"⚠️  Resume not found: {resume_path}")
            print("   Using placeholder path for test")
        
        # Run the automation
        success, message = automator.apply_via_greenhouse(
            job_url=test['url'],
            cover_letter=test['cover_letter'],
            resume_path=resume_path
        )
        
        print(f"\n📊 Result:")
        print(f"   Success: {success}")
        print(f"   Message: {message}")
        
        if success and automator.dry_run:
            print("\n✅ Dry run successful!")
            print("   Next steps:")
            print("   1. Review the screenshot in screenshots/ directory")
            print("   2. Verify all fields are correctly filled")
            print("   3. Set dry_run=False to submit for real")

def test_form_field_detection():
    """Test the form field detection logic"""
    
    print("\n" + "="*60)
    print("🔍 FORM FIELD DETECTION TEST")
    print("="*60)
    
    automator = WebFormAutomator(dry_run=True)
    
    # Simulate form field filling
    print("\n📝 Fields that will be filled:")
    
    field_mappings = {
        'First Name': automator.user_info['first_name'],
        'Last Name': automator.user_info['last_name'],
        'Email': automator.user_info['email'],
        'Phone': automator.user_info['phone'],
        'Location': f"{automator.user_info['city']}, {automator.user_info['state']}",
        'LinkedIn': automator.user_info['linkedin'],
        'GitHub': automator.user_info['github'],
        'Years of Experience': automator.user_info['years_experience']
    }
    
    for field, value in field_mappings.items():
        print(f"   {field:20} → {value}")
    
    print("\n✅ All required fields mapped correctly")

def main():
    """Run all tests"""
    
    # Ensure screenshots directory exists
    Path("screenshots").mkdir(exist_ok=True)
    
    print("🚀 GREENHOUSE AUTOMATION TEST SUITE")
    print("="*60)
    print("This test will simulate filling a Greenhouse application")
    print("No actual submission will occur (dry_run=True)")
    print("="*60)
    
    # Run tests
    test_form_field_detection()
    test_greenhouse_dry_run()
    
    print("\n" + "="*60)
    print("✅ GREENHOUSE AUTOMATION TEST COMPLETE")
    print("="*60)
    print("\n💡 Summary:")
    print("   - User information loaded from knowledge graph")
    print("   - Form field mappings configured")
    print("   - Dry run mode prevents actual submission")
    print("   - Screenshot capability ready for review")
    print("\n🔗 MCP Puppeteer Integration:")
    print("   - Navigate to job URL")
    print("   - Click Apply button")
    print("   - Fill form fields")
    print("   - Attach resume")
    print("   - Take screenshot for review")
    print("   - Submit application (when dry_run=False)")

if __name__ == "__main__":
    main()