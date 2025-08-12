#!/bin/bash
# Copy existing visualizations to portfolio

echo "📋 Copying existing visualizations to portfolio..."

# Mirador consciousness visualizations
echo "  ✓ Copying Mirador consciousness visuals..."
cp /Users/matthewscott/Projects/mirador/consciousness_test_visualization.png AI-ML-Portfolio/01-Consciousness-Discovery/visuals/ 2>/dev/null
cp /Users/matthewscott/Projects/mirador/consciousness_journey.png AI-ML-Portfolio/01-Consciousness-Discovery/visuals/ 2>/dev/null
cp /Users/matthewscott/Projects/mirador/model_ecosystem_visualization.png AI-ML-Portfolio/01-Consciousness-Discovery/visuals/ 2>/dev/null
cp /Users/matthewscott/Projects/mirador/mirador_architecture_diagram.png AI-ML-Portfolio/01-Consciousness-Discovery/visuals/ 2>/dev/null

# Copy SVG assets (for reference/conversion)
mkdir -p AI-ML-Portfolio/01-Consciousness-Discovery/visuals/svg
cp /Users/matthewscott/Projects/mirador/assets/*.svg AI-ML-Portfolio/01-Consciousness-Discovery/visuals/svg/ 2>/dev/null

echo "✅ Visual assets copied successfully!"
echo ""
echo "📁 Copied files:"
ls -la AI-ML-Portfolio/01-Consciousness-Discovery/visuals/*.png 2>/dev/null
echo ""
echo "Note: Run 'python3 generate_portfolio_visuals.py' to create additional visualizations"