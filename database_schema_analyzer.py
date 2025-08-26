#!/usr/bin/env python3
"""
Database Schema Analyzer for Consolidation
==========================================
Analyzes all SQLite databases and generates a comprehensive schema report.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

class DatabaseSchemaAnalyzer:
    def __init__(self):
        self.databases = [
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
            'unified_talent_optimizer.db',
            'verified_metrics.db',
            'your_profile.db'
        ]
        
        self.schema_report = {}
        
    def analyze_all_databases(self) -> Dict:
        """Analyze all databases and generate schema report."""
        print("=" * 70)
        print("DATABASE SCHEMA ANALYSIS REPORT")
        print("=" * 70)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        for db_path in self.databases:
            if Path(db_path).exists():
                self.analyze_database(db_path)
            else:
                print(f"⚠️  Not found: {db_path}")
                self.schema_report[db_path] = {"status": "NOT_FOUND"}
        
        return self.schema_report
    
    def analyze_database(self, db_path: str) -> None:
        """Analyze a single database."""
        print(f"\n📊 Analyzing: {db_path}")
        print("-" * 50)
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            db_info = {
                "status": "ANALYZED",
                "table_count": len(tables),
                "tables": {},
                "total_records": 0
            }
            
            for table in tables:
                if table == 'sqlite_sequence':
                    continue
                    
                table_info = self.analyze_table(cursor, table)
                db_info["tables"][table] = table_info
                db_info["total_records"] += table_info["record_count"]
                
                # Print table summary
                print(f"  📋 {table}: {table_info['record_count']} records, {table_info['column_count']} columns")
                
            conn.close()
            
            print(f"  Total: {db_info['total_records']} records across {len(tables)} tables")
            self.schema_report[db_path] = db_info
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.schema_report[db_path] = {"status": "ERROR", "error": str(e)}
    
    def analyze_table(self, cursor, table_name: str) -> Dict:
        """Analyze a single table."""
        # Validate table name
        if not all(c.isalnum() or c == '_' for c in table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        
        # Get schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Get record count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        record_count = cursor.fetchone()[0]
        
        # Get indexes
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        
        return {
            "record_count": record_count,
            "column_count": len(columns),
            "columns": [
                {
                    "name": col[1],
                    "type": col[2],
                    "nullable": not col[3],
                    "default": col[4],
                    "primary_key": bool(col[5])
                }
                for col in columns
            ],
            "indexes": [idx[1] for idx in indexes]
        }
    
    def identify_redundancies(self) -> Dict:
        """Identify redundant tables and columns across databases."""
        print("\n\n" + "=" * 70)
        print("REDUNDANCY ANALYSIS")
        print("=" * 70)
        
        redundancies = {
            "duplicate_tables": {},
            "similar_tables": {},
            "common_columns": {},
            "suggested_merges": []
        }
        
        # Find tables with similar names
        all_tables = {}
        for db_path, info in self.schema_report.items():
            if info.get("status") == "ANALYZED":
                for table_name in info.get("tables", {}).keys():
                    if table_name not in all_tables:
                        all_tables[table_name] = []
                    all_tables[table_name].append(db_path)
        
        # Identify duplicates
        for table_name, db_list in all_tables.items():
            if len(db_list) > 1:
                redundancies["duplicate_tables"][table_name] = db_list
                print(f"\n🔄 Duplicate table '{table_name}' found in:")
                for db in db_list:
                    records = self.schema_report[db]["tables"][table_name]["record_count"]
                    print(f"   - {db} ({records} records)")
        
        # Identify similar table names (job-related, application-related, etc.)
        table_categories = {
            "jobs": ["job", "position", "role", "opportunity"],
            "applications": ["application", "apply", "submission"],
            "companies": ["company", "employer", "organization"],
            "contacts": ["contact", "ceo", "executive", "person"],
            "tracking": ["track", "monitor", "status", "metric"]
        }
        
        for category, keywords in table_categories.items():
            matching_tables = []
            for db_path, info in self.schema_report.items():
                if info.get("status") == "ANALYZED":
                    for table_name in info.get("tables", {}).keys():
                        if any(keyword in table_name.lower() for keyword in keywords):
                            matching_tables.append((db_path, table_name))
            
            if matching_tables:
                redundancies["similar_tables"][category] = matching_tables
                print(f"\n📁 {category.upper()} tables:")
                for db, table in matching_tables:
                    records = self.schema_report[db]["tables"][table]["record_count"]
                    print(f"   - {db}/{table} ({records} records)")
        
        return redundancies
    
    def generate_consolidation_plan(self) -> Dict:
        """Generate a plan for database consolidation."""
        print("\n\n" + "=" * 70)
        print("CONSOLIDATION PLAN")
        print("=" * 70)
        
        plan = {
            "target_database": "unified_platform.db",
            "proposed_tables": {},
            "migration_steps": [],
            "estimated_records": 0
        }
        
        # Define the consolidated schema
        plan["proposed_tables"] = {
            "jobs": {
                "purpose": "All job opportunities from all sources",
                "source_tables": [
                    "job_discoveries", "job_applications", "jobs", 
                    "european_jobs", "linkedin_jobs", "principal_jobs"
                ],
                "key_columns": [
                    "id", "job_id", "company", "title", "location", 
                    "salary_min", "salary_max", "remote", "description",
                    "requirements", "url", "source", "discovered_date",
                    "priority_score", "status"
                ]
            },
            "applications": {
                "purpose": "All job applications and their status",
                "source_tables": [
                    "applications", "staged_applications", "sent_applications"
                ],
                "key_columns": [
                    "id", "job_id", "company", "position", "applied_date",
                    "application_method", "resume_version", "cover_letter",
                    "status", "response_received", "interview_scheduled"
                ]
            },
            "companies": {
                "purpose": "Company information and research",
                "source_tables": ["companies", "company_research"],
                "key_columns": [
                    "id", "name", "industry", "size", "location",
                    "website", "careers_page", "email_domain",
                    "research_notes", "priority_score"
                ]
            },
            "contacts": {
                "purpose": "CEO, hiring managers, and other contacts",
                "source_tables": ["contacts", "ceo_contacts", "executives"],
                "key_columns": [
                    "id", "company_id", "name", "title", "email",
                    "linkedin", "phone", "contacted", "response_received",
                    "notes", "priority_score"
                ]
            },
            "metrics": {
                "purpose": "Performance metrics and analytics",
                "source_tables": ["metrics", "verified_metrics", "campaign_tracking"],
                "key_columns": [
                    "id", "metric_name", "metric_value", "date",
                    "category", "verified"
                ]
            },
            "profile": {
                "purpose": "User profile and preferences",
                "source_tables": ["profile", "your_profile"],
                "key_columns": [
                    "id", "full_name", "email", "phone", "linkedin",
                    "github", "location", "target_roles", "target_salary_min",
                    "resume_versions", "preferences"
                ]
            }
        }
        
        print("\n📐 Proposed Unified Schema:")
        for table_name, details in plan["proposed_tables"].items():
            print(f"\n   {table_name.upper()}")
            print(f"   Purpose: {details['purpose']}")
            print(f"   Columns: {', '.join(details['key_columns'][:5])}...")
        
        # Calculate total records
        total_records = 0
        for db_path, info in self.schema_report.items():
            if info.get("status") == "ANALYZED":
                total_records += info.get("total_records", 0)
        
        plan["estimated_records"] = total_records
        print(f"\n📊 Total records to migrate: {total_records:,}")
        
        return plan
    
    def save_report(self, filename: str = "database_consolidation_report.json") -> None:
        """Save the complete analysis report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "databases_analyzed": len([d for d in self.schema_report.values() if d.get("status") == "ANALYZED"]),
            "schema_report": self.schema_report,
            "redundancies": self.identify_redundancies(),
            "consolidation_plan": self.generate_consolidation_plan()
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n\n✅ Report saved to: {filename}")
        
        return report


def main():
    """Run the database schema analysis."""
    analyzer = DatabaseSchemaAnalyzer()
    
    # Analyze all databases
    analyzer.analyze_all_databases()
    
    # Identify redundancies
    analyzer.identify_redundancies()
    
    # Generate consolidation plan
    analyzer.generate_consolidation_plan()
    
    # Save report
    report = analyzer.save_report()
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    
    return report


if __name__ == "__main__":
    main()