"""
Enhanced Field Intelligence Module for AIVIIZN
Intelligently names ALL fields, including undefined ones
Maps calculation variables and formulas
"""

import re
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import anthropic
from openai import AsyncOpenAI
try:
    import google.generativeai as genai
except ImportError:
    genai = None

def safe_json_serialize(obj):
    """Safely serialize objects for JSON, handling nested dicts"""
    if isinstance(obj, dict):
        return {str(k): safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [safe_json_serialize(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return safe_json_serialize(obj.__dict__)
    else:
        try:
            json.dumps(obj)
            return obj
        except TypeError:
            return str(obj)

@dataclass
class FieldIntelligence:
    """Result of intelligent field analysis"""
    original_name: str
    semantic_type: str
    ai_generated_name: str
    description: str
    data_type: str  # number, currency, percentage, date, text, boolean
    unit_of_measure: Optional[str]  # dollars, percent, days, sqft, etc.
    is_calculated: bool
    calculation_formula: Optional[str]
    related_fields: List[str]
    confidence: float
    context_clues: Dict

class EnhancedFieldMapper:
    """
    Advanced field identification using AI
    Names EVERYTHING, even undefined fields
    """
    
    def __init__(self, anthropic_client, openai_client=None):
        self.anthropic_client = anthropic_client
        self.openai_client = openai_client
        
        # Extended patterns including calculations
        self.CALCULATION_PATTERNS = {
            'sum': r'sum|total|grand.*total|subtotal',
            'average': r'avg|average|mean',
            'count': r'count|number.*of|qty|quantity',
            'percentage': r'percent|%|rate',
            'difference': r'diff|difference|variance|delta',
            'ratio': r'ratio|proportion',
            'product': r'product|multiply|times',
            'division': r'divide|per|ratio',
            'min': r'min|minimum|lowest',
            'max': r'max|maximum|highest',
            'net': r'net|after|remaining',
            'gross': r'gross|before|total'
        }
        
        # Data type patterns
        self.DATA_TYPE_PATTERNS = {
            'currency': r'\$|dollar|usd|amount|fee|cost|price|rent|payment|deposit',
            'percentage': r'%|percent|rate',
            'date': r'date|time|when|year|month|day',
            'count': r'count|number|qty|quantity|total',
            'measurement': r'sq.*ft|square|feet|meters|miles|acres',
            'boolean': r'yes|no|true|false|active|inactive|enabled|disabled',
            'identifier': r'id|number|code|key',
            'duration': r'days|months|years|hours|minutes|period|term'
        }
    
    async def analyze_field_intelligently(self, 
                                         field_name: str, 
                                         field_attributes: Dict,
                                         page_context: str,
                                         surrounding_fields: List[str]) -> FieldIntelligence:
        """
        Use AI to intelligently analyze and name any field
        Even if it doesn't match any pattern
        """
        
        # First check if it's a calculation
        is_calculated = self._is_likely_calculation(field_name, field_attributes)
        
        # Prepare context for AI
        context = {
            'field_name': field_name,
            'attributes': field_attributes,
            'page_context': page_context[:1000],  # First 1000 chars
            'surrounding_fields': surrounding_fields,
            'html_type': field_attributes.get('type', 'unknown')
        }
        
        # Use Claude for intelligent analysis
        prompt = f"""
        Analyze this form field from a property management system and provide intelligent naming and classification.
        
        Field Information:
        - Original name: {field_name}
        - HTML type: {field_attributes.get('type', 'unknown')}
        - Placeholder: {field_attributes.get('placeholder', '')}
        - Pattern: {field_attributes.get('pattern', '')}
        - Surrounding fields: {', '.join(surrounding_fields[:5])}
        
        Page context: {page_context[:500]}
        
        Please determine:
        1. What this field represents semantically (be specific)
        2. A clear, descriptive name for this field
        3. The data type (currency, percentage, date, number, text, etc.)
        4. Unit of measure if applicable (dollars, days, sqft, etc.)
        5. Whether this is likely a calculated field
        6. If calculated, what might be the formula
        7. What other fields it might be related to
        
        IMPORTANT: Even if the field name is cryptic like "field_123" or "x1", 
        use context clues to determine what it likely represents.
        
        Return as JSON with these fields:
        {{
            "semantic_type": "specific_type_name",
            "generated_name": "clear_descriptive_name",
            "description": "what this field represents",
            "data_type": "currency|percentage|date|number|text|boolean",
            "unit_of_measure": "dollars|percent|days|etc or null",
            "is_calculated": true/false,
            "calculation_formula": "likely formula or null",
            "related_fields": ["field1", "field2"],
            "confidence": 0.0-1.0,
            "reasoning": "explanation of analysis"
        }}
        """
        
        try:
            # Check if using Gemini
            if genai and hasattr(self.anthropic_client, 'generate_content'):
                # Using Gemini Ultra
                response = self.anthropic_client.generate_content(prompt)
                content = response.text
            else:
                # Using Claude
                response = self.anthropic_client.messages.create(
                    model="claude-opus-4-1-20250805",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            
            # Extract JSON
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                return FieldIntelligence(
                    original_name=field_name,
                    semantic_type=result.get('semantic_type', 'unknown'),
                    ai_generated_name=result.get('generated_name', field_name),
                    description=result.get('description', ''),
                    data_type=result.get('data_type', 'text'),
                    unit_of_measure=result.get('unit_of_measure'),
                    is_calculated=result.get('is_calculated', False),
                    calculation_formula=result.get('calculation_formula'),
                    related_fields=result.get('related_fields', []),
                    confidence=result.get('confidence', 0.5),
                    context_clues={'reasoning': result.get('reasoning', '')}
                )
        except Exception as e:
            print(f"AI analysis error: {e}")
        
        # Fallback to pattern-based detection
        return self._fallback_analysis(field_name, field_attributes)
    
    def _is_likely_calculation(self, field_name: str, attributes: Dict) -> bool:
        """Check if field is likely a calculated value"""
        field_lower = field_name.lower()
        
        # Check calculation patterns
        for calc_type, pattern in self.CALCULATION_PATTERNS.items():
            if re.search(pattern, field_lower):
                return True
        
        # Check if readonly or disabled (often calculated fields)
        if attributes.get('readonly') or attributes.get('disabled'):
            return True
        
        # Check for formula indicators
        formula_indicators = ['total', 'sum', 'avg', 'calc', 'computed', 'derived']
        return any(indicator in field_lower for indicator in formula_indicators)
    
    def _fallback_analysis(self, field_name: str, attributes: Dict) -> FieldIntelligence:
        """Fallback analysis using patterns"""
        field_lower = field_name.lower()
        
        # Detect data type
        data_type = 'text'
        unit_of_measure = None
        
        for dtype, pattern in self.DATA_TYPE_PATTERNS.items():
            if re.search(pattern, field_lower):
                data_type = dtype
                
                # Set unit of measure
                if dtype == 'currency':
                    unit_of_measure = 'dollars'
                elif dtype == 'percentage':
                    unit_of_measure = 'percent'
                elif dtype == 'measurement' and 'sq' in field_lower:
                    unit_of_measure = 'sqft'
                break
        
        # Generate a semantic name
        semantic_type = self._generate_semantic_type(field_name)
        
        return FieldIntelligence(
            original_name=field_name,
            semantic_type=semantic_type,
            ai_generated_name=self._generate_friendly_name(field_name),
            description=f"Field: {field_name}",
            data_type=data_type,
            unit_of_measure=unit_of_measure,
            is_calculated=self._is_likely_calculation(field_name, attributes),
            calculation_formula=None,
            related_fields=[],
            confidence=0.3,
            context_clues={}
        )
    
    def _generate_semantic_type(self, field_name: str) -> str:
        """Generate semantic type from field name"""
        # Remove common prefixes/suffixes
        cleaned = re.sub(r'^(txt|lbl|btn|chk|rad|sel|inp)_', '', field_name.lower())
        cleaned = re.sub(r'_(id|num|no|code)$', '', cleaned)
        
        # Convert to semantic format
        cleaned = cleaned.replace('_', ' ').replace('-', ' ')
        words = cleaned.split()
        
        # Join with underscores for semantic type
        return '_'.join(words) if words else 'unknown_field'
    
    def _generate_friendly_name(self, field_name: str) -> str:
        """Generate user-friendly name from field name"""
        # Remove technical prefixes
        cleaned = re.sub(r'^(txt|lbl|btn|chk|rad|sel|inp)_', '', field_name)
        
        # Convert underscores and hyphens to spaces
        cleaned = cleaned.replace('_', ' ').replace('-', ' ')
        
        # Capitalize appropriately
        return ' '.join(word.capitalize() for word in cleaned.split())

class CalculationVariableMapper:
    """
    Maps calculation variables to their source fields
    Understands formulas and their components
    """
    
    def __init__(self, anthropic_client):
        self.anthropic_client = anthropic_client
        
        # Common calculation patterns in property management
        self.FORMULA_PATTERNS = {
            'rent_total': 'base_rent + utilities + fees',
            'net_income': 'gross_income - expenses',
            'occupancy_rate': '(occupied_units / total_units) * 100',
            'late_fee': 'rent * late_fee_percentage',
            'security_deposit': 'monthly_rent * deposit_months',
            'proration': '(daily_rate * days_occupied)',
            'cap_rate': '(net_operating_income / property_value) * 100',
            'debt_service_ratio': 'net_operating_income / debt_service',
            'expense_ratio': 'operating_expenses / gross_income'
        }
    
    async def map_calculation_variables(self, 
                                       calculation_text: str,
                                       page_fields: List[Dict],
                                       page_content: str) -> List[Dict]:
        """
        Map variables in a calculation to their source fields
        Returns list of variable mappings
        """
        
        print("  ✨ Using Gemini to analyze JavaScript calculations")
        
        # Prepare field lookup - ensure field_name is a string
        field_lookup = {}
        for f in page_fields:
            # Ensure f is a dict and has field_name
            if isinstance(f, dict):
                field_name = f.get('field_name')
                # Convert to string if it's not already
                if field_name:
                    field_name_str = str(field_name) if not isinstance(field_name, str) else field_name
                    field_lookup[field_name_str] = f
            elif isinstance(f, str):
                # If f is already a string, use it as both key and value
                field_lookup[f] = {'field_name': f}
        
        # Create the field list for the prompt - FIX: single curly braces
        fields_for_prompt = [{
            'name': str(f.get('field_name', '')),
            'type': str(f.get('semantic_type', 'unknown')),
            'data_type': str(f.get('data_type', 'text'))
        } for f in page_fields[:20] if isinstance(f, dict) and f.get('field_name')]
        
        # Updated prompt to request cleaner JSON
        prompt = f"""
        Analyze this calculation/formula and map its variables to the available fields.
        
        Calculation: {calculation_text}
        
        Available fields on the page:
        {json.dumps(fields_for_prompt, indent=2)}
        
        For each variable in the calculation:
        1. Identify what it represents
        2. Match it to a field from the available fields if possible
        3. Determine its data type and unit of measure
        4. Explain its role in the calculation
        
        IMPORTANT: Return ONLY a valid JSON array. No markdown, no code blocks, no explanations.
        Start your response with [ and end with ]
        
        Format:
        [
            {{
                "variable_name": "var1",
                "semantic_meaning": "what this represents",
                "matched_field": "field_name or null",
                "data_type": "currency|number|percentage|etc",
                "unit_of_measure": "dollars|percent|days|etc",
                "role_in_calculation": "explanation",
                "example_value": "sample value"
            }}
        ]
        """
        
        try:
            # Check if using Gemini
            if genai and hasattr(self.anthropic_client, 'generate_content'):
                # Using Gemini Ultra
                try:
                    response = self.anthropic_client.generate_content(prompt)
                    content = response.text
                except Exception as gemini_error:
                    print(f"  ⚠️ Gemini error: {gemini_error}")
                    # Return empty list on Gemini error
                    return []
            else:
                # Using Claude
                response = self.anthropic_client.messages.create(
                    model="claude-opus-4-1-20250805",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            
            # Debug: Show what we got
            print(f"    📝 Raw AI response length: {len(content)} chars")
            
            # Clean up the response - handle empty or invalid responses
            if not content or len(content.strip()) == 0:
                print(f"    ⚠️ Empty response from AI")
                return []
            
            original_content = content
            
            # Step 1: Remove markdown code blocks if present
            if '```json' in content:
                # Extract content between ```json and ```
                parts = content.split('```json')
                if len(parts) > 1:
                    content = parts[1].split('```')[0]
                    print(f"    ✓ Extracted from json code block")
            elif '```' in content:
                # Extract content between ``` and ```
                parts = content.split('```')
                if len(parts) >= 3:  # Content is in parts[1]
                    content = parts[1]
                    print(f"    ✓ Extracted from code block")
            
            # Step 2: Clean up whitespace and common issues
            content = content.strip()
            
            # Step 2.5: Try to extract JSON if there's text before it
            # Sometimes Gemini adds explanation before the JSON
            if '[' in content:
                # Find the first [ and try from there
                json_start = content.find('[')
                if json_start > 0:
                    print(f"    🔍 Found JSON starting at position {json_start}")
                    content = content[json_start:]
            
            # Step 3: Try to find valid JSON array
            variables = None
            
            # Method 1: Try to parse as-is
            try:
                test_parse = json.loads(content)
                if isinstance(test_parse, list):
                    variables = test_parse
                    print(f"    ✓ Parsed JSON directly: {len(variables)} variables")
            except json.JSONDecodeError as e:
                print(f"    ⚠️ Error extracting calculations: {e}")
                # Show a preview of what we got to help debug
                if len(content) > 100:
                    print(f"    📄 Response preview: {content[:100]}...")
                else:
                    print(f"    📄 Full response: {content}")
            
            # Method 2: Find array boundaries more carefully
            if variables is None:
                # Look for the first [ and find the matching ]
                start_idx = content.find('[')
                if start_idx != -1:
                    # Count brackets to find the matching closing bracket
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
                            variables = json.loads(json_str)
                            print(f"    ✓ Extracted array by bracket matching: {len(variables)} variables")
                        except json.JSONDecodeError as e:
                            print(f"    ⚠️ Bracket matching parse failed: {e}")
            
            # Method 3: Try regex with more specific pattern
            if variables is None:
                # Look for array containing objects with variable_name field
                import re
                # This pattern is more specific to avoid greedy matching
                pattern = r'\[\s*\{[^}]*"variable_name"[^}]*\}(?:\s*,\s*\{[^}]*"variable_name"[^}]*\})*\s*\]'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    try:
                        variables = json.loads(match.group())
                        print(f"    ✓ Extracted with regex pattern: {len(variables)} variables")
                    except json.JSONDecodeError as e:
                        print(f"    ⚠️ Regex pattern parse failed: {e}")
            
            # Method 4: Last resort - try to fix common JSON issues
            if variables is None:
                # Try to fix common issues
                fixed_content = content
                
                # Replace single quotes with double quotes (common issue)
                fixed_content = re.sub(r"'([^']*)'", r'"\1"', fixed_content)
                
                # Remove trailing commas before ] or }
                fixed_content = re.sub(r',\s*\]', ']', fixed_content)
                fixed_content = re.sub(r',\s*\}', '}', fixed_content)
                
                # Try to parse the fixed content
                try:
                    test_parse = json.loads(fixed_content)
                    if isinstance(test_parse, list):
                        variables = test_parse
                        print(f"    ✓ Parsed after fixing JSON issues: {len(variables)} variables")
                except:
                    pass
            
            # If all methods failed, return empty list
            if variables is None:
                print(f"    ❌ All JSON extraction methods failed")
                if content and len(content) > 0:
                    preview_len = min(200, len(content))
                    print(f"    📄 Response preview: {content[:preview_len]}...")
                variables = []
            
            # Validate and clean the variables
            cleaned_variables = []
            if not isinstance(variables, list):
                print(f"    ⚠️ Variables is not a list, got {type(variables)}")
                variables = []
            
            for var in variables:
                if isinstance(var, dict) and 'variable_name' in var:
                    # Ensure all fields are strings
                    cleaned_var = {
                        'variable_name': str(var.get('variable_name', '')),
                        'semantic_meaning': str(var.get('semantic_meaning', '')),
                        'matched_field': str(var.get('matched_field', '')) if var.get('matched_field') else None,
                        'data_type': str(var.get('data_type', 'text')),
                        'unit_of_measure': str(var.get('unit_of_measure', '')) if var.get('unit_of_measure') else None,
                        'role_in_calculation': str(var.get('role_in_calculation', '')),
                        'example_value': str(var.get('example_value', '')) if var.get('example_value') else None
                    }
                    
                    # Add field mapping ID if we have a match
                    if cleaned_var['matched_field'] and cleaned_var['matched_field'] in field_lookup:
                        cleaned_var['field_mapping_id'] = field_lookup[cleaned_var['matched_field']].get('id')
                    
                    cleaned_variables.append(cleaned_var)
            
            print(f"    ✅ Returning {len(cleaned_variables)} mapped variables")
            return cleaned_variables
            
        except Exception as e:
            print(f"    ❌ Variable mapping error: {e}")
            import traceback
            print(f"    📋 Traceback: {traceback.format_exc()}")
            
        return []
    
    def extract_variables_from_formula(self, formula: str) -> List[str]:
        """
        Extract variable names from a formula string
        """
        # Remove operators and numbers
        formula_clean = re.sub(r'[+\-*/()=<>!&|]', ' ', formula)
        formula_clean = re.sub(r'\b\d+\.?\d*\b', '', formula_clean)
        
        # Extract potential variable names
        variables = []
        for word in formula_clean.split():
            word = word.strip()
            if word and not word.isdigit() and len(word) > 1:
                variables.append(word)
        
        return list(set(variables))
    
    def identify_formula_type(self, formula: str, variables: List[str]) -> str:
        """
        Identify what type of calculation this is
        """
        formula_lower = formula.lower()
        
        # Check against known patterns
        for formula_type, pattern in self.FORMULA_PATTERNS.items():
            pattern_lower = pattern.lower()
            # Simple matching - could be enhanced
            if any(op in formula_lower for op in ['+', '-', '*', '/']):
                # Check if variable names suggest the formula type
                if formula_type in formula_lower or \
                   any(formula_type.replace('_', ' ') in var.lower() for var in variables):
                    return formula_type
        
        # Analyze operators to guess type
        if '*' in formula and '%' in formula:
            return 'percentage_calculation'
        elif '/' in formula and len(variables) == 2:
            return 'ratio_calculation'
        elif '+' in formula and '-' not in formula:
            return 'sum_calculation'
        elif '-' in formula and '+' not in formula:
            return 'difference_calculation'
        
        return 'custom_calculation'

# Export the enhanced modules
__all__ = ['EnhancedFieldMapper', 'CalculationVariableMapper', 'FieldIntelligence']
