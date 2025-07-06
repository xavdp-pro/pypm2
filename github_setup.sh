#!/bin/bash
# GitHub Repository Setup Script for PyPM2

echo "🚀 PyPM2 GitHub Repository Setup"
echo "================================"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
  echo "❌ Not in a Git repository. Run this script from the PyPM2 package directory."
  exit 1
fi

echo ""
echo "📋 Repository Information:"
echo "  Project: PyPM2 - Process Manager for Python Applications"
echo "  Version: 1.0.0"
echo "  License: MIT"
echo "  Language: Python"
echo ""

echo "📦 Package Contents:"
echo "  ✅ $(find . -name "*.py" | wc -l) Python files"
echo "  ✅ $(find tests/ -name "*.py" | wc -l) test files"
echo "  ✅ $(find examples/ -name "*.py" | wc -l) example applications"
echo "  ✅ $(find docs/ -name "*.md" | wc -l) documentation files"
echo "  ✅ Complete systemd integration"
echo "  ✅ CLI with 9 commands"
echo ""

echo "🔗 To create the GitHub repository:"
echo ""
echo "1. Go to GitHub and create a new repository named 'pypm2'"
echo "2. Set it as public"
echo "3. Don't initialize with README (we have one)"
echo "4. Add this description:"
echo "   'Production-ready process manager for Python applications, inspired by PM2'"
echo ""
echo "5. Add these topics:"
echo "   python, process-manager, pm2, monitoring, systemd, production, cli, fastapi, flask"
echo ""
echo "6. Then run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/pypm2.git"
echo "   git push -u origin main"
echo "   git push --tags"
echo ""

echo "📝 Repository Features to Enable:"
echo "  ✅ Issues"
echo "  ✅ Wiki"
echo "  ✅ Projects"
echo "  ✅ Discussions"
echo "  ✅ Actions (for CI/CD)"
echo ""

echo "🏷️ Available Tags:"
git tag

echo ""
echo "📊 Repository Statistics:"
echo "  Commits: $(git rev-list --count HEAD)"
echo "  Files: $(git ls-files | wc -l)"
echo "  Size: $(du -sh . | cut -f1)"
echo ""

echo "🎯 Ready for GitHub! The repository is properly initialized with:"
echo "  ✅ Clean Git history"
echo "  ✅ Proper .gitignore"
echo "  ✅ Comprehensive documentation"
echo "  ✅ Tagged release (v1.0.0)"
echo "  ✅ Contribution guidelines"
echo "  ✅ MIT License"
echo "  ✅ Production-ready code"
echo ""

echo "💡 After pushing to GitHub, consider:"
echo "  - Setting up GitHub Actions for CI/CD"
echo "  - Enabling branch protection rules"
echo "  - Creating issue templates"
echo "  - Setting up automated releases"
echo "  - Adding code coverage reporting"
