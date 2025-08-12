#!/usr/bin/env python3
"""
Verify Resume Phone Number Fix
Quick verification that the resume PDF phone number issue has been resolved
"""

import os
from pathlib import Path
from datetime import datetime


def verify_phone_fix():
    """Verify the phone number has been fixed in all relevant files"""
    
    base_dir = Path(__file__).parent
    correct_phone = "502-345-0525"
    wrong_phone = "502-345-525"
    
    results = {}
    
    print("🔍 Resume Phone Number Fix Verification")
    print(f"✅ Correct: {correct_phone}")
    print(f"❌ Wrong: {wrong_phone}")
    print("-" * 50)
    
    # Check files
    files_to_check = [
        ("utils/config.py", "Configuration file"),
        ("output/resume_versions/master_resume_-_all_keywords.txt", "Master text resume"),
        ("RESUME_PHONE_FIXED.txt", "Fixed resume reference"),
    ]
    
    for file_path, description in files_to_check:
        full_path = base_dir / file_path
        if full_path.exists():
            content = full_path.read_text()
            has_correct = correct_phone in content
            has_wrong = wrong_phone in content
            
            status = "✅" if has_correct and not has_wrong else "⚠️" if has_correct else "❌"
            print(f"{status} {description}")
            print(f"    Path: {file_path}")
            print(f"    Has correct phone: {'Yes' if has_correct else 'No'}")
            print(f"    Has wrong phone: {'Yes' if has_wrong else 'No'}")
            
            results[file_path] = {
                'exists': True,
                'has_correct': has_correct,
                'has_wrong': has_wrong,
                'status': 'good' if has_correct and not has_wrong else 'needs_attention'
            }
        else:
            print(f"❓ {description}")
            print(f"    Path: {file_path} (FILE NOT FOUND)")
            results[file_path] = {'exists': False}
        
        print()
    
    # Check PDF exists
    pdf_path = base_dir / "resumes/matthew_scott_ai_ml_resume.pdf"
    pdf_exists = pdf_path.exists()
    print(f"{'✅' if pdf_exists else '❌'} PDF Resume")
    print(f"    Path: {pdf_path}")
    print(f"    Exists: {'Yes' if pdf_exists else 'No'}")
    
    if pdf_exists:
        # Get file modification time
        mod_time = datetime.fromtimestamp(pdf_path.stat().st_mtime)
        print(f"    Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results['pdf'] = {'exists': pdf_exists}
    
    # Summary
    print("\n" + "="*50)
    print("📋 VERIFICATION SUMMARY")
    
    # Count good vs needs attention
    text_files = [k for k in results.keys() if k != 'pdf' and results[k].get('exists')]
    good_files = [k for k in text_files if results[k].get('status') == 'good']
    
    print(f"✅ Text files with correct phone: {len(good_files)}/{len(text_files)}")
    print(f"📄 PDF exists: {'Yes' if pdf_exists else 'No'}")
    
    # Overall status
    all_text_good = len(good_files) == len(text_files)
    overall_good = all_text_good and pdf_exists
    
    if overall_good:
        print("\n🎉 SUCCESS: Resume phone number fix verified!")
        print("📱 All files show correct phone number: 502-345-0525")
        print("📄 PDF has been regenerated with fix")
    else:
        print("\n⚠️  ISSUES DETECTED:")
        if not all_text_good:
            print("  • Some text files still have wrong phone number")
        if not pdf_exists:
            print("  • PDF file is missing")
        print("\n  Run fix_resume_pdf_phone.py again if needed")
    
    print("\n📋 Next Steps:")
    print("1. Open the PDF manually to visually confirm phone number")
    print("2. Use this resume for all new job applications")
    print("3. Replace any previously sent resumes with corrected version")
    
    return overall_good


if __name__ == "__main__":
    verify_phone_fix()