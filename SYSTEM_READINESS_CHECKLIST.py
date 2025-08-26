#!/usr/bin/env python3
"""
Comprehensive System Readiness Checklist
Identifies gaps and missing components
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime
import subprocess

class SystemReadinessChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.ready_items = []
        
    def check_credentials(self):
        """Verify all credentials are correct"""
        print("🔍 Checking Credentials...")
        
        # Check database
        conn = sqlite3.connect("unified_platform.db")
        cursor = conn.cursor()
        identity = cursor.execute("SELECT * FROM profile").fetchone()
        conn.close()
        
        if 'guitargnar' in identity[5]:
            self.ready_items.append("✅ GitHub correctly set to guitargnar")
        else:
            self.issues.append("❌ GitHub still wrong (not guitargnar)")
            
        if identity[2] == 'matthewdscott7@gmail.com':
            self.ready_items.append("✅ Email correct: matthewdscott7@gmail.com")
        else:
            self.issues.append("❌ Email incorrect")
    
    def check_resume_files(self):
        """Check for actual resume files"""
        print("🔍 Checking Resume Files...")
        
        resume_dir = Path("resumes")
        if resume_dir.exists():
            pdf_files = list(resume_dir.glob("*.pdf"))
            docx_files = list(resume_dir.glob("*.docx"))
            
            if pdf_files:
                self.ready_items.append(f"✅ {len(pdf_files)} PDF resumes found")
            else:
                self.warnings.append("⚠️ No PDF resumes found - need to create")
                
            # Check for main resume
            main_resume = resume_dir / "matthew_scott_ai_ml_resume.pdf"
            if not main_resume.exists():
                self.issues.append("❌ Main resume missing: matthew_scott_ai_ml_resume.pdf")
        else:
            self.issues.append("❌ Resumes directory missing")
    
    def check_email_config(self):
        """Check email/Gmail configuration"""
        print("🔍 Checking Email Configuration...")
        
        # Check for Gmail credentials
        gmail_creds = Path("token.json")
        if gmail_creds.exists():
            self.ready_items.append("✅ Gmail token found")
        else:
            self.warnings.append("⚠️ Gmail token missing - need OAuth setup")
            
        # Check for credentials.json
        if Path("credentials.json").exists():
            self.ready_items.append("✅ Gmail credentials.json found")
        else:
            self.warnings.append("⚠️ Gmail credentials.json missing")
    
    def check_api_keys(self):
        """Check for AI API keys"""
        print("🔍 Checking API Keys...")
        
        keys_found = []
        keys_missing = []
        
        for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GROQ_API_KEY']:
            if os.environ.get(key):
                keys_found.append(key)
            else:
                keys_missing.append(key)
        
        if keys_found:
            self.ready_items.append(f"✅ API keys found: {', '.join(keys_found)}")
        if keys_missing:
            self.warnings.append(f"⚠️ API keys missing: {', '.join(keys_missing)}")
    
    def check_job_pipeline(self):
        """Check job application pipeline"""
        print("🔍 Checking Job Pipeline...")
        
        # Check for unapplied jobs
        try:
            conn = sqlite3.connect("unified_platform.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied = 0")
            unapplied = cursor.fetchone()[0]
            
            if unapplied > 0:
                self.ready_items.append(f"✅ {unapplied} jobs ready to apply")
            else:
                self.warnings.append("⚠️ No unapplied jobs in pipeline")
                
            # Check for high-priority jobs
            cursor.execute("""
                SELECT company, position 
                FROM jobs 
                WHERE applied = 0 
                ORDER BY max_salary DESC 
                LIMIT 3
            """)
            top_jobs = cursor.fetchall()
            
            if top_jobs:
                print("\n📋 Top Priority Jobs:")
                for company, position in top_jobs:
                    print(f"  • {company}: {position}")
                    
            conn.close()
        except Exception as e:
            self.issues.append(f"❌ Job database error: {e}")
    
    def check_linkedin_materials(self):
        """Check LinkedIn optimization materials"""
        print("🔍 Checking LinkedIn Materials...")
        
        linkedin_files = list(Path(".").glob("*linkedin*.md"))
        if linkedin_files:
            self.ready_items.append(f"✅ {len(linkedin_files)} LinkedIn templates found")
        else:
            self.warnings.append("⚠️ No LinkedIn materials found")
    
    def check_cover_letter_templates(self):
        """Check for cover letter templates"""
        print("🔍 Checking Cover Letter Templates...")
        
        if Path("WORK_EXPERIENCE_TEMPLATE.md").exists():
            self.ready_items.append("✅ Work experience template exists")
        else:
            self.issues.append("❌ Work experience template missing")
    
    def check_tracking_systems(self):
        """Check application tracking"""
        print("🔍 Checking Tracking Systems...")
        
        # Check for sent applications
        apps_dir = Path("applications_sent")
        if apps_dir.exists():
            sent_files = list(apps_dir.glob("*.txt"))
            if sent_files:
                self.ready_items.append(f"✅ {len(sent_files)} applications tracked")
        else:
            apps_dir.mkdir(exist_ok=True)
            self.warnings.append("⚠️ Created applications_sent directory")
    
    def check_ollama_models(self):
        """Check Ollama installation"""
        print("🔍 Checking Ollama Models...")
        
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                if lines:
                    self.ready_items.append(f"✅ {len(lines)} Ollama models available")
                else:
                    self.warnings.append("⚠️ No Ollama models installed")
        except:
            self.warnings.append("⚠️ Ollama not found or not running")
    
    def generate_action_items(self):
        """Generate prioritized action items"""
        print("\n" + "="*60)
        print("📋 ACTION ITEMS NEEDED")
        print("="*60)
        
        action_items = []
        
        # Critical issues
        if any("resume" in issue.lower() for issue in self.issues):
            action_items.append({
                'priority': 'CRITICAL',
                'action': 'Create/upload main resume PDF',
                'command': 'cp ~/Desktop/your_resume.pdf resumes/matthew_scott_ai_ml_resume.pdf'
            })
        
        if any("gmail" in warning.lower() for warning in self.warnings):
            action_items.append({
                'priority': 'HIGH',
                'action': 'Set up Gmail OAuth',
                'command': 'python3 setup_gmail_oauth.py'
            })
        
        if any("api" in warning.lower() for warning in self.warnings):
            action_items.append({
                'priority': 'MEDIUM',
                'action': 'Add API keys to environment',
                'command': 'export OPENAI_API_KEY="your-key-here"'
            })
        
        if not action_items:
            print("✅ No critical action items - system ready!")
        else:
            for item in action_items:
                print(f"\n[{item['priority']}] {item['action']}")
                print(f"  Command: {item['command']}")
        
        return action_items
    
    def run_full_check(self):
        """Run all checks"""
        print("🚀 SYSTEM READINESS CHECK")
        print("="*60)
        
        self.check_credentials()
        self.check_resume_files()
        self.check_email_config()
        self.check_api_keys()
        self.check_job_pipeline()
        self.check_linkedin_materials()
        self.check_cover_letter_templates()
        self.check_tracking_systems()
        self.check_ollama_models()
        
        # Generate report
        print("\n" + "="*60)
        print("📊 READINESS REPORT")
        print("="*60)
        
        if self.ready_items:
            print("\n✅ READY:")
            for item in self.ready_items:
                print(f"  {item}")
        
        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.issues:
            print("\n❌ ISSUES:")
            for issue in self.issues:
                print(f"  {issue}")
        
        # Generate action items
        action_items = self.generate_action_items()
        
        # Overall status
        print("\n" + "="*60)
        if not self.issues:
            print("✅ SYSTEM STATUS: READY FOR APPLICATIONS")
        elif len(self.issues) <= 2:
            print("⚠️ SYSTEM STATUS: MOSTLY READY (minor fixes needed)")
        else:
            print("❌ SYSTEM STATUS: NEEDS ATTENTION")
        
        return {
            'ready': len(self.ready_items),
            'warnings': len(self.warnings),
            'issues': len(self.issues),
            'action_items': action_items
        }

def main():
    checker = SystemReadinessChecker()
    results = checker.run_full_check()
    
    # Create status file
    with open("SYSTEM_STATUS.md", 'w') as f:
        f.write(f"# System Status Report\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write(f"## Summary\n")
        f.write(f"- Ready Items: {results['ready']}\n")
        f.write(f"- Warnings: {results['warnings']}\n")
        f.write(f"- Issues: {results['issues']}\n\n")
        
        if results['action_items']:
            f.write("## Action Items\n")
            for item in results['action_items']:
                f.write(f"- [{item['priority']}] {item['action']}\n")
    
    print(f"\n📄 Full report saved to: SYSTEM_STATUS.md")

if __name__ == "__main__":
    main()