#!/usr/bin/env python3
"""
Vector Store for Unified Career System
Manages embeddings for all jobs across systems for fast semantic search
"""

import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import sqlite3
import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedVectorStore:
    """
    Centralized vector store for job embeddings
    Supports semantic search across all job sources
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 cache_path: str = "unified_career_system/ml_engine/embeddings_cache.pkl"):
        """
        Initialize vector store with sentence transformer model
        
        Args:
            model_name: Sentence transformer model to use
            cache_path: Path to save/load embeddings cache
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.cache_path = Path(cache_path)
        
        # In-memory storage
        self.embeddings = {}  # job_uid -> embedding
        self.metadata = {}     # job_uid -> job metadata
        self.index = None      # numpy array for batch similarity
        self.index_ids = []    # job_uids in same order as index
        
        # Load existing cache if available
        self._load_cache()
        
        logger.info(f"Initialized UnifiedVectorStore with {model_name}")
        logger.info(f"Embedding dimension: {self.dimension}")
        logger.info(f"Cached embeddings: {len(self.embeddings)}")
        
    def _load_cache(self):
        """Load cached embeddings from disk"""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.embeddings = cache_data.get('embeddings', {})
                    self.metadata = cache_data.get('metadata', {})
                    self._rebuild_index()
                    logger.info(f"Loaded {len(self.embeddings)} cached embeddings")
            except Exception as e:
                logger.error(f"Failed to load cache: {e}")
                self.embeddings = {}
                self.metadata = {}
                
    def _save_cache(self):
        """Save embeddings cache to disk"""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, 'wb') as f:
                pickle.dump({
                    'embeddings': self.embeddings,
                    'metadata': self.metadata,
                    'timestamp': datetime.now().isoformat()
                }, f)
            logger.info(f"Saved {len(self.embeddings)} embeddings to cache")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            
    def _rebuild_index(self):
        """Rebuild numpy index for fast similarity search"""
        if self.embeddings:
            self.index_ids = list(self.embeddings.keys())
            embeddings_list = [self.embeddings[uid] for uid in self.index_ids]
            self.index = np.array(embeddings_list)
            logger.info(f"Rebuilt index with {len(self.index_ids)} embeddings")
        else:
            self.index = None
            self.index_ids = []
            
    def create_job_embedding(self, job: Dict[str, Any]) -> np.ndarray:
        """
        Create embedding for a job posting
        
        Args:
            job: Job dictionary with title, description, requirements, etc.
            
        Returns:
            Embedding vector
        """
        # Combine relevant fields with weights
        text_parts = []
        
        # Title is most important (appears twice)
        if job.get('position') or job.get('title'):
            title = job.get('position') or job.get('title')
            text_parts.append(f"Job Title: {title}")
            text_parts.append(title)  # Double weight for title
            
        # Company provides context
        if job.get('company'):
            text_parts.append(f"Company: {job['company']}")
            
        # Department/team
        if job.get('department'):
            text_parts.append(f"Department: {job['department']}")
            
        # Level/seniority
        if job.get('level'):
            text_parts.append(f"Level: {job['level']}")
            
        # Description (limited to prevent domination)
        if job.get('description'):
            desc = str(job['description'])[:1000]
            text_parts.append(f"Description: {desc}")
            
        # Requirements are crucial for matching
        if job.get('requirements'):
            if isinstance(job['requirements'], list):
                reqs = ', '.join(job['requirements'][:15])
            else:
                reqs = str(job['requirements'])[:500]
            text_parts.append(f"Requirements: {reqs}")
            
        # Nice to have / preferred
        if job.get('nice_to_have'):
            text_parts.append(f"Preferred: {job['nice_to_have']}")
            
        # Location and remote status
        if job.get('location'):
            text_parts.append(f"Location: {job['location']}")
        if job.get('remote_type'):
            text_parts.append(f"Remote: {job['remote_type']}")
            
        # Combine all parts
        full_text = " | ".join(text_parts)
        
        # Generate embedding
        embedding = self.model.encode(full_text, convert_to_numpy=True)
        
        return embedding
        
    def add_job(self, job: Dict[str, Any], job_uid: Optional[str] = None) -> str:
        """
        Add a job to the vector store
        
        Args:
            job: Job dictionary
            job_uid: Optional unique ID (will generate if not provided)
            
        Returns:
            Job UID
        """
        # Generate UID if not provided
        if not job_uid:
            job_uid = self._generate_uid(job)
            
        # Create embedding
        embedding = self.create_job_embedding(job)
        
        # Store embedding and metadata
        self.embeddings[job_uid] = embedding
        self.metadata[job_uid] = {
            'company': job.get('company'),
            'position': job.get('position') or job.get('title'),
            'location': job.get('location'),
            'remote': job.get('remote_type') or job.get('remote'),
            'source': job.get('source'),
            'added_date': datetime.now().isoformat(),
            'url': job.get('url')
        }
        
        # Rebuild index
        self._rebuild_index()
        
        # Save cache periodically (every 10 new jobs)
        if len(self.embeddings) % 10 == 0:
            self._save_cache()
            
        return job_uid
        
    def add_jobs_batch(self, jobs: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple jobs in batch
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of job UIDs
        """
        logger.info(f"Adding {len(jobs)} jobs to vector store...")
        
        uids = []
        for job in jobs:
            try:
                uid = self.add_job(job)
                uids.append(uid)
            except Exception as e:
                logger.error(f"Failed to add job: {e}")
                continue
                
        # Rebuild index once after batch
        self._rebuild_index()
        self._save_cache()
        
        logger.info(f"Successfully added {len(uids)} jobs")
        return uids
        
    def search_similar_jobs(self, query: str, top_k: int = 10,
                           min_similarity: float = 0.3) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar jobs using semantic search
        
        Args:
            query: Search query (can be job description, skills, or requirements)
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of (job_uid, similarity_score, metadata) tuples
        """
        if not self.index:
            logger.warning("No jobs in vector store")
            return []
            
        # Encode query
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        
        # Calculate similarities
        similarities = cosine_similarity([query_embedding], self.index)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Filter by minimum similarity and create results
        results = []
        for idx in top_indices:
            similarity = float(similarities[idx])
            if similarity >= min_similarity:
                job_uid = self.index_ids[idx]
                results.append((
                    job_uid,
                    similarity,
                    self.metadata[job_uid]
                ))
                
        return results
        
    def find_duplicate_jobs(self, job: Dict[str, Any], 
                           threshold: float = 0.85) -> List[Tuple[str, float]]:
        """
        Find potential duplicate jobs in the store
        
        Args:
            job: Job to check for duplicates
            threshold: Similarity threshold for duplicates
            
        Returns:
            List of (job_uid, similarity) for potential duplicates
        """
        if not self.index:
            return []
            
        # Create embedding for the job
        job_embedding = self.create_job_embedding(job)
        
        # Find similar jobs
        similarities = cosine_similarity([job_embedding], self.index)[0]
        
        # Find jobs above threshold
        duplicates = []
        for idx, similarity in enumerate(similarities):
            if similarity >= threshold:
                job_uid = self.index_ids[idx]
                # Check if it's not the same company/position
                metadata = self.metadata[job_uid]
                if (metadata['company'] == job.get('company') and 
                    metadata['position'] == (job.get('position') or job.get('title'))):
                    duplicates.append((job_uid, float(similarity)))
                    
        return duplicates
        
    def get_job_recommendations(self, profile: Dict[str, Any], 
                               top_k: int = 20) -> List[Tuple[str, float, Dict]]:
        """
        Get job recommendations based on user profile
        
        Args:
            profile: User profile with skills, experience, preferences
            top_k: Number of recommendations
            
        Returns:
            List of recommended jobs with scores
        """
        # Create profile text for embedding
        profile_parts = []
        
        if profile.get('skills'):
            profile_parts.append(f"Skills: {profile['skills']}")
            
        if profile.get('experience'):
            profile_parts.append(f"Experience: {profile['experience']}")
            
        if profile.get('desired_roles'):
            roles = ', '.join(profile['desired_roles']) if isinstance(profile['desired_roles'], list) else profile['desired_roles']
            profile_parts.append(f"Desired roles: {roles}")
            
        if profile.get('industries'):
            industries = ', '.join(profile['industries']) if isinstance(profile['industries'], list) else profile['industries']
            profile_parts.append(f"Industries: {industries}")
            
        profile_text = " | ".join(profile_parts)
        
        # Search for similar jobs
        recommendations = self.search_similar_jobs(profile_text, top_k=top_k)
        
        return recommendations
        
    def _generate_uid(self, job: Dict[str, Any]) -> str:
        """Generate unique ID for a job"""
        content = f"{job.get('company', '')}_{job.get('position', '')}_{job.get('location', '')}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
        
    def update_from_database(self, db_path: str):
        """
        Update vector store from unified database
        
        Args:
            db_path: Path to unified career database
        """
        logger.info(f"Updating vector store from database: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all active jobs
        cursor.execute("""
        SELECT job_uid, company, position, description, requirements,
               location, remote_type, department, level, nice_to_have,
               url, source
        FROM master_jobs
        WHERE is_active = 1
        """)
        
        jobs = cursor.fetchall()
        conn.close()
        
        added = 0
        updated = 0
        
        for row in jobs:
            job_uid = row[0]
            
            # Skip if already have recent embedding
            if job_uid in self.embeddings:
                updated += 1
                continue
                
            # Create job dict
            job = {
                'job_uid': job_uid,
                'company': row[1],
                'position': row[2],
                'description': row[3],
                'requirements': row[4],
                'location': row[5],
                'remote_type': row[6],
                'department': row[7],
                'level': row[8],
                'nice_to_have': row[9],
                'url': row[10],
                'source': row[11]
            }
            
            # Add to vector store
            self.add_job(job, job_uid)
            added += 1
            
        logger.info(f"Added {added} new embeddings, {updated} already existed")
        self._save_cache()
        
    def get_statistics(self) -> Dict:
        """Get vector store statistics"""
        stats = {
            'total_embeddings': len(self.embeddings),
            'embedding_dimension': self.dimension,
            'cache_size_mb': self.cache_path.stat().st_size / 1024 / 1024 if self.cache_path.exists() else 0,
            'sources': {}
        }
        
        # Count by source
        for metadata in self.metadata.values():
            source = metadata.get('source', 'unknown')
            stats['sources'][source] = stats['sources'].get(source, 0) + 1
            
        return stats


def main():
    """Test the unified vector store"""
    store = UnifiedVectorStore()
    
    # Add sample jobs
    sample_jobs = [
        {
            'company': 'AI Startup',
            'position': 'Senior ML Engineer',
            'description': 'Build cutting-edge ML models for production',
            'requirements': ['Python', 'TensorFlow', 'PyTorch', 'AWS'],
            'location': 'San Francisco',
            'remote_type': 'Hybrid'
        },
        {
            'company': 'Big Tech Co',
            'position': 'Machine Learning Scientist',
            'description': 'Research and develop new AI algorithms',
            'requirements': ['PhD', 'Deep Learning', 'Research', 'Publications'],
            'location': 'Remote',
            'remote_type': 'Full Remote'
        },
        {
            'company': 'Healthcare AI',
            'position': 'AI Engineer - Healthcare',
            'description': 'Apply AI to healthcare problems',
            'requirements': ['Python', 'Medical Imaging', 'FDA', 'Clinical'],
            'location': 'Boston',
            'remote_type': 'On-site'
        }
    ]
    
    print("🔄 Adding sample jobs to vector store...")
    uids = store.add_jobs_batch(sample_jobs)
    print(f"✅ Added {len(uids)} jobs")
    
    # Test semantic search
    print("\n🔍 Testing Semantic Search")
    print("=" * 60)
    
    query = "I want to work on deep learning models in production with Python"
    results = store.search_similar_jobs(query, top_k=3)
    
    print(f"Query: '{query}'")
    print(f"\nTop matches:")
    for uid, score, metadata in results:
        print(f"  • {metadata['position']} at {metadata['company']}")
        print(f"    Similarity: {score:.3f}")
        print(f"    Location: {metadata['location']} ({metadata['remote']})")
    
    # Test duplicate detection
    print("\n🔍 Testing Duplicate Detection")
    print("=" * 60)
    
    duplicate_job = {
        'company': 'AI Startup',
        'position': 'Senior ML Engineer',
        'description': 'Build ML models for our platform',
        'requirements': ['Python', 'TensorFlow'],
    }
    
    duplicates = store.find_duplicate_jobs(duplicate_job)
    if duplicates:
        print(f"Found {len(duplicates)} potential duplicate(s):")
        for uid, score in duplicates:
            print(f"  • UID: {uid}, Similarity: {score:.3f}")
    else:
        print("No duplicates found")
    
    # Test profile-based recommendations
    print("\n🎯 Testing Profile-Based Recommendations")
    print("=" * 60)
    
    profile = {
        'skills': 'Python, TensorFlow, Deep Learning, AWS, Production ML',
        'experience': '5 years building ML systems at scale',
        'desired_roles': ['ML Engineer', 'AI Engineer'],
        'industries': ['Tech', 'AI', 'Healthcare']
    }
    
    recommendations = store.get_job_recommendations(profile, top_k=3)
    print("Recommendations based on profile:")
    for uid, score, metadata in recommendations:
        print(f"  • {metadata['position']} at {metadata['company']}")
        print(f"    Match score: {score:.3f}")
    
    # Show statistics
    print("\n📊 Vector Store Statistics")
    print("=" * 60)
    stats = store.get_statistics()
    print(f"Total embeddings: {stats['total_embeddings']}")
    print(f"Embedding dimension: {stats['embedding_dimension']}")
    print(f"Cache size: {stats['cache_size_mb']:.2f} MB")
    
    print("\n✨ Vector store ready for production!")


if __name__ == "__main__":
    main()