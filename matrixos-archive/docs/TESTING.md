# MatrixOS Testing Guide

## Overview

MatrixOS includes a **comprehensive, integrated testing framework** designed for automated testing of LED matrix applications. Think of it as "Puppeteer for MatrixOS" - full automation of display rendering and input simulation.

**Philosophy:** Retro aesthetic meets modern engineering practices. While MatrixOS looks and feels like a retro system, it's built with modern testing and quality assurance in mind.

## Quick Start

```python
from matrixos.testing import TestRunner

def test_my_app():
    # Start app in headless mode
    runner = TestRunner("examples.platformer.main", max_duration=10.0)
    
    # Wait for initial render
    runner.wait(1.0)
    
    # Verify app rendered
    assert runner.display.render_count >= 30, "App should render at 30+ fps"
    
    # Find player sprite (blue color)
    player = runner.find_sprite((0, 150, 255), tolerance=10)
    assert player is not None, "Player should be visible"
    print(f"Player at position: {player}")
    
    # Simulate jumping
    runner.inject(' ')  # Space bar
    runner.wait(1.0)
    
    # Verify player moved vertically
    new_player = runner.find_sprite((0, 150, 255), tolerance=10)
    assert new_player[1] != player[1], "Player should jump"
    
    # Check for errors in logs
    runner.assert_no_errors_logged()

if __name__ == "__main__":
    test_my_app()
    print("✓ Test passed!")
```

Run it:
```bash
python3 test_my_app.py
```

## Architecture

The testing framework consists of four key components:

```
matrixos/testing/
├── display_adapter.py   # HeadlessDisplay - captures rendering
├── input_simulator.py   # InputSimulator - injects events
├── assertions.py        # Assertion library
└── runner.py           # TestRunner - high-level API
```

### 1. HeadlessDisplay

Replaces the terminal renderer with an in-memory buffer that:
- ✅ Captures all drawing operations (pixels, lines, text, etc.)
- ✅ Stores display state as Python lists (no numpy!)
- ✅ Never outputs to terminal/stdout
- ✅ Provides inspection methods (find colors, count pixels, etc.)

### 2. InputSimulator

Programmatically injects input events:
- ✅ Frame-perfect timing control
- ✅ Event sequences with delays
- ✅ Repeated inputs (hold button)
- ✅ All InputEvent types supported

### 3. TestRunner

High-level API that ties everything together:
- ✅ Loads apps in headless mode
- ✅ Manages event loop
- ✅ Provides helper methods (wait, inject, find_sprite)
- ✅ Integrates log inspection
- ✅ Tracks timing and FPS

### 4. Assertions

Rich assertion library for common test patterns:
- ✅ Pixel color verification
- ✅ Text rendering checks
- ✅ Color counting
- ✅ Render count verification
- ✅ Animation detection

## Core Features

### Display Buffer Inspection

**Get pixel colors:**
```python
runner = TestRunner("examples.myapp.main")
runner.wait(0.5)

# Get single pixel
color = runner.pixel_at(64, 64)
print(f"Center pixel: {color}")

# Get specific region
for y in range(10, 20):
    for x in range(10, 20):
        color = runner.pixel_at(x, y)
```

**Count colors:**
```python
# Count exact color matches
sky_pixels = runner.count_color((50, 100, 150))

# Count with tolerance (handles anti-aliasing)
sky_pixels = runner.count_color((50, 100, 150), tolerance=5)
```

**Find sprites:**
```python
# Find centroid of all blue pixels (player)
player_pos = runner.find_sprite((0, 150, 255), tolerance=10)
if player_pos:
    x, y = player_pos
    print(f"Player at ({x}, {y})")

# Find all connected regions (platforms)
platforms = runner.display.find_blobs((150, 75, 0), min_size=50)
print(f"Found {len(platforms)} platforms")
```

**Animation detection:**
```python
# Check if display is changing
if runner.display.is_changing(frames=3):
    print("App is animating")
else:
    print("App is static")
```

**Snapshot comparison (visual regression):**
```python
# Take initial snapshot
runner.snapshot("before_action")

# Do something
runner.inject(InputEvent.RIGHT)
runner.wait(1.0)

# Compare (returns similarity 0.0-1.0)
runner.assert_snapshot_matches("before_action", tolerance=0.05)
```

### Input Simulation

**Single events:**
```python
from matrixos.input import InputEvent

# Inject immediately
runner.inject(InputEvent.RIGHT)
runner.inject(' ')  # Space bar (ACTION)
runner.inject('A')  # Letter key
```

**Sequences:**
```python
# Inject sequence with delays
runner.inject_sequence([
    InputEvent.RIGHT,
    InputEvent.RIGHT,
    InputEvent.ACTION
], delay=0.1)  # 100ms between events
```

**Repeated inputs:**
```python
# Hold button (repeat 10 times)
runner.inject_repeat(InputEvent.RIGHT, count=10, delay=0.05)
```

**Advanced timing:**
```python
from matrixos.testing import InputSimulator

sim = InputSimulator()

# Schedule event for specific frame
sim.schedule_event(InputEvent.JUMP, at_frame=60)  # 1 second at 60fps

# Or after delay
sim.schedule_event(InputEvent.FIRE, after_delay=2.0)  # 2 seconds
```

### Waiting and Timing

**Wait for duration:**
```python
runner.wait(1.5)  # Wait 1.5 seconds (continues event loop)
```

**Wait specific frame count:**
```python
runner.wait_frames(60)  # Wait exactly 60 frames (1 second at 60fps)
```

**Wait for condition:**
```python
# Wait until player reaches x > 100
runner.wait_until(
    lambda: runner.find_sprite((0, 255, 0))[0] > 100,
    timeout=5.0
)
```

**Wait for text:**
```python
# Wait until "GAME OVER" appears
runner.wait_for_text("GAME OVER", timeout=10.0)
```

**Wait for animation:**
```python
# Wait until display starts changing
runner.wait_for_animation(timeout=5.0)
```

**Wait for stillness:**
```python
# Wait until display stops changing
runner.wait_for_still(duration=0.5)
```

### Log Inspection

**Read logs:**
```python
# Read all logs since app started
logs = runner.read_logs()

# Read only logs since test started
logs = runner.read_logs(since_test_start=True)

# Read specific app's logs
logs = runner.read_logs(app_name="platformer")
```

**Search logs:**
```python
# Check if log contains text
if runner.log_contains("Player jumped"):
    print("Jump was logged")

# Count occurrences
jump_count = runner.count_log_occurrences("Player jumped")
```

**Get log lines:**
```python
# Get as list of strings
lines = runner.get_log_lines()
for line in lines[-10:]:  # Last 10 lines
    print(line)
```

**Error detection:**
```python
# Get all error lines
errors = runner.get_error_logs()
if errors:
    print(f"Found {len(errors)} errors:")
    for error in errors:
        print(f"  {error}")

# Get warnings
warnings = runner.get_warning_logs()
```

**Assertions:**
```python
# Assert log contains specific text
runner.assert_log_contains("Session started")

# Assert no errors logged
runner.assert_no_errors_logged()

# Assert no warnings
assert len(runner.get_warning_logs()) == 0
```

**Debug failures:**
```python
# Print recent logs when test fails
try:
    assert player_pos[0] > 100
except AssertionError:
    runner.print_recent_logs(lines=20)
    raise
```

## Common Test Patterns

### Test Game Rendering

```python
def test_game_rendering():
    runner = TestRunner("examples.space_invaders.main", max_duration=10.0)
    runner.wait(1.0)
    
    # Verify app renders
    assert runner.display.render_count >= 30
    
    # Verify aliens are drawn (green pixels)
    alien_pixels = runner.count_color((0, 255, 0), tolerance=10)
    assert alien_pixels > 100, "Should have many alien pixels"
    
    # Verify player ship (white)
    player = runner.find_sprite((255, 255, 255), tolerance=10)
    assert player is not None
    assert player[1] > 100, "Player should be near bottom"
```

### Test Player Movement

```python
def test_player_movement():
    runner = TestRunner("examples.platformer.main", max_duration=10.0)
    runner.wait(0.5)
    
    # Get initial position
    initial_pos = runner.find_sprite((0, 150, 255), tolerance=10)
    assert initial_pos is not None
    
    # Move right
    runner.inject_repeat(InputEvent.RIGHT, count=20)
    runner.wait(1.0)
    
    # Verify movement
    new_pos = runner.find_sprite((0, 150, 255), tolerance=10)
    assert new_pos[0] > initial_pos[0], "Player should move right"
    print(f"Player moved from x={initial_pos[0]} to x={new_pos[0]}")
```

### Test Jump Mechanics

```python
def test_jump():
    runner = TestRunner("examples.platformer.main", max_duration=15.0)
    runner.wait(0.5)
    
    # Get ground position
    ground_y = runner.find_sprite((0, 150, 255))[1]
    
    # Jump
    runner.inject(' ')
    runner.wait(0.5)
    
    # Should be in air (lower y = higher on screen)
    air_y = runner.find_sprite((0, 150, 255))[1]
    assert air_y < ground_y - 30, "Player should jump up"
    
    # Wait for landing
    runner.wait(1.5)
    
    # Should be back on ground
    land_y = runner.find_sprite((0, 150, 255))[1]
    assert abs(land_y - ground_y) < 5, "Player should land"
```

### Test Text Display

```python
def test_score_display():
    runner = TestRunner("examples.game.main", max_duration=10.0)
    runner.wait(0.5)
    
    # Check if score text was drawn
    assert runner.text_visible("Score:")
    
    # Or check call log
    assert runner.display.text_was_drawn("Score:")
    
    # Get all text calls
    text_calls = runner.display.get_text_calls()
    print(f"Text drawn: {text_calls}")
```

### Test Collision Detection

```python
def test_bullet_hits_enemy():
    runner = TestRunner("examples.space_invaders.main", max_duration=10.0)
    runner.wait(0.5)
    
    # Count initial aliens
    initial_aliens = len(runner.display.find_blobs((0, 255, 0), min_size=10))
    
    # Fire multiple shots
    runner.inject_repeat(' ', count=10, delay=0.2)
    runner.wait(3.0)
    
    # Count remaining aliens
    final_aliens = len(runner.display.find_blobs((0, 255, 0), min_size=10))
    
    # Should have destroyed at least one
    assert final_aliens < initial_aliens, "Aliens should be destroyed"
```

### Test Animation

```python
def test_animation_running():
    runner = TestRunner("examples.demo.main", max_duration=10.0)
    runner.wait(0.5)
    
    # Take snapshot
    snapshot1 = runner.display.snapshot()
    
    # Wait a bit
    runner.wait(0.5)
    
    # Take another snapshot
    snapshot2 = runner.display.snapshot()
    
    # Should be different (animation running)
    similarity = runner.display.compare(snapshot1)
    assert similarity < 0.95, "Display should be animating"
```

### Test Error Handling

```python
def test_invalid_input():
    runner = TestRunner("examples.myapp.main", max_duration=10.0)
    runner.wait(0.5)
    
    # Send invalid input
    runner.inject('X')  # Not a valid key for this app
    runner.wait(0.5)
    
    # App should not crash
    assert runner.display.render_count > 0
    
    # Should not log errors
    runner.assert_no_errors_logged()
```

## Advanced Techniques

### Sprite Tracking Over Time

```python
def test_smooth_movement():
    runner = TestRunner("examples.platformer.main", max_duration=10.0)
    runner.wait(0.5)
    
    # Track player position over multiple frames
    positions = []
    
    runner.inject(InputEvent.RIGHT)  # Start moving
    
    for _ in range(10):
        runner.wait(0.1)
        pos = runner.find_sprite((0, 150, 255), tolerance=10)
        if pos:
            positions.append(pos[0])
    
    # Verify smooth progression (x always increasing)
    for i in range(len(positions) - 1):
        assert positions[i+1] > positions[i], f"Movement not smooth at frame {i}"
```

### Multi-Object Tracking

```python
def test_multiple_enemies():
    runner = TestRunner("examples.space_invaders.main", max_duration=10.0)
    runner.wait(1.0)
    
    # Find all enemy blobs
    enemies = runner.display.find_blobs((0, 255, 0), min_size=10)
    
    # Verify grid formation
    assert len(enemies) > 10, "Should have multiple enemies"
    
    # Get centroids
    positions = [runner.display.get_centroid(blob) for blob in enemies]
    
    # Verify they're in rows
    y_positions = [pos[1] for pos in positions]
    unique_rows = len(set(int(y/10) for y in y_positions))  # Group by 10px rows
    assert unique_rows >= 3, "Enemies should be in multiple rows"
```

### Performance Testing

```python
def test_maintains_framerate():
    runner = TestRunner("examples.game.main", max_duration=5.0)
    runner.wait(5.0)  # Run for 5 seconds
    
    # Check FPS
    fps = runner.get_fps()
    assert fps >= 50, f"FPS too low: {fps} (expected >= 50)"
    
    # Check render consistency
    renders = runner.display.render_count
    expected = 60 * 5  # 60fps * 5 seconds
    assert renders >= expected * 0.9, f"Only {renders} renders in 5s (expected ~{expected})"
```

### Visual Regression Testing

```python
def test_menu_layout():
    runner = TestRunner("examples.menu.main", max_duration=5.0)
    runner.wait(1.0)
    
    # Take snapshot of menu
    runner.snapshot("main_menu")
    
    # Navigate away and back
    runner.inject(InputEvent.RIGHT)
    runner.wait(0.5)
    runner.inject(InputEvent.LEFT)
    runner.wait(0.5)
    
    # Should look the same
    runner.assert_snapshot_matches("main_menu", tolerance=0.01)
```

## Running Tests

### Individual Tests

```bash
python3 tests/my_test.py
```

### Test Suites

MatrixOS includes three test suites:

```bash
# Quick sanity check (2 tests, ~20 seconds)
python3 tests/smoke_test.py

# Comprehensive feature tests (8 tests, ~90 seconds)
python3 tests/advanced_test.py

# Log integration tests (7 tests, ~70 seconds)
python3 tests/test_log_integration.py
```

### All Tests

```bash
# Run everything
python3 tests/smoke_test.py && \
python3 tests/advanced_test.py && \
python3 tests/test_log_integration.py
```

## Best Practices

### 1. Use Realistic Test Data

❌ **Bad:**
```python
assert runner.display.render_count == 60  # Assumes perfect 60fps
```

✅ **Good:**
```python
assert runner.display.render_count >= 30  # Allows for variation
```

### 2. Use Color Tolerance

❌ **Bad:**
```python
player = runner.find_sprite((0, 150, 255), tolerance=0)  # Exact match only
```

✅ **Good:**
```python
player = runner.find_sprite((0, 150, 255), tolerance=10)  # Handles anti-aliasing
```

### 3. Set Appropriate Timeouts

❌ **Bad:**
```python
runner = TestRunner("examples.myapp.main", max_duration=1.0)  # Too short!
```

✅ **Good:**
```python
runner = TestRunner("examples.myapp.main", max_duration=10.0)  # Reasonable
```

### 4. Always Check Logs

✅ **Good:**
```python
def test_my_feature():
    runner = TestRunner("examples.myapp.main")
    # ... test logic ...
    
    # Always check for errors
    runner.assert_no_errors_logged()
```

### 5. Use Descriptive Assertions

❌ **Bad:**
```python
assert player[0] > 100  # What does this mean?
```

✅ **Good:**
```python
assert player[0] > 100, f"Player should move right: x={player[0]}"
```

## Limitations

### What Testing CAN'T Detect

1. **Visual Quality** - Tests verify pixels exist, not if they look good
2. **Performance Feel** - 60fps technically met but feels laggy
3. **Audio** - No audio testing yet
4. **Hardware Issues** - Tests run headless, may miss LED matrix issues
5. **User Experience** - Controls work ≠ controls feel good

### Current Constraints

- **Display Size**: 128×128 (tests must use this size for accuracy)
- **Single App**: One app per test (can't test app switching yet)
- **Synchronous Only**: Apps must be synchronous (no threading yet)
- **Pure Python**: No numpy (intentional - minimal dependencies)

## Philosophy

MatrixOS testing embodies the project's philosophy:

**Retro aesthetic, modern practices:**
- 🎮 Retro: ZX Spectrum font, LED matrix aesthetic, 8-bit games
- 🔬 Modern: Automated testing, log inspection, CI/CD ready

**Minimal dependencies, maximum functionality:**
- Zero numpy (pure Python lists)
- Only Pillow for production
- Testing uses stdlib only

**Easy to understand, powerful when needed:**
- Simple API for common tasks (`find_sprite`, `inject`, `wait`)
- Advanced features available (`find_blobs`, `wait_until`, log inspection)
- No magic - everything is explicit

## Troubleshooting

### Test Times Out

```python
# Increase max_duration
runner = TestRunner("examples.myapp.main", max_duration=30.0)
```

### Can't Find Sprite

```python
# Increase tolerance
player = runner.find_sprite((0, 150, 255), tolerance=20)

# Or check actual colors
runner.wait(0.5)
print(f"Center pixel: {runner.pixel_at(64, 64)}")
for y in range(0, 128, 10):
    for x in range(0, 128, 10):
        print(f"({x},{y}): {runner.pixel_at(x, y)}")
```

### Logs Not Found

```python
# Use since_test_start=False to read all logs
logs = runner.read_logs(since_test_start=False)
print(logs)

# Or print recent logs
runner.print_recent_logs(lines=50)
```

### Test Flaky (Sometimes Passes)

```python
# Add more wait time
runner.wait(2.0)  # Instead of 0.5

# Use wait_until for conditions
runner.wait_until(
    lambda: runner.find_sprite((0, 255, 0)) is not None,
    timeout=5.0
)
```

## Future Enhancements

Planned improvements:

- [ ] **YAML Test Specs** - Non-programmers can write simple tests
- [ ] **Visual Diff Tool** - Show snapshot differences as images
- [ ] **Parallel Execution** - Run tests concurrently
- [ ] **Coverage Reports** - Track which app code is tested
- [ ] **Performance Benchmarks** - Track FPS over time
- [ ] **CI/CD Integration** - GitHub Actions workflow
- [ ] **Multi-App Tests** - Test app switching
- [ ] **Async Support** - Test threaded background tasks

## Contributing Tests

When adding new tests:

1. **Follow Naming Conventions**
   - `test_*.py` for test files
   - `test_*()` for test functions

2. **Use Descriptive Names**
   - ❌ `test_1()`, `test_basic()`
   - ✅ `test_player_jumps()`, `test_collision_detection()`

3. **Keep Tests Independent**
   - Each test should run standalone
   - Don't rely on global state

4. **Document Complex Tests**
   ```python
   def test_advanced_physics():
       """
       Verify gravity and jump mechanics work correctly.
       
       Tests:
       - Player falls when not on platform
       - Jump reaches expected height
       - Landing returns to ground level
       """
       # ... test code ...
   ```

5. **Check Logs**
   - Always call `runner.assert_no_errors_logged()`

## Conclusion

The MatrixOS testing framework provides comprehensive automation for LED matrix apps while maintaining the project's philosophy of simplicity and minimal dependencies. It's production-ready, well-documented, and designed to grow with the project.

**Remember:** Testing is about confidence, not perfection. Write tests that catch real bugs, and don't over-engineer. The framework is a tool to help you build better apps, not a burden to maintain.

Happy testing! 🧪✨
