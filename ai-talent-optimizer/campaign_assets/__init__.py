"""
Project Ascent Campaign Assets Module
Stores all campaign materials for the $400K+ Principal AI/ML role search
"""

from .resume_variants import (
    MASTER_RESUME,
    HEALTHCARE_AI_RESUME,
    PLATFORM_ENGINEERING_RESUME,
    AI_RESEARCH_RESUME
)

from .networking_templates import (
    HUMANA_VP_TEMPLATE,
    HEALTHCARE_AI_TEMPLATE,
    BIG_TECH_TEMPLATE,
    AI_RESEARCH_TEMPLATE,
    FOLLOW_UP_TEMPLATE
)

from .portfolio_assets import (
    BLOG_POST_LINK,
    GITHUB_PROFILE,
    PORTFOLIO_EVIDENCE,
    KEY_METRICS
)

from .campaign_config import (
    TIER_1_TARGETS,
    TIER_2_TARGETS,
    TIER_3_TARGETS,
    RESUME_MAPPING,
    TEMPLATE_MAPPING
)

__all__ = [
    'MASTER_RESUME',
    'HEALTHCARE_AI_RESUME',
    'PLATFORM_ENGINEERING_RESUME',
    'AI_RESEARCH_RESUME',
    'HUMANA_VP_TEMPLATE',
    'HEALTHCARE_AI_TEMPLATE',
    'BIG_TECH_TEMPLATE',
    'AI_RESEARCH_TEMPLATE',
    'FOLLOW_UP_TEMPLATE',
    'BLOG_POST_LINK',
    'GITHUB_PROFILE',
    'PORTFOLIO_EVIDENCE',
    'KEY_METRICS',
    'TIER_1_TARGETS',
    'TIER_2_TARGETS',
    'TIER_3_TARGETS',
    'RESUME_MAPPING',
    'TEMPLATE_MAPPING'
]