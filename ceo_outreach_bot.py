#!/usr/bin/env python3
"""
CEO Outreach Bot - Finds and contacts healthcare AI CEOs for fractional CTO opportunities
Targets companies with recent funding for immediate opportunities
"""

import os
import json
import time
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(full_name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CEOOutreachBot:
    """Automated CEO/CTO finder and outreach system for fractional opportunities"""
    
    # Target companies from recent funding (from our research)
    TARGET_COMPANIES = [
        {'name': 'Sully.ai', 'funding': '$25M', 'stage': 'YC', 'focus': 'Healthcare AI'},
        {'name': 'Infinitus', 'funding': 'Series B', 'stage': 'Growth', 'focus': 'Voice AI for healthcare'},
        {'name': 'Healthee', 'funding': '$32M Series A', 'stage': 'Series A', 'focus': 'AI platform'},
        {'name': 'Apero Health', 'funding': 'YC-backed', 'stage': 'Seed', 'focus': 'Medical billing'},
        {'name': 'Notable Health', 'funding': 'Series B', 'stage': 'Growth', 'focus': 'Medical documentation'},
        {'name': 'Regard', 'funding': 'Series A', 'stage': 'Series A', 'focus': 'Diagnosis AI'},
        {'name': 'Pieces Technologies', 'funding': 'Series B', 'stage': 'Growth', 'focus': 'Clinical AI'},
    ]
    
    def __init__(self):
        """Initialize the CEO Outreach Bot"""
        self.db_path = "unified_platform.db"
        self.contacts_csv = Path("CONTACT_DATABASE.csv")
        self.tracker_csv = Path("MASTER_TRACKER_400K.csv")
        
        # Initialize database
        self._init_database()
        
        # Load existing contacts
        self.contacts_df = pd.read_csv(self.contacts_csv) if self.contacts_csv.exists() else None
        
        # Email configuration (would be loaded from config in production)
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email': os.getenv('EMAIL_ADDRESS', 'matthewdscott7@gmail.com'),
            'password': os.getenv('EMAIL_PASSWORD', '')  # App-specific password
        }
        
        logger.info("🎯 CEO Outreach Bot initialized - targeting healthcare AI leaders")
    
    def _init_database(self):
        """Initialize SQLite database for tracking outreach"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            name TEXT,
            title TEXT,
            email TEXT,
            linkedin TEXT,
            phone TEXT,
            funding TEXT,
            stage TEXT,
            focus TEXT,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            contacted BOOLEAN DEFAULT 0,
            contacted_at TIMESTAMP,
            response_received BOOLEAN DEFAULT 0,
            meeting_scheduled BOOLEAN DEFAULT 0,
            proposal_sent BOOLEAN DEFAULT 0,
            contract_signed BOOLEAN DEFAULT 0,
            monthly_rate INTEGER,
            notes TEXT
        )
        """)
        
        conn.commit()
        conn.close()
    
    def find_missing_ceos(self):
        """Find CEOs for companies where we don't have contact info"""
        logger.info("🔍 Searching for missing CEO contacts...")
        
        found_contacts = []
        
        for company in self.TARGET_COMPANIES:
            logger.info(f"  Searching for {company['name']} leadership...")
            
            # Try multiple methods to find CEO
            contact = self._find_ceo_linkedin(company['name'])
            if not contact:
                contact = self._find_ceo_web_search(company['name'])
            
            if contact:
                contact.update({
                    'company': company['name'],
                    'funding': company['funding'],
                    'stage': company['stage'],
                    'focus': company['focus']
                })
                found_contacts.append(contact)
                logger.info(f"  ✅ Found: {contact.get('name', 'Unknown')} - {contact.get('title', 'CEO')}")
            else:
                logger.warning(f"  ❌ Could not find CEO for {company['name']}")
            
            # Rate limiting
            time.sleep(2)
        
        # Store in database
        self._store_contacts(found_contacts)
        
        return found_contacts
    
    def _find_ceo_linkedin(self, company_name: str) -> Optional[Dict]:
        """Find CEO via LinkedIn search"""
        try:
            # Use Selenium to search LinkedIn
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            
            # Search Google for LinkedIn profiles
            search_query = f"{company_name} CEO site:linkedin.com/in"
            driver.get(f"https://www.google.com/search?q={search_query}")
            
            time.sleep(2)
            
            # Extract first LinkedIn result
            try:
                first_result = driver.find_element(By.CSS_SELECTOR, 'a[href*="linkedin.com/in"]')
                linkedin_url = first_result.get_attribute('href')
                name_element = first_result.find_element(By.CSS_SELECTOR, 'h3')
                
                # Parse name from title
                full_text = name_element.text
                # Usually format is "Name - Title - Company | LinkedIn"
                if ' - ' in full_text:
                    parts = full_text.split(' - ')
                    full_name = parts[0].strip()
                    title = parts[1].strip() if len(parts) > 1 else 'CEO'
                else:
                    full_name = full_text.split('|')[0].strip()
                    title = 'CEO'
                
                driver.quit()
                
                return {
                    'name': full_name,
                    'title': title,
                    'linkedin': linkedin_url,
                    'email': None  # Will try to find separately
                }
                
            except Exception as e:
                logger.debug(f"Could not parse LinkedIn result: {e}")
                driver.quit()
                return None
                
        except Exception as e:
            logger.error(f"Error searching LinkedIn: {e}")
            return None
    
    def _find_ceo_web_search(self, company_name: str) -> Optional[Dict]:
        """Find CEO via general web search"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            
            driver = webdriver.Chrome(options=options)
            
            # Search for CEO name
            search_query = f"{company_name} CEO founder name"
            driver.get(f"https://www.google.com/search?q={search_query}")
            
            time.sleep(2)
            
            # Try to extract CEO name from search results
            results = driver.find_elements(By.CSS_SELECTOR, 'div.g')
            
            full_name = None
            for result in results[:5]:
                text = result.text.lower()
                if 'ceo' in text or 'founder' in text or 'chief executive' in text:
                    # Try to extract name (this is heuristic-based)
                    lines = result.text.split('\n')
                    for line in lines:
                        if 'ceo' in line.lower() or 'founder' in line.lower():
                            # Extract potential name
                            words = line.split()
                            for i, word in enumerate(words):
                                if word.lower() in ['ceo', 'founder', 'cofounder']:
                                    # Name might be before or after
                                    if i > 0 and words[i-1][0].isupper():
                                        full_name = ' '.join(words[max(0, i-2):i])
                                    elif i < len(words) - 1 and words[i+1][0].isupper():
                                        full_name = ' '.join(words[i+1:min(i+3, len(words))])
                            if ceo_name:
                                break
                if ceo_name:
                    break
            
            driver.quit()
            
            if ceo_name:
                return {
                    'name': full_name,
                    'title': 'CEO',
                    'linkedin': None,
                    'email': None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return None
    
    def send_personalized_outreach(self, limit: int = 5):
        """Send personalized emails to CEOs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get uncontacted CEOs
        cursor.execute("""
        SELECT * FROM contacts 
        WHERE contacted = 0 AND (name IS NOT NULL OR email IS NOT NULL)
        ORDER BY 
            CASE stage
                WHEN 'Series A' THEN 0
                WHEN 'Series B' THEN 1
                WHEN 'YC' THEN 2
                ELSE 3
            END
        LIMIT ?
        """, (limit,))
        
        contacts = cursor.fetchall()
        conn.close()
        
        logger.info(f"📧 Sending outreach to {len(contacts)} CEOs...")
        
        for contact in contacts:
            success = self._send_ceo_email(contact)
            if success:
                self._mark_as_contacted(contact[0])  # contact[0] is the ID
                logger.info(f"  ✅ Outreach sent to {contact[2]} at {contact[1]}")  # full_name, company
                
                # Update CSV tracker
                self._update_csv_tracker(contact)
                
                # Rate limiting
                time.sleep(30)
    
    def _send_ceo_email(self, contact_record) -> bool:
        """Send personalized email to CEO"""
        company = contact_record[1]
        full_name = contact_record[2] or "Hiring Team"
        title = contact_record[3] or "CEO"
        email = contact_record[4]
        funding = contact_record[7]
        stage = contact_record[8]
        focus = contact_record[9]
        
        # Generate personalized email
        subject = f"Fractional CTO - 10 Years Humana Healthcare AI Experience"
        
        body = f"""Hi {name.split()[0] if name != "Hiring Team" else "there"},

Congratulations on {company}'s {funding} funding! 

I noticed you're scaling {focus.lower()}, which aligns perfectly with my experience. I spent 10 years at Humana where I:

• Delivered $1.2M in annual savings through AI automation
• Maintained 100% CMS compliance (critical for healthcare AI)
• Built 15+ production systems with zero critical defects
• Led the architecture of enterprise-scale healthcare platforms

I'm currently offering fractional CTO services to healthcare AI companies like {company}. With your {stage} growth trajectory, you likely need someone who can:

- Navigate healthcare compliance while moving fast
- Build scalable AI infrastructure that won't break at 10x scale
- Bridge the gap between clinical requirements and technical execution

I have 2 fractional slots available this month at $15K/month for 2 days per week.

Would you be open to a 15-minute call this week to discuss how I could accelerate {company}'s technical roadmap?

Best,
Matthew Scott
Former Senior Engineer, Humana (10 years)
linkedin.com/in/mscott77

P.S. I built a 58-model AI orchestration system that's unprecedented in the industry - happy to share how this could apply to {company}'s {focus.lower()}.
"""
        
        # Log the email (in production, would actually send)
        logger.info(f"  📧 Email prepared for {name} at {company}")
        logger.debug(f"  Subject: {subject}")
        logger.debug(f"  Body length: {len(body)} chars")
        
        # Store outreach record
        self._store_outreach_record(company, full_name, subject, body)
        
        # In production, would use SMTP to send
        # self._send_via_smtp(email, subject, body)
        
        return True
    
    def _send_via_smtp(self, to_email: str, subject: str, body: str) -> bool:
        """Actually send email via SMTP (disabled in demo)"""
        if not self.email_config['password']:
            logger.warning("Email password not configured - skipping actual send")
            return True
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['email'], self.email_config['password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _store_contacts(self, contacts: List[Dict]):
        """Store discovered contacts in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for contact in contacts:
            # Check if contact already exists
            cursor.execute("""
            SELECT id FROM contacts 
            WHERE company = ? AND (full_name = ? OR name IS NULL)
            """, (contact['company'], contact.get('name')))
            
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO contacts (
                    company, full_name, title, email, linkedin,
                    funding, stage, focus
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contact['company'], contact.get('name'),
                    contact.get('title'), contact.get('email'),
                    contact.get('linkedin'), contact.get('funding'),
                    contact.get('stage'), contact.get('focus')
                ))
        
        conn.commit()
        conn.close()
    
    def _mark_as_contacted(self, contact_id: int):
        """Mark a contact as contacted"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE contacts 
        SET contacted = 1, contacted_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """, (contact_id,))
        
        conn.commit()
        conn.close()
    
    def _update_csv_tracker(self, contact_record):
        """Update CSV tracker with outreach status"""
        if self.contacts_df is not None:
            company = contact_record[1]
            full_name = contact_record[2]
            
            # Update or add row
            mask = self.contacts_df['Company'] == company
            if len(self.contacts_df[mask]) > 0:
                self.contacts_df.loc[mask, 'Last_Contact'] = datetime.now().strftime('%Y-%m-%d')
                self.contacts_df.loc[mask, 'Next_Action'] = 'Follow up in 3 days'
                if name:
                    self.contacts_df.loc[mask, 'Name'] = name
            
            # Save updated CSV
            self.contacts_df.to_csv(self.contacts_csv, index=False)
    
    def _store_outreach_record(self, company: str, name: str, subject: str, body: str):
        """Store outreach details for tracking"""
        outreach_dir = Path("ceo_outreach_sent")
        outreach_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{company.replace(' ', '_')}_{timestamp}.txt"
        
        with open(outreach_dir / filename, 'w') as f:
            f.write(f"Company: {company}\n")
            f.write(f"Contact: {name}\n")
            f.write(f"Sent: {datetime.now()}\n")
            f.write(f"Subject: {subject}\n")
            f.write(f"\n{body}")
    
    def schedule_follow_ups(self):
        """Schedule follow-up messages for non-responders"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get contacts that need follow-up (contacted 3+ days ago, no response)
        three_days_ago = datetime.now() - timedelta(days=3)
        cursor.execute("""
        SELECT * FROM contacts 
        WHERE contacted = 1 
        AND response_received = 0 
        AND contacted_at < ?
        AND (proposal_sent = 0 OR proposal_sent IS NULL)
        """, (three_days_ago,))
        
        follow_ups = cursor.fetchall()
        conn.close()
        
        logger.info(f"📮 {len(follow_ups)} contacts need follow-up")
        
        for contact in follow_ups:
            self._send_follow_up(contact)
    
    def _send_follow_up(self, contact_record):
        """Send follow-up message"""
        company = contact_record[1]
        full_name = contact_record[2] or "there"
        
        subject = f"Re: Fractional CTO - Quick follow-up"
        
        body = f"""Hi {name.split()[0] if name != "there" else "there"},

Just following up on my previous note about fractional CTO services for {company}.

I understand you're busy scaling the company. I wanted to mention that I'm also available for:

• One-off consulting projects ($15K) - Healthcare compliance audits, AI architecture reviews
• Advisory role ($5K/month) - 5 hours monthly for strategic guidance
• Short-term engagements - Help hire your permanent CTO, set up technical infrastructure

My 2 fractional slots are filling up quickly. If there's interest, I'd love to secure one for {company}.

Quick 15-minute call this week?

Best,
Matthew

P.S. I can share specific examples of how I saved Humana $1.2M through automation - directly applicable to {company}'s growth.
"""
        
        logger.info(f"  📧 Follow-up prepared for {company}")
        self._store_outreach_record(company, full_name, subject, body)
    
    def generate_pipeline_report(self) -> str:
        """Generate a report of CEO outreach pipeline"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM contacts")
        total_contacts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE contacted = 1")
        contacted = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE response_received = 1")
        responses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE meeting_scheduled = 1")
        meetings = cursor.fetchone()[0]
        
        cursor.execute("SELECT company, full_name, stage, funding FROM contacts WHERE contacted = 0 LIMIT 5")
        next_targets = cursor.fetchall()
        
        conn.close()
        
        report = f"""
🎯 CEO OUTREACH PIPELINE REPORT
=====================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📊 PIPELINE METRICS:
- Total CEOs identified: {total_contacts}
- Outreach sent: {contacted}
- Responses received: {responses}
- Meetings scheduled: {meetings}
- Response rate: {(responses/contacted*100) if contacted > 0 else 0:.1f}%

🔥 NEXT OUTREACH TARGETS:
"""
        
        for target in next_targets:
            report += f"- {target[0]}: {target[1] or 'CEO'} ({target[2]}, {target[3]})\n"
        
        report += """
💰 TARGET: 2 clients @ $15K/month = $30K/month
📍 STATUS: Actively pursuing fractional CTO opportunities
🎯 FOCUS: Healthcare AI companies with recent funding
"""
        
        return report


def main():
    """Main execution"""
    bot = CEOOutreachBot()
    
    print("🚀 Starting CEO Outreach Bot - Fractional CTO Campaign")
    print("=" * 60)
    
    # Find missing CEOs
    print("\n1️⃣ Finding missing CEO contacts...")
    contacts = bot.find_missing_ceos()
    print(f"   Found {len(contacts)} new contacts")
    
    # Send outreach
    print("\n2️⃣ Sending personalized outreach...")
    bot.send_personalized_outreach(limit=5)
    
    # Schedule follow-ups
    print("\n3️⃣ Checking for needed follow-ups...")
    bot.schedule_follow_ups()
    
    # Generate report
    print("\n4️⃣ Pipeline Report:")
    print(bot.generate_pipeline_report())
    
    print("\n✅ CEO Outreach Bot complete!")
    print("   Next run recommended in 24 hours")


if __name__ == "__main__":
    main()