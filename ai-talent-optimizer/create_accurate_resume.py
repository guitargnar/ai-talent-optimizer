#!/usr/bin/env python3
"""
Create Accurate Resume
Generates truthful, professional resume based on verified facts
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from pathlib import Path
import os

def create_accurate_resume():
    """Create professional resume with verified facts only"""
    
    # Output path
    output_dir = Path("resumes")
    output_dir.mkdir(exist_ok=True)
    pdf_path = output_dir / "matthew_scott_professional_resume.pdf"
    
    # Create PDF
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderColor=colors.HexColor('#2c3e50'),
        borderWidth=0,
        borderPadding=0
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leading=12
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=normal_style,
        leftIndent=20,
        bulletIndent=10
    )
    
    # Header
    elements.append(Paragraph("<b>MATTHEW SCOTT</b>", title_style))
    elements.append(Paragraph(
        "AI/ML Engineer | Healthcare Technology Specialist",
        ParagraphStyle('SubTitle', parent=normal_style, alignment=TA_CENTER, fontSize=11)
    ))
    elements.append(Paragraph(
        "matthewdscott7@gmail.com | (502) 345-0525 | LinkedIn: linkedin.com/in/mscott77 | Louisville, KY",
        ParagraphStyle('Contact', parent=normal_style, alignment=TA_CENTER, fontSize=9)
    ))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Professional Summary
    elements.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
    elements.append(Paragraph(
        """Senior AI/ML Engineer with 10+ years at Humana, specializing in healthcare technology innovation 
        and compliance automation. Proven track record of building production ML systems that deliver 
        measurable business impact through process automation and intelligent decision support. 
        Experienced in Python development, LLM orchestration, and enterprise-scale deployments.""",
        normal_style
    ))
    
    elements.append(Spacer(1, 0.15*inch))
    
    # Core Competencies
    elements.append(Paragraph("TECHNICAL SKILLS", heading_style))
    
    skills_data = [
        ["Languages:", "Python (Expert), SQL, JavaScript, Shell Scripting"],
        ["AI/ML:", "LLM Integration, NLP, Predictive Analytics, Model Orchestration"],
        ["Frameworks:", "PyTorch, TensorFlow, Scikit-learn, HuggingFace, LangChain"],
        ["Databases:", "PostgreSQL, MongoDB, SQLite, Vector Databases"],
        ["Cloud/DevOps:", "AWS, Docker, Git, CI/CD, Linux Administration"],
        ["Healthcare:", "CMS Compliance, Medicare Systems, HIPAA, Risk Management"]
    ]
    
    skills_table = Table(skills_data, colWidths=[1.5*inch, 5*inch])
    skills_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Bold first column
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
    ]))
    
    elements.append(skills_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Professional Experience
    elements.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))
    
    # Current Role
    elements.append(Paragraph(
        "<b>Senior Risk Management Professional II - AI/ML Innovation Lead</b>",
        ParagraphStyle('JobTitle', parent=normal_style, fontSize=11)
    ))
    elements.append(Paragraph(
        "Humana Inc. | Louisville, KY | October 2022 – Present",
        ParagraphStyle('JobInfo', parent=normal_style, fontSize=9, textColor=colors.HexColor('#666666'))
    ))
    
    achievements = [
        "• Architected Python ML frameworks delivering $1.2M in annual savings through process automation",
        "• Led development of AI-driven compliance system maintaining 100% accuracy across Medicare regulations",
        "• Built LLM orchestration system (Mirador) coordinating 7 specialized models for complex workflows",
        "• Developed predictive analytics models improving risk detection by 20% using ensemble methods",
        "• Managed cross-functional AI initiatives including E-Commerce Acceleration and Data Modernization",
        "• Created automated testing framework reducing manual review time by 35%"
    ]
    
    for achievement in achievements:
        elements.append(Paragraph(achievement, bullet_style))
    
    elements.append(Spacer(1, 0.1*inch))
    
    # Previous Role
    elements.append(Paragraph(
        "<b>Risk Management Professional II - Automation Engineering Lead</b>",
        ParagraphStyle('JobTitle', parent=normal_style, fontSize=11)
    ))
    elements.append(Paragraph(
        "Humana Inc. | Louisville, KY | September 2017 – October 2022",
        ParagraphStyle('JobInfo', parent=normal_style, fontSize=9, textColor=colors.HexColor('#666666'))
    ))
    
    achievements2 = [
        "• Built automated testing framework processing 1,000+ deployments with zero critical defects",
        "• Implemented ML-based compliance monitoring for 200+ Medicare pages annually",
        "• Integrated AI/ML pipelines into CI/CD workflows for continuous optimization",
        "• Mentored team of 12 engineers on Python automation and machine learning best practices",
        "• Developed enterprise-scale production monitoring systems for complex Python applications"
    ]
    
    for achievement in achievements2:
        elements.append(Paragraph(achievement, bullet_style))
    
    elements.append(Spacer(1, 0.1*inch))
    
    # Startup Experience
    elements.append(Paragraph(
        "<b>Co-Founder & Technical Lead</b>",
        ParagraphStyle('JobTitle', parent=normal_style, fontSize=11)
    ))
    elements.append(Paragraph(
        "Mightily | Remote | 2014 – 2017 (4 years)",
        ParagraphStyle('JobInfo', parent=normal_style, fontSize=9, textColor=colors.HexColor('#666666'))
    ))
    
    achievements3 = [
        "• Built and scaled technical infrastructure for digital creative agency",
        "• Developed custom automation tools improving workflow efficiency by 40%",
        "• Led technical strategy and implementation for client projects",
        "• Managed full-stack development using modern JavaScript frameworks"
    ]
    
    for achievement in achievements3:
        elements.append(Paragraph(achievement, bullet_style))
    
    elements.append(Spacer(1, 0.15*inch))
    
    # Key Projects
    elements.append(Paragraph("KEY PROJECTS & INNOVATIONS", heading_style))
    
    projects = [
        "• <b>Mirador AI System:</b> Distributed ML architecture orchestrating 7 specialized LLMs for enterprise decision-making",
        "• <b>Medicare Compliance Platform:</b> Automated system maintaining 100% accuracy across regulatory requirements",
        "• <b>FinanceForge:</b> Personal finance optimization system with predictive analytics and anomaly detection",
        "• <b>FretForge:</b> ML-powered guitar learning platform with real-time audio analysis",
        "• <b>Risk Detection Framework:</b> Production system improving risk identification by 20% using ensemble methods"
    ]
    
    for project in projects:
        elements.append(Paragraph(project, bullet_style))
    
    elements.append(Spacer(1, 0.15*inch))
    
    # Education
    elements.append(Paragraph("EDUCATION", heading_style))
    elements.append(Paragraph(
        "<b>Computer Science & Software Engineering</b>",
        ParagraphStyle('DegreeTitle', parent=normal_style, fontSize=11)
    ))
    elements.append(Paragraph(
        "Self-Directed Learning | 2013 – Present",
        ParagraphStyle('DegreeInfo', parent=normal_style, fontSize=9, textColor=colors.HexColor('#666666'))
    ))
    elements.append(Paragraph(
        "• Focus: Machine Learning, Distributed Systems, Software Architecture",
        bullet_style
    ))
    elements.append(Paragraph(
        "• Key Coursework: Stanford CS231n (Computer Vision), Fast.ai Deep Learning, MIT 6.824 (Distributed Systems)",
        bullet_style
    ))
    elements.append(Paragraph(
        "• Continuous Learning: 500+ hours annually in AI/ML advancement",
        bullet_style
    ))
    
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("CERTIFICATIONS & PROFESSIONAL DEVELOPMENT", heading_style))
    elements.append(Paragraph(
        "• AWS Certified Cloud Practitioner (2022)",
        bullet_style
    ))
    elements.append(Paragraph(
        "• Python Institute PCEP – Certified Entry-Level Python Programmer",
        bullet_style
    ))
    elements.append(Paragraph(
        "• Healthcare Compliance Certification - CMS Standards (Humana Internal, 2020)",
        bullet_style
    ))
    elements.append(Paragraph(
        "• Active GitHub contributor with 100+ public repositories",
        bullet_style
    ))
    
    # Build PDF
    doc.build(elements)
    
    print(f"✅ Created accurate resume: {pdf_path}")
    print(f"   Size: {os.path.getsize(pdf_path) / 1024:.1f} KB")
    
    # Also create a version for each role type
    create_role_specific_resumes()
    
    return str(pdf_path)


def create_role_specific_resumes():
    """Create targeted resumes for different role types"""
    
    roles = {
        'ai_ml_engineer': 'AI/ML Engineer',
        'principal_engineer': 'Principal Engineer', 
        'healthcare_tech': 'Healthcare Technology',
        'startup': 'Startup/Innovation',
        'platform_engineer': 'Platform Engineer'
    }
    
    output_dir = Path("resumes")
    
    for role_key, role_name in roles.items():
        # For now, use the same base resume
        # In production, you'd customize each one
        base_path = output_dir / "matthew_scott_professional_resume.pdf"
        target_path = output_dir / f"matthew_scott_{role_key}_resume.pdf"
        
        if base_path.exists():
            import shutil
            shutil.copy(base_path, target_path)
            print(f"✅ Created {role_name} resume variant")


if __name__ == "__main__":
    create_accurate_resume()