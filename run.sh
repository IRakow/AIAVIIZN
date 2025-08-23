#!/bin/bash
# AIVIIZN SaaS Quick Start Script

echo "🚀 AIVIIZN Multi-Tenant SaaS Agent"
echo "===================================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check for required files
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "   Please create a .env file with:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_SERVICE_KEY"
    echo "   - SUPABASE_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - OPENAI_API_KEY"
    exit 1
fi

# Menu
echo "What would you like to do?"
echo ""
echo "1) Setup database (first time)"
echo "2) Verify database setup"
echo "3) Test field identification"
echo "4) Run the SaaS agent"
echo "5) Run original agent (legacy)"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "📋 DATABASE SETUP INSTRUCTIONS"
        echo "=============================="
        echo ""
        echo "1. Go to your Supabase dashboard"
        echo "2. Navigate to SQL Editor"
        echo "3. Copy and paste the contents of: database_setup.sql"
        echo "4. Click 'Run' to execute"
        echo ""
        echo "The SQL file is located at:"
        echo "  /Users/ianrakow/Desktop/AIVIIZN/database_setup.sql"
        echo ""
        echo "After running the SQL, choose option 2 to verify setup."
        ;;
    
    2)
        echo ""
        echo "🔍 Verifying database setup..."
        echo ""
        python3 verify_database.py
        ;;
    
    3)
        echo ""
        echo "🧪 Testing field identification system..."
        echo ""
        python3 test_field_identification.py
        ;;
    
    4)
        echo ""
        echo "🚀 Starting AIVIIZN SaaS Agent..."
        echo ""
        python3 aiviizn_real_agent_saas.py
        ;;
    
    5)
        echo ""
        echo "⚠️  Running legacy single-tenant agent..."
        echo ""
        if [ -f "aiviizn_real_agent.py" ]; then
            python3 aiviizn_real_agent.py
        else
            echo "❌ Original agent file not found"
        fi
        ;;
    
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
