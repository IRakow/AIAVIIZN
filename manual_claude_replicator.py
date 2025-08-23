#!/usr/bin/env python3
"""
🎯 MANUAL CLAUDE REPLICATOR
Version that guides you through manual Claude interaction
"""

# Apply SSL fix
import ssl
import certifi
import os
ssl._create_default_https_context = ssl._create_unverified_context

# Import main components
import sys
sys.path.append('.')
from appfolio_pixel_perfect_replicator import AppFolioPixelPerfectReplicator
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class ManualClaudeReplicator(AppFolioPixelPerfectReplicator):
    """Version with manual Claude interaction"""
    
    def call_claude_desktop(self, prompt):
        """Manual Claude interaction instead of automation"""
        print("\n" + "="*80)
        print("🤖 CLAUDE DESKTOP INTERACTION NEEDED")
        print("="*80)
        
        # Save prompt to file for easy copying
        prompt_file = "/tmp/claude_prompt.txt"
        with open(prompt_file, 'w') as f:
            f.write(prompt)
        
        print("📝 I've saved a prompt for Claude Desktop.")
        print(f"📁 Prompt saved to: {prompt_file}")
        print()
        print("🔄 PLEASE DO THE FOLLOWING:")
        print("1. Open Claude Desktop")
        print("2. Start a new chat")
        print("3. Copy the prompt below and paste it into Claude")
        print("4. Wait for Claude's complete response")
        print("5. Copy Claude's ENTIRE response")
        print("6. Come back here and paste it")
        print()
        print("📋 PROMPT TO COPY:")
        print("-" * 40)
        print(prompt)
        print("-" * 40)
        print()
        
        # Wait for user to complete Claude interaction
        input("⏸️  Press ENTER when you've sent the prompt to Claude and are ready to paste the response...")
        
        print("📥 Please paste Claude's ENTIRE response below.")
        print("   (Press ENTER twice when done)")
        print()
        
        # Collect multi-line response
        response_lines = []
        print("Paste response:")
        while True:
            line = input()
            if line == "" and len(response_lines) > 0:
                break
            response_lines.append(line)
        
        response = "\n".join(response_lines)
        
        if response.strip():
            return {
                "ai_source": "Claude Desktop (Manual)",
                "validation_result": response,
                "timestamp": "manual_interaction",
                "success": True
            }
        else:
            return {
                "ai_source": "Claude Desktop (Manual)",
                "error": "No response provided",
                "success": False
            }
    
    # Skip external APIs
    async def validate_with_openai(self, page_analysis, page_info):
        return {"ai_source": "OpenAI", "validation_result": "SKIPPED", "success": True, "skipped": True}
    
    async def validate_with_gemini(self, page_analysis, page_info):
        return {"ai_source": "Gemini", "validation_result": "SKIPPED", "success": True, "skipped": True}
    
    async def validate_with_wolfram(self, page_analysis, page_info):
        return {"ai_source": "Wolfram", "validation_result": "SKIPPED", "success": True, "skipped": True}
    
    def analyze_consensus(self, ai_results):
        """Accept if Claude responds"""
        claude_results = [r for r in ai_results if 'Claude' in r.get('ai_source', '') and r.get('success', False)]
        
        return {
            "consensus_achieved": len(claude_results) >= 1,
            "mode": "MANUAL_CLAUDE_ONLY",
            "successful_validations": len(claude_results),
            "recommendation": "Proceed with manual Claude validation" if len(claude_results) >= 1 else "No Claude response",
            "requires_manual_review": len(claude_results) < 1
        }

def main():
    print("🎯 MANUAL CLAUDE APPFOLIO REPLICATOR")
    print("=" * 80)
    print("📋 This version guides you through manual Claude interaction")
    print("   Perfect for when automation isn't working")
    print()
    
    try:
        max_pages = int(input("📊 How many pages to process? (default 3): ") or "3")
    except ValueError:
        max_pages = 3
    
    print(f"\n🚀 Starting manual replication of up to {max_pages} pages...")
    print("   You'll be prompted to interact with Claude Desktop for each page")
    
    replicator = ManualClaudeReplicator()
    
    try:
        success = asyncio.run(replicator.run_complete_appfolio_replication(max_pages))
        
        if success:
            print("\n🎉 MANUAL REPLICATION COMPLETED!")
        else:
            print("\n❌ REPLICATION FAILED")
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user")

if __name__ == "__main__":
    main()
