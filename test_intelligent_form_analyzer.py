#!/usr/bin/env python3
"""
Test the new intelligent form analyzer with dynamic field discovery
"""

from web_form_automator import WebFormAutomator
from pathlib import Path
import json

def demonstrate_intelligent_analysis():
    """Demonstrate the new intelligent form analysis capabilities"""
    
    print("="*60)
    print("🧠 INTELLIGENT FORM ANALYZER DEMONSTRATION")
    print("="*60)
    print("\nThis demonstrates the enhanced Greenhouse automation that:")
    print("• Dynamically discovers ALL form fields")
    print("• Maps fields to your knowledge base")
    print("• Reports what can/cannot be filled")
    print("• Collects missing information interactively")
    print("="*60)
    
    # Initialize the intelligent automator
    automator = WebFormAutomator(dry_run=True)
    
    # Simulate form field discovery
    print("\n📡 PHASE 1: FORM FIELD DISCOVERY")
    print("-"*40)
    
    # Mock discovered fields from a real Greenhouse form
    mock_form_fields = [
        # Basic Information
        {'type': 'input', 'id': 'first_name', 'label': 'First Name*', 'required': True},
        {'type': 'input', 'id': 'last_name', 'label': 'Last Name*', 'required': True},
        {'type': 'input', 'id': 'email', 'label': 'Email*', 'required': True},
        {'type': 'input', 'id': 'phone', 'label': 'Phone*', 'required': True},
        
        # Education
        {'type': 'select', 'id': 'school', 'label': 'School*', 'required': True,
         'options': ['Columbia University', 'MIT', 'Stanford', 'Other']},
        {'type': 'select', 'id': 'degree', 'label': 'Degree*', 'required': True,
         'options': ['Bachelor\'s', 'Master\'s', 'PhD', 'Bootcamp']},
        {'type': 'select', 'id': 'discipline', 'label': 'Discipline*', 'required': True,
         'options': ['Computer Science', 'Software Engineering', 'Data Science', 'Other']},
        
        # Location & Work Authorization
        {'type': 'input', 'id': 'city_residence', 'label': 'City of current residence*', 'required': True},
        {'type': 'select', 'id': 'state_residence', 'label': 'State/Province*', 'required': True,
         'options': ['Kentucky', 'Texas', 'California', 'New York', 'Other']},
        {'type': 'select', 'id': 'country_residence', 'label': 'Country*', 'required': True,
         'options': ['United States', 'Canada', 'Other']},
        
        # Visa & Work Authorization
        {'type': 'select', 'id': 'visa_status', 'label': 'Will you need visa sponsorship?*', 'required': True,
         'options': ['Yes', 'No']},
        {'type': 'select', 'id': 'graduation_date', 'label': 'Graduation Date (or Expected)*', 'required': True,
         'options': ['Already graduated', '2024', '2025', '2026']},
        
        # Experience
        {'type': 'select', 'id': 'years_experience', 'label': 'Years of Professional Experience*', 'required': True,
         'options': ['0-2 years', '3-5 years', '6-10 years', '10+ years']},
        {'type': 'select', 'id': 'programming_languages', 'label': 'Primary Programming Languages*', 'required': True,
         'options': ['Python', 'Java', 'JavaScript', 'C++', 'Other']},
        
        # Optional Demographics
        {'type': 'select', 'id': 'gender_identity', 'label': 'Gender Identity (Optional)', 'required': False,
         'options': ['Male', 'Female', 'Non-binary', 'Prefer not to say']},
        {'type': 'select', 'id': 'race_ethnicity', 'label': 'Race/Ethnicity (Optional)', 'required': False,
         'options': ['Asian', 'Black', 'Hispanic', 'White', 'Other', 'Prefer not to say']},
        
        # Additional
        {'type': 'textarea', 'id': 'cover_letter', 'label': 'Cover Letter', 'required': False},
        {'type': 'file', 'id': 'resume', 'label': 'Resume/CV*', 'required': True},
        {'type': 'input', 'id': 'linkedin_url', 'label': 'LinkedIn Profile', 'required': False},
        {'type': 'input', 'id': 'github_url', 'label': 'GitHub Profile', 'required': False},
        {'type': 'input', 'id': 'portfolio_url', 'label': 'Portfolio Website', 'required': False}
    ]
    
    print(f"Discovered {len(mock_form_fields)} form fields:")
    print(f"  • Required fields: {sum(1 for f in mock_form_fields if f.get('required', False))}")
    print(f"  • Optional fields: {sum(1 for f in mock_form_fields if not f.get('required', False))}")
    print(f"  • Input fields: {sum(1 for f in mock_form_fields if f['type'] == 'input')}")
    print(f"  • Select dropdowns: {sum(1 for f in mock_form_fields if f['type'] == 'select')}")
    print(f"  • Text areas: {sum(1 for f in mock_form_fields if f['type'] == 'textarea')}")
    print(f"  • File uploads: {sum(1 for f in mock_form_fields if f['type'] == 'file')}")
    
    # Perform knowledge mapping
    print("\n🧠 PHASE 2: KNOWLEDGE MAPPING")
    print("-"*40)
    
    mapped_fields, unmapped_fields = automator.map_fields_to_knowledge(mock_form_fields)
    
    print(f"Mapping Results:")
    print(f"  ✅ Auto-fillable: {len(mapped_fields)} fields")
    print(f"  ❌ Need user input: {len(unmapped_fields)} fields")
    
    # Generate the field report
    print("\n📊 PHASE 3: FIELD ANALYSIS REPORT")
    print("-"*40)
    
    report = automator.generate_field_report(mapped_fields, unmapped_fields)
    print(report)
    
    # Simulate interactive collection (in dry run, we'll skip actual input)
    print("\n💬 PHASE 4: INTERACTIVE DATA COLLECTION")
    print("-"*40)
    
    if unmapped_fields:
        print("In live mode, the system would now:")
        print("1. Present each unmapped field")
        print("2. Show available options (for dropdowns)")
        print("3. Collect your input")
        print("4. Validate the data")
        print("\nExample fields that would be collected:")
        for field in unmapped_fields[:5]:  # Show first 5
            if field['type'] == 'select':
                options = field.get('options', [])
                print(f"  • {field['label']}")
                if options:
                    print(f"    Options: {', '.join(options[:3])}...")
            else:
                print(f"  • {field['label']} ({field['type']})")
    
    # Demonstrate the complete workflow
    print("\n🚀 PHASE 5: COMPLETE WORKFLOW SIMULATION")
    print("-"*40)
    
    print("The intelligent automation would:")
    print("1. ✅ Navigate to the job URL")
    print("2. ✅ Discover all form fields dynamically")
    print("3. ✅ Map fields to your knowledge base")
    print("4. ✅ Report what can/cannot be filled")
    print("5. ✅ Collect missing information from you")
    print("6. ✅ Fill all fields with complete data")
    print("7. ✅ Take screenshot for review")
    print("8. ⏸️  Wait for your approval to submit")
    
    print("\n" + "="*60)
    print("✨ INTELLIGENT FORM ANALYZER READY")
    print("="*60)
    print("\nKey Improvements:")
    print("• No more hardcoded field selectors")
    print("• Handles any Greenhouse form structure")
    print("• Interactive data collection for unknowns")
    print("• Complete field coverage")
    print("• Human-in-the-loop verification")

def test_real_application():
    """Test with a real Greenhouse URL"""
    
    print("\n" + "="*60)
    print("🎯 REAL APPLICATION TEST")
    print("="*60)
    
    # Use the mthree job URL from our live test
    job_url = "https://job-boards.greenhouse.io/mthreerecruitingportal/jobs/4406180006"
    
    cover_letter = """Dear mthree Team,

I am excited to apply for the Junior Software Engineer position. With 10+ years of Python experience 
and a strong foundation in software engineering principles, I am well-prepared to contribute to your 
team and grow through your comprehensive training program.

Best regards,
Matthew Scott"""
    
    print(f"\nTarget Job: mthree Junior Software Engineer")
    print(f"URL: {job_url}")
    
    # Initialize automator in dry run mode
    automator = WebFormAutomator(dry_run=True)
    
    print("\n🔄 Running Intelligent Form Analysis...")
    print("="*60)
    
    # This would actually navigate and analyze the real form
    # For demonstration, we'll use the mock analysis
    result = automator.apply_via_greenhouse(
        job_url=job_url,
        cover_letter=cover_letter,
        resume_path="resumes/base_resume.pdf"
    )
    
    success, message = result
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    print(f"Success: {success}")
    print(f"Message: {message}")
    
    if success:
        print("\n✅ The intelligent form analyzer successfully:")
        print("   • Discovered all form fields")
        print("   • Mapped known information")
        print("   • Identified gaps in knowledge")
        print("   • Prepared for data collection")
        print("   • Ready for form submission")

if __name__ == "__main__":
    # Ensure screenshots directory exists
    Path("screenshots").mkdir(exist_ok=True)
    
    # Run demonstrations
    demonstrate_intelligent_analysis()
    test_real_application()
    
    print("\n" + "="*60)
    print("🎉 INTELLIGENT FORM ANALYZER TEST COMPLETE")
    print("="*60)
    print("\nThe new architecture provides:")
    print("• Dynamic form discovery")
    print("• Intelligent field mapping")
    print("• Interactive data collection")
    print("• Complete form coverage")
    print("• Resilient automation")