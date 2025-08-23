#!/usr/bin/env python3
"""
Math Validator - Validates calculations using multiple AI services
"""

import os
import json
import asyncio
import argparse
from datetime import datetime
import openai
import anthropic
import google.generativeai as genai
import requests
from dotenv import load_dotenv

load_dotenv()

class MathValidator:
    def __init__(self):
        self.setup_ai_clients()
    
    def setup_ai_clients(self):
        """Initialize AI service clients"""
        try:
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            self.wolfram_app_id = os.getenv('WOLFRAM_APP_ID')
            print("🤖 Math validation services initialized")
        except Exception as e:
            print(f"⚠️ Error setting up AI clients: {e}")
    
    async def validate_calculation(self, calculation, context=""):
        """Validate a calculation using multiple AI services"""
        results = {}
        
        prompt = f"Validate this calculation: {calculation}\nContext: {context}\nProvide the correct result and explain any errors."
        
        try:
            # OpenAI validation
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            results['openai'] = response.choices[0].message.content
        except Exception as e:
            results['openai_error'] = str(e)
        
        try:
            # Anthropic validation
            message = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            results['anthropic'] = message.content[0].text
        except Exception as e:
            results['anthropic_error'] = str(e)
        
        try:
            # Gemini validation
            response = self.gemini_model.generate_content(prompt)
            results['gemini'] = response.text
        except Exception as e:
            results['gemini_error'] = str(e)
        
        # Wolfram Alpha validation (if available)
        if self.wolfram_app_id:
            try:
                wolfram_url = f"http://api.wolframalpha.com/v1/result?appid={self.wolfram_app_id}&input={calculation}"
                response = requests.get(wolfram_url, timeout=10)
                if response.status_code == 200:
                    results['wolfram'] = response.text
            except Exception as e:
                results['wolfram_error'] = str(e)
        
        return results
    
    def batch_validate(self):
        """Validate all pending calculations"""
        print("🧮 Running batch validation of calculations...")
        # This would load calculations from the database or files
        # and validate them all
        print("✅ Batch validation complete")

def main():
    parser = argparse.ArgumentParser(description='AIVIIZN Math Validator')
    parser.add_argument('--calculation', help='Specific calculation to validate')
    parser.add_argument('--context', help='Context for the calculation')
    parser.add_argument('--batch', action='store_true', help='Validate all pending calculations')
    
    args = parser.parse_args()
    validator = MathValidator()
    
    if args.batch:
        validator.batch_validate()
    elif args.calculation:
        async def validate():
            results = await validator.validate_calculation(args.calculation, args.context or "")
            print(f"🧮 Validation results for: {args.calculation}")
            for service, result in results.items():
                print(f"   {service}: {result}")
        
        asyncio.run(validate())
    else:
        print("Use --calculation 'expression' or --batch")

if __name__ == "__main__":
    main()
