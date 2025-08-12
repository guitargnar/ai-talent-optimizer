"""
Unit tests for application generation
"""

import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest


class TestResumeGeneration:
    """Test resume generation functionality"""

    @pytest.fixture
    def job_description(self):
        """Sample job description"""
        return {
            "company": "TechCorp",
            "position": "Senior ML Engineer",
            "description": """
                We are seeking a Senior ML Engineer with experience in:
                - PyTorch and TensorFlow
                - Distributed systems
                - MLOps and model deployment
                - Python and cloud platforms
            """,
            "requirements": [
                "5+ years ML experience",
                "MS/PhD in CS or related",
                "Production ML systems",
            ],
        }

    @pytest.fixture
    def base_resume(self):
        """Base resume data"""
        return {
            "name": "Matthew Scott",
            "email": "matthewdscott7@gmail.com",
            "phone": "(502) 345-0525",
            "linkedin": "linkedin.com/in/mscott77",
            "experience": [
                {
                    "title": "VP AI Strategy",
                    "company": "Humana",
                    "dates": "2020-2024",
                    "achievements": [
                        "Led AI initiatives saving $1.2M annually",
                        "Deployed ML models to production",
                        "Built distributed AI systems",
                    ],
                }
            ],
            "skills": ["Python", "PyTorch", "TensorFlow", "MLOps", "AWS"],
            "education": "MS Computer Science",
        }

    @pytest.mark.unit
    def test_keyword_extraction(self, job_description):
        """Test keyword extraction from job description"""

        def extract_keywords(description):
            """Extract relevant keywords"""
            keywords = []
            tech_terms = [
                "pytorch",
                "tensorflow",
                "python",
                "mlops",
                "aws",
                "gcp",
                "azure",
                "kubernetes",
                "docker",
                "ml",
                "ai",
            ]

            desc_lower = description.lower()
            for term in tech_terms:
                if term in desc_lower:
                    keywords.append(term)

            return keywords

        keywords = extract_keywords(job_description["description"])

        assert "pytorch" in keywords
        assert "tensorflow" in keywords
        assert "python" in keywords
        assert "mlops" in keywords

    @pytest.mark.unit
    def test_resume_tailoring(self, job_description, base_resume):
        """Test resume tailoring to job description"""

        def tailor_resume(resume, job_desc):
            """Tailor resume to job requirements"""
            tailored = resume.copy()

            # Extract keywords from job
            job_text = job_desc["description"].lower()

            # Reorder skills based on job requirements
            mentioned_skills = []
            other_skills = []

            for skill in resume["skills"]:
                if skill.lower() in job_text:
                    mentioned_skills.append(skill)
                else:
                    other_skills.append(skill)

            tailored["skills"] = mentioned_skills + other_skills

            # Add job-specific objective
            tailored["objective"] = f"Seeking {job_desc['position']} role at {job_desc['company']}"

            return tailored

        tailored = tailor_resume(base_resume, job_description)

        assert tailored["objective"] == "Seeking Senior ML Engineer role at TechCorp"
        assert tailored["skills"][0] in ["Python", "PyTorch", "TensorFlow", "MLOps"]

    @pytest.mark.unit
    def test_ats_optimization(self, base_resume):
        """Test ATS (Applicant Tracking System) optimization"""

        def calculate_ats_score(resume, job_keywords):
            """Calculate ATS compatibility score"""
            score = 0
            resume_text = json.dumps(resume).lower()

            for keyword in job_keywords:
                if keyword.lower() in resume_text:
                    score += 10

            # Check for proper formatting
            if "name" in resume and "email" in resume:
                score += 20
            if "experience" in resume:
                score += 10
            if "skills" in resume:
                score += 10

            return min(score, 100)  # Cap at 100

        job_keywords = ["Python", "ML", "PyTorch", "Production", "Distributed"]
        score = calculate_ats_score(base_resume, job_keywords)

        assert score >= 50  # Should have decent ATS score
        assert score <= 100


class TestCoverLetterGeneration:
    """Test cover letter generation"""

    @pytest.fixture
    def company_research(self):
        """Mock company research data"""
        return {
            "company": "TechCorp",
            "mission": "Building AI for good",
            "recent_news": "Raised $100M Series C",
            "culture": "Innovation and collaboration",
            "products": ["AI Platform", "ML Tools"],
        }

    @pytest.mark.unit
    def test_cover_letter_structure(self):
        """Test cover letter has proper structure"""

        def generate_cover_letter(company, position, highlights):
            """Generate cover letter"""
            letter = f"""Dear Hiring Team at {company},

I am writing to express my strong interest in the {position} position.

{highlights}

I would welcome the opportunity to discuss how my experience can contribute to {company}'s success.

Best regards,
Matthew Scott"""
            return letter

        letter = generate_cover_letter(
            "TechCorp",
            "ML Engineer",
            "With 10+ years of experience in ML and proven success at Humana...",
        )

        assert "Dear Hiring Team" in letter
        assert "TechCorp" in letter
        assert "ML Engineer" in letter
        assert "Best regards" in letter
        assert "Matthew Scott" in letter

    @pytest.mark.unit
    def test_company_research_integration(self, company_research):
        """Test integration of company research into cover letter"""

        def add_company_specifics(letter_template, research):
            """Add company-specific details"""
            additions = []

            if "mission" in research:
                additions.append(
                    f"I am particularly drawn to {research['company']}'s mission of {research['mission']}"
                )

            if "recent_news" in research:
                additions.append(
                    f"I was excited to learn about your recent achievement: {research['recent_news']}"
                )

            return additions

        specifics = add_company_specifics("", company_research)

        assert len(specifics) >= 2
        assert "Building AI for good" in specifics[0]
        assert "$100M Series C" in specifics[1]

    @pytest.mark.unit
    def test_achievement_highlighting(self):
        """Test highlighting relevant achievements"""
        achievements = [
            "$1.2M annual savings through AI",
            "10+ years healthcare technology",
            "Led teams of 5-10 engineers",
            "Published ML research papers",
        ]

        def select_top_achievements(achievements, job_focus, limit=3):
            """Select most relevant achievements"""
            scores = []

            for achievement in achievements:
                score = 0
                if "$" in achievement:  # Quantifiable impact
                    score += 3
                if any(word in achievement.lower() for word in job_focus):
                    score += 2
                if "led" in achievement.lower() or "managed" in achievement.lower():
                    score += 1

                scores.append((achievement, score))

            scores.sort(key=lambda x: x[1], reverse=True)
            return [ach for ach, _ in scores[:limit]]

        job_focus = ["ai", "ml", "savings", "technology"]
        top = select_top_achievements(achievements, job_focus)

        assert len(top) == 3
        assert "$1.2M annual savings through AI" in top  # Should be highest scored


class TestApplicationTracking:
    """Test application tracking functionality"""

    @pytest.mark.unit
    def test_application_logging(self, tmp_path):
        """Test logging applications to file"""
        log_file = tmp_path / "applications.json"

        application = {
            "company": "TechCorp",
            "position": "ML Engineer",
            "date": datetime.now().isoformat(),
            "status": "sent",
            "email": "careers@techcorp.com",
        }

        # Write application
        with open(log_file, "w") as f:
            json.dump([application], f)

        # Read and verify
        with open(log_file, "r") as f:
            logged = json.load(f)

        assert len(logged) == 1
        assert logged[0]["company"] == "TechCorp"
        assert logged[0]["status"] == "sent"

    @pytest.mark.unit
    def test_duplicate_application_detection(self):
        """Test detection of duplicate applications"""
        sent_applications = [
            ("TechCorp", "ML Engineer"),
            ("DataCo", "Data Scientist"),
            ("AIStartup", "Research Engineer"),
        ]

        def is_duplicate(company, position, sent_list):
            """Check if application is duplicate"""
            return (company, position) in sent_list

        assert is_duplicate("TechCorp", "ML Engineer", sent_applications) == True
        assert is_duplicate("NewCorp", "ML Engineer", sent_applications) == False
        assert is_duplicate("TechCorp", "Data Scientist", sent_applications) == False

    @pytest.mark.unit
    @patch("builtins.open", new_callable=mock_open)
    def test_application_folder_creation(self, mock_file):
        """Test creation of application folders"""

        def create_application_folder(company, position, date):
            """Create folder structure for application"""
            folder_name = f"{date}_{company.replace(' ', '_')}_{position.replace(' ', '_')}"
            files = {
                "resume.pdf": "resume_content",
                "cover_letter.txt": "letter_content",
                "company_research.json": '{"research": "data"}',
                "application_metadata.json": '{"status": "sent"}',
            }
            return folder_name, files

        folder, files = create_application_folder("Tech Corp", "ML Engineer", "2024-01-15")

        assert folder == "2024-01-15_Tech_Corp_ML_Engineer"
        assert "resume.pdf" in files
        assert "cover_letter.txt" in files
        assert "company_research.json" in files
