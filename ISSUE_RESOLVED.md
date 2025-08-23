# ✅ RESOLVED: Installation Issues

## The Problem
You encountered two issues:
1. **Dependency conflict**: `postgrest==0.16.8` conflicts with `supabase==2.0.2`
2. **Playwright error**: Browser closing unexpectedly

## Quick Fix

Run these commands in order:

```bash
# 1. Use the simple requirements file (no version conflicts)
pip3 install -r requirements-simple.txt

# 2. Install Playwright browser
python3 -m playwright install chromium

# 3. Test Playwright is working
python3 test_playwright.py

# 4. Run diagnostics
python3 diagnose_setup.py

# 5. If all tests pass, run the agent
python3 aiviizn_real_agent.py
```

## Alternative: Automated Setup

```bash
# Run the quickstart script which handles everything
python3 quickstart.py
```

## What Was Fixed

### 1. Dependency Conflict Resolution
- **Removed** explicit `postgrest` and `realtime` versions from requirements.txt
- Let `supabase` package install its own compatible dependencies
- Created `requirements-simple.txt` without version pinning

### 2. Browser Stability
- Added better error handling in the agent
- Created test script to verify Playwright setup
- Ensures browser stays open during extraction

### 3. New Helper Scripts
- `quickstart.py` - Automated setup
- `diagnose_setup.py` - Check all dependencies
- `test_playwright.py` - Test browser functionality
- `fix_dependencies.py` - Install packages one by one

## Verification Checklist

After installation, verify:

- [ ] No pip installation errors
- [ ] `python3 test_playwright.py` opens a browser successfully
- [ ] `python3 diagnose_setup.py` shows all green checkmarks
- [ ] `.env` file has your API keys

## The 5 New Calculation Extraction Methods

Your agent now includes:

1. **Excel Formula Extraction** - Intercepts Excel downloads
2. **Reverse Engineering** - Changes inputs, observes outputs  
3. **API Monitoring** - Captures calculation endpoints
4. **Source Code Mining** - Finds formulas in JavaScript
5. **Pattern Analysis** - Compares data across time periods

All methods run automatically when you process a page!

## Running the Enhanced Agent

```bash
python3 aiviizn_real_agent.py
```

The agent will:
1. Open browser window (don't close it!)
2. Wait for you to log into AppFolio
3. You navigate to any page
4. Press Enter to start extraction
5. **Automatically tries all 5 methods** to extract formulas
6. Synthesizes results with Claude
7. Stores everything in Supabase

## Expected Output

When working correctly, you'll see:
```
📊 Excel formulas extracted: 3 sheets
✓ Found formula in Sheet1!A5: =SUM(B2:B50)
✓ Reverse engineered: 5 relationships
✓ API triggers found: 3 endpoints
✓ Source code formulas: 7 hints
✓ Pattern formulas: 4 deduced
✓ Claude synthesized 8 definitive calculations
```

## If Issues Persist

1. Check Python version (need 3.8+):
   ```bash
   python3 --version
   ```

2. Clear pip cache and reinstall:
   ```bash
   pip3 cache purge
   pip3 install --upgrade pip
   pip3 install -r requirements-simple.txt
   ```

3. Check browser installation:
   ```bash
   python3 -m playwright install --help
   python3 -m playwright install chromium --force
   ```

## Success! 🎉

You now have the MOST ADVANCED calculation extraction system that:
- Extracts ACTUAL formulas (not just displayed values)
- Uses 5 different methods for accuracy
- Synthesizes with AI for best results
- Stores everything in your database

The formulas you extract will be the REAL calculations, like:
- `=SUM(B2:B50)*1.05` (from Excel)
- `total = rent * (1 + late_fee_rate)` (from reverse engineering)
- `/api/calculate/rent_roll` (from API monitoring)
