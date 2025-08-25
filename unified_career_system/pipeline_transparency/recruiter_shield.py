#!/usr/bin/env python3
"""
Recruiter Shield - Manage recruiter interactions and maintain first contact advantage
Transforms recruiters from gatekeepers to intelligence assets
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from unified_career_system.pipeline_transparency.pipeline_manager import PipelineManager

class AgencyType(Enum):
    """Types of recruiting agencies"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    CONTINGENCY = "contingency"
    RETAINED = "retained"
    FREELANCE = "freelance"

class RecruiterShield:
    """Manage recruiter relationships while maintaining first contact advantage"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'data_layer' / 'unified_career.db'
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.pipeline_manager = PipelineManager(db_path)
    
    def register_recruiter(self, name: str, email: str = None,
                          agency: str = None, agency_type: AgencyType = AgencyType.EXTERNAL,
                          linkedin: str = None, companies: List[str] = None) -> str:
        """Register a new recruiter interaction"""
        
        # Check if recruiter exists
        existing = self._find_recruiter(email or name)
        if existing:
            print(f"⚠️ Recruiter already registered: {name}")
            return existing['recruiter_uid']
        
        # Generate UID
        recruiter_uid = self._generate_uid(name, email or agency or datetime.now())
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO recruiter_interactions (
                recruiter_uid, name, email, agency, agency_type,
                linkedin_profile, companies_represented,
                first_contact_date, interaction_count,
                interaction_history
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            recruiter_uid, name, email, agency, agency_type.value,
            linkedin, json.dumps(companies or []),
            datetime.now(), 1,
            json.dumps([{
                'date': datetime.now().isoformat(),
                'type': 'initial_contact',
                'details': f'Registered {agency_type.value} recruiter'
            }])
        ))
        
        self.conn.commit()
        
        print(f"✅ Recruiter registered: {name} ({agency or 'Independent'})")
        print(f"   🔐 UID: {recruiter_uid}")
        
        return recruiter_uid
    
    def check_first_contact_conflict(self, recruiter_email: str,
                                    companies: List[str]) -> Dict:
        """Check if recruiter's companies conflict with existing pipeline"""
        
        # Find recruiter
        recruiter = self._find_recruiter(recruiter_email)
        if not recruiter:
            return {
                'recruiter_found': False,
                'message': 'Recruiter not in system'
            }
        
        conflicts = []
        new_opportunities = []
        
        for company in companies:
            # Check if we have first contact
            verification = self.pipeline_manager.verify_first_contact(company)
            
            if verification['has_contact']:
                conflicts.append({
                    'company': company,
                    'first_contact_date': verification['first_contact_date'],
                    'contact_type': verification['contact_type'],
                    'message': f"Already engaged since {verification['first_contact_date']}"
                })
            else:
                new_opportunities.append(company)
        
        # Update recruiter's overlap
        self._update_recruiter_overlap(recruiter['recruiter_uid'], conflicts)
        
        return {
            'recruiter': recruiter['name'],
            'companies_pitched': len(companies),
            'conflicts': len(conflicts),
            'new_opportunities': len(new_opportunities),
            'conflict_details': conflicts,
            'available_companies': new_opportunities,
            'recommendation': self._generate_recommendation(conflicts, new_opportunities)
        }
    
    def _generate_recommendation(self, conflicts: List[Dict],
                                new_opportunities: List[str]) -> str:
        """Generate recommendation for recruiter interaction"""
        
        if not conflicts:
            return "✅ No conflicts - recruiter can help with all companies"
        
        conflict_rate = len(conflicts) / (len(conflicts) + len(new_opportunities))
        
        if conflict_rate > 0.8:
            return "❌ High overlap - limited value from this recruiter"
        elif conflict_rate > 0.5:
            return "⚠️ Moderate overlap - selective engagement recommended"
        else:
            return "✅ Low overlap - recruiter can add value"
    
    def log_recruiter_interaction(self, recruiter_email: str,
                                 interaction_type: str,
                                 companies_discussed: List[str] = None,
                                 value_provided: Dict = None,
                                 notes: str = None) -> bool:
        """Log an interaction with a recruiter"""
        
        recruiter = self._find_recruiter(recruiter_email)
        if not recruiter:
            print(f"❌ Recruiter not found: {recruiter_email}")
            return False
        
        cursor = self.conn.cursor()
        
        # Get current history
        history = json.loads(recruiter['interaction_history'] or '[]')
        history.append({
            'date': datetime.now().isoformat(),
            'type': interaction_type,
            'companies': companies_discussed,
            'value': value_provided,
            'notes': notes
        })
        
        # Update companies pitched
        pitched = set(json.loads(recruiter['companies_pitched'] or '[]'))
        if companies_discussed:
            pitched.update(companies_discussed)
        
        # Update value assessment
        current_value = json.loads(recruiter['value_provided'] or '{}')
        if value_provided:
            current_value.update(value_provided)
        
        cursor.execute("""
            UPDATE recruiter_interactions
            SET interaction_history = ?,
                interaction_count = interaction_count + 1,
                last_contact_date = ?,
                companies_pitched = ?,
                value_provided = ?,
                updated_at = ?
            WHERE recruiter_uid = ?
        """, (
            json.dumps(history),
            datetime.now(),
            json.dumps(list(pitched)),
            json.dumps(current_value),
            datetime.now(),
            recruiter['recruiter_uid']
        ))
        
        self.conn.commit()
        
        print(f"📝 Interaction logged for {recruiter['name']}")
        
        return True
    
    def rate_recruiter(self, recruiter_email: str, quality_score: float,
                      is_trusted: bool = False, notes: str = None) -> bool:
        """Rate a recruiter's quality and trustworthiness"""
        
        recruiter = self._find_recruiter(recruiter_email)
        if not recruiter:
            return False
        
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE recruiter_interactions
            SET quality_score = ?,
                is_trusted = ?,
                notes = COALESCE(notes || '\n' || ?, notes, ?),
                updated_at = ?
            WHERE recruiter_uid = ?
        """, (
            quality_score, is_trusted,
            notes, notes,
            datetime.now(),
            recruiter['recruiter_uid']
        ))
        
        self.conn.commit()
        
        print(f"⭐ Recruiter rated: {recruiter['name']} - Score: {quality_score}/10")
        
        return True
    
    def generate_recruiter_report(self) -> Dict:
        """Generate report on all recruiter interactions"""
        
        cursor = self.conn.cursor()
        
        # Get all recruiters
        cursor.execute("""
            SELECT * FROM recruiter_interactions
            ORDER BY quality_score DESC NULLS LAST, interaction_count DESC
        """)
        
        recruiters = []
        total_value = {
            'insider_info': 0,
            'salary_data': 0,
            'introductions': 0,
            'interview_prep': 0
        }
        
        for row in cursor.fetchall():
            value = json.loads(row['value_provided'] or '{}')
            
            # Update total value
            for key in total_value:
                if value.get(key):
                    total_value[key] += 1
            
            recruiters.append({
                'name': row['name'],
                'agency': row['agency'],
                'interactions': row['interaction_count'],
                'quality_score': row['quality_score'],
                'is_trusted': row['is_trusted'],
                'companies_pitched': len(json.loads(row['companies_pitched'] or '[]')),
                'value_provided': value,
                'last_contact': row['last_contact_date']
            })
        
        # Calculate overlap statistics
        cursor.execute("""
            SELECT COUNT(DISTINCT company) 
            FROM contact_timeline
        """)
        pipeline_companies = cursor.fetchone()[0]
        
        return {
            'total_recruiters': len(recruiters),
            'trusted_recruiters': sum(1 for r in recruiters if r['is_trusted']),
            'total_interactions': sum(r['interactions'] for r in recruiters),
            'average_quality': sum(r['quality_score'] or 0 for r in recruiters) / len(recruiters) if recruiters else 0,
            'value_provided': total_value,
            'pipeline_companies': pipeline_companies,
            'top_recruiters': recruiters[:5],
            'recruiters': recruiters
        }
    
    def export_recruiter_shield_report(self, output_path: str = None) -> str:
        """Export report showing pipeline protection from recruiters"""
        
        if not output_path:
            output_path = f"recruiter_shield_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Get all companies in pipeline
        pipeline_companies = self.pipeline_manager.generate_first_contact_report()
        
        # Get recruiter report
        recruiter_report = self.generate_recruiter_report()
        
        shield_report = {
            'generated_at': datetime.now().isoformat(),
            'pipeline_protection': {
                'companies_engaged': len(pipeline_companies),
                'first_contact_established': len(pipeline_companies),
                'average_days_engaged': sum(c['days_engaged'] for c in pipeline_companies) / len(pipeline_companies) if pipeline_companies else 0
            },
            'recruiter_summary': {
                'total_recruiters': recruiter_report['total_recruiters'],
                'trusted_recruiters': recruiter_report['trusted_recruiters'],
                'value_received': recruiter_report['value_provided']
            },
            'protected_companies': [
                {
                    'company': c['company'],
                    'first_contact': c['first_contact'],
                    'days_protected': c['days_engaged']
                }
                for c in pipeline_companies[:20]  # Top 20
            ],
            'recruiter_effectiveness': recruiter_report['top_recruiters']
        }
        
        with open(output_path, 'w') as f:
            json.dump(shield_report, f, indent=2, default=str)
        
        print(f"🛡️ Recruiter Shield Report exported to: {output_path}")
        return output_path
    
    def _find_recruiter(self, identifier: str) -> Optional[Dict]:
        """Find recruiter by email or name"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM recruiter_interactions
            WHERE email = ? OR name = ?
        """, (identifier, identifier))
        
        return cursor.fetchone()
    
    def _update_recruiter_overlap(self, recruiter_uid: str, conflicts: List[Dict]):
        """Update recruiter's overlap with pipeline"""
        cursor = self.conn.cursor()
        
        overlap_companies = [c['company'] for c in conflicts]
        
        cursor.execute("""
            UPDATE recruiter_interactions
            SET overlap_with_pipeline = ?,
                updated_at = ?
            WHERE recruiter_uid = ?
        """, (
            json.dumps(overlap_companies),
            datetime.now(),
            recruiter_uid
        ))
        
        self.conn.commit()
    
    def _generate_uid(self, *args) -> str:
        """Generate unique identifier"""
        import hashlib
        content = ''.join(str(arg) for arg in args)
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def close(self):
        """Close connections"""
        self.conn.close()
        self.pipeline_manager.close()

def main():
    """Test recruiter shield"""
    shield = RecruiterShield()
    
    # Register a recruiter
    recruiter_uid = shield.register_recruiter(
        "Sarah Johnson",
        "sarah@techrecruit.com",
        "TechRecruit Inc",
        AgencyType.EXTERNAL,
        companies=["Anthropic", "OpenAI", "Google", "Meta"]
    )
    
    # Check for conflicts
    conflicts = shield.check_first_contact_conflict(
        "sarah@techrecruit.com",
        ["Anthropic", "OpenAI", "Databricks", "Scale AI"]
    )
    
    print("\n🛡️ First Contact Conflict Check:")
    print(json.dumps(conflicts, indent=2, default=str))
    
    # Log an interaction
    shield.log_recruiter_interaction(
        "sarah@techrecruit.com",
        "phone_call",
        companies_discussed=["Databricks", "Scale AI"],
        value_provided={
            "salary_data": True,
            "insider_info": True
        },
        notes="Provided comp ranges for Databricks ML roles"
    )
    
    # Rate the recruiter
    shield.rate_recruiter(
        "sarah@techrecruit.com",
        quality_score=8.5,
        is_trusted=True,
        notes="Good industry knowledge, respects first contact"
    )
    
    # Generate report
    report = shield.generate_recruiter_report()
    print("\n📊 Recruiter Report:")
    print(json.dumps(report, indent=2, default=str))
    
    shield.close()

if __name__ == "__main__":
    main()