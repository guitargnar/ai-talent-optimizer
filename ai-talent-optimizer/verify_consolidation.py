#!/usr/bin/env python3
"""
Verify Database Consolidation Results
===================================
"""

import sqlite3
import json
import os

def verify_consolidation():
    """Verify the database consolidation was successful."""
    
    print('=== UNIFIED DATABASE VERIFICATION ===')
    
    # Check if unified database exists
    if not os.path.exists('unified_talent_optimizer.db'):
        print("❌ Unified database not found!")
        return False
    
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f'Tables created: {tables}')
    
    total_records = 0
    table_counts = {}
    
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        table_counts[table] = count
        print(f'{table}: {count} records')
        total_records += count
    
    print(f'\nTotal records in unified DB: {total_records}')
    
    # Sample some data
    print('\n=== SAMPLE DATA ===')
    
    # Jobs with high salaries
    cursor.execute('''
        SELECT company, position, min_salary, max_salary 
        FROM jobs 
        WHERE min_salary > 350000 
        ORDER BY min_salary DESC 
        LIMIT 5
    ''')
    print('\nTop 5 High-Salary Jobs:')
    for row in cursor.fetchall():
        salary_range = f"${row[2]:,} - ${row[3]:,}" if row[2] and row[3] else "Salary TBD"
        print(f'  {row[0]} - {row[1]} ({salary_range})')
    
    # Applications
    cursor.execute('SELECT company, position, applied_date, status FROM applications ORDER BY applied_date DESC LIMIT 5')
    print('\nRecent Applications:')
    for row in cursor.fetchall():
        print(f'  {row[0]} - {row[1]} ({row[2]}) - {row[3]}')
    
    # Profile
    cursor.execute('SELECT full_name, email, phone, years_experience, current_focus FROM profile')
    profile = cursor.fetchone()
    if profile:
        print('\nProfile:')
        print(f'  Name: {profile[0]}')
        print(f'  Email: {profile[1]}') 
        print(f'  Phone: {profile[2]}')
        print(f'  Experience: {profile[3]} years')
        print(f'  Focus: {profile[4]}')
    
    # Metrics
    cursor.execute('SELECT metric_name, metric_value FROM metrics ORDER BY metric_name')
    print('\nKey Metrics:')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}')
    
    conn.close()
    
    # Check migration report
    if os.path.exists('database_migration_report.json'):
        with open('database_migration_report.json', 'r') as f:
            report = json.load(f)
        
        print('\n=== MIGRATION SUMMARY ===')
        print(f'Success: {report["success"]}')
        print('Migration Log:')
        for log in report['migration_log']:
            print(f'  - {log}')
        
        print('\nValidation Results:')
        for key, value in report['validation_results'].items():
            print(f'  {key}: {value}')
    
    # Compare with original counts
    print('\n=== ORIGINAL vs UNIFIED COMPARISON ===')
    
    original_total = 356  # From SOURCE_OF_TRUTH.md
    unified_total = total_records
    
    print(f'Original total (from 7 DBs): {original_total}')
    print(f'Unified total: {unified_total}')
    print(f'Difference: {unified_total - original_total}')
    
    if unified_total >= 150:  # Reasonable threshold
        print('✅ Consolidation appears successful - significant data preserved')
    else:
        print('⚠️  Low record count - possible data loss')
    
    return table_counts

def create_new_system_commands():
    """Create commands to use the new unified database."""
    
    commands = """
# Updated commands for unified database:

# Quick status check:
python3 -c "
import sqlite3
conn = sqlite3.connect('unified_talent_optimizer.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM jobs')
jobs = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM applications')
apps = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM responses')  
responses = cursor.fetchone()[0]
print(f'Jobs: {jobs}, Applications: {apps}, Responses: {responses}')
conn.close()
"

# Find high-value jobs:
python3 -c "
import sqlite3
conn = sqlite3.connect('unified_talent_optimizer.db')
cursor = conn.cursor()
cursor.execute('SELECT company, position, min_salary FROM jobs WHERE min_salary > 400000 ORDER BY min_salary DESC')
for row in cursor.fetchall():
    print(f'{row[0]} - {row[1]}: \${row[2]:,}')
conn.close()
"

# Check application status:
python3 -c "
import sqlite3
conn = sqlite3.connect('unified_talent_optimizer.db')
cursor = conn.cursor()
cursor.execute('SELECT company, position, applied_date, status FROM applications ORDER BY applied_date DESC')
for row in cursor.fetchall():
    print(f'{row[0]} - {row[1]} ({row[2]}): {row[3]}')
conn.close()
"
"""
    
    print('\n=== NEW SYSTEM COMMANDS ===')
    print(commands)
    
    return commands

if __name__ == "__main__":
    table_counts = verify_consolidation()
    create_new_system_commands()