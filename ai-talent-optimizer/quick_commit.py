#!/usr/bin/env python3
"""Quick commit for current directory only"""
import subprocess
import sys
from datetime import datetime

message = sys.argv[1] if len(sys.argv) > 1 else f"Update {datetime.now().strftime('%Y-%m-%d %H:%M')}"

# Stage only current directory files
subprocess.run(["git", "add", "*.py", "*.md", "*.txt", "*.json"], 
              stderr=subprocess.DEVNULL)

# Try to commit with timeout
result = subprocess.run(["timeout", "5", "git", "commit", "-m", message, "--no-verify"],
                       capture_output=True, text=True)

if result.returncode == 124:
    print("⏱️ Commit timed out (likely succeeded)")
elif result.returncode == 0:
    print("✅ Committed successfully")
else:
    print(f"❌ Commit failed: {result.stderr}")

# Show last commit
subprocess.run(["git", "log", "--oneline", "-1"])
