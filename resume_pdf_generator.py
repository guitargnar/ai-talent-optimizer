#!/usr/bin/env python3
"""
Convert text resumes to professional PDFs
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor
import textwrap

class ResumePDFGenerator:
    """Generate professional PDF resumes from text"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom styles for resume"""
        # Name style
        self.styles.add(ParagraphStyle(
            name='ResumeName',
            parent=self.styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceAfter=6
        ))
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='ResumeTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=14,
            textColor=HexColor('#444444'),
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Contact style
        self.styles.add(ParagraphStyle(
            name='Contact',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            spaceAfter=18
        ))
        
        # Section Header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            leading=14,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=8,
            spaceBefore=12,
            borderPadding=(0, 0, 0, 2),
            borderWidth=1,
            borderColor=HexColor('#1a1a1a')
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='ResumeBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=13,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))
        
        # Bullet points
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
            leftIndent=20,
            spaceAfter=4
        ))
    
    def text_to_pdf(self, text_file: str, pdf_file: str):
        """Convert text resume to PDF"""
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_file,
            pagesize=letter,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        # Read text content
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Build PDF story
        story = []
        
        # Process content line by line
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Name (first non-empty line)
            if i == 0 or (i < 5 and line.isupper() and 'MATTHEW' in line):
                story.append(Paragraph(line, self.styles['ResumeName']))
                i += 1
                continue
            
            # Title (second line)
            if i < 10 and '|' in line and 'Engineer' in line:
                story.append(Paragraph(line, self.styles['ResumeTitle']))
                i += 1
                continue
            
            # Contact info
            if 'Contact:' in line or '@' in line:
                story.append(Paragraph(line, self.styles['Contact']))
                i += 1
                continue
            
            # Section headers (lines with all caps or lines with ===)
            if '=====' in line:
                i += 1
                if i < len(lines):
                    header = lines[i].strip()
                    if header:
                        story.append(Paragraph(header, self.styles['SectionHeader']))
                    i += 1
                    if i < len(lines) and '=====' in lines[i]:
                        i += 1
                continue
            
            # Bullet points
            if line.startswith('•') or line.startswith('-'):
                # Clean up bullet point
                bullet_text = line[1:].strip()
                story.append(Paragraph(f"• {bullet_text}", self.styles['BulletPoint']))
                i += 1
                continue
            
            # Company/Position headers (contains dates or company names)
            if any(year in line for year in ['2022', '2023', '2024', '2025']) or line.endswith('Present'):
                story.append(Spacer(1, 6))
                story.append(Paragraph(f"<b>{line}</b>", self.styles['ResumeBody']))
                i += 1
                continue
            
            # Regular body text
            story.append(Paragraph(line, self.styles['ResumeBody']))
            i += 1
        
        # Build PDF
        doc.build(story)
        print(f"✅ Generated PDF: {pdf_file}")
    
    def convert_all_resumes(self, input_dir: str = "output/resume_versions", 
                           output_dir: str = "resumes"):
        """Convert all text resumes to PDFs"""
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all text files
        input_path = Path(input_dir)
        text_files = list(input_path.glob("*.txt"))
        
        converted = []
        for text_file in text_files:
            if "report" in text_file.name.lower():
                continue  # Skip report files
                
            # Generate PDF filename
            pdf_name = text_file.stem.replace('_', '_') + '.pdf'
            pdf_path = Path(output_dir) / pdf_name
            
            # Convert to PDF
            self.text_to_pdf(str(text_file), str(pdf_path))
            converted.append({
                'text': str(text_file),
                'pdf': str(pdf_path),
                'name': text_file.stem
            })
        
        # Create a main resume (master version)
        master_text = Path(input_dir) / "master_resume_-_all_keywords.txt"
        if master_text.exists():
            main_pdf = Path(output_dir) / "matthew_scott_ai_ml_resume.pdf"
            self.text_to_pdf(str(master_text), str(main_pdf))
            print(f"✅ Created main resume: {main_pdf}")
        
        return converted


def main():
    """Generate PDF resumes"""
    generator = ResumePDFGenerator()
    
    print("📄 Converting resumes to PDF...")
    converted = generator.convert_all_resumes()
    
    print(f"\n✅ Converted {len(converted)} resumes:")
    for item in converted:
        print(f"  • {item['name']}")
    
    print("\n📎 PDFs ready for email attachments!")


if __name__ == "__main__":
    # Check if reportlab is installed
    try:
        import reportlab
    except ImportError:
        print("❌ reportlab not installed. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab"])
        print("✅ reportlab installed. Please run the script again.")
        exit(1)
    
    main()