#!/bin/bash
# AIVIIZN Multi-Tenant Quick Setup

echo ""
echo "====================================="
echo "🚀 AIVIIZN MULTI-TENANT SETUP"
echo "====================================="
echo ""
echo "This will set up your multi-tenant database"
echo "⚠️  WARNING: This will DELETE all existing data!"
echo ""
echo "Press ENTER to continue or Ctrl+C to cancel..."
read

echo ""
echo "Starting setup assistant..."
echo ""

python3 setup_assistant.py

echo ""
echo "====================================="
echo "After running the SQL in Supabase..."
echo "====================================="
echo ""
echo "1. Test the system:"
echo "   python3 test_complete_system.py"
echo ""
echo "2. Run the new agent:"
echo "   python3 aiviizn_real_agent_saas.py"
echo ""
echo "Good luck! 🚀"
