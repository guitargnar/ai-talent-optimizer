#\!/bin/bash

# Create Isolated Git Repository for AI Talent Optimizer
# This fixes the timeout issues from tracking entire home directory

echo "🔧 Creating isolated Git repository for AI Talent Optimizer..."

# Get current directory
PROJECT_DIR="/Users/matthewscott/AI-ML-Portfolio/ai-talent-optimizer"
cd "$PROJECT_DIR"

# Check if already a git repo
if [ -d ".git" ]; then
    echo "⚠️  .git directory already exists in project"
    echo "Remove it first with: rm -rf .git"
    exit 1
fi

# Initialize new repository
echo "📁 Initializing new Git repository in: $PROJECT_DIR"
git init

# Create comprehensive .gitignore
echo "📝 Creating proper .gitignore..."
cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Databases
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# Environment
.env
token.json

# IDE
.vscode/
.idea/
.DS_Store

# Output
output/
applications_sent/

# Temporary
tmp/
temp/
*.tmp
GITIGNORE

echo "✅ .gitignore created"

# Add all project files
echo "📦 Adding project files..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: AI Talent Optimizer v2.0 - Isolated repository"

echo "✅ Repository created successfully\!"
git status
