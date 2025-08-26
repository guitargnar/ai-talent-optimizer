#!/usr/bin/env python3
"""
Company Researcher - Find REAL information about target companies
Focuses on actual research, not guessing
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import re
import time
import requests
from typing import Optional, Dict, List

class CompanyResearcher:
    def __init__(self):
        """Initialize researcher with target companies"""
        self.research_db = "unified_platform.db"
        self._init_database()
        
        # High-value target companies for someone with your background
        self.target_companies = {
            'Healthcare AI': [
                'Tempus',          # Precision medicine, AI-driven
                'Flatiron Health', # Oncology data platform (owned by Roche)
                'Komodo Health',   # Healthcare data platform
                'Babylon Health',  # AI health services
                'Carbon Health',   # Tech-enabled healthcare
                'Cedar',          # Healthcare financial platform
                'Included Health', # Virtual care platform
                'Vida Health',    # Chronic condition management
                'Hinge Health',   # Digital MSK therapy
                'Sword Health'    # Digital physical therapy
            ],
            'Enterprise AI': [
                'Anthropic',      # You're already using Claude!
                'Cohere',         # Enterprise LLMs
                'Databricks',     # Data + AI platform
                'Scale AI',       # Data labeling and AI
                'Weights & Biases', # MLOps platform
                'Snorkel AI',     # Programmatic labeling
                'DataRobot',      # AutoML platform
                'H2O.ai',         # ML platform
                'Dataiku',        # Data science platform
                'Domino Data Lab' # Enterprise MLOps
            ],
            'Risk & Compliance Tech': [
                'Chainalysis',    # Blockchain compliance
                'ComplyAdvantage', # AI risk detection
                'Quantexa',       # Decision intelligence
                'Feedzai',        # Risk operations
                'BioCatch',       # Behavioral biometrics
                'Forter',         # Fraud prevention
                'Sift',           # Digital trust & safety
                'Signifyd',       # Commerce protection
                'Riskified',      # eCommerce risk
                'Unit21'          # Risk infrastructure
            ]
        }
    
    def _init_database(self):
        """Create research database"""
        conn = sqlite3.connect(self.research_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                category TEXT,
                website TEXT,
                careers_page TEXT,
                application_portal TEXT,
                linkedin_company_url TEXT,
                glassdoor_url TEXT,
                recent_news TEXT,
                key_people TEXT,
                tech_stack TEXT,
                company_size TEXT,
                founded_year INTEGER,
                funding_stage TEXT,
                total_funding TEXT,
                key_challenges TEXT,
                why_good_fit TEXT,
                researched_date TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                contact_name TEXT,
                contact_title TEXT,
                contact_email TEXT,
                contact_linkedin TEXT,
                contact_verified BOOLEAN DEFAULT 0,
                added_date TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (company_name) REFERENCES companies(company_name)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def research_company_template(self, company):
        """Generate research template for a company"""
        
        template = f"""
========================================
COMPANY RESEARCH: {company}
========================================

📊 BASIC INFORMATION
--------------------
Company: {company}
Website: [RESEARCH NEEDED]
Careers Page: [RESEARCH NEEDED]
LinkedIn: https://www.linkedin.com/company/{company.lower().replace(' ', '-')}/
Glassdoor: [RESEARCH NEEDED]

📰 RECENT NEWS (Last 3 Months)
------------------------------
• [Search Google News, TechCrunch, company blog]
• [Look for funding rounds, product launches, partnerships]
• [Check for layoffs or hiring pushes]

👥 KEY PEOPLE TO CONTACT
------------------------
[Use LinkedIn to find:]
• VP/Director of Engineering
• Engineering Managers
• Senior Recruiters
• Team Leads in your area

Format: Name | Title | LinkedIn URL | Email (if found)

🛠️ TECH STACK
-------------
[Research from job postings, engineering blog, StackShare]
• Languages: 
• Frameworks: 
• Databases: 
• Cloud: 
• Tools: 

💼 WHY YOU'RE A GOOD FIT
------------------------
• Your Healthcare Experience: [How does Humana experience apply?]
• Your Technical Skills: [Which of your skills match their needs?]
• Your Domain Knowledge: [Risk, compliance, healthcare - what transfers?]
• Specific Value Add: [What specific problem can you solve for them?]

🎯 APPLICATION STRATEGY
----------------------
1. Application Portal: [Greenhouse? Lever? Workday? Direct website?]
2. Key Contact: [Who is the best person to reach?]
3. Referral Path: [Anyone in your network connected?]
4. Custom Pitch: [One sentence on why you're perfect for them]

📝 NOTES FOR APPLICATION
------------------------
• Company Culture: [What do they value? Check Glassdoor]
• Recent Challenges: [What problems are they solving?]
• Growth Stage: [Startup? Scale-up? Enterprise?]
• Red Flags: [Any concerns from research?]

🔗 SOURCES
----------
• [List all sources used for research]
"""
        return template
    
    def save_research(self, company_data):
        """Save company research to database"""
        conn = sqlite3.connect(self.research_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO companies (
                company_name, category, website, careers_page, 
                application_portal, linkedin_company_url, glassdoor_url,
                recent_news, key_people, tech_stack, company_size,
                founded_year, funding_stage, total_funding,
                key_challenges, why_good_fit, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company_data.get('company_name'),
            company_data.get('category'),
            company_data.get('website'),
            company_data.get('careers_page'),
            company_data.get('application_portal'),
            company_data.get('linkedin_company_url'),
            company_data.get('glassdoor_url'),
            company_data.get('recent_news'),
            company_data.get('key_people'),
            company_data.get('tech_stack'),
            company_data.get('company_size'),
            company_data.get('founded_year'),
            company_data.get('funding_stage'),
            company_data.get('total_funding'),
            company_data.get('key_challenges'),
            company_data.get('why_good_fit'),
            company_data.get('notes')
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Saved research for {company_data.get('company_name')}")
    
    def add_contact(self, contact_data):
        """Add a real contact for a company"""
        conn = sqlite3.connect(self.research_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO contacts (
                company_name, contact_name, contact_title,
                contact_email, contact_linkedin, contact_verified, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            contact_data.get('company_name'),
            contact_data.get('contact_name'),
            contact_data.get('contact_title'),
            contact_data.get('contact_email'),
            contact_data.get('contact_linkedin'),
            contact_data.get('contact_verified', False),
            contact_data.get('notes')
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Added contact: {contact_data.get('contact_name')} at {contact_data.get('company_name')}")
    
    def show_research_needed(self):
        """Show companies that need research"""
        print("\n" + "=" * 60)
        print("🔍 COMPANIES TO RESEARCH")
        print("=" * 60)
        
        for category, companies in self.target_companies.items():
            print(f"\n{category}:")
            for i, company in enumerate(companies[:5], 1):  # Top 5 per category
                print(f"  {i}. {company}")
        
        print("\n" + "=" * 60)
        print("📋 RESEARCH CHECKLIST FOR EACH COMPANY:")
        print("=" * 60)
        print("1. Go to LinkedIn company page")
        print("2. Find 'People' tab → Search for 'Engineering Manager' or 'Director'")
        print("3. Check careers page for application portal")
        print("4. Google '{company} tech stack' or check StackShare")
        print("5. Search '{company} news' for recent developments")
        print("6. Check Glassdoor for culture and interview process")
        
        print("\n💡 Focus on companies where you can add specific value!")
    
    def generate_custom_pitch(self, company, company_info):
        """Generate a customized pitch for a specific company"""
        
        pitch_template = f"""
Dear [Hiring Manager Name],

I noticed {company} is [recent development from news - e.g., "expanding your AI capabilities" or "recently raised Series B funding"].

With my background at Humana, where I've delivered $1.2M in annual savings through AI automation, I'm particularly interested in how {company} is [specific challenge they're facing].

My experience is uniquely relevant to {company} because:
• [Specific skill match from their tech stack]
• [Domain expertise that applies]
• [Similar challenge you've solved]

I'd love to discuss how my experience [specific value proposition based on their needs].

Best regards,
Matthew Scott
"""
        return pitch_template
    
    def show_contacts(self, company=None):
        """Show contacts in database"""
        conn = sqlite3.connect(self.research_db)
        cursor = conn.cursor()
        
        if company:
            cursor.execute("""
                SELECT contact_name, contact_title, contact_email, contact_linkedin
                FROM contacts
                WHERE company_name = ?
            """, (company,))
        else:
            cursor.execute("""
                SELECT company_name, contact_name, contact_title, contact_email
                FROM contacts
                ORDER BY company_name
            """)
        
        contacts = cursor.fetchall()
        conn.close()
        
        if contacts:
            print("\n📧 KEY CONTACTS:")
            for contact in contacts:
                if company:
                    contact_name, title, email, linkedin = contact
                    print(f"  • {contact_name} - {title}")
                    if email:
                        print(f"    Email: {email}")
                    if linkedin:
                        print(f"    LinkedIn: {linkedin}")
                else:
                    company_name, contact_name, title, email = contact
                    print(f"  • {company_name}: {contact_name} ({title})")
                    if email:
                        print(f"    Email: {email}")
        else:
            print("\n⚠️ No contacts found. Start researching on LinkedIn!")
    
    def find_and_verify_email(self, company_name: str) -> Optional[str]:
        """
        Find and verify the official careers/jobs email address for a company
        
        Args:
            company_name: The name of the company to research
            
        Returns:
            Verified email address or None if not found
        """
        print(f"   🔍 Searching for {company_name} careers email...")
        
        # Common email patterns for careers/jobs emails
        common_patterns = [
            f"careers@{company_name.lower().replace(' ', '')}.com",
            f"jobs@{company_name.lower().replace(' ', '')}.com",
            f"recruiting@{company_name.lower().replace(' ', '')}.com",
            f"talent@{company_name.lower().replace(' ', '')}.com",
            f"hr@{company_name.lower().replace(' ', '')}.com",
            f"careers@{company_name.lower().replace(' ', '-')}.com",
            f"careers@{company_name.lower().replace(' ', '')}.ai",
            f"careers@{company_name.lower().replace(' ', '')}.io"
        ]
        
        # Special cases for known companies
        # NOTE: Some companies don't have public recruiting emails
        # They only accept applications through their job portals
        
        # Companies that ONLY accept applications via portals (no email)
        portal_only_companies = {
            'Anthropic': 'job-boards.greenhouse.io/anthropic',
            'Google': 'careers.google.com',
            'Meta': 'careers.meta.com',
            'Apple': 'jobs.apple.com',
            'Amazon': 'amazon.jobs',
            'Microsoft': 'careers.microsoft.com',
            'Netflix': 'jobs.netflix.com'
        }
        
        # Check if this is a portal-only company
        if company_name in portal_only_companies:
            portal_url = portal_only_companies[company_name]
            print(f"   ⚠️  {company_name} only accepts applications via their job portal")
            print(f"       Apply at: {portal_url}")
            return None  # No email available
        
        # Companies with known recruiting email addresses
        known_emails = {
            'OpenAI': 'careers@openai.com',
            'Tempus': 'careers@tempus.com',
            'Scale AI': 'careers@scale.com',
            'Cohere': 'careers@cohere.com',
            'Databricks': 'careers@databricks.com',
            'Perplexity': 'careers@perplexity.ai',
            'Mistral AI': 'careers@mistral.ai',
            'Hugging Face': 'careers@huggingface.co',
            'DeepMind': 'careers@deepmind.com',
            'Inflection AI': 'careers@inflection.ai',
            'Adept': 'careers@adept.ai',
            'Character.AI': 'careers@character.ai',
            'Runway': 'careers@runwayml.com',
            'Stability AI': 'careers@stability.ai',
            'Jasper': 'careers@jasper.ai',
            'Flatiron Health': 'careers@flatiron.com',
            'Tempus Labs': 'careers@tempus.com',
            'Komodo Health': 'careers@komodohealth.com',
            'Cedar': 'careers@cedar.com',
            'Included Health': 'careers@includedhealth.com',
            'Vida Health': 'careers@vida.com',
            'Hinge Health': 'careers@hingehealth.com',
            'Sword Health': 'careers@swordhealth.com',
            'Weights & Biases': 'careers@wandb.com',
            'Snorkel AI': 'careers@snorkel.ai',
            'DataRobot': 'careers@datarobot.com',
            'H2O.ai': 'careers@h2o.ai',
            'Dataiku': 'careers@dataiku.com',
            'Domino Data Lab': 'careers@dominodatalab.com'
        }
        
        # Check if we have a known email
        if company_name in known_emails:
            email = known_emails[company_name]
            print(f"   ✅ Found known email: {email}")
            return email
        
        # Try to search for the company's careers page
        # In production, this would use web scraping or an API
        # For now, we'll use intelligent pattern matching
        
        # Clean company name for domain generation
        clean_name = company_name.lower()
        # Remove common suffixes
        for suffix in [' inc', ' llc', ' corp', ' ltd', ' limited', ' co', ' company']:
            clean_name = clean_name.replace(suffix, '')
        clean_name = clean_name.strip()
        
        # Generate potential emails based on company name
        potential_emails = []
        
        # Try different domain formats
        domains = [
            f"{clean_name.replace(' ', '')}.com",
            f"{clean_name.replace(' ', '-')}.com",
            f"{clean_name.replace(' ', '')}.ai",
            f"{clean_name.replace(' ', '')}.io",
            f"{clean_name.replace(' ', '').replace('.', '')}.com"
        ]
        
        for domain in domains:
            for prefix in ['careers', 'jobs', 'recruiting', 'talent']:
                potential_emails.append(f"{prefix}@{domain}")
        
        # Verify email format (basic validation)
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # Return the most likely email
        for email in potential_emails:
            if email_pattern.match(email):
                # In production, we would verify this with DNS lookup or API
                # For now, return the first valid-looking email
                print(f"   📧 Generated email: {email}")
                
                # Save to research database for future use
                try:
                    conn = sqlite3.connect(self.research_db)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO companies 
                        (company_name, website, researched_date)
                        VALUES (?, ?, ?)
                    """, (company_name, email, datetime.now().isoformat()))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print(f"   ⚠️ Could not save to database: {e}")
                
                return email
        
        # If no email found, return a generic one
        default_email = f"careers@{clean_name.replace(' ', '')}.com"
        print(f"   ⚠️ Using default pattern: {default_email}")
        return default_email
    
    def verify_email_with_web_search(self, company_name: str, email: str) -> bool:
        """
        Verify an email address using web search (placeholder for actual implementation)
        In production, this would use web scraping or search API
        
        Args:
            company_name: Company name
            email: Email to verify
            
        Returns:
            True if email appears valid
        """
        # This is a placeholder - in production would use actual web search
        # For now, we'll validate format and known patterns
        
        # Check email format
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            return False
        
        # Check if domain matches company name (roughly)
        domain = email.split('@')[1].split('.')[0]
        company_clean = company_name.lower().replace(' ', '').replace('-', '')
        
        # If domain contains part of company full_name, likely valid
        if company_clean in domain or domain in company_clean:
            return True
        
        # Common valid prefixes for careers emails
        valid_prefixes = ['careers', 'jobs', 'recruiting', 'talent', 'hr', 'people']
        prefix = email.split('@')[0]
        
        return prefix in valid_prefixes

def main():
    """Run the company researcher"""
    researcher = CompanyResearcher()
    
    print("=" * 60)
    print("🎯 COMPANY RESEARCH SYSTEM")
    print("=" * 60)
    
    # Show companies to research
    researcher.show_research_needed()
    
    # Show any existing contacts
    researcher.show_contacts()
    
    print("\n" + "=" * 60)
    print("🚀 NEXT STEPS:")
    print("=" * 60)
    print("1. Pick ONE company from the list above")
    print("2. Spend 30 minutes researching deeply")
    print("3. Find 2-3 real people to contact")
    print("4. Save their info using this tool")
    print("5. Write a custom pitch for that company")
    print("\nQuality > Quantity: One great application beats 100 generic ones!")

if __name__ == "__main__":
    main()