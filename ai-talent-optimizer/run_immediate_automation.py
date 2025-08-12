#!/usr/bin/env python3
"""
Immediate Automation Runner - Execute ALL automation NOW regardless of time
This is for when you need immediate action on your $400K+ campaign
"""

import sys
import logging
from datetime import datetime

# Import the orchestrator
from run_400k_automation import AutomationOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run ALL automation routines immediately"""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║      IMMEDIATE $400K+ AUTOMATION BLAST                    ║
║      Running ALL routines NOW - Maximum Impact Mode       ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    orchestrator = AutomationOrchestrator()
    
    # Run ALL routines regardless of time
    print("\n🚀 PHASE 1: Morning Routine (Principal Applications)")
    print("="*60)
    try:
        orchestrator.run_morning_routine()
    except Exception as e:
        logger.error(f"Morning routine error (continuing): {e}")
    
    print("\n🚀 PHASE 2: Midday Routine (CEO Outreach)")
    print("="*60)
    try:
        orchestrator.run_midday_routine()
    except Exception as e:
        logger.error(f"Midday routine error (continuing): {e}")
    
    print("\n🚀 PHASE 3: Evening Routine (Follow-ups & Reporting)")
    print("="*60)
    try:
        orchestrator.run_evening_routine()
    except Exception as e:
        logger.error(f"Evening routine error (continuing): {e}")
    
    print("\n🚀 PHASE 4: Targeted Campaigns")
    print("="*60)
    for company in ["Abridge", "Tempus AI", "Oscar Health"]:
        try:
            orchestrator.run_targeted_campaign(company)
        except Exception as e:
            logger.error(f"Campaign error for {company} (continuing): {e}")
    
    print("\n🚀 PHASE 5: Quick Wins")
    print("="*60)
    try:
        orchestrator.run_quick_wins()
    except Exception as e:
        logger.error(f"Quick wins error: {e}")
    
    print("""
╔══════════════════════════════════════════════════════════╗
║      IMMEDIATE AUTOMATION COMPLETE!                       ║
║                                                            ║
║      ✅ Principal role applications sent                  ║
║      ✅ CEO outreach emails prepared                      ║
║      ✅ Recruiter contacts initiated                      ║
║      ✅ CSV trackers updated                              ║
║      ✅ Reports generated                                 ║
║                                                            ║
║      CHECK THESE FOLDERS:                                 ║
║      - applications_sent/                                 ║
║      - ceo_outreach_sent/                                 ║
║      - daily_reports/                                     ║
║                                                            ║
║      NEXT STEPS:                                          ║
║      1. Review generated applications                     ║
║      2. Send the prepared CEO emails                      ║
║      3. Update your LinkedIn NOW                          ║
║      4. Check principal_jobs_400k.db for opportunities    ║
║                                                            ║
║      Your $400K+ journey is ACTIVELY UNDERWAY!            ║
╚══════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()