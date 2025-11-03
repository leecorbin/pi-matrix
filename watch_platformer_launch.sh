#!/bin/bash
# Interactive test to reproduce the Platformer hang
# This script will:
# 1. Clear logs
# 2. Start MatrixOS
# 3. Show you how to navigate and check logs

echo "=================================="
echo "Platformer Hang Reproduction Test"
echo "=================================="
echo

# Clear the log
rm -f settings/logs/launcher.log
echo "✓ Cleared launcher log"
echo

# Start monitoring the log in background
echo "Starting log monitor..."
touch settings/logs/launcher.log
tail -f settings/logs/launcher.log &
TAIL_PID=$!

echo
echo "=================================="
echo "NOW: Start MatrixOS in another terminal:"
echo "  python3 start.py"
echo
echo "Then:"
echo "  1. Use arrow keys to navigate to Platformer"
echo "  2. Press Enter to launch it"
echo "  3. Watch this window for log output"
echo "  4. Note which line is the LAST one before it hangs"
echo
echo "Press Ctrl+C here when done testing"
echo "=================================="

# Wait for user to stop
wait $TAIL_PID
