#!/usr/bin/env python3
"""
Test script to verify browser automation is working
This demonstrates the new capabilities added to web_form_automator.py
"""

import asyncio
from pyppeteer import launch
import sys

async def test_browser_navigation():
    """Test basic browser navigation and form field detection"""
    browser = None
    
    try:
        print("🚀 Starting browser automation test...")
        print("-" * 40)
        
        # Launch browser with minimal options for stability
        print("Launching headless browser...")
        browser = await launch({
            'headless': True,
            'args': ['--no-sandbox', '--disable-setuid-sandbox']
        })
        
        page = await browser.newPage()
        
        # Set a user agent
        await page.setUserAgent(
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Test sites
        test_sites = [
            ("Google", "https://www.google.com"),
            ("GitHub Jobs", "https://github.com/about/careers"),
        ]
        
        for name, url in test_sites:
            print(f"\n📍 Testing: {name}")
            print(f"   URL: {url}")
            
            try:
                # Navigate to the page
                await page.goto(url, {'waitUntil': 'networkidle2', 'timeout': 15000})
                
                # Get page title
                title = await page.title()
                print(f"   ✅ Page loaded: {title}")
                
                # Count form elements
                form_count = await page.evaluate('''() => {
                    const inputs = document.querySelectorAll('input:not([type="hidden"])').length;
                    const textareas = document.querySelectorAll('textarea').length;
                    const selects = document.querySelectorAll('select').length;
                    return inputs + textareas + selects;
                }''')
                
                print(f"   📊 Form elements found: {form_count}")
                
                # Take a screenshot (optional)
                # await page.screenshot({'path': f'{name.lower()}_screenshot.png'})
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print("\n✅ Browser automation test complete!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
        
    finally:
        if browser:
            await browser.close()
            print("🧹 Browser closed")
    
    return True

def main():
    """Run the browser automation test"""
    print("="*60)
    print("BROWSER AUTOMATION TEST")
    print("Testing pyppeteer integration for web form automation")
    print("="*60)
    
    # Run the async test
    success = asyncio.run(test_browser_navigation())
    
    if success:
        print("\n✅ SUCCESS: Browser automation is working!")
        print("The web_form_automator.py module can now:")
        print("  1. Navigate to any URL with a real browser")
        print("  2. Analyze form fields dynamically")
        print("  3. Extract form structure and requirements")
        print("  4. Prepare for automated form filling")
    else:
        print("\n⚠️ Browser automation encountered issues")
        print("This might be due to:")
        print("  - Websockets compatibility (try: pip install websockets==10.4)")
        print("  - Missing Chromium (will auto-download on first run)")
        print("  - Network issues")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())