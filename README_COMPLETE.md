# 🚀 AI Job Hunter - Complete System Documentation

## System Overview
A fully automated AI/ML job hunting system that discovers opportunities, generates tailored applications, tracks responses, and manages the entire job search pipeline with minimal manual intervention.

## 🎯 The Finish Line: What "Complete" Looks Like

### A complete system means:
1. **Daily Automation**: Runs automatically at 9am and 6pm without intervention
2. **Full Pipeline**: Discovery → Application → Tracking → Follow-up → Reporting
3. **Quality Control**: Smart rate limiting, personalized content, professional templates
4. **Complete Visibility**: Know exactly what was sent, when, and to whom
5. **Response Tracking**: Monitor replies and interview requests
6. **Continuous Improvement**: Learn from response rates and optimize

### Success Metrics:
- 10-20 quality applications sent daily
- 5-10% response rate (industry standard is 2-3%)
- Zero manual data entry required
- Complete audit trail of all activities
- Professional, personalized communications

---

## 📁 Project Structure
```
ai-talent-optimizer/
├── UNIFIED_AI_JOBS.db          # Central database
├── .env                        # Gmail credentials
├── data/
│   └── bcc_tracking_log.json   # Email tracking
├── resumes/                    # Generated PDF resumes
├── output/resume_versions/     # Text versions
└── logs/                       # Application logs
```

---

## 🚦 Quick Start Commands

### 1. Initial Setup (One Time)
```bash
# Navigate to project directory
cd ~/AI-ML-Portfolio/ai-talent-optimizer

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "EMAIL_ADDRESS=matthewdscott7@gmail.com" > .env
echo "EMAIL_APP_PASSWORD=your-app-password-here" >> .env

# Generate resumes (already done, but if needed)
python ats_ai_optimizer.py
python resume_pdf_generator.py

# Set up automated scheduling
python setup_scheduler.py
```

### 2. Daily Operations

#### 🔍 **Morning Routine (9am)**
```bash
# Full automation cycle
python run_automation.py

# Or run components individually:
python job_discovery.py          # Find new jobs
python automated_apply.py --batch 10  # Apply to 10 jobs
python generate_status_report.py      # See results
```

#### 📊 **Status Check (Anytime)**
```bash
# View current status
python generate_status_report.py

# Check specific company applications
sqlite3 UNIFIED_AI_JOBS.db "SELECT * FROM job_discoveries WHERE company LIKE '%OpenAI%'"

# View email tracking
python -c "import json; print(json.dumps(json.load(open('data/bcc_tracking_log.json')), indent=2))"
```

#### 🌆 **Evening Routine (6pm)**
```bash
# Check for responses and send follow-ups
python check_responses.py
python send_followup_email.py

# Review day's activity
python generate_status_report.py
```

### 3. Manual Controls

#### 📧 **Send Applications**
```bash
# Apply to specific number of jobs
python automated_apply.py --batch 5

# Apply to specific companies
sqlite3 UNIFIED_AI_JOBS.db "UPDATE job_discoveries SET applied=0 WHERE company='Anthropic'"
python automated_apply.py --batch 1
```

#### 🔄 **Manage Scheduler**
```bash
# Start automated scheduling
launchctl load ~/Library/LaunchAgents/com.ai.jobhunter.*.plist

# Stop automated scheduling
launchctl unload ~/Library/LaunchAgents/com.ai.jobhunter.*.plist

# Check if running
launchctl list | grep jobhunter
```

#### 🧹 **Maintenance**
```bash
# Clean old applications (>30 days)
sqlite3 UNIFIED_AI_JOBS.db "DELETE FROM job_discoveries WHERE applied=1 AND applied_date < datetime('now', '-30 days')"

# Reset specific applications
sqlite3 UNIFIED_AI_JOBS.db "UPDATE job_discoveries SET applied=0, applied_date=NULL WHERE company='OpenAI'"

# Backup database
cp UNIFIED_AI_JOBS.db "backups/UNIFIED_AI_JOBS_$(date +%Y%m%d).db"
```

---

## 📋 Complete Command Reference

### Core Commands
| Command | Purpose | Frequency |
|---------|---------|-----------|
| `python run_automation.py` | Full automation cycle | 2x daily |
| `python job_discovery.py` | Find new AI/ML jobs | Daily |
| `python automated_apply.py --batch N` | Send N applications | As needed |
| `python generate_status_report.py` | View system status | Anytime |
| `python check_responses.py` | Check for replies | 2x daily |

### Utility Commands
| Command | Purpose |
|---------|---------|
| `python test_single_application.py` | Test one application |
| `python send_resume_followups.py` | Follow up with resumes |
| `python ats_ai_optimizer.py` | Regenerate resumes |
| `python improved_application_templates.py` | View templates |

### Database Queries
```bash
# Count total applications
sqlite3 UNIFIED_AI_JOBS.db "SELECT COUNT(*) FROM job_discoveries WHERE applied=1"

# View recent applications
sqlite3 UNIFIED_AI_JOBS.db "SELECT company, position, applied_date FROM job_discoveries WHERE applied=1 ORDER BY applied_date DESC LIMIT 10"

# Find high-value pending jobs
sqlite3 UNIFIED_AI_JOBS.db "SELECT company, position, salary_range FROM job_discoveries WHERE applied=0 AND relevance_score >= 0.7 ORDER BY salary_range DESC"

# Check application rate
sqlite3 UNIFIED_AI_JOBS.db "SELECT DATE(applied_date) as date, COUNT(*) as count FROM job_discoveries WHERE applied=1 GROUP BY date ORDER BY date DESC LIMIT 7"
```

---

## 🔄 Daily Workflow

### Morning (9:00 AM)
1. System automatically runs `run_automation.py`
2. Discovers 50-100 new jobs
3. Filters for relevance (AI/ML, remote, salary)
4. Applies to top 10-15 opportunities
5. Logs all activities

### Midday Check (Optional)
```bash
# Quick status check
python generate_status_report.py

# See if any responses came in
python check_responses.py
```

### Evening (6:00 PM)
1. System runs response checker
2. Sends follow-ups where appropriate
3. Generates daily summary
4. Prepares next day's targets

---

## 📊 Monitoring & Optimization

### Key Metrics to Track
```bash
# Weekly performance report
python -c "
import sqlite3
import datetime
conn = sqlite3.connect('UNIFIED_AI_JOBS.db')
cursor = conn.cursor()

# Applications sent this week
week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
cursor.execute('SELECT COUNT(*) FROM job_discoveries WHERE applied=1 AND applied_date > ?', (week_ago,))
print(f'Applications this week: {cursor.fetchone()[0]}')

# Response rate (you'll need to track this manually for now)
# Companies by application count
cursor.execute('SELECT company, COUNT(*) as count FROM job_discoveries WHERE applied=1 GROUP BY company ORDER BY count DESC LIMIT 10')
print('\nTop companies applied to:')
for company, count in cursor.fetchall():
    print(f'  {company}: {count}')
"
```

### Optimization Checklist
- [ ] Monitor which resume versions get responses
- [ ] Track which cover letter styles work best
- [ ] Note interview request patterns
- [ ] Adjust relevance scoring based on outcomes
- [ ] Update templates based on feedback

---

## 🚨 Troubleshooting

### Common Issues

#### Email Authentication Failed
```bash
# Test authentication
python test_bcc_auth.py

# If fails, regenerate app password:
# 1. Go to https://myaccount.google.com/apppasswords
# 2. Generate new password
# 3. Update .env file
```

#### No Jobs Found
```bash
# Check job discovery
python job_discovery.py

# Manually add job
python manual_job_add.py
```

#### Application Not Sending
```bash
# Check for errors
python test_single_application.py

# Reset job status
sqlite3 UNIFIED_AI_JOBS.db "UPDATE job_discoveries SET applied=0 WHERE id=123"
```

---

## ✅ System Health Checklist

### Daily Health Check
```bash
# Run this to verify system health
python -c "
import os
import json
from pathlib import Path

print('🏥 System Health Check')
print('=' * 40)

# Check database
db_exists = Path('UNIFIED_AI_JOBS.db').exists()
print(f'✅ Database exists: {db_exists}')

# Check resumes
resume_count = len(list(Path('resumes').glob('*.pdf')))
print(f'✅ Resume PDFs: {resume_count}')

# Check BCC log
if Path('data/bcc_tracking_log.json').exists():
    with open('data/bcc_tracking_log.json') as f:
        log = json.load(f)
        print(f'✅ Emails tracked: {len(log[\"sent_emails\"])}')

# Check environment
env_exists = Path('.env').exists()
print(f'✅ Environment configured: {env_exists}')

print('\\n✨ System ready!' if all([db_exists, resume_count, env_exists]) else '\\n⚠️  Issues found!')
"
```

---

## 🎯 Definition of "Done"

The system is complete when:

1. **Automatic Daily Operation** ✅
   - Runs at 9am and 6pm without intervention
   - Handles all errors gracefully
   - Logs all activities

2. **Quality Applications** ✅
   - Personalized cover letters
   - Appropriate resume selection
   - Professional formatting
   - No spam triggers

3. **Complete Tracking** ✅
   - Every email logged with BCC
   - Database tracks all applications
   - Response monitoring active
   - Clear audit trail

4. **Actionable Insights** ✅
   - Daily/weekly reports
   - Response rate tracking
   - Company preference learning
   - Template optimization data

5. **Easy Maintenance** ✅
   - One-command health check
   - Simple troubleshooting
   - Clear documentation
   - Backup procedures

---

## 🚀 Next Level Features (Future)

1. **Response AI**: Automatically draft interview responses
2. **Calendar Integration**: Auto-schedule interviews
3. **Market Intelligence**: Track hiring trends
4. **A/B Testing**: Automatically test templates
5. **Multi-Platform**: Expand beyond email applications

---

## 📞 Support Commands

```bash
# Generate full system diagnostic
python system_diagnostic.py

# Export all data
python export_all_data.py

# Reset to clean state (careful!)
python factory_reset.py --confirm
```

---

**Remember**: The goal is 10-20 quality applications daily with minimal manual work. Quality over quantity - personalized, professional, and persistent.

Last Updated: 2025-01-08