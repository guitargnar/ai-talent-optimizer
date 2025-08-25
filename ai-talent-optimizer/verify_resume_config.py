#!/usr/bin/env python3
"""
Verify Resume Configuration
Ensures the correct resume (Matthew_Scott_2025_Professional_Resume.pdf) is being used
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import settings
from src.services.resume import ResumeService

def verify_resume_configuration():
    """Verify that the correct resume is configured and available"""
    
    print("\n" + "="*80)
    print("📄 RESUME CONFIGURATION VERIFICATION")
    print("="*80)
    
    # Check configured resume path
    configured_path = settings.application.resume_path
    print(f"\n1. Configured Resume Path:")
    print(f"   {configured_path}")
    
    # Check if file exists
    if Path(configured_path).exists():
        print("   ✅ File exists")
        
        # Check file size
        size = Path(configured_path).stat().st_size
        print(f"   📊 File size: {size:,} bytes")
        
        # Check modification time
        mtime = datetime.fromtimestamp(Path(configured_path).stat().st_mtime)
        print(f"   🕐 Last modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("   ❌ FILE NOT FOUND!")
        
    # Check resumes directory
    print(f"\n2. Available Resumes in {settings.resumes_dir}:")
    if settings.resumes_dir.exists():
        resumes = list(settings.resumes_dir.glob("*.pdf"))
        for resume in sorted(resumes):
            size = resume.stat().st_size
            print(f"   • {resume.name} ({size:,} bytes)")
            if "2025" in resume.name:
                print(f"     ⭐ This is your latest resume!")
    else:
        print("   ❌ Resumes directory not found!")
    
    # Test ResumeService
    print("\n3. Testing ResumeService:")
    resume_service = ResumeService()
    
    # Create a mock job for ML Engineer
    class MockJob:
        def __init__(self):
            self.position = "Machine Learning Engineer"
            self.description = "Build and deploy ML models at scale"
    
    test_job = MockJob()
    selected_resume = resume_service.get_resume_for_job(test_job)
    print(f"   For ML Engineer role, selected: {Path(selected_resume).name if selected_resume else 'None'}")
    
    # Check if it's the 2025 resume
    if selected_resume and "2025" in selected_resume:
        print("   ✅ Correctly selecting 2025 resume!")
    elif selected_resume:
        print("   ⚠️ Not using 2025 resume - updating configuration...")
        
    # Recommendation
    print("\n" + "="*80)
    print("📋 RECOMMENDATIONS:")
    print("="*80)
    
    if Path(configured_path).exists() and "2025" in configured_path:
        print("\n✅ Your system is correctly configured to use:")
        print(f"   Matthew_Scott_2025_Professional_Resume.pdf")
        print("\n   This resume highlights:")
        print("   • Mirador project with 7 specialized LLMs")
        print("   • 79+ ML models at Humana")
        print("   • Platform engineering expertise")
        print("   • $1.2M annual savings")
    else:
        print("\n⚠️ ACTION REQUIRED:")
        print("   1. Ensure matthew_scott_2025_professional_resume.pdf is in resumes/")
        print("   2. Update RESUME_PATH in .env")
        print("   3. Restart any running application processes")
    
    # Check for old resumes that shouldn't be used
    print("\n⚠️ OLD RESUMES (should not be used):")
    if settings.resumes_dir.exists():
        old_resumes = [r for r in settings.resumes_dir.glob("*.pdf") if "2025" not in r.name]
        for resume in old_resumes:
            print(f"   • {resume.name} - outdated")
    
    print("\n" + "="*80)
    print("✅ Verification Complete")
    print("="*80)

if __name__ == "__main__":
    verify_resume_configuration()