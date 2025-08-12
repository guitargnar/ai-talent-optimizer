#!/usr/bin/env python3
"""
Fix unified_config.json to add missing fields
"""

import json

# Load config
with open('unified_config.json', 'r') as f:
    config = json.load(f)

# Add missing fields for application criteria
if 'application_criteria' not in config:
    config['application_criteria'] = {}

config['application_criteria']['min_relevance_score'] = 0.3  # Lower threshold to find jobs
config['min_relevance_score'] = 0.3  # Backup field

# Also add high-value and negative keywords if missing
if 'high_value_keywords' not in config:
    config['high_value_keywords'] = [
        'AI', 'ML', 'machine learning', 'deep learning', 'LLM', 
        'computer vision', 'NLP', 'data science', 'python',
        'tensorflow', 'pytorch', 'remote', 'senior', 'staff', 
        'principal', 'GPT', 'transformer', 'neural network'
    ]

if 'negative_keywords' not in config:
    config['negative_keywords'] = [
        'junior', 'intern', 'entry level', 'clearance required',
        'on-site only', 'no remote', 'contract', 'part-time'
    ]

# Save updated config
with open('unified_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Config fixed! Added:")
print(f"  • min_relevance_score: {config['application_criteria']['min_relevance_score']}")
print(f"  • high_value_keywords: {len(config.get('high_value_keywords', []))} keywords")
print(f"  • negative_keywords: {len(config.get('negative_keywords', []))} keywords")