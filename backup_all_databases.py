#!/usr/bin/env python3
"""
Database Backup Utility
=======================
Creates a comprehensive backup of all database files before migration.
Ensures data safety during the consolidation process.
"""

import os
import zipfile
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

class DatabaseBackupManager:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_filename = f'database_backup_{self.timestamp}.zip'
        self.manifest_filename = f'backup_manifest_{self.timestamp}.json'
        
        # List of all databases to backup
        self.databases_to_backup = [
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
        
        self.backup_stats = {
            'total_files': 0,
            'total_size': 0,
            'backed_up': [],
            'not_found': [],
            'errors': []
        }
    
    def calculate_file_hash(self, filepath: str) -> str:
        """Calculate SHA256 hash of a file for integrity verification."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def create_backup(self) -> bool:
        """Create a comprehensive backup of all databases."""
        print("=" * 70)
        print("DATABASE BACKUP UTILITY")
        print("=" * 70)
        print(f"Backup file: {self.backup_filename}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        manifest = {
            'timestamp': self.timestamp,
            'backup_file': self.backup_filename,
            'databases': {}
        }
        
        try:
            with zipfile.ZipFile(self.backup_filename, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                for db_path in self.databases_to_backup:
                    if Path(db_path).exists():
                        print(f"✓ Backing up: {db_path}")
                        
                        # Get file stats
                        file_stats = os.stat(db_path)
                        file_size = file_stats.st_size
                        file_hash = self.calculate_file_hash(db_path)
                        
                        # Add to zip with preserved path structure
                        backup_zip.write(db_path, arcname=db_path)
                        
                        # Update manifest
                        manifest['databases'][db_path] = {
                            'size': file_size,
                            'hash': file_hash,
                            'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                        }
                        
                        # Update stats
                        self.backup_stats['backed_up'].append(db_path)
                        self.backup_stats['total_size'] += file_size
                        self.backup_stats['total_files'] += 1
                        
                    else:
                        print(f"⚠ Not found: {db_path}")
                        self.backup_stats['not_found'].append(db_path)
                
                # Add README to the backup
                readme_content = self.generate_readme()
                backup_zip.writestr('README.txt', readme_content)
                
                # Add manifest to the backup
                backup_zip.writestr('manifest.json', json.dumps(manifest, indent=2))
            
            # Save external manifest for verification
            with open(self.manifest_filename, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            self.print_summary()
            return True
            
        except Exception as e:
            print(f"\n❌ Backup failed: {e}")
            self.backup_stats['errors'].append(str(e))
            return False
    
    def generate_readme(self) -> str:
        """Generate README content for the backup."""
        readme = f"""DATABASE BACKUP README
======================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This backup contains all database files from the AI Talent Optimizer platform
prior to the database consolidation migration.

BACKUP CONTENTS:
----------------
Total databases backed up: {self.backup_stats['total_files']}
Total size: {self.format_bytes(self.backup_stats['total_size'])}

RESTORATION INSTRUCTIONS:
-------------------------
1. Extract this zip file to a safe location
2. To restore a specific database:
   - Copy the desired .db file to its original location
   - Ensure proper file permissions are set

3. To restore all databases:
   - Extract all files preserving the directory structure
   - Run: unzip -o {self.backup_filename}

VERIFICATION:
-------------
Use the manifest.json file to verify file integrity by checking SHA256 hashes.
Each database file's hash is recorded at the time of backup.

IMPORTANT NOTES:
----------------
- This backup was created before the database consolidation migration
- Keep this backup until the migration is verified successful
- The backup includes all 19 active database files
- Database files not found during backup are listed in the summary

For questions or issues, refer to the migration documentation.
"""
        return readme
    
    def format_bytes(self, bytes: int) -> str:
        """Format bytes into human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} TB"
    
    def print_summary(self):
        """Print backup summary."""
        print("\n" + "=" * 70)
        print("BACKUP SUMMARY")
        print("=" * 70)
        print(f"✅ Successfully backed up: {len(self.backup_stats['backed_up'])} databases")
        print(f"📦 Total backup size: {self.format_bytes(self.backup_stats['total_size'])}")
        print(f"📄 Backup file: {self.backup_filename}")
        print(f"📋 Manifest file: {self.manifest_filename}")
        
        if self.backup_stats['not_found']:
            print(f"\n⚠️  Not found ({len(self.backup_stats['not_found'])} files):")
            for db in self.backup_stats['not_found']:
                print(f"   - {db}")
        
        if self.backup_stats['errors']:
            print(f"\n❌ Errors encountered:")
            for error in self.backup_stats['errors']:
                print(f"   - {error}")
        
        print("\n💡 Next steps:")
        print("   1. Verify the backup file integrity")
        print("   2. Store backup in a safe location")
        print("   3. Proceed with schema creation")
    
    def verify_backup(self) -> bool:
        """Verify the integrity of the backup file."""
        print("\n" + "=" * 70)
        print("VERIFYING BACKUP")
        print("=" * 70)
        
        if not Path(self.backup_filename).exists():
            print("❌ Backup file not found!")
            return False
        
        if not Path(self.manifest_filename).exists():
            print("❌ Manifest file not found!")
            return False
        
        try:
            # Load manifest
            with open(self.manifest_filename, 'r') as f:
                manifest = json.load(f)
            
            # Verify zip file
            with zipfile.ZipFile(self.backup_filename, 'r') as backup_zip:
                # Check for corruption
                bad_files = backup_zip.testzip()
                if bad_files:
                    print(f"❌ Corrupted files in backup: {bad_files}")
                    return False
                
                # List contents
                file_list = backup_zip.namelist()
                print(f"✅ Backup contains {len(file_list)} files")
                print(f"✅ Backup integrity verified")
                
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False


def main():
    """Main execution function."""
    manager = DatabaseBackupManager()
    
    # Create backup
    print("🚀 Starting database backup process...")
    success = manager.create_backup()
    
    if success:
        # Verify backup
        if manager.verify_backup():
            print("\n✅ BACKUP COMPLETED SUCCESSFULLY")
            print(f"   Backup saved as: {manager.backup_filename}")
            return 0
        else:
            print("\n⚠️  Backup created but verification failed")
            return 1
    else:
        print("\n❌ BACKUP FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())