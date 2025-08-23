"""
AIVIIZN BATCH PROCESSOR TEMPLATE
Copy this into each new Claude chat window for autonomous processing
"""

# Batch Processing Instructions for Claude
BATCH_PROCESSING_TEMPLATE = """
🎯 AUTONOMOUS APPFOLIO BATCH PROCESSOR

Process these AppFolio pages autonomously with these exact steps:

FOR EACH URL IN THE BATCH:

1. **Navigate & Capture**
   - playwright:browser_navigate(url)
   - playwright:browser_take_screenshot(fullPage=true, filename="[page_name].png")
   - playwright:browser_snapshot()

2. **Extract Calculations**
   - Use playwright:browser_evaluate() to inject calculation capture JavaScript
   - Extract all numeric patterns, formulas, totals, percentages
   - Identify table structures and mathematical operations
   - Capture column headers and data types

3. **Store in Database**
   - supabase:execute_sql() to store page data in appfolio_pages table
   - supabase:execute_sql() to store calculation formulas in calculation_formulas table
   - Link relationships between pages and calculations

4. **Generate Templates**
   - Create working HTML template in /Users/ianrakow/Desktop/AIVIIZN/templates/[page_name].html
   - Build JavaScript calculation functions in /Users/ianrakow/Desktop/AIVIIZN/static/js/[page_name]_calculations.js
   - Generate Flask route information
   - Use exact AppFolio styling and layout

5. **Store Component Data**
   - supabase:execute_sql() to store in generated_components table
   - Record template path, route path, JavaScript file, calculation functions

6. **Verification**
   - Verify calculations work correctly
   - Test template renders properly
   - Confirm database entries are complete

🎯 PROCESS ALL URLS IN THE BATCH THEN PROVIDE SUMMARY

📊 Expected Output Per Page:
- ✅ Screenshot captured
- ✅ Calculations extracted & stored
- ✅ Working template created
- ✅ JavaScript functions generated
- ✅ Database entries complete
- ✅ Route information documented

🚀 Start processing immediately and work through all URLs systematically.
"""

# JavaScript calculation extraction template
CALCULATION_EXTRACTION_JS = """
() => {
    // Universal AppFolio calculation extractor
    const extractedData = {
        pageInfo: {
            title: document.title,
            url: window.location.href,
            reportType: 'auto_detected'
        },
        calculations: {
            totals: [],
            percentages: [],
            formulas: [],
            summaryRows: []
        },
        structure: {
            columns: [],
            dataRows: [],
            filters: {}
        }
    };
    
    // Extract column headers
    document.querySelectorAll('[role="columnheader"]').forEach((header, index) => {
        const headerText = header.textContent.trim();
        extractedData.structure.columns.push({
            index: index,
            name: headerText,
            type: headerText.includes('%') ? 'percentage' : 
                  headerText.includes('$') || headerText.includes('Amount') || headerText.includes('Total') ? 'monetary' : 
                  headerText.includes('Date') ? 'date' : 'text'
        });
    });
    
    // Extract all numeric data
    const allCells = document.querySelectorAll('[role="gridcell"]');
    let currentRow = [];
    
    allCells.forEach((cell, index) => {
        const cellText = cell.textContent.trim();
        currentRow.push(cellText);
        
        // Check if this completes a row (based on column count)
        if (extractedData.structure.columns.length > 0 && 
            (index + 1) % extractedData.structure.columns.length === 0) {
            
            // Process complete row
            const rowData = {};
            extractedData.structure.columns.forEach((col, i) => {
                rowData[col.name] = currentRow[i];
            });
            
            // Check if it's a total/summary row
            if (currentRow.some(cell => cell.includes('Total') || cell.includes('Summary'))) {
                extractedData.calculations.summaryRows.push(rowData);
            } else {
                extractedData.structure.dataRows.push(rowData);
            }
            
            currentRow = [];
        }
    });
    
    // Extract calculation patterns
    extractedData.structure.dataRows.forEach(row => {
        Object.entries(row).forEach(([column, value]) => {
            // Detect monetary values
            if (value.match(/^-?\$?[\d,]+\\.\\d{2}$/) || value.match(/^-?[\d,]+\\.\\d{2}$/)) {
                extractedData.calculations.totals.push({
                    column: column,
                    value: parseFloat(value.replace(/[,$]/g, '')) || 0,
                    type: 'monetary'
                });
            }
            
            // Detect percentages
            if (value.match(/^-?\\d+\\.\\d+$/) && parseFloat(value) <= 100) {
                extractedData.calculations.percentages.push({
                    column: column,
                    value: parseFloat(value),
                    type: 'percentage'
                });
            }
        });
    });
    
    // Extract filters/parameters
    document.querySelectorAll('strong').forEach(strong => {
        const text = strong.textContent.trim();
        const nextElement = strong.nextElementSibling;
        if (nextElement) {
            const value = nextElement.textContent.trim();
            if (text.includes(':')) {
                const key = text.replace(':', '').toLowerCase().replace(/\\s+/g, '_');
                extractedData.structure.filters[key] = value;
            }
        }
    });
    
    return extractedData;
}
"""
