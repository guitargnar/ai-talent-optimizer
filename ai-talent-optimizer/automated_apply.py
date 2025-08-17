#!/usr/bin/env python3
"""
Automated Application Script
This is the main entry point for scheduled automation runs.
Called by cron jobs at 9 AM and 6 PM daily.
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up logging
log_dir = project_dir / 'logs'
log_dir.mkdir(exist_ok=True)

# Determine log file based on time of day
hour = datetime.now().hour
if hour < 12:
    log_file = log_dir / f'morning_run_{datetime.now().strftime("%Y%m%d")}.log'
else:
    log_file = log_dir / f'evening_run_{datetime.now().strftime("%Y%m%d")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main automation function."""
    try:
        logger.info("=" * 50)
        logger.info("🚀 Starting Automated Application Run")
        logger.info(f"Time: {datetime.now().isoformat()}")
        logger.info("=" * 50)
        
        # Import here to avoid circular imports
        from src.services.email_discovery import EmailDiscoveryService
        from src.services.application import ApplicationService
        from src.models.database import DatabaseManager
        
        # Step 1: Discover new emails
        logger.info("📧 Discovering email addresses...")
        email_service = EmailDiscoveryService()
        discovered = email_service.bulk_discover_emails(limit=20)
        logger.info(f"✅ Discovered {len(discovered)} new email addresses")
        
        # Step 2: Run applications directly
        logger.info("📤 Sending applications...")
        try:
            # Use the ApplicationService directly
            db = DatabaseManager()
            app_service = ApplicationService(db)
            
            # Send batch of applications
            results = app_service.batch_apply(count=10)
            logger.info(f"✅ Sent {results.get('sent', 0)} applications successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during application sending: {e}")
        
        # Step 3: Check for responses
        logger.info("📥 Checking for responses...")
        try:
            from check_responses import check_recent_responses
            responses = check_recent_responses()
            if responses:
                logger.info(f"✅ Found {len(responses)} new responses!")
            else:
                logger.info("📭 No new responses yet")
        except ImportError:
            logger.warning("Response checker not available, skipping...")
        except Exception as e:
            logger.error(f"Error checking responses: {e}")
        
        # Step 4: Process follow-ups
        logger.info("🔄 Processing follow-ups...")
        try:
            from follow_up_system import process_follow_ups
            follow_ups = process_follow_ups()
            logger.info(f"✅ Sent {follow_ups} follow-up emails")
        except ImportError:
            logger.warning("Follow-up system not available, skipping...")
        except Exception as e:
            logger.error(f"Error processing follow-ups: {e}")
        
        logger.info("=" * 50)
        logger.info("✅ Automation run completed successfully")
        logger.info("=" * 50)
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Fatal error in automation: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)