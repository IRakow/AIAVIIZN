#!/bin/bash

# Simple runner for processing pages one at a time

echo ""
echo "🚀 AIVIIZN PAGE PROCESSOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if state file exists to show queue
if [ -f "data/replicator_state.json" ]; then
    echo "📋 Current queue:"
    python3 -c "import json; state=json.load(open('data/replicator_state.json')); print('\n'.join(f'  {i+1}. {url}' for i,url in enumerate(state.get('queue',[])[:()]))"
    echo ""
fi

# Run the processor
if [ "$1" != "" ]; then
    echo "Processing specific URL: $1"
    python3 process_next_page.py "$1"
else
    echo "Processing next in queue..."
    python3 process_next_page.py
fi
