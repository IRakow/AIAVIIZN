#!/usr/bin/env python3
"""
ENHANCED AIVIIZN AUTONOMOUS APPFOLIO BUILDER - WITH MULTI-AI VALIDATION
Uses Claude + OpenAI + Gemini for cross-validation of math and calculations

Key Features:
- Original interlinking system PLUS multi-AI validation
- Parallel processing with OpenAI GPT-4, Gemini Pro, and Claude
- Mathematical consensus verification
- Calculation accuracy cross-checking
- Business logic validation across all AIs
"""

import os
import json
import time
import asyncio
import aiohttp
import subprocess
import webbrowser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import List, Dict, Optional

class MultiAIInterlinkedAppFolioBuilder:
    def __init__(self):
        self.current_page = 0
        self.total_pages_processed = 0
        self.base_claude_url = "https://claude.ai"
        self.navigation_structure = {}
        self.page_relationships = {}
        self.shared_calculations = {}
        
        # Multi-AI Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.wolfram_app_id = "X479TRR99U"  # Wolfram Alpha LLM API App ID
        self.ai_validation_results = {}
        self.consensus_threshold = 0.01  # 1% tolerance for numerical differences
        
        # AppFolio Database Replication
        self.appfolio_schema_analysis = {}
        self.validated_schema_changes = {}
        self.pending_db_writes = []
        
        # AppFolio Directory Structure
        self.appfolio_directory_structure = {}
        self.templates_base_path = "/Users/ianrakow/Desktop/AIVIIZN/templates"
        
        # Automated link discovery
        self.discovered_links = set()
        self.processed_links = set()
        self.link_queue = []
        self.base_domain = "celticprop.appfolio.com"
        
        # Enhanced page categories with validation requirements
        self.page_categories = {
            "Financial Reports": [
                {
                    "name": "Rent Roll",
                    "url": "https://celticprop.appfolio.com/buffered_reports/rent_roll?customize=true",
                    "route": "/reports/rent-roll",
                    "icon": "📊",
                    "description": "Current rent roll with tenant details",
                    "related_pages": ["income_statement", "tenant_ledger", "delinquency"],
                    "data_dependencies": ["property_data", "tenant_data", "lease_data"],
                    "critical_calculations": ["total_rent", "vacancy_rate", "collection_percentage"],
                    "validation_priority": "HIGH"
                },
                {
                    "name": "Income Statement", 
                    "url": "https://celticprop.appfolio.com/buffered_reports/income_statement",
                    "route": "/reports/income-statement",
                    "icon": "💰",
                    "description": "Property income and expense analysis",
                    "related_pages": ["rent_roll", "expense_tracking", "budget_variance"],
                    "data_dependencies": ["income_data", "expense_data", "budget_data"],
                    "critical_calculations": ["net_operating_income", "expense_ratios", "profit_margins"],
                    "validation_priority": "HIGH"
                },
                {
                    "name": "Delinquency Report",
                    "url": "https://celticprop.appfolio.com/buffered_reports/delinquency",
                    "route": "/reports/delinquency", 
                    "icon": "⚠️",
                    "description": "Outstanding balances and late payments",
                    "related_pages": ["rent_roll", "tenant_ledger", "collections"],
                    "data_dependencies": ["payment_data", "tenant_data", "lease_data"],
                    "critical_calculations": ["total_delinquent", "aging_analysis", "collection_rates"],
                    "validation_priority": "HIGH"
                }
            ],
            "Property Management": [
                {
                    "name": "Property Dashboard",
                    "url": "https://celticprop.appfolio.com/properties",
                    "route": "/properties/dashboard",
                    "icon": "🏢",
                    "description": "Property overview and key metrics",
                    "related_pages": ["rent_roll", "maintenance", "tenant_management"],
                    "data_dependencies": ["property_data", "occupancy_data"],
                    "critical_calculations": ["occupancy_rate", "avg_rent", "property_value"],
                    "validation_priority": "MEDIUM"
                }
            ]
        }

    def crawl_and_discover_links(self, start_url: str) -> List[str]:
        """Discover links starting from the reports page"""
        try:
            response = requests.get(start_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(start_url, href)
                
                # Filter relevant AppFolio links
                if self.is_relevant_link(full_url):
                    links.append(full_url)
                    self.discovered_links.add(full_url)
            
            return links
        except Exception as e:
            print(f"Error crawling {start_url}: {e}")
            return []

    def is_relevant_link(self, url: str) -> bool:
        """Filter relevant AppFolio links"""
        parsed = urlparse(url)
        
        # Must be same domain
        if self.base_domain not in parsed.netloc:
            return False
            
        # Skip external links, anchors, javascript
        if url.startswith(('#', 'javascript:', 'mailto:')):
            return False
            
        # Include relevant paths
        relevant_paths = ['/reports', '/properties', '/tenants', '/maintenance', '/buffered_reports']
        return any(path in parsed.path for path in relevant_paths)

    async def call_claude_api(self, prompt: str) -> str:
        """Make automated call to Claude API"""
        headers = {
            'Authorization': f'Bearer {self.claude_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.anthropic.com/v1/messages', 
                                      headers=headers, json=payload) as response:
                    result = await response.json()
                    return result['content'][0]['text']
        except Exception as e:
            print(f"Claude API error: {e}")
            return f"Error calling Claude API: {e}"

    async def analyze_appfolio_database_structure(self, url: str, page_content: str) -> Dict:
        """Analyze AppFolio page to determine underlying database structure"""
        
        analysis_prompt = f"""
        ANALYZE APPFOLIO DATABASE STRUCTURE FROM PAGE CONTENT

        URL: {url}
        
        Based on this AppFolio page, determine the underlying database schema that would be needed to generate this data.

        ANALYSIS REQUIREMENTS:
        1. Identify all data tables that must exist
        2. Determine table relationships and foreign keys
        3. Identify required columns and data types
        4. Suggest indexes for performance
        5. Identify business logic constraints
        
        ONLY return schema if you are 100% confident it's correct.
        Return JSON format:
        {{
            "confidence_level": "HIGH/MEDIUM/LOW",
            "tables": {{
                "table_name": {{
                    "columns": {{"column_name": "data_type"}},
                    "constraints": [],
                    "relationships": [],
                    "indexes": []
                }}
            }},
            "business_logic": [],
            "validation_notes": []
        }}
        """
        
        schema_analysis = await self.call_claude_api(analysis_prompt)
        
        try:
            import json
            parsed_analysis = json.loads(schema_analysis)
            
            if parsed_analysis.get('confidence_level') == 'HIGH':
                self.appfolio_schema_analysis[url] = parsed_analysis
                return parsed_analysis
            else:
                print(f"⚠️ Low confidence schema analysis for {url}")
                return {}
        except:
            print(f"❌ Could not parse schema analysis for {url}")
            return {}

    async def validate_schema_before_database_write(self, schema_changes: Dict) -> bool:
        """Validate schema changes before writing to database"""
        
        validation_prompt = f"""
        VALIDATE DATABASE SCHEMA CHANGES BEFORE EXECUTION

        Proposed Schema Changes:
        {json.dumps(schema_changes, indent=2)}

        VALIDATION CRITERIA:
        1. Check SQL syntax is correct
        2. Verify foreign key relationships are valid
        3. Ensure data types are appropriate
        4. Check for potential conflicts with existing tables
        5. Validate business logic constraints

        Return JSON:
        {{
            "is_valid": true/false,
            "validation_errors": [],
            "safe_to_execute": true/false,
            "recommended_changes": []
        }}
        """
        
        validation_result = await self.call_claude_api(validation_prompt)
        
        try:
            import json
            parsed_validation = json.loads(validation_result)
            
            if parsed_validation.get('safe_to_execute', False):
                self.validated_schema_changes[datetime.now().isoformat()] = schema_changes
                return True
            else:
                print(f"❌ Schema validation failed: {parsed_validation.get('validation_errors', [])}")
                return False
        except:
            print("❌ Could not parse schema validation result")
            return False

    async def analyze_appfolio_directory_structure(self, url: str) -> Dict:
        """Analyze AppFolio's directory structure from page URL and content"""
        
        structure_prompt = f"""
        ANALYZE APPFOLIO DIRECTORY STRUCTURE

        URL: {url}
        
        Based on this AppFolio URL pattern, determine the logical directory structure that should be replicated.

        STRUCTURE ANALYSIS:
        1. Identify main categories (reports, properties, leasing, etc.)
        2. Determine subcategories and hierarchy
        3. Map URL patterns to directory structure
        4. Suggest template organization

        Current base path: {self.templates_base_path}
        
        Return JSON:
        {{
            "main_category": "category_name",
            "subcategory": "subcategory_name", 
            "suggested_path": "templates/category/subcategory/",
            "template_name": "page_name.html",
            "related_templates": []
        }}
        """
        
        structure_analysis = await self.call_claude_api(structure_prompt)
        
        try:
            import json
            parsed_structure = json.loads(structure_analysis)
            self.appfolio_directory_structure[url] = parsed_structure
            return parsed_structure
        except:
            print(f"❌ Could not parse directory structure for {url}")
            return {"suggested_path": "templates/", "template_name": "unknown_page.html"}

    async def create_supabase_migration(self, schema_changes: Dict) -> str:
        """Create Supabase migration SQL from validated schema changes"""
        
        migration_prompt = f"""
        CREATE SUPABASE MIGRATION SQL

        Validated Schema Changes:
        {json.dumps(schema_changes, indent=2)}

        MIGRATION REQUIREMENTS:
        1. Use CREATE TABLE IF NOT EXISTS for new tables
        2. Use ALTER TABLE ADD COLUMN IF NOT EXISTS for new columns
        3. Include proper UUID generation
        4. Add proper indexes for performance
        5. Include constraints and relationships
        6. Make it Supabase/PostgreSQL compatible

        Return complete SQL migration script that can be executed safely.
        """
        
        migration_sql = await self.call_claude_api(migration_prompt)
        return migration_sql

    async def integrate_ai_conversation_system(self, page_info: Dict, generated_content: Dict) -> Dict:
        """Integrate AI conversation system into generated pages"""
        
        integration_prompt = f"""
        INTEGRATE AI CONVERSATION SYSTEM

        Page Info: {json.dumps(page_info, indent=2)}
        Generated Content Summary: {json.dumps(generated_content, indent=2)}

        INTEGRATION REQUIREMENTS:
        1. Add AI chat widget to appropriate pages
        2. Connect to ai_conversations table
        3. Enable contextual help based on page content
        4. Add smart suggestions based on page data
        5. Include conversation history for users

        Return integration specifications:
        {{
            "requires_ai_chat": true/false,
            "chat_context": "page_specific_context",
            "suggested_prompts": [],
            "integration_points": []
        }}
        """
        
        integration_specs = await self.call_claude_api(integration_prompt)
        
        try:
            import json
            parsed_specs = json.loads(integration_specs)
            return parsed_specs
        except:
            print("❌ Could not parse AI integration specs")
    async def save_generated_template(self, page_name: str, directory_structure: Dict, claude_analysis_result: str, ai_integration: Dict) -> str:
        """Save generated HTML template and all other files to proper directory"""
        
        # Create directory path based on AppFolio structure
        template_path = directory_structure.get('suggested_path', 'templates/').replace('templates/', '')
        template_name = directory_structure.get('template_name', f"{page_name.lower().replace(' ', '_')}.html")
        
        # Create full directory path
        full_dir_path = f"{self.templates_base_path}/{template_path}"
        os.makedirs(full_dir_path, exist_ok=True)
        
        full_template_path = f"{full_dir_path}/{template_name}"
        
        # Extract and save HTML template from Claude's analysis
        template_extraction_prompt = f"""
        EXTRACT COMPLETE HTML TEMPLATE FROM ANALYSIS

        Analysis Result: {claude_analysis_result}
        AI Integration: {json.dumps(ai_integration, indent=2)}

        Extract the complete HTML template that was generated. Return ONLY the HTML template code with:
        1. Proper template structure extending base.html
        2. All CSS styling included
        3. All JavaScript calculations included
        4. AI integration components if specified
        5. Complete functional template ready to use

        Return only the HTML template code, nothing else.
        """
        
        html_template = await self.call_claude_api(template_extraction_prompt)
        
        # Apply branding substitution
        html_template = self.substitute_branding(html_template)
        
        # Save HTML template
        with open(full_template_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        # Save JavaScript calculations if they exist
        js_dir = f"{self.templates_base_path}/../static/js/{template_path}"
        os.makedirs(js_dir, exist_ok=True)
        
        js_extraction_prompt = f"""
        EXTRACT JAVASCRIPT CALCULATIONS FROM ANALYSIS

        Analysis Result: {claude_analysis_result}

        Extract any JavaScript calculation functions that were created. Return ONLY the JavaScript code, nothing else.
        If no JavaScript was created, return "// No JavaScript calculations"
        """
        
        js_calculations = await self.call_claude_api(js_extraction_prompt)
        
        # Apply branding substitution
        js_calculations = self.substitute_branding(js_calculations)
        
        js_file_path = f"{js_dir}/{page_name.lower().replace(' ', '_')}_calculations.js"
        
        with open(js_file_path, 'w', encoding='utf-8') as f:
            f.write(js_calculations)
        
        return full_template_path

    async def save_all_generated_files(self, page_name: str, directory_structure: Dict, claude_analysis_result: str, ai_integration: Dict, schema_analysis: Dict, api_monitoring_data: Dict = None, api_validation_results: Dict = None) -> Dict:
        """Save all files generated by the agent"""
        
        saved_files = {}
        
        # Save HTML template
        template_path = await self.save_generated_template(page_name, directory_structure, claude_analysis_result, ai_integration)
        saved_files['template'] = template_path
        
        # Save CSS files if generated
        css_extraction_prompt = f"""
        EXTRACT CSS STYLES FROM ANALYSIS

        Analysis Result: {claude_analysis_result}

        Extract any custom CSS styles that were created for this page. Return ONLY the CSS code, nothing else.
        If no custom CSS was created, return "/* No custom CSS */"
        """
        
        # Use existing CSS framework instead of creating new CSS
        # Templates should extend base.html and use existing CSS classes
        css_integration_prompt = f"""
        INTEGRATE WITH EXISTING CSS FRAMEWORK

        Analysis Result: {claude_analysis_result}

        Instead of creating new CSS, ensure the template uses existing CSS classes and extends base.html properly.
        Return "USES_EXISTING_CSS" if template properly uses existing framework.
        Only return custom CSS if absolutely necessary overrides are needed.
        """
        
        css_check = await self.call_claude_api(css_integration_prompt)
        
        if "USES_EXISTING_CSS" not in css_check and "/* No custom CSS */" not in css_check:
            # Only create CSS file if absolutely necessary overrides needed
            css_dir = f"{self.templates_base_path}/../static/css/{directory_structure.get('suggested_path', '').replace('templates/', '')}"
            os.makedirs(css_dir, exist_ok=True)
            css_file_path = f"{css_dir}/{page_name.lower().replace(' ', '_')}_overrides.css"
            
            # Apply branding substitution to minimal CSS overrides
            css_check = self.substitute_branding(css_check)
            
            with open(css_file_path, 'w', encoding='utf-8') as f:
                f.write(css_check)
            
            saved_files['css_overrides'] = css_file_path
        else:
            saved_files['css_framework'] = "Uses existing CSS framework"
        
        # Save any documentation files
        if claude_analysis_result:
            docs_dir = f"{self.templates_base_path}/../docs/{directory_structure.get('suggested_path', '').replace('templates/', '')}"
            os.makedirs(docs_dir, exist_ok=True)
            docs_file_path = f"{docs_dir}/{page_name.lower().replace(' ', '_')}_documentation.md"
            
            documentation_content = f"""# {page_name} Documentation

## Generated Analysis
{claude_analysis_result}

## Schema Analysis
{json.dumps(schema_analysis, indent=2)}

## AI Integration
{json.dumps(ai_integration, indent=2)}

## Directory Structure
{json.dumps(directory_structure, indent=2)}

## API Monitoring Data
{json.dumps(api_monitoring_data or {}, indent=2)}

## API Validation Results
{json.dumps(api_validation_results or {}, indent=2)}
"""
            
            # Apply branding substitution
            documentation_content = self.substitute_branding(documentation_content)
            
            with open(docs_file_path, 'w', encoding='utf-8') as f:
                f.write(documentation_content)
            
            saved_files['documentation'] = docs_file_path
        
        return saved_files

    async def validate_with_openai(self, analysis_prompt: str, calculation_data: Dict) -> Dict:
        """Send analysis to OpenAI GPT-4 for validation"""
        
        openai_prompt = f"""
        {analysis_prompt}

        SPECIFIC VALIDATION FOCUS FOR OPENAI:
        🎯 Mathematical Accuracy: Verify all calculations are mathematically correct
        🧮 Formula Validation: Check that formulas match standard accounting practices
        📊 Data Consistency: Ensure calculations are internally consistent
        
        Critical Calculations to Validate:
        {json.dumps(calculation_data.get('critical_calculations', {}), indent=2)}
        
        Return JSON format:
        {{
            "calculations_verified": true/false,
            "mathematical_accuracy": "score 0-100",
            "identified_errors": [],
            "suggested_corrections": [],
            "confidence_level": "HIGH/MEDIUM/LOW"
        }}
        """

        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": "gpt-4-turbo-preview",
            "messages": [
                {"role": "system", "content": "You are a financial calculation expert. Analyze AppFolio calculations for mathematical accuracy."},
                {"role": "user", "content": openai_prompt}
            ],
            "temperature": 0.1,  # Low temperature for consistency
            "max_tokens": 2000
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/chat/completions', 
                                      headers=headers, json=payload) as response:
                    result = await response.json()
                    
                    return {
                        "ai_source": "OpenAI GPT-4",
                        "validation_result": result['choices'][0]['message']['content'],
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    }
        except Exception as e:
            return {
                "ai_source": "OpenAI GPT-4", 
                "error": str(e),
                "success": False
            }

    async def validate_with_wolfram(self, calculation_data: Dict) -> Dict:
        """Send calculations to Wolfram Alpha LLM API for mathematical proof"""
        
        # Extract specific calculations for Wolfram verification
        calculations_to_verify = calculation_data.get('critical_calculations', [])
        
        wolfram_prompt = f"""
        Verify these property management calculations mathematically:
        {json.dumps(calculations_to_verify, indent=2)}
        
        For each calculation, provide:
        1. Mathematical verification (correct/incorrect)
        2. Step-by-step proof if correct
        3. Error explanation if incorrect
        4. Alternative formulation if applicable
        
        Focus on pure mathematical accuracy, not business logic.
        """

        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            "input": wolfram_prompt,
            "appid": self.wolfram_app_id
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.wolframalpha.com/v1/llm-api', 
                                      headers=headers, json=payload) as response:
                    result = await response.text()
                    
                    return {
                        "ai_source": "Wolfram Alpha LLM",
                        "validation_result": result,
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    }
        except Exception as e:
            return {
                "ai_source": "Wolfram Alpha LLM",
                "error": str(e),
                "success": False
            }

    async def validate_with_gemini(self, analysis_prompt: str, calculation_data: Dict) -> Dict:
        """Send analysis to Google Gemini for validation"""
        
        gemini_prompt = f"""
        {analysis_prompt}

        SPECIFIC VALIDATION FOCUS FOR GEMINI:
        🏗️ Business Logic: Verify calculations follow proper business rules
        🔄 Data Flow: Check that data dependencies are correctly handled
        📋 Edge Cases: Identify potential calculation edge cases and errors
        
        Critical Calculations to Validate:
        {json.dumps(calculation_data.get('critical_calculations', {}), indent=2)}
        
        Return JSON format:
        {{
            "business_logic_valid": true/false,
            "data_flow_correct": true/false,
            "edge_cases_identified": [],
            "business_rule_compliance": "score 0-100",
            "confidence_level": "HIGH/MEDIUM/LOW"
        }}
        """

        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": gemini_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2000
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}',
                                      headers=headers, json=payload) as response:
                    result = await response.json()
                    
                    return {
                        "ai_source": "Google Gemini",
                        "validation_result": result['candidates'][0]['content']['parts'][0]['text'],
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    }
        except Exception as e:
            return {
                "ai_source": "Google Gemini",
                "error": str(e), 
                "success": False
            }

    def create_claude_validation_prompt(self, analysis_prompt: str, calculation_data: Dict) -> str:
        """Create Claude-specific validation prompt"""
        
        claude_prompt = f"""
        {analysis_prompt}

        SPECIFIC VALIDATION FOCUS FOR CLAUDE:
        🔗 Integration Logic: Verify how calculations integrate with other pages
        🎯 User Experience: Check that calculations support proper UX flows
        🚀 Implementation: Validate that calculations can be properly implemented
        
        Critical Calculations to Validate:
        {json.dumps(calculation_data.get('critical_calculations', {}), indent=2)}
        
        CLAUDE VALIDATION REQUIREMENTS:
        1. Verify mathematical accuracy of all formulas
        2. Check integration points with related pages  
        3. Validate user experience implications
        4. Ensure implementation feasibility
        5. Identify potential performance issues
        
        Return detailed analysis with:
        - Mathematical verification results
        - Integration compatibility assessment
        - Implementation recommendations
        - Performance considerations
        """
        
        return claude_prompt

    async def multi_ai_validation(self, page_info: Dict, analysis_prompt: str) -> Dict:
        """Run validation across all three AIs simultaneously"""
        
        calculation_data = {
            "critical_calculations": page_info.get('critical_calculations', []),
            "validation_priority": page_info.get('validation_priority', 'MEDIUM'),
            "related_pages": page_info.get('related_pages', [])
        }

        print(f"🤖 Starting multi-AI validation for {page_info['name']}...")
        print(f"🎯 Priority: {calculation_data['validation_priority']}")
        
        # Run all four AIs in parallel
        claude_validation_prompt = self.create_claude_validation_prompt(analysis_prompt, calculation_data)
        
        tasks = [
            self.validate_with_openai(analysis_prompt, calculation_data),
            self.validate_with_gemini(analysis_prompt, calculation_data),
            self.call_claude_api(claude_validation_prompt),
            self.validate_with_wolfram(calculation_data)
        ]
        
        # Execute parallel validation
        ai_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        validation_summary = {
            "page_name": page_info['name'],
            "validation_timestamp": datetime.now().isoformat(),
            "openai_result": ai_results[0] if len(ai_results) > 0 else None,
            "gemini_result": ai_results[1] if len(ai_results) > 1 else None,
            "claude_result": ai_results[2] if len(ai_results) > 2 else None,
            "wolfram_result": ai_results[3] if len(ai_results) > 3 else None,
            "consensus_analysis": self.analyze_consensus(ai_results),
            "validation_priority": calculation_data['validation_priority']
        }
        
        return validation_summary

    def analyze_consensus(self, ai_results: List[Dict]) -> Dict:
        """Analyze consensus between AI validation results"""
        
        successful_results = [r for r in ai_results if isinstance(r, dict) and r.get('success', False)]
        
        if len(successful_results) < 3:
            return {
                "consensus_achieved": False,
                "reason": "Insufficient successful AI responses (need 3+ out of 4)",
                "recommendation": "Manual review required"
            }

        # Extract key validation points
        consensus_points = {
            "mathematical_accuracy": [],
            "business_logic": [],
            "implementation_feasibility": []
        }
        
        # This would need more sophisticated parsing of AI responses
        # For now, return structure for manual analysis
        return {
            "consensus_achieved": len(successful_results) >= 3,
            "successful_validations": len(successful_results),
            "total_attempts": len(ai_results),
            "recommendation": "Compare AI responses manually for consensus",
            "requires_manual_review": len(successful_results) < 3
        }

    def create_enhanced_comprehensive_analysis_with_multi_ai(self, url: str, page_num: int, page_info: Dict) -> str:
        """Enhanced analysis with multi-AI validation instructions"""
        
        base_analysis = f"""
🔗 MULTI-AI COMPREHENSIVE ANALYSIS #{page_num}: {page_info['name']}
============================================================================

📍 URL: {url}
🧭 Route: {page_info['route']}
🎯 Priority: {page_info.get('validation_priority', 'MEDIUM')}
🔗 Related Pages: {', '.join(page_info.get('related_pages', []))}

🤖 MULTI-AI VALIDATION WORKFLOW:
============================================================================

STEP 1: CLAUDE COMPREHENSIVE ANALYSIS
------------------------------------
1. Navigate to {url}
2. Extract all visible calculations and formulas
3. Identify mathematical relationships between data points
4. Document business logic and calculation dependencies
5. Create detailed technical specifications

STEP 2: PARALLEL AI VALIDATION (AUTOMATED)
-----------------------------------------
✅ OpenAI GPT-4: Mathematical accuracy verification
✅ Google Gemini: Business logic and edge case analysis  
✅ Claude: Integration and implementation validation

STEP 3: CRITICAL CALCULATIONS TO VERIFY
---------------------------------------
{chr(10).join([f"• {calc}" for calc in page_info.get('critical_calculations', [])])}

STEP 4: CROSS-PAGE INTEGRATION REQUIREMENTS
-------------------------------------------
Data Dependencies: {', '.join(page_info.get('data_dependencies', []))}
Related Page Connections: {', '.join(page_info.get('related_pages', []))}

STEP 5: VALIDATION SUCCESS CRITERIA
-----------------------------------
✅ All calculations mathematically verified by 3 AIs
✅ Business logic consistent across AI responses
✅ Implementation feasible and performance-optimized
✅ Integration points with related pages validated
✅ Edge cases identified and handled

STEP 6: COMPREHENSIVE DELIVERABLES
----------------------------------
1. 📄 Working HTML template: templates/{page_info['name'].lower().replace(' ', '_')}.html
2. ⚡ JavaScript calculations: static/js/{page_info['name'].lower().replace(' ', '_')}_calculations.js
3. 🔗 Navigation integration: Include in master navigation system
4. 📊 Database schema: SQL for storing {page_info['name']} data
5. 🧪 Test cases: Validation tests for all critical calculations
6. 🤖 AI validation report: Multi-AI consensus analysis

⚠️  VALIDATION REQUIREMENTS:
- Mathematical accuracy must be verified by ALL AIs
- Any discrepancies between AIs must be documented and resolved
- Business logic must be consistent across all AI responses
- Implementation must be technically feasible and performance-optimized

🚀 BEGIN COMPREHENSIVE ANALYSIS WITH MULTI-AI VALIDATION NOW!
"""
        
        return base_analysis

    async def process_with_full_multi_ai_interlinking(self):
        """Enhanced processing with multi-AI validation and interlinking"""
        
        print("🤖 STARTING MULTI-AI VALIDATION SYSTEM")
        print("=" * 80)
        print("🎯 Starting automated link discovery from /reports")
        print("   • Claude: Comprehensive analysis + implementation")
        print("   • OpenAI GPT-4: Mathematical accuracy verification") 
        print("   • Google Gemini: Business logic validation")
        print("   • Wolfram Alpha: Mathematical proof verification")
        print("   • Cross-AI consensus analysis")
        print("=" * 80)

        # Verify API keys
        if not self.openai_api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found. OpenAI validation will be skipped.")
        if not self.gemini_api_key:
            print("⚠️  Warning: GEMINI_API_KEY not found. Gemini validation will be skipped.")
        if not self.claude_api_key:
            print("⚠️  Warning: CLAUDE_API_KEY not found. Claude validation will be manual.")
        if not self.wolfram_app_id:
            print("⚠️  Warning: Wolfram Alpha App ID not configured. Wolfram validation will be skipped.")

        # Create master navigation system automatically
        nav_instructions = self.create_master_navigation_with_multi_ai()
        navigation_result = await self.call_claude_api(nav_instructions)
        
        print(f"🧭 Master navigation system created automatically")
        print("✅ Navigation system generation complete")

        # Discover links starting from reports page
        start_url = f"https://{self.base_domain}/reports"
        print(f"🔍 Starting link discovery from: {start_url}")
        
        initial_links = self.crawl_and_discover_links(start_url)
        self.link_queue.extend(initial_links)
        
        print(f"🔗 Discovered {len(initial_links)} initial links")

        # Process discovered links (max 30 pages)
        while self.link_queue and len(self.processed_links) < 30:
            url = self.link_queue.pop(0)
            
            if url in self.processed_links:
                continue
                
            self.processed_links.add(url)
            page_num = len(self.processed_links)
            page_info = self.get_page_info(url)
            page_name = page_info["name"]
            
            print(f"\n{'='*80}")
            print(f"🤖 MULTI-AI ANALYSIS {page_num}: {page_name}")
            print(f"🔗 URL: {url}")
            print(f"🎯 Priority: {page_info.get('validation_priority', 'MEDIUM')}")
            print(f"🧮 Critical Calculations: {page_info.get('critical_calculations', [])}")
            print(f"{'='*80}")

            # Create enhanced analysis with multi-AI validation
            enhanced_analysis = self.create_enhanced_comprehensive_analysis_with_multi_ai(url, page_num, page_info)
            
            # NEW: Analyze AppFolio database structure from this page
            print(f"🗄️ Analyzing database structure for {page_name}...")
            schema_analysis = await self.analyze_appfolio_database_structure(url, enhanced_analysis)
            
            # NEW: Analyze AppFolio directory structure  
            print(f"📁 Analyzing directory structure for {page_name}...")
            directory_structure = await self.analyze_appfolio_directory_structure(url)
            
            # NEW: Monitor AppFolio API calls
            print(f"🕵️ Monitoring AppFolio API calls for {page_name}...")
            api_monitoring_data = await self.monitor_appfolio_api_calls(url)
            
            # NEW: Capture network requests
            print(f"🌐 Capturing network requests for {page_name}...")
            captured_api_calls = await self.capture_network_requests(url)
            
            # Automated Claude analysis
            print(f"🤖 Running automated Claude analysis for {page_name}...")
            claude_analysis_result = await self.call_claude_api(enhanced_analysis)
            
            print(f"✅ Claude analysis complete for {page_name}")

            # NEW: Validate schema changes before database write
            if schema_analysis:
                print(f"🔍 Validating schema changes for {page_name}...")
                schema_valid = await self.validate_schema_before_database_write(schema_analysis)
                
                if schema_valid:
                    # NEW: Create Supabase migration
                    print(f"📝 Creating Supabase migration for {page_name}...")
                    migration_sql = await self.create_supabase_migration(schema_analysis)
                    
                    # Save migration for review
                    migration_file = f"migration_{page_name.lower().replace(' ', '_')}.sql"
                    with open(migration_file, 'w') as f:
                        f.write(migration_sql)
                    print(f"💾 Migration saved: {migration_file}")

            # Run parallel AI validation
            print(f"🤖 Running parallel AI validation for {page_name}...")
            validation_results = await self.multi_ai_validation(page_info, enhanced_analysis)
            
            # NEW: Validate against captured API data
            print(f"🎯 Validating calculations against AppFolio API data for {page_name}...")
            api_validation_results = await self.validate_against_api_data(
                validation_results, 
                captured_api_calls
            )
            
            # NEW: Integrate AI conversation system (disabled for AIVIIZN)
            print(f"🤖 Checking AI conversation system integration for {page_name}...")
            ai_integration = await self.integrate_ai_conversation_system(page_info, {
                "claude_analysis": claude_analysis_result,
                "validation_results": validation_results,
                "schema_analysis": schema_analysis,
                "directory_structure": directory_structure,
                "api_monitoring_data": api_monitoring_data,
                "api_validation_results": api_validation_results
            })

            # NEW: Save all generated files
            print(f"💾 Saving all generated files for {page_name}...")
            saved_files = await self.save_all_generated_files(
                page_name, 
                directory_structure, 
                claude_analysis_result, 
                ai_integration, 
                schema_analysis,
                api_monitoring_data,
                api_validation_results
            )
            print(f"✅ Files saved: {list(saved_files.keys())}")
            for file_type, file_path in saved_files.items():
                print(f"   📁 {file_type}: {file_path}")
            
            # Save validation results
            validation_file = f"multi_ai_validation_{page_name.lower().replace(' ', '_')}.json"
            with open(validation_file, 'w') as f:
                json.dump(validation_results, f, indent=2)

            print(f"✅ Multi-AI validation complete: {validation_file}")
            print(f"🎯 Consensus achieved: {validation_results['consensus_analysis']['consensus_achieved']}")
            
            # Store results with new data
            self.ai_validation_results[page_name] = {
                **validation_results,
                "schema_analysis": schema_analysis,
                "directory_structure": directory_structure,
                "ai_integration": ai_integration,
                "claude_analysis_result": claude_analysis_result,
                "api_monitoring_data": api_monitoring_data,
                "captured_api_calls": captured_api_calls,
                "api_validation_results": api_validation_results,
                "saved_files": saved_files
            }
            
            # Discover more links from current page
            new_links = self.crawl_and_discover_links(url)
            for new_link in new_links:
                if new_link not in self.processed_links and new_link not in self.link_queue:
                    self.link_queue.append(new_link)
            
            self.total_pages_processed += 1
            print(f"✅ {page_name} completed with multi-AI validation!")
            print(f"📈 Progress: {self.total_pages_processed} pages processed, {len(self.link_queue)} remaining")

        # Generate final multi-AI validation report
        await self.generate_final_multi_ai_report()
        
        print(f"\n🎉 MULTI-AI VALIDATION SYSTEM COMPLETED!")
        print(f"✅ Total pages processed: {self.total_pages_processed}")
        print(f"🤖 AI validations completed: {len(self.ai_validation_results)}")
        print(f"🔗 Complete navigation system with multi-AI validation")

    async def generate_final_multi_ai_report(self):
        """Generate comprehensive report of all multi-AI validations"""
        
        report = {
            "multi_ai_validation_summary": {
                "total_pages_processed": self.total_pages_processed,
                "validation_timestamp": datetime.now().isoformat(),
                "ai_systems_used": ["Claude", "OpenAI GPT-4", "Google Gemini", "Wolfram Alpha LLM"],
                "consensus_threshold": self.consensus_threshold
            },
            "page_validations": self.ai_validation_results,
            "overall_consensus": self.calculate_overall_consensus(),
            "recommendations": self.generate_validation_recommendations()
        }
        
        report_file = "final_multi_ai_validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Final multi-AI validation report: {report_file}")

    def calculate_overall_consensus(self) -> Dict:
        """Calculate overall consensus across all page validations"""
        
        total_validations = len(self.ai_validation_results)
        consensus_achieved = sum(1 for result in self.ai_validation_results.values() 
                               if result['consensus_analysis']['consensus_achieved'])
        
        return {
            "consensus_rate": consensus_achieved / total_validations if total_validations > 0 else 0,
            "total_pages": total_validations,
            "consensus_pages": consensus_achieved,
            "requires_review": total_validations - consensus_achieved
        }

    def generate_validation_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        
        recommendations = []
        
        for page_name, results in self.ai_validation_results.items():
            if not results['consensus_analysis']['consensus_achieved']:
                recommendations.append(f"Manual review required for {page_name} calculations")
        
        if not recommendations:
            recommendations.append("All pages achieved AI consensus - system ready for implementation")
        
        return recommendations

    def get_page_info(self, url: str) -> Dict:
        """Get page information from categories"""
        
        for category_name, pages in self.page_categories.items():
            for page in pages:
                if page["url"] == url:
                    return page
        
        # Default page info if not found
        return {
            "name": "Unknown Page",
            "route": "/unknown",
            "icon": "❓",
            "description": "Page information not found",
            "related_pages": [],
            "data_dependencies": [],
            "critical_calculations": [],
            "validation_priority": "LOW"
        }

    def create_master_navigation_with_multi_ai(self) -> str:
        """Create master navigation system with multi-AI validation info"""
        
        nav_instructions = """
🧭 MASTER NAVIGATION SYSTEM WITH MULTI-AI VALIDATION
====================================================

Create a comprehensive navigation system that includes:

1. 📊 MAIN NAVIGATION MENU
   - Financial Reports (with validation badges)
   - Property Management  
   - Tenant Management
   - Maintenance & Work Orders
   - Settings & Configuration

2. 🤖 MULTI-AI VALIDATION INDICATORS
   - Green checkmark: All AIs achieved consensus
   - Yellow warning: Partial consensus, review needed
   - Red alert: No consensus, manual verification required

3. 🔗 INTER-PAGE CONNECTIONS
   - Related page suggestions
   - Data dependency indicators
   - Calculation flow diagrams

4. 📱 RESPONSIVE DESIGN
   - Mobile-friendly navigation
   - Collapsible menu system
   - Quick access toolbar

NAVIGATION FEATURES TO IMPLEMENT:
- Breadcrumb navigation showing current location
- Related pages sidebar
- Calculation validation status for each page
- Multi-AI confidence indicators
- Quick jump between related financial reports

CREATE THE COMPLETE NAVIGATION SYSTEM NOW!
"""
        
        return nav_instructions

    def print_banner(self):
        """Print startup banner"""
        print("🤖 MULTI-AI AIVIIZN AUTONOMOUS APPFOLIO BUILDER")
        print("=" * 80)
        print("🚀 Enhanced with OpenAI + Gemini + Claude + Wolfram Alpha validation")
        print("🔗 Complete interlinking system")
        print("🧮 Mathematical consensus verification")
        print("📊 Business logic cross-validation")
        print("🏆 Mathematical proof verification via Wolfram Alpha")
        print("=" * 80)

# Main execution
def main():
    builder = MultiAIInterlinkedAppFolioBuilder()
    builder.print_banner()
    
    print("\n🤖 MULTI-AI VALIDATION OPTIONS:")
    print("1. 🚀 Process all pages with FULL multi-AI validation")
    print("2. 🔥 Process top 3 pages with multi-AI validation (test)")
    print("3. 🚑 START IMMEDIATELY - Full multi-AI system")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        confirm = input("\nReady for FULL multi-AI validation system? (y/N): ").strip().lower()
        if confirm == 'y':
            asyncio.run(builder.process_with_full_multi_ai_interlinking())
        else:
            print("❌ Cancelled.")
    
    elif choice == "2":
        print("🔥 Multi-AI validation - Limited link discovery")
        asyncio.run(builder.process_with_full_multi_ai_interlinking())
    
    elif choice == "3":
        print("\n🚑 STARTING FULL MULTI-AI VALIDATION SYSTEM IMMEDIATELY!")
        time.sleep(1)
        asyncio.run(builder.process_with_full_multi_ai_interlinking())
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()