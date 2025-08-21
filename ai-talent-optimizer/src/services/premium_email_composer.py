"""
Premium Email Composer - High-quality, researched, personalized emails
"""

import random
from typing import Dict, List, Optional
from datetime import datetime

class PremiumEmailComposer:
    """Generate A+ quality personalized emails with research and specificity"""
    
    def __init__(self):
        self.company_research = self._load_company_research()
        self.role_templates = self._load_role_specific_templates()
    
    def _load_company_research(self) -> Dict:
        """Company-specific research and talking points"""
        return {
            'Scale AI': {
                'recent_news': 'Series F funding at $13.8B valuation',
                'products': ['Data Engine', 'Nucleus', 'RLHF platform'],
                'leaders': ['Alexandr Wang (CEO)', 'Lucy Guo (co-founder)'],
                'mission': 'accelerating AI development through better data',
                'challenges': 'scaling data quality at enterprise level',
                'culture': 'move fast, high ownership, technical excellence'
            },
            'Figma': {
                'recent_news': 'Adobe acquisition fell through, staying independent',
                'products': ['Figma Design', 'FigJam', 'Dev Mode'],
                'leaders': ['Dylan Field (CEO)', 'Evan Wallace (CTO)'],
                'mission': 'make design accessible and collaborative',
                'challenges': 'scaling real-time collaboration infrastructure',
                'culture': 'design-first, collaborative, playful'
            },
            'Plaid': {
                'recent_news': 'expanded to 8,000+ financial institutions',
                'products': ['Link', 'Auth', 'Balance', 'Identity'],
                'leaders': ['Zach Perret (CEO)', 'William Hockey (CTO)'],
                'mission': 'democratize financial services through technology',
                'challenges': 'maintaining bank relationships while scaling',
                'culture': 'mission-driven, technical rigor, transparency'
            },
            'Zocdoc': {
                'recent_news': 'IPO preparation and national expansion',
                'products': ['Patient booking platform', 'Provider tools'],
                'leaders': ['Oliver Kharraz (CEO/Founder)'],
                'mission': 'give power to the patient in healthcare',
                'challenges': 'healthcare system integration complexity',
                'culture': 'patient-first, data-driven, healthcare expertise'
            }
        }
    
    def _load_role_specific_templates(self) -> Dict:
        """Templates specific to role types"""
        return {
            'engineering_manager': {
                'opening': "I noticed your {team_name} team is scaling rapidly. Having grown engineering teams from 5 to 50+ at Humana while maintaining velocity, I understand the challenges you're facing.",
                'value_prop': "I bring a unique combination: technical depth (built systems processing 1M+ requests/day), people leadership (managed 12+ engineers), and healthcare domain expertise that translates directly to {industry} challenges.",
                'specific_skills': ['team scaling', 'technical architecture', 'stakeholder management', 'agile transformation']
            },
            'senior_engineer': {
                'opening': "Your work on {technical_challenge} caught my attention. I recently solved a similar distributed systems challenge at Humana using {relevant_tech}.",
                'value_prop': "With 10 years building production ML systems, I can contribute immediately to {company}'s {product}. My recent work orchestrating 7 LLMs for decision-making directly applies to your scale challenges.",
                'specific_skills': ['Python expert', 'distributed systems', 'ML ops', 'system design']
            },
            'ai_ml_engineer': {
                'opening': "I've been following {company}'s approach to {ml_approach}. Your recent paper on {topic} aligns perfectly with the ensemble methods I implemented at Humana.",
                'value_prop': "I don't just implement models - I build production ML systems. At Humana, my predictive analytics framework improved risk detection by 20% while maintaining 100% regulatory compliance.",
                'specific_skills': ['PyTorch', 'LLM fine-tuning', 'MLOps', 'vector databases']
            },
            'platform_engineer': {
                'opening': "Building platforms that developers love is my passion. Your team's focus on {platform_aspect} resonates with the developer experience improvements I led at Humana.",
                'value_prop': "I've managed infrastructure supporting 86K+ files and 117 Python modules with zero downtime. I understand both the technical complexity and human factors in platform engineering.",
                'specific_skills': ['Kubernetes', 'CI/CD', 'infrastructure as code', 'monitoring']
            }
        }
    
    def compose_premium_email(self, job: Dict) -> Dict:
        """Generate a premium quality email with research and personalization"""
        
        company = job.get('company', 'your company')
        position = job.get('position', 'this position')
        
        # Get company research
        research = self.company_research.get(company, {})
        
        # Determine role type
        role_type = self._determine_role_type(position)
        template = self.role_templates.get(role_type, self.role_templates['senior_engineer'])
        
        # Generate personalized subject
        subject = self._generate_premium_subject(company, position, research)
        
        # Generate premium body
        body = self._generate_premium_body(company, position, research, template)
        
        return {
            'subject': subject,
            'body': body,
            'quality_score': self._calculate_quality_score(body, research),
            'personalization_level': 'high',
            'research_included': bool(research)
        }
    
    def _determine_role_type(self, position: str) -> str:
        """Determine the type of role from position title"""
        position_lower = position.lower()
        
        if any(term in position_lower for term in ['manager', 'lead', 'director', 'head']):
            return 'engineering_manager'
        elif any(term in position_lower for term in ['ml', 'machine learning', 'ai', 'artificial']):
            return 'ai_ml_engineer'
        elif any(term in position_lower for term in ['platform', 'infrastructure', 'devops', 'sre']):
            return 'platform_engineer'
        else:
            return 'senior_engineer'
    
    def _generate_premium_subject(self, company: str, position: str, research: Dict) -> str:
        """Generate a high-quality, specific subject line"""
        
        if research:
            # Company-specific subjects
            subjects = [
                f"Re: {position} - My experience with {research.get('challenges', 'similar challenges')}",
                f"{research.get('recent_news', 'Your growth')} + my healthcare AI experience",
                f"Excited about {research.get('products', ['your product'])[0]} - relevant experience from Humana",
                f"{company}'s {research.get('mission', 'mission')} resonates - 10 years building compliant AI"
            ]
        else:
            # Generic but better subjects
            subjects = [
                f"Re: {position} - Scaled similar systems at Fortune 50",
                f"{position} role - Directly relevant experience",
                f"Your {position} opening - Let's discuss",
                f"Application: {position} - Matthew Scott"
            ]
        
        return random.choice(subjects)
    
    def _generate_premium_body(self, company: str, position: str, research: Dict, template: Dict) -> str:
        """Generate a premium email body with research and specificity"""
        
        # Determine greeting
        greeting = "Hi Hiring Team"  # Will be replaced with actual name when available
        
        # Opening with research
        if research:
            # More natural, varied openings
            openings = [
                f"I saw the news about {company}'s {research.get('recent_news', 'recent growth')} - congratulations! "
                f"It made me realize how well my experience scaling ML systems at Humana aligns with your current challenges.",
                
                f"Your team's work on {research.get('products', ['your platform'])[0]} caught my attention. "
                f"I've been solving similar problems at Humana, and I'd love to bring that experience to {company}.",
                
                f"I've been tracking {company}'s journey, especially {research.get('recent_news', 'your growth')}. "
                f"My decade building enterprise AI feels directly relevant to where you're headed.",
                
                f"After reading about {research.get('recent_news', 'your expansion')}, I had to reach out. "
                f"The challenges you're tackling are exactly what energizes me as an engineer."
            ]
            import random
            opening = random.choice(openings)
        else:
            opening = template['opening'].format(
                team_name=f"{company} engineering",
                technical_challenge="scaling challenges",
                relevant_tech="distributed Python systems",
                company=company,
                product="platform",
                ml_approach="production ML",
                topic="ML systems",
                platform_aspect="developer experience"
            )
        
        # More conversational middle section
        middle_options = [
            f"\n\nHere's why I'm a strong fit:\n"
            f"• I've tackled {research.get('challenges', 'similar scaling challenges')}\n"
            f"• My team delivered $1.2M in savings - I know how to drive real impact\n"
            f"• Deep expertise in {', '.join(template.get('specific_skills', ['Python', 'ML'])[:2])}\n",
            
            f"\n\nA few relevant highlights from my background:\n"
            f"• Built ML systems processing millions of requests daily\n"
            f"• Led cross-functional teams through complex technical migrations\n"
            f"• Passionate about {research.get('culture', 'technical excellence').split(',')[0]}\n",
            
            f"\n\nWhat caught my eye about this role:\n"
            f"• You need someone who's scaled {research.get('challenges', 'complex systems')} - I've done it\n"
            f"• The technical stack ({', '.join(template.get('specific_skills', ['Python'])[:2])}) is my sweet spot\n"
            f"• {company}'s culture of {research.get('culture', 'innovation').split(',')[0]} matches my approach\n"
        ]
        
        middle = random.choice(middle_options) if research else middle_options[0]
        
        # Specific connection to role
        connection = f"\n\nSpecifically for the {position} role, "
        
        role_type = self._determine_role_type(position)
        if role_type == 'engineering_manager':
            connection += "my experience scaling teams from 5 to 50+ while maintaining technical excellence "
            connection += f"maps directly to {company}'s current growth phase."
        elif role_type == 'ai_ml_engineer':
            connection += "my work orchestrating 7 specialized LLMs for enterprise decision-making "
            connection += f"demonstrates the production ML expertise {company} needs."
        else:
            connection += "my track record of building and scaling production systems "
            connection += f"would contribute immediately to {company}'s technical challenges."
        
        # More natural, varied closings
        closing_options = [
            f"\n\nI'd love to chat about how my experience could help {company} "
            f"tackle your next set of challenges. Are you available for a quick call next week?",
            
            f"\n\nWould you be open to a conversation about how my background aligns "
            f"with {company}'s roadmap? I'm particularly interested in {research.get('products', ['your platform'])[0] if research else 'your technical challenges'}.",
            
            f"\n\nI'm genuinely excited about what {company} is building. "
            f"Let's connect to discuss how I could contribute to your team's success.",
            
            f"\n\nI'd appreciate the chance to learn more about your team's priorities "
            f"and share how my experience could help achieve them. When works for you?"
        ]
        
        closing = random.choice(closing_options)
        closing += "\n\nBest,\nMatthew"
        
        # Add signature
        signature = "\n\n--\nMatthew Scott\nmatthewdscott7@gmail.com\n(502) 345-0525\nlinkedin.com/in/mscott77\ngithub.com/guitargnar"
        
        return greeting + ",\n\n" + opening + middle + connection + closing + signature
    
    def _calculate_quality_score(self, body: str, research: Dict) -> float:
        """Calculate quality score of the email"""
        score = 0.5  # Base score
        
        # Check for research elements
        if research:
            score += 0.2
        
        # Check for specificity
        if any(word in body for word in ['specifically', 'particular', 'exactly']):
            score += 0.1
        
        # Check for quantified results
        if '$' in body or '%' in body:
            score += 0.1
        
        # Check for technical specificity
        tech_terms = ['Python', 'ML', 'distributed', 'Kubernetes', 'PyTorch']
        if sum(1 for term in tech_terms if term in body) >= 2:
            score += 0.1
        
        return min(score, 1.0)


def upgrade_email_quality(job: Dict) -> Dict:
    """Generate a premium quality email for a job"""
    composer = PremiumEmailComposer()
    return composer.compose_premium_email(job)


if __name__ == "__main__":
    # Test with different companies
    test_jobs = [
        {'company': 'Scale AI', 'position': 'Senior ML Engineer'},
        {'company': 'Figma', 'position': 'Engineering Manager'},
        {'company': 'Plaid', 'position': 'Platform Engineer'},
        {'company': 'Zocdoc', 'position': 'AI/ML Engineer'}
    ]
    
    print("=== PREMIUM EMAIL EXAMPLES ===\n")
    
    for job in test_jobs:
        email = upgrade_email_quality(job)
        print(f"Company: {job['company']}")
        print(f"Position: {job['position']}")
        print(f"Subject: {email['subject']}")
        print(f"Quality Score: {email['quality_score']:.0%}")
        print("\nBody Preview:")
        print(email['body'][:500] + "...")
        print("\n" + "="*50 + "\n")