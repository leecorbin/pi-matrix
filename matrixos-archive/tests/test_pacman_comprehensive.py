#!/usr/bin/env python3
"""
Comprehensive Pac-Man Test Suite

Tests game physics, collision detection, sprite positioning, and movement.
Longer timeouts to ensure we capture all issues.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from matrixos.testing import TestRunner
from matrixos.input import InputEvent


def check_sprite_in_wall(sprite_pos, wall_color=(33, 33, 222), tolerance=20):
    """Check if sprite overlaps with a wall."""
    if not sprite_pos:
        return None
    
    x, y = sprite_pos
    # Check 8 pixels around sprite center for wall collision
    offsets = [(-3, 0), (3, 0), (0, -3), (0, 3), (-3, -3), (3, -3), (-3, 3), (3, 3)]
    
    wall_collisions = []
    for dx, dy in offsets:
        pixel = runner.pixel_at(int(x + dx), int(y + dy))
        if pixel:
            r, g, b = pixel
            # Check if it's a wall (blue-ish)
            if abs(r - wall_color[0]) < tolerance and \
               abs(g - wall_color[1]) < tolerance and \
               abs(b - wall_color[2]) < tolerance:
                wall_collisions.append((dx, dy))
    
    return wall_collisions


print("\n" + "=" * 80)
print("🎮 COMPREHENSIVE PAC-MAN TEST SUITE")
print("=" * 80)

# Use longer timeout for thorough testing (60 seconds)
runner = TestRunner("examples.pacman.main", max_duration=60.0)
runner.wait(3.0)

print("\n" + "=" * 80)
print("TEST 1: Initial Rendering")
print("=" * 80)

render_count = runner.display.render_count
print(f"Render count after 3s: {render_count}")
assert render_count >= 60, f"Expected at least 60 renders, got {render_count}"
print("✓ App is rendering at reasonable framerate")

print("\n" + "=" * 80)
print("TEST 2: Sprite Detection & Positioning")
print("=" * 80)

# Find Pac-Man (yellow)
pacman = runner.find_sprite((255, 255, 0), tolerance=20)
print(f"Pac-Man position: {pacman}")
assert pacman is not None, "❌ Could not find Pac-Man sprite!"
print("✓ Pac-Man sprite detected")

# Check if Pac-Man is in a wall
pacman_walls = check_sprite_in_wall(pacman)
if pacman_walls:
    print(f"⚠️  WARNING: Pac-Man appears to be overlapping walls at offsets: {pacman_walls}")
    print(f"   Position: {pacman}")
else:
    print("✓ Pac-Man is not overlapping walls")

# Find ghosts (multiple colors)
ghost_colors = {
    "Blinky (red)": (255, 0, 0),
    "Pinky (pink)": (255, 184, 255),
    "Inky (cyan)": (0, 255, 255),
    "Clyde (orange)": (255, 184, 82)
}

ghosts_found = {}
for name, color in ghost_colors.items():
    ghost = runner.find_sprite(color, tolerance=20)
    ghosts_found[name] = ghost
    if ghost:
        print(f"✓ {name} detected at {ghost}")
        # Check wall collision
        ghost_walls = check_sprite_in_wall(ghost)
        if ghost_walls:
            print(f"  ⚠️  WARNING: {name} overlapping walls at offsets: {ghost_walls}")
    else:
        print(f"⚠️  {name} not detected")

# Find walls (blue-ish - actual color is (33, 33, 222))
wall_pixels = runner.count_color((33, 33, 222), tolerance=20)
print(f"\nWall pixels detected: {wall_pixels}")
assert wall_pixels > 100, f"Expected to find maze walls, found {wall_pixels}"
print("✓ Maze walls detected")

# Find dots (white)
dot_pixels = runner.count_color((255, 255, 255), tolerance=20)
print(f"Dot pixels detected: {dot_pixels}")
print("✓ Dots detected" if dot_pixels > 50 else "⚠️  Few dots detected")

print("\n" + "=" * 80)
print("TEST 3: Pac-Man Movement (Extended Test)")
print("=" * 80)

pacman_before = runner.find_sprite((255, 255, 0), tolerance=20)
print(f"Pac-Man starting position: {pacman_before}")

# Try moving right
print("\n→ Testing RIGHT movement...")
runner.inject(InputEvent.RIGHT)
runner.wait(2.0)  # Longer wait to ensure movement happens

pacman_after_right = runner.find_sprite((255, 255, 0), tolerance=20)
print(f"Pac-Man position after RIGHT: {pacman_after_right}")

if pacman_before and pacman_after_right:
    dx = pacman_after_right[0] - pacman_before[0]
    dy = pacman_after_right[1] - pacman_before[1]
    print(f"Movement: dx={dx:.1f}, dy={dy:.1f}")
    
    if abs(dx) > 3 or abs(dy) > 3:
        print("✓ Pac-Man successfully moved!")
    else:
        print("❌ Pac-Man did NOT move significantly")
        print("   Expected dx > 3, got dx={:.1f}".format(dx))
else:
    print("❌ Could not detect Pac-Man before/after")

# Try moving down
print("\n↓ Testing DOWN movement...")
pacman_before_down = runner.find_sprite((255, 255, 0), tolerance=20)
runner.inject(InputEvent.DOWN)
runner.wait(2.0)

pacman_after_down = runner.find_sprite((255, 255, 0), tolerance=20)
if pacman_before_down and pacman_after_down:
    dy = pacman_after_down[1] - pacman_before_down[1]
    print(f"Movement: dy={dy:.1f}")
    if abs(dy) > 3:
        print("✓ Pac-Man successfully moved DOWN")
    else:
        print("❌ Pac-Man did NOT move DOWN significantly")

print("\n" + "=" * 80)
print("TEST 4: Ghost Movement")
print("=" * 80)

print("Waiting 4 seconds to observe ghost movement...")
ghosts_initial = {name: runner.find_sprite(color, tolerance=20) 
                  for name, color in ghost_colors.items()}

runner.wait(4.0)

ghosts_after = {name: runner.find_sprite(color, tolerance=20) 
                for name, color in ghost_colors.items()}

ghosts_moved = 0
for name in ghost_colors.keys():
    before = ghosts_initial.get(name)
    after = ghosts_after.get(name)
    
    if before and after:
        dx = after[0] - before[0]
        dy = after[1] - before[1]
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 3:
            print(f"✓ {name} moved {distance:.1f} pixels")
            ghosts_moved += 1
        else:
            print(f"❌ {name} did NOT move (distance: {distance:.1f})")
    else:
        print(f"⚠️  {name} detection issue")

if ghosts_moved > 0:
    print(f"\n✓ {ghosts_moved} ghost(s) are moving")
else:
    print("\n❌ NO ghosts are moving!")

print("\n" + "=" * 80)
print("TEST 5: Game State Updates")
print("=" * 80)

logs = runner.read_logs()

# Check for on_update calls
update_calls = logs.count("Pac-Man pos:")
print(f"on_update() debug lines found: {update_calls}")

if update_calls > 0:
    print("✓ on_update() is being called")
    # Show a sample
    for line in logs.split('\n'):
        if "Pac-Man pos:" in line:
            print(f"  Sample: {line.strip()}")
            break
else:
    print("❌ on_update() does NOT appear to be running!")

# Check for errors
errors = runner.get_error_logs()
if errors:
    print(f"\n⚠️  ERRORS DETECTED:")
    for error in errors.split('\n')[:5]:  # Show first 5
        print(f"  {error}")
else:
    print("\n✓ No errors in logs")

print("\n" + "=" * 80)
print("TEST 6: Animation Detection")
print("=" * 80)

is_animating = runner.display.is_changing(frames=30)
print(f"Display changing over 30 frames: {is_animating}")

if is_animating:
    print("✓ Game is animating (display is changing)")
else:
    print("⚠️  Game may be static (display not changing much)")

print("\n" + "=" * 80)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 80)

issues_found = []
recommendations = []

# Analyze findings
if pacman_walls:
    issues_found.append("Pac-Man spawns inside/overlapping walls")
    recommendations.append("Check initial spawn position in __init__() - may need to align to grid")

ghost_wall_issues = sum(1 for name, pos in ghosts_found.items() 
                        if pos and check_sprite_in_wall(pos))
if ghost_wall_issues > 0:
    issues_found.append(f"{ghost_wall_issues} ghost(s) overlapping walls")
    recommendations.append("Verify ghost spawn positions align with maze grid")

if ghosts_moved == 0:
    issues_found.append("Ghosts are not moving")
    recommendations.append("Check ghost AI update logic in on_update()")
    recommendations.append("Verify ghost direction vectors are being set")

if update_calls == 0:
    issues_found.append("on_update() not running")
    recommendations.append("Check on_activate() doesn't override base class without calling super()")

if issues_found:
    print("\n🐛 ISSUES FOUND:")
    for i, issue in enumerate(issues_found, 1):
        print(f"  {i}. {issue}")
    
    print("\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
else:
    print("\n✅ All tests passed! Game appears to be working correctly.")

print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)
