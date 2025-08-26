#!/usr/bin/env python3
"""
Master application generator using persistent context
Generates complete application packages from job descriptions
"""

import sqlite3
import json
import os
import re
from datetime import datetime
from pathlib import Path
import shutil

class ApplicationGenerator:
    def __init__(self):
        self.load_context()
        self.company = None
        self.title = None
        self.job_id = None
        
    def load_context(self):
        """Load the persistent context"""
        # Read generated context
        context_path = "CURRENT_PROFILE_CONTEXT.md"
        if Path(context_path).exists():
            with open(context_path, 'r') as f:
                self.context = f.read()
        else:
            # Generate it if missing
            from profile_context_generator import ProfileContextGenerator
            generator = ProfileContextGenerator()
            self.context = generator.generate_context_document()
        
        # Load from database
        conn = sqlite3.connect("unified_platform.db")
        cursor = conn.cursor()
        
        # Get all data
        self.identity = cursor.execute("SELECT * FROM profile").fetchone()
        self.metrics = dict(cursor.execute("SELECT metric_name, metric_value FROM metrics").fetchall())
        self.skills = cursor.execute("SELECT * FROM technical_skills").fetchall()
        self.projects = cursor.execute("SELECT * FROM major_projects").fetchall()
        self.narratives = dict(cursor.execute("SELECT narrative_type, narrative_text FROM positioning_narratives").fetchall())
        
        conn.close()
    
    def analyze_role(self, job_description):
        """Analyze the job description for key elements"""
        analysis = {
            'company': None,
            'position': None,
            'location': None,
            'salary_range': None,
            'job_id': None,
            'remote': False,
            'experience_required': None,
            'key_skills': [],
            'nice_to_haves': [],
            'red_flags': [],
            'match_score': 0,
            'strategic_value': None
        }
        
        # Extract company (look for common patterns)
        if 'Humana' in job_description:
            analysis['company'] = 'Humana'
            analysis['strategic_value'] = 'Former employer - institutional knowledge advantage'
        
        # Extract position title
        title_patterns = [
            r'Senior Cognitive/ML Python Engineer',
            r'Principal.*Engineer',
            r'Staff.*Engineer',
            r'Senior.*Engineer',
            r'Machine Learning Engineer',
            r'ML Engineer'
        ]
        for pattern in title_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                analysis['position'] = match.group(0)
                break
        
        # Extract job ID
        job_id_match = re.search(r'Job ID:\s*([A-Z0-9-]+)', job_description)
        if job_id_match:
            analysis['job_id'] = job_id_match.group(1)
        
        # Extract salary
        salary_match = re.search(r'\$([0-9,]+)\s*-\s*\$([0-9,]+)', job_description)
        if salary_match:
            min_sal = int(salary_match.group(1).replace(',', ''))
            max_sal = int(salary_match.group(2).replace(',', ''))
            analysis['salary_range'] = f"${min_sal:,} - ${max_sal:,}"
        
        # Check for remote
        if re.search(r'remote|work.from.home|wfh', job_description, re.IGNORECASE):
            analysis['remote'] = True
            analysis['location'] = 'Remote'
        
        # Extract key technologies
        tech_keywords = [
            'Python', 'PyTorch', 'TensorFlow', 'LLM', 'Large Language Model',
            'GenAI', 'Generative AI', 'RAG', 'Langchain', 'FastAPI', 'Flask',
            'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure', 'Machine Learning',
            'Deep Learning', 'NLP', 'Transformer', 'BERT', 'GPT'
        ]
        
        found_skills = []
        for tech in tech_keywords:
            if re.search(tech, job_description, re.IGNORECASE):
                found_skills.append(tech)
        analysis['key_skills'] = found_skills
        
        # Calculate match score
        match_points = 0
        if analysis['remote']:
            match_points += 20
        if 'LLM' in found_skills or 'Large Language Model' in found_skills:
            match_points += 30
        if 'Python' in found_skills:
            match_points += 20
        if analysis['company'] == 'Humana':
            match_points += 20
        if len(found_skills) > 5:
            match_points += 10
        
        analysis['match_score'] = min(match_points, 100)
        
        # Store for later use
        self.company = analysis['company'] or 'Company'
        self.title = analysis['position'] or 'Position'
        self.job_id = analysis['job_id']
        
        return analysis
    
    def generate_cover_letter(self, role_analysis):
        """Generate tailored cover letter using context"""
        company = role_analysis['company'] or 'Hiring Team'
        title = role_analysis['position'] or 'the position'
        
        # Select appropriate narrative based on role
        if 'Principal' in position or 'Staff' in position:
            opening_narrative = self.narratives.get('Principal Positioning', self.narratives['Power Statement'])
        else:
            opening_narrative = self.narratives.get('Outgrowth Story', self.narratives['One-Liner'])
        
        cover_letter = f"""Dear {company} Hiring Team,

{opening_narrative}

I am writing to express my strong interest in the {position} position at {company}. My unique combination of enterprise-scale platform development and cutting-edge AI/ML expertise makes me an ideal candidate for this role.

**What I've Built - The Evidence of My Capabilities:**

I haven't been waiting for permission to work at the Principal/Staff level. On my own time, I've architected and deployed:
- A multi-agent AI platform with 113 Python modules and 15+ production databases
- An intelligent automation system that's processed 1,600+ real-world interactions
- CEO-level outreach capabilities with personalized messaging orchestration
- Email verification and campaign management rivaling commercial CRM systems
- Real-time analytics dashboards tracking complex success metrics

This isn't theoretical knowledge - I modified 27 production modules today alone. I'm currently running 13 MCP servers that power this infrastructure.

**Technical Alignment with Your Needs:**

Your requirements for {', '.join(role_analysis['key_skills'][:3])} align perfectly with my daily work:
- **Python Mastery**: Managing 86,279 Python files with 10+ years of experience
- **LLM/GenAI Expertise**: Deployed 60+ Ollama models with RAG implementation
- **Scale & Architecture**: Platform complexity exceeding most startup MVPs
- **Production Systems**: 15+ databases, 1,045 automation scripts, continuous deployment

**Why This Role, Why Now:**

"""
        
        if company == 'Humana':
            cover_letter += """Having previously contributed to Humana, I understand your systems, culture, and challenges. But more importantly, I've spent the time since building exactly what Humana needs for its cognitive computing initiatives. I've outgrown my current role through aggressive self-directed learning and platform development.

The GenAI/LLM focus of this role perfectly matches the systems I've been building. I can bring immediate value through both my institutional knowledge and my cutting-edge capabilities.
"""
        else:
            cover_letter += """I've reached the ceiling in my current position, evidenced by the fact that I've built an enterprise platform on nights and weekends just to stay challenged. I need a role that matches my actual output - not my current title.

Your focus on {', '.join(role_analysis['key_skills'][:2])} aligns with the exact technologies I've been deploying in production. I don't just understand these concepts - I have working systems using them right now.
"""
        
        cover_letter += f"""
**The Value I Bring:**

Unlike candidates who might need ramp-up time, I can deliver immediate impact:
- Day 1: Contribute to architecture decisions with principal-level experience
- Week 1: Deploy production-ready LLM/GenAI solutions
- Month 1: Establish new best practices based on my platform learnings
- Quarter 1: Lead initiatives that typically require senior technical leadership

**Let's Connect:**

I'm excited about the opportunity to bring my platform-building experience and innovative approach to {company}. I'd welcome the chance to discuss how my proven ability to architect and deploy enterprise-scale systems can contribute to your team's success.

You can review my work at github.com/mds1, where you'll find evidence of the scale and sophistication I bring. I'm immediately available for a technical discussion about how my experience aligns with your needs.

Best regards,

{self.identity[1]}
{self.identity[2]}
{self.identity[3]}
{self.identity[4]}
{self.identity[5]}

P.S. I modified 27 production modules today while writing this application. This is my normal velocity - imagine what I could accomplish focused solely on {company}'s challenges."""
        
        return cover_letter
    
    def tailor_resume_content(self, role_analysis):
        """Generate tailored resume content"""
        
        resume_content = f"""MATTHEW SCOTT
{self.identity[2]} | {self.identity[3]} | {self.identity[4]} | {self.identity[5]}
{self.identity[6]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLATFORM BUILDER | 113 PYTHON MODULES | 1,600+ AUTOMATED INTERACTIONS | PRINCIPAL-LEVEL ARCHITECT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXECUTIVE SUMMARY

Self-directed ML engineer operating at Principal level with evidence to prove it:
• Architected multi-agent platform with 113 Python modules and 15+ databases
• Managing 86,279 Python files across production systems
• 1,600+ automated interactions processed through intelligent orchestration
• 27 production modules modified today (continuous feature deployment)
• 13 MCP servers currently running in production environment

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEY METRICS THAT MATTER

• Platform Scale: 113 Python modules, 15+ databases, 1,045 shell scripts
• Development Velocity: 20-30 files modified daily
• System Complexity: 10+ microservices, multi-agent architecture
• Production Reality: 1,600+ real interactions processed
• Innovation Rate: CEO outreach, email verification, campaign orchestration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TECHNICAL EXPERTISE

AI/ML & GENAI PLATFORMS
• LLM Orchestration: 60+ Ollama models deployed in production
• RAG Systems: Production implementation for personalization
• Multi-Agent Architecture: 113 Python modules in active system
• Prompt Engineering: Multi-model consensus, chain-of-thought
• Fine-tuning: Domain-specific model optimization

LANGUAGES & FRAMEWORKS
• Python (10+ years): 86,279 files under management
• Shell/Bash: 1,045 automation scripts
• SQL: 15+ production databases
• FastAPI/Flask: RESTful API design and implementation

INFRASTRUCTURE & SCALE
• Microservices: 13 MCP servers running continuously
• Databases: SQLite, PostgreSQL, complex schema design
• Automation: Email verification, bounce detection, campaign orchestration
• Analytics: Real-time metrics dashboards

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MAJOR PROJECTS - EVIDENCE OF PRINCIPAL-LEVEL WORK

AI CAREER INTELLIGENCE PLATFORM (2024 - Present)
• Scale: 113 Python modules, 15 databases, 1,600+ interactions processed
• Architecture: Multi-agent design with specialized bots
• Capabilities: CEO outreach, email verification, intelligent messaging
• Impact: Automated executive-level positioning and strategic outreach
• Tech Stack: Python, SQLite, LLMs, RAG, FastAPI, MCP Servers

LLM ORCHESTRATION FRAMEWORK (2024)
• Deployed 60+ fine-tuned models using Ollama
• Multi-model consensus and evaluation systems
• Domain-specific agents for specialized tasks
• Production deployment with real-time monitoring

EMAIL VERIFICATION & CAMPAIGN SYSTEM (2024)
• Production email verification with DNS/SMTP validation
• Bounce detection reducing rate from 100% to <5%
• Campaign orchestration with personalized messaging
• Gmail API integration for response tracking

CONSCIOUSNESS IN AI RESEARCH (2024)
• Exploratory research into emergent AI behaviors
• Custom testing frameworks for self-awareness metrics
• Bridge consciousness implementation and evaluation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROFESSIONAL EXPERIENCE

[Current Role] - While maintaining day job responsibilities:
• Built enterprise platform exceeding most startup MVPs
• Daily feature deployment (20-30 files modified)
• Architected systems typically requiring 5-10 engineers
• Self-directed upskilling in GenAI/LLMs

[Previous experience would go here...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EDUCATION & CONTINUOUS LEARNING

• Formal education credentials
• Self-directed learning: Built production LLM systems
• Daily development: 27 modules modified today alone
• Research: Consciousness in AI, emergent behaviors

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE PROOF IS IN THE PRODUCTION

"I don't talk about potential - I deliver production systems. While others discuss GenAI, 
I've deployed it. My 'side project' is a platform that rivals commercial products."

GitHub: github.com/mds1 | Active Development: 27 files modified today
"""
        
        return resume_content
    
    def create_interview_prep(self, role_analysis):
        """Create interview preparation materials"""
        
        prep_content = f"""# INTERVIEW PREPARATION - {self.company} {self.position}

## 🎯 Key Messages to Deliver

### Opening Statement (Tell me about yourself)
"{self.narratives['Power Statement']}"

Follow with: I'm particularly excited about this role because [specific reason based on job description].

## 💪 STAR Stories Ready to Deploy

### 1. Building at Scale (System Design Question)
**Situation**: Needed a job application system but found existing tools inadequate
**Task**: Build enterprise-scale platform for intelligent automation
**Action**: 
- Architected multi-agent system with 113 Python modules
- Implemented 15+ databases with complex relationships
- Deployed 10+ microservices for specialized functions
- Created email verification, bounce detection, campaign orchestration
**Result**: 1,600+ interactions processed, CEO-level outreach capability, platform rivaling commercial products

### 2. LLM/GenAI Implementation (Technical Deep Dive)
**Situation**: Needed personalized content generation at scale
**Task**: Implement LLM orchestration with quality control
**Action**:
- Deployed 60+ Ollama models locally
- Built RAG system for personalization
- Implemented multi-model consensus for quality
- Created prompt chaining for complex workflows
**Result**: Production system generating tailored content with verification

### 3. Problem-Solving Under Constraints (Behavioral)
**Situation**: 100% email bounce rate discovered in system
**Task**: Fix deliverability while maintaining automation
**Action**:
- Built email verification with DNS/SMTP validation
- Implemented bounce detection system
- Created fallback strategies
- Developed company research module
**Result**: Reduced bounce rate to <5%, improved deliverability

## 🎤 Anticipated Questions & Power Answers

### "Why are you interested in this role?"
"I've already been doing this work - I just haven't had the title. My platform with 113 Python modules and 15 databases proves I operate at Principal level. I modified 27 production modules today. I need a role that matches my output."

### "What's your experience with [specific technology]?"
For any technology mentioned:
- If you have it: "I'm currently using [tech] in production. For example, [specific example from your platform]"
- If you don't: "While I haven't used [tech] specifically, I've built similar systems using [related tech]. I modified 27 production modules today - I learn by building."

### "Describe a complex system you've built"
"My AI platform has 113 Python modules, 15 databases, and 10+ microservices. It's processed 1,600+ real interactions. Want me to walk you through the architecture?"
[Then describe multi-agent design, database relationships, service communication]

### "How do you stay current with technology?"
"I don't just read about tech - I build with it. I've deployed 60+ LLM models, implemented RAG, built multi-agent systems. I modified 27 production files today. My learning is hands-on and immediate."

### "What's your biggest weakness?"
"I can over-engineer when bored. That's literally why I built an enterprise platform on personal time. I need challenges that match my capacity, which is why I'm here."

### "Why should we hire you over other candidates?"
"Other candidates might talk about their potential. I can show you 86,279 Python files, 1,045 automation scripts, and a platform processing real data. I built this because I was bored. Imagine what I'll build when engaged on your challenges."

## 📊 Technical Topics to Highlight

Based on the job requirements, emphasize:
"""
        
        for skill in role_analysis['key_skills'][:10]:
            prep_content += f"- **{skill}**: [Your specific experience with this]\n"
        
        prep_content += f"""

## 🚀 Questions to Ask Them

### Technical/Architecture
1. "What's the current scale of your ML infrastructure?"
2. "How are you approaching LLM deployment and orchestration?"
3. "What's your strategy for RAG implementation?"

### Team/Culture
1. "What does principal-level impact look like here?"
2. "How much autonomy do engineers have in architecture decisions?"
3. "What's the most complex system your team has built recently?"

### Growth/Impact
1. "What would success look like in this role after 6 months?"
2. "What are the biggest technical challenges facing the team?"
3. "How does this role contribute to the company's AI strategy?"

## 💥 Closing Statement

"I want to be clear about what you're getting: someone who builds at principal level, with production systems to prove it. I modified 27 files today while preparing for this conversation. This is my normal velocity. I don't need ramp-up time - I need challenges that match my capacity. {self.company} has those challenges, and I'm ready to solve them."

## 📝 Post-Interview Follow-Up Template

Subject: Thank you - Excited about [specific technical challenge discussed]

Dear [Interviewer],

Thank you for our discussion about the {self.position} role. I was particularly intrigued by [specific technical challenge].

Given my experience with [relevant part of your platform], I already have ideas about approaching this:
[Brief technical insight]

I modified 27 production modules today, including [relevant technical area]. This is the velocity and innovation I'd bring to {self.company}.

Looking forward to next steps.

Best regards,
{self.identity[1]}

---
Remember: You're not interviewing for a job. You're demonstrating that you're already doing the job at a higher level than the title suggests.
"""
        
        return prep_content
    
    def save_application_package(self, role_analysis, cover_letter, resume, interview_prep):
        """Save all materials to organized directory structure"""
        
        # Create directory structure
        company_dir = self.company.replace(' ', '_').replace('/', '_')
        position_dir = self.position.replace(' ', '_').replace('/', '_')
        
        if self.job_id:
            position_dir = f"{position_dir}_{self.job_id}"
        
        base_path = Path("applications") / company_dir / position_dir
        base_path.mkdir(parents=True, exist_ok=True)
        
        # Save job description
        job_desc_path = base_path / "job_description.txt"
        with open(job_desc_path, 'w') as f:
            f.write(self.job_description)
        
        # Save cover letter
        cover_letter_path = base_path / "cover_letter.txt"
        with open(cover_letter_path, 'w') as f:
            f.write(cover_letter)
        
        # Save resume
        resume_version = base_path / "resume_tailored.txt"
        with open(resume_version, 'w') as f:
            f.write(resume)
        
        # Save interview prep
        prep_path = base_path / "interview_prep.md"
        with open(prep_path, 'w') as f:
            f.write(interview_prep)
        
        # Save application metadata
        metadata = {
            'generated': datetime.now().isoformat(),
            'company': self.company,
            'position': self.title,
            'job_id': self.job_id,
            'role_analysis': role_analysis,
            'match_score': role_analysis['match_score'],
            'files': {
                'job_description': str(job_desc_path),
                'cover_letter': str(cover_letter_path),
                'resume': str(resume_version),
                'interview_prep': str(prep_path)
            }
        }
        
        metadata_path = base_path / "application_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return base_path
    
    def generate_for_role(self, job_description):
        """Main method to generate complete application package"""
        
        self.job_description = job_description
        
        # Analyze the role
        print("📊 Analyzing role...")
        role_analysis = self.analyze_role(job_description)
        
        print(f"  Company: {role_analysis['company']}")
        print(f"  Position: {role_analysis['position']}")
        print(f"  Match Score: {role_analysis['match_score']}/100")
        
        # Generate materials
        print("\n📝 Generating materials...")
        cover_letter = self.generate_cover_letter(role_analysis)
        print("  ✅ Cover letter generated")
        
        resume = self.tailor_resume_content(role_analysis)
        print("  ✅ Resume tailored")
        
        interview_prep = self.create_interview_prep(role_analysis)
        print("  ✅ Interview prep created")
        
        # Save everything
        print("\n💾 Saving application package...")
        package_path = self.save_application_package(
            role_analysis, cover_letter, resume, interview_prep
        )
        print(f"  ✅ Saved to: {package_path}")
        
        # Generate summary
        summary = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 APPLICATION PACKAGE GENERATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Company: {self.company}
Position: {self.position}
Match Score: {role_analysis['match_score']}/100
Salary: {role_analysis.get('salary_range', 'Not specified')}

📁 Materials Generated:
✅ Cover Letter - Emphasizing platform scale (113 modules, 15 DBs)
✅ Resume - Tailored with metrics (86,279 Python files, 27 modified today)
✅ Interview Prep - STAR stories and power answers ready
✅ Metadata - Tracking and analysis data

📍 Location: {package_path}

🎯 Key Differentiators Emphasized:
• Built platform with 113 Python modules
• Managing 86,279 Python files
• 27 production modules modified today
• 13 MCP servers currently running
• 1,600+ automated interactions processed

💡 Next Steps:
1. Review materials in {package_path}
2. Submit application with tailored materials
3. Use interview prep for preparation
4. Follow up using provided template
"""
        
        print(summary)
        
        return {
            'analysis': role_analysis,
            'package_path': str(package_path),
            'summary': summary
        }

def main():
    """Interactive application generator"""
    print("🚀 APPLICATION GENERATOR")
    print("="*60)
    print("Paste the job description below.")
    print("When done, type 'END' on a new line:")
    print()
    
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    
    if not lines:
        print("❌ No job description provided")
        return
    
    job_description = '\n'.join(lines)
    
    # Generate application
    generator = ApplicationGenerator()
    result = generator.generate_for_role(job_description)
    
    print("\n✅ Application package complete!")
    print(f"📁 Find your materials in: {result['package_path']}")

if __name__ == "__main__":
    # Check if we have a saved job description (for testing)
    test_file = "last_job_description.txt"
    if Path(test_file).exists():
        print("Found saved job description. Using it for testing...")
        with open(test_file, 'r') as f:
            job_desc = f.read()
        generator = ApplicationGenerator()
        generator.generate_for_role(job_desc)
    else:
        main()