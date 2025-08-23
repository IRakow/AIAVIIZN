#!/usr/bin/env python3
"""
LAUNCH AIVIIZN WITH AI-POWERED FIELD INTELLIGENCE
Quick start script for the enhanced agent
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the AI-powered agent
from aiviizn_real_agent_with_ai_intelligence import AIVIIZNRealAgent

def main():
    """Launch the AI-powered agent"""
    print("\n" + "="*60)
    print("🚀 AIVIIZN AI-POWERED FIELD INTELLIGENCE SYSTEM")
    print("="*60)
    print("\nFeatures:")
    print("  ✨ AI names ALL fields intelligently")
    print("  🧮 Maps calculation variables to source fields")
    print("  🔍 Identifies data types and units automatically")
    print("  🛡️ Prevents duplicate pages and fields")
    print("  📊 Tracks formulas and their relationships")
    print("\n" + "="*60)
    
    try:
        # Create and run the agent
        agent = AIVIIZNRealAgent()
        asyncio.run(agent.run())
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
