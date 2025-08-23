#!/bin/bash

# Create backup directory with timestamp
BACKUP_DIR="/Users/ianrakow/Desktop/AIVIIZN/Agent All Working"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🔄 CREATING BACKUP OF AGENT FILES"
echo "=================================="
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Copy main agent files
echo "📋 Copying main agent files..."
cp aiviizn_real_agent_with_ai_intelligence_updated.py "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ Main agent script"
cp enhanced_field_intelligence.py "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ Field intelligence"
cp dual_model_analyzer.py "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ Dual model analyzer"
cp field_consensus_analyzer.py "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ Field consensus"
cp comprehensive_data_extractor.py "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ Data extractor"

# Copy configuration
echo ""
echo "⚙️ Copying configuration..."
cp .env "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ Environment config"
cp aiviizn_config.json "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ AIVIIZN config"

# Copy database schemas
echo ""
echo "🗄️ Copying database schemas..."
cp complete_database_setup.sql "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ Complete DB setup"
cp database_field_mapping_schema.sql "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ Field mapping schema"
cp fix_pages_table_schema.sql "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ Pages table fix"

# Copy directories
echo ""
echo "📁 Copying directories..."

# Templates
if [ -d "templates" ]; then
    cp -r templates "$BACKUP_DIR/"
    TEMPLATE_COUNT=$(find "$BACKUP_DIR/templates" -type f -name "*.html" | wc -l)
    echo "  ✅ Templates directory ($TEMPLATE_COUNT HTML files)"
fi

# Data
if [ -d "data" ]; then
    cp -r data "$BACKUP_DIR/"
    echo "  ✅ Data directory"
fi

# Session data
if [ -d "session_data" ]; then
    cp -r session_data "$BACKUP_DIR/"
    echo "  ✅ Session data"
fi

# Screenshots
if [ -d "screenshots" ]; then
    cp -r screenshots "$BACKUP_DIR/"
    SCREENSHOT_COUNT=$(find "$BACKUP_DIR/screenshots" -type f | wc -l)
    echo "  ✅ Screenshots ($SCREENSHOT_COUNT files)"
fi

# Create backup info file
echo ""
echo "📝 Creating backup info..."
cat > "$BACKUP_DIR/backup_info_$TIMESTAMP.txt" << EOF
AIVIIZN Agent Backup
====================
Date: $(date)
Timestamp: $TIMESTAMP

This backup contains:
- Main agent Python scripts
- AI field intelligence modules
- Configuration files (.env, configs)
- Database schemas (SQL files)
- Templates directory (all HTML templates)
- Data directory (JSON state files)
- Session data
- Screenshots

To restore:
1. Copy all files back to /Users/ianrakow/Desktop/AIVIIZN/
2. Ensure .env file has correct API keys
3. Run: python3 aiviizn_real_agent_with_ai_intelligence_updated.py
EOF

echo "  ✅ Backup info created"

# Show summary
echo ""
echo "=========================================="
echo "✅ BACKUP COMPLETE!"
echo ""
echo "📁 Location: $BACKUP_DIR"
echo "📄 Info file: backup_info_$TIMESTAMP.txt"
echo ""

# Calculate size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "💾 Total backup size: $BACKUP_SIZE"
echo "=========================================="
