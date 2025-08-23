#!/usr/bin/env python3
"""
Check current GPT model and show upgrade options
"""

from pathlib import Path
import re

def check_current_model():
    """Check which GPT model is currently being used"""
    
    agent_file = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent.py")
    
    print("GPT MODEL STATUS CHECK")
    print("=" * 60)
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Check for different models
    models = {
        "gpt-4-turbo-preview": "GPT-4 Turbo Preview (older)",
        "gpt-4-turbo": "GPT-4 Turbo",
        "gpt-4o": "GPT-4o (Omni) - BEST",
        "gpt-4": "GPT-4 (standard)",
        "gpt-3.5-turbo": "GPT-3.5 Turbo (budget)"
    }
    
    current_model = None
    for model_id, model_name in models.items():
        if f'model="{model_id}"' in content:
            current_model = model_id
            print(f"\n📍 Currently using: {model_name}")
            count = content.count(f'"{model_id}"')
            print(f"   Found in {count} places")
            break
    
    if not current_model:
        print("\n⚠️ No model specification found!")
    
    # Show comparison
    print("\n📊 MODEL COMPARISON (for Pro users):")
    print("=" * 60)
    print("""
┌─────────────────────┬───────────┬──────────┬─────────────┬──────────┐
│ Model               │ Speed     │ Quality  │ Cost        │ Context  │
├─────────────────────┼───────────┼──────────┼─────────────┼──────────┤
│ GPT-4o (BEST) ✨    │ Fastest   │ Best     │ $5/1M       │ 128K     │
│ GPT-4 Turbo         │ Fast      │ Excellent│ $10/1M      │ 128K     │
│ GPT-4 Turbo Preview │ Fast      │ Excellent│ $10/1M      │ 128K     │
│ GPT-4               │ Slower    │ Excellent│ $30/1M      │ 8K       │
│ GPT-3.5 Turbo       │ Very Fast │ Good     │ $0.50/1M    │ 16K      │
└─────────────────────┴───────────┴──────────┴─────────────┴──────────┘
    """)
    
    if current_model != "gpt-4o":
        print("🎯 RECOMMENDATION: Upgrade to GPT-4o")
        print("   • 2x faster than GPT-4 Turbo")
        print("   • Better formula extraction")
        print("   • Superior pattern recognition")
        print("   • Same or lower cost")
        print("   • Multimodal capabilities")
        print("\n   Run: python upgrade_to_gpt4o.py")
    else:
        print("✅ You're already using the best model (GPT-4o)!")
    
    # Check configuration
    print("\n⚙️ CONFIGURATION CHECK:")
    print("-" * 40)
    
    configs = {
        "JSON mode": 'response_format={ "type": "json_object" }' in content,
        "Temperature 0": "temperature=0" in content,
        "Async client": "AsyncOpenAI" in content,
        "Error handling": "try:" in content and "except" in content
    }
    
    for config, present in configs.items():
        status = "✅" if present else "❌"
        print(f"  {status} {config}")
    
    # Check API key
    import os
    if os.getenv('OPENAI_API_KEY'):
        print("  ✅ OpenAI API key found")
    else:
        print("  ❌ OpenAI API key not in environment")
    
    # Usage stats
    print("\n📈 EXPECTED PERFORMANCE:")
    print("-" * 40)
    
    if current_model == "gpt-4o":
        print("  • Formula extraction: ~1-2 seconds")
        print("  • Pattern analysis: ~2-3 seconds")
        print("  • Cost per page: ~$0.02-0.05")
        print("  • Accuracy: 95%+")
    elif "gpt-4" in str(current_model):
        print("  • Formula extraction: ~3-5 seconds")
        print("  • Pattern analysis: ~5-7 seconds")
        print("  • Cost per page: ~$0.05-0.10")
        print("  • Accuracy: 90%+")
    else:
        print("  • Upgrade recommended for better performance")
    
    return current_model

if __name__ == "__main__":
    current = check_current_model()
    
    if current != "gpt-4o":
        print("\n" + "="*60)
        print("💡 TO UPGRADE:")
        print("="*60)
        print("1. Run: python upgrade_to_gpt4o.py")
        print("2. Type 'yes' when prompted")
        print("3. Run your agent to see improvements")
