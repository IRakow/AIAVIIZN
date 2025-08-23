#!/usr/bin/env python3
"""
Backup all agent-related files to 'Agent All Working' directory
"""

import shutil
import os
from pathlib import Path
from datetime import datetime

# Source and destination directories
source_dir = Path("/Users/ianrakow/Desktop/AIVIIZN")
backup_dir = source_dir / "Agent All Working"

# Create backup timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_info_file = backup_dir / f"backup_info_{timestamp}.txt"

# List of important files to backup
important_files = [
    # Main agent files
    "aiviizn_real_agent_with_ai_intelligence_updated.py",
    "aiviizn_real_agent_with_ai_intelligence.py",
    "enhanced_field_intelligence.py",
    "dual_model_analyzer.py",
    "field_consensus_analyzer.py",
    "comprehensive_data_extractor.py",
    "calculation_capture_test.py",
    "automated_appfolio_builder_PLAYWRIGHT_ENHANCED.py",
    
    # Configuration files
    ".env",
    "aiviizn_config.json",
    
    # Database schemas
    "complete_database_setup.sql",
    "database_field_mapping_schema.sql",
    "supabase_maintenance_schema.sql",
    "schema.sql",
    "database_setup.sql",
    
    # Scripts and utilities
    "auto.sh",
    "run.sh",
    "monitor_progress.sh",
    "deploy_production.sh",
    "fix_schema_now.py",
    "fix_pages_table_schema.sql",
    
    # Documentation
    "README.md",
    "PROJECT_DOCUMENTATION.md",
    "README_COMPREHENSIVE_APPFOLIO_CLONE.md",
    "INTERLINKING_SYSTEM_DOCUMENTATION.md",
    "AI_FIELD_INTELLIGENCE_README.md",
    
    # Recent fixes and patches
    "replace_save_template.py",
    "fix_template_directories.py",
    "inject_visibility.py",
    "template_logging_patch.py",
    
    # App files
    "app.py",
    "app_generated.py",
    "dashboard.html",
    
    # Important data files
    "data/processed_pages.json",
    "data/discovered_links.json", 
    "data/identified_fields.json",
    "data/ai_field_mappings.json",
    "data/statistics.json",
]

# Directories to backup
important_dirs = [
    "templates",
    "static",
    "data",
    "session_data",
    "screenshots",
]

print("🔄 BACKING UP AGENT FILES TO 'Agent All Working'")
print("=" * 60)

# Copy individual files
copied_files = 0
skipped_files = 0

for file_path in important_files:
    source_file = source_dir / file_path
    if source_file.exists():
        # Create subdirectory if needed
        dest_file = backup_dir / file_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(source_file, dest_file)
            copied_files += 1
            print(f"✅ Copied: {file_path}")
        except Exception as e:
            print(f"⚠️ Error copying {file_path}: {e}")
            skipped_files += 1
    else:
        if not file_path.startswith("data/"):  # Don't warn about data files
            print(f"⚠️ Not found: {file_path}")
        skipped_files += 1

# Copy directories
print("\n📁 Copying directories...")
for dir_name in important_dirs:
    source_subdir = source_dir / dir_name
    if source_subdir.exists() and source_subdir.is_dir():
        dest_subdir = backup_dir / dir_name
        try:
            if dest_subdir.exists():
                shutil.rmtree(dest_subdir)
            shutil.copytree(source_subdir, dest_subdir)
            # Count files in directory
            file_count = sum(1 for _ in dest_subdir.rglob('*') if _.is_file())
            print(f"✅ Copied directory: {dir_name} ({file_count} files)")
        except Exception as e:
            print(f"⚠️ Error copying directory {dir_name}: {e}")

# Create backup info file
with open(backup_info_file, 'w') as f:
    f.write(f"AIVIIZN Agent Backup\n")
    f.write(f"Timestamp: {timestamp}\n")
    f.write(f"Files copied: {copied_files}\n")
    f.write(f"Files skipped: {skipped_files}\n")
    f.write(f"\nBackup includes:\n")
    f.write("- Main agent scripts\n")
    f.write("- Configuration files\n")
    f.write("- Database schemas\n")
    f.write("- Templates directory\n")
    f.write("- Data directory\n")
    f.write("- Session data\n")
    f.write("- Screenshots\n")

print("\n" + "=" * 60)
print(f"✅ BACKUP COMPLETE!")
print(f"📁 Location: {backup_dir}")
print(f"📊 Files copied: {copied_files}")
print(f"📊 Files skipped: {skipped_files}")
print(f"📄 Backup info: {backup_info_file.name}")
print("=" * 60)

# Show backup size
total_size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
print(f"💾 Total backup size: {total_size / (1024*1024):.2f} MB")
