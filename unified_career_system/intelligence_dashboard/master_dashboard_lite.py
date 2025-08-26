#!/usr/bin/env python3
"""
Master Intelligence Dashboard - Lite Version (No ML Dependencies)
Works without sentence-transformers, torch, or tensorflow
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from unified_career_system.data_layer.master_database import MasterDatabase

class MasterDashboardLite:
    """Lite version of dashboard without ML dependencies"""
    
    def __init__(self):
        # Use the correct path to the database
        import os
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data_layer',
            "unified_platform.db"
        )
        self.db = MasterDatabase(db_path)
        
        # Dashboard state
        self.refresh_interval = 30  # seconds
        self.last_refresh = None
        self.cache = {}
        
    def get_system_overview(self) -> Dict:
        """Get high-level system metrics"""
        print("\n📊 GATHERING SYSTEM METRICS...")
        
        overview = {
            'timestamp': datetime.now().isoformat(),
            'database': self._get_database_stats(),
            'applications': self._get_application_stats(),
            'responses': self._get_response_stats(),
            'daily_progress': self._get_daily_progress(),
            'system_health': self._get_system_health()
        }
        
        return overview
    
    def _get_database_stats(self) -> Dict:
        """Get database statistics"""
        conn = self.db.conn
        cursor = conn.cursor()
        
        stats = {}
        
        # Total jobs
        cursor.execute("SELECT COUNT(*) FROM jobs")
        stats['total_jobs'] = cursor.fetchone()[0]
        
        # Jobs by source
        cursor.execute("""
            SELECT source, COUNT(*) 
            FROM jobs 
            GROUP BY source 
            ORDER BY COUNT(*) DESC
        """)
        stats['by_source'] = dict(cursor.fetchall())
        
        # New jobs today
        cursor.execute("""
            SELECT COUNT(*) 
            FROM jobs 
            WHERE date(discovered_date) = date('now')
        """)
        stats['new_today'] = cursor.fetchone()[0]
        
        # Active jobs (not expired)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM jobs 
            WHERE is_active = 1
        """)
        stats['active_jobs'] = cursor.fetchone()[0]
        
        # Don't close connection - it's persistent
        return stats
    
    def _get_application_stats(self) -> Dict:
        """Get application statistics"""
        conn = self.db.conn
        cursor = conn.cursor()
        
        stats = {}
        
        # Total applications
        cursor.execute("SELECT COUNT(*) FROM applications")
        stats['total_sent'] = cursor.fetchone()[0]
        
        # Applications today
        cursor.execute("""
            SELECT COUNT(*) 
            FROM applications 
            WHERE date(applied_date) = date('now')
        """)
        stats['sent_today'] = cursor.fetchone()[0]
        
        # Applications by status
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM applications 
            GROUP BY status
        """)
        stats['by_status'] = dict(cursor.fetchall())
        
        # Applications by channel
        cursor.execute("""
            SELECT method, COUNT(*) 
            FROM applications 
            GROUP BY application_method
        """)
        stats['by_channel'] = dict(cursor.fetchall())
        
        # Success rate
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN response_type IN ('interview', 'offer') THEN 1 END) * 100.0 / 
                NULLIF(COUNT(*), 0) as success_rate
            FROM applications
            WHERE response_type IS NOT NULL
        """)
        result = cursor.fetchone()
        stats['success_rate'] = round(result[0] if result[0] else 0, 1)
        
        # Don't close connection - it's persistent
        return stats
    
    def _get_response_stats(self) -> Dict:
        """Get email response statistics"""
        conn = self.db.conn
        cursor = conn.cursor()
        
        stats = {}
        
        # Response types
        cursor.execute("""
            SELECT response_type, COUNT(*) 
            FROM applications 
            WHERE response_type IS NOT NULL
            GROUP BY response_type
        """)
        stats['by_type'] = dict(cursor.fetchall())
        
        # Response rate
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) * 100.0 / 
                NULLIF(COUNT(*), 0) as response_rate
            FROM applications
        """)
        result = cursor.fetchone()
        stats['response_rate'] = round(result[0] if result[0] else 0, 1)
        
        # Average response time
        cursor.execute("""
            SELECT AVG(julianday(response_date) - julianday(applied_date))
            FROM applications
            WHERE response_date IS NOT NULL
        """)
        result = cursor.fetchone()
        stats['avg_response_days'] = round(result[0] if result[0] else 0, 1)
        
        # Don't close connection - it's persistent
        return stats
    
    def _get_daily_progress(self) -> Dict:
        """Get today's progress towards daily goals"""
        goal_applications = 50
        goal_responses = 5
        goal_interviews = 2
        
        conn = self.db.conn
        cursor = conn.cursor()
        
        # Today's applications
        cursor.execute("""
            SELECT COUNT(*) 
            FROM applications 
            WHERE date(applied_date) = date('now')
        """)
        today_apps = cursor.fetchone()[0]
        
        # Today's responses
        cursor.execute("""
            SELECT COUNT(*) 
            FROM emails 
            WHERE date(received_date) = date('now') 
            AND classification IN ('interview', 'offer', 'rejection')
        """)
        today_responses = cursor.fetchone()[0]
        
        # Today's interviews scheduled
        cursor.execute("""
            SELECT COUNT(*) 
            FROM applications 
            WHERE date(response_date) = date('now') 
            AND response_type = 'interview'
        """)
        today_interviews = cursor.fetchone()[0]
        
        # Don't close connection - it's persistent
        
        return {
            'applications': {
                'current': today_apps,
                'goal': goal_applications,
                'progress': min(100, round(today_apps * 100 / goal_applications))
            },
            'responses': {
                'current': today_responses,
                'goal': goal_responses,
                'progress': min(100, round(today_responses * 100 / goal_responses))
            },
            'interviews': {
                'current': today_interviews,
                'goal': goal_interviews,
                'progress': min(100, round(today_interviews * 100 / goal_interviews))
            }
        }
    
    def _get_system_health(self) -> Dict:
        """Get system health indicators"""
        health = {
            'status': 'healthy',
            'components': {},
            'alerts': []
        }
        
        # Check database
        try:
            conn = self.db.conn
            conn.execute("SELECT 1")
            health['components']['database'] = 'operational'
        except:
            health['components']['database'] = 'error'
            health['status'] = 'degraded'
            health['alerts'].append("Database connection issue")
        
        # Check rate limits
        conn = self.db.conn
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM applications 
            WHERE datetime(applied_date) > datetime('now', '-1 hour')
        """)
        recent_apps = cursor.fetchone()[0]
        # Don't close connection - it's persistent
        
        if recent_apps > 15:
            health['alerts'].append(f"High application rate: {recent_apps}/hour")
        
        health['components']['ml_engine'] = 'not_loaded'
        health['components']['gmail'] = 'not_configured'
        health['alerts'].append("Running in lite mode (no ML dependencies)")
        
        return health
    
    def get_job_discovery_feed(self, limit: int = 20) -> List[Dict]:
        """Get recent job discoveries"""
        print("\n🔍 DISCOVERING NEW OPPORTUNITIES...")
        
        conn = self.db.conn
        cursor = conn.cursor()
        
        # Get recent jobs
        cursor.execute("""
            SELECT 
                j.*,
                c.response_rate,
                c.avg_response_days,
                CASE 
                    WHEN j.discovered_date > datetime('now', '-1 day') THEN 'new'
                    WHEN j.discovered_date > datetime('now', '-3 days') THEN 'recent'
                    ELSE 'older'
                END as freshness
            FROM jobs j
            LEFT JOIN company_intelligence c ON j.company = c.company_name
            WHERE j.is_active = 1
            ORDER BY j.discovered_date DESC
            LIMIT ?
        """, (limit,))
        
        jobs = []
        for row in cursor.fetchall():
            job = dict(zip([col[0] for col in cursor.description], row))
            jobs.append(job)
        
        # Don't close connection - it's persistent
        return jobs
    
    def display_dashboard(self):
        """Display the complete dashboard"""
        print("\n" + "="*80)
        print("🚀 UNIFIED CAREER INTELLIGENCE DASHBOARD (LITE)")
        print("="*80)
        
        # Get all data
        overview = self.get_system_overview()
        
        # System Overview
        print("\n📊 SYSTEM OVERVIEW")
        print("-" * 40)
        db_stats = overview['database']
        print(f"Total Jobs: {db_stats['total_jobs']} ({db_stats['active_jobs']} active)")
        print(f"New Today: {db_stats['new_today']}")
        if db_stats['by_source']:
            print(f"Sources: {', '.join(f'{k}:{v}' for k,v in list(db_stats['by_source'].items())[:3])}")
        
        # Application Stats
        print("\n📮 APPLICATION STATS")
        print("-" * 40)
        app_stats = overview['applications']
        print(f"Total Sent: {app_stats['total_sent']}")
        print(f"Sent Today: {app_stats['sent_today']}")
        print(f"Success Rate: {app_stats['success_rate']}%")
        
        # Response Stats
        print("\n📧 RESPONSE STATS")
        print("-" * 40)
        resp_stats = overview['responses']
        print(f"Response Rate: {resp_stats['response_rate']}%")
        print(f"Avg Response Time: {resp_stats['avg_response_days']} days")
        if resp_stats['by_type']:
            print(f"Types: {resp_stats['by_type']}")
        
        # Daily Progress
        print("\n🎯 DAILY PROGRESS")
        print("-" * 40)
        progress = overview['daily_progress']
        for metric, data in progress.items():
            bar = "█" * (data['progress'] // 5) + "░" * (20 - data['progress'] // 5)
            print(f"{metric.capitalize()}: [{bar}] {data['current']}/{data['goal']} ({data['progress']}%)")
        
        # System Health
        print("\n💚 SYSTEM HEALTH")
        print("-" * 40)
        health = overview['system_health']
        print(f"Status: {health['status'].upper()}")
        for component, status in health['components'].items():
            icon = "✅" if status == 'operational' else "⚠️" if status == 'limited' else "❌"
            print(f"  {icon} {component}: {status}")
        
        if health['alerts']:
            print("\n⚠️ ALERTS:")
            for alert in health['alerts']:
                print(f"  - {alert}")
        
        # Top Jobs
        print("\n🔥 RECENT JOBS")
        print("-" * 40)
        jobs = self.get_job_discovery_feed(5)
        for job in jobs[:5]:
            print(f"{job['company']} - {job['title']}")
            print(f"  {job.get('freshness', '')} | {job.get('location', 'Remote')}")
        
        print("\n" + "="*80)
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Note: Running in LITE mode without ML dependencies")
        print("="*80)

def main():
    """Run the lite dashboard"""
    dashboard = MasterDashboardLite()
    dashboard.display_dashboard()

if __name__ == "__main__":
    main()