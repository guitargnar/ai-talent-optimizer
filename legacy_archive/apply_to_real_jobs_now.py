#!/usr/bin/env python3
"""
Apply to REAL $400K+ Jobs - Generate materials and provide direct application links
"""

import sqlite3
from datetime import datetime
import webbrowser
import os

def get_top_jobs(limit=5):
    """Get top priority real jobs from database"""
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT company, position, url, min_salary, max_salary, notes
        FROM principal_jobs
        WHERE applied = 0
        ORDER BY max_salary DESC
        LIMIT ?
    """, (limit,))
    
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def generate_cover_letter(company, position, salary_range):
    """Generate targeted cover letter for principal/staff position"""
    
    # Company-specific highlights
    company_specific = {
        "Meta": "Having followed Meta's evolution in AI, particularly your work on LLaMA and generative AI systems, I'm excited about the opportunity to contribute to your next generation of AI products.",
        "Google": "Google's commitment to advancing AI for healthcare aligns perfectly with my experience leading ML initiatives that delivered $1.2M in savings at Humana through predictive healthcare analytics.",
        "Inworld AI": "Your work on AI characters and immersive experiences represents the frontier of human-AI interaction. My experience building scalable ML platforms serving 50M+ users positions me well to contribute to Inworld's growth.",
        "Reddit": "Reddit's scale challenges in embedding generation and recommendation systems align with my expertise in building high-throughput ML systems processing 100K+ requests daily.",
        "Tempus": "Having worked extensively in healthcare AI at Humana, I understand the critical importance of precision medicine. Your mission to bring AI to cancer care deeply resonates with my commitment to impactful ML applications.",
        "Abridge": "Your AI-powered medical conversation platform addresses a critical need in healthcare. My experience with NLP systems and healthcare data at Humana makes me uniquely qualified for this role.",
    }
    
    cover_letter = f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {position} position at {company}. With over 10 years of experience building production ML systems and a proven track record of delivering multi-million dollar impact through AI initiatives, I am excited about the opportunity to contribute to your team at the principal/staff level.

{company_specific.get(company, f"I've been following {company}'s innovative work in AI/ML and am impressed by your technical leadership and vision in the space.")}

My qualifications for this senior role include:

Technical Leadership & Impact:
• Led ML initiatives at Humana that delivered $1.2M in verified savings through predictive analytics
• Architected and deployed ML platforms serving 50M+ users with 99.9% uptime
• Transformed risk prediction accuracy by 47% using advanced neural architectures
• Built and mentored teams of 5-10 ML engineers, establishing best practices and technical standards

Deep Technical Expertise:
• 10+ years Python, with extensive experience in PyTorch, TensorFlow, and JAX
• Designed distributed training systems handling 100TB+ datasets
• Expert in transformer architectures, GNNs, and large-scale embedding systems
• Published research on neural architecture search and AutoML optimization

Principal-Level Contributions:
• Define technical roadmaps aligning ML initiatives with business objectives
• Lead architecture reviews and establish engineering standards
• Mentor senior engineers and drive technical excellence across teams
• Bridge technical complexity with business stakeholder communication

Healthcare & Enterprise AI Experience:
• Reduced Medicare Advantage prediction errors by 31% through ensemble methods
• Implemented HIPAA-compliant ML pipelines processing sensitive health data
• Achieved 89% accuracy in provider network optimization
• Successfully working remotely since 2015, proven ability to lead distributed teams

The {position} role at {company} presents an exciting opportunity to apply my experience at the intersection of cutting-edge ML research and production systems. I'm particularly drawn to the technical challenges of {salary_range} and the opportunity to work with world-class engineers on problems that impact millions of users.

I would welcome the opportunity to discuss how my experience in building and scaling ML systems can contribute to {company}'s continued success. Thank you for considering my application.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77
github.com/mds1"""
    
    return cover_letter

def generate_application_package(job):
    """Generate complete application package for a job"""
    company, position, url, min_sal, max_sal, notes = job
    salary_range = f"${min_sal:,}-${max_sal:,}"
    
    print(f"\n{'='*70}")
    print(f"📋 APPLICATION PACKAGE: {company}")
    print(f"{'='*70}")
    print(f"Position: {position}")
    print(f"Salary Range: {salary_range}")
    print(f"Application URL: {url}")
    
    # Generate cover letter
    cover_letter = generate_cover_letter(company, position, salary_range)
    
    # Save to file
    safe_filename = f"{company}_{position}".replace(" ", "_").replace("/", "_")[:50]
    filename = f"applications_sent/{safe_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"COMPANY: {company}\n")
        f.write(f"POSITION: {position}\n")
        f.write(f"SALARY RANGE: {salary_range}\n")
        f.write(f"APPLICATION URL: {url}\n")
        f.write(f"GENERATED: {datetime.now().isoformat()}\n")
        f.write(f"\n{'='*70}\n")
        f.write("COVER LETTER:\n")
        f.write(f"{'='*70}\n\n")
        f.write(cover_letter)
        f.write(f"\n\n{'='*70}\n")
        f.write("KEY POINTS TO EMPHASIZE IN APPLICATION:\n")
        f.write(f"{'='*70}\n")
        f.write("1. 10+ years ML experience with proven $1.2M impact\n")
        f.write("2. Healthcare AI expertise (perfect for Tempus, Abridge, Oscar)\n")
        f.write("3. Scale experience: 50M+ users, 100K+ requests/day\n")
        f.write("4. Principal-level skills: Technical leadership, mentoring, architecture\n")
        f.write("5. Remote work success since 2015\n")
    
    print(f"\n✅ Application materials saved to: {filename}")
    
    # Mark as applied in database
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE principal_jobs 
        SET applied = 1, applied_at = CURRENT_TIMESTAMP
        WHERE company = ? AND position = ?
    """, (company, position))
    conn.commit()
    conn.close()
    
    return filename, url

def main():
    print("🚀 REAL $400K+ JOB APPLICATION SYSTEM")
    print("="*70)
    print("Generating application materials for top opportunities...")
    
    # Get top jobs
    jobs = get_top_jobs(5)
    
    if not jobs:
        print("❌ No jobs found in database")
        return
    
    application_urls = []
    
    for job in jobs:
        filename, url = generate_application_package(job)
        application_urls.append((job[0], job[1], url, filename))
    
    print("\n" + "="*70)
    print("🎯 READY TO APPLY - CLICK THESE LINKS:")
    print("="*70)
    
    for i, (company, position, url, filename) in enumerate(application_urls, 1):
        print(f"\n{i}. {company} - {position}")
        print(f"   📄 Cover Letter: {filename}")
        print(f"   🔗 APPLY NOW: {url}")
    
    print("\n" + "="*70)
    print("📝 INSTRUCTIONS:")
    print("="*70)
    print("1. Open each application URL above")
    print("2. Copy the cover letter from the saved file")
    print("3. Upload your resume: resumes/matthew_scott_ai_ml_resume.pdf")
    print("4. Fill out the application form")
    print("5. Submit!")
    print("\n💡 TIP: Apply to all 5 within the next hour for best results")
    print("🎯 These are REAL jobs with REAL URLs - apply immediately!")
    
    # Offer to open URLs
    print("\n" + "="*70)
    open_browser = input("Open all application URLs in browser? (yes/no): ")
    if open_browser.lower() == 'yes':
        for company, position, url, _ in application_urls:
            print(f"Opening {company} application...")
            webbrowser.open(url)
    
    print("\n✅ Application materials generated for 5 positions")
    print("🚀 Go apply now while positions are still open!")

if __name__ == "__main__":
    main()