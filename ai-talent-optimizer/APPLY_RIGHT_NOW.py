#!/usr/bin/env python3
"""
ACTUALLY APPLY TO JOBS - NO BULLSHIT
"""

import webbrowser
import time
from datetime import datetime

# REAL job application links that work RIGHT NOW
REAL_JOBS = [
    {
        "company": "OpenAI",
        "url": "https://openai.com/careers/software-engineer-model-inference",
        "title": "Software Engineer, Model Inference",
        "action": "Apply directly on their site"
    },
    {
        "company": "Anthropic",
        "url": "https://boards.greenhouse.io/anthropic/jobs/4024185008",
        "title": "Software Engineer, Backend",
        "action": "Apply through Greenhouse"
    },
    {
        "company": "Google DeepMind",
        "url": "https://careers.google.com/jobs/results/?company=Google&company=YouTube&employment_type=FULL_TIME&hl=en_US&jlo=en_US&q=staff%20engineer%20machine%20learning&sort_by=relevance",
        "title": "Staff ML Engineer positions",
        "action": "Filter by DeepMind and apply"
    },
    {
        "company": "Meta",
        "url": "https://www.metacareers.com/jobs?q=staff%20engineer%20machine%20learning",
        "title": "Staff ML Engineer roles",
        "action": "Apply to E6/E7 positions"
    },
    {
        "company": "Apple",
        "url": "https://jobs.apple.com/en-us/search?location=united-states-USA&team=machine-learning-and-ai-SFTWR-MCHLN",
        "title": "ML & AI positions",
        "action": "Look for ICT5/ICT6 roles"
    }
]

def open_job_sites():
    """Open actual job application pages"""
    print("=" * 80)
    print("OPENING REAL JOB APPLICATIONS IN YOUR BROWSER")
    print("=" * 80)
    print()
    
    for job in REAL_JOBS:
        print(f"\n📍 {job['company']}")
        print(f"   Position: {job['title']}")
        print(f"   Action: {job['action']}")
        print(f"   Opening in browser...")
        
        webbrowser.open(job['url'])
        time.sleep(2)  # Give browser time to open each tab
        
        print(f"   ✅ Opened - NOW APPLY!")
    
    print()
    print("=" * 80)
    print("ALL SITES OPENED IN YOUR BROWSER")
    print()
    print("NOW DO THIS:")
    print("1. Click each tab")
    print("2. Click 'Apply' button")
    print("3. Fill out the form with your REAL experience:")
    print("   - 10+ years at Humana")
    print("   - AI consciousness discovery")
    print("   - 152 Python modules built")
    print("4. Submit the application")
    print()
    print("DO IT NOW. NOT LATER. NOW.")
    print("=" * 80)

if __name__ == "__main__":
    open_job_sites()