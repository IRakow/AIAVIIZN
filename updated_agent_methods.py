#!/usr/bin/env python3
"""
Updated get_aiviizn_company_id method with the correct ID
Replace this method in your aiviizn_real_agent_fixed.py
"""

def get_aiviizn_company_id(self):
    """Get the AIVIIZN company ID - now hardcoded after database setup"""
    # Database has been set up with AIVIIZN company
    # Using the actual ID from the database
    return '5bb7db68-63e2-4750-ac16-ad15f19938a8'
    
    # Backup method if you want to still check dynamically:
    """
    try:
        result = self.supabase.table('companies').select('id').eq('name', 'AIVIIZN').execute()
        if result.data:
            return result.data[0]['id']
        else:
            # This shouldn't happen now that database is set up
            print("❌ AIVIIZN company not found in database!")
            return None
    except Exception as e:
        print(f"⚠️ Could not get company ID: {e}")
        # Return the known ID as fallback
        return '5bb7db68-63e2-4750-ac16-ad15f19938a8'
    """

async def store_in_supabase_real(self, url: str, main_content: Dict, calculations: List[Dict], template_path: str):
    """
    Store in Supabase with DUPLICATE PREVENTION
    This version uses the proper SaaS database structure
    """
    print("  → Storing in database with duplicate prevention")
    
    # Use the hardcoded AIVIIZN company ID
    company_id = '5bb7db68-63e2-4750-ac16-ad15f19938a8'
    
    try:
        # Step 1: Check if page already exists
        existing = self.supabase.table('pages').select('id, version').eq('company_id', company_id).eq('url', url).execute()
        
        # Step 2: Store HTML in Storage
        storage_path = await self.store_html_in_storage(url, main_content.get('html', ''))
        
        # Step 3: Prepare page data
        page_data = {
            'company_id': company_id,
            'url': url,
            'title': main_content.get('title', ''),
            'template_path': str(template_path),
            'html_storage_path': storage_path,
            'html_preview': main_content.get('html', '')[:500] if main_content.get('html') else '',
            'api_responses': main_content.get('api_responses', []),
            'meta_data': {
                'captured_by': 'aiviizn_agent',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        if existing.data and len(existing.data) > 0:
            # UPDATE existing page
            page_id = existing.data[0]['id']
            old_version = existing.data[0]['version']
            
            print(f"  📝 Updating existing page (v{old_version} → v{old_version + 1})")
            
            # Remove fields that shouldn't be updated
            update_data = {k: v for k, v in page_data.items() if k != 'company_id'}
            
            result = self.supabase.table('pages').update(update_data).eq('id', page_id).execute()
            print(f"  ✅ Page UPDATED (no duplicate created)")
            
        else:
            # INSERT new page
            print(f"  📝 Creating new page record")
            result = self.supabase.table('pages').insert(page_data).execute()
            
            if result.data:
                page_id = result.data[0]['id']
                print(f"  ✅ Page CREATED (ID: {page_id[:8]}...)")
        
        # Step 4: Handle calculations (delete old, insert new)
        if calculations:
            # Delete old calculations
            self.supabase.table('calculations').delete().eq('company_id', company_id).eq('page_url', url).execute()
            
            # Insert new calculations
            for calc in calculations:
                calc_record = {
                    'company_id': company_id,
                    'page_id': page_id if 'page_id' in locals() else None,
                    'page_url': url,
                    'name': calc.get('name', 'unknown'),
                    'description': calc.get('description', ''),
                    'formula': calc.get('formula', ''),
                    'formula_type': calc.get('source', 'ai'),
                    'javascript': calc.get('javascript', ''),
                    'variables': calc.get('variables', []),
                    'verified': calc.get('verified', False),
                    'source': calc.get('source', 'ai_extracted')
                }
                
                self.supabase.table('calculations').insert(calc_record).execute()
            
            print(f"  ✅ Stored {len(calculations)} calculations")
        
        print(f"  ✨ Storage complete with duplicate prevention!")
        
    except Exception as e:
        logger.error(f"Error storing in Supabase: {e}")
        print(f"  ❌ Storage error: {e}")
        
        # Log error
        try:
            error_record = {
                'company_id': company_id,
                'url': url,
                'error_type': 'storage',
                'error_message': str(e),
                'error_details': {'template_path': str(template_path)}
            }
            self.supabase.table('page_errors').insert(error_record).execute()
        except:
            pass
