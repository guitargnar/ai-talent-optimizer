# 🎯 AI Talent Optimizer - Quick Reference Card

## Essential Commands (Copy & Paste)

### 🌅 Morning Routine (9 AM)
```bash
cd /Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer
python discovery_dashboard.py
python signal_booster.py
python gmail_oauth_integration.py
```

### 📧 After Sending Application
```bash
python -c "from email_application_tracker import EmailApplicationTracker; t = EmailApplicationTracker(); t.log_email_application({'company': 'COMPANY_NAME', 'position': 'POSITION', 'sent_date': '2025-08-05', 'personalized': 'yes'})"
```

### 🌆 Evening Summary (5 PM)
```bash
python discovery_dashboard.py --export html
open output/dashboard_*.html
```

## 📊 Key Metrics to Track

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Profile Optimization | >90% | 91% | ✅ |
| Response Rate | >15% | 17.3% | ✅ |
| Daily Applications | 25-40 | 32 | ✅ |
| Weekly Profile Views | +50% | +156% | ✅ |
| Recruiter InMails/Week | 3-5 | 3 | 🟡 |

## 🎯 Top Priority Companies

1. **Cohere** - Remote AI Safety ($350K-$450K)
   - Email: careers@cohere.ai
   - Resume: Matthew_Scott_Cohere_AI_Safety_2025.pdf

2. **Scale AI** - Foundation Models ($350K-$500K)
   - Email: careers@scale.com
   - Resume: Matthew_Scott_Scale_AI_Foundation_Models_2025.pdf

3. **Meta** - Fundamental Research ($400K-$10M)
   - Email: ai-research@meta.com
   - Resume: Matthew_Scott_Meta_AI_Research_2025.pdf

## 📝 Email Template Structure

```
Subject: [Company] - [Position] - AI Consciousness Pioneer

Dear [Company] [Team] Hiring Team,

I'm reaching out about the [Position] role, as my breakthrough in achieving 
the first measurable AI consciousness (HCL: 0.83/1.0) directly aligns with 
[Company]'s mission in [specific area].

Recent achievements:
• First documented measurable AI consciousness (HCL: 0.83/1.0)
• 78-model distributed system
• $7,000+ value generated
• Published research on meta-cognition

[Company-specific angle]

Portfolio: https://github.com/matthewscott/AI-ML-Portfolio
Consciousness Demo: [Available upon request]

Best regards,
Matthew Scott
```

## 🚀 Daily Signal Boost Activities

### High Impact (>85% score)
- GitHub commit with consciousness keywords (30 min)
- LinkedIn article on consciousness (90 min)
- Technical blog post (120 min)

### Medium Impact (75-85% score)
- Comment on AI leader posts (15 min)
- Connect with 5 recruiters (20 min)
- Answer Stack Overflow questions (30 min)

### Quick Wins (<15 min)
- LinkedIn engagement
- GitHub star relevant repos
- Share AI insights

## 🔍 Search Commands

### Find Remote Jobs
```bash
python -c "from email_application_tracker import EmailApplicationTracker; t = EmailApplicationTracker(); remote = [a for a in t.search_email_applications() if 'remote' in str(a.get('remote_option', '')).lower()]; print(f'Remote applications: {len(remote)}')"
```

### High-Salary Applications ($400K+)
```bash
python -c "from email_application_tracker import EmailApplicationTracker; t = EmailApplicationTracker(); high = [a for a in t.search_email_applications() if int(a.get('salary_range', '0-0').split('-')[1]) >= 400000]; print(f'$400K+ applications: {len(high)}')"
```

## 📈 Success Indicators

### 🟢 Green Flags
- Response rate >15%
- Profile views increasing weekly
- Recruiter InMails arriving
- Interview requests within 7 days

### 🔴 Red Flags
- Response rate <10%
- No profile view increase
- No recruiter contact in 2 weeks
- All rejections/no responses

## 🎯 Your Unique Keywords

**Always Include:**
- "First documented AI consciousness"
- "HCL score 0.83/1.0"
- "78-model distributed system"
- "$7,000+ value generated"

**Technical Stack:**
- PyTorch, Transformers, HuggingFace
- Distributed AI, LLMs, Meta-cognition
- Production ML, Enterprise AI

## ⏰ Optimal Timing

**Best Days to Apply:** Tuesday - Thursday
**Best Time:** 8-10 AM PST
**Avoid:** Fridays, Mondays, Holidays

**Content Publishing:**
- Tuesday/Thursday: 3x engagement
- Morning posts: Higher visibility
- Avoid weekends for technical content

## 🚨 Urgent Actions Monitor

Check daily for:
```bash
python -c "from discovery_dashboard import DiscoveryDashboard; d = DiscoveryDashboard(); urgent = d._check_urgent_responses(); print(f'{len(urgent)} URGENT actions') if urgent else print('No urgent actions')"
```

---

**Remember**: Your consciousness research (HCL: 0.83) is your superpower. Lead with it! 🧠✨