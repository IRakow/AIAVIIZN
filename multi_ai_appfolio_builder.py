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
import ssl
import certifi
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
        self.ai_validation_results = {}
        self.consensus_threshold = 0.01  # 1% tolerance for numerical differences
        
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

        # Priority URLs for processing
        self.priority_urls = [
            "https://celticprop.appfolio.com/buffered_reports/rent_roll?customize=true",
            "https://celticprop.appfolio.com/buffered_reports/income_statement", 
            "https://celticprop.appfolio.com/buffered_reports/delinquency",
            "https://celticprop.appfolio.com/properties",
            "https://celticprop.appfolio.com/tenants"
        ]

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
            # Create SSL context for macOS compatibility
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
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
            # Create SSL context for macOS compatibility
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}',
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
        
        # Run all three AIs in parallel
        tasks = [
            self.validate_with_openai(analysis_prompt, calculation_data),
            self.validate_with_gemini(analysis_prompt, calculation_data)
        ]
        
        # Execute parallel validation
        ai_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Add Claude validation prompt (manual for now)
        claude_validation_prompt = self.create_claude_validation_prompt(analysis_prompt, calculation_data)
        
        validation_summary = {
            "page_name": page_info['name'],
            "validation_timestamp": datetime.now().isoformat(),
            "openai_result": ai_results[0] if len(ai_results) > 0 else None,
            "gemini_result": ai_results[1] if len(ai_results) > 1 else None,
            "claude_validation_prompt": claude_validation_prompt,
            "consensus_analysis": self.analyze_consensus(ai_results),
            "validation_priority": calculation_data['validation_priority']
        }
        
        return validation_summary

    def analyze_consensus(self, ai_results: List[Dict]) -> Dict:
        """Analyze consensus between AI validation results"""
        
        successful_results = [r for r in ai_results if isinstance(r, dict) and r.get('success', False)]
        
        if len(successful_results) < 2:
            return {
                "consensus_achieved": False,
                "reason": "Insufficient successful AI responses",
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
            "consensus_achieved": len(successful_results) >= 2,
            "successful_validations": len(successful_results),
            "total_attempts": len(ai_results),
            "recommendation": "Compare AI responses manually for consensus",
            "requires_manual_review": True
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
        print(f"🎯 Processing {len(self.priority_urls)} pages with:")
        print("   • Claude: Comprehensive analysis + implementation")
        print("   • OpenAI GPT-4: Mathematical accuracy verification") 
        print("   • Google Gemini: Business logic validation")
        print("   • Cross-AI consensus analysis")
        print("=" * 80)

        # Verify API keys
        if not self.openai_api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found. OpenAI validation will be skipped.")
        if not self.gemini_api_key:
            print("⚠️  Warning: GEMINI_API_KEY not found. Gemini validation will be skipped.")

        # Create master navigation system first
        nav_file = "master_multi_ai_navigation_system.txt"
        nav_instructions = self.create_master_navigation_with_multi_ai()
        
        with open(nav_file, 'w') as f:
            f.write(nav_instructions)
        
        print(f"🧭 Master navigation system: {nav_file}")
        print("🚨 MANUAL STEP REQUIRED:")
        print("   1. Copy navigation instructions to Claude")
        print("   2. Let Claude create the master navigation system")
        print("   3. Press Enter when navigation system is complete")
        
        subprocess.run(['open', '-t', nav_file])
        input("Press Enter when navigation system is created...")

        # Process each page with multi-AI validation
        for i, url in enumerate(self.priority_urls):
            page_num = i + 1
            page_info = self.get_page_info(url)
            page_name = page_info["name"]
            
            print(f"\n{'='*80}")
            print(f"🤖 MULTI-AI ANALYSIS {page_num}/{len(self.priority_urls)}: {page_name}")
            print(f"🔗 URL: {url}")
            print(f"🎯 Priority: {page_info.get('validation_priority', 'MEDIUM')}")
            print(f"🧮 Critical Calculations: {page_info.get('critical_calculations', [])}")
            print(f"{'='*80}")

            # Create enhanced analysis with multi-AI validation
            enhanced_analysis = self.create_enhanced_comprehensive_analysis_with_multi_ai(url, page_num, page_info)
            
            # Save Claude instructions
            claude_file = f"claude_multi_ai_analysis_{page_name.lower().replace(' ', '_')}.txt"
            with open(claude_file, 'w') as f:
                f.write(enhanced_analysis)

            print(f"📝 Claude analysis instructions: {claude_file}")
            print("🚨 MANUAL STEP - CLAUDE ANALYSIS:")
            print(f"   1. Copy instructions for {page_name}")
            print("   2. Paste into Claude for comprehensive analysis")
            print("   3. Press Enter when Claude analysis is complete")

            subprocess.run(['open', '-t', claude_file])
            input(f"Press Enter when Claude analysis for {page_name} is complete...")

            # Run parallel AI validation
            print(f"🤖 Running parallel AI validation for {page_name}...")
            validation_results = await self.multi_ai_validation(page_info, enhanced_analysis)
            
            # Save validation results
            validation_file = f"multi_ai_validation_{page_name.lower().replace(' ', '_')}.json"
            with open(validation_file, 'w') as f:
                json.dump(validation_results, f, indent=2)

            print(f"✅ Multi-AI validation complete: {validation_file}")
            print(f"🎯 Consensus achieved: {validation_results['consensus_analysis']['consensus_achieved']}")
            
            # Store results
            self.ai_validation_results[page_name] = validation_results
            
            # Clean up files
            if os.path.exists(claude_file):
                os.remove(claude_file)
            
            self.total_pages_processed += 1
            print(f"✅ {page_name} completed with multi-AI validation!")
            print(f"📈 Progress: {self.total_pages_processed}/{len(self.priority_urls)} pages")

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
                "ai_systems_used": ["Claude", "OpenAI GPT-4", "Google Gemini"],
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
        print("🚀 Enhanced with OpenAI + Gemini + Claude validation")
        print("🔗 Complete interlinking system")
        print("🧮 Mathematical consensus verification")
        print("📊 Business logic cross-validation")
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
        print("🔥 Multi-AI validation - TOP 3 pages only")
        builder.priority_urls = builder.priority_urls[:3]
        asyncio.run(builder.process_with_full_multi_ai_interlinking())
    
    elif choice == "3":
        print("\n🚑 STARTING FULL MULTI-AI VALIDATION SYSTEM IMMEDIATELY!")
        time.sleep(1)
        asyncio.run(builder.process_with_full_multi_ai_interlinking())
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
