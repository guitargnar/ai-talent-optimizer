#!/usr/bin/env python3
"""
Quality Application Tracker - Focus on depth, not volume
Track real applications with actual research and personalization
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

class QualityApplicationTracker:
    def __init__(self):
        """Initialize quality-focused tracker"""
        self.db_path = "QUALITY_APPLICATIONS.db"
        self._init_database()
    
    def _init_database(self):
        """Create database focused on quality metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                
                -- Research Quality Metrics
                research_hours REAL DEFAULT 0,
                company_research_complete BOOLEAN DEFAULT 0,
                found_hiring_manager BOOLEAN DEFAULT 0,
                found_team_members BOOLEAN DEFAULT 0,
                read_recent_news BOOLEAN DEFAULT 0,
                understand_tech_stack BOOLEAN DEFAULT 0,
                
                -- Contact Quality
                contact_name TEXT,
                contact_title TEXT,
                contact_method TEXT,  -- LinkedIn, Email, Referral
                contact_verified BOOLEAN DEFAULT 0,
                
                -- Application Quality
                custom_cover_letter BOOLEAN DEFAULT 0,
                resume_tailored BOOLEAN DEFAULT 0,
                addressed_requirements BOOLEAN DEFAULT 0,
                showed_company_knowledge BOOLEAN DEFAULT 0,
                
                -- Submission Details
                application_method TEXT,  -- Portal, Email, LinkedIn
                portal_link TEXT,
                submitted_date TEXT,
                
                -- Follow-up
                followed_up BOOLEAN DEFAULT 0,
                follow_up_date TEXT,
                follow_up_method TEXT,
                
                -- Response Tracking
                response_received BOOLEAN DEFAULT 0,
                response_date TEXT,
                response_type TEXT,  -- Interview, Rejection, Auto-reply
                interview_scheduled BOOLEAN DEFAULT 0,
                
                -- Quality Score (0-100)
                quality_score INTEGER DEFAULT 0,
                
                -- Notes
                why_interested TEXT,
                unique_value_prop TEXT,
                notes TEXT,
                
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def calculate_quality_score(self, app_data):
        """Calculate quality score based on effort and personalization"""
        score = 0
        
        # Research quality (40 points)
        if app_data.get('company_research_complete'): score += 10
        if app_data.get('found_hiring_manager'): score += 10
        if app_data.get('found_team_members'): score += 5
        if app_data.get('read_recent_news'): score += 5
        if app_data.get('understand_tech_stack'): score += 10
        
        # Contact quality (20 points)
        if app_data.get('contact_name'): score += 10
        if app_data.get('contact_verified'): score += 10
        
        # Application quality (30 points)
        if app_data.get('custom_cover_letter'): score += 10
        if app_data.get('resume_tailored'): score += 10
        if app_data.get('addressed_requirements'): score += 5
        if app_data.get('showed_company_knowledge'): score += 5
        
        # Effort metric (10 points)
        research_hours = app_data.get('research_hours', 0)
        if research_hours >= 0.5: score += 5
        if research_hours >= 1.0: score += 5
        
        return min(score, 100)  # Cap at 100
    
    def add_application(self, app_data):
        """Add a quality application"""
        
        # Calculate quality score
        app_data['quality_score'] = self.calculate_quality_score(app_data)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        columns = list(app_data.keys())
        placeholders = ['?' for _ in columns]
        
        query = f"""
            INSERT INTO quality_applications ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """
        
        cursor.execute(query, list(app_data.values()))
        app_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        print(f"✅ Added quality application to {app_data['company']}")
        print(f"   Quality Score: {app_data['quality_score']}/100")
        
        return app_id
    
    def show_dashboard(self):
        """Show quality metrics dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(quality_score) as avg_quality,
                SUM(response_received) as responses,
                SUM(interview_scheduled) as interviews,
                AVG(research_hours) as avg_research_hours
            FROM quality_applications
        """)
        
        stats = cursor.fetchone()
        total, avg_quality, responses, interviews, avg_hours = stats
        
        print("\n" + "=" * 60)
        print("📊 QUALITY APPLICATION DASHBOARD")
        print("=" * 60)
        
        print(f"\n📈 Overall Metrics:")
        print(f"  Total Applications: {total or 0}")
        print(f"  Average Quality Score: {avg_quality or 0:.1f}/100")
        print(f"  Response Rate: {(responses or 0)/(total or 1)*100:.1f}%")
        print(f"  Interview Rate: {(interviews or 0)/(total or 1)*100:.1f}%")
        print(f"  Avg Research Time: {avg_hours or 0:.1f} hours")
        
        # Top quality applications
        cursor.execute("""
            SELECT company, position, quality_score, response_received, interview_scheduled
            FROM quality_applications
            ORDER BY quality_score DESC
            LIMIT 5
        """)
        
        top_apps = cursor.fetchall()
        
        if top_apps:
            print(f"\n🏆 Top Quality Applications:")
            for company, position, score, response, interview in top_apps:
                status = "📅 Interview!" if interview else "✅ Response" if response else "⏳ Waiting"
                print(f"  • {company}: {position}")
                print(f"    Quality: {score}/100 | Status: {status}")
        
        # Applications needing follow-up
        three_days_ago = (datetime.now() - timedelta(days=3)).isoformat()
        cursor.execute("""
            SELECT company, position, submitted_date
            FROM quality_applications
            WHERE followed_up = 0
            AND submitted_date < ?
            AND response_received = 0
        """, (three_days_ago,))
        
        need_followup = cursor.fetchall()
        
        if need_followup:
            print(f"\n📮 Need Follow-up (3+ days old):")
            for company, position, submitted in need_followup:
                days_ago = (datetime.now() - datetime.fromisoformat(submitted)).days
                print(f"  • {company}: {position} ({days_ago} days ago)")
        
        conn.close()
        
        # Quality recommendations
        print("\n" + "=" * 60)
        print("💡 QUALITY RECOMMENDATIONS:")
        print("=" * 60)
        
        if total == 0:
            print("• Start with ONE deeply researched application")
            print("• Spend at least 1 hour researching the company")
            print("• Find the actual hiring manager on LinkedIn")
        elif avg_quality and avg_quality < 70:
            print("• Your quality score is low - spend more time researching")
            print("• Make sure to tailor each resume to the job")
            print("• Find specific people to contact, not generic emails")
        elif responses == 0:
            print("• No responses yet - consider your approach")
            print("• Are you applying to appropriate level roles?")
            print("• Is your value proposition clear?")
            print("• Follow up after 3-5 days")
        else:
            print("• Keep up the quality approach!")
            print("• Your response rate is positive")
            print("• Continue deep research before applying")
    
    def create_application_checklist(self, company, position):
        """Create a checklist for a quality application"""
        
        checklist = f"""
========================================
APPLICATION CHECKLIST: {company}
Position: {position}
========================================

RESEARCH PHASE (Minimum 1 hour)
--------------------------------
□ Company website reviewed
□ Recent news articles read (last 3 months)
□ Glassdoor reviews checked
□ Tech stack researched
□ Company challenges identified
□ Growth stage understood

PEOPLE RESEARCH (LinkedIn)
--------------------------
□ Hiring manager identified
  Name: ________________
  Title: _______________
□ Team members found
  Names: _______________
□ Recruiter identified
  Name: ________________
□ Common connections checked

CUSTOMIZATION
-------------
□ Resume tailored to job description
□ Cover letter addresses specific requirements
□ Company knowledge demonstrated
□ Unique value proposition clear
□ Specific problems you'll solve mentioned

APPLICATION METHOD
-----------------
□ Portal link found: ________________
□ OR Direct contact identified
□ Application submitted via: ___________
□ Confirmation received

QUALITY CHECKS
--------------
□ No generic "Dear Hiring Manager"
□ Company name spelled correctly
□ Position title exact
□ No template language
□ Proofread by someone else

FOLLOW-UP PLAN
--------------
□ Calendar reminder set (3 days)
□ Follow-up message drafted
□ LinkedIn connection requests sent
□ Thank you note if interviewed

========================================
Target Quality Score: 80+/100
========================================
"""
        return checklist

def main():
    """Run quality tracker"""
    tracker = QualityApplicationTracker()
    
    # Show dashboard
    tracker.show_dashboard()
    
    print("\n" + "=" * 60)
    print("🎯 QUALITY OVER QUANTITY")
    print("=" * 60)
    print("The new approach:")
    print("• 1 great application > 10 generic ones")
    print("• Research depth matters more than speed")
    print("• Real people > generic emails")
    print("• Company knowledge > keyword matching")
    print("\nYour goal: 5 applications with 80+ quality scores")

if __name__ == "__main__":
    main()