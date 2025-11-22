#!/bin/bash
# Watch the debug log in real-time

LOG_FILE="/tmp/matrixos_debug.log"

# Clear old log
> "$LOG_FILE"

echo "Watching MatrixOS debug log: $LOG_FILE"
echo "Press Ctrl+C to stop"
echo "=========================================="

tail -f "$LOG_FILE"
