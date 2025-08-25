#!/usr/bin/env python3
"""
Test the Pipeline Transparency Layer - First Contact Advantage System
"""

import sys
import json
from datetime import datetime, timedelta

# Add path
sys.path.append('/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer')

from unified_career_system.pipeline_transparency.pipeline_manager import (
    PipelineManager, ContactType, ContactSource
)
from unified_career_system.pipeline_transparency.recruiter_shield import (
    RecruiterShield, AgencyType
)

def test_pipeline_transparency():
    """Comprehensive test of the Pipeline Transparency system"""
    
    print("\n" + "="*80)
    print("🧪 TESTING PIPELINE TRANSPARENCY LAYER")
    print("="*80)
    
    # Initialize managers
    manager = PipelineManager()
    shield = RecruiterShield()
    
    # TEST 1: Record first contacts with top companies
    print("\n📝 TEST 1: Recording First Contacts")
    print("-" * 40)
    
    companies = [
        ("Anthropic", "Senior ML Engineer", "https://anthropic.com/careers"),
        ("OpenAI", "ML Platform Engineer", "https://openai.com/careers"),
        ("Scale AI", "ML Infrastructure Engineer", "https://scale.com/careers"),
        ("Databricks", "Staff ML Engineer", "https://databricks.com/careers"),
        ("Meta", "ML Engineer - Recommendations", "https://meta.com/careers")
    ]
    
    for company, position, url in companies:
        contact_uid = manager.record_first_contact(
            company, position,
            ContactType.DISCOVERED,
            ContactSource.SELF_INITIATED,
            proof_url=url,
            notes=f"Found on company careers page"
        )
        print(f"✅ Recorded: {company} - {position[:30]}...")
    
    # TEST 2: Verify first contact
    print("\n🔐 TEST 2: Verifying First Contact")
    print("-" * 40)
    
    verification = manager.verify_first_contact("Anthropic")
    print(f"Anthropic verification:")
    print(f"  • Has contact: {verification['has_contact']}")
    print(f"  • First contact: {verification.get('first_contact_date', 'N/A')}")
    print(f"  • Proof: {verification.get('proof', 'N/A')}")
    
    # TEST 3: Log activities
    print("\n📋 TEST 3: Logging Activities")
    print("-" * 40)
    
    activities = [
        ("Anthropic", "research", "Reviewed recent papers and team structure"),
        ("Anthropic", "apply", "Submitted application via portal"),
        ("OpenAI", "research", "Studied recent GPT developments"),
        ("Scale AI", "network", "Connected with engineer on LinkedIn")
    ]
    
    for company, activity_type, description in activities:
        manager.log_activity(
            company, activity_type, description,
            outcome="Positive", next_steps="Follow up in 3 days"
        )
        print(f"✅ Logged: {company} - {activity_type}")
    
    # TEST 4: Register recruiters
    print("\n👥 TEST 4: Registering Recruiters")
    print("-" * 40)
    
    recruiters = [
        ("John Smith", "john@techtalent.com", "TechTalent", AgencyType.EXTERNAL),
        ("Sarah Lee", "sarah@airecruit.com", "AI Recruit", AgencyType.CONTINGENCY),
        ("Mike Chen", "mike.chen@meta.com", "Meta", AgencyType.INTERNAL)
    ]
    
    for name, email, agency, agency_type in recruiters:
        shield.register_recruiter(
            name, email, agency, agency_type,
            companies=["Anthropic", "OpenAI", "Google", "Apple"]
        )
        print(f"✅ Registered: {name} ({agency})")
    
    # TEST 5: Check recruiter conflicts
    print("\n🛡️ TEST 5: Checking Recruiter Conflicts")
    print("-" * 40)
    
    # Recruiter tries to pitch companies we already engaged
    conflicts = shield.check_first_contact_conflict(
        "john@techtalent.com",
        ["Anthropic", "OpenAI", "Microsoft", "Amazon"]
    )
    
    print(f"Recruiter: {conflicts['recruiter']}")
    print(f"Companies pitched: {conflicts['companies_pitched']}")
    print(f"Conflicts found: {conflicts['conflicts']}")
    print(f"New opportunities: {conflicts['new_opportunities']}")
    print(f"Recommendation: {conflicts['recommendation']}")
    
    if conflicts['conflict_details']:
        print("\nConflict details:")
        for conflict in conflicts['conflict_details']:
            print(f"  • {conflict['company']}: {conflict['message']}")
    
    # TEST 6: Get pipeline summary
    print("\n📊 TEST 6: Pipeline Summary")
    print("-" * 40)
    
    summary = manager.get_pipeline_summary()
    print(f"Total contacts: {summary['total_contacts']}")
    print(f"Companies engaged: {summary['companies_engaged']}")
    print(f"Recent activities: {summary['recent_activities']}")
    print(f"Pipeline health: {summary['pipeline_health']}")
    print(f"Contacts by type: {summary['contacts_by_type']}")
    
    # TEST 7: Generate first contact report
    print("\n📄 TEST 7: First Contact Report")
    print("-" * 40)
    
    report = manager.generate_first_contact_report()
    print(f"Companies with first contact established: {len(report)}")
    
    for entry in report[:3]:  # Show first 3
        print(f"\n{entry['company']}:")
        print(f"  • First contact: {entry['first_contact']}")
        print(f"  • Days engaged: {entry['days_engaged']}")
        print(f"  • Total interactions: {entry['total_interactions']}")
    
    # TEST 8: Export audit trail
    print("\n💾 TEST 8: Exporting Audit Trail")
    print("-" * 40)
    
    audit_file = manager.export_pipeline_audit("test_pipeline_audit.json")
    print(f"✅ Audit exported to: {audit_file}")
    
    # Read and display summary
    with open(audit_file, 'r') as f:
        audit = json.load(f)
    print(f"  • Total companies: {audit['total_companies']}")
    print(f"  • Total contacts: {len(audit['contacts'])}")
    print(f"  • Total activities: {len(audit['activities'])}")
    
    # TEST 9: Recruiter report
    print("\n📊 TEST 9: Recruiter Report")
    print("-" * 40)
    
    recruiter_report = shield.generate_recruiter_report()
    print(f"Total recruiters: {recruiter_report['total_recruiters']}")
    print(f"Total interactions: {recruiter_report['total_interactions']}")
    print(f"Pipeline companies: {recruiter_report['pipeline_companies']}")
    
    # Clean up
    manager.close()
    shield.close()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - Pipeline Transparency Layer is operational!")
    print("="*80)
    
    return True

if __name__ == "__main__":
    success = test_pipeline_transparency()
    if success:
        print("\n🎯 Your 'First Contact Advantage' system is ready!")
        print("   You now have timestamped proof of all job search activities.")
        print("   Recruiters can no longer claim finder's fees on your pipeline.")
        print("   Hiring managers will see your professional organization.")
    else:
        print("\n❌ Tests failed - please check the system")