#!/usr/bin/env python3
"""
Dry Run Test - Simulate sending applications to assess quality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.premium_email_composer import upgrade_email_quality
from src.models.database import DatabaseManager, Job
import json

def dry_run_applications():
    """Simulate sending to top companies and assess quality"""
    
    print("="*70)
    print("🔬 DRY RUN QUALITY ASSESSMENT")
    print("="*70)
    
    # Get real jobs from database
    db = DatabaseManager()
    session = db.get_session()
    
    # Get top jobs from different companies (NOT Anthropic)
    jobs = session.query(Job).filter(
        Job.applied == False,
        Job.company.in_(['Scale AI', 'Figma', 'Plaid', 'Zocdoc', 'Temporal Technologies']),
        Job.relevance_score >= 0.8
    ).order_by(
        Job.relevance_score.desc()
    ).limit(5).all()
    
    quality_scores = []
    emails = []
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{'='*70}")
        print(f"📧 APPLICATION #{i}")
        print(f"{'='*70}")
        print(f"Company: {job.company}")
        print(f"Position: {job.position}")
        print(f"Location: {job.location}")
        print(f"Relevance: {job.relevance_score:.0%}")
        
        # Generate email
        try:
            email = upgrade_email_quality(job.__dict__)
            quality_scores.append(email.get('quality_score', 0))
            emails.append(email)
            
            print(f"\n📊 QUALITY METRICS:")
            print(f"   Quality Score: {email.get('quality_score', 0):.0%}")
            print(f"   Research Included: {email.get('research_included', False)}")
            print(f"   Personalization: {email.get('personalization_level', 'medium')}")
            
            print(f"\n📮 EMAIL CONTENT:")
            print(f"Subject: {email['subject']}")
            print(f"\nBody:")
            print("-"*70)
            print(email['body'])
            print("-"*70)
            
            # Quality Analysis
            print(f"\n🔍 QUALITY ANALYSIS:")
            
            # Check for problems
            problems = []
            body = email['body']
            subject = email['subject']
            
            if 'Hiring Team' in body:
                problems.append("❌ Generic 'Hiring Team' greeting")
            else:
                print("✅ Personalized greeting")
                
            if 'recent developments' in body.lower() and 'Series F' not in body:
                problems.append("❌ Vague 'recent developments'")
            else:
                print("✅ Specific company research mentioned")
                
            if body.count(job.company) < 2:
                problems.append("⚠️ Company name mentioned too little")
            elif body.count(job.company) > 5:
                problems.append("⚠️ Company name repeated too much")
            else:
                print(f"✅ Company mentioned {body.count(job.company)} times (appropriate)")
                
            if 'Humana' in body:
                humana_count = body.count('Humana')
                if humana_count > 2:
                    problems.append(f"⚠️ Humana mentioned {humana_count} times (too much)")
                else:
                    print(f"✅ Humana mentioned {humana_count} time(s) (appropriate)")
            else:
                print("✅ No Humana mentions (good variety)")
                
            if '$1.2M' in body:
                print("✅ Quantified results included")
            else:
                problems.append("⚠️ No quantified results")
                
            if job.position in body:
                print("✅ Position title referenced")
            else:
                problems.append("❌ Position not mentioned in body")
                
            if '✓' in body:
                problems.append("⚠️ Unprofessional checkmarks used")
                
            # Technical terms check
            tech_terms = ['Python', 'ML', 'AI', 'distributed', 'LLM', 'PyTorch', 'Kubernetes']
            tech_found = [term for term in tech_terms if term in body]
            if len(tech_found) >= 2:
                print(f"✅ Technical depth: {', '.join(tech_found)}")
            else:
                problems.append("⚠️ Lacks technical specificity")
            
            # Print problems
            if problems:
                print("\n⚠️ ISSUES FOUND:")
                for problem in problems:
                    print(f"   {problem}")
            else:
                print("\n🎉 NO MAJOR ISSUES - HIGH QUALITY EMAIL!")
                
        except Exception as e:
            print(f"❌ Error generating email: {e}")
            quality_scores.append(0)
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 OVERALL ASSESSMENT")
    print(f"{'='*70}")
    
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"\n📈 Average Quality Score: {avg_quality:.0%}")
        
        if avg_quality >= 0.9:
            grade = "A"
            verdict = "EXCELLENT - Ready to send!"
        elif avg_quality >= 0.8:
            grade = "B+"
            verdict = "GOOD - Will get responses"
        elif avg_quality >= 0.7:
            grade = "B"
            verdict = "DECENT - Some improvements needed"
        else:
            grade = "C+"
            verdict = "POOR - Needs significant work"
            
        print(f"📝 Grade: {grade}")
        print(f"✅ Verdict: {verdict}")
        
        # Check variety
        subjects = [e['subject'] for e in emails if e]
        unique_subjects = len(set(subjects))
        print(f"\n📬 Email Variety:")
        print(f"   Unique subjects: {unique_subjects}/{len(subjects)}")
        
        if unique_subjects == len(subjects):
            print("   ✅ Excellent variety - no repetition")
        elif unique_subjects >= len(subjects) * 0.7:
            print("   ✅ Good variety")
        else:
            print("   ❌ Too repetitive")
    
    session.close()
    
    return quality_scores

if __name__ == "__main__":
    scores = dry_run_applications()
    
    print("\n" + "="*70)
    print("🎯 RECOMMENDATION")
    print("="*70)
    
    if scores and sum(scores)/len(scores) >= 0.8:
        print("\n✅ System is ready for production use!")
        print("Run: python guided_apply.py")
    else:
        print("\n❌ System needs improvements before sending")
        print("Issues to fix before proceeding")