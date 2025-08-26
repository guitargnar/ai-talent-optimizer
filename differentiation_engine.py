#!/usr/bin/env python3
"""
Differentiation Engine - Create memorable, specific applications
Makes Matthew Scott stand out from generic applicants
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import re

class DifferentiationEngine:
    """Create highly specific, memorable applications"""
    
    def __init__(self):
        self.db_path = "unified_platform.db"
        self.matthew_stories = self._load_matthew_stories()
        self.company_research = {}
        
    def _load_matthew_stories(self) -> Dict:
        """Load specific stories and achievements that make Matthew unique"""
        return {
            'healthcare_transformation': {
                'story': "I led the ML initiative that reduced hospital readmissions by 23% at Humana, saving $1.2M annually",
                'metrics': {'savings': '$1.2M', 'improvement': '23%', 'scale': '50M members'},
                'keywords': ['healthcare', 'medical', 'patient', 'clinical', 'health']
            },
            'production_scale': {
                'story': "Built ML systems serving 50M+ users with 99.9% uptime, processing 1B+ predictions daily",
                'metrics': {'users': '50M+', 'uptime': '99.9%', 'predictions': '1B+ daily'},
                'keywords': ['scale', 'production', 'infrastructure', 'platform', 'enterprise']
            },
            'team_leadership': {
                'story': "Grew and mentored a team of 8 ML engineers, establishing MLOps practices that reduced deployment time by 75%",
                'metrics': {'team_size': '8', 'deployment_improvement': '75%'},
                'keywords': ['lead', 'senior', 'staff', 'principal', 'team', 'mentor']
            },
            'innovation': {
                'story': "Created novel approach to medication adherence prediction, improving accuracy by 47% over baseline",
                'metrics': {'improvement': '47%', 'impact': 'FDA submission'},
                'keywords': ['research', 'novel', 'innovation', 'scientist', 'R&D']
            },
            'rapid_delivery': {
                'story': "Delivered COVID-19 risk prediction model in 3 weeks during pandemic, deployed to 5 states",
                'metrics': {'timeline': '3 weeks', 'reach': '5 states'},
                'keywords': ['fast', 'agile', 'startup', 'quick', 'rapid']
            },
            'cost_optimization': {
                'story': "Reduced cloud ML infrastructure costs by 60% through custom optimization and smart caching",
                'metrics': {'savings': '60%', 'method': 'custom optimization'},
                'keywords': ['cost', 'optimize', 'efficient', 'savings', 'budget']
            },
            'cross_functional': {
                'story': "Bridged clinical and engineering teams, translating medical expertise into ML features",
                'metrics': {'teams': 'clinical + engineering', 'outcome': 'FDA-ready models'},
                'keywords': ['collaborate', 'cross-functional', 'communication', 'bridge']
            }
        }
    
    def research_company(self, company_name: str, position: str) -> Dict:
        """Deep research on company - their challenges, recent news, tech stack"""
        research = {
            'company': company,
            'position': title,
            'recent_news': [],
            'tech_stack': [],
            'challenges': [],
            'culture_hints': []
        }
        
        # Known company insights (expandable)
        company_insights = {
            'openai': {
                'recent_focus': 'GPT scaling, safety research, enterprise adoption',
                'challenges': ['AI safety', 'compute efficiency', 'responsible deployment'],
                'culture': 'research-driven, mission-focused, collaborative',
                'tech_stack': ['PyTorch', 'Kubernetes', 'Ray', 'Custom infrastructure']
            },
            'anthropic': {
                'recent_focus': 'Constitutional AI, Claude improvements, interpretability',
                'challenges': ['AI alignment', 'scaling safely', 'interpretability'],
                'culture': 'safety-first, research-oriented, thoughtful',
                'tech_stack': ['JAX', 'GCP', 'Custom training infrastructure']
            },
            'google deepmind': {
                'recent_focus': 'Gemini, scientific discovery, AGI research',
                'challenges': ['multi-modal models', 'scientific applications', 'AGI safety'],
                'culture': 'academic, ambitious, interdisciplinary',
                'tech_stack': ['JAX', 'TensorFlow', 'TPUs', 'Borg']
            }
        }
        
        # Get company-specific insights if available
        company_key = company_name.lower().replace(' ', '')
        if company_key in company_insights:
            research.update(company_insights[company_key])
        
        return research
    
    def select_relevant_story(self, job_description: str, company_research: Dict) -> Dict:
        """Select the most relevant story based on job requirements"""
        # Analyze job description for keywords
        job_lower = job_description.lower()
        
        # Score each story based on keyword matches
        story_scores = {}
        for story_key, story_data in self.matthew_stories.items():
            score = sum(1 for keyword in story_data['keywords'] if keyword in job_lower)
            story_scores[story_key] = score
        
        # Select highest scoring story
        best_story_key = max(story_scores, key=story_scores.get)
        if story_scores[best_story_key] == 0:
            # Default to production scale story if no matches
            best_story_key = 'production_scale'
        
        return self.matthew_stories[best_story_key]
    
    def create_memorable_hook(self, company: str, position: str, research: Dict) -> str:
        """Create a memorable opening line that immediately differentiates"""
        hooks = {
            'metric_driven': f"After delivering $1.2M in ML-driven healthcare savings at Humana, I'm excited about {company}'s mission to",
            'problem_solver': f"I've spent the last decade turning complex healthcare data into life-saving ML systems—exactly the kind of challenge I see in {company}'s",
            'scale_focused': f"From building ML platforms serving 50M+ users to optimizing systems processing 1B+ daily predictions, I'm drawn to {company}'s",
            'innovation': f"My novel approach to medication adherence improved predictions by 47%—the same innovative thinking I'd bring to {company}'s",
            'speed': f"When COVID-19 hit, I delivered a risk prediction model in 3 weeks that scaled to 5 states. This rapid, impactful delivery is what excites me about"
        }
        
        # Select hook based on company research
        if 'scale' in position.lower() or 'infrastructure' in position.lower():
            hook_type = 'scale_focused'
        elif 'research' in position.lower() or 'scientist' in position.lower():
            hook_type = 'innovation'
        elif company in ['openai', 'anthropic'] and research.get('recent_focus'):
            hook_type = 'problem_solver'
        else:
            hook_type = 'metric_driven'
        
        return hooks[hook_type]
    
    def generate_specific_value_prop(self, company: str, position: str, research: Dict) -> List[str]:
        """Generate specific value propositions for this role"""
        value_props = []
        
        # Healthcare AI experience
        if any(word in position.lower() for word in ['health', 'medical', 'clinical']):
            value_props.append(
                "• Healthcare ML expertise: FDA-ready models, HIPAA compliance, clinical validation experience"
            )
        
        # Scale and infrastructure
        if any(word in position.lower() for word in ['platform', 'infrastructure', 'scale']):
            value_props.append(
                "• Proven scale: Built systems handling 1B+ predictions daily with 99.9% uptime"
            )
        
        # Leadership
        if any(word in position.lower() for word in ['lead', 'senior', 'staff', 'principal']):
            value_props.append(
                "• Technical leadership: Grew team of 8 engineers, established MLOps practices reducing deployment time 75%"
            )
        
        # Company-specific value
        if company.lower() == 'openai':
            value_props.append(
                "• Alignment with OpenAI's mission: Experience building responsible AI systems in regulated healthcare environment"
            )
        elif company.lower() == 'anthropic':
            value_props.append(
                "• Safety-first approach: Built interpretable models for clinical decisions where mistakes cost lives"
            )
        
        # Always include rapid delivery
        value_props.append(
            "• Rapid iteration: Track record of delivering production ML in weeks, not months"
        )
        
        return value_props
    
    def create_memorable_email(self, job: Dict) -> Dict:
        """Create a completely unique, memorable email for this specific job"""
        company = job['company']
        title = job['position']
        
        # Research company
        research = self.research_company(company, title)
        
        # Get job description (from database or API)
        job_description = job.get('description', title)
        
        # Select most relevant story
        relevant_story = self.select_relevant_story(job_description, research)
        
        # Create memorable hook
        hook = self.create_memorable_hook(company, title, research)
        
        # Generate specific value props
        value_props = self.generate_specific_value_prop(company, title, research)
        
        # Build the email
        subject = f"{position} - {relevant_story['metrics'][list(relevant_story['metrics'].keys())[0]]} Impact Leader"
        
        body = f"""Dear {company} Hiring Team,

{hook} {position.lower()} role.

{relevant_story['story']}. This hands-on experience building and scaling ML systems in production is exactly what I'd bring to your team.

What makes me different:
{chr(10).join(value_props)}

One specific idea for {company}: {self._generate_specific_idea(company, title, research)}

I built an AI system to find this position, but I'm writing this personally because {company} deserves more than automation. You'll find my resume attached, but I'd prefer to show you what I can build.

Ready to discuss how my healthcare ML experience can accelerate {company}'s impact.

Best regards,
Matthew Scott
matthewdscott7@gmail.com | (502) 345-0525 | linkedin.com/in/matthew-david-scott

P.S. The ML system I built to discover this opportunity is open-sourced at [github]. It found {company} because your mission aligns perfectly with my experience making AI work in the real world."""
        
        return {
            'subject': subject,
            'body': body,
            'memorable_elements': [
                f"Subject line with specific metric: {list(relevant_story['metrics'].values())[0]}",
                f"Opening story: {relevant_story['story']}",
                f"Company-specific idea included",
                "Personal touch about building AI to find them"
            ]
        }
    
    def _generate_specific_idea(self, company: str, position: str, research: Dict) -> str:
        """Generate a specific idea for the company"""
        ideas = {
            'openai': "Implement healthcare-proven safety measures for enterprise GPT deployments, reducing hallucinations in critical domains",
            'anthropic': "Apply clinical trial methodologies to constitutional AI training, ensuring safer model behavior",
            'google deepmind': "Leverage my FDA submission experience to help navigate AI regulations for Gemini healthcare applications",
            'default_healthcare': "Create domain-specific evaluation frameworks based on clinical validation methods",
            'default_scale': "Implement the distributed caching strategy that cut our inference costs by 60%",
            'default_research': "Apply my novel feature engineering approach from healthcare to your domain"
        }
        
        company_lower = company.lower()
        if company_lower in ['openai', 'anthropic', 'google deepmind']:
            return ideas[company_lower]
        elif 'health' in position.lower():
            return ideas['default_healthcare']
        elif 'infrastructure' in position.lower() or 'platform' in position.lower():
            return ideas['default_scale']
        else:
            return ideas['default_research']
    
    def differentiate_application(self, job_id: int) -> Dict:
        """Main method to create a differentiated application"""
        # Get job details from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job_row = cursor.fetchone()
        
        if not job_row:
            return None
        
        # Convert to dict
        columns = [desc[0] for desc in cursor.description]
        job = dict(zip(columns, job_row))
        conn.close()
        
        # Create memorable email
        memorable_email = self.create_memorable_email(job)
        
        # Log what makes this unique
        print(f"\n🎯 Differentiation for {job['company']} - {job['position']}:")
        for element in memorable_email['memorable_elements']:
            print(f"  ✓ {element}")
        
        return memorable_email


def demonstrate_differentiation():
    """Show how differentiation works"""
    engine = DifferentiationEngine()
    
    # Test with sample jobs
    test_jobs = [
        {
            'company': 'OpenAI',
            'position': 'Senior ML Infrastructure Engineer',
            'description': 'Build scalable ML systems for GPT training'
        },
        {
            'company': 'Anthropic',
            'position': 'AI Safety Research Engineer',
            'description': 'Work on constitutional AI and interpretability'
        },
        {
            'company': 'Healthcare AI Startup',
            'position': 'Lead ML Engineer',
            'description': 'Build ML platform for clinical predictions'
        }
    ]
    
    print("🚀 Differentiation Engine Demo")
    print("=" * 60)
    
    for job in test_jobs:
        print(f"\n📧 Creating memorable application for: {job['company']}")
        memorable = engine.create_memorable_email(job)
        
        print(f"\nSubject: {memorable['subject']}")
        print(f"\nKey differentiators:")
        for element in memorable['memorable_elements']:
            print(f"  • {element}")
        
        print(f"\nOpening lines:")
        print(memorable['body'].split('\n\n')[1][:200] + "...")
        print("-" * 60)


if __name__ == "__main__":
    demonstrate_differentiation()