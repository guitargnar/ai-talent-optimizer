#!/usr/bin/env python3
"""
Main Automation Runner for AI Job Hunter
Orchestrates all components of the job hunting system
"""

import subprocess
import sys
import time
from datetime import datetime
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)


class AIJobHunterAutomation:
    """Main automation orchestrator"""
    
    def __init__(self):
        self.base_dir = Path("/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer")
        self.log = logging.getLogger(__name__)
        
    def check_environment(self):
        """Check that all required files exist"""
        self.log.info("🔍 Checking environment...")
        
        required_files = [
            'unified_ai_hunter.py',
            'automated_apply.py',
            'unified_email_automation.py',
            '.env',
            'UNIFIED_AI_JOBS.db'
        ]
        
        missing = []
        for file in required_files:
            if not (self.base_dir / file).exists():
                missing.append(file)
        
        if missing:
            self.log.error(f"❌ Missing required files: {missing}")
            return False
        
        self.log.info("✅ Environment check passed")
        return True
    
    def run_discovery(self):
        """Run job discovery process"""
        self.log.info("🔍 Running job discovery...")
        
        try:
            result = subprocess.run(
                ['python3', 'unified_ai_hunter.py', '--daily'],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            if result.returncode == 0:
                self.log.info("✅ Job discovery completed successfully")
                # Extract job count from output
                if "Discovered" in result.stdout:
                    self.log.info(result.stdout.split('\n')[-5])
                return True
            else:
                self.log.error(f"❌ Job discovery failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log.error(f"❌ Error running discovery: {e}")
            return False
    
    def run_applications(self, batch_size=5):
        """Run automated applications"""
        self.log.info(f"📧 Running automated applications (batch size: {batch_size})...")
        
        try:
            # Check if we have jobs to apply to
            result = subprocess.run(
                ['sqlite3', 'UNIFIED_AI_JOBS.db', 
                 'SELECT COUNT(*) FROM job_discoveries WHERE applied = 0 AND relevance_score >= 0.6'],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            available_jobs = int(result.stdout.strip())
            if available_jobs == 0:
                self.log.info("No suitable jobs to apply to")
                return True
            
            self.log.info(f"Found {available_jobs} suitable jobs")
            
            # Run applications
            result = subprocess.run(
                ['python3', 'automated_apply.py', '--batch', str(batch_size)],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            if result.returncode == 0:
                self.log.info("✅ Applications sent successfully")
                print(result.stdout)
                return True
            else:
                self.log.error(f"❌ Application process failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log.error(f"❌ Error running applications: {e}")
            return False
    
    def check_responses(self):
        """Check email responses"""
        self.log.info("📧 Checking email responses...")
        
        try:
            result = subprocess.run(
                ['python3', 'gmail_recent_monitor.py'],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            if result.returncode == 0:
                self.log.info("✅ Email check completed")
                # Extract response count
                if "Total Job Responses:" in result.stdout:
                    for line in result.stdout.split('\n'):
                        if "Total Job Responses:" in line:
                            self.log.info(line)
                return True
            else:
                self.log.warning(f"Email check had issues: {result.stderr}")
                return False
                
        except Exception as e:
            self.log.error(f"❌ Error checking emails: {e}")
            return False
    
    def generate_report(self):
        """Generate daily report"""
        self.log.info("📊 Generating daily report...")
        
        try:
            # Get database stats
            result = subprocess.run(
                ['sqlite3', '-column', '-header', 'UNIFIED_AI_JOBS.db',
                 '''SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN applied = 1 THEN 1 END) as applied,
                    COUNT(DISTINCT company) as companies,
                    AVG(relevance_score) as avg_score
                 FROM job_discoveries'''],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            print("\n📊 DATABASE STATISTICS")
            print("=" * 60)
            print(result.stdout)
            
            # Get today's activity
            result = subprocess.run(
                ['sqlite3', '-column', '-header', 'UNIFIED_AI_JOBS.db',
                 '''SELECT company, position, relevance_score 
                    FROM job_discoveries 
                    WHERE applied = 0 
                    ORDER BY relevance_score DESC 
                    LIMIT 5'''],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            print("\n🎯 TOP OPPORTUNITIES")
            print("=" * 60)
            print(result.stdout)
            
            self.log.info("✅ Report generated")
            return True
            
        except Exception as e:
            self.log.error(f"❌ Error generating report: {e}")
            return False
    
    def run_full_automation(self, apply_batch=5):
        """Run complete automation cycle"""
        print("\n🚀 AI JOB HUNTER AUTOMATION")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Check environment
        if not self.check_environment():
            return False
        
        # Run discovery
        print("\n📍 Step 1: Job Discovery")
        if not self.run_discovery():
            self.log.warning("Discovery failed, continuing...")
        
        time.sleep(2)
        
        # Check responses
        print("\n📍 Step 2: Check Email Responses")
        if not self.check_responses():
            self.log.warning("Email check failed, continuing...")
        
        time.sleep(2)
        
        # Run applications
        print("\n📍 Step 3: Send Applications")
        if not self.run_applications(apply_batch):
            self.log.warning("Applications failed, continuing...")
        
        time.sleep(2)
        
        # Generate report
        print("\n📍 Step 4: Generate Report")
        self.generate_report()
        
        print("\n✅ AUTOMATION COMPLETE!")
        print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True


def main():
    """Main entry point"""
    automation = AIJobHunterAutomation()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--discover':
            automation.run_discovery()
        elif sys.argv[1] == '--apply':
            batch = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            automation.run_applications(batch)
        elif sys.argv[1] == '--check':
            automation.check_responses()
        elif sys.argv[1] == '--report':
            automation.generate_report()
        else:
            print("Usage: python run_automation.py [--discover|--apply N|--check|--report]")
    else:
        # Run full automation
        automation.run_full_automation()


if __name__ == "__main__":
    main()