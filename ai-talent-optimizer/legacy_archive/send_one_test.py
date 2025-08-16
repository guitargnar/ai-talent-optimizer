#!/usr/bin/env python3
"""Send one test application to Netflix"""

from unified_email_engine import UnifiedEmailEngine
import os

def main():
    print("Sending test application to Netflix...")
    
    engine = UnifiedEmailEngine()
    resume = "/Users/matthewscott/AI-ML-Portfolio/MATTHEW_SCOTT_RESUME_2025.pdf"
    
    if not os.path.exists(resume):
        print(f"Resume not found at {resume}")
        # List available resumes
        resume_dir = "/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/resumes/"
        if os.path.exists(resume_dir):
            pdfs = [f for f in os.listdir(resume_dir) if f.endswith('.pdf')]
            if pdfs:
                resume = os.path.join(resume_dir, pdfs[0])
                print(f"Using: {resume}")
    
    attachments = [resume] if os.path.exists(resume) else []
    
    body = """Dear Netflix Hiring Team,

I'm writing about Staff ML Engineer opportunities at Netflix.

With 10+ years at Fortune 50 Humana, I've delivered $1.2M in annual savings through AI automation while building production systems processing 1M+ records daily. My platform includes 117 Python modules and 89 orchestrated AI models.

I'm excited about Netflix's innovation in ML-powered content recommendations and believe my enterprise-scale experience would add immediate value.

Resume attached. Available for immediate discussion.

Best regards,
Matthew Scott
(502) 345-0525
matthewdscott7@gmail.com
linkedin.com/in/mscott77
github.com/guitargnar"""
    
    try:
        success, result = engine.send_email(
            to_email="talent@netflix.com",
            subject="Staff ML Engineer Application - Matthew Scott",
            body=body,
            attachments=attachments,
            email_type='application'
        )
        
        if success:
            print(f"✅ SENT! Tracking: {result}")
        else:
            print(f"❌ Failed: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()