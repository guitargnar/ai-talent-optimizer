#!/usr/bin/env python3
"""
Session Startup Script - Quick context loading for Claude sessions
Run this at the start of each new Claude session to load all context
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import subprocess

class SessionSetup:
    def __init__(self):
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def check_environment(self):
        """Verify all required files exist"""
        print("🔍 Checking environment...")
        
        required_files = [
            "unified_platform.db",
            "unified_platform.db",
            "profile_context_generator.py",
            "generate_application.py",
            "add_job_from_user.py"
        ]
        
        missing = []
        for file in required_files:
            if Path(file).exists():
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} (missing)")
                missing.append(file)
        
        if missing:
            print("\n⚠️ Missing files detected. Running setup...")
            self.run_initial_setup()
        
        return len(missing) == 0
    
    def run_initial_setup(self):
        """Run initial setup if files are missing"""
        scripts = [
            "create_profile_database.py",
            "populate_real_400k_jobs.py"
        ]
        
        for script in scripts:
            if Path(script).exists():
                print(f"Running {script}...")
                subprocess.run(["python3", script])
    
    def generate_fresh_context(self):
        """Generate fresh context document"""
        print("\n📊 Generating fresh context...")
        
        from profile_context_generator import ProfileContextGenerator
        generator = ProfileContextGenerator()
        context = generator.generate_context_document()
        
        return context
    
    def show_current_metrics(self):
        """Display current platform metrics"""
        print("\n📈 Current Platform Metrics:")
        print("="*60)
        
        # Count Python files
        py_files = list(Path.cwd().glob("*.py"))
        print(f"  Python modules in directory: {len(py_files)}")
        
        # Count databases
        db_files = list(Path.cwd().glob("*.db"))
        print(f"  Active databases: {len(db_files)}")
        
        # Check for recent activity
        today = datetime.now().date()
        modified_today = 0
        for f in py_files:
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).date()
                if mtime == today:
                    modified_today += 1
            except:
                pass
        print(f"  Files modified today: {modified_today}")
        
        # Check job database
        if Path("unified_platform.db").exists():
            conn = sqlite3.connect("unified_platform.db")
            cursor = conn.cursor()
            
            # Count jobs
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied = 0")
            unapplied = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied = 1")
            applied = cursor.fetchone()[0]
            
            print(f"  Jobs to apply to: {unapplied}")
            print(f"  Jobs applied: {applied}")
            
            conn.close()
    
    def create_session_file(self):
        """Create session tracking file"""
        session_file = f"sessions/session_{self.session_id}.md"
        
        # Create sessions directory
        Path("sessions").mkdir(exist_ok=True)
        
        content = f"""# Session {self.session_id}
Started: {datetime.now().isoformat()}

## Context Loaded
- Profile database: ✅
- Job database: ✅
- Context document: CURRENT_PROFILE_CONTEXT.md

## Quick Commands

### Generate Application from Job Description
```python
from generate_application import ApplicationGenerator
generator = ApplicationGenerator()

# Paste job description in triple quotes
job_desc = '''
[PASTE JOB DESCRIPTION HERE]
'''

result = generator.generate_for_role(job_desc)
```

### Add New Job Manually
```python
from add_job_from_user import add_single_job
add_single_job()
```

### Apply to Top Jobs
```bash
python3 apply_to_real_jobs_now.py
```

### Refresh Context
```bash
python3 profile_context_generator.py
```

## Session Notes
[Add your notes here]

---
"""
        
        with open(session_file, 'w') as f:
            f.write(content)
        
        return session_file
    
    def show_quick_start(self):
        """Display quick start commands"""
        print("\n🚀 QUICK START COMMANDS")
        print("="*60)
        print("""
1. Generate application from job posting:
   python3 -c "from generate_application import ApplicationGenerator; g = ApplicationGenerator(); g.generate_for_role(input('Paste job description: '))"

2. Add a new job:
   python3 add_job_from_user.py

3. Apply to top jobs:
   python3 apply_to_real_jobs_now.py

4. Refresh context:
   python3 profile_context_generator.py

5. View recent jobs:
   sqlite3 principal_jobs_400k.db "SELECT company, title, min_salary FROM jobs ORDER BY discovered_at DESC LIMIT 5"
""")
    
    def load_pending_tasks(self):
        """Check for any pending tasks"""
        print("\n📝 Checking for pending tasks...")
        
        # Check for saved job descriptions
        if Path("last_job_description.txt").exists():
            print("  ⚠️ Found saved job description - ready to generate application")
            print("     Run: python3 generate_application.py")
        
        # Check for unapplied jobs
        if Path("unified_platform.db").exists():
            conn = sqlite3.connect("unified_platform.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT company, position 
                FROM jobs 
                WHERE applied = 0 
                ORDER BY max_salary DESC 
                LIMIT 3
            """)
            
            top_jobs = cursor.fetchall()
            if top_jobs:
                print("\n  📋 Top unapplied jobs:")
                for company, position in top_jobs:
                    print(f"     - {company}: {position}")
            
            conn.close()
    
    def run(self):
        """Main setup flow"""
        print("🚀 SESSION STARTUP SCRIPT")
        print("="*60)
        print(f"Session ID: {self.session_id}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check environment
        self.check_environment()
        
        # Generate fresh context
        self.generate_fresh_context()
        
        # Show metrics
        self.show_current_metrics()
        
        # Create session file
        session_file = self.create_session_file()
        print(f"\n📁 Session file created: {session_file}")
        
        # Check pending tasks
        self.load_pending_tasks()
        
        # Show quick start
        self.show_quick_start()
        
        print("\n✅ SESSION READY!")
        print("="*60)
        print("""
Your profile context is loaded and ready.
CURRENT_PROFILE_CONTEXT.md contains all your metrics.

To generate an application, just paste a job description!
""")
        
        return True

def main():
    """Run session setup"""
    setup = SessionSetup()
    setup.run()
    
    # Offer to generate application immediately
    print("\n" + "="*60)
    choice = input("Do you have a job description to process? (yes/no): ").strip()
    
    if choice.lower() == 'yes':
        print("\nStarting application generator...")
        from generate_application import ApplicationGenerator
        
        print("Paste the job description below.")
        print("When done, type 'END' on a new line:")
        print()
        
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        
        if lines:
            job_description = '\n'.join(lines)
            generator = ApplicationGenerator()
            result = generator.generate_for_role(job_description)
            print(f"\n✅ Application generated: {result['package_path']}")

if __name__ == "__main__":
    main()