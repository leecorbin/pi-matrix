#!/usr/bin/env python3
"""
Test launching Platformer through the full MatrixOS stack
to identify where the hang occurs
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from matrixos.logger import get_logger
from matrixos.display import MatrixDisplay
from matrixos.input import MatrixInput
from matrixos.app_framework import OSContext
from pathlib import Path

logger = get_logger("FullLaunchTest")

logger.info("Starting full MatrixOS launch test for Platformer")
logger.info("=" * 60)

# Step 1: Create display
logger.info("Step 1: Creating MatrixDisplay...")
start = time.time()
matrix = MatrixDisplay(width=128, height=128)
elapsed = time.time() - start
logger.info(f"Step 1 PASSED - took {elapsed:.3f}s")

# Step 2: Create input handler
logger.info("Step 2: Creating MatrixInput...")
start = time.time()
input_handler = MatrixInput()
elapsed = time.time() - start
logger.info(f"Step 2 PASSED - took {elapsed:.3f}s")

# Step 3: Create OS context
logger.info("Step 3: Creating OSContext...")
start = time.time()
os_context = OSContext(matrix, input_handler)
elapsed = time.time() - start
logger.info(f"Step 3 PASSED - took {elapsed:.3f}s")

# Step 4: Import and instantiate Platformer
logger.info("Step 4: Importing Platformer module...")
start = time.time()
import importlib.util
spec = importlib.util.spec_from_file_location(
    "platformer_full_test",
    "examples/platformer/main.py"
)
module = importlib.util.module_from_spec(spec)
logger.info("Step 4a: About to exec_module...")
spec.loader.exec_module(module)
elapsed = time.time() - start
logger.info(f"Step 4 PASSED - exec_module took {elapsed:.3f}s")

# Step 5: Create game instance
logger.info("Step 5: Creating PlatformerGame instance...")
start = time.time()
game = module.PlatformerGame()
elapsed = time.time() - start
logger.info(f"Step 5 PASSED - took {elapsed:.3f}s")

# Step 6: Register app
logger.info("Step 6: Registering app with OSContext...")
start = time.time()
os_context.register_app(game)
elapsed = time.time() - start
logger.info(f"Step 6 PASSED - took {elapsed:.3f}s")

# Step 7: Switch to app
logger.info("Step 7: Switching to app...")
start = time.time()
os_context.switch_to_app(game)
elapsed = time.time() - start
logger.info(f"Step 7 PASSED - took {elapsed:.3f}s")

# Step 8: Call run() for a few iterations
logger.info("Step 8: Running event loop for 3 frames...")
start = time.time()

# Patch the run loop to exit after a few frames
original_run = os_context.run
frame_count = [0]

def limited_run():
    while frame_count[0] < 3:
        # Process one frame
        os_context._process_frame()
        frame_count[0] += 1
        time.sleep(1/60)  # 60fps
    logger.info("Completed 3 frames")

os_context.run = limited_run

try:
    os_context.run()
except Exception as e:
    logger.error(f"Error during run: {e}")

elapsed = time.time() - start
logger.info(f"Step 8 PASSED - took {elapsed:.3f}s")

logger.info("=" * 60)
logger.info("FULL LAUNCH TEST PASSED - No hang detected!")
print("\nFull launch test passed! Check settings/logs/fulllaunchtest.log for details.")
