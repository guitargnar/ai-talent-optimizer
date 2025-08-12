#!/usr/bin/env python3
"""
Manual Quick Apply - Direct application links and instructions for immediate action
Since web scraping requires login credentials, this provides direct links to apply NOW
"""

import webbrowser
from datetime import datetime
import pandas as pd
from pathlib import Path

class ManualQuickApply:
    """Provides direct links and instructions for immediate manual applications"""
    
    # Direct application links for top companies
    DIRECT_APPLY_LINKS = {
        'Abridge': {
            'careers_page': 'https://jobs.ashbyhq.com/abridge',
            'principal_search': 'https://jobs.ashbyhq.com/abridge?search=principal+engineer',
            'staff_search': 'https://jobs.ashbyhq.com/abridge?search=staff+engineer',
            'senior_search': 'https://jobs.ashbyhq.com/abridge?search=senior+engineer',
            'notes': '$550M funding - APPLY TO ALL ENGINEERING ROLES'
        },
        'Tempus AI': {
            'careers_page': 'https://www.tempus.com/careers/',
            'open_positions': 'https://www.tempus.com/careers/open-positions/',
            'engineering': 'https://www.tempus.com/careers/?department=Engineering',
            'notes': '59 open positions - Public company, stable'
        },
        'Oscar Health': {
            'careers_page': 'https://www.hioscar.com/careers',
            'engineering': 'https://www.hioscar.com/careers/search?department=Engineering',
            'notes': 'GenAI implementation - Healthcare focus'
        },
        'UnitedHealth Group': {
            'careers_page': 'https://careers.unitedhealthgroup.com/',
            'tech_jobs': 'https://careers.unitedhealthgroup.com/job-search?category=Technology',
            'notes': 'Fortune 10 - Massive AI transformation'
        },
        'CVS Health': {
            'careers_page': 'https://jobs.cvshealth.com/',
            'tech_jobs': 'https://jobs.cvshealth.com/search-jobs?orgIds=1292&kt=1',
            'notes': 'Healthcare tech transformation'
        },
        'Medium': {
            'careers_page': 'https://jobs.medium.com/',
            'vp_engineering': 'https://jobs.medium.com/jobs',
            'notes': 'VP Engineering role - Reports to CEO'
        }
    }
    
    # CEO LinkedIn profiles for direct messaging
    CEO_LINKEDIN_PROFILES = {
        'Shiv Rao (Abridge CEO)': 'https://www.linkedin.com/in/shivrao/',
        'Eric Lefkofsky (Tempus CEO)': 'https://www.linkedin.com/in/ericlefkofsky/',
        'Mario Schlosser (Oscar Health CEO)': 'https://www.linkedin.com/in/marioschlosser/',
        'Tony Stubblebine (Medium CEO)': 'https://www.linkedin.com/in/tonystubblebine/',
        'Ankit Jain (Infinitus CEO)': 'https://www.linkedin.com/in/ankitjain/',
        'Guy Benjamin (Healthee CEO)': 'https://www.linkedin.com/in/guybenjamin/',
        'Pranay Kapadia (Notable Health CEO)': 'https://www.linkedin.com/in/pranaykapadia/',
        'Eli Ben-Joseph (Regard CEO)': 'https://www.linkedin.com/in/elibenjoseph/',
    }
    
    # Recruiter contact pages
    RECRUITER_CONTACTS = {
        'Kaye/Bassman Healthcare IT': 'https://kbic.com/recruiting/healthcare-information-technology/',
        'Direct Recruiters': 'https://www.directrecruiters.com/contact-us/',
        'Korn Ferry': 'https://www.kornferry.com/contact',
        'Russell Reynolds': 'https://www.russellreynolds.com/contact-us',
        'Elite Technical': 'https://www.elitetechnical.com/contact/'
    }
    
    def __init__(self):
        self.tracker_csv = Path("MASTER_TRACKER_400K.csv")
        self.applied_log = Path("manual_applications_log.txt")
    
    def open_all_priority_applications(self):
        """Open all priority application pages in browser"""
        print("\n🚀 OPENING PRIORITY APPLICATION PAGES")
        print("="*60)
        
        # Open Abridge first (highest priority)
        print("\n1️⃣ ABRIDGE - $550M funding - APPLY TO ALL")
        for key, url in self.DIRECT_APPLY_LINKS['Abridge'].items():
            if key != 'notes':
                print(f"   Opening: {key}")
                webbrowser.open(url)
        
        # Open Tempus AI
        print("\n2️⃣ TEMPUS AI - 59 positions")
        for key, url in self.DIRECT_APPLY_LINKS['Tempus AI'].items():
            if key != 'notes':
                print(f"   Opening: {key}")
                webbrowser.open(url)
        
        # Open other high priority
        for company in ['Oscar Health', 'UnitedHealth Group', 'Medium']:
            print(f"\n3️⃣ {company.upper()}")
            webbrowser.open(self.DIRECT_APPLY_LINKS[company]['careers_page'])
    
    def generate_application_checklist(self):
        """Generate a checklist for manual applications"""
        checklist = f"""
╔══════════════════════════════════════════════════════════╗
║      IMMEDIATE APPLICATION CHECKLIST                      ║
║      Complete these NOW - Target: $400K+                  ║
╚══════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 TIER 1 - DO THESE FIRST (Next 30 Minutes)
============================================

□ ABRIDGE (All Engineering Roles)
  ➤ Go to: https://jobs.ashbyhq.com/abridge
  ➤ Apply to: Principal Engineer, Staff Engineer, Senior Engineer
  ➤ In cover letter: Mention $1.2M Humana savings + healthcare expertise
  ➤ CEO: Message Shiv Rao on LinkedIn

□ TEMPUS AI (All Principal/Staff)
  ➤ Go to: https://www.tempus.com/careers/
  ➤ Filter: Engineering Department
  ➤ Apply to: ALL Principal/Staff/Senior roles
  ➤ Emphasize: Healthcare AI experience + compliance

□ OSCAR HEALTH (GenAI Roles)
  ➤ Go to: https://www.hioscar.com/careers
  ➤ Search: "Principal" OR "Staff" OR "AI"
  ➤ Apply to: All matching positions
  ➤ Highlight: InsurTech + AI combination

🎯 TIER 2 - DO THESE SECOND (Next Hour)
========================================

□ MEDIUM (VP Engineering)
  ➤ Go to: https://jobs.medium.com/
  ➤ Apply to: VP Engineering role
  ➤ This reports to CEO - emphasize leadership

□ UNITEDHEALTH GROUP
  ➤ Go to: https://careers.unitedhealthgroup.com/
  ➤ Search: "Principal Engineer" in Technology
  ➤ Apply to: Top 5 matches

□ CVS HEALTH
  ➤ Go to: https://jobs.cvshealth.com/
  ➤ Filter: Technology roles
  ➤ Apply to: Principal/Staff positions

📧 CEO LINKEDIN MESSAGES (Send These NOW)
==========================================

□ Shiv Rao (Abridge): https://www.linkedin.com/in/shivrao/
  Message: "Congrats on $550M! 10yr Humana experience..."

□ Eric Lefkofsky (Tempus): https://www.linkedin.com/in/ericlefkofsky/
  Message: "Your precision medicine vision aligns with my Humana work..."

□ Mario Schlosser (Oscar): https://www.linkedin.com/in/marioschlosser/
  Message: "Your InsurTech innovation + my $1.2M automation..."

□ Tony Stubblebine (Medium): https://www.linkedin.com/in/tonystubblebine/
  Message: "VP Eng role - I bring 10yr enterprise + startup experience..."

📞 RECRUITER CONTACTS (Call/Email Today)
=========================================

□ Kaye/Bassman: https://kbic.com/recruiting/healthcare-information-technology/
  ➤ Call their Healthcare IT team
  ➤ Mention: Principal roles, $400K+ target

□ Direct Recruiters: https://www.directrecruiters.com/contact-us/
  ➤ Submit executive profile
  ➤ Highlight: Healthcare + AI expertise

□ Korn Ferry: https://www.kornferry.com/contact
  ➤ Contact Healthcare practice
  ➤ Position: Principal/Staff level

🔄 LINKEDIN UPDATES (Do Immediately)
====================================

□ Update Headline: "Fractional CTO | 10yr Humana | $1.2M Saved | Available"
□ Update About: Add your Principal Engineer positioning
□ Post: "After 10 years at Humana and $1.2M in savings, exploring Principal roles"
□ Connect: With 10 recruiters in healthcare IT

📊 TRACKING (After Each Application)
====================================
After each application, note:
- Company: _____________
- Position: _____________
- Applied: ✓
- Cover Letter Customized: ✓
- Resume Version: Principal / Staff / General
- Follow-up Date: _____________

💡 KEY MESSAGES TO EMPHASIZE
============================
✓ $1.2M annual savings at Humana (3x ROI)
✓ 10 years Fortune 50 experience
✓ 100% CMS compliance record
✓ 15+ production systems
✓ Zero critical defects
✓ 58-model AI system built
✓ Available immediately

⏰ TIME TARGETS
===============
By End of Hour 1: 5+ applications submitted
By End of Hour 2: 10+ applications submitted
By End of Day: 20+ applications, 10+ CEO messages, 5+ recruiter contacts

REMEMBER: You're worth $400K+. Apply with confidence!
"""
        return checklist
    
    def log_application(self, company: str, position: str):
        """Log a completed application"""
        with open(self.applied_log, 'a') as f:
            f.write(f"{datetime.now()}: Applied to {company} - {position}\n")
        
        # Update CSV tracker
        if self.tracker_csv.exists():
            df = pd.read_csv(self.tracker_csv)
            # Update relevant row if exists
            mask = df['Item'] == company
            if len(df[mask]) > 0:
                df.loc[mask, 'Status'] = 'APPLIED'
                df.loc[mask, 'Date'] = datetime.now().strftime('%Y-%m-%d')
                df.to_csv(self.tracker_csv, index=False)
        
        print(f"✅ Logged: {company} - {position}")
    
    def generate_cover_letter_template(self, company: str, position: str) -> str:
        """Generate a cover letter template for quick copying"""
        template = f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {position} position at {company}.

With 10+ years at Humana where I delivered $1.2M in annual savings through AI automation while maintaining 100% CMS compliance, I bring the exact combination of enterprise healthcare expertise and technical innovation that {company} needs at this critical growth stage.

Key qualifications for this role:

• **Proven ROI**: Delivered $1.2M in quantified savings at Fortune 50 scale - I provide 3x return on any salary investment
• **Zero Defects**: Maintained perfect production record across 15+ critical healthcare systems
• **AI Innovation**: Built an unprecedented 58-model AI orchestration system demonstrating architectural expertise
• **Healthcare Expertise**: Deep understanding of CMS compliance, HIPAA, and healthcare workflows
• **Scale**: Architected systems serving 50M+ users with 99.9% uptime

I've been operating at Principal level for years at Humana - architecting distributed systems, leading cross-functional initiatives, and establishing technical standards that scaled across the organization. My 432,000+ lines of production code demonstrate not just coding ability, but the system design expertise expected of Principal Engineers.

I'm particularly excited about {company}'s {"recent $550M funding and rapid scaling" if company == "Abridge" else "growth in healthcare AI"}. Your mission aligns perfectly with my passion for using technology to improve healthcare delivery.

Available for immediate start with flexibility on location. My compensation expectations align with Principal Engineer market rates ($450K+), which represents strong ROI given my proven ability to deliver multiples of that in value.

I look forward to discussing how my unique combination of healthcare domain expertise and technical innovation can accelerate {company}'s success.

Best regards,
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77
"""
        return template
    
    def launch_application_blitz(self):
        """Launch the full application blitz"""
        print(self.generate_application_checklist())
        
        print("\n" + "="*60)
        print("OPENING PRIORITY APPLICATION PAGES IN YOUR BROWSER...")
        print("="*60)
        
        input("\nPress ENTER to open all priority job pages in your browser...")
        
        self.open_all_priority_applications()
        
        print("\n✅ All priority pages opened!")
        print("\n📋 COVER LETTER TEMPLATE (Copy this for applications):")
        print("="*60)
        print(self.generate_cover_letter_template("Abridge", "Principal Engineer")[:500] + "...")
        
        print("\n" + "="*60)
        print("🚀 GO APPLY NOW! Log each application with this script.")
        print("="*60)
        
        # Save checklist to file
        checklist_file = Path("APPLICATION_CHECKLIST.txt")
        with open(checklist_file, 'w') as f:
            f.write(self.generate_application_checklist())
        print(f"\n📄 Checklist saved to: {checklist_file}")
        
        # Save cover letter template
        template_file = Path("COVER_LETTER_TEMPLATE.txt")
        with open(template_file, 'w') as f:
            f.write(self.generate_cover_letter_template("[Company]", "[Position]"))
        print(f"📄 Cover letter template saved to: {template_file}")


def main():
    """Execute the manual application blitz"""
    blitz = ManualQuickApply()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║      MANUAL QUICK APPLY - $400K+ POSITIONS                ║
║      Direct Links to Apply RIGHT NOW                      ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    blitz.launch_application_blitz()
    
    print("\n🎯 After applying, log your applications:")
    print("   Example: blitz.log_application('Abridge', 'Principal Engineer')")
    
    return blitz


if __name__ == "__main__":
    blitz = main()