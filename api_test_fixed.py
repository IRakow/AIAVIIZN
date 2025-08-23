#!/usr/bin/env python3
"""
Quick test to verify OpenAI and Gemini API connections work
Fixed version for macOS SSL certificate issues
"""

import os
import asyncio
import aiohttp
import json
import ssl
import certifi

async def test_openai_connection():
    """Test OpenAI API connection with SSL fix"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        return {"success": False, "error": "OPENAI_API_KEY not found"}
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "model": "gpt-4-turbo-preview",
        "messages": [
            {"role": "user", "content": "Calculate 2+2 and respond with just the number."}
        ],
        "max_tokens": 10
    }
    
    try:
        # Create SSL context using certifi certificates
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post('https://api.openai.com/v1/chat/completions',
                                  headers=headers, json=payload, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True, 
                        "response": result['choices'][0]['message']['content'].strip(),
                        "status": "OpenAI connection successful"
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def test_gemini_connection():
    """Test Gemini API connection with SSL fix"""
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        return {"success": False, "error": "GEMINI_API_KEY not found"}
    
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "contents": [{
            "parts": [{"text": "Calculate 3+3 and respond with just the number."}]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 10
        }
    }
    
    try:
        # Create SSL context using certifi certificates
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}',
                                  headers=headers, json=payload, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "response": result['candidates'][0]['content']['parts'][0]['text'].strip(),
                        "status": "Gemini connection successful"
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def run_api_tests():
    """Run all API tests"""
    print("🤖 TESTING MULTI-AI API CONNECTIONS (SSL FIXED)")
    print("=" * 50)
    
    # Test OpenAI
    print("🧮 Testing OpenAI GPT-4...")
    openai_result = await test_openai_connection()
    if openai_result["success"]:
        print(f"✅ OpenAI: {openai_result['status']}")
        print(f"   Response: {openai_result['response']}")
    else:
        print(f"❌ OpenAI: {openai_result['error']}")
    
    print()
    
    # Test Gemini
    print("🧮 Testing Google Gemini...")
    gemini_result = await test_gemini_connection()
    if gemini_result["success"]:
        print(f"✅ Gemini: {gemini_result['status']}")
        print(f"   Response: {gemini_result['response']}")
    else:
        print(f"❌ Gemini: {gemini_result['error']}")
    
    print()
    print("=" * 50)
    
    # Summary
    openai_ok = openai_result["success"]
    gemini_ok = gemini_result["success"]
    
    if openai_ok and gemini_ok:
        print("🎉 ALL API CONNECTIONS WORKING!")
        print("✅ Ready to run multi-AI AppFolio builder")
        return True
    elif openai_ok or gemini_ok:
        working = "OpenAI" if openai_ok else "Gemini"
        not_working = "Gemini" if openai_ok else "OpenAI"
        print(f"⚠️  PARTIAL SUCCESS: {working} working, {not_working} needs setup")
        print("🔧 You can still run with reduced AI validation")
        return False
    else:
        print("❌ NO API CONNECTIONS WORKING")
        print("🔧 Please check your API keys and try again")
        return False

if __name__ == "__main__":
    asyncio.run(run_api_tests())
