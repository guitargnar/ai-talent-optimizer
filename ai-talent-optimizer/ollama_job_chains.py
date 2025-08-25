#!/usr/bin/env python3
"""
Ollama Model Chains for AI Talent Optimizer
Maximize your $250/month by chaining multiple AI models for superior results
"""

import subprocess
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

class OllamaJobChains:
    """Chain multiple Ollama models for sophisticated job application workflows"""
    
    def __init__(self):
        self.db_path = "UNIFIED_AI_JOBS.db"
        
    def run_model(self, model: str, prompt: str) -> str:
        """Run a single Ollama model"""
        try:
            result = subprocess.run(
                ['ollama', 'run', model],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=120
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Error running {model}: {e}")
            return ""
    
    def chain_models(self, models: List[str], initial_prompt: str) -> str:
        """Chain multiple models, passing output from one to the next"""
        current_output = initial_prompt
        
        for i, model in enumerate(models):
            print(f"  [{i+1}/{len(models)}] Running {model}...")
            current_output = self.run_model(model, current_output)
            if not current_output:
                print(f"    ⚠️ Model {model} produced no output")
                break
        
        return current_output
    
    # ========================================================================
    # POWER CHAINS - Combine Multiple Models for Superior Results
    # ========================================================================
    
    def ultimate_cover_letter_chain(self, company: str, role: str, job_description: str) -> str:
        """
        Chain 1: Ultimate Cover Letter Generator
        Uses 4+ models to create exceptional personalized content
        """
        print(f"\n🔗 ULTIMATE COVER LETTER CHAIN for {company} - {role}")
        
        # Step 1: LinkedIn Writer analyzes the company
        prompt1 = f"""Analyze this company and role for a cover letter:
Company: {company}
Role: {role}
Job Description: {job_description}

Extract key requirements and company values."""
        
        # Chain through specialized models
        models = [
            "linkedin-writer:latest",     # Professional writing
            "llama3.1:latest",            # General intelligence
            "deepseek-coder-v2:16b",      # Technical depth
            "gemma2:latest"               # Final polish
        ]
        
        result = self.chain_models(models, prompt1)
        print(f"  ✅ Generated {len(result)} characters of content")
        return result
    
    def technical_assessment_chain(self, job_description: str) -> Dict:
        """
        Chain 2: Technical Skills Matcher
        Analyzes job requirements and matches with your skills
        """
        print(f"\n🔗 TECHNICAL ASSESSMENT CHAIN")
        
        prompt = f"""Analyze these job requirements and identify:
1. Required technical skills
2. Nice-to-have skills
3. Red flags or concerns
4. Estimated difficulty level

Job Description:
{job_description}

Provide structured analysis."""
        
        # Use technical models
        models = [
            "deepseek-coder-v2:16b",      # Code analysis
            "python_expert:latest",        # Python expertise
            "codellama:latest",           # General coding
            "qwen2.5:latest"              # Structured output
        ]
        
        result = self.chain_models(models, prompt)
        return {"analysis": result}
    
    def company_research_chain(self, company: str) -> str:
        """
        Chain 3: Deep Company Research
        Generates insights about the company for personalization
        """
        print(f"\n🔗 COMPANY RESEARCH CHAIN for {company}")
        
        prompt = f"""Research {company} and provide:
1. Company mission and values
2. Recent news or achievements
3. Technology stack they likely use
4. Culture and work environment
5. Key talking points for an interview

Company: {company}"""
        
        models = [
            "llama3.1:latest",            # General knowledge
            "gemma2:latest",              # Analysis
            "linkedin-writer:latest"      # Professional insights
        ]
        
        return self.chain_models(models, prompt)
    
    def interview_prep_chain(self, company: str, role: str) -> str:
        """
        Chain 4: Interview Preparation
        Generates likely interview questions and answers
        """
        print(f"\n🔗 INTERVIEW PREP CHAIN for {company} - {role}")
        
        prompt = f"""Generate interview preparation for:
Company: {company}
Role: {role}

Provide:
1. 10 likely technical questions
2. 5 behavioral questions
3. Strong answers showcasing 10+ years experience
4. Questions to ask the interviewer"""
        
        models = [
            "llama3.1:latest",
            "deepseek-coder-v2:16b",
            "linkedin-writer:latest",
            "qwen2.5:latest"
        ]
        
        return self.chain_models(models, prompt)
    
    def salary_negotiation_chain(self, company: str, role: str, location: str = "Remote") -> str:
        """
        Chain 5: Salary Negotiation Strategy
        """
        print(f"\n🔗 SALARY NEGOTIATION CHAIN for {company}")
        
        prompt = f"""Create salary negotiation strategy for:
Company: {company}
Role: {role}
Location: {location}
Experience: 10+ years in AI/ML

Provide:
1. Market rate analysis
2. Negotiation tactics
3. Counter-offer strategies
4. Total compensation targets"""
        
        models = [
            "llama3.1:latest",
            "gemma2:latest",
            "gpt-oss:20b"  # Larger model for complex reasoning
        ]
        
        return self.chain_models(models, prompt)
    
    def bulk_personalization_chain(self, companies: List[Dict]) -> List[Dict]:
        """
        Chain 6: Bulk Personalization
        Process multiple companies at once
        """
        print(f"\n🔗 BULK PERSONALIZATION CHAIN for {len(companies)} companies")
        
        personalized = []
        for company in companies:
            prompt = f"""Create a personalized opening line for:
Company: {company['name']}
Role: {company.get('role', 'Software Engineer')}
Focus: {company.get('focus', 'Technology')}

Make it specific and compelling."""
            
            # Quick chain for bulk processing
            models = ["linkedin-writer:latest", "gemma2:latest"]
            result = self.chain_models(models, prompt)
            
            company['personalized_opening'] = result
            personalized.append(company)
        
        return personalized
    
    def application_quality_scorer(self, cover_letter: str, resume_text: str, job_description: str) -> float:
        """
        Chain 7: Application Quality Scorer
        Evaluates your application before sending
        """
        print(f"\n🔗 APPLICATION QUALITY SCORER")
        
        prompt = f"""Score this job application from 0-100:

Job Description:
{job_description[:500]}

Cover Letter:
{cover_letter[:500]}

Resume excerpt:
{resume_text[:500]}

Provide:
1. Overall score (0-100)
2. Strengths
3. Weaknesses
4. Improvement suggestions"""
        
        models = [
            "llama3.1:latest",
            "deepseek-coder-v2:16b",
            "gemma2:latest"
        ]
        
        result = self.chain_models(models, prompt)
        
        # Extract score from result
        try:
            # Simple extraction - look for number between 0-100
            import re
            scores = re.findall(r'\b([0-9]{1,2}|100)\b', result)
            if scores:
                return float(scores[0]) / 100
        except:
            pass
        
        return 0.75  # Default score
    
    # ========================================================================
    # AUTOMATED WORKFLOWS
    # ========================================================================
    
    def auto_enhance_all_applications(self):
        """
        Automatically enhance all pending applications in database
        """
        print("\n🚀 AUTO-ENHANCING ALL PENDING APPLICATIONS")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get high-value pending jobs
        cursor.execute("""
            SELECT company, position, job_url, description
            FROM job_discoveries
            WHERE applied = 0 AND relevance_score >= 0.65
            ORDER BY relevance_score DESC
            LIMIT 10
        """)
        
        jobs = cursor.fetchall()
        print(f"Found {len(jobs)} high-value jobs to enhance")
        
        enhanced_applications = []
        
        for company, position, url, description in jobs:
            print(f"\n  Processing: {company} - {position}")
            
            # Run multiple chains
            cover_letter = self.ultimate_cover_letter_chain(company, position, description or "")
            research = self.company_research_chain(company)
            technical = self.technical_assessment_chain(description or position)
            
            enhanced_applications.append({
                'company': company,
                'position': position,
                'cover_letter': cover_letter,
                'research': research,
                'technical_analysis': technical,
                'quality_score': self.application_quality_scorer(
                    cover_letter, 
                    "10+ years Python, AI/ML expertise", 
                    description or position
                )
            })
            
            print(f"    ✅ Enhanced with quality score: {enhanced_applications[-1]['quality_score']:.2%}")
        
        conn.close()
        return enhanced_applications
    
    def continuous_improvement_loop(self):
        """
        Run continuous improvement on your application materials
        """
        print("\n♾️ CONTINUOUS IMPROVEMENT LOOP")
        
        # Load your resume
        resume_path = Path.home() / "AI-ML-Portfolio" / "ai-talent-optimizer" / "resumes"
        
        improvement_prompts = [
            "How can this resume better showcase AI/ML expertise?",
            "What keywords are missing for ATS systems?",
            "How to better quantify achievements?",
            "What modern skills should be highlighted?",
            "How to show thought leadership?"
        ]
        
        for prompt in improvement_prompts:
            print(f"\n  Analyzing: {prompt}")
            
            models = ["llama3.1:latest", "linkedin-writer:latest", "gemma2:latest"]
            result = self.chain_models(models, f"{prompt}\n\nContext: 10+ years experience, 74 Ollama models, 274 Python modules")
            
            print(f"    💡 Insight: {result[:200]}...")
    
def main():
    """Demo the power of Ollama chains"""
    chains = OllamaJobChains()
    
    print("="*60)
    print("🚀 OLLAMA MODEL CHAINS FOR JOB APPLICATIONS")
    print("="*60)
    print("Maximizing your $250/month Claude investment!")
    print("\nAvailable Power Chains:")
    print("1. Ultimate Cover Letter Chain (4 models)")
    print("2. Technical Assessment Chain (4 models)")
    print("3. Company Research Chain (3 models)")
    print("4. Interview Prep Chain (4 models)")
    print("5. Salary Negotiation Chain (3 models)")
    print("6. Bulk Personalization Chain (2 models)")
    print("7. Application Quality Scorer (3 models)")
    print("="*60)
    
    # Demo with Anthropic
    print("\n📊 DEMO: Enhancing application for Anthropic")
    
    cover_letter = chains.ultimate_cover_letter_chain(
        "Anthropic",
        "ML Engineer",
        "Build safe AI systems, work with Claude, implement RLHF"
    )
    
    research = chains.company_research_chain("Anthropic")
    
    print(f"\n✅ Generated personalized content using 7+ models!")
    print(f"   Cover Letter: {len(cover_letter)} chars")
    print(f"   Research: {len(research)} chars")
    
    print("\n💡 TIP: Run auto_enhance_all_applications() to process all pending jobs!")

if __name__ == "__main__":
    main()