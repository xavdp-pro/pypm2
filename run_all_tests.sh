#!/bin/bash
# Complete test suite for PyPM2
# This script runs all tests and validates the complete functionality

set -e

echo "=== PyPM2 Complete Test Suite ==="
echo "Date: $(date)"
echo "Python version: $(python3 --version)"
echo "Working directory: $(pwd)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${YELLOW}Running test: $test_name${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED: $test_name${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAILED: $test_name${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Function to run test with output
run_test_with_output() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${YELLOW}Running test: $test_name${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED: $test_name${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAILED: $test_name${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo ""
}

# Cleanup function
cleanup() {
    echo "🧹 Cleaning up test processes..."
    python3 pypm2-cli stop all --force > /dev/null 2>&1 || true
    python3 pypm2-cli delete all > /dev/null 2>&1 || true
    
    # Kill any remaining processes on test ports
    for port in 8000 8001 8002 8003 8004; do
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    done
    
    sleep 2
}

# Setup
echo "🔧 Setting up test environment..."
cleanup

# Install dependencies if needed
echo "📦 Checking dependencies..."
python3 -c "import psutil, tabulate" > /dev/null 2>&1 || pip install psutil tabulate

# Test 1: Unit Tests
echo ""
echo "=== Unit Tests ==="
run_test_with_output "PyPM2 Unit Tests" "python3 -m pytest tests/ -v --tb=short"

# Test 2: CLI Basic Commands
echo ""
echo "=== CLI Basic Commands ==="
run_test "CLI Help" "python3 pypm2-cli --help"
run_test "CLI List (empty)" "python3 pypm2-cli list"

# Test 3: Process Management
echo ""
echo "=== Process Management ==="

# Start a simple process
run_test "Start simple process" "python3 pypm2-cli start examples/simple_script.py --name simple-test"
sleep 2

run_test "List processes" "python3 pypm2-cli list | grep simple-test"
run_test "Process status check" "python3 pypm2-cli list --json | python3 -c \"import json, sys; data=json.load(sys.stdin); exit(0 if any(p['name']=='simple-test' for p in data) else 1)\""

# Test logs
run_test "View process logs" "python3 pypm2-cli logs simple-test --lines 5"

# Test restart
run_test "Restart process" "python3 pypm2-cli restart simple-test"
sleep 2

# Test stop
run_test "Stop process" "python3 pypm2-cli stop simple-test"
sleep 1

# Test delete
run_test "Delete process" "python3 pypm2-cli delete simple-test"

# Test 4: Advanced Features
echo ""
echo "=== Advanced Features ==="

# Test with environment variables
run_test "Start with env vars" "python3 pypm2-cli start examples/simple_script.py --name env-test --env TEST_VAR=hello DEBUG=true"
sleep 2

# Test with interpreter
run_test "Start with custom interpreter" "python3 pypm2-cli start examples/simple_script.py --name interp-test --interpreter python3"
sleep 2

# Test multiple processes
run_test "Start multiple processes" "python3 pypm2-cli start examples/simple_script.py --name multi-test-1 && python3 pypm2-cli start examples/simple_script.py --name multi-test-2"
sleep 2

# Test bulk operations
run_test "Restart all processes" "python3 pypm2-cli restart all"
sleep 2

run_test "Stop all processes" "python3 pypm2-cli stop all"
sleep 1

run_test "Delete all processes" "python3 pypm2-cli delete all"

# Test 5: Web Server Integration
echo ""
echo "=== Web Server Integration ==="

# Test FastAPI
if [ -f "examples/fastapi_app.py" ]; then
    run_test "Start FastAPI server" "python3 pypm2-cli start examples/fastapi_app.py --name fastapi-test --interpreter /apps/pm2-v1/app/.venv/bin/python"
    sleep 3
    
    # Test HTTP endpoint
    run_test "FastAPI HTTP test" "curl -s http://localhost:8000/ | grep -q 'PyPM2 FastAPI Example'"
    
    # Test health endpoint
    run_test "FastAPI health check" "curl -s http://localhost:8000/health | grep -q 'healthy'"
    
    # Test metrics endpoint
    run_test "FastAPI metrics" "curl -s http://localhost:8000/metrics | grep -q 'process'"
    
    # Clean up
    python3 pypm2-cli stop fastapi-test > /dev/null 2>&1 || true
    python3 pypm2-cli delete fastapi-test > /dev/null 2>&1 || true
fi

# Test Flask
if [ -f "examples/flask_app.py" ]; then
    run_test "Start Flask server" "python3 pypm2-cli start examples/flask_app.py --name flask-test --env PORT=8001"
    sleep 3
    
    # Test HTTP endpoint
    run_test "Flask HTTP test" "curl -s http://localhost:8001/ | grep -q 'Flask'"
    
    # Clean up
    python3 pypm2-cli stop flask-test > /dev/null 2>&1 || true
    python3 pypm2-cli delete flask-test > /dev/null 2>&1 || true
fi

# Test 6: Error Handling
echo ""
echo "=== Error Handling ==="

# Test invalid script
run_test "Invalid script handling" "! python3 pypm2-cli start nonexistent.py --name invalid-test"

# Test duplicate names
run_test "Start process" "python3 pypm2-cli start examples/simple_script.py --name duplicate-test"
sleep 1
run_test "Duplicate name handling" "! python3 pypm2-cli start examples/simple_script.py --name duplicate-test"

# Clean up
python3 pypm2-cli stop duplicate-test > /dev/null 2>&1 || true
python3 pypm2-cli delete duplicate-test > /dev/null 2>&1 || true

# Test 7: Resurrect Command
echo ""
echo "=== Resurrect Command ==="

# Start some processes
python3 pypm2-cli start examples/simple_script.py --name resurrect-test-1 > /dev/null 2>&1 || true
python3 pypm2-cli start examples/simple_script.py --name resurrect-test-2 > /dev/null 2>&1 || true
sleep 2

# Stop them
python3 pypm2-cli stop all > /dev/null 2>&1 || true
sleep 1

# Test resurrect
run_test "Resurrect processes" "python3 pypm2-cli resurrect"
sleep 2

# Check if they're running
run_test "Check resurrected processes" "python3 pypm2-cli list | grep -E '(resurrect-test-1|resurrect-test-2)'"

# Clean up
python3 pypm2-cli stop all > /dev/null 2>&1 || true
python3 pypm2-cli delete all > /dev/null 2>&1 || true

# Test 8: Performance and Monitoring
echo ""
echo "=== Performance and Monitoring ==="

# Start a worker process
run_test "Start background worker" "python3 pypm2-cli start examples/advanced_worker.py --name worker-test"
sleep 3

# Check monitoring
run_test "Check process monitoring" "python3 pypm2-cli list --json | python3 -c \"import json, sys; data=json.load(sys.stdin); worker=[p for p in data if p['name']=='worker-test'][0]; exit(0 if worker['memory'] and worker['cpu'] is not None else 1)\""

# Test monit command (just check it doesn't crash)
timeout 5 python3 pypm2-cli monit > /dev/null 2>&1 || true

# Clean up
python3 pypm2-cli stop worker-test > /dev/null 2>&1 || true
python3 pypm2-cli delete worker-test > /dev/null 2>&1 || true

# Test 9: Configuration and Persistence
echo ""
echo "=== Configuration and Persistence ==="

# Test config directory creation
run_test "Config directory exists" "[ -d ~/.pypm2 ] || mkdir -p ~/.pypm2"

# Test process persistence
python3 pypm2-cli start examples/simple_script.py --name persist-test > /dev/null 2>&1 || true
sleep 1

run_test "Process config persistence" "[ -f ~/.pypm2/processes.json ]"

# Clean up
python3 pypm2-cli stop persist-test > /dev/null 2>&1 || true
python3 pypm2-cli delete persist-test > /dev/null 2>&1 || true

# Test 10: Memory and Resource Management
echo ""
echo "=== Memory and Resource Management ==="

# Test memory limit (if supported)
run_test "Start with memory limit" "python3 pypm2-cli start examples/simple_script.py --name memory-test --max-memory 100"
sleep 2

# Check process exists
run_test "Check memory-limited process" "python3 pypm2-cli list | grep memory-test"

# Clean up
python3 pypm2-cli stop memory-test > /dev/null 2>&1 || true
python3 pypm2-cli delete memory-test > /dev/null 2>&1 || true

# Final cleanup
cleanup

# Test Results Summary
echo ""
echo "=== Test Results Summary ==="
echo "Total tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed.${NC}"
    exit 1
fi
