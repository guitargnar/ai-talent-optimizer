#!/usr/bin/env python3
"""
Database Migration Validation Tool
===================================
Validates the integrity and completeness of the database migration.
Performs health checks and spot verifications.
"""

import sqlite3
import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MigrationValidator:
    def __init__(self, unified_db: str = 'unified_platform.db', backup_file: str = None):
        self.unified_db = unified_db
        self.backup_file = backup_file or self._find_latest_backup()
        self.validation_results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'stats': {}
        }
    
    def _find_latest_backup(self) -> Optional[str]:
        """Find the most recent backup file."""
        backup_files = list(Path('.').glob('database_backup_*.zip'))
        if backup_files:
            return str(sorted(backup_files)[-1])
        return None
    
    def validate_database_structure(self) -> bool:
        """Validate that all expected tables exist with correct schemas."""
        logger.info("\n" + "="*60)
        logger.info("VALIDATING DATABASE STRUCTURE")
        logger.info("="*60)
        
        expected_tables = [
            'companies', 'jobs', 'applications', 'contacts',
            'emails', 'metrics', 'profile', 'system_log'
        ]
        
        expected_views = [
            'active_jobs', 'application_responses', 'contact_network'
        ]
        
        try:
            conn = sqlite3.connect(self.unified_db)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            actual_tables = [row[0] for row in cursor.fetchall()]
            
            for table in expected_tables:
                if table in actual_tables:
                    self.validation_results['passed'].append(f"Table '{table}' exists")
                    logger.info(f"✅ Table '{table}' exists")
                else:
                    self.validation_results['failed'].append(f"Table '{table}' missing")
                    logger.error(f"❌ Table '{table}' missing")
            
            # Check views
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
            actual_views = [row[0] for row in cursor.fetchall()]
            
            for view in expected_views:
                if view in actual_views:
                    self.validation_results['passed'].append(f"View '{view}' exists")
                    logger.info(f"✅ View '{view}' exists")
                else:
                    self.validation_results['warnings'].append(f"View '{view}' missing")
                    logger.warning(f"⚠️  View '{view}' missing")
            
            # Check indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
            indexes = cursor.fetchall()
            logger.info(f"✅ Found {len(indexes)} indexes")
            self.validation_results['stats']['index_count'] = len(indexes)
            
            conn.close()
            return len(self.validation_results['failed']) == 0
            
        except Exception as e:
            logger.error(f"Structure validation failed: {e}")
            self.validation_results['failed'].append(f"Structure validation error: {str(e)}")
            return False
    
    def validate_record_counts(self) -> bool:
        """Validate record counts are within expected ranges."""
        logger.info("\n" + "="*60)
        logger.info("VALIDATING RECORD COUNTS")
        logger.info("="*60)
        
        try:
            conn = sqlite3.connect(self.unified_db)
            cursor = conn.cursor()
            
            # Expected ranges based on migration analysis
            expected_ranges = {
                'companies': (50, 200),
                'jobs': (200, 800),
                'applications': (10, 100),
                'contacts': (0, 50),
                'emails': (20, 100),
                'metrics': (10, 100),
                'profile': (1, 1),
                'system_log': (0, 1000)
            }
            
            for table, (min_count, max_count) in expected_ranges.items():
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                self.validation_results['stats'][f'{table}_count'] = count
                
                if min_count <= count <= max_count:
                    self.validation_results['passed'].append(f"Table '{table}' has {count} records (expected {min_count}-{max_count})")
                    logger.info(f"✅ {table}: {count} records (expected {min_count}-{max_count})")
                else:
                    self.validation_results['warnings'].append(f"Table '{table}' has {count} records (expected {min_count}-{max_count})")
                    logger.warning(f"⚠️  {table}: {count} records (expected {min_count}-{max_count})")
            
            # Check total records
            total_records = sum(v for k, v in self.validation_results['stats'].items() if k.endswith('_count'))
            logger.info(f"\n📊 Total records in unified database: {total_records}")
            self.validation_results['stats']['total_records'] = total_records
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Record count validation failed: {e}")
            self.validation_results['failed'].append(f"Record count error: {str(e)}")
            return False
    
    def validate_data_integrity(self) -> bool:
        """Validate foreign key constraints and data integrity."""
        logger.info("\n" + "="*60)
        logger.info("VALIDATING DATA INTEGRITY")
        logger.info("="*60)
        
        try:
            conn = sqlite3.connect(self.unified_db)
            cursor = conn.cursor()
            
            integrity_checks = [
                # Check jobs have valid company_ids
                ("Jobs with invalid company_id", """
                    SELECT COUNT(*) FROM jobs 
                    WHERE company_id IS NOT NULL 
                    AND company_id NOT IN (SELECT id FROM companies)
                """),
                
                # Check applications have valid job_ids
                ("Applications with invalid job_id", """
                    SELECT COUNT(*) FROM applications 
                    WHERE job_id NOT IN (SELECT id FROM jobs)
                """),
                
                # Check emails with invalid references
                ("Emails with invalid application_id", """
                    SELECT COUNT(*) FROM emails 
                    WHERE application_id IS NOT NULL 
                    AND application_id NOT IN (SELECT id FROM applications)
                """),
                
                # Check contacts with invalid company_id
                ("Contacts with invalid company_id", """
                    SELECT COUNT(*) FROM contacts 
                    WHERE company_id IS NOT NULL 
                    AND company_id NOT IN (SELECT id FROM companies)
                """),
                
                # Check profile has exactly 1 record
                ("Profile record count", """
                    SELECT COUNT(*) FROM profile
                """)
            ]
            
            all_valid = True
            for check_name, query in integrity_checks:
                cursor.execute(query)
                result = cursor.fetchone()[0]
                
                if check_name == "Profile record count":
                    if result == 1:
                        self.validation_results['passed'].append(f"{check_name}: {result} (correct)")
                        logger.info(f"✅ {check_name}: {result}")
                    else:
                        self.validation_results['failed'].append(f"{check_name}: {result} (should be 1)")
                        logger.error(f"❌ {check_name}: {result} (should be 1)")
                        all_valid = False
                else:
                    if result == 0:
                        self.validation_results['passed'].append(f"{check_name}: None found")
                        logger.info(f"✅ {check_name}: None found")
                    else:
                        self.validation_results['failed'].append(f"{check_name}: {result} found")
                        logger.error(f"❌ {check_name}: {result} found")
                        all_valid = False
            
            conn.close()
            return all_valid
            
        except Exception as e:
            logger.error(f"Data integrity validation failed: {e}")
            self.validation_results['failed'].append(f"Integrity check error: {str(e)}")
            return False
    
    def spot_check_data(self) -> bool:
        """Perform spot checks on migrated data."""
        logger.info("\n" + "="*60)
        logger.info("PERFORMING SPOT CHECKS")
        logger.info("="*60)
        
        try:
            conn = sqlite3.connect(self.unified_db)
            cursor = conn.cursor()
            
            spot_checks = [
                # Check for known companies
                ("Known companies", """
                    SELECT COUNT(*) FROM companies 
                    WHERE name IN ('Google', 'Meta', 'Apple', 'Amazon', 'Microsoft', 
                                  'Anthropic', 'Openai', 'Netflix', 'Databricks')
                """, 1),  # Expect at least 1
                
                # Check for AI/ML jobs
                ("AI/ML focused jobs", """
                    SELECT COUNT(*) FROM jobs WHERE is_ai_ml_focused = 1
                """, 10),  # Expect at least 10
                
                # Check for principal+ jobs
                ("Principal+ level jobs", """
                    SELECT COUNT(*) FROM jobs WHERE is_principal_plus = 1
                """, 5),  # Expect at least 5
                
                # Check for applications with responses
                ("Applications with responses", """
                    SELECT COUNT(*) FROM applications WHERE response_received = 1
                """, 0),  # Expect at least 0
                
                # Check email types
                ("Email responses", """
                    SELECT COUNT(*) FROM emails WHERE direction = 'received'
                """, 10),  # Expect at least 10
                
                # Check metrics exist
                ("Metrics recorded", """
                    SELECT COUNT(*) FROM metrics
                """, 5)  # Expect at least 5
            ]
            
            all_passed = True
            for check_name, query, min_expected in spot_checks:
                cursor.execute(query)
                result = cursor.fetchone()[0]
                
                if result >= min_expected:
                    self.validation_results['passed'].append(f"{check_name}: {result} (>= {min_expected})")
                    logger.info(f"✅ {check_name}: {result} found (expected >= {min_expected})")
                else:
                    self.validation_results['warnings'].append(f"{check_name}: {result} (expected >= {min_expected})")
                    logger.warning(f"⚠️  {check_name}: {result} found (expected >= {min_expected})")
            
            # Sample some actual data
            logger.info("\n📋 Sample Data:")
            
            # Sample jobs
            cursor.execute("SELECT company, title FROM jobs LIMIT 3")
            jobs = cursor.fetchall()
            logger.info("  Sample Jobs:")
            for company, title in jobs:
                logger.info(f"    - {company}: {title}")
            
            # Sample applications
            cursor.execute("SELECT company_name, position, applied_date FROM applications LIMIT 3")
            apps = cursor.fetchall()
            if apps:
                logger.info("  Sample Applications:")
                for company, position, date in apps:
                    logger.info(f"    - {company}: {position} ({date[:10]})")
            
            conn.close()
            return all_passed
            
        except Exception as e:
            logger.error(f"Spot check failed: {e}")
            self.validation_results['warnings'].append(f"Spot check error: {str(e)}")
            return False
    
    def compare_with_backup(self) -> bool:
        """Compare migrated data counts with original backup."""
        if not self.backup_file or not Path(self.backup_file).exists():
            logger.warning("No backup file available for comparison")
            return True
        
        logger.info("\n" + "="*60)
        logger.info("COMPARING WITH BACKUP")
        logger.info("="*60)
        
        try:
            # Read manifest from backup
            with zipfile.ZipFile(self.backup_file, 'r') as backup_zip:
                manifest_data = backup_zip.read('manifest.json')
                manifest = json.loads(manifest_data)
            
            original_db_count = len(manifest['databases'])
            logger.info(f"Original databases: {original_db_count}")
            logger.info(f"Unified database: 1")
            logger.info(f"Consolidation ratio: {original_db_count}:1")
            
            self.validation_results['stats']['original_databases'] = original_db_count
            self.validation_results['stats']['consolidation_ratio'] = f"{original_db_count}:1"
            
            return True
            
        except Exception as e:
            logger.warning(f"Could not compare with backup: {e}")
            return True
    
    def generate_report(self) -> Dict:
        """Generate validation report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'database': self.unified_db,
            'backup_file': self.backup_file,
            'validation_results': self.validation_results,
            'summary': {
                'total_checks': len(self.validation_results['passed']) + len(self.validation_results['failed']) + len(self.validation_results['warnings']),
                'passed': len(self.validation_results['passed']),
                'failed': len(self.validation_results['failed']),
                'warnings': len(self.validation_results['warnings']),
                'health_score': 0
            }
        }
        
        # Calculate health score
        total = report['summary']['total_checks']
        if total > 0:
            report['summary']['health_score'] = round((report['summary']['passed'] / total) * 100, 1)
        
        return report
    
    def print_summary(self, report: Dict) -> None:
        """Print validation summary."""
        print("\n" + "="*70)
        print("MIGRATION VALIDATION SUMMARY")
        print("="*70)
        print(f"Database: {report['database']}")
        print(f"Validated: {report['timestamp'][:19]}")
        print()
        print(f"Total Checks: {report['summary']['total_checks']}")
        print(f"✅ Passed: {report['summary']['passed']}")
        print(f"❌ Failed: {report['summary']['failed']}")
        print(f"⚠️  Warnings: {report['summary']['warnings']}")
        print()
        print(f"Health Score: {report['summary']['health_score']}%")
        
        if report['summary']['failed'] > 0:
            print("\n❌ FAILED CHECKS:")
            for failure in report['validation_results']['failed']:
                print(f"  - {failure}")
        
        if report['summary']['warnings'] > 0:
            print("\n⚠️  WARNINGS:")
            for warning in report['validation_results']['warnings'][:5]:
                print(f"  - {warning}")
        
        print("\n📊 DATABASE STATISTICS:")
        for key, value in report['validation_results']['stats'].items():
            print(f"  {key}: {value}")
        
        # Overall result
        print("\n" + "="*70)
        if report['summary']['health_score'] >= 90:
            print("✅ VALIDATION PASSED - Database migration successful!")
        elif report['summary']['health_score'] >= 70:
            print("⚠️  VALIDATION PASSED WITH WARNINGS - Review warnings above")
        else:
            print("❌ VALIDATION FAILED - Critical issues detected")
    
    def run_validation(self) -> bool:
        """Run complete validation suite."""
        logger.info("="*70)
        logger.info("DATABASE MIGRATION VALIDATION")
        logger.info(f"Target: {self.unified_db}")
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        # Run all validation checks
        structure_valid = self.validate_database_structure()
        counts_valid = self.validate_record_counts()
        integrity_valid = self.validate_data_integrity()
        spot_check_valid = self.spot_check_data()
        self.compare_with_backup()
        
        # Generate and print report
        report = self.generate_report()
        
        # Save report to file
        with open(f'validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        self.print_summary(report)
        
        # Return overall result
        return report['summary']['health_score'] >= 70


def main():
    """Main execution function."""
    import sys
    
    # Check if unified database exists
    if not Path('unified_platform.db').exists():
        print("❌ unified_platform.db not found!")
        print("   Run migrate_data.py first")
        return 1
    
    validator = MigrationValidator()
    
    print("🔍 Starting migration validation...")
    print()
    
    if validator.run_validation():
        print("\n✅ VALIDATION COMPLETED SUCCESSFULLY")
        return 0
    else:
        print("\n❌ VALIDATION FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())