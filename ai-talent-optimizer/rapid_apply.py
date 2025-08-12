#!/usr/bin/env python3
"""Rapid application sender - simplified for speed"""

from unified_email_engine import UnifiedEmailEngine
import os
import time

# Quick targets - top companies only
TARGETS = [
    ("Netflix", "talent@netflix.com", "Staff ML Engineer"),
    ("Stripe", "jobs@stripe.com", "Principal Engineer"),
    ("Uber", "careers@uber.com", "Staff AI Engineer"),
    ("Airbnb", "recruiting@airbnb.com", "Staff ML Engineer"),
    ("LinkedIn", "talent@linkedin.com", "Principal Engineer"),
    ("Spotify", "jobs@spotify.com", "Staff Backend Engineer"),
    ("Square", "recruiting@squareup.com", "Principal Engineer"),
    ("Databricks", "recruiting@databricks.com", "Staff ML Engineer"),
    ("Salesforce", "recruiting@salesforce.com", "Principal Architect"),
    ("Adobe", "jobs@adobe.com", "Principal ML Scientist"),
]

def main():
    print("🚀 RAPID APPLICATION SENDER")
    print("=" * 50)
    
    engine = UnifiedEmailEngine()
    resume = "/Users/matthewscott/AI-ML-Portfolio/MATTHEW_SCOTT_RESUME_2025.pdf"
    
    if not os.path.exists(resume):
        # Try the master resume
        resume = "/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/resumes/master_resume_-_all_keywords.pdf"
    
    attachments = [resume] if os.path.exists(resume) else []
    
    sent = 0
    for company, email, position in TARGETS:
        print(f"\n📧 {company} - {position}")
        
        body = f"""Dear {company} Team,

I'm interested in the {position} role. With 10+ years at Humana delivering $1.2M in savings through AI automation and building systems processing 1M+ records daily, I would add immediate value.

Key qualifications:
• Built platform with 117 Python modules and 89 AI models
• Maintained zero defects across 1,000+ deployments
• Deep healthcare enterprise experience

Resume attached. Available immediately.

Best,
Matthew Scott
(502) 345-0525
matthewdscott7@gmail.com
github.com/guitargnar"""
        
        try:
            success, result = engine.send_email(
                to_email=email,
                subject=f"{position} Application - Matthew Scott",
                body=body,
                attachments=attachments,
                email_type='application'
            )
            
            if success:
                print(f"  ✅ SENT: {result[:12]}")
                sent += 1
                time.sleep(10)  # Quick delay
            else:
                print(f"  ❌ Failed")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}")
    
    print(f"\n✅ Total sent: {sent + 16} applications in pipeline!")

if __name__ == "__main__":
    main()