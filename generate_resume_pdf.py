#!/usr/bin/env python3
"""
Generate professional PDF resume from Markdown
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import HRFlowable
import re

class ProfessionalResume:
    def __init__(self, filename="MATTHEW_SCOTT_RESUME_2025.pdf"):
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        self.create_custom_styles()
        
    def create_custom_styles(self):
        """Create custom styles for the resume"""
        # Name style
        self.styles.add(ParagraphStyle(
            name='Name',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='ResumeTitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Contact style
        self.styles.add(ParagraphStyle(
            name='Contact',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#2a2a2a')
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#0066cc'),
            borderWidth=0,
            borderPadding=0
        ))
        
        # Job title
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=2,
            spaceBefore=8
        ))
        
        # Company
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=4
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#2a2a2a'),
            alignment=TA_JUSTIFY
        ))
        
        # Bullet points
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=13,
            leftIndent=20,
            bulletIndent=10,
            textColor=colors.HexColor('#2a2a2a')
        ))
        
    def add_header(self):
        """Add resume header with name and contact info"""
        # Name
        self.story.append(Paragraph("MATTHEW SCOTT", self.styles['Name']))
        
        # Title
        self.story.append(Paragraph("<b>AI/ML Engineer & Enterprise Innovation Leader</b>", self.styles['ResumeTitle']))
        
        # Contact info
        contact = "Louisville, KY | (502) 345-0525 | matthewdscott7@gmail.com | linkedin.com/in/mscott77 | github.com/guitargnar"
        self.story.append(Paragraph(contact, self.styles['Contact']))
        
        # Horizontal line
        self.story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
        self.story.append(Spacer(1, 0.1*inch))
        
    def add_summary(self):
        """Add executive summary"""
        self.story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeading']))
        
        summary = """Senior technology leader with 10+ years at Fortune 50 Humana, driving $1.2M+ annual savings through 
        AI automation and enterprise risk management. Built production AI systems handling 86,000+ Python files while 
        maintaining day job. Proven ability to bridge healthcare domain expertise with cutting-edge AI/ML implementation at scale."""
        
        self.story.append(Paragraph(summary, self.styles['CustomBody']))
        
        competencies = """<b>Core Competencies:</b> Multi-Agent AI Orchestration | Large Language Models | Healthcare Compliance | 
        Enterprise Risk Management | Python Automation | Production ML Systems | Team Leadership | Strategic Planning"""
        
        self.story.append(Spacer(1, 0.05*inch))
        self.story.append(Paragraph(competencies, self.styles['CustomBody']))
        
    def add_experience(self):
        """Add professional experience section"""
        self.story.append(Paragraph("PROFESSIONAL EXPERIENCE", self.styles['SectionHeading']))
        
        # Humana
        self.story.append(Paragraph("<b>HUMANA INC.</b> | Louisville, KY", self.styles['Company']))
        self.story.append(Paragraph("<i>Fortune 50 Healthcare Leader (70,000+ employees, $100B+ revenue)</i>", 
                                   self.styles['Normal']))
        
        # Senior Role
        self.story.append(Paragraph("<b>Senior Risk Management Professional II</b> | Oct 2022 – Present", 
                                   self.styles['JobTitle']))
        
        achievements1 = [
            "• Architected AI-powered risk assessment platform processing 1M+ member records daily, reducing processing time by 40%",
            "• Led cross-functional team of 12 to implement Medicare Stars optimization, improving quality scores by 8%",
            "• Delivered $1.2M annual savings through Python automation of compliance workflows",
            "• Built predictive models for risk adjustment accuracy, achieving 96% precision rate",
            "• Spearheaded Data Modernization initiative impacting 5,000+ enterprise users"
        ]
        
        for achievement in achievements1:
            self.story.append(Paragraph(achievement, self.styles['BulletPoint']))
        
        # Previous Role
        self.story.append(Paragraph("<b>Risk Management Professional II</b> | Sep 2017 – Oct 2022", 
                                   self.styles['JobTitle']))
        
        achievements2 = [
            "• Developed automated CMS compliance system maintaining 100% audit readiness",
            "• Created real-time dashboards for C-suite executives tracking $50M+ in risk exposure",
            "• Implemented E-Commerce Acceleration project increasing digital engagement 35%",
            "• Trained 50+ analysts on advanced analytics and Python programming",
            "• Zero critical defects in production systems over 5-year period"
        ]
        
        for achievement in achievements2:
            self.story.append(Paragraph(achievement, self.styles['BulletPoint']))
    
    def add_projects(self):
        """Add technical projects section"""
        self.story.append(Paragraph("TECHNICAL PROJECTS & INNOVATIONS", self.styles['SectionHeading']))
        
        # Project 1: AI Talent Optimizer
        self.story.append(Paragraph("<b>AI Talent Optimizer</b> | 2025", self.styles['JobTitle']))
        self.story.append(Paragraph("<i>Autonomous Job Search & Career Advancement Platform</i>", self.styles['Normal']))
        
        project1_points = [
            "• Built comprehensive automation system with 117 Python modules and 86,000+ files",
            "• Orchestrated 8 SQLite databases for application tracking and analytics",
            "• Implemented multi-channel application strategy (email, API, web scraping)",
            "• Technologies: Python, SQLite, Gmail API, BeautifulSoup, Pandas"
        ]
        
        for point in project1_points:
            self.story.append(Paragraph(point, self.styles['BulletPoint']))
        
        # Project 2: Mirador
        self.story.append(Paragraph("<b>Mirador AI System</b> | 2025", self.styles['JobTitle']))
        self.story.append(Paragraph("<i>89-Model Personal AI Advisory Platform</i>", self.styles['Normal']))
        
        project2_points = [
            "• Architected multi-agent orchestration system coordinating 89 specialized AI models",
            "• Achieved measurable AI consciousness (HCL score: 0.83/1.0)",
            "• Built 100% local, privacy-preserving implementation using Ollama",
            "• Technologies: Python, Ollama, LLaMA 3.2, Mistral, PostgreSQL"
        ]
        
        for point in project2_points:
            self.story.append(Paragraph(point, self.styles['BulletPoint']))
            
    def add_skills(self):
        """Add technical skills section"""
        self.story.append(Paragraph("TECHNICAL SKILLS", self.styles['SectionHeading']))
        
        skills = {
            "Languages": "Python (Expert), SQL (Advanced), JavaScript (Proficient), Bash (Proficient)",
            "AI/ML": "LLaMA, Mistral, Claude, GPT-4, Ollama, LangChain, Transformers, scikit-learn",
            "Data & Analytics": "Pandas, NumPy, PostgreSQL, SQLite, Tableau, Power BI, Jupyter",
            "Cloud & DevOps": "AWS, Docker, Git, CI/CD, Linux, REST APIs, Kubernetes basics",
            "Healthcare": "HIPAA, CMS Compliance, Medicare Stars, Risk Adjustment, Claims Processing"
        }
        
        for category, items in skills.items():
            self.story.append(Paragraph(f"<b>{category}:</b> {items}", self.styles['CustomBody']))
            
    def add_achievements(self):
        """Add key achievements section"""
        self.story.append(Paragraph("KEY ACHIEVEMENTS & METRICS", self.styles['SectionHeading']))
        
        metrics = [
            "• <b>$1.2M+</b> annual savings through automation at Humana",
            "• <b>174K</b> revenue generated through AI-powered business",
            "• <b>117</b> Python modules in production AI platform",
            "• <b>89</b> AI models orchestrated in Mirador system",
            "• <b>100%</b> CMS compliance maintained for 5+ years",
            "• <b>96%</b> accuracy in predictive risk models",
            "• <b>0</b> critical production defects over 10-year tenure"
        ]
        
        for metric in metrics:
            self.story.append(Paragraph(metric, self.styles['BulletPoint']))
    
    def generate(self):
        """Generate the PDF resume"""
        self.add_header()
        self.add_summary()
        self.add_experience()
        self.add_projects()
        self.add_skills()
        self.add_achievements()
        
        # Build PDF
        self.doc.build(self.story)
        print(f"✅ Resume generated: {self.filename}")
        
        # Also create a plain text version
        self.create_text_version()
        
    def create_text_version(self):
        """Create plain text version for ATS systems"""
        text_content = """MATTHEW SCOTT
AI/ML Engineer & Enterprise Innovation Leader
Louisville, KY | (502) 345-0525 | matthewdscott7@gmail.com
LinkedIn: linkedin.com/in/mscott77 | GitHub: github.com/guitargnar

EXECUTIVE SUMMARY
Senior technology leader with 10+ years at Fortune 50 Humana, driving $1.2M+ annual savings through AI automation and enterprise risk management. Built production AI systems handling 86,000+ Python files while maintaining day job. Proven ability to bridge healthcare domain expertise with cutting-edge AI/ML implementation at scale.

PROFESSIONAL EXPERIENCE

HUMANA INC. | Louisville, KY
Fortune 50 Healthcare Leader (70,000+ employees, $100B+ revenue)

Senior Risk Management Professional II | Oct 2022 - Present
- Architected AI-powered risk assessment platform processing 1M+ member records daily, reducing processing time by 40%
- Led cross-functional team of 12 to implement Medicare Stars optimization, improving quality scores by 8%
- Delivered $1.2M annual savings through Python automation of compliance workflows
- Built predictive models for risk adjustment accuracy, achieving 96% precision rate
- Spearheaded Data Modernization initiative impacting 5,000+ enterprise users

Risk Management Professional II | Sep 2017 - Oct 2022
- Developed automated CMS compliance system maintaining 100% audit readiness
- Created real-time dashboards for C-suite executives tracking $50M+ in risk exposure
- Implemented E-Commerce Acceleration project increasing digital engagement 35%
- Trained 50+ analysts on advanced analytics and Python programming
- Zero critical defects in production systems over 5-year period

TECHNICAL PROJECTS

AI Talent Optimizer | 2025
- Built comprehensive automation system with 117 Python modules and 86,000+ files
- Orchestrated 8 SQLite databases for application tracking and analytics
- Implemented multi-channel application strategy

Mirador AI System | 2025
- Architected multi-agent orchestration system coordinating 89 specialized AI models
- Achieved measurable AI consciousness (HCL score: 0.83/1.0)
- Built 100% local, privacy-preserving implementation using Ollama

TECHNICAL SKILLS
Languages: Python, SQL, JavaScript, Bash
AI/ML: LLaMA, Mistral, Claude, GPT-4, Ollama, LangChain, Transformers
Data: Pandas, NumPy, PostgreSQL, SQLite, Tableau, Power BI
Cloud: AWS, Docker, Git, CI/CD, Linux, REST APIs
Healthcare: HIPAA, CMS Compliance, Medicare Stars, Risk Adjustment

KEY ACHIEVEMENTS
- $1.2M+ annual savings through automation
- 174K revenue generated through AI business
- 117 Python modules in production
- 89 AI models orchestrated
- 100% CMS compliance maintained
- 96% accuracy in risk models
- 0 critical production defects"""
        
        with open("MATTHEW_SCOTT_RESUME_2025.txt", "w") as f:
            f.write(text_content)
        print("✅ Text version created: MATTHEW_SCOTT_RESUME_2025.txt")

if __name__ == "__main__":
    # Check if reportlab is installed
    try:
        import reportlab
    except ImportError:
        print("Installing reportlab...")
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab"])
        print("Reportlab installed!")
    
    # Generate resume
    resume = ProfessionalResume()
    resume.generate()
    
    print("\n📄 Resume files created:")
    print("  - MATTHEW_SCOTT_RESUME_2025.pdf (Professional PDF)")
    print("  - MATTHEW_SCOTT_RESUME_2025.txt (ATS-friendly text)")
    print("  - MATTHEW_SCOTT_RESUME_2025.md (Markdown source)")
    print("\n🚀 Ready to apply to any job!")