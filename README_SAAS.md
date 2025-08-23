# AIVIIZN Multi-Tenant SaaS Agent

## 🚀 What's New - Complete Multi-Tenant Architecture

This is a **complete refactor** of the AIVIIZN agent to support multiple property management companies as a true SaaS platform.

### Key Features

1. **Multi-Company Support**: Each company has isolated data
2. **Intelligent Field Mapping**: Automatically identifies and maps fields like tenant names, unit numbers, rent amounts, etc.
3. **Entity Extraction**: Captures and stores actual tenants, units, properties, payments, etc.
4. **Learning System**: Improves field recognition over time across all companies
5. **Company-Specific Templates**: Each company gets their own customized templates
6. **Complete Data Isolation**: Row-level security ensures companies never see each other's data

## 📊 New Database Structure

The system now uses a proper multi-tenant architecture with these tables:

- **companies**: Core tenant table for each property management company
- **field_mappings**: How each company's fields map to our standard fields
- **captured_pages**: Page content with company isolation
- **captured_entities**: Actual tenants, units, properties extracted from pages
- **company_calculations**: Formulas and calculations per company
- **company_templates**: Generated templates per company
- **field_patterns**: Machine learning patterns that improve over time

## 🔧 Setup Instructions

### 1. Database Setup

```bash
# 1. Go to your Supabase dashboard
# 2. Navigate to SQL Editor
# 3. Copy and run the entire contents of: database_setup.sql
# 4. (Optional) If you have existing data, also run: database_migration.sql
```

### 2. Environment Variables

Make sure your `.env` file has:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
SUPABASE_KEY=your_anon_key
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_gpt4_key  # For intelligent field analysis
```

### 3. Run the New Agent

```bash
python aiviizn_real_agent_saas.py
```

## 🎯 How It Works

### Field Recognition System

The agent now intelligently identifies what each field means:

```python
# Examples of automatic field recognition:
"Tenant Name" → tenant_name (95% confidence)
"Monthly Rent" → rent_amount (95% confidence) 
"Unit #" → unit_number (90% confidence)
"Lease Start Date" → lease_start (90% confidence)
```

### Entity Extraction

When processing a page with a tenant list, the system:
1. Identifies it's a tenant table
2. Maps each column to standard fields
3. Extracts each row as a tenant entity
4. Stores with company isolation

### Company Onboarding Flow

1. **Create Company Profile**
   - Company name
   - Domain
   - Base URL

2. **Initial Capture**
   - Agent captures pages
   - Automatically identifies fields
   - Extracts entities

3. **Field Verification** (Optional)
   - Review auto-detected fields
   - Correct any misidentifications
   - System learns from corrections

4. **Template Generation**
   - Creates company-specific templates
   - Uses their field mappings
   - Maintains their calculations

## 📦 What Gets Captured

For each company, the system captures:

### 1. Field Mappings
- Source field name (what they call it)
- Field type (our standard type)
- Confidence score
- CSS selector for finding it
- Sample values

### 2. Entities
- **Tenants**: Names, emails, phones, lease info
- **Units**: Numbers, types, bedrooms, rent amounts
- **Properties**: Names, addresses, details
- **Payments**: Amounts, dates, statuses
- **Leases**: Start/end dates, terms

### 3. Calculations
- All formulas found
- JavaScript implementations
- API endpoints
- Confidence levels

## 🔐 Security & Isolation

- **Complete data isolation** between companies
- **Row-level security** in database
- **Company-specific directories** for templates
- **Encrypted sensitive data** (when configured)
- **No data mixing** between tenants

## 🎨 Template System

Each company gets templates that:
- Use their specific field mappings
- Include their calculations
- Maintain their branding (replaced with AIVIIZN)
- Load their isolated data

## 📈 Learning System

The system improves over time:
1. Each field identification increases pattern confidence
2. Patterns shared across companies (anonymized)
3. Higher accuracy with more companies
4. Manual corrections improve future detection

## 🛠️ Troubleshooting

### If field detection is wrong:
- The system stores confidence scores
- Low confidence fields can be manually verified
- Corrections improve future detection

### If entities aren't extracted:
- Check the entity type detection in `determine_entity_type()`
- Verify table headers match expected patterns
- Review field mappings for that page

### If calculations are missing:
- All original calculation methods preserved
- GPT-4 analysis still works
- Check API response capture

## 📚 API Usage

### Get company data:
```javascript
const { data: entities } = await supabase
    .from('captured_entities')
    .select('*')
    .eq('company_id', companyId)
    .eq('entity_type', 'tenant');
```

### Get field mappings:
```javascript
const { data: mappings } = await supabase
    .from('field_mappings')
    .select('*')
    .eq('company_id', companyId)
    .eq('page_url', currentUrl);
```

## 🚦 Migration from Old System

If you have existing data:
1. Run `database_migration.sql` after setup
2. Old data moved to a "Migrated" company
3. All pages and calculations preserved
4. Can be re-processed with field mapping

## ✨ Benefits of New Architecture

1. **Scalable**: Add unlimited companies
2. **Intelligent**: Learns field patterns
3. **Secure**: Complete data isolation
4. **Maintainable**: Clean separation of concerns
5. **Reusable**: Templates work across similar systems
6. **Future-proof**: Ready for SaaS deployment

## 📞 Support

For issues or questions:
- Check the logs in `/Users/ianrakow/Desktop/AIVIIZN/agent.log`
- Review field mappings in database
- Verify company_id is set correctly
- Ensure all environment variables are set

## 🔄 Next Steps

1. **Add Authentication**: Implement proper user auth
2. **Add API Endpoints**: RESTful API for data access
3. **Add Admin Dashboard**: Manage companies and mappings
4. **Add Billing**: Subscription management
5. **Add White-labeling**: Custom branding per company

---

**Note**: This is a complete rewrite. All original functionality is preserved, but the data model is completely different. Make sure to backup any existing data before migrating.
