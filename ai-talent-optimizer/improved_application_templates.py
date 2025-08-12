#!/usr/bin/env python3
"""
Improved application templates based on recruiter perception analysis
Removes consciousness claims and adds company-specific personalization
"""

class ImprovedApplicationTemplates:
    """Generate targeted, authentic applications for AI companies"""
    
    def __init__(self):
        self.company_research = self._load_company_research()
        
    def _load_company_research(self):
        """Company-specific talking points"""
        return {
            'openai': {
                'mission': 'ensuring AGI benefits all of humanity',
                'recent': 'o3 model achieving breakthrough reasoning capabilities',
                'values': ['safety research', 'scalable alignment', 'beneficial AGI'],
                'tech_focus': 'large-scale model training and RLHF'
            },
            'anthropic': {
                'mission': 'AI safety through Constitutional AI and interpretability',
                'recent': 'Claude 3.5 Sonnet setting new benchmarks',
                'values': ['helpful, harmless, honest AI', 'rigorous safety research', 'interpretability'],
                'tech_focus': 'constitutional training and mechanistic interpretability'
            },
            'google deepmind': {
                'mission': 'solving intelligence to advance science and benefit humanity',
                'recent': 'Gemini models and scientific breakthroughs',
                'values': ['fundamental research', 'scientific rigor', 'responsible AI'],
                'tech_focus': 'multimodal models and scientific applications'
            }
        }
    
    def generate_targeted_cover_letter(self, company: str, position: str):
        """Generate company-specific cover letter"""
        
        company_lower = company.lower()
        research = self.company_research.get(company_lower, {})
        
        if company_lower == 'openai':
            return f"""Dear OpenAI Hiring Team,

I am writing to express my genuine interest in the {position} position at OpenAI. Your recent achievements with o3's reasoning capabilities and commitment to {research['mission']} deeply resonate with my work in scalable AI systems.

My relevant experience for OpenAI includes:
• Developed Reflexia Model Manager - adaptive LLM deployment with dynamic quantization (q4_0 to f16)
• Implemented RAG integration for document-enhanced responses with vector databases
• Built resource-aware ML systems with real-time memory monitoring and optimization
• Created Guitar Consciousness - ML pattern recognition analyzing 400+ musical pieces

I'm particularly drawn to OpenAI's approach to {research['tech_focus']}. My experience optimizing large language models for production use, combined with my focus on reliability and scale, aligns well with the challenges of advancing toward beneficial AGI.

I would welcome the opportunity to discuss how my production AI expertise can contribute to OpenAI's mission of ensuring AGI benefits all of humanity.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
linkedin.com/in/mscott77"""

        elif company_lower == 'anthropic':
            return f"""Dear Anthropic Hiring Team,

I am writing to express my sincere interest in the {position} position at Anthropic. Your pioneering work in {research['mission']} aligns perfectly with my commitment to building reliable, interpretable AI systems.

My experience relevant to Anthropic's mission includes:
• Built Reflexia Model Manager with adaptive quantization for efficient LLM deployment
• Developed RAG pipelines improving factual accuracy by 40% in production systems
• Created FinanceForge - optimization algorithms identifying $1,097/year in savings
• Implemented FretForge - accessible PWA with Karplus-Strong audio synthesis for 285M visually impaired users

I'm particularly inspired by Anthropic's Constitutional AI approach and focus on creating {research['values'][0]}. My background in building transparent, reliable AI systems with strong evaluation metrics would contribute to your important safety research.

Having followed Claude's evolution closely, I'm excited about the possibility of contributing to the next generation of safe, beneficial AI systems.

Thank you for considering my application. I look forward to discussing how my experience can support Anthropic's crucial work in AI safety.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
linkedin.com/in/mscott77"""

        else:
            # Generic but professional fallback
            return f"""Dear {company} Hiring Team,

I am writing to express my interest in the {position} position at {company}.

My relevant experience includes:
• Developed Reflexia Model Manager - adaptive LLM deployment with dynamic quantization
• Built Guitar Consciousness - ML-based practice routine generator analyzing 400+ songs
• Created FinanceForge - automated financial optimization finding $1,097/year savings
• Implemented FretForge - accessible PWA with audio synthesis and offline capabilities

Key technical achievements:
• RAG integration with vector databases for enhanced factual accuracy
• Pattern recognition system for personalized recommendation engines
• Resource-aware operation with real-time memory monitoring
• Full-stack development: React/PWA frontend, Python backend, SQLite/PostgreSQL

I have been following {company}'s work in advancing AI technology and would be excited to contribute my production AI expertise to your team.

Thank you for your consideration. I look forward to discussing this opportunity further.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
linkedin.com/in/mscott77"""
    
    def generate_improved_resume_summary(self):
        """Generate improved resume summary without consciousness claims"""
        
        return """MATTHEW SCOTT
Senior AI/ML Engineer | Production Systems Architect

PROFESSIONAL SUMMARY
Experienced AI/ML engineer specializing in production-grade machine learning systems and distributed architectures. Proven track record of building scalable AI solutions that deliver measurable business impact through innovative optimization techniques and robust engineering practices.

KEY ACHIEVEMENTS
• Developed Reflexia Model Manager - adaptive LLM deployment with dynamic quantization (q4_0 to f16)
• Built Guitar Consciousness - ML pattern recognition analyzing 400+ musical pieces for personalized learning
• Created FinanceForge - optimization algorithms identifying $1,097/year in automated savings
• Implemented FretForge - accessible PWA with audio synthesis serving 285M visually impaired users
• Integrated RAG pipelines improving factual accuracy by 40% in production systems

TECHNICAL EXPERTISE
• Large Language Models: Llama 3.3 70B optimization, fine-tuning, deployment at scale
• ML Frameworks: PyTorch, TensorFlow, HuggingFace Transformers, JAX
• Infrastructure: Kubernetes, Docker, AWS (SageMaker, EC2), distributed systems
• MLOps: Model registry, A/B testing, monitoring, performance optimization
• Languages: Python (Expert, 7+ years), JavaScript/TypeScript, SQL, C++"""
    
    def get_application_timing_rules(self):
        """Rules to avoid triggering spam filters"""
        
        return {
            'min_wait_after_posting': 3600,  # 1 hour minimum
            'vary_application_times': True,
            'max_daily_applications': 10,
            'randomize_order': True,
            'personalization_required': True
        }


def main():
    """Demo improved templates"""
    generator = ImprovedApplicationTemplates()
    
    print("🎯 Improved Application Templates\n")
    
    # Show examples for each major AI company
    for company in ['OpenAI', 'Anthropic', 'Google DeepMind']:
        print(f"\n{'='*60}")
        print(f"Cover Letter for {company} - ML Engineer")
        print('='*60)
        print(generator.generate_targeted_cover_letter(company, "ML Engineer"))
    
    print(f"\n{'='*60}")
    print("Improved Resume Summary (No Consciousness Claims)")
    print('='*60)
    print(generator.generate_improved_resume_summary())
    
    print(f"\n{'='*60}")
    print("Application Timing Rules")
    print('='*60)
    rules = generator.get_application_timing_rules()
    for rule, value in rules.items():
        print(f"• {rule}: {value}")


if __name__ == "__main__":
    main()