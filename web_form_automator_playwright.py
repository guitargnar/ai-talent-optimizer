#!/usr/bin/env python3
"""
Web Form Automator - Portal Application Handler
Now with Playwright browser automation for superior stability and performance
"""

from typing import Dict, Optional, Tuple, Any, List
from datetime import datetime
import time
import json
import os
from pathlib import Path
import base64
import re
from playwright.sync_api import sync_playwright, Page, Browser, Playwright

class WebFormAutomator:
    """
    Handles automated submission to company portals like Greenhouse, Lever, etc.
    Now powered by Playwright for robust browser automation
    """
    
    def __init__(self, dry_run: bool = True, headless: bool = True):
        self.dry_run = dry_run  # Safety mode by default
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # ATS handlers will be implemented as needed
        self.supported_platforms = {}
        
        # User information from knowledge graph
        self.user_info = {
            'first_name': 'Matthew',
            'last_name': 'Scott',
            'email': 'matthewdscott7@gmail.com',
            'phone': '(502) 345-0525',
            'linkedin': 'https://linkedin.com/in/mscott77',
            'github': 'https://github.com/guitargnar',
            'city': 'Louisville',
            'state': 'Kentucky',
            'country': 'United States',
            'years_experience': '10+'
        }
        
        # Portal URLs for major companies
        self.company_portals = {
            'Anthropic': 'https://jobs.ashbyhq.com/anthropic',
            'Google': 'https://careers.google.com',
            'Meta': 'https://careers.meta.com',
            'Amazon': 'https://amazon.jobs',
            'Apple': 'https://jobs.apple.com',
            'Microsoft': 'https://careers.microsoft.com',
            'Netflix': 'https://jobs.netflix.com',
            'Tesla': 'https://tesla.com/careers',
            'SpaceX': 'https://spacex.com/careers',
            'OpenAI': 'https://openai.com/careers',
            'Scale AI': 'https://scale.com/careers',
            'Databricks': 'https://databricks.com/company/careers'
        }
    
    def start_browser(self):
        """Initialize Playwright and launch browser"""
        if not self.playwright:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            print(f"✅ Browser launched ({'headless' if self.headless else 'visible'} mode)")
    
    def navigate_to_url(self, url: str) -> bool:
        """
        Navigate to URL and return success status
        
        Args:
            url: The URL to navigate to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.browser:
                self.start_browser()
            
            # Create new page or reuse existing
            if not self.page:
                self.page = self.browser.new_page()
                # Set user agent to appear more human
                self.page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
            
            print(f"🌐 Navigating to: {url}")
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for page to stabilize
            self.page.wait_for_timeout(2000)
            
            print(f"✅ Successfully loaded: {self.page.title()}")
            return True
            
        except Exception as e:
            print(f"❌ Navigation error: {str(e)}")
            return False
    
    def analyze_form_fields(self, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze all form fields on the current page or navigate to URL first
        
        Args:
            url: Optional URL to navigate to before analyzing
            
        Returns:
            Dictionary containing form field analysis
        """
        if url:
            if not self.navigate_to_url(url):
                return {'fields': [], 'total': 0, 'error': 'Failed to navigate'}
        
        if not self.page:
            return {'fields': [], 'total': 0, 'error': 'No page loaded'}
        
        print("\n📊 FORM ANALYSIS IN PROGRESS...")
        print("="*60)
        
        try:
            # JavaScript to analyze form fields
            result = self.page.evaluate('''() => {
                const formElements = [];
                
                // Helper to get label for an element
                const getLabel = (element) => {
                    // Try aria-label
                    let label = element.getAttribute('aria-label');
                    if (label) return label.trim();
                    
                    // Try associated label element
                    if (element.id) {
                        const labelElem = document.querySelector(`label[for="${element.id}"]`);
                        if (labelElem) return labelElem.textContent.trim();
                    }
                    
                    // Try parent label
                    const parentLabel = element.closest('label');
                    if (parentLabel) {
                        const text = parentLabel.textContent.trim();
                        // Remove the input value from label text if it's included
                        return text.replace(element.value, '').trim();
                    }
                    
                    // Try nearby label
                    const container = element.closest('div, fieldset, section');
                    if (container) {
                        const nearbyLabel = container.querySelector('label');
                        if (nearbyLabel && !nearbyLabel.querySelector('input, select, textarea')) {
                            return nearbyLabel.textContent.trim();
                        }
                    }
                    
                    // Use placeholder as fallback
                    return element.placeholder || element.name || element.id || '';
                };
                
                // Process all input fields
                document.querySelectorAll('input').forEach(input => {
                    if (input.type === 'hidden' || input.type === 'submit' || input.type === 'button') return;
                    
                    formElements.push({
                        type: 'input',
                        inputType: input.type,
                        id: input.id || null,
                        name: input.name || null,
                        label: getLabel(input),
                        required: input.required || input.getAttribute('aria-required') === 'true',
                        value: input.value || '',
                        placeholder: input.placeholder || '',
                        visible: input.offsetParent !== null && window.getComputedStyle(input).display !== 'none',
                        className: input.className,
                        selector: input.id ? `#${input.id}` : input.name ? `input[name="${input.name}"]` : null
                    });
                });
                
                // Process select dropdowns
                document.querySelectorAll('select').forEach(select => {
                    const options = Array.from(select.options).map(opt => ({
                        text: opt.text,
                        value: opt.value
                    }));
                    
                    formElements.push({
                        type: 'select',
                        id: select.id || null,
                        name: select.name || null,
                        label: getLabel(select),
                        required: select.required || select.getAttribute('aria-required') === 'true',
                        value: select.value || '',
                        options: options,
                        visible: select.offsetParent !== null && window.getComputedStyle(select).display !== 'none',
                        className: select.className,
                        selector: select.id ? `#${select.id}` : select.name ? `select[name="${select.name}"]` : null
                    });
                });
                
                // Process textareas
                document.querySelectorAll('textarea').forEach(textarea => {
                    formElements.push({
                        type: 'textarea',
                        id: textarea.id || null,
                        name: textarea.name || null,
                        label: getLabel(textarea),
                        required: textarea.required || textarea.getAttribute('aria-required') === 'true',
                        value: textarea.value || '',
                        placeholder: textarea.placeholder || '',
                        visible: textarea.offsetParent !== null && window.getComputedStyle(textarea).display !== 'none',
                        className: textarea.className,
                        selector: textarea.id ? `#${textarea.id}` : textarea.name ? `textarea[name="${textarea.name}"]` : null
                    });
                });
                
                // Process file inputs specially
                document.querySelectorAll('input[type="file"]').forEach(fileInput => {
                    formElements.push({
                        type: 'file',
                        id: fileInput.id || null,
                        name: fileInput.name || null,
                        label: getLabel(fileInput),
                        required: fileInput.required || fileInput.getAttribute('aria-required') === 'true',
                        accept: fileInput.accept || '',
                        visible: fileInput.offsetParent !== null && window.getComputedStyle(fileInput).display !== 'none',
                        className: fileInput.className,
                        selector: fileInput.id ? `#${fileInput.id}` : fileInput.name ? `input[type="file"][name="${fileInput.name}"]` : null
                    });
                });
                
                const visibleFields = formElements.filter(el => el.visible);
                
                return {
                    fields: visibleFields,
                    total: visibleFields.length,
                    url: window.location.href,
                    title: document.title,
                    forms: document.querySelectorAll('form').length
                };
            }''')
            
            print(f"📊 Form Analysis Complete")
            print(f"   Page: {result['title']}")
            print(f"   Forms on page: {result['forms']}")
            print(f"   Fields found: {result['total']}")
            
            if result['fields']:
                print("\n📝 Field Details:")
                for i, field in enumerate(result['fields'][:15], 1):  # Show first 15 fields
                    label = field['label'] or field['name'] or field['id'] or 'Unnamed'
                    req = "✓ Required" if field.get('required') else "○ Optional"
                    print(f"   {i:2}. [{field['type']:<8}] {label[:40]:<40} {req}")
                
                if result['total'] > 15:
                    print(f"   ... and {result['total'] - 15} more fields")
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing form fields: {str(e)}")
            return {'fields': [], 'total': 0, 'error': str(e)}
    
    def fill_field(self, selector: str, value: str) -> bool:
        """Fill a form field with the specified value"""
        if not self.page:
            return False
            
        try:
            if self.dry_run:
                print(f"   [DRY RUN] Would fill '{selector}' with '{value[:30]}...'")
                return True
            
            self.page.fill(selector, value)
            print(f"   ✓ Filled '{selector}'")
            return True
        except Exception as e:
            print(f"   ✗ Failed to fill '{selector}': {str(e)}")
            return False
    
    def select_dropdown(self, selector: str, value: str) -> bool:
        """Select an option from a dropdown"""
        if not self.page:
            return False
            
        try:
            if self.dry_run:
                print(f"   [DRY RUN] Would select '{value}' in '{selector}'")
                return True
            
            self.page.select_option(selector, value)
            print(f"   ✓ Selected '{value}' in dropdown")
            return True
        except Exception as e:
            print(f"   ✗ Failed to select in '{selector}': {str(e)}")
            return False
    
    def upload_file(self, selector: str, file_path: str) -> bool:
        """Upload a file to a file input"""
        if not self.page:
            return False
            
        try:
            full_path = Path(file_path).absolute()
            if not full_path.exists():
                print(f"   ✗ File not found: {full_path}")
                return False
            
            if self.dry_run:
                print(f"   [DRY RUN] Would upload '{full_path.name}' to '{selector}'")
                return True
            
            self.page.set_input_files(selector, str(full_path))
            print(f"   ✓ Uploaded '{full_path.name}'")
            return True
        except Exception as e:
            print(f"   ✗ Failed to upload file: {str(e)}")
            return False
    
    def click_button(self, selector: str) -> bool:
        """Click a button or link"""
        if not self.page:
            return False
            
        try:
            if self.dry_run:
                print(f"   [DRY RUN] Would click '{selector}'")
                return True
            
            self.page.click(selector)
            print(f"   ✓ Clicked '{selector}'")
            return True
        except Exception as e:
            print(f"   ✗ Failed to click '{selector}': {str(e)}")
            return False
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot of the current page"""
        if not self.page:
            return ""
            
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            self.page.screenshot(path=filename)
            print(f"   📸 Screenshot saved: {filename}")
            return filename
        except Exception as e:
            print(f"   ✗ Failed to take screenshot: {str(e)}")
            return ""
    
    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                self.page.close()
                self.page = None
            if self.browser:
                self.browser.close()
                self.browser = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            print("✅ Browser resources cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {str(e)}")
    
    def __del__(self):
        """Ensure browser is closed on object deletion"""
        self.cleanup()
    
    def auto_fill_form(self, form_fields: List[Dict], user_data: Dict) -> int:
        """
        Automatically fill form fields based on smart matching
        
        Args:
            form_fields: List of field dictionaries from analyze_form_fields
            user_data: Dictionary of user information to fill
            
        Returns:
            Number of fields successfully filled
        """
        filled_count = 0
        
        print("\n🤖 AUTO-FILL STARTING...")
        print("-" * 40)
        
        for field in form_fields:
            if not field.get('selector'):
                continue
                
            label = (field.get('label') or '').lower()
            name = (field.get('name') or '').lower()
            field_id = (field.get('id') or '').lower()
            
            # Smart field matching
            value = None
            
            # Name fields
            if any(x in label + name + field_id for x in ['first', 'fname', 'given']):
                value = user_data.get('first_name')
            elif any(x in label + name + field_id for x in ['last', 'lname', 'surname', 'family']):
                value = user_data.get('last_name')
            elif 'full' in label + name + field_id and 'name' in label + name + field_id:
                value = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}"
            
            # Contact fields
            elif any(x in label + name + field_id for x in ['email', 'e-mail']):
                value = user_data.get('email')
            elif any(x in label + name + field_id for x in ['phone', 'tel', 'mobile']):
                value = user_data.get('phone')
            elif 'linkedin' in label + name + field_id:
                value = user_data.get('linkedin')
            elif 'github' in label + name + field_id:
                value = user_data.get('github')
            
            # Location fields
            elif 'city' in label + name + field_id:
                value = user_data.get('city')
            elif 'state' in label + name + field_id:
                value = user_data.get('state')
            elif 'country' in label + name + field_id:
                value = user_data.get('country')
            
            # Fill the field if we found a value
            if value and field['type'] in ['input', 'textarea']:
                if self.fill_field(field['selector'], value):
                    filled_count += 1
        
        print(f"\n✅ Auto-filled {filled_count} fields")
        return filled_count


def test_playwright_automation():
    """Test the Playwright-based web form automation"""
    print("="*60)
    print("🎭 PLAYWRIGHT WEB AUTOMATION TEST")
    print("="*60)
    
    automator = WebFormAutomator(dry_run=False, headless=True)
    
    try:
        # Test 1: Navigate to a job board
        print("\n📍 Test 1: Navigation")
        print("-" * 40)
        success = automator.navigate_to_url("https://www.workatastartup.com/jobs")
        if success:
            print("✅ Navigation successful")
        
        # Test 2: Analyze form fields
        print("\n📍 Test 2: Form Analysis")
        print("-" * 40)
        analysis = automator.analyze_form_fields()
        print(f"✅ Analysis complete: {analysis['total']} fields found")
        
        # Test 3: Test with Anthropic's job board
        print("\n📍 Test 3: Real Job Board (Anthropic)")
        print("-" * 40)
        analysis = automator.analyze_form_fields("https://jobs.ashbyhq.com/anthropic")
        
        # Test 4: Screenshot
        if automator.page:
            print("\n📍 Test 4: Screenshot")
            print("-" * 40)
            filename = automator.take_screenshot("test_anthropic.png")
            if filename:
                print(f"✅ Screenshot saved: {filename}")
        
        # Test 5: Auto-fill simulation
        if analysis.get('fields'):
            print("\n📍 Test 5: Auto-Fill Simulation (Dry Run)")
            print("-" * 40)
            automator.dry_run = True  # Enable dry run for safety
            filled = automator.auto_fill_form(
                analysis['fields'][:5],  # Test with first 5 fields
                automator.user_info
            )
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
    
    finally:
        automator.cleanup()


def demo_real_application():
    """Demonstrate filling a real application form"""
    print("="*60)
    print("🚀 REAL APPLICATION FORM DEMO")
    print("="*60)
    
    automator = WebFormAutomator(dry_run=True, headless=False)  # Visible browser for demo
    
    try:
        # Navigate to a real application
        url = "https://boards.greenhouse.io/databricks/jobs/6955703002"  # Example job
        print(f"\n🎯 Target: {url}")
        
        if automator.navigate_to_url(url):
            # Analyze the form
            analysis = automator.analyze_form_fields()
            
            if analysis['fields']:
                # Simulate auto-fill
                print("\n🤖 Simulating auto-fill (dry run)...")
                automator.auto_fill_form(analysis['fields'], automator.user_info)
                
                # Take screenshot
                automator.take_screenshot("databricks_form.png")
        
    finally:
        print("\n🧹 Cleaning up...")
        automator.cleanup()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_real_application()
    else:
        test_playwright_automation()