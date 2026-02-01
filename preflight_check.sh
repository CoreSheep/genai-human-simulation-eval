#!/bin/bash
# Pre-flight check script - Run before pushing to GitHub

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     GitHub Pre-Flight Check                                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check 1: Python files exist
echo "✓ Checking Python source files..."
if [ -f "evaluate.py" ] && [ -f "src/data_loader.py" ]; then
    echo "  ✅ Source files present"
else
    echo "  ❌ Missing source files!"
    exit 1
fi

# Check 2: Documentation exists
echo "✓ Checking documentation..."
if [ -f "README.md" ] && [ -f ".gitignore" ]; then
    echo "  ✅ Documentation complete"
else
    echo "  ❌ Missing documentation!"
    exit 1
fi

# Check 3: Check for API keys or secrets
echo "✓ Checking for API keys or secrets..."
if grep -r "sk-" . --include="*.py" --include="*.json" 2>/dev/null | grep -v ".pyc" | grep -v "__pycache__"; then
    echo "  ⚠️  WARNING: Found potential API keys in files!"
    echo "  Please remove before pushing to GitHub"
    exit 1
else
    echo "  ✅ No API keys found in source"
fi

# Check 4: .gitignore is working
echo "✓ Checking .gitignore configuration..."
if [ -f ".gitignore" ]; then
    echo "  ✅ .gitignore file exists"
    
    # Check if it excludes the right things
    if grep -q "__pycache__" .gitignore && grep -q "*.pdf" .gitignore; then
        echo "  ✅ .gitignore properly configured"
    else
        echo "  ⚠️  .gitignore may need updating"
    fi
else
    echo "  ❌ No .gitignore file!"
    exit 1
fi

# Check 5: File sizes
echo "✓ Checking file sizes..."
large_files=$(find . -type f -size +10M -not -path "./.git/*" 2>/dev/null)
if [ -z "$large_files" ]; then
    echo "  ✅ No files larger than 10MB"
else
    echo "  ⚠️  WARNING: Large files found:"
    echo "$large_files"
    echo "  Consider adding to .gitignore"
fi

# Check 6: Test that code can be imported
echo "✓ Checking Python imports..."
if python3 -c "import sys; sys.path.insert(0, 'src'); from data_loader import DataLoader" 2>/dev/null; then
    echo "  ✅ Python modules can be imported"
else
    echo "  ⚠️  Import check failed (may need dependencies)"
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  PRE-FLIGHT CHECK COMPLETE!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Your repository is ready for GitHub! 🚀"
echo ""
echo "Quick stats:"
echo "  • Source files: $(find src -name "*.py" 2>/dev/null | wc -l | tr -d ' ') Python files"
echo "  • Documentation: $(find . -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ') markdown files"
echo "  • Visualizations: $(find outputs/figures -name "*.png" 2>/dev/null | wc -l | tr -d ' ') PNG charts"
echo ""
echo "Next step: Run ./setup_github.sh to push to GitHub"
echo ""
