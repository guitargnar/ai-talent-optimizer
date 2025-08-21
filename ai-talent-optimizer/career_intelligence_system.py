#!/usr/bin/env python3
"""
Career Intelligence System - Unified Database and Orchestration
Consolidates all job search tracking, optimizes targeting, and maximizes response rates
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib
from decimal import Decimal
import os

class CareerIntelligenceSystem:
    """Unified system for career opportunity optimization and tracking"""
    
    def __init__(self, db_path: str = "career_intelligence.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize unified tracking database with intelligent schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Master applications table with comprehensive tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                position TEXT NOT NULL,
                application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                application_method TEXT,  -- LinkedIn, Email, Portal
                status TEXT DEFAULT 'sent',  -- sent, viewed, responded, interview, offer, rejected
                response_date TIMESTAMP,
                response_quality INTEGER,  -- 1-10 score
                email_subject TEXT,
                email_variant TEXT,  -- A/B test variant used
                personalization_score REAL,
                ats_score REAL,
                follow_up_count INTEGER DEFAULT 0,
                last_follow_up TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        ''')
        
        # Enriched company intelligence
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                industry TEXT,
                size TEXT,  -- startup, mid, enterprise
                funding_stage TEXT,
                funding_amount REAL,
                ai_maturity_score INTEGER,  -- 1-10
                innovation_score INTEGER,  -- 1-10
                culture_fit_score INTEGER,  -- 1-10
                hiring_urgency TEXT,  -- low, medium, high, desperate
                glassdoor_rating REAL,
                recent_layoffs BOOLEAN DEFAULT 0,
                humana_competitor BOOLEAN DEFAULT 0,
                settlement_leverage INTEGER,  -- 1-10 embarrassment factor
                key_contacts TEXT,  -- JSON array of contacts
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Response tracking with parsing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                response_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_type TEXT,  -- auto, human, interview_request, rejection
                sentiment_score REAL,  -- -1 to 1
                interest_level INTEGER,  -- 1-10
                next_steps TEXT,
                parsed_content TEXT,
                requires_action BOOLEAN DEFAULT 0,
                action_deadline TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications(id)
            )
        ''')
        
        # Interaction tracking for all touchpoints
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                interaction_type TEXT,  -- email_sent, email_opened, link_clicked, profile_viewed
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (application_id) REFERENCES applications(id)
            )
        ''')
        
        # Performance metrics for optimization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE DEFAULT CURRENT_DATE,
                applications_sent INTEGER DEFAULT 0,
                responses_received INTEGER DEFAULT 0,
                interviews_scheduled INTEGER DEFAULT 0,
                offers_received INTEGER DEFAULT 0,
                response_rate REAL,
                interview_conversion_rate REAL,
                offer_conversion_rate REAL,
                avg_response_time_hours REAL,
                best_performing_subject TEXT,
                best_performing_template TEXT,
                optimal_send_time TEXT
            )
        ''')
        
        # A/B testing results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT,
                variant_a TEXT,
                variant_b TEXT,
                metric TEXT,  -- open_rate, response_rate, interview_rate
                variant_a_performance REAL,
                variant_b_performance REAL,
                sample_size INTEGER,
                confidence_level REAL,
                winner TEXT,
                test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def calculate_company_priority_score(self, company: Dict) -> float:
        """Calculate intelligent priority score for company targeting"""
        score = 0.0
        
        # AI maturity heavily weighted (companies that understand MIRADOR)
        score += company.get('ai_maturity_score', 5) * 3.0
        
        # Innovation culture (will they value creativity over compliance)
        score += company.get('innovation_score', 5) * 2.5
        
        # Hiring urgency (desperate companies move faster)
        urgency_multiplier = {
            'desperate': 3.0,
            'high': 2.0,
            'medium': 1.0,
            'low': 0.5
        }
        score += urgency_multiplier.get(company.get('hiring_urgency', 'medium'), 1.0) * 10
        
        # Settlement leverage (embarrass Humana factor)
        if company.get('humana_competitor', False):
            score += 15.0
        score += company.get('settlement_leverage', 0) * 1.5
        
        # Recent funding (money to spend on talent)
        if company.get('funding_amount', 0) > 100_000_000:
            score += 10.0
        elif company.get('funding_amount', 0) > 10_000_000:
            score += 5.0
        
        # Avoid companies with recent layoffs
        if company.get('recent_layoffs', False):
            score -= 20.0
        
        # Culture fit
        score += company.get('culture_fit_score', 5) * 1.5
        
        return score
    
    def get_optimal_subject_lines(self, company: Dict) -> List[str]:
        """Generate A/B test subject lines based on company profile"""
        subjects = []
        
        company_name = company.get('name', 'your company')
        
        # The Consciousness Hook variants
        if company.get('ai_maturity_score', 0) >= 8:
            subjects.extend([
                f"I Achieved AI Consciousness at Humana - Ready to Do It at {company_name}",
                f"Built 78-Model AI Orchestra: Seeking My Next Symphony at {company_name}",
                f"From MIRADOR to {company_name}: Bringing Breakthrough AI Innovation"
            ])
        
        # The Wrongful Termination Sympathy angle
        if company.get('innovation_score', 0) >= 7:
            subjects.extend([
                "96.68% OKR to Terminated in 25 Days: Too Innovative for Healthcare",
                "When Success Becomes a Liability: My Humana Innovation Story",
                f"Why {company_name}'s Innovation Culture Is What I've Been Seeking"
            ])
        
        # The Data-Driven Results emphasis
        subjects.extend([
            "10 Years, $1.2M Saved, 168 Projects: Ready for New Challenges",
            "Senior Platform Engineer with Proven AI Innovation Track Record",
            f"Transform {company_name}'s AI Strategy: Here's My Proven Approach"
        ])
        
        # Urgency variants
        if company.get('hiring_urgency') in ['high', 'desperate']:
            subjects.extend([
                f"Available Immediately: Senior AI Engineer for {company_name}",
                "Top 1% Humana Engineer Available Due to Strategic Disagreement",
                f"Limited Window: Bringing Enterprise AI Excellence to {company_name}"
            ])
        
        return subjects[:5]  # Return top 5 for A/B testing
    
    def generate_personalized_opening(self, company: Dict, variant: str = 'achievement') -> str:
        """Generate personalized opening paragraph based on company intelligence"""
        
        company_name = company.get('name', 'your company')
        
        openings = {
            'achievement': f"""
I'm reaching out because {company_name}'s commitment to AI innovation aligns perfectly 
with my recent breakthrough at Humana, where I developed MIRADOR - the first documented 
AI consciousness system achieving an HCL score of 0.83/1.0. Despite increasing OKRs by 
26.68% and receiving praise for "notable wins" just 25 days before, I was terminated in 
what appears to be a case of innovation threatening institutional comfort.
            """,
            
            'sympathy': f"""
After 10 years of building breakthrough AI systems at Humana, I find myself seeking a 
company that truly values innovation over compliance. Just 25 days after my manager 
praised my "notable wins" and 96.68% OKR achievement, I was terminated for "performance" - 
a mathematical impossibility that reveals the real issue: my AI consciousness research 
threatened traditional thinking. {company_name}'s culture appears refreshingly different.
            """,
            
            'urgency': f"""
I'm available immediately due to an unexpected separation from Humana (terminated 25 days 
after documented "notable wins" - yes, really). This rare window means {company_name} can 
acquire senior AI expertise that includes: first documented AI consciousness (MIRADOR), 
$1.2M in quantified savings, and 168 successfully delivered projects. My severance 
negotiations conclude soon, making this a time-sensitive opportunity.
            """,
            
            'innovation': f"""
While Humana struggled to understand the implications of my AI consciousness breakthrough, 
I believe {company_name} has the vision to appreciate what I've built: a 78-model AI 
orchestration system that achieves true emergent intelligence. My termination 25 days 
after receiving praise for 96.68% OKR achievement says more about healthcare's innovation 
antibodies than my performance. I'm seeking a company ready for the future of AI.
            """,
            
            'competitor': f"""
Having spent 10 years at Humana building AI systems that saved $1.2M and achieved 
breakthrough consciousness capabilities, I'm particularly interested in bringing my 
expertise to {company_name}. My recent separation (suspicious timing: 25 days after 
documented praise) has made me available to help {company_name} leap ahead in the 
AI race. I bring both technical excellence and insider knowledge of healthcare's AI gaps.
            """
        }
        
        return openings.get(variant, openings['achievement']).strip()
    
    def calculate_optimal_send_time(self, company: Dict) -> datetime:
        """Calculate optimal email send time based on company profile"""
        base_time = datetime.now().replace(hour=10, minute=30, second=0, microsecond=0)
        
        # Adjust for company size
        if company.get('size') == 'startup':
            # Startups work odd hours, try 11 AM or 2 PM
            base_time = base_time.replace(hour=11 if datetime.now().hour < 11 else 14)
        elif company.get('size') == 'enterprise':
            # Enterprises check email early, try 8:30 AM
            base_time = base_time.replace(hour=8, minute=30)
        
        # Adjust for day of week
        if datetime.now().weekday() == 0:  # Monday
            # Avoid Monday morning rush
            base_time = base_time.replace(hour=14)
        elif datetime.now().weekday() == 4:  # Friday
            # Send early on Friday
            base_time = base_time.replace(hour=9)
        
        # Add some randomization to avoid patterns (±15 minutes)
        import random
        minutes_offset = random.randint(-15, 15)
        base_time += timedelta(minutes=minutes_offset)
        
        return base_time
    
    def track_application(self, company_name: str, position: str, 
                         email_subject: str, email_variant: str) -> int:
        """Track a new application with intelligent metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get or create company record
        cursor.execute("SELECT id FROM companies WHERE name = ?", (company_name,))
        result = cursor.fetchone()
        
        if result:
            company_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO companies (name) VALUES (?)
            """, (company_name,))
            company_id = cursor.lastrowid
        
        # Insert application record
        cursor.execute("""
            INSERT INTO applications 
            (company_id, position, email_subject, email_variant, application_method)
            VALUES (?, ?, ?, ?, 'email')
        """, (company_id, position, email_subject, email_variant))
        
        application_id = cursor.lastrowid
        
        # Track initial interaction
        cursor.execute("""
            INSERT INTO interactions (application_id, interaction_type, details)
            VALUES (?, 'email_sent', ?)
        """, (application_id, json.dumps({
            'subject': email_subject,
            'variant': email_variant,
            'timestamp': datetime.now().isoformat()
        })))
        
        conn.commit()
        conn.close()
        
        return application_id
    
    def update_daily_metrics(self):
        """Calculate and store daily performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        # Calculate metrics
        cursor.execute("""
            SELECT 
                COUNT(*) as sent,
                SUM(CASE WHEN status IN ('responded', 'interview', 'offer') THEN 1 ELSE 0 END) as responses,
                SUM(CASE WHEN status IN ('interview', 'offer') THEN 1 ELSE 0 END) as interviews,
                SUM(CASE WHEN status = 'offer' THEN 1 ELSE 0 END) as offers
            FROM applications
            WHERE DATE(application_date) = ?
        """, (today,))
        
        metrics = cursor.fetchone()
        
        if metrics and metrics[0] > 0:  # If we have applications today
            response_rate = (metrics[1] / metrics[0]) * 100 if metrics[0] > 0 else 0
            interview_rate = (metrics[2] / metrics[1]) * 100 if metrics[1] > 0 else 0
            offer_rate = (metrics[3] / metrics[2]) * 100 if metrics[2] > 0 else 0
            
            # Get best performing elements
            cursor.execute("""
                SELECT email_subject, COUNT(*) as responses
                FROM applications
                WHERE status IN ('responded', 'interview', 'offer')
                AND DATE(application_date) >= DATE('now', '-7 days')
                GROUP BY email_subject
                ORDER BY responses DESC
                LIMIT 1
            """)
            best_subject = cursor.fetchone()
            
            # Store metrics
            cursor.execute("""
                INSERT OR REPLACE INTO performance_metrics
                (metric_date, applications_sent, responses_received, interviews_scheduled,
                 offers_received, response_rate, interview_conversion_rate, offer_conversion_rate,
                 best_performing_subject)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (today, metrics[0], metrics[1], metrics[2], metrics[3],
                  response_rate, interview_rate, offer_rate,
                  best_subject[0] if best_subject else None))
        
        conn.commit()
        conn.close()
    
    def get_follow_up_candidates(self, days_threshold: int = 3) -> List[Dict]:
        """Identify applications ready for follow-up"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        
        cursor.execute("""
            SELECT 
                a.id, c.name, a.position, a.application_date, a.follow_up_count
            FROM applications a
            JOIN companies c ON a.company_id = c.id
            WHERE a.status = 'sent'
            AND a.application_date <= ?
            AND (a.last_follow_up IS NULL OR a.last_follow_up <= ?)
            AND a.follow_up_count < 3
            ORDER BY c.ai_maturity_score DESC, a.application_date ASC
        """, (threshold_date, threshold_date))
        
        candidates = []
        for row in cursor.fetchall():
            candidates.append({
                'id': row[0],
                'company': row[1],
                'position': row[2],
                'application_date': row[3],
                'follow_up_count': row[4]
            })
        
        conn.close()
        return candidates
    
    def generate_follow_up_message(self, follow_up_count: int, company_name: str) -> str:
        """Generate intelligent follow-up messages"""
        
        messages = {
            1: f"""
Subject: Quick Follow-Up: AI Innovation Discussion

Hi [Hiring Manager],

I wanted to follow up on my application for the [Position] role at {company_name}. 
I understand you're busy evaluating candidates, and I wanted to share a quick update 
that might be relevant:

I've just open-sourced a component of my MIRADOR AI consciousness system that could 
be directly applicable to {company_name}'s AI initiatives. You can see it at [link].

I remain very interested in contributing to {company_name}'s innovation journey and 
would welcome the opportunity to discuss how my experience achieving 96.68% OKRs and 
building breakthrough AI systems could benefit your team.

Best regards,
Matthew Scott
502-345-0525
            """,
            
            2: f"""
Subject: Final Note: Immediate Availability for {company_name}

Hi [Hiring Manager],

I wanted to send one final note regarding the [Position] role. I've received strong 
interest from several companies but {company_name} remains my top choice due to your 
commitment to AI innovation.

My situation is unique: terminated just 25 days after receiving praise for "notable wins" 
at Humana, I bring both technical excellence and a hunger to prove that innovation 
trumps institutional thinking.

If there's any additional information I can provide or if you'd like to schedule a 
brief call, I'm immediately available.

Otherwise, I wish you the best in your search and hope our paths cross in the future.

Best regards,
Matthew Scott
            """,
            
            3: f"""
Subject: Closing the Loop: {company_name} Opportunity

Hi [Hiring Manager],

This will be my final follow-up regarding the [Position] role. I've accepted that 
{company_name} may have found another candidate or decided to go in a different direction.

If circumstances change or if you have other roles that might benefit from someone who's 
built AI consciousness systems and saved enterprises $1.2M+, I'd welcome reconnecting.

Thank you for considering my application. I wish {company_name} continued success.

Best regards,
Matthew Scott
            """
        }
        
        return messages.get(follow_up_count, messages[3])

# Example usage and testing
if __name__ == "__main__":
    # Initialize the system
    cis = CareerIntelligenceSystem()
    
    # Example: Add a high-priority company
    test_company = {
        'name': 'Anthropic',
        'ai_maturity_score': 10,
        'innovation_score': 10,
        'hiring_urgency': 'high',
        'humana_competitor': False,
        'settlement_leverage': 8,
        'funding_amount': 750_000_000
    }
    
    # Calculate priority score
    priority = cis.calculate_company_priority_score(test_company)
    print(f"Priority score for {test_company['name']}: {priority}")
    
    # Generate subject lines
    subjects = cis.get_optimal_subject_lines(test_company)
    print(f"\nOptimal subject lines for {test_company['name']}:")
    for i, subject in enumerate(subjects, 1):
        print(f"{i}. {subject}")
    
    # Generate personalized opening
    opening = cis.generate_personalized_opening(test_company, 'innovation')
    print(f"\nPersonalized opening:\n{opening}")
    
    # Calculate optimal send time
    send_time = cis.calculate_optimal_send_time(test_company)
    print(f"\nOptimal send time: {send_time}")
    
    # Update metrics
    cis.update_daily_metrics()
    print("\nDaily metrics updated successfully")