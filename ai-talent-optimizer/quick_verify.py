#!/usr/bin/env python3
"""Quick verification - no interaction needed"""
import subprocess
from pathlib import Path
from datetime import datetime

print(f"⚡ QUICK METRICS CHECK - {datetime.now().strftime('%H:%M:%S')}")
print("="*50)

# Count files
py_files = len(list(Path.cwd().glob("*.py")))
db_files = len(list(Path.cwd().glob("*.db")))

# Check MCP
result = subprocess.run(['pgrep', '-f', 'mcp-server'], capture_output=True, text=True)
mcp_count = len(result.stdout.strip().split('\n')) if result.stdout else 0

# Today's changes
today = datetime.now().date()
modified = sum(1 for f in Path.cwd().glob("*.py") 
              if datetime.fromtimestamp(f.stat().st_mtime).date() == today)

print(f"Python modules: {py_files}")
print(f"Databases: {db_files}")
print(f"MCP servers: {mcp_count}")
print(f"Modified today: {modified}")
print("="*50)
