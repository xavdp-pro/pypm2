#!/bin/bash
# PyPM2 Installation Script

set -e

echo "=== PyPM2 Installation ==="

# Check Python version
python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" || {
    echo "❌ Python 3.8+ is required"
    exit 1
}

# Install package
echo "📦 Installing PyPM2..."
pip install -e .

# Make CLI executable
chmod +x pypm2-cli

# Create symlink if /usr/local/bin is writable
if [ -w /usr/local/bin ]; then
    ln -sf "$(pwd)/pypm2-cli" /usr/local/bin/pypm2
    echo "✅ PyPM2 CLI installed to /usr/local/bin/pypm2"
else
    echo "⚠️  Add $(pwd) to your PATH to use 'pypm2' command"
fi

# Run tests
echo "🧪 Running tests..."
python3 -m pytest tests/ -v

echo ""
echo "🎉 PyPM2 installation completed!"
echo ""
echo "Usage:"
echo "  pypm2 start app.py --name myapp"
echo "  pypm2 list"
echo "  pypm2 logs myapp"
echo "  pypm2 stop myapp"
echo ""
echo "For systemd integration:"
echo "  sudo systemd/install_systemd.sh"
