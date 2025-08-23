#!/bin/bash
# Quick setup script for the SaaS database fix

echo "🚀 AIVIIZN SaaS Database Setup Script"
echo "======================================"
echo ""
echo "This script will guide you through setting up the database"
echo ""

# Step 1: Show SQL files
echo "📋 Step 1: Database Setup Files Ready"
echo "--------------------------------------"
echo "✅ complete_saas_database_setup.sql - Main database schema"
echo "✅ create_storage_bucket.sql - Storage bucket setup"
echo "✅ store_in_supabase_saas_ready.py - Updated Python method"
echo ""

# Step 2: Open Supabase
echo "📋 Step 2: Open Supabase SQL Editor"
echo "------------------------------------"
echo "Opening Supabase SQL Editor in browser..."
open "https://supabase.com/dashboard/project/fqhrnybxymnxhicmcnbf/sql"
echo ""
echo "1. Click 'New Query'"
echo "2. Copy and paste the SQL from: complete_saas_database_setup.sql"
echo "3. Click 'Run'"
echo ""
read -p "Press ENTER when you've run the SQL setup..."

# Step 3: Create Storage Bucket
echo ""
echo "📋 Step 3: Create Storage Bucket"
echo "---------------------------------"
echo "Opening Supabase Storage..."
open "https://supabase.com/dashboard/project/fqhrnybxymnxhicmcnbf/storage/buckets"
echo ""
echo "1. Click 'New Bucket'"
echo "2. Name: page-content"
echo "3. Public: No"
echo "4. File size: 50MB"
echo "5. Click 'Create'"
echo ""
read -p "Press ENTER when you've created the bucket..."

# Step 4: Test the setup
echo ""
echo "📋 Step 4: Testing Database Setup"
echo "----------------------------------"
python3 test_saas_database.py

echo ""
echo "📋 Step 5: Check for Existing Duplicates"
echo "-----------------------------------------"
python3 check_duplicates.py

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Update your agent with the new store_in_supabase_real method"
echo "   from: store_in_supabase_saas_ready.py"
echo ""
echo "2. Run your agent:"
echo "   python aiviizn_real_agent_fixed.py"
echo ""
echo "Your system now has:"
echo "✅ Proper SaaS multi-tenancy"
echo "✅ Complete duplicate prevention"
echo "✅ Version tracking"
echo "✅ Error logging"
echo "✅ Link discovery"
echo ""
echo "🎉 Happy scraping without duplicates!"
