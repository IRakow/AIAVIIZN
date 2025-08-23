#!/usr/bin/env python3
"""
AIVIIZN Clean Slate Script
Resets everything for a fresh start
"""

import os
import json
import shutil
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

# Load environment
load_dotenv()

def clean_slate():
    """Reset everything to start fresh"""
    print("🧹 AIVIIZN CLEAN SLATE - Starting fresh")
    print("=" * 60)
    
    project_root = Path("/Users/ianrakow/Desktop/AIVIIZN")
    
    # 1. Clear state files
    print("\n📁 Clearing state files...")
    state_files = {
        "processed_pages.json": [],
        "discovered_links.json": []
    }
    
    for filename, content in state_files.items():
        filepath = project_root / "data" / filename
        with open(filepath, 'w') as f:
            json.dump(content, f, indent=2)
        print(f"  ✓ Reset {filename}")
    
    # 2. Clear screenshots
    print("\n📸 Clearing screenshots...")
    screenshots_dir = project_root / "data" / "screenshots"
    if screenshots_dir.exists():
        for screenshot in screenshots_dir.glob("*.png"):
            screenshot.unlink()
            print(f"  ✓ Deleted {screenshot.name}")
    
    # 3. Clear generated templates (keep base.html and core templates)
    print("\n📄 Clearing generated templates...")
    keep_templates = ['base.html', 'login.html', 'dashboard.html']
    templates_dir = project_root / "templates"
    
    # Clear subdirectories but keep structure
    subdirs_to_clean = ['reports', 'properties', 'vacancies', 'accounting', 'maintenance', 'leasing']
    for subdir in subdirs_to_clean:
        subdir_path = templates_dir / subdir
        if subdir_path.exists():
            for template in subdir_path.glob("*.html"):
                template.unlink()
                print(f"  ✓ Deleted {subdir}/{template.name}")
    
    # 4. Clear log file
    print("\n📝 Clearing log file...")
    log_file = project_root / "agent.log"
    if log_file.exists():
        # Keep the file but clear contents
        with open(log_file, 'w') as f:
            f.write("")
        print("  ✓ Log file cleared")
    
    # 5. Clear Supabase tables
    print("\n🗄️ Clearing Supabase tables...")
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)
            
            # Clear calculations first (foreign key constraint)
            result = supabase.table('calculations').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            print(f"  ✓ Cleared calculations table")
            
            # Clear pages
            result = supabase.table('pages').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            print(f"  ✓ Cleared pages table")
        else:
            print("  ⚠️ Supabase credentials not found - skip database clearing")
            print("     Run these SQL commands manually in Supabase:")
            print("     DELETE FROM calculations;")
            print("     DELETE FROM pages;")
    except Exception as e:
        print(f"  ⚠️ Could not clear Supabase: {e}")
        print("     Run these SQL commands manually in Supabase:")
        print("     DELETE FROM calculations;")
        print("     DELETE FROM pages;")
    
    print("\n" + "=" * 60)
    print("✨ CLEAN SLATE COMPLETE!")
    print("=" * 60)
    print("\nYour AIVIIZN system is reset and ready for a fresh start:")
    print("  ✓ State files cleared")
    print("  ✓ Screenshots removed")
    print("  ✓ Generated templates cleaned")
    print("  ✓ Log file reset")
    print("  ✓ Database tables cleared (or instructions provided)")
    print("\n🚀 You can now run: python aiviizn_real_agent.py")
    print("   The agent will start completely fresh!")

if __name__ == "__main__":
    response = input("\n⚠️ This will clear all processed data. Continue? (y/n): ")
    if response.lower() == 'y':
        clean_slate()
    else:
        print("Cancelled.")
