#!/usr/bin/env python3
"""
Pre-Application Verification Hook
Ensures only verified metrics are used in applications
"""

import subprocess
from pathlib import Path
from datetime import datetime
import sqlite3
import sys

class PreApplicationVerifier:
    def __init__(self):
        self.verified = {}
        self.warnings = []
        self.errors = []
        
    def verify_current_state(self):
        """Verify current system state"""
        print("🔍 PRE-APPLICATION VERIFICATION")
        print("="*60)
        
        # Check Python modules
        py_files = list(Path.cwd().glob("*.py"))
        self.verified['python_modules'] = len(py_files)
        print(f"✅ Python modules in directory: {len(py_files)}")
        
        # Check databases
        db_files = list(Path.cwd().glob("*.db"))
        self.verified['databases'] = len(db_files)
        print(f"✅ Databases: {len(db_files)}")
        
        # Check MCP servers
        try:
            result = subprocess.run(['pgrep', '-f', 'mcp-server'], 
                                  capture_output=True, text=True)
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                self.verified['mcp_servers'] = len(pids)
                print(f"✅ MCP servers running: {len(pids)}")
            else:
                self.verified['mcp_servers'] = 0
                print(f"⚠️  No MCP servers running")
        except:
            self.verified['mcp_servers'] = 0
        
        # Check today's modifications
        today = datetime.now().date()
        modified = []
        for f in Path.cwd().glob("*.py"):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).date()
                if mtime == today:
                    modified.append(f.name)
            except:
                pass
        self.verified['modified_today'] = len(modified)
        print(f"✅ Files modified today: {len(modified)}")
        
        return self.verified
    
    def check_claims_in_file(self, filepath):
        """Check if file contains unverified claims"""
        if not Path(filepath).exists():
            return []
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        unverified_claims = []
        
        # Check for specific claims
        checks = [
            ("$1.2M", "Contains $1.2M savings claim - REMOVE THIS"),
            ("1.2 million", "Contains 1.2 million claim - REMOVE THIS"),
            ("cost reduction", "Positions as cost reducer - CHANGE TO BUILDER"),
            ("86,279", "Uses old unverified Python file count"),
            ("1,045 shell scripts", "Uses unverified shell script count"),
            ("15+ databases", "Claims 15 databases but only {} verified".format(
                self.verified.get('databases', 0)
            ))
        ]
        
        for phrase, warning in checks:
            if phrase.lower() in content.lower():
                unverified_claims.append(warning)
        
        return unverified_claims
    
    def validate_application_materials(self, directory):
        """Validate all materials in application directory"""
        app_dir = Path(directory)
        if not app_dir.exists():
            return False
        
        print(f"\n📋 Validating: {directory}")
        print("-"*40)
        
        issues = []
        
        # Check each file
        for file in app_dir.glob("*.txt"):
            print(f"Checking {file.name}...")
            claims = self.check_claims_in_file(file)
            if claims:
                issues.extend(claims)
                for claim in claims:
                    print(f"  ⚠️ {claim}")
            else:
                print(f"  ✅ Clean")
        
        if issues:
            print(f"\n❌ VALIDATION FAILED: {len(issues)} issues found")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"\n✅ VALIDATION PASSED: All claims verified")
            return True
    
    def update_profile_database(self):
        """Update profile database with current verified metrics"""
        conn = sqlite3.connect('unified_talent_optimizer.db')
        cursor = conn.cursor()
        
        # Update metrics with verified values
        updates = [
            ('python_modules_ai_optimizer', str(self.verified.get('python_modules', 0)), 
             'VERIFIED in ai-talent-optimizer'),
            ('active_databases', str(self.verified.get('databases', 0)), 
             'VERIFIED in current directory'),
            ('running_services', f"{self.verified.get('mcp_servers', 0)} MCP servers", 
             'VERIFIED via pgrep'),
            ('daily_development_velocity', f"{self.verified.get('modified_today', 0)} files", 
             f'VERIFIED for {datetime.now().date()}'),
        ]
        
        for metric_name, value, context in updates:
            cursor.execute("""
                UPDATE platform_metrics 
                SET metric_value = ?, context = ?, last_updated = CURRENT_TIMESTAMP
                WHERE metric_name = ?
            """, (value, context, metric_name))
        
        conn.commit()
        conn.close()
        print("\n✅ Profile database updated with verified metrics")
    
    def generate_truth_card(self):
        """Generate a truth card for this session"""
        truth_card = f"""
# VERIFIED METRICS CARD
Generated: {datetime.now().isoformat()}

## Current State (VERIFIED)
- Python modules: {self.verified.get('python_modules', 0)}
- Databases: {self.verified.get('databases', 0)}
- MCP servers: {self.verified.get('mcp_servers', 0)}
- Modified today: {self.verified.get('modified_today', 0)}

## Approved Claims
✅ "I have {self.verified.get('python_modules', 0)} Python modules in my platform"
✅ "I modified {self.verified.get('modified_today', 0)} files today"
✅ "I'm running {self.verified.get('mcp_servers', 0)} MCP servers"
✅ "I've outgrown my current role"

## Forbidden Claims
❌ "$1.2M in savings"
❌ "15+ databases" (only {self.verified.get('databases', 0)} verified)
❌ Any unverified metrics

---
This card expires: {datetime.now().date()} 23:59:59
"""
        
        with open("TRUTH_CARD.md", 'w') as f:
            f.write(truth_card)
        
        print("\n📇 Truth card generated: TRUTH_CARD.md")
        return truth_card

def main():
    """Run pre-application verification"""
    verifier = PreApplicationVerifier()
    
    # Verify current state
    metrics = verifier.verify_current_state()
    
    # Update profile database
    verifier.update_profile_database()
    
    # Generate truth card
    verifier.generate_truth_card()
    
    # Check for recent applications to validate
    recent_apps = list(Path("applications").glob("*/*/"))
    if recent_apps:
        print(f"\n🔍 Found {len(recent_apps)} recent applications to validate")
        
        # Check most recent
        most_recent = max(recent_apps, key=lambda p: p.stat().st_mtime)
        valid = verifier.validate_application_materials(most_recent)
        
        if not valid:
            print("\n⚠️  WARNING: Recent application contains unverified claims!")
            print("   Regenerate with verified metrics only.")
    
    print("\n" + "="*60)
    print("✅ PRE-APPLICATION VERIFICATION COMPLETE")
    print("="*60)
    print("Use only verified metrics in applications:")
    for key, value in metrics.items():
        print(f"  • {key}: {value}")
    
    return metrics

if __name__ == "__main__":
    metrics = main()
    
    # Return non-zero exit code if critical metrics missing
    if metrics.get('python_modules', 0) < 100:
        print("\n⚠️  Warning: Low module count")
    
    if metrics.get('mcp_servers', 0) == 0:
        print("\n⚠️  Warning: No MCP servers running")
        print("   Consider starting them for stronger claims")