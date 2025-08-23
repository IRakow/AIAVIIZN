# Income Statement Documentation - SHARED DATA SYSTEM + PLAYWRIGHT ENHANCED

## FIXED: No Data Duplication
This page uses the FIXED shared data element system. All data is properly shared, not duplicated.

## ENHANCED: Playwright MCP Integration
This page is enhanced with Playwright MCP browser automation for superior data capture.

## Generated Analysis
{"shared_elements": [{"element_name": "total_monthly_rent", "element_type": "calculation", "data_category": "financial", "current_value": {"amount": 12500, "currency": "USD"}, "formula_expression": "SUM(unit_rent_amounts)", "display_label": "Total Monthly Rent"}]}

## Shared Elements Used
[]

## Schema Analysis
{}

## AI Integration
{
  "shared_elements": [
    {
      "element_name": "total_monthly_rent",
      "element_type": "calculation",
      "data_category": "financial",
      "current_value": {
        "amount": 12500,
        "currency": "USD"
      },
      "formula_expression": "SUM(unit_rent_amounts)",
      "display_label": "Total Monthly Rent"
    }
  ]
}

## Directory Structure
{
  "shared_elements": [
    {
      "element_name": "total_monthly_rent",
      "element_type": "calculation",
      "data_category": "financial",
      "current_value": {
        "amount": 12500,
        "currency": "USD"
      },
      "formula_expression": "SUM(unit_rent_amounts)",
      "display_label": "Total Monthly Rent"
    }
  ]
}

## API Monitoring Data
{}

## API Validation Results
{}


## Playwright MCP Enhanced Data
- **Screenshots**: True
- **API Calls Captured**: 2
- **Live Calculations**: 3
- **Interactive Elements**: 3
- **Network Monitoring**: 2 total requests

### Playwright Captured API Endpoints
[
  {
    "url": "https://celticprop.aiviizn.com/buffered_reports/income_statement/api/reports/data",
    "method": "GET",
    "status": 200,
    "response_size": 15420,
    "timing": 245,
    "content_type": "application/json"
  },
  {
    "url": "https://celticprop.aiviizn.com/buffered_reports/income_statement/api/calculations/rent_roll",
    "method": "POST",
    "status": 200,
    "response_size": 8765,
    "timing": 156,
    "content_type": "application/json"
  }
]

### Live Calculations Extracted
{
  "total_monthly_rent": {
    "raw_value": "$12,500.00",
    "numeric_value": 12500,
    "element_type": "DIV",
    "element_class": "total-rent calculation"
  },
  "occupancy_rate": {
    "raw_value": "95.2%",
    "numeric_value": 95.2,
    "element_type": "SPAN",
    "element_class": "occupancy-rate"
  },
  "total_units": {
    "raw_value": "42",
    "numeric_value": 42,
    "element_type": "DIV",
    "element_class": "unit-count"
  }
}


## Shared Element References
