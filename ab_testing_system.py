#!/usr/bin/env python3
"""
A/B Testing System for Job Applications
Automatically rotates between different resume versions and cover letter styles
Tracks performance to optimize response rates
"""

import json
import random
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class ABTestingSystem:
    """Manage A/B testing for job applications"""
    
    def __init__(self):
        self.db_path = "UNIFIED_AI_JOBS.db"
        self.config_path = "ab_testing_config.json"
        self.results_path = "data/ab_testing_results.json"
        
        # Load or create configuration
        self.config = self._load_config()
        
        # Track current test rotation
        self.current_test_index = 0
        
    def _load_config(self):
        """Load or create A/B testing configuration"""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default configuration
            config = {
                "resume_versions": {
                    "technical": {
                        "path": "resumes/technical_deep_dive.pdf",
                        "description": "Technical focus with detailed project descriptions",
                        "weight": 0.25,
                        "applications": 0,
                        "responses": 0,
                        "interviews": 0
                    },
                    "executive": {
                        "path": "resumes/executive_leadership.pdf",
                        "description": "Leadership and business impact focus",
                        "weight": 0.25,
                        "applications": 0,
                        "responses": 0,
                        "interviews": 0
                    },
                    "balanced": {
                        "path": "resumes/matthew_scott_ai_ml_resume.pdf",
                        "description": "Balanced technical and leadership",
                        "weight": 0.35,
                        "applications": 0,
                        "responses": 0,
                        "interviews": 0
                    },
                    "master": {
                        "path": "resumes/master_resume_-_all_keywords.pdf",
                        "description": "Keyword-optimized for ATS",
                        "weight": 0.15,
                        "applications": 0,
                        "responses": 0,
                        "interviews": 0
                    }
                },
                "cover_letter_styles": {
                    "technical": {
                        "template": "technical_achievements",
                        "opening": "As an AI/ML engineer with 10+ years building production systems",
                        "weight": 0.33,
                        "applications": 0,
                        "responses": 0
                    },
                    "impact": {
                        "template": "business_impact",
                        "opening": "Having delivered $1.2M in savings through AI innovation",
                        "weight": 0.33,
                        "applications": 0,
                        "responses": 0
                    },
                    "innovative": {
                        "template": "consciousness_research",
                        "opening": "As a pioneer in AI consciousness research (HCL: 0.83/1.0)",
                        "weight": 0.34,
                        "applications": 0,
                        "responses": 0
                    }
                },
                "application_timing": {
                    "morning": {"hours": [9, 10, 11], "weight": 0.4},
                    "afternoon": {"hours": [14, 15, 16], "weight": 0.35},
                    "evening": {"hours": [18, 19, 20], "weight": 0.25}
                },
                "test_settings": {
                    "min_applications_per_variant": 10,
                    "confidence_threshold": 0.95,
                    "auto_optimize": True,
                    "optimization_interval_days": 7
                }
            }
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return config
    
    def select_resume_version(self, company_type: str = None) -> Tuple[str, str]:
        """Select resume version using weighted random selection or rules"""
        
        # Special rules for certain company types
        if company_type:
            if company_type in ['startup', 'AI company', 'research lab']:
                # Prefer technical or innovative for these
                if random.random() < 0.7:
                    return self._get_resume_path('technical')
            elif company_type in ['enterprise', 'Fortune 500']:
                # Prefer executive for these
                if random.random() < 0.7:
                    return self._get_resume_path('executive')
        
        # Weighted random selection
        versions = list(self.config['resume_versions'].keys())
        weights = [self.config['resume_versions'][v]['weight'] for v in versions]
        
        selected = random.choices(versions, weights=weights)[0]
        return self._get_resume_path(selected)
    
    def _get_resume_path(self, version: str) -> Tuple[str, str]:
        """Get resume path and version name"""
        resume_info = self.config['resume_versions'][version]
        return resume_info['path'], version
    
    def select_cover_letter_style(self) -> Tuple[str, str]:
        """Select cover letter style using weighted random selection"""
        styles = list(self.config['cover_letter_styles'].keys())
        weights = [self.config['cover_letter_styles'][s]['weight'] for s in styles]
        
        selected = random.choices(styles, weights=weights)[0]
        return self.config['cover_letter_styles'][selected]['opening'], selected
    
    def get_optimal_timing(self) -> int:
        """Get optimal hour to send application"""
        current_hour = datetime.now().hour
        
        # Check if current hour is in any timing window
        for period, settings in self.config['application_timing'].items():
            if current_hour in settings['hours']:
                return current_hour
        
        # Otherwise, return the next optimal hour
        all_hours = []
        for period, settings in self.config['application_timing'].items():
            all_hours.extend(settings['hours'])
        
        # Find next available hour
        all_hours.sort()
        for hour in all_hours:
            if hour > current_hour:
                return hour
        
        # If no hours left today, return first hour tomorrow
        return all_hours[0]
    
    def track_application(self, company: str, position: str, resume_version: str, 
                         cover_letter_style: str):
        """Track that an application was sent with specific variants"""
        # Update configuration counts
        self.config['resume_versions'][resume_version]['applications'] += 1
        self.config['cover_letter_styles'][cover_letter_style]['applications'] += 1
        
        # Save configuration
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Update database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE job_discoveries 
            SET resume_version = ? 
            WHERE company = ? AND position = ?
            ORDER BY date_applied DESC
            LIMIT 1
        """, (resume_version, company, position))
        
        conn.commit()
        conn.close()
    
    def update_response_metrics(self):
        """Update A/B test metrics based on database responses"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get response metrics by resume version
        cursor.execute("""
            SELECT resume_version, 
                   COUNT(*) as applications,
                   SUM(CASE WHEN response_received = 1 THEN 1 ELSE 0 END) as responses,
                   SUM(CASE WHEN interview_scheduled = 1 THEN 1 ELSE 0 END) as interviews
            FROM job_discoveries 
            WHERE applied = 1 AND resume_version IS NOT NULL
            GROUP BY resume_version
        """)
        
        results = cursor.fetchall()
        
        # Update configuration with actual metrics
        for version, apps, responses, interviews in results:
            if version in self.config['resume_versions']:
                self.config['resume_versions'][version]['applications'] = apps
                self.config['resume_versions'][version]['responses'] = responses
                self.config['resume_versions'][version]['interviews'] = interviews
        
        conn.close()
        
        # Save updated configuration
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def calculate_performance(self) -> Dict:
        """Calculate performance metrics for each variant"""
        self.update_response_metrics()
        
        performance = {
            'resume_versions': {},
            'cover_letter_styles': {},
            'best_combination': None,
            'recommendations': []
        }
        
        # Calculate resume version performance
        for version, data in self.config['resume_versions'].items():
            apps = data['applications']
            if apps > 0:
                response_rate = (data['responses'] / apps) * 100
                interview_rate = (data['interviews'] / apps) * 100
                
                performance['resume_versions'][version] = {
                    'applications': apps,
                    'response_rate': round(response_rate, 1),
                    'interview_rate': round(interview_rate, 1),
                    'score': round(response_rate + (interview_rate * 2), 1)  # Weight interviews more
                }
        
        # Calculate cover letter style performance
        for style, data in self.config['cover_letter_styles'].items():
            apps = data['applications']
            if apps > 0:
                response_rate = (data['responses'] / apps) * 100
                
                performance['cover_letter_styles'][style] = {
                    'applications': apps,
                    'response_rate': round(response_rate, 1)
                }
        
        # Find best performing combination
        if performance['resume_versions']:
            best_resume = max(performance['resume_versions'].items(), 
                            key=lambda x: x[1].get('score', 0))
            performance['best_combination'] = {
                'resume': best_resume[0],
                'score': best_resume[1].get('score', 0)
            }
        
        # Generate recommendations
        performance['recommendations'] = self._generate_recommendations(performance)
        
        # Save results
        with open(self.results_path, 'w') as f:
            json.dump(performance, f, indent=2)
        
        return performance
    
    def _generate_recommendations(self, performance: Dict) -> List[str]:
        """Generate actionable recommendations based on performance"""
        recommendations = []
        
        # Check if we have enough data
        total_apps = sum(v.get('applications', 0) 
                        for v in performance['resume_versions'].values())
        
        if total_apps < 20:
            recommendations.append(f"Need {20 - total_apps} more applications for statistically significant results")
            return recommendations
        
        # Find underperforming versions
        for version, metrics in performance['resume_versions'].items():
            if metrics['applications'] >= 10 and metrics['response_rate'] < 5:
                recommendations.append(f"Consider retiring '{version}' resume (response rate: {metrics['response_rate']}%)")
        
        # Find top performers
        if performance['best_combination']:
            best = performance['best_combination']
            recommendations.append(f"Increase weight for '{best['resume']}' resume (score: {best['score']})")
        
        return recommendations
    
    def auto_optimize(self):
        """Automatically adjust weights based on performance"""
        if not self.config['test_settings']['auto_optimize']:
            return
        
        performance = self.calculate_performance()
        
        # Adjust resume version weights
        total_score = sum(v.get('score', 1) 
                         for v in performance['resume_versions'].values())
        
        if total_score > 0:
            for version in self.config['resume_versions']:
                if version in performance['resume_versions']:
                    score = performance['resume_versions'][version].get('score', 1)
                    # New weight proportional to performance
                    new_weight = score / total_score
                    self.config['resume_versions'][version]['weight'] = round(new_weight, 3)
        
        # Save optimized configuration
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print("✅ Weights auto-optimized based on performance")
    
    def display_dashboard(self):
        """Display A/B testing dashboard"""
        performance = self.calculate_performance()
        
        print("\n" + "="*60)
        print("🧪 A/B TESTING DASHBOARD")
        print("="*60)
        
        print("\n📄 RESUME VERSION PERFORMANCE:")
        for version, metrics in performance['resume_versions'].items():
            print(f"\n  {version.upper()}:")
            print(f"    Applications: {metrics['applications']}")
            print(f"    Response Rate: {metrics['response_rate']}%")
            print(f"    Interview Rate: {metrics['interview_rate']}%")
            print(f"    Score: {metrics['score']}")
        
        if performance['best_combination']:
            print(f"\n🏆 BEST PERFORMER: {performance['best_combination']['resume']}")
            print(f"   Score: {performance['best_combination']['score']}")
        
        print("\n💬 COVER LETTER STYLE PERFORMANCE:")
        for style, metrics in performance['cover_letter_styles'].items():
            print(f"  {style}: {metrics['applications']} sent, {metrics['response_rate']}% response rate")
        
        if performance['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for rec in performance['recommendations']:
                print(f"  • {rec}")
        
        print("\n" + "="*60)
        
        # Show current weights
        print("\n⚖️  CURRENT WEIGHTS:")
        for version, data in self.config['resume_versions'].items():
            print(f"  {version}: {data['weight']*100:.0f}%")
        
        print("\n" + "="*60 + "\n")

def main():
    """Main execution for testing"""
    ab_system = ABTestingSystem()
    
    # Display current performance
    ab_system.display_dashboard()
    
    # Example: Select variants for next application
    print("\n🎲 NEXT APPLICATION VARIANTS:")
    resume_path, resume_version = ab_system.select_resume_version()
    cover_opening, cover_style = ab_system.select_cover_letter_style()
    optimal_hour = ab_system.get_optimal_timing()
    
    print(f"  Resume: {resume_version} ({resume_path})")
    print(f"  Cover Letter: {cover_style}")
    print(f"  Opening: '{cover_opening}...'")
    print(f"  Send at: {optimal_hour}:00")
    
    # Check if optimization is needed
    total_apps = sum(v['applications'] 
                    for v in ab_system.config['resume_versions'].values())
    
    if total_apps > 0 and total_apps % 20 == 0:
        print("\n🔄 Running auto-optimization...")
        ab_system.auto_optimize()

if __name__ == "__main__":
    main()