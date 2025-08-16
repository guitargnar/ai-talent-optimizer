#!/usr/bin/env python3
"""
PROJECT ASCENT - Master Control Center
The Process is the Product: Automating the $400K+ job search
"""

import sys
import os
from datetime import datetime
import subprocess

def display_banner():
    """Display Project Ascent banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗             ║
║     ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝             ║
║     ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║                ║
║     ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║                ║
║     ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║                ║
║     ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝                ║
║                                                                              ║
║                    █████╗ ███████╗ ██████╗███████╗███╗   ██╗████████╗      ║
║                   ██╔══██╗██╔════╝██╔════╝██╔════╝████╗  ██║╚══██╔══╝      ║
║                   ███████║███████╗██║     █████╗  ██╔██╗ ██║   ██║         ║
║                   ██╔══██║╚════██║██║     ██╔══╝  ██║╚██╗██║   ██║         ║
║                   ██║  ██║███████║╚██████╗███████╗██║ ╚████║   ██║         ║
║                   ╚═╝  ╚═╝╚══════╝ ╚═════╝╚══════╝╚═╝  ╚═══╝   ╚═╝         ║
║                                                                              ║
║            🚀 THE PROCESS IS THE PRODUCT - $400K+ OR BUST! 🚀              ║
║                                                                              ║
║                    Orchestrating 78 Models to Land 1 Job                    ║
║                         Because Manual is for Mortals                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def display_menu():
    """Display main menu"""
    menu = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROJECT ASCENT CONTROL CENTER                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [1] 🎯 Run Daily Campaign Sequence (Generate & Send Messages)             │
│  [2] 📬 Check & Record Responses                                          │
│  [3] 📊 View Live Dashboard                                               │
│  [4] 📈 Generate Analytics Report                                         │
│  [5] 🔄 Identify Follow-Up Targets                                        │
│  [6] 💼 Generate New Application Materials                                │
│  [7] 🧪 Test Message Generator                                            │
│  [8] 📝 Update Campaign Configuration                                     │
│  [9] 🎨 Generate Custom Message                                           │
│  [0] 🚪 Exit                                                              │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Campaign Stats:                                                           │
│  • Demonstrating AI capabilities through automation                        │
│  • Every message sent = proof of technical competence                      │
│  • The automation itself IS the portfolio                                  │
└─────────────────────────────────────────────────────────────────────────────┘
    """
    print(menu)

# DECOMMISSIONED: Strategic Pivot to Human-Centric Approach [2025-08-12]
def run_daily_campaign():
    """[DECOMMISSIONED] Execute daily campaign sequence - NOW DISABLED
    
    This automated campaign has been disabled after analysis showed:
    - 0% response rate over 223 days
    - Only 5 total outreach attempts
    - Automated approach perceived as high-risk by hiring managers
    - Contradicts trust-building required for $400K+ roles
    
    New approach: Manual, high-touch engagement using intelligence dossiers
    """
    print("\n⚠️ AUTOMATED CAMPAIGN DECOMMISSIONED")
    print("=" * 70)
    print("The automated outreach has been strategically disabled.")
    print("\nWhy this change?")
    print("• 0% response rate proved automation damages brand")
    print("• Senior roles require human judgment and relationship building")
    print("• Humana facing AI trust crisis - automation is their nightmare")
    print("\nNew approach:")
    print("• Use intelligence dossiers in targets/ directory")
    print("• Send 2-3 highly personalized messages per week")
    print("• Focus on Directors/Senior Managers, not CEOs")
    print("• Lead with $1.2M savings and 99.9% uptime metrics")
    print("\nNext step: View target dossiers and craft personalized outreach")
    print("=" * 70)

def check_responses():
    """Check and record responses"""
    print("\n📬 Opening Response Tracker...")
    subprocess.run([sys.executable, "track_responses.py"])

def view_dashboard():
    """Update and view dashboard"""
    print("\n📊 Updating Live Dashboard...")
    subprocess.run([sys.executable, "update_dashboard.py"])
    
    # Also try to open in default editor
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", "campaign_dashboard.md"])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["start", "campaign_dashboard.md"], shell=True)
        else:  # Linux
            subprocess.run(["xdg-open", "campaign_dashboard.md"])
    except:
        print("📄 Dashboard saved to campaign_dashboard.md - open manually to view")

def generate_analytics():
    """Generate analytics report"""
    print("\n📈 Generating Analytics Report...")
    from track_responses import ResponseTracker
    tracker = ResponseTracker()
    report = tracker.generate_response_report()
    print(report)
    
    # Save report
    report_path = f"analytics_reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    os.makedirs("analytics_reports", exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\n📄 Report saved to: {report_path}")

def identify_followups():
    """Identify follow-up targets"""
    print("\n🔄 Identifying Follow-Up Targets...")
    from track_responses import ResponseTracker
    tracker = ResponseTracker()
    candidates = tracker.get_follow_up_candidates()
    
    print(f"\n📋 {len(candidates)} targets need follow-up:")
    for i, c in enumerate(candidates[:20], 1):
        print(f"{i:2}. {c['name']:<25} at {c['company']:<20} ({c['days_since']} days ago)")
    
    if len(candidates) > 20:
        print(f"    ... and {len(candidates) - 20} more")

def generate_application():
    """Generate new application materials"""
    print("\n💼 Application Material Generator")
    print("=" * 60)
    
    company = input("Company Name: ").strip()
    position = input("Position Title: ").strip()
    tier = input("Tier (1=Humana, 2=Healthcare, 3=Tech/Research): ").strip()
    
    from intelligent_message_generator import IntelligentMessageGenerator
    generator = IntelligentMessageGenerator()
    
    tier_map = {"1": "tier_1", "2": "tier_2", "3": "tier_3"}
    tier_key = tier_map.get(tier, "tier_2")
    
    # Generate outreach message
    subject, message = generator.generate_message(
        "Hiring Manager",
        company,
        tier_key,
        position
    )
    
    print("\n" + "=" * 60)
    print("GENERATED OUTREACH MESSAGE")
    print("=" * 60)
    print(f"Subject: {subject}\n")
    print(message)
    
    # Select appropriate resume
    from campaign_assets.campaign_config import RESUME_MAPPING
    resume_type = RESUME_MAPPING.get(tier_key, "MASTER_RESUME")
    
    print("\n" + "=" * 60)
    print(f"RECOMMENDED RESUME: {resume_type}")
    print("Use the appropriate resume from your variants folder")
    print("=" * 60)

def test_generator():
    """Test message generator"""
    print("\n🧪 Testing Message Generator...")
    subprocess.run([sys.executable, "intelligent_message_generator.py"])

def update_configuration():
    """Update campaign configuration"""
    print("\n📝 Opening Campaign Configuration...")
    config_path = "campaign_assets/campaign_config.py"
    
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", config_path])
        elif sys.platform == "win32":
            subprocess.run(["start", config_path], shell=True)
        else:
            subprocess.run(["xdg-open", config_path])
    except:
        print(f"📄 Open {config_path} in your editor to update configuration")

def generate_custom_message():
    """Generate a custom message interactively"""
    print("\n🎨 Custom Message Generator")
    print("=" * 60)
    
    name = input("Contact Name: ").strip()
    company = input("Company: ").strip()
    tier = input("Tier (1=Humana, 2=Healthcare, 3=Tech/Research): ").strip()
    
    # Optional context
    print("\nOptional Context (press Enter to skip):")
    project = input("Specific Project/Initiative: ").strip()
    tech = input("Specific Technology: ").strip()
    challenge = input("Specific Challenge: ").strip()
    
    context = {}
    if project:
        context["specific_project"] = project
    if tech:
        context["specific_technology"] = tech
    if challenge:
        context["specific_challenge"] = challenge
    
    from intelligent_message_generator import IntelligentMessageGenerator
    generator = IntelligentMessageGenerator()
    
    tier_map = {"1": "tier_1", "2": "tier_2", "3": "tier_3"}
    tier_key = tier_map.get(tier, "tier_2")
    
    subject, message = generator.generate_message(
        name,
        company,
        tier_key,
        specific_context=context
    )
    
    print("\n" + "=" * 60)
    print("GENERATED MESSAGE")
    print("=" * 60)
    print(f"Subject: {subject}\n")
    print(message)
    
    # Save option
    save = input("\nSave this message? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"generated_messages/{company}_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        os.makedirs("generated_messages", exist_ok=True)
        with open(filename, 'w') as f:
            f.write(f"Subject: {subject}\n\n{message}")
        print(f"✅ Message saved to: {filename}")

def display_philosophy():
    """Display the Project Ascent philosophy"""
    philosophy = """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                     THE PROCESS IS THE PRODUCT                       ║
    ╠═══════════════════════════════════════════════════════════════════════╣
    ║                                                                       ║
    ║  This isn't just a job search tool - it's a DEMONSTRATION of your   ║
    ║  capabilities. Every automated message sent proves you can:          ║
    ║                                                                       ║
    ║  • Architect complex automation systems                              ║
    ║  • Implement intelligent personalization at scale                    ║
    ║  • Track and optimize based on data                                  ║
    ║  • Build production-grade Python applications                        ║
    ║  • Orchestrate multiple components into a unified platform           ║
    ║                                                                       ║
    ║  When they ask "Show me what you've built" - you point to THIS.     ║
    ║  The very system that brought them your application.                 ║
    ║                                                                       ║
    ║  78 models got you here. This automation will get you there.        ║
    ║                                                                       ║
    ║  Every line of code = Evidence of expertise                          ║
    ║  Every message sent = Proof of execution                             ║
    ║  Every response tracked = Data-driven mindset                        ║
    ║                                                                       ║
    ║                         $400K+ awaits. LET'S GO!                     ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
    print(philosophy)

def main():
    """Main entry point for Project Ascent"""
    
    display_banner()
    display_philosophy()
    
    while True:
        display_menu()
        
        choice = input("\n🎯 Select Action: ").strip()
        
        if choice == '1':
            run_daily_campaign()
        elif choice == '2':
            check_responses()
        elif choice == '3':
            view_dashboard()
        elif choice == '4':
            generate_analytics()
        elif choice == '5':
            identify_followups()
        elif choice == '6':
            generate_application()
        elif choice == '7':
            test_generator()
        elif choice == '8':
            update_configuration()
        elif choice == '9':
            generate_custom_message()
        elif choice == '0':
            print("\n" + "=" * 80)
            print("🚀 PROJECT ASCENT - Signing Off")
            print("Remember: You're not looking for a job.")
            print("You're selecting which company gets your $1.2M impact.")
            print("The automation continues... The ascent is inevitable.")
            print("=" * 80)
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\n✅ Press Enter to continue...")

if __name__ == "__main__":
    main()