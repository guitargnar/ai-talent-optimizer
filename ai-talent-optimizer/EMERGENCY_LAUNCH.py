#!/usr/bin/env python3
"""
EMERGENCY JOB SEARCH LAUNCHER
For immediate, high-volume job search after termination
Target: 50-75 applications per day across all suitable roles
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import time

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_career_system.data_layer.master_database import MasterDatabase
from unified_career_system.data_layer.job_aggregator import JobAggregator
from unified_career_system.pipeline_transparency.pipeline_manager import (
    PipelineManager, ContactType, ContactSource
)

class EmergencyJobSearchLauncher:
    """Emergency system for rapid job search deployment"""
    
    def __init__(self):
        self.start_date = datetime.now()
        self.termination_date = datetime(2025, 8, 19)  # Monday
        self.days_since_termination = (datetime.now() - self.termination_date).days
        
        # Initialize systems
        self.db = MasterDatabase()
        self.aggregator = JobAggregator()
        self.pipeline = PipelineManager()
        
        # Wide net configuration
        self.config = {
            'ml_threshold': 0.3,  # Lower threshold for wider net
            'daily_target': 50,    # Applications per day
            'include_stretch': True,  # Include roles we're 60% qualified for
            'include_adjacent': True,  # Platform, Data, Infrastructure roles
            'salary_flexibility': 0.2,  # Accept 20% below target
            'location': 'any',  # Remote, hybrid, or local
            'urgency': 'immediate'  # Available immediately
        }
        
    def launch_emergency_search(self):
        """Launch comprehensive emergency job search"""
        
        print("\n" + "="*80)
        print("🚨 EMERGENCY JOB SEARCH LAUNCHER")
        print(f"📅 Termination Date: {self.termination_date.strftime('%Y-%m-%d')}")
        print(f"⏱️ Days Since: {self.days_since_termination}")
        print("🎯 Target: 250 applications this week")
        print("="*80)
        
        # Phase 1: Assessment
        self._assess_current_state()
        
        # Phase 2: Wide Net Discovery
        self._discover_all_opportunities()
        
        # Phase 3: Generate Application Plan
        self._generate_application_plan()
        
        # Phase 4: Documentation for Unemployment
        self._generate_unemployment_docs()
        
        # Phase 5: Launch Instructions
        self._provide_launch_instructions()
        
    def _assess_current_state(self):
        """Assess current pipeline state"""
        print("\n📊 CURRENT PIPELINE STATUS")
        print("-" * 40)
        
        conn = self.db.conn
        cursor = conn.cursor()
        
        # Total jobs in database
        cursor.execute("SELECT COUNT(*) FROM master_jobs")
        total_jobs = cursor.fetchone()[0]
        
        # Applications sent
        cursor.execute("SELECT COUNT(*) FROM master_applications")
        total_apps = cursor.fetchone()[0]
        
        # Recent applications (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM master_applications 
            WHERE date(applied_date) > date('now', '-7 days')
        """)
        recent_apps = cursor.fetchone()[0]
        
        print(f"📂 Total Jobs Available: {total_jobs}")
        print(f"✉️ Total Applications Sent: {total_apps}")
        print(f"📈 Recent Applications (7 days): {recent_apps}")
        
        if recent_apps < 50:
            print("\n⚠️ APPLICATION RATE TOO LOW!")
            print("   Need to increase to 50/day immediately")
        
        # Check for responses
        cursor.execute("""
            SELECT COUNT(*) FROM master_applications 
            WHERE response_type IS NOT NULL
        """)
        responses = cursor.fetchone()[0]
        
        if total_apps > 0:
            response_rate = (responses / total_apps) * 100
            print(f"📧 Response Rate: {response_rate:.1f}%")
        
    def _discover_all_opportunities(self):
        """Discover all available opportunities with wide net"""
        print("\n🔍 DISCOVERING ALL OPPORTUNITIES")
        print("-" * 40)
        
        # Target roles for wide net
        target_roles = [
            # Primary targets
            "ML Engineer", "Machine Learning Engineer", "AI Engineer",
            "Senior ML Engineer", "Staff ML Engineer", "Principal ML Engineer",
            
            # Adjacent roles
            "Data Engineer", "Platform Engineer", "MLOps Engineer",
            "Data Scientist", "Applied Scientist", "Research Engineer",
            "Software Engineer - ML", "Backend Engineer - AI",
            
            # Leadership roles
            "ML Lead", "AI Lead", "Engineering Manager - ML",
            "Technical Lead - AI", "ML Architect",
            
            # Specialized
            "NLP Engineer", "Computer Vision Engineer", "Deep Learning Engineer",
            "LLM Engineer", "GenAI Engineer"
        ]
        
        print(f"🎯 Searching for {len(target_roles)} role types")
        
        # Get all active jobs
        conn = self.db.conn
        cursor = conn.cursor()
        
        suitable_jobs = []
        
        for role in target_roles:
            cursor.execute("""
                SELECT job_uid, company, position, ml_score 
                FROM master_jobs 
                WHERE is_active = 1 
                AND (position LIKE ? OR position LIKE ?)
                AND (ml_score > ? OR ml_score IS NULL)
                ORDER BY ml_score DESC
            """, (f"%{role}%", f"%{role.lower()}%", self.config['ml_threshold']))
            
            jobs = cursor.fetchall()
            suitable_jobs.extend(jobs)
            
            if jobs:
                print(f"  ✓ {role}: {len(jobs)} positions found")
        
        print(f"\n📊 TOTAL SUITABLE POSITIONS: {len(suitable_jobs)}")
        
        # Remove duplicates
        unique_jobs = {}
        for job in suitable_jobs:
            if job[0] not in unique_jobs:
                unique_jobs[job[0]] = job
        
        print(f"📌 UNIQUE POSITIONS: {len(unique_jobs)}")
        
        return unique_jobs
    
    def _generate_application_plan(self):
        """Generate aggressive application plan"""
        print("\n📋 EMERGENCY APPLICATION PLAN")
        print("-" * 40)
        
        # Week 1 Plan (Days 1-5)
        week1_plan = {
            'Monday': {'target': 50, 'focus': 'Top tier ML roles'},
            'Tuesday': {'target': 50, 'focus': 'Senior positions'},
            'Wednesday': {'target': 50, 'focus': 'Platform/Infrastructure'},
            'Thursday': {'target': 50, 'focus': 'Data Engineering'},
            'Friday': {'target': 50, 'focus': 'Any ML/AI role'}
        }
        
        print("WEEK 1 TARGETS (250 total):")
        for day, plan in week1_plan.items():
            print(f"  {day}: {plan['target']} applications - {plan['focus']}")
        
        # Generate batch commands
        print("\n🚀 LAUNCH COMMANDS:")
        print("-" * 40)
        
        commands = [
            "# Morning batch (25 applications)",
            "python3 unified_career_system/application_pipeline/orchestrator.py --count 25 --priority high",
            "",
            "# Afternoon batch (25 applications)",
            "python3 unified_career_system/application_pipeline/orchestrator.py --count 25 --priority medium",
            "",
            "# Check responses every 2 hours",
            "python3 unified_career_system/response_hub/gmail_central.py",
            "",
            "# End of day report",
            "python3 unified_career_system/intelligence_dashboard/system_status_report.py"
        ]
        
        for cmd in commands:
            print(cmd)
        
        # Save plan to file
        plan_file = f"emergency_plan_{datetime.now().strftime('%Y%m%d')}.json"
        with open(plan_file, 'w') as f:
            json.dump({
                'created': datetime.now().isoformat(),
                'termination_date': self.termination_date.isoformat(),
                'week1_plan': week1_plan,
                'total_target_week1': 250,
                'total_target_month': 700
            }, f, indent=2)
        
        print(f"\n✅ Plan saved to: {plan_file}")
        
    def _generate_unemployment_docs(self):
        """Generate documentation for unemployment claims"""
        print("\n📄 UNEMPLOYMENT DOCUMENTATION")
        print("-" * 40)
        
        # Create job search log
        log_file = f"job_search_log_{datetime.now().strftime('%Y%m%d')}.txt"
        
        with open(log_file, 'w') as f:
            f.write("JOB SEARCH ACTIVITY LOG\n")
            f.write("="*50 + "\n\n")
            f.write(f"Name: Matthew Scott\n")
            f.write(f"Termination Date: {self.termination_date.strftime('%Y-%m-%d')}\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Get all applications
            conn = self.db.conn
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ma.applied_date, mj.company, mj.position, 
                       ma.application_method, ma.response_type
                FROM master_applications ma
                JOIN master_jobs mj ON ma.job_uid = mj.job_uid
                ORDER BY ma.applied_date DESC
            """)
            
            f.write("APPLICATION HISTORY\n")
            f.write("-"*50 + "\n")
            
            for row in cursor.fetchall():
                f.write(f"\nDate: {row[0] or 'Unknown'}\n")
                f.write(f"Company: {row[1]}\n")
                f.write(f"Position: {row[2]}\n")
                f.write(f"Method: {row[3] or 'Online'}\n")
                f.write(f"Response: {row[4] or 'Pending'}\n")
                f.write("-"*30 + "\n")
            
            # Add summary
            cursor.execute("SELECT COUNT(*) FROM master_applications")
            total = cursor.fetchone()[0]
            
            f.write(f"\nTOTAL APPLICATIONS: {total}\n")
            f.write(f"ACTIVE JOB SEARCH: YES\n")
            f.write(f"AVAILABLE FOR WORK: IMMEDIATELY\n")
        
        print(f"✅ Documentation saved to: {log_file}")
        print("   Use this for unemployment claims as proof of job search")
        
    def _provide_launch_instructions(self):
        """Provide clear launch instructions"""
        print("\n" + "="*80)
        print("🚀 IMMEDIATE ACTION ITEMS")
        print("="*80)
        
        instructions = [
            "\n1️⃣ RIGHT NOW (Next 30 minutes):",
            "   • Update LinkedIn to 'Open to Work' (recruiters only)",
            "   • Set up email alerts on all job boards",
            "   • Message 5 former colleagues about opportunities",
            "",
            "2️⃣ TODAY (Next 4 hours):",
            "   • Run morning batch: 25 applications",
            "   • Document all activities in pipeline tracker",
            "   • Set up interviews for any responses",
            "",
            "3️⃣ THIS WEEK (Days 1-5):",
            "   • 250 total applications (50/day)",
            "   • Respond to all emails within 2 hours",
            "   • Track everything for unemployment",
            "",
            "4️⃣ ONGOING DAILY ROUTINE:",
            "   9am: Check responses, schedule interviews",
            "   10am: Launch morning batch (25 apps)",
            "   12pm: LinkedIn networking (1 hour)",
            "   2pm: Launch afternoon batch (25 apps)",
            "   4pm: Interview prep and skills practice",
            "   6pm: Check responses, log activities",
            "   7pm: Plan next day"
        ]
        
        for instruction in instructions:
            print(instruction)
        
        print("\n" + "="*80)
        print("💪 MOTIVATIONAL REMINDER")
        print("="*80)
        print("\n• This is temporary - you will land something better")
        print("• The system handles rejection - you handle success")
        print("• Every application increases your odds")
        print("• Multiple offers = negotiation power")
        print("• Document everything for protection\n")
        
        print("🎯 Statistical Projection:")
        print("   250 applications → 10-15 responses → 5 interviews → 2-3 offers")
        print("   Timeline: 2-3 weeks to first offer\n")

def main():
    """Launch emergency job search"""
    launcher = EmergencyJobSearchLauncher()
    launcher.launch_emergency_search()
    
    print("\n" + "="*80)
    print("✅ EMERGENCY SYSTEM READY")
    print("="*80)
    print("\nYour job search automation is configured for maximum impact.")
    print("Follow the instructions above to launch 250 applications this week.")
    print("\nYou've got this! 💪")

if __name__ == "__main__":
    main()