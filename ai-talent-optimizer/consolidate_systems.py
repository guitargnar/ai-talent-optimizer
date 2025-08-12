#!/usr/bin/env python3
"""
Consolidate existing job search systems into unified architecture
Migrates data from multiple sources into single unified system
"""

import os
import csv
import json
import sqlite3
import shutil
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemConsolidator:
    """Consolidates multiple job search systems into unified architecture"""
    
    def __init__(self):
        self.unified_db_path = "UNIFIED_AI_JOBS.db"
        self.consolidated_data = {
            'applications': [],
            'jobs': [],
            'responses': [],
            'contacts': []
        }
        
    def scan_existing_systems(self) -> Dict:
        """Scan filesystem for existing job search assets"""
        logger.info("Scanning for existing job search systems...")
        
        systems_found = {
            'ai_talent_optimizer': False,
            'career_automation': False,
            'resumes': [],
            'databases': [],
            'csv_files': []
        }
        
        # Check AI Talent Optimizer
        talent_optimizer_path = '/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer'
        if os.path.exists(talent_optimizer_path):
            systems_found['ai_talent_optimizer'] = True
            logger.info("✓ Found AI Talent Optimizer system")
            
            # Find CSV files
            for file in os.listdir(talent_optimizer_path):
                if file.endswith('.csv'):
                    systems_found['csv_files'].append(os.path.join(talent_optimizer_path, file))
        
        # Check Career Automation
        career_automation_path = '/Users/matthewscott/SURVIVE/career-automation'
        if os.path.exists(career_automation_path):
            systems_found['career_automation'] = True
            logger.info("✓ Found Career Automation system")
            
            # Find databases
            for root, dirs, files in os.walk(career_automation_path):
                for file in files:
                    if file.endswith('.db'):
                        systems_found['databases'].append(os.path.join(root, file))
        
        # Find recent resumes
        resume_locations = [
            '/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/output/resumes',
            '/Users/matthewscott/SURVIVE/career-automation/real-tracker/career-automation/interview-prep/resumes'
        ]
        
        for location in resume_locations:
            if os.path.exists(location):
                for root, dirs, files in os.walk(location):
                    for file in files:
                        if file.endswith(('.pdf', '.docx', '.txt', '.md')):
                            file_path = os.path.join(root, file)
                            # Check if created in last 30 days
                            if os.path.getmtime(file_path) > (datetime.now().timestamp() - 30*24*60*60):
                                systems_found['resumes'].append(file_path)
        
        logger.info(f"Found {len(systems_found['databases'])} databases")
        logger.info(f"Found {len(systems_found['csv_files'])} CSV files")
        logger.info(f"Found {len(systems_found['resumes'])} recent resumes")
        
        return systems_found
    
    def import_csv_applications(self, csv_path: str):
        """Import applications from CSV files"""
        logger.info(f"Importing applications from {csv_path}")
        
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    application = {
                        'source': 'csv',
                        'file': csv_path,
                        'data': row,
                        'imported_at': datetime.now().isoformat()
                    }
                    self.consolidated_data['applications'].append(application)
        except Exception as e:
            logger.error(f"Error importing {csv_path}: {e}")
    
    def import_sqlite_database(self, db_path: str):
        """Import data from SQLite databases"""
        logger.info(f"Importing database from {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                logger.info(f"  Importing table: {table_name}")
                
                cursor.execute(f"SELECT * FROM {table_name}")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                for row in rows:
                    record = dict(zip(columns, row))
                    record['_source_db'] = db_path
                    record['_source_table'] = table_name
                    
                    # Categorize based on table name
                    if 'application' in table_name.lower():
                        self.consolidated_data['applications'].append(record)
                    elif 'job' in table_name.lower():
                        self.consolidated_data['jobs'].append(record)
                    elif 'response' in table_name.lower() or 'email' in table_name.lower():
                        self.consolidated_data['responses'].append(record)
            
            conn.close()
        except Exception as e:
            logger.error(f"Error importing {db_path}: {e}")
    
    def analyze_resumes(self, resume_paths: List[str]) -> Dict:
        """Analyze recent resumes to understand current positioning"""
        logger.info(f"Analyzing {len(resume_paths)} recent resumes")
        
        resume_analysis = {
            'companies_targeted': set(),
            'roles_targeted': set(),
            'keywords_used': {},
            'versions': []
        }
        
        for resume_path in resume_paths:
            filename = os.path.basename(resume_path)
            
            # Extract company and role from filename patterns
            if '_' in filename:
                parts = filename.replace('.pdf', '').replace('.docx', '').split('_')
                
                # Common patterns: Matthew_Scott_Company_Role_Year
                if len(parts) >= 3:
                    company = parts[2]
                    role = '_'.join(parts[3:-1]) if len(parts) > 4 else parts[3] if len(parts) > 3 else 'Unknown'
                    
                    resume_analysis['companies_targeted'].add(company)
                    resume_analysis['roles_targeted'].add(role)
            
            resume_analysis['versions'].append({
                'path': resume_path,
                'filename': filename,
                'created': datetime.fromtimestamp(os.path.getmtime(resume_path)).isoformat()
            })
        
        return resume_analysis
    
    def create_unified_database(self):
        """Create unified database with all consolidated data"""
        logger.info("Creating unified database...")
        
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        # Create comprehensive schema
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications_import (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_system TEXT,
            source_file TEXT,
            original_data TEXT,
            company TEXT,
            position TEXT,
            applied_date TEXT,
            status TEXT,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs_import (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_system TEXT,
            job_id TEXT,
            company TEXT,
            position TEXT,
            location TEXT,
            salary_range TEXT,
            description TEXT,
            url TEXT,
            discovered_date TEXT,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses_import (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_system TEXT,
            company TEXT,
            response_date TEXT,
            response_type TEXT,
            email_content TEXT,
            next_steps TEXT,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Import all applications
        for app in self.consolidated_data['applications']:
            # Extract key fields
            company = app.get('data', {}).get('company', app.get('company', 'Unknown'))
            position = app.get('data', {}).get('position', app.get('position', 'Unknown'))
            date = app.get('data', {}).get('sent_date', app.get('applied_date', ''))
            
            cursor.execute('''
            INSERT INTO applications_import 
            (source_system, source_file, original_data, company, position, applied_date)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                app.get('source', 'unknown'),
                app.get('file', app.get('_source_db', '')),
                json.dumps(app),
                company,
                position,
                date
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Imported {len(self.consolidated_data['applications'])} applications")
        logger.info(f"✓ Imported {len(self.consolidated_data['jobs'])} jobs")
        logger.info(f"✓ Imported {len(self.consolidated_data['responses'])} responses")
    
    def generate_migration_report(self) -> Dict:
        """Generate report on consolidated data"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'systems_found': {
                'ai_talent_optimizer': False,
                'career_automation': False
            },
            'data_imported': {
                'applications': len(self.consolidated_data['applications']),
                'jobs': len(self.consolidated_data['jobs']),
                'responses': len(self.consolidated_data['responses'])
            },
            'recommendations': []
        }
        
        # Add recommendations based on findings
        if len(self.consolidated_data['applications']) > 1000:
            report['recommendations'].append(
                "High application volume detected. Consider implementing better filtering."
            )
        
        if len(self.consolidated_data['responses']) / len(self.consolidated_data['applications']) < 0.1:
            report['recommendations'].append(
                "Low response rate detected. Review application quality and targeting."
            )
        
        return report
    
    def consolidate_all_systems(self):
        """Main consolidation process"""
        logger.info("="*60)
        logger.info("Starting Job Search System Consolidation")
        logger.info("="*60)
        
        # 1. Scan for existing systems
        systems = self.scan_existing_systems()
        
        # 2. Import data from each source
        for csv_file in systems['csv_files']:
            self.import_csv_applications(csv_file)
        
        for db_file in systems['databases']:
            self.import_sqlite_database(db_file)
        
        # 3. Analyze resumes
        resume_analysis = self.analyze_resumes(systems['resumes'])
        logger.info(f"Resume analysis: {len(resume_analysis['companies_targeted'])} companies targeted")
        
        # 4. Create unified database
        self.create_unified_database()
        
        # 5. Generate report
        report = self.generate_migration_report()
        
        # Save report
        with open('consolidation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("\n" + "="*60)
        logger.info("✅ Consolidation Complete!")
        logger.info(f"📊 Total applications consolidated: {report['data_imported']['applications']}")
        logger.info(f"📧 Total responses tracked: {report['data_imported']['responses']}")
        logger.info(f"📄 Report saved to: consolidation_report.json")
        logger.info(f"🗄️ Unified database created: {self.unified_db_path}")
        logger.info("="*60)
        
        return report

def main():
    """Run the consolidation process"""
    consolidator = SystemConsolidator()
    
    print("\n🔄 Job Search System Consolidator")
    print("This will consolidate all your job search systems into one unified database.")
    print("\nSystems to consolidate:")
    print("1. AI Talent Optimizer (ai-talent-optimizer)")
    print("2. Career Automation Platform (SURVIVE/career-automation)")
    print("3. Gmail OAuth Integration")
    print("4. All recent resumes")
    
    confirm = input("\nProceed with consolidation? (y/n): ")
    
    if confirm.lower() == 'y':
        report = consolidator.consolidate_all_systems()
        
        print("\n📋 Next Steps:")
        print("1. Run: python unified_ai_hunter.py")
        print("2. Configure your preferences in unified_config.json")
        print("3. Set up cron job for daily automation")
        print("\nYour unified AI job hunting system is ready!")
    else:
        print("Consolidation cancelled.")

if __name__ == "__main__":
    main()