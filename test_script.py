#!/usr/bin/env python3

print("🧪 Testing script basics...")

# Test imports
try:
    import os
    import json
    import time
    import subprocess
    import webbrowser
    from datetime import datetime
    from typing import List, Dict
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")

# Test basic functionality
try:
    from autonomous_appfolio_builder import AutonomousAppFolioBuilder
    builder = AutonomousAppFolioBuilder()
    print(f"✅ Builder created, {len(builder.priority_urls)} URLs loaded")
    print(f"📋 First URL: {builder.priority_urls[0]}")
    
    # Test page name extraction
    test_url = builder.priority_urls[0]
    page_name = builder.get_page_name(test_url)
    template_name = builder.get_template_name(test_url)
    print(f"📄 Page name: {page_name}")
    print(f"📁 Template name: {template_name}")
    
except Exception as e:
    print(f"❌ Builder error: {e}")
    import traceback
    traceback.print_exc()

print("🧪 Test complete")
