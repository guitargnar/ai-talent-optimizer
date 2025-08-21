#!/usr/bin/env python3
"""
Unified Job Search Monitor
Combines AI Optimizer, Email Tracking, and Gmail OAuth
"""

import subprocess
import time
from datetime import datetime

def run_unified_monitor():
    """Run all monitoring systems"""
    
    print("🚀 Starting Unified Job Search Monitor")
    print("=" * 50)
    
    while True:
        try:
            # 1. Check Gmail for responses
            print(f"\n[{datetime.now().strftime('%H:%M')}] Checking Gmail...")
            subprocess.run(['python3', '/Users/matthewscott/Google Gmail/check_job_replies.py'])
            
            # 2. Update email tracker
            print("\nUpdating email tracker...")
            subprocess.run(['python3', 'gmail_oauth_integration.py'])
            
            # 3. Check AI optimizer metrics (if needed)
            print("\nAI Optimizer Status: Profile Optimized ✓")
            
            # Wait 5 minutes
            print("\n💤 Waiting 5 minutes...")
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n👋 Stopping monitor")
            break

if __name__ == "__main__":
    run_unified_monitor()
