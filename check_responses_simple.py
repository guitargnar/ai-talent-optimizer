#!/usr/bin/env python3
"""
Simple Response Checker - Uses existing Gmail integration
"""

from gmail_app_password_integration import GmailAppPasswordIntegration
import sqlite3
import json
from datetime import datetime
from pathlib import Path

def main():
    print("📧 Checking for job application responses...")
    
    # Initialize Gmail checker
    gmail = GmailAppPasswordIntegration()
    
    try:
        # Connect to Gmail
        gmail.connect()
        
        # Search for responses (last 7 days)
        responses = gmail.search_job_responses(days_back=7)
        
        # Generate report
        gmail.generate_report()
        
        # Count total responses
        total = sum(len(msgs) for msgs in responses.values())
        
        if total > 0:
            print(f"\n✅ Found {total} responses!")
            
            # Save to tracking file
            response_data = {
                'last_check': datetime.now().isoformat(),
                'responses': {
                    'positive': len(responses.get('positive', [])),
                    'rejection': len(responses.get('rejection', [])),
                    'neutral': len(responses.get('neutral', []))
                }
            }
            
            Path('data').mkdir(exist_ok=True)
            with open('data/response_summary.json', 'w') as f:
                json.dump(response_data, f, indent=2)
                
            # Calculate response rate
            conn = sqlite3.connect("unified_platform.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied=1")
            total_applied = cursor.fetchone()[0]
            conn.close()
            
            response_rate = (total / total_applied * 100) if total_applied > 0 else 0
            print(f"\n📊 Response Rate: {response_rate:.1f}% ({total}/{total_applied})")
        else:
            print("\n📭 No responses found yet (this is normal for recent applications)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTip: Make sure your Gmail credentials are set in .env file")

if __name__ == "__main__":
    main()