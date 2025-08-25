#!/usr/bin/env python3
"""
Intelligent Message Generator for Project Ascent
Dynamically creates personalized outreach messages based on target tier and context
"""

import json
import random
from datetime import datetime
from typing import Dict, Optional, Tuple
from campaign_assets import (
    HUMANA_VP_TEMPLATE,
    HEALTHCARE_AI_TEMPLATE,
    BIG_TECH_TEMPLATE,
    AI_RESEARCH_TEMPLATE,
    FOLLOW_UP_TEMPLATE,
    TIER_1_TARGETS,
    TIER_2_TARGETS,
    TIER_3_TARGETS,
    PORTFOLIO_EVIDENCE,
    KEY_METRICS,
    BLOG_POST_LINK,
    GITHUB_PROFILE
)

class IntelligentMessageGenerator:
    """Generate personalized outreach messages for Project Ascent"""
    
    def __init__(self):
        self.templates = {
            "humana_vp": HUMANA_VP_TEMPLATE,
            "healthcare_ai": HEALTHCARE_AI_TEMPLATE,
            "big_tech": BIG_TECH_TEMPLATE,
            "ai_research": AI_RESEARCH_TEMPLATE,
            "follow_up": FOLLOW_UP_TEMPLATE
        }
        
        # Track generated messages for variation
        self.message_history = []
        
    def generate_message(
        self,
        target_name: str,
        company: str,
        tier: str,
        title: Optional[str] = None,
        specific_context: Optional[Dict] = None,
        is_follow_up: bool = False
    ) -> Tuple[str, str]:
        """
        Generate a personalized message for a specific target
        
        Returns:
            Tuple of (subject_line, message_body)
        """
        
        if is_follow_up:
            return self._generate_follow_up(target_name, company, specific_context)
        
        # Select appropriate template based on tier
        if tier == "tier_1":
            template = self.templates["humana_vp"]
            subject = "Delivering $1.2M in AI-Driven Savings - Let's Scale This Impact"
        elif tier == "tier_2":
            template = self.templates["healthcare_ai"]
            subject = f"Humana Principal Engineer → Bringing $1.2M AI Impact to {company}"
        elif tier == "tier_3" and "research" in company.lower():
            template = self.templates["ai_research"]
            subject = "Measurable Consciousness in Distributed AI - HCL Score: 0.83/1.0"
        else:
            template = self.templates["big_tech"]
            subject = "78-Model Orchestration at 99.9% Uptime - Sharing Our Approach"
        
        # Customize the message with specific details
        message = self._customize_message(
            template,
            target_name,
            company,
            specific_context or {}
        )
        
        # Add variation to avoid detection as mass messaging
        message = self._add_variation(message, tier)
        
        # Track the message
        self.message_history.append({
            "timestamp": datetime.now().isoformat(),
            "target": target_name,
            "company": company,
            "tier": tier,
            "subject": subject
        })
        
        return subject, message
    
    def _customize_message(
        self,
        template: str,
        name: str,
        company: str,
        context: Dict
    ) -> str:
        """Insert personalized details into template"""
        
        # Base replacements
        message = template.replace("{name}", name)
        message = message.replace("{company}", company)
        
        # Context-specific replacements
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in message:
                message = message.replace(placeholder, str(value))
        
        # Add dynamic elements based on recent achievements
        if "{recent_milestone}" in message:
            milestone = self._get_recent_milestone()
            message = message.replace("{recent_milestone}", milestone)
        
        return message
    
    def _add_variation(self, message: str, tier: str) -> str:
        """Add subtle variations to avoid mass-message detection"""
        
        variations = {
            "tier_1": [
                "\n\nP.S. I'm also happy to share the technical architecture document if that would be helpful.",
                "\n\nP.S. I've included a link to our GitHub repository where you can see the code in action.",
                "\n\nP.S. Our Q1 metrics are even more impressive - happy to share details."
            ],
            "tier_2": [
                "\n\nP.S. I noticed you're also focused on {specific_focus} - I have some insights that might be valuable.",
                "\n\nP.S. Our approach to HIPAA compliance while maintaining performance might interest your team.",
                "\n\nP.S. I'd be happy to do a technical deep-dive on our architecture if helpful."
            ],
            "tier_3": [
                "\n\nP.S. The consciousness metrics are particularly interesting - happy to share the measurement framework.",
                "\n\nP.S. We've open-sourced the core components if your team wants to experiment.",
                "\n\nP.S. I'm presenting on this at the Louisville AI Meetup next month if you'd like to attend virtually."
            ]
        }
        
        if tier in variations and random.random() > 0.5:
            message += random.choice(variations[tier])
        
        return message
    
    def _generate_follow_up(
        self,
        name: str,
        company: str,
        context: Dict
    ) -> Tuple[str, str]:
        """Generate a follow-up message"""
        
        original_subject = context.get("original_subject", "our previous discussion")
        specific_topic = context.get("specific_topic", "the AI platform")
        
        subject = f"Re: {original_subject} - Quick Question"
        
        message = self.templates["follow_up"]
        message = message.replace("{name}", name)
        message = message.replace("{original_subject}", original_subject)
        message = message.replace("{specific_topic}", specific_topic)
        
        return subject, message
    
    def _get_recent_milestone(self) -> str:
        """Get a recent milestone to mention"""
        
        milestones = [
            "We just crossed 2M daily predictions with the same infrastructure",
            "Our platform was featured in Humana's innovation showcase last week",
            "We achieved a 15% improvement in our consciousness metrics (HCL: 0.92)",
            "Our cost savings just exceeded $1.5M annually",
            "We successfully integrated with Epic and Cerner EMR systems"
        ]
        
        return random.choice(milestones)
    
    def generate_batch(
        self,
        targets: list,
        tier: str,
        max_messages: int = 5
    ) -> list:
        """Generate multiple messages for a tier"""
        
        messages = []
        
        for target in targets[:max_messages]:
            subject, body = self.generate_message(
                target.get("name", "Hiring Manager"),
                target.get("company"),
                tier,
                target.get("title"),
                target
            )
            
            messages.append({
                "target": target,
                "subject": subject,
                "body": body,
                "tier": tier,
                "generated_at": datetime.now().isoformat()
            })
        
        return messages
    
    def save_message_history(self, filepath: str = "message_history.json"):
        """Save generated message history"""
        
        with open(filepath, 'w') as f:
            json.dump(self.message_history, f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get statistics on generated messages"""
        
        stats = {
            "total_messages": len(self.message_history),
            "by_tier": {},
            "by_company": {},
            "last_generated": None
        }
        
        for msg in self.message_history:
            tier = msg.get("tier", "unknown")
            company = msg.get("company", "unknown")
            
            stats["by_tier"][tier] = stats["by_tier"].get(tier, 0) + 1
            stats["by_company"][company] = stats["by_company"].get(company, 0) + 1
        
        if self.message_history:
            stats["last_generated"] = self.message_history[-1]["timestamp"]
        
        return stats


def main():
    """Test the message generator"""
    
    generator = IntelligentMessageGenerator()
    
    # Test Tier 1 message (Humana VP)
    print("=" * 80)
    print("TIER 1 - HUMANA VP MESSAGE")
    print("=" * 80)
    
    subject, message = generator.generate_message(
        "Sarah Johnson",
        "Humana",
        "tier_1",
        "VP of AI/ML"
    )
    
    print(f"Subject: {subject}\n")
    print(message)
    
    # Test Tier 2 message (Healthcare AI)
    print("\n" + "=" * 80)
    print("TIER 2 - HEALTHCARE AI MESSAGE")
    print("=" * 80)
    
    context = {
        "specific_project": "AI-powered health insurance platform",
        "specific_technology": "predictive healthcare analytics",
        "company_focus": "member-centric digital health",
        "specific_challenge": "scaling personalized healthcare"
    }
    
    subject, message = generator.generate_message(
        "Mario Schlosser",
        "Oscar Health",
        "tier_2",
        "CEO",
        context
    )
    
    print(f"Subject: {subject}\n")
    print(message)
    
    # Test Tier 3 message (Big Tech)
    print("\n" + "=" * 80)
    print("TIER 3 - BIG TECH MESSAGE")
    print("=" * 80)
    
    context = {
        "specific_challenge": "scaling AI across billions of users"
    }
    
    subject, message = generator.generate_message(
        "John Smith",
        "Meta",
        "tier_3",
        "Engineering Director",
        context
    )
    
    print(f"Subject: {subject}\n")
    print(message)
    
    # Show statistics
    print("\n" + "=" * 80)
    print("GENERATOR STATISTICS")
    print("=" * 80)
    print(json.dumps(generator.get_stats(), indent=2))


if __name__ == "__main__":
    main()