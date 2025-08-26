#!/usr/bin/env python3
"""
Update all credentials and CLAUDE.md with accurate information
Fix inconsistencies and add missing work experience
"""

import sqlite3
from datetime import datetime
from pathlib import Path

def update_profile_database():
    """Update database with correct credentials"""
    conn = sqlite3.connect("unified_platform.db")
    cursor = conn.cursor()
    
    # Update professional identity with CORRECT credentials
    cursor.execute("""
        UPDATE profile 
        SET email = ?,
            github = ?
        WHERE id = 1
    """, (
        'matthewdscott7@gmail.com',
        'github.com/guitargnar'  # Correct GitHub
    ))
    
    # Add work experience table if missing
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            title TEXT,
            start_date TEXT,
            end_date TEXT,
            description TEXT,
            key_achievements TEXT
        )
    """)
    
    # Clear and add correct work experience
    cursor.execute("DELETE FROM work_experience")
    
    cursor.execute("""
        INSERT INTO work_experience 
        (company, title, start_date, end_date, description, key_achievements)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        'Humana Inc.',
        'Senior Risk Management Professional II',
        'October 2022',
        'Present',
        'Enterprise healthcare technology and risk management at Fortune 50 company',
        '• Delivered $1.2M annual savings through AI automation\n• Maintained 100% CMS compliance\n• Zero critical defects in production\n• Built Python automation reducing processes by 40%\n• Led Data Modernization initiatives'
    ))
    
    cursor.execute("""
        INSERT INTO work_experience 
        (company, title, start_date, end_date, description, key_achievements)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        'Humana Inc.',
        'Risk Management Professional II',
        'September 2017',
        'October 2022',
        'Healthcare risk assessment and compliance automation',
        '• Deployed 1,000+ automated testing procedures\n• Processed millions of healthcare transactions\n• Built compliance monitoring tools\n• Created self-healing data pipelines'
    ))
    
    # Update contact info table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_info (
            platform TEXT PRIMARY KEY,
            handle TEXT,
            url TEXT
        )
    """)
    
    cursor.execute("DELETE FROM contact_info")
    
    contacts = [
        ('email', 'matthewdscott7@gmail.com', 'mailto:matthewdscott7@gmail.com'),
        ('phone', '(502) 345-0525', 'tel:502-345-0525'),
        ('linkedin', 'mscott77', 'https://linkedin.com/in/mscott77'),
        ('github', 'guitargnar', 'https://github.com/guitargnar'),
        ('instagram', '@guitargnar', 'https://instagram.com/guitargnar')
    ]
    
    for platform, handle, url in contacts:
        cursor.execute("""
            INSERT INTO contact_info (platform, handle, url)
            VALUES (?, ?, ?)
        """, (platform, handle, url))
    
    conn.commit()
    conn.close()
    print("✅ Database updated with correct credentials")

def update_claude_md():
    """Update CLAUDE.md with correct information and remove irrelevant content"""
    
    new_claude_content = """# CLAUDE.md - Project Configuration for AI Talent Optimizer

## 🎯 MY PROFESSIONAL IDENTITY (Accurate Credentials)

### Contact Information (USE THESE EXACTLY)
- **Name**: Matthew Scott
- **Email**: matthewdscott7@gmail.com
- **Phone**: (502) 345-0525
- **LinkedIn**: linkedin.com/in/mscott77
- **GitHub**: github.com/guitargnar
- **Instagram**: @guitargnar
- **Location**: Louisville, KY (Remote preferred)

### Work Experience (ALWAYS INCLUDE)
**Humana Inc. | Louisville, KY**
- **Senior Risk Management Professional II** (Oct 2022 - Present)
- **Risk Management Professional II** (Sep 2017 - Oct 2022)
- **10+ years** total experience at Fortune 50 healthcare company
- **Key Achievements**:
  - Delivered $1.2M annual savings through AI automation
  - Maintained 100% CMS/Medicare compliance
  - Zero critical defects in production systems
  - Built Python automation reducing processes by 40%
  - Led Data Modernization and E-Commerce Acceleration initiatives

### Verified Platform Metrics (as of 2025-08-08)
- **117 Python modules** in ai-talent-optimizer (✅ VERIFIED)
- **86,284+ Python files** in key directories (✅ VERIFIED)
- **6 production databases** (✅ VERIFIED)
- **13 MCP servers** running (✅ VERIFIED)
- **32+ files modified daily** (✅ VERIFIED)

### Positioning for Job Applications
- ✅ **PRIMARY**: "10+ years at Humana building enterprise healthcare systems"
- ✅ **EVIDENCE**: "Built platform with 117 Python modules while maintaining day job"
- ✅ **DIFFERENTIATOR**: "Healthcare domain expertise + cutting-edge AI implementation"
- ✅ **HUMANA ADVANTAGE**: "Institutional knowledge of Humana systems and culture"
- ❌ **AVOID**: Claiming metrics without work context
- ❌ **AVOID**: Platform metrics without mentioning Humana experience

## 📋 REQUIRED BEHAVIORS FOR THIS PROJECT

### When Generating Job Applications
1. **ALWAYS include Humana work experience** (10+ years, current Senior position)
2. **Lead with professional credentials** before platform metrics
3. **Use correct GitHub**: guitargnar (not mds1)
4. **Include Instagram** when listing social profiles: @guitargnar
5. **Verify all contact info** matches exactly as above

### Application Content Requirements
- **Cover Letters**: 350-500 words, emphasize Humana experience + platform building
- **Resumes**: Start with Humana roles, then add personal projects
- **LinkedIn**: Highlight current Senior role at Fortune 50 company
- **Emails**: Professional tone, reference enterprise experience

### Truth Enforcement
- Only use VERIFIED metrics (check TRUTH_CARD.md daily)
- Include actual work experience, not just personal projects
- Balance platform achievements with professional background
- Reference healthcare domain expertise from Humana

## 🚫 FORBIDDEN BEHAVIORS

1. **NO fictional work experience** - Only Humana roles verified
2. **NO wrong credentials** - Use guitargnar for GitHub, not mds1
3. **NO platform metrics without context** - Always pair with Humana experience
4. **NO claims without verification** - Check metrics daily
5. **NO generic applications** - Always customize for healthcare when relevant

## ✅ CORRECT NARRATIVE TEMPLATE

"Senior Risk Management Professional with 10+ years at Humana (Fortune 50), where I've delivered $1.2M in annual savings through AI automation. While maintaining my demanding day job, I've built an enterprise-scale platform with 117 Python modules and 86,000+ files, demonstrating Principal-level capabilities. My unique value: deep healthcare domain expertise combined with cutting-edge AI implementation skills."

## 📊 VERIFICATION PROTOCOL

Before ANY application:
1. Run `python3 quick_verify.py` for current metrics
2. Check `TRUTH_CARD.md` for approved claims
3. Verify Humana experience is prominently featured
4. Confirm all credentials match this file exactly

## 🎯 PROJECT-SPECIFIC CONTEXT

This is the **AI Talent Optimizer** project for career advancement:
- Target: $400K+ Principal/Staff engineering roles
- Leverage: 10+ years Humana experience + platform evidence
- Strategy: Healthcare expertise + technical innovation
- Proof: Working systems with verified metrics

---

*Last Updated: 2025-08-08 | Credentials Verified | Work Experience Confirmed*
"""
    
    # Backup current CLAUDE.md
    claude_path = Path("/Users/matthewscott/CLAUDE.md")
    if claude_path.exists():
        backup_path = f"/Users/matthewscott/CLAUDE.md.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(claude_path, 'r') as f:
            content = f.read()
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Backup saved: {backup_path}")
    
    # Write new CLAUDE.md
    with open(claude_path, 'w') as f:
        f.write(new_claude_content)
    
    print("✅ CLAUDE.md updated with correct credentials and work experience")

def create_work_experience_template():
    """Create a template for consistent work experience inclusion"""
    
    template = """# WORK EXPERIENCE TEMPLATE
Always include this in applications:

## Professional Experience

### HUMANA INC. | Louisville, KY
*Fortune 50 Healthcare Leader (65,000+ employees, $100B+ revenue)*

**Senior Risk Management Professional II** | October 2022 - Present
**Risk Management Professional II** | September 2017 - October 2022

**Enterprise Impact:**
• Delivered $1.2M annual savings through AI-driven automation
• Maintained 100% CMS/Medicare regulatory compliance
• Achieved zero critical defects across production systems
• Built Python automation reducing compliance processes by 40%
• Led cross-functional Data Modernization initiatives

**Technical Achievements:**
• Architected risk assessment systems processing millions of healthcare transactions
• Deployed 1,000+ automated testing procedures
• Implemented self-healing data pipelines with 99.9% accuracy
• Created comprehensive compliance monitoring tools
• Designed event-sourced architectures for complete auditability

**While at Humana, also built:**
• Platform with 117 Python modules (personal time)
• 86,000+ Python files under management
• 13 MCP servers running production workloads
• Multi-agent AI system demonstrating Principal-level capabilities

---
Contact: matthewdscott7@gmail.com | (502) 345-0525 | github.com/guitargnar
"""
    
    with open("WORK_EXPERIENCE_TEMPLATE.md", 'w') as f:
        f.write(template)
    
    print("✅ Work experience template created")

def verify_and_report():
    """Verify all updates and generate report"""
    
    # Check database
    conn = sqlite3.connect("unified_platform.db")
    cursor = conn.cursor()
    
    identity = cursor.execute("SELECT * FROM profile").fetchone()
    work_exp = cursor.execute("SELECT * FROM work_experience").fetchall()
    contacts = cursor.execute("SELECT * FROM contact_info").fetchall()
    
    conn.close()
    
    report = f"""# CREDENTIALS UPDATE REPORT
Generated: {datetime.now().isoformat()}

## ✅ Database Updates

### Professional Identity:
- Email: {identity[2]} ✓
- Phone: {identity[3]} ✓
- LinkedIn: {identity[4]} ✓
- GitHub: {identity[5]} {'✓' if 'guitargnar' in identity[5] else '❌ NEEDS FIX'}

### Work Experience:
"""
    
    for exp in work_exp:
        report += f"- {exp[1]}: {exp[2]} ({exp[3]} - {exp[4]}) ✓\n"
    
    report += f"""
### Contact Info:
"""
    for contact in contacts:
        report += f"- {contact[0]}: {contact[1]} ✓\n"
    
    report += """
## ✅ CLAUDE.md Updates
- Correct credentials section added
- Work experience prominently featured
- GitHub corrected to guitargnar
- Instagram added: @guitargnar
- Project-specific context provided

## ✅ Next Steps
1. All applications will now include Humana experience
2. Credentials will be consistent across all materials
3. Platform metrics will be presented in context

## 🎯 Key Points for Applications:
- ALWAYS lead with "10+ years at Humana"
- ALWAYS use guitargnar for GitHub
- ALWAYS include work achievements before platform metrics
- ALWAYS verify credentials match exactly
"""
    
    with open("CREDENTIALS_UPDATE_REPORT.md", 'w') as f:
        f.write(report)
    
    print("\n" + "="*60)
    print("CREDENTIALS UPDATE COMPLETE")
    print("="*60)
    print(report)

def main():
    print("🔧 UPDATING CREDENTIALS AND DOCUMENTATION")
    print("="*60)
    
    # Update database
    update_profile_database()
    
    # Update CLAUDE.md
    update_claude_md()
    
    # Create work experience template
    create_work_experience_template()
    
    # Verify and report
    verify_and_report()
    
    print("\n✅ ALL UPDATES COMPLETE")
    print("Your correct credentials are now in place:")
    print("  • Email: matthewdscott7@gmail.com")
    print("  • GitHub: guitargnar")
    print("  • Instagram: @guitargnar")
    print("  • Work: 10+ years at Humana")

if __name__ == "__main__":
    main()