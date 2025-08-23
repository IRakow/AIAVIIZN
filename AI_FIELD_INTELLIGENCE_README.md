# AI-Powered Field Intelligence Integration

## Overview

The AIVIIZN agent now includes **AI-powered field intelligence** that can:
- **Name ANY field intelligently**, even cryptic ones like "field_123" or "x1"
- **Identify semantic types** with high confidence
- **Map calculation variables** to their source fields
- **Detect data types and units** automatically
- **Understand field relationships** and dependencies

## Architecture

```
┌─────────────────────────────────────┐
│   aiviizn_real_agent_with_ai.py    │ ← Main Agent
│  (Enhanced with AI Intelligence)    │
└──────────────┬──────────────────────┘
               │
               ├── Imports & Uses
               ▼
┌─────────────────────────────────────┐
│   enhanced_field_intelligence.py    │ ← AI Module
│  (EnhancedFieldMapper)              │
│  (CalculationVariableMapper)        │
└─────────────────────────────────────┘
```

## Key Components

### 1. **EnhancedFieldMapper** (AI Module)
- Uses Claude/GPT to analyze fields semantically
- Generates descriptive names for cryptic fields
- Identifies data types (currency, percentage, date, etc.)
- Detects units of measure (dollars, days, sqft, etc.)
- Determines if fields are calculated
- Provides confidence scores

### 2. **CalculationVariableMapper** (AI Module)
- Maps calculation formulas to source fields
- Identifies formula types (sum, ratio, percentage, etc.)
- Extracts variables from formulas
- Links variables to actual form fields

### 3. **Main Agent Integration**
- Falls back to pattern matching if AI fails
- Stores AI-generated names in database
- Tracks statistics on AI performance
- Beautiful templates with AI insights

## How It Works

### Field Analysis Flow

1. **Field Discovery**
   ```
   Form Field Found → "field_abc_123"
   ```

2. **AI Analysis**
   ```python
   # Agent sends to AI with context
   field_intelligence = await enhanced_field_mapper.analyze_field_intelligently(
       field_name="field_abc_123",
       field_attributes={...},
       page_context="Property management rent roll...",
       surrounding_fields=["tenant_name", "unit_number", ...]
   )
   ```

3. **AI Response**
   ```json
   {
       "semantic_type": "monthly_rent",
       "ai_generated_name": "Monthly Rent Amount",
       "data_type": "currency",
       "unit_of_measure": "dollars",
       "is_calculated": false,
       "confidence": 0.92
   }
   ```

4. **Storage & Display**
   - Original name kept for form submission
   - AI name shown to users
   - Both stored in database

## Database Schema Updates

The `field_mappings` table now includes:

```sql
ai_generated_name VARCHAR(255)     -- AI's descriptive name
data_type VARCHAR(50)              -- currency, percentage, date, etc.
unit_of_measure VARCHAR(50)        -- dollars, percent, days, etc.
is_calculated BOOLEAN              -- Is this a calculated field?
calculation_formula TEXT           -- Formula if calculated
related_fields JSONB              -- Related field names
context_clues JSONB               -- AI's reasoning
```

## Running the System

### Quick Start
```bash
# Make executable
chmod +x run_ai_agent.sh

# Run
./run_ai_agent.sh
```

### Or directly with Python
```bash
python3 run_ai_agent.py
```

## Features in Action

### 1. Cryptic Field Naming
**Before:** `field_123`, `x1`, `val_a`  
**After:** `Monthly Rent Amount`, `Unit Number`, `Security Deposit`

### 2. Calculation Detection
Automatically identifies:
- Total fields (sum of other fields)
- Percentage calculations
- Date calculations (lease duration)
- Financial ratios

### 3. Data Type Recognition
- **Currency fields** → number inputs with step="0.01"
- **Date fields** → date pickers
- **Boolean fields** → checkboxes
- **Percentage fields** → labeled with %

## Statistics Tracking

The system tracks:
- **Fields Identified**: Total fields found
- **Fields AI-Named**: Fields given better names by AI
- **Calculations Mapped**: Formulas with mapped variables
- **AI Naming Rate**: Percentage successfully renamed

## Example Output

```
🧠 AI-IDENTIFIED FIELDS:
══════════════════════════════════════

✨ AI-NAMED FIELDS:
  • field_123 → Monthly Rent Amount (rent_amount)
  • x1 → Unit Square Footage (unit_size)
  • calc_a → Total Monthly Payment (calculated)

📊 CALCULATED FIELDS:
  • Total Monthly Payment
    Formula: base_rent + utilities + fees

📈 BY DATA TYPE:
  • currency: 15 fields
  • date: 8 fields
  • percentage: 3 fields
  • text: 22 fields
```

## Benefits

1. **No More Cryptic Names**: Every field gets a meaningful name
2. **Automatic Documentation**: AI explains what each field does
3. **Better Data Quality**: Correct data types and validation
4. **Calculation Understanding**: Know how values are computed
5. **Reduced Errors**: AI catches field purposes humans might miss

## Fallback Mechanism

If AI analysis fails, the system:
1. Falls back to pattern-based detection
2. Uses HTML attributes (type, placeholder)
3. Keeps original field name
4. Logs the failure for review

## Configuration

Set these environment variables:
```bash
ANTHROPIC_API_KEY=your_claude_key    # Required
OPENAI_API_KEY=your_openai_key      # Optional but recommended
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
```

## Performance

- **AI Analysis**: ~1-2 seconds per form
- **Caching**: Results stored to avoid re-analysis
- **Batch Processing**: Multiple fields analyzed together
- **Smart Skipping**: Duplicate fields not re-analyzed

## Future Enhancements

- [ ] Multi-language field naming
- [ ] Industry-specific terminology
- [ ] Custom field naming rules
- [ ] Validation rule generation
- [ ] Auto-generate field documentation
- [ ] Machine learning from corrections

## Troubleshooting

### AI naming not working?
- Check API keys are set
- Verify internet connection
- Check API rate limits

### Fields not being renamed?
- Look for "AI NAMED" badge in templates
- Check `ai_field_mappings.json` in data folder
- Review agent.log for errors

### Calculations not detected?
- Ensure fields have proper attributes
- Check if marked as readonly/disabled
- Review calculation patterns in module

## Support

For issues or questions:
1. Check `agent.log` for detailed errors
2. Review `data/statistics.json` for metrics
3. Examine `data/ai_field_mappings.json` for mappings

---

**Version**: 1.0.0  
**Last Updated**: August 2025  
**Status**: Production Ready with AI Intelligence
