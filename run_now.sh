#!/bin/bash
# Manual run script for AI Job Hunter

cd /Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer

echo "🚀 AI Job Hunter - Manual Run"
echo "============================="
echo ""

# Activate virtual environment if it exists
if [ -f "google-env/bin/activate" ]; then
    source google-env/bin/activate
fi

# Run the automation
python3 run_automation.py

echo ""
echo "✅ Manual run complete!"
