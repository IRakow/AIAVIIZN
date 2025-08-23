# AIVIIZN Terminal Agent - AppFolio Replicator

A sophisticated terminal agent that systematically copies AppFolio functionality to your AIVIIZN property management system.

## 🚀 Quick Start

1. **Setup** (one time):
   ```bash
   ./setup.sh  # Already completed!
   ```

2. **Configure** your `.env` file with API keys

3. **Start** the agent:
   ```bash
   ./start_mcp.sh  # MCP version (RECOMMENDED)
   ./start.sh      # Standalone version
   ```

## 🎯 What It Does

- **🌐 Persistent Browser**: Opens once, stays open entire session
- **📄 Page Processing**: Systematically processes AppFolio pages one by one
- **🧮 Math Extraction**: Captures and validates all calculations
- **🎨 Design Replication**: Copies exact look and feel
- **🗄️ Database Storage**: Stores everything in Supabase
- **🔗 Link Discovery**: Automatically finds and queues new pages
- **🤖 AI Validation**: Uses OpenAI, Claude, Gemini, and Wolfram Alpha

## 📁 Generated Files

- `templates/reports/` - Generated AIVIIZN templates
- `screenshots/` - Full page screenshots
- `discovered_links.json` - All found AppFolio links
- `session_data/` - Processing session logs

## 🛠️ Commands

### Main Commands
```bash
./start_mcp.sh                # MCP-powered agent (RECOMMENDED)
./start.sh                    # Interactive menu
./run_mcp_agent.sh --start-reports # Start MCP with reports page
./run_agent.sh --start-reports # Start standalone with reports page
./monitor.sh                  # Check system status
```

### Link Management
```bash
python3 link_tracker.py --status  # Show link status
python3 link_tracker.py --report  # Generate report
python3 link_tracker.py --next    # Get next link
```

### Math Validation
```bash
python3 math_validator.py --batch              # Validate all
python3 math_validator.py --calculation "1+1"  # Test specific
```

## 🔧 How It Works

### MCP Version (Recommended)
1. **Terminal Coordinates**: Agent coordinates from terminal
2. **Browser Opens**: You log into AppFolio manually
3. **Claude MCP Processing**: Claude uses MCP servers to process pages
4. **AI Analysis**: Multiple AI services analyze each page
5. **Template Generation**: Creates AIVIIZN templates via MCP
6. **Database Storage**: Saves all data to Supabase via MCP

### Standalone Version
1. **Browser Opens**: Persistent Chromium browser starts
2. **Manual Login**: You log into AppFolio manually
3. **Automatic Processing**: Agent takes over and processes pages
4. **AI Analysis**: Multiple AI services analyze each page
5. **Template Generation**: Creates AIVIIZN templates
6. **Database Storage**: Saves all data to Supabase

## 📊 Progress Tracking

The system tracks:
- ✅ Pages processed
- ⏳ Pages pending
- 🧮 Calculations found
- 🔗 Links discovered
- 📄 Templates generated

## 🎨 Template Structure

Generated templates follow your existing structure:
```
templates/
├── reports/     # Financial reports
├── properties/  # Property management
├── accounting/  # Accounting pages
├── maintenance/ # Maintenance tracking
└── leasing/     # Leasing workflow
```

## 💾 Database Schema

Stores data in normalized tables:
- `appfolio_pages` - Page metadata
- `calculations` - Extracted math
- `templates` - Generated files
- `shared_data` - Normalized business data

## 🔐 Security

- All API keys in `.env` file
- No AppFolio credentials stored
- Browser data stays local
- Supabase for secure cloud storage

## 🚀 Next Steps

1. Run `./start_mcp.sh` to begin (RECOMMENDED)
2. Or run `./start.sh` for standalone mode
3. Log into AppFolio when prompted
4. Let the agent process pages automatically
5. Review generated templates in `templates/`
6. Integrate templates into your Flask app

## 📞 Support

Check logs and status:
```bash
./monitor.sh              # System overview
tail -f terminal_agent.log # Live log viewing
```
