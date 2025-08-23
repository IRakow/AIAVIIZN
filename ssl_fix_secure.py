#!/usr/bin/env python3
"""
Secure SSL Certificate Fix for AIVIIZN AppFolio Builder
This fix properly configures SSL without disabling security
"""

import ssl
import certifi
import aiohttp
import os
import sys
from pathlib import Path

def create_secure_ssl_context():
    """Create a secure SSL context using certifi certificates"""
    context = ssl.create_default_context(cafile=certifi.where())
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context

def configure_ssl_environment():
    """Configure environment variables for SSL certificates"""
    cert_file = certifi.where()
    
    # Set environment variables
    os.environ['SSL_CERT_FILE'] = cert_file
    os.environ['REQUESTS_CA_BUNDLE'] = cert_file
    os.environ['CURL_CA_BUNDLE'] = cert_file
    
    print(f"✅ SSL environment configured")
    print(f"📍 Certificate file: {cert_file}")
    
    return cert_file

def create_aiohttp_connector():
    """Create aiohttp connector with proper SSL context"""
    ssl_context = create_secure_ssl_context()
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    return connector

def fix_python_certificates():
    """Fix Python certificate installation (macOS specific)"""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # Common paths for Python certificates
    possible_cert_paths = [
        f"/Applications/Python {python_version}/Install Certificates.command",
        f"/usr/local/bin/python{python_version}",
        "/usr/bin/python3"
    ]
    
    print("🔍 Checking Python certificate installation...")
    
    for path in possible_cert_paths:
        if Path(path).exists():
            print(f"Found Python installation: {path}")
            break
    
    # Try to install certificates
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "certifi"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ certifi package updated successfully")
        else:
            print(f"⚠️ Warning: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ Could not update certifi: {e}")

def apply_comprehensive_ssl_fix():
    """Apply comprehensive SSL fix"""
    print("🔧 Applying comprehensive SSL fix...")
    
    # Step 1: Fix Python certificates
    fix_python_certificates()
    
    # Step 2: Configure environment
    configure_ssl_environment()
    
    # Step 3: Test SSL connection
    test_ssl_connection()
    
    print("✅ SSL fix complete!")

def test_ssl_connection():
    """Test SSL connection to API endpoints"""
    import requests
    
    test_urls = [
        "https://api.openai.com",
        "https://generativelanguage.googleapis.com", 
        "https://api.wolframalpha.com",
        "https://api.anthropic.com"
    ]
    
    print("🧪 Testing SSL connections...")
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url}: Connection successful")
        except requests.exceptions.SSLError as e:
            print(f"❌ {url}: SSL Error - {e}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ {url}: Connection error (may be normal) - {type(e).__name__}")

if __name__ == "__main__":
    apply_comprehensive_ssl_fix()
