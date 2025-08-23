#!/usr/bin/env python3
"""
Quick test to ensure the agent can be imported and initialized
"""

import sys
import traceback

def test_import():
    """Test if the agent can be imported"""
    try:
        print("Testing import...")
        from aiviizn_real_agent_with_ai_intelligence_updated import AIVIIZNRealAgent
        print("✅ Import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False
    except SyntaxError as e:
        print(f"❌ Syntax error in file: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False

def test_initialization():
    """Test if the agent can be initialized"""
    try:
        print("\nTesting initialization...")
        from aiviizn_real_agent_with_ai_intelligence_updated import AIVIIZNRealAgent
        agent = AIVIIZNRealAgent()
        print("✅ Initialization successful")
        
        # Check key attributes
        print("\nChecking attributes:")
        attrs = ['supabase', 'company_id', 'field_mapper', 'enhanced_field_mapper']
        for attr in attrs:
            if hasattr(agent, attr):
                print(f"  ✅ {attr} exists")
            else:
                print(f"  ❌ {attr} missing")
        
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("🔍 Testing AIVIIZN Agent")
    print("="*60)
    
    if test_import():
        test_initialization()
    
    print("="*60)

if __name__ == "__main__":
    main()
