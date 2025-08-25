#!/usr/bin/env python3
"""
Smart Routing System for Unified Career Platform
Prevents duplicates and optimizes application routing across all systems
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
import hashlib
import json
import logging
from enum import Enum
from dataclasses import dataclass

# Add parent path
sys.path.append(str(Path(__file__).parent.parent.parent))
from unified_career_system.data_layer.master_database import MasterDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RouteDecision(Enum):
    """Routing decisions"""
    APPLY = "apply"
    SKIP_DUPLICATE = "skip_duplicate"
    SKIP_COOLDOWN = "skip_cooldown"  
    SKIP_PENALTY = "skip_penalty"
    SKIP_LIMIT = "skip_limit"
    SKIP_BLACKLIST = "skip_blacklist"
    DEFER = "defer"


@dataclass 
class RoutingResult:
    """Result of routing decision"""
    job_uid: str
    company: str
    position: str
    decision: RouteDecision
    reason: str
    recommended_method: Optional[str] = None
    retry_after: Optional[datetime] = None
    duplicate_of: Optional[str] = None


class SmartRouter:
    """
    Intelligent routing system to prevent duplicates and optimize applications
    
    Features:
    - Cross-system duplicate detection
    - Company penalty tracking
    - Cooldown period enforcement
    - Daily/weekly limits
    - Blacklist management
    - Intelligent retry scheduling
    """
    
    def __init__(self, db_path: str = "unified_career_system/data_layer/unified_career.db"):
        """Initialize the smart router"""
        self.db_path = db_path
        self.master_db = MasterDatabase(db_path)
        
        # Routing rules
        self.rules = {
            'max_per_company_daily': 3,
            'max_per_company_weekly': 5,
            'max_per_company_total': 10,
            'cooldown_after_rejection': 30,  # days
            'cooldown_after_no_response': 14,  # days
            'cooldown_between_applications': 7,  # days
            'max_daily_total': 75,
            'max_weekly_total': 300
        }
        
        # Company blacklist (never apply)
        self.blacklist = set()
        self._load_blacklist()
        
        # Penalty scores
        self.penalty_thresholds = {
            'low': 3.0,
            'medium': 5.0,
            'high': 7.0,
            'critical': 9.0
        }
        
        # Duplicate detection cache
        self.duplicate_cache = {}
        self._build_duplicate_cache()
        
        logger.info("Initialized SmartRouter with cross-system duplicate prevention")
        
    def _load_blacklist(self):
        """Load company blacklist from database"""
        cursor = self.master_db.conn.cursor()
        
        # Companies with critical penalties or explicit blacklist
        cursor.execute("""
        SELECT company_name FROM company_intelligence
        WHERE penalty_score >= ? OR notes LIKE '%blacklist%'
        """, (self.penalty_thresholds['critical'],))
        
        for row in cursor.fetchall():
            self.blacklist.add(row[0].lower())
            
        logger.info(f"Loaded {len(self.blacklist)} blacklisted companies")
        
    def _build_duplicate_cache(self):
        """Build cache of existing applications for duplicate detection"""
        cursor = self.master_db.conn.cursor()
        
        # Get all applications from last 90 days
        cursor.execute("""
        SELECT j.company, j.position, j.job_uid, a.applied_date
        FROM master_applications a
        JOIN master_jobs j ON a.job_uid = j.job_uid
        WHERE a.applied_date > date('now', '-90 days')
        """)
        
        for row in cursor.fetchall():
            company = row[0].lower()
            position = self._normalize_position(row[1])
            
            key = f"{company}:{position}"
            if key not in self.duplicate_cache:
                self.duplicate_cache[key] = []
                
            self.duplicate_cache[key].append({
                'job_uid': row[2],
                'applied_date': row[3]
            })
            
        logger.info(f"Built duplicate cache with {len(self.duplicate_cache)} unique positions")
        
    def _normalize_position(self, position: str) -> str:
        """Normalize position title for comparison"""
        if not position:
            return ""
            
        # Remove common variations
        normalized = position.lower()
        replacements = [
            ('senior', 'sr'),
            ('junior', 'jr'),
            ('engineer', 'eng'),
            ('developer', 'dev'),
            ('i ', '1 '),
            ('ii ', '2 '),
            ('iii ', '3 '),
            (' - ', ' '),
            ('/', ' '),
            ('(', ''),
            (')', ''),
            ',', ''
        ]
        
        for old, new in replacements:
            normalized = normalized.replace(old, new)
            
        # Remove extra spaces
        normalized = ' '.join(normalized.split())
        
        return normalized
        
    def route_application(self, job: Dict) -> RoutingResult:
        """
        Make routing decision for a job application
        
        Args:
            job: Job dictionary with company, position, etc.
            
        Returns:
            RoutingResult with decision and reasoning
        """
        company = job.get('company', '').lower()
        position = job.get('position', '')
        job_uid = job.get('job_uid', '')
        
        # Check 1: Blacklist
        if company in self.blacklist:
            return RoutingResult(
                job_uid=job_uid,
                company=job['company'],
                position=position,
                decision=RouteDecision.SKIP_BLACKLIST,
                reason=f"{job['company']} is blacklisted"
            )
            
        # Check 2: Duplicate detection
        duplicate_check = self._check_duplicate(company, position)
        if duplicate_check['is_duplicate']:
            return RoutingResult(
                job_uid=job_uid,
                company=job['company'],
                position=position,
                decision=RouteDecision.SKIP_DUPLICATE,
                reason=f"Already applied to similar position on {duplicate_check['applied_date']}",
                duplicate_of=duplicate_check['job_uid']
            )
            
        # Check 3: Company limits
        company_limits = self._check_company_limits(company)
        if not company_limits['can_apply']:
            return RoutingResult(
                job_uid=job_uid,
                company=job['company'],
                position=position,
                decision=RouteDecision.SKIP_LIMIT,
                reason=company_limits['reason'],
                retry_after=company_limits.get('retry_after')
            )
            
        # Check 4: Cooldown periods
        cooldown = self._check_cooldown(company)
        if cooldown['in_cooldown']:
            return RoutingResult(
                job_uid=job_uid,
                company=job['company'],
                position=position,
                decision=RouteDecision.SKIP_COOLDOWN,
                reason=cooldown['reason'],
                retry_after=cooldown['cooldown_until']
            )
            
        # Check 5: Penalty score
        penalty = self._check_penalty(company)
        if penalty['should_skip']:
            return RoutingResult(
                job_uid=job_uid,
                company=job['company'],
                position=position,
                decision=RouteDecision.SKIP_PENALTY,
                reason=penalty['reason']
            )
            
        # Check 6: Daily/weekly totals
        if not self._check_daily_limit():
            return RoutingResult(
                job_uid=job_uid,
                company=job['company'],
                position=position,
                decision=RouteDecision.DEFER,
                reason="Daily application limit reached",
                retry_after=datetime.now() + timedelta(days=1)
            )
            
        # All checks passed - determine best method
        method = self._determine_best_method(job)
        
        return RoutingResult(
            job_uid=job_uid,
            company=job['company'],
            position=position,
            decision=RouteDecision.APPLY,
            reason="All checks passed",
            recommended_method=method
        )
        
    def _check_duplicate(self, company: str, position: str) -> Dict:
        """Check if we've already applied to this position"""
        normalized_position = self._normalize_position(position)
        key = f"{company}:{normalized_position}"
        
        if key in self.duplicate_cache:
            # Found exact match
            most_recent = max(self.duplicate_cache[key], 
                            key=lambda x: x['applied_date'])
            return {
                'is_duplicate': True,
                'job_uid': most_recent['job_uid'],
                'applied_date': most_recent['applied_date']
            }
            
        # Check for similar positions (fuzzy match)
        for cached_key, applications in self.duplicate_cache.items():
            cached_company, cached_position = cached_key.split(':', 1)
            
            if cached_company == company:
                # Check position similarity
                if self._are_positions_similar(normalized_position, cached_position):
                    most_recent = max(applications, 
                                    key=lambda x: x['applied_date'])
                    return {
                        'is_duplicate': True,
                        'job_uid': most_recent['job_uid'],
                        'applied_date': most_recent['applied_date']
                    }
                    
        return {'is_duplicate': False}
        
    def _are_positions_similar(self, pos1: str, pos2: str) -> bool:
        """Check if two positions are essentially the same"""
        # Remove level indicators
        for level in ['sr', 'jr', '1', '2', '3', 'i', 'ii', 'iii', 'iv', 'v']:
            pos1 = pos1.replace(level, '')
            pos2 = pos2.replace(level, '')
            
        # Calculate word overlap
        words1 = set(pos1.split())
        words2 = set(pos2.split())
        
        if not words1 or not words2:
            return False
            
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        
        # 70% similarity threshold
        return (overlap / total) >= 0.7 if total > 0 else False
        
    def _check_company_limits(self, company: str) -> Dict:
        """Check if we're within application limits for this company"""
        cursor = self.master_db.conn.cursor()
        
        # Daily limit
        cursor.execute("""
        SELECT COUNT(*) FROM master_applications a
        JOIN master_jobs j ON a.job_uid = j.job_uid
        WHERE LOWER(j.company) = LOWER(?)
        AND DATE(a.applied_date) = DATE('now')
        """, (company,))
        
        daily_count = cursor.fetchone()[0]
        
        if daily_count >= self.rules['max_per_company_daily']:
            return {
                'can_apply': False,
                'reason': f"Daily limit ({self.rules['max_per_company_daily']}) reached for {company}",
                'retry_after': datetime.now() + timedelta(days=1)
            }
            
        # Weekly limit
        cursor.execute("""
        SELECT COUNT(*) FROM master_applications a
        JOIN master_jobs j ON a.job_uid = j.job_uid
        WHERE LOWER(j.company) = LOWER(?)
        AND a.applied_date > date('now', '-7 days')
        """, (company,))
        
        weekly_count = cursor.fetchone()[0]
        
        if weekly_count >= self.rules['max_per_company_weekly']:
            return {
                'can_apply': False,
                'reason': f"Weekly limit ({self.rules['max_per_company_weekly']}) reached for {company}",
                'retry_after': datetime.now() + timedelta(days=7)
            }
            
        # Total limit
        cursor.execute("""
        SELECT COUNT(*) FROM master_applications a
        JOIN master_jobs j ON a.job_uid = j.job_uid
        WHERE LOWER(j.company) = LOWER(?)
        """, (company,))
        
        total_count = cursor.fetchone()[0]
        
        if total_count >= self.rules['max_per_company_total']:
            return {
                'can_apply': False,
                'reason': f"Maximum applications ({self.rules['max_per_company_total']}) reached for {company}"
            }
            
        return {'can_apply': True}
        
    def _check_cooldown(self, company: str) -> Dict:
        """Check if company is in cooldown period"""
        cursor = self.master_db.conn.cursor()
        
        # Check for recent rejection
        cursor.execute("""
        SELECT MAX(a.response_date) FROM master_applications a
        JOIN master_jobs j ON a.job_uid = j.job_uid
        WHERE LOWER(j.company) = LOWER(?)
        AND a.response_type = 'rejection'
        """, (company,))
        
        last_rejection = cursor.fetchone()[0]
        
        if last_rejection:
            rejection_date = datetime.fromisoformat(last_rejection)
            cooldown_until = rejection_date + timedelta(days=self.rules['cooldown_after_rejection'])
            
            if datetime.now() < cooldown_until:
                return {
                    'in_cooldown': True,
                    'reason': f"In cooldown after rejection (until {cooldown_until.date()})",
                    'cooldown_until': cooldown_until
                }
                
        # Check for recent application
        cursor.execute("""
        SELECT MAX(a.applied_date) FROM master_applications a
        JOIN master_jobs j ON a.job_uid = j.job_uid
        WHERE LOWER(j.company) = LOWER(?)
        """, (company,))
        
        last_application = cursor.fetchone()[0]
        
        if last_application:
            app_date = datetime.fromisoformat(last_application)
            cooldown_until = app_date + timedelta(days=self.rules['cooldown_between_applications'])
            
            if datetime.now() < cooldown_until:
                return {
                    'in_cooldown': True,
                    'reason': f"Too soon after last application (wait until {cooldown_until.date()})",
                    'cooldown_until': cooldown_until
                }
                
        return {'in_cooldown': False}
        
    def _check_penalty(self, company: str) -> Dict:
        """Check company penalty score"""
        cursor = self.master_db.conn.cursor()
        
        cursor.execute("""
        SELECT penalty_score FROM company_intelligence
        WHERE LOWER(company_name) = LOWER(?)
        """, (company,))
        
        result = cursor.fetchone()
        
        if not result:
            return {'should_skip': False}
            
        penalty_score = result[0] or 0
        
        if penalty_score >= self.penalty_thresholds['high']:
            return {
                'should_skip': True,
                'reason': f"High penalty score ({penalty_score:.1f}) for {company}"
            }
            
        return {'should_skip': False}
        
    def _check_daily_limit(self) -> bool:
        """Check if we're within daily application limits"""
        cursor = self.master_db.conn.cursor()
        
        cursor.execute("""
        SELECT COUNT(*) FROM master_applications
        WHERE DATE(applied_date) = DATE('now')
        """)
        
        today_count = cursor.fetchone()[0]
        
        return today_count < self.rules['max_daily_total']
        
    def _determine_best_method(self, job: Dict) -> str:
        """Determine the best application method for this job"""
        # Priority order based on success rates
        if job.get('contact_email'):
            return 'email'
        elif 'linkedin.com' in job.get('url', ''):
            return 'linkedin'
        elif 'greenhouse' in job.get('url', '').lower():
            return 'greenhouse'
        elif 'lever' in job.get('url', '').lower():
            return 'lever'
        else:
            return 'portal'
            
    def batch_route(self, jobs: List[Dict]) -> List[RoutingResult]:
        """
        Route multiple jobs at once
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of routing results
        """
        results = []
        
        for job in jobs:
            result = self.route_application(job)
            results.append(result)
            
            # Update cache if applying
            if result.decision == RouteDecision.APPLY:
                self._update_cache_for_application(job)
                
        return results
        
    def _update_cache_for_application(self, job: Dict):
        """Update duplicate cache when applying to a job"""
        company = job.get('company', '').lower()
        position = self._normalize_position(job.get('position', ''))
        key = f"{company}:{position}"
        
        if key not in self.duplicate_cache:
            self.duplicate_cache[key] = []
            
        self.duplicate_cache[key].append({
            'job_uid': job.get('job_uid'),
            'applied_date': datetime.now().isoformat()
        })
        
    def get_routing_stats(self) -> Dict:
        """Get routing statistics"""
        cursor = self.master_db.conn.cursor()
        
        # Today's applications
        cursor.execute("""
        SELECT COUNT(*) FROM master_applications
        WHERE DATE(applied_date) = DATE('now')
        """)
        today_count = cursor.fetchone()[0]
        
        # This week's applications
        cursor.execute("""
        SELECT COUNT(*) FROM master_applications
        WHERE applied_date > date('now', '-7 days')
        """)
        week_count = cursor.fetchone()[0]
        
        # Companies in cooldown
        cursor.execute("""
        SELECT COUNT(DISTINCT company_name) FROM company_intelligence
        WHERE cooldown_until > datetime('now')
        """)
        cooldown_count = cursor.fetchone()[0]
        
        return {
            'today_applications': today_count,
            'week_applications': week_count,
            'daily_remaining': self.rules['max_daily_total'] - today_count,
            'weekly_remaining': self.rules['max_weekly_total'] - week_count,
            'blacklisted_companies': len(self.blacklist),
            'companies_in_cooldown': cooldown_count,
            'duplicate_cache_size': len(self.duplicate_cache)
        }
        
    def clear_old_cache(self, days: int = 90):
        """Clear old entries from duplicate cache"""
        cutoff = datetime.now() - timedelta(days=days)
        
        for key in list(self.duplicate_cache.keys()):
            # Filter out old applications
            self.duplicate_cache[key] = [
                app for app in self.duplicate_cache[key]
                if datetime.fromisoformat(app['applied_date']) > cutoff
            ]
            
            # Remove empty entries
            if not self.duplicate_cache[key]:
                del self.duplicate_cache[key]
                
        logger.info(f"Cleared cache entries older than {days} days")


def main():
    """Test the smart router"""
    router = SmartRouter()
    
    print("🚦 Smart Routing System v1.0")
    print("=" * 60)
    
    # Get routing stats
    stats = router.get_routing_stats()
    print("\n📊 Current Routing Status:")
    print(f"  • Today's applications: {stats['today_applications']}/{router.rules['max_daily_total']}")
    print(f"  • Week's applications: {stats['week_applications']}/{router.rules['max_weekly_total']}")
    print(f"  • Blacklisted companies: {stats['blacklisted_companies']}")
    print(f"  • Companies in cooldown: {stats['companies_in_cooldown']}")
    print(f"  • Duplicate cache size: {stats['duplicate_cache_size']} positions")
    
    # Test routing decisions
    test_jobs = [
        {
            'job_uid': 'test1',
            'company': 'TechCorp',
            'position': 'Senior ML Engineer',
            'url': 'https://techcorp.com/jobs/123'
        },
        {
            'job_uid': 'test2',
            'company': 'TechCorp',
            'position': 'Sr. Machine Learning Engineer',  # Similar to above
            'url': 'https://techcorp.com/jobs/456'
        },
        {
            'job_uid': 'test3',
            'company': 'StartupAI',
            'position': 'ML Engineer',
            'url': 'https://linkedin.com/jobs/789',
            'contact_email': 'jobs@startupai.com'
        }
    ]
    
    print("\n🧪 Testing Routing Decisions:")
    print("=" * 60)
    
    for job in test_jobs:
        result = router.route_application(job)
        
        print(f"\n{job['position']} at {job['company']}:")
        print(f"  Decision: {result.decision.value}")
        print(f"  Reason: {result.reason}")
        if result.recommended_method:
            print(f"  Method: {result.recommended_method}")
        if result.retry_after:
            print(f"  Retry after: {result.retry_after.date()}")
            
    print("\n✨ Smart routing test complete!")


if __name__ == "__main__":
    main()