#!/usr/bin/env python3
"""
Quick Message Generator - Instant personalized messages for immediate use
Run this to get messages for any company RIGHT NOW
"""

from intelligent_messaging_system import IntelligentMessagingSystem, OutreachChannel, MessageStyle
from message_campaign_orchestrator import MessageCampaignOrchestrator
from pathlib import Path
import json

def generate_quick_messages():
    """Generate messages for immediate use"""
    
    system = IntelligentMessagingSystem()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║     QUICK MESSAGE GENERATOR - Copy & Send NOW             ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Priority companies based on your research
    priority_targets = [
        {
            'company': 'Abridge',
            'ceo': 'Shiv Rao',
            'recent_news': '$550M Series C funding',
            'mission': 'Eliminate administrative burden in healthcare',
            'pain_points': ['Scaling engineering team', 'Healthcare compliance'],
            'your_angle': 'Healthcare automation expertise from Humana'
        },
        {
            'company': 'Tempus',
            'ceo': 'Eric Lefkofsky',
            'recent_news': 'IPO at $8B valuation, 59 open positions',
            'mission': 'Make precision medicine a reality through AI',
            'pain_points': ['Rapid scaling', 'AI/ML implementation'],
            'your_angle': '58-model AI system experience'
        },
        {
            'company': 'Oscar Health',
            'ceo': 'Mario Schlosser',
            'recent_news': 'GenAI implementation for member experience',
            'mission': 'Make healthcare simple and intuitive',
            'pain_points': ['InsurTech innovation', 'Member experience'],
            'your_angle': 'Insurance + AI expertise from Humana'
        },
        {
            'company': 'Medium',
            'ceo': 'Tony Stubblebine',
            'recent_news': 'VP Engineering role reporting to CEO',
            'mission': 'Deepen understanding through quality content',
            'pain_points': ['Platform scaling', 'Content recommendation'],
            'your_angle': 'Enterprise discipline + startup innovation'
        },
        {
            'company': 'Infinitus',
            'ceo': 'Ankit Jain',
            'recent_news': 'Automating healthcare phone calls with AI',
            'mission': 'Automate healthcare communications',
            'pain_points': ['Voice AI at scale', 'Healthcare integrations'],
            'your_angle': 'Automated complex workflows at Humana'
        }
    ]
    
    output_dir = Path("ready_to_send_messages")
    output_dir.mkdir(exist_ok=True)
    
    all_messages = {}
    
    for target in priority_targets:
        print(f"\n📝 Generating messages for {target['company']}...")
        
        # Create custom profile based on known data
        profile = system.research_company(target['company'])
        
        # Override with our specific research
        profile.ceo_name = target['ceo']
        profile.recent_news = [target['recent_news']]
        profile.mission_statement = target['mission']
        profile.pain_points = target['pain_points']
        
        # Generate LinkedIn message
        linkedin_msg = system.create_message(
            profile,
            OutreachChannel.LINKEDIN,
            style=MessageStyle.STARTUP_CASUAL if profile.size == 'startup' else MessageStyle.VISIONARY_STRATEGIC
        )
        
        # Generate email
        email_msg = system.create_message(
            profile,
            OutreachChannel.EMAIL,
            style=MessageStyle.DATA_DRIVEN
        )
        
        # Generate cover letter
        cover_letter = system.create_message(
            profile,
            OutreachChannel.APPLICATION_COVER,
            style=MessageStyle.FORMAL_ENTERPRISE if profile.size == 'enterprise' else MessageStyle.TECHNICAL_DETAILED
        )
        
        # Save to files
        company_dir = output_dir / target['company'].replace(' ', '_')
        company_dir.mkdir(exist_ok=True)
        
        # LinkedIn message
        with open(company_dir / "linkedin_message.txt", 'w') as f:
            f.write(f"TO: {target['ceo']} (CEO of {target['company']})\n")
            f.write(f"CHANNEL: LinkedIn Direct Message\n")
            f.write(f"PERSONALIZATION SCORE: {linkedin_msg['personalization_score']:.0f}%\n")
            f.write("="*60 + "\n\n")
            f.write(linkedin_msg['message'])
        
        # Email
        with open(company_dir / "email_message.txt", 'w') as f:
            f.write(f"TO: {target['ceo']}@{target['company'].lower().replace(' ', '')}.com\n")
            f.write(f"SUBJECT: {email_msg['subject']}\n")
            f.write(f"PERSONALIZATION SCORE: {email_msg['personalization_score']:.0f}%\n")
            f.write("="*60 + "\n\n")
            f.write(email_msg['message'])
        
        # Cover letter
        with open(company_dir / "cover_letter.txt", 'w') as f:
            f.write(f"FOR: Principal Engineer Position at {target['company']}\n")
            f.write(f"PERSONALIZATION SCORE: {cover_letter['personalization_score']:.0f}%\n")
            f.write("="*60 + "\n\n")
            f.write(cover_letter['message'])
        
        # Store for summary
        all_messages[target['company']] = {
            'linkedin': linkedin_msg,
            'email': email_msg,
            'cover_letter': cover_letter,
            'ceo': target['ceo'],
            'angle': target['your_angle']
        }
        
        print(f"✅ Messages ready for {target['company']}")
        print(f"   📊 Personalization: {linkedin_msg['personalization_score']:.0f}%")
    
    # Create master summary
    summary = """
📋 READY-TO-SEND MESSAGE SUMMARY
════════════════════════════════════════════════════════════

🎯 SEND THESE IN THIS ORDER:

1. SHIV RAO (Abridge) - HIGHEST PRIORITY
   LinkedIn: ready_to_send_messages/Abridge/linkedin_message.txt
   Angle: Healthcare automation expertise + $550M funding acknowledgment
   Action: Send LinkedIn message NOW (already started conversation)

2. ERIC LEFKOFSKY (Tempus) - HIGH PRIORITY  
   LinkedIn: ready_to_send_messages/Tempus/linkedin_message.txt
   Angle: 58-model AI system + precision medicine alignment
   Action: Send after Abridge (10 min gap)

3. MARIO SCHLOSSER (Oscar Health) - HIGH PRIORITY
   LinkedIn: ready_to_send_messages/Oscar_Health/linkedin_message.txt
   Angle: InsurTech + AI from Humana perspective
   Action: Send in afternoon

4. TONY STUBBLEBINE (Medium) - MEDIUM PRIORITY
   LinkedIn: ready_to_send_messages/Medium/linkedin_message.txt
   Angle: VP Engineering role reporting directly to him
   Action: Send tomorrow morning

5. ANKIT JAIN (Infinitus) - MEDIUM PRIORITY
   LinkedIn: ready_to_send_messages/Infinitus/linkedin_message.txt
   Angle: Healthcare workflow automation expertise
   Action: Send tomorrow afternoon

📊 PERSONALIZATION SCORES:
"""
    
    for company, msgs in all_messages.items():
        avg_score = (msgs['linkedin']['personalization_score'] + 
                    msgs['email']['personalization_score']) / 2
        summary += f"- {company}: {avg_score:.0f}% personalized\n"
    
    summary += """

💡 TIPS FOR SENDING:
1. Check if they've viewed your profile first
2. Send LinkedIn messages between 7-9 AM or 2-3 PM
3. Space messages 10-15 minutes apart
4. Follow their company page before messaging
5. Engage with their recent posts if any

📁 ALL MESSAGES SAVED TO: ready_to_send_messages/

⚡ QUICK COPY COMMANDS:
- cat ready_to_send_messages/Abridge/linkedin_message.txt
- cat ready_to_send_messages/Tempus/linkedin_message.txt
- cat ready_to_send_messages/Oscar_Health/linkedin_message.txt

🎯 EXPECTED OUTCOMES:
- 20-30% will view your profile
- 10-15% will respond
- 5% will lead to interviews
- 1-2% will convert to offers

GO SEND THESE NOW! Time is money at $400K+ level.
"""
    
    # Save summary
    with open(output_dir / "README_SEND_NOW.txt", 'w') as f:
        f.write(summary)
    
    print(summary)
    
    return all_messages


def generate_follow_up_templates():
    """Generate follow-up templates for non-responders"""
    
    follow_ups = {
        '3_day': """Hi {first_name},

Quick follow-up on my message about {company}'s {recent_achievement}.

I realize you're managing {challenge}. My experience {specific_value} could help accelerate this.

Worth a brief call?

Matthew""",
        
        '7_day': """Hi {first_name},

I know you're incredibly busy with {company_priority}.

I'll be direct: I can start immediately as {role} and bring 10 years of healthcare expertise that would normally take months to find.

If timing isn't right, I understand. I'll continue following {company}'s impressive journey.

Best,
Matthew""",
        
        '14_day_final': """Hi {first_name},

Final follow-up - I'm accepting a position soon but {company} remains my top choice because {specific_reason}.

If there's someone else on your team I should connect with about {role} opportunities, I'd appreciate the introduction.

Either way, best wishes with {company_goal}.

Matthew"""
    }
    
    output_dir = Path("ready_to_send_messages") / "follow_up_templates"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for timing, template in follow_ups.items():
        with open(output_dir / f"{timing}_template.txt", 'w') as f:
            f.write(f"FOLLOW-UP TEMPLATE: {timing.replace('_', ' ').upper()}\n")
            f.write("="*60 + "\n\n")
            f.write(template)
            f.write("\n\n" + "="*60 + "\n")
            f.write("VARIABLES TO REPLACE:\n")
            f.write("- {first_name}: CEO's first name\n")
            f.write("- {company}: Company name\n")
            f.write("- {recent_achievement}: Their recent news/funding\n")
            f.write("- {challenge}: Their main challenge\n")
            f.write("- {specific_value}: Your relevant experience\n")
            f.write("- {company_priority}: Their current focus\n")
            f.write("- {role}: Target position\n")
            f.write("- {specific_reason}: Why this company\n")
            f.write("- {company_goal}: Their mission/objective\n")
    
    print("✅ Follow-up templates created in: ready_to_send_messages/follow_up_templates/")


if __name__ == "__main__":
    # Generate all messages
    messages = generate_quick_messages()
    
    # Generate follow-up templates
    generate_follow_up_templates()
    
    print("\n" + "="*60)
    print("🚀 ALL MESSAGES READY TO SEND!")
    print("📁 Location: ready_to_send_messages/")
    print("⏰ Send the first one NOW - every minute counts!")
    print("="*60)