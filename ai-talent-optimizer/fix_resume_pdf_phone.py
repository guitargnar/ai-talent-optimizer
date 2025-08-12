#!/usr/bin/env python3
"""
Fix Resume PDF Phone Number Issue

This script addresses the high-priority issue where the PDF resume shows
"502-345-525" instead of the correct "502-345-0525".

Solution approach:
1. Fix the master text resume file
2. Regenerate the PDF with correct phone number
3. Verify the fix worked
4. Provide clear next steps

Usage: python3 fix_resume_pdf_phone.py
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


class ResumePhoneFixer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.master_text = self.base_dir / "output/resume_versions/master_resume_-_all_keywords.txt"
        self.main_pdf = self.base_dir / "resumes/matthew_scott_ai_ml_resume.pdf"
        self.correct_phone = "502-345-0525"
        self.wrong_phone = "502-345-525"
        
    def backup_files(self):
        """Create backups of existing files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup text file
        if self.master_text.exists():
            backup_text = self.master_text.with_suffix(f'.backup_{timestamp}.txt')
            shutil.copy2(self.master_text, backup_text)
            print(f"📋 Backed up text resume to: {backup_text.name}")
        
        # Backup PDF file
        if self.main_pdf.exists():
            backup_pdf = self.main_pdf.with_suffix(f'.backup_{timestamp}.pdf')
            shutil.copy2(self.main_pdf, backup_pdf)
            print(f"📄 Backed up PDF resume to: {backup_pdf.name}")
    
    def fix_master_text_resume(self):
        """Fix phone number in master text resume"""
        if not self.master_text.exists():
            raise FileNotFoundError(f"Master text resume not found: {self.master_text}")
        
        # Read current content
        content = self.master_text.read_text()
        
        # Check if fix is needed
        if self.wrong_phone not in content:
            if self.correct_phone in content:
                print("✅ Phone number already correct in text resume")
                return False
            else:
                print("⚠️  Phone number pattern not found in text resume")
                return False
        
        # Apply fix
        updated_content = content.replace(self.wrong_phone, self.correct_phone)
        
        # Verify the change
        if updated_content == content:
            print("❌ No changes made to text resume")
            return False
        
        # Write updated content
        self.master_text.write_text(updated_content)
        print(f"✅ Fixed phone number in: {self.master_text}")
        return True
    
    def regenerate_pdf(self):
        """Regenerate PDF from corrected text resume"""
        try:
            # Import the PDF generator
            from resume_pdf_generator import ResumePDFGenerator
            
            # Create generator instance
            generator = ResumePDFGenerator()
            
            # Generate new PDF
            generator.text_to_pdf(str(self.master_text), str(self.main_pdf))
            print(f"✅ Regenerated PDF: {self.main_pdf}")
            return True
            
        except ImportError as e:
            print(f"❌ Could not import PDF generator: {e}")
            print("📦 Installing reportlab...")
            import subprocess
            try:
                subprocess.check_call(["pip", "install", "reportlab"])
                print("✅ Reportlab installed, please run script again")
                return False
            except Exception as install_error:
                print(f"❌ Failed to install reportlab: {install_error}")
                return False
                
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            return False
    
    def verify_fix(self):
        """Verify that the phone number has been fixed"""
        verification_results = {}
        
        # Check text file
        if self.master_text.exists():
            text_content = self.master_text.read_text()
            verification_results['text_has_correct'] = self.correct_phone in text_content
            verification_results['text_has_wrong'] = self.wrong_phone in text_content
        
        # Check PDF exists (we can't easily read PDF content)
        verification_results['pdf_exists'] = self.main_pdf.exists()
        
        # Check config file for comparison
        config_file = self.base_dir / "utils/config.py"
        if config_file.exists():
            config_content = config_file.read_text()
            verification_results['config_correct'] = self.correct_phone in config_content
        
        return verification_results
    
    def run_fix(self):
        """Execute the complete fix process"""
        print("🔧 Starting Resume PDF Phone Number Fix")
        print(f"📱 Correct phone: {self.correct_phone}")
        print(f"❌ Wrong phone: {self.wrong_phone}")
        print("-" * 50)
        
        try:
            # Step 1: Create backups
            print("📋 Creating backups...")
            self.backup_files()
            
            # Step 2: Fix text resume
            print("\n📝 Fixing master text resume...")
            text_fixed = self.fix_master_text_resume()
            
            if not text_fixed:
                print("ℹ️  Text resume may already be correct or fix not needed")
            
            # Step 3: Regenerate PDF
            print("\n📄 Regenerating PDF resume...")
            pdf_generated = self.regenerate_pdf()
            
            if not pdf_generated:
                print("❌ PDF regeneration failed")
                return False
            
            # Step 4: Verify fix
            print("\n✅ Verifying fix...")
            results = self.verify_fix()
            
            print(f"  • Text has correct phone: {'✅' if results.get('text_has_correct') else '❌'}")
            print(f"  • Text has wrong phone: {'❌' if results.get('text_has_wrong') else '✅'}")
            print(f"  • PDF file exists: {'✅' if results.get('pdf_exists') else '❌'}")
            print(f"  • Config has correct phone: {'✅' if results.get('config_correct') else '❌'}")
            
            # Final status
            success = (results.get('text_has_correct', False) and 
                      not results.get('text_has_wrong', True) and 
                      results.get('pdf_exists', False))
            
            print("\n" + "="*50)
            if success:
                print("🎉 SUCCESS: Resume PDF phone number has been fixed!")
                print(f"📄 Updated file: {self.main_pdf}")
                print(f"📱 Phone now shows: {self.correct_phone}")
            else:
                print("⚠️  PARTIAL SUCCESS: Some issues remain")
                print("   Manual verification recommended")
            
            print("\n📋 Next Steps:")
            print("1. Check the PDF manually to confirm phone displays correctly")
            print("2. Use the updated PDF for all job applications")
            print("3. Update any existing applications with corrected resume")
            print("4. Archive backup files once verified working")
            
            return success
            
        except Exception as e:
            print(f"❌ Error during fix process: {e}")
            return False


def main():
    """Main execution function"""
    print("Resume PDF Phone Number Fixer")
    print("Fixing: 502-345-525 → 502-345-0525")
    print("="*50)
    
    fixer = ResumePhoneFixer()
    success = fixer.run_fix()
    
    if success:
        print("\n✅ Fix completed successfully!")
        exit(0)
    else:
        print("\n❌ Fix completed with issues")
        print("📞 Manual PDF editing may be required")
        exit(1)


if __name__ == "__main__":
    main()