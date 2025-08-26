#!/usr/bin/env python3
"""
Check the status of your $400K+ automation campaign
Shows what's been done and what's pending
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import os

def check_principal_jobs():
    """Check status of principal job applications"""
    db_path = "unified_platform.db"
    if not Path(db_path).exists():
        print("❌ No principal jobs database found yet")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM jobs")
    result = cursor.fetchone()
    total = result[0] if result else 0
    
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied = 1")
    result = cursor.fetchone()
    applied = result[0] if result else 0
    
    cursor.execute("SELECT company, title, min_salary FROM jobs WHERE applied = 0 LIMIT 5")
    pending = cursor.fetchall()
    
    conn.close()
    
    print(f"""
📊 PRINCIPAL JOBS STATUS:
  Total opportunities found: {total}
  Applications sent: {applied}
  Pending applications: {total - applied}
    """)
    
    if pending:
        print("  Next targets:")
        for job in pending:
            print(f"    - {job[0]}: {job[1]} (${job[2]:,}+)")

def check_ceo_outreach():
    """Check status of CEO outreach"""
    db_path = "unified_platform.db"
    if not Path(db_path).exists():
        print("❌ No CEO outreach database found yet")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM contacts")
    result = cursor.fetchone()
    total = result[0] if result else 0
    
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE contacted = 1")
    result = cursor.fetchone()
    contacted = result[0] if result else 0
    
    cursor.execute("SELECT company, name FROM contacts WHERE contacted = 0 LIMIT 5")
    pending = cursor.fetchall()
    
    conn.close()
    
    print(f"""
📧 CEO OUTREACH STATUS:
  Total CEOs identified: {total}
  Outreach sent: {contacted}
  Pending outreach: {total - contacted}
    """)
    
    if pending:
        print("  Next targets:")
        for ceo in pending:
            print(f"    - {ceo[0]}: {ceo[1] or 'CEO'}")

def check_csv_trackers():
    """Check CSV tracker updates"""
    master_tracker = Path("MASTER_TRACKER_400K.csv")
    
    if master_tracker.exists():
        df = pd.read_csv(master_tracker)
        
        # Count statuses
        todo_count = len(df[df['Status'] == 'TODO'])
        done_count = len(df[df['Status'] == 'DONE'])
        applied_count = len(df[df['Status'] == 'APPLIED'])
        
        print(f"""
📋 CSV TRACKER STATUS:
  TODO items: {todo_count}
  COMPLETED items: {done_count}
  APPLIED positions: {applied_count}
        """)
        
        # Show recent automation logs
        automation_logs = df[df['Section'] == 'AUTOMATION_LOG'].tail(5)
        if not automation_logs.empty:
            print("\n  Recent automation activity:")
            for _, log in automation_logs.iterrows():
                print(f"    - {log['Date']}: {log['Item']}")
    else:
        print("❌ Master tracker CSV not found")

def check_output_folders():
    """Check what's been generated"""
    folders = {
        'applications_sent': 'Application letters',
        'ceo_outreach_sent': 'CEO emails',
        'daily_reports': 'Daily reports'
    }
    
    print("\n📁 OUTPUT FILES:")
    for folder, description in folders.items():
        folder_path = Path(folder)
        if folder_path.exists():
            files = list(folder_path.glob('*'))
            print(f"  {description}: {len(files)} files")
            if files:
                # Show most recent 3
                recent = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
                for f in recent:
                    print(f"    - {f.name}")
        else:
            print(f"  {description}: Folder not created yet")

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║      $400K+ AUTOMATION STATUS CHECK                       ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print(f"Status as of: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    check_principal_jobs()
    check_ceo_outreach()
    check_csv_trackers()
    check_output_folders()
    
    print("""
═══════════════════════════════════════════════════════════

💡 NEXT ACTIONS:
1. Run: python run_immediate_automation.py (for full blast)
2. Run: python principal_role_hunter.py (for job applications)
3. Run: python ceo_outreach_bot.py (for CEO contacts)
4. Check MASTER_TRACKER_400K.csv for detailed status

Your path to $400K+ requires consistent daily execution!
    """)

if __name__ == "__main__":
    main()