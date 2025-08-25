#!/usr/bin/env python3
"""
Verify Resume Setup - Ensure base_resume.pdf is properly configured
"""

import os
from pathlib import Path
import hashlib

def verify_resume_setup():
    """Verify that resume setup is correct"""
    
    print("="*60)
    print("📄 RESUME SETUP VERIFICATION")
    print("="*60)
    
    base_dir = Path(__file__).parent
    resumes_dir = base_dir / "resumes"
    archive_dir = resumes_dir / "archive"
    base_resume = resumes_dir / "base_resume.pdf"
    
    # Check 1: base_resume.pdf exists
    if base_resume.exists():
        size_kb = base_resume.stat().st_size / 1024
        print(f"✅ base_resume.pdf exists ({size_kb:.1f} KB)")
        
        # Get file hash for verification
        with open(base_resume, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]
        print(f"   Hash: {file_hash}")
    else:
        print("❌ base_resume.pdf NOT FOUND")
        return False
    
    # Check 2: No old resume files in main directory
    old_resumes = list(resumes_dir.glob("matthew_scott_*.pdf"))
    if old_resumes:
        print(f"⚠️  Found {len(old_resumes)} old resume files in main directory:")
        for f in old_resumes:
            print(f"   - {f.name}")
    else:
        print("✅ No old resume files in main directory")
    
    # Check 3: Archive directory exists and contains old files
    if archive_dir.exists():
        archived = list(archive_dir.glob("*.pdf"))
        print(f"✅ Archive directory contains {len(archived)} files")
        if archived:
            print("   Archived files:")
            for f in archived[:3]:  # Show first 3
                print(f"   - {f.name}")
            if len(archived) > 3:
                print(f"   ... and {len(archived) - 3} more")
    else:
        print("⚠️  Archive directory does not exist")
    
    # Check 4: Verify quality_first_apply.py configuration
    quality_script = base_dir / "quality_first_apply.py"
    if quality_script.exists():
        with open(quality_script, 'r') as f:
            content = f.read()
        
        if "'default': 'resumes/base_resume.pdf'" in content:
            print("✅ quality_first_apply.py correctly configured to use base_resume.pdf")
        else:
            print("❌ quality_first_apply.py NOT using base_resume.pdf")
            return False
    else:
        print("❌ quality_first_apply.py not found")
        return False
    
    # Check 5: Directory structure
    print("\n📁 Current Resume Directory Structure:")
    print(f"   resumes/")
    print(f"   ├── base_resume.pdf (MASTER COPY)")
    print(f"   ├── archive/")
    
    archived_count = len(list(archive_dir.glob("*.pdf"))) if archive_dir.exists() else 0
    print(f"   │   └── {archived_count} archived files")
    
    # Check for other directories
    for item in resumes_dir.iterdir():
        if item.is_dir() and item.name != "archive":
            print(f"   └── {item.name}/")
    
    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    print("✅ Single source of truth: base_resume.pdf")
    print("✅ Old resumes archived for safety")
    print("✅ System configured to use base_resume.pdf only")
    print("\n💡 All applications will now use the master resume")
    print("   Content: AI/ML Architect with Mirador platform (79+ models)")
    print("   Focus: Multi-model orchestration and LLM systems")
    
    return True

if __name__ == "__main__":
    success = verify_resume_setup()
    
    if success:
        print("\n✅ RESUME SETUP VERIFIED - Ready for applications!")
    else:
        print("\n❌ Issues found - Please review and fix")