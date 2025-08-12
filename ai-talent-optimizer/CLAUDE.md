# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL: Use Only ACCURATE Tracking Tools

### ✅ CORRECT WORKFLOW (No False Positives!)
```bash
# 1. View REAL metrics (not inflated)
python3 true_metrics_dashboard.py

# 2. Check for bounced emails
python3 bounce_detector.py  

# 3. Check for ACTUAL interview requests
python3 accurate_response_checker.py

# 4. Send applications with email verification
python3 automated_apply.py --batch 10
```

### ❌ DO NOT USE (100% False Positives!)
```bash
python3 enhanced_response_checker.py  # WRONG - counts non-job emails as responses
```

## Project Overview

AI Talent Optimizer is a comprehensive job search automation system designed for AI/ML engineers. It focuses on maximizing visibility to AI-powered recruitment systems through profile optimization, automated application tracking, and signal boosting strategies.

**VERIFIED STATUS**: 73+ applications sent, BCC tracking confirmed working, but ZERO actual interview responses received (previous "24.7% response rate" was false positives).

## ✅ WORKING Commands (Use These!)

### Primary Application Commands
```bash
# Check current application status - WORKS PERFECTLY
python3 check_automation_status.py

# Apply to top AI jobs - SENDS 5 APPLICATIONS
python3 apply_top_ai_jobs.py

# Run full automation cycle - COMPREHENSIVE
python3 run_automation.py

# Send personalized applications - UNIQUE CONTENT
python3 personalized_apply.py

# Generate detailed status report
python3 generate_status_report.py
```

### 🆕 ACCURATE TRACKING COMMANDS (Fixed!)

#### True Metrics Dashboard (NO FALSE POSITIVES)
```bash
# View ONLY verified metrics - no assumptions or false positives
python3 true_metrics_dashboard.py
```

#### Response Tracking & Analytics
```bash
# ⚠️ DEPRECATED - DO NOT USE - Has 100% false positive rate
# python3 enhanced_response_checker.py  # ❌ COUNTS NON-JOB EMAILS AS RESPONSES

# ✅ USE INSTEAD - Accurate response checking with strict validation
python3 accurate_response_checker.py

# Gmail credentials automatically loaded from .env file
# Location: /Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/.env
```

#### Email Verification & Bounce Detection
```bash
# Detect and track bounced emails
python3 bounce_detector.py

# Verify email addresses before sending
python3 email_verification_system.py
```

#### A/B Testing System
```bash
# View A/B testing performance dashboard
python3 ab_testing_system.py

# Auto-optimize based on performance (every 20 applications)
python3 -c "from ab_testing_system import ABTestingSystem; ab = ABTestingSystem(); ab.auto_optimize()"
```

#### Smart Follow-Up Automation
```bash
# Send follow-ups to applications 3+ days old
python3 smart_followup_system.py

# Dry run to preview follow-ups
python3 smart_followup_system.py --dry-run

# Analyze follow-up effectiveness
python3 smart_followup_system.py --analyze
```

### Daily Workflow (ACCURATE - No False Positives!)
```bash
# Morning routine (9 AM)
cd /Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer
python3 true_metrics_dashboard.py   # View REAL metrics (no false positives!)
python3 bounce_detector.py          # Check for bounced emails (NEW!)
python3 accurate_response_checker.py # Check for REAL responses only
python3 run_automation.py           # Full automation cycle
python3 apply_top_ai_jobs.py        # Target AI-specific roles

# Afternoon (2 PM)
python3 automated_apply.py --batch 8  # Send batch applications (with email verification!)
python3 smart_followup_system.py      # Send follow-ups

# Evening (6 PM)
python3 apply_top_ai_jobs.py          # Another round
python3 ab_testing_system.py          # Review A/B test results
python3 true_metrics_dashboard.py     # End-of-day REAL metrics

# Check ACTUAL metrics (not inflated!)
sqlite3 UNIFIED_AI_JOBS.db "SELECT COUNT(*) as total, SUM(response_received) as responses FROM job_discoveries WHERE applied = 1;"
```

### Profile Optimization
```bash
# Optimize profiles
python profile_optimizer.py

# Generate visibility content
python visibility_amplifier.py

# Generate optimized resumes
python ats_ai_optimizer.py
```

### Testing & Monitoring
```bash
# System health check
python system_health_check.py

# Test email functionality
python test_email_send.py

# Check response metrics
python check_responses.py
```

## System Architecture

### Core Components
- **discovery_dashboard.py** - Central monitoring dashboard combining all metrics
- **unified_ai_hunter.py** - Main job discovery and tracking system
- **run_automation.py** - Orchestrates all automation components
- **email_application_tracker.py** - Tracks email applications with CSV storage
- **gmail_oauth_integration.py** - Gmail OAuth for monitoring responses

### Data Storage
- **UNIFIED_AI_JOBS.db** - SQLite database for job listings and applications
- **MASTER_TRACKER_400K.csv** - Priority company tracking spreadsheet
- **data/email_applications.csv** - Email application history
- **data/signal_activity_log.json** - Signal boost activity tracking

### Key Paths
- Base directory: `/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer`
- Career automation: `/Users/matthewscott/SURVIVE/career-automation`
- Gmail integration: `/Users/matthewscott/Google Gmail`
- Output directory: `output/` (resumes, dashboards, reports)

## Development Guidelines

### When Adding Features
1. Ensure data persistence (CSV or SQLite)
2. Add to discovery_dashboard.py for monitoring
3. Include in run_automation.py orchestration
4. Create terminal-friendly output (no complex UIs)

### Key Metrics Tracked
- Profile optimization score (target: 90%+)
- Daily application rate (target: 30+)
- Response rate (target: 15%+)  
- Interview conversion (target: 2%+)
- Signal boost ROI (target: 150%+)

### Authentication & Configuration
- Gmail OAuth: Uses token.json for authentication
- Environment variables: .env file for API keys
- CSV tracking: Append-only for history preservation

## Critical Files Not to Modify
- **MASTER_TRACKER_400K.csv** - Manual tracking document, read-only from code
- **token.json** - Gmail OAuth credentials
- **.env** - Environment configuration

## ⚠️ KNOWN ISSUES (Don't Use These)

### Broken Commands
```bash
# DON'T USE - Has 100% false positive rate
python3 enhanced_response_checker.py  # ❌ Counts ALL emails as job responses (API notifications, billing, etc.)

# USE INSTEAD
python3 accurate_response_checker.py  # ✅ Only counts REAL interview requests

# DON'T USE - Has import error
python3 check_responses.py  # ❌ GmailJobResponseChecker missing

# USE INSTEAD
python3 check_responses_simple.py  # ✅ Works

# DON'T USE - Returns no results
python3 ceo_outreach_bot.py  # ❌ Can't find CEO contacts
```

### Common Issues & Solutions

### Gmail Integration
- If OAuth fails: Re-run `python setup_gmail_oauth.py`
- Token refresh: Automatic, but can force with `python gmail_oauth_integration.py`
- For response checking: Use `check_responses_simple.py` NOT `check_responses.py`

### Database Issues
- Schema updates: Run `python fix_database_schema.py`
- Corruption: Backup exists at `UNIFIED_AI_JOBS.db.backup`
- Current count: 73+ applications successfully tracked

### Application Tracking
- Duplicate detection: Based on company + position + date
- CSV corruption: Backup at `data/email_applications.csv.backup`
- BCC tracking: Working correctly for all sent applications

## Testing Approach
- No formal test suite currently
- Manual testing via individual component scripts
- Use `test_*.py` files for component validation
- Check `system_health_check.py` for overall status

## Performance Targets
- Dashboard load: < 2 seconds
- Email check: < 5 seconds  
- Application submission: < 10 seconds
- Daily automation run: < 30 minutes total

## Deployment Notes
- Runs locally only (no cloud deployment)
- Manual execution via terminal or cron
- No web interface (terminal/CSV output only)
- Python 3.9+ required for all components

## 📊 REAL Success Metrics (Verified - No False Positives!)
- **Total Applications Sent**: 73+ ✅
- **BCC Tracking Confirmed**: 76 emails tracked to matthewdscott7+jobapps@gmail.com ✅
- **ACTUAL Interview Requests**: 0 (verified with strict validation)
- **False Positives Eliminated**: 111 non-job emails excluded
- **Email Verification**: Now checks MX records and legitimacy before sending
- **Bounce Detection**: Actively tracking and removing invalid addresses
- **TRUE Response Rate**: 0% (based on accurate checking, not inflated numbers)

### ⚠️ CRITICAL DISCOVERY
The "24.7% response rate" was completely FALSE:
- OpenAI emails were about GPU scheduler proposals (not job applications)
- HuggingFace emails were model access approvals (not interviews)
- NO actual interview requests have been received yet

## 🎯 Priority Manual Applications
These companies require manual application (not in scraped database):
- **Abridge** - $550M funding, CEO contacted
- **Tempus AI** - 59 open positions
- **Oscar Health** - GenAI implementation underway

## ⚠️ DO NOT USE: AI Trinity Platform
The AI Trinity Platform in other directories has significant issues:
- Database schema errors
- Missing dependencies
- Returns fake/mock data
- Parameter confusion in AI chat mode
**Stick to the AI Talent Optimizer - it's proven to work!**