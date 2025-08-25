# Resume Selection Logic
import random
import os

RESUME_DIR = "/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/resumes"

def select_resume_for_job(job_info):
    """Select appropriate resume based on job requirements"""
    
    resumes = {
        'technical': ['technical_deep_dive.pdf', 'master_resume_-_all_keywords.pdf'],
        'leadership': ['executive_leadership.pdf', 'master_resume_-_all_keywords.pdf'],
        'general': ['master_resume_-_all_keywords.pdf']
    }
    
    # Analyze job title/description
    job_text = f"{job_info.get('position', '')} {job_info.get('description', '')}".lower()
    
    if any(word in job_text for word in ['senior', 'lead', 'principal', 'director', 'manager']):
        category = 'leadership'
    elif any(word in job_text for word in ['engineer', 'developer', 'ml', 'ai', 'data']):
        category = 'technical'
    else:
        category = 'general'
    
    # Get available resumes for category
    available = []
    for resume_name in resumes.get(category, resumes['general']):
        resume_path = os.path.join(RESUME_DIR, resume_name)
        if os.path.exists(resume_path):
            available.append(resume_path)
    
    # Fallback to any available resume
    if not available:
        for file in os.listdir(RESUME_DIR):
            if file.endswith('.pdf'):
                available.append(os.path.join(RESUME_DIR, file))
    
    if available:
        return random.choice(available)
    return None
