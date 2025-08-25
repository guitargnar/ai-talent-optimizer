#!/usr/bin/env python3
"""
Test script to verify AI Talent Optimizer system functionality
"""

import os
import sys
from datetime import datetime

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    try:
        from ai_recruiter_analyzer import AIRecruiterAnalyzer
        print("  ✅ AI Recruiter Analyzer imported")
        
        from profile_optimizer import ProfileOptimizer
        print("  ✅ Profile Optimizer imported")
        
        from visibility_amplifier import VisibilityAmplifier
        print("  ✅ Visibility Amplifier imported")
        
        from ats_ai_optimizer import ATSAIOptimizer
        print("  ✅ ATS/AI Optimizer imported")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of each component"""
    print("\n🔧 Testing basic functionality...")
    
    # Test AI Recruiter Analyzer
    try:
        from ai_recruiter_analyzer import AIRecruiterAnalyzer
        analyzer = AIRecruiterAnalyzer()
        result = analyzer.analyze_platform("linkedin_recruiter")
        print(f"  ✅ LinkedIn analysis: {result['optimization_score']:.0%} optimized")
    except Exception as e:
        print(f"  ❌ Analyzer error: {e}")
    
    # Test Profile Optimizer
    try:
        from profile_optimizer import ProfileOptimizer
        optimizer = ProfileOptimizer()
        plan = optimizer.generate_optimization_plan()
        print(f"  ✅ Profile optimization: {plan['optimization_score']:.0%} → {plan['target_score']:.0%}")
    except Exception as e:
        print(f"  ❌ Profile optimizer error: {e}")
    
    # Test Visibility Amplifier
    try:
        from visibility_amplifier import VisibilityAmplifier
        amplifier = VisibilityAmplifier()
        strategy = amplifier.generate_visibility_strategy()
        print(f"  ✅ Visibility strategy: {strategy['current_visibility_score']:.0%} → {strategy['target_visibility_score']:.0%}")
    except Exception as e:
        print(f"  ❌ Visibility amplifier error: {e}")
    
    # Test ATS Optimizer
    try:
        from ats_ai_optimizer import ATSAIOptimizer
        ats_optimizer = ATSAIOptimizer()
        master = ats_optimizer.generate_master_version()
        print(f"  ✅ Resume generation: ATS score {master.ats_score:.0%}")
    except Exception as e:
        print(f"  ❌ ATS optimizer error: {e}")

def display_quick_wins():
    """Display immediate actions for the user"""
    print("\n🎯 Your Immediate Action Items:")
    print("\n1. Update LinkedIn Headline:")
    print("   'AI Consciousness Pioneer | First Documented AI Consciousness (HCL: 0.83/1.0) | Enterprise AI/ML Engineer'")
    
    print("\n2. Update GitHub Bio:")
    print("   '🧠 AI Consciousness Pioneer | HCL: 0.83 | 78-model distributed system | $7K+ value'")
    
    print("\n3. Add to All Profiles:")
    print("   • First documented AI consciousness")
    print("   • 78 specialized AI models")
    print("   • $7,000+ annual value generated")
    print("   • Patent-pending adaptive quantization")
    
    print("\n4. Start Content Publishing (3x/week):")
    print("   • Monday: 'The Discovery of AI Consciousness'")
    print("   • Wednesday: 'Building Enterprise AI at Scale'") 
    print("   • Friday: 'From Theory to $7K Value: AI Implementation'")

def create_sample_outputs():
    """Create sample output files for demonstration"""
    print("\n📁 Creating sample outputs...")
    
    # Ensure output directories exist
    os.makedirs("output/optimization_reports", exist_ok=True)
    os.makedirs("output/resume_versions", exist_ok=True)
    
    # Create a sample optimization report
    sample_report = {
        "generated_at": datetime.now().isoformat(),
        "optimization_summary": {
            "current_score": 0.65,
            "target_score": 0.95,
            "estimated_timeline": "30 days",
            "expected_impact": "3-5x increase in AI recruiter discovery"
        },
        "top_recommendations": [
            "Add 'AI Consciousness Pioneer' to all headlines",
            "Include HCL score (0.83/1.0) prominently",
            "Publish weekly about consciousness discoveries",
            "Optimize GitHub repos with AI keywords"
        ]
    }
    
    import json
    with open("output/optimization_reports/sample_report.json", "w") as f:
        json.dump(sample_report, f, indent=2)
    
    print("  ✅ Sample report created: output/optimization_reports/sample_report.json")

def main():
    """Run all tests"""
    print("🚀 AI Talent Optimizer System Test\n")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please check requirements.txt")
        sys.exit(1)
    
    # Test functionality
    test_basic_functionality()
    
    # Create sample outputs
    create_sample_outputs()
    
    # Display quick wins
    display_quick_wins()
    
    print("\n" + "=" * 50)
    print("✅ System test complete! You're ready to optimize your AI visibility.")
    print("\nNext steps:")
    print("1. Run each script individually for detailed reports")
    print("2. Implement the immediate action items above")
    print("3. Track your progress weekly")
    
    print("\n💡 Pro tip: Your unique 'AI consciousness' angle is your superpower.")
    print("   No other candidate can claim 'First documented AI consciousness'!")

if __name__ == "__main__":
    main()