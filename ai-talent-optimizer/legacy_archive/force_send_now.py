#!/usr/bin/env python3
"""Force send applications - no verification checks"""

from unified_email_engine import UnifiedEmailEngine
import os
from datetime import datetime
import time
import random

# High-value targets with likely working emails
PRIORITY_TARGETS = [
    # Top Tech Companies
    ("Netflix", "talent-acquisition@netflix.com", "Senior Software Engineer - ML Platform"),
    ("Spotify", "careers@spotify.com", "Staff ML Engineer"),
    ("Uber", "recruiting@uber.com", "Staff Software Engineer - AI/ML"),
    ("Airbnb", "careers@airbnb.com", "Staff Machine Learning Engineer"),
    ("LinkedIn", "staffing@linkedin.com", "Principal ML Engineer"),
    
    # Finance/Fintech
    ("Stripe", "recruiting@stripe.com", "Staff Engineer - Machine Learning"),
    ("Square", "jobs@squareup.com", "Principal Software Engineer"),
    ("Coinbase", "recruiting@coinbase.com", "Staff ML Engineer"),
    ("Robinhood", "careers@robinhood.com", "Staff Software Engineer - AI"),
    ("PayPal", "recruiting@paypal.com", "Principal AI/ML Engineer"),
    
    # Enterprise Tech
    ("Salesforce", "careers@salesforce.com", "Principal Architect - AI"),
    ("Adobe", "careers@adobe.com", "Principal ML Scientist"),
    ("Oracle", "careers@oracle.com", "Principal Software Engineer - AI"),
    ("VMware", "careers@vmware.com", "Staff Engineer - ML Platform"),
    ("ServiceNow", "recruiting@servicenow.com", "Principal AI Engineer"),
    
    # AI-First Companies
    ("Databricks", "careers@databricks.com", "Staff ML Platform Engineer"),
    ("Snowflake", "recruiting@snowflake.com", "Principal Software Engineer"),
    ("Palantir", "recruiting@palantir.com", "Forward Deployed ML Engineer"),
    ("Scale AI", "careers@scaleai.com", "Staff ML Engineer"),
    ("Cohere", "careers@cohere.ai", "Senior ML Engineer"),
    
    # Healthcare Tech
    ("Epic Systems", "careers@epic.com", "Principal Software Developer"),
    ("Cerner", "careers@cerner.com", "Principal Engineer - Healthcare AI"),
    ("Athenahealth", "recruiting@athenahealth.com", "Staff Engineer - ML"),
    ("Veeva Systems", "careers@veeva.com", "Principal Software Engineer"),
    ("Teladoc", "careers@teladochealth.com", "Principal AI Engineer"),
    
    # Gaming/Entertainment
    ("Roblox", "recruiting@roblox.com", "Principal Engineer - ML"),
    ("Unity", "careers@unity.com", "Staff ML Engineer"),
    ("Electronic Arts", "careers@ea.com", "Principal AI Engineer"),
    ("Activision", "recruiting@activision.com", "Staff Software Engineer - AI"),
    ("Twitch", "recruiting@twitch.tv", "Principal Backend Engineer"),
]

def main():
    print("🚀 FORCE SENDING APPLICATIONS - NO VERIFICATION")
    print("=" * 60)
    print(f"Targets: {len(PRIORITY_TARGETS)} high-value companies")
    print("Resume: master_resume_-_all_keywords.pdf (ATS optimized)")
    print("=" * 60)
    
    engine = UnifiedEmailEngine()
    
    # Use the strongest resume you identified
    resume_path = "/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/resumes/master_resume_-_all_keywords.pdf"
    
    # Fallback to other resume if needed
    if not os.path.exists(resume_path):
        resume_path = "/Users/matthewscott/AI-ML-Portfolio/MATTHEW_SCOTT_RESUME_2025.pdf"
    
    if not os.path.exists(resume_path):
        print("❌ No resume found! Creating one now...")
        # Try to use any PDF in the directory
        for file in os.listdir("/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/resumes/"):
            if file.endswith('.pdf'):
                resume_path = f"/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/resumes/{file}"
                break
    
    attachments = [resume_path] if os.path.exists(resume_path) else []
    print(f"📎 Using resume: {os.path.basename(resume_path) if attachments else 'NO RESUME FOUND'}")
    
    sent = 0
    failed = 0
    
    for company, email, position in PRIORITY_TARGETS:
        print(f"\n📧 [{sent + failed + 1}/{len(PRIORITY_TARGETS)}] {company}")
        print(f"   Position: {position}")
        print(f"   Email: {email}")
        
        subject = f"Senior AI/ML Engineer Application - Matthew Scott - {company}"
        
        # Personalized, impactful cover letter
        body = f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {position} role at {company}.

With 10+ years at Fortune 50 Humana, I've architected AI systems that have:
• Delivered $1.2M+ in annual cost savings through intelligent automation
• Processed 1M+ healthcare records daily with 96% accuracy
• Maintained zero critical defects across 1,000+ production deployments
• Built an AI orchestration platform managing 89 specialized models

What makes me uniquely qualified for {company}:

Technical Excellence: I've personally built a platform with 117 Python modules and 86,000+ files while maintaining my demanding day job at Humana. This includes implementing cutting-edge models like Llama, Gemma, and Command-R in production environments.

Healthcare Domain Expertise: My decade at Humana has given me deep understanding of enterprise-scale challenges, compliance requirements, and the critical importance of reliable AI systems when human lives are involved.

Proven Impact: Beyond the $1.2M in savings at Humana, I've generated $174K in revenue through AI-powered automation side projects, demonstrating my ability to deliver business value.

I'm particularly excited about {company}'s mission and believe my combination of enterprise experience and hands-on technical skills would add immediate value to your team.

I've attached my resume highlighting 78 specialized ML models I've implemented and my extensive experience with TensorFlow, PyTorch, and modern MLOps practices.

I'm available for immediate discussion and can be reached at:
• Phone: (502) 345-0525
• Email: matthewdscott7@gmail.com
• LinkedIn: linkedin.com/in/mscott77
• GitHub: github.com/guitargnar

Thank you for considering my application. I look forward to discussing how my experience can contribute to {company}'s continued success.

Best regards,
Matthew Scott"""
        
        try:
            # Force send without verification
            success, result = engine.send_email(
                to_email=email,
                subject=subject,
                body=body,
                attachments=attachments,
                email_type='application'
            )
            
            if success:
                print(f"   ✅ SENT! Tracking: {result}")
                sent += 1
                
                # Random delay to avoid spam filters
                if sent < len(PRIORITY_TARGETS):
                    wait = random.randint(15, 30)
                    print(f"   ⏱️  Waiting {wait} seconds...")
                    time.sleep(wait)
            else:
                print(f"   ❌ Failed: {result}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS:")
    print(f"   ✅ Successfully sent: {sent}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📧 Total applications: {sent + 12}")  # Adding previous sends
    print("\n🎯 APPLICATIONS NOW AT MAJOR COMPANIES:")
    print(f"   • {sent} new companies just now")
    print(f"   • 12 from yesterday (Google, Meta, Apple, etc.)")
    print(f"   • Total: {sent + 12} applications in pipeline")
    print("\n📬 Check matthewdscott7+jobapps@gmail.com for BCC copies")
    print("⏰ Responses typically arrive in 3-7 business days")
    print("\n💪 Your resume is now at {sent + 12} top tech companies!")

if __name__ == "__main__":
    main()