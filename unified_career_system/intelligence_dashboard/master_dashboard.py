#!/usr/bin/env python3
"""
Master Intelligence Dashboard - Phase 5
Real-time command center for unified career automation
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
from unified_career_system.ml_engine.job_matcher import JobMatcher
from unified_career_system.application_pipeline.orchestrator import ApplicationOrchestrator
from unified_career_system.response_hub.gmail_central import GmailCentral

class MasterDashboard:
    """Real-time intelligence dashboard for career automation"""
    
    def __init__(self):
        self.db = MasterDatabase()
        self.matcher = JobMatcher()
        self.orchestrator = ApplicationOrchestrator()
        self.gmail = GmailCentral()
        
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
            'ml_performance': self._get_ml_stats(),
            'daily_progress': self._get_daily_progress(),
            'system_health': self._get_system_health()
        }
        
        return overview
    
    def _get_database_stats(self) -> Dict:
        """Get database statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total jobs
        cursor.execute("SELECT COUNT(*) FROM master_jobs")
        stats['total_jobs'] = cursor.fetchone()[0]
        
        # Jobs by source
        cursor.execute("""
            SELECT source, COUNT(*) 
            FROM master_jobs 
            GROUP BY source 
            ORDER BY COUNT(*) DESC
        """)
        stats['by_source'] = dict(cursor.fetchall())
        
        # New jobs today
        cursor.execute("""
            SELECT COUNT(*) 
            FROM master_jobs 
            WHERE date(discovered_at) = date('now')
        """)
        stats['new_today'] = cursor.fetchone()[0]
        
        # Active jobs (not expired)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM master_jobs 
            WHERE status = 'active'
        """)
        stats['active_jobs'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def _get_application_stats(self) -> Dict:
        """Get application statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total applications
        cursor.execute("SELECT COUNT(*) FROM master_applications")
        stats['total_sent'] = cursor.fetchone()[0]
        
        # Applications today
        cursor.execute("""
            SELECT COUNT(*) 
            FROM master_applications 
            WHERE date(applied_at) = date('now')
        """)
        stats['sent_today'] = cursor.fetchone()[0]
        
        # Applications by status
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM master_applications 
            GROUP BY status
        """)
        stats['by_status'] = dict(cursor.fetchall())
        
        # Applications by channel
        cursor.execute("""
            SELECT application_channel, COUNT(*) 
            FROM master_applications 
            GROUP BY application_channel
        """)
        stats['by_channel'] = dict(cursor.fetchall())
        
        # Success rate
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN response_type IN ('interview', 'offer') THEN 1 END) * 100.0 / 
                NULLIF(COUNT(*), 0) as success_rate
            FROM master_applications
            WHERE response_type IS NOT NULL
        """)
        result = cursor.fetchone()
        stats['success_rate'] = round(result[0] if result[0] else 0, 1)
        
        conn.close()
        return stats
    
    def _get_response_stats(self) -> Dict:
        """Get email response statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Response types
        cursor.execute("""
            SELECT response_type, COUNT(*) 
            FROM master_applications 
            WHERE response_type IS NOT NULL
            GROUP BY response_type
        """)
        stats['by_type'] = dict(cursor.fetchall())
        
        # Response rate
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) * 100.0 / 
                NULLIF(COUNT(*), 0) as response_rate
            FROM master_applications
        """)
        result = cursor.fetchone()
        stats['response_rate'] = round(result[0] if result[0] else 0, 1)
        
        # Average response time
        cursor.execute("""
            SELECT AVG(julianday(response_received_at) - julianday(applied_at))
            FROM master_applications
            WHERE response_received_at IS NOT NULL
        """)
        result = cursor.fetchone()
        stats['avg_response_days'] = round(result[0] if result[0] else 0, 1)
        
        conn.close()
        return stats
    
    def _get_ml_stats(self) -> Dict:
        """Get ML model performance statistics"""
        stats = {
            'models_active': 5,
            'embeddings_cached': len(self.matcher.vector_store.embeddings) if hasattr(self.matcher, 'vector_store') else 0,
            'avg_match_score': 0,
            'high_priority_jobs': 0,
            'recommendations_today': 0
        }
        
        # Get match statistics
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT AVG(ml_score) 
            FROM master_jobs 
            WHERE ml_score IS NOT NULL
        """)
        result = cursor.fetchone()
        stats['avg_match_score'] = round(result[0] if result[0] else 0, 3)
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM master_jobs 
            WHERE ml_score > 0.8 AND status = 'active'
        """)
        stats['high_priority_jobs'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def _get_daily_progress(self) -> Dict:
        """Get today's progress towards daily goals"""
        goal_applications = 50
        goal_responses = 5
        goal_interviews = 2
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Today's applications
        cursor.execute("""
            SELECT COUNT(*) 
            FROM master_applications 
            WHERE date(applied_at) = date('now')
        """)
        today_apps = cursor.fetchone()[0]
        
        # Today's responses
        cursor.execute("""
            SELECT COUNT(*) 
            FROM email_tracking 
            WHERE date(received_at) = date('now') 
            AND classification IN ('interview', 'offer', 'rejection')
        """)
        today_responses = cursor.fetchone()[0]
        
        # Today's interviews scheduled
        cursor.execute("""
            SELECT COUNT(*) 
            FROM master_applications 
            WHERE date(response_received_at) = date('now') 
            AND response_type = 'interview'
        """)
        today_interviews = cursor.fetchone()[0]
        
        conn.close()
        
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
            conn = self.db.get_connection()
            conn.execute("SELECT 1")
            conn.close()
            health['components']['database'] = 'operational'
        except:
            health['components']['database'] = 'error'
            health['status'] = 'degraded'
            health['alerts'].append("Database connection issue")
        
        # Check ML models
        try:
            if hasattr(self.matcher, 'ensemble') and self.matcher.ensemble:
                health['components']['ml_engine'] = 'operational'
            else:
                health['components']['ml_engine'] = 'limited'
        except:
            health['components']['ml_engine'] = 'error'
            health['status'] = 'degraded'
            health['alerts'].append("ML models not loaded")
        
        # Check Gmail
        try:
            if self.gmail.service:
                health['components']['gmail'] = 'operational'
            else:
                health['components']['gmail'] = 'not_configured'
        except:
            health['components']['gmail'] = 'error'
            health['alerts'].append("Gmail API not configured")
        
        # Check rate limits
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM master_applications 
            WHERE datetime(applied_at) > datetime('now', '-1 hour')
        """)
        recent_apps = cursor.fetchone()[0]
        conn.close()
        
        if recent_apps > 15:
            health['alerts'].append(f"High application rate: {recent_apps}/hour")
        
        return health
    
    def get_job_discovery_feed(self, limit: int = 20) -> List[Dict]:
        """Get real-time job discovery feed"""
        print("\n🔍 DISCOVERING NEW OPPORTUNITIES...")
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get recent high-score jobs
        cursor.execute("""
            SELECT 
                j.*,
                c.response_rate,
                c.avg_response_days,
                CASE 
                    WHEN j.discovered_at > datetime('now', '-1 day') THEN 'new'
                    WHEN j.discovered_at > datetime('now', '-3 days') THEN 'recent'
                    ELSE 'older'
                END as freshness
            FROM master_jobs j
            LEFT JOIN company_intelligence c ON j.company = c.company_name
            WHERE j.status = 'active'
            ORDER BY 
                CASE WHEN j.discovered_at > datetime('now', '-1 day') THEN 1 ELSE 0 END DESC,
                j.ml_score DESC,
                j.discovered_at DESC
            LIMIT ?
        """, (limit,))
        
        jobs = []
        for row in cursor.fetchall():
            job = dict(zip([col[0] for col in cursor.description], row))
            
            # Add recommendation
            if job['ml_score']:
                if job['ml_score'] > 0.8:
                    job['recommendation'] = '🔥 HIGHLY RECOMMENDED'
                elif job['ml_score'] > 0.6:
                    job['recommendation'] = '⭐ RECOMMENDED'
                elif job['ml_score'] > 0.4:
                    job['recommendation'] = '👍 WORTH CONSIDERING'
                else:
                    job['recommendation'] = '📌 BACKUP OPTION'
            
            jobs.append(job)
        
        conn.close()
        return jobs
    
    def get_application_tracker(self) -> Dict:
        """Get detailed application status tracking"""
        print("\n📋 TRACKING APPLICATION STATUS...")
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get all applications with details
        cursor.execute("""
            SELECT 
                a.*,
                j.title,
                j.location,
                j.salary_min,
                j.salary_max,
                c.response_rate,
                c.interview_rate
            FROM master_applications a
            JOIN master_jobs j ON a.job_id = j.job_id
            LEFT JOIN company_intelligence c ON a.company = c.company_name
            ORDER BY a.applied_at DESC
        """)
        
        applications = []
        for row in cursor.fetchall():
            app = dict(zip([col[0] for col in cursor.description], row))
            
            # Calculate days since application
            applied_date = datetime.fromisoformat(app['applied_at'])
            app['days_waiting'] = (datetime.now() - applied_date).days
            
            # Add status indicator
            if app['response_type'] == 'interview':
                app['status_icon'] = '🎉'
            elif app['response_type'] == 'offer':
                app['status_icon'] = '🏆'
            elif app['response_type'] == 'rejection':
                app['status_icon'] = '❌'
            elif app['days_waiting'] > 14:
                app['status_icon'] = '⏰'
            else:
                app['status_icon'] = '⏳'
            
            applications.append(app)
        
        # Group by status
        tracker = {
            'all_applications': applications,
            'by_status': defaultdict(list),
            'follow_up_needed': [],
            'interviews_scheduled': []
        }
        
        for app in applications:
            tracker['by_status'][app['status']].append(app)
            
            if app['days_waiting'] > 7 and not app['response_type']:
                tracker['follow_up_needed'].append(app)
            
            if app['response_type'] == 'interview':
                tracker['interviews_scheduled'].append(app)
        
        conn.close()
        return tracker
    
    def get_performance_analytics(self) -> Dict:
        """Get detailed performance analytics"""
        print("\n📈 ANALYZING PERFORMANCE...")
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        analytics = {
            'company_performance': self._analyze_company_performance(cursor),
            'channel_effectiveness': self._analyze_channel_effectiveness(cursor),
            'timing_analysis': self._analyze_timing(cursor),
            'ml_accuracy': self._analyze_ml_accuracy(cursor),
            'weekly_trends': self._analyze_weekly_trends(cursor)
        }
        
        conn.close()
        return analytics
    
    def _analyze_company_performance(self, cursor) -> List[Dict]:
        """Analyze performance by company"""
        cursor.execute("""
            SELECT 
                company,
                COUNT(*) as applications,
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as responses,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews,
                COUNT(CASE WHEN response_type = 'offer' THEN 1 END) as offers,
                ROUND(
                    COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) * 100.0 / 
                    COUNT(*), 1
                ) as response_rate
            FROM master_applications
            GROUP BY company
            HAVING COUNT(*) > 0
            ORDER BY response_rate DESC, applications DESC
        """)
        
        return [dict(zip([col[0] for col in cursor.description], row)) 
                for row in cursor.fetchall()]
    
    def _analyze_channel_effectiveness(self, cursor) -> Dict:
        """Analyze effectiveness by application channel"""
        cursor.execute("""
            SELECT 
                application_channel,
                COUNT(*) as total,
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as responses,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews,
                ROUND(
                    COUNT(CASE WHEN response_type = 'interview' THEN 1 END) * 100.0 / 
                    COUNT(*), 1
                ) as interview_rate
            FROM master_applications
            GROUP BY application_channel
        """)
        
        return {row[0]: {
            'total': row[1],
            'responses': row[2],
            'interviews': row[3],
            'interview_rate': row[4]
        } for row in cursor.fetchall()}
    
    def _analyze_timing(self, cursor) -> Dict:
        """Analyze best times for applications"""
        cursor.execute("""
            SELECT 
                strftime('%H', applied_at) as hour,
                COUNT(*) as applications,
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as responses,
                ROUND(
                    COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) * 100.0 / 
                    COUNT(*), 1
                ) as response_rate
            FROM master_applications
            GROUP BY hour
            ORDER BY response_rate DESC
        """)
        
        by_hour = [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT 
                strftime('%w', applied_at) as day_of_week,
                COUNT(*) as applications,
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as responses,
                ROUND(
                    COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) * 100.0 / 
                    COUNT(*), 1
                ) as response_rate
            FROM master_applications
            GROUP BY day_of_week
            ORDER BY day_of_week
        """)
        
        by_day = [dict(zip([col[0] for col in cursor.description], row)) 
                  for row in cursor.fetchall()]
        
        return {
            'by_hour': by_hour,
            'by_day_of_week': by_day
        }
    
    def _analyze_ml_accuracy(self, cursor) -> Dict:
        """Analyze ML model accuracy"""
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN ml_score > 0.8 THEN 'high'
                    WHEN ml_score > 0.6 THEN 'medium'
                    WHEN ml_score > 0.4 THEN 'low'
                    ELSE 'very_low'
                END as score_range,
                COUNT(*) as jobs,
                COUNT(CASE WHEN job_id IN (SELECT job_id FROM master_applications) THEN 1 END) as applied,
                COUNT(CASE WHEN job_id IN (
                    SELECT job_id FROM master_applications WHERE response_type = 'interview'
                ) THEN 1 END) as interviews
            FROM master_jobs
            WHERE ml_score IS NOT NULL
            GROUP BY score_range
        """)
        
        accuracy = {}
        for row in cursor.fetchall():
            score_range = row[0]
            accuracy[score_range] = {
                'jobs': row[1],
                'applied': row[2],
                'interviews': row[3],
                'application_rate': round(row[2] * 100.0 / row[1], 1) if row[1] > 0 else 0,
                'interview_rate': round(row[3] * 100.0 / row[2], 1) if row[2] > 0 else 0
            }
        
        return accuracy
    
    def _analyze_weekly_trends(self, cursor) -> List[Dict]:
        """Analyze weekly trends"""
        cursor.execute("""
            SELECT 
                strftime('%Y-W%W', applied_at) as week,
                COUNT(*) as applications,
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as responses,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews
            FROM master_applications
            GROUP BY week
            ORDER BY week DESC
            LIMIT 8
        """)
        
        return [dict(zip([col[0] for col in cursor.description], row)) 
                for row in cursor.fetchall()]
    
    def display_dashboard(self):
        """Display the complete dashboard"""
        print("\n" + "="*80)
        print("🚀 UNIFIED CAREER INTELLIGENCE DASHBOARD")
        print("="*80)
        
        # Get all data
        overview = self.get_system_overview()
        
        # System Overview
        print("\n📊 SYSTEM OVERVIEW")
        print("-" * 40)
        db_stats = overview['database']
        print(f"Total Jobs: {db_stats['total_jobs']} ({db_stats['active_jobs']} active)")
        print(f"New Today: {db_stats['new_today']}")
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
        
        # Top Opportunities
        print("\n🔥 TOP OPPORTUNITIES")
        print("-" * 40)
        jobs = self.get_job_discovery_feed(5)
        for job in jobs[:5]:
            print(f"{job.get('recommendation', '')} {job['company']} - {job['title']}")
            print(f"  Score: {job.get('ml_score', 0):.2f} | {job.get('freshness', '')} | {job.get('location', 'Remote')}")
        
        print("\n" + "="*80)
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
    
    def run_continuous(self):
        """Run dashboard in continuous mode"""
        print("Starting continuous dashboard mode...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                self.display_dashboard()
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\nDashboard stopped.")

def main():
    """Run the master dashboard"""
    dashboard = MasterDashboard()
    
    # Check for continuous mode
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        dashboard.run_continuous()
    else:
        dashboard.display_dashboard()
        
        # Show additional analytics
        print("\n" + "="*80)
        print("📈 DETAILED ANALYTICS")
        print("="*80)
        
        analytics = dashboard.get_performance_analytics()
        
        # Company Performance
        print("\n🏢 TOP PERFORMING COMPANIES")
        print("-" * 40)
        for company in analytics['company_performance'][:5]:
            print(f"{company['company']}: {company['response_rate']}% response rate")
            print(f"  Apps: {company['applications']} | Interviews: {company['interviews']}")
        
        # Channel Effectiveness
        print("\n📡 CHANNEL EFFECTIVENESS")
        print("-" * 40)
        for channel, stats in analytics['channel_effectiveness'].items():
            print(f"{channel}: {stats['interview_rate']}% interview rate ({stats['total']} sent)")
        
        # ML Accuracy
        print("\n🤖 ML MODEL ACCURACY")
        print("-" * 40)
        for score_range, stats in analytics['ml_accuracy'].items():
            print(f"{score_range.upper()} scores: {stats['interview_rate']}% interview rate")
            print(f"  Jobs: {stats['jobs']} | Applied: {stats['applied']}")

if __name__ == "__main__":
    main()