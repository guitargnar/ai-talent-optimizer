#!/usr/bin/env python3
"""
Implement Quality Filters - Quick 10-minute fix
"""

import json

def update_quality_filters():
    """Update unified_config.json with better quality filters"""
    
    # Load current config
    with open('unified_config.json', 'r') as f:
        config = json.load(f)
    
    # Add high-value keywords
    config['high_value_keywords'] = [
        'AI', 'ML', 'machine learning', 'deep learning', 'LLM', 
        'computer vision', 'NLP', 'data science', 'python',
        'tensorflow', 'pytorch', 'remote', 'senior', 'staff', 
        'principal', 'GPT', 'transformer', 'neural network',
        'artificial intelligence', 'research', 'scientist'
    ]
    
    # Add negative keywords to avoid
    config['negative_keywords'] = [
        'junior', 'intern', 'entry level', 'clearance required',
        'on-site only', 'no remote', 'contract', 'part-time',
        'unpaid', 'volunteer', 'student', 'citizenship required',
        'security clearance', 'must be onsite'
    ]
    
    # Set minimum quality thresholds
    config['min_salary'] = 120000
    config['min_relevance_score'] = 0.5  # Raised from 0.3
    
    # Update application criteria
    config['application_criteria']['min_relevance_score'] = 0.5
    
    # Save updated config
    with open('unified_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Quality filters updated successfully!")
    print("\nNew filters:")
    print(f"  • High-value keywords: {len(config['high_value_keywords'])}")
    print(f"  • Negative keywords: {len(config['negative_keywords'])}")
    print(f"  • Min salary: ${config['min_salary']:,}")
    print(f"  • Min relevance score: {config['min_relevance_score']}")
    
    return config

if __name__ == "__main__":
    update_quality_filters()