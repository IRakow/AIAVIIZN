#!/bin/bash

# Backup Claude's Working Files
# Created: August 21, 2025

echo "📁 Backing up Claude's working files..."

# Create backup directory
mkdir -p backup_working_claude_files
cd backup_working_claude_files

# Copy the main working files
cp ../beautiful_terminal_agent.py ./
cp ../run_beautiful.sh ./
cp ../BEAUTIFUL_TEMPLATES_README.md ./
cp ../make_executable.sh ./

echo "✅ Backed up these working files:"
echo "  - beautiful_terminal_agent.py (Main enhanced agent)"
echo "  - run_beautiful.sh (Launcher script)"
echo "  - BEAUTIFUL_TEMPLATES_README.md (Documentation)"
echo "  - make_executable.sh (Permission script)"

echo ""
echo "📍 Files saved in: backup_working_claude_files/"
echo "🎯 These are the files Claude created that work together"
