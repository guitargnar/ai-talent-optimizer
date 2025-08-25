# 🎯 AI Job Hunter - Quick Command Reference

Copy and paste these commands directly into your terminal.

## 📍 Navigate to Project
```bash
cd ~/AI-ML-Portfolio/ai-talent-optimizer
```

## 🚀 Essential Daily Commands

### Morning Routine (Run Once)
```bash
# Run complete automation (discovers jobs + applies)
python run_automation.py
```

### Check Status (Anytime)
```bash
# See what's been done today
python generate_status_report.py
```

### Manual Application Batch
```bash
# Apply to 5 more jobs
python automated_apply.py --batch 5
```

### Evening Check
```bash
# Check for responses (implement based on your email setup)
python check_responses.py
```

## 📊 Quick Database Checks

### See Recent Applications
```bash
sqlite3 UNIFIED_AI_JOBS.db "SELECT company, position, applied_date FROM job_discoveries WHERE applied=1 ORDER BY applied_date DESC LIMIT 10"
```

### Count Today's Applications
```bash
sqlite3 UNIFIED_AI_JOBS.db "SELECT COUNT(*) FROM job_discoveries WHERE applied=1 AND DATE(applied_date) = DATE('now')"
```

### Find Best Unapplied Jobs
```bash
sqlite3 UNIFIED_AI_JOBS.db "SELECT company, position, salary_range FROM job_discoveries WHERE applied=0 ORDER BY relevance_score DESC LIMIT 10"
```

## 🔧 Quick Fixes

### Test Email System
```bash
python test_bcc_auth.py
```

### Regenerate Resumes (if needed)
```bash
python ats_ai_optimizer.py && python resume_pdf_generator.py
```

### View Email Log
```bash
cat data/bcc_tracking_log.json | python -m json.tool | less
```

## 🏃 One-Liner Status Check
```bash
echo "📊 Today's Activity:" && sqlite3 UNIFIED_AI_JOBS.db "SELECT COUNT(*) || ' applications sent' FROM job_discoveries WHERE applied=1 AND DATE(applied_date) = DATE('now')" && echo "📧 Total sent:" && sqlite3 UNIFIED_AI_JOBS.db "SELECT COUNT(*) FROM job_discoveries WHERE applied=1"
```

## ⏰ Start/Stop Automation
```bash
# Start daily automation
launchctl load ~/Library/LaunchAgents/com.ai.jobhunter.*.plist

# Stop daily automation  
launchctl unload ~/Library/LaunchAgents/com.ai.jobhunter.*.plist
```

---
💡 **Pro Tip**: Save this file somewhere handy or bookmark it for quick access!