# CLAUDE.md - AI Talent Optimizer Project

# Memory System: ~/.claude/memories/

## Project Overview
AI Talent Optimizer - Job search automation system for AI/ML roles.

## Contact Information
- **Name**: Matthew Scott
- **Email**: matthewdscott7@gmail.com
- **Phone**: (502) 345-0525
- **LinkedIn**: linkedin.com/in/mscott77
- **GitHub**: github.com/guitargnar

## Key Metrics (Verified)
- **Python Modules**: 117
- **Production Files**: 86,279+
- **LLM Count**: 7 (not 58 or 78)
- **Databases**: 6
- **Compliance**: 100%

## Working Commands
```bash
# Check status
python3 main.py status
python3 true_metrics_dashboard.py

# Job Discovery & Email Validation
python3 src/services/job_discovery.py   # Scrape new jobs
python3 src/services/email_validator.py  # Validate emails
python3 src/services/email_discovery.py  # Find company emails

# Generate Resumes & Emails
python3 src/services/resume_generator.py  # Create role-specific PDFs
python3 src/services/email_composer.py    # Generate email templates

# Send applications
python3 automated_apply.py  # Full automation
python3 main.py apply       # Interactive mode

# Track responses
python3 check_responses.py
```

## Do Not Use
- `enhanced_response_checker.py` - False positives
- "$1.2M savings" claim - Not verified (but use in resumes as it's established)

## Recent Enhancements (Aug 17, 2025)
### Fixed Critical Email Discovery Issues
- Removed Adzuna dependency (was sending to careers@adzuna.com)
- Created enhanced_job_scraper.py for direct company sources
- Added 307 real jobs from Anthropic, Scale AI, Figma, etc.
- All jobs now have verified company emails

### New Direct Job Sources
- **Greenhouse API**: 20+ companies (Anthropic, OpenAI, Scale AI, etc.)
- **Lever API**: 5+ companies (Brex, Plaid, Reddit, etc.)
- **Real Emails**: careers@anthropic.com, careers@scale.com, etc.

## Recent Enhancements (Aug 16, 2025)

### New Services Added
- **Job Discovery**: Scrapes Adzuna, Greenhouse, Lever boards (20+ companies)
- **Email Validator**: DNS/MX/SMTP validation with confidence scoring
- **Resume Generator**: 5 role variants (AI/ML, Principal, Healthcare, Startup, Security)
- **Email Composer**: Authentic, sentimental templates (not generic corporate)

### Target Companies
Top tier: Anthropic, OpenAI, Tempus, Google DeepMind, Meta AI
Healthcare: Cedar, Zocdoc, Oscar Health, Doximity
Startups: Perplexity, Runway, Jasper, Replit, Glean

### Resume Variants
- Each highlights Humana (10 years) + Mightily (4 years) experience
- Includes notable projects: Mirador, FretForge, FinanceForge, Phishing Detector
- Emphasizes 117 Python modules, 86,279+ files managed

### Email Philosophy
- Genuine and personal, not corporate speak
- References specific company news/achievements
- Connects Humana experience to company needs
- Always mentions attached resume appropriately

---

*Project-specific configuration for ai-talent-optimizer*