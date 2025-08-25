# 🚀 AI Job Hunter Automation - Complete Setup Guide

## What Has Been Automated

### 1. **Job Discovery** (Automated)
- Searches 6+ sources for AI/ML jobs every day at 9am and 6pm
- Discovers 25-50 new opportunities per run
- Filters by relevance score and salary
- Saves to unified database

### 2. **Email Tracking** (Automated)
- **BCC Tracking**: All sent applications are automatically tracked
- **Gmail Monitoring**: Responses from 15 target companies monitored
- **Follow-up Scheduling**: Automatic reminders at 3, 7, and 14 days

### 3. **Application Submission** (Semi-Automated)
- Generates personalized cover letters
- Tracks all applications in database
- Rate-limited to prevent spam
- BCC tracking for all sent emails

### 4. **Response Monitoring** (Automated)
- Checks Gmail every 30 minutes
- Categorizes responses (interview, rejection, etc.)
- Alerts for urgent actions

### 5. **Daily Reporting** (Automated)
- Morning and evening summaries
- Performance metrics
- Top opportunities list
- Action items

## 🎯 Quick Start Commands

```bash
# Manual full run
./run_now.sh

# Run job discovery only
python unified_ai_hunter.py --daily

# Send applications (batch of 5)
python automated_apply.py --batch 5

# Check email responses
python gmail_recent_monitor.py

# Generate report
python run_automation.py --report

# View database stats
sqlite3 -column -header UNIFIED_AI_JOBS.db "SELECT COUNT(*) as total, COUNT(CASE WHEN applied=1 THEN 1 END) as applied FROM job_discoveries"
```

## 📅 Scheduled Automation

The system runs automatically:
- **9:00 AM**: Morning discovery + applications
- **6:00 PM**: Evening discovery + applications
- **Every 30 min**: Email response checking

### Managing the Schedule

```bash
# Start morning job manually
launchctl start com.matthewscott.aijobhunter.morning

# Stop automation
launchctl stop com.matthewscott.aijobhunter.morning

# View logs
tail -f logs/morning_run.log
```

## 📊 Current Status

```bash
# Check what's in the database
sqlite3 UNIFIED_AI_JOBS.db "SELECT company, position, salary_range FROM job_discoveries WHERE applied=0 ORDER BY relevance_score DESC LIMIT 5"

# See today's activity
cat daily_summaries/summary_$(date +%Y%m%d).json | jq .
```

## 🔧 Configuration Files

### Key Files to Edit:
1. **`.env`** - Email credentials and API keys
2. **`unified_config.json`** - Job preferences and targets
3. **`email_config.json`** - Email settings and BCC addresses

### Important Paths:
- Database: `UNIFIED_AI_JOBS.db`
- Logs: `logs/`
- Daily summaries: `daily_summaries/`
- Email tracking: `data/`

## 🚨 Troubleshooting

### If jobs aren't being discovered:
```bash
# Test scrapers
python connect_job_scrapers.py --test

# Check API credentials
cat .env | grep ADZUNA
```

### If emails aren't sending:
```bash
# Test email setup
python setup_email.py

# Check credentials
python test_email_automation.py
```

### If automation isn't running:
```bash
# Check launchd status
launchctl list | grep aijobhunter

# View error logs
tail -f logs/morning_run_error.log
```

## 💡 Next Steps & Improvements

### What's Working:
- ✅ Job discovery from multiple sources
- ✅ Email tracking with BCC
- ✅ Automated scheduling
- ✅ Database tracking
- ✅ Daily reporting

### Future Enhancements:
1. **Resume Customization** - Generate job-specific resumes
2. **Company Research** - Auto-research before applying
3. **Interview Prep** - Generate prep materials when interview scheduled
4. **LinkedIn Integration** - Auto-connect with recruiters
5. **Success Analytics** - Track what's working best

## 📈 Performance Metrics

Based on current configuration:
- **Discovery**: 50-100 jobs/day
- **Applications**: 20-30/day (rate limited)
- **Response Rate**: Track via reports
- **Time Investment**: ~2 hours saved/day

## 🎉 You're All Set!

The AI Job Hunter is now running automatically. It will:
1. Find new AI/ML jobs twice daily
2. Send personalized applications
3. Track all responses
4. Alert you to urgent actions

Just check your email for interview requests and let the system handle the repetitive work!

---

*Remember: The goal is maximum impact with minimum effort. Let automation handle the volume while you focus on the high-value interactions.*