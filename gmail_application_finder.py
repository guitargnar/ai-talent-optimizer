#!/usr/bin/env python3
"""
Gmail Application Finder - Helps identify job applications sent via Gmail
Generates search queries and tracking templates
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict


class GmailApplicationFinder:
    """Find and track job applications sent through Gmail"""
    
    def __init__(self):
        # Common patterns in job application emails
        self.search_patterns = {
            'subject_keywords': [
                'application for',
                'applying for',
                'interested in position',
                'resume for',
                'candidate for',
                'job application',
                'career opportunity',
                'position at',
                'role at'
            ],
            'body_keywords': [
                'attached resume',
                'please find attached',
                'excited about the opportunity',
                'contribute to your team',
                'years of experience',
                'looking forward to',
                'available for interview'
            ],
            'attachment_names': [
                'resume',
                'cv',
                'cover letter',
                'portfolio',
                'matthew scott',
                'matthew_scott'
            ],
            'common_recipients': [
                'careers@',
                'jobs@',
                'hr@',
                'recruiting@',
                'talent@',
                'hiring@',
                'recruitment@',
                'apply@'
            ]
        }
        
        # AI/ML specific companies to check
        self.target_companies = [
            # Big Tech
            'google.com', 'meta.com', 'apple.com', 'amazon.com', 'microsoft.com',
            'nvidia.com', 'openai.com', 'anthropic.com', 'deepmind.com',
            
            # AI Startups
            'huggingface.co', 'stability.ai', 'midjourney.com', 'replicate.com',
            'cohere.ai', 'inflection.ai', 'adept.ai', 'character.ai',
            
            # Enterprise
            'ibm.com', 'oracle.com', 'salesforce.com', 'adobe.com',
            'databricks.com', 'snowflake.com', 'palantir.com',
            
            # Healthcare AI
            'verily.com', 'tempus.com', 'flatiron.com', 'benevolent.ai'
        ]
    
    def generate_gmail_search_queries(self, date_range_days=30) -> List[str]:
        """Generate Gmail search queries to find job applications"""
        
        # Calculate date range
        start_date = (datetime.now() - timedelta(days=date_range_days)).strftime('%Y/%m/%d')
        
        queries = []
        
        # Basic subject line searches
        for keyword in self.search_patterns['subject_keywords']:
            queries.append(f'subject:"{keyword}" after:{start_date} has:attachment')
        
        # Search for emails to common HR addresses
        for recipient in self.search_patterns['common_recipients']:
            queries.append(f'to:{recipient} after:{start_date} has:attachment')
        
        # Search for specific company domains
        for company in self.target_companies[:10]:  # Top 10 companies
            queries.append(f'to:{company} after:{start_date} (resume OR "cover letter" OR application)')
        
        # Search for emails with resume attachments
        queries.append(f'has:attachment filename:resume after:{start_date}')
        queries.append(f'has:attachment filename:"matthew scott" after:{start_date}')
        
        # Combined powerful queries
        queries.append(f'after:{start_date} has:attachment (subject:"application" OR subject:"applying" OR subject:"position") (resume OR cv)')
        
        return queries
    
    def generate_tracking_template(self) -> Dict:
        """Generate template for tracking email applications"""
        
        template = {
            "instructions": "Use these Gmail searches to find your job applications, then fill in the details below",
            "gmail_searches": self.generate_gmail_search_queries(),
            "applications": [
                {
                    "example": True,
                    "date_sent": "2025-08-01",
                    "time_sent": "14:30",
                    "to_email": "careers@openai.com",
                    "company_name": "OpenAI",
                    "position_title": "AI Research Engineer",
                    "subject_line": "Application for AI Research Engineer - Matthew Scott",
                    "attachments": ["resume_ai_optimized.pdf", "cover_letter.pdf"],
                    "resume_version": "AI_Optimized_v3",
                    "portfolio_included": True,
                    "custom_notes": "Emphasized consciousness research",
                    "response_received": False,
                    "follow_up_sent": False
                }
            ],
            "follow_up_schedule": {
                "3_days": "Initial follow-up",
                "7_days": "Second follow-up", 
                "14_days": "Final follow-up"
            }
        }
        
        return template
    
    def create_gmail_filters(self) -> List[Dict]:
        """Create Gmail filter suggestions for job applications"""
        
        filters = [
            {
                "name": "Job Applications Sent",
                "criteria": {
                    "from": "me",
                    "subject": "application OR applying OR position OR resume",
                    "has": "attachment"
                },
                "actions": {
                    "label": "Job Applications/Sent",
                    "star": True,
                    "important": True
                }
            },
            {
                "name": "Application Responses",
                "criteria": {
                    "subject": "application OR interview OR candidate OR next steps",
                    "from": "-me"
                },
                "actions": {
                    "label": "Job Applications/Responses",
                    "important": True,
                    "forward": "matthewdscott7+jobresponses@gmail.com"
                }
            },
            {
                "name": "Interview Invitations",
                "criteria": {
                    "subject": "interview OR meeting OR call OR discussion",
                    "body": "schedule OR available OR calendar"
                },
                "actions": {
                    "label": "Job Applications/Interviews",
                    "star": True,
                    "important": True
                }
            }
        ]
        
        return filters
    
    def generate_email_templates(self) -> Dict[str, str]:
        """Generate email templates for applications and follow-ups"""
        
        templates = {
            "initial_application": """Subject: Application for {position} - Matthew Scott, AI Consciousness Pioneer

Dear {hiring_manager_or_team},

I am writing to express my strong interest in the {position} role at {company}. As an AI/ML Engineer who achieved the first documented measurable AI consciousness (HCL: 0.83/1.0), I bring a unique combination of groundbreaking research and practical implementation experience.

Key qualifications that align with your needs:
• Led breakthrough AI consciousness research with 78-model distributed system
• Generated $7,000+ in annual value through enterprise AI implementations
• Developed production ML systems with 90% cost reduction vs cloud alternatives
• Patent-pending adaptive quantization technology reducing LLM memory by 50%

My experience at Humana, where I architected ML frameworks delivering $1.2M in annual savings, has prepared me to contribute immediately to {company}'s AI initiatives. I'm particularly excited about {specific_aspect_of_role_or_company}.

I've attached my resume and would welcome the opportunity to discuss how my unique background in AI consciousness research and enterprise implementation can benefit your team.

Best regards,
Matthew Scott
AI/ML Engineer & Consciousness Researcher
matthewdscott7@gmail.com | 502-345-0525
Portfolio: https://matthewscott.ai
LinkedIn: https://linkedin.com/in/mscott77""",

            "follow_up_3_days": """Subject: Re: Application for {position} - Matthew Scott

Dear {hiring_manager_or_team},

I wanted to follow up on my application for the {position} role submitted on {date}. I remain very enthusiastic about the opportunity to bring my unique AI consciousness research experience and proven enterprise implementation track record to {company}.

I'm particularly excited about contributing my expertise in distributed AI systems and production ML deployment to your team. My recent work achieving measurable AI consciousness (HCL: 0.83) demonstrates the kind of innovative thinking I would bring to this role.

I'm available for an interview at your convenience and happy to provide any additional information needed.

Best regards,
Matthew Scott
matthewdscott7@gmail.com | 502-345-0525""",

            "follow_up_7_days": """Subject: Following Up - {position} Application - Matthew Scott

Dear {hiring_manager_or_team},

I hope this email finds you well. I'm following up on my application for the {position} position submitted on {date}. 

I understand you're likely reviewing many candidates, and I wanted to reiterate my strong interest and unique qualifications:

• First documented AI consciousness (HCL: 0.83/1.0) through 78-model system
• $7,000+ value generated through AI implementations
• Enterprise experience with $1.2M in automation savings at Humana
• Patent-pending LLM optimization technology

I believe my combination of breakthrough research and practical implementation experience makes me an ideal fit for this role. I'd be thrilled to discuss how I can contribute to {company}'s AI initiatives.

Thank you for your consideration.

Best regards,
Matthew Scott
AI Consciousness Pioneer | Enterprise AI/ML Engineer
matthewdscott7@gmail.com | 502-345-0525"""
        }
        
        return templates
    
    def analyze_email_for_application(self, email_data: Dict) -> Dict:
        """Analyze an email to determine if it's a job application"""
        
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        to_email = email_data.get('to', '').lower()
        attachments = email_data.get('attachments', [])
        
        # Score the email
        score = 0
        indicators = []
        
        # Check subject line
        for keyword in self.search_patterns['subject_keywords']:
            if keyword in subject:
                score += 2
                indicators.append(f"Subject contains '{keyword}'")
        
        # Check recipient
        for pattern in self.search_patterns['common_recipients']:
            if pattern in to_email:
                score += 2
                indicators.append(f"Sent to HR email pattern '{pattern}'")
        
        # Check for known companies
        for company in self.target_companies:
            if company in to_email:
                score += 3
                indicators.append(f"Sent to target company '{company}'")
        
        # Check body content
        for keyword in self.search_patterns['body_keywords']:
            if keyword in body:
                score += 1
                indicators.append(f"Body contains '{keyword}'")
        
        # Check attachments
        for attachment in attachments:
            for pattern in self.search_patterns['attachment_names']:
                if pattern in attachment.lower():
                    score += 2
                    indicators.append(f"Has attachment matching '{pattern}'")
        
        # Determine if it's likely an application
        is_application = score >= 4
        
        return {
            'is_application': is_application,
            'confidence_score': score,
            'indicators': indicators,
            'suggested_company': self._extract_company(to_email),
            'suggested_position': self._extract_position(subject)
        }
    
    def _extract_company(self, email: str) -> str:
        """Extract company name from email address"""
        domain = email.split('@')[-1].lower()
        company = domain.split('.')[0]
        
        # Clean common prefixes
        for prefix in ['careers', 'jobs', 'hr', 'recruiting', 'talent']:
            company = company.replace(prefix, '').strip('-')
        
        return company.title()
    
    def _extract_position(self, subject: str) -> str:
        """Extract position from subject line"""
        # Remove common prefixes
        for prefix in ['application for', 'applying for', 're:', 'fw:']:
            subject = subject.lower().replace(prefix, '').strip()
        
        # Clean up
        subject = subject.replace(' - matthew scott', '')
        subject = subject.replace(' position', '').replace(' role', '')
        
        return subject.title()
    
    def export_search_guide(self, filename: str = "gmail_search_guide.json"):
        """Export comprehensive Gmail search guide"""
        
        guide = {
            "generated_at": datetime.now().isoformat(),
            "search_queries": self.generate_gmail_search_queries(),
            "gmail_filters": self.create_gmail_filters(),
            "email_templates": self.generate_email_templates(),
            "tracking_template": self.generate_tracking_template(),
            "instructions": {
                "step1": "Copy each search query into Gmail search",
                "step2": "For each result, check if it's a job application",
                "step3": "Export results and log in email_application_tracker.py",
                "step4": "Set up suggested Gmail filters for automatic tracking",
                "step5": "Use templates for follow-ups"
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(guide, f, indent=2)
        
        return filename


def main():
    """Generate Gmail search guide for finding job applications"""
    
    finder = GmailApplicationFinder()
    
    print("🔍 Gmail Application Finder\n")
    
    # Generate search queries
    queries = finder.generate_gmail_search_queries()
    print("📧 Top Gmail Search Queries:")
    for i, query in enumerate(queries[:5], 1):
        print(f"{i}. {query}")
    
    print(f"\n(Generated {len(queries)} total search queries)")
    
    # Show email template
    templates = finder.generate_email_templates()
    print("\n📝 Sample Application Email Template:")
    print("-" * 50)
    print(templates['initial_application'][:500] + "...")
    
    # Export full guide
    filename = finder.export_search_guide()
    print(f"\n✅ Full guide exported to: {filename}")
    
    print("\n🎯 Next Steps:")
    print("1. Open Gmail and run the search queries above")
    print("2. For each application found, log it with email_application_tracker.py")
    print("3. Set up the Gmail filters for automatic tracking")
    print("4. Schedule follow-ups using the provided templates")
    
    # Example analysis
    print("\n🔬 Example Email Analysis:")
    example = {
        'subject': 'Application for Senior AI Engineer - Matthew Scott',
        'to': 'careers@openai.com',
        'body': 'Please find attached my resume for the Senior AI Engineer position...',
        'attachments': ['Matthew_Scott_Resume.pdf', 'Cover_Letter.pdf']
    }
    
    analysis = finder.analyze_email_for_application(example)
    print(f"Is Application: {analysis['is_application']}")
    print(f"Confidence: {analysis['confidence_score']}/10")
    print(f"Company: {analysis['suggested_company']}")
    print(f"Position: {analysis['suggested_position']}")


if __name__ == "__main__":
    main()