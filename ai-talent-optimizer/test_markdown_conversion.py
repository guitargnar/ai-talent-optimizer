#!/usr/bin/env python3
"""
Test the Markdown to Plain Text conversion for emails
"""

import re
from quality_first_apply import QualityFirstApplicationSystem

def test_markdown_conversion():
    """Test the markdown to plain text conversion"""
    
    # Sample email with Markdown formatting
    markdown_email = """Hi Anthropic Team,

As a daily Claude user who's built extensive systems with your technology, I believe my unique combination of enterprise experience and cutting-edge AI implementation makes me an exceptional fit for this role.

**Why I'm Different:**

I haven't been waiting for permission to work at the Principal/Staff level. While maintaining my day job, I've built:
• An AI platform with 274 Python modules processing real-world data
• Orchestration for 74 specialized Ollama models
• Production systems with 15+ databases and 1,000+ deployments
• Complete automation pipelines exceeding many startup MVPs

**Specific Value for Anthropic:**
• Using Claude daily for 6+ months
• Built 274-file AI system using Claude Code
• Deep understanding of LLM capabilities and limitations

**Technical Alignment:**

Your focus on AI safety and research aligns perfectly with my experience:
• 10+ years Python in production environments
• Deep LLM/GenAI expertise (60+ models deployed)
• Platform architecture at enterprise scale
• Already using Claude extensively, deep alignment with mission

**Immediate Impact:**

Unlike candidates who need ramp-up time, I can contribute from day one:
• Architecture decisions backed by real implementation experience
• Production-ready code with proven patterns
• Cross-functional leadership from technical depth

I'd love to contribute to the team behind the AI assistant I rely on every day.

Best regards,
Matthew Scott"""
    
    # Initialize the system
    system = QualityFirstApplicationSystem()
    
    # Convert to plain text
    plain_text = system._markdown_to_plain_text(markdown_email)
    
    print("="*60)
    print("MARKDOWN TO PLAIN TEXT CONVERSION TEST")
    print("="*60)
    
    print("\n📝 ORIGINAL MARKDOWN:")
    print("-"*40)
    print(markdown_email[:300] + "...")
    
    print("\n✉️ CONVERTED PLAIN TEXT:")
    print("-"*40)
    print(plain_text[:500] + "...")
    
    print("\n🔍 VERIFICATION CHECKS:")
    print("-"*40)
    
    # Check that markdown symbols are removed
    checks = [
        ("No double asterisks **", "**" not in plain_text),
        ("No single asterisks *", plain_text.count("*") == 0),
        ("Bullets converted to dashes", "• " not in plain_text and "- " in plain_text),
        ("Bold text converted to UPPERCASE", "WHY I'M DIFFERENT:" in plain_text),
        ("Section headers in UPPERCASE", "TECHNICAL ALIGNMENT:" in plain_text),
        ("Clean spacing", "\n\n\n" not in plain_text)
    ]
    
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
    
    print("\n📊 FULL CONVERTED EMAIL:")
    print("="*60)
    print(plain_text)
    print("="*60)
    
    return plain_text

if __name__ == "__main__":
    test_markdown_conversion()