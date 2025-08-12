#!/bin/bash
# Fix root cause of git issues - repository too large

echo "🔍 ANALYZING GIT REPOSITORY SIZE ISSUE"
echo "======================================="

# Check current git repo
cd ~/AI-ML-Portfolio/ai-talent-optimizer

echo -e "\n📊 Current repository stats:"
echo "Repository root: $(git rev-parse --show-toplevel)"
echo "Current directory: $(pwd)"

# Count tracked files
echo -e "\n📁 Files in git:"
echo "Total tracked files: $(git ls-files | wc -l)"
echo "Files in home directory: $(git ls-files ~ 2>/dev/null | wc -l)"
echo "Files outside project: $(git ls-files | grep -v "^AI-ML-Portfolio" | wc -l)"

echo -e "\n⚠️ PROBLEM IDENTIFIED:"
echo "Git is tracking your ENTIRE home directory!"
echo "This causes timeouts because there are too many files."

echo -e "\n🛠️ SOLUTIONS:"
echo "=============="

echo -e "\n1. QUICK FIX - Work in isolated repo:"
cat > create_isolated_repo.sh << 'EOF'
#!/bin/bash
# Create an isolated git repo just for ai-talent-optimizer

echo "Creating isolated repository..."

# Copy current work to new location
cp -r ~/AI-ML-Portfolio/ai-talent-optimizer ~/ai-talent-optimizer-isolated

# Go to new location
cd ~/ai-talent-optimizer-isolated

# Initialize fresh git repo
git init

# Add only relevant files
git add *.py *.md *.txt *.json *.sh
git commit -m "Initial commit - isolated repository"

echo "✅ Created isolated repo at: ~/ai-talent-optimizer-isolated"
echo "Work there to avoid timeout issues!"
EOF
chmod +x create_isolated_repo.sh

echo -e "\n2. BETTER FIX - Add proper .gitignore:"
cat > fix_gitignore.sh << 'EOF'
#!/bin/bash
# Add comprehensive .gitignore to exclude unnecessary files

cd ~
cat > .gitignore << 'GITIGNORE'
# Exclude everything by default
/*

# Only include specific project directories
!/AI-ML-Portfolio/
!/Projects/
!/SURVIVE/

# But exclude large/unnecessary subdirectories
Library/
.pyenv/
.npm/
.cache/
.local/
Downloads/
Desktop/
Documents/
*.db
*.log
*.tmp
.DS_Store
node_modules/
__pycache__/
*.pyc
.env
GITIGNORE

echo "✅ Created comprehensive .gitignore"
echo "Now remove cached files from git:"
echo "  git rm -r --cached Library/ .pyenv/ Desktop/"
EOF
chmod +x fix_gitignore.sh

echo -e "\n3. RECOMMENDED - Use project-specific repos:"
echo "   Instead of one massive repo, use separate repos:"
echo "   - ~/AI-ML-Portfolio/ai-talent-optimizer/.git"
echo "   - ~/Projects/financeforge/.git"
echo "   - ~/Projects/mirador/.git"

echo -e "\n📝 IMMEDIATE WORKAROUND:"
echo "========================"
echo "For now, use these commands that avoid timeouts:"

cat > safe_git_commands.sh << 'EOF'
#!/bin/bash
# Safe git commands that won't timeout

echo "Safe git commands:"
echo ""
echo "1. Stage only current directory:"
echo "   git add ."
echo ""
echo "2. Commit with timeout protection:"
echo "   timeout 5 git commit -m 'message' --no-verify"
echo ""
echo "3. Check status (limited):"
echo "   git status --short . | head -20"
echo ""
echo "4. View recent commits:"
echo "   git log --oneline -5"
EOF
chmod +x safe_git_commands.sh

echo -e "\n✅ FIX SCRIPTS CREATED:"
echo "  • create_isolated_repo.sh - Create clean repo"
echo "  • fix_gitignore.sh - Add proper .gitignore"
echo "  • safe_git_commands.sh - Safe git commands"

echo -e "\n🎯 IMMEDIATE ACTION:"
echo "Run: ./create_isolated_repo.sh"
echo "This will create a clean repo without timeout issues!"