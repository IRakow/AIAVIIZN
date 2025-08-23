# 🎯 APPFOLIO PIXEL-PERFECT REPLICATOR

**Complete terminal application for exact AppFolio replication with multi-AI validation**

## 🚀 Features

### ✅ Complete Browser Automation
- **Playwright integration** for real browser control
- **Manual authentication** support with wait detection
- **Network request monitoring** for API analysis
- **Full page screenshots** and accessibility extraction

### ✅ Multi-AI Validation System
- **OpenAI GPT-4**: Mathematical accuracy verification
- **Google Gemini**: Business logic validation  
- **Wolfram Alpha**: Mathematical proof verification
- **Claude Desktop**: Integration and implementation analysis
- **Consensus threshold**: 1% tolerance for numerical differences

### ✅ Pixel-Perfect Template Generation
- **Extends your existing base.html** framework
- **Uses your CSS classes** and Bootstrap structure
- **Follows AppFolio naming** conventions exactly
- **Complete JavaScript calculations** with Supabase integration
- **Database schema generation** with safety validation

### ✅ Complete File Management
- **Organized directory structure** mirroring AppFolio
- **Template, JavaScript, CSS, SQL** file generation
- **Documentation and validation** results
- **Error handling** with immediate stops

## 📦 Installation

### 1. Setup (First Time Only)
```bash
# Make setup script executable
chmod +x make_executable.sh
./make_executable.sh

# Run setup
./setup_replicator.sh
```

### 2. Configure API Keys
Add to your `.env` file:
```bash
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here  
WOLFRAM_APP_ID=your_wolfram_app_id_here
```

## 🚀 Usage

### Quick Start
```bash
./start_replicator.sh
```

### Manual Start
```bash
python3 appfolio_pixel_perfect_replicator.py
```

## 🔄 Process Flow

### 1. **Browser Initialization**
- Opens Chromium browser (visible for authentication)
- Navigates to AppFolio reports page
- Waits for manual authentication

### 2. **Page Analysis** 
- Extracts complete HTML structure
- Captures all buttons, forms, tables, calculations
- Takes full-page screenshots
- Documents navigation and relationships

### 3. **Multi-AI Validation**
- **OpenAI**: Verifies mathematical accuracy
- **Gemini**: Validates business logic and edge cases
- **Wolfram**: Provides mathematical proof verification  
- **Claude**: Analyzes integration and implementation
- **Consensus**: Requires 3/4 AI agreement to proceed

### 4. **Template Generation**
- Creates pixel-perfect HTML templates
- Generates matching JavaScript calculations
- Produces database schemas
- Saves comprehensive documentation

### 5. **File Organization**
```
templates/
├── reports/
│   ├── accounting/
│   │   ├── income_statement.html
│   │   ├── balance_sheet.html
│   │   └── cash_flow.html
│   ├── property/
│   │   ├── rent_roll.html
│   │   └── vacancy_report.html
│   └── tenant/
│       ├── delinquency.html
│       └── tenant_ledger.html

static/js/reports/
├── income_statement_calculations.js
├── rent_roll_calculations.js
└── delinquency_calculations.js

docs/reports/
├── income_statement_schema.sql
├── rent_roll_validation.json
└── comprehensive_report.json
```

## ⚠️ Critical Features

### **Error Handling**
- **Immediate stops** on consensus failure
- **Manual review flags** for discrepancies
- **Comprehensive logging** to `appfolio_replication.log`
- **State preservation** for resume capability

### **Quality Assurance**
- **Mathematical consensus** (1% tolerance threshold)
- **Business logic validation** across all AIs
- **Schema safety checks** before database writes
- **Template integration** with existing AIVIIZN framework

### **Performance**
- **Parallel AI validation** for speed
- **Incremental link discovery** (not all at once)
- **Efficient file organization** 
- **Progress tracking** with detailed reporting

## 📊 Output

### **Generated Files**
- **HTML Templates**: Exact AppFolio replicas using your framework
- **JavaScript**: Complete calculation implementations
- **SQL Schemas**: Database structures for all data
- **Documentation**: Validation results and analysis
- **Screenshots**: Visual references for each page

### **Validation Reports**
- **Multi-AI consensus analysis**
- **Mathematical verification results**
- **Business logic compliance scores**
- **Integration recommendations**
- **Performance considerations**

## 🛡️ Safety Features

### **Consensus Requirements**
- Minimum 3/4 AI systems must agree
- Mathematical accuracy within 1% tolerance
- Business logic validation mandatory
- Implementation feasibility confirmed

### **Database Protection**
- Schema validation before execution
- SQL syntax verification
- Conflict detection with existing tables
- Rollback capability planning

### **Error Prevention**
- Immediate stop on validation failure
- Manual review requirements for discrepancies
- Comprehensive error logging
- State preservation for debugging

## 📈 Progress Tracking

The system provides real-time feedback:
```
🎯 PROCESSING PAGE 3: Income Statement
📍 URL: https://celticprop.appfolio.com/buffered_reports/income_statement
🏷️  Category: Accounting Reports
🎯 Priority: HIGH
================================================================================
📄 Step 1: Extracting complete page structure...
✅ Extracted 47 links, 23 buttons, 5 forms, 3 tables
🔗 Step 2: Discovering new links...
🤖 Step 3: Running multi-AI validation...
✅ COMPLETED: Income Statement
📊 Progress: 3 pages processed
🔗 New links: 12
💾 Files saved: 4
```

## 🎯 Success Metrics

- **Pixel-perfect visual accuracy**
- **Mathematical consensus achievement**
- **Complete functional replication**
- **Database schema compatibility**
- **Integration with AIVIIZN framework**

---

**Ready to create exact AppFolio replicas with multi-AI validation!**

Run `./start_replicator.sh` to begin the pixel-perfect replication process.
