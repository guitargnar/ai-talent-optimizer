#!/usr/bin/env python3
"""
AI Job Hunter Dashboard - Visual Status Overview
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import os

class Dashboard:
    """Visual dashboard for job hunting status"""
    
    def __init__(self):
        self.db_path = "unified_platform.db"
        self.bcc_log_path = "data/bcc_tracking_log.json"
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.full_name == 'posix' else 'cls')
    
    def print_header(self):
        """Print dashboard header"""
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 20 + "AI JOB HUNTER DASHBOARD" + " " * 15 + "║")
        print("║" + " " * 58 + "║")
        print("║" + f"  Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " " * 26 + "║")
        print("╚" + "═" * 58 + "╝")
    
    def get_stats(self):
        """Get current statistics"""
        stats = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total jobs
            cursor.execute("SELECT COUNT(*) FROM jobs")
            stats['total_jobs'] = cursor.fetchone()[0]
            
            # Applied jobs
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied=1")
            stats['total_applied'] = cursor.fetchone()[0]
            
            # Today's applications
            cursor.execute("""
                SELECT COUNT(*) FROM jobs 
                WHERE applied=1 AND DATE(applied_date) = DATE('now')
            """)
            stats['today_applied'] = cursor.fetchone()[0]
            
            # This week's applications
            cursor.execute("""
                SELECT COUNT(*) FROM jobs 
                WHERE applied=1 AND applied_date > datetime('now', '-7 days')
            """)
            stats['week_applied'] = cursor.fetchone()[0]
            
            # Pending high-value
            cursor.execute("""
                SELECT COUNT(*) FROM jobs 
                WHERE applied=0 AND relevance_score >= 0.65
            """)
            stats['pending_high'] = cursor.fetchone()[0]
            
            # Top companies applied
            cursor.execute("""
                SELECT company, COUNT(*) as count 
                FROM jobs 
                WHERE applied=1 
                GROUP BY company 
                ORDER BY count DESC 
                LIMIT 5
            """)
            stats['top_companies'] = cursor.fetchall()
            
            # Recent applications
            cursor.execute("""
                SELECT company, title, applied_date 
                FROM jobs 
                WHERE applied=1 
                ORDER BY applied_date DESC 
                LIMIT 5
            """)
            stats['recent_apps'] = cursor.fetchall()
            
            # Application rate by day
            cursor.execute("""
                SELECT DATE(applied_date) as date, COUNT(*) as count 
                FROM jobs 
                WHERE applied=1 AND applied_date > datetime('now', '-7 days')
                GROUP BY date 
                ORDER BY date DESC
            """)
            stats['daily_rate'] = cursor.fetchall()
            
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
            return None
        
        # Email stats
        if Path(self.bcc_log_path).exists():
            with open(self.bcc_log_path) as f:
                bcc_log = json.load(f)
                stats['total_emails'] = len(bcc_log.get('sent_emails', {}))
        else:
            stats['total_emails'] = 0
        
        return stats
    
    def print_summary_box(self, stats):
        """Print summary statistics"""
        print("\n┌─── SUMMARY ─────────────────────────────────────────────┐")
        print(f"│ Total Jobs Discovered:  {stats['total_jobs']:>6} │ Applications Sent: {stats['total_applied']:>6} │")
        print(f"│ Applied Today:          {stats['today_applied']:>6} │ This Week:         {stats['week_applied']:>6} │")
        print(f"│ High-Value Pending:     {stats['pending_high']:>6} │ Emails Tracked:    {stats['total_emails']:>6} │")
        print("└─────────────────────────────────────────────────────────┘")
    
    def print_activity_chart(self, stats):
        """Print daily activity chart"""
        print("\n📊 LAST 7 DAYS ACTIVITY")
        print("─" * 40)
        
        if stats['daily_rate']:
            max_count = max(count for _, count in stats['daily_rate'])
            
            for date_str, count in stats['daily_rate']:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                day_name = date_obj.strftime('%a')
                bar_length = int((count / max_count) * 20) if max_count > 0 else 0
                bar = "█" * bar_length
                print(f"{date_str} ({day_name}): {bar} {count}")
        else:
            print("No activity in the last 7 days")
    
    def print_recent_applications(self, stats):
        """Print recent applications"""
        print("\n📧 RECENT APPLICATIONS")
        print("─" * 60)
        
        if stats['recent_apps']:
            for company, title, date_str in stats['recent_apps']:
                date_obj = datetime.fromisoformat(date_str)
                time_ago = datetime.now() - date_obj
                
                if time_ago.days == 0:
                    if time_ago.seconds < 3600:
                        ago = f"{time_ago.seconds // 60} minutes ago"
                    else:
                        ago = f"{time_ago.seconds // 3600} hours ago"
                else:
                    ago = f"{time_ago.days} days ago"
                
                # Truncate long text
                company = company[:20] + "..." if len(company) > 20 else company
                title = position[:30] + "..." if len(title) > 30 else position
                
                print(f"• {company:<23} │ {position:<33} │ {ago}")
        else:
            print("No recent applications")
    
    def print_top_companies(self, stats):
        """Print top companies"""
        print("\n🏢 TOP COMPANIES APPLIED TO")
        print("─" * 40)
        
        if stats['top_companies']:
            for company, count in stats['top_companies']:
                bar = "▓" * count
                print(f"{company:<25} {bar} ({count})")
        else:
            print("No applications sent yet")
    
    def print_next_actions(self, stats):
        """Print recommended next actions"""
        print("\n⚡ RECOMMENDED ACTIONS")
        print("─" * 60)
        
        if stats['today_applied'] < 10:
            remaining = 10 - stats['today_applied']
            print(f"• Send {remaining} more applications today: python automated_apply.py --batch {remaining}")
        
        if stats['pending_high'] > 20:
            print(f"• High-value jobs available! Review: python automated_apply.py --batch 10")
        
        if stats['week_applied'] < 50:
            print("• Below weekly target (50). Increase daily applications.")
        
        print("\n💡 Quick Commands:")
        print("  • Status Report: python generate_status_report.py")
        print("  • Apply Now:     python automated_apply.py --batch 5")
        print("  • Full Auto:     python run_automation.py")
    
    def display(self):
        """Display the dashboard"""
        self.clear_screen()
        self.print_header()
        
        stats = self.get_stats()
        if not stats:
            print("\n❌ Could not load statistics. Check database connection.")
            return
        
        self.print_summary_box(stats)
        self.print_activity_chart(stats)
        self.print_recent_applications(stats)
        self.print_top_companies(stats)
        self.print_next_actions(stats)
        
        print("\n" + "─" * 60)
        print("Press Ctrl+C to exit | Auto-refresh disabled")
        print("─" * 60)


def main():
    """Run dashboard"""
    dashboard = Dashboard()
    
    try:
        dashboard.display()
        
        # Keep dashboard open
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\n\n👋 Exiting dashboard...")


if __name__ == "__main__":
    main()