#!/bin/bash

# AIVIIZN Terminal Agent Setup Script
# This script sets up the complete terminal agent system

set -e  # Exit on error

echo "🚀 Setting up AIVIIZN Terminal Agent System"
echo "============================================"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_warning "This script is optimized for macOS. Some features may not work on other systems."
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command_exists python3; then
    print_error "Python 3 is required but not installed."
    exit 1
fi

# Check pip
if ! command_exists pip3; then
    print_error "pip3 is required but not installed."
    exit 1
fi

# Check Node.js (for Playwright)
if ! command_exists node; then
    print_warning "Node.js not found. Installing via Homebrew..."
    if command_exists brew; then
        brew install node
    else
        print_error "Please install Node.js manually"
        exit 1
    fi
fi

print_success "Prerequisites check completed"

# Create virtual environment
print_status "Setting up Python virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."

# Create requirements file for the terminal agent
cat > requirements_terminal_agent.txt << EOF
# Core dependencies
playwright>=1.40.0
openai>=1.3.0
anthropic>=0.8.0
google-generativeai>=0.3.0
supabase>=2.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0

# Flask and web dependencies
flask>=3.0.0
flask-session>=0.5.0
jinja2>=3.1.0

# Data processing
pandas>=2.1.0
numpy>=1.24.0

# Async support
aiohttp>=3.9.0
asyncio-throttle>=1.0.0

# Logging and monitoring
structlog>=23.0.0
python-dotenv>=1.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
EOF

pip install -r requirements_terminal_agent.txt

print_success "Python dependencies installed"

# Install Playwright browsers
print_status "Installing Playwright browsers..."
playwright install
playwright install-deps
print_success "Playwright browsers installed"

# Create directory structure
print_status "Creating directory structure..."

mkdir -p screenshots
mkdir -p logs
mkdir -p reports
mkdir -p templates/reports
mkdir -p templates/admin
mkdir -p templates/properties
mkdir -p templates/accounting
mkdir -p templates/maintenance
mkdir -p templates/leasing
mkdir -p static/js
mkdir -p static/css

print_success "Directory structure created"

# Create the main terminal agent files
print_status "Creating terminal agent files..."

# Save the terminal agent script
cat > terminal_agent.py << 'EOF'
# The terminal agent code would go here - this is a placeholder
# In practice, you would copy the full terminal agent code from the artifact
print("Terminal Agent - Use the code from the artifact above")
EOF

# Save the link tracker script
cat > link_tracker.py << 'EOF'
# The link tracker code would go here - this is a placeholder
# In practice, you would copy the full link tracker code from the artifact
print("Link Tracker - Use the code from the artifact above")
EOF

# Save the math validator script
cat > math_validator.py << 'EOF'
# The math validator code would go here - this is a placeholder
# In practice, you would copy the full math validator code from the artifact
print("Math Validator - Use the code from the artifact above")
EOF

# Make scripts executable
chmod +x terminal_agent.py
chmod +x link_tracker.py
chmod +x math_validator.py

print_success "Terminal agent files created"

# Check .env file
print_status "Checking environment configuration..."

if [ ! -f ".env" ]; then
    print_warning ".env file not found. Please ensure your .env file exists with all required API keys."
    cat > .env.example << 'EOF'
# AIVIIZN Environment Configuration

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key

# AI API Keys
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
WOLFRAM_APP_ID=your_wolfram_id

# Flask Configuration
SECRET_KEY=your_secret_key
FLASK_ENV=development

# Application Settings
APP_NAME=AIVIIZN Property Management
COMPANY_NAME=AIVIIZN Property Management
EOF
    print_warning "Created .env.example - please copy to .env and fill in your API keys"
else
    print_success ".env file found"
fi

# Create launcher scripts
print_status "Creating launcher scripts..."

# Main launcher
cat > run_terminal_agent.sh << 'EOF'
#!/bin/bash

# AIVIIZN Terminal Agent Launcher

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your API keys."
    exit 1
fi

# Run the terminal agent
echo "🤖 Starting AIVIIZN Terminal Agent..."
python3 terminal_agent.py "$@"
EOF

# Link tracker launcher
cat > run_link_tracker.sh << 'EOF'
#!/bin/bash

# Link Tracker Launcher

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

source venv/bin/activate
python3 link_tracker.py "$@"
EOF

# Math validator launcher
cat > run_math_validator.sh << 'EOF'
#!/bin/bash

# Math Validator Launcher

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

source venv/bin/activate
python3 math_validator.py "$@"
EOF

# Make launchers executable
chmod +x run_terminal_agent.sh
chmod +x run_link_tracker.sh
chmod +x run_math_validator.sh

print_success "Launcher scripts created"

# Create quick start script
cat > quick_start.sh << 'EOF'
#!/bin/bash

# AIVIIZN Terminal Agent Quick Start

echo "🚀 AIVIIZN Terminal Agent - Quick Start"
echo "======================================"

echo "Available commands:"
echo ""
echo "1. Start with Reports Page:"
echo "   ./run_terminal_agent.sh --start-reports"
echo ""
echo "2. Process Specific URL:"
echo "   ./run_terminal_agent.sh --url https://celticprop.appfolio.com/reports"
echo ""
echo "3. Check Link Status:"
echo "   ./run_link_tracker.sh --status"
echo ""
echo "4. Validate Calculations:"
echo "   ./run_math_validator.sh --batch"
echo ""
echo "5. Generate Progress Report:"
echo "   ./run_link_tracker.sh --report"
echo ""

read -p "Enter your choice (1-5) or press Enter to start with reports: " choice

case $choice in
    1|"")
        echo "Starting with reports page..."
        ./run_terminal_agent.sh --start-reports
        ;;
    2)
        read -p "Enter URL: " url
        ./run_terminal_agent.sh --url "$url"
        ;;
    3)
        ./run_link_tracker.sh --status
        ;;
    4)
        ./run_math_validator.sh --batch
        ;;
    5)
        ./run_link_tracker.sh --report
        ;;
    *)
        echo "Invalid choice. Use ./run_terminal_agent.sh --help for more options."
        ;;
esac
EOF

chmod +x quick_start.sh

print_success "Quick start script created"

# Create monitoring script
cat > monitor_progress.sh << 'EOF'
#!/bin/bash

# Progress Monitoring Script

source venv/bin/activate

echo "📊 AIVIIZN Terminal Agent - Progress Monitor"
echo "=========================================="

# Check link status
echo "🔗 Link Processing Status:"
python3 link_tracker.py --status

echo ""
echo "📈 Recent Progress:"
python3 link_tracker.py --export

echo ""
echo "🔍 Next Priority Links:"
python3 link_tracker.py --next

# Check if there are any failed validations
echo ""
echo "⚠️  System Health Check:"
echo "- Screenshots directory: $(ls -1 screenshots 2>/dev/null | wc -l) files"
echo "- Templates directory: $(find templates -name "*.html" 2>/dev/null | wc -l) templates"
echo "- Log files: $(ls -1 *.log 2>/dev/null | wc -l) files"

echo ""
echo "Use './quick_start.sh' to continue processing or"
echo "Use './run_terminal_agent.sh --help' for more options"
EOF

chmod +x monitor_progress.sh

print_success "Monitoring script created"

# Create update script
cat > update_system.sh << 'EOF'
#!/bin/bash

# System Update Script

echo "🔄 Updating AIVIIZN Terminal Agent System..."

source venv/bin/activate

# Update Python packages
pip install --upgrade -r requirements_terminal_agent.txt

# Update Playwright
playwright install

# Clean up old logs (keep last 10)
find logs -name "*.log" -type f | sort | head -n -10 | xargs rm -f 2>/dev/null || true

# Clean up old screenshots (keep last 50)
find screenshots -name "*.png" -type f | sort | head -n -50 | xargs rm -f 2>/dev/null || true

echo "✅ System updated successfully"
EOF

chmod +x update_system.sh

print_success "Update script created"

# Final checks and summary
print_status "Running final checks..."

# Check if all required files exist
required_files=(".env" "terminal_agent.py" "link_tracker.py" "math_validator.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    print_success "All required files are present"
else
    print_warning "Missing files: ${missing_files[*]}"
fi

# Create README
cat > README_TERMINAL_AGENT.md << 'EOF'
# AIVIIZN Terminal Agent System

## Overview

The AIVIIZN Terminal Agent is a sophisticated system that systematically copies AppFolio functionality to your AIVIIZN property management system. It uses multiple AI services to ensure accuracy and completeness.

## Features

- **Systematic Page Processing**: Visits AppFolio pages one by one
- **Multi-AI Validation**: Uses OpenAI, Claude, Gemini, and Wolfram Alpha
- **Template Generation**: Creates Flask templates with exact functionality
- **Database Integration**: Stores everything in Supabase
- **Link Discovery**: Automatically finds and queues new pages
- **Math Validation**: Ensures calculations are correct

## Quick Start

1. **Setup**: Run `./setup.sh` (already done)
2. **Configure**: Ensure your `.env` file has all API keys
3. **Start**: Run `./quick_start.sh`

## Usage Commands

### Terminal Agent
```bash
# Start with reports page
./run_terminal_agent.sh --start-reports

# Process specific URL
./run_terminal_agent.sh --url https://celticprop.appfolio.com/reports

# Process all discovered links
./run_terminal_agent.sh
```

### Link Tracker
```bash
# Check status
./run_link_tracker.sh --status

# Generate report
./run_link_tracker.sh --report

# Get next link to process
./run_link_tracker.sh --next

# Reset failed links
./run_link_tracker.sh --reset-failed
```

### Math Validator
```bash
# Validate specific calculation
./run_math_validator.sh --calculation "1250 + 950" --context "monthly rent totals"

# Validate all calculations for a page
./run_math_validator.sh --page-id 1

# Batch validate all pending
./run_math_validator.sh --batch
```

### Monitoring
```bash
# Check overall progress
./monitor_progress.sh

# Update system
./update_system.sh
```

## Directory Structure

```
AIVIIZN/
├── terminal_agent.py           # Main agent script
├── link_tracker.py            # Link management
├── math_validator.py          # AI validation system
├── templates/                 # Generated templates
│   ├── reports/              # Report templates
│   ├── admin/                # Admin templates
│   └── ...
├── screenshots/              # Page screenshots
├── logs/                     # System logs
├── reports/                  # Progress reports
└── venv/                     # Python environment
```

## Configuration

All configuration is done through the `.env` file:

```env
# Supabase
SUPABASE_URL=your_url
SUPABASE_SERVICE_KEY=your_key

# AI APIs
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key
WOLFRAM_APP_ID=your_id
```

## Workflow

1. **Discovery**: Agent visits starting page and discovers links
2. **Processing**: Each page is analyzed, screenshotted, and processed
3. **Validation**: Calculations are validated by multiple AI services
4. **Generation**: Templates and routes are generated for AIVIIZN
5. **Storage**: Everything is saved to Supabase database
6. **Iteration**: Process continues with discovered links

## Database Schema

The system uses these main tables:
- `appfolio_pages`: Captured page information
- `calculation_formulas`: Extracted calculations
- `multi_ai_validations`: AI validation results
- `generated_components`: Created templates
- `shared_data_elements`: Normalized data elements

## Troubleshooting

### Common Issues

1. **Login Required**: If AppFolio requires login, the browser will pause for manual login
2. **Rate Limiting**: System includes delays to avoid rate limiting
3. **API Errors**: Check your API keys in `.env` file
4. **Memory Issues**: Process pages in smaller batches if needed

### Log Files

- `terminal_agent.log`: Main agent activity
- `app.log`: Flask application logs
- Session reports in `reports/` directory

## Next Steps

1. Review generated templates in `templates/` directory
2. Test calculations with the validator
3. Integrate templates into your Flask application
4. Deploy to production when ready

## Support

For issues or questions:
1. Check the log files
2. Run `./monitor_progress.sh` for system status
3. Use `--help` flag with any script for options
EOF

print_success "Documentation created"

# Final summary
echo ""
echo "🎉 AIVIIZN Terminal Agent Setup Complete!"
echo "========================================"
echo ""
echo "📁 Files created:"
echo "   ✓ Python virtual environment"
echo "   ✓ Terminal agent scripts"
echo "   ✓ Launcher scripts"
echo "   ✓ Monitoring tools"
echo "   ✓ Documentation"
echo ""
echo "🚀 Next steps:"
echo "   1. Ensure your .env file has all API keys"
echo "   2. Run: ./quick_start.sh"
echo "   3. Monitor progress with: ./monitor_progress.sh"
echo ""
echo "💡 Tips:"
echo "   - Start with the reports page for best results"
echo "   - Use the math validator to ensure accuracy"
echo "   - Check the progress regularly"
echo "   - Review generated templates before deploying"
echo ""

# Deactivate virtual environment
deactivate

print_success "Setup completed successfully! 🚀"

echo ""
echo "Run './quick_start.sh' to begin processing AppFolio pages."