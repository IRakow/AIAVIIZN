#!/usr/bin/env python3
"""
Link Tracker - Manages discovered AppFolio links
"""

import json
import os
import argparse
from datetime import datetime

class LinkTracker:
    def __init__(self):
        self.links_file = "discovered_links.json"
        self.load_links()
    
    def load_links(self):
        """Load existing links data"""
        try:
            if os.path.exists(self.links_file):
                with open(self.links_file, 'r') as f:
                    data = json.load(f)
                    self.processed = set(data.get('processed', []))
                    self.pending = data.get('pending', [])
            else:
                self.processed = set()
                self.pending = []
        except Exception as e:
            print(f"Error loading links: {e}")
            self.processed = set()
            self.pending = []
    
    def status(self):
        """Show current status"""
        print(f"📊 Link Status:")
        print(f"   Processed: {len(self.processed)}")
        print(f"   Pending: {len(self.pending)}")
        print(f"   Total discovered: {len(self.processed) + len(self.pending)}")
        
        if self.pending:
            print(f"\n🔗 Next 5 pending links:")
            for i, link in enumerate(self.pending[:5]):
                print(f"   {i+1}. {link}")
    
    def next_link(self):
        """Get next link to process"""
        if self.pending:
            return self.pending[0]
        else:
            print("No pending links")
            return None
    
    def generate_report(self):
        """Generate progress report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'processed_count': len(self.processed),
            'pending_count': len(self.pending),
            'processed_links': list(self.processed),
            'pending_links': self.pending
        }
        
        report_file = f"reports/link_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved: {report_file}")

def main():
    parser = argparse.ArgumentParser(description='AIVIIZN Link Tracker')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--next', action='store_true', help='Get next link to process')
    parser.add_argument('--report', action='store_true', help='Generate progress report')
    
    args = parser.parse_args()
    tracker = LinkTracker()
    
    if args.status:
        tracker.status()
    elif args.next:
        next_link = tracker.next_link()
        if next_link:
            print(f"🔗 Next link: {next_link}")
    elif args.report:
        tracker.generate_report()
    else:
        tracker.status()

if __name__ == "__main__":
    main()
