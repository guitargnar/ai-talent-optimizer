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
