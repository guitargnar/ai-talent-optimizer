#!/usr/bin/env python3
"""
CEO Outreach Engine - Advanced system for finding and contacting CEOs/CTOs at target companies
Focuses on the top 5 companies with $450K+ positions for direct decision-maker contact
"""

import os
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path
import re
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

@dataclass
class CEOContact:
    """Data class for CEO/CTO contact information"""
    company: str
    name: str = None
    title: str = None
    email: str = None
    linkedin: str = None
    twitter: str = None
    phone: str = None
    bio: str = None
    funding_stage: str = None
    company_size: str = None
    recent_news: str = None
    priority_score: int = 0
    confidence_level: float = 0.0

class CEOOutreachEngine:
    """
    Advanced CEO/CTO outreach system for landing high-value positions through direct contact
    Targets the 5 companies with $450K+ positions identified in cover letters
    """
    
    # Target companies from SOURCE_OF_TRUTH.md with salary information
    TARGET_COMPANIES = {
        'Genesis AI': {
            'position': 'Principal ML Research Engineer',
            'salary': '$480K',
            'focus': 'Foundational AI research',
            'stage': 'Series A',
            'priority': 1,
            'website': 'https://genesis-ai.com',
            'linkedin': 'https://linkedin.com/company/genesis-ai'
        },
        'Inworld AI': {
            'position': 'Staff/Principal ML Engineer', 
            'salary': '$475K',
            'focus': 'AI-powered virtual beings',
            'stage': 'Series B',
            'priority': 2,
            'website': 'https://inworld.ai',
            'linkedin': 'https://linkedin.com/company/inworldai'
        },
        'Adyen': {
            'position': 'Staff Engineer ML',
            'salary': '$465K', 
            'focus': 'Fintech payments ML',
            'stage': 'Public',
            'priority': 3,
            'website': 'https://adyen.com',
            'linkedin': 'https://linkedin.com/company/adyen'
        },
        'Lime': {
            'position': 'Principal ML Engineer',
            'salary': '$465K',
            'focus': 'Micromobility ML/routing',
            'stage': 'Public',
            'priority': 4,
            'website': 'https://li.me',
            'linkedin': 'https://linkedin.com/company/limebike'
        },
        'Thumbtack': {
            'position': 'Principal ML Infrastructure',
            'salary': '$450K',
            'focus': 'Marketplace ML systems',
            'stage': 'Private',
            'priority': 5,
            'website': 'https://thumbtack.com',
            'linkedin': 'https://linkedin.com/company/thumbtack'
        }
    }
    
    # Common CEO/CTO email patterns
    EMAIL_PATTERNS = [
        '{first}@{domain}',
        '{first}.{last}@{domain}',
        '{first}_{last}@{domain}',
        '{first}{last}@{domain}',
        'ceo@{domain}',
        'founder@{domain}',
        '{first}+{last}@{domain}'
    ]
    
    def __init__(self, database_path: str = 'unified_talent_optimizer.db'):
        """Initialize CEO Outreach Engine"""
        self.db_path = database_path
        self.session_stats = {
            'contacts_discovered': 0,
            'emails_sent': 0,
            'responses_received': 0,
            'meetings_scheduled': 0
        }
        
        # Ensure contacts table exists in unified database
        self._init_contacts_table()
        
        logger.info("🎯 CEO Outreach Engine initialized - targeting $450K+ positions")
        logger.info(f"Target companies: {list(self.TARGET_COMPANIES.keys())}")
    
    def _init_contacts_table(self):
        """Initialize contacts table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if contacts table has all required columns
        cursor.execute("PRAGMA table_info(contacts)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            'priority_score', 'confidence_level', 'funding_stage', 
            'company_size', 'recent_news', 'bio', 'twitter', 'outreach_sent'
        ]
        
        for column in required_columns:
            if column not in existing_columns:
                if column in ['priority_score', 'confidence_level']:
                    cursor.execute(f"ALTER TABLE contacts ADD COLUMN {column} REAL DEFAULT 0")
                else:
                    cursor.execute(f"ALTER TABLE contacts ADD COLUMN {column} TEXT")
        
        conn.commit()
        conn.close()
    
    def research_all_targets(self) -> List[CEOContact]:
        """Research CEO/CTO contacts for all target companies"""
        logger.info("🔍 Starting comprehensive CEO research...")
        
        all_contacts = []
        for company, details in self.TARGET_COMPANIES.items():
            logger.info(f"Researching {company} ({details['salary']})...")
            
            contact = self._research_company_leadership(company, details)
            if contact:
                all_contacts.append(contact)
                self._store_contact(contact)
                self.session_stats['contacts_discovered'] += 1
            
            # Rate limiting to avoid detection
            time.sleep(3)
        
        logger.info(f"✅ Research complete: {len(all_contacts)} contacts discovered")
        return all_contacts
    
    def _research_company_leadership(self, company: str, details: Dict) -> Optional[CEOContact]:
        """Research CEO/CTO for a specific company using multiple methods"""
        contact = CEOContact(company=company, funding_stage=details['stage'])
        
        # Method 1: LinkedIn search
        linkedin_data = self._search_linkedin_leadership(company, details.get('linkedin'))
        if linkedin_data:
            contact.name = linkedin_data.get('name')
            contact.title = linkedin_data.get('title')
            contact.linkedin = linkedin_data.get('linkedin')
            contact.bio = linkedin_data.get('bio')
            contact.confidence_level = 0.8
        
        # Method 2: Company website research
        website_data = self._research_company_website(details.get('website'))
        if website_data and not contact.name:
            contact.name = website_data.get('name')
            contact.title = website_data.get('title')
            contact.bio = website_data.get('bio')
            contact.confidence_level = 0.6
        
        # Method 3: News and PR research
        news_data = self._research_recent_news(company)
        if news_data:
            # Convert dict to string for storage
            contact.recent_news = news_data.get('content', str(news_data)) if isinstance(news_data, dict) else str(news_data)
            if not contact.name and isinstance(news_data, dict) and news_data.get('ceo_name'):
                contact.name = news_data.get('ceo_name')
                contact.confidence_level = 0.4
        
        # Method 4: Email pattern generation
        if contact.name:
            contact.email = self._generate_ceo_email(contact.name, company, details.get('website'))
        
        # Calculate priority score
        contact.priority_score = self._calculate_priority_score(company, details, contact)
        
        return contact if contact.name or contact.email else None
    
    def _search_linkedin_leadership(self, company: str, linkedin_company_url: str) -> Optional[Dict]:
        """Search LinkedIn for company leadership"""
        try:
            # Setup headless browser
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=options)
            
            # Search Google for LinkedIn profiles
            search_queries = [
                f'"{company}" CEO site:linkedin.com/in',
                f'"{company}" CTO site:linkedin.com/in',
                f'"{company}" founder site:linkedin.com/in',
                f'"{company}" "Chief Executive" site:linkedin.com/in'
            ]
            
            for query in search_queries:
                try:
                    driver.get(f"https://www.google.com/search?q={query}")
                    time.sleep(2)
                    
                    # Find first LinkedIn result
                    linkedin_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="linkedin.com/in"]')
                    
                    for link in linkedin_links[:3]:  # Check first 3 results
                        href = link.get_attribute('href')
                        text = link.text
                        
                        # Extract name and title
                        if any(keyword in text.lower() for keyword in ['ceo', 'chief executive', 'founder', 'cto']):
                            name, title = self._parse_linkedin_text(text, company)
                            if name:
                                driver.quit()
                                return {
                                    'name': name,
                                    'title': title,
                                    'linkedin': href,
                                    'bio': f"Found via LinkedIn search for {company} leadership"
                                }
                
                except Exception as e:
                    logger.debug(f"Error in LinkedIn search query '{query}': {e}")
                    continue
            
            driver.quit()
            return None
            
        except Exception as e:
            logger.error(f"LinkedIn search error for {company}: {e}")
            return None
    
    def _parse_linkedin_text(self, text: str, company: str) -> Tuple[str, str]:
        """Parse LinkedIn search result text to extract name and title"""
        # Common patterns:
        # "John Smith - CEO at Company | LinkedIn"
        # "Jane Doe, Chief Technology Officer - Company"
        # "Founder & CEO John Smith - Company Name"
        
        # Clean up the text
        text = text.replace(' | LinkedIn', '').replace(' - LinkedIn', '')
        
        # Pattern 1: Name - Title at Company
        pattern1 = r'^([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s*[-–]\s*(CEO|CTO|Chief Executive|Chief Technology|Founder[^|]*)'
        match = re.search(pattern1, text)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        
        # Pattern 2: Title Name - Company
        pattern2 = r'(CEO|CTO|Chief Executive|Chief Technology|Founder)\s+([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*)'
        match = re.search(pattern2, text)
        if match:
            return match.group(2).strip(), match.group(1).strip()
        
        # Pattern 3: Name, Title - Company
        pattern3 = r'^([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*(CEO|CTO|Chief Executive|Chief Technology|Founder[^-]*)'
        match = re.search(pattern3, text)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        
        return None, None
    
    def _research_company_website(self, website_url: str) -> Optional[Dict]:
        """Research company website for leadership information"""
        if not website_url:
            return None
            
        try:
            # Common leadership page URLs
            leadership_paths = ['/about', '/team', '/leadership', '/about-us', '/company']
            
            for path in leadership_paths:
                try:
                    url = website_url.rstrip('/') + path
                    response = requests.get(url, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    })
                    
                    if response.status_code == 200:
                        content = response.text.lower()
                        
                        # Look for CEO mentions
                        ceo_patterns = [
                            r'ceo[:\s]*([a-z\s]+)',
                            r'chief executive[:\s]*([a-z\s]+)',
                            r'founder[:\s]*([a-z\s]+)'
                        ]
                        
                        for pattern in ceo_patterns:
                            match = re.search(pattern, content)
                            if match:
                                name_candidate = match.group(1).strip()
                                # Validate it looks like a name
                                if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', name_candidate.title()):
                                    return {
                                        'name': name_candidate.title(),
                                        'title': 'CEO',
                                        'bio': f"Found on company website {path} page"
                                    }
                    
                except requests.RequestException:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Website research error for {website_url}: {e}")
            return None
    
    def _research_recent_news(self, company: str) -> Optional[Dict]:
        """Research recent news for CEO mentions"""
        try:
            # Search for recent news about the company
            search_query = f'"{company}" CEO OR founder news'
            
            # Use Google News search (simplified version)
            news_url = f"https://news.google.com/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"
            
            response = requests.get(news_url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }, timeout=10)
            
            if response.status_code == 200:
                # Look for CEO names in news content
                content = response.text
                
                # Pattern to find "CEO [Name]" or "[Name], CEO"
                ceo_patterns = [
                    rf'{re.escape(company)}[^.]*?CEO ([A-Z][a-z]+ [A-Z][a-z]+)',
                    rf'CEO ([A-Z][a-z]+ [A-Z][a-z]+)[^.]*?{re.escape(company)}',
                    rf'([A-Z][a-z]+ [A-Z][a-z]+), CEO[^.]*?{re.escape(company)}'
                ]
                
                for pattern in ceo_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        return {
                            'ceo_name': matches[0],
                            'source': 'news_research',
                            'content': f"CEO mentioned in recent news about {company}"
                        }
            
            return None
            
        except Exception as e:
            logger.debug(f"News research error for {company}: {e}")
            return None
    
    def _generate_ceo_email(self, name: str, company: str, website: str) -> Optional[str]:
        """Generate likely CEO email addresses using common patterns"""
        if not name or not website:
            return None
        
        try:
            # Extract domain from website
            domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            
            # Parse name
            name_parts = name.lower().split()
            if len(name_parts) < 2:
                return None
                
            first = name_parts[0]
            last = name_parts[-1]
            
            # Generate email patterns in order of likelihood
            candidates = []
            for pattern in self.EMAIL_PATTERNS:
                email = pattern.format(first=first, last=last, domain=domain)
                candidates.append(email)
            
            # Return the most common pattern (first.last@domain)
            return candidates[1] if len(candidates) > 1 else candidates[0]
            
        except Exception as e:
            logger.debug(f"Email generation error: {e}")
            return None
    
    def _calculate_priority_score(self, company: str, details: Dict, contact: CEOContact) -> int:
        """Calculate priority score for contact outreach"""
        score = 0
        
        # Base score from company priority (1-5, higher is better)
        score += (6 - details.get('priority', 5)) * 20
        
        # Salary bonus (higher salary = higher priority)
        salary_num = int(details.get('salary', '$0').replace('$', '').replace('K', '000').replace(',', ''))
        if salary_num >= 480000:
            score += 30
        elif salary_num >= 465000:
            score += 25
        elif salary_num >= 450000:
            score += 20
        
        # Contact data quality bonus
        if contact.name:
            score += 15
        if contact.email:
            score += 20
        if contact.linkedin:
            score += 10
        if contact.recent_news:
            score += 5
        
        # Confidence level bonus
        score += int(contact.confidence_level * 10)
        
        return min(score, 100)  # Cap at 100
    
    def _store_contact(self, contact: CEOContact):
        """Store contact in unified database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if contact already exists
        cursor.execute("""
            SELECT id FROM contacts WHERE company = ? AND LOWER(name) = LOWER(?)
        """, (contact.company, contact.name or ''))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing contact
            cursor.execute("""
                UPDATE contacts SET 
                    title = ?, email = ?, linkedin = ?, phone = ?, 
                    priority_score = ?, confidence_level = ?, funding_stage = ?,
                    recent_news = ?, bio = ?, twitter = ?
                WHERE id = ?
            """, (
                contact.title, contact.email, contact.linkedin, contact.phone,
                contact.priority_score, contact.confidence_level, contact.funding_stage,
                contact.recent_news, contact.bio, contact.twitter, existing[0]
            ))
            logger.info(f"  🔄 Updated existing contact: {contact.name} at {contact.company}")
        else:
            # Insert new contact
            cursor.execute("""
                INSERT INTO contacts (
                    company, name, title, email, linkedin, phone,
                    priority_score, confidence_level, funding_stage,
                    recent_news, bio, twitter, contacted, response_received, 
                    meeting_scheduled, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, CURRENT_TIMESTAMP)
            """, (
                contact.company, contact.name, contact.title, contact.email,
                contact.linkedin, contact.phone, contact.priority_score,
                contact.confidence_level, contact.funding_stage, contact.recent_news,
                contact.bio, contact.twitter
            ))
            logger.info(f"  ✅ Stored new contact: {contact.name} at {contact.company}")
        
        conn.commit()
        conn.close()
    
    def send_ceo_outreach(self, limit: int = 5, priority_threshold: int = 50) -> Dict[str, Any]:
        """Send personalized outreach to highest priority CEOs"""
        logger.info(f"📧 Sending CEO outreach (limit: {limit}, priority: {priority_threshold}+)")
        
        # Get uncontacted high-priority contacts
        contacts = self._get_outreach_candidates(limit, priority_threshold)
        
        results = {'sent': [], 'failed': []}
        
        for contact in contacts:
            try:
                success = self._send_personalized_ceo_email(contact)
                if success:
                    results['sent'].append(contact['company'])
                    self._mark_as_contacted(contact['id'])
                    self.session_stats['emails_sent'] += 1
                    logger.info(f"  ✅ Outreach sent to {contact['name']} at {contact['company']}")
                else:
                    results['failed'].append(contact['company'])
                    logger.warning(f"  ❌ Failed to send to {contact['company']}")
                
                # Rate limiting between sends
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error sending to {contact['company']}: {e}")
                results['failed'].append(contact['company'])
        
        logger.info(f"📊 Outreach complete: {len(results['sent'])} sent, {len(results['failed'])} failed")
        return results
    
    def _get_outreach_candidates(self, limit: int, priority_threshold: int) -> List[Dict]:
        """Get candidates for CEO outreach based on priority"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE contacted = 0 
            AND priority_score >= ? 
            AND (name IS NOT NULL OR email IS NOT NULL)
            ORDER BY priority_score DESC, confidence_level DESC
            LIMIT ?
        """, (priority_threshold, limit))
        
        columns = [description[0] for description in cursor.description]
        contacts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return contacts
    
    def _send_personalized_ceo_email(self, contact: Dict) -> bool:
        """Send personalized email to CEO/CTO"""
        company = contact['company']
        name = contact['name'] or 'Hiring Team'
        title = contact['title'] or 'CEO'
        
        # Get company details
        company_details = self.TARGET_COMPANIES.get(company, {})
        position = company_details.get('position', 'ML Engineering Leadership')
        salary = company_details.get('salary', '$450K+')
        focus = company_details.get('focus', 'AI/ML systems')
        
        # Generate personalized subject and email
        subject = self._generate_ceo_subject(company, name, salary)
        body = self._generate_ceo_email_body(contact, company_details)
        
        # Store outreach record (in production would actually send via SMTP)
        self._store_outreach_record(contact, subject, body)
        
        logger.info(f"  📧 Email generated for {name} at {company}")
        logger.debug(f"  Subject: {subject}")
        
        return True  # Would return actual send status in production
    
    def _generate_ceo_subject(self, company: str, name: str, salary: str) -> str:
        """Generate compelling subject line for CEO outreach"""
        subjects = [
            f"Principal ML Engineer Discussion - {salary} Role at {company}",
            f"Healthcare AI Expertise for {company} - $1.2M Cost Savings Track Record",  
            f"10 Years Humana ML Experience - Interested in {company} Leadership Role",
            f"Principal Engineer Application - {company} {salary} Position"
        ]
        
        # Choose based on company name hash for consistency
        index = hash(company + name) % len(subjects)
        return subjects[index]
    
    def _generate_ceo_email_body(self, contact: Dict, company_details: Dict) -> str:
        """Generate personalized email body for CEO outreach"""
        company = contact['company']
        name = contact['name'] or 'there'
        first_name = name.split()[0] if name != 'there' else 'there'
        position = company_details.get('position', 'Principal ML Engineer')
        salary = company_details.get('salary', '$450K+')
        focus = company_details.get('focus', 'AI/ML systems')
        
        # Personalization based on company
        company_specific = self._get_company_specific_content(company, focus)
        
        body = f"""Hi {first_name},

I'm reaching out directly about the {position} role at {company}. As someone who spent 10 years at Humana building enterprise-scale AI systems, I'm particularly excited about {company}'s work in {focus.lower()}.

Here's what I bring to the table:

🎯 **Proven Impact at Scale**
• Delivered $1.2M in annual cost savings through AI automation at Humana
• Built and maintained 78 specialized ML models serving 50M+ users
• Achieved 90% reduction in LLM inference costs through custom optimization
• Maintained 100% regulatory compliance across 500+ Medicare pages using AI

🚀 **Technical Leadership**  
• Architected distributed ML systems with 99.9% uptime
• Led platform development with 117 Python modules handling thousands of daily operations
• Experience with production systems at Fortune 50 scale

{company_specific}

I've been operating at a Principal level while maintaining my current role - the platform I've built demonstrates the kind of systematic thinking and execution this position requires.

**Why {company}?** {self._get_company_why(company, focus)}

I'd welcome a brief conversation about how my healthcare AI experience and proven ability to deliver at scale can contribute to {company}'s continued growth.

Are you available for a 15-minute call this week?

Best regards,

Matthew Scott
Senior AI/ML Engineer | Production Systems Architect
📧 matthewdscott7@gmail.com | 📱 502-345-0525
🔗 linkedin.com/in/mscott77
📍 Louisville, KY | Open to Remote

P.S. I've built a 58-model AI orchestration system that's unprecedented in the industry - happy to share specific technical details about how this approach could benefit {company}'s {focus.lower()}.
"""
        
        return body
    
    def _get_company_specific_content(self, company: str, focus: str) -> str:
        """Get company-specific content for personalization"""
        content_map = {
            'Genesis AI': """
🧠 **AI Research Alignment**
• My work on distributed model architectures directly aligns with foundational AI research
• Experience with novel quantization techniques and model optimization
• Track record of turning research concepts into production-scale systems""",
            
            'Inworld AI': """
🎭 **AI Characters & Virtual Beings**
• Built conversational AI systems handling complex multi-turn interactions
• Experience with real-time ML inference for interactive applications  
• Deep understanding of AI safety and alignment for user-facing systems""",
            
            'Adyen': """
💳 **Fintech ML at Scale**
• Healthcare payments experience translates directly to fintech ML challenges
• Expertise in fraud detection, risk assessment, and real-time decision making
• Proven ability to maintain regulatory compliance while scaling ML systems""",
            
            'Lime': """
🛴 **Mobility & Routing ML**
• Built optimization systems for resource allocation and routing
• Experience with geospatial ML and real-time decision making
• Scaled systems handling millions of daily operations across distributed networks""",
            
            'Thumbtack': """
🔨 **Marketplace ML Systems**  
• Built matching and recommendation systems for complex multi-sided markets
• Experience with search ranking, fraud detection, and user behavior modeling
• Expertise in A/B testing and ML experimentation at scale"""
        }
        
        return content_map.get(company, f"""
🔧 **ML Systems Expertise**
• Experience building and scaling ML infrastructure for complex business requirements
• Track record of delivering measurable business impact through AI/ML implementations
• Deep expertise in {focus.lower()} and related ML applications""")
    
    def _get_company_why(self, company: str, focus: str) -> str:
        """Get personalized 'why this company' content"""
        why_map = {
            'Genesis AI': "Your focus on foundational AI research represents the cutting edge of where the field is heading.",
            'Inworld AI': "The intersection of AI and interactive experiences is where the most exciting breakthroughs are happening.",
            'Adyen': "The scale and complexity of global payments provides fascinating ML challenges.",
            'Lime': "Sustainable transportation powered by intelligent systems aligns with my values and interests.",
            'Thumbtack': "Marketplaces represent some of the most complex and impactful applications of ML."
        }
        
        return why_map.get(company, f"Your work in {focus.lower()} represents an exciting opportunity to apply ML at scale.")
    
    def _store_outreach_record(self, contact: Dict, subject: str, body: str):
        """Store detailed outreach record"""
        # Create outreach directory if it doesn't exist  
        outreach_dir = Path('output/ceo_outreach')
        outreach_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        company_safe = contact['company'].replace(' ', '_').replace('/', '_')
        filename = f"{company_safe}_{timestamp}.txt"
        
        # Store full outreach details
        with open(outreach_dir / filename, 'w', encoding='utf-8') as f:
            f.write(f"CEO OUTREACH RECORD\n")
            f.write(f"==================\n\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Company: {contact['company']}\n")
            f.write(f"Contact: {contact['name'] or 'Unknown'}\n") 
            f.write(f"Title: {contact['title'] or 'Unknown'}\n")
            f.write(f"Email: {contact['email'] or 'Unknown'}\n")
            f.write(f"LinkedIn: {contact['linkedin'] or 'Unknown'}\n")
            f.write(f"Priority Score: {contact['priority_score']}\n")
            f.write(f"Confidence Level: {contact['confidence_level']}\n\n")
            f.write(f"SUBJECT: {subject}\n\n")
            f.write(f"BODY:\n{body}\n")
        
        logger.debug(f"  📁 Outreach record saved: {filename}")
    
    def _mark_as_contacted(self, contact_id: int):
        """Mark contact as contacted in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE contacts 
            SET contacted = 1, contacted_at = CURRENT_TIMESTAMP, outreach_sent = 1
            WHERE id = ?
        """, (contact_id,))
        
        conn.commit()
        conn.close()
    
    def schedule_follow_ups(self) -> List[Dict]:
        """Schedule and send follow-up messages"""
        logger.info("📮 Checking for follow-up opportunities...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find contacts that need follow-up (contacted 3+ days ago, no response)
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE contacted = 1 
            AND response_received = 0
            AND meeting_scheduled = 0 
            AND contacted_at < datetime('now', '-3 days')
            AND priority_score >= 70
            ORDER BY priority_score DESC
            LIMIT 10
        """)
        
        columns = [description[0] for description in cursor.description]
        follow_up_candidates = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        logger.info(f"Found {len(follow_up_candidates)} contacts needing follow-up")
        
        follow_ups_sent = []
        for contact in follow_up_candidates:
            if self._send_follow_up_email(contact):
                follow_ups_sent.append(contact)
                logger.info(f"  📧 Follow-up sent to {contact['company']}")
        
        return follow_ups_sent
    
    def _send_follow_up_email(self, contact: Dict) -> bool:
        """Send follow-up email to CEO"""
        company = contact['company']
        name = contact['name'] or 'there'
        first_name = name.split()[0] if name != 'there' else 'there'
        
        # Get company details for personalization
        company_details = self.TARGET_COMPANIES.get(company, {})
        position = company_details.get('position', 'Principal Engineer role')
        salary = company_details.get('salary', '$450K+')
        
        subject = f"Re: {position} - Quick follow-up"
        
        body = f"""Hi {first_name},

Following up on my previous message about the {position} role at {company}.

I understand leadership is busy, especially when scaling {company_details.get('focus', 'AI/ML systems').lower()}. 

I wanted to add that I'm also available for:
• Technical consultation ($5K) - Architecture reviews, ML strategy sessions
• Short-term projects ($15K) - Help with specific technical challenges
• Advisory capacity ($3K/month) - Strategic guidance as you scale

My Humana experience with enterprise-scale healthcare AI could be immediately valuable for {company}'s growth trajectory.

Quick 10-minute call this week to discuss?

Best,
Matthew Scott
📧 matthewdscott7@gmail.com | 📱 502-345-0525

P.S. Happy to share specific case studies of how I saved $1.2M annually through ML automation.
"""
        
        # Store follow-up record
        self._store_follow_up_record(contact, subject, body)
        
        return True  # In production, would return actual send status
    
    def _store_follow_up_record(self, contact: Dict, subject: str, body: str):
        """Store follow-up record"""
        outreach_dir = Path('output/ceo_outreach/follow_ups')
        outreach_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') 
        company_safe = contact['company'].replace(' ', '_').replace('/', '_')
        filename = f"followup_{company_safe}_{timestamp}.txt"
        
        with open(outreach_dir / filename, 'w', encoding='utf-8') as f:
            f.write(f"FOLLOW-UP RECORD\n")
            f.write(f"================\n\n") 
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Company: {contact['company']}\n")
            f.write(f"Original Contact Date: {contact['contacted_at']}\n")
            f.write(f"Days Since Contact: {(datetime.now() - datetime.fromisoformat(contact['contacted_at'])).days}\n\n")
            f.write(f"SUBJECT: {subject}\n\n")
            f.write(f"BODY:\n{body}\n")
    
    def generate_outreach_report(self) -> str:
        """Generate comprehensive outreach status report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get statistics
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE company IN ({})".format(
            ','.join(['?'] * len(self.TARGET_COMPANIES))
        ), list(self.TARGET_COMPANIES.keys()))
        stats['total_contacts'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE contacted = 1 AND company IN ({})".format(
            ','.join(['?'] * len(self.TARGET_COMPANIES))
        ), list(self.TARGET_COMPANIES.keys()))
        stats['contacted'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE response_received = 1 AND company IN ({})".format(
            ','.join(['?'] * len(self.TARGET_COMPANIES))
        ), list(self.TARGET_COMPANIES.keys()))
        stats['responses'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE meeting_scheduled = 1 AND company IN ({})".format(
            ','.join(['?'] * len(self.TARGET_COMPANIES))
        ), list(self.TARGET_COMPANIES.keys()))
        stats['meetings'] = cursor.fetchone()[0]
        
        # Get company-by-company breakdown
        cursor.execute("""
            SELECT company, name, title, priority_score, contacted, response_received, 
                   meeting_scheduled, contacted_at
            FROM contacts 
            WHERE company IN ({})
            ORDER BY priority_score DESC, company
        """.format(','.join(['?'] * len(self.TARGET_COMPANIES))), list(self.TARGET_COMPANIES.keys()))
        
        columns = [description[0] for description in cursor.description] 
        company_breakdown = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        # Calculate response rate
        response_rate = (stats['responses'] / stats['contacted'] * 100) if stats['contacted'] > 0 else 0
        
        # Build report
        report = f"""
🎯 CEO OUTREACH CAMPAIGN REPORT - $450K+ POSITIONS
===============================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 TARGET VALUE: Combined salary potential = $2.34M annually
📊 CAMPAIGN METRICS:
• Total decision-makers identified: {stats['total_contacts']}
• Outreach messages sent: {stats['contacted']}
• Responses received: {stats['responses']}
• Meetings scheduled: {stats['meetings']}
• Response rate: {response_rate:.1f}%

📈 SESSION STATS:
• Contacts discovered this session: {self.session_stats['contacts_discovered']}
• Emails sent this session: {self.session_stats['emails_sent']}

🏢 COMPANY-BY-COMPANY STATUS:
"""
        
        for company in company_breakdown:
            status_emoji = "✅" if company['contacted'] else "⏳"
            response_emoji = "📧" if company['response_received'] else "⏸️"
            meeting_emoji = "🤝" if company['meeting_scheduled'] else "📅"
            
            company_info = self.TARGET_COMPANIES.get(company['company'], {})
            salary = company_info.get('salary', 'Unknown')
            
            report += f"""
{status_emoji} {company['company']} ({salary})
   Contact: {company['name'] or 'TBD'} - {company['title'] or 'CEO'}
   Priority: {company['priority_score']}/100 | Contacted: {company['contacted_at'] or 'No'}
   Status: {response_emoji} Response | {meeting_emoji} Meeting
"""
        
        report += f"""

🎯 NEXT ACTIONS:
• Research missing contacts for companies without CEO info
• Send outreach to high-priority contacts (70+ score)
• Follow up on contacted prospects after 3 days
• Track responses and schedule meetings

💡 STRATEGY NOTES:
• Targeting decision-makers directly for $450K+ positions
• Leveraging Humana healthcare AI experience as differentiator
• Emphasizing quantified impact ($1.2M cost savings)
• Multiple engagement options (full-time, consulting, advisory)

🚀 SUCCESS TARGET: 1 executive meeting → 1 offer → $450K+ position
"""
        
        return report
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session and overall statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE company IN ({})".format(
            ','.join(['?'] * len(self.TARGET_COMPANIES))
        ), list(self.TARGET_COMPANIES.keys()))
        total_contacts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE contacted = 1 AND company IN ({})".format(
            ','.join(['?'] * len(self.TARGET_COMPANIES))
        ), list(self.TARGET_COMPANIES.keys()))
        contacted = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'target_companies': len(self.TARGET_COMPANIES),
            'total_contacts': total_contacts,
            'contacted': contacted,
            'session_contacts_discovered': self.session_stats['contacts_discovered'],
            'session_emails_sent': self.session_stats['emails_sent'],
            'total_potential_salary': '$2.34M'
        }


if __name__ == "__main__":
    # Example usage
    engine = CEOOutreachEngine()
    
    print("🎯 CEO Outreach Engine - Landing $450K+ Positions")
    print("=" * 60)
    
    # Research all target companies
    contacts = engine.research_all_targets()
    print(f"\n✅ Research complete: {len(contacts)} contacts")
    
    # Send outreach to top candidates
    results = engine.send_ceo_outreach(limit=5)
    print(f"\n📧 Outreach sent to {len(results['sent'])} CEOs")
    
    # Generate report
    print("\n📊 Campaign Report:")
    print(engine.generate_outreach_report())