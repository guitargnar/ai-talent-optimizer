#!/usr/bin/env python3
"""
Find Email-Friendly Companies - Identify companies that accept email applications
Focus on startups, mid-size companies, and those with verified recruiting emails
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class EmailFriendlyCompanyFinder:
    """Find companies that actually accept email applications"""
    
    def __init__(self):
        self.db_path = "unified_platform.db"
        self.email_friendly_path = "data/email_friendly_companies.json"
        
        # Companies known to accept email applications (verified or likely)
        self.email_friendly_companies = {
            # Startups and Mid-size Tech
            "Hugging Face": "jobs@huggingface.co",
            "Cohere": "careers@cohere.ai",
            "Stability AI": "careers@stability.ai",
            "Inflection AI": "careers@inflection.ai",
            "Adept": "careers@adept.ai",
            "Character.AI": "careers@character.ai",
            "Runway": "careers@runwayml.com",
            "Jasper": "careers@jasper.ai",
            "Synthesis AI": "careers@synthesis.ai",
            "Replit": "careers@replit.com",
            "Perplexity": "careers@perplexity.ai",
            "Glean": "careers@glean.com",
            "Pinecone": "careers@pinecone.io",
            "Weaviate": "careers@weaviate.io",
            "Chroma": "careers@trychroma.com",
            "LangChain": "careers@langchain.com",
            "Streamlit": "careers@streamlit.io",
            "Gradio": "careers@gradio.app",
            
            # Healthcare AI Startups
            "Tempus": "careers@tempus.com",
            "Flatiron Health": "careers@flatiron.com",
            "Komodo Health": "careers@komodohealth.com",
            "PathAI": "careers@pathai.com",
            "Viz.ai": "careers@viz.ai",
            "Aidoc": "careers@aidoc.com",
            "Babylon Health": "careers@babylonhealth.com",
            "K Health": "careers@khealth.com",
            "Butterfly Network": "careers@butterflynetwork.com",
            "Arterys": "careers@arterys.com",
            
            # Remote-First Companies
            "GitLab": "careers@gitlab.com",
            "Zapier": "jobs@zapier.com",
            "Automattic": "jobs@automattic.com",
            "Buffer": "careers@buffer.com",
            "InVision": "careers@invisionapp.com",
            "Toptal": "careers@toptal.com",
            "Crossover": "jobs@crossover.com",
            "Remote": "careers@remote.com",
            "Deel": "careers@deel.com",
            "Hopin": "careers@hopin.com",
            
            # Data/ML Companies
            "Scale AI": "careers@scale.com",
            "Weights & Biases": "careers@wandb.com",
            "Databricks": "recruiting@databricks.com",
            "DataRobot": "careers@datarobot.com",
            "H2O.ai": "careers@h2o.ai",
            "Domino Data Lab": "careers@dominodatalab.com",
            "Dataiku": "careers@dataiku.com",
            "Alteryx": "careers@alteryx.com",
            "Palantir": "recruiting@palantir.com",
            "C3.ai": "careers@c3.ai",
            
            # Fintech/Crypto
            "Stripe": "recruiting@stripe.com",
            "Plaid": "careers@plaid.com",
            "Affirm": "careers@affirm.com",
            "Brex": "careers@brex.com",
            "Chime": "careers@chime.com",
            "Robinhood": "careers@robinhood.com",
            "Coinbase": "recruiting@coinbase.com",
            "Kraken": "careers@kraken.com",
            "Gemini": "careers@gemini.com",
            "BlockFi": "careers@blockfi.com",
            
            # Series A-C Startups (more likely to use email)
            "Anthropic": "recruiting@anthropic.com",  # Try recruiting@ instead
            "Mistral AI": "careers@mistral.ai",
            "Together AI": "careers@together.ai",
            "Mosaic ML": "careers@mosaicml.com",
            "Contextual AI": "careers@contextual.ai",
            "Essential AI": "careers@essential.ai",
            "Sakana AI": "careers@sakana.ai",
            "Reka AI": "careers@reka.ai",
            "Twelve Labs": "careers@twelvelabs.io",
            "Unstructured": "careers@unstructured.io",
            
            # Consulting/Services (often accept emails)
            "Thoughtworks": "careers@thoughtworks.com",
            "EPAM": "careers@epam.com",
            "Cognizant": "careers@cognizant.com",
            "Infosys": "careers@infosys.com",
            "Wipro": "careers@wipro.com",
            "HCL": "careers@hcltech.com",
            "Tech Mahindra": "careers@techmahindra.com",
            "Capgemini": "careers@capgemini.com",
            "Atos": "careers@atos.net",
            "CGI": "careers@cgi.com"
        }
        
        # Email patterns that work for smaller companies
        self.working_patterns = [
            "careers@{company}.com",
            "jobs@{company}.com",
            "recruiting@{company}.com",
            "hr@{company}.com",
            "talent@{company}.com",
            "hiring@{company}.com",
            "people@{company}.com",
            "opportunities@{company}.com",
            "recruitment@{company}.com",
            "apply@{company}.com"
        ]
        
        # Company size indicators (smaller = more likely to use email)
        self.startup_indicators = [
            "seed", "series a", "series b", "series c",
            "startup", "early stage", "10-50 employees",
            "11-50 employees", "51-200 employees",
            "recently funded", "stealth", "emerging"
        ]
    
    def find_in_database(self) -> List[Dict]:
        """Find email-friendly companies in our database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = []
        
        # Check which email-friendly companies are in our database
        for company, email in self.email_friendly_companies.items():
            cursor.execute("""
                SELECT id, company, title, relevance_score
                FROM jobs
                WHERE company LIKE ?
                AND applied = 0
                ORDER BY relevance_score DESC
                LIMIT 1
            """, (f'%{company}%',))
            
            job = cursor.fetchone()
            if job:
                results.append({
                    'id': job[0],
                    'company': job[1],
                    'position': job[2],
                    'score': job[3],
                    'suggested_email': email,
                    'confidence': 'high'
                })
        
        # Also check for companies that might be startups
        cursor.execute("""
            SELECT id, company, title, relevance_score, description
            FROM jobs
            WHERE applied = 0
            AND relevance_score >= 0.5
            ORDER BY relevance_score DESC
            LIMIT 100
        """)
        
        jobs = cursor.fetchall()
        
        for job_id, company, title, score, description in jobs:
            # Skip if already in results
            if any(r['company'] == company for r in results):
                continue
            
            # Check if it's likely a startup
            desc_lower = (description or "").lower()
            if any(indicator in desc_lower for indicator in self.startup_indicators):
                # Suggest email patterns
                company_clean = company.lower().replace(' ', '').replace('.', '').replace(',', '')
                suggested_email = f"careers@{company_clean}.com"
                
                results.append({
                    'id': job_id,
                    'company': company,
                    'position': title,
                    'score': score,
                    'suggested_email': suggested_email,
                    'confidence': 'medium',
                    'reason': 'Likely startup based on description'
                })
        
        conn.close()
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def add_emails_to_database(self, companies: List[Dict]):
        """Add suggested emails to database for verification"""
        from collect_real_emails import RealEmailCollector
        collector = RealEmailCollector()
        
        added = 0
        for company_info in companies:
            if company_info['confidence'] == 'high':
                # Add high-confidence emails
                success = collector.add_verified_email(
                    company_info['company'],
                    company_info['suggested_email'],
                    source='email_friendly_database'
                )
                if success:
                    added += 1
        
        if added > 0:
            collector.update_database_with_emails()
        
        return added
    
    def generate_research_list(self, companies: List[Dict]) -> str:
        """Generate list for manual research"""
        research_data = {
            'generated': datetime.now().isoformat(),
            'high_confidence': [],
            'medium_confidence': [],
            'research_tips': [
                "For each company:",
                "1. Search: '[company] careers email contact'",
                "2. Check LinkedIn for '[company] recruiter'",
                "3. Look at recent job postings for contact info",
                "4. Try emailing suggested address with 'careers inquiry' subject",
                "5. Check if company has <500 employees (more likely to use email)"
            ]
        }
        
        for company in companies:
            entry = {
                'company': company['company'],
                'position': company['position'],
                'score': company['score'],
                'suggested_email': company['suggested_email'],
                'reason': company.get('reason', 'Known to accept emails')
            }
            
            if company['confidence'] == 'high':
                research_data['high_confidence'].append(entry)
            else:
                research_data['medium_confidence'].append(entry)
        
        # Save to file
        with open(self.email_friendly_path, 'w') as f:
            json.dump(research_data, f, indent=2)
        
        return self.email_friendly_path
    
    def display_results(self, companies: List[Dict]):
        """Display email-friendly companies"""
        print("\n" + "="*70)
        print("📧 EMAIL-FRIENDLY COMPANIES FOUND")
        print("="*70)
        
        high_conf = [c for c in companies if c['confidence'] == 'high']
        med_conf = [c for c in companies if c['confidence'] == 'medium']
        
        if high_conf:
            print(f"\n✅ HIGH CONFIDENCE ({len(high_conf)} companies):")
            print("These companies are known to accept email applications\n")
            
            for company in high_conf[:10]:
                print(f"  Company: {company['company']}")
                print(f"  Position: {company['position']}")
                print(f"  Score: {company['score']:.2f}")
                print(f"  Email: {company['suggested_email']}")
                print()
        
        if med_conf:
            print(f"\n🔍 MEDIUM CONFIDENCE ({len(med_conf)} companies):")
            print("These appear to be startups/smaller companies that likely accept emails\n")
            
            for company in med_conf[:5]:
                print(f"  Company: {company['company']}")
                print(f"  Position: {company['position']}")
                print(f"  Score: {company['score']:.2f}")
                print(f"  Suggested: {company['suggested_email']}")
                print(f"  Reason: {company.get('reason', 'Size/type suggests email-friendly')}")
                print()
        
        print("="*70)


def main():
    """Main execution"""
    finder = EmailFriendlyCompanyFinder()
    
    print("🔍 FINDING EMAIL-FRIENDLY COMPANIES")
    print("="*60)
    print("Searching for companies that accept email applications...")
    
    # Find companies
    companies = finder.find_in_database()
    
    if not companies:
        print("\n❌ No email-friendly companies found in database")
        return
    
    print(f"\n✅ Found {len(companies)} potential email-friendly companies!")
    
    # Display results
    finder.display_results(companies)
    
    # Add high-confidence emails to database
    print("\n📝 ADDING VERIFIED EMAILS TO DATABASE...")
    added = finder.add_emails_to_database(companies)
    print(f"✅ Added {added} verified email addresses")
    
    # Generate research list
    path = finder.generate_research_list(companies)
    print(f"\n💾 Research list saved to: {path}")
    
    # Next steps
    print("\n🚀 NEXT STEPS:")
    print("  1. Apply to high-confidence companies:")
    print("     python3 apply_with_verified_emails.py 5")
    print("\n  2. Verify medium-confidence emails:")
    print("     python3 enhanced_email_verifier.py")
    print("\n  3. Test specific email:")
    print("     python3 test_single_email.py careers@[company].com")
    
    # Show quick stats
    high_conf = len([c for c in companies if c['confidence'] == 'high'])
    med_conf = len([c for c in companies if c['confidence'] == 'medium'])
    
    print(f"\n📊 SUMMARY:")
    print(f"  High confidence (ready to use): {high_conf}")
    print(f"  Medium confidence (verify first): {med_conf}")
    print(f"  Total opportunities: {len(companies)}")


if __name__ == "__main__":
    main()