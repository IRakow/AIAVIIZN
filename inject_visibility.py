#!/usr/bin/env python3
"""
DIRECT INJECTION: Add real-time template visibility
This will show you EXACTLY what's being created as it happens
"""

# Open the agent file and find the save_template method
agent_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py"

# Read the file
with open(agent_file, 'r') as f:
    lines = f.readlines()

# Find the save_template method line by line
for i, line in enumerate(lines):
    if 'def save_template(self, url: str, html: str) -> str:' in line:
        print(f"Found save_template at line {i+1}")
        
        # Find where to inject the logging (after "try:")
        for j in range(i+1, min(i+20, len(lines))):
            if 'try:' in lines[j]:
                # Insert logging right after try:
                indent = '            '  # Adjust indent as needed
                
                # Find where template_path is set
                for k in range(j+1, min(j+50, len(lines))):
                    if 'with open(template_path' in lines[k]:
                        # Insert our logging right before the file write
                        logging_code = f'''
            # REAL-TIME VISIBILITY - SHOW WHAT'S BEING CREATED
            print(f"\\n{'='*60}")
            print(f"🎯 CREATING TEMPLATE RIGHT NOW:")
            print(f"📂 DIRECTORY: {{template_path.parent}}")
            print(f"📄 FILENAME: {{template_path.name}}")
            print(f"🔗 FULL PATH: {{template_path}}")
            print(f"💾 SIZE: {{len(html):,}} bytes")
            print(f"🌐 FROM URL: {{url}}")
            print(f"{'='*60}\\n")
            
'''
                        lines.insert(k, logging_code)
                        
                        # Write back
                        with open(agent_file, 'w') as f:
                            f.writelines(lines)
                        
                        print("\n✅ SUCCESS! Real-time visibility added!")
                        print("\n🎯 You will now see for EVERY template:")
                        print("   📂 The exact directory")
                        print("   📄 The exact filename") 
                        print("   🔗 The full path")
                        print("   💾 The file size")
                        print("   🌐 The source URL")
                        print("\nRun your agent NOW to see this output!")
                        exit(0)
                        
print("❌ Could not patch - please add manually")
