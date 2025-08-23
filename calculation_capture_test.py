#!/usr/bin/env python3
"""
AIVIIZN CALCULATION CAPTURE TEST
Small working test to verify AppFolio math extraction and replication

This test version focuses on:
✅ Capturing real calculations from AppFolio pages
✅ Extracting formulas, variables, and math operations
✅ Storing calculation data in Supabase
✅ Creating working replicated calculations
✅ Integrating with existing AIVIIZN base template
"""

import asyncio
import json
import re
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import logging

class AppFolioCalculationCapture:
    """Captures and analyzes real calculations from AppFolio pages"""
    
    def __init__(self, supabase_project_id: str):
        self.supabase_project_id = supabase_project_id
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.captures_dir = Path("calculation_captures")
        self.captures_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    async def initialize_browser(self):
        """Initialize browser for AppFolio capture"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await context.new_page()
        
        # Monitor JavaScript execution for calculations
        self.calculations_found = []
        
        await self.page.add_init_script("""
            // Capture all mathematical operations
            window.originalMath = {};
            Object.getOwnPropertyNames(Math).forEach(prop => {
                if (typeof Math[prop] === 'function') {
                    window.originalMath[prop] = Math[prop];
                    Math[prop] = function(...args) {
                        window.calculationCapture = window.calculationCapture || [];
                        const result = window.originalMath[prop].apply(Math, args);
                        window.calculationCapture.push({
                            operation: prop,
                            arguments: args,
                            result: result,
                            timestamp: Date.now(),
                            stack: new Error().stack
                        });
                        return result;
                    };
                }
            });
            
            // Capture arithmetic operations
            window.originalNumberPrototype = {};
            ['valueOf', 'toString'].forEach(method => {
                window.originalNumberPrototype[method] = Number.prototype[method];
            });
            
            // Capture calculation contexts
            window.captureCalculation = function(type, formula, variables, result) {
                window.customCalculations = window.customCalculations || [];
                window.customCalculations.push({
                    type: type,
                    formula: formula,
                    variables: variables,
                    result: result,
                    timestamp: Date.now(),
                    context: document.title
                });
            };
        """)
        
        self.logger.info("✅ Browser initialized with calculation capture")
    
    async def capture_page_calculations(self, url: str) -> Dict[str, Any]:
        """Capture all calculations from a specific AppFolio page"""
        self.logger.info(f"🧮 Capturing calculations from: {url}")
        
        # Navigate to page
        await self.page.goto(url, wait_until='networkidle')
        await asyncio.sleep(5)  # Wait for calculations to load
        
        # Handle login if needed
        if 'login' in await self.page.url() or 'sign' in await self.page.url():
            print("🔐 Please login manually and press ENTER when ready...")
            input()
            await self.page.wait_for_load_state('networkidle')
        
        # Extract page information
        title = await self.page.title()
        
        # Take screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.captures_dir / f"calc_{timestamp}.png"
        await self.page.screenshot(path=screenshot_path, full_page=True)
        
        # Extract JavaScript calculations
        js_calculations = await self.page.evaluate("""
            () => {
                return {
                    mathOperations: window.calculationCapture || [],
                    customCalculations: window.customCalculations || [],
                    allScripts: Array.from(document.scripts).map(s => s.textContent).filter(t => t && t.includes('*') || t.includes('+') || t.includes('calculate'))
                };
            }
        """)
        
        # Extract HTML-based calculations (tables, forms, etc.)
        html_calculations = await self.extract_html_calculations()
        
        # Extract financial data patterns
        financial_patterns = await self.extract_financial_patterns()
        
        # Store in Supabase
        page_data = {
            'url': url,
            'title': title,
            'page_type': self.determine_page_type(url),
            'screenshot_path': str(screenshot_path),
            'js_calculations': js_calculations,
            'html_calculations': html_calculations,
            'financial_patterns': financial_patterns,
            'captured_at': datetime.now().isoformat()
        }
        
        await self.store_in_supabase(page_data)
        
        return page_data
    
    async def extract_html_calculations(self) -> List[Dict]:
        """Extract calculations from HTML tables, forms, and text"""
        calculations = []
        
        # Find all tables with numerical data
        tables = await self.page.query_selector_all('table')
        for table in tables:
            table_data = await self.analyze_table_calculations(table)
            if table_data:
                calculations.extend(table_data)
        
        # Find all input fields with calculations
        inputs = await self.page.query_selector_all('input[type="number"], input[value*="$"], input[value*="%"]')
        for input_elem in inputs:
            input_data = await self.analyze_input_calculation(input_elem)
            if input_data:
                calculations.append(input_data)
        
        # Find text-based calculations
        text_calculations = await self.page.evaluate("""
            () => {
                const patterns = [
                    /\\$[\\d,]+\\.\\d{2}/g,  // Money amounts
                    /\\d+\\.\\d{2}%/g,       // Percentages
                    /\\d+\\s*[+\\-*/]\\s*\\d+/g,  // Basic math
                    /Total\\s*:?\\s*\\$[\\d,]+/gi,  // Totals
                    /Balance\\s*:?\\s*\\$[\\d,]+/gi  // Balances
                ];
                
                const calculations = [];
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                
                let node;
                while (node = walker.nextNode()) {
                    const text = node.textContent.trim();
                    patterns.forEach((pattern, index) => {
                        const matches = text.match(pattern);
                        if (matches) {
                            calculations.push({
                                type: ['money', 'percentage', 'arithmetic', 'total', 'balance'][index],
                                text: text,
                                matches: matches,
                                element: node.parentElement.tagName,
                                context: node.parentElement.textContent.trim().substring(0, 100)
                            });
                        }
                    });
                }
                
                return calculations;
            }
        """)
        
        calculations.extend(text_calculations)
        return calculations
    
    async def analyze_table_calculations(self, table) -> List[Dict]:
        """Analyze a table for calculations"""
        calculations = []
        
        # Get table data
        rows = await table.query_selector_all('tr')
        if len(rows) < 2:
            return calculations
        
        # Get headers
        header_cells = await rows[0].query_selector_all('th, td')
        headers = []
        for cell in header_cells:
            headers.append(await cell.inner_text())
        
        # Analyze data rows
        for i, row in enumerate(rows[1:], 1):
            cells = await row.query_selector_all('td')
            row_data = []
            for cell in cells:
                cell_text = await cell.inner_text()
                row_data.append(cell_text.strip())
            
            # Look for calculation patterns
            calculation = self.detect_row_calculation(headers, row_data, i)
            if calculation:
                calculations.append(calculation)
        
        return calculations
    
    def detect_row_calculation(self, headers: List[str], row_data: List[str], row_index: int) -> Optional[Dict]:
        """Detect if a table row contains calculations"""
        money_pattern = r'\$[\d,]+\.?\d*'
        percentage_pattern = r'\d+\.?\d*%'
        
        # Find monetary values
        money_values = []
        percentage_values = []
        
        for i, (header, value) in enumerate(zip(headers, row_data)):
            money_match = re.search(money_pattern, value)
            if money_match:
                amount = float(re.sub(r'[\$,]', '', money_match.group()))
                money_values.append({
                    'column': header,
                    'value': amount,
                    'index': i,
                    'raw': value
                })
            
            percent_match = re.search(percentage_pattern, value)
            if percent_match:
                percent = float(percent_match.group().replace('%', ''))
                percentage_values.append({
                    'column': header,
                    'value': percent,
                    'index': i,
                    'raw': value
                })
        
        # If we have multiple money values, check for calculations
        if len(money_values) >= 2:
            # Look for totals, subtotals, etc.
            for total_header in ['total', 'amount', 'balance', 'due', 'owed']:
                total_col = next((mv for mv in money_values if total_header.lower() in mv['column'].lower()), None)
                if total_col:
                    other_values = [mv for mv in money_values if mv != total_col]
                    
                    # Check if total equals sum of others
                    calculated_total = sum(mv['value'] for mv in other_values)
                    if abs(calculated_total - total_col['value']) < 0.01:
                        return {
                            'type': 'table_sum',
                            'formula': f"SUM({', '.join(mv['column'] for mv in other_values)})",
                            'variables': {mv['column']: mv['value'] for mv in other_values},
                            'result': total_col['value'],
                            'context': f"Row {row_index}",
                            'verification': 'sum_verified'
                        }
        
        return None
    
    async def analyze_input_calculation(self, input_elem) -> Optional[Dict]:
        """Analyze an input field for calculations"""
        value = await input_elem.get_attribute('value')
        name = await input_elem.get_attribute('name')
        id_attr = await input_elem.get_attribute('id')
        
        if not value:
            return None
        
        # Look for calculation patterns
        money_match = re.search(r'\$[\d,]+\.?\d*', value)
        if money_match:
            amount = float(re.sub(r'[\$,]', '', money_match.group()))
            return {
                'type': 'input_field',
                'field_name': name or id_attr,
                'value': amount,
                'raw_value': value,
                'element_type': 'input'
            }
        
        return None
    
    async def extract_financial_patterns(self) -> Dict[str, Any]:
        """Extract common financial calculation patterns"""
        patterns = await self.page.evaluate("""
            () => {
                const financialPatterns = {
                    totals: [],
                    percentages: [],
                    balances: [],
                    calculations: []
                };
                
                // Find common financial terms
                const text = document.body.textContent;
                
                // Rent calculations
                const rentMatches = text.match(/rent\\s*:?\\s*\\$[\\d,]+\\.?\\d*/gi);
                if (rentMatches) {
                    financialPatterns.calculations.push({
                        type: 'rent',
                        matches: rentMatches
                    });
                }
                
                // Fee calculations  
                const feeMatches = text.match(/fee\\s*:?\\s*\\$[\\d,]+\\.?\\d*/gi);
                if (feeMatches) {
                    financialPatterns.calculations.push({
                        type: 'fees',
                        matches: feeMatches
                    });
                }
                
                // Balance calculations
                const balanceMatches = text.match(/balance\\s*:?\\s*\\$[\\d,]+\\.?\\d*/gi);
                if (balanceMatches) {
                    financialPatterns.balances = balanceMatches;
                }
                
                return financialPatterns;
            }
        """)
        
        return patterns
    
    def determine_page_type(self, url: str) -> str:
        """Determine the type of AppFolio page"""
        if 'reports' in url.lower():
            return 'reports'
        elif 'dashboard' in url.lower():
            return 'dashboard'
        elif 'tenants' in url.lower():
            return 'tenants'
        elif 'accounting' in url.lower():
            return 'accounting'
        elif 'properties' in url.lower():
            return 'properties'
        else:
            return 'general'
    
    async def store_in_supabase(self, page_data: Dict[str, Any]):
        """Store captured data in Supabase"""
        # This would use the actual Supabase MCP tools
        # For now, save locally and show SQL
        
        # Save page data
        page_sql = f"""
        INSERT INTO captured_pages (url, page_type, title, screenshot_path, api_calls, interactive_elements)
        VALUES ('{page_data['url']}', '{page_data['page_type']}', '{page_data['title']}', 
                '{page_data['screenshot_path']}', '{json.dumps(page_data.get('js_calculations', {}))}',
                '{json.dumps(page_data.get('html_calculations', []))}');
        """
        
        # Save calculations
        for calc in page_data.get('html_calculations', []):
            if calc.get('type') == 'table_sum':
                calc_sql = f"""
                INSERT INTO appfolio_calculations (page_url, calculation_type, formula, variables, result_value, calculation_context)
                VALUES ('{page_data['url']}', '{calc['type']}', '{calc['formula']}', 
                        '{json.dumps(calc['variables'])}', {calc['result']}, '{calc['context']}');
                """
                print(f"📊 Calculation SQL: {calc_sql}")
        
        print(f"💾 Page SQL: {page_sql}")
        
        # Save to JSON for inspection
        json_file = self.captures_dir / f"calculation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(page_data, f, indent=2, default=str)
        
        self.logger.info(f"✅ Data saved to {json_file}")
    
    async def close(self):
        """Clean up browser"""
        if self.browser:
            await self.browser.close()

async def test_calculation_capture():
    """Test the calculation capture system"""
    print("🧪 AIVIIZN CALCULATION CAPTURE TEST")
    print("=" * 50)
    
    # Test with reports page first
    test_url = input("Enter AppFolio reports URL (default: https://celticprop.appfolio.com/reports): ").strip()
    if not test_url:
        test_url = "https://celticprop.appfolio.com/reports"
    
    capture = AppFolioCalculationCapture("sejebqdhcilwcpjpznep")
    
    try:
        await capture.initialize_browser()
        result = await capture.capture_page_calculations(test_url)
        
        print(f"\n✅ CAPTURE COMPLETE!")
        print(f"📄 Page: {result['title']}")
        print(f"🧮 Calculations found: {len(result.get('html_calculations', []))}")
        print(f"💰 Financial patterns: {len(result.get('financial_patterns', {}).get('calculations', []))}")
        print(f"📸 Screenshot: {result['screenshot_path']}")
        
        # Show found calculations
        if result.get('html_calculations'):
            print(f"\n📊 CALCULATIONS FOUND:")
            for i, calc in enumerate(result['html_calculations'][:3], 1):
                print(f"  {i}. Type: {calc.get('type')}")
                if 'formula' in calc:
                    print(f"     Formula: {calc['formula']}")
                if 'result' in calc:
                    print(f"     Result: ${calc['result']:.2f}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await capture.close()

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_calculation_capture())
