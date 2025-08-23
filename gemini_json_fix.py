#!/usr/bin/env python3
"""
Fix for Gemini JSON parsing errors
Apply this pattern wherever you see "Using Gemini to analyze JavaScript calculations"
"""

import json
import re

def parse_gemini_response(response_text):
    """
    Safely parse Gemini's response to extract JSON
    Handles cases where Gemini adds text before/after JSON
    """
    try:
        # First try direct parsing
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON array from the response
    content = response_text.strip()
    
    # Remove markdown code blocks if present
    if '```json' in content:
        content = content.split('```json')[1].split('```')[0]
    elif '```' in content:
        content = content.split('```')[1].split('```')[0]
    
    # Find JSON array boundaries
    if '[' in content:
        start_idx = content.find('[')
        if start_idx != -1:
            # Find matching closing bracket
            bracket_count = 0
            end_idx = -1
            in_string = False
            escape_next = False
            
            for i in range(start_idx, len(content)):
                char = content[i]
                
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"' and not escape_next:
                    in_string = not in_string
                
                if not in_string:
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_idx = i
                            break
            
            if end_idx != -1:
                try:
                    json_str = content[start_idx:end_idx + 1]
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
    
    # Try regex pattern
    pattern = r'\[.*?\]'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    
    # If all fails, return empty list
    print(f"    ⚠️ Could not extract JSON from Gemini response")
    return []

# REPLACEMENT CODE PATTERN
# Find this pattern in your code:
"""
print("    ✨ Using Gemini to analyze JavaScript calculations")
response = self.gemini_model.generate_content(prompt)
# ... JSON parsing attempt ...
essential_indices = json.loads(json_match.group())  # THIS IS WHERE IT FAILS
"""

# Replace with this:
"""
print("    ✨ Using Gemini to analyze JavaScript calculations")
try:
    response = self.gemini_model.generate_content(prompt)
    
    # Use the safe parsing function
    essential_indices = parse_gemini_response(response.text)
    
    if not essential_indices:
        print("    ⚠️ Gemini returned no valid indices, skipping script analysis")
        return []
    
    # Continue with your logic...
    for i in essential_indices:
        if i < len(page_data.get('scripts', [])):
            # ... rest of your code
    
except Exception as e:
    print(f"    ⚠️ Error analyzing scripts with Gemini: {e}")
    # Fallback to pattern matching or return empty
    return []
"""
