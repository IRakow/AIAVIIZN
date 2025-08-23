"""
Debug script to find the actual unhashable type error
"""

import traceback

# Add debugging to the calculation mapper
debug_code = '''
    async def extract_calculations_with_mapping(self, page_data: Dict, fields: List[Dict]) -> List[Dict]:
        """Extract calculations and map their variables to fields"""
        try:
            print("  🧮 Extracting calculations with variable mapping...")
            
            # First extract calculations using Claude
            calculations = await self.extract_calculations_real(page_data)
            
            # Now map variables for each calculation
            enhanced_calculations = []
            # Create field list in exact format the mapper expects
            fields_for_mapper = []
            for field in fields:
                # DEBUG: Check what field actually is
                print(f"    DEBUG: field type = {type(field)}")
                if not isinstance(field, dict):
                    print(f"    WARNING: field is not a dict: {field}")
                    continue
                    
                fields_for_mapper.append({
                    'field_name': field.get('field_name', ''),
                    'semantic_type': field.get('semantic_type', 'unknown'),
                    'data_type': field.get('data_type', 'text')
                })
            
            print(f"    DEBUG: Created {len(fields_for_mapper)} fields for mapper")
            
            for i, calc in enumerate(calculations):
                print(f"    DEBUG: Processing calculation {i+1}/{len(calculations)}")
                formula = calc.get('formula', '')
                if formula:
                    try:
                        # Map variables to fields
                        variable_mappings = await self.calculation_mapper.map_calculation_variables(
                            formula,
                            fields_for_mapper,
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
                    except Exception as map_error:
                        print(f"    ERROR mapping calc {i+1}: {map_error}")
                        print(f"    Traceback: {traceback.format_exc()}")
                        calc['variable_mappings'] = []
                        calc['formula_type'] = 'unknown'
                
                enhanced_calculations.append(calc)
            
            return enhanced_calculations
            
        except Exception as e:
            print(f"  ⚠️ Error in calculation mapping: {e}")
            print(f"  Full traceback:\\n{traceback.format_exc()}")
            return []
'''

print("Add this debug version to your agent file to see exactly where the error occurs.")
print("\nThe actual issue might be:")
print("1. The 'fields' parameter might contain non-dict items")
print("2. Something in the calculation_mapper is using a dict as a key")
print("3. The formula_type identification might be the issue")
print("\nReplace the extract_calculations_with_mapping method with the debug version above")
print("to see the exact line where the error happens.")
