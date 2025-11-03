#!/usr/bin/env python3
"""
Test script to launch a specific app and monitor its logs
"""

import sys
import subprocess
import time
from pathlib import Path

# App to test
APP_NAME = "platformer"  # Change this to test different apps

print(f"Testing app: {APP_NAME}")
print("=" * 60)

# Clear the launcher log
log_file = Path("settings/logs/launcher.log")
if log_file.exists():
    log_file.unlink()
    print("Cleared launcher log")

# Start MatrixOS in background
print("Starting MatrixOS...")
process = subprocess.Popen(
    ["python3", "start.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Wait for startup
time.sleep(2)

# Send Enter key to launch first app (or navigate to the app)
# For now, just let it run and we'll manually navigate
print(f"MatrixOS started. Navigate to {APP_NAME} and press Enter.")
print("Monitoring log file...")
print("=" * 60)

# Tail the log file
try:
    tail = subprocess.Popen(
        ["tail", "-f", str(log_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Read log output
    for line in tail.stdout:
        print(line, end='')
        
except KeyboardInterrupt:
    print("\n\nStopping...")
    tail.terminate()
    process.terminate()
    sys.exit(0)
