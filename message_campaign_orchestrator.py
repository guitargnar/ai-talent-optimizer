#!/usr/bin/env python3
"""
Message Campaign Orchestrator - Runs personalized outreach campaigns at scale
Integrates with the Intelligent Messaging System to execute targeted campaigns
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path
from intelligent_messaging_system import (
    IntelligentMessagingSystem, 
    CompanyProfile, 
    MessageStyle, 
    OutreachChannel
)

class MessageCampaignOrchestrator:
    """Orchestrates multi-channel outreach campaigns with personalization"""
    
    def __init__(self):
        self.messaging_system = IntelligentMessagingSystem()
        self.campaign_db = Path("campaign_database.json")
        self.outreach_queue = Path("outreach_queue.csv")
        self.response_tracker = Path("response_tracker.csv")
        
        # Load campaign data
        self.campaigns = self._load_campaigns()
        self.daily_limits = {
            'linkedin': 20,
            'email': 30,
            'total': 40
        }
        
    def create_campaign(
        self,
        name: str,
        target_companies: List[Dict],
        campaign_type: str = 'mixed',  # 'ceo', 'recruiter', 'application', 'mixed'
        urgency: str = 'high'  # 'urgent', 'high', 'medium', 'low'
    ) -> str:
        """Create a new outreach campaign"""
        
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        campaign = {
            'id': campaign_id,
            'name': name,
            'created': datetime.now().isoformat(),
            'type': campaign_type,
            'urgency': urgency,
            'target_companies': target_companies,
            'status': 'active',
            'messages_sent': 0,
            'responses': 0,
            'interviews': 0,
            'offers': 0
        }
        
        self.campaigns[campaign_id] = campaign
        self._save_campaigns()
        
        print(f"✅ Created campaign: {name} ({campaign_id})")
        return campaign_id
    
    def execute_daily_campaigns(self):
        """Execute all active campaigns respecting daily limits"""
        
        print("""
╔══════════════════════════════════════════════════════════╗
║     EXECUTING DAILY OUTREACH CAMPAIGNS                    ║
╚══════════════════════════════════════════════════════════╝
        """)
        
        # Get active campaigns sorted by urgency
        active_campaigns = self._get_active_campaigns_by_priority()
        
        daily_messages = {
            'linkedin': 0,
            'email': 0,
            'total': 0
        }
        
        messages_sent = []
        
        for campaign in active_campaigns:
            if daily_messages['total'] >= self.daily_limits['total']:
                print(f"📊 Daily limit reached ({self.daily_limits['total']} messages)")
                break
            
            print(f"\n🎯 Executing campaign: {campaign['name']}")
            
            for target in campaign['target_companies']:
                if daily_messages['total'] >= self.daily_limits['total']:
                    break
                
                # Check if already contacted
                if self._already_contacted(target['name'], campaign['id']):
                    continue
                
                # Research company
                profile = self.messaging_system.research_company(
                    target['name'],
                    target.get('job_url')
                )
                
                # Determine best channel based on campaign type
                channel = self._determine_channel(campaign['type'], daily_messages)
                
                if not channel:
                    continue
                
                # Generate personalized message
                message_data = self.messaging_system.create_message(
                    profile,
                    channel,
                    style=self._determine_style(profile, campaign['type'])
                )
                
                # "Send" message (log it)
                self._send_message(message_data, campaign, target)
                
                # Update counters
                daily_messages[channel.value] += 1
                daily_messages['total'] += 1
                messages_sent.append(message_data)
                
                # Rate limiting
                time.sleep(2)  # Avoid overwhelming APIs
                
                print(f"   ✉️ Sent {channel.value} to {target['name']} (Score: {message_data['personalization_score']:.0f}%)")
        
        # Generate daily report
        self._generate_daily_report(messages_sent, daily_messages)
        
        return messages_sent
    
    def load_company_intel_from_csv(self, csv_path: str):
        """Load company intelligence from your CSV trackers"""
        
        df = pd.read_csv(csv_path)
        companies = []
        
        for _, row in df.iterrows():
            if row.get('Status') in ['TODO', 'PENDING']:
                company = {
                    'name': row.get('Item', row.get('Company', '')),
                    'contact': row.get('Contact', ''),
                    'role': row.get('Target', row.get('Position', 'Principal Engineer')),
                    'compensation': row.get('Value/Comp', '$400K+'),
                    'priority': row.get('Priority', 'MEDIUM'),
                    'notes': row.get('Notes', ''),
                    'job_url': row.get('URL', '')
                }
                companies.append(company)
        
        return companies
    
    def create_targeted_campaign_from_tracker(self):
        """Create campaigns directly from your CSV tracker"""
        
        # Load high-priority targets from tracker
        tracker_path = "MASTER_TRACKER_400K.csv"
        companies = self.load_company_intel_from_csv(tracker_path)
        
        # Group by priority
        urgent_companies = [c for c in companies if c['priority'] in ['URGENT', 'HIGHEST']]
        high_companies = [c for c in companies if c['priority'] == 'HIGH']
        medium_companies = [c for c in companies if c['priority'] == 'MEDIUM']
        
        campaigns_created = []
        
        # Create urgent campaign
        if urgent_companies:
            campaign_id = self.create_campaign(
                name="URGENT - Abridge & Tempus Blitz",
                target_companies=urgent_companies[:10],
                campaign_type='mixed',
                urgency='urgent'
            )
            campaigns_created.append(campaign_id)
        
        # Create high priority campaign
        if high_companies:
            campaign_id = self.create_campaign(
                name="HIGH - Fortune 500 Principal Roles",
                target_companies=high_companies[:10],
                campaign_type='application',
                urgency='high'
            )
            campaigns_created.append(campaign_id)
        
        # Create CEO outreach campaign
        ceo_targets = [c for c in companies if 'CEO' in c.get('contact', '')]
        if ceo_targets:
            campaign_id = self.create_campaign(
                name="CEO Direct - Fractional CTO Pitches",
                target_companies=ceo_targets[:5],
                campaign_type='ceo',
                urgency='high'
            )
            campaigns_created.append(campaign_id)
        
        print(f"\n✅ Created {len(campaigns_created)} campaigns from tracker")
        return campaigns_created
    
    def _determine_channel(self, campaign_type: str, daily_messages: Dict) -> Optional[OutreachChannel]:
        """Determine best channel based on campaign type and limits"""
        
        if campaign_type == 'ceo':
            if daily_messages['linkedin'] < self.daily_limits['linkedin']:
                return OutreachChannel.LINKEDIN
            elif daily_messages['email'] < self.daily_limits['email']:
                return OutreachChannel.EMAIL
        elif campaign_type == 'application':
            return OutreachChannel.APPLICATION_COVER
        elif campaign_type == 'recruiter':
            if daily_messages['email'] < self.daily_limits['email']:
                return OutreachChannel.EMAIL
            elif daily_messages['linkedin'] < self.daily_limits['linkedin']:
                return OutreachChannel.LINKEDIN
        else:  # mixed
            # Alternate between channels
            if daily_messages['linkedin'] <= daily_messages['email']:
                if daily_messages['linkedin'] < self.daily_limits['linkedin']:
                    return OutreachChannel.LINKEDIN
            if daily_messages['email'] < self.daily_limits['email']:
                return OutreachChannel.EMAIL
        
        return None
    
    def _determine_style(self, profile: CompanyProfile, campaign_type: str) -> MessageStyle:
        """Determine message style based on campaign and company"""
        
        if campaign_type == 'ceo':
            if profile.size == 'startup':
                return MessageStyle.STARTUP_CASUAL
            else:
                return MessageStyle.VISIONARY_STRATEGIC
        elif campaign_type == 'recruiter':
            return MessageStyle.DATA_DRIVEN
        elif campaign_type == 'application':
            if profile.size == 'enterprise':
                return MessageStyle.FORMAL_ENTERPRISE
            else:
                return MessageStyle.TECHNICAL_DETAILED
        else:
            # Let the messaging system auto-detect
            return self.messaging_system._determine_best_style(profile)
    
    def _send_message(self, message_data: Dict, campaign: Dict, target: Dict):
        """Log sent message and update campaign stats"""
        
        # Save message to file
        output_dir = Path("campaign_messages") / campaign['id']
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{target['name']}_{message_data['channel']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_dir / filename, 'w') as f:
            if message_data.get('subject'):
                f.write(f"Subject: {message_data['subject']}\n\n")
            f.write(message_data['message'])
        
        # Log to outreach queue
        outreach_entry = {
            'timestamp': datetime.now().isoformat(),
            'campaign_id': campaign['id'],
            'company': target['name'],
            'contact': target.get('contact', ''),
            'channel': message_data['channel'],
            'style': message_data['style'],
            'personalization_score': message_data['personalization_score'],
            'status': 'sent',
            'follow_up_date': (datetime.now() + timedelta(days=3)).isoformat()
        }
        
        df = pd.DataFrame([outreach_entry])
        if self.outreach_queue.exists():
            df.to_csv(self.outreach_queue, mode='a', header=False, index=False)
        else:
            df.to_csv(self.outreach_queue, index=False)
        
        # Update campaign stats
        campaign['messages_sent'] += 1
        self._save_campaigns()
    
    def _already_contacted(self, company: str, campaign_id: str) -> bool:
        """Check if company already contacted in this campaign"""
        
        if not self.outreach_queue.exists():
            return False
        
        df = pd.read_csv(self.outreach_queue)
        contacted = df[(df['company'] == company) & (df['campaign_id'] == campaign_id)]
        return len(contacted) > 0
    
    def _get_active_campaigns_by_priority(self) -> List[Dict]:
        """Get active campaigns sorted by urgency"""
        
        urgency_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
        
        active = [c for c in self.campaigns.values() if c['status'] == 'active']
        active.sort(key=lambda x: urgency_order.get(x['urgency'], 99))
        
        return active
    
    def _generate_daily_report(self, messages_sent: List[Dict], daily_totals: Dict):
        """Generate daily campaign report"""
        
        report = f"""
📊 DAILY CAMPAIGN REPORT - {datetime.now().strftime('%Y-%m-%d')}
{'='*60}

MESSAGES SENT:
- LinkedIn: {daily_totals['linkedin']}
- Email: {daily_totals['email']}
- Total: {daily_totals['total']}

PERSONALIZATION SCORES:
"""
        
        if messages_sent:
            scores = [m['personalization_score'] for m in messages_sent]
            report += f"- Average: {sum(scores)/len(scores):.1f}%\n"
            report += f"- Highest: {max(scores):.1f}%\n"
            report += f"- Lowest: {min(scores):.1f}%\n"
        
        report += f"\nTOP PERSONALIZED MESSAGES:\n"
        top_messages = sorted(messages_sent, key=lambda x: x['personalization_score'], reverse=True)[:3]
        for msg in top_messages:
            report += f"- {msg['company']}: {msg['personalization_score']:.0f}% ({msg['channel']})\n"
        
        report += f"\nCAMPAIGN PERFORMANCE:\n"
        for campaign in self.campaigns.values():
            if campaign['status'] == 'active':
                response_rate = (campaign['responses'] / campaign['messages_sent'] * 100) if campaign['messages_sent'] > 0 else 0
                report += f"- {campaign['name']}: {campaign['messages_sent']} sent, {response_rate:.1f}% response rate\n"
        
        # Save report
        report_path = Path("campaign_reports") / f"report_{datetime.now().strftime('%Y%m%d')}.txt"
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(report)
        return report
    
    def track_response(self, company: str, responded: bool, 
                      response_quality: str = None, next_step: str = None):
        """Track responses to messages"""
        
        # Update messaging system's tracking
        self.messaging_system.track_response(company, responded)
        
        # Find the campaign
        if self.outreach_queue.exists():
            df = pd.read_csv(self.outreach_queue)
            company_rows = df[df['company'] == company]
            
            if not company_rows.empty:
                campaign_id = company_rows.iloc[-1]['campaign_id']
                
                # Update campaign stats
                if campaign_id in self.campaigns:
                    campaign = self.campaigns[campaign_id]
                    if responded:
                        campaign['responses'] += 1
                    if next_step == 'interview':
                        campaign['interviews'] += 1
                    if next_step == 'offer':
                        campaign['offers'] += 1
                    self._save_campaigns()
        
        # Log response
        response_entry = {
            'timestamp': datetime.now().isoformat(),
            'company': company,
            'responded': responded,
            'response_quality': response_quality,
            'next_step': next_step
        }
        
        df = pd.DataFrame([response_entry])
        if self.response_tracker.exists():
            df.to_csv(self.response_tracker, mode='a', header=False, index=False)
        else:
            df.to_csv(self.response_tracker, index=False)
    
    def get_follow_up_queue(self) -> List[Dict]:
        """Get companies that need follow-up"""
        
        if not self.outreach_queue.exists():
            return []
        
        df = pd.read_csv(self.outreach_queue)
        df['follow_up_date'] = pd.to_datetime(df['follow_up_date'])
        
        # Get messages that need follow-up
        today = datetime.now()
        needs_followup = df[
            (df['follow_up_date'] <= today) & 
            (df['status'] == 'sent')
        ]
        
        follow_ups = []
        for _, row in needs_followup.iterrows():
            # Check if already responded
            if self.response_tracker.exists():
                responses = pd.read_csv(self.response_tracker)
                if row['company'] in responses['company'].values:
                    continue
            
            follow_ups.append({
                'company': row['company'],
                'original_sent': row['timestamp'],
                'channel': row['channel'],
                'campaign_id': row['campaign_id']
            })
        
        return follow_ups
    
    def execute_follow_ups(self):
        """Execute follow-up messages"""
        
        follow_ups = self.get_follow_up_queue()
        
        if not follow_ups:
            print("No follow-ups needed today")
            return
        
        print(f"\n📮 Executing {len(follow_ups)} follow-ups...")
        
        for follow_up in follow_ups:
            # Get company profile
            profile = self.messaging_system.research_company(follow_up['company'])
            
            # Create follow-up message
            follow_up_template = f"""Hi {profile.ceo_name.split()[0] if profile.ceo_name else 'there'},

Following up on my message from {follow_up['original_sent'][:10]} about opportunities at {profile.name}.

I understand you're incredibly busy. If there's a better person on your team to discuss {profile.target_role} opportunities, I'd appreciate the connection.

My experience delivering $1.2M in savings at Humana could directly benefit {profile.name}'s growth.

Best,
Matthew"""
            
            # Save follow-up
            output_dir = Path("campaign_messages") / "follow_ups"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{follow_up['company']}_followup_{datetime.now().strftime('%Y%m%d')}.txt"
            with open(output_dir / filename, 'w') as f:
                f.write(follow_up_template)
            
            print(f"   📤 Follow-up ready for {follow_up['company']}")
            
            # Update status
            df = pd.read_csv(self.outreach_queue)
            df.loc[df['company'] == follow_up['company'], 'status'] = 'followed_up'
            df.to_csv(self.outreach_queue, index=False)
    
    def _load_campaigns(self) -> Dict:
        """Load campaigns from database"""
        if self.campaign_db.exists():
            with open(self.campaign_db, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_campaigns(self):
        """Save campaigns to database"""
        with open(self.campaign_db, 'w') as f:
            json.dump(self.campaigns, f, indent=2)
    
    def get_campaign_analytics(self) -> str:
        """Generate comprehensive campaign analytics"""
        
        report = """
📈 CAMPAIGN ANALYTICS DASHBOARD
════════════════════════════════════════════════════════════
"""
        
        total_sent = sum(c['messages_sent'] for c in self.campaigns.values())
        total_responses = sum(c['responses'] for c in self.campaigns.values())
        total_interviews = sum(c['interviews'] for c in self.campaigns.values())
        total_offers = sum(c['offers'] for c in self.campaigns.values())
        
        report += f"""
OVERALL METRICS:
- Messages Sent: {total_sent}
- Responses: {total_responses} ({total_responses/total_sent*100:.1f}% rate)
- Interviews: {total_interviews} ({total_interviews/total_sent*100:.1f}% conversion)
- Offers: {total_offers} ({total_offers/total_sent*100:.1f}% conversion)

CAMPAIGN BREAKDOWN:
"""
        
        for campaign in sorted(self.campaigns.values(), 
                              key=lambda x: x['responses']/x['messages_sent'] if x['messages_sent'] > 0 else 0,
                              reverse=True):
            
            response_rate = (campaign['responses'] / campaign['messages_sent'] * 100) if campaign['messages_sent'] > 0 else 0
            
            report += f"""
{campaign['name']}:
  Status: {campaign['status']}
  Urgency: {campaign['urgency']}
  Sent: {campaign['messages_sent']}
  Response Rate: {response_rate:.1f}%
  Interviews: {campaign['interviews']}
  Offers: {campaign['offers']}
"""
        
        # Channel effectiveness
        if self.outreach_queue.exists():
            df = pd.read_csv(self.outreach_queue)
            channel_stats = df.groupby('channel').size()
            
            report += "\nCHANNEL DISTRIBUTION:\n"
            for channel, count in channel_stats.items():
                report += f"- {channel}: {count} messages\n"
        
        return report


def main():
    """Demo the campaign orchestrator"""
    
    orchestrator = MessageCampaignOrchestrator()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║     MESSAGE CAMPAIGN ORCHESTRATOR                         ║
║     Automated, Personalized, Tracked                      ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Create campaigns from your CSV tracker
    print("\n1️⃣ Creating campaigns from tracker...")
    campaigns = orchestrator.create_targeted_campaign_from_tracker()
    
    # Execute daily campaigns
    print("\n2️⃣ Executing daily campaigns...")
    messages = orchestrator.execute_daily_campaigns()
    
    # Check for follow-ups
    print("\n3️⃣ Checking for follow-ups...")
    orchestrator.execute_follow_ups()
    
    # Show analytics
    print("\n4️⃣ Campaign Analytics:")
    print(orchestrator.get_campaign_analytics())
    
    print("\n✅ Campaign orchestration complete!")
    print(f"📁 Messages saved to: campaign_messages/")
    print(f"📊 Reports saved to: campaign_reports/")
    
    return orchestrator


if __name__ == "__main__":
    orchestrator = main()