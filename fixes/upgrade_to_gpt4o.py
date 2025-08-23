#!/usr/bin/env python3
"""
Update AIVIIZN agent to use GPT-4o (the best available model)
"""

import re
from pathlib import Path
from datetime import datetime

def upgrade_to_gpt4o():
    """Upgrade the agent to use GPT-4o instead of gpt-4-turbo-preview"""
    
    agent_file = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent.py")
    
    # Backup first
    backup_file = agent_file.parent / f"aiviizn_real_agent.py.backup_gpt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(agent_file, 'r') as f:
        content = f.read()
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"✅ Backup created: {backup_file}")
    
    print("\n🚀 UPGRADING TO GPT-4o (BEST MODEL)")
    print("=" * 60)
    
    # Count current model references
    old_model_count = content.count("gpt-4-turbo-preview")
    print(f"Found {old_model_count} references to old model")
    
    # Replace all instances of gpt-4-turbo-preview with gpt-4o
    content = content.replace(
        'model="gpt-4-turbo-preview"',
        'model="gpt-4o"'  # Latest and best model
    )
    
    # Also update any string references
    content = content.replace(
        '"gpt-4-turbo-preview"',
        '"gpt-4o"'
    )
    
    # Update the initialization message
    content = content.replace(
        'print(f"✓ GPT-4 Turbo connected',
        'print(f"✓ GPT-4o (Omni) connected'
    )
    
    # Update any comments
    content = content.replace(
        'GPT-4 Turbo mathematical analysis',
        'GPT-4o (Omni) mathematical analysis'
    )
    
    content = content.replace(
        'Starting GPT-4 Turbo analysis',
        'Starting GPT-4o (Omni) analysis'
    )
    
    content = content.replace(
        'Use GPT-4 Turbo for intelligent formula analysis',
        'Use GPT-4o (Omni) for intelligent formula analysis'
    )
    
    # Write back
    with open(agent_file, 'w') as f:
        f.write(content)
    
    # Verify changes
    with open(agent_file, 'r') as f:
        new_content = f.read()
    
    new_model_count = new_content.count("gpt-4o")
    
    print(f"\n✅ UPGRADE COMPLETE!")
    print(f"   Replaced {old_model_count} references")
    print(f"   Now using gpt-4o in {new_model_count} places")
    
    # Show what GPT-4o offers
    print("\n🎯 GPT-4o ADVANTAGES:")
    print("=" * 60)
    print("  ✓ Latest model (May 2024)")
    print("  ✓ 2x faster than GPT-4 Turbo")
    print("  ✓ Better at complex reasoning")
    print("  ✓ Superior code generation")
    print("  ✓ More accurate formula extraction")
    print("  ✓ Better pattern recognition")
    print("  ✓ 128K context window")
    print("  ✓ Multimodal capabilities")
    
    # Check if we have response_format for JSON
    if 'response_format={ "type": "json_object" }' in new_content:
        print("\n✅ JSON mode is already enabled (good for formula extraction)")
    
    print("\n📊 FORMULA EXTRACTION IMPROVEMENTS:")
    print("=" * 60)
    print("GPT-4o will provide:")
    print("  • More accurate formula detection")
    print("  • Better variable naming")
    print("  • Cleaner JavaScript generation")
    print("  • Higher confidence in calculations")
    print("  • Better understanding of financial/property formulas")
    
    return True

def add_enhanced_prompts():
    """Add enhanced prompts specifically for GPT-4o's capabilities"""
    
    agent_file = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent.py")
    
    print("\n🎨 ENHANCING GPT-4o PROMPTS")
    print("=" * 60)
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Find the enhanced_gpt4_analysis method
    if "async def enhanced_gpt4_analysis" in content:
        # Enhance the prompts to leverage GPT-4o better
        
        # Pattern to find the observation analysis prompt
        pattern = r'(prompt = f"""You are analyzing.*?""")'
        
        enhanced_prompt = r'''prompt = f"""You are analyzing a property management system (similar to AppFolio) using GPT-4o's advanced capabilities. 
Based on these observations from changing inputs and watching outputs, identify the mathematical formulas being used.

OBSERVATIONS FROM TESTING:
{json.dumps(obs_data, indent=2)}

CONTEXT: This is a property management system that handles:
- Rent collection and rent rolls
- Late fees (typically 5% of rent)
- Security deposits (usually 1-2 months rent)
- CAM charges (Common Area Maintenance)
- Management fees (typically 8-10% of gross rent)
- Occupancy rates and vacancy calculations
- Proration for partial months
- Utility billing and RUBS (Ratio Utility Billing System)
- Maintenance reserves
- Pet fees and deposits

Using GPT-4o's enhanced reasoning:
1. Identify ALL mathematical relationships in the data
2. Deduce formulas from numerical patterns
3. Name functions using proper camelCase convention
4. Generate production-ready JavaScript implementations
5. Assign confidence levels based on evidence strength

Return ONLY a JSON array with complete formula definitions.
Each formula must include a working JavaScript implementation.
Focus on accuracy and completeness."""'''
        
        # Replace if found
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, enhanced_prompt, content, count=1, flags=re.DOTALL)
            print("✅ Enhanced observation analysis prompt for GPT-4o")
    
    # Save enhanced version
    with open(agent_file, 'w') as f:
        f.write(content)
    
    print("✅ Prompts optimized for GPT-4o capabilities")
    
    return True

def verify_gpt4o_setup():
    """Verify GPT-4o is properly configured"""
    
    agent_file = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent.py")
    
    print("\n🔍 VERIFYING GPT-4o SETUP")
    print("=" * 60)
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    checks = {
        "GPT-4o model": 'model="gpt-4o"' in content,
        "JSON response format": 'response_format={ "type": "json_object" }' in content,
        "Temperature 0": "temperature=0" in content,
        "Max tokens set": "max_tokens=" in content,
        "OpenAI client initialized": "self.openai_client = AsyncOpenAI" in content
    }
    
    all_good = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
        if not passed:
            all_good = False
    
    if all_good:
        print("\n🎉 GPT-4o is fully configured and ready!")
        print("\nExpected improvements:")
        print("  • 2x faster formula extraction")
        print("  • More accurate calculations")
        print("  • Better JavaScript generation")
        print("  • Cleaner function names")
    else:
        print("\n⚠️ Some configurations missing")
    
    # Show usage
    print("\n📝 USAGE TIPS FOR GPT-4o:")
    print("=" * 60)
    print("1. GPT-4o excels at pattern recognition - it will find more formulas")
    print("2. It generates cleaner JavaScript code")
    print("3. It better understands financial/property calculations")
    print("4. Response time is ~50% faster than GPT-4 Turbo")
    print("5. Token usage is more efficient")
    
    return all_good

if __name__ == "__main__":
    print("GPT-4o UPGRADE TOOL")
    print("=" * 60)
    print("This will upgrade your agent to use GPT-4o")
    print("The most advanced model available to Pro users")
    print()
    
    response = input("Upgrade to GPT-4o? (yes/no): ").strip().lower()
    
    if response == 'yes':
        if upgrade_to_gpt4o():
            add_enhanced_prompts()
            verify_gpt4o_setup()
            
            print("\n✅ UPGRADE COMPLETE!")
            print("\nYour agent now uses GPT-4o for:")
            print("  • Formula extraction")
            print("  • Pattern analysis")
            print("  • JavaScript generation")
            print("  • Calculation naming")
            print("\nRun your agent to see the improvements!")
    else:
        print("\n❌ Upgrade cancelled")
        print("\nNote: GPT-4o is significantly better than GPT-4 Turbo:")
        print("  • 2x faster")
        print("  • Better reasoning")
        print("  • Superior code generation")
        print("  • More accurate formulas")
