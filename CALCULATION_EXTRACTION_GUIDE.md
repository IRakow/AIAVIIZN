# Advanced Calculation Extraction for AIVIIZN Agent

## Overview
The AIVIIZN Real Agent now includes **5 advanced methods** to extract the ACTUAL calculations and formulas from AppFolio, not just the displayed numbers.

## New Features Added

### 1. 🔬 Reverse Engineering Calculations
**Method:** `reverse_engineer_calculations()`

- Changes input values and observes output changes
- Deduces mathematical relationships between inputs and outputs
- Identifies which fields trigger recalculations

### 2. 📊 Excel Formula Extraction
**Method:** `extract_excel_formulas()`

- Clicks "Export to Excel" buttons automatically
- Extracts ACTUAL formulas from Excel cells (not just values)
- Most accurate method when Excel export is available

### 3. 🎯 API Calculation Trigger Analysis
**Method:** `analyze_calculation_triggers()`

- Monitors network requests when buttons are clicked
- Identifies calculation endpoints (e.g., `/api/calculate/`)
- Captures request parameters for formula reconstruction

### 4. 💭 Source Code Formula Mining
**Method:** `extract_formula_comments()`

- Scans JavaScript comments for formula descriptions
- Finds calculation functions in page source
- Extracts data attributes containing formulas

### 5. 🔄 Pattern Deduction from Comparisons
**Method:** `deduce_formulas_from_patterns()`

- Changes date filters to get multiple data points
- Compares values across different time periods
- Identifies constants vs calculated values

## How It Works

The main method `extract_calculations_real()` now:

1. **Tries all 5 methods** to gather evidence
2. **Sends findings to Claude** for synthesis
3. **Verifies formulas with Wolfram Alpha** (optional)
4. **Generates JavaScript implementations** of formulas
5. **Stores everything in Supabase** for analysis

## Installation

```bash
# Install new dependencies
pip install wolframalpha openpyxl

# Or use requirements.txt
pip install -r requirements.txt
```

## Configuration

Add these to your `.env` file:

```env
# Existing keys
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
ANTHROPIC_API_KEY=your-anthropic-key

# New keys for calculation extraction
WOLFRAM_APP_ID=your-wolfram-alpha-app-id  # Optional but recommended
```

## Usage

Run the agent as normal:

```bash
python aiviizn_real_agent.py
```

The agent will automatically:
- Try to find Excel export buttons
- Monitor API calls
- Test input changes
- Extract all possible formulas

## Example Output

When successful, you'll see calculations like:

```javascript
// Extracted from Excel: =SUM(B2:B50)
async function calculateRentRoll() {
    const { data } = await supabase
        .from('units')
        .select('rent');
    return data.reduce((sum, unit) => sum + unit.rent, 0);
}

// Deduced from pattern analysis
function calculateOccupancyRate(occupied, total) {
    return total > 0 ? (occupied / total * 100).toFixed(2) : 0;
}

// Found in source code
// Formula: late_fee = rent * 0.05 after 5 days
function calculateLateFee(rent, daysLate) {
    return daysLate > 5 ? rent * 0.05 : 0;
}
```

## Database Storage

Extracted formulas are stored in Supabase:

### `api_responses` table
```sql
CREATE TABLE api_responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    page_url TEXT,
    endpoint TEXT,
    response_data JSONB,
    extracted_formulas JSONB,
    captured_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `calculations` table
- Stores verified formulas
- Includes JavaScript implementations
- Links to source pages
- Tracks verification status

## Best Practices

1. **Excel Export First**: Always look for Excel export - it has the most accurate formulas
2. **Multiple Methods**: Use multiple extraction methods for validation
3. **Test Different Pages**: Similar pages (different months) help identify patterns
4. **Save API Responses**: Store all API data for later analysis

## Troubleshooting

### Excel Export Not Working
- Ensure `openpyxl` is installed
- Check if export button exists on page
- Some exports may be CSV, not Excel

### No Calculations Found
- Page might calculate server-side only
- Try changing date ranges
- Look for "Calculate" or "Update" buttons

### Wolfram Verification Fails
- Wolfram is optional
- Complex formulas may not verify
- Focus on Excel/API methods instead

## Results

With these methods, you can now extract:
- ✅ Exact formulas (not just displayed values)
- ✅ Calculation relationships
- ✅ API endpoint parameters
- ✅ Hidden calculations in JavaScript
- ✅ Excel formulas from exports

This gives you the COMPLETE calculation logic from AppFolio, not just the final numbers!
