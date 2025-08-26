#!/usr/bin/env python3
"""
Find and Apply to Best ML/AI Engineering Positions
Searches existing database for top matches and helps apply
"""

import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

def find_best_ml_jobs(limit=10):
    """Find the best ML/AI engineering positions from database"""
    print("\n🔍 Finding Best ML/AI Engineering Positions...")
    print("=" * 60)
    
    db_path = Path("unified_platform.db")
    if not db_path.exists():
        print("❌ Database not found")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find ML/AI positions from top companies
    query = """
    SELECT DISTINCT
        job_id,
        company,
        title,
        location,
        remote_option,
        salary_range,
        url,
        description,
        company_email,
        relevance_score
    FROM jobs
    WHERE (
        LOWER(title) LIKE '%ml%' OR
        LOWER(title) LIKE '%machine learning%' OR
        LOWER(title) LIKE '%ai%' OR
        LOWER(title) LIKE '%artificial intelligence%' OR
        LOWER(title) LIKE '%data scien%' OR
        LOWER(title) LIKE '%deep learn%' OR
        LOWER(title) LIKE '%neural%' OR
        company IN ('Anthropic', 'OpenAI', 'Scale AI', 'Figma', 'Plaid', 
                    'Airtable', 'Temporal Technologies', 'Zocdoc', 'Doximity')
    )
    AND applied != 1
    ORDER BY 
        CASE 
            WHEN company = 'Anthropic' THEN 1
            WHEN company = 'OpenAI' THEN 2
            WHEN company = 'Scale AI' THEN 3
            WHEN company = 'Google' THEN 4
            WHEN company = 'Meta' THEN 5
            ELSE 6
        END,
        relevance_score DESC
    LIMIT ?
    """
    
    cursor.execute(query, (limit * 2,))  # Get extra to filter
    jobs = cursor.fetchall()
    
    # Process and score jobs
    scored_jobs = []
    for job in jobs:
        job_dict = {
            'job_id': job[0],
            'company': job[1],
            'position': job[2],
            'location': job[3],
            'remote_option': job[4],
            'salary_range': job[5],
            'url': job[6],
            'description': job[7] or '',
            'company_email': job[8],
            'relevance_score': job[9]
        }
        
        # Calculate match score
        score = calculate_match_score(job_dict)
        job_dict['match_score'] = score
        scored_jobs.append(job_dict)
    
    # Sort by match score and take top N
    scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    best_jobs = scored_jobs[:limit]
    
    print(f"\n✅ Found {len(best_jobs)} top ML/AI positions:")
    print("\n" + "─" * 60)
    
    for i, job in enumerate(best_jobs, 1):
        print(f"\n{i}. {job['position']} at {job['company']}")
        print(f"   📍 Location: {job['location'] or 'Not specified'}")
        if job['remote_option']:
            print(f"   🏠 Remote: {job['remote_option']}")
        if job['salary_range']:
            print(f"   💰 Salary: {job['salary_range']}")
        print(f"   🎯 Match Score: {job['match_score']:.0%}")
        if job['company_email']:
            print(f"   📧 Email: {job['company_email']}")
        if job['url']:
            print(f"   🔗 URL: {job['url'][:60]}...")
    
    conn.close()
    return best_jobs

def calculate_match_score(job):
    """Calculate match score for a job"""
    score = 0.0
    
    # Position matching (40%)
    position_lower = job['position'].lower()
    ml_keywords = ['ml', 'machine learning', 'ai', 'artificial intelligence', 
                   'deep learning', 'neural', 'nlp', 'computer vision']
    senior_keywords = ['senior', 'staff', 'principal', 'lead']
    
    # Check for ML keywords
    ml_match = sum(1 for kw in ml_keywords if kw in position_lower)
    score += (ml_match / len(ml_keywords)) * 0.3
    
    # Bonus for senior positions
    if any(kw in position_lower for kw in senior_keywords):
        score += 0.1
    
    # Company tier (30%)
    top_companies = ['anthropic', 'openai', 'google', 'meta', 'scale ai']
    good_companies = ['figma', 'plaid', 'airtable', 'stripe', 'netflix']
    
    company_lower = job['company'].lower()
    if any(c in company_lower for c in top_companies):
        score += 0.3
    elif any(c in company_lower for c in good_companies):
        score += 0.2
    else:
        score += 0.1
    
    # Remote preference (20%)
    if job['remote_option']:
        if 'remote' in str(job['remote_option']).lower():
            score += 0.2
        else:
            score += 0.1
    
    # Salary (10%)
    if job['salary_range']:
        salary_str = str(job['salary_range'])
        if any(s in salary_str for s in ['150', '160', '170', '180', '190', '200', '250']):
            score += 0.1
    
    return min(score, 1.0)

def create_application_package(job):
    """Create tailored application package for a job"""
    
    # Generate tailored cover letter
    cover_letter = f"""Dear Hiring Team at {job['company']},

I am writing to express my strong interest in the {job['position']} position at {job['company']}. With my proven track record of building production ML systems that have generated over $1.2M in value, I am excited about the opportunity to contribute to your team.

My recent accomplishments include:

• **Job Intelligence Platform**: Built an end-to-end ML platform with TensorFlow 2.20, achieving 92% salary prediction accuracy and 0.4+ vector similarity matching. The system processes 1000+ jobs daily using advanced NLP and clustering algorithms.

• **Mirador AI Platform**: Architected a 79+ model orchestration system achieving 99.3% success rate, processing 250K+ requests monthly. Implemented RAG pipelines, vector databases, and multi-modal AI capabilities.

• **Production Impact**: At Humana (10 years), I built ML systems that automated Medicare compliance workflows, saving $1.2M annually while maintaining 100% CMS adherence.

My technical expertise aligns perfectly with your requirements:
- Deep experience with TensorFlow, PyTorch, and modern ML frameworks
- Production deployment of LLMs, embeddings, and neural architectures  
- Strong foundation in MLOps, distributed systems, and scalable infrastructure
- Proven ability to translate complex ML research into business value

I am particularly drawn to {job['company']} because of your work in advancing AI capabilities. I believe my combination of technical depth and business impact would make me a valuable addition to your team.

I would welcome the opportunity to discuss how my experience building production ML systems can contribute to {job['company']}'s continued success.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77
"""
    
    return {
        'cover_letter': cover_letter,
        'resume_path': '/Users/matthewscott/Desktop/MATTHEW_SCOTT_AI_ML_ENGINEER_2025.pdf',
        'email_subject': f"Application for {job['position']} - Matthew Scott"
    }

def prepare_applications(jobs):
    """Prepare applications for selected jobs"""
    print("\n📮 Preparing Application Packages...")
    print("=" * 60)
    
    applications = []
    for job in jobs:
        package = create_application_package(job)
        
        app_data = {
            'job': job,
            'cover_letter': package['cover_letter'],
            'resume_path': package['resume_path'],
            'subject': package['email_subject'],
            'to_email': job['company_email'] or f"careers@{job['company'].lower().replace(' ', '')}.com"
        }
        
        applications.append(app_data)
        
        # Save to file with unique identifier
        position_slug = job['position'][:30].replace(' ', '_').replace('/', '_').replace(',', '')
        filename = f"application_{job['company'].replace(' ', '_')}_{position_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(app_data, f, indent=2)
        
        print(f"✅ Prepared application for {job['company']} - {job['position']}")
        print(f"   Saved to: {filename}")
    
    return applications

def show_next_steps(applications):
    """Show next steps for sending applications"""
    print("\n🎯 Next Steps to Apply:")
    print("=" * 60)
    
    print("\nOption 1: Send via Guided Apply (Recommended)")
    print("─" * 40)
    print("python3 guided_apply.py")
    print("This will walk you through each application interactively")
    
    print("\nOption 2: Send Specific Applications")
    print("─" * 40)
    for i, app in enumerate(applications[:3], 1):
        print(f"\n{i}. {app['job']['company']} - {app['job']['position']}")
        print(f"   Email: {app['to_email']}")
        print(f"   Subject: {app['subject']}")
    
    print("\nOption 3: Review Applications First")
    print("─" * 40)
    print("python3 preview_applications.py")
    print("Review all prepared applications before sending")
    
    print("\n💡 Tips:")
    print("• Applications are saved as JSON files for review")
    print("• The system tracks all sent applications automatically")
    print("• Responses are monitored via Gmail OAuth")
    print("• Check status with: python3 main.py status")

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("🚀 ML/AI ENGINEER JOB FINDER & APPLICATOR")
    print("=" * 60)
    
    # Find best jobs
    best_jobs = find_best_ml_jobs(limit=10)
    
    if not best_jobs:
        print("\n❌ No suitable jobs found")
        return
    
    # Check for command line argument for non-interactive mode
    if len(sys.argv) > 1:
        if sys.argv[1] == '--auto':
            # Auto-select top 5 ML engineering positions
            ml_positions = [job for job in best_jobs if 'machine learning' in job['position'].lower()]
            selected_jobs = ml_positions[:5] if ml_positions else best_jobs[:5]
            print(f"\n✅ Auto-selected {len(selected_jobs)} ML engineering positions")
        else:
            selected_jobs = best_jobs[:3]
    else:
        # Ask user to select jobs to apply to
        print("\n" + "=" * 60)
        print("📋 SELECT JOBS TO APPLY TO")
        print("=" * 60)
        print("\nEnter job numbers to apply to (comma-separated, or 'all' for all):")
        print("Example: 1,2,3 or all")
        print("Press Enter to select top 3 by default")
        
        try:
            selection = input("\nYour selection: ").strip()
        except EOFError:
            # Running in non-interactive mode
            selection = ''
        
        if selection.lower() == 'all':
            selected_jobs = best_jobs
        elif selection == '':
            selected_jobs = best_jobs[:3]
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_jobs = [best_jobs[i] for i in indices if 0 <= i < len(best_jobs)]
            except:
                print("Invalid selection, using top 3")
                selected_jobs = best_jobs[:3]
    
    print(f"\n✅ Selected {len(selected_jobs)} jobs to apply to")
    
    # Prepare applications
    applications = prepare_applications(selected_jobs)
    
    # Show next steps
    show_next_steps(applications)
    
    print("\n" + "=" * 60)
    print("✨ Ready to apply to top ML/AI positions!")
    print("=" * 60)

if __name__ == "__main__":
    main()