# 📄 Resume Usage Guide - Which Resume Is Used Where

## Summary of Resume Systems

### 1. 🇪🇺 European Job Applications
**Type**: Custom-generated text resumes for each position  
**Location**: `resumes/european/`  
**Format**: Plain text (.txt) - needs PDF conversion  
**Count**: 10 unique resumes created  

Each resume is **specifically tailored** to the job with:
- Company-specific project examples
- Matched requirements from job posting
- Country-specific visa eligibility statements
- Localized formatting (UK £, EU €, Swedish SEK)

### 2. 🔗 LinkedIn Easy Apply
**Type**: Single PDF resume for all applications  
**Location**: `resumes/matthew_scott_2025_professional_resume.pdf`  
**Format**: PDF (59KB)  
**Usage**: Uploaded automatically by Selenium  

This is your **general resume** that gets attached to all LinkedIn Easy Apply applications.

### 3. 📧 Email Applications
**Type**: Various PDF resumes based on role type  
**Options Available**:
- `matthew_scott_ai_ml_engineer_resume.pdf` - General AI/ML roles
- `matthew_scott_healthcare_tech_resume.pdf` - Healthcare companies
- `matthew_scott_principal_engineer_resume.pdf` - Senior/Principal roles
- `matthew_scott_startup_resume.pdf` - Startup positions
- `matthew_scott_platform_engineer_resume.pdf` - Platform/Infrastructure

## Which Resume for Which Company?

### European Companies (Custom Generated)
| Company | Resume File | Key Emphasis |
|---------|------------|--------------|
| DeepMind | `DeepMind_Senior_Machine_Learning_Engineer.txt` | Research, 7 LLMs, healthcare AI |
| Spotify | `Spotify_Principal_Engineer_-_ML_Platform.txt` | Recommendation systems, scale |
| Booking.com | `Booking.com_Staff_ML_Engineer_-_Personalization.txt` | E-commerce ML, personalization |
| Revolut | `Revolut_Lead_ML_Engineer_-_Fraud_Detection.txt` | Fraud detection, financial ML |
| Adyen | `Adyen_Principal_Engineer_-_ML_Platform.txt` | Payment systems, platform eng |
| Zalando | `Zalando_Senior_AI_Engineer_-_Fashion_Tech.txt` | Computer vision, e-commerce |
| Datadog | `Datadog_Staff_Engineer_-_AI_Observability.txt` | Observability, monitoring |
| Klarna | `Klarna_Senior_ML_Engineer_-_Credit_Risk.txt` | Credit risk, financial modeling |
| Meta Dublin | `Meta_Dublin_ML_Engineer_-_Reality_Labs.txt` | Computer vision, AR/VR |
| SAP | `SAP_Principal_AI_Architect.txt` | Enterprise architecture, MLOps |

### US Companies (PDF Resumes)
- **Default**: `matthew_scott_2025_professional_resume.pdf` (59KB)
- **Healthcare**: Use `matthew_scott_healthcare_tech_resume.pdf`
- **Startups**: Use `matthew_scott_startup_resume.pdf`
- **Principal Roles**: Use `matthew_scott_principal_engineer_resume.pdf`

## How to Convert European Resumes to PDF

The European resumes are in text format and need conversion:

```bash
# Option 1: Use a text-to-PDF converter
# Install first: brew install pandoc
pandoc resumes/european/DeepMind_Senior_Machine_Learning_Engineer.txt \
  -o resumes/european/DeepMind_Senior_Machine_Learning_Engineer.pdf

# Option 2: Open in text editor and print to PDF
open resumes/european/DeepMind_Senior_Machine_Learning_Engineer.txt
# Then File -> Print -> Save as PDF

# Option 3: Use Python script (we can create one)
python3 convert_resumes_to_pdf.py
```

## Key Information Across All Resumes

### Consistent Points (All Resumes Include):
✅ **10 years at Humana** (2015-Present)  
✅ **$1.2M annual savings** through ML automation  
✅ **7 specialized LLMs** in Mirador platform  
✅ **100% Medicare compliance** record  
✅ **117 Python modules** in production  

### Variable Points (Customized per Job):
- **European**: Visa sponsorship eligibility, GDPR experience
- **Healthcare**: Medicare/CMS expertise, HIPAA compliance  
- **Startups**: Scrappy problem-solving, rapid prototyping
- **Principal**: Leadership experience, architecture design
- **Platform**: Infrastructure, scaling, DevOps

## Quick Commands

```bash
# View all European resumes
ls -la resumes/european/

# View main PDF resume
open resumes/matthew_scott_2025_professional_resume.pdf

# Check which resume LinkedIn uses
grep resume_path linkedin_config.json

# Count total resumes available
find resumes -name "*.pdf" -o -name "*.txt" | wc -l
```

## Recommendations

1. **For European applications**: Use the custom `.txt` resumes and convert to PDF
2. **For LinkedIn Easy Apply**: Current PDF is good (59KB, comprehensive)
3. **For direct email**: Choose PDF based on company type
4. **For US companies**: Use the main professional resume PDF

---

*Last updated: 2025-08-21*  
*Total resumes available: 18 (10 European custom + 8 US PDFs)*