#!/usr/bin/env python3
"""
LinkedIn Job URL Processor
Processes LinkedIn job URLs from various sources and manages Easy Apply automation
"""

import json
import sqlite3
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import sys

# Import the Easy Apply bot
from linkedin_easy_apply_automation import LinkedInEasyApplyBot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinkedInJobProcessor:
    """Process and manage LinkedIn job URLs for Easy Apply automation"""
    
    def __init__(self):
        self.db_path = Path("unified_platform.db")
        self.job_urls_file = Path('linkedin_job_urls.txt')
        self.processed_urls_file = Path('processed_linkedin_urls.json')
        
        # Load processed URLs history
        self.processed_urls = self._load_processed_urls()
        
    def _load_processed_urls(self) -> Dict:
        """Load history of processed URLs"""
        if self.processed_urls_file.exists():
            with open(self.processed_urls_file, 'r') as f:
                return json.load(f)
        return {"processed": [], "failed": [], "skipped": []}
    
    def _save_processed_urls(self):
        """Save processed URLs history"""
        with open(self.processed_urls_file, 'w') as f:
            json.dump(self.processed_urls, f, indent=2)
    
    def validate_linkedin_url(self, url: str) -> bool:
        """Validate if URL is a valid LinkedIn job URL"""
        patterns = [
            r'linkedin\.com/jobs/view/\d+',
            r'linkedin\.com/jobs/collections/',
            r'linkedin\.com/jobs/search'
        ]
        
        for pattern in patterns:
            if re.search(pattern, url):
                return True
        return False
    
    def extract_job_id_from_url(self, url: str) -> Optional[str]:
        """Extract job ID from LinkedIn URL"""
        # Pattern: /jobs/view/{job_id}
        match = re.search(r'/jobs/view/(\d+)', url)
        if match:
            return match.group(1)
        
        # Pattern: currentJobId={job_id} in query params
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'currentJobId' in params:
            return params['currentJobId'][0]
        
        return None
    
    def load_urls_from_file(self, file_path: Optional[Path] = None) -> List[str]:
        """Load LinkedIn job URLs from a text file"""
        file_path = file_path or self.job_urls_file
        
        if not file_path.exists():
            # Create sample file
            sample_content = """# LinkedIn Job URLs - One per line
# Lines starting with # are comments
# Example URLs:
# https://www.linkedin.com/jobs/view/1234567890
# https://www.linkedin.com/jobs/view/0987654321

# Add your LinkedIn job URLs below:
"""
            with open(file_path, 'w') as f:
                f.write(sample_content)
            logger.info(f"Created sample file at {file_path}")
            return []
        
        urls = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    if self.validate_linkedin_url(line):
                        urls.append(line)
                    else:
                        logger.warning(f"Invalid LinkedIn URL: {line}")
        
        return urls
    
    def load_urls_from_database(self, only_easy_apply: bool = True) -> List[str]:
        """Load LinkedIn job URLs from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT url FROM jobs 
            WHERE applied = 0 
            AND url IS NOT NULL 
            AND url != ''
        """
        
        if only_easy_apply:
            query += " AND (description LIKE '%Easy Apply%' OR description LIKE '%easy apply%')"
        
        query += " ORDER BY discovered_date DESC LIMIT 50"
        
        cursor.execute(query)
        urls = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return urls
    
    def filter_new_urls(self, urls: List[str]) -> List[str]:
        """Filter out already processed URLs"""
        all_processed = set(
            self.processed_urls.get('processed', []) +
            self.processed_urls.get('failed', []) +
            self.processed_urls.get('skipped', [])
        )
        
        new_urls = [url for url in urls if url not in all_processed]
        
        logger.info(f"Total URLs: {len(urls)}, New URLs: {len(new_urls)}, Already processed: {len(urls) - len(new_urls)}")
        
        return new_urls
    
    def prioritize_urls(self, urls: List[str]) -> List[str]:
        """Prioritize URLs based on various factors"""
        # For now, just return as-is
        # Future: Could prioritize by company, posting date, etc.
        return urls
    
    def process_urls_batch(self, urls: List[str], auto_submit: bool = False, max_applications: int = 10):
        """Process a batch of LinkedIn job URLs"""
        
        # Filter new URLs
        new_urls = self.filter_new_urls(urls)
        
        if not new_urls:
            logger.info("No new URLs to process")
            return
        
        # Prioritize URLs
        prioritized_urls = self.prioritize_urls(new_urls)[:max_applications]
        
        logger.info(f"Processing {len(prioritized_urls)} job URLs")
        
        # Update config for auto_submit
        config_path = Path('linkedin_config.json')
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            config['auto_submit'] = auto_submit
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        # Initialize bot and process URLs
        bot = LinkedInEasyApplyBot(headless=False)
        
        try:
            bot.setup_driver()
            
            if bot.login_to_linkedin():
                for url in prioritized_urls:
                    try:
                        success = bot.apply_to_job(url)
                        
                        if success:
                            self.processed_urls['processed'].append(url)
                        else:
                            self.processed_urls['skipped'].append(url)
                            
                    except Exception as e:
                        logger.error(f"Error processing {url}: {str(e)}")
                        self.processed_urls['failed'].append(url)
                    
                    # Save progress after each URL
                    self._save_processed_urls()
            else:
                logger.error("Failed to login to LinkedIn")
                
        finally:
            bot.cleanup()
    
    def generate_report(self) -> str:
        """Generate a report of processed URLs"""
        report = []
        report.append("=" * 60)
        report.append("LINKEDIN JOB PROCESSING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Statistics
        total_processed = len(self.processed_urls.get('processed', []))
        total_failed = len(self.processed_urls.get('failed', []))
        total_skipped = len(self.processed_urls.get('skipped', []))
        total = total_processed + total_failed + total_skipped
        
        report.append("STATISTICS:")
        report.append(f"  Total URLs processed: {total}")
        report.append(f"  Successfully applied: {total_processed}")
        report.append(f"  Failed: {total_failed}")
        report.append(f"  Skipped: {total_skipped}")
        
        if total > 0:
            success_rate = (total_processed / total) * 100
            report.append(f"  Success rate: {success_rate:.1f}%")
        
        report.append("")
        
        # Recent applications
        if self.processed_urls.get('processed'):
            report.append("RECENT SUCCESSFUL APPLICATIONS (Last 10):")
            for url in self.processed_urls['processed'][-10:]:
                job_id = self.extract_job_id_from_url(url)
                report.append(f"  • Job ID: {job_id}")
                report.append(f"    URL: {url}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """Main function for processing LinkedIn job URLs"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process LinkedIn job URLs for Easy Apply')
    parser.add_argument('--file', type=str, help='Path to file containing LinkedIn URLs')
    parser.add_argument('--database', action='store_true', help='Load URLs from database')
    parser.add_argument('--url', type=str, help='Single LinkedIn job URL to process')
    parser.add_argument('--auto-submit', action='store_true', help='Automatically submit applications')
    parser.add_argument('--max', type=int, default=10, help='Maximum number of applications')
    parser.add_argument('--report', action='store_true', help='Generate report only')
    
    args = parser.parse_args()
    
    processor = LinkedInJobProcessor()
    
    if args.report:
        # Generate and print report
        print(processor.generate_report())
        return
    
    # Collect URLs from various sources
    urls = []
    
    if args.url:
        # Single URL provided
        if processor.validate_linkedin_url(args.url):
            urls.append(args.url)
        else:
            print(f"Invalid LinkedIn URL: {args.url}")
            return
    
    if args.file:
        # Load from specific file
        file_urls = processor.load_urls_from_file(Path(args.file))
        urls.extend(file_urls)
    elif args.database:
        # Load from database
        db_urls = processor.load_urls_from_database()
        urls.extend(db_urls)
    else:
        # Default: Load from standard file
        file_urls = processor.load_urls_from_file()
        urls.extend(file_urls)
    
    if not urls:
        print("\n⚠️ No URLs to process!")
        print("\nUsage examples:")
        print("  python3 linkedin_job_processor.py --url https://www.linkedin.com/jobs/view/123456")
        print("  python3 linkedin_job_processor.py --file my_job_urls.txt")
        print("  python3 linkedin_job_processor.py --database")
        print("  python3 linkedin_job_processor.py --report")
        print("\nOr add URLs to linkedin_job_urls.txt and run without arguments")
        return
    
    # Process URLs
    print(f"\n🎯 Found {len(urls)} LinkedIn job URLs")
    
    response = input("\nProceed with Easy Apply automation? (y/n): ")
    if response.lower() == 'y':
        processor.process_urls_batch(
            urls,
            auto_submit=args.auto_submit,
            max_applications=args.max
        )
        
        # Print report after processing
        print("\n" + processor.generate_report())
    else:
        print("Automation cancelled")


if __name__ == "__main__":
    main()