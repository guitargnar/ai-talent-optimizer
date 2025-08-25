#!/usr/bin/env python3
"""
Email System Cleanup Script
Consolidates and cleans up the email tracking implementation
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path


class EmailSystemCleanup:
    """Clean up and consolidate email tracking systems"""
    
    def __init__(self):
        self.ai_portfolio_dir = Path("/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer")
        self.survive_dir = Path("/Users/matthewscott/SURVIVE/career-automation/real-tracker/career-automation/interview-prep")
        
        # Backup directory
        self.backup_dir = self.ai_portfolio_dir / f"backups/email_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Files to consolidate
        self.email_files = {
            'email_application_tracker.py': 'Core email tracking functionality',
            'gmail_oauth_integration.py': 'Gmail OAuth response monitoring',
            'send_followup_email.py': 'Follow-up email automation',
            'email_automation_setup.py': 'Email configuration setup',
            'test_email_automation.py': 'Email testing utilities',
            'bcc_email_tracker.py': 'BCC tracking enhancement',
            'unified_email_automation.py': 'Unified email system'
        }
        
        self.cleanup_report = {
            'backed_up': [],
            'consolidated': [],
            'created': [],
            'errors': [],
            'recommendations': []
        }
    
    def backup_existing_files(self):
        """Backup all email-related files"""
        print("📦 Backing up existing email files...")
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup from both directories
        for directory in [self.ai_portfolio_dir, self.survive_dir]:
            if directory.exists():
                for file_name in self.email_files.keys():
                    file_path = directory / file_name
                    if file_path.exists():
                        backup_path = self.backup_dir / f"{directory.name}_{file_name}"
                        shutil.copy2(file_path, backup_path)
                        self.cleanup_report['backed_up'].append(str(file_path))
                        print(f"  ✅ Backed up: {file_path.name}")
    
    def consolidate_to_ai_portfolio(self):
        """Consolidate all email files to AI portfolio directory"""
        print("\n📂 Consolidating email files to AI portfolio...")
        
        # Copy email files from SURVIVE to AI portfolio if they don't exist
        files_to_copy = [
            'email_application_tracker.py',
            'send_followup_email.py',
            'email_automation_setup.py',
            'test_email_automation.py'
        ]
        
        for file_name in files_to_copy:
            source = self.survive_dir / file_name
            dest = self.ai_portfolio_dir / file_name
            
            if source.exists() and not dest.exists():
                shutil.copy2(source, dest)
                self.cleanup_report['consolidated'].append(file_name)
                print(f"  ✅ Consolidated: {file_name}")
    
    def create_email_config(self):
        """Create unified email configuration file"""
        print("\n⚙️  Creating unified email configuration...")
        
        config = {
            "email_settings": {
                "primary_email": "matthewdscott7@gmail.com",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 465,
                "use_ssl": True
            },
            "bcc_tracking": {
                "enabled": True,
                "addresses": {
                    "applications": "matthewdscott7+jobapps@gmail.com",
                    "followups": "matthewdscott7+followups@gmail.com",
                    "networking": "matthewdscott7+networking@gmail.com"
                }
            },
            "gmail_oauth": {
                "enabled": True,
                "monitored_companies": [
                    "Anthropic", "Netflix", "CoreWeave", "Scale AI", 
                    "Airtable", "Canva", "Checkr", "Flexport", "Gusto",
                    "Instacart", "Plaid", "Robinhood", "Samsara", 
                    "Snowflake", "Affirm"
                ]
            },
            "followup_schedule": {
                "initial": 3,
                "second": 7,
                "final": 14
            },
            "templates": {
                "signature": "\n\nBest regards,\nMatthew Scott\nmatthewdscott7@gmail.com\n(502) 345-0525\nlinkedin.com/in/mscott77"
            }
        }
        
        config_path = self.ai_portfolio_dir / "email_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.cleanup_report['created'].append('email_config.json')
        print("  ✅ Created: email_config.json")
    
    def create_setup_script(self):
        """Create easy setup script for email system"""
        print("\n📝 Creating setup script...")
        
        setup_content = '''#!/usr/bin/env python3
"""
Quick Setup for Email Automation System
Run this to configure everything needed for email tracking
"""

import os
import sys
from pathlib import Path

def setup_email_automation():
    print("🚀 Email Automation Setup")
    print("=" * 60)
    
    # Check for .env file
    if not Path('.env').exists():
        print("\\n⚠️  No .env file found!")
        print("\\nCreating .env template...")
        
        env_template = """# Email Configuration
EMAIL_ADDRESS=matthewdscott7@gmail.com
EMAIL_APP_PASSWORD=your-16-char-app-password
EMAIL_NAME=Matthew David Scott

# Optional
BACKUP_EMAIL=your.backup@email.com
"""
        
        with open('.env', 'w') as f:
            f.write(env_template)
        
        print("✅ Created .env template")
        print("\\n⚠️  IMPORTANT: Add your Gmail app password to .env")
        print("\\nTo get app password:")
        print("1. Enable 2FA at: https://myaccount.google.com/security")
        print("2. Generate app password at: https://myaccount.google.com/apppasswords")
        return False
    
    # Test email configuration
    print("\\n🧪 Testing email configuration...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        email = os.getenv('EMAIL_ADDRESS')
        password = os.getenv('EMAIL_APP_PASSWORD')
        
        if not password or password == 'your-16-char-app-password':
            print("❌ Email app password not configured in .env")
            return False
        
        print(f"✅ Email: {email}")
        print("✅ App password: ******* (hidden)")
        
        # Test imports
        print("\\n📦 Checking dependencies...")
        try:
            import smtplib
            import ssl
            from email.mime.text import MIMEText
            print("✅ Email libraries available")
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            return False
        
        print("\\n✅ Email automation ready to use!")
        print("\\nQuick start commands:")
        print("  python unified_email_automation.py --report   # Generate report")
        print("  python unified_email_automation.py --sync     # Sync all systems")
        print("  python unified_email_automation.py --loop     # Run automation")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

if __name__ == "__main__":
    if setup_email_automation():
        sys.exit(0)
    else:
        sys.exit(1)
'''
        
        setup_path = self.ai_portfolio_dir / "setup_email.py"
        with open(setup_path, 'w') as f:
            f.write(setup_content)
        
        os.chmod(setup_path, 0o755)
        self.cleanup_report['created'].append('setup_email.py')
        print("  ✅ Created: setup_email.py")
    
    def fix_gmail_oauth_setup(self):
        """Fix the f-string error in setup_gmail_oauth.py"""
        print("\n🔧 Fixing Gmail OAuth setup script...")
        
        setup_file = self.ai_portfolio_dir / "setup_gmail_oauth.py"
        if setup_file.exists():
            # Read the file
            with open(setup_file, 'r') as f:
                content = f.read()
            
            # Fix the f-string issue by escaping braces
            # Find and replace the problematic pattern
            if 'f"Your brand represents {company}' in content:
                content = content.replace(
                    'f"Your brand represents {company}',
                    'f"Your brand represents {{company}}'
                )
                
                # Write back
                with open(setup_file, 'w') as f:
                    f.write(content)
                
                self.cleanup_report['consolidated'].append('Fixed setup_gmail_oauth.py f-string error')
                print("  ✅ Fixed f-string formatting error")
        else:
            print("  ⚠️  setup_gmail_oauth.py not found")
    
    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        print("\n📊 Generating cleanup report...")
        
        # Add recommendations
        self.cleanup_report['recommendations'] = [
            "1. Run 'python setup_email.py' to configure email system",
            "2. Add Gmail app password to .env file",
            "3. Set up Gmail filters for BCC addresses",
            "4. Test with 'python unified_email_automation.py --report'",
            "5. Schedule daily runs with Claude Code or cron"
        ]
        
        # Save report
        report_path = self.ai_portfolio_dir / "EMAIL_CLEANUP_REPORT.md"
        
        with open(report_path, 'w') as f:
            f.write("# Email System Cleanup Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write("The email tracking system has been assessed and enhanced with:\n")
            f.write("- BCC tracking capability\n")
            f.write("- Unified automation system\n")
            f.write("- Consolidated file structure\n")
            f.write("- Fixed configuration issues\n\n")
            
            f.write("## Actions Taken\n\n")
            
            if self.cleanup_report['backed_up']:
                f.write(f"### Backed Up ({len(self.cleanup_report['backed_up'])} files)\n")
                for file in self.cleanup_report['backed_up']:
                    f.write(f"- {file}\n")
                f.write(f"\nBackup location: `{self.backup_dir}`\n\n")
            
            if self.cleanup_report['consolidated']:
                f.write(f"### Consolidated ({len(self.cleanup_report['consolidated'])} items)\n")
                for item in self.cleanup_report['consolidated']:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            if self.cleanup_report['created']:
                f.write(f"### Created ({len(self.cleanup_report['created'])} files)\n")
                for file in self.cleanup_report['created']:
                    f.write(f"- {file}\n")
                f.write("\n")
            
            if self.cleanup_report['errors']:
                f.write(f"### Errors ({len(self.cleanup_report['errors'])})\n")
                for error in self.cleanup_report['errors']:
                    f.write(f"- ❌ {error}\n")
                f.write("\n")
            
            f.write("## Email Tracking Methods\n\n")
            f.write("1. **Manual Logging** - Track sent applications in CSV/JSON\n")
            f.write("2. **Gmail OAuth** - Monitor responses from 15 companies\n")
            f.write("3. **BCC Tracking** - Automatic capture via +aliases\n")
            f.write("4. **Unified System** - Combines all methods\n\n")
            
            f.write("## Next Steps\n\n")
            for i, rec in enumerate(self.cleanup_report['recommendations'], 1):
                f.write(f"{rec}\n")
            
            f.write("\n## File Structure\n\n")
            f.write("```\n")
            f.write("ai-talent-optimizer/\n")
            f.write("├── email_application_tracker.py    # Core tracking\n")
            f.write("├── gmail_oauth_integration.py      # Response monitoring\n")
            f.write("├── bcc_email_tracker.py           # BCC enhancement\n")
            f.write("├── unified_email_automation.py     # Combined system\n")
            f.write("├── send_followup_email.py         # Follow-up automation\n")
            f.write("├── email_automation_setup.py      # Configuration\n")
            f.write("├── setup_email.py                 # Quick setup script\n")
            f.write("├── email_config.json              # Unified config\n")
            f.write("└── .env                          # Credentials (create this)\n")
            f.write("```\n")
        
        print(f"  ✅ Report saved to: {report_path}")
        
        return report_path
    
    def run_cleanup(self):
        """Run complete cleanup process"""
        print("🧹 Email System Cleanup")
        print("=" * 60)
        
        # Step 1: Backup
        self.backup_existing_files()
        
        # Step 2: Consolidate
        self.consolidate_to_ai_portfolio()
        
        # Step 3: Create config
        self.create_email_config()
        
        # Step 4: Create setup script
        self.create_setup_script()
        
        # Step 5: Fix known issues
        self.fix_gmail_oauth_setup()
        
        # Step 6: Generate report
        report_path = self.generate_cleanup_report()
        
        print("\n✅ Cleanup complete!")
        print(f"\n📄 See full report: {report_path}")
        print("\n🚀 Next step: Run 'python setup_email.py' to configure")


def main():
    """Run email system cleanup"""
    cleanup = EmailSystemCleanup()
    cleanup.run_cleanup()


if __name__ == "__main__":
    main()