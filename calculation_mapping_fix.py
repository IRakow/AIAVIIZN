"""
Fix for the calculation mapping error in aiviizn_real_agent_with_ai_intelligence_updated.py
Add this function to your AIVIIZNRealAgent class
"""

def clean_fields_for_json(self, fields: List[Dict]) -> List[Dict]:
    """Clean fields to ensure they're JSON serializable"""
    cleaned_fields = []
    for field in fields:
        # Create a clean copy of the field
        clean_field = {}
        for key, value in field.items():
            # Convert any non-serializable values to strings
            if isinstance(value, dict):
                # Flatten nested dicts to strings for JSON serialization
                clean_field[key] = str(value)
            elif isinstance(value, list):
                # Clean lists recursively
                clean_list = []
                for item in value:
                    if isinstance(item, dict):
                        clean_list.append(str(item))
                    else:
                        clean_list.append(item)
                clean_field[key] = clean_list
            elif hasattr(value, '__dict__'):
                # Convert objects to string representation
                clean_field[key] = str(value)
            else:
                # Keep simple values as-is
                clean_field[key] = value
        cleaned_fields.append(clean_field)
    return cleaned_fields

# Then update your extract_calculations_with_mapping method to use this:

async def extract_calculations_with_mapping(self, page_data: Dict, fields: List[Dict]) -> List[Dict]:
    """Extract calculations and map their variables to fields"""
    try:
        print("  🧮 Extracting calculations with variable mapping...")
        
        # First extract calculations
        calculations = await self.extract_calculations_real(page_data)
        
        # Clean fields to ensure they're JSON serializable
        cleaned_fields = self.clean_fields_for_json(fields)
        
        # Now map variables for each calculation
        enhanced_calculations = []
        for calc in calculations:
            formula = calc.get('formula', '')
            if formula:
                try:
                    # Map variables to cleaned fields
                    variable_mappings = await self.calculation_mapper.map_calculation_variables(
                        formula,
                        cleaned_fields,  # Use cleaned fields instead
                        page_data.get('text_content', '')
                    )
                    
                    calc['variable_mappings'] = variable_mappings
                    calc['formula_type'] = self.calculation_mapper.identify_formula_type(
                        formula,
                        [v['variable_name'] for v in variable_mappings] if variable_mappings else []
                    )
                    
                    if variable_mappings:
                        self.stats['calculations_mapped'] += 1
                        print(f"    ✓ Mapped calculation: {calc.get('name')} with {len(variable_mappings)} variables")
                except Exception as mapping_error:
                    print(f"    ⚠️ Could not map variables: {mapping_error}")
                    calc['variable_mappings'] = []
                    calc['formula_type'] = 'unknown'
            
            enhanced_calculations.append(calc)
        
        return enhanced_calculations
        
    except Exception as e:
        print(f"  ⚠️ Error in calculation mapping: {e}")
        # Return calculations without mappings rather than empty list
        return calculations if 'calculations' in locals() else []
