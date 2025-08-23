#!/usr/bin/env python3
"""
PRODUCTION FIX: Environment and Dependencies Setup
Fixes only the broken parts for production deployment
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def install_production_dependencies():
    """Install latest production dependencies"""
    print("🚀 Installing PRODUCTION dependencies with latest versions...")
    
    # Upgrade pip first
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # Install from production requirements
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_production.txt"], check=True)
    
    # Install Playwright browsers
    subprocess.run(["playwright", "install", "chromium"], check=True)
    subprocess.run(["playwright", "install-deps"], check=True)
    
    print("✅ Production dependencies installed")

def fix_env_loading():
    """Add proper environment loading to existing scripts WITHOUT changing functionality"""
    print("🔧 Fixing environment loading...")
    
    # Add dotenv loading to the beginning of each script
    env_fix = """
# PRODUCTION FIX: Proper environment loading
from dotenv import load_dotenv
load_dotenv()
"""
    
    scripts = ['terminal_agent.py', 'math_validator.py', 'link_tracker.py']
    
    for script in scripts:
        if os.path.exists(script):
            with open(script, 'r') as f:
                content = f.read()
            
            # Only add if not already present
            if 'from dotenv import load_dotenv' not in content:
                # Insert after the first import block
                lines = content.split('\n')
                
                # Find the end of the docstring and imports
                insert_pos = 0
                in_docstring = False
                for i, line in enumerate(lines):
                    if '"""' in line:
                        in_docstring = not in_docstring
                        if not in_docstring:
                            insert_pos = i + 1
                    elif not in_docstring and (line.startswith('import ') or line.startswith('from ')):
                        insert_pos = max(insert_pos, i + 1)
                
                # Insert the fix
                lines.insert(insert_pos, env_fix)
                
                with open(script, 'w') as f:
                    f.write('\n'.join(lines))
                
                print(f"✅ Fixed environment loading in {script}")

def create_directories():
    """Create all necessary directories"""
    print("📁 Creating production directories...")
    
    dirs = [
        'screenshots', 'logs', 'reports', 'templates/reports', 
        'templates/admin', 'templates/properties', 'templates/accounting',
        'templates/maintenance', 'templates/leasing', 'templates/communication'
    ]
    
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def make_executable():
    """Make scripts executable"""
    print("🔐 Setting executable permissions...")
    
    for file in Path('.').glob('*.py'):
        os.chmod(file, 0o755)
    for file in Path('.').glob('*.sh'):
        os.chmod(file, 0o755)
    
    print("✅ Scripts made executable")

def main():
    """Run production fixes"""
    print("🔥 PRODUCTION FIXES - AIVIIZN Terminal Agent")
    print("=" * 50)
    
    if not os.path.exists('.env'):
        print("❌ Run from AIVIIZN directory (where .env is)")
        sys.exit(1)
    
    try:
        install_production_dependencies()
        fix_env_loading() 
        create_directories()
        make_executable()
        
        print("\n🎉 PRODUCTION FIXES COMPLETE!")
        print("🚀 System is now production-ready")
        print("\n▶️  Start with: ./quick_start.sh")
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
