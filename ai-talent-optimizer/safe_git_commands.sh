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
