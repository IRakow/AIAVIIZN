#!/usr/bin/env python3
"""
Fix for JSON parsing errors when using Gemini to analyze calculations
"""

import json
import re

def safe_parse_gemini_json(response_text):
    """
    Safely parse JSON from Gemini response, handling common issues
    """
    if not response_text:
        return None
    
    # Original response for debugging
    original = response_text
    
    # Method 1: Try to parse as-is
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Method 2: Extract JSON from markdown code blocks
    if '```json' in response_text:
        match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
    
    # Method 3: Extract JSON from any code blocks
    if '```' in response_text:
        match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
    
    # Method 4: Find JSON object or array
    # Look for {...} or [...]
    json_object_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
    json_array_match = re.search(r'\[[^\[\]]*\]', response_text, re.DOTALL)
    
    if json_object_match:
        try:
            return json.loads(json_object_match.group())
        except json.JSONDecodeError:
            pass
    
    if json_array_match:
        try:
            return json.loads(json_array_match.group())
        except json.JSONDecodeError:
            pass
    
    # Method 5: Try to find nested JSON with multiple levels
    # This handles more complex JSON structures
    def find_json_boundaries(text, start_char, end_char):
        start_idx = text.find(start_char)
        if start_idx == -1:
            return None
        
        count = 0
        in_string = False
        escape_next = False
        
        for i in range(start_idx, len(text)):
            if escape_next:
                escape_next = False
                continue
            
            if text[i] == '\\' and not escape_next:
                escape_next = True
                continue
            
            if text[i] == '"' and not escape_next:
                in_string = not in_string
            
            if not in_string:
                if text[i] == start_char:
                    count += 1
                elif text[i] == end_char:
                    count -= 1
                    if count == 0:
                        return text[start_idx:i+1]
        
        return None
    
    # Try to find object
    json_str = find_json_boundaries(response_text, '{', '}')
    if json_str:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try to find array
    json_str = find_json_boundaries(response_text, '[', ']')
    if json_str:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Method 6: Clean up common issues
    cleaned = response_text.strip()
    
    # Remove BOM if present
    if cleaned.startswith('\ufeff'):
        cleaned = cleaned[1:]
    
    # Remove trailing commas
    cleaned = re.sub(r',\s*}', '}', cleaned)
    cleaned = re.sub(r',\s*]', ']', cleaned)
    
    # Try parsing cleaned version
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # If all methods fail, return None
    print(f"Failed to parse JSON from Gemini response")
    print(f"Response preview: {response_text[:200]}...")
    return None


# Example usage for fixing calculation analysis
def analyze_calculations_with_gemini(gemini_model, calculations_text):
    """
    Analyze calculations using Gemini and safely parse the JSON response
    """
    prompt = f"""
    Analyze these JavaScript calculations and return information about them.
    
    Calculations:
    {calculations_text}
    
    Return ONLY valid JSON with no additional text, in this format:
    [
        {{
            "name": "calculation_name",
            "formula": "the_formula",
            "variables": ["var1", "var2"],
            "type": "sum|product|ratio|other"
        }}
    ]
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        
        # Use safe parsing method
        result = safe_parse_gemini_json(response.text)
        
        if result is None:
            print("⚠️ Could not parse Gemini response as JSON, using empty list")
            return []
        
        return result
        
    except Exception as e:
        print(f"⚠️ Error analyzing calculations with Gemini: {e}")
        return []


# Test the fix
if __name__ == "__main__":
    # Test various response formats
    test_cases = [
        '{"result": "test"}',  # Valid JSON
        '```json\n{"result": "test"}\n```',  # JSON in code block
        'Here is the JSON:\n{"result": "test"}',  # JSON with text before
        '{"result": "test"}\nSome extra text',  # JSON with text after
        '```\n[{"item": 1}, {"item": 2}]\n```',  # Array in code block
        'Invalid JSON here',  # Invalid JSON
        '',  # Empty response
    ]
    
    print("Testing JSON parsing fix:")
    print("="*50)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test[:30]}...")
        result = safe_parse_gemini_json(test)
        print(f"Result: {result}")
    
    print("\n✅ Fix ready to be applied!")
