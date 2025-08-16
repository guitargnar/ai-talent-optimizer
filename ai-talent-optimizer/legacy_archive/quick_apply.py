#!/usr/bin/env python3
"""Quick application sender using working email system"""

from unified_email_engine import UnifiedEmailEngine
import os
from datetime import datetime

# Top tech companies to apply to
TARGETS = [
    ("Google", "careers@google.com", "Principal Engineer - AI/ML"),
    ("Meta", "recruiting@meta.com", "Staff Software Engineer"),  
    ("Apple", "aiml-jobs@apple.com", "Senior ML Engineer"),
    ("Microsoft", "staffing@microsoft.com", "Principal Engineer - Azure AI"),
    ("Amazon", "amazonjobs@amazon.com", "Principal Engineer - AWS AI")
]

def main():
    print("🚀 QUICK JOB APPLICATION SENDER")
    print("=" * 60)
    
    # Initialize email engine
    engine = UnifiedEmailEngine()
    
    # Attach resume
    resume_path = "/Users/matthewscott/AI-ML-Portfolio/MATTHEW_SCOTT_RESUME_2025.pdf"
    attachments = [resume_path] if os.path.exists(resume_path) else []
    
    sent_count = 0
    
    for company, email, position in TARGETS:
        print(f"\n📧 Applying to {company} - {position}")
        
        subject = f"Application for {position} - Matthew Scott"
        
        body = f"""Dear {company} Hiring Team,

I am writing to express my interest in the {position} role.

With 10+ years at Fortune 50 Humana, I've delivered $1.2M+ annual savings through AI automation. 
I've built production systems with 117 Python modules processing 1M+ records daily while maintaining 
100% compliance and zero critical defects.

My recent work includes architecting an 89-model AI orchestration system and generating $174K 
revenue through AI-powered automation.

I would welcome the opportunity to discuss how my enterprise experience and AI expertise can 
contribute to {company}'s continued innovation.

Best regards,
Matthew Scott
(502) 345-0525
matthewdscott7@gmail.com
linkedin.com/in/mscott77
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
                sent_count += 1
            else:
                print(f"  ❌ Failed: {result}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: Sent {sent_count}/{len(TARGETS)} applications")
    print("📧 All BCCs sent to: matthewdscott7+jobapps@gmail.com")
    print("Check responses in 3-7 days!")

if __name__ == "__main__":
    main()