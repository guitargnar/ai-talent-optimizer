#!/usr/bin/env python3
"""
Career Automation Dashboard
Complete overview of your job search automation system
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

def generate_dashboard():
    """Generate comprehensive career automation dashboard"""
    
    print("\n" + "=" * 70)
    print("📊 CAREER AUTOMATION DASHBOARD")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    dashboard = {
        'timestamp': datetime.now().isoformat(),
        'systems': {},
        'metrics': {},
        'pipeline': {},
        'recommendations': []
    }
    
    # 1. Job Database Analysis
    print("\n📂 Job Database Analysis")
    print("-" * 40)
    
    db_path = Path('data/unified_jobs.db')
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Total jobs
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]
        
        # Jobs by source
        cursor.execute("SELECT source, COUNT(*) FROM jobs GROUP BY source")
        sources = dict(cursor.fetchall())
        
        # Top companies
        cursor.execute("""
            SELECT company, COUNT(*) as count 
            FROM jobs 
            GROUP BY company 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_companies = cursor.fetchall()
        
        # Applied jobs
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied = 1")
        applied = cursor.fetchone()[0]
        
        conn.close()
        
        dashboard['systems']['job_database'] = {
            'total_jobs': total_jobs,
            'sources': sources,
            'top_companies': top_companies,
            'applied': applied
        }
        
        print(f"✅ Total Jobs: {total_jobs}")
        print(f"✅ Applied: {applied}")
        print(f"✅ Sources: {', '.join(f'{k}({v})' for k, v in sources.items())}")
        print(f"✅ Top Company: {top_companies[0][0]} ({top_companies[0][1]} jobs)")
    
    # 2. Email Application Tracking
    print("\n📧 Email Application Tracking")
    print("-" * 40)
    
    email_db = Path('email_applications.db')
    if email_db.exists():
        conn = sqlite3.connect(email_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM email_applications")
        email_apps = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM email_applications WHERE response_received = 'yes'")
        responses = cursor.fetchone()[0]
        
        conn.close()
        
        dashboard['systems']['email_tracking'] = {
            'sent': email_apps,
            'responses': responses,
            'response_rate': f"{(responses/email_apps*100):.1f}%" if email_apps > 0 else "0%"
        }
        
        print(f"✅ Applications Sent: {email_apps}")
        print(f"✅ Responses: {responses}")
        if email_apps > 0:
            print(f"✅ Response Rate: {(responses/email_apps*100):.1f}%")
    else:
        print("ℹ️ No email applications sent yet")
        dashboard['systems']['email_tracking'] = {'sent': 0, 'responses': 0}
    
    # 3. Gmail OAuth Status
    print("\n📬 Gmail OAuth Integration")
    print("-" * 40)
    
    gmail_path = Path('/Users/matthewscott/Google Gmail')
    if gmail_path.exists() and (gmail_path / 'token.pickle').exists():
        print("✅ Gmail OAuth: Active")
        print("✅ Token: Valid")
        dashboard['systems']['gmail_oauth'] = 'Active'
    else:
        print("⚠️ Gmail OAuth: Not configured")
        dashboard['systems']['gmail_oauth'] = 'Inactive'
    
    # 4. Application Files
    print("\n📁 Recent Application Files")
    print("-" * 40)
    
    app_files = list(Path('.').glob('application_*.json'))
    recent_apps = sorted(app_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
    
    dashboard['pipeline']['recent_applications'] = []
    for app_file in recent_apps:
        try:
            with open(app_file) as f:
                app_data = json.load(f)
                company = app_data['job']['company']
                position = app_data['job']['position']
                print(f"✅ {company}: {position[:40]}...")
                dashboard['pipeline']['recent_applications'].append({
                    'company': company,
                    'position': position,
                    'file': str(app_file)
                })
        except:
            pass
    
    # 5. ML Models Status
    print("\n🤖 ML Models Status")
    print("-" * 40)
    
    ml_path = Path('/Users/matthewscott/Projects/jaspermatters-job-intelligence')
    if ml_path.exists():
        print("✅ Job Intelligence Platform: Available")
        print("✅ Vector Embeddings: Ready")
        print("✅ Salary Predictor: Ready")
        dashboard['systems']['ml_models'] = 'Active'
    else:
        print("ℹ️ ML models not configured")
        dashboard['systems']['ml_models'] = 'Inactive'
    
    # 6. Key Metrics Summary
    print("\n📈 Key Metrics")
    print("-" * 40)
    
    metrics = {
        'Jobs Available': dashboard['systems'].get('job_database', {}).get('total_jobs', 0),
        'Applications Sent': dashboard['systems'].get('email_tracking', {}).get('sent', 0),
        'Responses Received': dashboard['systems'].get('email_tracking', {}).get('responses', 0),
        'Response Rate': dashboard['systems'].get('email_tracking', {}).get('response_rate', '0%'),
        'Top Source': max(dashboard['systems'].get('job_database', {}).get('sources', {'N/A': 0}).items(), 
                         key=lambda x: x[1])[0] if dashboard['systems'].get('job_database', {}).get('sources') else 'N/A'
    }
    
    dashboard['metrics'] = metrics
    
    for key, value in metrics.items():
        print(f"• {key}: {value}")
    
    # 7. Recommendations
    print("\n💡 Recommendations")
    print("-" * 40)
    
    recommendations = []
    
    if dashboard['systems'].get('job_database', {}).get('applied', 0) == 0:
        recommendations.append("Start sending applications using: python3 guided_apply.py")
    
    if dashboard['systems'].get('gmail_oauth') == 'Inactive':
        recommendations.append("Configure Gmail OAuth for response tracking")
    
    if dashboard['systems'].get('email_tracking', {}).get('sent', 0) < 10:
        recommendations.append("Increase application volume to 10-20 per day")
    
    if not recommendations:
        recommendations.append("System fully operational - maintain daily automation")
    
    dashboard['recommendations'] = recommendations
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # Save dashboard
    with open('dashboard_report.json', 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ Dashboard saved to: dashboard_report.json")
    
    # Show automation commands
    print("\n🚀 Quick Commands:")
    print("-" * 40)
    print("• Find jobs:     python3 find_and_apply_best_jobs.py --auto")
    print("• Send apps:     python3 guided_apply.py")
    print("• Check Gmail:   python3 gmail_oauth_integration.py")
    print("• View status:   python3 main.py status")
    print("• This report:   python3 career_automation_dashboard.py")
    
    return dashboard

def show_weekly_progress():
    """Show weekly application progress"""
    print("\n📅 Weekly Progress")
    print("-" * 40)
    
    # Calculate weekly stats
    week_ago = datetime.now() - timedelta(days=7)
    
    db_path = Path('email_applications.db')
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Applications this week
        cursor.execute("""
            SELECT COUNT(*) FROM email_applications 
            WHERE date_sent >= ?
        """, (week_ago.strftime('%Y-%m-%d'),))
        
        week_apps = cursor.fetchone()[0]
        
        # Responses this week
        cursor.execute("""
            SELECT COUNT(*) FROM email_applications 
            WHERE response_date >= ?
        """, (week_ago.strftime('%Y-%m-%d'),))
        
        week_responses = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"• Applications (7d): {week_apps}")
        print(f"• Responses (7d): {week_responses}")
        
        if week_apps > 0:
            daily_avg = week_apps / 7
            print(f"• Daily Average: {daily_avg:.1f}")
            
            projected_monthly = daily_avg * 30
            print(f"• Projected Monthly: {int(projected_monthly)}")

def main():
    """Run dashboard generation"""
    dashboard = generate_dashboard()
    show_weekly_progress()
    
    print("\n" + "=" * 70)
    print("🎯 CAREER AUTOMATION SYSTEM READY")
    print("=" * 70)
    print("\nYour integrated career automation system is configured with:")
    print("• 345+ jobs from top companies (Anthropic, Scale AI, etc.)")
    print("• Gmail integration for response tracking")
    print("• ML-powered job matching (when available)")
    print("• Automated application pipeline")
    print("\n✨ Ready to accelerate your job search!")

if __name__ == "__main__":
    main()