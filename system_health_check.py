#!/usr/bin/env python3
"""
System Health Check - Validates the AI Job Hunter is ready to run
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

class SystemHealthCheck:
    """Comprehensive health check for AI Job Hunter"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
        
    def print_header(self, title):
        """Print section header"""
        print(f"\n{'='*50}")
        print(f"🔍 {title}")
        print('='*50)
    
    def check_pass(self, message):
        """Record passing check"""
        print(f"✅ {message}")
        self.checks_passed += 1
    
    def check_fail(self, message):
        """Record failing check"""
        print(f"❌ {message}")
        self.checks_failed += 1
    
    def check_warn(self, message):
        """Record warning"""
        print(f"⚠️  {message}")
        self.warnings.append(message)
    
    def check_environment(self):
        """Check environment setup"""
        self.print_header("Environment Configuration")
        
        # Check .env file
        if Path('.env').exists():
            self.check_pass(".env file exists")
            
            # Load and validate
            from dotenv import dotenv_values
            config = dotenv_values('.env')
            
            if config.get('EMAIL_ADDRESS'):
                self.check_pass(f"Email configured: {config['EMAIL_ADDRESS']}")
            else:
                self.check_fail("EMAIL_ADDRESS not set in .env")
            
            if config.get('EMAIL_APP_PASSWORD'):
                self.check_pass("Email app password configured")
            else:
                self.check_fail("EMAIL_APP_PASSWORD not set in .env")
        else:
            self.check_fail(".env file missing - create with EMAIL_ADDRESS and EMAIL_APP_PASSWORD")
    
    def check_database(self):
        """Check database status"""
        self.print_header("Database Status")
        
        db_path = "UNIFIED_AI_JOBS.db"
        if Path(db_path).exists():
            self.check_pass("Database exists")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check total jobs
                cursor.execute("SELECT COUNT(*) FROM job_discoveries")
                total = cursor.fetchone()[0]
                self.check_pass(f"Total jobs in database: {total}")
                
                # Check applied jobs
                cursor.execute("SELECT COUNT(*) FROM job_discoveries WHERE applied=1")
                applied = cursor.fetchone()[0]
                self.check_pass(f"Applications sent: {applied}")
                
                # Check today's applications
                cursor.execute("""
                    SELECT COUNT(*) FROM job_discoveries 
                    WHERE applied=1 AND DATE(applied_date) = DATE('now')
                """)
                today = cursor.fetchone()[0]
                if today > 0:
                    self.check_pass(f"Applications sent today: {today}")
                else:
                    self.check_warn("No applications sent today")
                
                # Check pending high-value jobs
                cursor.execute("""
                    SELECT COUNT(*) FROM job_discoveries 
                    WHERE applied=0 AND relevance_score >= 0.65
                """)
                pending = cursor.fetchone()[0]
                self.check_pass(f"High-value jobs pending: {pending}")
                
                conn.close()
            except Exception as e:
                self.check_fail(f"Database error: {e}")
        else:
            self.check_fail("Database not found - run job_discovery.py first")
    
    def check_resumes(self):
        """Check resume files"""
        self.print_header("Resume Files")
        
        resume_dir = Path("resumes")
        if resume_dir.exists():
            self.check_pass("Resume directory exists")
            
            required_resumes = [
                "matthew_scott_ai_ml_resume.pdf",
                "technical_deep_dive.pdf",
                "executive_leadership.pdf",
                "master_resume_-_all_keywords.pdf"
            ]
            
            for resume in required_resumes:
                if (resume_dir / resume).exists():
                    size = (resume_dir / resume).stat().st_size
                    self.check_pass(f"{resume} ({size:,} bytes)")
                else:
                    self.check_fail(f"{resume} missing")
        else:
            self.check_fail("Resume directory missing - run resume generation")
    
    def check_email_tracking(self):
        """Check email tracking system"""
        self.print_header("Email Tracking")
        
        tracking_file = Path("data/bcc_tracking_log.json")
        if tracking_file.exists():
            self.check_pass("BCC tracking log exists")
            
            with open(tracking_file) as f:
                log = json.load(f)
            
            total_emails = len(log.get('sent_emails', {}))
            self.check_pass(f"Total tracked emails: {total_emails}")
            
            # Check recent emails
            recent_count = 0
            for email_id, data in log.get('sent_emails', {}).items():
                sent_date = datetime.fromisoformat(data['sent_date'])
                if sent_date > datetime.now() - timedelta(days=7):
                    recent_count += 1
            
            if recent_count > 0:
                self.check_pass(f"Emails sent in last 7 days: {recent_count}")
            else:
                self.check_warn("No emails sent in last 7 days")
        else:
            self.check_warn("BCC tracking log not found - will be created on first email")
    
    def check_python_imports(self):
        """Check required Python packages"""
        self.print_header("Python Dependencies")
        
        required_packages = [
            'requests',
            'beautifulsoup4',
            'reportlab',
            'python-dotenv',
            'google-auth',
            'google-auth-oauthlib',
            'google-auth-httplib2'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                self.check_pass(f"{package} installed")
            except ImportError:
                self.check_fail(f"{package} missing - run: pip install {package}")
    
    def check_scheduler(self):
        """Check if scheduler is set up"""
        self.print_header("Automation Scheduler")
        
        try:
            # Check if launchd jobs exist
            result = subprocess.run(
                ['launchctl', 'list'], 
                capture_output=True, 
                text=True
            )
            
            if 'jobhunter' in result.stdout:
                self.check_pass("Scheduler is running")
            else:
                self.check_warn("Scheduler not running - run: python setup_scheduler.py")
        except:
            self.check_warn("Could not check scheduler status")
    
    def check_recent_activity(self):
        """Check recent system activity"""
        self.print_header("Recent Activity")
        
        # Check if system ran today
        try:
            conn = sqlite3.connect('unified_talent_optimizer.db')
            cursor = conn.cursor()
            
            # Last job discovery
            cursor.execute("""
                SELECT MAX(discovered_date) FROM job_discoveries
            """)
            last_discovery = cursor.fetchone()[0]
            if last_discovery:
                self.check_pass(f"Last job discovery: {last_discovery}")
            
            # Last application
            cursor.execute("""
                SELECT company, position, applied_date 
                FROM job_discoveries 
                WHERE applied=1 
                ORDER BY applied_date DESC 
                LIMIT 1
            """)
            last_app = cursor.fetchone()
            if last_app:
                self.check_pass(f"Last application: {last_app[0]} - {last_app[1]} ({last_app[2]})")
            
            conn.close()
        except Exception as e:
            self.check_warn(f"Could not check recent activity: {e}")
    
    def run_all_checks(self):
        """Run all health checks"""
        print("\n🏥 AI JOB HUNTER SYSTEM HEALTH CHECK")
        print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.check_environment()
        self.check_database()
        self.check_resumes()
        self.check_email_tracking()
        self.check_python_imports()
        self.check_scheduler()
        self.check_recent_activity()
        
        # Summary
        self.print_header("Health Check Summary")
        
        total_checks = self.checks_passed + self.checks_failed
        health_score = (self.checks_passed / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n📊 Health Score: {health_score:.0f}%")
        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        
        if self.checks_failed == 0:
            print("\n✨ System is healthy and ready to run!")
            print("\n🚀 Quick start: python run_automation.py")
        else:
            print("\n🔧 Please fix the issues above before running automation")
            print("\n📖 See README_COMPLETE.md for detailed setup instructions")
        
        return self.checks_failed == 0


def main():
    """Run health check"""
    checker = SystemHealthCheck()
    healthy = checker.run_all_checks()
    
    # Exit with appropriate code
    sys.exit(0 if healthy else 1)


if __name__ == "__main__":
    main()