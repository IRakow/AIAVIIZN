# AIVIIZN EXACT PAGE REPLICATOR

## 🎯 **WHAT THIS DOES**

This terminal agent creates pages that:

1. **KEEP YOUR LAYOUT** - Uses YOUR `/templates/base.html` exactly
   - Your sidebar stays
   - Your navigation stays
   - Your header/footer stays
   - Your color scheme stays

2. **COPY APPFOLIO'S EXACT MAIN CONTENT** - The middle part is EXACTLY like AppFolio
   - Same forms
   - Same tables
   - Same buttons
   - Same calculations
   - Same functionality

3. **FULLY FUNCTIONAL WITH SUPABASE** - Everything actually works
   - Forms submit to Supabase
   - Tables load from Supabase
   - Calculations use real data
   - Updates in real-time

## 📋 **HOW IT WORKS**

```
YOUR BASE.HTML                    +                    APPFOLIO MAIN CONTENT
┌─────────────────────┐                               ┌──────────────────┐
│ AIVIIZN Header      │                               │                  │
├─────────────────────┤                               │   Reports Page   │
│ Your    │           │           COMBINED            │   Exact Forms    │
│ Sidebar │  [MAIN]   │  ━━━━━━━━━━━━━━━━━━━━━>     │   Exact Tables   │
│ Menu    │           │                               │   Exact Calcs    │
│         │           │                               │                  │
└─────────────────────┘                               └──────────────────┘
     Your Layout                                        AppFolio's Content
```

## 🚀 **RUN THE AGENT**

```bash
cd /Users/ianrakow/Desktop/AIVIIZN
python3 aiviizn_terminal_agent.py
```

## 📊 **WHAT HAPPENS**

```
╔══════════════════════════════════════════════════════════════╗
║              EXACT PAGE REPLICATION SYSTEM                  ║
║      Your Layout + AppFolio's Exact Functionality           ║
╚══════════════════════════════════════════════════════════════╝

🎯 Starting URL: https://celticprop.appfolio.com/reports
📁 Will create: /templates/reports/index.html
🎨 Using YOUR base.html + EXACT AppFolio content

[1/7] 🌐 CAPTURING: AppFolio page structure...
  → Navigating to AppFolio page...
  → Capturing complete HTML...
  → Extracting all forms and tables...
  ✓ Page captured completely

[2/7] 📦 EXTRACTING: Main content area only...
  → Identifying main content area...
  → Removing AppFolio navigation...
  → Preserving all calculations...
  ✓ Main content extracted

[3/7] 🧮 FORMULAS: Extracting calculations...
  ✓ Calculations perfected by Claude Opus
  ✓ Formulas validated
  ✓ Supabase integration ready

[4/7] 💾 DATABASE: Mapping to normalized structure...
  → Found existing: John Smith (id: 42)
  ✓ Data normalized - zero duplicates

[5/7] 🎨 TEMPLATE: Creating with your base.html...
  ✓ Template created with YOUR base.html
  ✓ EXACT AppFolio content preserved
  ✓ All functionality operational

[6/7] 🔌 SUPABASE: Wiring up functionality...
  ✓ All functionality connected to Supabase

[7/7] 🔗 LINKS: Finding new pages...
  ✓ Found 10 new pages to process

✨ PAGE REPLICATED EXACTLY ✨
📁 Template: /templates/reports/index.html
🎨 Your layout: ✓ Preserved
📦 AppFolio content: ✓ Exact copy
⚡ Functionality: ✓ Fully operational
💾 Supabase: ✓ Connected
```

## 📁 **GENERATED TEMPLATE STRUCTURE**

```django
{% extends "base.html" %}  <!-- YOUR BASE.HTML -->

{% block content %}
<!-- EXACT APPFOLIO MAIN CONTENT HERE -->
<div class="appfolio-content">
    <!-- Exact forms from AppFolio -->
    <!-- Exact tables from AppFolio -->
    <!-- Exact calculations from AppFolio -->
    <!-- But connected to YOUR Supabase -->
</div>
{% endblock %}
```

## 💾 **NORMALIZED DATABASE**

Data is stored ONCE and referenced everywhere:

```sql
-- Person "John Smith" exists ONCE
tenants (id: 42, name: "John Smith")

-- Referenced everywhere by ID
leases (tenant_id: 42)
payments (tenant_id: 42)
maintenance_requests (tenant_id: 42)
```

## ⚡ **KEY FEATURES**

### **YOUR Layout Preserved:**
- ✅ Your sidebar navigation
- ✅ Your header/branding
- ✅ Your color scheme
- ✅ Your base.html structure

### **EXACT AppFolio Functionality:**
- ✅ Same forms and fields
- ✅ Same table structures
- ✅ Same calculations
- ✅ Same button actions
- ✅ Same data flow

### **Fully Operational:**
- ✅ Forms submit to Supabase
- ✅ Tables load real data
- ✅ Calculations work perfectly
- ✅ Real-time updates
- ✅ All features functional

## 🎯 **IMPORTANT NOTES**

1. **NO APPFOLIO BRANDING** - Everything says AIVIIZN
2. **NO CELTIC REFERENCES** - All removed
3. **YOUR LAYOUT** - base.html preserved exactly
4. **THEIR FUNCTIONALITY** - Main content exact copy
5. **FULLY WORKING** - Not templates, but operational pages

## 🔧 **REQUIREMENTS**

- Python 3
- Playwright MCP configured
- Supabase MCP configured
- Anthropic API key in .env

## 📝 **URL MAPPING**

```
AppFolio URL                    →  Your Template
/reports                        →  /templates/reports/index.html
/reports/rent_roll              →  /templates/reports/rent_roll.html
/reports/income_statement       →  /templates/reports/income_statement.html
/maintenance/work_orders        →  /templates/maintenance/work_orders.html
/leasing/applications          →  /templates/leasing/applications.html
```

## 🚀 **START NOW**

```bash
cd /Users/ianrakow/Desktop/AIVIIZN
python3 aiviizn_terminal_agent.py
```

The agent will:
1. Start with /reports page
2. Keep YOUR base.html layout
3. Copy EXACT AppFolio main content
4. Make everything work with Supabase
5. Queue next page for processing
