#!/bin/bash
# Make sure script is executable
chmod +x auto.sh

echo "🚀 AIVIIZN APPLESCRIPT AUTOMATION LAUNCHER - WITH INTERLINKING"
echo "=============================================================="
echo ""

cd /Users/ianrakow/Desktop/AIVIIZN

echo "🎯 Choose automation level:"
echo ""
echo "BASIC AUTOMATION:"
echo "1. 🧪 Test AppleScript automation"
echo "2. 🔍 Run system diagnostics"
echo "3. 🚀 Basic automation (30 pages - simplified instructions)"
echo ""
echo "COMPREHENSIVE ANALYSIS:"
echo "4. 🔬 FULL comprehensive analysis (30 pages - all calculations/APIs)"
echo "5. 🔥 Comprehensive TOP 10 (priority pages with full analysis)"
echo "6. 🔧 Patched detailed analysis (30 pages - fixed original script)"
echo ""
echo "🔗 INTERLINKING SYSTEM (RECOMMENDED):"
echo "7. 🧭 FULL interlinking system (comprehensive + navigation)"
echo "8. 🎯 Interlinking TOP 5 (test interlinking system)"
echo ""
echo "STATUS:"
echo "9. 📋 Show automation summary"
echo ""

read -p "Enter choice (1-9): " choice

case $choice in
    1)
        echo "🧪 Testing AppleScript automation..."
        python3 test_applescript.py
        ;;
    2)
        echo "🔍 Running diagnostics..."
        python3 diagnose.py
        ;;
    3)
        echo "🚀 Starting BASIC automation (simplified instructions)..."
        echo "⚠️  WARNING: This uses simplified instructions without full analysis"
        echo "Choose option 5 when prompted!"
        sleep 3
        ./start_builder.sh
        ;;
    4)
        echo "🔬 Starting COMPREHENSIVE technical analysis..."
        echo "⚡ Extracts ALL calculations, API calls, math functions"
        echo "🎯 Full mathematical and technical depth per page"
        echo "⚠️  NOTE: No interlinking - pages will be isolated"
        sleep 3
        python3 autonomous_appfolio_builder_comprehensive.py
        ;;
    5)
        echo "🔥 Starting COMPREHENSIVE analysis - TOP 10 priority pages..."
        echo "🔬 Maximum technical depth for most important AppFolio pages"
        echo "⚠️  NOTE: No interlinking - good for testing individual pages"
        sleep 2
        python3 -c "
import sys
sys.path.append('.')
from autonomous_appfolio_builder_comprehensive import AutonomousAppFolioBuilderComprehensive
builder = AutonomousAppFolioBuilderComprehensive()
builder.priority_urls = builder.priority_urls[:10]
builder.print_banner()
print('🔥 COMPREHENSIVE analysis - TOP 10 pages')
builder.process_with_comprehensive_analysis()
"
        ;;
    6)
        echo "🔧 Starting PATCHED detailed analysis..."
        echo "📋 This fixes the original script to use detailed instructions"
        echo "⚠️  NOTE: No interlinking system included"
        sleep 2
        python3 autonomous_appfolio_builder_patched.py
        ;;
    7)
        echo "🧭 Starting FULL INTERLINKING SYSTEM..."
        echo "🔗 Comprehensive analysis + complete navigation system"
        echo "📊 Creates proper page relationships and data sharing"
        echo "🎯 All pages connected with consistent navigation"
        echo "📱 Mobile-responsive menu and breadcrumb navigation"
        echo "⚡ This is the MOST COMPLETE option!"
        sleep 3
        python3 autonomous_appfolio_builder_with_interlinking.py
        ;;
    8)
        echo "🎯 Starting INTERLINKING SYSTEM - TOP 5 pages..."
        echo "🔗 Test the interlinking system with priority pages"
        echo "🧭 Perfect for testing navigation and page connections"
        sleep 2
        python3 -c "
import sys
sys.path.append('.')
from autonomous_appfolio_builder_with_interlinking import InterlinkedAppFolioBuilder
builder = InterlinkedAppFolioBuilder()
builder.priority_urls = builder.priority_urls[:5]
builder.print_banner()
print('🎯 INTERLINKING SYSTEM - TOP 5 pages')
builder.process_with_full_interlinking()
"
        ;;
    9)
        echo "📋 Showing automation summary..."
        python3 ready.py
        ;;
    *)
        echo "❌ Invalid choice"
        echo ""
        echo "💡 RECOMMENDATIONS:"
        echo "   🧭 Option 7: FULL interlinking system (BEST - creates complete system)"
        echo "   🎯 Option 8: Test interlinking with TOP 5 pages (great for testing)"
        echo "   🔥 Option 5: Comprehensive analysis without interlinking"
        echo "   🔧 Option 6: Patched version (middle ground)"
        echo "   🚀 Option 3: Basic automation (not recommended)"
        echo ""
        echo "Run: ./auto.sh to try again"
        ;;
esac

echo ""
echo "🎯 FEATURE COMPARISON:"
echo "┌─────────────────────────────────────────────────────────────────┐"
echo "│ Feature                    │ Basic │ Patched │ Comprehensive │ Interlinked │"
echo "├─────────────────────────────────────────────────────────────────┤"
echo "│ Page extraction           │   ✓   │    ✓    │      ✓        │      ✓      │"
echo "│ Mathematical analysis     │   ✗   │    ✓    │      ✓        │      ✓      │"
echo "│ API/Network analysis      │   ✗   │    ✗    │      ✓        │      ✓      │"
echo "│ JavaScript functions      │   ✗   │    ✗    │      ✓        │      ✓      │"
echo "│ Navigation system         │   ✗   │    ✗    │      ✗        │      ✓      │"
echo "│ Page interlinking         │   ✗   │    ✗    │      ✗        │      ✓      │"
echo "│ Shared data/filters       │   ✗   │    ✗    │      ✗        │      ✓      │"
echo "│ Related page connections  │   ✗   │    ✗    │      ✗        │      ✓      │"
echo "│ Breadcrumb navigation     │   ✗   │    ✗    │      ✗        │      ✓      │"
echo "│ Mobile responsive menu    │   ✗   │    ✗    │      ✗        │      ✓      │"
echo "└─────────────────────────────────────────────────────────────────┘"
echo ""
echo "🔗 INTERLINKING BENEFITS:"
echo "   • Seamless navigation between all AppFolio reports"
echo "   • Shared filters (property/date) persist across pages"
echo "   • Related reports automatically suggested"
echo "   • Data flows between connected reports"
echo "   • Consistent UI/UX matching AppFolio exactly"
echo "   • Mobile-responsive navigation menu"
echo "   • Breadcrumb navigation shows current location"
echo "   • Quick actions and shortcuts between related data"
