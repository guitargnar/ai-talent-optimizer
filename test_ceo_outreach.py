#!/usr/bin/env python3
"""
Test CEO Outreach System
Quick validation that the CEO outreach integration works with the unified database
"""

import sys
from pathlib import Path
import sqlite3
import logging

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from core.ceo_outreach_engine import CEOOutreachEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_database_integration():
    """Test that the CEO outreach system integrates with unified database"""
    print("🧪 Testing CEO Outreach System Integration")
    print("=" * 50)
    
    # Test 1: Initialize engine and verify database connection
    print("\n1️⃣ Testing Database Connection...")
    try:
        engine = CEOOutreachEngine()
        print("   ✅ CEO Outreach Engine initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize engine: {e}")
        return False
    
    # Test 2: Verify contacts table has required columns
    print("\n2️⃣ Testing Database Schema...")
    try:
        conn = sqlite3.connect('unified_talent_optimizer.db')
        cursor = conn.cursor()
        
        # Check contacts table exists and has required columns
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['company', 'name', 'title', 'email', 'linkedin', 'priority_score']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"   ❌ Missing columns: {missing_columns}")
            return False
        else:
            print("   ✅ All required columns present in contacts table")
            
        conn.close()
    except Exception as e:
        print(f"   ❌ Database schema error: {e}")
        return False
    
    # Test 3: Test contact storage
    print("\n3️⃣ Testing Contact Storage...")
    try:
        from core.ceo_outreach_engine import CEOContact
        
        # Create test contact
        test_contact = CEOContact(
            company="Test Company",
            name="Test CEO",
            title="Chief Executive Officer",
            email="ceo@testcompany.com",
            linkedin="https://linkedin.com/in/testceo",
            priority_score=85,
            confidence_level=0.9
        )
        
        engine._store_contact(test_contact)
        print("   ✅ Test contact stored successfully")
        
        # Verify it was stored
        conn = sqlite3.connect('unified_talent_optimizer.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE company = 'Test Company'")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            print("   ✅ Test contact retrieved successfully")
        else:
            print("   ❌ Test contact not found in database")
            return False
            
    except Exception as e:
        print(f"   ❌ Contact storage error: {e}")
        return False
    
    # Test 4: Test target company configuration
    print("\n4️⃣ Testing Target Companies Configuration...")
    try:
        target_companies = list(engine.TARGET_COMPANIES.keys())
        expected_companies = ['Genesis AI', 'Inworld AI', 'Adyen', 'Lime', 'Thumbtack']
        
        if set(target_companies) == set(expected_companies):
            print("   ✅ All target companies configured correctly")
            for company in target_companies:
                details = engine.TARGET_COMPANIES[company]
                print(f"      • {company}: {details['position']} ({details['salary']})")
        else:
            print(f"   ❌ Target company mismatch: {target_companies}")
            return False
            
    except Exception as e:
        print(f"   ❌ Target company configuration error: {e}")
        return False
    
    # Test 5: Test email generation
    print("\n5️⃣ Testing Email Generation...")
    try:
        # Create test contact data
        test_contact_data = {
            'company': 'Genesis AI',
            'name': 'Test CEO',
            'title': 'Chief Executive Officer',
            'email': 'ceo@genesis-ai.com',
            'linkedin': 'https://linkedin.com/in/testceo',
            'priority_score': 90,
            'confidence_level': 0.8
        }
        
        # Test email body generation
        company_details = engine.TARGET_COMPANIES['Genesis AI']
        email_body = engine._generate_ceo_email_body(test_contact_data, company_details)
        
        # Verify email contains key elements
        required_elements = [
            'Genesis AI',
            'Principal ML Research Engineer', 
            '$1.2M',
            'Humana',
            'Matthew Scott',
            'foundational AI research'
        ]
        
        missing_elements = [elem for elem in required_elements if elem not in email_body]
        
        if missing_elements:
            print(f"   ❌ Email missing elements: {missing_elements}")
            return False
        else:
            print("   ✅ Email generation working correctly")
            print(f"      Email length: {len(email_body)} characters")
            
    except Exception as e:
        print(f"   ❌ Email generation error: {e}")
        return False
    
    # Test 6: Test stats generation
    print("\n6️⃣ Testing Statistics Generation...")
    try:
        stats = engine.get_stats()
        required_stats = ['target_companies', 'total_contacts', 'contacted', 'total_potential_salary']
        
        if all(key in stats for key in required_stats):
            print("   ✅ Statistics generation working")
            print(f"      Target companies: {stats['target_companies']}")
            print(f"      Total contacts: {stats['total_contacts']}")
            print(f"      Total potential salary: {stats['total_potential_salary']}")
        else:
            print(f"   ❌ Missing stats keys: {[k for k in required_stats if k not in stats]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Statistics generation error: {e}")
        return False
    
    # Cleanup: Remove test contact
    try:
        conn = sqlite3.connect('unified_talent_optimizer.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE company = 'Test Company'")
        conn.commit()
        conn.close()
        print("\n🧹 Test data cleaned up")
    except:
        pass
    
    print("\n✅ ALL TESTS PASSED - CEO Outreach System Ready!")
    print("\n🚀 Next Steps:")
    print("   1. Run research: python run_ceo_outreach.py --mode research")
    print("   2. Send outreach: python run_ceo_outreach.py --mode outreach")
    print("   3. Generate report: python run_ceo_outreach.py --mode report")
    print("   4. Full campaign: python run_ceo_outreach.py --mode full")
    
    return True


def test_cli_integration():
    """Test CLI integration"""
    print("\n🖥️  Testing CLI Integration...")
    
    try:
        # Test CLI import
        from cli.main import cli
        print("   ✅ CLI imports CEO outreach successfully")
        
        # Check if outreach command exists
        commands = [cmd.name for cmd in cli.commands.values()]
        if 'outreach' in commands:
            print("   ✅ Outreach command available in CLI")
        else:
            print("   ❌ Outreach command not found in CLI")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ CLI integration error: {e}")
        return False


if __name__ == "__main__":
    print("🎯 CEO OUTREACH SYSTEM - INTEGRATION TEST")
    print("Testing system targeting $450K+ positions at 5 companies")
    
    # Run database integration tests
    db_success = test_database_integration()
    
    # Run CLI integration tests  
    cli_success = test_cli_integration()
    
    if db_success and cli_success:
        print("\n🎉 CEO OUTREACH SYSTEM FULLY OPERATIONAL!")
        print("\nTarget Companies & Positions:")
        print("• Genesis AI - Principal ML Research Engineer ($480K)")
        print("• Inworld AI - Staff/Principal ML Engineer ($475K)")
        print("• Adyen - Staff Engineer ML ($465K)")
        print("• Lime - Principal ML Engineer ($465K)")
        print("• Thumbtack - Principal ML Infrastructure ($450K)")
        print("\n💰 Total Annual Potential: $2.34M")
        print("\n🚀 System ready for CEO outreach campaign!")
    else:
        print("\n❌ System has integration issues - check errors above")
        sys.exit(1)