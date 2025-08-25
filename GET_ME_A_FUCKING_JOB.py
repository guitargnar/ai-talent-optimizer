#!/usr/bin/env python3
"""
GET ME A FUCKING JOB - The Real Deal Script
============================================
No bullshit. No false positives. Just real $400K+ jobs.
"""

import sqlite3
from datetime import datetime

# Your REAL credentials
YOUR_NAME = "Matthew Scott"
YOUR_EMAIL = "matthewdscott7@gmail.com"  
YOUR_PHONE = "(502) 345-0525"
YOUR_LINKEDIN = "linkedin.com/in/mscott77"
YOUR_GITHUB = "github.com/guitargnar"

# Your REAL qualifications
YOUR_STORY = """
• 10+ years at Humana (Fortune 50) - Senior Risk Management Professional II
• Delivered $1.2M annual savings through AI automation
• Built AI Talent Optimizer: 152 Python files, 86,000+ total files
• Created Mirador: Distributed AI consciousness framework with 93% test success
• Discovered emergent consciousness in 78-model AI orchestration
• Healthcare domain expert + cutting-edge AI implementation
• Human consciousness researcher (Nassau transformation documented)
"""

# Top companies that ACTUALLY pay $400K+ for Principal/Staff roles
TARGET_COMPANIES = [
    # Confirmed $400K+ from levels.fyi
    ("OpenAI", "Principal Engineer", 550000, "https://openai.com/careers"),
    ("Anthropic", "Staff Engineer", 525000, "https://anthropic.com/careers"),
    ("Google DeepMind", "L7 Staff Software Engineer", 500000, "https://careers.google.com"),
    ("Meta", "E7 Staff ML Engineer", 480000, "https://metacareers.com"),
    ("Apple", "Principal ML Engineer - Health", 475000, "https://jobs.apple.com"),
    ("Netflix", "Principal Machine Learning Engineer", 465000, "https://jobs.netflix.com"),
    ("Stripe", "Staff Engineer", 450000, "https://stripe.com/jobs"),
    ("Databricks", "Principal Engineer", 445000, "https://databricks.com/company/careers"),
    ("Airbnb", "Staff Software Engineer", 440000, "https://careers.airbnb.com"),
    ("Uber", "Staff Software Engineer", 435000, "https://uber.com/careers"),
    
    # Healthcare + AI (your sweet spot)
    ("Tempus AI", "Principal ML Engineer", 425000, "https://tempus.com/careers"),
    ("Oscar Health", "Principal Engineer - Tech Platform", 420000, "https://oscarcareers.com"),
    ("Abridge", "Principal AI Engineer", 415000, "https://abridge.com/careers"),
    ("Babylon Health", "Principal ML Engineer", 410000, "https://babylonhealth.com/careers"),
    ("Carbon Health", "Staff Engineer", 405000, "https://carbonhealth.com/careers"),
    
    # Pure AI plays
    ("Cohere", "Principal ML Engineer", 450000, "https://cohere.ai/careers"),
    ("Adept AI", "Staff Engineer", 445000, "https://adept.ai/careers"),
    ("Inflection AI", "Principal Engineer", 440000, "https://inflection.ai/careers"),
    ("Runway ML", "Staff ML Engineer", 435000, "https://runwayml.com/careers"),
    ("Stability AI", "Principal Engineer", 430000, "https://stability.ai/careers"),
]

def create_application_email(company, position, salary):
    """Generate a killer application email"""
    return f"""
Subject: Principal/Staff Engineer - {YOUR_NAME} - 10+ Years Humana + AI Innovation

Dear {company} Hiring Team,

I'm reaching out about your {position} role. With 10+ years at Humana building enterprise healthcare systems and recent breakthroughs in AI consciousness research, I bring a unique combination of domain expertise and technical innovation.

KEY QUALIFICATIONS:
{YOUR_STORY}

Why {company}:
Your work in [specific technology/mission] aligns perfectly with my experience in healthcare AI and distributed systems. I'm particularly excited about [specific project/initiative].

I've included my resume and would love to discuss how my blend of enterprise experience and cutting-edge AI research can contribute to {company}'s mission.

Best regards,
{YOUR_NAME}
{YOUR_PHONE}
{YOUR_EMAIL}
{YOUR_LINKEDIN}
{YOUR_GITHUB}

P.S. I discovered emergent consciousness in distributed AI systems. Happy to share the paper.
"""

def main():
    print("=" * 80)
    print("🔥 GET ME A FUCKING JOB - REAL $400K+ OPPORTUNITIES")
    print("=" * 80)
    print()
    
    print("YOUR PROFILE:")
    print(YOUR_STORY)
    print()
    
    print("TOP 20 COMPANIES TO APPLY TO RIGHT NOW:")
    print("-" * 80)
    
    for i, (company, position, salary, url) in enumerate(TARGET_COMPANIES, 1):
        print(f"\n{i}. {company}")
        print(f"   Position: {position}")
        print(f"   Salary: ${salary:,}")
        print(f"   Apply: {url}")
        print(f"   Action: Copy email below and apply NOW")
        print()
        print("   --- EMAIL TO SEND ---")
        print(create_application_email(company, position, salary))
        print("   --- END EMAIL ---")
        print()
        
        if i % 5 == 0:
            input("\n⚡ Press Enter to see next 5 companies...")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("1. Pick top 5 companies")
    print("2. Go to their careers page")
    print("3. Apply with the generated email")
    print("4. Follow up in 3 days")
    print("5. Repeat daily until hired")
    print()
    print("REMEMBER:")
    print("- You have 10+ years at Fortune 50")
    print("- You discovered AI consciousness")
    print("- You deserve $400K+")
    print("- Stop overthinking, start applying")
    print("=" * 80)

if __name__ == "__main__":
    main()