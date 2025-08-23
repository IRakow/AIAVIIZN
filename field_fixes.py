#!/usr/bin/env python3
"""
Fixes for field analysis errors:
1. FieldIntelligence missing arguments
2. NoneType.lower() error
"""

# Find and replace these in aiviizn_real_agent_with_ai_intelligence_updated.py

# FIX 1: Around line 738 - Add missing arguments to FieldIntelligence
OLD_CODE_1 = """                    # Convert to FieldIntelligence object for compatibility
                    from enhanced_field_intelligence import FieldIntelligence
                    field_intelligence = FieldIntelligence(
                        ai_generated_name=consensus_result.get('ai_generated_name', field_name),
                        semantic_type=consensus_result.get('semantic_type', 'unknown'),
                        data_type=consensus_result.get('data_type', 'text'),
                        unit_of_measure=consensus_result.get('unit_of_measure'),
                        is_calculated=consensus_result.get('is_calculated', False),
                        calculation_formula=consensus_result.get('calculation_formula'),
                        related_fields=consensus_result.get('related_fields', []),
                        confidence=consensus_result.get('confidence', 0.5),
                        context_clues=consensus_result.get('context_clues', {})
                    )"""

NEW_CODE_1 = """                    # Convert to FieldIntelligence object for compatibility
                    from enhanced_field_intelligence import FieldIntelligence
                    field_intelligence = FieldIntelligence(
                        original_name=field_name,  # Added missing required argument
                        ai_generated_name=consensus_result.get('ai_generated_name', field_name),
                        semantic_type=consensus_result.get('semantic_type', 'unknown'),
                        data_type=consensus_result.get('data_type', 'text'),
                        unit_of_measure=consensus_result.get('unit_of_measure'),
                        is_calculated=consensus_result.get('is_calculated', False),
                        calculation_formula=consensus_result.get('calculation_formula'),
                        related_fields=consensus_result.get('related_fields', []),
                        confidence=consensus_result.get('confidence', 0.5),
                        context_clues=consensus_result.get('context_clues', {}),
                        description=consensus_result.get('description', '')  # Added missing required argument
                    )"""

# FIX 2: Around line 149 - Fix NoneType.lower() error
OLD_CODE_2 = """        # Check placeholders and labels
        placeholder = field_attributes.get('placeholder', '').lower()
        if placeholder:"""

NEW_CODE_2 = """        # Check placeholders and labels - handle None case
        placeholder = field_attributes.get('placeholder') or ''
        placeholder = placeholder.lower() if placeholder else ''
        if placeholder:"""

def apply_fixes():
    """Apply both fixes to the main file"""
    import os
    file_path = '/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Apply Fix 1
    if OLD_CODE_1 in content:
        content = content.replace(OLD_CODE_1, NEW_CODE_1)
        print("✓ Applied Fix 1: Added missing FieldIntelligence arguments")
    else:
        print("⚠️ Fix 1 pattern not found - may already be applied or code changed")
    
    # Apply Fix 2
    if OLD_CODE_2 in content:
        content = content.replace(OLD_CODE_2, NEW_CODE_2)
        print("✓ Applied Fix 2: Fixed NoneType.lower() error")
    else:
        print("⚠️ Fix 2 pattern not found - may already be applied or code changed")
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("\n✅ Fixes applied to aiviizn_real_agent_with_ai_intelligence_updated.py")

if __name__ == "__main__":
    apply_fixes()
