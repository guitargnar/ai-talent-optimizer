#!/usr/bin/env python3
"""
Test Full Automation Pipeline
Verifies all components work together
"""

import sys
from pathlib import Path
import logging

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.job_discovery import EnhancedJobDiscovery
from src.services.email_validator import EmailValidator
from src.services.resume_generator import ResumeGenerator
from src.services.email_composer import EmailComposer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_full_pipeline():
    """Test the complete automation pipeline"""
    
    print("\n" + "="*60)
    print("🚀 TESTING FULL AUTOMATION PIPELINE")
    print("="*60)
    
    results = {
        'job_discovery': False,
        'email_validation': False,
        'resume_generation': False,
        'email_composition': False
    }
    
    # Test 1: Job Discovery
    print("\n📍 Testing Job Discovery...")
    try:
        discovery = EnhancedJobDiscovery()
        # Just test with one source for speed
        jobs = discovery.scrape_adzuna_jobs(max_results=5)
        if jobs:
            print(f"✅ Job Discovery: Found {len(jobs)} jobs")
            results['job_discovery'] = True
        else:
            print("❌ Job Discovery: No jobs found")
    except Exception as e:
        print(f"❌ Job Discovery Error: {e}")
    
    # Test 2: Email Validation
    print("\n📍 Testing Email Validation...")
    try:
        validator = EmailValidator()
        test_emails = [
            {'email': 'careers@anthropic.com', 'company': 'Anthropic'},
            {'email': 'invalid@fake123456.com', 'company': 'Fake Company'}
        ]
        validation_results = validator.validate_batch(test_emails)
        
        valid_count = sum(1 for r in validation_results.values() if r['valid'])
        print(f"✅ Email Validation: {valid_count}/{len(test_emails)} valid")
        results['email_validation'] = True
    except Exception as e:
        print(f"❌ Email Validation Error: {e}")
    
    # Test 3: Resume Generation
    print("\n📍 Testing Resume Generation...")
    try:
        generator = ResumeGenerator()
        resume_path = generator.generate_resume_variant('ai_ml_engineer', 'Test Company')
        if Path(resume_path).exists():
            print(f"✅ Resume Generation: Created {Path(resume_path).name}")
            results['resume_generation'] = True
        else:
            print("❌ Resume Generation: File not created")
    except Exception as e:
        print(f"❌ Resume Generation Error: {e}")
    
    # Test 4: Email Composition
    print("\n📍 Testing Email Composition...")
    try:
        composer = EmailComposer()
        job_data = {
            'company': 'Test Company',
            'position': 'Senior AI Engineer',
            'company_email': 'careers@testcompany.com'
        }
        email = composer.compose_email(job_data)
        
        if email['subject'] and email['body']:
            print(f"✅ Email Composition: Generated email with {len(email['body'])} chars")
            print(f"   Subject: {email['subject'][:50]}...")
            results['email_composition'] = True
        else:
            print("❌ Email Composition: Empty email generated")
    except Exception as e:
        print(f"❌ Email Composition Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 PIPELINE TEST RESULTS")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {component.replace('_', ' ').title()}: {'PASSED' if status else 'FAILED'}")
    
    print(f"\nOverall: {passed}/{total} components working")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS GO! Ready for production use.")
        print("\nNext steps:")
        print("1. Run: python automated_apply.py")
        print("2. Monitor: tail -f logs/evening_run_*.log")
        print("3. Check: python main.py status")
    else:
        print("\n⚠️ Some components need attention before launch.")
        print("Review the errors above and fix before running automation.")
    
    return passed == total

if __name__ == "__main__":
    success = test_full_pipeline()
    sys.exit(0 if success else 1)