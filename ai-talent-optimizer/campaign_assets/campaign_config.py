"""
Campaign Configuration for Project Ascent
Tiered targeting system with resume and template mappings
"""

# Tier 1: Internal Humana VPs and Leadership
TIER_1_TARGETS = [
    {
        "name": "VP of AI/ML",
        "company": "Humana",
        "title": "Vice President, Artificial Intelligence & Machine Learning",
        "priority": "CRITICAL",
        "notes": "Direct path to Principal role internally"
    },
    {
        "name": "VP of Digital Innovation",
        "company": "Humana",
        "title": "Vice President, Digital Innovation & Transformation",
        "priority": "CRITICAL",
        "notes": "Champions enterprise AI initiatives"
    },
    {
        "name": "VP of Healthcare Technology",
        "company": "Humana",
        "title": "Vice President, Healthcare Technology Solutions",
        "priority": "HIGH",
        "notes": "Oversees technical platforms"
    },
    {
        "name": "CTO",
        "company": "Humana",
        "title": "Chief Technology Officer",
        "priority": "HIGH",
        "notes": "Ultimate decision maker for tech initiatives"
    }
]

# Tier 2: Healthcare AI Companies
TIER_2_TARGETS = [
    {
        "name": "Mario Schlosser",
        "company": "Oscar Health",
        "title": "CEO & Co-Founder",
        "priority": "HIGH",
        "linkedin": "https://www.linkedin.com/in/marioschlosser/",
        "specific_project": "AI-powered health insurance platform",
        "specific_technology": "predictive healthcare analytics",
        "company_focus": "member-centric digital health",
        "specific_challenge": "scaling personalized healthcare recommendations"
    },
    {
        "name": "Eric Lefkofsky",
        "company": "Tempus",
        "title": "CEO & Founder",
        "priority": "HIGH",
        "linkedin": "https://www.linkedin.com/in/elefkofsky/",
        "specific_project": "precision medicine platform",
        "specific_technology": "clinical and molecular data analytics",
        "company_focus": "AI-driven precision medicine",
        "specific_challenge": "integrating multi-modal healthcare data"
    },
    {
        "name": "Florian Otto",
        "company": "Cedar",
        "title": "CEO & Co-Founder",
        "priority": "MEDIUM",
        "specific_project": "patient financial experience platform",
        "specific_technology": "healthcare billing automation",
        "company_focus": "patient financial engagement",
        "specific_challenge": "simplifying healthcare payments"
    },
    {
        "name": "Shiv Rao",
        "company": "Abridge",
        "title": "CEO & Founder",
        "priority": "HIGH",
        "specific_project": "medical conversation AI",
        "specific_technology": "clinical NLP",
        "company_focus": "automating medical documentation",
        "specific_challenge": "real-time medical transcription accuracy"
    }
]

# Tier 3: Big Tech & AI Research Companies
TIER_3_TARGETS = [
    {
        "name": "Healthcare AI Lead",
        "company": "Meta",
        "priority": "HIGH",
        "specific_challenge": "scaling AI across billions of users",
        "notes": "E7 Staff ML Engineer roles"
    },
    {
        "name": "Health AI Lead",
        "company": "Google",
        "priority": "HIGH",
        "specific_challenge": "democratizing healthcare AI",
        "notes": "L7 Staff Software Engineer roles"
    },
    {
        "name": "HealthLake Team",
        "company": "Amazon",
        "priority": "MEDIUM",
        "specific_challenge": "HIPAA-compliant ML at scale",
        "notes": "Principal Engineer roles"
    },
    {
        "name": "Healthcare Initiative",
        "company": "OpenAI",
        "priority": "MOONSHOT",
        "specific_paper": "GPT-4 medical applications",
        "notes": "Research engineer roles"
    },
    {
        "name": "Applied AI Team",
        "company": "Anthropic",
        "priority": "MOONSHOT",
        "specific_paper": "Constitutional AI for healthcare",
        "notes": "Safety-focused AI roles"
    }
]

# Resume mapping by tier
RESUME_MAPPING = {
    "tier_1": "HEALTHCARE_AI_RESUME",  # Emphasize Humana experience
    "tier_2": "HEALTHCARE_AI_RESUME",  # Healthcare domain expertise
    "tier_3_platform": "PLATFORM_ENGINEERING_RESUME",  # Scale and systems
    "tier_3_research": "AI_RESEARCH_RESUME"  # Innovation and research
}

# Template mapping by tier
TEMPLATE_MAPPING = {
    "tier_1": "HUMANA_VP_TEMPLATE",
    "tier_2": "HEALTHCARE_AI_TEMPLATE",
    "tier_3_tech": "BIG_TECH_TEMPLATE",
    "tier_3_research": "AI_RESEARCH_TEMPLATE",
    "follow_up": "FOLLOW_UP_TEMPLATE"
}

# Daily targets for sustained campaign
CAMPAIGN_TARGETS = {
    "applications_per_day": 5,
    "networking_messages_per_day": 3,
    "follow_ups_per_week": 10,
    "linkedin_posts_per_week": 3,
    "github_commits_per_week": 5
}

# Success metrics to track
SUCCESS_METRICS = {
    "target_callback_rate": 0.15,  # 15%
    "target_interview_rate": 0.10,  # 10%
    "target_offer_timeline_days": 60,  # 2 months
    "minimum_salary": 250000,
    "target_salary": 400000,
    "acceptable_titles": [
        "Principal Engineer",
        "Staff Engineer",
        "Principal ML Engineer",
        "Staff ML Engineer",
        "VP Engineering",
        "Director of AI",
        "Head of AI Platform"
    ]
}