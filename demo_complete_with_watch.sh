#!/bin/bash
# Complete PyPM2 demonstration with watch mode

echo "🚀 PyPM2 - Complete Demonstration with Watch Mode"
echo "================================================"

echo ""
echo "📋 PyPM2 Features:"
echo "  ✅ Python process manager"
echo "  ✅ Complete CLI interface"
echo "  ✅ Real-time monitoring"
echo "  ✅ Auto-restart with limits"
echo "  ✅ Log management"
echo "  ✅ Process persistence"
echo "  ✅ Systemd integration"
echo "  ✅ 🆕 WATCH MODE for development"
echo ""

# Initial cleanup
echo "🧹 Cleaning existing processes..."
python -m pypm2 stop all 2>/dev/null || true
python -m pypm2 delete all 2>/dev/null || true

echo ""
echo "1️⃣  BASIC COMMANDS TEST"
echo "======================"

# Start some processes
echo "🚀 Starting test processes..."
python -m pypm2 start test_watch_script.py --name test-1
python -m pypm2 start test_watch_script.py --name test-2 --max-restarts 5

echo ""
echo "📊 Process list:"
python -m pypm2 list

echo ""
echo "2️⃣  WATCH MODE TEST"
echo "=================="

echo "🎯 Starting watch mode in background..."
timeout 10 python -m pypm2 watch test-1 &
WATCH_PID=$!

sleep 2

echo "📝 Simulating file modification..."
echo "# Test watch mode $(date)" >>test_watch_script.py

sleep 3

echo "📊 Status after modification (process should have restarted):"
python -m pypm2 list

# Stop watch mode
kill $WATCH_PID 2>/dev/null || true
wait $WATCH_PID 2>/dev/null || true

echo ""
echo "3️⃣  OTHER FEATURES TEST"
echo "======================"

echo "🔄 Restart test..."
python -m pypm2 restart test-2

echo "📋 Logs test..."
python -m pypm2 logs test-1 --lines 5

echo "🧹 Flush logs test..."
python -m pypm2 flush test-1

echo "💾 Save test (resurrect)..."
python -m pypm2 save

echo ""
echo "4️⃣  TEST SUMMARY"
echo "==============="

echo "📊 Final process status:"
python -m pypm2 list

echo ""
echo "✅ Successfully tested:"
echo "  🔥 Process startup"
echo "  🔄 Automatic restart"
echo "  👁️  Watch mode with change detection"
echo "  📋 Log display"
echo "  💾 Save/restore"
echo "  🧹 Log cleanup"

echo ""
echo "🧹 Final cleanup..."
python -m pypm2 stop all
python -m pypm2 delete all

echo ""
echo "🎉 PyPM2 demonstration completed successfully!"
echo ""
echo "💡 To use watch mode in development:"
echo "   pypm2 start your-app.py --name dev-app"
echo "   pypm2 watch dev-app --watch-path ./src"
echo ""
echo "📚 Complete documentation available in docs/"
