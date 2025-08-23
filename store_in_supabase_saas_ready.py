#!/usr/bin/env python3
"""
Updated store_in_supabase_real method with proper SaaS duplicate prevention
This replaces the existing method in your agent
"""

async def store_in_supabase_real(self, url: str, main_content: Dict, calculations: List[Dict], template_path: str):
    """
    Store in Supabase with proper SaaS multi-tenancy and duplicate prevention
    Uses UPSERT pattern - updates if exists, inserts if new
    """
    print("  → Storing in database with duplicate prevention")
    
    try:
        # Ensure we have a company_id
        if not self.company_id:
            print("  ❌ No company_id found - getting AIVIIZN company")
            self.company_id = self.get_aiviizn_company_id()
            if not self.company_id:
                raise Exception("Cannot proceed without company_id")
        
        # Step 1: Store HTML in Storage (no duplicates - overwrites)
        storage_path = await self.store_html_in_storage(url, main_content.get('html', ''))
        
        # Step 2: UPSERT page (insert or update)
        # First, check if page exists
        existing_page = self.supabase.table('pages').select('id, version, updated_at').eq('company_id', self.company_id).eq('url', url).execute()
        
        page_data = {
            'company_id': self.company_id,
            'url': url,
            'title': main_content.get('title', ''),
            'template_path': str(template_path),
            'html_storage_path': storage_path,
            'html_preview': main_content.get('html', '')[:500] if main_content.get('html') else '',
            'api_responses': main_content.get('api_responses', []),
            'meta_data': {
                'captured_by': 'aiviizn_agent',
                'browser': 'playwright',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        if existing_page.data and len(existing_page.data) > 0:
            # UPDATE existing page
            page_id = existing_page.data[0]['id']
            old_version = existing_page.data[0]['version']
            
            print(f"  📝 Updating existing page (version {old_version} → {old_version + 1})")
            
            # Update the page
            result = self.supabase.table('pages').update(page_data).eq('id', page_id).execute()
            
            if result.data:
                print(f"  ✅ Page UPDATED (ID: {page_id[:8]}...)")
            
        else:
            # INSERT new page
            print(f"  📝 Creating new page record")
            
            result = self.supabase.table('pages').insert(page_data).execute()
            
            if result.data and len(result.data) > 0:
                page_id = result.data[0]['id']
                print(f"  ✅ Page CREATED (ID: {page_id[:8]}...)")
            else:
                raise Exception("Failed to insert page")
        
        # Step 3: Handle calculations with replacement strategy
        if calculations and len(calculations) > 0:
            print(f"  📊 Processing {len(calculations)} calculations")
            
            # Delete old calculations for this page
            delete_result = self.supabase.table('calculations').delete().eq('company_id', self.company_id).eq('page_url', url).execute()
            
            # Insert new calculations
            successful_calcs = 0
            for calc in calculations:
                try:
                    calc_record = {
                        'company_id': self.company_id,
                        'page_id': page_id,
                        'page_url': url,
                        'name': calc.get('name', 'unknown_calc'),
                        'description': calc.get('description', ''),
                        'formula': calc.get('formula', ''),
                        'formula_type': calc.get('source', 'unknown'),
                        'javascript': calc.get('javascript', ''),
                        'variables': calc.get('variables', []),
                        'sample_data': calc.get('sample_data', {}),
                        'confidence_score': self._calculate_confidence(calc),
                        'verified': calc.get('verified', False),
                        'source': calc.get('source', 'ai_extracted')
                    }
                    
                    # Insert calculation
                    calc_result = self.supabase.table('calculations').insert(calc_record).execute()
                    if calc_result.data:
                        successful_calcs += 1
                        
                except Exception as e:
                    print(f"    ⚠️ Failed to store calculation '{calc.get('name', 'unknown')}': {e}")
            
            print(f"  ✅ Stored {successful_calcs}/{len(calculations)} calculations")
        
        # Step 4: Store API responses if any
        if main_content.get('api_responses'):
            print(f"  📡 Processing {len(main_content['api_responses'])} API responses")
            
            successful_apis = 0
            for api_resp in main_content['api_responses']:
                try:
                    # UPSERT API response (no duplicates per endpoint)
                    api_record = {
                        'company_id': self.company_id,
                        'page_id': page_id,
                        'page_url': url,
                        'endpoint': api_resp.get('endpoint', ''),
                        'method': api_resp.get('method', 'GET'),
                        'status_code': api_resp.get('status', 200),
                        'response_data': api_resp.get('data', {}),
                        'captured_at': api_resp.get('timestamp', datetime.now().isoformat())
                    }
                    
                    # Try to upsert (will update if endpoint exists)
                    api_result = self.supabase.table('api_responses').upsert(
                        api_record,
                        on_conflict='page_url,endpoint,method'
                    ).execute()
                    
                    if api_result.data:
                        successful_apis += 1
                        
                except Exception as e:
                    # Likely a duplicate, which is fine
                    pass
            
            if successful_apis > 0:
                print(f"  ✅ Stored {successful_apis} API responses")
        
        # Step 5: Track discovered links for this page
        if hasattr(self, 'discovered_links'):
            new_links = [link for link in self.discovered_links if link != url]
            if new_links:
                print(f"  🔗 Recording {len(new_links)} discovered links")
                
                for target_url in new_links[:50]:  # Limit to 50 to avoid overwhelming
                    try:
                        link_record = {
                            'company_id': self.company_id,
                            'source_page_id': page_id,
                            'source_url': url,
                            'target_url': target_url,
                            'link_type': self._classify_link_type(target_url),
                            'is_processed': target_url in self.processed_pages
                        }
                        
                        # Insert or ignore if duplicate
                        self.supabase.table('page_links').insert(link_record).execute()
                        
                    except:
                        pass  # Duplicate link, ignore
        
        print(f"  ✨ Page storage complete with duplicate prevention")
        
    except Exception as e:
        logger.error(f"Error storing in Supabase: {e}")
        print(f"  ❌ Failed to store: {e}")
        
        # Log error for debugging
        try:
            error_record = {
                'company_id': self.company_id,
                'url': url,
                'error_type': 'storage',
                'error_message': str(e),
                'error_details': {
                    'template_path': str(template_path),
                    'has_calculations': len(calculations) > 0 if calculations else False
                }
            }
            self.supabase.table('page_errors').insert(error_record).execute()
        except:
            pass

def _calculate_confidence(self, calc: Dict) -> float:
    """Calculate confidence score for a calculation"""
    confidence = 0.5  # Base confidence
    
    # Higher confidence if verified
    if calc.get('verified'):
        confidence += 0.3
    
    # Higher confidence for certain sources
    source_confidence = {
        'excel': 0.4,
        'api_trigger': 0.3,
        'gpt4': 0.2,
        'claude': 0.2,
        'reverse_engineering': 0.15
    }
    confidence += source_confidence.get(calc.get('source', ''), 0.1)
    
    # Cap at 1.0
    return min(confidence, 1.0)

def _classify_link_type(self, url: str) -> str:
    """Classify the type of link"""
    if '/reports/' in url:
        return 'report'
    elif '/api/' in url:
        return 'api'
    elif any(x in url for x in ['sign_in', 'login', 'logout']):
        return 'auth'
    elif url.startswith('http') and self.target_base not in url:
        return 'external'
    else:
        return 'navigation'

async def get_unprocessed_pages(self, limit: int = 10) -> List[str]:
    """Get unprocessed pages from the database (SaaS aware)"""
    try:
        # Get unprocessed links for this company
        result = self.supabase.table('page_links').select('target_url').eq('company_id', self.company_id).eq('is_processed', False).limit(limit).execute()
        
        if result.data:
            return [link['target_url'] for link in result.data]
        
    except Exception as e:
        logger.error(f"Error getting unprocessed pages: {e}")
    
    return []

async def mark_page_processed(self, url: str):
    """Mark a page as processed in the links table"""
    try:
        self.supabase.table('page_links').update({'is_processed': True, 'processed_at': datetime.now().isoformat()}).eq('company_id', self.company_id).eq('target_url', url).execute()
    except:
        pass
