#!/usr/bin/env python3
"""
Scheduler Configuration for AI Job Hunter
Sets up automated runs at 9am and 6pm daily
"""

import schedule
import time
import subprocess
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

def run_job_discovery():
    """Run job discovery and application process"""
    logging.info("🔍 Starting job discovery...")
    
    try:
        # Run unified AI hunter
        subprocess.run(['python', 'unified_ai_hunter.py', '--daily'], check=True)
        logging.info("✅ Job discovery complete")
        
        # Run automated applications
        subprocess.run(['python', 'automated_apply.py', '--batch', '10'], check=True)
        logging.info("✅ Automated applications complete")
        
        # Send daily report
        subprocess.run(['python', 'unified_email_automation.py', '--report'], check=True)
        logging.info("✅ Daily report sent")
        
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error in job discovery: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")

def run_email_sync():
    """Sync email systems"""
    logging.info("📧 Syncing email systems...")
    
    try:
        subprocess.run(['python', 'unified_email_automation.py', '--sync'], check=True)
        logging.info("✅ Email sync complete")
    except Exception as e:
        logging.error(f"❌ Error in email sync: {e}")

def main():
    """Main scheduler loop"""
    logging.info("🤖 AI Job Hunter Scheduler Started")
    
    # Schedule jobs
    schedule.every().day.at("09:00").do(run_job_discovery)
    schedule.every().day.at("18:00").do(run_job_discovery)
    schedule.every(30).minutes.do(run_email_sync)
    
    # Run once on startup
    run_email_sync()
    
    logging.info("📅 Scheduled jobs:")
    logging.info("  - Job discovery: 9:00 AM and 6:00 PM daily")
    logging.info("  - Email sync: Every 30 minutes")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logging.info("\n👋 Scheduler stopped")
            break
        except Exception as e:
            logging.error(f"Scheduler error: {e}")
            time.sleep(300)  # Wait 5 minutes on error

if __name__ == "__main__":
    main()
