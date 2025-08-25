#!/usr/bin/env python3
"""
LinkedIn Job Finder - Find current Easy Apply jobs
Generates search URLs for immediate application
"""

import webbrowser
from datetime import datetime
from urllib.parse import quote

def generate_linkedin_searches():
    """Generate LinkedIn search URLs for ML/AI positions"""
    
    print("\n" + "="*60)
    print("🔍 LINKEDIN JOB SEARCH GENERATOR")
    print("="*60)
    print("Finding Easy Apply ML/AI positions posted this week...")
    
    # Search queries optimized for Easy Apply
    searches = [
        {
            "title": "Principal/Staff ML Engineers - Easy Apply",
            "query": "principal machine learning engineer OR staff ML engineer",
            "filters": "&f_AL=true&f_TPR=r604800",  # Easy Apply + Past Week
            "location": "United States"
        },
        {
            "title": "Senior ML Engineers - Remote",
            "query": "senior machine learning engineer",
            "filters": "&f_AL=true&f_TPR=r604800&f_WT=2",  # Easy Apply + Past Week + Remote
            "location": "United States"
        },
        {
            "title": "AI/ML Platform Engineers",
            "query": "ML platform engineer OR MLOps engineer",
            "filters": "&f_AL=true&f_TPR=r86400",  # Easy Apply + Past 24 hours
            "location": "United States"
        },
        {
            "title": "Healthcare AI/ML",
            "query": "healthcare machine learning OR medical AI",
            "filters": "&f_AL=true&f_TPR=r604800",
            "location": "United States"
        },
        {
            "title": "LLM/GenAI Engineers",
            "query": "LLM engineer OR generative AI engineer",
            "filters": "&f_AL=true&f_TPR=r604800",
            "location": "United States"
        },
        {
            "title": "European ML - Visa Sponsorship",
            "query": "machine learning engineer visa sponsorship",
            "filters": "&f_AL=true&f_TPR=r2592000",  # Past month
            "location": "European Union"
        },
        {
            "title": "London ML Roles",
            "query": "machine learning engineer",
            "filters": "&f_AL=true&f_TPR=r604800",
            "location": "London, United Kingdom"
        },
        {
            "title": "Amsterdam Tech Roles",
            "query": "ML engineer OR data scientist",
            "filters": "&f_AL=true&f_TPR=r604800",
            "location": "Amsterdam, Netherlands"
        }
    ]
    
    # Target companies to search
    target_companies = [
        "Anthropic", "OpenAI", "DeepMind", "Meta", "Google",
        "Microsoft", "Apple", "Tempus", "Scale AI", "Cohere",
        "Databricks", "Snowflake", "Stripe", "Spotify", "Netflix"
    ]
    
    print("\n📋 SEARCH CATEGORIES:")
    print("-" * 40)
    
    search_urls = []
    
    for i, search in enumerate(searches, 1):
        # Build LinkedIn search URL
        base_url = "https://www.linkedin.com/jobs/search/?"
        keywords = f"keywords={quote(search['query'])}"
        location = f"&location={quote(search['location'])}"
        filters = search['filters']
        
        full_url = base_url + keywords + location + filters
        
        search_urls.append({
            "title": search['title'],
            "url": full_url
        })
        
        print(f"{i}. {search['title']}")
        print(f"   📍 Location: {search['location']}")
        print(f"   🔍 Query: {search['query'][:50]}...")
    
    print("\n🏢 TARGET COMPANIES:")
    print("-" * 40)
    print(", ".join(target_companies))
    
    # Company-specific searches
    print("\n🎯 COMPANY-SPECIFIC SEARCHES:")
    print("-" * 40)
    
    for company in target_companies[:5]:  # Top 5 companies
        company_url = f"https://www.linkedin.com/jobs/search/?keywords={quote(company + ' machine learning')}&f_AL=true&f_TPR=r2592000"
        search_urls.append({
            "title": f"{company} - ML Roles",
            "url": company_url
        })
        print(f"• {company} - Easy Apply ML positions")
    
    print("\n" + "="*60)
    print("HOW TO USE THESE SEARCHES:")
    print("="*60)
    
    instructions = """
    1. SELECT a search number to open in browser
    2. FILTER further by:
       - "Easy Apply" (if not already)
       - "Past 24 hours" or "Past week"
       - Your preferred location
    
    3. COLLECT job URLs:
       - Right-click on job title
       - Copy link address
       - Paste into linkedin_job_urls.txt
    
    4. RUN automation:
       python3 linkedin_job_processor.py
    
    5. TIPS for best results:
       - Apply to jobs < 3 days old
       - Prioritize < 50 applicants
       - Check "actively recruiting" badge
    """
    
    print(instructions)
    
    # Interactive menu
    while True:
        print("\nOptions:")
        print("1-8: Open specific search")
        print("c1-c5: Open company search")
        print("all: Open all searches")
        print("save: Save URLs to file")
        print("q: Quit")
        
        choice = input("\nEnter choice: ").lower()
        
        if choice == 'q':
            break
        elif choice == 'all':
            print("\n🚀 Opening all searches...")
            for item in search_urls[:8]:  # First 8 general searches
                print(f"   Opening: {item['title']}")
                webbrowser.open(item['url'])
        elif choice == 'save':
            save_search_urls(search_urls)
        elif choice.startswith('c'):
            try:
                idx = int(choice[1:]) - 1
                if 0 <= idx < 5:
                    company_search = search_urls[8 + idx]  # Company searches start at index 8
                    print(f"\n🎯 Opening {company_search['title']}...")
                    webbrowser.open(company_search['url'])
            except (ValueError, IndexError):
                print("❌ Invalid company number")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < 8:
                    search = search_urls[idx]
                    print(f"\n🔍 Opening {search['title']}...")
                    webbrowser.open(search['url'])
                else:
                    print("❌ Invalid number")
            except ValueError:
                print("❌ Invalid input")
    
    print("\n✨ Happy job hunting!")
    print("📝 Remember to save promising job URLs to linkedin_job_urls.txt")


def save_search_urls(search_urls):
    """Save search URLs to a file"""
    filename = f"linkedin_searches_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    
    with open(filename, 'w') as f:
        f.write("# LinkedIn Job Search URLs\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        for item in search_urls:
            f.write(f"# {item['title']}\n")
            f.write(f"{item['url']}\n\n")
    
    print(f"\n✅ Saved {len(search_urls)} search URLs to {filename}")


if __name__ == "__main__":
    generate_linkedin_searches()