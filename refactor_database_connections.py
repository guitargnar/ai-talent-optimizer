#!/usr/bin/env python3
"""
Database Connection Refactoring Tool
====================================
Updates all Python files to use the unified database schema.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict
import shutil
from datetime import datetime

class DatabaseRefactorer:
    def __init__(self):
        self.unified_db = 'unified_platform.db'
        self.backup_dir = f'refactor_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        # Old database names to replace
        self.old_databases = [
            'ai_talent_optimizer.db',
            'APPLICATION_TRACKING.db',
            'campaign_tracking.db', 
            'career_automation.db',
            'ceo_outreach.db',
            'COMPANY_RESEARCH.db',
            'data/applications.db',
            'data/european_jobs.db',
            'data/linkedin_jobs.db',
            'data/unified_jobs.db',
            'job_applications.db',
            'principal_jobs_400k.db',
            'QUALITY_APPLICATIONS.db',
            'REAL_JOBS.db',
            'UNIFIED_AI_JOBS.db',
            'unified_career.db',
            'unified_career_system/data_layer/unified_career.db',
            'unified_talent_optimizer.db',
            'verified_metrics.db',
            'your_profile.db'
        ]
        
        # Table mapping from old to new
        self.table_mappings = {
            # Old table -> New table
            'job_discoveries': 'jobs',
            'job_opportunities': 'jobs',
            'principal_jobs': 'jobs',
            'european_jobs': 'jobs',
            'linkedin_jobs': 'jobs',
            'master_jobs': 'jobs',
            
            'staged_applications': 'applications',
            'unified_applications': 'applications',
            'quality_applications': 'applications',
            'application_tracking': 'applications',
            'master_applications': 'applications',
            
            'ceo_contacts': 'contacts',
            'key_contacts': 'contacts',
            'company_people': 'contacts',
            
            'gmail_responses': 'emails',
            'responses': 'emails',
            'email_tracking': 'emails',
            
            'company_research': 'companies',
            'company_intelligence': 'companies',
            
            'verified_metrics': 'metrics',
            'platform_metrics': 'metrics',
            'campaign_metrics': 'metrics',
            
            'professional_identity': 'profile',
            'profiles': 'profile'
        }
        
        # Column mappings
        self.column_mappings = {
            'jobs': {
                'company_name': 'company',
                'job_title': 'title',
                'position': 'title',
                'link': 'url',
                'min_salary': 'salary_min',
                'max_salary': 'salary_max',
                'remote': 'remote_type',
                'created_at': 'discovered_date'
            },
            'applications': {
                'company_name': 'company_name',
                'job_title': 'position',
                'role': 'position',
                'application_date': 'applied_date',
                'application_method': 'method',
                'resume_path': 'resume_version',
                'email_sent': 'status'
            },
            'contacts': {
                'name': 'full_name',
                'ceo_name': 'full_name',
                'contacted_date': 'contacted_date'
            }
        }
        
        self.files_refactored = []
        self.errors = []
    
    def backup_files(self, files: List[str]) -> None:
        """Create backup of all files before refactoring."""
        os.makedirs(self.backup_dir, exist_ok=True)
        for file_path in files:
            if Path(file_path).exists():
                backup_path = Path(self.backup_dir) / Path(file_path).name
                shutil.copy2(file_path, backup_path)
    
    def find_python_files(self) -> List[str]:
        """Find all Python files that connect to databases."""
        python_files = []
        
        # Search patterns
        patterns = [
            r'sqlite3\.connect',
            r'\.db[\'"\)]',
            r'DATABASE_PATH',
            r'db_path'
        ]
        
        for py_file in Path('.').glob('**/*.py'):
            # Skip backup directories and virtual environments
            if any(skip in str(py_file) for skip in ['backup', 'venv', 'ml-env', '__pycache__']):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in patterns:
                        if re.search(pattern, content):
                            python_files.append(str(py_file))
                            break
            except Exception:
                pass
        
        return python_files
    
    def refactor_database_connections(self, content: str) -> str:
        """Refactor database connections in content."""
        # Replace database file references
        for old_db in self.old_databases:
            # Handle various quote styles and path formats
            content = re.sub(
                rf'["\']({re.escape(old_db)})["\']',
                f'"{self.unified_db}"',
                content
            )
            content = re.sub(
                rf'Path\(["\']({re.escape(old_db)})["\']\)',
                f'Path("{self.unified_db}")',
                content
            )
        
        # Update default database paths
        content = re.sub(
            r'DEFAULT_DB\s*=\s*["\'][^"\']+\.db["\']',
            f'DEFAULT_DB = "{self.unified_db}"',
            content
        )
        
        content = re.sub(
            r'DATABASE_PATH\s*=\s*["\'][^"\']+\.db["\']',
            f'DATABASE_PATH = "{self.unified_db}"',
            content
        )
        
        content = re.sub(
            r'db_path\s*=\s*["\'][^"\']+\.db["\']',
            f'db_path = "{self.unified_db}"',
            content
        )
        
        return content
    
    def refactor_table_names(self, content: str) -> str:
        """Refactor table names in SQL queries."""
        for old_table, new_table in self.table_mappings.items():
            # Update FROM clauses
            content = re.sub(
                rf'FROM\s+{old_table}\b',
                f'FROM {new_table}',
                content,
                flags=re.IGNORECASE
            )
            
            # Update INSERT INTO
            content = re.sub(
                rf'INSERT\s+INTO\s+{old_table}\b',
                f'INSERT INTO {new_table}',
                content,
                flags=re.IGNORECASE
            )
            
            # Update UPDATE statements
            content = re.sub(
                rf'UPDATE\s+{old_table}\b',
                f'UPDATE {new_table}',
                content,
                flags=re.IGNORECASE
            )
            
            # Update DELETE FROM
            content = re.sub(
                rf'DELETE\s+FROM\s+{old_table}\b',
                f'DELETE FROM {new_table}',
                content,
                flags=re.IGNORECASE
            )
            
            # Update CREATE TABLE IF NOT EXISTS
            content = re.sub(
                rf'CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+{old_table}\b',
                f'CREATE TABLE IF NOT EXISTS {new_table}',
                content,
                flags=re.IGNORECASE
            )
        
        return content
    
    def refactor_column_names(self, content: str) -> str:
        """Refactor column names in SQL queries."""
        for table, columns in self.column_mappings.items():
            for old_col, new_col in columns.items():
                if old_col != new_col:
                    # Update column references
                    content = re.sub(
                        rf'\b{old_col}\b(?=\s*[,\)=<>])',
                        new_col,
                        content
                    )
        
        return content
    
    def refactor_file(self, file_path: str) -> bool:
        """Refactor a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Skip if already using unified database
            if 'unified_platform.db' in original_content:
                return True
            
            # Apply refactoring
            content = original_content
            content = self.refactor_database_connections(content)
            content = self.refactor_table_names(content)
            content = self.refactor_column_names(content)
            
            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_refactored.append(file_path)
                return True
            
            return True
            
        except Exception as e:
            self.errors.append(f"{file_path}: {str(e)}")
            return False
    
    def add_database_config(self) -> None:
        """Create centralized database configuration."""
        config_content = '''#!/usr/bin/env python3
"""
Unified Database Configuration
==============================
Central configuration for the unified platform database.
"""

import os
from pathlib import Path

# Database Configuration
UNIFIED_DB_PATH = os.environ.get('UNIFIED_DB_PATH', 'unified_platform.db')
UNIFIED_DB = Path(UNIFIED_DB_PATH)

# Ensure database exists
if not UNIFIED_DB.exists():
    raise FileNotFoundError(f"Unified database not found: {UNIFIED_DB}")

# Table names
class Tables:
    COMPANIES = 'companies'
    JOBS = 'jobs'
    APPLICATIONS = 'applications'
    CONTACTS = 'contacts'
    EMAILS = 'emails'
    METRICS = 'metrics'
    PROFILE = 'profile'
    SYSTEM_LOG = 'system_log'

# View names
class Views:
    ACTIVE_JOBS = 'active_jobs'
    APPLICATION_RESPONSES = 'application_responses'
    CONTACT_NETWORK = 'contact_network'

def get_connection():
    """Get a connection to the unified database."""
    import sqlite3
    return sqlite3.connect(str(UNIFIED_DB))

def get_db_path():
    """Get the path to the unified database."""
    return str(UNIFIED_DB)
'''
        
        with open('unified_db_config.py', 'w') as f:
            f.write(config_content)
        
        print("✅ Created unified_db_config.py")
    
    def run_refactoring(self) -> bool:
        """Execute the refactoring process."""
        print("="*70)
        print("DATABASE CONNECTION REFACTORING")
        print("="*70)
        
        # Find files to refactor
        print("\n🔍 Finding Python files with database connections...")
        python_files = self.find_python_files()
        print(f"   Found {len(python_files)} files")
        
        # Create backups
        print("\n📦 Creating backups...")
        self.backup_files(python_files)
        print(f"   Backed up to: {self.backup_dir}/")
        
        # Refactor files
        print("\n🔧 Refactoring database connections...")
        success_count = 0
        for file_path in python_files:
            if self.refactor_file(file_path):
                success_count += 1
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path}")
        
        # Create config file
        self.add_database_config()
        
        # Print summary
        print("\n" + "="*70)
        print("REFACTORING SUMMARY")
        print("="*70)
        print(f"Files processed: {len(python_files)}")
        print(f"Files refactored: {len(self.files_refactored)}")
        print(f"Files unchanged: {len(python_files) - len(self.files_refactored)}")
        print(f"Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n⚠️  Errors encountered:")
            for error in self.errors[:5]:
                print(f"  - {error}")
        
        print(f"\n✅ Refactoring complete!")
        print(f"   Backup directory: {self.backup_dir}/")
        print(f"   Config file: unified_db_config.py")
        
        return len(self.errors) == 0


def main():
    """Main execution function."""
    refactorer = DatabaseRefactorer()
    
    print("🔄 Starting database connection refactoring...")
    print("   This will update all Python files to use unified_platform.db")
    print()
    
    if refactorer.run_refactoring():
        print("\n✅ REFACTORING COMPLETED SUCCESSFULLY")
        return 0
    else:
        print("\n⚠️  REFACTORING COMPLETED WITH WARNINGS")
        return 0  # Still success, just with warnings


if __name__ == "__main__":
    import sys
    sys.exit(main())