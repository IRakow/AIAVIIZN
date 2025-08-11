#!/bin/bash

# Install dependencies for AIVIIZN

echo "Installing AIVIIZN dependencies..."

# Check if pip3 is available
if command -v pip3 &> /dev/null; then
    echo "Using pip3..."
    pip3 install -r requirements.txt
# Check if python3 has pip module
elif command -v python3 &> /dev/null; then
    echo "Using python3 -m pip..."
    python3 -m pip install -r requirements.txt
# Try pip
elif command -v pip &> /dev/null; then
    echo "Using pip..."
    pip install -r requirements.txt
else
    echo "Error: pip not found. Please install Python and pip first."
    echo ""
    echo "On macOS, you can install Python with:"
    echo "  brew install python3"
    echo ""
    echo "Or download from: https://www.python.org/downloads/"
    exit 1
fi

echo ""
echo "Dependencies installed successfully!"
echo ""
echo "To run the application:"
echo "  python3 app.py"
echo ""
echo "Then open: http://localhost:8080"
