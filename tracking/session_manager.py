"""
AIVIIZN Page Processing Session Manager
Use this in any Claude chat to continue processing
"""

import json
from pathlib import Path

class SessionManager:
    def __init__(self):
        self.tracking_dir = Path("/Users/ianrakow/Desktop/AIVIIZN/tracking")
        self.state_file = self.tracking_dir / "state.json"
        self.processed_file = self.tracking_dir / "processed.json"
        self.queue_file = self.tracking_dir / "queue.json"
        self.formulas_file = self.tracking_dir / "formulas.json"
        self.mappings_file = self.tracking_dir / "data_mappings.json"
        
    def get_current_state(self):
        """Check what needs to be done next"""
        with open(self.state_file, 'r') as f:
            state = json.load(f)
        
        with open(self.processed_file, 'r') as f:
            processed = json.load(f)
            
        with open(self.queue_file, 'r') as f:
            queue = json.load(f)
            
        # Find next unprocessed page
        next_page = None
        for page in queue:
            if page not in processed:
                next_page = page
                break
                
        return {
            'status': state['current_status'],
            'last_processed': state['last_processed'],
            'next_to_process': next_page,
            'total_processed': len(processed),
            'remaining': len(queue) - len(processed),
            'session_count': state['session_count']
        }
        
    def mark_page_complete(self, url, template_path, formulas):
        """Mark a page as processed"""
        # Update processed list
        with open(self.processed_file, 'r') as f:
            processed = json.load(f)
        
        if url not in processed:
            processed.append(url)
            
        with open(self.processed_file, 'w') as f:
            json.dump(processed, f, indent=2)
            
        # Update state
        with open(self.state_file, 'r') as f:
            state = json.load(f)
            
        state['last_processed'] = url
        state['current_status'] = 'ready_for_next'
        state['session_count'] += 1
        state['last_updated'] = str(datetime.now())
        
        # Find next page
        with open(self.queue_file, 'r') as f:
            queue = json.load(f)
            
        next_page = None
        for page in queue:
            if page not in processed:
                next_page = page
                break
                
        state['next_to_process'] = next_page
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
        # Save formulas
        with open(self.formulas_file, 'r') as f:
            all_formulas = json.load(f)
            
        all_formulas[url] = formulas
        
        with open(self.formulas_file, 'w') as f:
            json.dump(all_formulas, f, indent=2)
            
        return {
            'completed': url,
            'template': template_path,
            'next': next_page,
            'progress': f"{len(processed)}/{len(queue)}"
        }
        
    def get_progress_report(self):
        """Get detailed progress report"""
        with open(self.processed_file, 'r') as f:
            processed = json.load(f)
            
        with open(self.queue_file, 'r') as f:
            queue = json.load(f)
            
        return {
            'completed_pages': processed,
            'remaining_pages': [p for p in queue if p not in processed],
            'completion_percentage': (len(processed) / len(queue) * 100) if queue else 0
        }

# Usage in any chat:
# from session_manager import SessionManager
# sm = SessionManager()
# state = sm.get_current_state()
# print(f"Next to process: {state['next_to_process']}")
