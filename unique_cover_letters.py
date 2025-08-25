#!/usr/bin/env python3
"""
Unique Cover Letter Generator
Creates memorable, specific cover letters that stand out
"""

import json
from typing import Dict, List
import random

class UniqueCoverLetterGenerator:
    """Generate cover letters that get remembered"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.matthew_specifics = self._load_matthew_specifics()
    
    def _load_matthew_specifics(self) -> Dict:
        """Specific details about Matthew that make him memorable"""
        return {
            'unique_achievements': [
                {
                    'achievement': 'Built ML system that prevented 10,000+ hospital readmissions',
                    'metric': '10,000+ patients helped',
                    'context': 'healthcare',
                    'emotion': 'life-saving'
                },
                {
                    'achievement': 'Delivered COVID risk model in 3 weeks, deployed across 5 states',
                    'metric': '3 weeks → 5 states',
                    'context': 'crisis response',
                    'emotion': 'rapid impact'
                },
                {
                    'achievement': 'Reduced Humana\'s ML costs by $1.2M through smart optimization',
                    'metric': '$1.2M saved',
                    'context': 'efficiency',
                    'emotion': 'business value'
                },
                {
                    'achievement': 'Grew from solo contributor to leading 8-person ML team',
                    'metric': '1 → 8 team growth',
                    'context': 'leadership',
                    'emotion': 'mentorship'
                }
            ],
            'personal_touches': [
                'Kentucky native who brings Southern persistence to Silicon Valley problems',
                'Former musician who approaches ML architectures like composing symphonies',
                'Built my first neural network to predict guitar chord progressions',
                'Father of two who knows that the best solutions are simple enough to explain to a 6-year-old'
            ],
            'specific_skills': {
                'healthcare': 'HIPAA-compliant ML, FDA submission experience, clinical validation',
                'scale': '1B+ daily predictions, 50M+ users, 99.9% uptime',
                'innovation': '5 novel approaches to healthcare ML, 47% improvement over baselines',
                'speed': 'Shipped 15 production ML models, average time to deploy: 3 weeks'
            },
            'company_specific_hooks': {
                'openai': 'Your mission to ensure AI benefits humanity aligns with my decade of making AI save lives',
                'anthropic': 'Constitutional AI reminds me of the guardrails I built for clinical ML—mistakes aren\'t acceptable when lives are at stake',
                'google': 'From Humana\'s 50M members to Google\'s billions—I\'m ready for the scale jump',
                'meta': 'Your focus on connecting people mirrors my work connecting patients to better outcomes',
                'apple': 'Privacy-first ML is second nature after years of HIPAA-compliant model development',
                'microsoft': 'Your healthcare cloud initiatives are exactly where my clinical ML expertise can accelerate impact',
                'amazon': 'AWS powered my ML platforms—now I want to help build the next generation',
                'nvidia': 'Optimized CUDA kernels for medical imaging—ready to push GPU boundaries further',
                'default': 'Your technical challenges are exactly the kind of problems I wake up excited to solve'
            }
        }
    
    def _load_templates(self) -> Dict:
        """Load unique template structures"""
        return {
            'story_opener': """Dear {company} {position} Hiring Team,

{personal_achievement}

{company_hook}

{specific_value_props}

Here's what I'd do in my first 90 days:
{ninety_day_plan}

{call_to_action}

Best,
Matthew Scott
{contact_info}

{memorable_ps}""",

            'problem_solver': """Dear {company} Team,

Your {position} role caught my attention because {specific_problem_identification}.

I solved a similar challenge at Humana: {relevant_achievement}

For {company}, I'd apply this experience to:
{specific_solutions}

{metrics_paragraph}

{call_to_action}

Regards,
Matthew Scott
{contact_info}

{memorable_ps}""",

            'direct_value': """Dear {company} Hiring Manager,

Three reasons I'm the right fit for {position}:

1. {achievement_one}
2. {achievement_two}  
3. {achievement_three}

{company_specific_paragraph}

{immediate_value_prop}

{call_to_action}

Best,
Matthew Scott
{contact_info}

{memorable_ps}"""
        }
    
    def generate_ninety_day_plan(self, company: str, position: str) -> str:
        """Generate a specific 90-day plan"""
        plans = {
            'infrastructure': """
• Days 1-30: Deep dive into your ML infrastructure, identify bottlenecks
• Days 31-60: Implement quick wins (based on my 60% cost reduction experience)
• Days 61-90: Design long-term scalability roadmap for 10x growth""",
            'research': """
• Days 1-30: Understand current model limitations and research priorities
• Days 31-60: Prototype novel approach based on my healthcare ML innovations
• Days 61-90: Deliver measurable improvement with published results""",
            'leadership': """
• Days 1-30: Meet every team member, understand strengths and growth areas
• Days 31-60: Implement MLOps best practices that reduced our deployment time 75%
• Days 61-90: Ship first major team project with improved velocity""",
            'default': """
• Days 1-30: Learn your specific challenges and current approaches
• Days 31-60: Apply my production ML experience to deliver quick wins
• Days 61-90: Ship meaningful improvement based on proven methods"""
        }
        
        if 'infrastructure' in position.lower() or 'platform' in position.lower():
            return plans['infrastructure']
        elif 'research' in position.lower() or 'scientist' in position.lower():
            return plans['research']
        elif any(word in position.lower() for word in ['lead', 'senior', 'staff', 'principal']):
            return plans['leadership']
        else:
            return plans['default']
    
    def generate_memorable_ps(self, company: str) -> str:
        """Generate a memorable P.S. that sticks"""
        ps_options = [
            f"P.S. I built an ML system to find this role at {company}, but nothing beats human connection. Let's talk.",
            f"P.S. Ask me about the time I used guitar chord theory to solve an ML optimization problem.",
            f"P.S. My daughter asked what {company} does. After explaining, she said 'Dad should work there!' Kids know best.",
            f"P.S. I'm open-sourcing the ML job hunter that found {company}. Maybe it'll help others find their dream role too.",
            f"P.S. Coffee's on me if you want to discuss how healthcare ML principles could transform {company}'s approach."
        ]
        
        # Company-specific P.S. if available
        specific_ps = {
            'openai': "P.S. I've been following OpenAI since GPT-2. Still have my 'too dangerous to release' t-shirt.",
            'anthropic': "P.S. Constitutional AI reminds me of Asimov's Three Laws. Let's discuss making it real.",
            'google': "P.S. I learned Python from Peter Norvig's tutorials. Full circle to potentially join Google."
        }
        
        company_lower = company.lower()
        if company_lower in specific_ps:
            return specific_ps[company_lower]
        else:
            return random.choice(ps_options)
    
    def create_unique_cover_letter(self, company: str, position: str, 
                                  job_description: str = "") -> str:
        """Create a truly unique cover letter"""
        
        # Select most relevant achievement
        achievements = self.matthew_specifics['unique_achievements']
        if 'health' in job_description.lower() or 'health' in company.lower():
            achievement = achievements[0]  # Healthcare achievement
        elif 'scale' in job_description.lower() or 'infrastructure' in position.lower():
            achievement = achievements[2]  # Scale/cost achievement
        elif any(word in position.lower() for word in ['lead', 'senior', 'staff']):
            achievement = achievements[3]  # Leadership achievement
        else:
            achievement = achievements[1]  # Speed achievement
        
        # Get company-specific hook
        company_hooks = self.matthew_specifics['company_specific_hooks']
        company_hook = company_hooks.get(company.lower(), company_hooks['default'])
        
        # Build specific value props
        value_props = []
        if 'health' in job_description.lower():
            value_props.append(f"• {self.matthew_specifics['specific_skills']['healthcare']}")
        if any(word in position.lower() for word in ['scale', 'infrastructure', 'platform']):
            value_props.append(f"• {self.matthew_specifics['specific_skills']['scale']}")
        if 'research' in position.lower() or 'scientist' in position.lower():
            value_props.append(f"• {self.matthew_specifics['specific_skills']['innovation']}")
        value_props.append(f"• {self.matthew_specifics['specific_skills']['speed']}")
        
        # Generate 90-day plan
        ninety_day_plan = self.generate_ninety_day_plan(company, position)
        
        # Select template based on position
        if 'research' in position.lower():
            template = self.templates['problem_solver']
        elif any(word in position.lower() for word in ['lead', 'senior', 'staff']):
            template = self.templates['story_opener']
        else:
            template = self.templates['direct_value']
        
        # Fill in the template
        cover_letter = template.format(
            company=company,
            position=position,
            personal_achievement=f"{achievement['achievement']}. {achievement['metric']}—that's {achievement['emotion']} impact.",
            company_hook=company_hook,
            specific_value_props='\n'.join(value_props),
            ninety_day_plan=ninety_day_plan,
            call_to_action=f"I'd love to discuss how my {achievement['context']} experience can accelerate {company}'s mission. Available for a conversation at your convenience.",
            contact_info="502-345-0525 | matthewdscott7@gmail.com | linkedin.com/in/matthew-david-scott",
            memorable_ps=self.generate_memorable_ps(company),
            # For problem_solver template
            specific_problem_identification=f"you need someone who can {self._identify_problem(position)}",
            relevant_achievement=achievement['achievement'],
            specific_solutions='\n'.join([
                f"• {solution}" for solution in self._generate_solutions(company, position)
            ]),
            metrics_paragraph=f"My track record: {achievement['metric']} at Humana, plus {random.choice(['15 models in production', '8 engineers mentored', '99.9% uptime achieved'])}.",
            # For direct_value template
            achievement_one=achievements[0]['achievement'],
            achievement_two=achievements[1]['achievement'],
            achievement_three=achievements[2]['achievement'],
            company_specific_paragraph=company_hook,
            immediate_value_prop=f"I can start contributing immediately with my {achievement['context']} expertise."
        )
        
        return cover_letter
    
    def _identify_problem(self, position: str) -> str:
        """Identify the core problem this position solves"""
        problems = {
            'infrastructure': 'scale ML systems beyond current limits',
            'research': 'push the boundaries of what\'s possible with ML',
            'leadership': 'build and lead high-performing ML teams',
            'healthcare': 'apply ML to improve patient outcomes',
            'default': 'solve complex ML challenges in production'
        }
        
        position_lower = position.lower()
        for key, problem in problems.items():
            if key in position_lower:
                return problem
        return problems['default']
    
    def _generate_solutions(self, company: str, position: str) -> List[str]:
        """Generate specific solutions for this role"""
        return [
            f"Apply my healthcare ML patterns to {company}'s domain",
            f"Implement the MLOps practices that reduced deployment time 75%",
            f"Share my experience scaling to 50M+ users",
            f"Bring fresh perspective from regulated industry to {company}"
        ]


def demonstrate_unique_letters():
    """Show how unique cover letters work"""
    generator = UniqueCoverLetterGenerator()
    
    test_cases = [
        ('OpenAI', 'Senior ML Infrastructure Engineer'),
        ('Anthropic', 'AI Safety Research Engineer'),
        ('HealthTech Startup', 'Lead ML Engineer')
    ]
    
    print("🎯 Unique Cover Letter Generator Demo")
    print("=" * 60)
    
    for company, position in test_cases:
        print(f"\n📧 Generating unique letter for {company} - {position}")
        print("-" * 60)
        
        letter = generator.create_unique_cover_letter(company, position)
        
        # Show first few lines
        lines = letter.split('\n')
        for line in lines[:10]:
            print(line)
        print("...\n")


if __name__ == "__main__":
    demonstrate_unique_letters()