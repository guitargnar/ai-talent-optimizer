#!/usr/bin/env python3
"""
Resume Knowledge Base - Stores resume content and variations
"""

class ResumeKnowledgeBase:
    """Manage resume variations and content"""
    
    def __init__(self):
        self.base_resume = {
            'name': 'Matthew David Scott',
            'email': 'matthewdscott7@gmail.com',
            'phone': '(502) 345-0525',
            'linkedin': 'linkedin.com/in/mscott77',
            'summary': 'Senior AI/ML professional with 10+ years of experience and proven track record of delivering $1.2M in AI-driven savings at Humana.',
            'skills': ['Python', 'Machine Learning', 'Healthcare AI', 'Distributed Systems']
        }
    
    def get_resume_for_job(self, job_title, company):
        """Generate customized resume for specific job"""
        # For now, return base resume
        return self.base_resume
    
    def get_skills_for_role(self, role_type):
        """Get relevant skills for role type"""
        return self.base_resume['skills']
