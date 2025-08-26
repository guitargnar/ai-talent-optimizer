#!/usr/bin/env python3
"""
LinkedIn Easy Apply Automation System
Automates applying to jobs with Easy Apply feature via direct links
Uses Selenium for browser automation with safety controls
"""

import json
import sqlite3
import time
import random
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import hashlib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_easy_apply.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LinkedInEasyApplyBot:
    """Automates LinkedIn Easy Apply job applications"""
    
    def __init__(self, headless: bool = False):
        """Initialize the automation bot
        
        Args:
            headless: Run browser in headless mode (no UI)
        """
        self.driver = None
        self.wait = None
        self.headless = headless
        self.logged_in = False
        
        # Load configuration
        self.config_path = Path('linkedin_config.json')
        self.config = self._load_config()
        
        # Database setup
        self.db_path = Path("unified_platform.db")
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Application tracking
        self.applications_submitted = 0
        self.applications_failed = 0
        self.session_start = datetime.now()
        
        # Rate limiting
        self.min_delay = 3  # Minimum seconds between actions
        self.max_delay = 7  # Maximum seconds between actions
        self.applications_per_session = 10  # Safety limit
        
    def _load_config(self) -> Dict:
        """Load or create configuration file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Create default config
        default_config = {
            "linkedin_email": "",
            "linkedin_password": "",
            "profile": {
                "phone": "(502) 345-0525",
                "email": "matthewdscott7@gmail.com",
                "linkedin_url": "linkedin.com/in/mscott77",
                "current_company": "Humana",
                "years_experience": "10",
                "degree": "Self-Directed Learning",
                "school": "Independent Study",
                "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "AI"]
            },
            "resume_path": "/Users/matthewscott/Desktop/MATTHEW_SCOTT_AI_ML_ENGINEER_2025.pdf",
            "cover_letter_template": "I am excited about this opportunity...",
            "auto_submit": False,  # Safety: require confirmation before submitting
            "max_applications_per_day": 50
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"Created config file at {self.config_path}")
        logger.info("Please update linkedin_email and linkedin_password before running")
        
        return default_config
    
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        options = Options()
        
        # Essential options for automation
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to appear more human
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Additional options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        if self.headless:
            options.add_argument('--headless')
        
        # Create driver
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Execute script to prevent detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("Chrome driver initialized successfully")
    
    def login_to_linkedin(self) -> bool:
        """Login to LinkedIn account"""
        if not self.config['linkedin_email'] or not self.config['linkedin_password']:
            logger.error("LinkedIn credentials not configured in linkedin_config.json")
            return False
        
        try:
            logger.info("Navigating to LinkedIn login page...")
            self.driver.get('https://www.linkedin.com/login')
            self._random_delay()
            
            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(self.config['linkedin_email'])
            self._random_delay(1, 2)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.config['linkedin_password'])
            self._random_delay(1, 2)
            
            # Click sign in
            sign_in_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            sign_in_button.click()
            
            # Wait for login to complete
            self._random_delay(3, 5)
            
            # Check if logged in successfully
            if "feed" in self.driver.current_url or "linkedin.com/in/" in self.driver.current_url:
                logger.info("Successfully logged in to LinkedIn")
                self.logged_in = True
                return True
            else:
                logger.error("Login may have failed - please check manually")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def _random_delay(self, min_sec: float = None, max_sec: float = None):
        """Add random delay to simulate human behavior"""
        min_sec = min_sec or self.min_delay
        max_sec = max_sec or self.max_delay
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def is_easy_apply_job(self, job_url: str) -> bool:
        """Check if a job has Easy Apply option"""
        try:
            self.driver.get(job_url)
            self._random_delay()
            
            # Look for Easy Apply button
            easy_apply_button = self.driver.find_elements(
                By.XPATH, 
                "//button[contains(@class, 'jobs-apply-button') and contains(., 'Easy Apply')]"
            )
            
            return len(easy_apply_button) > 0
            
        except Exception as e:
            logger.error(f"Error checking Easy Apply status: {str(e)}")
            return False
    
    def extract_job_details(self, job_url: str) -> Dict:
        """Extract job details from LinkedIn job page"""
        try:
            self.driver.get(job_url)
            self._random_delay()
            
            # Extract job information
            job_details = {
                'url': job_url,
                'job_id': self._extract_job_id(job_url),
                'company': '',
                'position': '',
                'location': '',
                'description': '',
                'posted_date': datetime.now().isoformat()
            }
            
            # Get company name
            try:
                company_elem = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "a[data-tracking-control-full_name='public_jobs_topcard-org-name']"
                )
                job_details['company'] = company_elem.text.strip()
            except:
                pass
            
            # Get position title
            try:
                position_elem = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "h1.top-card-layout__title"
                )
                job_details['position'] = position_elem.text.strip()
            except:
                pass
            
            # Get location
            try:
                location_elem = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "span.topcard__flavor--bullet"
                )
                job_details['location'] = location_elem.text.strip()
            except:
                pass
            
            # Get description
            try:
                description_elem = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "div.show-more-less-html__markup"
                )
                job_details['description'] = description_elem.text.strip()[:500]  # First 500 chars
            except:
                pass
            
            return job_details
            
        except Exception as e:
            logger.error(f"Error extracting job details: {str(e)}")
            return {}
    
    def _extract_job_id(self, url: str) -> str:
        """Extract job ID from LinkedIn URL"""
        # LinkedIn job URLs typically have the job ID in the path
        # Example: https://www.linkedin.com/jobs/view/1234567890
        parts = url.split('/')
        for i, part in enumerate(parts):
            if part == 'view' and i + 1 < len(parts):
                return parts[i + 1].split('?')[0]
        
        # Fallback: create hash from URL
        return hashlib.md5(url.encode()).hexdigest()[:10]
    
    def fill_easy_apply_form(self) -> bool:
        """Fill out the Easy Apply form"""
        try:
            # Click Easy Apply button
            easy_apply_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'jobs-apply-button') and contains(., 'Easy Apply')]")
                )
            )
            easy_apply_button.click()
            self._random_delay()
            
            # Handle multi-page application
            while True:
                # Fill current page
                self._fill_current_page()
                
                # Look for Next or Submit button
                next_button = self.driver.find_elements(
                    By.XPATH, 
                    "//button[@aria-label='Continue to next step']"
                )
                
                submit_button = self.driver.find_elements(
                    By.XPATH,
                    "//button[@aria-label='Submit application']"
                )
                
                review_button = self.driver.find_elements(
                    By.XPATH,
                    "//button[@aria-label='Review your application']"
                )
                
                if submit_button:
                    # Final submission
                    if self.config.get('auto_submit', False):
                        logger.info("Submitting application...")
                        submit_button[0].click()
                        self._random_delay(2, 4)
                        return True
                    else:
                        logger.info("Application ready for review (auto_submit disabled)")
                        return False
                        
                elif review_button:
                    # Review step
                    review_button[0].click()
                    self._random_delay()
                    
                elif next_button:
                    # Continue to next page
                    next_button[0].click()
                    self._random_delay()
                else:
                    # No more buttons found
                    break
            
            return True
            
        except TimeoutException:
            logger.error("Timeout while filling application form")
            return False
        except Exception as e:
            logger.error(f"Error filling application: {str(e)}")
            return False
    
    def _fill_current_page(self):
        """Fill fields on current application page"""
        try:
            # Phone number
            phone_inputs = self.driver.find_elements(
                By.XPATH, 
                "//input[@type='tel' or contains(@id, 'phone')]"
            )
            for input_elem in phone_inputs:
                if not input_elem.get_attribute('value'):
                    input_elem.clear()
                    input_elem.send_keys(self.config['profile']['phone'])
                    self._random_delay(0.5, 1)
            
            # Email (usually pre-filled)
            email_inputs = self.driver.find_elements(
                By.XPATH,
                "//input[@type='email' or contains(@id, 'email')]"
            )
            for input_elem in email_inputs:
                if not input_elem.get_attribute('value'):
                    input_elem.clear()
                    input_elem.send_keys(self.config['profile']['email'])
                    self._random_delay(0.5, 1)
            
            # Years of experience
            experience_inputs = self.driver.find_elements(
                By.XPATH,
                "//input[contains(@id, 'experience') or contains(@full_name, 'experience')]"
            )
            for input_elem in experience_inputs:
                if not input_elem.get_attribute('value'):
                    input_elem.clear()
                    input_elem.send_keys(self.config['profile']['years_experience'])
                    self._random_delay(0.5, 1)
            
            # Handle dropdowns
            self._handle_dropdowns()
            
            # Handle radio buttons (usually Yes/No questions)
            self._handle_radio_buttons()
            
            # Upload resume if needed
            self._upload_resume()
            
        except Exception as e:
            logger.warning(f"Error filling current page: {str(e)}")
    
    def _handle_dropdowns(self):
        """Handle dropdown selections"""
        try:
            dropdowns = self.driver.find_elements(By.TAG_NAME, "select")
            
            for dropdown in dropdowns:
                try:
                    select = Select(dropdown)
                    # Select first non-empty option
                    options = select.options
                    if len(options) > 1:
                        select.select_by_index(1)
                        self._random_delay(0.5, 1)
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"Error handling dropdowns: {str(e)}")
    
    def _handle_radio_buttons(self):
        """Handle radio button selections (default to Yes)"""
        try:
            # Find all radio button groups
            radio_groups = self.driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'jobs-easy-apply-form-section__grouping')]"
            )
            
            for group in radio_groups:
                # Check if it's a Yes/No question
                labels = group.find_elements(By.TAG_NAME, "label")
                for label in labels:
                    if "Yes" in label.text:
                        radio = label.find_element(By.TAG_NAME, "input")
                        if not radio.is_selected():
                            radio.click()
                            self._random_delay(0.5, 1)
                        break
                        
        except Exception as e:
            logger.debug(f"Error handling radio buttons: {str(e)}")
    
    def _upload_resume(self):
        """Upload resume if file input is present"""
        try:
            file_inputs = self.driver.find_elements(
                By.XPATH,
                "//input[@type='file']"
            )
            
            for file_input in file_inputs:
                if file_input.is_displayed():
                    resume_version = self.config.get('resume_path', '')
                    if resume_path and Path(resume_version).exists():
                        file_input.send_keys(resume_version)
                        logger.info("Resume uploaded")
                        self._random_delay(1, 2)
                        
        except Exception as e:
            logger.debug(f"Error uploading resume: {str(e)}")
    
    def apply_to_job(self, job_url: str) -> bool:
        """Apply to a single job via Easy Apply"""
        try:
            # Check application limit
            if self.applications_submitted >= self.applications_per_session:
                logger.warning(f"Reached session limit of {self.applications_per_session} applications")
                return False
            
            logger.info(f"Processing job: {job_url}")
            
            # Extract job details
            job_details = self.extract_job_details(job_url)
            if not job_details:
                logger.error("Could not extract job details")
                return False
            
            logger.info(f"Job: {job_details.get('position', 'Unknown')} at {job_details.get('company', 'Unknown')}")
            
            # Check if Easy Apply is available
            if not self.is_easy_apply_job(job_url):
                logger.info("Not an Easy Apply job - skipping")
                self._record_application(job_details, status='not_easy_apply')
                return False
            
            # Check if already applied
            if self._already_applied(job_details.get('job_id', '')):
                logger.info("Already applied to this job - skipping")
                return False
            
            # Fill and submit application
            success = self.fill_easy_apply_form()
            
            if success:
                logger.info(f"✅ Successfully applied to {job_details.get('company', 'Unknown')}")
                self.applications_submitted += 1
                self._record_application(job_details, status='submitted')
            else:
                logger.warning(f"⚠️ Application prepared but not submitted (review required)")
                self.applications_failed += 1
                self._record_application(job_details, status='prepared')
            
            return success
            
        except Exception as e:
            logger.error(f"Error applying to job: {str(e)}")
            self.applications_failed += 1
            return False
    
    def _already_applied(self, job_id: str) -> bool:
        """Check if already applied to this job"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM jobs 
                WHERE job_id = ? AND applied = 1
            """, (job_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return False
    
    def _record_application(self, job_details: Dict, status: str):
        """Record application in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or update job record
            cursor.execute("""
                INSERT OR REPLACE INTO linkedin_jobs (
                    job_id, company, title, location, url, 
                    description, applied, applied_date, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_details.get('job_id', ''),
                job_details.get('company', ''),
                job_details.get('position', ''),
                job_details.get('location', ''),
                job_details.get('url', ''),
                job_details.get('description', ''),
                1 if status == 'submitted' else 0,
                datetime.now().isoformat() if status == 'submitted' else None,
                'easy_apply'
            ))
            
            # Add to application tracking
            cursor.execute("""
                INSERT INTO applications (
                    company, title, job_id, method,
                    application_status, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                job_details.get('company', ''),
                job_details.get('position', ''),
                job_details.get('job_id', ''),
                'linkedin_easy_apply',
                status,
                f"Applied via Easy Apply automation on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error recording application: {str(e)}")
    
    def apply_to_multiple_jobs(self, job_urls: List[str]):
        """Apply to multiple jobs from a list of URLs"""
        logger.info(f"Starting batch application for {len(job_urls)} jobs")
        
        # Setup and login
        if not self.driver:
            self.setup_driver()
        
        if not self.logged_in:
            if not self.login_to_linkedin():
                logger.error("Failed to login - aborting")
                return
        
        # Process each job
        for i, job_url in enumerate(job_urls, 1):
            logger.info(f"\nProcessing job {i}/{len(job_urls)}")
            
            try:
                self.apply_to_job(job_url)
                
                # Rate limiting between applications
                if i < len(job_urls):
                    delay = random.uniform(30, 60)  # 30-60 seconds between applications
                    logger.info(f"Waiting {delay:.0f} seconds before next application...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error processing job: {str(e)}")
                continue
        
        # Summary
        self._print_summary()
    
    def _print_summary(self):
        """Print session summary"""
        duration = datetime.now() - self.session_start
        
        logger.info("\n" + "="*60)
        logger.info("SESSION SUMMARY")
        logger.info("="*60)
        logger.info(f"Duration: {duration}")
        logger.info(f"Applications submitted: {self.applications_submitted}")
        logger.info(f"Applications failed: {self.applications_failed}")
        logger.info(f"Success rate: {self.applications_submitted / max(1, self.applications_submitted + self.applications_failed) * 100:.1f}%")
        logger.info("="*60)
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


def main():
    """Main function for testing"""
    # Example job URLs - replace with actual LinkedIn job URLs
    job_urls = [
        # Add LinkedIn job URLs here
        # "https://www.linkedin.com/jobs/view/1234567890",
    ]
    
    # Check if URLs provided
    if not job_urls:
        print("\n⚠️ No job URLs provided!")
        print("\nTo use this script:")
        print("1. Update linkedin_config.json with your credentials")
        print("2. Add LinkedIn job URLs to the job_urls list in main()")
        print("3. Run the script again")
        return
    
    # Initialize bot
    bot = LinkedInEasyApplyBot(headless=False)  # Set to True for headless mode
    
    try:
        # Apply to jobs
        bot.apply_to_multiple_jobs(job_urls)
        
    finally:
        # Cleanup
        bot.cleanup()


if __name__ == "__main__":
    main()