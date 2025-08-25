#!/usr/bin/env python3
"""Send more applications to companies with verified emails"""

from unified_email_engine import UnifiedEmailEngine
import os
from datetime import datetime
import time
import random

# Companies with VERIFIED working emails
VERIFIED_TARGETS = [
    ("Databricks", "recruiting@databricks.com", "Staff ML Engineer"),
    ("Stripe", "jobs@stripe.com", "Principal Engineer"),
    ("Square", "recruiting@squareup.com", "Staff Software Engineer"),
    ("Uber", "recruiting@uber.com", "Senior Staff Engineer - AI"),
    ("Lyft", "recruiting@lyft.com", "Principal ML Engineer"),
    ("Airbnb", "recruiting@airbnb.com", "Staff Software Engineer"),
    ("LinkedIn", "talent@linkedin.com", "Principal Engineer"),
    ("Netflix", "talent@netflix.com", "Senior Software Engineer"),
    ("Spotify", "jobs@spotify.com", "Staff Backend Engineer"),
    ("Slack", "recruiting@slack.com", "Principal Engineer"),
    ("Zoom", "careers@zoom.us", "Staff Engineer - AI/ML"),
    ("DocuSign", "recruiting@docusign.com", "Principal Engineer"),
    ("Salesforce", "recruiting@salesforce.com", "Principal Architect"),
    ("Adobe", "jobs@adobe.com", "Principal Scientist - AI"),
    ("VMware", "jobs@vmware.com", "Staff Engineer"),
    ("Splunk", "recruiting@splunk.com", "Principal Software Engineer"),
    ("Twilio", "jobs@twilio.com", "Staff Engineer"),
    ("Pinterest", "recruiting@pinterest.com", "Staff ML Engineer"),
    ("Reddit", "jobs@reddit.com", "Staff Backend Engineer"),
    ("Discord", "jobs@discord.com", "Senior Staff Engineer")
]

def main():
    print("🚀 SENDING MORE APPLICATIONS NOW")
    print("=" * 60)
    print(f"Target: {len(VERIFIED_TARGETS)} verified companies")
    print("=" * 60)
    
    engine = UnifiedEmailEngine()
    resume_path = "/Users/matthewscott/AI-ML-Portfolio/MATTHEW_SCOTT_RESUME_2025.pdf"
    attachments = [resume_path] if os.path.exists(resume_path) else []
    
    sent = 0
    failed = 0
    
    for company, email, position in VERIFIED_TARGETS:
        print(f"\n📧 [{sent + failed + 1}/{len(VERIFIED_TARGETS)}] {company} - {position}")
        
        subject = f"Application for {position} - Matthew Scott"
        
        body = f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {position} role at {company}.

With 10+ years at Fortune 50 Humana, I've delivered $1.2M+ in annual savings through AI automation while maintaining zero critical defects in production systems. My unique combination of enterprise healthcare experience and cutting-edge AI implementation makes me an ideal candidate for this role.

Key achievements relevant to {company}:
• Built AI systems processing 1M+ records daily with 96% accuracy
• Architected platform with 117 Python modules and 89 orchestrated AI models  
• Led teams of 12+ engineers while maintaining hands-on technical excellence
• Generated $174K revenue through AI-powered automation side project

I'm particularly excited about {company}'s innovations in technology and believe my experience scaling AI systems at enterprise level would add immediate value to your team.

I've attached my resume for your review and would welcome the opportunity to discuss how my skills align with your needs.

Best regards,
Matthew Scott
(502) 345-0525
matthewdscott7@gmail.com
linkedin.com/in/mscott77
github.com/guitargnar
"""
        
        try:
            success, result = engine.send_email(
                to_email=email,
                subject=subject,
                body=body,
                attachments=attachments,
                email_type='application'
            )
            
            if success:
                print(f"  ✅ SENT! Tracking: {result}")
                sent += 1
                
                # Wait between sends
                if sent < len(VERIFIED_TARGETS):
                    wait = random.randint(20, 40)
                    print(f"  ⏱️  Waiting {wait} seconds...")
                    time.sleep(wait)
            else:
                print(f"  ❌ Failed: {result}")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS:")
    print(f"  ✅ Sent: {sent}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📧 Total applications to date: {sent + 16}")
    print("\n🎯 Your resume is now at {sent + 16} major tech companies!")
    print("📧 All BCC'd to: matthewdscott7+jobapps@gmail.com")

if __name__ == "__main__":
    main()