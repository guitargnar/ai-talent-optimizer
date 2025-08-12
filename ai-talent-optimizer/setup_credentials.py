#!/usr/bin/env python3
"""
Set up credentials and test connectivity
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_credentials():
    """Verify all credentials are loaded"""
    
    print("🔐 Verifying Credentials...")
    print("="*50)
    
    credentials = {
        "EMAIL_ADDRESS": os.getenv("EMAIL_ADDRESS"),
        "EMAIL_APP_PASSWORD": os.getenv("EMAIL_APP_PASSWORD"),
        "ADZUNA_APP_ID": os.getenv("ADZUNA_APP_ID"),
        "ADZUNA_APP_KEY": os.getenv("ADZUNA_APP_KEY")
    }
    
    all_good = True
    
    for key, value in credentials.items():
        if value:
            masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
            print(f"✅ {key}: {masked_value}")
        else:
            print(f"❌ {key}: Not found")
            all_good = False
    
    print("\n" + "="*50)
    
    if all_good:
        print("✅ All credentials found!")
        
        # Test Adzuna
        print("\n🔍 Testing Adzuna API...")
        try:
            import requests
            url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
            params = {
                "app_id": credentials["ADZUNA_APP_ID"],
                "app_key": credentials["ADZUNA_APP_KEY"],
                "what": "machine learning",
                "results_per_page": 1
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                print("✅ Adzuna API working!")
                data = response.json()
                print(f"   Found {data.get('count', 0)} ML jobs")
            else:
                print(f"❌ Adzuna API error: {response.status_code}")
        except Exception as e:
            print(f"❌ Adzuna test failed: {e}")
        
        # Test Gmail (without OAuth for now)
        print("\n📧 Gmail credentials configured")
        print("   Run 'python setup_gmail_oauth.py' to authenticate")
        
    else:
        print("❌ Some credentials are missing!")
        print("\nTo fix:")
        print("1. Check .env file exists")
        print("2. Ensure all values are set")
        print("3. No spaces around = signs")
    
    return all_good

def update_config_files():
    """Update config files to use environment variables"""
    
    print("\n📝 Updating configuration files...")
    
    # Update the free job scraper to use env vars
    config_updates = [
        ("/Users/matthewscott/SURVIVE/career-automation/real-tracker/career-automation/interview-prep/free_job_scraper.py",
         "self.adzuna_app_id = None",
         "self.adzuna_app_id = os.getenv('ADZUNA_APP_ID')"),
        ("/Users/matthewscott/SURVIVE/career-automation/real-tracker/career-automation/interview-prep/free_job_scraper.py",
         "self.adzuna_app_key = None",
         "self.adzuna_app_key = os.getenv('ADZUNA_APP_KEY')")
    ]
    
    for file_path, old_line, new_line in config_updates:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if old_line in content:
                    content = content.replace(old_line, new_line)
                    print(f"✅ Updated {os.path.basename(file_path)}")
                else:
                    print(f"⚠️  Pattern not found in {os.path.basename(file_path)}")
                    
            except Exception as e:
                print(f"❌ Error updating {file_path}: {e}")

def main():
    """Main setup function"""
    
    print("🚀 AI Talent Optimizer - Credential Setup")
    print("="*50)
    
    # First verify credentials
    if verify_credentials():
        print("\n✅ Setup complete!")
        print("\n🎯 Next steps:")
        print("1. Run: python setup_gmail_oauth.py")
        print("2. Test: python unified_ai_hunter.py --test")
        print("3. Check Claude Code pipeline: claude run check_status")
    else:
        print("\n❌ Setup incomplete - fix credentials first")

if __name__ == "__main__":
    main()