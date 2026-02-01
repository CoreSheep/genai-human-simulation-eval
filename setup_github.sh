#!/bin/bash
# GitHub Repository Setup Script
# Run this after creating your repository on github.com

set -e  # Exit on error

echo "=================================="
echo "GitHub Repository Setup"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "evaluate.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Prompt for GitHub username and repo name
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter repository name (default: roland-berger-genai-evaluation): " REPO_NAME
REPO_NAME=${REPO_NAME:-roland-berger-genai-evaluation}

echo ""
echo "Setting up repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

# Check if there are any commits
if ! git rev-parse HEAD >/dev/null 2>&1; then
    echo ""
    echo "📝 Creating initial commit..."
    
    # Add all files
    git add .
    
    # Create initial commit
    git commit -m "Initial commit: GenAI human simulation evaluation framework

- Multi-dimensional evaluation (semantic, stylistic, LLM-as-judge)
- Complete technical report and executive pitch deck
- Professional visualizations and analysis
- Evaluation of 3 human simulations across 10 questions each

Key Features:
- Async I/O for efficient API calls
- Comprehensive documentation with human-like annotations
- Production-ready code with type hints
- Beautiful visualizations for reports

Deliverables:
✅ Source code (Python)
✅ Technical report (2-page PDF)
✅ Executive pitch deck (Apple-style)
✅ Evaluation results and visualizations"
    
    echo "✅ Initial commit created"
else
    echo "✅ Commits already exist"
fi

# Set up remote
echo ""
echo "🔗 Setting up remote repository..."

# Remove existing origin if it exists
git remote remove origin 2>/dev/null || true

# Add new origin
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo "✅ Remote 'origin' configured"

# Rename branch to main if needed
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo ""
    echo "🔄 Renaming branch to 'main'..."
    git branch -M main
    echo "✅ Branch renamed to main"
fi

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
echo ""
read -p "Ready to push? This will upload your code to GitHub. (y/n): " CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    git push -u origin main
    echo ""
    echo "=================================="
    echo "✅ SUCCESS!"
    echo "=================================="
    echo ""
    echo "Your repository is now live at:"
    echo "🔗 https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "Next steps:"
    echo "  1. Visit your repository on GitHub"
    echo "  2. Add a description and topics (tags)"
    echo "  3. Consider adding a LICENSE file"
    echo "  4. Share the link on your resume/portfolio!"
    echo ""
else
    echo ""
    echo "⏸️  Push cancelled. When you're ready, run:"
    echo "   git push -u origin main"
    echo ""
fi
