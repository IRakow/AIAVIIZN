async def store_in_supabase_real(self, url: str, main_content: Dict, calculations: List[Dict], template_path: str):
    """Store in Supabase with DUPLICATE PREVENTION and HTML in Storage"""
    print("  → Storing in database")
    
    try:
        # STEP 1: Check if page already exists for this company
        existing = self.supabase.table('pages').select('id, url, updated_at').eq('company_id', self.company_id).eq('url', url).execute()
        
        if existing.data and len(existing.data) > 0:
            print(f"  ⚠️ Page already exists (ID: {existing.data[0]['id']})")
            print(f"     Last updated: {existing.data[0]['updated_at']}")
            
            # Ask user what to do
            if not self.auto_mode:
                choice = input("     Update existing page? (y/n/skip): ").strip().lower()
                if choice == 'skip' or choice == 'n':
                    print("     → Skipping duplicate")
                    return
            
            # UPDATE existing record instead of INSERT
            page_id = existing.data[0]['id']
            
            # Store new HTML in Storage
            storage_path = await self.store_html_in_storage(url, main_content.get('html', ''))
            
            # Update the existing record
            update_record = {
                'title': main_content.get('title', ''),
                'template_path': str(template_path),
                'html_storage_path': storage_path,
                'html_preview': main_content.get('html', '')[:500],
                'calculations': calculations,
                'api_responses': main_content.get('api_responses', []),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('pages').update(update_record).eq('id', page_id).execute()
            print(f"  ✓ Page UPDATED (prevented duplicate)")
            
        else:
            # NEW PAGE - Insert as normal
            print(f"  → New page, inserting...")
            
            # Store HTML in Storage
            storage_path = await self.store_html_in_storage(url, main_content.get('html', ''))
            
            # Create new record
            page_record = {
                'company_id': self.company_id,
                'url': url,
                'title': main_content.get('title', ''),
                'template_path': str(template_path),
                'html_storage_path': storage_path,
                'html_preview': main_content.get('html', '')[:500],
                'calculations': calculations,
                'api_responses': main_content.get('api_responses', []),
                'captured_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('pages').insert(page_record).execute()
            print(f"  ✓ New page INSERTED")
        
        # Handle calculations with duplicate prevention
        if calculations:
            # Delete old calculations for this page
            self.supabase.table('calculations').delete().eq('company_id', self.company_id).eq('page_url', url).execute()
            
            # Insert fresh calculations
            for calc in calculations:
                calc_record = {
                    'company_id': self.company_id,
                    'page_url': url,
                    'name': calc.get('name', 'unknown'),
                    'description': calc.get('description', ''),
                    'formula': calc.get('formula', ''),
                    'javascript': calc.get('javascript', ''),
                    'variables': calc.get('variables', []),
                    'verified': calc.get('verified', False),
                    'created_at': datetime.now().isoformat()
                }
                self.supabase.table('calculations').insert(calc_record).execute()
            print(f"  ✓ {len(calculations)} calculations stored (replaced old ones)")
            
    except Exception as e:
        logger.error(f"Error storing in Supabase: {e}")
        print(f"  ❌ Failed to store in database: {e}")
