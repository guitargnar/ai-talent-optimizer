#!/bin/bash
# Setup script for job automation system

echo "🚀 Setting up Job Automation System"
echo "===================================="

# Navigate to directory
cd /Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install dnspython python-dotenv

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file..."
    cat > .env << EOF
EMAIL_ADDRESS=matthewdscott7@gmail.com
EMAIL_APP_PASSWORD=your_app_password_here
EOF
    echo "❗ Please edit .env and add your EMAIL_APP_PASSWORD"
fi

# Check for resumes
if [ ! -d resumes ]; then
    mkdir resumes
    echo "📁 Created resumes directory"
    echo "❗ Please add your PDF resumes to the resumes/ directory"
fi

# Run system check
echo ""
echo "🔍 Running system check..."
python3 - << EOF
import sys
sys.path.insert(0, "/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer")

print("Checking imports...")
try:
    import dns.resolver
    print("  ✅ DNS resolver available")
except:
    print("  ❌ DNS resolver missing - run: pip install dnspython")

try:
    from dotenv import load_dotenv
    print("  ✅ Dotenv available")
except:
    print("  ❌ Dotenv missing - run: pip install python-dotenv")

try:
    from email_validator import EmailValidator
    print("  ✅ Email validator available")
except:
    print("  ❌ Email validator not found")

try:
    from db_config import get_db_connection
    print("  ✅ Database config available")
except:
    print("  ❌ Database config missing")

print("\n✅ Setup check complete!")
EOF

echo ""
echo "===================================="
echo "✅ Setup complete!"
echo ""
echo "To use the system:"
echo "  1. Edit .env with your app password"
echo "  2. Add PDFs to resumes/ directory"
echo "  3. Run: python3 integrated_automation.py"
