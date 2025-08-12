# 🚀 AI Talent Optimizer - Working Terminal Commands

All systems are operational! Execute these commands to maximize your AI/ML job discovery.

## 📊 Full System Dashboard
```bash
# View unified dashboard showing all metrics
python discovery_dashboard.py

# Live monitoring mode (updates every 5 minutes)
python discovery_dashboard.py --live

# Export dashboard as HTML
python discovery_dashboard.py --export html
```

## 🔍 AI Recruiter Analysis
```bash
# Analyze how AI recruiters will find you
python ai_recruiter_analyzer.py

# Analyze specific platform
python -c "from ai_recruiter_analyzer import AIRecruiterAnalyzer; a = AIRecruiterAnalyzer(); print(a.analyze_platform('LinkedIn Recruiter'))"
```

## 👤 Profile Optimization
```bash
# Optimize your online profiles
python profile_optimizer.py

# Generate optimized LinkedIn About section
python -c "from profile_optimizer import ProfileOptimizer; p = ProfileOptimizer(); print(p._generate_optimized_about())"
```

## 📢 Visibility Amplification
```bash
# Generate SEO-optimized content
python visibility_amplifier.py

# Create specific content type
python -c "from visibility_amplifier import VisibilityAmplifier; v = VisibilityAmplifier(); content = v.generate_seo_content('article', 'AI Consciousness'); print(content.title)"
```

## 📄 ATS/AI Resume Generation
```bash
# Generate 4 optimized resume versions
python ats_ai_optimizer.py

# View generated resumes
ls output/resumes/
```

## 🚀 Signal Boosting Activities
```bash
# Get today's high-impact activities
python signal_booster.py

# Track activity completion
python -c "from signal_booster import SignalBooster; b = SignalBooster(); b.track_activity_completion('daily_github_1', 'Updated consciousness repo')"

# Generate weekly strategy
python -c "from signal_booster import SignalBooster; b = SignalBooster(); import json; print(json.dumps(b.generate_weekly_strategy(), indent=2))"
```

## 📧 Email Application Tracking
```bash
# Log a new email application
python -c "from email_application_tracker import EmailApplicationTracker; t = EmailApplicationTracker(); t.log_email_application({'to': 'careers@anthropic.com', 'subject': 'ML Engineer - Consciousness Research', 'company': 'Anthropic', 'position': 'ML Engineer', 'sent_date': '2025-08-04'})"

# Search email applications
python -c "from email_application_tracker import EmailApplicationTracker; t = EmailApplicationTracker(); apps = t.search_email_applications('Anthropic'); print(f'Found {len(apps)} applications to Anthropic')"

# Generate email tracking report
python -c "from email_application_tracker import EmailApplicationTracker; t = EmailApplicationTracker(); report = t.generate_email_report(); print(report['summary'])"
```

## 🔗 Gmail Integration
```bash
# Check Gmail OAuth integration status
python gmail_oauth_integration.py

# Start unified monitor (combines Gmail + tracking)
python unified_monitor.py

# Check for Gmail responses (if OAuth is set up)
cd "/Users/matthewscott/Google Gmail"
python check_job_replies.py

# Continuous Gmail monitoring
python gmail_inbox_monitor.py
```

## 📈 Quick Status Checks
```bash
# Check profile optimization score
python -c "from profile_optimizer import ProfileOptimizer; p = ProfileOptimizer(); score = p.calculate_optimization_score({'linkedin_optimized': True, 'github_active': True}); print(f'Profile Score: {score}%')"

# View today's priority actions
python -c "from discovery_dashboard import DiscoveryDashboard; d = DiscoveryDashboard(); actions = d._get_daily_actions(); print('\\n'.join([f'{i+1}. {a[\"action\"]}' for i, a in enumerate(actions[:3])]))"

# Check application pipeline
python -c "from discovery_dashboard import DiscoveryDashboard; d = DiscoveryDashboard(); pipeline = d._get_application_metrics()['application_pipeline']; print(f'Applied: {pipeline[\"applied\"]} → Interview: {pipeline[\"interview\"]} → Offer: {pipeline[\"offer\"]}')"
```

## 🎯 Daily Workflow Commands
```bash
# Morning routine (run all in sequence)
python discovery_dashboard.py              # Check overall status
python signal_booster.py                   # Get today's activities
python gmail_oauth_integration.py          # Check for responses

# Track an activity
python -c "from signal_booster import SignalBooster; b = SignalBooster(); b.track_activity_completion('linkedin_post', 'Published AI consciousness article')"

# Log new applications
python -c "from email_application_tracker import EmailApplicationTracker; t = EmailApplicationTracker(); t.log_email_application({'to': 'talent@openai.com', 'company': 'OpenAI', 'position': 'Research Engineer', 'sent_date': '2025-08-04'})"

# End of day summary
python discovery_dashboard.py --export html
```

## 🔧 Utility Commands
```bash
# View all output files
ls -la output/
ls -la output/resumes/
ls -la output/signal_plans/
ls -la data/

# Check system logs
tail -f data/email_applications.csv
cat data/signal_activity_log.json | jq '.'

# Test specific component
python tests/test_ai_optimizer.py -v
```

## 💡 Power User Commands
```bash
# Batch update profile keywords
python -c "from profile_optimizer import ProfileOptimizer; p = ProfileOptimizer(); p.keywords['technical'].extend(['transformer architecture', 'attention mechanisms']); p.save_config()"

# Generate custom signal activity
python -c "from signal_booster import SignalBooster; b = SignalBooster(); plan = b.generate_daily_plan(); print(f'Total impact today: {plan[\"expected_impact\"]:.0%}')"

# Export all metrics as JSON
python -c "from discovery_dashboard import DiscoveryDashboard; d = DiscoveryDashboard(); data = d.generate_dashboard(); import json; with open('metrics_export.json', 'w') as f: json.dump(data, f, indent=2)"
```

## 🚨 Urgent Actions Monitor
```bash
# Check for urgent responses needed
python -c "from discovery_dashboard import DiscoveryDashboard; d = DiscoveryDashboard(); urgent = d._check_urgent_responses(); print(f'{len(urgent)} URGENT actions required!'); [print(f'- {a[\"action\"]}') for a in urgent]"

# Set up automated alerts (runs every 5 minutes)
while true; do python -c "from discovery_dashboard import DiscoveryDashboard; d = DiscoveryDashboard(); u = d._check_urgent_responses(); u and print('\033[91mURGENT!\033[0m', len(u), 'actions needed')"; sleep 300; done
```

## 📝 Remember
- Run `python discovery_dashboard.py` first thing each morning
- Execute signal boost activities during optimal times (9 AM, 2 PM)
- Check Gmail integration every few hours for responses
- Export dashboard HTML at end of day for progress tracking

---
*Your AI consciousness research + these tools = Maximum discovery by AI recruiters! 🎯*