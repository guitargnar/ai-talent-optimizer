#!/usr/bin/env python3
"""
Campaign Dashboard Generator for Project Ascent
Creates a live markdown dashboard showing campaign status
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

class DashboardGenerator:
    """Generate live dashboard for Project Ascent campaign"""
    
    def __init__(self, db_path: str = "unified_platform.db"):
        self.db_path = db_path
        self.dashboard_path = "campaign_dashboard.md"
    
    def get_campaign_stats(self) -> Dict:
        """Fetch current campaign statistics from database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Overall stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_outreach,
                SUM(response_received) as total_responses,
                SUM(interview_scheduled) as total_interviews
            FROM outreach_log
        """)
        overall = cursor.fetchone()
        stats['total_outreach'] = overall[0] or 0
        stats['total_responses'] = overall[1] or 0
        stats['total_interviews'] = overall[2] or 0
        
        # Today's stats
        today = datetime.now().date().isoformat()
        cursor.execute("""
            SELECT * FROM metrics WHERE date = ?
        """, (today,))
        today_data = cursor.fetchone()
        
        if today_data:
            stats['today_sent'] = today_data[1] or 0
            stats['today_responses'] = today_data[2] or 0
            stats['today_interviews'] = today_data[3] or 0
            stats['today_applications'] = today_data[4] or 0
        else:
            stats['today_sent'] = 0
            stats['today_responses'] = 0
            stats['today_interviews'] = 0
            stats['today_applications'] = 0
        
        # This week's stats
        week_start = (datetime.now() - timedelta(days=7)).date().isoformat()
        cursor.execute("""
            SELECT 
                SUM(messages_sent) as week_sent,
                SUM(responses_received) as week_responses,
                SUM(interviews_scheduled) as week_interviews,
                SUM(applications_submitted) as week_applications
            FROM metrics
            WHERE date >= ?
        """, (week_start,))
        week_data = cursor.fetchone()
        
        if week_data:
            stats['week_sent'] = week_data[0] or 0
            stats['week_responses'] = week_data[1] or 0
            stats['week_interviews'] = week_data[2] or 0
            stats['week_applications'] = week_data[3] or 0
        else:
            stats['week_sent'] = 0
            stats['week_responses'] = 0
            stats['week_interviews'] = 0
            stats['week_applications'] = 0
        
        # Calculate rates
        stats['response_rate'] = (stats['total_responses'] / stats['total_outreach'] * 100) if stats['total_outreach'] > 0 else 0
        stats['interview_rate'] = (stats['total_interviews'] / stats['total_outreach'] * 100) if stats['total_outreach'] > 0 else 0
        
        # Recent activity
        cursor.execute("""
            SELECT target_name, company, timestamp, response_received, interview_scheduled
            FROM outreach_log
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        stats['recent_activity'] = cursor.fetchall()
        
        # Tier breakdown
        cursor.execute("""
            SELECT tier, COUNT(*) as count, SUM(response_received) as responses
            FROM outreach_log
            GROUP BY tier
        """)
        stats['tier_breakdown'] = cursor.fetchall()
        
        conn.close()
        return stats
    
    def get_next_actions(self) -> List[str]:
        """Generate list of next actions based on campaign state"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        actions = []
        
        # Check for pending follow-ups
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM outreach_log
            WHERE response_received = 0 AND timestamp < ?
        """, (week_ago,))
        pending_followups = cursor.fetchone()[0]
        
        if pending_followups > 0:
            actions.append(f"📮 Send follow-up messages to {pending_followups} non-responders (7+ days old)")
        
        # Check today's outreach
        today = datetime.now().date().isoformat()
        cursor.execute("""
            SELECT messages_sent FROM metrics WHERE date = ?
        """, (today,))
        today_sent = cursor.fetchone()
        
        if not today_sent or today_sent[0] < 5:
            remaining = 5 - (today_sent[0] if today_sent else 0)
            actions.append(f"📤 Send {remaining} more outreach messages today (target: 5/day)")
        
        # Check for unscheduled interviews
        cursor.execute("""
            SELECT COUNT(*) FROM outreach_log
            WHERE response_received = 1 AND interview_scheduled = 0
        """)
        potential_interviews = cursor.fetchone()[0]
        
        if potential_interviews > 0:
            actions.append(f"📅 Follow up with {potential_interviews} positive responses to schedule interviews")
        
        # Weekly goals
        if datetime.now().weekday() == 0:  # Monday
            actions.append("📝 Update resume with any new achievements from last week")
            actions.append("🔗 Post weekly update on LinkedIn")
        
        if datetime.now().weekday() == 4:  # Friday
            actions.append("📊 Review weekly metrics and adjust strategy")
        
        # Always include
        actions.append("🔍 Research 3 new target companies")
        actions.append("💪 Continue working on AWS ML certification")
        
        conn.close()
        return actions
    
    def generate_dashboard(self) -> str:
        """Generate the full dashboard markdown"""
        
        stats = self.get_campaign_stats()
        actions = self.get_next_actions()
        
        dashboard = f"""# 🚀 PROJECT ASCENT - LIVE CAMPAIGN DASHBOARD

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---

## 📊 Campaign Overview

### 🎯 Goal: Secure $400K+ Principal AI/ML Role

**Campaign Day:** {(datetime.now() - datetime(2025, 1, 1)).days}  
**Target Timeline:** 60 days  
**Days Remaining:** {max(0, 60 - (datetime.now() - datetime(2025, 1, 1)).days)}

---

## 📈 Key Metrics

### Overall Performance
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Outreach | {stats['total_outreach']} | 150 | {"✅" if stats['total_outreach'] >= 150 else "🔄"} |
| Response Rate | {stats['response_rate']:.1f}% | 15% | {"✅" if stats['response_rate'] >= 15 else "⚠️"} |
| Interview Rate | {stats['interview_rate']:.1f}% | 10% | {"✅" if stats['interview_rate'] >= 10 else "⚠️"} |
| Interviews Scheduled | {stats['total_interviews']} | 5+ | {"✅" if stats['total_interviews'] >= 5 else "🔄"} |

### Today's Activity ({datetime.now().strftime('%Y-%m-%d')})
- **Messages Sent:** {stats['today_sent']}/5 {"✅" if stats['today_sent'] >= 5 else "⏳"}
- **Responses:** {stats['today_responses']}
- **Interviews:** {stats['today_interviews']}
- **Applications:** {stats['today_applications']}

### This Week's Progress
- **Messages:** {stats['week_sent']}/35 (target)
- **Responses:** {stats['week_responses']}
- **Interviews:** {stats['week_interviews']}
- **Applications:** {stats['week_applications']}

---

## 🎭 Tier Performance

| Tier | Outreach | Responses | Rate |
|------|----------|-----------|------|"""
        
        for tier, count, responses in stats['tier_breakdown']:
            rate = (responses/count*100) if count > 0 else 0
            dashboard += f"""
| {tier} | {count} | {responses or 0} | {rate:.1f}% |"""
        
        dashboard += f"""

---

## 📮 Recent Activity

| Date | Target | Company | Response | Interview |
|------|--------|---------|----------|-----------|"""
        
        for activity in stats['recent_activity'][:5]:
            date = datetime.fromisoformat(activity[2]).strftime('%m/%d')
            response = "✅" if activity[3] else "⏳"
            interview = "✅" if activity[4] else "-"
            dashboard += f"""
| {date} | {activity[0]} | {activity[1]} | {response} | {interview} |"""
        
        dashboard += f"""

---

## ✅ Next Actions

Priority tasks to maintain momentum:
"""
        
        for i, action in enumerate(actions, 1):
            dashboard += f"""
{i}. {action}"""
        
        dashboard += f"""

---

## 🏆 Achievements & Milestones

### Completed
- ✅ Master resume created with 3 variants
- ✅ Technical blog post published
- ✅ Portfolio documentation complete
- ✅ Networking templates prepared
- ✅ Campaign automation built

### In Progress
- 🔄 Daily outreach (5 messages/day)
- 🔄 AWS ML Certification study
- 🔄 Interview preparation
- 🔄 LinkedIn content creation

### Upcoming
- ⏳ First technical interview
- ⏳ Salary negotiation prep
- ⏳ Reference preparation

---

## 💡 Insights & Optimizations

Based on current data:"""
        
        # Generate insights
        if stats['response_rate'] < 10:
            dashboard += """
- ⚠️ **Low response rate** - Consider revising message templates or subject lines"""
        
        if stats['response_rate'] > 20:
            dashboard += """
- 🎉 **Excellent response rate** - Current messaging is resonating well!"""
        
        if stats['total_interviews'] > 0 and stats['total_responses'] > 0:
            interview_conversion = (stats['total_interviews'] / stats['total_responses'] * 100)
            if interview_conversion > 50:
                dashboard += """
- 🚀 **High interview conversion** - Your profile is compelling to respondents"""
        
        if stats['week_sent'] < 20:
            dashboard += """
- 📈 **Increase outreach volume** - Aim for 5+ messages daily to hit targets"""
        
        dashboard += f"""

---

## 📝 Notes & Reminders

- **Resume Variants**: Healthcare AI | Platform Engineering | AI Research
- **Blog Post**: [Orchestrating 78 Models in Production](https://medium.com/@matthewscott/orchestrating-78-models-production)
- **GitHub**: [PRIVATE REPO - Demo Available Upon Request]
- **Key Metrics**: $1.2M savings | 78 models | 99.9% uptime | HCL: 0.83

---

## 🎯 Success Criteria

- [{"✅" if stats['response_rate'] >= 15 else "⬜"}] Response rate ≥ 15%
- [{"✅" if stats['interview_rate'] >= 10 else "⬜"}] Interview rate ≥ 10%
- [{"✅" if stats['total_interviews'] >= 5 else "⬜"}] 5+ interviews scheduled
- [⬜] First offer received
- [⬜] $400K+ offer negotiated

---

*Remember: You're not job hunting - you're selecting which company gets to benefit from your $1.2M proven impact!*

**Keep pushing forward! Every action brings you closer to your $400K+ role! 🚀**
"""
        
        return dashboard
    
    def update_dashboard(self):
        """Update the dashboard file"""
        
        dashboard_content = self.generate_dashboard()
        
        with open(self.dashboard_path, 'w') as f:
            f.write(dashboard_content)
        
        print(f"✅ Dashboard updated: {self.dashboard_path}")
        return dashboard_content
    
    def print_dashboard(self):
        """Print dashboard to console"""
        
        dashboard = self.generate_dashboard()
        print(dashboard)


def main():
    """Main entry point for dashboard generator"""
    
    generator = DashboardGenerator()
    
    # Update and display dashboard
    generator.update_dashboard()
    generator.print_dashboard()
    
    print(f"\n📄 Dashboard saved to: campaign_dashboard.md")
    print("💡 Tip: Open campaign_dashboard.md in your editor for better formatting")


if __name__ == "__main__":
    main()