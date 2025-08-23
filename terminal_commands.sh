#!/bin/bash
# COPY THESE COMMANDS INTO YOUR TERMINAL

# 1. GO TO PROJECT
cd /Users/ianrakow/Desktop/AIVIIZN

# 2. CHECK DEPENDENCIES
python3 check_dependencies.py

# 3. IF ERRORS, RUN SETUP
chmod +x setup.sh
./setup.sh

# 4. PROCESS FIRST PAGE
chmod +x process.sh
./process.sh

# 5. PROCESS NEXT PAGE (repeat as needed)
./process.sh

# That's it! One page at a time.
