# FIELD MAPPING & DUPLICATE PREVENTION SYSTEM

## WHO DETERMINES WHAT FIELDS? 

### 1. **PYTHON CODE (Not AI) Determines:**
```python
company_id = self.get_aiviizn_company_id()  # Fixed company mapping
url = page_url                               # URL from browser
title = await self.page.title()              # Page title from browser
template_path = generated_path               # Path from URL structure
captured_at = datetime.now()                 # Timestamp
```

### 2. **BEAUTIFULSOUP Determines Content Structure:**
```python
def extract_main_content_real(self, page_data):
    # BeautifulSoup finds and extracts main content area
    # Removes headers, navigation, footers
    # Returns structured HTML
```

### 3. **GPT-4 Determines Calculations:**
```python
async def enhanced_gpt4_analysis(self, observations, api_data):
    # GPT-4 analyzes patterns and creates:
    # - name (function name)
    # - formula (mathematical expression)
    # - variables (input parameters)
    # - javascript (implementation)
```

### 4. **CLAUDE Synthesizes Final Structure:**
```python
async def synthesize_calculations_with_claude(self, found_calculations):
    # Claude takes all findings and creates final:
    # - Verified calculations
    # - Enhanced descriptions
    # - Production-ready JavaScript
```

## DUPLICATE PREVENTION SYSTEM (MUST ADD)

### CURRENT PROBLEMS:
❌ No check if page exists before inserting
❌ No check if calculation exists
❌ No unique constraints in database
❌ Same page processed multiple times = duplicates

### SOLUTION 1: Check Before Insert
```python
# Check if exists
existing = supabase.table('pages').select('id').eq('company_id', company_id).eq('url', url).execute()

if existing.data:
    # UPDATE instead of INSERT
    supabase.table('pages').update(data).eq('id', existing.data[0]['id']).execute()
else:
    # INSERT new record
    supabase.table('pages').insert(data).execute()
```

### SOLUTION 2: Database Unique Constraints
```sql
-- Add to your Supabase
ALTER TABLE pages 
ADD CONSTRAINT unique_company_url 
UNIQUE (company_id, url);

ALTER TABLE calculations
ADD CONSTRAINT unique_company_page_calc
UNIQUE (company_id, page_url, name);
```

### SOLUTION 3: Upsert Pattern
```python
# Use upsert (insert or update)
supabase.table('pages').upsert(
    page_record,
    on_conflict='company_id,url'  # If these match, update instead
).execute()
```

## FIELD MAPPING FLOW

```
1. Browser captures page
   ↓
2. Python extracts metadata (url, title, timestamp)
   ↓
3. BeautifulSoup extracts content structure
   ↓
4. GPT-4 analyzes calculations (if needed)
   ↓
5. Claude synthesizes final structure
   ↓
6. Python maps to database schema:
   {
     company_id: UUID (from get_aiviizn_company_id)
     url: TEXT (from browser)
     title: TEXT (from page)
     html_storage_path: TEXT (from Storage upload)
     calculations: JSONB (from GPT-4 + Claude)
     api_responses: JSONB (from intercepted APIs)
     captured_at: TIMESTAMP (from Python)
   }
   ↓
7. CHECK FOR DUPLICATES (missing!)
   ↓
8. Insert or Update in Supabase
```

## TO FIX IMMEDIATELY:

1. **Add unique constraint in Supabase:**
```sql
ALTER TABLE pages ADD CONSTRAINT unique_company_url UNIQUE (company_id, url);
```

2. **Replace store_in_supabase_real with the duplicate-prevention version**

3. **Add this to __init__ to track processed URLs in memory:**
```python
self.stored_urls = set()  # Track what we've stored this session
```

4. **Quick check before processing:**
```python
if url in self.stored_urls:
    print(f"  ⚠️ Already stored {url} this session")
    return
```

## WHO READS SUPABASE?

Currently: **NOBODY reads before writing!** 
- ❌ Claude doesn't read Supabase
- ❌ GPT-4 doesn't read Supabase  
- ❌ Python code doesn't check for existing records

Should be: **Python checks for duplicates**
- ✅ Check if page exists before inserting
- ✅ Check if calculations exist
- ✅ Update instead of insert when duplicate found
