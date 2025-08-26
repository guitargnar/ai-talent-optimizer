#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI Talent Optimizer
Tests all core functionality and reports what's actually working
"""

import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def test_result(full_name, passed, details=""):
    """Print test result with color coding"""
    if passed:
        print(f"{GREEN}✅ PASS{RESET}: {name}")
    else:
        print(f"{RED}❌ FAIL{RESET}: {name}")
    if details:
        print(f"   Details: {details}")

class SystemTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def test_cli_interface(self):
        """Test CLI is importable and functional"""
        print("\n📋 Testing CLI Interface...")
        try:
            # Try importing CLI
            sys.path.insert(0, str(Path(__file__).parent))
            from cli import main
            test_result("CLI import", True)
            self.passed += 1
            
            # Test that it has expected commands
            import click
            ctx = click.Context(main.cli)
            commands = main.cli.list_commands(ctx)
            expected = ['apply', 'discover', 'email', 'status']
            for cmd in expected:
                if cmd in commands:
                    test_result(f"CLI command: {cmd}", True)
                    self.passed += 1
                else:
                    test_result(f"CLI command: {cmd}", False)
                    self.failed += 1
        except Exception as e:
            test_result("CLI import", False, str(e))
            self.failed += 1
    
    def test_databases(self):
        """Test database connectivity and data"""
        print("\n📊 Testing Databases...")
        
        db_files = list(Path('.').glob('*.db'))
        print(f"Found {len(db_files)} database files")
        
        for db_path in db_files:
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                # Count records in each table
                total_records = 0
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                        count = cursor.fetchone()[0]
                        total_records += count
                    except:
                        pass
                
                conn.close()
                test_result(f"Database: {db_path.name}", True, 
                           f"{len(tables)} tables, {total_records} total records")
                self.passed += 1
                
            except Exception as e:
                test_result(f"Database: {db_path.name}", False, str(e))
                self.failed += 1
    
    def test_gmail_oauth(self):
        """Test Gmail OAuth configuration"""
        print("\n📧 Testing Gmail OAuth...")
        
        # Check for credentials
        creds_path = Path.home() / ".gmail_job_tracker" / "credentials.json"
        if creds_path.exists():
            test_result("Gmail credentials.json", True, str(creds_path))
            self.passed += 1
        else:
            test_result("Gmail credentials.json", False, "Not found")
            self.failed += 1
        
        # Check for token
        token_path = Path.home() / ".gmail_job_tracker" / "token.json"
        if token_path.exists():
            test_result("Gmail token.json", True, "Token exists")
            self.passed += 1
        else:
            test_result("Gmail token.json", False, "Token needs generation")
            self.warnings += 1
    
    def test_applications_sent(self):
        """Test applications tracking"""
        print("\n📤 Testing Applications...")
        
        apps_dir = Path("applications_sent")
        if apps_dir.exists():
            apps = list(apps_dir.glob("*.txt"))
            test_result("Applications directory", True, f"{len(apps)} applications found")
            self.passed += 1
            
            # Show recent applications
            if apps:
                print("\n   Recent applications:")
                for app in sorted(apps)[-5:]:
                    print(f"   • {app.name}")
        else:
            test_result("Applications directory", False, "Directory not found")
            self.failed += 1
    
    def test_cover_letters(self):
        """Test cover letter generation"""
        print("\n📝 Testing Cover Letters...")
        
        cover_dir = Path("output/cover_letters")
        if cover_dir.exists():
            letters = list(cover_dir.glob("*.txt"))
            test_result("Cover letters", True, f"{len(letters)} letters generated")
            self.passed += 1
            
            if letters:
                print("\n   Generated cover letters:")
                for letter in letters:
                    print(f"   • {letter.name}")
        else:
            test_result("Cover letters directory", False)
            self.failed += 1
    
    def test_python_files(self):
        """Count and verify Python files"""
        print("\n🐍 Testing Python Files...")
        
        py_files = list(Path('.').glob('**/*.py'))
        test_result("Python file count", True, f"{len(py_files)} files found")
        self.passed += 1
        
        # Test key files exist
        key_files = [
            'cli/main.py',
            'utils/config.py',
            'follow_up_system.py',
            'apply_to_top_jobs.py'
        ]
        
        for file_path in key_files:
            if Path(file_path).exists():
                test_result(f"Key file: {file_path}", True)
                self.passed += 1
            else:
                test_result(f"Key file: {file_path}", False)
                self.failed += 1
    
    def test_configuration(self):
        """Test configuration values"""
        print("\n⚙️ Testing Configuration...")
        
        try:
            from utils.config import Config
            
            # Test personal info
            assert Config.PERSONAL['phone'] == "502-345-0525"
            test_result("Phone number", True, "502-345-0525")
            self.passed += 1
            
            assert Config.PERSONAL['email'] == "matthewdscott7@gmail.com"
            test_result("Email", True, Config.PERSONAL['email'])
            self.passed += 1
            
            assert Config.PERSONAL['github'] == "github.com/guitargnar"
            test_result("GitHub", True, Config.PERSONAL['github'])
            self.passed += 1
            
        except Exception as e:
            test_result("Configuration", False, str(e))
            self.failed += 1
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total = self.passed + self.failed + self.warnings
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"{YELLOW}Warnings: {self.warnings}{RESET}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        # Critical issues
        if self.failed > 0:
            print(f"\n{RED}⚠️ CRITICAL ISSUES TO FIX:{RESET}")
            if "token.json" in str(self.warnings):
                print("1. Generate Gmail token for email sending")
            print("2. Review failed tests above")
        
        # Recommendations
        print(f"\n{YELLOW}📋 RECOMMENDATIONS:{RESET}")
        print("1. Consolidate databases into single source")
        print("2. Update documentation to match reality")
        print("3. Fix resume PDF phone number")
        print("4. Send prepared applications")
        
        return pass_rate

def main():
    """Run all tests"""
    print("🧪 AI Talent Optimizer - Comprehensive Test Suite")
    print("="*60)
    print(f"Testing at: {datetime.now()}")
    print(f"Directory: {os.getcwd()}")
    
    tester = SystemTester()
    
    # Run all tests
    tester.test_cli_interface()
    tester.test_databases()
    tester.test_gmail_oauth()
    tester.test_applications_sent()
    tester.test_cover_letters()
    tester.test_python_files()
    tester.test_configuration()
    
    # Generate report
    pass_rate = tester.generate_report()
    
    # Save results
    with open("TEST_RESULTS.md", "w") as f:
        f.write(f"# Test Results - {datetime.now()}\n\n")
        f.write(f"- Passed: {tester.passed}\n")
        f.write(f"- Failed: {tester.failed}\n")
        f.write(f"- Warnings: {tester.warnings}\n")
        f.write(f"- Pass Rate: {pass_rate:.1f}%\n")
    
    print(f"\n📄 Results saved to TEST_RESULTS.md")
    
    # Exit code based on failures
    sys.exit(0 if tester.failed == 0 else 1)

if __name__ == "__main__":
    main()