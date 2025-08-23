#!/usr/bin/env python3
"""
Check if all requirements are met for the AI agent
"""

import sys
import subprocess

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ⚠️ Python 3.8+ required")
        return False
    return True

def check_imports():
    """Check if all required libraries can be imported"""
    required_imports = [
        ('playwright.async_api', 'Playwright'),
        ('supabase', 'Supabase'),
        ('anthropic', 'Anthropic Claude'),
        ('openai', 'OpenAI GPT-4'),
        ('google.generativeai', 'Google Gemini'),
        ('bs4', 'BeautifulSoup'),
        ('dotenv', 'python-dotenv'),
        ('openpyxl', 'Excel processing'),
    ]
    
    all_good = True
    print("\n📦 Required Libraries:")
    for module, name in required_imports:
        try:
            __import__(module)
            print(f"  ✓ {name} ({module})")
        except ImportError as e:
            print(f"  ❌ {name} ({module}) - NOT INSTALLED")
            all_good = False
    
    return all_good

def check_env_vars():
    """Check environment variables"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    required_vars = [
        ('SUPABASE_URL', 'Supabase URL'),
        ('SUPABASE_SERVICE_KEY', 'Supabase Service Key'),
        ('SUPABASE_KEY', 'Supabase Anon Key'),
        ('ANTHROPIC_API_KEY', 'Claude API Key'),
    ]
    
    optional_vars = [
        ('OPENAI_API_KEY', 'OpenAI API Key'),
        ('GEMINI_API_KEY', 'Gemini API Key'),
        ('TARGET_BASE_URL', 'Target Site URL'),
    ]
    
    all_good = True
    print("\n🔑 Required Environment Variables:")
    for var, name in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✓ {name} ({var}): {'*' * 8}{value[-8:] if len(value) > 8 else '****'}")
        else:
            print(f"  ❌ {name} ({var}): NOT SET")
            all_good = False
    
    print("\n🔑 Optional Environment Variables:")
    for var, name in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✓ {name} ({var}): {'*' * 8}{value[-8:] if len(value) > 8 else '****'}")
        else:
            print(f"  ⚠️ {name} ({var}): NOT SET (optional)")
    
    return all_good

def check_files():
    """Check required files"""
    import os
    from pathlib import Path
    
    base_dir = Path("/Users/ianrakow/Desktop/AIVIIZN")
    
    required_files = [
        'enhanced_field_intelligence.py',
        '.env',
    ]
    
    required_dirs = [
        'templates',
        'static',
        'data',
        'screenshots',
        'tracking',
    ]
    
    all_good = True
    print("\n📁 Required Files:")
    for file in required_files:
        path = base_dir / file
        if path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ❌ {file} - NOT FOUND")
            all_good = False
    
    print("\n📂 Required Directories:")
    for dir in required_dirs:
        path = base_dir / dir
        if path.exists():
            print(f"  ✓ {dir}/")
        else:
            print(f"  ❌ {dir}/ - NOT FOUND")
            all_good = False
    
    return all_good

def check_tracking_files():
    """Check tracking file states"""
    import json
    from pathlib import Path
    
    base_dir = Path("/Users/ianrakow/Desktop/AIVIIZN")
    
    tracking_files = [
        'tracking/processed.json',
        'tracking/queue.json',
        'discovered_links.json',
        'discovery_tracker.json',
        'data/processed_pages.json',
        'data/discovered_links.json',
        'data/identified_fields.json',
        'data/ai_field_mappings.json',
    ]
    
    print("\n📊 Tracking Files Status:")
    for file in tracking_files:
        path = base_dir / file
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        count = len(data)
                        status = "EMPTY" if count == 0 else f"{count} items"
                    elif isinstance(data, dict):
                        if 'discovered_pages' in data:
                            count = len(data.get('discovered_pages', {}))
                            status = "EMPTY" if count == 0 else f"{count} pages"
                        elif 'processed' in data:
                            count = len(data.get('processed', []))
                            status = "EMPTY" if count == 0 else f"{count} processed"
                        else:
                            count = len(data)
                            status = "EMPTY" if count == 0 else f"{count} entries"
                    else:
                        status = "UNKNOWN FORMAT"
                    print(f"  ✓ {file}: {status}")
            except Exception as e:
                print(f"  ⚠️ {file}: Error reading - {e}")
        else:
            print(f"  ❌ {file}: NOT FOUND")

def main():
    print("="*60)
    print("🔍 AIVIIZN AI Agent Requirements Check")
    print("="*60)
    
    checks = []
    
    # Check Python version
    checks.append(check_python_version())
    
    # Check imports
    try:
        checks.append(check_imports())
    except Exception as e:
        print(f"\n❌ Error checking imports: {e}")
        checks.append(False)
    
    # Check environment variables
    try:
        checks.append(check_env_vars())
    except Exception as e:
        print(f"\n❌ Error checking environment: {e}")
        checks.append(False)
    
    # Check files
    try:
        checks.append(check_files())
    except Exception as e:
        print(f"\n❌ Error checking files: {e}")
        checks.append(False)
    
    # Check tracking files
    try:
        check_tracking_files()
    except Exception as e:
        print(f"\n❌ Error checking tracking files: {e}")
    
    # Summary
    print("\n" + "="*60)
    if all(checks):
        print("✅ ALL REQUIREMENTS MET - Ready to run!")
        print("\nTo start the agent, run:")
        print("  python3 aiviizn_real_agent_with_ai_intelligence_updated.py")
    else:
        print("❌ SOME REQUIREMENTS MISSING")
        print("\nTo install missing Python packages:")
        print("  pip install -r requirements_mcp_agent.txt")
        print("  pip install -r requirements.txt")
        print("\nTo set up environment variables:")
        print("  1. Edit the .env file")
        print("  2. Add your API keys")
        print("\nTo install Playwright browsers:")
        print("  playwright install chromium")
    
    print("="*60)

if __name__ == "__main__":
    main()
