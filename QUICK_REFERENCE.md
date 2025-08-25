# ⚡ QUICK REFERENCE - AI Talent Optimizer

## 🎯 Essential Commands (Copy & Paste)

### Daily Use (In Order)
```bash
# 1. Navigate to project
cd ~/AI-ML-Portfolio/ai-talent-optimizer

# 2. Check status
python main.py status

# 3. Preview opportunities
python preview_applications.py

# 4. Send applications (choose one):
python guided_apply.py          # Interactive (recommended)
python send_batch_applications.py  # Automated batch

# 5. Verify sent
open "https://mail.google.com/mail/u/0/#sent"
```

---

## 🚀 One-Line Commands

### See What You'll Send (Safe)
```bash
cd ~/AI-ML-Portfolio/ai-talent-optimizer && python preview_applications.py
```

### Send One Application (Interactive)
```bash
cd ~/AI-ML-Portfolio/ai-talent-optimizer && python guided_apply.py
```

### Send Multiple (Batch)
```bash
cd ~/AI-ML-Portfolio/ai-talent-optimizer && python send_batch_applications.py
```

### Check Responses
```bash
cd ~/AI-ML-Portfolio/ai-talent-optimizer && python check_responses.py
```

---

## 📊 Expected Outputs Reference

### ✅ GOOD Status
```
📈 Database Statistics:
  • Total jobs: 345        <- Good! Have opportunities
  • Applications sent: 12   <- Working! Sending apps
  • Responses received: 0   <- Normal for first week
```

### ❌ BAD Status  
```
❌ Configuration Invalid   <- Run: python setup_email_smtp.py
Total jobs: 0            <- Run: python src/services/enhanced_job_scraper.py
```

---

*Quick Reference v3.1 | Updated: Aug 17, 2025*
