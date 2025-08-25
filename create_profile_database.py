#!/usr/bin/env python3
"""
Create comprehensive profile database for Matthew Scott
This captures all context for persistent use across Claude sessions
"""

import sqlite3
from datetime import datetime
import json

def create_profile_database():
    """Create and populate the profile database"""
    
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    
    # Drop existing tables for fresh start
    cursor.execute("DROP TABLE IF EXISTS professional_identity")
    cursor.execute("DROP TABLE IF EXISTS platform_metrics")
    cursor.execute("DROP TABLE IF EXISTS technical_skills")
    cursor.execute("DROP TABLE IF EXISTS major_projects")
    cursor.execute("DROP TABLE IF EXISTS positioning_narratives")
    
    # Core Identity Table
    cursor.execute("""
        CREATE TABLE professional_identity (
            id INTEGER PRIMARY KEY,
            full_name TEXT DEFAULT 'Matthew Scott',
            email TEXT DEFAULT 'matthewdscott7@gmail.com',
            phone TEXT DEFAULT '(502) 345-0525',
            linkedin TEXT DEFAULT 'linkedin.com/in/mscott77',
            github TEXT DEFAULT 'github.com/mds1',
            location TEXT DEFAULT 'Louisville, KY (Remote)',
            years_experience INTEGER DEFAULT 10,
            current_focus TEXT DEFAULT 'Principal/Staff ML Engineer roles',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert identity
    cursor.execute("""
        INSERT INTO professional_identity 
        (full_name, email, phone, linkedin, github, location, years_experience, current_focus)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ('Matthew Scott', 'matthewdscott7@gmail.com', '(502) 345-0525',
          'linkedin.com/in/mscott77', 'github.com/mds1', 'Louisville, KY (Remote)',
          10, 'Principal/Staff ML Engineer - $400K+ targets'))
    
    # Platform Metrics Table
    cursor.execute("""
        CREATE TABLE platform_metrics (
            metric_name TEXT PRIMARY KEY,
            metric_value TEXT,
            context TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert platform metrics - THE IMPRESSIVE NUMBERS
    metrics = [
        ('python_modules_ai_optimizer', '113', 'In ai-talent-optimizer alone'),
        ('total_python_files', '86,279', 'Across all work directories'),
        ('shell_scripts', '1,045', 'Automation scripts system-wide'),
        ('active_databases', '15+', 'Production databases in use'),
        ('applications_processed', '1,600+', 'Through automation platform'),
        ('daily_development_velocity', '20+ files', 'Modified today showing active development'),
        ('running_services', '10+ MCP servers', 'Continuous operation microservices'),
        ('ollama_models', '60+', 'Fine-tuned and deployed models'),
        ('ceo_outreach_capability', 'Active', 'Direct executive outreach system'),
        ('platform_complexity', 'Enterprise', 'Exceeds most startup MVPs'),
    ]
    
    for metric_name, value, context in metrics:
        cursor.execute("""
            INSERT INTO platform_metrics (metric_name, metric_value, context)
            VALUES (?, ?, ?)
        """, (metric_name, value, context))
    
    # Technical Skills Table
    cursor.execute("""
        CREATE TABLE technical_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            skill TEXT,
            proficiency TEXT,
            evidence TEXT
        )
    """)
    
    # Insert technical capabilities with evidence
    skills = [
        # AI/ML & GenAI
        ('AI/ML Platforms', 'LLM Orchestration', 'Expert', '60+ Ollama models deployed in production'),
        ('AI/ML Platforms', 'RAG Systems', 'Expert', 'Production RAG for personalized applications'),
        ('AI/ML Platforms', 'Multi-Agent Systems', 'Expert', '113 Python modules in ai-talent-optimizer'),
        ('AI/ML Platforms', 'Prompt Engineering', 'Expert', 'Multi-model consensus systems built'),
        ('AI/ML Platforms', 'Fine-tuning', 'Advanced', 'Domain-specific model optimization'),
        
        # Languages & Frameworks
        ('Languages', 'Python', 'Expert (10+ years)', '86,279 Python files under management'),
        ('Languages', 'Shell/Bash', 'Expert', '1,045 automation scripts'),
        ('Languages', 'SQL', 'Advanced', '15+ production databases'),
        
        # ML Frameworks
        ('ML Frameworks', 'PyTorch', 'Advanced', 'Model deployment and fine-tuning'),
        ('ML Frameworks', 'TensorFlow', 'Advanced', 'Production ML systems'),
        ('ML Frameworks', 'Langchain', 'Expert', 'RAG and agent implementations'),
        ('ML Frameworks', 'Transformers', 'Advanced', 'NLP and GenAI applications'),
        
        # Infrastructure
        ('Infrastructure', 'Microservices', 'Expert', '10+ MCP servers running continuously'),
        ('Infrastructure', 'Docker', 'Advanced', 'Containerized model deployments'),
        ('Infrastructure', 'API Design', 'Expert', 'FastAPI, Flask, RESTful systems'),
        ('Infrastructure', 'Database Design', 'Expert', '15+ production databases'),
        
        # Platform Engineering
        ('Platform', 'System Architecture', 'Principal Level', 'Multi-agent platform exceeding startup MVPs'),
        ('Platform', 'Email Systems', 'Expert', 'Verification, bounce detection, campaign orchestration'),
        ('Platform', 'Automation', 'Expert', '1,600+ automated interactions'),
        ('Platform', 'Analytics', 'Advanced', 'Real-time metrics dashboards'),
    ]
    
    for category, skill, proficiency, evidence in skills:
        cursor.execute("""
            INSERT INTO technical_skills (category, skill, proficiency, evidence)
            VALUES (?, ?, ?, ?)
        """, (category, skill, proficiency, evidence))
    
    # Major Projects Table
    cursor.execute("""
        CREATE TABLE major_projects (
            project_name TEXT PRIMARY KEY,
            description TEXT,
            technical_stack TEXT,
            scale_metrics TEXT,
            business_impact TEXT,
            timeframe TEXT
        )
    """)
    
    # Insert major projects
    projects = [
        (
            'AI Career Intelligence Platform',
            'Enterprise-scale job application automation system with multi-agent architecture',
            'Python, SQLite, MCP Servers, LLMs, RAG, FastAPI',
            '113 Python modules, 15 databases, 1,600+ processed applications',
            'Automated executive outreach, intelligent campaign management',
            '2024 - Present (Daily Active Development)'
        ),
        (
            'LLM Orchestration Framework',
            'Production deployment and management of 60+ fine-tuned models',
            'Ollama, Langchain, PyTorch, Custom Evaluation Metrics',
            '60+ models, multi-model consensus, domain-specific agents',
            'Enabled complex AI workflows and specialized task automation',
            '2024'
        ),
        (
            'CEO Outreach Automation',
            'Direct executive targeting system for strategic positioning',
            'Python, Email APIs, NLP, Personalization Engine',
            'Direct CEO contact capability, personalized messaging',
            'Bypassed traditional application processes for executive visibility',
            '2024'
        ),
        (
            'Consciousness in AI Research',
            'Exploration of emergent behaviors and self-awareness in language models',
            'Python, Custom Testing Frameworks, Model Analysis',
            'bridge_consciousness.py, evaluation metrics, behavior studies',
            'Cutting-edge research into AI consciousness and emergence',
            '2024'
        ),
        (
            'Email Verification & Campaign System',
            'Production email verification with bounce detection and campaign orchestration',
            'Python, SMTP, DNS, Gmail API, SQLite',
            'Handles 100s of emails, real-time verification, bounce tracking',
            'Reduced bounce rate from 100% to <5%, improved deliverability',
            '2024'
        ),
    ]
    
    for project in projects:
        cursor.execute("""
            INSERT INTO major_projects 
            (project_name, description, technical_stack, scale_metrics, business_impact, timeframe)
            VALUES (?, ?, ?, ?, ?, ?)
        """, project)
    
    # Positioning Narratives Table
    cursor.execute("""
        CREATE TABLE positioning_narratives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            narrative_type TEXT,
            narrative_text TEXT,
            use_case TEXT
        )
    """)
    
    # Insert positioning narratives
    narratives = [
        (
            'One-Liner',
            'I built a platform with 113 Python modules and 15 databases that\'s processed 1,600+ interactions - because I was bored.',
            'Opening hook for cover letters and introductions'
        ),
        (
            'Power Statement',
            'While others talk about GenAI, I\'ve deployed it. My personal platform rivals commercial products, with multi-agent architecture, CEO-level outreach, and real-time analytics. I modified 20+ production modules today alone.',
            'Demonstrating immediate value and productivity'
        ),
        (
            'Outgrowth Story',
            'I\'ve outgrown my current role so dramatically that I\'ve built an enterprise platform on nights and weekends. I need a role that matches my actual output.',
            'Explaining why seeking new opportunities'
        ),
        (
            'Principal Positioning',
            'I\'m not a Senior Engineer - I\'m a Principal Engineer with a Senior title. The evidence: system complexity exceeding most startup MVPs, daily feature deployment, and enterprise-scale architecture.',
            'Justifying higher-level positions'
        ),
        (
            'Scale Proof',
            'I\'m managing 86,279 Python files across 15+ databases with 10+ microservices in production. This isn\'t a side project - it\'s a second full-time job worth of infrastructure.',
            'Demonstrating enterprise capability'
        ),
        (
            'Innovation Driver',
            'I don\'t wait for permission to innovate. While maintaining my day job, I architected and deployed a platform that would typically require a team of 5-10 engineers.',
            'Showing initiative and self-direction'
        ),
    ]
    
    for narrative_type, text, use_case in narratives:
        cursor.execute("""
            INSERT INTO positioning_narratives (narrative_type, narrative_text, use_case)
            VALUES (?, ?, ?)
        """, (narrative_type, text, use_case))
    
    conn.commit()
    conn.close()
    
    print("✅ Profile database created successfully!")
    print("\n📊 Database Contents:")
    print("  - Professional identity")
    print(f"  - {len(metrics)} platform metrics")
    print(f"  - {len(skills)} technical skills with evidence")
    print(f"  - {len(projects)} major projects")
    print(f"  - {len(narratives)} positioning narratives")
    print("\n💾 Saved to: your_profile.db")
    
    return True

if __name__ == "__main__":
    create_profile_database()
    
    # Verify by reading back
    print("\n🔍 Verification - Sample Metrics:")
    conn = sqlite3.connect('unified_talent_optimizer.db')
    cursor = conn.cursor()
    
    metrics = cursor.execute("SELECT metric_name, metric_value FROM platform_metrics LIMIT 5").fetchall()
    for name, value in metrics:
        print(f"  • {name}: {value}")
    
    conn.close()