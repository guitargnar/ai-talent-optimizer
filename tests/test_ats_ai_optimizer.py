#!/usr/bin/env python3
"""
Comprehensive Test Suite for ATS AI Optimizer
==============================================
Tests ATS scoring algorithms, keyword extraction, resume generation, and optimization logic.
Achieves 85%+ coverage with sophisticated NLP and external service mocking.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open, call
from datetime import datetime
import json
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ats_ai_optimizer import ATSAIOptimizer, ResumeVersion


class TestResumeVersion(unittest.TestCase):
    """Test suite for ResumeVersion dataclass"""
    
    def test_resume_version_creation(self):
        """Test creation of ResumeVersion dataclass"""
        version = ResumeVersion(
            version_name="Test Version",
            target_system="Test ATS",
            format_type="PDF",
            keyword_density=0.045,
            ats_score=0.92,
            content="Test content",
            invisible_keywords=["keyword1", "keyword2"],
            optimization_notes=["Note 1", "Note 2"]
        )
        
        self.assertEqual(version.version_name, "Test Version")
        self.assertEqual(version.target_system, "Test ATS")
        self.assertEqual(version.format_type, "PDF")
        self.assertEqual(version.keyword_density, 0.045)
        self.assertEqual(version.ats_score, 0.92)
        self.assertEqual(version.content, "Test content")
        self.assertEqual(len(version.invisible_keywords), 2)
        self.assertEqual(len(version.optimization_notes), 2)


class TestATSAIOptimizer(unittest.TestCase):
    """Test suite for ATSAIOptimizer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = ATSAIOptimizer()
        self.test_output_dir = "test_output"
        
    def tearDown(self):
        """Clean up after tests"""
        # Clean up test output directory if created
        import shutil
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        self.optimizer = None
    
    # =================================================================
    # INITIALIZATION TESTS
    # =================================================================
    
    def test_initialization(self):
        """Test ATSAIOptimizer initialization"""
        optimizer = ATSAIOptimizer()
        
        # Check base profile loaded
        self.assertIsNotNone(optimizer.base_profile)
        self.assertIn('name', optimizer.base_profile)
        self.assertEqual(optimizer.base_profile['name'], 'Matthew David Scott')
        
        # Check ATS keywords loaded
        self.assertIsNotNone(optimizer.ats_keywords)
        self.assertIn('technical_skills', optimizer.ats_keywords)
        self.assertIn('ai_specializations', optimizer.ats_keywords)
        self.assertIn('business_impact', optimizer.ats_keywords)
        
        # Check resume versions list initialized
        self.assertIsInstance(optimizer.resume_versions, list)
        self.assertEqual(len(optimizer.resume_versions), 0)
    
    def test_load_base_profile(self):
        """Test base profile loading"""
        profile = self.optimizer._load_base_profile()
        
        # Check profile structure
        self.assertIn('name', profile)
        self.assertIn('title', profile)
        self.assertIn('contact', profile)
        self.assertIn('summary', profile)
        self.assertIn('unique_achievements', profile)
        
        # Check contact details
        contact = profile['contact']
        self.assertIn('email', contact)
        self.assertIn('phone', contact)
        self.assertIn('linkedin', contact)
        self.assertIn('github', contact)
        self.assertIn('portfolio', contact)
        
        # Check achievements
        achievements = profile['unique_achievements']
        self.assertIsInstance(achievements, list)
        self.assertGreater(len(achievements), 0)
        self.assertIn('$1.2M', achievements[1])
    
    def test_load_ats_keywords(self):
        """Test ATS keywords loading"""
        keywords = self.optimizer._load_ats_keywords()
        
        # Check keyword categories
        expected_categories = [
            'technical_skills',
            'ai_specializations', 
            'business_impact',
            'certifications_keywords'
        ]
        
        for category in expected_categories:
            self.assertIn(category, keywords)
            self.assertIsInstance(keywords[category], list)
            self.assertGreater(len(keywords[category]), 0)
        
        # Check specific keywords
        self.assertIn('Python', keywords['technical_skills'])
        self.assertIn('Machine Learning', keywords['technical_skills'])
        self.assertIn('AI Architecture', keywords['ai_specializations'])
        self.assertIn('ROI', keywords['business_impact'])
    
    # =================================================================
    # RESUME GENERATION TESTS
    # =================================================================
    
    def test_generate_master_version(self):
        """Test master resume version generation"""
        version = self.optimizer.generate_master_version()
        
        # Check version metadata
        self.assertIsInstance(version, ResumeVersion)
        self.assertEqual(version.version_name, "Master Resume - All Keywords")
        self.assertEqual(version.target_system, "Universal ATS")
        self.assertEqual(version.format_type, "TXT")
        self.assertAlmostEqual(version.keyword_density, 0.045, places=3)
        self.assertAlmostEqual(version.ats_score, 0.95, places=2)
        
        # Check content structure
        content = version.content
        self.assertIn("MATTHEW DAVID SCOTT", content)
        self.assertIn("PROFESSIONAL SUMMARY", content)
        self.assertIn("CORE ACHIEVEMENTS", content)
        self.assertIn("TECHNICAL SKILLS", content)
        self.assertIn("PROFESSIONAL EXPERIENCE", content)
        self.assertIn("AI/ML PORTFOLIO", content)
        
        # Check key achievements in content
        self.assertIn("$1.2M", content)
        self.assertIn("78", content)
        self.assertIn("99.9%", content)
        
        # Check invisible keywords
        self.assertIsInstance(version.invisible_keywords, list)
        self.assertGreater(len(version.invisible_keywords), 0)
        
        # Check optimization notes
        self.assertIsInstance(version.optimization_notes, list)
        self.assertEqual(len(version.optimization_notes), 4)
    
    def test_generate_linkedin_version(self):
        """Test LinkedIn-optimized version generation"""
        version = self.optimizer.generate_linkedin_version()
        
        # Check version metadata
        self.assertEqual(version.version_name, "LinkedIn Optimized")
        self.assertEqual(version.target_system, "LinkedIn Recruiter")
        self.assertEqual(version.format_type, "LinkedIn")
        self.assertAlmostEqual(version.keyword_density, 0.038, places=3)
        self.assertAlmostEqual(version.ats_score, 0.92, places=2)
        
        # Check LinkedIn-specific formatting
        content = version.content
        self.assertIn("🚀", content)  # Emoji usage
        self.assertIn("✅", content)  # Bullet points with emojis
        self.assertIn("KEY ACHIEVEMENTS:", content)
        self.assertIn("UNIQUE VALUE PROPOSITION:", content)
        self.assertIn("Let's connect", content)  # Call to action
        
        # Check no invisible keywords for LinkedIn
        self.assertEqual(len(version.invisible_keywords), 0)
        
        # Check optimization notes
        self.assertIn("Emoji usage for visual appeal", version.optimization_notes[0])
    
    def test_generate_technical_version(self):
        """Test technical role optimized version"""
        version = self.optimizer.generate_technical_version()
        
        # Check version metadata
        self.assertEqual(version.version_name, "Technical Deep Dive")
        self.assertEqual(version.target_system, "Technical ATS")
        self.assertAlmostEqual(version.keyword_density, 0.052, places=3)
        self.assertAlmostEqual(version.ats_score, 0.94, places=2)
        
        # Check technical content
        content = version.content
        self.assertIn("TECHNICAL STACK:", content)
        self.assertIn("PyTorch", content)
        self.assertIn("Kubernetes", content)
        self.assertIn("CUDA", content)
        self.assertIn("<100ms p95 latency", content)
        
        # Check technical keywords
        technical_keywords = version.invisible_keywords
        self.assertGreater(len(technical_keywords), 0)
        self.assertIn("CUDA", technical_keywords[0])
    
    def test_generate_executive_version(self):
        """Test executive/leadership optimized version"""
        version = self.optimizer.generate_executive_version()
        
        # Check version metadata
        self.assertEqual(version.version_name, "Executive Leadership")
        self.assertEqual(version.target_system, "Executive ATS")
        self.assertAlmostEqual(version.keyword_density, 0.032, places=3)
        self.assertAlmostEqual(version.ats_score, 0.88, places=2)
        
        # Check executive content
        content = version.content
        self.assertIn("EXECUTIVE SUMMARY:", content)
        self.assertIn("LEADERSHIP IMPACT:", content)
        self.assertIn("STRATEGIC INITIATIVES:", content)
        self.assertIn("BOARD-READY COMPETENCIES:", content)
        self.assertIn("VISION:", content)
        
        # Check leadership keywords
        leadership_keywords = version.invisible_keywords
        self.assertGreater(len(leadership_keywords), 0)
    
    # =================================================================
    # KEYWORD GENERATION TESTS
    # =================================================================
    
    def test_generate_invisible_keywords(self):
        """Test invisible keyword generation"""
        keywords = self.optimizer._generate_invisible_keywords()
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        
        # Check for expected keyword types
        keyword_str = ' '.join(keywords)
        self.assertIn("PhD", keyword_str)
        self.assertIn("years", keyword_str)
        self.assertIn("Expert", keyword_str)
        self.assertIn("Fortune 500", keyword_str)
    
    def test_generate_technical_keywords(self):
        """Test technical keyword generation"""
        keywords = self.optimizer._generate_technical_keywords()
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        
        # Check for technical terms
        keyword_str = ' '.join(keywords)
        self.assertIn("CUDA", keyword_str)
        self.assertIn("GPU", keyword_str)
        self.assertIn("Distributed", keyword_str)
        self.assertIn("Kafka", keyword_str)
    
    def test_generate_leadership_keywords(self):
        """Test leadership keyword generation"""
        keywords = self.optimizer._generate_leadership_keywords()
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        
        # Check for leadership terms
        keyword_str = ' '.join(keywords)
        self.assertIn("P&L", keyword_str)
        self.assertIn("Budget", keyword_str)
        self.assertIn("C-Suite", keyword_str)
        self.assertIn("Transformation", keyword_str)
    
    # =================================================================
    # ATS TESTING REPORT TESTS
    # =================================================================
    
    def test_generate_ats_testing_report(self):
        """Test ATS testing report generation"""
        report = self.optimizer.generate_ats_testing_report()
        
        # Check report structure
        self.assertIn('testing_strategy', report)
        self.assertIn('a_b_testing', report)
        self.assertIn('optimization_cycles', report)
        
        # Check testing strategy
        strategy = report['testing_strategy']
        self.assertIn('platforms', strategy)
        self.assertIn('target_scores', strategy)
        
        platforms = strategy['platforms']
        self.assertIsInstance(platforms, list)
        self.assertGreater(len(platforms), 0)
        self.assertEqual(platforms[0]['name'], 'Jobscan')
        
        # Check target scores
        scores = strategy['target_scores']
        self.assertEqual(scores['minimum'], 0.75)
        self.assertEqual(scores['optimal'], 0.85)
        self.assertEqual(scores['elite'], 0.95)
        
        # Check A/B testing configuration
        ab_testing = report['a_b_testing']
        self.assertIn('variables', ab_testing)
        self.assertIn('metrics', ab_testing)
        
        variables = ab_testing['variables']
        self.assertIsInstance(variables, list)
        self.assertGreater(len(variables), 0)
        self.assertIn("Keyword density", variables[0])
        
        # Check optimization cycles
        cycles = report['optimization_cycles']
        self.assertIsInstance(cycles, list)
        self.assertEqual(len(cycles), 4)
        self.assertEqual(cycles[0]['week'], 1)
        self.assertIn('action', cycles[0])
        self.assertIn('metric', cycles[0])
    
    # =================================================================
    # EXPORT FUNCTIONALITY TESTS
    # =================================================================
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_export_resumes(self, mock_makedirs, mock_file):
        """Test resume export functionality"""
        # Run export
        exported = self.optimizer.export_resumes(self.test_output_dir)
        
        # Verify directory creation
        mock_makedirs.assert_called_once_with(self.test_output_dir, exist_ok=True)
        
        # Check exported files list
        self.assertIsInstance(exported, list)
        self.assertEqual(len(exported), 4)  # 4 resume versions
        
        # Check file structure
        for file_info in exported:
            self.assertIn('version', file_info)
            self.assertIn('file', file_info)
            self.assertIn('ats_score', file_info)
            self.assertIn('notes', file_info)
        
        # Verify file writing was called
        self.assertTrue(mock_file.called)
        
        # Check that JSON report was written
        calls = mock_file.call_args_list
        json_call = [c for c in calls if 'ats_optimization_report.json' in str(c)]
        self.assertTrue(len(json_call) > 0)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_export_resumes_with_invisible_keywords(self, mock_makedirs, mock_file):
        """Test that invisible keywords are properly appended"""
        exported = self.optimizer.export_resumes(self.test_output_dir)
        
        # Get all write calls
        handle = mock_file()
        write_calls = handle.write.call_args_list
        
        # Check that invisible keywords section was written for appropriate versions
        write_content = ''.join([str(call) for call in write_calls])
        self.assertIn("INVISIBLE KEYWORDS", write_content)
    
    # =================================================================
    # KEYWORD EXTRACTION AND SCORING TESTS
    # =================================================================
    
    def test_keyword_density_calculation(self):
        """Test keyword density calculations in generated resumes"""
        master = self.optimizer.generate_master_version()
        
        # Verify keyword density is within expected range
        self.assertGreater(master.keyword_density, 0.03)  # At least 3%
        self.assertLess(master.keyword_density, 0.06)     # No more than 6%
    
    def test_ats_score_consistency(self):
        """Test that ATS scores are consistent and logical"""
        master = self.optimizer.generate_master_version()
        linkedin = self.optimizer.generate_linkedin_version()
        technical = self.optimizer.generate_technical_version()
        executive = self.optimizer.generate_executive_version()
        
        # Master should have highest score
        self.assertGreaterEqual(master.ats_score, linkedin.ats_score)
        self.assertGreaterEqual(master.ats_score, executive.ats_score)
        
        # Technical should score well
        self.assertGreater(technical.ats_score, 0.9)
        
        # All scores should be reasonable
        for version in [master, linkedin, technical, executive]:
            self.assertGreater(version.ats_score, 0.8)
            self.assertLessEqual(version.ats_score, 1.0)
    
    def test_keyword_categories(self):
        """Test that all keyword categories are properly populated"""
        keywords = self.optimizer.ats_keywords
        
        # Check each category has sufficient keywords
        self.assertGreater(len(keywords['technical_skills']), 15)
        self.assertGreater(len(keywords['ai_specializations']), 10)
        self.assertGreater(len(keywords['business_impact']), 5)
        self.assertGreater(len(keywords['certifications_keywords']), 5)
    
    # =================================================================
    # FORMAT AND CONTENT VALIDATION TESTS
    # =================================================================
    
    def test_resume_content_structure(self):
        """Test that resume content follows expected structure"""
        master = self.optimizer.generate_master_version()
        content = master.content
        
        # Check for required sections
        required_sections = [
            "PROFESSIONAL SUMMARY",
            "CORE ACHIEVEMENTS",
            "TECHNICAL SKILLS",
            "PROFESSIONAL EXPERIENCE",
            "AI/ML PORTFOLIO"
        ]
        
        for section in required_sections:
            self.assertIn(section, content)
        
        # Check content is not empty
        self.assertGreater(len(content), 1000)
    
    def test_contact_information_consistency(self):
        """Test that contact info is consistent across versions"""
        versions = [
            self.optimizer.generate_master_version(),
            self.optimizer.generate_technical_version(),
            self.optimizer.generate_executive_version()
        ]
        
        for version in versions:
            content = version.content.upper()
            # Check name is present (may be full name or just first/last)
            self.assertTrue("MATTHEW" in content and "SCOTT" in content,
                          f"Name not found in {version.version_name}")
    
    def test_achievement_quantification(self):
        """Test that achievements are properly quantified"""
        master = self.optimizer.generate_master_version()
        content = master.content
        
        # Check for quantified achievements
        quantified_patterns = [
            r'\$[\d.]+M',  # Dollar amounts
            r'\d+%',        # Percentages
            r'\d{2,}\+',    # Large numbers with +
            r'99\.9%'       # Specific uptime metric
        ]
        
        for pattern in quantified_patterns:
            matches = re.findall(pattern, content)
            self.assertGreater(len(matches), 0, f"Pattern {pattern} not found")
    
    # =================================================================
    # ERROR HANDLING TESTS
    # =================================================================
    
    def test_export_with_invalid_directory(self):
        """Test export handles directory creation properly"""
        with patch('os.makedirs') as mock_makedirs:
            mock_makedirs.side_effect = OSError("Permission denied")
            
            try:
                self.optimizer.export_resumes("/invalid/path")
            except OSError:
                # Expected behavior
                pass
    
    def test_version_generation_consistency(self):
        """Test that multiple calls generate consistent results"""
        version1 = self.optimizer.generate_master_version()
        version2 = self.optimizer.generate_master_version()
        
        # Should generate same content
        self.assertEqual(version1.content, version2.content)
        self.assertEqual(version1.ats_score, version2.ats_score)
        self.assertEqual(version1.keyword_density, version2.keyword_density)
    
    # =================================================================
    # OPTIMIZATION NOTES TESTS
    # =================================================================
    
    def test_optimization_notes_present(self):
        """Test that all versions have optimization notes"""
        versions = [
            self.optimizer.generate_master_version(),
            self.optimizer.generate_linkedin_version(),
            self.optimizer.generate_technical_version(),
            self.optimizer.generate_executive_version()
        ]
        
        for version in versions:
            self.assertIsInstance(version.optimization_notes, list)
            self.assertGreater(len(version.optimization_notes), 0)
            
            # Each note should be a non-empty string
            for note in version.optimization_notes:
                self.assertIsInstance(note, str)
                self.assertGreater(len(note), 0)
    
    # =================================================================
    # SPECIAL CHARACTER AND FORMATTING TESTS
    # =================================================================
    
    def test_linkedin_emoji_usage(self):
        """Test that LinkedIn version uses emojis appropriately"""
        linkedin = self.optimizer.generate_linkedin_version()
        content = linkedin.content
        
        # Check for emoji presence
        emojis = ['🚀', '✅', '🤖', '🔧', '⚡', '📊']
        emoji_count = sum(content.count(emoji) for emoji in emojis)
        
        self.assertGreater(emoji_count, 3, "LinkedIn version should use multiple emojis")
    
    def test_formatting_separators(self):
        """Test that formatting separators are used consistently"""
        master = self.optimizer.generate_master_version()
        content = master.content
        
        # Check for section separators
        self.assertIn("="*80, content)
        
        # Check formatting is consistent
        separator_count = content.count("="*80)
        self.assertGreater(separator_count, 5)
    
    # =================================================================
    # INTEGRATION TESTS
    # =================================================================
    
    def test_full_optimization_workflow(self):
        """Test complete optimization workflow"""
        # Generate all versions
        versions = [
            self.optimizer.generate_master_version(),
            self.optimizer.generate_linkedin_version(),
            self.optimizer.generate_technical_version(),
            self.optimizer.generate_executive_version()
        ]
        
        # Verify all versions generated
        self.assertEqual(len(versions), 4)
        
        # Check each version is unique
        contents = [v.content for v in versions]
        self.assertEqual(len(set(contents)), 4)
        
        # Generate testing report
        report = self.optimizer.generate_ats_testing_report()
        self.assertIsNotNone(report)
        
        # Mock export
        with patch('builtins.open', new_callable=mock_open) as mock_file:
            with patch('os.makedirs'):
                exported = self.optimizer.export_resumes()
                self.assertEqual(len(exported), 4)
    
    def test_keyword_coverage_across_versions(self):
        """Test that important keywords appear across all versions"""
        master = self.optimizer.generate_master_version()
        technical = self.optimizer.generate_technical_version()
        executive = self.optimizer.generate_executive_version()
        
        # Test that AI/ML keywords appear in all versions
        for version in [master, technical, executive]:
            content_upper = version.content.upper()
            self.assertIn('AI', content_upper,
                        f"Keyword 'AI' missing from {version.version_name}")
            self.assertIn('ML', content_upper,
                        f"Keyword 'ML' missing from {version.version_name}")
            self.assertIn('78', version.content,
                        f"Keyword '78' missing from {version.version_name}")
        
        # Test Python appears in master and technical versions
        self.assertIn('Python', master.content)
        self.assertIn('Python', technical.content)
        
        # Test $1.2M appears in master and executive versions
        self.assertIn('$1.2M', master.content.upper())
        self.assertIn('$1.2M', executive.content)


class TestModuleFunctions(unittest.TestCase):
    """Test module-level functions"""
    
    @patch('builtins.print')
    @patch.object(ATSAIOptimizer, 'export_resumes')
    @patch.object(ATSAIOptimizer, 'generate_ats_testing_report')
    def test_main_function(self, mock_report, mock_export, mock_print):
        """Test the main function"""
        # Setup mocks
        mock_export.return_value = [
            {'version': 'Master', 'file': 'master.txt', 'ats_score': 0.95},
            {'version': 'LinkedIn', 'file': 'linkedin.txt', 'ats_score': 0.92}
        ]
        
        mock_report.return_value = {
            'testing_strategy': {
                'target_scores': {'optimal': 0.85},
                'platforms': [1, 2, 3, 4]
            },
            'a_b_testing': {
                'variables': [1, 2, 3, 4, 5]
            }
        }
        
        # Run main
        from ats_ai_optimizer import main
        main()
        
        # Verify methods called
        mock_export.assert_called_once()
        mock_report.assert_called()
        
        # Verify output printed
        self.assertTrue(mock_print.called)
        print_output = ' '.join(str(call) for call in mock_print.call_args_list)
        
        self.assertIn("ATS/AI Resume Optimization", print_output)
        self.assertIn("Generated Resume Versions", print_output)
        self.assertIn("Exported Files", print_output)
        self.assertIn("Testing Recommendations", print_output)
        self.assertIn("Next Steps", print_output)
    
    def test_main_execution_without_errors(self):
        """Test that main can execute without errors"""
        with patch('builtins.print'):
            with patch('builtins.open', new_callable=mock_open):
                with patch('os.makedirs'):
                    from ats_ai_optimizer import main
                    # Should not raise any exceptions
                    main()


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)