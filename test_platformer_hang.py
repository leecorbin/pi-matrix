#!/usr/bin/env python3
"""
Direct test of Platformer app launch to identify hang
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from matrixos.logger import get_logger

logger = get_logger("PlatformerTest")

logger.info("Starting Platformer direct import test")
logger.info("=" * 60)

# Test 1: Can we import the app framework?
logger.info("Test 1: Importing app_framework...")
start = time.time()
from matrixos.app_framework import App
elapsed = time.time() - start
logger.info(f"Test 1 PASSED - took {elapsed:.3f}s")

# Test 2: Can we import InputEvent?
logger.info("Test 2: Importing InputEvent...")
start = time.time()
from matrixos.input import InputEvent
elapsed = time.time() - start
logger.info(f"Test 2 PASSED - took {elapsed:.3f}s")

# Test 3: Can we load the platformer module?
logger.info("Test 3: Loading platformer/main.py module...")
start = time.time()

import importlib.util
spec = importlib.util.spec_from_file_location(
    "platformer_test",
    "examples/platformer/main.py"
)
logger.info("Test 3a: spec_from_file_location completed")

module = importlib.util.module_from_spec(spec)
logger.info("Test 3b: module_from_spec completed")

logger.info("Test 3c: About to exec_module (THIS IS WHERE IT MIGHT HANG)")
spec.loader.exec_module(module)
elapsed = time.time() - start
logger.info(f"Test 3 PASSED - exec_module took {elapsed:.3f}s")

# Test 4: Can we instantiate the game class?
logger.info("Test 4: Instantiating PlatformerGame class...")
start = time.time()
game = module.PlatformerGame()
elapsed = time.time() - start
logger.info(f"Test 4 PASSED - took {elapsed:.3f}s")

logger.info("=" * 60)
logger.info("ALL TESTS PASSED - No hang detected!")
print("\nAll tests passed! Check settings/logs/platformertest.log for details.")
