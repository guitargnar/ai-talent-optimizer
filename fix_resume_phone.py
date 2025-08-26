#!/usr/bin/env python3
"""
Fix Resume Phone Number
Updates all resume references to include complete phone number
"""

import os
import json
from pathlib import Path

def fix_phone_number():
    """Fix phone number in all configuration and documentation"""
    
    correct_phone = "502-345-0525"
    
    # Fix in utils/config.py
    config_path = Path("utils/config.py")
    if config_path.exists():
        content = config_path.read_text()
        content = content.replace('"502-345-525"', f'"{correct_phone}"')
        content = content.replace("502-345-525", correct_phone)
        config_path.write_text(content)
        print(f"✅ Fixed phone in utils/config.py")
    
    # Fix in your_profile.db
    import sqlite3
    if Path("unified_platform.db").exists():
        conn = sqlite3.connect("unified_platform.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE profile SET phone = ? WHERE email = ?",
                      (correct_phone, "matthewdscott7@gmail.com"))
        conn.commit()
        conn.close()
        print(f"✅ Fixed phone in your_profile.db")
    
    # Fix in ai_talent_optimizer.db
    if Path("unified_platform.db").exists():
        conn = sqlite3.connect("unified_platform.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE profile SET phone = ? WHERE email = ?",
                      (correct_phone, "matthewdscott7@gmail.com"))
        conn.commit()
        conn.close()
        print(f"✅ Fixed phone in ai_talent_optimizer.db")
    
    # Create updated resume text file for reference
    resume_text = f"""MATTHEW SCOTT
Senior AI/ML Engineer | Production Systems Architect
📧 matthewdscott7@gmail.com | 📱 {correct_phone}
🔗 linkedin.com/in/mscott77 | 💻 github.com/guitargnar
📍 Louisville, KY | Open to Remote

PROFESSIONAL SUMMARY
Senior Risk Management Professional II at Humana with 10+ years experience building enterprise healthcare systems. 
Architected Python ML frameworks delivering significant annual savings through 40% process automation.
Built enterprise-scale platform with 117 Python modules while maintaining demanding day job, demonstrating 
Principal-level engineering capabilities. Seeking $400K+ Principal/Staff roles to leverage my unique combination 
of healthcare domain expertise and cutting-edge AI implementation skills.

KEY ACHIEVEMENTS
• Built distributed ML system with 78 specialized models for complex decision-making
• Developed production AI systems serving 50M+ users across healthcare systems  
• Reduced LLM inference costs by 90% through custom adaptive quantization
• Maintained 100% compliance across 500+ Medicare regulatory pages using AI
• Processing 1,600+ concurrent operations with 99.9% uptime

Note: PDF resume needs manual update to correct phone number from 502-345-525 to {correct_phone}
"""
    
    with open("RESUME_PHONE_FIXED.txt", "w") as f:
        f.write(resume_text)
    
    print(f"\n📱 Phone number updated to: {correct_phone}")
    print("📄 Created RESUME_PHONE_FIXED.txt with correct information")
    print("\n⚠️  IMPORTANT: The PDF resume at 'resumes/matthew_scott_ai_ml_resume.pdf'")
    print("   still shows 502-345-525 and needs to be manually regenerated or edited")
    
    return correct_phone

if __name__ == "__main__":
    fix_phone_number()