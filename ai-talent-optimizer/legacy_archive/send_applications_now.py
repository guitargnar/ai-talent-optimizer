#!/usr/bin/env python3
"""
SEND JOB APPLICATIONS NOW
Using Matthew Scott's resume to apply to high-paying tech jobs
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import time
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration
EMAIL = os.getenv('EMAIL_ADDRESS', 'matthewdscott7@gmail.com')
PASSWORD = os.getenv('EMAIL_APP_PASSWORD', '')

# High-value target companies
TARGET_COMPANIES = [
    {
        "company": "OpenAI",
        "email": "careers@openai.com",
        "position": "Principal Engineer - AI Infrastructure",
        "salary": "$500K+"
    },
    {
        "company": "Anthropic",
        "email": "careers@anthropic.com",
        "position": "Staff Software Engineer - Claude",
        "salary": "$450K+"
    },
    {
        "company": "Google DeepMind",
        "email": "deepmind-careers@google.com",
        "position": "Senior Staff Engineer - LLM",
        "salary": "$500K+"
    },
    {
        "company": "Meta AI",
        "email": "airecruiting@meta.com",
        "position": "Principal ML Engineer",
        "salary": "$475K+"
    },
    {
        "company": "Microsoft",
        "email": "staffing@microsoft.com",
        "position": "Principal Software Engineer - Azure AI",
        "salary": "$425K+"
    },
    {
        "company": "Apple",
        "email": "aiml-jobs@apple.com", 
        "position": "Senior Machine Learning Engineer",
        "salary": "$450K+"
    },
    {
        "company": "NVIDIA",
        "email": "careers@nvidia.com",
        "position": "Principal Engineer - AI Systems",
        "salary": "$500K+"
    },
    {
        "company": "Databricks",
        "email": "recruiting@databricks.com",
        "position": "Staff Software Engineer - ML Platform",
        "salary": "$425K+"
    },
    {
        "company": "Snowflake",
        "email": "careers@snowflake.com",
        "position": "Principal Engineer - AI/ML",
        "salary": "$450K+"
    },
    {
        "company": "Cohere",
        "email": "careers@cohere.ai",
        "position": "Staff Engineer - LLM Infrastructure",
        "salary": "$400K+"
    }
]

def create_email_body(company, position):
    """Create personalized email body"""
    return f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {position} role at {company}.

With 10+ years at Fortune 50 Humana, I've delivered $1.2M+ in annual savings through AI automation while maintaining zero critical defects in production systems. My unique value proposition combines:

• Enterprise Scale: Built AI systems processing 1M+ healthcare records daily
• Technical Depth: Architected platform with 117 Python modules and 89 orchestrated AI models
• Healthcare Domain Expertise: 100% CMS compliance maintained for 5+ years
• Innovation Leadership: Filed 3 AI patents, trained 50+ engineers, led teams of 12+

Recent achievements particularly relevant to {company}:
- Built Mirador, an 89-model AI orchestration system achieving 0.83/1.0 consciousness score
- Generated $174K revenue through AI-powered e-commerce automation
- Created AI Talent Optimizer managing 86,000+ Python files in production
- Published open-source PromptLibrary with 500+ GitHub stars

I'm particularly excited about {company}'s work in AI and believe my combination of enterprise experience and cutting-edge implementation would add immediate value to your team.

I've attached my resume for your review and would welcome the opportunity to discuss how my experience aligns with your needs.

Best regards,
Matthew Scott
(502) 345-0525
matthewdscott7@gmail.com
linkedin.com/in/mscott77
github.com/guitargnar
"""

def send_application(company_info):
    """Send application email with resume"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = company_info['email']
        msg['Bcc'] = 'matthewdscott7+jobapps@gmail.com'
        msg['Subject'] = f"Application for {company_info['position']} - Matthew Scott"
        
        # Add body
        body = create_email_body(company_info['company'], company_info['position'])
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach resume
        resume_path = "/Users/matthewscott/AI-ML-Portfolio/MATTHEW_SCOTT_RESUME_2025.pdf"
        if os.path.exists(resume_path):
            with open(resume_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="Matthew_Scott_Resume_2025.pdf"'
            )
            msg.attach(part)
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL, [company_info['email'], 'matthewdscott7+jobapps@gmail.com'], text)
        
        print(f"✅ SENT to {company_info['company']} - {company_info['position']} ({company_info['salary']})")
        return True
        
    except Exception as e:
        print(f"❌ FAILED {company_info['company']}: {str(e)}")
        return False

def main():
    print("🚀 SENDING JOB APPLICATIONS WITH MATTHEW SCOTT'S RESUME")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {len(TARGET_COMPANIES)} high-value companies")
    print("=" * 60)
    
    if not PASSWORD:
        print("❌ Email password not configured in environment")
        print("Set EMAIL_APP_PASSWORD environment variable")
        return
    
    sent = 0
    failed = 0
    
    for i, company in enumerate(TARGET_COMPANIES, 1):
        print(f"\n[{i}/{len(TARGET_COMPANIES)}] Applying to {company['company']}...")
        
        if send_application(company):
            sent += 1
        else:
            failed += 1
        
        # Wait between sends
        if i < len(TARGET_COMPANIES):
            wait_time = random.randint(30, 60)
            print(f"⏱️  Waiting {wait_time} seconds...")
            time.sleep(wait_time)
    
    print("\n" + "=" * 60)
    print("📊 RESULTS:")
    print(f"  ✅ Sent: {sent}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📧 All applications BCC'd to: matthewdscott7+jobapps@gmail.com")
    print("\n🎯 Check for responses in 3-7 days!")
    print("=" * 60)

if __name__ == "__main__":
    main()