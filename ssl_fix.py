#!/usr/bin/env python3
"""
SSL Certificate Fix for AppFolio Replicator
Apply this before running the main script
"""

import ssl
import certifi
import os

def fix_ssl_certificates():
    """Fix SSL certificate issues on macOS"""
    
    # Method 1: Use certifi certificates
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    
    # Method 2: Create unverified context (for testing only)
    ssl._create_default_https_context = ssl._create_unverified_context
    
    print("✅ SSL certificate fix applied")
    print(f"📍 Using certificates from: {certifi.where()}")

if __name__ == "__main__":
    fix_ssl_certificates()
