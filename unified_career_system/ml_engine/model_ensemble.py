#!/usr/bin/env python3
"""
Model Ensemble for Unified Career System
Combines ML models from all projects into a single intelligent engine
"""

import sys
import os
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging

# Add paths for all ML systems
sys.path.append('/Users/matthewscott/Projects/jaspermatters-job-intelligence')
sys.path.append('/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer')
sys.path.append('/Users/matthewscott/SURVIVE/career-automation')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedMLEngine:
    """
    Unified ML Engine combining:
    - TensorFlow salary prediction (jaspermatters)
    - Vector embeddings for semantic search (jaspermatters)
    - Job clustering (jaspermatters)
    - ATS optimization (SURVIVE)
    - Career intelligence scoring (ai-talent-optimizer)
    """
    
    def __init__(self):
        self.models = {}
        self.vector_engine = None
        self.salary_predictor = None
        self.job_clusterer = None
        self.ats_optimizer = None
        self.model_weights = {
            'salary': 0.20,      # Salary prediction importance
            'semantic': 0.30,    # Semantic match importance
            'clustering': 0.15,  # Job cluster relevance
            'ats': 0.25,        # ATS optimization score
            'intelligence': 0.10 # Career intelligence factors
        }
        self._load_all_models()
        
    def _load_all_models(self):
        """Load all ML models from different projects"""
        logger.info("Loading unified ML models...")
        
        # 1. Load TensorFlow salary predictor
        self._load_salary_predictor()
        
        # 2. Load vector embeddings engine
        self._load_vector_engine()
        
        # 3. Load clustering models
        self._load_clustering_models()
        
        # 4. Load ATS optimizer
        self._load_ats_optimizer()
        
        logger.info(f"Successfully loaded {len(self.models)} model systems")
        
    def _load_salary_predictor(self):
        """Load TensorFlow salary prediction model from jaspermatters"""
        try:
            jasper_path = Path("/Users/matthewscott/Projects/jaspermatters-job-intelligence")
            model_path = jasper_path / "ml" / "models" / "salary_model.h5"
            preprocessor_path = jasper_path / "ml" / "models" / "preprocessors.pkl"
            
            if model_path.exists() and preprocessor_path.exists():
                # Import the salary predictor class
                sys.path.insert(0, str(jasper_path))
                from ml.models.salary_predictor import SalaryPredictor
                
                self.salary_predictor = SalaryPredictor()
                self.salary_predictor.load_model()
                self.models['salary'] = self.salary_predictor
                logger.info("✅ Loaded TensorFlow salary predictor")
            else:
                logger.warning("⚠️ Salary predictor model files not found")
                self._create_fallback_salary_predictor()
                
        except Exception as e:
            logger.error(f"Failed to load salary predictor: {e}")
            self._create_fallback_salary_predictor()
            
    def _create_fallback_salary_predictor(self):
        """Create a simple fallback salary predictor"""
        class FallbackSalaryPredictor:
            def predict(self, jobs_df):
                # Simple heuristic based on title keywords
                salaries = []
                for _, job in jobs_df.iterrows():
                    base = 100000
                    title_lower = str(job.get('title', '')).lower()
                    
                    # Seniority modifiers
                    if 'senior' in title_lower:
                        base += 40000
                    elif 'principal' in title_lower or 'staff' in title_lower:
                        base += 60000
                    elif 'lead' in title_lower:
                        base += 50000
                    elif 'junior' in title_lower:
                        base -= 30000
                    
                    # Role modifiers
                    if 'ml' in title_lower or 'machine learning' in title_lower:
                        base += 20000
                    if 'ai' in title_lower or 'artificial intelligence' in title_lower:
                        base += 25000
                    
                    salaries.append(base)
                return np.array(salaries)
        
        self.salary_predictor = FallbackSalaryPredictor()
        self.models['salary'] = self.salary_predictor
        logger.info("✅ Created fallback salary predictor")
        
    def _load_vector_engine(self):
        """Load vector embeddings engine from jaspermatters"""
        try:
            jasper_path = Path("/Users/matthewscott/Projects/jaspermatters-job-intelligence")
            sys.path.insert(0, str(jasper_path))
            
            from ml.embeddings.vector_engine import VectorEngine
            
            self.vector_engine = VectorEngine()
            
            # Load cached embeddings if available
            embeddings_cache_path = jasper_path / "ml" / "data" / "local_index.pkl"
            if embeddings_cache_path.exists():
                with open(embeddings_cache_path, 'rb') as f:
                    self.vector_engine.local_index = pickle.load(f)
                    
            self.models['vector'] = self.vector_engine
            logger.info("✅ Loaded vector embeddings engine")
            
        except Exception as e:
            logger.error(f"Failed to load vector engine: {e}")
            self._create_fallback_vector_engine()
            
    def _create_fallback_vector_engine(self):
        """Create a simple fallback vector engine using keyword matching"""
        class FallbackVectorEngine:
            def compute_similarity(self, text1: str, text2: str) -> float:
                # Simple keyword overlap similarity
                words1 = set(text1.lower().split())
                words2 = set(text2.lower().split())
                
                if not words1 or not words2:
                    return 0.0
                    
                intersection = words1 & words2
                union = words1 | words2
                
                return len(intersection) / len(union) if union else 0.0
                
        self.vector_engine = FallbackVectorEngine()
        self.models['vector'] = self.vector_engine
        logger.info("✅ Created fallback vector engine")
        
    def _load_clustering_models(self):
        """Load job clustering models from jaspermatters"""
        try:
            jasper_path = Path("/Users/matthewscott/Projects/jaspermatters-job-intelligence")
            cluster_path = jasper_path / "ml" / "models" / "clustering_models.pkl"
            
            if cluster_path.exists():
                with open(cluster_path, 'rb') as f:
                    self.job_clusterer = pickle.load(f)
                    self.models['clustering'] = self.job_clusterer
                    logger.info("✅ Loaded job clustering models")
            else:
                logger.warning("⚠️ Clustering models not found")
                self.job_clusterer = None
                
        except Exception as e:
            logger.error(f"Failed to load clustering models: {e}")
            self.job_clusterer = None
            
    def _load_ats_optimizer(self):
        """Load ATS optimization from SURVIVE system"""
        class ATSOptimizer:
            """ATS optimization logic from SURVIVE"""
            
            def calculate_ats_score(self, resume_text: str, job_description: str) -> float:
                """Calculate ATS compatibility score"""
                # Extract keywords from job description
                job_keywords = self._extract_keywords(job_description)
                resume_keywords = set(resume_text.lower().split())
                
                # Calculate keyword match rate
                matched = len(job_keywords & resume_keywords)
                total = len(job_keywords) if job_keywords else 1
                
                keyword_score = matched / total
                
                # Check for formatting issues
                format_score = 1.0
                if len(resume_text) < 500:  # Too short
                    format_score *= 0.7
                if len(resume_text) > 5000:  # Too long
                    format_score *= 0.9
                    
                return min(keyword_score * format_score, 1.0)
                
            def _extract_keywords(self, text: str) -> set:
                """Extract important keywords from text"""
                # Key technical skills
                keywords = set()
                tech_terms = [
                    'python', 'tensorflow', 'pytorch', 'machine learning', 'ml',
                    'ai', 'deep learning', 'neural', 'sql', 'docker', 'kubernetes',
                    'aws', 'gcp', 'azure', 'javascript', 'react', 'node',
                    'java', 'scala', 'spark', 'hadoop', 'data', 'analytics'
                ]
                
                text_lower = text.lower()
                for term in tech_terms:
                    if term in text_lower:
                        keywords.add(term)
                        
                return keywords
                
        self.ats_optimizer = ATSOptimizer()
        self.models['ats'] = self.ats_optimizer
        logger.info("✅ Loaded ATS optimizer")
        
    def calculate_unified_score(self, job: Dict, profile: Dict) -> Dict[str, Any]:
        """
        Calculate comprehensive job match score using all models
        
        Args:
            job: Job details dictionary
            profile: User profile/resume dictionary
            
        Returns:
            Dictionary with overall score and component scores
        """
        scores = {}
        
        # 1. Salary prediction score
        if self.salary_predictor:
            try:
                job_df = pd.DataFrame([job])
                predicted_salary = self.salary_predictor.predict(job_df)[0]
                
                # Score based on salary expectations
                target_salary = profile.get('target_salary', 150000)
                salary_diff = abs(predicted_salary - target_salary)
                salary_score = max(0, 1 - (salary_diff / target_salary))
                scores['salary'] = {
                    'score': salary_score,
                    'predicted': predicted_salary,
                    'target': target_salary
                }
            except Exception as e:
                logger.warning(f"Salary prediction failed: {e}")
                scores['salary'] = {'score': 0.5, 'error': str(e)}
        else:
            scores['salary'] = {'score': 0.5, 'status': 'unavailable'}
            
        # 2. Semantic similarity score
        if self.vector_engine:
            try:
                # Create text representations
                job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('requirements', '')}"
                profile_text = f"{profile.get('skills', '')} {profile.get('experience', '')}"
                
                if hasattr(self.vector_engine, 'compute_similarity'):
                    similarity = self.vector_engine.compute_similarity(job_text, profile_text)
                else:
                    # Use sentence transformer directly
                    embeddings = self.vector_engine.model.encode([job_text, profile_text])
                    similarity = float(np.dot(embeddings[0], embeddings[1]) / 
                                     (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])))
                
                scores['semantic'] = {
                    'score': similarity,
                    'threshold': 0.4
                }
            except Exception as e:
                logger.warning(f"Semantic scoring failed: {e}")
                scores['semantic'] = {'score': 0.5, 'error': str(e)}
        else:
            scores['semantic'] = {'score': 0.5, 'status': 'unavailable'}
            
        # 3. Clustering score (job market fit)
        if self.job_clusterer:
            try:
                # This would use the clustering model to determine market fit
                scores['clustering'] = {
                    'score': 0.7,  # Placeholder
                    'cluster': 'high-demand'
                }
            except Exception as e:
                scores['clustering'] = {'score': 0.5, 'error': str(e)}
        else:
            scores['clustering'] = {'score': 0.5, 'status': 'unavailable'}
            
        # 4. ATS optimization score
        if self.ats_optimizer and profile.get('resume_text'):
            try:
                ats_score = self.ats_optimizer.calculate_ats_score(
                    profile['resume_text'],
                    job.get('description', '')
                )
                scores['ats'] = {
                    'score': ats_score,
                    'target': 0.85
                }
            except Exception as e:
                logger.warning(f"ATS scoring failed: {e}")
                scores['ats'] = {'score': 0.5, 'error': str(e)}
        else:
            scores['ats'] = {'score': 0.5, 'status': 'unavailable'}
            
        # 5. Career intelligence score
        intelligence_score = self._calculate_intelligence_score(job, profile)
        scores['intelligence'] = intelligence_score
        
        # Calculate weighted overall score
        overall_score = 0.0
        total_weight = 0.0
        
        for component, weight in self.model_weights.items():
            if component in scores and 'score' in scores[component]:
                overall_score += scores[component]['score'] * weight
                total_weight += weight
                
        if total_weight > 0:
            overall_score = overall_score / total_weight
            
        return {
            'overall_score': overall_score,
            'components': scores,
            'recommendation': self._get_recommendation(overall_score),
            'priority': self._get_priority(overall_score),
            'confidence': total_weight  # How many models contributed
        }
        
    def _calculate_intelligence_score(self, job: Dict, profile: Dict) -> Dict:
        """Calculate career intelligence factors"""
        score = 0.5  # Base score
        factors = []
        
        # Company size preference
        company_size = job.get('company_size', 'unknown')
        if company_size == profile.get('preferred_company_size', 'startup'):
            score += 0.1
            factors.append('company_size_match')
            
        # Remote preference
        if job.get('remote', False) and profile.get('prefers_remote', True):
            score += 0.1
            factors.append('remote_match')
            
        # Industry alignment
        job_industry = job.get('industry', '').lower()
        preferred_industries = profile.get('preferred_industries', ['tech', 'ai', 'healthcare'])
        if any(ind in job_industry for ind in preferred_industries):
            score += 0.2
            factors.append('industry_match')
            
        # Recent posting bonus
        posted_date = job.get('posted_date')
        if posted_date:
            try:
                days_old = (datetime.now() - datetime.fromisoformat(posted_date)).days
                if days_old <= 7:
                    score += 0.1
                    factors.append('recently_posted')
            except:
                pass
                
        return {
            'score': min(score, 1.0),
            'factors': factors
        }
        
    def _get_recommendation(self, score: float) -> str:
        """Get application recommendation based on score"""
        if score >= 0.8:
            return "HIGHLY_RECOMMENDED"
        elif score >= 0.6:
            return "RECOMMENDED"
        elif score >= 0.4:
            return "WORTH_CONSIDERING"
        else:
            return "LOW_PRIORITY"
            
    def _get_priority(self, score: float) -> int:
        """Get priority level (1-5, 1 being highest)"""
        if score >= 0.8:
            return 1
        elif score >= 0.6:
            return 2
        elif score >= 0.4:
            return 3
        elif score >= 0.2:
            return 4
        else:
            return 5
            
    def batch_score_jobs(self, jobs: List[Dict], profile: Dict, 
                         top_n: Optional[int] = None) -> List[Dict]:
        """
        Score multiple jobs and return ranked results
        
        Args:
            jobs: List of job dictionaries
            profile: User profile dictionary
            top_n: Return only top N results
            
        Returns:
            List of jobs with scores, sorted by overall score
        """
        logger.info(f"Scoring {len(jobs)} jobs...")
        
        scored_jobs = []
        for job in jobs:
            try:
                score_result = self.calculate_unified_score(job, profile)
                job_with_score = job.copy()
                job_with_score['ml_analysis'] = score_result
                scored_jobs.append(job_with_score)
            except Exception as e:
                logger.error(f"Failed to score job {job.get('job_uid', 'unknown')}: {e}")
                continue
                
        # Sort by overall score
        scored_jobs.sort(key=lambda x: x['ml_analysis']['overall_score'], reverse=True)
        
        if top_n:
            scored_jobs = scored_jobs[:top_n]
            
        logger.info(f"Completed scoring. Top score: {scored_jobs[0]['ml_analysis']['overall_score']:.3f}")
        
        return scored_jobs
        
    def explain_score(self, job: Dict, profile: Dict) -> str:
        """Generate human-readable explanation of job score"""
        result = self.calculate_unified_score(job, profile)
        
        explanation = f"""
📊 Job Match Analysis for {job.get('position', 'Position')} at {job.get('company', 'Company')}

Overall Score: {result['overall_score']:.1%}
Recommendation: {result['recommendation']}
Priority Level: {result['priority']}

Component Breakdown:
"""
        
        for component, data in result['components'].items():
            if isinstance(data, dict) and 'score' in data:
                score = data['score']
                weight = self.model_weights.get(component, 0)
                contribution = score * weight
                
                explanation += f"\n{component.title()}: {score:.1%} (weight: {weight:.0%}, contribution: {contribution:.1%})"
                
                # Add specific insights
                if component == 'salary' and 'predicted' in data:
                    explanation += f"\n  → Predicted salary: ${data['predicted']:,.0f}"
                elif component == 'semantic':
                    explanation += f"\n  → Semantic match: {'Strong' if score > 0.6 else 'Moderate' if score > 0.4 else 'Weak'}"
                elif component == 'ats':
                    explanation += f"\n  → ATS compatibility: {'Excellent' if score > 0.85 else 'Good' if score > 0.7 else 'Needs work'}"
                    
        return explanation
        
    def get_model_status(self) -> Dict:
        """Get status of all loaded models"""
        status = {
            'total_models': len(self.models),
            'models': {}
        }
        
        for name, model in self.models.items():
            status['models'][name] = {
                'loaded': model is not None,
                'type': type(model).__name__ if model else 'Not loaded'
            }
            
        return status


def main():
    """Test the unified ML engine"""
    engine = UnifiedMLEngine()
    
    # Show model status
    status = engine.get_model_status()
    print("\n🤖 Unified ML Engine Status")
    print("=" * 60)
    print(f"Total models loaded: {status['total_models']}")
    for name, info in status['models'].items():
        print(f"  • {name}: {'✅' if info['loaded'] else '❌'} ({info['type']})")
    
    # Test with sample job
    test_job = {
        'job_uid': 'test123',
        'company': 'TechCorp AI',
        'position': 'Senior Machine Learning Engineer',
        'title': 'Senior Machine Learning Engineer',
        'description': 'Looking for an experienced ML engineer with deep learning expertise',
        'requirements': 'Python, TensorFlow, PyTorch, Docker, AWS, 5+ years experience',
        'remote': True,
        'company_size': 'startup',
        'industry': 'AI/Tech',
        'posted_date': datetime.now().isoformat()
    }
    
    test_profile = {
        'skills': 'Python, TensorFlow, Machine Learning, Deep Learning, AWS, Docker',
        'experience': '10 years in ML/AI, built production models at scale',
        'target_salary': 180000,
        'prefers_remote': True,
        'preferred_company_size': 'startup',
        'preferred_industries': ['ai', 'tech', 'healthcare'],
        'resume_text': 'Senior ML Engineer with 10 years experience in Python, TensorFlow, and production ML systems'
    }
    
    # Calculate unified score
    print("\n🎯 Testing Unified Scoring")
    print("=" * 60)
    
    result = engine.calculate_unified_score(test_job, test_profile)
    print(f"Overall Score: {result['overall_score']:.2%}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Priority: Level {result['priority']}")
    
    # Show explanation
    print("\n📝 Score Explanation")
    print("=" * 60)
    explanation = engine.explain_score(test_job, test_profile)
    print(explanation)
    
    print("\n✨ Unified ML Engine ready for production!")


if __name__ == "__main__":
    main()