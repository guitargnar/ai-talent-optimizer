#!/usr/bin/env python3
"""
Intelligent Messaging System - Modular, research-driven outreach for $400K+ roles
Analyzes company data to create perfectly tailored messages that convert
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from enum import Enum

class MessageStyle(Enum):
    """Different messaging styles based on company culture"""
    FORMAL_ENTERPRISE = "formal_enterprise"
    STARTUP_CASUAL = "startup_casual"
    TECHNICAL_DETAILED = "technical_detailed"
    VISIONARY_STRATEGIC = "visionary_strategic"
    DATA_DRIVEN = "data_driven"
    MISSION_FOCUSED = "mission_focused"

class OutreachChannel(Enum):
    """Communication channels"""
    LINKEDIN = "linkedin"
    EMAIL = "email"
    TWITTER = "twitter"
    APPLICATION_COVER = "application_cover"

@dataclass
class CompanyProfile:
    """Complete company intelligence profile"""
    name: str
    industry: str
    size: str  # startup, growth, enterprise
    funding_stage: str
    recent_news: List[str]
    mission_statement: str
    core_values: List[str]
    tech_stack: List[str]
    pain_points: List[str]
    leadership_style: str
    recent_achievements: List[str]
    open_positions: int
    target_role: str
    compensation_range: str
    ceo_name: str
    ceo_background: str
    company_culture: str

@dataclass
class PersonalNarrative:
    """Your story elements to weave into messages"""
    core_value_prop: str = "$1.2M saved at Humana through AI automation"
    unique_angle: str = "Claude Code analysis revealed opportunity"
    pain_point: str = "Under-utilized despite proven impact"
    superpower: str = "58-model AI orchestration system"
    availability: str = "Available immediately"
    proof_points: List[str] = None
    
    def __post_init__(self):
        if self.proof_points is None:
            self.proof_points = [
                "10 years Fortune 50 experience",
                "100% CMS compliance record",
                "Zero critical defects across 15+ systems",
                "432,000+ lines of production code",
                "3 years hands-on AI/ML experience"
            ]

class IntelligentMessagingSystem:
    """Creates highly personalized outreach based on deep company research"""
    
    def __init__(self):
        self.personal_narrative = PersonalNarrative()
        self.message_templates = self._load_message_templates()
        self.company_research_db = Path("company_research.json")
        self.message_history = Path("message_history.csv")
        self.effectiveness_tracker = Path("message_effectiveness.json")
        
        # Load or initialize databases
        self.company_data = self._load_company_research()
        self.message_performance = self._load_effectiveness_data()
        
    def _load_message_templates(self) -> Dict:
        """Load modular message components"""
        return {
            "hooks": {
                "funding": "Congratulations on your {funding_amount} {funding_round}. {specific_insight}",
                "growth": "Impressive {metric} growth - {specific_number} {timeframe}.",
                "mission": "Your mission to {mission_verb} {mission_object} resonates deeply with my {experience}.",
                "news": "Just saw the news about {recent_achievement}. {personal_connection}",
                "problem": "I've been thinking about {company}'s challenge with {pain_point}.",
                "innovation": "Your approach to {innovation_area} using {technology} is exactly where healthcare is heading.",
            },
            "bridges": {
                "claude_authentic": "I've been using Claude Code to analyze the {industry} landscape, and {company} consistently stands out because {reason}.",
                "underutilized": "After {years} years at {current_company} where I {achievement}, I'm seeking opportunities where my {skill} can have greater impact.",
                "goldmine": "I'm sitting on {years} years of {domain} insights and {specific_asset} that could accelerate {company_goal}.",
                "proven_roi": "My track record of delivering {roi_multiple}x ROI through {method} aligns perfectly with {company_need}.",
                "immediate_value": "I can start contributing to {specific_initiative} immediately, bringing {unique_value}.",
            },
            "value_props": {
                "quantified_impact": "At {previous_company}, I delivered {specific_metric} through {method}, directly applicable to {company_challenge}.",
                "technical_depth": "Built {technical_achievement} that {business_impact}, exactly the scale {company} needs for {objective}.",
                "domain_expertise": "{years} years navigating {industry} regulations while innovating - crucial for {company}'s {regulated_area}.",
                "speed_to_impact": "Unlike typical candidates who need {typical_ramp}, my {expertise} means delivering value from day one.",
                "risk_mitigation": "My {compliance_record} and {quality_metric} de-risk your {critical_project}.",
            },
            "calls_to_action": {
                "specific_role": "I'd love to discuss how my {expertise} could accelerate {company}'s {initiative} in the {role_title} position.",
                "fractional": "Would you be open to exploring how {time_commitment} of Fortune 50 expertise could accelerate {company_goal}?",
                "discovery": "Could we find {time_duration} to discuss how my experience {specific_experience} could benefit {team_or_initiative}?",
                "mutual_benefit": "I see a strong alignment between {company_need} and my {capability}. Worth a conversation?",
                "urgency": "With only {availability_window} in my schedule, I'm being selective. {company} is my top choice because {specific_reason}.",
            },
            "style_modifiers": {
                MessageStyle.FORMAL_ENTERPRISE: {
                    "greeting": "Dear {title} {last_name}",
                    "closing": "Best regards",
                    "tone_words": ["leverage", "synergies", "stakeholders", "strategic", "enterprise"]
                },
                MessageStyle.STARTUP_CASUAL: {
                    "greeting": "Hi {first_name}",
                    "closing": "Best",
                    "tone_words": ["build", "ship", "iterate", "disrupt", "scale"]
                },
                MessageStyle.TECHNICAL_DETAILED: {
                    "greeting": "Hi {first_name}",
                    "closing": "Best",
                    "tone_words": ["architecture", "latency", "throughput", "distributed", "pipeline"]
                },
                MessageStyle.VISIONARY_STRATEGIC: {
                    "greeting": "Hi {first_name}",
                    "closing": "Best wishes",
                    "tone_words": ["transform", "revolutionize", "paradigm", "future", "vision"]
                },
            }
        }
    
    def research_company(self, company_name: str, role_url: str = None) -> CompanyProfile:
        """Deep research on company to inform messaging"""
        print(f"🔍 Researching {company_name}...")
        
        # Check cache first
        if company_name in self.company_data:
            return CompanyProfile(**self.company_data[company_name])
        
        # Scrape job posting if URL provided
        job_data = self._scrape_job_posting(role_url) if role_url else {}
        
        # Research company website
        company_data = self._research_company_site(company_name)
        
        # Analyze news and social media
        recent_news = self._get_recent_news(company_name)
        
        # Build profile
        profile = CompanyProfile(
            name=company_name,
            industry=job_data.get('industry', 'Healthcare Technology'),
            size=self._determine_company_size(company_name),
            funding_stage=self._get_funding_info(company_name),
            recent_news=recent_news,
            mission_statement=company_data.get('mission', ''),
            core_values=company_data.get('values', []),
            tech_stack=job_data.get('tech_stack', []),
            pain_points=self._identify_pain_points(job_data, company_data),
            leadership_style=self._analyze_leadership_style(company_name),
            recent_achievements=company_data.get('achievements', []),
            open_positions=job_data.get('open_positions', 0),
            target_role=job_data.get('role_title', 'Principal Engineer'),
            compensation_range=job_data.get('compensation', '$400K+'),
            ceo_name=company_data.get('ceo_name', ''),
            ceo_background=company_data.get('ceo_background', ''),
            company_culture=self._analyze_culture(company_data, job_data)
        )
        
        # Cache the research
        self.company_data[company_name] = profile.__dict__
        self._save_company_research()
        
        return profile
    
    def create_message(
        self, 
        company_profile: CompanyProfile,
        channel: OutreachChannel,
        style: MessageStyle = None,
        role_specific: bool = True,
        test_variant: str = 'A'
    ) -> Dict[str, str]:
        """Generate a perfectly tailored message based on research"""
        
        # Auto-detect best style if not specified
        if not style:
            style = self._determine_best_style(company_profile)
        
        # Select message components based on research
        hook = self._select_best_hook(company_profile)
        bridge = self._select_best_bridge(company_profile)
        value_prop = self._select_best_value_prop(company_profile)
        cta = self._select_best_cta(company_profile, channel)
        
        # Personalize each component
        hook = self._personalize_component(hook, company_profile)
        bridge = self._personalize_component(bridge, company_profile)
        value_prop = self._personalize_component(value_prop, company_profile)
        cta = self._personalize_component(cta, company_profile)
        
        # Apply style modifiers
        greeting = self._get_greeting(company_profile, style)
        closing = self._get_closing(style)
        
        # Construct message based on channel
        if channel == OutreachChannel.LINKEDIN:
            message = self._build_linkedin_message(
                greeting, hook, bridge, value_prop, cta, closing
            )
        elif channel == OutreachChannel.EMAIL:
            message = self._build_email_message(
                greeting, hook, bridge, value_prop, cta, closing, company_profile
            )
        elif channel == OutreachChannel.APPLICATION_COVER:
            message = self._build_cover_letter(
                greeting, hook, bridge, value_prop, cta, closing, company_profile
            )
        else:
            message = f"{greeting},\n\n{hook}\n\n{bridge}\n\n{value_prop}\n\n{cta}\n\n{closing},\nMatthew Scott"
        
        # A/B test variants
        if test_variant == 'B':
            message = self._create_variant_b(message, company_profile)
        
        # Track message creation
        self._log_message(company_profile, channel, style, message)
        
        return {
            "message": message,
            "subject": self._generate_subject_line(company_profile, channel),
            "company": company_profile.name,
            "channel": channel.value,
            "style": style.value,
            "variant": test_variant,
            "personalization_score": self._calculate_personalization_score(message, company_profile)
        }
    
    def _select_best_hook(self, profile: CompanyProfile) -> str:
        """Choose the most relevant hook based on company research"""
        if profile.funding_stage and 'Series' in profile.funding_stage:
            return self.message_templates["hooks"]["funding"]
        elif profile.recent_achievements:
            return self.message_templates["hooks"]["news"]
        elif profile.mission_statement:
            return self.message_templates["hooks"]["mission"]
        elif profile.pain_points:
            return self.message_templates["hooks"]["problem"]
        else:
            return self.message_templates["hooks"]["innovation"]
    
    def _select_best_bridge(self, profile: CompanyProfile) -> str:
        """Choose the most relevant bridge based on company culture"""
        if profile.company_culture == 'innovative':
            return self.message_templates["bridges"]["claude_authentic"]
        elif profile.size == 'enterprise':
            return self.message_templates["bridges"]["proven_roi"]
        elif profile.size == 'startup':
            return self.message_templates["bridges"]["immediate_value"]
        else:
            return self.message_templates["bridges"]["goldmine"]
    
    def _select_best_value_prop(self, profile: CompanyProfile) -> str:
        """Choose the most compelling value prop for this company"""
        if 'compliance' in str(profile.pain_points).lower():
            return self.message_templates["value_props"]["risk_mitigation"]
        elif profile.tech_stack:
            return self.message_templates["value_props"]["technical_depth"]
        elif profile.industry == 'Healthcare':
            return self.message_templates["value_props"]["domain_expertise"]
        elif profile.size == 'startup':
            return self.message_templates["value_props"]["speed_to_impact"]
        else:
            return self.message_templates["value_props"]["quantified_impact"]
    
    def _select_best_cta(self, profile: CompanyProfile, channel: OutreachChannel) -> str:
        """Choose the most appropriate call-to-action"""
        if channel == OutreachChannel.LINKEDIN and profile.ceo_name:
            return self.message_templates["calls_to_action"]["discovery"]
        elif profile.target_role:
            return self.message_templates["calls_to_action"]["specific_role"]
        elif profile.size == 'startup':
            return self.message_templates["calls_to_action"]["fractional"]
        else:
            return self.message_templates["calls_to_action"]["mutual_benefit"]
    
    def _personalize_component(self, template: str, profile: CompanyProfile) -> str:
        """Fill in template with specific company data"""
        replacements = {
            "{company}": profile.name,
            "{funding_amount}": profile.funding_stage.split()[-1] if profile.funding_stage else "recent",
            "{funding_round}": profile.funding_stage.split()[0] if profile.funding_stage else "funding",
            "{specific_insight}": profile.recent_achievements[0] if profile.recent_achievements else "This positions you perfectly for scale",
            "{mission_verb}": profile.mission_statement.split()[0] if profile.mission_statement else "transform",
            "{mission_object}": ' '.join(profile.mission_statement.split()[1:3]) if profile.mission_statement else "healthcare delivery",
            "{experience}": "decade at Humana",
            "{recent_achievement}": profile.recent_achievements[0] if profile.recent_achievements else "your recent growth",
            "{personal_connection}": "This aligns with my work automating healthcare workflows",
            "{pain_point}": profile.pain_points[0] if profile.pain_points else "scaling technical infrastructure",
            "{innovation_area}": profile.tech_stack[0] if profile.tech_stack else "AI-driven automation",
            "{technology}": profile.tech_stack[1] if len(profile.tech_stack) > 1 else "machine learning",
            "{industry}": profile.industry,
            "{reason}": f"of your {profile.core_values[0] if profile.core_values else 'innovation'}",
            "{years}": "10",
            "{current_company}": "Humana",
            "{achievement}": "delivered $1.2M in annual savings",
            "{skill}": "AI orchestration expertise",
            "{domain}": "healthcare enterprise",
            "{specific_asset}": "58-model AI system architecture",
            "{company_goal}": f"your {profile.mission_statement[:30] if profile.mission_statement else 'growth objectives'}",
            "{roi_multiple}": "3",
            "{method}": "intelligent automation",
            "{company_need}": profile.pain_points[0] if profile.pain_points else "scaling challenges",
            "{specific_initiative}": f"your {profile.target_role.lower()} initiatives",
            "{unique_value}": "proven healthcare AI patterns",
            "{previous_company}": "Humana",
            "{specific_metric}": "$1.2M annual savings",
            "{company_challenge}": profile.pain_points[0] if profile.pain_points else "growth challenges",
            "{technical_achievement}": "a 58-model AI orchestration system",
            "{business_impact}": "saved $1.2M annually",
            "{objective}": "next growth phase",
            "{regulated_area}": "compliance requirements",
            "{typical_ramp}": "3-6 months to understand healthcare",
            "{expertise}": "healthcare domain knowledge",
            "{compliance_record}": "100% CMS compliance",
            "{quality_metric}": "zero critical defects",
            "{critical_project}": f"{profile.target_role} hire",
            "{role_title}": profile.target_role,
            "{time_commitment}": "2 days per week",
            "{time_duration}": "15 minutes",
            "{specific_experience}": "automating complex healthcare workflows",
            "{team_or_initiative}": f"your {profile.target_role.lower()} team",
            "{capability}": "proven ability to deliver $1M+ in value",
            "{availability_window}": "2 fractional slots",
            "{specific_reason}": f"your {profile.mission_statement[:50] if profile.mission_statement else 'vision aligns with my expertise'}",
            "{title}": "Mr." if profile.ceo_name else "",
            "{last_name}": profile.ceo_name.split()[-1] if profile.ceo_name else "",
            "{first_name}": profile.ceo_name.split()[0] if profile.ceo_name else "there",
        }
        
        for key, value in replacements.items():
            template = template.replace(key, str(value))
        
        return template
    
    def _determine_best_style(self, profile: CompanyProfile) -> MessageStyle:
        """Auto-detect the best messaging style based on company culture"""
        if profile.size == 'enterprise':
            return MessageStyle.FORMAL_ENTERPRISE
        elif profile.size == 'startup' and len(profile.tech_stack) > 3:
            return MessageStyle.TECHNICAL_DETAILED
        elif profile.size == 'startup':
            return MessageStyle.STARTUP_CASUAL
        elif 'transform' in profile.mission_statement.lower():
            return MessageStyle.VISIONARY_STRATEGIC
        elif profile.recent_achievements:
            return MessageStyle.DATA_DRIVEN
        else:
            return MessageStyle.MISSION_FOCUSED
    
    def _build_linkedin_message(
        self, greeting: str, hook: str, bridge: str, 
        value_prop: str, cta: str, closing: str
    ) -> str:
        """Build LinkedIn message (shorter, more casual)"""
        return f"""{greeting},

{hook}

{bridge}

{value_prop}

{cta}

{closing},
Matthew Scott"""
    
    def _build_email_message(
        self, greeting: str, hook: str, bridge: str,
        value_prop: str, cta: str, closing: str, profile: CompanyProfile
    ) -> str:
        """Build email message (longer, more detailed)"""
        return f"""{greeting},

{hook}

{bridge}

{value_prop}

Specific to {profile.name}:
• Your tech stack ({', '.join(profile.tech_stack[:3]) if profile.tech_stack else 'modern stack'}) - I've worked with similar at scale
• Your mission to {profile.mission_statement[:50] if profile.mission_statement else 'transform healthcare'} - aligns with my passion
• Your recent {profile.recent_achievements[0] if profile.recent_achievements else 'growth'} - I can accelerate this trajectory

{cta}

{closing},
Matthew Scott
matthewdscott7@gmail.com
(502) 345-0525
linkedin.com/in/mscott77

P.S. I'm available immediately and have already researched {profile.name}'s technical challenges. Ready to contribute from day one."""
    
    def _build_cover_letter(
        self, greeting: str, hook: str, bridge: str,
        value_prop: str, cta: str, closing: str, profile: CompanyProfile
    ) -> str:
        """Build formal cover letter for applications"""
        return f"""{greeting},

{hook}

{bridge}

{value_prop}

Why I'm the ideal {profile.target_role} for {profile.name}:

• **Proven ROI**: My $1.2M in annual savings at Humana demonstrates I deliver 3x return on any salary investment
• **Domain Expertise**: 10 years in healthcare technology means zero ramp-up time on regulatory requirements
• **Technical Excellence**: Built systems serving 50M+ users with 99.9% uptime and zero critical defects
• **Innovation Track Record**: My 58-model AI orchestration system shows architectural thinking at Principal level
• **Immediate Availability**: Ready to start contributing to {profile.name}'s success immediately

Your {profile.target_role} role requires someone who can balance technical excellence with business impact. My track record demonstrates exactly this balance - from writing 432,000+ lines of production code to delivering quantifiable business value.

{cta}

Thank you for considering my application. I look forward to discussing how my unique combination of healthcare expertise and technical innovation can accelerate {profile.name}'s mission.

{closing},
Matthew Scott

Attachments:
- Resume
- Portfolio: github.com/[username]
- References available upon request"""
    
    def _generate_subject_line(self, profile: CompanyProfile, channel: OutreachChannel) -> str:
        """Create compelling subject lines"""
        if channel == OutreachChannel.EMAIL:
            subjects = [
                f"{profile.target_role} - $1.2M Proven ROI + {profile.industry} Expertise",
                f"Re: {profile.name}'s {profile.target_role} Position - 10yr Healthcare Experience",
                f"{profile.ceo_name.split()[0] if profile.ceo_name else profile.name} - Fortune 50 Engineer Available for {profile.target_role}",
                f"Your {profile.pain_points[0] if profile.pain_points else 'scaling'} challenge - I solved this at Humana",
                f"{profile.recent_achievements[0][:30] if profile.recent_achievements else 'Your growth'} + My expertise = Acceleration"
            ]
            # Return the most relevant subject
            return subjects[0]
        return ""
    
    def _calculate_personalization_score(self, message: str, profile: CompanyProfile) -> float:
        """Score how personalized the message is (0-100)"""
        score = 0
        
        # Check for company name mentions
        score += message.lower().count(profile.name.lower()) * 10
        
        # Check for specific details
        if profile.ceo_name and profile.ceo_name in message:
            score += 15
        if profile.mission_statement and any(word in message for word in profile.mission_statement.split()[:5]):
            score += 10
        if profile.recent_achievements and any(ach in message for ach in profile.recent_achievements):
            score += 15
        if profile.tech_stack and any(tech in message for tech in profile.tech_stack):
            score += 10
        if profile.funding_stage and profile.funding_stage in message:
            score += 10
        
        # Check for personal narrative elements
        if "$1.2M" in message:
            score += 10
        if "58-model" in message or "58 model" in message:
            score += 10
        if "Claude Code" in message:
            score += 10
        
        return min(score, 100)
    
    def _scrape_job_posting(self, url: str) -> Dict:
        """Extract key information from job posting"""
        # This would actually scrape the job posting
        # For now, return sample data
        return {
            'role_title': 'Principal Engineer',
            'tech_stack': ['Python', 'Kubernetes', 'AWS', 'React'],
            'industry': 'Healthcare Technology',
            'compensation': '$450-550K',
            'open_positions': 15
        }
    
    def _research_company_site(self, company_name: str) -> Dict:
        """Research company website for mission, values, etc."""
        # This would actually scrape company website
        # For now, return sample data based on company
        company_data = {
            'Abridge': {
                'mission': 'Eliminate administrative burden in healthcare through AI',
                'values': ['Innovation', 'Impact', 'Integrity'],
                'ceo_name': 'Shiv Rao',
                'ceo_background': 'Former Carnegie Mellon researcher',
                'achievements': ['$550M Series C funding', 'Partnership with major health systems']
            },
            'Tempus': {
                'mission': 'Make precision medicine a reality through AI and data',
                'values': ['Data-driven', 'Patient-focused', 'Innovation'],
                'ceo_name': 'Eric Lefkofsky',
                'ceo_background': 'Serial entrepreneur, Groupon co-founder',
                'achievements': ['IPO at $8B valuation', '59 open positions']
            }
        }
        return company_data.get(company_name, {})
    
    def _get_recent_news(self, company_name: str) -> List[str]:
        """Get recent news about company"""
        # Would search news APIs
        news_items = {
            'Abridge': ['$550M Series C led by Lightspeed', 'Expansion to 15 new health systems'],
            'Tempus': ['Public offering completed', 'New AI lab opened in Chicago']
        }
        return news_items.get(company_name, [])
    
    def _identify_pain_points(self, job_data: Dict, company_data: Dict) -> List[str]:
        """Identify company pain points from research"""
        pain_points = []
        
        if job_data.get('open_positions', 0) > 10:
            pain_points.append('Scaling engineering team rapidly')
        if 'compliance' in str(job_data).lower() or 'healthcare' in str(company_data).lower():
            pain_points.append('Healthcare compliance complexity')
        if 'AI' in str(job_data) or 'ML' in str(job_data):
            pain_points.append('AI/ML implementation at scale')
        
        return pain_points
    
    def _determine_company_size(self, company_name: str) -> str:
        """Determine if startup, growth, or enterprise"""
        # Would check employee count, funding, etc.
        sizes = {
            'Abridge': 'growth',
            'Tempus': 'growth', 
            'UnitedHealth': 'enterprise',
            'Oscar Health': 'growth'
        }
        return sizes.get(company_name, 'growth')
    
    def _get_funding_info(self, company_name: str) -> str:
        """Get funding information"""
        funding = {
            'Abridge': 'Series C $550M',
            'Tempus': 'Public $8B',
            'Oscar Health': 'Public $7B'
        }
        return funding.get(company_name, '')
    
    def _analyze_leadership_style(self, company_name: str) -> str:
        """Analyze leadership communication style"""
        styles = {
            'Abridge': 'Visionary but grounded',
            'Tempus': 'Data-driven entrepreneurial',
            'Oscar Health': 'Mission-driven innovative'
        }
        return styles.get(company_name, 'Professional')
    
    def _analyze_culture(self, company_data: Dict, job_data: Dict) -> str:
        """Determine company culture"""
        if 'move fast' in str(company_data).lower():
            return 'startup-fast'
        elif 'innovation' in str(company_data).lower():
            return 'innovative'
        elif 'patient' in str(company_data).lower():
            return 'mission-driven'
        else:
            return 'professional'
    
    def _get_greeting(self, profile: CompanyProfile, style: MessageStyle) -> str:
        """Get appropriate greeting based on style"""
        style_mods = self.message_templates["style_modifiers"].get(style, {})
        greeting = style_mods.get("greeting", "Hi {first_name}")
        
        return greeting.format(
            title="Mr." if profile.ceo_name else "",
            last_name=profile.ceo_name.split()[-1] if profile.ceo_name else "",
            first_name=profile.ceo_name.split()[0] if profile.ceo_name else "there"
        )
    
    def _get_closing(self, style: MessageStyle) -> str:
        """Get appropriate closing based on style"""
        style_mods = self.message_templates["style_modifiers"].get(style, {})
        return style_mods.get("closing", "Best")
    
    def _create_variant_b(self, message_a: str, profile: CompanyProfile) -> str:
        """Create B variant for A/B testing"""
        # Make the message more direct/shorter
        lines = message_a.split('\n')
        # Remove middle paragraph for brevity
        if len(lines) > 8:
            lines = lines[:4] + lines[-4:]
        return '\n'.join(lines)
    
    def _log_message(self, profile: CompanyProfile, channel: OutreachChannel, 
                     style: MessageStyle, message: str):
        """Log message for tracking"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'company': profile.name,
            'channel': channel.value,
            'style': style.value,
            'ceo': profile.ceo_name,
            'role': profile.target_role,
            'message_length': len(message),
            'personalization_score': self._calculate_personalization_score(message, profile)
        }
        
        # Append to CSV
        df = pd.DataFrame([log_entry])
        if self.message_history.exists():
            df.to_csv(self.message_history, mode='a', header=False, index=False)
        else:
            df.to_csv(self.message_history, index=False)
    
    def _load_company_research(self) -> Dict:
        """Load cached company research"""
        if self.company_research_db.exists():
            with open(self.company_research_db, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_company_research(self):
        """Save company research to cache"""
        with open(self.company_research_db, 'w') as f:
            json.dump(self.company_data, f, indent=2)
    
    def _load_effectiveness_data(self) -> Dict:
        """Load message effectiveness tracking"""
        if self.effectiveness_tracker.exists():
            with open(self.effectiveness_tracker, 'r') as f:
                return json.load(f)
        return {
            'response_rates': {},
            'best_performing': {},
            'style_effectiveness': {}
        }
    
    def track_response(self, company: str, responded: bool, 
                       converted_to_interview: bool = False):
        """Track message effectiveness"""
        if company not in self.message_performance['response_rates']:
            self.message_performance['response_rates'][company] = {
                'sent': 0,
                'responded': 0,
                'interviewed': 0
            }
        
        stats = self.message_performance['response_rates'][company]
        stats['sent'] += 1
        if responded:
            stats['responded'] += 1
        if converted_to_interview:
            stats['interviewed'] += 1
        
        # Save updated stats
        with open(self.effectiveness_tracker, 'w') as f:
            json.dump(self.message_performance, f, indent=2)
    
    def generate_batch_messages(self, companies: List[Tuple[str, str]]) -> List[Dict]:
        """Generate messages for multiple companies efficiently"""
        messages = []
        
        for company_name, role_url in companies:
            print(f"\n📝 Generating message for {company_name}...")
            
            # Research company
            profile = self.research_company(company_name, role_url)
            
            # Generate messages for different channels
            linkedin_msg = self.create_message(
                profile, 
                OutreachChannel.LINKEDIN,
                test_variant='A'
            )
            
            email_msg = self.create_message(
                profile,
                OutreachChannel.EMAIL,
                test_variant='A'
            )
            
            cover_letter = self.create_message(
                profile,
                OutreachChannel.APPLICATION_COVER,
                test_variant='A'
            )
            
            messages.append({
                'company': company_name,
                'linkedin': linkedin_msg,
                'email': email_msg,
                'cover_letter': cover_letter,
                'profile': profile
            })
        
        return messages
    
    def get_performance_report(self) -> str:
        """Generate performance report of messaging effectiveness"""
        report = "📊 MESSAGE EFFECTIVENESS REPORT\n"
        report += "=" * 50 + "\n\n"
        
        for company, stats in self.message_performance['response_rates'].items():
            response_rate = (stats['responded'] / stats['sent'] * 100) if stats['sent'] > 0 else 0
            interview_rate = (stats['interviewed'] / stats['sent'] * 100) if stats['sent'] > 0 else 0
            
            report += f"{company}:\n"
            report += f"  Sent: {stats['sent']}\n"
            report += f"  Response Rate: {response_rate:.1f}%\n"
            report += f"  Interview Rate: {interview_rate:.1f}%\n\n"
        
        return report


def main():
    """Demo the intelligent messaging system"""
    system = IntelligentMessagingSystem()
    
    # Example: Generate messages for priority companies
    priority_companies = [
        ('Abridge', 'https://jobs.ashbyhq.com/abridge/principal-engineer'),
        ('Tempus', 'https://tempus.com/careers/principal-engineer'),
        ('Oscar Health', 'https://hioscar.com/careers/principal-engineer')
    ]
    
    print("""
╔══════════════════════════════════════════════════════════╗
║     INTELLIGENT MESSAGING SYSTEM - $400K+ OUTREACH        ║
║     Personalized, Research-Driven, High-Converting        ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    messages = system.generate_batch_messages(priority_companies)
    
    # Save messages to files
    output_dir = Path("personalized_messages")
    output_dir.mkdir(exist_ok=True)
    
    for msg_set in messages:
        company = msg_set['company']
        
        # Save LinkedIn message
        with open(output_dir / f"{company}_linkedin.txt", 'w') as f:
            f.write(msg_set['linkedin']['message'])
            
        # Save email
        with open(output_dir / f"{company}_email.txt", 'w') as f:
            f.write(f"Subject: {msg_set['email']['subject']}\n\n")
            f.write(msg_set['email']['message'])
            
        # Save cover letter
        with open(output_dir / f"{company}_cover_letter.txt", 'w') as f:
            f.write(msg_set['cover_letter']['message'])
        
        print(f"\n✅ Generated messages for {company}")
        print(f"   Personalization Score: {msg_set['linkedin']['personalization_score']:.0f}%")
    
    print(f"\n📁 All messages saved to: {output_dir}/")
    print("\n" + system.get_performance_report())
    
    return system


if __name__ == "__main__":
    system = main()