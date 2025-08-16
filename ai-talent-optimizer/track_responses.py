#!/usr/bin/env python3
"""
Response Tracker for Project Ascent
Monitors and analyzes campaign responses to optimize future outreach
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

class ResponseTracker:
    """Track and analyze responses to outreach campaigns"""
    
    def __init__(self, db_path: str = "campaign_tracking.db"):
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database tables exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add response tracking columns if they don't exist
        try:
            cursor.execute("""
                ALTER TABLE outreach_log 
                ADD COLUMN response_date TEXT
            """)
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("""
                ALTER TABLE outreach_log 
                ADD COLUMN response_sentiment TEXT
            """)
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("""
                ALTER TABLE outreach_log 
                ADD COLUMN response_content TEXT
            """)
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()
        conn.close()
    
    def record_response(
        self,
        target_name: str,
        company: str,
        response_type: str,
        sentiment: Optional[str] = None,
        content: Optional[str] = None,
        interview_scheduled: bool = False
    ) -> bool:
        """
        Record a response from an outreach target
        
        Args:
            target_name: Name of the person who responded
            company: Company name
            response_type: Type of response (positive, negative, neutral, auto-reply)
            sentiment: Optional sentiment analysis
            content: Optional response content summary
            interview_scheduled: Whether an interview was scheduled
            
        Returns:
            True if recorded successfully
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update the most recent outreach to this target
        cursor.execute("""
            UPDATE outreach_log 
            SET response_received = 1,
                response_date = ?,
                response_sentiment = ?,
                response_content = ?,
                interview_scheduled = ?
            WHERE target_name = ? AND company = ?
            AND id = (
                SELECT id FROM outreach_log 
                WHERE target_name = ? AND company = ?
                ORDER BY timestamp DESC LIMIT 1
            )
        """, (
            datetime.now().isoformat(),
            response_type,
            content,
            1 if interview_scheduled else 0,
            target_name,
            company,
            target_name,
            company
        ))
        
        # Update daily metrics
        if cursor.rowcount > 0:
            today = datetime.now().date().isoformat()
            cursor.execute("""
                UPDATE campaign_metrics 
                SET responses_received = responses_received + 1,
                    interviews_scheduled = interviews_scheduled + ?
                WHERE date = ?
            """, (1 if interview_scheduled else 0, today))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def get_response_analytics(self) -> Dict:
        """
        Analyze response patterns to optimize future outreach
        
        Returns:
            Dictionary with analytics insights
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall response rate
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sent,
                SUM(response_received) as total_responses,
                SUM(interview_scheduled) as total_interviews
            FROM outreach_log
        """)
        overall = cursor.fetchone()
        
        # Response rate by tier
        cursor.execute("""
            SELECT 
                tier,
                COUNT(*) as sent,
                SUM(response_received) as responses,
                SUM(interview_scheduled) as interviews
            FROM outreach_log
            GROUP BY tier
        """)
        by_tier = cursor.fetchall()
        
        # Response rate by company
        cursor.execute("""
            SELECT 
                company,
                COUNT(*) as sent,
                SUM(response_received) as responses,
                SUM(interview_scheduled) as interviews
            FROM outreach_log
            GROUP BY company
            ORDER BY responses DESC
            LIMIT 10
        """)
        by_company = cursor.fetchall()
        
        # Time to response analysis
        cursor.execute("""
            SELECT 
                AVG(julianday(response_date) - julianday(timestamp)) as avg_days_to_response
            FROM outreach_log
            WHERE response_received = 1 AND response_date IS NOT NULL
        """)
        avg_response_time = cursor.fetchone()[0]
        
        # Best performing message subjects
        cursor.execute("""
            SELECT 
                subject,
                COUNT(*) as sent,
                SUM(response_received) as responses,
                ROUND(CAST(SUM(response_received) AS FLOAT) / COUNT(*) * 100, 1) as response_rate
            FROM outreach_log
            GROUP BY subject
            HAVING sent >= 3
            ORDER BY response_rate DESC
            LIMIT 5
        """)
        best_subjects = cursor.fetchall()
        
        conn.close()
        
        analytics = {
            "overall": {
                "total_sent": overall[0] or 0,
                "total_responses": overall[1] or 0,
                "total_interviews": overall[2] or 0,
                "response_rate": f"{(overall[1]/overall[0]*100 if overall[0] else 0):.1f}%",
                "interview_rate": f"{(overall[2]/overall[0]*100 if overall[0] else 0):.1f}%"
            },
            "by_tier": {},
            "by_company": {},
            "avg_response_time_days": round(avg_response_time, 1) if avg_response_time else None,
            "best_performing_subjects": []
        }
        
        # Process tier data
        for tier, sent, responses, interviews in by_tier:
            analytics["by_tier"][tier] = {
                "sent": sent,
                "responses": responses or 0,
                "interviews": interviews or 0,
                "response_rate": f"{(responses/sent*100 if sent else 0):.1f}%"
            }
        
        # Process company data
        for company, sent, responses, interviews in by_company:
            analytics["by_company"][company] = {
                "sent": sent,
                "responses": responses or 0,
                "interviews": interviews or 0,
                "response_rate": f"{(responses/sent*100 if sent else 0):.1f}%"
            }
        
        # Process subject data
        for subject, sent, responses, rate in best_subjects:
            analytics["best_performing_subjects"].append({
                "subject": subject[:50] + "..." if len(subject) > 50 else subject,
                "sent": sent,
                "responses": responses or 0,
                "response_rate": f"{rate}%"
            })
        
        return analytics
    
    def get_follow_up_candidates(self, days_since: int = 7) -> List[Dict]:
        """
        Identify candidates for follow-up messages
        
        Args:
            days_since: Number of days since initial outreach
            
        Returns:
            List of targets needing follow-up
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_since)).isoformat()
        
        cursor.execute("""
            SELECT 
                target_name,
                company,
                tier,
                subject,
                timestamp
            FROM outreach_log
            WHERE response_received = 0
            AND timestamp < ?
            AND status != 'follow_up_sent'
            ORDER BY timestamp DESC
        """, (cutoff_date,))
        
        candidates = []
        for row in cursor.fetchall():
            candidates.append({
                "name": row[0],
                "company": row[1],
                "tier": row[2],
                "original_subject": row[3],
                "original_date": row[4],
                "days_since": (datetime.now() - datetime.fromisoformat(row[4])).days
            })
        
        conn.close()
        return candidates
    
    def generate_response_report(self) -> str:
        """Generate a comprehensive response analytics report"""
        
        analytics = self.get_response_analytics()
        follow_ups = self.get_follow_up_candidates()
        
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║              PROJECT ASCENT - RESPONSE ANALYTICS               ║
║                   {datetime.now().strftime('%Y-%m-%d %H:%M')}                        ║
╚════════════════════════════════════════════════════════════════╝

📊 OVERALL PERFORMANCE
─────────────────────────────────
Total Outreach:     {analytics['overall']['total_sent']}
Total Responses:    {analytics['overall']['total_responses']}
Total Interviews:   {analytics['overall']['total_interviews']}
Response Rate:      {analytics['overall']['response_rate']}
Interview Rate:     {analytics['overall']['interview_rate']}
Avg Response Time:  {analytics['avg_response_time_days'] or 'N/A'} days

📈 PERFORMANCE BY TIER
─────────────────────────────────"""
        
        for tier, data in analytics['by_tier'].items():
            report += f"""
{tier.upper()}:
  Sent: {data['sent']} | Responses: {data['responses']} | Rate: {data['response_rate']}
  Interviews: {data['interviews']}"""
        
        report += """

🏢 TOP RESPONDING COMPANIES
─────────────────────────────────"""
        
        for i, (company, data) in enumerate(list(analytics['by_company'].items())[:5], 1):
            report += f"""
{i}. {company}:
   Response Rate: {data['response_rate']} ({data['responses']}/{data['sent']})"""
        
        if analytics['best_performing_subjects']:
            report += """

📧 BEST PERFORMING SUBJECTS
─────────────────────────────────"""
            
            for i, subj in enumerate(analytics['best_performing_subjects'], 1):
                report += f"""
{i}. "{subj['subject']}"
   Response Rate: {subj['response_rate']} ({subj['responses']}/{subj['sent']})"""
        
        report += f"""

🔔 FOLLOW-UP NEEDED ({len(follow_ups)} targets)
─────────────────────────────────"""
        
        for i, candidate in enumerate(follow_ups[:5], 1):
            report += f"""
{i}. {candidate['name']} at {candidate['company']}
   Days since outreach: {candidate['days_since']}"""
        
        if len(follow_ups) > 5:
            report += f"\n   ... and {len(follow_ups) - 5} more"
        
        report += """

💡 OPTIMIZATION INSIGHTS
─────────────────────────────────"""
        
        # Generate insights based on data
        insights = []
        
        # Tier performance insight
        best_tier = max(analytics['by_tier'].items(), 
                       key=lambda x: float(x[1]['response_rate'].rstrip('%')))
        if best_tier[0]:
            insights.append(f"• {best_tier[0].upper()} has the best response rate at {best_tier[1]['response_rate']}")
        
        # Response time insight
        if analytics['avg_response_time_days']:
            if analytics['avg_response_time_days'] < 3:
                insights.append("• Fast response time suggests high engagement - keep momentum!")
            elif analytics['avg_response_time_days'] > 7:
                insights.append("• Slow responses - consider more urgent subject lines")
        
        # Follow-up insight
        if len(follow_ups) > 10:
            insights.append(f"• {len(follow_ups)} messages need follow-up - prioritize top targets")
        
        # Interview conversion insight
        if analytics['overall']['total_responses'] > 0:
            interview_conversion = (analytics['overall']['total_interviews'] / 
                                  analytics['overall']['total_responses'] * 100)
            if interview_conversion < 30:
                insights.append("• Low interview conversion - refine value proposition")
            elif interview_conversion > 50:
                insights.append("• Excellent interview conversion - scale up outreach!")
        
        for insight in insights:
            report += f"\n{insight}"
        
        report += """

🎯 RECOMMENDED ACTIONS
─────────────────────────────────
1. Send follow-ups to non-responders after 7 days
2. Double down on best-performing message templates
3. A/B test new subject lines for lower-performing tiers
4. Schedule interviews ASAP to maintain momentum
5. Update LinkedIn with any new achievements

Keep pushing! Every response brings you closer to $400K+ 🚀
"""
        
        return report
    
    def check_for_responses_manual(self):
        """
        Manual response checking interface
        (Placeholder for automated email/LinkedIn checking)
        """
        print("\n📬 MANUAL RESPONSE CHECKER")
        print("=" * 60)
        print("Enter any responses you've received:")
        print("(Type 'done' when finished)")
        print("-" * 60)
        
        while True:
            print("\nNew Response:")
            name = input("Contact Name (or 'done'): ").strip()
            
            if name.lower() == 'done':
                break
            
            company = input("Company: ").strip()
            response_type = input("Response Type (positive/negative/neutral/auto-reply): ").strip()
            interview = input("Interview scheduled? (y/n): ").strip().lower() == 'y'
            notes = input("Notes (optional): ").strip()
            
            success = self.record_response(
                name,
                company,
                response_type,
                sentiment=response_type,
                content=notes,
                interview_scheduled=interview
            )
            
            if success:
                print("✅ Response recorded successfully!")
            else:
                print("❌ Failed to record response")


def main():
    """Main entry point for response tracking"""
    
    tracker = ResponseTracker()
    
    while True:
        print("\n🎯 PROJECT ASCENT - RESPONSE TRACKER")
        print("=" * 60)
        print("1. Check for new responses (manual)")
        print("2. View response analytics")
        print("3. Get follow-up candidates")
        print("4. Generate full report")
        print("5. Exit")
        print("-" * 60)
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            tracker.check_for_responses_manual()
        elif choice == '2':
            analytics = tracker.get_response_analytics()
            print(json.dumps(analytics, indent=2))
        elif choice == '3':
            candidates = tracker.get_follow_up_candidates()
            print(f"\n📋 {len(candidates)} targets need follow-up:")
            for c in candidates[:10]:
                print(f"  • {c['name']} at {c['company']} ({c['days_since']} days)")
        elif choice == '4':
            report = tracker.generate_response_report()
            print(report)
            
            # Save report
            report_path = f"response_reports/response_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            import os
            os.makedirs("response_reports", exist_ok=True)
            with open(report_path, 'w') as f:
                f.write(report)
            print(f"\n📄 Report saved to: {report_path}")
        elif choice == '5':
            break
        else:
            print("Invalid option")
    
    print("\n👋 Response tracker closed")


if __name__ == "__main__":
    main()