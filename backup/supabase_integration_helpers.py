"""
SUPABASE INTEGRATION HELPER FUNCTIONS FOR MULTI-AI AGENT
Add these methods to your MultiAIInterlinkedAppFolioBuilder class
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

class SupabaseIntegration:
    """Helper methods for Supabase database integration"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def log_validation_result(self, 
                                  page_id: int,
                                  formula_id: int, 
                                  validation_results: Dict) -> str:
        """Log multi-AI validation result to database"""
        
        # Extract AI results
        openai_result = validation_results.get('openai_result')
        gemini_result = validation_results.get('gemini_result') 
        claude_result = validation_results.get('claude_result')
        wolfram_result = validation_results.get('wolfram_result')
        consensus_analysis = validation_results.get('consensus_analysis', {})
        
        validation_data = {
            'page_id': page_id,
            'formula_id': formula_id,
            'openai_result': openai_result,
            'gemini_result': gemini_result,
            'claude_result': claude_result,
            'wolfram_result': wolfram_result,
            'consensus_achieved': consensus_analysis.get('consensus_achieved', False),
            'consensus_score': consensus_analysis.get('consensus_score', 0),
            'successful_validations': consensus_analysis.get('successful_validations', 0),
            'total_attempts': consensus_analysis.get('total_attempts', 0),
            'validation_priority': validation_results.get('validation_priority', 'MEDIUM'),
            'final_recommendation': consensus_analysis.get('recommendation', ''),
            'requires_manual_review': consensus_analysis.get('requires_manual_review', False)
        }
        
        result = self.supabase.table('multi_ai_validations').insert(validation_data).execute()
        return result.data[0]['id'] if result.data else None
    
    async def log_api_call(self, 
                          validation_id: str,
                          ai_provider: str,
                          success: bool,
                          response_time_ms: int = None,
                          error_message: str = None) -> None:
        """Log AI API call for monitoring"""
        
        api_data = {
            'validation_id': validation_id,
            'ai_provider': ai_provider,
            'success': success,
            'response_time_ms': response_time_ms,
            'error_message': error_message,
            'request_timestamp': datetime.now().isoformat()
        }
        
        self.supabase.table('ai_api_monitoring').insert(api_data).execute()
    
    async def get_next_validation_queue(self, limit: int = 10) -> List[Dict]:
        """Get next high priority formulas to validate"""
        
        query = """
        SELECT 
            cf.id as formula_id,
            ap.id as page_id,
            ap.url as page_url,
            ap.title as page_title,
            cf.formula_type,
            cf.formula_expression,
            CASE 
                WHEN ap.page_type IN ('rent_roll_report', 'income_statement', 'delinquency_report') THEN 'HIGH'
                WHEN ap.page_type IN ('account_totals', 'property_dashboard') THEN 'MEDIUM'
                ELSE 'LOW'
            END as priority
        FROM calculation_formulas cf
        JOIN appfolio_pages ap ON cf.page_id = ap.id
        LEFT JOIN multi_ai_validations mav ON cf.id = mav.formula_id
        WHERE cf.verification_status = 'pending'
            AND mav.id IS NULL
        ORDER BY 
            CASE 
                WHEN ap.page_type IN ('rent_roll_report', 'income_statement', 'delinquency_report') THEN 1
                WHEN ap.page_type IN ('account_totals', 'property_dashboard') THEN 2
                ELSE 3
            END
        LIMIT %s
        """
        
        result = self.supabase.rpc('execute_sql', {'query': query % limit}).execute()
        return result.data if result.data else []
    
    async def save_discovered_page(self, 
                                 url: str,
                                 title: str,
                                 page_type: str,
                                 html_content: str = None) -> int:
        """Save discovered AppFolio page"""
        
        page_data = {
            'url': url,
            'title': title,
            'page_type': page_type,
            'html_content': html_content,
            'discovered_at': datetime.now().isoformat()
        }
        
        # Use upsert to handle duplicates
        result = self.supabase.table('appfolio_pages').upsert(
            page_data, 
            on_conflict='url'
        ).execute()
        
        return result.data[0]['id'] if result.data else None
    
    async def save_calculation_formula(self,
                                     page_id: int,
                                     formula_type: str,
                                     formula_expression: str,
                                     variables: Dict,
                                     javascript_code: str = None,
                                     context_description: str = None) -> int:
        """Save discovered calculation formula"""
        
        formula_data = {
            'page_id': page_id,
            'formula_type': formula_type,
            'formula_expression': formula_expression,
            'variables': variables,
            'javascript_code': javascript_code,
            'context_description': context_description,
            'verification_status': 'pending'
        }
        
        result = self.supabase.table('calculation_formulas').insert(formula_data).execute()
        return result.data[0]['id'] if result.data else None
    
    async def get_validation_dashboard(self) -> List[Dict]:
        """Get current validation dashboard status"""
        
        result = self.supabase.table('validation_dashboard').select('*').execute()
        return result.data if result.data else []
    
    async def get_ai_api_performance(self) -> List[Dict]:
        """Get AI API performance metrics"""
        
        result = self.supabase.table('ai_api_performance').select('*').execute()
        return result.data if result.data else []
    
    async def update_formula_status(self, 
                                  formula_id: int,
                                  status: str,
                                  expected_result: float = None) -> None:
        """Update formula verification status"""
        
        update_data = {'verification_status': status}
        if expected_result is not None:
            update_data['expected_result'] = expected_result
            
        self.supabase.table('calculation_formulas').update(
            update_data
        ).eq('id', formula_id).execute()
    
    async def get_system_health(self) -> Dict:
        """Get overall system health metrics"""
        
        query = """
        SELECT 
            (SELECT COUNT(*) FROM appfolio_pages) as total_pages,
            (SELECT COUNT(*) FROM calculation_formulas) as total_formulas,
            (SELECT COUNT(*) FROM multi_ai_validations) as total_validations,
            (SELECT COUNT(*) FROM multi_ai_validations WHERE consensus_achieved = true) as successful_validations,
            (SELECT COUNT(*) FROM multi_ai_validations WHERE requires_manual_review = true) as manual_reviews_needed,
            (SELECT ROUND(AVG(consensus_score), 2) FROM multi_ai_validations WHERE consensus_achieved = true) as avg_consensus_score
        """
        
        result = self.supabase.rpc('execute_sql', {'query': query}).execute()
        return result.data[0] if result.data else {}

# =============================================================================
# EXAMPLE INTEGRATION INTO YOUR AGENT CLASS
# =============================================================================

# Add this to your MultiAIInterlinkedAppFolioBuilder class:

def __init__(self):
    # ... existing initialization ...
    
    # Add Supabase integration
    import os
    from supabase import create_client
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    self.supabase = create_client(supabase_url, supabase_key)
    self.db = SupabaseIntegration(self.supabase)

async def enhanced_multi_ai_validation_with_db(self, page_info: Dict, analysis_prompt: str) -> Dict:
    """Enhanced validation with database logging"""
    
    # Get page and formula IDs from database
    page_id = await self.db.save_discovered_page(
        url=page_info['url'],
        title=page_info['name'],
        page_type=page_info.get('page_type', 'unknown')
    )
    
    # Run multi-AI validation (your existing code)
    validation_results = await self.multi_ai_validation(page_info, analysis_prompt)
    
    # For each formula discovered, save to database
    for calc in page_info.get('critical_calculations', []):
        formula_id = await self.db.save_calculation_formula(
            page_id=page_id,
            formula_type=calc,
            formula_expression=f"Calculate {calc}",
            variables={},
            context_description=page_info.get('description', '')
        )
        
        # Log validation result
        validation_id = await self.db.log_validation_result(
            page_id=page_id,
            formula_id=formula_id,
            validation_results=validation_results
        )
        
        # Update formula status if consensus achieved
        if validation_results['consensus_analysis']['consensus_achieved']:
            await self.db.update_formula_status(formula_id, 'verified')
    
    return validation_results

async def print_enhanced_dashboard(self):
    """Print enhanced dashboard with database metrics"""
    
    dashboard = await self.db.get_validation_dashboard()
    api_performance = await self.db.get_ai_api_performance()
    system_health = await self.db.get_system_health()
    
    print("\n" + "="*80)
    print("🤖 MULTI-AI VALIDATION DASHBOARD")
    print("="*80)
    
    for page in dashboard:
        print(f"📄 {page['page_title']}")
        print(f"   📊 Calculations: {page['total_formulas']}/{page['calculations_count']}")
        print(f"   ✅ Consensus Rate: {page.get('consensus_rate_percent', 0)}%")
        print(f"   🕒 Last Validation: {page.get('last_validation', 'Never')}")
        print()
    
    print("\n🤖 AI API PERFORMANCE:")
    for api in api_performance:
        print(f"   {api['ai_provider']}: {api['success_rate_percent']}% success")
    
    print(f"\n📈 SYSTEM HEALTH:")
    print(f"   Total Pages: {system_health.get('total_pages', 0)}")
    print(f"   Total Validations: {system_health.get('total_validations', 0)}")
    print(f"   Success Rate: {system_health.get('avg_consensus_score', 0)}%")
    print("="*80)
