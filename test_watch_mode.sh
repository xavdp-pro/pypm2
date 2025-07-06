#!/bin/bash
"""
PyPM2 watch mode automated test
"""

echo "🎯 PyPM2 watch mode test"
echo "========================"

# Start watch mode in background
echo "🚀 Starting watch mode in background..."
python -m pypm2 watch test-watch &
WATCH_PID=$!

sleep 2

echo "📝 Modifying test file..."
# Add comment to file to trigger restart
echo "# Test modification $(date)" >>test_watch_script.py

sleep 3

echo "📊 Process status after modification:"
python -m pypm2 list

sleep 2

# Stop watch mode
echo "🛑 Stopping watch mode..."
kill $WATCH_PID 2>/dev/null

# Clean test process
echo "🧹 Cleanup..."
python -m pypm2 stop test-watch

echo "✅ Watch mode test completed!"
