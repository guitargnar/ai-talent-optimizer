#!/usr/bin/env python3
"""
Patch unified_ai_hunter.py to use real job discovery
"""

import os
import shutil
from datetime import datetime

def patch_unified_hunter():
    """Update unified_ai_hunter.py with real job discovery"""
    
    # Backup original
    backup_file = f"unified_ai_hunter.py.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy("unified_ai_hunter.py", backup_file)
    print(f"✅ Created backup: {backup_file}")
    
    # Read the file
    with open("unified_ai_hunter.py", 'r') as f:
        content = f.read()
    
    # Find the discover_ai_jobs method
    old_method = '''    def discover_ai_jobs(self, max_jobs: int = 50) -> List[Dict]:
        """Discover new AI/ML jobs from all sources"""
        logger.info(f"Discovering up to {max_jobs} new AI/ML jobs...")
        
        all_jobs = []
        
        # Simulate job discovery (in production, would use actual scrapers)
        # This is where you'd integrate EnhancedJobScraper
        
        logger.info(f"Discovered {len(all_jobs)} potential AI/ML jobs")
        return all_jobs'''
    
    new_method = '''    def discover_ai_jobs(self, max_jobs: int = 50) -> List[Dict]:
        """Discover new AI/ML jobs from all sources"""
        logger.info(f"Discovering up to {max_jobs} new AI/ML jobs...")
        
        # Use the job scraper integration
        try:
            from connect_job_scrapers import JobScraperIntegration
            scraper_integration = JobScraperIntegration()
            
            # Discover jobs
            jobs = scraper_integration.discover_ai_jobs(max_jobs)
            
            # Save to database
            if jobs:
                scraper_integration.save_to_unified_db(jobs)
            
            logger.info(f"Discovered {len(jobs)} potential AI/ML jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"Job discovery failed: {e}")
            logger.info("Falling back to manual job entry mode")
            return []'''
    
    # Replace the method
    if old_method in content:
        content = content.replace(old_method, new_method)
        
        # Write back
        with open("unified_ai_hunter.py", 'w') as f:
            f.write(content)
        
        print("✅ Successfully patched unified_ai_hunter.py")
        print("\n📝 Changes made:")
        print("- discover_ai_jobs() now uses real job scrapers")
        print("- Automatic fallback if scrapers fail")
        print("- Jobs saved to unified database")
        
        return True
    else:
        print("❌ Could not find the method to patch")
        print("The file may have already been modified")
        return False

def verify_dependencies():
    """Check if required dependencies are available"""
    print("\n🔍 Checking dependencies...")
    
    dependencies = {
        'selenium': False,
        'beautifulsoup4': False,
        'requests': True,  # Usually available
        'pandas': False
    }
    
    for dep in dependencies:
        try:
            __import__(dep.replace('beautifulsoup4', 'bs4'))
            dependencies[dep] = True
            print(f"✅ {dep}: Installed")
        except ImportError:
            print(f"❌ {dep}: Not installed")
    
    # Check career-automation modules
    import sys
    sys.path.append('/Users/matthewscott/SURVIVE/career-automation/real-tracker/career-automation/interview-prep')
    
    try:
        from free_job_scraper import FreeJobScraper
        print("✅ free_job_scraper: Available")
    except ImportError:
        print("❌ free_job_scraper: Not available")
    
    return all(dependencies.values())

def main():
    print("🔧 Unified AI Hunter Patcher")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists("unified_ai_hunter.py"):
        print("❌ Error: unified_ai_hunter.py not found")
        print("Please run this from the ai-talent-optimizer directory")
        return
    
    # Verify dependencies
    deps_ok = verify_dependencies()
    
    if not deps_ok:
        print("\n⚠️  Warning: Some dependencies are missing")
        print("The system will still work but with limited scraping capabilities")
        print("\nTo install missing dependencies:")
        print("pip install selenium beautifulsoup4 pandas")
    
    # Apply patch
    print("\n🚀 Applying patch...")
    success = patch_unified_hunter()
    
    if success:
        print("\n✅ Patch complete!")
        print("\n📝 Next steps:")
        print("1. Test job discovery: python connect_job_scrapers.py --test")
        print("2. Run unified hunter: python unified_ai_hunter.py")
        print("3. Select option 2 to discover new jobs")
        
        print("\n💡 The system will now:")
        print("- Try free API sources first (no auth needed)")
        print("- Fall back to web scraping if available")
        print("- Use hardcoded opportunities if all else fails")
    else:
        print("\n❌ Patch failed")
        print("Please check the file manually")

if __name__ == "__main__":
    main()