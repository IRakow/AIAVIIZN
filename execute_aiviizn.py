#!/usr/bin/env python3
"""
🚀 AIVIIZN EXECUTION SCRIPT
Run this to execute the working AIVIIZN system using Claude MCP tools

This script provides the exact steps to execute with Claude.
"""

import os
import json
from datetime import datetime

def main():
    print("🚀 AIVIIZN REAL WORKING SYSTEM - EXECUTION GUIDE")
    print("=" * 60)
    print()
    
    # Load configuration
    config_path = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        print("✅ Configuration loaded successfully")
        print(f"📊 Project ID: {config.get('project_id')}")
        print(f"🔗 URLs to process: {len(config.get('verified_urls', []))}")
        print()
    else:
        print("❌ Configuration file not found!")
        return
    
    print("📋 STEP-BY-STEP EXECUTION:")
    print()
    
    print("STEP 1: Initialize Database")
    print("=" * 30)
    print("Execute this in Claude chat:")
    print()
    print("Create the database tables with supabase:execute_sql")
    print()
    
    print("STEP 2: Capture AppFolio Pages")
    print("=" * 30)
    print("For each URL, execute these MCP tools in sequence:")
    print("1. playwright:browser_navigate")
    print("2. playwright:browser_evaluate")
    print("3. playwright:browser_take_screenshot")
    print("4. supabase:execute_sql (to store data)")
    print()
    
    print("STEP 3: Generate Working Templates")
    print("=" * 30)
    print("Use filesystem:write_file to create:")
    print("- HTML templates in /templates/reports/")
    print("- JavaScript files in /static/js/")
    print("- Flask routes in /app/routes/")
    print()
    
    print("🔗 URLs TO PROCESS:")
    for i, url in enumerate(config.get('verified_urls', []), 1):
        print(f"{i}. {url}")
    print()
    
    print("🎯 TO START: Run the working system file:")
    print("python3 aiviizn_real_working_system.py")
    print()
    print("Then execute each step using Claude MCP tools as shown above.")

if __name__ == "__main__":
    main()
