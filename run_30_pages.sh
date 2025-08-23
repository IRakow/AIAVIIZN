#!/bin/bash
# REAL MCP AUTOMATION - 30 PAGES
# This script coordinates with Claude to execute real MCP commands

echo "🚀 REAL AIVIIZN AUTOMATION - 30 PAGES"
echo "======================================"
echo ""
echo "This will process the first 30 AppFolio pages using:"
echo "• Real browser automation (playwright)"
echo "• Real database storage (supabase)" 
echo "• Real screenshot capture"
echo "• Real template generation"
echo ""

# List of first 30 URLs
URLS=(
    "https://celticprop.appfolio.com/buffered_reports/account_totals?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/balance_sheet?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/balance_sheet_comparative?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/balance_sheet_comparison?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/bank_account_activity?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/bank_account_association?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/cash_flow?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/twelve_month_cash_flow?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/cash_flow_comparison?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/cash_flow_detail?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/chart_of_accounts?customize=false"
    "https://celticprop.appfolio.com/buffered_reports/expense_distribution?customize=false"
    "https://celticprop.appfolio.com/buffered_reports/general_ledger?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/income_statement?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/twelve_month_income_statement?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/income_statement_comparative?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/income_statement_comparison?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/income_statement_date_range?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/loans?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/trial_balance?customize=false"
    "https://celticprop.appfolio.com/buffered_reports/trial_balance_by_property?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/trust_account_balance?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/trust_account_balance_detail?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/rent_roll?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/rent_roll_commercial?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/rent_roll_itemized?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/delinquency?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/delinquency_as_of?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/tenant_ledger?customize=true"
    "https://celticprop.appfolio.com/buffered_reports/property_performance?customize=true"
)

echo "📊 Found ${#URLS[@]} URLs to process"
echo ""

# Save URLs to file for Claude to process
echo "# FIRST 30 APPFOLIO URLS FOR AUTOMATION" > first_30_urls.txt
echo "# Generated: $(date)" >> first_30_urls.txt
echo "" >> first_30_urls.txt

for i in "${!URLS[@]}"; do
    page_num=$((i + 1))
    echo "# Page $page_num: ${URLS[$i]}" >> first_30_urls.txt
    echo "${URLS[$i]}" >> first_30_urls.txt
    echo "" >> first_30_urls.txt
done

echo "📝 URLs saved to: first_30_urls.txt"
echo ""
echo "🤖 NEXT STEP:"
echo "Tell Claude: 'Process the URLs in first_30_urls.txt using real MCP automation'"
echo ""
echo "Claude will then execute:"
echo "• playwright:browser_navigate for each URL"
echo "• playwright:browser_evaluate to extract calculations"  
echo "• playwright:browser_take_screenshot for each page"
echo "• supabase:execute_sql to store data"
echo "• filesystem:write_file to generate templates"
echo ""
echo "✋ STOPPING AT 30 PAGES EXACTLY"
