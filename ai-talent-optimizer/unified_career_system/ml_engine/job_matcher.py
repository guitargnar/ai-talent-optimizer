#!/usr/bin/env python3
"""
Intelligent Job Matcher for Unified Career System
Uses ensemble ML to find and rank the best job opportunities
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import logging

# Add parent path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from unified_career_system.ml_engine.model_ensemble import UnifiedMLEngine
from unified_career_system.ml_engine.vector_store import UnifiedVectorStore
from unified_career_system.data_layer.master_database import MasterDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentJobMatcher:
    """
    Intelligent job matching system that combines:
    - ML scoring from ensemble
    - Semantic search from vector store
    - Historical performance data
    - User preferences and constraints
    """
    
    def __init__(self, db_path: str = "unified_career_system/data_layer/unified_career.db"):
        """Initialize the job matcher with all ML components"""
        self.db_path = db_path
        self.master_db = MasterDatabase(db_path)
        self.ml_engine = UnifiedMLEngine()
        self.vector_store = UnifiedVectorStore()
        
        # Load user profile
        self.user_profile = self._load_user_profile()
        
        # Update vector store from database
        self.vector_store.update_from_database(db_path)
        
        # Performance tracking
        self.performance_cache = {}
        self._load_performance_data()
        
        logger.info("Initialized IntelligentJobMatcher")
        
    def _load_user_profile(self) -> Dict:
        """Load or create user profile for matching"""
        # In production, this would load from user settings
        return {
            'skills': 'Python, TensorFlow, PyTorch, Machine Learning, Deep Learning, '
                     'SQL, Docker, Kubernetes, AWS, Production ML, Neural Networks, '
                     'Computer Vision, NLP, MLOps',
            'experience': '10+ years in ML/AI engineering, built production models at scale, '
                         'led ML teams, developed ML platforms',
            'target_salary': 180000,
            'min_salary': 150000,
            'prefers_remote': True,
            'preferred_company_size': 'startup',
            'preferred_industries': ['ai', 'tech', 'healthcare', 'fintech'],
            'desired_roles': ['ML Engineer', 'Senior ML Engineer', 'Principal ML Engineer',
                            'Staff ML Engineer', 'AI Engineer', 'Machine Learning Scientist'],
            'avoid_companies': [],  # Companies to exclude
            'location_preferences': ['Remote', 'San Francisco', 'New York', 'Seattle'],
            'resume_text': self._load_resume_text()
        }
        
    def _load_resume_text(self) -> str:
        """Load resume text for ATS scoring"""
        # Try to load from file
        resume_path = Path("/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/resumes/current_resume.txt")
        if resume_path.exists():
            with open(resume_path, 'r') as f:
                return f.read()
        
        # Fallback resume text
        return """
        Matthew Scott - Senior Machine Learning Engineer
        10+ years experience building production ML systems
        
        Skills: Python, TensorFlow, PyTorch, Machine Learning, Deep Learning,
        Computer Vision, NLP, SQL, Docker, Kubernetes, AWS, GCP
        
        Experience:
        - Built ML platform processing 1M+ predictions daily
        - Developed 79+ specialized ML models for healthcare
        - Achieved $1.2M annual savings through ML optimization
        - Led team of 5 ML engineers
        """
        
    def _load_performance_data(self):
        """Load historical performance data for learning"""
        cursor = self.master_db.conn.cursor()
        
        # Load response rates by company
        cursor.execute("""
        SELECT c.company_name, 
               COUNT(a.id) as applications,
               SUM(CASE WHEN a.response_received = 1 THEN 1 ELSE 0 END) as responses,
               AVG(a.days_to_response) as avg_response_time
        FROM company_intelligence c
        LEFT JOIN master_applications a ON c.company_name = 
            (SELECT company FROM master_jobs WHERE job_uid = a.job_uid)
        GROUP BY c.company_name
        """)
        
        for row in cursor.fetchall():
            company = row[0]
            if company and row[1] > 0:
                self.performance_cache[company] = {
                    'applications': row[1],
                    'responses': row[2] or 0,
                    'response_rate': (row[2] or 0) / row[1] if row[1] else 0,
                    'avg_response_time': row[3]
                }
                
    def find_best_matches(self, limit: int = 20, 
                         min_score: float = 0.5) -> List[Dict]:
        """
        Find the best job matches using all available signals
        
        Args:
            limit: Maximum number of matches to return
            min_score: Minimum score threshold
            
        Returns:
            List of matched jobs with scores and explanations
        """
        logger.info(f"Finding best job matches (limit={limit}, min_score={min_score})")
        
        # Step 1: Get active jobs from database
        cursor = self.master_db.conn.cursor()
        cursor.execute("""
        SELECT job_uid, company, position, location, remote_type,
               salary_min, salary_max, description, requirements,
               url, source, discovered_date, department, level
        FROM master_jobs
        WHERE is_active = 1 AND applied = 0
        ORDER BY discovered_date DESC
        LIMIT 500
        """)
        
        jobs = []
        for row in cursor.fetchall():
            job = {
                'job_uid': row[0],
                'company': row[1],
                'position': row[2],
                'title': row[2],  # Alias for compatibility
                'location': row[3],
                'remote_type': row[4],
                'remote': 'remote' in str(row[4]).lower() if row[4] else False,
                'salary_min': row[5],
                'salary_max': row[6],
                'description': row[7],
                'requirements': row[8],
                'url': row[9],
                'source': row[10],
                'discovered_date': row[11],
                'department': row[12],
                'level': row[13]
            }
            
            # Skip if in avoid list
            if job['company'] in self.user_profile.get('avoid_companies', []):
                continue
                
            jobs.append(job)
            
        if not jobs:
            logger.warning("No active jobs found")
            return []
            
        # Step 2: Score all jobs using ML ensemble
        scored_jobs = self.ml_engine.batch_score_jobs(jobs, self.user_profile)
        
        # Step 3: Enhance with additional signals
        enhanced_jobs = []
        for job in scored_jobs:
            if job['ml_analysis']['overall_score'] < min_score:
                continue
                
            # Add semantic search score
            semantic_results = self.vector_store.search_similar_jobs(
                self.user_profile['skills'] + ' ' + ' '.join(self.user_profile['desired_roles']),
                top_k=100,
                min_similarity=0.3
            )
            
            semantic_score = 0.5  # Default
            for uid, score, _ in semantic_results:
                if uid == job['job_uid']:
                    semantic_score = score
                    break
                    
            # Add historical performance score
            company_perf = self.performance_cache.get(job['company'], {})
            performance_score = company_perf.get('response_rate', 0.1)
            
            # Add recency score (newer jobs are better)
            try:
                days_old = (datetime.now() - datetime.fromisoformat(job['discovered_date'])).days
                recency_score = max(0, 1 - (days_old / 30))  # Linear decay over 30 days
            except:
                recency_score = 0.5
                
            # Calculate final composite score
            composite_score = (
                job['ml_analysis']['overall_score'] * 0.5 +
                semantic_score * 0.2 +
                performance_score * 0.15 +
                recency_score * 0.15
            )
            
            # Create enhanced job entry
            enhanced_job = {
                **job,
                'match_score': composite_score,
                'ml_score': job['ml_analysis']['overall_score'],
                'semantic_score': semantic_score,
                'performance_score': performance_score,
                'recency_score': recency_score,
                'recommendation': job['ml_analysis']['recommendation'],
                'priority': job['ml_analysis']['priority'],
                'components': job['ml_analysis']['components'],
                'match_reasons': self._generate_match_reasons(job, job['ml_analysis'])
            }
            
            enhanced_jobs.append(enhanced_job)
            
        # Step 4: Sort by composite score
        enhanced_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Step 5: Apply diversity (don't return too many from same company)
        diversified_jobs = self._apply_diversity(enhanced_jobs, limit)
        
        logger.info(f"Found {len(diversified_jobs)} matches with scores >= {min_score}")
        
        return diversified_jobs
        
    def _generate_match_reasons(self, job: Dict, ml_analysis: Dict) -> List[str]:
        """Generate human-readable match reasons"""
        reasons = []
        
        # Check component scores
        components = ml_analysis.get('components', {})
        
        # Salary match
        if 'salary' in components and components['salary'].get('score', 0) > 0.7:
            reasons.append("Excellent salary match")
        elif 'salary' in components and components['salary'].get('score', 0) > 0.5:
            reasons.append("Good salary range")
            
        # Semantic match
        if 'semantic' in components and components['semantic'].get('score', 0) > 0.6:
            reasons.append("Strong skills alignment")
        elif 'semantic' in components and components['semantic'].get('score', 0) > 0.4:
            reasons.append("Good skills match")
            
        # ATS score
        if 'ats' in components and components['ats'].get('score', 0) > 0.85:
            reasons.append("Excellent ATS compatibility")
        elif 'ats' in components and components['ats'].get('score', 0) > 0.7:
            reasons.append("Good ATS score potential")
            
        # Intelligence factors
        if 'intelligence' in components:
            factors = components['intelligence'].get('factors', [])
            if 'remote_match' in factors:
                reasons.append("Remote position available")
            if 'industry_match' in factors:
                reasons.append("Preferred industry")
            if 'recently_posted' in factors:
                reasons.append("Recently posted")
                
        # Company size
        if job.get('company_size') == self.user_profile.get('preferred_company_size'):
            reasons.append(f"Preferred company size ({job['company_size']})")
            
        return reasons
        
    def _apply_diversity(self, jobs: List[Dict], limit: int) -> List[Dict]:
        """Apply diversity to avoid too many jobs from same company"""
        company_counts = {}
        diversified = []
        
        for job in jobs:
            company = job['company']
            
            # Allow max 3 jobs per company
            if company_counts.get(company, 0) >= 3:
                continue
                
            diversified.append(job)
            company_counts[company] = company_counts.get(company, 0) + 1
            
            if len(diversified) >= limit:
                break
                
        return diversified
        
    def get_application_strategy(self, job: Dict) -> Dict:
        """
        Get personalized application strategy for a specific job
        
        Args:
            job: Job dictionary with match scores
            
        Returns:
            Strategy dictionary with timing, approach, and talking points
        """
        strategy = {
            'priority': job.get('priority', 3),
            'timing': {},
            'approach': {},
            'talking_points': [],
            'keywords_to_emphasize': [],
            'avoid_mentioning': []
        }
        
        # Timing recommendations
        match_score = job.get('match_score', 0.5)
        if match_score > 0.8:
            strategy['timing'] = {
                'urgency': 'HIGH',
                'apply_within': '24 hours',
                'best_time': 'Tuesday morning or Thursday morning',
                'follow_up': '3 days after application'
            }
        elif match_score > 0.6:
            strategy['timing'] = {
                'urgency': 'MEDIUM',
                'apply_within': '2-3 days',
                'best_time': 'Weekday morning',
                'follow_up': '5 days after application'
            }
        else:
            strategy['timing'] = {
                'urgency': 'LOW',
                'apply_within': '1 week',
                'best_time': 'Any weekday',
                'follow_up': '1 week after application'
            }
            
        # Approach recommendations
        components = job.get('components', {})
        
        # Check ATS score
        ats_score = components.get('ats', {}).get('score', 0.5)
        if ats_score < 0.7:
            strategy['approach']['resume'] = 'Customize heavily with job keywords'
            strategy['keywords_to_emphasize'] = self._extract_missing_keywords(job)
        else:
            strategy['approach']['resume'] = 'Current resume is well-matched'
            
        # Cover letter approach
        if job.get('company_size') == 'startup':
            strategy['approach']['cover_letter'] = 'Emphasize entrepreneurial spirit and impact'
            strategy['talking_points'].append('Experience building from scratch')
            strategy['talking_points'].append('Comfortable with ambiguity')
        elif job.get('company_size') == 'enterprise':
            strategy['approach']['cover_letter'] = 'Emphasize scale and process'
            strategy['talking_points'].append('Experience with large-scale systems')
            strategy['talking_points'].append('Process and documentation skills')
            
        # Industry-specific points
        if 'healthcare' in str(job.get('company', '')).lower():
            strategy['talking_points'].append('Healthcare ML experience at Humana')
            strategy['talking_points'].append('Understanding of HIPAA and compliance')
        elif 'ai' in str(job.get('company', '')).lower():
            strategy['talking_points'].append('Mirador platform with 79+ models')
            strategy['talking_points'].append('Production ML at scale')
            
        # What to avoid
        if job.get('company') != 'Humana':
            strategy['avoid_mentioning'].append('Specific Humana internal processes')
        strategy['avoid_mentioning'].append('Negative experiences')
        strategy['avoid_mentioning'].append('Salary expectations in cover letter')
        
        return strategy
        
    def _extract_missing_keywords(self, job: Dict) -> List[str]:
        """Extract keywords missing from resume but present in job"""
        job_text = f"{job.get('description', '')} {job.get('requirements', '')}"
        
        # Common important keywords to check
        important_keywords = [
            'python', 'tensorflow', 'pytorch', 'kubernetes', 'docker',
            'aws', 'gcp', 'azure', 'sql', 'nosql', 'kafka', 'spark',
            'airflow', 'mlflow', 'scikit-learn', 'pandas', 'numpy',
            'rest', 'api', 'microservices', 'ci/cd', 'git'
        ]
        
        missing = []
        job_lower = job_text.lower()
        resume_lower = self.user_profile['resume_text'].lower()
        
        for keyword in important_keywords:
            if keyword in job_lower and keyword not in resume_lower:
                missing.append(keyword)
                
        return missing[:5]  # Top 5 missing keywords
        
    def track_application_outcome(self, job_uid: str, outcome: str):
        """
        Track the outcome of an application for learning
        
        Args:
            job_uid: Job unique identifier
            outcome: 'applied', 'responded', 'interview', 'offer', 'rejected'
        """
        cursor = self.master_db.conn.cursor()
        
        # Update application status
        cursor.execute("""
        UPDATE master_applications
        SET outcome = ?, last_updated = CURRENT_TIMESTAMP
        WHERE job_uid = ?
        """, (outcome, job_uid))
        
        # Update company intelligence if responded
        if outcome in ['responded', 'interview', 'offer']:
            cursor.execute("""
            UPDATE company_intelligence
            SET total_responses = total_responses + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE company_name = (
                SELECT company FROM master_jobs WHERE job_uid = ?
            )
            """, (job_uid,))
            
        self.master_db.conn.commit()
        
        # Reload performance cache
        self._load_performance_data()
        
    def get_daily_recommendations(self, target_count: int = 25) -> Dict:
        """
        Get daily job application recommendations
        
        Args:
            target_count: Target number of applications per day
            
        Returns:
            Dictionary with categorized recommendations
        """
        # Get best matches
        all_matches = self.find_best_matches(limit=target_count * 2)
        
        # Categorize by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for job in all_matches:
            if job['priority'] == 1:
                high_priority.append(job)
            elif job['priority'] == 2:
                medium_priority.append(job)
            else:
                low_priority.append(job)
                
        # Build recommendation plan
        recommendations = {
            'date': datetime.now().isoformat(),
            'target_count': target_count,
            'high_priority': high_priority[:10],
            'medium_priority': medium_priority[:10],
            'low_priority': low_priority[:5],
            'total_available': len(all_matches),
            'strategy': {
                'morning_batch': high_priority[:8],
                'afternoon_batch': medium_priority[:8],
                'evening_batch': low_priority[:9] if target_count >= 25 else []
            }
        }
        
        return recommendations


def main():
    """Test the intelligent job matcher"""
    matcher = IntelligentJobMatcher()
    
    print("🎯 Intelligent Job Matcher")
    print("=" * 60)
    
    # Get best matches
    print("\n🔍 Finding Best Job Matches...")
    matches = matcher.find_best_matches(limit=5, min_score=0.4)
    
    if matches:
        print(f"\n📊 Top {len(matches)} Matches:")
        print("=" * 60)
        
        for i, job in enumerate(matches, 1):
            print(f"\n{i}. {job['position']} at {job['company']}")
            print(f"   📍 Location: {job['location']} ({job.get('remote_type', 'Not specified')})")
            print(f"   💰 Salary: ${job.get('salary_min', 0):,}-${job.get('salary_max', 0):,}" 
                  if job.get('salary_min') else "   💰 Salary: Not specified")
            print(f"   🎯 Match Score: {job['match_score']:.1%}")
            print(f"   📈 Components:")
            print(f"      - ML Score: {job['ml_score']:.1%}")
            print(f"      - Semantic: {job['semantic_score']:.1%}")
            print(f"      - Performance: {job['performance_score']:.1%}")
            print(f"      - Recency: {job['recency_score']:.1%}")
            print(f"   ✨ Match Reasons:")
            for reason in job['match_reasons']:
                print(f"      • {reason}")
                
            # Get application strategy
            strategy = matcher.get_application_strategy(job)
            print(f"   📋 Application Strategy:")
            print(f"      Priority: Level {strategy['priority']}")
            print(f"      Urgency: {strategy['timing']['urgency']}")
            print(f"      Apply within: {strategy['timing']['apply_within']}")
            
    else:
        print("No matches found. Consider adjusting criteria.")
        
    # Get daily recommendations
    print("\n📅 Daily Application Plan")
    print("=" * 60)
    
    daily = matcher.get_daily_recommendations(target_count=25)
    print(f"Target: {daily['target_count']} applications")
    print(f"Available: {daily['total_available']} qualified matches")
    print(f"\nRecommended Schedule:")
    print(f"  Morning (9-11am): {len(daily['strategy']['morning_batch'])} high-priority")
    print(f"  Afternoon (2-4pm): {len(daily['strategy']['afternoon_batch'])} medium-priority")
    if daily['strategy']['evening_batch']:
        print(f"  Evening (6-8pm): {len(daily['strategy']['evening_batch'])} additional")
        
    print("\n✨ Intelligent job matching ready for production!")


if __name__ == "__main__":
    main()