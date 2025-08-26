#!/usr/bin/env python3
"""
Pipeline Manager - Core pipeline tracking with first contact advantage
Maintains timestamped proof of all job search activities
"""

import os
import sys
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ContactType(Enum):
    """Types of first contact"""
    DISCOVERED = "discovered"
    APPLIED = "applied"
    RECRUITER_INBOUND = "recruiter_inbound"
    REFERRAL = "referral"
    NETWORKING = "networking"
    COLD_OUTREACH = "cold_outreach"

class ContactSource(Enum):
    """Source of contact"""
    SELF_INITIATED = "self_initiated"
    INBOUND = "inbound"
    REFERRAL = "referral"
    EVENT = "event"
    AUTOMATED = "automated"

class PipelineManager:
    """Manage job search pipeline with first contact tracking"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'data_layer' / "unified_platform.db"
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def record_first_contact(self, company: str, position: str = None,
                            contact_type: ContactType = ContactType.DISCOVERED,
                            contact_source: ContactSource = ContactSource.SELF_INITIATED,
                            proof_url: str = None, notes: str = None) -> str:
        """Record first contact with a company/position"""
        
        # Check if contact already exists
        existing = self._check_existing_contact(company, title)
        if existing:
            print(f"⚠️ Contact already exists for {company} - {position or 'General'}")
            return existing['contact_uid']
        
        # Generate unique ID
        contact_uid = self._generate_uid(company, title, datetime.now())
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO contact_timeline (
                contact_uid, company, title, first_contact_date,
                contact_type, contact_source, contact_proof, proof_type,
                notes, interaction_history
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contact_uid, company, title, datetime.now(),
            contact_type.value, contact_source.value,
            proof_url, 'url' if proof_url else None,
            notes,
            json.dumps([{
                'date': datetime.now().isoformat(),
                'type': 'first_contact',
                'details': f'{contact_type.value} via {contact_source.value}'
            }])
        ))
        
        self.conn.commit()
        
        print(f"✅ First contact recorded: {company} - {position or 'General'}")
        print(f"   📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   🔐 UID: {contact_uid}")
        
        return contact_uid
    
    def _check_existing_contact(self, company: str, position: str = None) -> Optional[Dict]:
        """Check if contact already exists"""
        cursor = self.conn.cursor()
        
        if position:
            cursor.execute("""
                SELECT * FROM contact_timeline 
                WHERE company = ? AND title = ?
            """, (company, title))
        else:
            cursor.execute("""
                SELECT * FROM contact_timeline 
                WHERE company = ? AND position IS NULL
            """, (company,))
        
        return cursor.fetchone()
    
    def verify_first_contact(self, company: str, position: str = None) -> Dict:
        """Verify and return first contact proof for a company"""
        
        cursor = self.conn.cursor()
        
        # Get all contacts for this company
        cursor.execute("""
            SELECT contact_uid, title, first_contact_date, 
                   contact_type, contact_proof, verification_status
            FROM contact_timeline
            WHERE company = ?
            ORDER BY first_contact_date ASC
        """, (company,))
        
        contacts = cursor.fetchall()
        
        if not contacts:
            return {
                'has_contact': False,
                'company': company,
                'message': 'No prior contact recorded'
            }
        
        first = contacts[0]
        
        return {
            'has_contact': True,
            'company': company,
            'first_contact_date': first['first_contact_date'],
            'contact_type': first['contact_type'],
            'proof': first['contact_proof'],
            'verification_status': first['verification_status'],
            'total_interactions': len(contacts),
            'positions': [c['position'] for c in contacts if c['position']],
            'message': f"First contact established on {first['first_contact_date']}"
        }
    
    def log_activity(self, company: str, activity_type: str,
                    description: str, position: str = None,
                    outcome: str = None, next_steps: str = None) -> str:
        """Log an activity in the pipeline"""
        
        # Generate activity UID
        activity_uid = self._generate_uid(company, activity_type, datetime.now())
        
        # Find related contact
        contact = self._check_existing_contact(company, title)
        contact_uid = contact['contact_uid'] if contact else None
        
        # If no contact exists, create one
        if not contact_uid:
            contact_uid = self.record_first_contact(
                company, title,
                ContactType.DISCOVERED,
                ContactSource.SELF_INITIATED,
                notes=f"Created from activity: {activity_type}"
            )
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO pipeline_activities (
                activity_uid, company, title, activity_type,
                activity_date, description, outcome, next_steps,
                contact_uid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            activity_uid, company, title, activity_type,
            datetime.now(), description, outcome, next_steps,
            contact_uid
        ))
        
        # Update contact timeline
        if contact_uid:
            self._update_contact_interaction(contact_uid, activity_type, description)
        
        self.conn.commit()
        
        print(f"📝 Activity logged: {company} - {activity_type}")
        
        return activity_uid
    
    def _update_contact_interaction(self, contact_uid: str, 
                                   activity_type: str, description: str):
        """Update contact interaction history"""
        cursor = self.conn.cursor()
        
        # Get current interaction history
        cursor.execute("""
            SELECT interaction_history, interaction_count 
            FROM contact_timeline 
            WHERE contact_uid = ?
        """, (contact_uid,))
        
        result = cursor.fetchone()
        history = json.loads(result['interaction_history']) if result else []
        count = result['interaction_count'] if result else 0
        
        # Add new interaction
        history.append({
            'date': datetime.now().isoformat(),
            'type': activity_type,
            'details': description
        })
        
        # Update contact
        cursor.execute("""
            UPDATE contact_timeline
            SET interaction_history = ?,
                interaction_count = ?,
                last_interaction_date = ?,
                updated_at = ?
            WHERE contact_uid = ?
        """, (
            json.dumps(history),
            count + 1,
            datetime.now(),
            datetime.now(),
            contact_uid
        ))
    
    def get_pipeline_summary(self) -> Dict:
        """Get summary of entire pipeline"""
        cursor = self.conn.cursor()
        
        # Total contacts
        cursor.execute("SELECT COUNT(*) FROM contact_timeline")
        total_contacts = cursor.fetchone()[0]
        
        # Contacts by type
        cursor.execute("""
            SELECT contact_type, COUNT(*) as count
            FROM contact_timeline
            GROUP BY contact_type
        """)
        by_type = {row['contact_type']: row['count'] for row in cursor.fetchall()}
        
        # Recent activities
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pipeline_activities 
            WHERE activity_date > datetime('now', '-7 days')
        """)
        recent_activities = cursor.fetchone()[0]
        
        # Companies engaged
        cursor.execute("SELECT COUNT(DISTINCT company) FROM contact_timeline")
        companies_engaged = cursor.fetchone()[0]
        
        # Average interactions per contact
        cursor.execute("SELECT AVG(interaction_count) FROM contact_timeline")
        avg_interactions = cursor.fetchone()[0] or 0
        
        return {
            'total_contacts': total_contacts,
            'companies_engaged': companies_engaged,
            'contacts_by_type': by_type,
            'recent_activities': recent_activities,
            'avg_interactions': round(avg_interactions, 1),
            'pipeline_health': self._calculate_pipeline_health()
        }
    
    def _calculate_pipeline_health(self) -> str:
        """Calculate overall pipeline health"""
        cursor = self.conn.cursor()
        
        # Check activity in last 7 days
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pipeline_activities 
            WHERE activity_date > datetime('now', '-7 days')
        """)
        recent = cursor.fetchone()[0]
        
        if recent > 20:
            return "🔥 Very Active"
        elif recent > 10:
            return "✅ Healthy"
        elif recent > 5:
            return "⚠️ Moderate"
        else:
            return "❌ Needs Attention"
    
    def generate_first_contact_report(self, companies: List[str] = None) -> List[Dict]:
        """Generate report proving first contact for specified companies"""
        cursor = self.conn.cursor()
        
        if companies:
            placeholders = ','.join('?' * len(companies))
            query = f"""
                SELECT company, MIN(first_contact_date) as first_contact,
                       COUNT(*) as total_interactions,
                       GROUP_CONCAT(DISTINCT title) as positions
                FROM contact_timeline
                WHERE company IN ({placeholders})
                GROUP BY company
            """
            cursor.execute(query, companies)
        else:
            cursor.execute("""
                SELECT company, MIN(first_contact_date) as first_contact,
                       COUNT(*) as total_interactions,
                       GROUP_CONCAT(DISTINCT title) as positions
                FROM contact_timeline
                GROUP BY company
                ORDER BY first_contact_date DESC
                LIMIT 50
            """)
        
        report = []
        for row in cursor.fetchall():
            report.append({
                'company': row['company'],
                'first_contact': row['first_contact'],
                'days_engaged': (datetime.now() - datetime.fromisoformat(row['first_contact'])).days,
                'total_interactions': row['total_interactions'],
                'positions': row['positions'].split(',') if row['positions'] else []
            })
        
        return report
    
    def export_pipeline_audit(self, output_path: str = None) -> str:
        """Export complete pipeline audit trail"""
        if not output_path:
            output_path = f"pipeline_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        cursor = self.conn.cursor()
        
        # Get all contacts
        cursor.execute("""
            SELECT * FROM contact_timeline
            ORDER BY first_contact_date
        """)
        contacts = [dict(row) for row in cursor.fetchall()]
        
        # Get all activities
        cursor.execute("""
            SELECT * FROM pipeline_activities
            ORDER BY activity_date
        """)
        activities = [dict(row) for row in cursor.fetchall()]
        
        audit = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_pipeline_summary(),
            'contacts': contacts,
            'activities': activities,
            'total_companies': len(set(c['company'] for c in contacts)),
            'date_range': {
                'start': min(c['first_contact_date'] for c in contacts) if contacts else None,
                'end': datetime.now().isoformat()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(audit, f, indent=2, default=str)
        
        print(f"✅ Pipeline audit exported to: {output_path}")
        return output_path
    
    def _generate_uid(self, *args) -> str:
        """Generate unique identifier"""
        content = ''.join(str(arg) for arg in args)
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Test pipeline manager"""
    manager = PipelineManager()
    
    # Record some test contacts
    manager.record_first_contact(
        "Anthropic", "ML Engineer",
        ContactType.DISCOVERED,
        ContactSource.SELF_INITIATED,
        proof_url="https://anthropic.com/careers",
        notes="Found via direct search"
    )
    
    # Log an activity
    manager.log_activity(
        "Anthropic", "research",
        "Researched company culture and recent papers",
        title="ML Engineer",
        outcome="Good fit identified",
        next_steps="Prepare customized application"
    )
    
    # Get pipeline summary
    summary = manager.get_pipeline_summary()
    print("\n📊 Pipeline Summary:")
    print(json.dumps(summary, indent=2))
    
    # Verify first contact
    verification = manager.verify_first_contact("Anthropic")
    print("\n🔐 First Contact Verification:")
    print(json.dumps(verification, indent=2, default=str))
    
    manager.close()

if __name__ == "__main__":
    main()