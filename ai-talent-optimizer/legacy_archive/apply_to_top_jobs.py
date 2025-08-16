#!/usr/bin/env python3
"""
Apply to Top Priority Jobs
Sends applications to highest-value positions
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from utils.config import Config
from data.models import init_database, Job, Application

def generate_tailored_cover_letter(company, position, salary):
    """Generate personalized cover letter for each company"""
    
    config = Config()
    
    # Company-specific insights
    company_insights = {
        "Genesis AI": "I'm particularly excited about Genesis AI's focus on foundational AI research and the opportunity to work on cutting-edge ML systems.",
        "Inworld AI": "Inworld's work on AI-driven virtual characters aligns perfectly with my experience building distributed systems with 78 specialized models.",
        "Adyen": "Adyen's global payment platform would benefit from my expertise in building high-reliability systems processing thousands of concurrent operations.",
        "Lime": "My experience optimizing ML systems for 90% cost reduction would be valuable for Lime's urban mobility challenges.",
        "Thumbtack": "My infrastructure expertise, demonstrated through building a platform with 117 Python modules, aligns with Thumbtack's ML infrastructure needs."
    }
    
    insight = company_insights.get(company, f"I'm impressed by {company}'s innovative approach and believe my skills would add significant value.")
    
    letter = f"""Dear Hiring Team at {company},

I am writing to express my strong interest in the {position} position at {company}. With over 10 years of experience at Humana, where I've architected enterprise-scale AI systems while building a comprehensive platform with 117 Python modules, I am excited about the opportunity to bring my expertise to your team.

{insight}

As a Senior Risk Management Professional II at Humana, I've delivered significant value through:
• Building distributed ML systems with 78 specialized models for complex decision-making
• Developing production AI systems serving 50M+ users across healthcare systems
• Reducing LLM inference costs by 90% through custom adaptive quantization
• Maintaining 100% compliance across 500+ Medicare regulatory pages using AI

What sets me apart is that I've been operating at a Principal level while maintaining my demanding day job. The enterprise platform I've built processes thousands of operations daily with 99.9% uptime, demonstrating the kind of impact I could bring to {company}.

My unique combination of healthcare domain expertise and cutting-edge AI implementation makes me an ideal fit for this role. I've already proven my ability to deliver at the level this position requires, as evidenced by the scale and complexity of systems I've built.

I would welcome the opportunity to discuss how my experience scaling AI systems at a Fortune 50 company can contribute to {company}'s continued success.

{config.EMAIL_SIGNATURE}
"""
    
    return letter

def apply_to_jobs():
    """Apply to top 5 priority jobs"""
    
    config = Config()
    session = init_database()
    
    print("🚀 Starting applications to top priority jobs...")
    
    # Get top 5 jobs
    top_jobs = session.query(Job).filter(
        Job.max_salary >= 450000
    ).order_by(Job.max_salary.desc()).limit(5).all()
    
    applications_sent = []
    
    for job in top_jobs:
        print(f"\n📧 Applying to {job.company} - {job.position}")
        print(f"   💰 Salary: ${job.max_salary:,}")
        
        # Check if already applied
        existing = session.query(Application).filter_by(job_id=job.id).first()
        if existing:
            print(f"   ✅ Already applied on {existing.applied_date}")
            continue
        
        # Generate cover letter
        cover_letter = generate_tailored_cover_letter(
            job.company, 
            job.position,
            job.max_salary
        )
        
        # Create application record
        application = Application(
            job_id=job.id,
            applied_date=datetime.utcnow(),
            resume_version="matthew_scott_ai_ml_resume.pdf",
            cover_letter_version=f"{job.company.lower().replace(' ', '_')}_cover.txt",
            application_method="email",
            status='prepared',
            notes=f"Target salary: ${job.max_salary:,}"
        )
        session.add(application)
        
        # Save cover letter
        cover_letter_path = f"output/cover_letters/{job.company.lower().replace(' ', '_')}_cover_letter.txt"
        Path("output/cover_letters").mkdir(parents=True, exist_ok=True)
        with open(cover_letter_path, 'w') as f:
            f.write(cover_letter)
        
        print(f"   ✅ Cover letter saved: {cover_letter_path}")
        print(f"   ✅ Application prepared and tracked")
        
        applications_sent.append({
            'company': job.company,
            'position': job.position,
            'salary': job.max_salary,
            'cover_letter': cover_letter_path
        })
    
    session.commit()
    
    # Summary
    print("\n" + "="*60)
    print("📊 APPLICATION SUMMARY")
    print("="*60)
    print(f"Applications prepared: {len(applications_sent)}")
    
    for app in applications_sent:
        print(f"\n✅ {app['company']}")
        print(f"   Position: {app['position']}")
        print(f"   Salary: ${app['salary']:,}")
        print(f"   Cover Letter: {app['cover_letter']}")
    
    print("\n📧 NEXT STEPS:")
    print("1. Review cover letters in output/cover_letters/")
    print("2. Send applications via email or apply through company websites")
    print("3. Track responses using: python3 cli/main.py email --check-responses")
    
    # Create email template
    email_template = f"""
Subject: Principal/Staff ML Engineer - Matthew Scott

Dear Hiring Team,

Please find attached my resume for the [POSITION] role at [COMPANY].

[INSERT COVER LETTER HERE]

Best regards,
Matthew Scott
"""
    
    with open("output/email_template.txt", 'w') as f:
        f.write(email_template)
    print("\n📄 Email template saved: output/email_template.txt")
    
    return applications_sent

if __name__ == "__main__":
    apply_to_jobs()