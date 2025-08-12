#!/bin/bash
# Install dependencies for portfolio visualization

echo "Installing Python dependencies for AI/ML Portfolio visualization..."

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Please install Python 3 first."
    exit 1
fi

# Install required packages
pip3 install matplotlib seaborn networkx numpy

echo "✅ Dependencies installed successfully!"
echo "You can now run: python3 generate_portfolio_visuals.py"