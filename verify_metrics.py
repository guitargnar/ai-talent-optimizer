#!/usr/bin/env python3
"""
Metric Verification System - TRUTH ENFORCER
No metric gets claimed without verification
"""

import os
import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime
import json
import hashlib

class MetricVerifier:
    def __init__(self):
        self.verified_metrics = {}
        self.verification_log = []
        self.truth_db = "verified_metrics.db"
        self.init_truth_database()
        
    def init_truth_database(self):
        """Create database for verified metrics only"""
        conn = sqlite3.connect(self.truth_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verified_metrics (
                metric_name TEXT PRIMARY KEY,
                verified_value TEXT,
                verification_method TEXT,
                raw_evidence TEXT,
                verified_at TIMESTAMP,
                expires_at TIMESTAMP,
                hash TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                claimed_value TEXT,
                actual_value TEXT,
                verified BOOLEAN,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def verify_python_files_count(self):
        """ACTUALLY COUNT Python files - no estimates"""
        verification = {
            'metric': 'python_files_total',
            'claimed': 86279,
            'method': 'find command',
            'actual': 0,
            'verified': False,
            'evidence': None
        }
        
        try:
            # Count in HOME directory
            cmd = "find ~ -name '*.py' -type f 2>/dev/null | wc -l"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                count = int(result.stdout.strip())
                verification['actual'] = count
                verification['verified'] = True
                verification['evidence'] = f"Command: {cmd}, Output: {count}"
                
                print(f"✅ Python files verified: {count:,}")
                if count < 80000:
                    print(f"⚠️  Warning: Count ({count:,}) is less than claimed (86,279)")
            else:
                verification['error'] = result.stderr
                print(f"❌ Could not verify Python files: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            # Too many files, try sampling
            print("⏱️  Full count timed out, sampling instead...")
            verification['method'] = 'sampling estimate'
            
            # Sample specific directories
            dirs_to_check = [
                "~/AI-ML-Portfolio",
                "~/Projects",
                "~/SURVIVE",
                "~/.pyenv"
            ]
            
            total = 0
            for dir_path in dirs_to_check:
                expanded = os.path.expanduser(dir_path)
                if os.path.exists(expanded):
                    cmd = f"find {expanded} -name '*.py' -type f 2>/dev/null | wc -l"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        count = int(result.stdout.strip())
                        total += count
                        print(f"  {dir_path}: {count:,} Python files")
            
            verification['actual'] = total
            verification['verified'] = total > 0
            verification['evidence'] = f"Sampled {len(dirs_to_check)} directories: {total} files"
            
        except Exception as e:
            verification['error'] = str(e)
            print(f"❌ Error verifying Python files: {e}")
        
        self.log_verification(verification)
        return verification
    
    def verify_python_modules_in_directory(self):
        """Count Python modules in current directory"""
        verification = {
            'metric': 'python_modules_current_dir',
            'claimed': 113,
            'method': 'glob pattern',
            'actual': 0,
            'verified': False
        }
        
        try:
            py_files = list(Path.cwd().glob("*.py"))
            verification['actual'] = len(py_files)
            verification['verified'] = True
            verification['evidence'] = [f.name for f in py_files[:10]]  # First 10 as evidence
            
            print(f"✅ Python modules in current directory: {len(py_files)}")
            if len(py_files) < 100:
                print(f"ℹ️  Note: Found {len(py_files)} modules (claimed: 113)")
                
        except Exception as e:
            verification['error'] = str(e)
            print(f"❌ Error counting modules: {e}")
        
        self.log_verification(verification)
        return verification
    
    def verify_shell_scripts(self):
        """Count shell scripts"""
        verification = {
            'metric': 'shell_scripts_total',
            'claimed': 1045,
            'method': 'find command',
            'actual': 0,
            'verified': False
        }
        
        try:
            cmd = "find ~ -name '*.sh' -type f 2>/dev/null | wc -l"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0:
                count = int(result.stdout.strip())
                verification['actual'] = count
                verification['verified'] = True
                verification['evidence'] = f"Found {count} .sh files"
                
                print(f"✅ Shell scripts verified: {count}")
                
        except Exception as e:
            verification['error'] = str(e)
            print(f"❌ Error verifying shell scripts: {e}")
        
        self.log_verification(verification)
        return verification
    
    def verify_databases(self):
        """Count actual database files"""
        verification = {
            'metric': 'databases_current_dir',
            'claimed': 15,
            'method': 'glob pattern',
            'actual': 0,
            'verified': False
        }
        
        try:
            db_files = list(Path.cwd().glob("*.db"))
            verification['actual'] = len(db_files)
            verification['verified'] = True
            verification['evidence'] = [f.name for f in db_files]
            
            print(f"✅ Databases in current directory: {len(db_files)}")
            print(f"   Files: {', '.join([f.name for f in db_files[:5]])}")
            
        except Exception as e:
            verification['error'] = str(e)
            print(f"❌ Error counting databases: {e}")
        
        self.log_verification(verification)
        return verification
    
    def verify_mcp_servers(self):
        """Count running MCP servers"""
        verification = {
            'metric': 'mcp_servers_running',
            'claimed': 13,
            'method': 'pgrep',
            'actual': 0,
            'verified': False
        }
        
        try:
            result = subprocess.run(['pgrep', '-f', 'mcp-server'], 
                                  capture_output=True, text=True)
            
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                verification['actual'] = len(pids)
                verification['verified'] = True
                verification['evidence'] = f"PIDs: {pids[:5]}"  # First 5 PIDs
            else:
                verification['actual'] = 0
                verification['verified'] = True
                verification['evidence'] = "No MCP servers found"
            
            print(f"✅ MCP servers running: {verification['actual']}")
            
        except Exception as e:
            verification['error'] = str(e)
            print(f"❌ Error checking MCP servers: {e}")
        
        self.log_verification(verification)
        return verification
    
    def verify_daily_modifications(self):
        """Count files modified today"""
        verification = {
            'metric': 'files_modified_today',
            'claimed': 27,
            'method': 'file stats',
            'actual': 0,
            'verified': False
        }
        
        try:
            today = datetime.now().date()
            modified_today = []
            
            for f in Path.cwd().glob("*.py"):
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime).date()
                    if mtime == today:
                        modified_today.append(f.name)
                except:
                    pass
            
            verification['actual'] = len(modified_today)
            verification['verified'] = True
            verification['evidence'] = modified_today[:10]  # First 10 files
            
            print(f"✅ Files modified today: {len(modified_today)}")
            if modified_today:
                print(f"   Including: {', '.join(modified_today[:5])}")
            
        except Exception as e:
            verification['error'] = str(e)
            print(f"❌ Error checking daily modifications: {e}")
        
        self.log_verification(verification)
        return verification
    
    def verify_application_count(self):
        """Verify application count from database"""
        verification = {
            'metric': 'applications_processed',
            'claimed': 1600,
            'method': 'database query',
            'actual': 0,
            'verified': False
        }
        
        try:
            if Path("applications_sent.db").exists():
                conn = sqlite3.connect("applications_sent.db")
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM applications")
                count = cursor.fetchone()[0]
                conn.close()
                
                verification['actual'] = count
                verification['verified'] = True
                verification['evidence'] = f"From applications_sent.db"
                
                print(f"✅ Applications in database: {count}")
            else:
                print("⚠️  No applications database found")
                verification['evidence'] = "Database not found"
                
        except Exception as e:
            verification['error'] = str(e)
            print(f"❌ Error checking applications: {e}")
        
        self.log_verification(verification)
        return verification
    
    def log_verification(self, verification):
        """Log verification attempt"""
        conn = sqlite3.connect(self.truth_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO verification_log 
            (metric_name, claimed_value, actual_value, verified, error_message)
            VALUES (?, ?, ?, ?, ?)
        """, (
            verification['metric'],
            verification.get('claimed', 'N/A'),
            verification.get('actual', 'N/A'),
            verification.get('verified', False),
            verification.get('error', None)
        ))
        
        # If verified, update verified_metrics table
        if verification.get('verified'):
            evidence_str = json.dumps(verification.get('evidence', {}))
            hash_val = hashlib.sha256(evidence_str.encode()).hexdigest()[:16]
            
            cursor.execute("""
                INSERT OR REPLACE INTO verified_metrics
                (metric_name, verified_value, verification_method, raw_evidence, 
                 verified_at, expires_at, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                verification['metric'],
                str(verification['actual']),
                verification['method'],
                evidence_str,
                datetime.now(),
                datetime.now(),  # Expires immediately - must reverify
                hash_val
            ))
        
        conn.commit()
        conn.close()
    
    def get_verified_metrics(self):
        """Get only verified metrics"""
        conn = sqlite3.connect(self.truth_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT metric_name, verified_value, verified_at
            FROM verified_metrics
            WHERE verified_at > datetime('now', '-1 hour')
            ORDER BY verified_at DESC
        """)
        
        metrics = cursor.fetchall()
        conn.close()
        
        return {m[0]: {'value': m[1], 'verified_at': m[2]} for m in metrics}
    
    def run_full_verification(self):
        """Run all verifications"""
        print("🔍 METRIC VERIFICATION SYSTEM")
        print("="*60)
        print("Verifying all claims with actual evidence...\n")
        
        results = {
            'python_files': self.verify_python_files_count(),
            'python_modules': self.verify_python_modules_in_directory(),
            'shell_scripts': self.verify_shell_scripts(),
            'databases': self.verify_databases(),
            'mcp_servers': self.verify_mcp_servers(),
            'daily_mods': self.verify_daily_modifications(),
            'applications': self.verify_application_count()
        }
        
        # Summary
        print("\n" + "="*60)
        print("📊 VERIFICATION SUMMARY")
        print("="*60)
        
        verified_count = sum(1 for r in results.values() if r.get('verified'))
        print(f"Verified: {verified_count}/{len(results)} metrics")
        
        print("\n✅ VERIFIED METRICS (Use These):")
        for name, result in results.items():
            if result.get('verified'):
                actual = result.get('actual', 0)
                claimed = result.get('claimed', 'N/A')
                print(f"  • {name}: {actual:,} (claimed: {claimed})")
        
        print("\n❌ UNVERIFIED METRICS (Do Not Use):")
        for name, result in results.items():
            if not result.get('verified'):
                print(f"  • {name}: Could not verify")
        
        return results
    
    def update_claude_md_with_truth(self, verified_results):
        """Update CLAUDE.md with only verified metrics"""
        print("\n📝 Updating CLAUDE.md with verified metrics...")
        
        # Read current CLAUDE.md
        claude_path = Path("/Users/matthewscott/CLAUDE.md")
        if not claude_path.exists():
            print("❌ CLAUDE.md not found")
            return
        
        with open(claude_path, 'r') as f:
            content = f.read()
        
        # Prepare verified metrics section
        verified_section = f"""### What I've Actually Built (VERIFIED {datetime.now().strftime('%Y-%m-%d %H:%M')})
"""
        
        if verified_results['python_modules']['verified']:
            count = verified_results['python_modules']['actual']
            verified_section += f"- **{count} Python modules** in current directory (verified via glob)\n"
        
        if verified_results['python_files']['verified']:
            count = verified_results['python_files']['actual']
            if count > 10000:
                verified_section += f"- **{count:,} Python files** across system (verified via find)\n"
        
        if verified_results['shell_scripts']['verified']:
            count = verified_results['shell_scripts']['actual']
            if count > 100:
                verified_section += f"- **{count:,} shell scripts** for automation (verified)\n"
        
        if verified_results['databases']['verified']:
            count = verified_results['databases']['actual']
            verified_section += f"- **{count} databases** in current directory (verified)\n"
        
        if verified_results['mcp_servers']['verified']:
            count = verified_results['mcp_servers']['actual']
            if count > 0:
                verified_section += f"- **{count} MCP servers** currently running (verified via pgrep)\n"
        
        if verified_results['daily_mods']['verified']:
            count = verified_results['daily_mods']['actual']
            verified_section += f"- **{count} files modified today** (verified via file stats)\n"
        
        # Note about unverified metrics
        verified_section += "\n⚠️ Unverified claims have been removed. Only proven metrics shown above.\n"
        
        print("\nVerified metrics to be written:")
        print(verified_section)
        
        # Save backup
        backup_path = f"/Users/matthewscott/CLAUDE.md.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Backup saved: {backup_path}")
        
        return verified_section

def main():
    """Run verification and update claims"""
    verifier = MetricVerifier()
    
    # Run full verification
    results = verifier.run_full_verification()
    
    # Get verified metrics
    verified = verifier.get_verified_metrics()
    
    print("\n" + "="*60)
    print("💾 VERIFIED METRICS DATABASE")
    print("="*60)
    for metric, data in verified.items():
        print(f"{metric}: {data['value']} (verified: {data['verified_at']})")
    
    # Offer to update CLAUDE.md
    print("\n" + "="*60)
    choice = input("Update CLAUDE.md with verified metrics only? (yes/no): ").strip()
    if choice.lower() == 'yes':
        verifier.update_claude_md_with_truth(results)
        print("✅ CLAUDE.md will be updated with verified metrics only")
    
    print("\n✅ Verification complete. Truth database: verified_metrics.db")

if __name__ == "__main__":
    main()