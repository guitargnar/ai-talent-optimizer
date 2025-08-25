# CLAUDE.md - AI Talent Optimizer Project

# Memory System: ~/.claude/memories/

## Project Overview
AI Talent Optimizer - Strategic Career Platform v2.0 with human-in-the-loop workflow

## Contact Information
- **Name**: Matthew Scott
- **Email**: matthewdscott7@gmail.com
- **Phone**: (502) 345-0525
- **LinkedIn**: linkedin.com/in/mscott77
- **GitHub**: github.com/guitargnar

## Key Metrics (as of Aug 23, 2025)
- **Ollama Models**: 74 specialized models available
- **Real Source Files**: 274 Python files (NOT 22,247 - that included venv)
- **Applications Sent**: 17 REAL (some were DB-only)
- **High-Priority Jobs**: 48 pending (0.65+ score)
- **Bounce Rate**: 45.5% - needs email verification

## 🚀 PRIMARY COMMANDS (v2.0 - Strategic Platform)
```bash
# MAIN ENTRY POINT - USE THIS
python3 orchestrator.py          # Strategic command center with approval workflow

# Alternative Entry Points
python3 dynamic_apply.py "Job Title"    # Discover and apply to specific roles
python3 quality_first_apply.py          # Direct quality applications to top companies

# Metrics & Status
python3 true_metrics_dashboard.py       # Real metrics (no false positives)

# DO NOT USE - SENDS GENERIC SPAM
# python3 batch_send_smtp.py - Generic emails, no personalization
# python3 automated_apply.py - Deprecated, use orchestrator.py
```

## 🎯 Strategic Platform Architecture (v2.0)

### Workflow: Human-in-the-Loop
1. **Discover** - Find jobs online
2. **Generate** - Create personalized content  
3. **Stage** - Queue for review (staged_applications table)
4. **Review** - Human approval required
5. **Send** - Only after explicit approval

### Quality-First Features
- Company-specific research and personalization
- Resume variant selection (ai_ml, healthcare, platform, principal, startup)
- Smart subject lines (no generic "Application")
- 30-second professional spacing between sends
- BCC tracking for all sent applications

### Database Changes
- Added `staged_applications` table for review queue
- Status tracking: pending_review, sent, deleted
- Personalization scoring (0.85-0.99)
- Full email content storage for review

## ⚠️ CRITICAL DISCOVERIES (Aug 23, 2025)

### The 22,247 Files Issue - RESOLVED
- **Reality**: Only 274 actual source files
- **Problem**: 21,971 files were in ml-env virtual environment (2.5GB)
- **Largest real file**: 47KB (perfectly reasonable)
- **Action**: Exclude ml-env from all operations

### Email Sending Truth
- `batch_send_smtp.py` sends GENERIC SPAM - DO NOT USE
- Many "sent" applications were database-only (no email sent)
- Real sent count is likely much lower than reported
- Use orchestrator.py for quality-controlled sending

## Target Companies (Priority)
**Tier 1**: Anthropic, OpenAI, Tempus, Scale AI, Cohere
**Tier 2**: Databricks, Perplexity, Mistral AI, Hugging Face
**Healthcare AI**: Tempus, Flatiron Health, Komodo Health
**Platform**: Databricks, Snowflake, Weights & Biases

## Resume Variants Available
- `matthew_scott_ai_ml_engineer_resume.pdf` - AI/ML roles
- `matthew_scott_healthcare_tech_resume.pdf` - Healthcare companies
- `matthew_scott_platform_engineer_resume.pdf` - Infrastructure roles
- `matthew_scott_principal_engineer_resume.pdf` - Senior positions
- `matthew_scott_startup_resume.pdf` - Startup environments

## Session Handoff Notes
- **Latest commit**: 98014f1 (Strategic Platform v2.0)
- **Release tag**: v2.0.0
- **Key achievement**: Transformed generic system to quality-first platform
- **Next session**: Start with `python3 orchestrator.py`

## Future Integration Stubs (Ready for Enhancement)
- `WebFormAutomator` - Puppeteer integration for Greenhouse/Lever
- `LinkedInResearcher` - Find hiring managers
- `generate_content_with_ollama` - Chain 74 models for content

---

*Strategic Career Platform v2.0 - Quality First, Human Approved*