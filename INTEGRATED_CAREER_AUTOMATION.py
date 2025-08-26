#!/usr/bin/env python3
"""
INTEGRATED CAREER AUTOMATION SYSTEM
Combines job scraping, Gmail tracking, ML-powered matching, and application automation
"""

import os
import json
import sqlite3
import pickle
import smtplib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Add paths for existing systems
sys.path.append('/Users/matthewscott/Projects/jaspermatters-job-intelligence')
sys.path.append('/Users/matthewscott/Google Gmail')
sys.path.append('/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer')

# Import existing components
from gmail_oauth_integration import GmailOAuthIntegration
from email_application_tracker import EmailApplicationTracker
from core.job_discovery import JobDiscovery
from core.application import ApplicationEngine  # Fixed import

# Import ML components from jaspermatters (if available)
try:
    from ml.embeddings.vector_engine import VectorSearchEngine
    from ml.models.salary_predictor import SalaryPredictor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML components not available - using basic matching")


class IntegratedCareerAutomation:
    """
    Master orchestrator for all career automation tasks:
    1. Job Discovery & Scraping
    2. ML-Powered Job Matching
    3. Automated Applications
    4. Gmail Response Tracking
    5. Analytics & Reporting
    """
    
    def __init__(self):
        """Initialize all components"""
        print("🚀 Initializing Integrated Career Automation System...")
        
        # Core components
        self.gmail_integration = GmailOAuthIntegration()
        self.email_tracker = EmailApplicationTracker()
        self.job_discovery = JobDiscovery()
        self.app_engine = ApplicationEngine()  # Fixed to use ApplicationEngine
        
        # ML components (if available)
        if ML_AVAILABLE:
            self.vector_engine = VectorSearchEngine()
            self.salary_predictor = SalaryPredictor()
        else:
            self.vector_engine = None
            self.salary_predictor = None
        
        # Configuration
        self.config = self._load_config()
        self.db_path = Path('/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/career_automation.db')
        self.resume_version = Path('/Users/matthewscott/Desktop/MATTHEW_SCOTT_AI_ML_ENGINEER_2025.pdf')
        
        # Initialize database
        self._init_database()
        
        # Gmail credentials
        self.gmail_app_password = os.getenv('GMAIL_APP_PASSWORD', '')
        self.gmail_address = 'matthewdscott7@gmail.com'
        
        print("✅ All systems initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration settings"""
        return {
            'target_roles': [
                'AI/ML Engineer',
                'Machine Learning Engineer', 
                'Senior ML Engineer',
                'AI Architect',
                'ML Platform Engineer',
                'Principal ML Engineer'
            ],
            'target_salary_min': 180000,
            'target_salary_max': 220000,
            'preferred_locations': ['Remote', 'Louisville, KY', 'San Francisco', 'New York'],
            'required_skills_match': 0.7,  # 70% skill match minimum
            'auto_apply_threshold': 0.85,  # 85% match for auto-application
            'daily_application_limit': 10,
            'response_check_interval_hours': 24
        }
    
    def _init_database(self):
        """Initialize SQLite database for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                company TEXT,
                role TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                location TEXT,
                source TEXT,
                match_score REAL,
                applied_date TEXT,
                email_sent TEXT,
                email_id TEXT,
                response_received TEXT DEFAULT 'pending',
                response_type TEXT,
                response_date TEXT,
                interview_scheduled TEXT,
                gmail_message_id TEXT,
                status TEXT DEFAULT 'active',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Job opportunities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                company TEXT,
                role TEXT,
                description TEXT,
                requirements TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                predicted_salary INTEGER,
                location TEXT,
                remote_ok BOOLEAN,
                source TEXT,
                url TEXT,
                match_score REAL,
                vector_similarity REAL,
                skills_extracted TEXT,
                discovered_date TEXT,
                expires_date TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Response analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS response_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_date TEXT,
                total_applications INTEGER,
                responses_received INTEGER,
                interviews_scheduled INTEGER,
                rejections INTEGER,
                response_rate REAL,
                avg_response_time_days REAL,
                top_responding_companies TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def discover_new_jobs(self, sources: List[str] = None) -> Dict:
        """
        Discover new job opportunities from multiple sources
        """
        print("\n🔍 Discovering New Job Opportunities...")
        
        if not sources:
            sources = ['greenhouse', 'lever', 'adzuna', 'linkedin', 'indeed']
        
        all_jobs = []
        
        for source in sources:
            print(f"  Scraping {source}...")
            try:
                if source == 'greenhouse':
                    jobs = self._scrape_greenhouse()
                elif source == 'lever':
                    jobs = self._scrape_lever()
                elif source == 'adzuna':
                    jobs = self.job_discovery.scrape_adzuna_jobs()
                else:
                    jobs = []
                
                all_jobs.extend(jobs)
                print(f"    ✓ Found {len(jobs)} jobs from {source}")
            except Exception as e:
                print(f"    ✗ Error scraping {source}: {e}")
        
        # Process and score jobs
        processed_jobs = self._process_and_score_jobs(all_jobs)
        
        # Save to database
        self._save_jobs_to_db(processed_jobs)
        
        return {
            'total_discovered': len(all_jobs),
            'qualified_jobs': len([j for j in processed_jobs if j['match_score'] >= self.config['required_skills_match']]),
            'auto_apply_candidates': len([j for j in processed_jobs if j['match_score'] >= self.config['auto_apply_threshold']]),
            'jobs': processed_jobs
        }
    
    def _process_and_score_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Process jobs with ML scoring and filtering
        """
        if ML_AVAILABLE and self.vector_engine:
            print("\n🤖 Processing jobs with ML models...")
        else:
            print("\n📊 Processing jobs with keyword matching...")
        
        processed = []
        my_profile = self._get_my_profile()
        
        for job in jobs:
            try:
                if ML_AVAILABLE and self.vector_engine:
                    # Create job embedding
                    job_text = f"{job.get('role', '')} {job.get('description', '')} {job.get('requirements', '')}"
                    job_embedding = self.vector_engine.create_job_embedding({'description': job_text})
                    
                    # Calculate similarity to my profile
                    similarity = self.vector_engine.calculate_similarity(job_embedding, my_profile['embedding'])
                    
                    # Predict salary if not provided
                    if not job.get('salary_min'):
                        predicted_salary = self.salary_predictor.predict_salary(job)
                        job['predicted_salary'] = predicted_salary
                else:
                    # Fallback to keyword matching
                    similarity = self._calculate_keyword_similarity(job, my_profile)
                    job['predicted_salary'] = 150000  # Default estimate
                
                # Calculate overall match score
                match_score = self._calculate_match_score(job, similarity)
                
                job['vector_similarity'] = float(similarity)
                job['match_score'] = float(match_score)
                
                processed.append(job)
                
            except Exception as e:
                print(f"    Error processing job {job.get('role')}: {e}")
        
        # Sort by match score
        processed.sort(key=lambda x: x['match_score'], reverse=True)
        
        return processed
    
    def _calculate_match_score(self, job: Dict, similarity: float) -> float:
        """
        Calculate comprehensive match score
        """
        score = 0.0
        weights = {
            'similarity': 0.4,
            'salary': 0.2,
            'location': 0.2,
            'role': 0.2
        }
        
        # Similarity score
        score += similarity * weights['similarity']
        
        # Salary score
        if job.get('salary_min'):
            if job['salary_min'] >= self.config['target_salary_min']:
                score += weights['salary']
            else:
                score += (job['salary_min'] / self.config['target_salary_min']) * weights['salary']
        else:
            score += 0.5 * weights['salary']  # Unknown salary gets half credit
        
        # Location score
        if any(loc in str(job.get('location', '')).lower() for loc in ['remote', 'anywhere']):
            score += weights['location']
        elif any(pref.lower() in str(job.get('location', '')).lower() 
                for pref in self.config['preferred_locations']):
            score += weights['location'] * 0.8
        else:
            score += weights['location'] * 0.3
        
        # Role match score
        role_lower = str(job.get('role', '')).lower()
        if any(target.lower() in role_lower for target in self.config['target_roles']):
            score += weights['role']
        elif 'ml' in role_lower or 'ai' in role_lower or 'machine learning' in role_lower:
            score += weights['role'] * 0.7
        
        return min(score, 1.0)
    
    def _calculate_keyword_similarity(self, job: Dict, profile: Dict) -> float:
        """
        Calculate similarity using keyword matching (fallback when ML not available)
        """
        job_text = f"{job.get('role', '')} {job.get('description', '')} {job.get('requirements', '')}".lower()
        
        # Key skills to match
        ml_keywords = ['machine learning', 'ml', 'ai', 'tensorflow', 'pytorch', 'neural', 
                       'deep learning', 'nlp', 'computer vision', 'data science']
        
        matches = sum(1 for keyword in ml_keywords if keyword in job_text)
        similarity = min(matches / len(ml_keywords), 1.0)
        
        # Boost for specific companies
        if any(company in str(job.get('company', '')).lower() 
               for company in ['anthropic', 'openai', 'google', 'meta', 'scale']):
            similarity = min(similarity + 0.2, 1.0)
        
        return similarity
    
    def auto_apply_to_jobs(self, limit: int = None) -> Dict:
        """
        Automatically apply to high-match jobs
        """
        if limit is None:
            limit = self.config['daily_application_limit']
        
        print(f"\n📮 Auto-Applying to Top {limit} Jobs...")
        
        # Get top unapplie jobs
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM jobs 
            WHERE status = 'new' 
            AND match_score >= ?
            ORDER BY match_score DESC
            LIMIT ?
        ''', (self.config['auto_apply_threshold'], limit))
        
        jobs = cursor.fetchall()
        conn.close()
        
        results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'applications': []
        }
        
        for job in jobs:
            job_dict = self._row_to_dict(job)
            
            print(f"\n  Applying to {job_dict['company']} - {job_dict['role']}")
            print(f"    Match Score: {job_dict['match_score']:.2%}")
            
            try:
                # Generate tailored cover letter
                cover_letter = self._generate_cover_letter(job_dict)
                
                # Send application email
                email_result = self._send_application_email(job_dict, cover_letter)
                
                if email_result['success']:
                    # Update database
                    self._update_application_status(job_dict['job_id'], 'applied', email_result['email_id'])
                    results['successful'] += 1
                    results['applications'].append({
                        'company': job_dict['company'],
                        'role': job_dict['role'],
                        'email_id': email_result['email_id']
                    })
                    print(f"    ✅ Application sent successfully!")
                else:
                    results['failed'] += 1
                    print(f"    ❌ Failed to send: {email_result.get('error')}")
                
            except Exception as e:
                results['failed'] += 1
                print(f"    ❌ Error: {e}")
            
            results['attempted'] += 1
            
            # Rate limiting
            time.sleep(30)  # 30 seconds between applications
        
        return results
    
    def check_gmail_responses(self) -> Dict:
        """
        Check Gmail for responses and update tracking
        """
        print("\n📧 Checking Gmail for Responses...")
        
        # Sync with Gmail OAuth
        processed_ids = self.gmail_integration.sync_gmail_responses()
        
        # Get recent emails
        recent_emails = self._check_recent_emails()
        
        # Update application statuses
        updates = self._process_email_responses(recent_emails)
        
        # Generate analytics
        analytics = self._generate_response_analytics()
        
        return {
            'emails_processed': len(processed_ids),
            'responses_found': updates['responses'],
            'interviews_scheduled': updates['interviews'],
            'rejections': updates['rejections'],
            'analytics': analytics
        }
    
    def _check_recent_emails(self) -> List[Dict]:
        """
        Check recent emails for job responses
        """
        import imaplib
        import email
        from email.header import decode_header
        
        try:
            # Connect to Gmail
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.gmail_address, self.gmail_app_password)
            mail.select("inbox")
            
            # Search for recent emails (last 7 days)
            date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'(SINCE "{date}")')
            
            email_data = []
            
            for num in messages[0].split():
                status, data = mail.fetch(num, "(RFC822)")
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Extract email details
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                from_email = msg["From"]
                date_received = msg["Date"]
                
                # Get body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                
                email_data.append({
                    'subject': subject,
                    'from': from_email,
                    'date': date_received,
                    'body': body[:500],  # First 500 chars
                    'message_id': msg["Message-ID"]
                })
            
            mail.close()
            mail.logout()
            
            return email_data
            
        except Exception as e:
            print(f"    Error checking emails: {e}")
            return []
    
    def _process_email_responses(self, emails: List[Dict]) -> Dict:
        """
        Process emails to identify job responses
        """
        updates = {
            'responses': 0,
            'interviews': 0,
            'rejections': 0
        }
        
        # Keywords for classification
        interview_keywords = ['interview', 'call', 'meet', 'schedule', 'chat', 'discussion']
        rejection_keywords = ['unfortunately', 'not moving forward', 'other candidates', 
                            'not a fit', 'decided to', 'position has been filled']
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for email_data in emails:
            # Check if this is a job response
            cursor.execute('''
                SELECT company, job_id FROM applications 
                WHERE response_received = 'pending'
            ''')
            
            pending_apps = cursor.fetchall()
            
            for company, job_id in pending_apps:
                if company.lower() in email_data['from'].lower() or \
                   company.lower() in email_data['subject'].lower():
                    
                    # Classify response
                    text = (email_data['subject'] + ' ' + email_data['body']).lower()
                    
                    if any(kw in text for kw in interview_keywords):
                        response_type = 'interview_request'
                        updates['interviews'] += 1
                    elif any(kw in text for kw in rejection_keywords):
                        response_type = 'rejection'
                        updates['rejections'] += 1
                    else:
                        response_type = 'response'
                        updates['responses'] += 1
                    
                    # Update database
                    cursor.execute('''
                        UPDATE applications 
                        SET response_received = 'yes',
                            response_type = ?,
                            response_date = ?,
                            gmail_message_id = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE job_id = ?
                    ''', (response_type, datetime.now().strftime('%Y-%m-%d'), 
                         email_data['message_id'], job_id))
                    
                    print(f"    ✓ {company}: {response_type}")
        
        conn.commit()
        conn.close()
        
        return updates
    
    def generate_dashboard_report(self) -> Dict:
        """
        Generate comprehensive dashboard report
        """
        print("\n📊 Generating Dashboard Report...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_applications,
                COUNT(CASE WHEN response_received = 'yes' THEN 1 END) as responses,
                COUNT(CASE WHEN response_type = 'interview_request' THEN 1 END) as interviews,
                COUNT(CASE WHEN response_type = 'rejection' THEN 1 END) as rejections
            FROM applications
            WHERE applied_date >= date('now', '-30 days')
        ''')
        
        stats = cursor.fetchone()
        
        # Response rate
        response_rate = (stats[1] / stats[0] * 100) if stats[0] > 0 else 0
        
        # Top performing companies
        cursor.execute('''
            SELECT company, response_type, COUNT(*) as count
            FROM applications
            WHERE response_received = 'yes'
            GROUP BY company, response_type
            ORDER BY count DESC
            LIMIT 10
        ''')
        
        top_companies = cursor.fetchall()
        
        # Job pipeline
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN status = 'new' THEN 1 END) as new_jobs,
                COUNT(CASE WHEN match_score >= 0.85 THEN 1 END) as high_match,
                COUNT(CASE WHEN match_score >= 0.7 THEN 1 END) as qualified
            FROM jobs
        ''')
        
        pipeline = cursor.fetchone()
        
        conn.close()
        
        report = {
            'summary': {
                'total_applications_30d': stats[0],
                'responses_received': stats[1],
                'interviews_scheduled': stats[2],
                'rejections': stats[3],
                'response_rate': f"{response_rate:.1f}%"
            },
            'pipeline': {
                'new_opportunities': pipeline[0],
                'high_match_jobs': pipeline[1],
                'qualified_jobs': pipeline[2]
            },
            'top_responding_companies': top_companies,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save report
        report_path = Path('/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/dashboard_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report saved to {report_path}")
        
        return report
    
    def run_daily_automation(self):
        """
        Run complete daily automation cycle
        """
        print("\n" + "="*60)
        print("🤖 RUNNING DAILY CAREER AUTOMATION")
        print("="*60)
        
        # Step 1: Discover new jobs
        discovery_results = self.discover_new_jobs()
        print(f"\n✅ Discovered {discovery_results['total_discovered']} new jobs")
        print(f"   - Qualified: {discovery_results['qualified_jobs']}")
        print(f"   - Auto-apply candidates: {discovery_results['auto_apply_candidates']}")
        
        # Step 2: Auto-apply to top matches
        if discovery_results['auto_apply_candidates'] > 0:
            apply_results = self.auto_apply_to_jobs()
            print(f"\n✅ Applied to {apply_results['successful']} jobs")
        
        # Step 3: Check for responses
        response_results = self.check_gmail_responses()
        print(f"\n✅ Found {response_results['responses_found']} new responses")
        print(f"   - Interviews: {response_results['interviews_scheduled']}")
        print(f"   - Rejections: {response_results['rejections']}")
        
        # Step 4: Generate report
        report = self.generate_dashboard_report()
        
        print("\n" + "="*60)
        print("📈 DAILY SUMMARY")
        print("="*60)
        print(f"Applications (30d): {report['summary']['total_applications_30d']}")
        print(f"Response Rate: {report['summary']['response_rate']}")
        print(f"Interview Pipeline: {report['summary']['interviews_scheduled']}")
        print(f"New Opportunities: {report['pipeline']['new_opportunities']}")
        
        return report
    
    def _get_my_profile(self) -> Dict:
        """Get my profile for matching"""
        profile = {
            'skills': [
                'Python', 'TensorFlow', 'PyTorch', 'scikit-learn',
                'LangChain', 'Docker', 'Kubernetes', 'AWS', 'MLOps',
                'Neural Networks', 'NLP', 'Computer Vision', 'RAG',
                'FastAPI', 'PostgreSQL', 'Redis'
            ],
            'experience_years': 10,
            'current_role': 'AI/ML Engineer',
            'desired_roles': self.config['target_roles']
        }
        
        # Add embedding if ML is available
        if ML_AVAILABLE and self.vector_engine:
            profile['embedding'] = self.vector_engine.create_job_embedding({
                'description': """
                AI/ML Engineer with proven ability to architect production systems including 
                79+ model orchestration platform achieving 99.3% success rate. 
                Built 6 major AI systems generating $1.2M+ value through automation. 
                Expertise in TensorFlow, PyTorch, LLMs, MLOps, and scalable AI architecture.
                """
            })
        else:
            profile['embedding'] = None
        
        return profile
    
    def _generate_cover_letter(self, job: Dict) -> str:
        """Generate tailored cover letter"""
        template = f"""Dear Hiring Team at {job['company']},

I am writing to express my strong interest in the {job['role']} position at {job['company']}. 
With my experience building production ML systems including a Job Intelligence Platform achieving 
92% accuracy and a 79+ model orchestration platform, I am excited about the opportunity to 
contribute to your team.

My recent work includes:
• Architected end-to-end ML platform with TensorFlow neural networks (134 features)
• Built multi-agent AI orchestration managing 79+ specialized models with 99.3% success rate
• Generated $1.2M+ value through AI automation and optimization
• Developed semantic search systems using Sentence-BERT with production deployment

I am particularly drawn to {job['company']} because of your innovative work in the AI/ML space. 
My experience aligns well with your requirements, and I am confident I can make significant 
contributions to your team.

I have attached my resume for your review and would welcome the opportunity to discuss how 
my skills and experience can benefit {job['company']}.

Best regards,
Matthew Scott
Portfolio: jaspermatters.com
GitHub: github.com/guitargnar
"""
        return template
    
    def _send_application_email(self, job: Dict, cover_letter: str) -> Dict:
        """Send application email with resume"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = job.get('email', f"careers@{job['company'].lower().replace(' ', '')}.com")
            msg['Subject'] = f"Application for {job['role']} - Matthew Scott"
            
            # Add cover letter
            msg.attach(MIMEText(cover_letter, 'plain'))
            
            # Attach resume
            if self.resume_path.exists():
                with open(self.resume_version, 'rb') as f:
                    attach = MIMEApplication(f.read(), _subtype="pdf")
                    attach.add_header('Content-Disposition', 'attachment', 
                                    filename='Matthew_Scott_AI_ML_Engineer_Resume.pdf')
                    msg.attach(attach)
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.gmail_address, self.gmail_app_password)
            
            text = msg.as_string()
            server.sendmail(self.gmail_address, msg['To'], text)
            server.quit()
            
            # Generate email ID
            email_id = f"auto_{job['job_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return {'success': True, 'email_id': email_id}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _update_application_status(self, job_id: str, status: str, email_id: str = None):
        """Update application status in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update job opportunity status
        cursor.execute('''
            UPDATE jobs 
            SET status = ? 
            WHERE job_id = ?
        ''', (status, job_id))
        
        # Get job details
        cursor.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
        job = cursor.fetchone()
        
        if job:
            # Insert into applications table
            cursor.execute('''
                INSERT INTO applications (
                    job_id, company, position, salary_min, salary_max, 
                    location, source, match_score, applied_date, 
                    status, email_id, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id, job[2], job[3], job[6], job[7], job[9],
                job[11], job[13], datetime.now().strftime('%Y-%m-%d'),
                'yes', email_id, 'active'
            ))
        
        conn.commit()
        conn.close()
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary"""
        columns = [
            'id', 'job_id', 'company', 'role', 'description', 'requirements',
            'salary_min', 'salary_max', 'predicted_salary', 'location',
            'remote_ok', 'source', 'url', 'match_score', 'vector_similarity',
            'skills_extracted', 'discovered_date', 'expires_date', 'status', 'created_at'
        ]
        return dict(zip(columns, row))
    
    def _scrape_greenhouse(self) -> List[Dict]:
        """Scrape Greenhouse boards"""
        # Implementation would go here
        return []
    
    def _scrape_lever(self) -> List[Dict]:
        """Scrape Lever boards"""
        # Implementation would go here
        return []
    
    def _save_jobs_to_db(self, jobs: List[Dict]):
        """Save jobs to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for job in jobs:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO job_opportunities (
                        job_id, company, position, description, requirements,
                        salary_min, salary_max, predicted_salary, location,
                        remote_ok, source, url, match_score, vector_similarity,
                        skills_extracted, discovered_date, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job.get('job_id', f"{job['company']}_{job['role']}_{datetime.now().timestamp()}"),
                    job.get('company'),
                    job.get('role'),
                    job.get('description', ''),
                    job.get('requirements', ''),
                    job.get('salary_min'),
                    job.get('salary_max'),
                    job.get('predicted_salary'),
                    job.get('location'),
                    job.get('remote_ok', False),
                    job.get('source'),
                    job.get('url'),
                    job.get('match_score', 0),
                    job.get('vector_similarity', 0),
                    json.dumps(job.get('skills_extracted', [])),
                    datetime.now().strftime('%Y-%m-%d'),
                    'new'
                ))
            except Exception as e:
                print(f"Error saving job {job.get('role')}: {e}")
        
        conn.commit()
        conn.close()
    
    def _generate_response_analytics(self) -> Dict:
        """Generate response analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                AVG(JULIANDAY(response_date) - JULIANDAY(applied_date)) as avg_response_time,
                COUNT(*) as total_responses
            FROM applications
            WHERE response_received = 'yes'
            AND response_date IS NOT NULL
            AND applied_date IS NOT NULL
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'avg_response_time_days': result[0] if result[0] else 0,
            'total_responses': result[1] if result[1] else 0
        }


def main():
    """Main execution"""
    automation = IntegratedCareerAutomation()
    
    # Run daily automation
    report = automation.run_daily_automation()
    
    print("\n✅ Career automation complete!")
    print(f"   Report saved to dashboard_report.json")


if __name__ == "__main__":
    main()