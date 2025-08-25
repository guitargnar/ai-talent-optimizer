#!/usr/bin/env python3
"""
Safety Check Script - Monitor and Control Automated Sending
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def check_safety_status():
    """Check if auto-send is disabled"""
    safety_flag = Path(__file__).parent / "DISABLE_AUTO_SEND.txt"
    
    print("="*60)
    print("🔒 AI TALENT OPTIMIZER SAFETY CHECK")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check safety flag
    if safety_flag.exists():
        print("\n✅ SAFETY MODE: ENABLED")
        print("   Auto-sending is DISABLED")
        print("   Applications require manual approval via orchestrator.py")
        
        with open(safety_flag) as f:
            content = f.read()
            print(f"\n   Safety flag contents:")
            for line in content.split('\n')[:5]:
                print(f"   {line}")
    else:
        print("\n⚠️  SAFETY MODE: DISABLED")
        print("   Auto-sending is ENABLED")
        print("   Scripts can send without approval")
    
    # Check for cron jobs
    print("\n" + "-"*60)
    print("📅 CHECKING FOR SCHEDULED AUTOMATION:")
    
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout:
            job_keywords = ['maximize_claude', 'ollama_job', 'quality_first', 'automated_apply', 'batch_send']
            found_jobs = []
            for line in result.stdout.split('\n'):
                if any(keyword in line for keyword in job_keywords):
                    found_jobs.append(line)
            
            if found_jobs:
                print("\n⚠️  FOUND AUTOMATION CRON JOBS:")
                for job in found_jobs:
                    print(f"   {job}")
            else:
                print("   ✅ No job automation cron jobs found")
        else:
            print("   ✅ No cron jobs configured")
    except:
        print("   ✅ No cron system active")
    
    # Check for running processes
    print("\n" + "-"*60)
    print("🔄 CHECKING FOR RUNNING PROCESSES:")
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = []
        keywords = ['maximize_claude_value', 'quality_first_apply', 'automated_apply', 'batch_send_smtp']
        
        for line in result.stdout.split('\n'):
            if any(keyword in line for keyword in keywords) and 'grep' not in line:
                processes.append(line[:100])  # First 100 chars
        
        if processes:
            print("\n⚠️  FOUND RUNNING AUTOMATION:")
            for proc in processes:
                print(f"   {proc}")
        else:
            print("   ✅ No automation processes running")
    except:
        print("   ✅ Could not check processes")
    
    # Provide options
    print("\n" + "="*60)
    print("🎮 CONTROL OPTIONS:")
    print("="*60)
    
    if safety_flag.exists():
        print("\nTo RE-ENABLE auto-sending:")
        print("  rm DISABLE_AUTO_SEND.txt")
        print("\nTo use human-in-the-loop approval:")
        print("  python3 orchestrator.py")
    else:
        print("\nTo DISABLE auto-sending:")
        print("  touch DISABLE_AUTO_SEND.txt")
        print("\nTo send with approval:")
        print("  python3 orchestrator.py")
    
    print("\nTo check recent emails sent:")
    print("  python3 true_metrics_dashboard.py")
    
    print("\n" + "="*60)

def disable_all_automation():
    """Emergency stop for all automation"""
    print("\n🚨 EMERGENCY STOP - Disabling all automation...")
    
    # Create safety flag
    safety_flag = Path(__file__).parent / "DISABLE_AUTO_SEND.txt"
    if not safety_flag.exists():
        safety_flag.write_text(f"EMERGENCY STOP\nDisabled: {datetime.now()}\n")
        print("✅ Created safety flag - auto-send disabled")
    
    # Kill any running Python automation
    keywords = ['maximize_claude_value', 'quality_first_apply', 'automated_apply', 'batch_send']
    for keyword in keywords:
        os.system(f"pkill -f 'python.*{keyword}' 2>/dev/null")
    
    print("✅ Terminated any running automation processes")
    print("✅ System is now in SAFE MODE")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--emergency-stop":
        disable_all_automation()
    else:
        check_safety_status()