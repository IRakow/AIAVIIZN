# AIVIIZN Installation & Troubleshooting Guide

## Quick Start (Recommended)

```bash
# Run the automated setup
python3 quickstart.py

# Diagnose any issues
python3 diagnose_setup.py

# Run the agent
python3 aiviizn_real_agent.py
```

## Manual Installation

### Step 1: Install Dependencies

Due to version conflicts, install packages individually:

```bash
# Core packages (install these first)
pip3 install --upgrade playwright
pip3 install --upgrade anthropic
pip3 install --upgrade supabase
pip3 install --upgrade beautifulsoup4
pip3 install --upgrade python-dotenv

# Additional packages for calculation extraction
pip3 install --upgrade wolframalpha
pip3 install --upgrade openpyxl

# Install Playwright browser
python3 -m playwright install chromium
```

### Step 2: Configure Environment

Create a `.env` file with your API keys:

```bash
# Copy the template
cp .env.example .env

# Edit with your actual keys
nano .env  # or use any text editor
```

Required keys:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Anon/public key from Supabase
- `SUPABASE_SERVICE_KEY` - Service role key from Supabase
- `ANTHROPIC_API_KEY` - Claude API key
- `WOLFRAM_APP_ID` - (Optional) Wolfram Alpha API

## Troubleshooting

### Dependency Conflicts

If you see:
```
ERROR: Cannot install postgrest==0.16.8 and supabase==2.0.2
```

**Solution:** The requirements.txt has been updated. Use:
```bash
pip3 install --upgrade supabase
# This will install compatible versions of all supabase dependencies
```

### Playwright Browser Issues

If you see:
```
playwright._impl._errors.TargetClosedError: Target page, context or browser has been closed
```

**Solutions:**
1. Reinstall the browser:
   ```bash
   python3 -m playwright install chromium --force
   ```

2. Check browser is working:
   ```bash
   python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=False); input('Press Enter to close...'); b.close(); p.stop()"
   ```

3. Make sure you don't close the browser window while the agent is running

### pip vs pip3

If `pip` command not found, use `pip3`:
```bash
# Instead of: pip install package
# Use: pip3 install package

# Or create an alias
alias pip=pip3
```

### Environment Variables Not Loading

If API keys aren't being read:
1. Check `.env` file exists in the project root
2. Verify format (no spaces around `=`):
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJI...
   ```
3. Test loading:
   ```python
   from dotenv import load_dotenv
   import os
   load_dotenv()
   print(os.getenv('SUPABASE_URL'))
   ```

### Supabase Connection Issues

If Supabase connection fails:
1. Verify your keys are correct
2. Check if tables exist in Supabase:
   - `pages`
   - `calculations`
   - `api_responses`
3. Create tables using SQL Editor in Supabase Dashboard

### Missing openpyxl Warning

If you see:
```
⚠️ openpyxl not installed - Excel formula extraction disabled
```

**Solution:**
```bash
pip3 install openpyxl
```

This is optional but recommended for extracting formulas from Excel exports.

## Verification Steps

Run the diagnostic script to check everything:

```bash
python3 diagnose_setup.py
```

You should see:
- ✅ All dependencies installed
- ✅ Environment variables set
- ✅ Playwright browser working
- ✅ Project directories exist

## Running the Agent

Once everything is installed:

```bash
python3 aiviizn_real_agent.py
```

1. Browser window will open
2. Log into AppFolio manually
3. Navigate to any page you want to extract
4. Press Enter in terminal to start extraction
5. Agent will extract calculations using all 5 methods

## Advanced Calculation Extraction

The agent now uses 5 methods to extract formulas:
1. **Excel Export** - Most accurate if available
2. **Reverse Engineering** - Changes inputs, observes outputs
3. **API Monitoring** - Captures calculation endpoints
4. **Source Mining** - Finds formulas in JavaScript
5. **Pattern Analysis** - Compares across time periods

All methods run automatically and results are synthesized by Claude.

## Getting Help

If issues persist:
1. Check `agent.log` for detailed errors
2. Run `python3 diagnose_setup.py` for system check
3. Ensure you're using Python 3.8 or higher
4. Try the individual dependency installer: `python3 fix_dependencies.py`

## Success Indicators

When working correctly, you'll see:
- Browser opens and stays open
- "✓ Page captured with X API responses"
- "✓ Excel formulas extracted: X sheets" (if Excel export available)
- "✓ Reverse engineered: X relationships"
- "✓ Claude synthesized X definitive calculations"
- Beautiful templates created in `/templates` directory
