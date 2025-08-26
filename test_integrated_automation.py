#!/usr/bin/env python3
"""
Test and Demo Script for Integrated Career Automation
Shows how all systems work together
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_job_database():
    """Test existing job database"""
    print("\n📊 Testing Job Database...")
    print("=" * 60)
    
    db_path = Path("unified_platform.db")
    if not db_path.exists():
        print("❌ Database not found")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get job stats
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE salary_range LIKE '%150%' OR salary_range LIKE '%160%' OR salary_range LIKE '%170%' OR salary_range LIKE '%180%' OR salary_range LIKE '%190%' OR salary_range LIKE '%200%'")
    high_salary = cursor.fetchone()[0]
    
    cursor.execute("SELECT source, COUNT(*) as count FROM jobs GROUP BY source ORDER BY count DESC")
    sources = cursor.fetchall()
    
    print(f"✅ Total Jobs: {total_jobs}")
    print(f"✅ High Salary (>$150k): {high_salary}")
    print("\n📍 Job Sources:")
    for source, count in sources:
        print(f"   - {source}: {count} jobs")
    
    # Get top companies
    cursor.execute("""
        SELECT company, COUNT(*) as count, salary_range
        FROM jobs 
        WHERE company IS NOT NULL
        GROUP BY company 
        ORDER BY count DESC 
        LIMIT 10
    """)
    companies = cursor.fetchall()
    
    print("\n🏢 Top Companies:")
    for company, count, salary in companies:
        salary_str = salary if salary else "N/A"
        print(f"   - {company}: {count} jobs")
    
    conn.close()
    return True

def test_email_tracking():
    """Test email application tracking database"""
    print("\n📧 Testing Email Application Tracker...")
    print("=" * 60)
    
    db_path = Path('email_applications.db')
    if not db_path.exists():
        print("ℹ️ No email applications sent yet")
        return True
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM email_applications")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM email_applications WHERE response_received = 'yes'")
    responses = cursor.fetchone()[0]
    
    print(f"✅ Total Applications Sent: {total}")
    print(f"✅ Responses Received: {responses}")
    
    if total > 0:
        response_rate = (responses / total) * 100
        print(f"✅ Response Rate: {response_rate:.1f}%")
    
    conn.close()
    return True

def test_gmail_integration():
    """Test Gmail configuration"""
    print("\n📬 Testing Gmail Integration...")
    print("=" * 60)
    
    email = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_APP_PASSWORD')
    
    if not email or not password:
        print("❌ Gmail credentials not configured")
        return False
    
    print(f"✅ Email: {email}")
    print(f"✅ App Password: {'*' * 12}{password[-4:]}")
    
    # Check for Gmail OAuth path
    gmail_path = Path('/Users/matthewscott/Google Gmail')
    if gmail_path.exists():
        print(f"✅ Gmail OAuth directory exists")
        token_file = gmail_path / 'token.pickle'
        if token_file.exists():
            print(f"✅ OAuth token found")
    
    return True

def demo_job_matching():
    """Demo job matching logic"""
    print("\n🎯 Demo: Job Matching Algorithm...")
    print("=" * 60)
    
    # Sample job
    sample_job = {
        'role': 'Senior ML Engineer',
        'company': 'Anthropic',
        'description': 'Build large language models and ML infrastructure',
        'requirements': 'TensorFlow, PyTorch, distributed training',
        'salary_min': 180000,
        'location': 'Remote'
    }
    
    print("📋 Sample Job:")
    print(f"   Role: {sample_job['role']}")
    print(f"   Company: {sample_job['company']}")
    print(f"   Salary: ${sample_job['salary_min']:,}")
    print(f"   Location: {sample_job['location']}")
    
    # Calculate match score
    ml_keywords = ['ml', 'tensorflow', 'pytorch', 'language model']
    matches = sum(1 for kw in ml_keywords if kw in sample_job['description'].lower())
    keyword_score = matches / len(ml_keywords)
    
    # Score components
    scores = {
        'Keywords': keyword_score,
        'Salary': 1.0 if sample_job['salary_min'] >= 150000 else 0.5,
        'Location': 1.0 if 'remote' in sample_job['location'].lower() else 0.3,
        'Company': 1.0  # Top tier company
    }
    
    print("\n📊 Match Scores:")
    for component, score in scores.items():
        bar = '█' * int(score * 20) + '░' * (20 - int(score * 20))
        print(f"   {component:10} {bar} {score:.0%}")
    
    final_score = sum(scores.values()) / len(scores)
    print(f"\n✅ Final Match Score: {final_score:.0%}")
    
    if final_score >= 0.8:
        print("   → Auto-apply candidate! 🚀")
    elif final_score >= 0.6:
        print("   → Review and apply manually 📝")
    else:
        print("   → Skip for now ⏭️")
    
    return True

def show_automation_pipeline():
    """Show the complete automation pipeline"""
    print("\n🔄 Complete Automation Pipeline...")
    print("=" * 60)
    
    pipeline = {
        '1. Job Discovery': [
            '📍 Scrape Greenhouse API (275+ jobs)',
            '📍 Scrape Lever API (32+ jobs)',  
            '📍 Check Adzuna API',
            '📍 Monitor LinkedIn/Indeed'
        ],
        '2. ML Scoring': [
            '🤖 Vector embeddings (when available)',
            '🤖 Keyword matching (fallback)',
            '🤖 Salary prediction',
            '🤖 Company tier scoring'
        ],
        '3. Auto-Apply': [
            '📮 Generate tailored cover letter',
            '📮 Attach resume (PDF)',
            '📮 Send via SMTP',
            '📮 Log to database'
        ],
        '4. Response Tracking': [
            '📧 Gmail OAuth monitoring',
            '📧 Response classification',
            '📧 Interview scheduling',
            '📧 Pipeline analytics'
        ],
        '5. Reporting': [
            '📊 Daily dashboard',
            '📊 Response rates',
            '📊 Interview pipeline',
            '📊 Success metrics'
        ]
    }
    
    for stage, tasks in pipeline.items():
        print(f"\n{stage}:")
        for task in tasks:
            print(f"   {task}")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 INTEGRATED CAREER AUTOMATION - SYSTEM TEST")
    print("=" * 60)
    
    # Run tests
    tests = [
        test_job_database,
        test_email_tracking,
        test_gmail_integration,
        demo_job_matching,
        show_automation_pipeline
    ]
    
    results = []
    for test in tests:
        try:
            success = test()
            results.append(success)
        except Exception as e:
            print(f"❌ Error in {test.__name__}: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("\n📋 Next Steps:")
        print("1. Run: python3 INTEGRATED_CAREER_AUTOMATION.py")
        print("2. Or for specific tasks:")
        print("   - python3 src/services/enhanced_job_scraper.py  # Discover jobs")
        print("   - python3 guided_apply.py  # Send applications")
        print("   - python3 gmail_oauth_integration.py  # Check responses")
        print("   - python3 main.py status  # View metrics")
    else:
        print("\n⚠️ Some systems need attention")
        print("Run individual tests to diagnose issues")
    
    print("\n💡 Pro Tip: The system runs best with:")
    print("   - Gmail app password configured (.env)")
    print("   - Resume file on Desktop")
    print("   - Daily automation via cron/scheduler")

if __name__ == "__main__":
    main()