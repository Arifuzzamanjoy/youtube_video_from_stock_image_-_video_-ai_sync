#!/bin/bash

# Automated Video Content Generation - Startup Script
# This script activates the virtual environment and runs the main application

echo "========================================="
echo "  Video Content Generation Pipeline"
echo "========================================="
echo ""

# Navigate to project directory
cd /root/Agent/content

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file with your API keys."
    exit 1
fi

echo "Environment activated!"
echo ""

# Display usage options
echo "Usage Options:"
echo "1. Run with single product:"
echo "   python main.py --product 'Product Name' --keywords features performance design"
echo ""
echo "2. Run in batch mode (from products.txt):"
echo "   python main.py --batch"
echo ""
echo "3. Run with custom format:"
echo "   python main.py --product 'Product Name' --format mp4"
echo ""

# If arguments provided, run with those
if [ $# -gt 0 ]; then
    echo "Running with provided arguments..."
    python main.py "$@"
else
    echo "Running in interactive mode..."
    echo "Enter product name (or press Enter to use products.txt):"
    read product_name
    
    if [ -z "$product_name" ]; then
        python main.py --batch
    else
        python main.py --product "$product_name" --keywords features performance design
    fi
fi

echo ""
echo "========================================="
echo "  Process Complete!"
echo "========================================="
