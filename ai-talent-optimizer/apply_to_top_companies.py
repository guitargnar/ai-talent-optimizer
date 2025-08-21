#!/usr/bin/env python3
"""
Apply to Top ML/AI Companies Beyond Anthropic
Targets Scale AI, Plaid, Figma, and other top companies
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

def get_top_ml_positions():
    """Get ML positions from top companies"""
    
    db_path = Path('data/unified_jobs.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get positions from Scale AI, Plaid, Figma
    query = """
    SELECT DISTINCT
        job_id,
        company,
        position,
        location,
        remote_option,
        salary_range,
        url,
        company_email
    FROM jobs
    WHERE company IN ('Scale AI', 'Plaid', 'Figma', 'Zocdoc', 'Doximity')
    AND (
        LOWER(position) LIKE '%ml%' OR
        LOWER(position) LIKE '%machine learning%' OR
        LOWER(position) LIKE '%ai%' OR
        LOWER(position) LIKE '%engineer%' OR
        LOWER(position) LIKE '%data%'
    )
    AND applied != 1
    ORDER BY 
        CASE 
            WHEN company = 'Scale AI' THEN 1
            WHEN company = 'Plaid' THEN 2
            WHEN company = 'Figma' THEN 3
            ELSE 4
        END
    LIMIT 10
    """
    
    cursor.execute(query)
    jobs = cursor.fetchall()
    conn.close()
    
    return [
        {
            'job_id': job[0],
            'company': job[1],
            'position': job[2],
            'location': job[3],
            'remote_option': job[4],
            'salary_range': job[5],
            'url': job[6],
            'company_email': job[7] or f"careers@{job[1].lower().replace(' ', '')}.com"
        }
        for job in jobs
    ]

def create_tailored_cover_letter(job):
    """Create company-specific cover letter"""
    
    company_specific = {
        'Scale AI': """I'm particularly excited about Scale AI's mission to accelerate AI development through better data. Your work on RLHF and model evaluation aligns perfectly with my experience building production ML systems that have processed millions of data points with 99.3% accuracy.""",
        
        'Plaid': """Plaid's financial infrastructure powers the apps I use daily, and I'm passionate about applying ML to make financial services more accessible. My experience building FinanceForge and working with sensitive healthcare data at Humana has prepared me to handle the unique challenges of financial ML systems.""",
        
        'Figma': """As someone who has built collaborative AI tools, I deeply appreciate Figma's vision for design collaboration. I'm excited about the opportunity to apply ML to enhance creative workflows, having built similar real-time systems processing 250K+ requests monthly.""",
        
        'Zocdoc': """Having spent 10 years at Humana working on healthcare technology, I understand the complexities of medical systems. I'm excited about Zocdoc's mission to simplify healthcare access and would love to apply my ML expertise to improve patient-provider matching.""",
        
        'Doximity': """Your platform's impact on medical collaboration resonates with my healthcare background at Humana. I've built ML systems that ensure 100% Medicare compliance while processing complex medical data, experience directly applicable to Doximity's physician network."""
    }
    
    company_paragraph = company_specific.get(job['company'], 
        f"I'm excited about {job['company']}'s innovative work and believe my experience building production ML systems would be valuable to your team.")
    
    cover_letter = f"""Dear Hiring Team at {job['company']},

I am writing to express my strong interest in the {job['position']} position. With my proven track record of building production ML systems that have generated over $1.2M in value, I am excited about the opportunity to contribute to {job['company']}'s mission.

{company_paragraph}

My recent technical accomplishments include:

• **Job Intelligence Platform**: Built an end-to-end ML platform with TensorFlow 2.20, achieving 92% salary prediction accuracy using advanced NLP and clustering algorithms processing 1000+ jobs daily.

• **Mirador AI Platform**: Architected a 79+ model orchestration system achieving 99.3% success rate, implementing RAG pipelines, vector databases, and multi-modal AI capabilities serving 250K+ requests monthly.

• **Enterprise Impact**: During my 10 years at Humana, I built ML systems that automated Medicare compliance workflows, saving $1.2M annually while maintaining 100% CMS adherence.

My technical expertise includes:
- Deep proficiency in TensorFlow, PyTorch, and modern ML frameworks
- Production deployment of LLMs, embeddings, and neural architectures
- Strong foundation in MLOps, distributed systems, and scalable infrastructure
- Proven ability to translate ML research into measurable business value

I would welcome the opportunity to discuss how my experience can contribute to {job['company']}'s continued success in the {job['position']} role.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77
github.com/guitargnar
"""
    
    return cover_letter

def prepare_applications():
    """Prepare applications for top companies"""
    
    print("\n🔍 Finding Top ML Positions...")
    print("=" * 60)
    
    jobs = get_top_ml_positions()
    
    if not jobs:
        print("❌ No new positions found")
        return []
    
    print(f"✅ Found {len(jobs)} positions:\n")
    
    applications = []
    for i, job in enumerate(jobs[:5], 1):  # Limit to 5
        print(f"{i}. {job['position']} at {job['company']}")
        print(f"   📍 {job['location'] or 'Location not specified'}")
        
        # Create application package
        cover_letter = create_tailored_cover_letter(job)
        
        app_data = {
            'job': job,
            'cover_letter': cover_letter,
            'resume_path': '/Users/matthewscott/Desktop/MATTHEW_SCOTT_AI_ML_ENGINEER_2025.pdf',
            'subject': f"Application for {job['position']} - Matthew Scott",
            'to_email': job['company_email']
        }
        
        # Save to file
        position_slug = job['position'][:30].replace(' ', '_').replace('/', '_').replace(',', '')
        filename = f"application_{job['company'].replace(' ', '_')}_{position_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(app_data, f, indent=2)
        
        applications.append(filename)
        print(f"   ✅ Saved: {filename}\n")
    
    return applications

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("🚀 APPLYING TO TOP ML/AI COMPANIES")
    print("=" * 60)
    
    # Prepare applications
    app_files = prepare_applications()
    
    if app_files:
        print("\n" + "=" * 60)
        print("✅ APPLICATIONS READY")
        print("=" * 60)
        print(f"\n{len(app_files)} applications prepared for:")
        print("• Scale AI - AI Infrastructure roles")
        print("• Plaid - Financial ML positions")
        print("• Figma - Design ML opportunities")
        print("• Healthcare tech companies")
        
        print("\n📮 To send these applications:")
        print("python3 send_prepared_applications.py")
        
        print("\n💡 These companies are known for:")
        print("• Competitive salaries ($180-250K)")
        print("• Strong engineering cultures")
        print("• ML/AI focus and innovation")
        print("• Remote-friendly policies")
    
    print("\n✨ Good luck with your applications!")

if __name__ == "__main__":
    main()