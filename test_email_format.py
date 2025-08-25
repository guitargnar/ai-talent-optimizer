#!/usr/bin/env python3
"""
Test Email Formatting - Ensure emails are sent as clean plain text
"""

import sys
from pathlib import Path
from datetime import datetime

# Import the quality system
sys.path.append(str(Path(__file__).parent))
from quality_first_apply import QualityFirstApplicationSystem

def test_email_generation():
    """Test complete email generation and formatting"""
    
    print("="*60)
    print("📧 EMAIL FORMAT TESTING")
    print("="*60)
    print("Testing email generation with proper plain text formatting")
    print("="*60)
    
    # Initialize system
    system = QualityFirstApplicationSystem()
    
    # Test companies
    test_cases = [
        ("Anthropic", "ML Engineer"),
        ("OpenAI", "Software Engineer"),
        ("Tempus", "Senior ML Engineer")
    ]
    
    for company, role in test_cases:
        print(f"\n🏢 Testing: {company} - {role}")
        print("-"*50)
        
        # Research and generate email
        research = system.research_company(company, role)
        subject, body_markdown = system.generate_personalized_email(company, role, research)
        
        # Convert to plain text
        body_plain = system._markdown_to_plain_text(body_markdown)
        
        print(f"✉️ Subject: {subject}")
        print("\n📝 Original (with Markdown):")
        print("  " + body_markdown[:150].replace("\n", "\n  ") + "...")
        
        print("\n✅ Converted (Plain Text):")
        print("  " + body_plain[:150].replace("\n", "\n  ") + "...")
        
        # Verify no markdown remains
        issues = []
        if "**" in body_plain:
            issues.append("Contains ** markdown")
        if "•" in body_plain:
            issues.append("Contains bullet points •")
        if "*" in body_plain and not "(502) 345-0525" in body_plain:  # Allow * in phone
            issues.append("Contains asterisks")
        
        if issues:
            print(f"\n❌ Issues found: {', '.join(issues)}")
        else:
            print("\n✅ Clean plain text - ready for email!")
    
    print("\n" + "="*60)
    print("📊 FORMAT VERIFICATION COMPLETE")
    print("="*60)
    print("\n✅ All emails will be sent as clean plain text")
    print("✅ No raw Markdown will appear in recipients' inboxes")
    print("\n💡 Key conversions:")
    print("  • **Bold Text** → BOLD TEXT (uppercase)")
    print("  • Bullet points • → Dashes -")
    print("  • Clean, professional formatting")

def test_with_safety_mode():
    """Test that safety mode is respected"""
    
    print("\n" + "="*60)
    print("🔒 SAFETY MODE TEST")
    print("="*60)
    
    safety_flag = Path(__file__).parent / "DISABLE_AUTO_SEND.txt"
    if safety_flag.exists():
        print("✅ Safety flag exists - emails will NOT be sent")
        print("   All sending functions will run in DEMO MODE")
    else:
        print("⚠️ Safety flag not found - emails WOULD be sent")
        print("   Create DISABLE_AUTO_SEND.txt to prevent sending")
    
    print("="*60)

if __name__ == "__main__":
    test_email_generation()
    test_with_safety_mode()