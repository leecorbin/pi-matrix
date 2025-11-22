#!/usr/bin/env python3
"""
Pac-Man Debugging Test Suite

Diagnoses why:
1. Pac-Man won't move
2. Ghosts won't move

Usage: python3 tests/test_pacman_debug.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from matrixos.testing import TestRunner
from matrixos.input import InputEvent
import time


def test_pacman_initial_state():
    """Test 1: Verify Pac-Man starts in correct state."""
    print("\n🔍 TEST 1: Initial State")
    print("=" * 60)
    
    runner = TestRunner("examples.pacman.main", max_duration=10.0)
    runner.wait(1.0)
    
    # Check that game rendered
    assert runner.display.render_count > 0, "Game should render"
    print(f"✓ Game rendered {runner.display.render_count} times")
    
    # Look for Pac-Man (yellow)
    yellow_pixels = runner.count_color((255, 255, 0), tolerance=20)
    print(f"✓ Found {yellow_pixels} yellow pixels (Pac-Man)")
    assert yellow_pixels > 0, "Pac-Man should be visible"
    
    # Look for ghosts (multiple colors)
    red_pixels = runner.count_color((255, 0, 0), tolerance=20)
    pink_pixels = runner.count_color((255, 184, 255), tolerance=20)
    cyan_pixels = runner.count_color((0, 255, 255), tolerance=20)
    orange_pixels = runner.count_color((255, 184, 82), tolerance=20)
    
    total_ghost_pixels = red_pixels + pink_pixels + cyan_pixels + orange_pixels
    print(f"✓ Found {total_ghost_pixels} ghost pixels (R:{red_pixels} P:{pink_pixels} C:{cyan_pixels} O:{orange_pixels})")
    
    # Look for maze (blue walls)
    blue_pixels = runner.count_color((33, 33, 222), tolerance=20)
    print(f"✓ Found {blue_pixels} blue pixels (maze walls)")
    assert blue_pixels > 100, "Maze should be visible"
    
    # Look for dots (white/cream)
    dot_pixels = runner.count_color((255, 200, 150), tolerance=20)
    print(f"✓ Found {dot_pixels} dot pixels")
    
    print("\n📍 Initial state check: PASSED")
    runner.stop()


def test_pacman_responds_to_input():
    """Test 2: Verify Pac-Man responds to arrow key input."""
    print("\n🔍 TEST 2: Input Response")
    print("=" * 60)
    
    runner = TestRunner("examples.pacman.main", max_duration=10.0)
    runner.wait(1.0)
    
    # Find Pac-Man's initial position
    pacman = runner.find_sprite((255, 255, 0), tolerance=20)
    assert pacman is not None, "Should find Pac-Man"
    initial_x, initial_y = pacman
    print(f"✓ Pac-Man initial position: ({initial_x}, {initial_y})")
    
    # Try moving RIGHT
    print("\n→ Testing RIGHT arrow...")
    runner.inject(InputEvent.RIGHT)
    runner.wait(2.0)  # Wait 2 seconds for movement
    
    pacman_after_right = runner.find_sprite((255, 255, 0), tolerance=20)
    assert pacman_after_right is not None, "Pac-Man should still exist"
    
    right_x, right_y = pacman_after_right
    print(f"  After RIGHT: ({right_x}, {right_y})")
    print(f"  Movement: dx={right_x - initial_x}, dy={right_y - initial_y}")
    
    if right_x > initial_x:
        print(f"  ✓ Pac-Man moved RIGHT by {right_x - initial_x} pixels")
    else:
        print(f"  ❌ Pac-Man did NOT move right (expected x > {initial_x}, got {right_x})")
    
    # Try moving DOWN
    print("\n↓ Testing DOWN arrow...")
    runner.inject(InputEvent.DOWN)
    runner.wait(2.0)
    
    pacman_after_down = runner.find_sprite((255, 255, 0), tolerance=20)
    down_x, down_y = pacman_after_down
    print(f"  After DOWN: ({down_x}, {down_y})")
    print(f"  Movement: dx={down_x - right_x}, dy={down_y - right_y}")
    
    if down_y > right_y:
        print(f"  ✓ Pac-Man moved DOWN by {down_y - right_y} pixels")
    else:
        print(f"  ❌ Pac-Man did NOT move down (expected y > {right_y}, got {down_y})")
    
    # Try moving LEFT
    print("\n← Testing LEFT arrow...")
    runner.inject(InputEvent.LEFT)
    runner.wait(2.0)
    
    pacman_after_left = runner.find_sprite((255, 255, 0), tolerance=20)
    left_x, left_y = pacman_after_left
    print(f"  After LEFT: ({left_x}, {left_y})")
    print(f"  Movement: dx={left_x - down_x}, dy={left_y - down_y}")
    
    if left_x < down_x:
        print(f"  ✓ Pac-Man moved LEFT by {down_x - left_x} pixels")
    else:
        print(f"  ❌ Pac-Man did NOT move left (expected x < {down_x}, got {left_x})")
    
    # Try moving UP
    print("\n↑ Testing UP arrow...")
    runner.inject(InputEvent.UP)
    runner.wait(2.0)
    
    pacman_after_up = runner.find_sprite((255, 255, 0), tolerance=20)
    up_x, up_y = pacman_after_up
    print(f"  After UP: ({up_x}, {up_y})")
    print(f"  Movement: dx={up_x - left_x}, dy={up_y - left_y}")
    
    if up_y < left_y:
        print(f"  ✓ Pac-Man moved UP by {left_y - up_y} pixels")
    else:
        print(f"  ❌ Pac-Man did NOT move up (expected y < {left_y}, got {up_y})")
    
    print("\n📍 Input response check: COMPLETED")
    print(f"   Total movement from start: dx={up_x - initial_x}, dy={up_y - initial_y}")
    
    runner.stop()


def test_pacman_continuous_movement():
    """Test 3: Check if Pac-Man continues moving after input."""
    print("\n🔍 TEST 3: Continuous Movement")
    print("=" * 60)
    
    runner = TestRunner("examples.pacman.main", max_duration=10.0)
    runner.wait(1.0)
    
    # Find initial position
    pacman_start = runner.find_sprite((255, 255, 0), tolerance=20)
    start_x, start_y = pacman_start
    print(f"✓ Pac-Man start: ({start_x}, {start_y})")
    
    # Press RIGHT once
    runner.inject(InputEvent.RIGHT)
    runner.wait(0.5)
    
    # Check position after 0.5s
    pacman_05s = runner.find_sprite((255, 255, 0), tolerance=20)
    x_05s, y_05s = pacman_05s
    print(f"✓ After 0.5s: ({x_05s}, {y_05s}) - moved {x_05s - start_x} pixels")
    
    # Wait another 0.5s WITHOUT pressing anything
    runner.wait(0.5)
    
    # Check if movement continued
    pacman_10s = runner.find_sprite((255, 255, 0), tolerance=20)
    x_10s, y_10s = pacman_10s
    print(f"✓ After 1.0s: ({x_10s}, {y_10s}) - moved {x_10s - start_x} pixels total")
    
    # Wait another 0.5s
    runner.wait(0.5)
    
    pacman_15s = runner.find_sprite((255, 255, 0), tolerance=20)
    x_15s, y_15s = pacman_15s
    print(f"✓ After 1.5s: ({x_15s}, {y_15s}) - moved {x_15s - start_x} pixels total")
    
    # Check if movement is continuous
    movement_05_10 = x_10s - x_05s
    movement_10_15 = x_15s - x_10s
    
    print(f"\nMovement analysis:")
    print(f"  0.0s → 0.5s: {x_05s - start_x} pixels")
    print(f"  0.5s → 1.0s: {movement_05_10} pixels")
    print(f"  1.0s → 1.5s: {movement_10_15} pixels")
    
    if movement_05_10 > 0 and movement_10_15 > 0:
        print(f"\n✓ Pac-Man continues moving after single input press")
    else:
        print(f"\n❌ Pac-Man stopped moving after input!")
        print(f"   This suggests movement isn't being maintained in on_update()")
    
    runner.stop()


def test_ghost_movement():
    """Test 4: Check if ghosts move over time."""
    print("\n🔍 TEST 4: Ghost Movement")
    print("=" * 60)
    
    runner = TestRunner("examples.pacman.main", max_duration=10.0)
    runner.wait(1.0)
    
    # Find all ghosts by color (we know there are 4)
    print("Looking for ghosts...")
    
    # Take snapshot at start
    initial_red = runner.count_color((255, 0, 0), tolerance=20)
    initial_pink = runner.count_color((255, 184, 255), tolerance=20)
    initial_cyan = runner.count_color((0, 255, 255), tolerance=20)
    initial_orange = runner.count_color((255, 184, 82), tolerance=20)
    
    print(f"Initial ghost pixels: R={initial_red}, P={initial_pink}, C={initial_cyan}, O={initial_orange}")
    
    # Wait 3 seconds
    print("\nWaiting 3 seconds for ghosts to move...")
    runner.wait(3.0)
    
    # Check positions again
    final_red = runner.count_color((255, 0, 0), tolerance=20)
    final_pink = runner.count_color((255, 184, 255), tolerance=20)
    final_cyan = runner.count_color((0, 255, 255), tolerance=20)
    final_orange = runner.count_color((255, 184, 82), tolerance=20)
    
    print(f"Final ghost pixels: R={final_red}, P={final_pink}, C={final_cyan}, O={final_orange}")
    
    # Check if pixel counts changed (would indicate movement)
    red_changed = abs(final_red - initial_red) > 5
    pink_changed = abs(final_pink - initial_pink) > 5
    cyan_changed = abs(final_cyan - initial_cyan) > 5
    orange_changed = abs(final_orange - initial_orange) > 5
    
    any_changed = red_changed or pink_changed or cyan_changed or orange_changed
    
    print(f"\nMovement detected:")
    print(f"  Red ghost: {'YES' if red_changed else 'NO'} (change: {final_red - initial_red})")
    print(f"  Pink ghost: {'YES' if pink_changed else 'NO'} (change: {final_pink - initial_pink})")
    print(f"  Cyan ghost: {'YES' if cyan_changed else 'NO'} (change: {final_cyan - initial_cyan})")
    print(f"  Orange ghost: {'YES' if orange_changed else 'NO'} (change: {final_orange - initial_orange})")
    
    if any_changed:
        print(f"\n✓ At least one ghost moved")
    else:
        print(f"\n❌ No ghosts moved!")
        print(f"   This suggests ghost.update() isn't working properly")
    
    runner.stop()


def test_frame_rate():
    """Test 5: Check if game is updating at proper frame rate."""
    print("\n🔍 TEST 5: Frame Rate")
    print("=" * 60)
    
    runner = TestRunner("examples.pacman.main", max_duration=10.0)
    runner.wait(2.0)
    
    render_count = runner.display.render_count
    print(f"✓ Rendered {render_count} frames in 2 seconds")
    print(f"  Average: {render_count / 2.0:.1f} fps")
    
    if render_count >= 50:  # At least 25fps
        print(f"  ✓ Frame rate is good (target: 60fps)")
    else:
        print(f"  ⚠️  Frame rate is low (got {render_count/2:.1f}fps, expected ~60fps)")
    
    runner.stop()


def test_on_update_called():
    """Test 6: Verify on_update is being called."""
    print("\n🔍 TEST 6: on_update() Execution")
    print("=" * 60)
    
    runner = TestRunner("examples.pacman.main", max_duration=10.0)
    runner.wait(2.0)
    
    # Check logs for debug output from on_update
    logs = runner.read_logs()
    
    if "Pac-Man pos:" in logs:
        print("✓ Found debug output from on_update()")
        # Extract the debug info
        for line in logs.split('\n'):
            if "Pac-Man pos:" in line or "Ghost 0 pos:" in line:
                print(f"  {line.strip()}")
    else:
        print("❌ No debug output from on_update() found in logs")
        print("   This suggests on_update() might not be running")
    
    print(f"\n✓ Checking for errors...")
    errors = runner.get_error_logs()
    if errors:
        print(f"❌ Found errors in logs:")
        for line in errors.split('\n')[:10]:  # First 10 error lines
            print(f"  {line}")
    else:
        print(f"✓ No errors in logs")
    
    runner.stop()


def test_collision_detection():
    """Test 7: Check if collision detection works."""
    print("\n🔍 TEST 7: Collision Detection")
    print("=" * 60)
    
    runner = TestRunner("examples.pacman.main", max_duration=10.0)
    runner.wait(1.0)
    
    # Get initial dot count
    initial_dots = runner.count_color((255, 200, 150), tolerance=20)
    print(f"✓ Initial dots: {initial_dots} pixels")
    
    # Try to move Pac-Man to eat dots
    print("\nMoving Pac-Man to eat dots...")
    runner.inject(InputEvent.RIGHT)
    runner.wait(2.0)
    
    # Check if dot count decreased
    final_dots = runner.count_color((255, 200, 150), tolerance=20)
    print(f"✓ Final dots: {final_dots} pixels")
    
    dots_eaten = initial_dots - final_dots
    print(f"\nDots eaten: {dots_eaten} pixels")
    
    if dots_eaten > 0:
        print(f"✓ Collision detection working (dots were eaten)")
    else:
        print(f"⚠️  No dots eaten (either Pac-Man didn't move or collision detection not working)")
    
    runner.stop()


def run_all_tests():
    """Run all diagnostic tests."""
    print("\n" + "=" * 60)
    print("🎮 PAC-MAN DIAGNOSTIC TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Initial State", test_pacman_initial_state),
        ("Input Response", test_pacman_responds_to_input),
        ("Continuous Movement", test_pacman_continuous_movement),
        ("Ghost Movement", test_ghost_movement),
        ("Frame Rate", test_frame_rate),
        ("on_update() Execution", test_on_update_called),
        ("Collision Detection", test_collision_detection),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, "✓ PASSED"))
        except AssertionError as e:
            results.append((name, f"❌ FAILED: {e}"))
        except Exception as e:
            results.append((name, f"💥 ERROR: {e}"))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        print(f"{result:40} - {name}")
    
    passed = sum(1 for _, r in results if "✓" in r)
    total = len(results)
    
    print("=" * 60)
    print(f"Result: {passed}/{total} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
