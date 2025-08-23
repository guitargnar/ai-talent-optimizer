#!/usr/bin/env python3
"""
Strategic Career Platform Orchestrator v2.0
Human-in-the-loop command center for career automation
Main entry point with staging, review, and approval workflows
"""

import os
import sys
import sqlite3
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

# Import our existing modules
sys.path.append(str(Path(__file__).parent))
from quality_first_apply import QualityFirstApplicationSystem
from dynamic_apply import DynamicJobApplicationSystem

# ============================================================================
# FUTURE INTEGRATION STUBS
# ============================================================================

class WebFormAutomator:
    """Puppeteer integration for automated form filling"""
    
    def __init__(self):
        self.browser = None
        self.page = None
        
    def apply_via_greenhouse(self, job_url: str) -> bool:
        """
        Apply to a job via Greenhouse ATS
        Future implementation will use Puppeteer
        """
        print(f"[FUTURE] Would apply via Greenhouse: {job_url}")
        # TODO: Implement with MCP Puppeteer server
        return False
    
    def apply_via_lever(self, job_url: str) -> bool:
        """Apply to a job via Lever ATS"""
        print(f"[FUTURE] Would apply via Lever: {job_url}")
        # TODO: Implement with MCP Puppeteer server
        return False
    
    def screenshot_confirmation(self) -> str:
        """Take screenshot of application confirmation"""
        # TODO: Implement screenshot capture
        return "confirmation_screenshot.png"


class LinkedInResearcher:
    """LinkedIn integration for finding key contacts"""
    
    def __init__(self):
        self.session = None
        
    def find_hiring_manager(self, company: str, role: str) -> Dict:
        """Find the hiring manager for a specific role"""
        print(f"[FUTURE] Would search LinkedIn for {role} hiring manager at {company}")
        # TODO: Implement LinkedIn API or scraping
        return {
            'name': 'Unknown',
            'title': 'Hiring Manager',
            'profile_url': None
        }
    
    def find_team_members(self, company: str, department: str) -> List[Dict]:
        """Find team members in the target department"""
        print(f"[FUTURE] Would find {department} team at {company}")
        # TODO: Implement team discovery
        return []
    
    def get_company_insights(self, company: str) -> Dict:
        """Get recent company updates and insights"""
        # TODO: Implement company research
        return {
            'recent_news': [],
            'employee_count': 0,
            'growth_rate': 'Unknown'
        }


def generate_content_with_ollama(company_info: Dict, job_description: str) -> Dict:
    """
    Generate personalized content using Ollama models
    Future implementation will chain multiple models
    """
    print("[FUTURE] Would use Ollama models for content generation")
    # TODO: Implement Ollama model chaining
    # Example: 
    # - Use company_researcher model for insights
    # - Use cover_letter_writer model for content
    # - Use tone_optimizer model for refinement
    return {
        'cover_letter': 'Generated content would go here',
        'key_points': [],
        'personalization_score': 0.95
    }


# ============================================================================
# STRATEGIC ORCHESTRATOR
# ============================================================================

class StrategicCareerOrchestrator:
    """Main orchestrator with human-in-the-loop workflow"""
    
    def __init__(self):
        self.db_path = "UNIFIED_AI_JOBS.db"
        self.quality_system = QualityFirstApplicationSystem()
        self.dynamic_system = DynamicJobApplicationSystem()
        
        # Future integrations (currently stubs)
        self.web_automator = WebFormAutomator()
        self.linkedin_researcher = LinkedInResearcher()
        
        # Initialize database with new schema
        self._upgrade_database_schema()
        
        # Session tracking
        self.session_start = datetime.now()
        self.session_stats = {
            'discovered': 0,
            'staged': 0,
            'reviewed': 0,
            'sent': 0
        }
    
    def _upgrade_database_schema(self):
        """Upgrade database schema for staging workflow"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create staged_applications table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staged_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                email_to TEXT NOT NULL,
                email_subject TEXT NOT NULL,
                email_body TEXT NOT NULL,
                resume_path TEXT NOT NULL,
                status TEXT DEFAULT 'pending_review',
                created_date TEXT NOT NULL,
                reviewed_date TEXT,
                sent_date TEXT,
                notes TEXT,
                personalization_score REAL,
                FOREIGN KEY (job_id) REFERENCES job_discoveries(id)
            )
        """)
        
        # Add status column to job_discoveries if not exists
        cursor.execute("""
            SELECT COUNT(*) FROM pragma_table_info('job_discoveries') 
            WHERE name='application_status'
        """)
        
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE job_discoveries 
                ADD COLUMN application_status TEXT DEFAULT 'not_applied'
            """)
        
        conn.commit()
        conn.close()
    
    def discover_and_stage_jobs(self, search_term: str):
        """Discover jobs and create staged applications"""
        print("\n" + "="*60)
        print("🔍 DISCOVERY & STAGING WORKFLOW")
        print("="*60)
        
        # Step 1: Discover jobs
        print(f"\n📡 Discovering jobs for: {search_term}")
        discovered_jobs = self.dynamic_system.discover_new_jobs_online(search_term)
        
        if not discovered_jobs:
            print("❌ No jobs discovered")
            return
        
        print(f"✅ Found {len(discovered_jobs)} opportunities")
        self.session_stats['discovered'] += len(discovered_jobs)
        
        # Step 2: Update database
        new_jobs = self.dynamic_system.update_database_with_discoveries(discovered_jobs)
        
        if not new_jobs:
            print("⚠️  All jobs already in database")
            return
        
        # Step 3: Generate and stage applications
        print(f"\n✍️  Generating personalized applications for {len(new_jobs)} jobs...")
        
        for job in new_jobs:
            self._stage_application(job)
            self.session_stats['staged'] += 1
        
        print(f"\n✅ Staged {len(new_jobs)} applications for review")
        print("Use [R]eview to approve and send")
    
    def _stage_application(self, job: Dict):
        """Generate and stage a single application"""
        # Generate personalized content
        research = self.quality_system.research_company(
            job['company_name'], 
            job['job_title']
        )
        
        subject, body = self.quality_system.generate_personalized_email(
            job['company_name'],
            job['job_title'],
            research
        )
        
        resume_path = self.quality_system.select_resume(
            job['company_name'],
            job['job_title']
        )
        
        # Calculate personalization score
        personalization_score = 0.85  # Base score
        if research.get('key_points'):
            personalization_score += 0.10
        if 'specific_value' in body:
            personalization_score += 0.05
        
        # Save to staging table
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO staged_applications (
                job_id, company, role, email_to, 
                email_subject, email_body, resume_path,
                status, created_date, personalization_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending_review', ?, ?)
        """, (
            job.get('db_id'),
            job['company_name'],
            job['job_title'],
            job.get('email', f"careers@{job['company_name'].lower().replace(' ', '')}.com"),
            subject,
            body,
            resume_path,
            datetime.now().isoformat(),
            personalization_score
        ))
        
        conn.commit()
        conn.close()
        
        print(f"   📋 Staged: {job['company_name']} - {job['job_title']} [Score: {personalization_score:.2f}]")
    
    def review_pending_applications(self):
        """Interactive review and approval workflow"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get pending applications
        cursor.execute("""
            SELECT id, company, role, email_to, email_subject, 
                   email_body, resume_path, personalization_score
            FROM staged_applications
            WHERE status = 'pending_review'
            ORDER BY personalization_score DESC
        """)
        
        pending = cursor.fetchall()
        conn.close()
        
        if not pending:
            print("\n✅ No pending applications to review")
            return
        
        print("\n" + "="*60)
        print(f"📋 REVIEW QUEUE: {len(pending)} Applications")
        print("="*60)
        
        for i, app in enumerate(pending, 1):
            app_id, company, role, email_to, subject, body, resume, score = app
            
            # Clear screen for better readability
            print("\n" + "="*60)
            print(f"📧 APPLICATION {i}/{len(pending)}")
            print("="*60)
            print(f"Company:    {company}")
            print(f"Role:       {role}")
            print(f"Email To:   {email_to}")
            print(f"Resume:     {Path(resume).name}")
            print(f"Quality:    {'⭐' * int(score * 5)} ({score:.2f})")
            print(f"\nSubject:    {subject}")
            print("\n--- Email Preview ---")
            print(body[:400] + "..." if len(body) > 400 else body)
            print("-" * 40)
            
            # Get user decision
            while True:
                decision = input("\n(A)pprove & Send, (S)kip, (E)dit, (D)elete, (Q)uit: ").lower()
                
                if decision == 'a':
                    # Send the application
                    success = self._send_staged_application(app_id, app)
                    if success:
                        print("✅ Application sent successfully!")
                        self.session_stats['sent'] += 1
                    else:
                        print("❌ Failed to send application")
                    break
                    
                elif decision == 's':
                    print("⏭️  Skipped")
                    break
                    
                elif decision == 'e':
                    # Future: Allow editing
                    print("📝 [FUTURE] Edit functionality coming soon")
                    break
                    
                elif decision == 'd':
                    self._delete_staged_application(app_id)
                    print("🗑️  Deleted")
                    break
                    
                elif decision == 'q':
                    print("👋 Returning to main menu")
                    return
                    
                else:
                    print("❌ Invalid choice. Please select A, S, E, D, or Q")
            
            self.session_stats['reviewed'] += 1
            
            # Brief pause between reviews
            if i < len(pending):
                time.sleep(1)
    
    def _send_staged_application(self, app_id: int, app_data: Tuple) -> bool:
        """Send a staged application"""
        _, company, role, email_to, subject, body, resume_path, _ = app_data
        
        try:
            # Use the quality system to send
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.quality_system.email
            msg['To'] = email_to
            msg['Subject'] = subject
            msg['Bcc'] = f"{self.quality_system.email.split('@')[0]}+jobapps@gmail.com"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach resume
            if Path(resume_path).exists():
                with open(resume_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 
                                  f'attachment; filename="{Path(resume_path).name}"')
                    msg.attach(part)
            
            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.quality_system.email, self.quality_system.password)
                server.send_message(msg)
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE staged_applications 
                SET status = 'sent', sent_date = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), app_id))
            
            # Also update job_discoveries
            cursor.execute("""
                UPDATE job_discoveries 
                SET applied = 1, 
                    applied_date = ?,
                    application_status = 'sent'
                WHERE company = ? AND position = ?
            """, (datetime.now().isoformat(), company, role))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending: {str(e)}")
            return False
    
    def _delete_staged_application(self, app_id: int):
        """Delete a staged application"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE staged_applications 
            SET status = 'deleted' 
            WHERE id = ?
        """, (app_id,))
        
        conn.commit()
        conn.close()
    
    def show_status_dashboard(self):
        """Show comprehensive status dashboard"""
        print("\n" + "="*60)
        print("📊 STRATEGIC CAREER PLATFORM STATUS")
        print("="*60)
        
        # Run the true metrics dashboard
        try:
            result = subprocess.run(
                ["python3", "true_metrics_dashboard.py"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )
            print(result.stdout)
        except:
            print("❌ Could not load metrics dashboard")
        
        # Add staging metrics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'pending_review' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent,
                COUNT(CASE WHEN status = 'deleted' THEN 1 END) as deleted
            FROM staged_applications
        """)
        
        pending, sent, deleted = cursor.fetchone()
        conn.close()
        
        print("\n📋 STAGING QUEUE:")
        print(f"  Pending Review: {pending}")
        print(f"  Sent: {sent}")
        print(f"  Deleted: {deleted}")
        
        # Session stats
        print(f"\n📈 CURRENT SESSION ({self.session_start.strftime('%H:%M')}):")
        print(f"  Jobs Discovered: {self.session_stats['discovered']}")
        print(f"  Applications Staged: {self.session_stats['staged']}")
        print(f"  Applications Reviewed: {self.session_stats['reviewed']}")
        print(f"  Applications Sent: {self.session_stats['sent']}")
    
    def run_interactive_dashboard(self):
        """Main interactive dashboard loop"""
        print("\n" + "="*60)
        print("🎯 STRATEGIC CAREER PLATFORM v2.0")
        print("="*60)
        print("Welcome to your AI-powered career command center")
        print("Human-in-the-loop workflow ensures quality and control")
        
        while True:
            print("\n" + "-"*40)
            print("MAIN MENU")
            print("-"*40)
            print("[D] Discover New Jobs")
            print("[R] Review Pending Applications")
            print("[S] Status Dashboard")
            print("[A] Advanced Features (Coming Soon)")
            print("[Q] Quit")
            print("-"*40)
            
            choice = input("\nSelect option: ").lower()
            
            if choice == 'd':
                search_term = input("\nEnter job title to search: ")
                if search_term:
                    self.discover_and_stage_jobs(search_term)
                    
            elif choice == 'r':
                self.review_pending_applications()
                
            elif choice == 's':
                self.show_status_dashboard()
                
            elif choice == 'a':
                self._show_advanced_menu()
                
            elif choice == 'q':
                print("\n👋 Goodbye! Your career awaits.")
                self._show_session_summary()
                break
                
            else:
                print("❌ Invalid option. Please try again.")
    
    def _show_advanced_menu(self):
        """Show advanced features menu (future capabilities)"""
        print("\n" + "="*60)
        print("🚀 ADVANCED FEATURES (Coming Soon)")
        print("="*60)
        print("\n1. 🌐 Web Form Automation (Greenhouse/Lever)")
        print("   - Auto-fill application forms")
        print("   - Screenshot confirmations")
        print("\n2. 🤖 Ollama Model Integration")
        print("   - Chain 74 models for content generation")
        print("   - Dynamic personalization")
        print("\n3. 🔗 LinkedIn Integration")
        print("   - Find hiring managers")
        print("   - Research team members")
        print("   - Company insights")
        print("\n4. 📧 Advanced Email Features")
        print("   - A/B testing")
        print("   - Follow-up automation")
        print("   - Response tracking")
        
        input("\nPress Enter to return to main menu...")
    
    def _show_session_summary(self):
        """Show session summary on exit"""
        duration = datetime.now() - self.session_start
        
        print("\n" + "="*60)
        print("📊 SESSION SUMMARY")
        print("="*60)
        print(f"Duration: {duration}")
        print(f"Jobs Discovered: {self.session_stats['discovered']}")
        print(f"Applications Staged: {self.session_stats['staged']}")
        print(f"Applications Sent: {self.session_stats['sent']}")
        
        if self.session_stats['sent'] > 0:
            print(f"\n✨ Great work! {self.session_stats['sent']} quality applications sent.")
            print("Check your email in 24-48 hours for responses.")


def main():
    """Main entry point"""
    orchestrator = StrategicCareerOrchestrator()
    
    try:
        orchestrator.run_interactive_dashboard()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        orchestrator._show_session_summary()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Please report this issue for debugging")


if __name__ == "__main__":
    main()