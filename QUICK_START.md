## 🚀 QUICK START - TERMINAL COMMANDS

Run these commands in your terminal to start the agent:

```bash
# Navigate to project
cd /Users/ianrakow/Desktop/AIVIIZN

# Make the script executable (only needed once)
chmod +x start_agent.sh

# Run the agent
./start_agent.sh
```

Or run directly with Python:

```bash
cd /Users/ianrakow/Desktop/AIVIIZN
python3 aiviizn_terminal_agent.py
```

## 📋 WHAT HAPPENS:

1. **Agent starts** and connects to Supabase
2. **Navigates** to https://celticprop.appfolio.com/reports using Playwright
3. **Captures** the complete page structure
4. **Extracts** all formulas and calculations
5. **Sends to Claude Opus** to perfect the math
6. **Generates beautiful template** at /templates/reports/index.html
7. **Stores normalized data** in Supabase (no duplicates)
8. **Shows next page** to process

## ⚡ IMPORTANT:

- The agent creates **FULLY OPERATIONAL** pages, not basic templates
- Every calculation works with **REAL MATH**
- Pages are **ABSOLUTELY BEAUTIFUL** with animations and modern UI
- Data is **NORMALIZED** - stored once, referenced everywhere
- Everything is **PRODUCTION-READY**

## 🎯 FIRST PAGE:

The agent will start with:
- **Source**: https://celticprop.appfolio.com/reports  
- **Target**: /templates/reports/index.html

Then it will discover and queue all linked pages for processing.

## 💡 TIPS:

- Process one page at a time for best results
- Each page gets its own dedicated analysis
- The agent will show you discovered links after each page
- You can quit anytime with 'q' and resume later

## 🔥 START NOW:

```bash
./start_agent.sh
```
