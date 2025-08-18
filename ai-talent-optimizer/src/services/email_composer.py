"""
Email Composer Service
Creates authentic, sentimental, and honest email templates
"""

import logging
import random
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class EmailComposer:
    """Generate authentic and personalized email templates"""
    
    def __init__(self, templates_dir: str = "templates/email"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Load templates
        self.subject_templates = self._load_subject_templates()
        self.opening_templates = self._load_opening_templates()
        self.connection_templates = self._load_connection_templates()
        self.value_templates = self._load_value_templates()
        self.closing_templates = self._load_closing_templates()
        
    def _load_subject_templates(self) -> List[str]:
        """Load subject line templates - honest and personal"""
        return [
            "Genuinely excited about {company}'s {recent_achievement}",
            "10 years at Humana + passion for {company_focus}",
            "Your {recent_news} inspired me to reach out",
            "{position} role - Healthcare AI experience from Humana",
            "Re: {position} - Built similar at Fortune 50 scale",
            "Louisville-based engineer interested in {company}",
            "From healthcare compliance to {company_mission}",
            "Your team's work on {product} resonates with me",
            "Applied AI at Humana - excited about {company}",
            "{name}, your post about {topic} inspired this application"
        ]
    
    def _load_opening_templates(self) -> List[str]:
        """Load opening paragraph templates"""
        return [
            "Hi {first_name},\n\nI just read about {company_event}, and it immediately reminded me of a similar challenge we solved at Humana. The parallels are striking, and I had to reach out.",
            
            "Hi {first_name},\n\nAfter 10 years at Humana building AI systems for healthcare, {company}'s mission to {company_mission} feels like the natural next step in my journey.",
            
            "Hi {first_name},\n\nI've been following {company}'s journey since {milestone}, and your approach to {approach} aligns perfectly with the systems I've been building.",
            
            "Hi {first_name},\n\nYour recent {announcement} caught my attention - we implemented something remarkably similar that saved $1.2M annually.",
            
            "Hi {first_name},\n\nI'm writing from Louisville where I've spent the last decade transforming healthcare operations. {company}'s work in {field} represents exactly the kind of challenge I'm passionate about.",
            
            "Hi {first_name},\n\nI discovered {company} while researching {topic}, and I'm genuinely impressed by your approach. It mirrors the philosophy I've applied building AI systems at scale.",
            
            "Hi {first_name},\n\nThe {position} role at {company} feels like it was written for my exact background - 10 years in healthcare tech, deep domain knowledge, and a passion for {focus_area}.",
            
            "Hi {first_name},\n\nI'm reaching out because {company}'s commitment to {value} resonates deeply with me. I've built my career around similar principles in Fortune 50 environments.",
            
            "Hi {first_name},\n\nWhile researching companies actually making a difference in {industry}, {company} stood out. Your innovative approach is exactly what drew me to this field.",
            
            "Hi {first_name},\n\nI've been quietly building AI systems for a decade, but {company}'s recent {development} made me realize it's time to bring this experience to a more innovative environment."
        ]
    
    def _load_connection_templates(self) -> List[str]:
        """Load connection/relevance paragraphs"""
        return [
            "I architected a privacy-first AI platform managing enterprise-scale systems across multiple teams. What excites me about {company} is the opportunity to apply this proven experience to help scale your operations.",
            
            "My work orchestrating 7 specialized LLMs through the Mirador system directly relates to {company}'s needs in {area}. The difference is you're pushing boundaries I can only dream about in a Fortune 50 environment.",
            
            "I've spent years ensuring 100% regulatory compliance while innovating - a balance I know {company} values as you scale {product}. This unique perspective could help navigate similar challenges.",
            
            "The $1.2M in savings I delivered through automation came from deeply understanding both the technical and human sides of complex systems. {company}'s human-centered approach to {area} speaks to this same philosophy.",
            
            "What sets me apart isn't just the technical skills - it's 10 years of building AI in one of the most regulated industries. For {company}'s work in {field}, this experience navigating compliance while innovating is invaluable.",
            
            "I built AI systems from scratch, growing from manual processes to automated intelligence. {company} is at a similar inflection point with {product}, and I know exactly how to scale it.",
            
            "My experience spans both enterprise and startup (Mightily) environments. I understand the speed {company} needs while maintaining the reliability your customers expect.",
            
            "Beyond my day job, I've built passion projects like FretForge (guitar learning platform) and security tools achieving 95% accuracy. This shows the creativity and initiative I'd bring to {company}.",
            
            "Having managed 1,000+ deployments with zero critical defects, I understand the reliability {company} needs as you scale {service} to millions of users.",
            
            "The healthcare domain expertise combined with my personal AI projects (check my GitHub) gives me a unique lens for {company}'s challenges in {area}."
        ]
    
    def _load_value_templates(self) -> List[str]:
        """Load value proposition paragraphs"""
        return [
            "I can help {company} with:\n• Scaling AI systems from prototype to production (done it with 86k+ files)\n• Ensuring compliance without sacrificing innovation (100% track record)\n• Building with a privacy-first approach (critical for {industry})",
            
            "Specifically for the {position} role, I bring:\n• Proven ability to deliver measurable ROI ($1.2M at Humana)\n• Deep healthcare domain knowledge\n• Hands-on experience with LLM orchestration and vector databases",
            
            "What I'd contribute to {company}:\n• Enterprise-grade engineering practices from Fortune 50\n• Startup agility from Mightily experience  \n• Fresh perspective from someone who's built in constraints",
            
            "Three reasons I'm ideal for {company}:\n1. I've already solved similar problems at scale\n2. My healthcare background aligns with {company_focus}\n3. I'm genuinely passionate about {mission} (check my GitHub projects)",
            
            "How I'd impact {company} immediately:\n• Apply lessons from 1,000+ production deployments\n• Bring tested automation frameworks\n• Share insights from building AI in highly regulated spaces",
            
            "My unique value to {company}:\n• Technical depth (117 Python modules in production)\n• Domain expertise (10 years healthcare)\n• Proven innovation within constraints",
            
            "I'd help {company} avoid the pitfalls I've navigated:\n• Scaling without breaking compliance\n• Automating without losing human touch\n• Innovating within regulatory frameworks",
            
            "For {company}'s next phase, you need someone who's:\n• Built at enterprise scale ✓\n• Maintained startup speed ✓  \n• Delivered measurable results ✓",
            
            "I see {company} facing challenges I've solved:\n• Privacy-first architecture at scale\n• AI adoption in traditional industries\n• Balancing innovation with reliability",
            
            "My experience directly addresses {company}'s needs:\n• Scalable AI architecture (did this at Humana)\n• Healthcare compliance (built this in Mirador)\n• Production reliability (proven in production)"
        ]
    
    def _load_closing_templates(self) -> List[str]:
        """Load closing paragraphs"""
        return [
            "I've attached my resume highlighting relevant experience. Would love to discuss how my background could accelerate {company}'s mission.\n\nWarmly,\nMatthew",
            
            "The attached resume provides details, but I'd prefer to show you what I can build. Happy to share my GitHub projects or do a technical deep-dive.\n\nBest,\nMatthew",
            
            "I've included my resume for reference, though my real proof is in the systems I've built. Let's talk about how I can contribute to {company}'s next chapter.\n\nLooking forward,\nMatthew",
            
            "Attached is my resume with full details. I'm ready to bring 10 years of healthcare AI experience to {company}.\n\nExcited to connect,\nMatthew",
            
            "Please see the attached resume for my technical background. More importantly, I'm genuinely excited about {company}'s mission and ready to contribute.\n\nBest regards,\nMatthew",
            
            "I've attached my resume, but I'd rather show than tell. Happy to walk through how I'd approach {company}'s current challenges.\n\nThanks for considering,\nMatthew",
            
            "The attached resume covers my experience, but I'm most excited to discuss {company}'s future and how I can help build it.\n\nHope to talk soon,\nMatthew",
            
            "Resume attached with formal details. What matters is I've solved these problems before and I'm ready to do it again with {company}.\n\nBest,\nMatthew",
            
            "I've included my resume highlighting relevant projects. Would love to discuss how my unique background fits {company}'s needs.\n\nSincerely,\nMatthew",
            
            "Attached is my resume, but my GitHub tells the real story. Ready to bring this experience to {company}.\n\nLooking forward to connecting,\nMatthew"
        ]
    
    def compose_email(self, job_data: Dict, company_research: Optional[Dict] = None) -> Dict:
        """Compose a complete email for a job application"""
        
        # Extract job details
        company = job_data.get('company', 'your company')
        position = job_data.get('position', 'this role')
        
        # Use research data if available
        if company_research:
            recent_news = company_research.get('recent_news', 'recent developments')
            company_mission = company_research.get('mission', 'your mission')
            company_focus = company_research.get('focus', 'your focus area')
            recent_achievement = company_research.get('achievement', 'recent success')
        else:
            recent_news = "recent developments"
            company_mission = "your mission"  
            company_focus = "your technology"
            recent_achievement = "recent progress"
        
        # Determine first name (try to extract from email or use default)
        email_to = job_data.get('email_to', job_data.get('company_email', ''))
        first_name = self._extract_first_name(email_to, company)
        
        # Create template variables
        variables = {
            'company': company,
            'position': position,
            'first_name': first_name,
            'recent_news': recent_news,
            'company_mission': company_mission,
            'company_focus': company_focus,
            'recent_achievement': recent_achievement,
            'company_event': recent_news,
            'milestone': 'your founding',
            'approach': company_focus,
            'announcement': recent_news,
            'field': self._determine_field(position),
            'topic': company_focus,
            'value': 'innovation',
            'industry': self._determine_industry(company),
            'specific_approach': company_focus,
            'development': recent_achievement,
            'company_challenge': f"scaling {company_focus}",
            'area': company_focus,
            'product': 'your platform',
            'challenge': 'regulatory compliance',
            'stakeholders': 'users',
            'service': 'your service',
            'target_scale': 'millions of users',
            'mission': company_mission,
            'specific_need_1': 'Scalable AI architecture',
            'specific_need_2': 'Healthcare compliance',
            'specific_need_3': 'Production reliability',
            'name': first_name
        }
        
        # Select templates
        subject_template = random.choice(self.subject_templates)
        opening_template = random.choice(self.opening_templates)
        connection_template = random.choice(self.connection_templates)
        value_template = random.choice(self.value_templates)
        closing_template = random.choice(self.closing_templates)
        
        # Format templates
        try:
            subject = subject_template.format(**variables)
        except:
            subject = f"{position} - Matthew Scott (10 years at Humana)"
        
        try:
            opening = opening_template.format(**variables)
            connection = connection_template.format(**variables)
            value = value_template.format(**variables)
            closing = closing_template.format(**variables)
        except Exception as e:
            logger.warning(f"Template formatting issue: {e}, using defaults")
            opening = f"Hi {first_name},\n\nI'm interested in the {position} role at {company}."
            connection = f"With 10 years at Humana building AI systems, I can contribute immediately."
            value = f"I bring proven experience in healthcare AI and enterprise-scale development."
            closing = f"Resume attached. Looking forward to discussing.\n\nBest,\nMatthew"
        
        # Combine into full email
        body = f"{opening}\n\n{connection}\n\n{value}\n\n{closing}"
        
        # Add signature
        signature = "\n\n--\nMatthew Scott\nmatthewdscott7@gmail.com\n(502) 345-0525\nlinkedin.com/in/mscott77\ngithub.com/guitargnar"
        
        full_body = body + signature
        
        return {
            'subject': subject,
            'body': full_body,
            'to': email_to or f"careers@{company.lower().replace(' ', '')}.com",
            'personalization_score': self._calculate_personalization(company_research),
            'template_version': 'v2_authentic',
            'generated_at': datetime.now().isoformat()
        }
    
    def _extract_first_name(self, email: str, company: str) -> str:
        """Try to extract first name from email or use appropriate default"""
        if email and '@' in email:
            # Try to extract name from email
            local_part = email.split('@')[0]
            # Common patterns: firstname.lastname, firstname_lastname, firstnamelastname
            for separator in ['.', '_', '-']:
                if separator in local_part:
                    potential_name = local_part.split(separator)[0]
                    if len(potential_name) > 2:
                        return potential_name.capitalize()
        
        # Use Hiring Manager or Team as fallback
        return "Hiring Team"
    
    def _determine_field(self, position: str) -> str:
        """Determine field based on position"""
        position_lower = position.lower()
        
        if any(term in position_lower for term in ['ai', 'ml', 'machine learning', 'data scientist']):
            return "AI/ML"
        elif any(term in position_lower for term in ['principal', 'staff', 'architect']):
            return "technical leadership"
        elif any(term in position_lower for term in ['backend', 'frontend', 'full stack']):
            return "software engineering"
        else:
            return "technology"
    
    def _determine_industry(self, company: str) -> str:
        """Determine industry based on company"""
        company_lower = company.lower()
        
        healthcare_companies = ['tempus', 'cedar', 'zocdoc', 'oscar', 'doximity']
        if any(comp in company_lower for comp in healthcare_companies):
            return "healthcare technology"
        
        ai_companies = ['openai', 'anthropic', 'hugging', 'cohere', 'scale']
        if any(comp in company_lower for comp in ai_companies):
            return "artificial intelligence"
        
        return "technology"
    
    def _calculate_personalization(self, research: Optional[Dict]) -> int:
        """Calculate personalization score"""
        if not research:
            return 60
        
        score = 60
        if research.get('recent_news'):
            score += 10
        if research.get('mission'):
            score += 10
        if research.get('focus'):
            score += 10
        if research.get('achievement'):
            score += 10
        
        return min(score, 100)
    
    def save_template(self, email_data: Dict, filename: str) -> str:
        """Save email template to file"""
        filepath = self.templates_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"TO: {email_data['to']}\n")
            f.write(f"SUBJECT: {email_data['subject']}\n")
            f.write(f"PERSONALIZATION: {email_data['personalization_score']}%\n")
            f.write("="*50 + "\n\n")
            f.write(email_data['body'])
        
        logger.info(f"Saved email template to {filepath}")
        return str(filepath)

def generate_sample_emails():
    """Generate sample emails for testing"""
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    composer = EmailComposer()
    
    # Sample jobs
    sample_jobs = [
        {
            'company': 'Anthropic',
            'position': 'Senior AI Engineer',
            'company_email': 'careers@anthropic.com'
        },
        {
            'company': 'Tempus',
            'position': 'Principal Engineer',
            'company_email': 'careers@tempus.com'
        },
        {
            'company': 'OpenAI',
            'position': 'ML Infrastructure Engineer',
            'company_email': 'careers@openai.com'
        }
    ]
    
    # Sample research data
    research = {
        'recent_news': 'Series C funding announcement',
        'mission': 'democratize AI for everyone',
        'focus': 'responsible AI development',
        'achievement': '$500M valuation'
    }
    
    print("\n" + "="*50)
    print("✉️ Email Template Generation")
    print("="*50)
    
    for job in sample_jobs:
        email = composer.compose_email(job, research)
        filename = f"{job['company'].lower()}_{datetime.now().strftime('%Y%m%d')}.txt"
        filepath = composer.save_template(email, filename)
        
        print(f"\n📧 {job['company']} - {job['position']}")
        print(f"Subject: {email['subject']}")
        print(f"Personalization: {email['personalization_score']}%")
        print(f"Saved to: {Path(filepath).name}")
    
    return True

if __name__ == "__main__":
    generate_sample_emails()