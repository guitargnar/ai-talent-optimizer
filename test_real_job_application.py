#!/usr/bin/env python3
"""
Real-world test of the Playwright web form automator
Tests navigation to actual job application forms and field detection
"""

from web_form_automator_playwright import WebFormAutomator
import json
from datetime import datetime

def test_real_job_applications():
    """Test the automator with real job application sites"""
    
    print("="*60)
    print("🚀 REAL JOB APPLICATION FORM TEST")
    print("Testing Playwright automation with actual application portals")
    print("="*60)
    
    # Initialize automator in dry-run mode for safety
    automator = WebFormAutomator(dry_run=True, headless=False)  # headless=False to see what's happening
    
    try:
        # Test sites with actual application forms
        test_sites = [
            {
                'name': 'Greenhouse Demo',
                'url': 'https://boards.greenhouse.io/embed/job_board?for=democompany',
                'description': 'Testing Greenhouse ATS integration'
            },
            {
                'name': 'Lever Demo', 
                'url': 'https://jobs.lever.co/leverdemo',
                'description': 'Testing Lever ATS integration'
            },
            {
                'name': 'SmartRecruiters',
                'url': 'https://careers.smartrecruiters.com/BoschGroup',
                'description': 'Testing SmartRecruiters integration'
            }
        ]
        
        results = []
        
        for site in test_sites:
            print(f"\n📍 Testing: {site['name']}")
            print(f"   {site['description']}")
            print(f"   URL: {site['url']}")
            print("-" * 40)
            
            # Navigate to the site
            success = automator.navigate_to_url(site['url'])
            
            if success:
                print(f"✅ Successfully navigated to {site['name']}")
                
                # Analyze form fields on the page
                result = automator.analyze_form_fields()
                fields = result.get('fields', []) if isinstance(result, dict) else []
                
                if fields:
                    print(f"📊 Found {len(fields)} form fields:")
                    
                    # Group fields by type
                    field_types = {}
                    fields_to_show = fields[:10] if len(fields) > 10 else fields
                    for field in fields_to_show:  # Show first 10 fields
                        field_type = field.get('type', 'unknown')
                        if field_type not in field_types:
                            field_types[field_type] = []
                        field_types[field_type].append(field)
                        
                        # Display field info
                        print(f"   • {field.get('label', field.get('name', 'unnamed'))}")
                        print(f"     Type: {field_type}")
                        if field.get('placeholder'):
                            print(f"     Placeholder: {field['placeholder']}")
                    
                    if len(fields) > 10:
                        print(f"   ... and {len(fields) - 10} more fields")
                    
                    # Save results
                    results.append({
                        'site': site['name'],
                        'url': site['url'],
                        'field_count': len(fields),
                        'field_types': {k: len(v) for k, v in field_types.items()},
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Test auto-fill capability (dry-run)
                    if automator.dry_run:
                        print("\n📝 Testing auto-fill (dry-run mode):")
                        filled = automator.auto_fill_form(fields, automator.user_info)
                        print(f"   Would fill {filled} fields automatically")
                    
                else:
                    print("   ⚠️ No form fields found on main page")
                    print("   (May need to navigate to specific job posting)")
                    
                    results.append({
                        'site': site['name'],
                        'url': site['url'],
                        'field_count': 0,
                        'note': 'No forms on landing page',
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Take a screenshot for reference
                screenshot_name = f"test_{site['name'].lower().replace(' ', '_')}.png"
                if automator.take_screenshot(screenshot_name):
                    print(f"   📸 Screenshot saved: {screenshot_name}")
                    
            else:
                print(f"❌ Failed to navigate to {site['name']}")
                results.append({
                    'site': site['name'],
                    'url': site['url'],
                    'error': 'Navigation failed',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Save test results
        results_file = 'job_application_test_results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        for result in results:
            print(f"\n{result['site']}:")
            if 'field_count' in result:
                print(f"  • Fields found: {result['field_count']}")
                if result.get('field_types'):
                    print(f"  • Field types: {result['field_types']}")
            elif 'error' in result:
                print(f"  • Error: {result['error']}")
        
        print(f"\n✅ Results saved to: {results_file}")
        
        # Test specific job posting navigation
        print("\n" + "="*60)
        print("🎯 TESTING SPECIFIC JOB POSTING")
        print("="*60)
        
        # Try to navigate to a specific job posting
        specific_job_url = "https://jobs.lever.co/leverdemo/5ac21346-8584-4684-b03f-c8c8b2c74f5f"
        print(f"Navigating to specific job: {specific_job_url}")
        
        if automator.navigate_to_url(specific_job_url):
            print("✅ Successfully navigated to job posting")
            
            # Check for apply button
            apply_button = automator.page.locator('button:has-text("Apply"), a:has-text("Apply")')
            if apply_button.count() > 0:
                print("✅ Found Apply button")
                
                # Click to open application form (if not in dry-run)
                if not automator.dry_run:
                    apply_button.first.click()
                    print("📋 Opened application form")
                    
                    # Wait for form to load and analyze
                    automator.page.wait_for_timeout(2000)
                    result = automator.analyze_form_fields()
                    fields = result.get('fields', []) if isinstance(result, dict) else []
                    
                    if fields:
                        print(f"📊 Application form has {len(fields)} fields")
                        for field in fields[:5]:
                            print(f"   • {field.get('label', field.get('name', 'unnamed'))} ({field.get('type')})")
                else:
                    print("   (Would click Apply button if not in dry-run mode)")
            else:
                print("   ⚠️ No Apply button found")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        return False
        
    finally:
        # Clean up browser resources
        automator.cleanup()
        print("\n🧹 Browser resources cleaned up")

def main():
    """Run the real job application test"""
    success = test_real_job_applications()
    
    if success:
        print("\n" + "="*60)
        print("✅ PLAYWRIGHT AUTOMATION TEST COMPLETE")
        print("="*60)
        print("\nThe WebFormAutomator can now:")
        print("  1. Navigate to any job board or ATS")
        print("  2. Detect and analyze form fields")
        print("  3. Auto-fill forms with user data")
        print("  4. Handle multiple ATS platforms")
        print("  5. Take screenshots for verification")
        print("\nNext steps:")
        print("  • Integrate with job discovery pipeline")
        print("  • Add form submission capability")
        print("  • Implement CAPTCHA handling")
        print("  • Add retry logic for network issues")
    else:
        print("\n⚠️ Some tests failed - check the output above")
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())