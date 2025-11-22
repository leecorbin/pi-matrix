#!/usr/bin/env python3
"""
Quick Pac-Man Bug Report

Identifies the root causes of Pac-Man not working.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from matrixos.testing import TestRunner
from matrixos.input import InputEvent


print("\n" + "=" * 70)
print("🐛 PAC-MAN BUG DIAGNOSIS")
print("=" * 70)

runner = TestRunner("examples.pacman.main", max_duration=5.0)
runner.wait(2.0)

logs = runner.read_logs()

print("\n1️⃣  CHECKING: Does on_update() run?")
print("-" * 70)
if "Pac-Man pos:" in logs:
    print("✓ YES - on_update() is running")
    # Extract positions
    for line in logs.split('\n'):
        if "Pac-Man pos:" in line:
            print(f"  {line.strip()}")
            break
else:
    print("❌ NO - on_update() is NOT running!")
    print("   This means the game loop isn't updating game state.")

print("\n2️⃣  CHECKING: Initial state in render()")
print("-" * 70)
if "First render" in logs:
    for line in logs.split('\n'):
        if "First render" in line or "Ghost Blinky" in line:
            print(f"  {line.strip()}")
    print("✓ render() is being called")
else:
    print("⚠️  No render debug output found")

print("\n3️⃣  CHECKING: Movement after input")
print("-" * 70)
pacman_before = runner.find_sprite((255, 255, 0), tolerance=20)
print(f"Pac-Man position before input: {pacman_before}")

runner.inject(InputEvent.RIGHT)
runner.wait(1.0)

pacman_after = runner.find_sprite((255, 255, 0), tolerance=20)
print(f"Pac-Man position after RIGHT:  {pacman_after}")

if pacman_before and pacman_after:
    dx = pacman_after[0] - pacman_before[0]
    dy = pacman_after[1] - pacman_before[1]
    print(f"Movement: dx={dx:.1f}, dy={dy:.1f}")
    
    if abs(dx) < 1 and abs(dy) < 1:
        print("❌ Pac-Man did NOT move!")
    else:
        print("✓ Pac-Man moved")

print("\n" + "=" * 70)
print("🔍 ROOT CAUSE ANALYSIS")
print("=" * 70)

# Read the actual Pac-Man code to check for issues
with open('examples/pacman/main.py', 'r') as f:
    code = f.read()
    
    # Check on_activate
    if 'def on_activate(self):\n        """App activated."""\n        pass' in code:
        print("\n❌ BUG FOUND: on_activate() is empty!")
        print("   Location: class PacManGame, line ~347")
        print("   Problem: This overrides the base class which sets self.dirty = True")
        print("   Fix: Either remove on_activate() or call super().on_activate()")
    
    # Check on_update
    if 'def on_update(self, delta_time):' in code:
        print("\n✓ on_update() is defined")
        # But does on_update set dirty?
        on_update_section = code.split('def on_update(self, delta_time):')[1].split('def ')[0]
        if 'self.dirty = True' in on_update_section:
            print("  ✓ on_update() sets self.dirty = True")
        else:
            print("  ⚠️  on_update() doesn't consistently set self.dirty")

print("\n" + "=" * 70)
print("💡 RECOMMENDED FIXES")
print("=" * 70)
print("""
1. Remove empty on_activate() method (lines ~347-349)
   OR change it to:
   
   def on_activate(self):
       super().on_activate()  # This sets self.dirty = True
       # Any other activation code here

2. The base App class already sets self.dirty = True in on_activate(),
   but PacManGame overrides it with an empty method, breaking the pattern.
""")

print("=" * 70)
