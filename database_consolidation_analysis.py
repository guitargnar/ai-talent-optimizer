#!/usr/bin/env python3
"""
AI Talent Optimizer - Database Consolidation Analysis
====================================================

Analyzes all 7 databases and creates a consolidation strategy.
Goal: Merge all 365 records into 1 unified, authoritative database.
"""

import sqlite3
import json
import logging
from datetime import datetime
import hashlib
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseAnalyzer:
    def __init__(self):
        self.databases = [
            'UNIFIED_AI_JOBS.db',
            'job_applications.db', 
            'your_profile.db',
            'principal_jobs_400k.db',
            'ai_talent_optimizer.db',
            'verified_metrics.db',
            'ceo_outreach.db'
        ]
        
        self.analysis_results = {}
        
    def analyze_all_databases(self):
        """Analyze each database structure and content."""
        logger.info("Starting comprehensive database analysis...")
        
        for db_file in self.databases:
            if os.path.exists(db_file):
                self.analysis_results[db_file] = self._analyze_database(db_file)
            else:
                logger.warning(f"Database not found: {db_file}")
                self.analysis_results[db_file] = {"status": "NOT_FOUND"}
        
        return self.analysis_results
    
    def _analyze_database(self, db_file):
        """Analyze a single database."""
        logger.info(f"Analyzing {db_file}...")
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [t[0] for t in cursor.fetchall()]
            
            db_info = {
                "status": "FOUND",
                "total_tables": len(tables),
                "tables": {},
                "total_records": 0,
                "primary_purpose": self._determine_purpose(db_file),
                "data_types": []
            }
            
            for table in tables:
                if table != 'sqlite_sequence':
                    table_info = self._analyze_table(cursor, table)
                    db_info["tables"][table] = table_info
                    db_info["total_records"] += table_info["record_count"]
            
            conn.close()
            
            # Determine what type of data this database primarily contains
            db_info["data_types"] = self._classify_data_types(db_info["tables"])
            
            return db_info
            
        except Exception as e:
            logger.error(f"Error analyzing {db_file}: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def _analyze_table(self, cursor, table_name):
        """Analyze a single table."""
        # Validate table name to prevent SQL injection
        # SQLite table names can only contain alphanumeric and underscore
        if not all(c.isalnum() or c == '_' for c in table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        
        # Get record count - safe because table_name is validated
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        record_count = cursor.fetchone()[0]
        
        # Get schema - safe because table_name is validated
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        
        # Sample data (if any records exist)
        sample_data = None
        if record_count > 0:
            # Safe because table_name is validated
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            sample_data = cursor.fetchone()
        
        return {
            "record_count": record_count,
            "columns": [(col[1], col[2]) for col in schema],
            "column_count": len(schema),
            "primary_key": [col[1] for col in schema if col[5] == 1],
            "sample_data": sample_data
        }
    
    def _determine_purpose(self, db_file):
        """Determine the primary purpose of each database."""
        purposes = {
            'UNIFIED_AI_JOBS.db': 'Job discovery and application tracking',
            'job_applications.db': 'Job discovery and tracking',
            'your_profile.db': 'Personal profile and credentials',
            'principal_jobs_400k.db': 'High-value principal/staff roles',
            'ai_talent_optimizer.db': 'Core application system',
            'verified_metrics.db': 'Verified personal metrics',
            'ceo_outreach.db': 'CEO/executive contact tracking'
        }
        return purposes.get(db_file, 'Unknown')
    
    def _classify_data_types(self, tables):
        """Classify what types of data this database contains."""
        data_types = []
        
        for table_name, table_info in tables.items():
            columns = [col[0] for col in table_info["columns"]]
            
            if any(col in ['company', 'position', 'job_id'] for col in columns):
                data_types.append('job_data')
            
            if any(col in ['applied_date', 'application_date', 'sent_date'] for col in columns):
                data_types.append('application_tracking')
            
            if any(col in ['response_date', 'response_type', 'email_content'] for col in columns):
                data_types.append('response_tracking')
            
            if any(col in ['full_name', 'email', 'phone', 'linkedin'] for col in columns):
                data_types.append('profile_data')
            
            if any(col in ['metric_name', 'metric_value', 'verified'] for col in columns):
                data_types.append('metrics_data')
        
        return list(set(data_types))
    
    def create_consolidation_strategy(self):
        """Create a strategy for consolidating all databases."""
        logger.info("Creating consolidation strategy...")
        
        strategy = {
            "target_schema": self._design_unified_schema(),
            "migration_plan": self._create_migration_plan(),
            "data_deduplication": self._design_dedup_strategy(),
            "validation_rules": self._create_validation_rules()
        }
        
        return strategy
    
    def _design_unified_schema(self):
        """Design the unified database schema."""
        return {
            "jobs": {
                "purpose": "All discovered jobs",
                "columns": [
                    ("id", "INTEGER PRIMARY KEY"),
                    ("job_id", "TEXT UNIQUE"),
                    ("company", "TEXT NOT NULL"),
                    ("position", "TEXT NOT NULL"),
                    ("location", "TEXT"),
                    ("remote", "BOOLEAN"),
                    ("min_salary", "INTEGER"),
                    ("max_salary", "INTEGER"),
                    ("salary_range", "TEXT"),
                    ("description", "TEXT"),
                    ("requirements", "TEXT"),
                    ("url", "TEXT"),
                    ("source", "TEXT"),
                    ("discovered_date", "TIMESTAMP"),
                    ("relevance_score", "REAL"),
                    ("priority_score", "REAL"),
                    ("healthcare_focused", "BOOLEAN DEFAULT 0"),
                    ("ai_focused", "BOOLEAN DEFAULT 0"),
                    ("status", "TEXT DEFAULT 'new'"),
                    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                    ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                ]
            },
            "applications": {
                "purpose": "All job applications sent",
                "columns": [
                    ("id", "INTEGER PRIMARY KEY"),
                    ("job_id", "INTEGER REFERENCES jobs(id)"),
                    ("company", "TEXT NOT NULL"),
                    ("position", "TEXT NOT NULL"),
                    ("applied_date", "TIMESTAMP"),
                    ("application_method", "TEXT"),
                    ("resume_version", "TEXT"),
                    ("cover_letter_version", "TEXT"),
                    ("email_sent", "BOOLEAN DEFAULT 0"),
                    ("email_address", "TEXT"),
                    ("status", "TEXT DEFAULT 'sent'"),
                    ("ats_score", "REAL"),
                    ("tracking_id", "TEXT"),
                    ("notes", "TEXT"),
                    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                    ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                ]
            },
            "responses": {
                "purpose": "All responses received from applications",
                "columns": [
                    ("id", "INTEGER PRIMARY KEY"),
                    ("application_id", "INTEGER REFERENCES applications(id)"),
                    ("company", "TEXT"),
                    ("email_id", "TEXT"),
                    ("from_email", "TEXT"),
                    ("subject", "TEXT"),
                    ("received_date", "TIMESTAMP"),
                    ("response_type", "TEXT"),
                    ("email_content", "TEXT"),
                    ("action_required", "BOOLEAN DEFAULT 0"),
                    ("action_taken", "TEXT"),
                    ("interview_scheduled", "BOOLEAN DEFAULT 0"),
                    ("processed_date", "TIMESTAMP"),
                    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                ]
            },
            "profile": {
                "purpose": "Personal profile information",
                "columns": [
                    ("id", "INTEGER PRIMARY KEY"),
                    ("full_name", "TEXT"),
                    ("email", "TEXT"),
                    ("phone", "TEXT"),
                    ("linkedin", "TEXT"),
                    ("github", "TEXT"),
                    ("location", "TEXT"),
                    ("years_experience", "INTEGER"),
                    ("current_focus", "TEXT"),
                    ("target_salary_min", "INTEGER"),
                    ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                ]
            },
            "contacts": {
                "purpose": "CEO and executive contacts",
                "columns": [
                    ("id", "INTEGER PRIMARY KEY"),
                    ("company", "TEXT"),
                    ("name", "TEXT"),
                    ("title", "TEXT"),
                    ("email", "TEXT"),
                    ("linkedin", "TEXT"),
                    ("phone", "TEXT"),
                    ("contacted", "BOOLEAN DEFAULT 0"),
                    ("contacted_at", "TIMESTAMP"),
                    ("response_received", "BOOLEAN DEFAULT 0"),
                    ("notes", "TEXT"),
                    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                ]
            },
            "metrics": {
                "purpose": "Verified personal and system metrics",
                "columns": [
                    ("id", "INTEGER PRIMARY KEY"),
                    ("metric_name", "TEXT UNIQUE"),
                    ("metric_value", "TEXT"),
                    ("verification_method", "TEXT"),
                    ("verified_at", "TIMESTAMP"),
                    ("expires_at", "TIMESTAMP"),
                    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                ]
            }
        }
    
    def _create_migration_plan(self):
        """Create detailed migration plan."""
        return {
            "phase_1_preparation": [
                "Create backup of all existing databases",
                "Create new unified database with target schema",
                "Set up data validation functions"
            ],
            "phase_2_data_migration": [
                "Migrate job data from all sources (dedup by company+position)",
                "Migrate application data (dedup by company+applied_date)",
                "Migrate response data (dedup by email_id)",
                "Migrate profile data (single record)",
                "Migrate contact data",
                "Migrate metrics data"
            ],
            "phase_3_validation": [
                "Verify record counts match expected totals",
                "Check for duplicate data",
                "Validate foreign key relationships",
                "Test core queries work correctly"
            ],
            "phase_4_cleanup": [
                "Archive old databases",
                "Update all scripts to use new database",
                "Update configuration files"
            ]
        }
    
    def _design_dedup_strategy(self):
        """Design deduplication strategy."""
        return {
            "jobs": {
                "primary_key": ["company", "position"],
                "merge_strategy": "keep_most_complete_record",
                "conflict_resolution": "prefer_higher_salary_range"
            },
            "applications": {
                "primary_key": ["company", "position", "applied_date"],
                "merge_strategy": "keep_latest_application",
                "conflict_resolution": "prefer_records_with_tracking_data"
            },
            "responses": {
                "primary_key": ["email_id"],
                "merge_strategy": "keep_all_unique_responses",
                "conflict_resolution": "prefer_most_recent"
            }
        }
    
    def _create_validation_rules(self):
        """Create validation rules for migration."""
        return [
            "Total records in unified DB should equal sum of unique records",
            "All company names should be consistent (e.g., 'Google' not 'Google Inc.')",
            "All dates should be in ISO format",
            "All salary ranges should be integers or NULL",
            "No duplicate jobs (same company + position)",
            "All applications must reference valid jobs",
            "All responses must reference valid applications"
        ]

def main():
    """Run the database analysis."""
    analyzer = DatabaseAnalyzer()
    
    # Analyze all databases
    results = analyzer.analyze_all_databases()
    
    # Create consolidation strategy
    strategy = analyzer.create_consolidation_strategy()
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "analysis_results": results,
        "consolidation_strategy": strategy,
        "summary": {
            "total_databases": len([r for r in results.values() if r.get("status") == "FOUND"]),
            "total_records": sum(r.get("total_records", 0) for r in results.values()),
            "databases_with_data": len([r for r in results.values() if r.get("total_records", 0) > 0])
        }
    }
    
    # Save analysis report
    with open('database_consolidation_analysis.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info(f"Analysis complete. Found {report['summary']['total_records']} total records across {report['summary']['total_databases']} databases.")
    
    # Print summary
    print("\n=== DATABASE CONSOLIDATION ANALYSIS ===")
    print(f"Total Databases Found: {report['summary']['total_databases']}")
    print(f"Total Records: {report['summary']['total_records']}")
    print("\nDatabase Breakdown:")
    
    for db_file, info in results.items():
        if info.get("status") == "FOUND":
            print(f"  {db_file}: {info['total_records']} records across {info['total_tables']} tables")
            print(f"    Purpose: {info['primary_purpose']}")
            print(f"    Data Types: {', '.join(info['data_types'])}")
    
    print(f"\nDetailed analysis saved to: database_consolidation_analysis.json")
    
    return report

if __name__ == "__main__":
    main()