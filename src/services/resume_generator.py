"""
Resume Generator Service
Creates role-specific resume variants highlighting Humana/Mightily experience and notable projects
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor

logger = logging.getLogger(__name__)

class ResumeGenerator:
    """Generate role-specific resume variants"""
    
    def __init__(self, output_dir: str = "resumes/generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Core experience data
        self.experience = self._load_experience_data()
        self.projects = self._load_project_data()
        self.skills = self._load_skills_data()
        
    def _load_experience_data(self) -> Dict:
        """Load work experience data"""
        return {
            'humana': {
                'company': 'Humana Inc.',
                'location': 'Louisville, KY',
                'positions': [
                    {
                        'title': 'Senior Risk Management Professional II',
                        'period': 'October 2022 - Present',
                        'highlights': [
                            'Architected privacy-first AI platform with 117 Python modules managing 86,279+ production files',
                            'Orchestrated 7 specialized LLMs through local Mirador system with zero cloud dependencies',
                            'Achieved 98.68% OKR improvement through PowerShell/ServiceNow automation',
                            'Reduced manual compliance processes by 40% through intelligent automation frameworks',
                            'Maintained 100% CMS/Medicare compliance across all systems and deployments',
                            'Enabled 5+ consecutive successful Medicare AEP launches without critical issues'
                        ],
                        'technologies': ['Python', 'LLM Orchestration', 'ServiceNow', 'PowerShell', 'ChromaDB']
                    },
                    {
                        'title': 'Risk Management Professional II',
                        'period': 'September 2017 - October 2022',
                        'highlights': [
                            'Managed 1,000+ document deployments during AEP with zero critical defects',
                            'Self-taught Python and immediately applied to production systems, reducing manual work by 40%',
                            'Built comprehensive testing frameworks scaling to support 1M+ Medicare members'
                        ],
                        'technologies': ['Python', 'SQL', 'Test Automation', 'Data Analysis']
                    },
                    {
                        'title': 'Risk Management Analyst',
                        'period': 'January 2016 - September 2017',
                        'highlights': [
                            'Pioneered automated testing methodologies adopted across enterprise',
                            'Established data analysis practices using Splunk and analytics platforms'
                        ],
                        'technologies': ['Splunk', 'Testing Frameworks', 'Process Automation']
                    }
                ],
                'total_tenure': '10+ years',
                'key_achievement': 'Delivered $1.2M annual savings through intelligent automation'
            },
            'mightily': {
                'company': 'Mightily',
                'location': 'Louisville, KY',
                'positions': [
                    {
                        'title': 'Digital Marketing Professional',
                        'period': 'March 2012 - January 2016',
                        'highlights': [
                            'Led digital transformation initiatives for 50+ local businesses',
                            'Developed data-driven marketing strategies increasing client ROI by 200%',
                            'Built automated reporting systems tracking campaign performance',
                            'Managed multi-channel campaigns across social, email, and web platforms'
                        ],
                        'technologies': ['Analytics', 'Marketing Automation', 'Web Development', 'SEO/SEM']
                    }
                ],
                'total_tenure': '4 years',
                'key_achievement': 'Transformed traditional businesses through digital innovation'
            }
        }
    
    def _load_project_data(self) -> Dict:
        """Load notable project data"""
        return {
            'mirador': {
                'name': 'Mirador AI Orchestration Framework',
                'description': 'Local-first AI platform orchestrating multiple LLMs',
                'highlights': [
                    'Built distributed AI architecture with 7 specialized models',
                    'Implemented vector database operations using ChromaDB',
                    'Achieved 100% privacy compliance with zero cloud dependencies',
                    'Processed 86,279+ files with intelligent automation'
                ],
                'technologies': ['Python', 'Ollama', 'ChromaDB', 'FastAPI', 'LangChain'],
                'github': 'github.com/guitargnar/mirador'
            },
            'fretforge': {
                'name': 'FretForge Guitar Learning Platform',
                'description': 'Interactive guitar education platform with AI assistance',
                'highlights': [
                    'Developed real-time tablature rendering system',
                    'Implemented progressive skill tracking algorithms',
                    'Created responsive web interface with offline capabilities',
                    'Built comprehensive exercise library with 1000+ patterns'
                ],
                'technologies': ['JavaScript', 'React', 'Web Audio API', 'Python'],
                'github': 'github.com/guitargnar/fretforge'
            },
            'financeforge': {
                'name': 'FinanceForge Financial Tracker',
                'description': 'Privacy-focused personal finance management system',
                'highlights': [
                    'Built secure transaction categorization using ML',
                    'Implemented real-time budget tracking and alerts',
                    'Created predictive analytics for spending patterns',
                    'Maintained 100% data privacy with local-only storage'
                ],
                'technologies': ['Python', 'SQLite', 'Pandas', 'Scikit-learn'],
                'github': 'github.com/guitargnar/financeforge'
            },
            'ai_talent_optimizer': {
                'name': 'AI Talent Optimizer',
                'description': 'Automated job application system with AI optimization',
                'highlights': [
                    'Scraped and processed 500+ job listings daily',
                    'Built intelligent email discovery and validation system',
                    'Created dynamic resume generation for role-specific applications',
                    'Implemented response tracking and follow-up automation'
                ],
                'technologies': ['Python', 'SQLite', 'NLP', 'Email Automation'],
                'github': 'github.com/guitargnar/ai-talent-optimizer'
            },
            'phishing_detector': {
                'name': 'Advanced Phishing Detection System',
                'description': 'ML-powered email security tool',
                'highlights': [
                    'Achieved 95% accuracy in phishing detection',
                    'Processed 10,000+ emails with real-time analysis',
                    'Implemented ensemble learning with multiple models',
                    'Created Gmail integration for automatic protection'
                ],
                'technologies': ['Python', 'Scikit-learn', 'Gmail API', 'NLP'],
                'github': 'github.com/guitargnar/phishing-detector'
            }
        }
    
    def _load_skills_data(self) -> Dict:
        """Load skills categorized by domain"""
        return {
            'ai_ml': [
                'LLM Orchestration', 'Multi-Agent Systems', 'Vector Databases',
                'ChromaDB', 'Ollama', 'LangChain', 'Hugging Face', 'PyTorch',
                'Scikit-learn', 'NLP', 'Computer Vision'
            ],
            'programming': [
                'Python', 'JavaScript', 'SQL', 'PowerShell', 'Bash',
                'React', 'FastAPI', 'Node.js', 'Git'
            ],
            'healthcare': [
                'HIPAA Compliance', 'CMS Regulations', 'Medicare Systems',
                'Clinical Workflows', 'Risk Management', 'Healthcare Analytics'
            ],
            'architecture': [
                'System Design', 'Microservices', 'Event-Driven Architecture',
                'Distributed Systems', 'API Design', 'Database Design'
            ],
            'tools': [
                'ServiceNow', 'Splunk', 'Docker', 'Kubernetes', 'AWS',
                'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch'
            ]
        }
    
    def generate_resume_variant(self, role_type: str, company: Optional[str] = None) -> str:
        """Generate a resume variant for a specific role type"""
        
        # Define role-specific configurations
        role_configs = {
            'ai_ml_engineer': {
                'title': 'Senior AI/ML Engineer',
                'focus_projects': ['mirador', 'ai_talent_optimizer', 'phishing_detector'],
                'focus_skills': ['ai_ml', 'programming', 'architecture'],
                'humana_emphasis': 'ai_platform'
            },
            'principal_engineer': {
                'title': 'Principal Engineer',
                'focus_projects': ['mirador', 'fretforge', 'financeforge'],
                'focus_skills': ['architecture', 'ai_ml', 'programming'],
                'humana_emphasis': 'leadership'
            },
            'healthcare_tech': {
                'title': 'Healthcare Technology Leader',
                'focus_projects': ['mirador', 'financeforge', 'phishing_detector'],
                'focus_skills': ['healthcare', 'ai_ml', 'architecture'],
                'humana_emphasis': 'compliance'
            },
            'startup_engineer': {
                'title': 'Full-Stack AI Engineer',
                'focus_projects': ['fretforge', 'ai_talent_optimizer', 'mirador'],
                'focus_skills': ['programming', 'ai_ml', 'tools'],
                'humana_emphasis': 'innovation'
            },
            'security_engineer': {
                'title': 'Security & AI Engineer',
                'focus_projects': ['phishing_detector', 'mirador', 'financeforge'],
                'focus_skills': ['ai_ml', 'healthcare', 'architecture'],
                'humana_emphasis': 'security'
            }
        }
        
        config = role_configs.get(role_type, role_configs['ai_ml_engineer'])
        
        # Generate PDF
        filename = f"{role_type}_{datetime.now().strftime('%Y%m%d')}.pdf"
        if company:
            filename = f"{company.lower().replace(' ', '_')}_{filename}"
        
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build resume content
        content = self._build_resume_content(config, company)
        
        # Generate PDF
        doc.build(content)
        
        logger.info(f"Generated resume variant: {filepath}")
        return str(filepath)
    
    def _build_resume_content(self, config: Dict, company: Optional[str]) -> List:
        """Build resume content for PDF generation"""
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        name_style = ParagraphStyle(
            'CustomName',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1e3a5f'),
            alignment=TA_CENTER
        )
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#1e3a5f'),
            spaceAfter=6
        )
        
        # Header
        story.append(Paragraph("MATTHEW SCOTT", name_style))
        story.append(Paragraph(config['title'], title_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Contact info
        contact = "matthewdscott7@gmail.com | (502) 345-0525 | linkedin.com/in/mscott77 | github.com/guitargnar"
        story.append(Paragraph(contact, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Professional Summary
        story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
        
        if config['humana_emphasis'] == 'ai_platform':
            summary = f"Senior AI/ML Engineer with 10+ years at Humana building enterprise healthcare AI systems. Architected privacy-first platform with 117 Python modules managing 86,279+ production files. Specialized in local-first AI architectures maintaining 100% regulatory compliance."
        elif config['humana_emphasis'] == 'leadership':
            summary = f"Principal-level engineer with 10+ years at Fortune 50 Humana, demonstrating technical leadership across 117 Python modules and 86,279+ production files. Proven track record of zero critical defects across 1,000+ deployments."
        elif config['humana_emphasis'] == 'compliance':
            summary = f"Healthcare technology leader with 10+ years at Humana maintaining 100% CMS/Medicare compliance. Built HIPAA-compliant AI systems processing sensitive healthcare data with zero violations across decade-long tenure."
        elif config['humana_emphasis'] == 'innovation':
            summary = f"Entrepreneurial engineer with 10+ years at Humana and 4 years at digital agency Mightily. Built multiple production AI systems from scratch, including Mirador orchestration framework managing 7 LLMs locally."
        else:  # security
            summary = f"Security-focused AI engineer with 10+ years at Humana building zero-trust architectures. Developed advanced phishing detection achieving 95% accuracy and maintained 100% compliance across all deployments."
        
        if company:
            summary += f" Excited to bring this expertise to {company}."
        
        story.append(Paragraph(summary, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Key Projects
        story.append(Paragraph("KEY PROJECTS", heading_style))
        
        for project_key in config['focus_projects']:
            project = self.projects[project_key]
            project_text = f"<b>{project['name']}</b>: {project['description']}"
            story.append(Paragraph(project_text, styles['Normal']))
            
            for highlight in project['highlights'][:2]:  # Top 2 highlights
                story.append(Paragraph(f"• {highlight}", styles['Normal']))
            
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.1*inch))
        
        # Professional Experience - Humana
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))
        
        humana = self.experience['humana']
        position = humana['positions'][0]  # Most recent
        
        story.append(Paragraph(f"<b>{position['title']}</b>", styles['Normal']))
        story.append(Paragraph(f"{humana['company']} | {humana['location']} | {position['period']}", styles['Normal']))
        
        for highlight in position['highlights'][:4]:  # Top 4 highlights
            story.append(Paragraph(f"• {highlight}", styles['Normal']))
        
        story.append(Spacer(1, 0.1*inch))
        
        # Mightily experience (brief)
        mightily = self.experience['mightily']
        mightily_pos = mightily['positions'][0]
        
        story.append(Paragraph(f"<b>{mightily_pos['title']}</b>", styles['Normal']))
        story.append(Paragraph(f"{mightily['company']} | {mightily['location']} | {mightily_pos['period']}", styles['Normal']))
        story.append(Paragraph(f"• {mightily['key_achievement']}", styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Skills
        story.append(Paragraph("TECHNICAL SKILLS", heading_style))
        
        for skill_category in config['focus_skills']:
            skills = self.skills[skill_category]
            skill_text = f"<b>{skill_category.replace('_', ' ').title()}</b>: {', '.join(skills[:8])}"
            story.append(Paragraph(skill_text, styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Education
        story.append(Paragraph("EDUCATION", heading_style))
        story.append(Paragraph("Bachelor of Science | University of Louisville", styles['Normal']))
        
        return story
    
    def generate_all_variants(self) -> Dict[str, str]:
        """Generate all resume variants"""
        variants = {}
        
        role_types = [
            'ai_ml_engineer',
            'principal_engineer',
            'healthcare_tech',
            'startup_engineer',
            'security_engineer'
        ]
        
        for role_type in role_types:
            filepath = self.generate_resume_variant(role_type)
            variants[role_type] = filepath
            
        logger.info(f"Generated {len(variants)} resume variants")
        return variants

def generate_resumes():
    """Standalone function to generate resume variants"""
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    generator = ResumeGenerator()
    
    # Generate all variants
    variants = generator.generate_all_variants()
    
    print("\n" + "="*50)
    print("📄 Resume Generation Complete!")
    print("="*50)
    
    for role_type, filepath in variants.items():
        print(f"✅ {role_type}: {Path(filepath).name}")
    
    # Generate company-specific versions for top targets
    top_companies = ['Anthropic', 'OpenAI', 'Tempus', 'Google DeepMind']
    
    print("\n🎯 Generating company-specific versions...")
    
    for company in top_companies:
        filepath = generator.generate_resume_variant('ai_ml_engineer', company)
        print(f"✅ {company}: {Path(filepath).name}")
    
    return variants

if __name__ == "__main__":
    generate_resumes()