#!/usr/bin/env python3
"""
Test Coverage Analysis Tool
============================
Analyzes test coverage and identifies critical files needing tests.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class CoverageAnalyzer:
    def __init__(self):
        self.critical_modules = [
            # Core application modules
            'orchestrator.py',
            'dynamic_apply.py',
            'quality_first_apply.py',
            'generate_application.py',
            'company_researcher.py',
            
            # Database modules
            'migrate_data.py',
            'validate_migration.py',
            'unified_db_config.py',
            
            # Email and response tracking
            'accurate_response_checker.py',
            'bounce_detector.py',
            'email_verification_system.py',
            'smart_followup_system.py',
            
            # Metrics and monitoring
            'true_metrics_dashboard.py',
            'ab_testing_system.py',
            'optimization_dashboard.py',
            
            # Career automation
            'career_intelligence_system.py',
            'differentiation_engine.py',
            'profile_context_generator.py',
        ]
        
        # Files to exclude from analysis
        self.exclude_patterns = [
            'test_',
            'EMERGENCY',
            'QUARANTINE',
            'legacy_archive',
            '__pycache__',
            '.pyc',
            'backup',
            'GET_ME_A',
            'SEND_JOBS',
            'APPLY_JOBS',
            'APPLY_RIGHT',
        ]
    
    def run_coverage(self) -> Dict:
        """Run pytest with coverage and capture results."""
        print("Running test coverage analysis...")
        
        cmd = [
            'pytest',
            '--cov=.',
            '--cov-report=json',
            '--ignore=ml-env',
            '--ignore=venv',
            '--ignore=google-env',
            '--ignore=legacy_archive',
            '--ignore=QUARANTINE_OLD_AUTOMATION',
            '-q'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Load coverage data
        coverage_file = Path('coverage.json')
        if coverage_file.exists():
            with open(coverage_file, 'r') as f:
                return json.load(f)
        return {}
    
    def analyze_coverage(self, coverage_data: Dict) -> List[Tuple[str, float, int]]:
        """Analyze coverage data and return sorted list of files."""
        if not coverage_data or 'files' not in coverage_data:
            return []
        
        file_coverage = []
        
        for filepath, data in coverage_data['files'].items():
            # Skip excluded patterns
            if any(pattern in filepath for pattern in self.exclude_patterns):
                continue
            
            # Only include Python files
            if not filepath.endswith('.py'):
                continue
            
            filename = Path(filepath).name
            total_lines = len(data.get('executed_lines', [])) + len(data.get('missing_lines', []))
            executed = len(data.get('executed_lines', []))
            
            if total_lines > 0:
                coverage_percent = (executed / total_lines) * 100
                file_coverage.append((filename, coverage_percent, total_lines))
        
        # Sort by coverage percentage (ascending) and lines of code (descending)
        file_coverage.sort(key=lambda x: (x[1], -x[2]))
        
        return file_coverage
    
    def identify_critical_gaps(self, file_coverage: List[Tuple[str, float, int]]) -> List[Tuple[str, float, int]]:
        """Identify critical files with low coverage."""
        critical_gaps = []
        
        for filename, coverage, lines in file_coverage:
            # Check if it's a critical module
            if filename in self.critical_modules:
                if coverage < 50:  # Less than 50% coverage
                    critical_gaps.append((filename, coverage, lines))
        
        return critical_gaps[:5]  # Return top 5
    
    def generate_report(self):
        """Generate comprehensive coverage report."""
        print("="*70)
        print("TEST COVERAGE ANALYSIS REPORT")
        print("="*70)
        
        # Run coverage
        coverage_data = self.run_coverage()
        
        if not coverage_data:
            print("❌ Failed to generate coverage data")
            return
        
        # Get overall statistics
        totals = coverage_data.get('totals', {})
        overall_coverage = totals.get('percent_covered', 0)
        
        print(f"\n📊 OVERALL METRICS:")
        print(f"  Total Coverage: {overall_coverage:.1f}%")
        print(f"  Total Files: {totals.get('num_files', 0)}")
        print(f"  Total Lines: {totals.get('num_statements', 0)}")
        print(f"  Covered Lines: {totals.get('num_statements', 0) - totals.get('missing_lines', 0)}")
        print(f"  Missing Lines: {totals.get('missing_lines', 0)}")
        
        # Analyze file coverage
        file_coverage = self.analyze_coverage(coverage_data)
        
        # Show files with lowest coverage
        print(f"\n❌ FILES WITH LOWEST COVERAGE:")
        for i, (filename, coverage, lines) in enumerate(file_coverage[:10], 1):
            print(f"  {i:2}. {filename:40} {coverage:5.1f}% ({lines} lines)")
        
        # Identify critical gaps
        critical_gaps = self.identify_critical_gaps(file_coverage)
        
        print(f"\n🚨 CRITICAL FILES NEEDING TESTS:")
        print("  (These are high-priority modules with low coverage)")
        for i, (filename, coverage, lines) in enumerate(critical_gaps, 1):
            print(f"  {i}. {filename:40} {coverage:5.1f}% coverage ({lines} lines)")
            print(f"     Priority: HIGH - Core functionality")
        
        # Show files with best coverage
        print(f"\n✅ FILES WITH BEST COVERAGE:")
        best_coverage = sorted(file_coverage, key=lambda x: -x[1])[:5]
        for i, (filename, coverage, lines) in enumerate(best_coverage, 1):
            if coverage > 0:
                print(f"  {i}. {filename:40} {coverage:5.1f}% ({lines} lines)")
        
        # Recommendations
        print(f"\n📝 RECOMMENDATIONS:")
        print("  1. Focus on testing critical files first (orchestrator.py, dynamic_apply.py)")
        print("  2. Aim for 80% coverage on core modules")
        print("  3. Create integration tests for database operations")
        print("  4. Add unit tests for email validation and response checking")
        print("  5. Mock external dependencies (Gmail API, Ollama)")
        
        return critical_gaps

def main():
    """Main execution function."""
    analyzer = CoverageAnalyzer()
    critical_gaps = analyzer.generate_report()
    
    if critical_gaps:
        print(f"\n🎯 ACTION PLAN:")
        print("  Create unit tests for these files in priority order:")
        for i, (filename, _, _) in enumerate(critical_gaps, 1):
            test_file = f"tests/test_{filename.replace('.py', '')}.py"
            print(f"    {i}. Create {test_file}")
    
    print("\n" + "="*70)
    print("Run 'pytest --cov=. --cov-report=html' for detailed HTML report")
    print("="*70)

if __name__ == "__main__":
    main()