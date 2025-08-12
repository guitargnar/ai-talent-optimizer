#!/usr/bin/env python3
"""
Application Delivery Monitor
Continuously monitors for bounced emails and alerts on failures
"""

import imaplib
import email
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv("/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer/.env")


class DeliveryMonitor:
    """Monitor email delivery status"""
    
    def __init__(self):
        self.email_address = os.getenv("EMAIL_ADDRESS", "matthewdscott7@gmail.com")
        self.email_password = os.getenv("EMAIL_APP_PASSWORD", "")
        self.bounce_log = []
        self.load_bounce_log()
    
    def load_bounce_log(self):
        """Load previous bounce log"""
        try:
            with open('bounce_log.json', 'r') as f:
                self.bounce_log = json.load(f)
        except:
            self.bounce_log = []
    
    def save_bounce_log(self):
        """Save bounce log"""
        with open('bounce_log.json', 'w') as f:
            json.dump(self.bounce_log, f, indent=2)
    
    def check_for_bounces(self, hours_back=24):
        """Check for bounced emails in the last N hours"""
        
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.email_address, self.email_password)
            mail.select('inbox')
            
            # Search for bounce notifications
            date = (datetime.now() - timedelta(hours=hours_back)).strftime("%d-%b-%Y")
            _, messages = mail.search(None, f'(FROM "mailer-daemon" SINCE {date})')
            
            new_bounces = []
            
            if messages[0]:
                email_ids = messages[0].split()
                
                for email_id in email_ids:
                    _, msg = mail.fetch(email_id, '(RFC822)')
                    msg_data = email.message_from_bytes(msg[0][1])
                    
                    date_str = msg_data.get('Date', '')
                    
                    # Get body
                    body = ""
                    if msg_data.is_multipart():
                        for part in msg_data.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                                except:
                                    continue
                    else:
                        try:
                            body = msg_data.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            body = ""
                    
                    # Extract failed email
                    import re
                    email_match = re.search(r"wasn't delivered to ([^\s]+)", body)
                    if email_match:
                        failed_email = email_match.group(1)
                        
                        # Check if we've already logged this
                        if not any(b['email'] == failed_email and b['date'] == date_str 
                                 for b in self.bounce_log):
                            
                            bounce_info = {
                                'email': failed_email,
                                'date': date_str,
                                'timestamp': datetime.now().isoformat(),
                                'reason': self.extract_bounce_reason(body)
                            }
                            
                            new_bounces.append(bounce_info)
                            self.bounce_log.append(bounce_info)
            
            mail.logout()
            
            if new_bounces:
                self.alert_on_bounces(new_bounces)
                self.save_bounce_log()
            
            return new_bounces
            
        except Exception as e:
            print(f"Error checking bounces: {e}")
            return []
    
    def extract_bounce_reason(self, body):
        """Extract reason for bounce"""
        if "domain" in body and "couldn't be found" in body:
            return "Domain doesn't exist"
        elif "address couldn't be found" in body:
            return "Email address invalid"
        elif "mailbox is full" in body:
            return "Recipient mailbox full"
        elif "message size exceeds" in body:
            return "Message too large"
        else:
            return "Unknown bounce reason"
    
    def alert_on_bounces(self, bounces):
        """Alert when bounces are detected"""
        print("\n" + "="*60)
        print("🚨 DELIVERY FAILURE ALERT")
        print("="*60)
        print(f"\n{len(bounces)} new bounced email(s) detected!\n")
        
        for bounce in bounces:
            print(f"❌ Failed to deliver to: {bounce['email']}")
            print(f"   Reason: {bounce['reason']}")
            print(f"   Time: {bounce['date']}")
            print()
        
        print("ACTION REQUIRED: These applications did not reach the companies!")
        print("Please re-apply using alternative methods.")
    
    def get_delivery_stats(self):
        """Get delivery statistics"""
        total_bounces = len(self.bounce_log)
        
        # Group by domain
        domain_bounces = defaultdict(int)
        for bounce in self.bounce_log:
            domain = bounce['email'].split('@')[1] if '@' in bounce['email'] else 'unknown'
            domain_bounces[domain] += 1
        
        # Group by reason
        reason_counts = defaultdict(int)
        for bounce in self.bounce_log:
            reason_counts[bounce['reason']] += 1
        
        return {
            'total_bounces': total_bounces,
            'by_domain': dict(domain_bounces),
            'by_reason': dict(reason_counts),
            'recent_bounces': self.bounce_log[-10:]  # Last 10
        }
    
    def continuous_monitor(self, check_interval=3600):
        """Run continuous monitoring (default: check every hour)"""
        print("🔍 Starting continuous delivery monitoring...")
        print(f"Checking every {check_interval/60:.0f} minutes")
        print("Press Ctrl+C to stop\n")
        
        while True:
            try:
                # Check for bounces
                new_bounces = self.check_for_bounces(hours_back=2)
                
                if not new_bounces:
                    print(f"[{datetime.now().strftime('%H:%M')}] ✅ No new bounces detected")
                
                # Wait before next check
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n\nMonitoring stopped.")
                break
            except Exception as e:
                print(f"Error during monitoring: {e}")
                time.sleep(check_interval)


def main():
    """Run delivery monitor"""
    
    print("📧 APPLICATION DELIVERY MONITOR")
    print("="*60)
    
    monitor = DeliveryMonitor()
    
    print("\nOptions:")
    print("1. Check recent bounces (last 24 hours)")
    print("2. View delivery statistics")
    print("3. Start continuous monitoring")
    print("4. Export bounce log")
    
    choice = input("\nSelect option (1-4): ")
    
    if choice == '1':
        print("\n🔍 Checking for recent bounces...")
        bounces = monitor.check_for_bounces(hours_back=24)
        
        if not bounces:
            print("✅ No bounces in the last 24 hours")
        else:
            print(f"\n📊 Found {len(bounces)} bounced email(s)")
    
    elif choice == '2':
        stats = monitor.get_delivery_stats()
        print("\n📊 DELIVERY STATISTICS")
        print("="*60)
        print(f"Total Bounces Logged: {stats['total_bounces']}")
        
        print("\n❌ Bounces by Domain:")
        for domain, count in sorted(stats['by_domain'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {domain}: {count}")
        
        print("\n📋 Bounce Reasons:")
        for reason, count in stats['by_reason'].items():
            print(f"   {reason}: {count}")
    
    elif choice == '3':
        monitor.continuous_monitor()
    
    elif choice == '4':
        filename = f"bounce_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(monitor.bounce_log, f, indent=2)
        print(f"✅ Bounce log exported to {filename}")


if __name__ == "__main__":
    main()