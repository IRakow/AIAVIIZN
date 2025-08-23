#!/usr/bin/env python3
"""
AIVIIZN MCP Terminal Agent - Works with Claude MCP servers
This agent coordinates with Claude's MCP servers for processing
"""

import os
import json
import time
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class MCPTerminalAgent:
    """Terminal agent that coordinates with Claude MCP servers"""
    
    def __init__(self):
        self.session_start = datetime.now()
        self.processed_urls = set()
        self.pending_urls = []
        self.links_file = "discovered_links.json"
        self.load_session_data()
    
    def load_session_data(self):
        """Load existing session data"""
        try:
            if os.path.exists(self.links_file):
                with open(self.links_file, 'r') as f:
                    data = json.load(f)
                    self.processed_urls = set(data.get('processed', []))
                    self.pending_urls = data.get('pending', [])
                    print(f"📊 Loaded {len(self.processed_urls)} processed, {len(self.pending_urls)} pending URLs")
        except Exception as e:
            print(f"⚠️ Error loading session data: {e}")
    
    def save_session_data(self):
        """Save current session state"""
        try:
            data = {
                'processed': list(self.processed_urls),
                'pending': self.pending_urls,
                'session_start': self.session_start.isoformat(),
                'last_update': datetime.now().isoformat()
            }
            
            with open(self.links_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Error saving session data: {e}")
    
    def start_claude_session(self, url):
        """Open Claude Desktop for MCP-powered processing"""
        try:
            # Create instructions for Claude
            instructions = f"""
🤖 AIVIIZN MCP Agent Instructions

Process this AppFolio page using your MCP servers:

**Target URL:** {url}

**Using MCP Servers:**
1. **Playwright MCP** - Navigate to URL, capture screenshots
2. **Supabase MCP** - Store page data and analysis
3. **Filesystem MCP** - Save templates and files

**Tasks:**
1. Navigate to: {url}
2. Take full page screenshot
3. Extract all calculations and formulas
4. Analyze page functionality and design
5. Generate AIVIIZN template in /templates/ directory
6. Store analysis in Supabase
7. Discover and record all AppFolio links
8. Validate calculations with multiple AI services

**Template Structure:**
- Replace "AppFolio" with "AIVIIZN"
- Replace "Celtic Property" with "AIVIIZN"
- Keep exact layout and functionality
- Store in appropriate /templates/ subdirectory

**Return:** Confirmation of completion and discovered links
"""
            
            # Save instructions to file
            instructions_file = f"instructions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(instructions_file, 'w') as f:
                f.write(instructions)
            
            print(f"📝 Instructions saved: {instructions_file}")
            print(f"🤖 Ready for Claude MCP processing of: {url}")
            
            return instructions_file
            
        except Exception as e:
            print(f"⚠️ Error creating Claude session: {e}")
            return None
    
    def open_browser_to_url(self, url):
        """Open browser to the target URL"""
        try:
            print(f"🌐 Opening browser to: {url}")
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"⚠️ Error opening browser: {e}")
            return False
    
    def process_with_mcp(self, start_url=None):
        """Start processing with MCP coordination"""
        
        if not start_url:
            start_url = "https://celticprop.appfolio.com/reports"
        
        if start_url not in self.pending_urls and start_url not in self.processed_urls:
            self.pending_urls.append(start_url)
        
        print(f"\n🎯 AIVIIZN MCP Terminal Agent Started")
        print(f"📍 Starting URL: {start_url}")
        print(f"⏰ Session started: {self.session_start}")
        print(f"🤖 Using Claude MCP servers for processing")
        print(f"📊 Current status: {len(self.processed_urls)} processed, {len(self.pending_urls)} pending")
        
        # Open browser for manual login if needed
        self.open_browser_to_url(start_url)
        
        print(f"\n🔐 Please log into AppFolio in the browser if needed")
        print(f"📱 Then return here to coordinate with Claude MCP processing")
        
        while self.pending_urls:
            current_url = self.pending_urls[0]
            
            print(f"\n🔍 Ready to process: {current_url}")
            
            # Create instructions for Claude
            instructions_file = self.start_claude_session(current_url)
            
            if instructions_file:
                print(f"\n🤖 Claude MCP Processing Instructions:")
                print(f"   1. Use Playwright MCP to navigate to: {current_url}")
                print(f"   2. Use Supabase MCP to store analysis")
                print(f"   3. Use Filesystem MCP to save templates")
                print(f"   4. Process instructions from: {instructions_file}")
                
                # Wait for user confirmation that Claude completed the task
                print(f"\n⏸️ Coordinate with Claude to process this page")
                print(f"   Tell Claude to follow instructions in: {instructions_file}")
                print(f"   When Claude completes processing, press Enter...")
                
                input()
                
                # Mark as processed
                self.pending_urls.remove(current_url)
                self.processed_urls.add(current_url)
                self.save_session_data()
                
                print(f"✅ Marked as completed: {current_url}")
                print(f"📊 Progress: {len(self.processed_urls)} processed, {len(self.pending_urls)} pending")
                
                # Brief pause before next
                time.sleep(1)
            else:
                print(f"❌ Failed to create instructions for: {current_url}")
                self.pending_urls.remove(current_url)
        
        print(f"\n🎉 All queued pages processed!")
        print(f"📊 Final status: {len(self.processed_urls)} pages processed")
        print(f"📁 Check templates/ directory for generated files")
        print(f"🗄️ Check Supabase for stored analysis data")
    
    def add_url(self, url):
        """Add URL to processing queue"""
        if url not in self.processed_urls and url not in self.pending_urls:
            self.pending_urls.append(url)
            self.save_session_data()
            print(f"➕ Added to queue: {url}")
        else:
            print(f"⚠️ URL already processed or queued: {url}")
    
    def show_status(self):
        """Show current processing status"""
        print(f"\n📊 AIVIIZN MCP Agent Status:")
        print(f"   Processed: {len(self.processed_urls)}")
        print(f"   Pending: {len(self.pending_urls)}")
        print(f"   Session started: {self.session_start}")
        
        if self.pending_urls:
            print(f"\n🔗 Next 5 pending URLs:")
            for i, url in enumerate(self.pending_urls[:5]):
                print(f"   {i+1}. {url}")
        
        if self.processed_urls:
            print(f"\n✅ Recently processed:")
            recent = list(self.processed_urls)[-3:]
            for url in recent:
                print(f"   ✓ {url}")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AIVIIZN MCP Terminal Agent')
    parser.add_argument('--url', help='Add specific URL to queue')
    parser.add_argument('--start-reports', action='store_true', help='Start with reports page')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--add', help='Add URL to queue')
    
    args = parser.parse_args()
    
    agent = MCPTerminalAgent()
    
    if args.status:
        agent.show_status()
    elif args.add:
        agent.add_url(args.add)
    elif args.url:
        agent.process_with_mcp(args.url)
    elif args.start_reports:
        agent.process_with_mcp("https://celticprop.appfolio.com/reports")
    else:
        # Interactive mode
        print("🚀 AIVIIZN MCP Terminal Agent")
        print("=" * 40)
        print("1. Start with reports page")
        print("2. Process specific URL") 
        print("3. Show status")
        print("4. Add URL to queue")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            agent.process_with_mcp("https://celticprop.appfolio.com/reports")
        elif choice == "2":
            url = input("Enter URL: ").strip()
            if url:
                agent.process_with_mcp(url)
        elif choice == "3":
            agent.show_status()
        elif choice == "4":
            url = input("Enter URL to add: ").strip()
            if url:
                agent.add_url(url)
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
