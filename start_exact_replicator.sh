#!/bin/bash

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                   AIVIIZN EXACT PAGE REPLICATOR                   ║"
echo "╠════════════════════════════════════════════════════════════════════╣"
echo "║                                                                    ║"
echo "║  YOUR LAYOUT (base.html)    +    APPFOLIO'S EXACT CONTENT        ║"
echo "║  ┌──────────────────┐            ┌─────────────────────┐         ║"
echo "║  │ AIVIIZN Header   │            │  Reports Dashboard  │         ║"
echo "║  ├──────┬───────────┤            │  • Rent Roll calc   │         ║"
echo "║  │ Your │           │     ═══>   │  • Occupancy rate   │         ║"
echo "║  │ Side │  [MAIN]   │            │  • Payment forms    │         ║"
echo "║  │ Bar  │           │            │  • Data tables      │         ║"
echo "║  └──────┴───────────┘            └─────────────────────┘         ║"
echo "║                                                                    ║"
echo "║  ✓ Your navigation stays         ✓ Exact functionality           ║"
echo "║  ✓ Your branding stays           ✓ Real calculations             ║"
echo "║  ✓ Your sidebar stays            ✓ Supabase connected            ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Starting agent in 3 seconds..."
echo ""
sleep 3

cd /Users/ianrakow/Desktop/AIVIIZN
python3 aiviizn_terminal_agent.py
