# MatrixOS Automated Testing Framework

## Overview

This is a **headless testing system** that lets you:
- Test apps without a terminal display
- Simulate input events programmatically
- Capture and verify display output
- Create automated test suites
- Catch rendering bugs before deployment

Think of it as **Puppeteer for MatrixOS** - full automation of the display and input system.

## Architecture

### 1. Headless Display Adapter

Replace the terminal renderer with a buffer-only renderer that:
- Captures all drawing operations
- Stores the final display state as a 2D array
- Never outputs to terminal/stdout
- Can serialize display state for comparisons

### 2. Input Event Simulator

Programmatically inject input events:
- Arrow keys (UP, DOWN, LEFT, RIGHT)
- Action buttons (OK, ACTION, BACK)
- Timing control (inject events at specific frames)

### 3. Test Assertions

Verify display state:
- Check pixel colors at specific coordinates
- Verify text rendering
- Count objects on screen
- Compare against golden screenshots

## Implementation Plan

### Phase 1: Headless Renderer (Easy)

Create `matrixos/testing/headless_display.py`:

```python
class HeadlessDisplay:
    """Display adapter that captures output without rendering."""
    
    def __init__(self, width=128, height=128):
        self.width = width
        self.height = height
        self.buffer = self._create_buffer()
        self.show_count = 0  # Track number of renders
    
    def _create_buffer(self):
        """Create empty buffer."""
        return [[(0, 0, 0) for _ in range(self.width)] 
                for _ in range(self.height)]
    
    def show(self, renderer=None, clear_screen=True):
        """Capture show() call without rendering."""
        self.show_count += 1
        # Don't print anything!
    
    def get_pixel(self, x, y):
        """Get pixel value at coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.buffer[y][x]
        return None
    
    def get_buffer_snapshot(self):
        """Get copy of entire buffer."""
        return [row[:] for row in self.buffer]
    
    def count_pixels(self, color):
        """Count pixels of a specific color."""
        count = 0
        for row in self.buffer:
            for pixel in row:
                if pixel == color:
                    count += 1
        return count
    
    def find_text(self, text):
        """Check if text appears in buffer (naive search)."""
        # Would need to check against font rendering
        pass
```

### Phase 2: Input Simulator (Easy)

Create `matrixos/testing/input_simulator.py`:

```python
from matrixos.input import InputEvent

class InputSimulator:
    """Simulate keyboard input programmatically."""
    
    def __init__(self):
        self.event_queue = []
        self.frame = 0
    
    def schedule_event(self, key, at_frame=None):
        """Schedule an input event."""
        if at_frame is None:
            at_frame = self.frame + 1
        self.event_queue.append((at_frame, key))
    
    def get_key(self, timeout=0.0):
        """Get next scheduled event if frame matches."""
        for i, (frame, key) in enumerate(self.event_queue):
            if frame == self.frame:
                self.event_queue.pop(i)
                return InputEvent(key)
        return None
    
    def advance_frame(self):
        """Move to next frame."""
        self.frame += 1
    
    def inject_sequence(self, keys, delay=1):
        """Schedule a sequence of keys with delays."""
        for i, key in enumerate(keys):
            self.schedule_event(key, self.frame + i * delay)
```

### Phase 3: Test Runner (Medium)

Create `matrixos/testing/test_runner.py`:

```python
import sys
from matrixos.app_framework import AppFramework
from matrixos.testing.headless_display import HeadlessDisplay
from matrixos.testing.input_simulator import InputSimulator

class TestRunner:
    """Run automated tests on MatrixOS apps."""
    
    def __init__(self, width=128, height=128):
        self.display = HeadlessDisplay(width, height)
        self.input = InputSimulator()
        self.framework = AppFramework(
            self.display, 
            self.input,
            headless=True
        )
    
    def run_test(self, app_module, test_script):
        """
        Run a test script on an app.
        
        Args:
            app_module: Path to app's main.py (e.g., "examples.platformer.main")
            test_script: Function that defines the test
        """
        # Import and run the app
        module = __import__(app_module, fromlist=['run'])
        
        # Run test script which schedules inputs and assertions
        test_script(self)
        
        # Run the app with scheduled inputs
        module.run(self.framework)
    
    def assert_pixel(self, x, y, color, message=""):
        """Assert pixel has expected color."""
        actual = self.display.get_pixel(x, y)
        if actual != color:
            raise AssertionError(
                f"{message}\nExpected {color} at ({x},{y}), got {actual}"
            )
    
    def assert_render_count(self, expected, message=""):
        """Assert number of renders."""
        actual = self.display.show_count
        if actual != expected:
            raise AssertionError(
                f"{message}\nExpected {expected} renders, got {actual}"
            )
    
    def run_for_frames(self, count):
        """Run simulation for N frames."""
        for _ in range(count):
            self.framework.tick()
            self.input.advance_frame()
```

### Phase 4: Example Tests (Easy)

Create `tests/test_platformer.py`:

```python
#!/usr/bin/env python3
from matrixos.testing.test_runner import TestRunner
from matrixos.input import InputEvent

def test_platformer_launches():
    """Test that Platformer launches and renders."""
    runner = TestRunner()
    
    def test_script(runner):
        # App should render on activation
        pass
    
    runner.run_test("examples.platformer.main", test_script)
    
    # Should have rendered at least once
    runner.assert_render_count(
        expected=1,
        message="Platformer should render on launch"
    )
    print("✓ Platformer launches successfully")

def test_platformer_movement():
    """Test that player moves with arrow keys."""
    runner = TestRunner()
    
    def test_script(runner):
        # Schedule: RIGHT key press after 10 frames
        runner.input.schedule_event(InputEvent.RIGHT, at_frame=10)
        runner.run_for_frames(20)
    
    runner.run_test("examples.platformer.main", test_script)
    
    # Check that player sprite moved right
    # (Would need to know player color and track position)
    print("✓ Platformer player movement works")

def test_platformer_no_crash():
    """Test that Platformer doesn't crash for 100 frames."""
    runner = TestRunner()
    
    def test_script(runner):
        # Inject random inputs
        runner.input.schedule_event(InputEvent.RIGHT, at_frame=10)
        runner.input.schedule_event(InputEvent.ACTION, at_frame=20)
        runner.input.schedule_event(InputEvent.LEFT, at_frame=30)
        runner.run_for_frames(100)
    
    try:
        runner.run_test("examples.platformer.main", test_script)
        print("✓ Platformer runs 100 frames without crashing")
    except Exception as e:
        print(f"✗ Platformer crashed: {e}")
        raise

if __name__ == "__main__":
    test_platformer_launches()
    test_platformer_movement()
    test_platformer_no_crash()
```

## Usage

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/

# Run specific test
python3 tests/test_platformer.py

# With verbose output
python3 -m pytest tests/ -v

# Save screenshots
python3 tests/test_platformer.py --save-screenshots
```

### Writing Tests

```python
from matrixos.testing import TestRunner
from matrixos.input import InputEvent

def test_my_app():
    runner = TestRunner(width=128, height=128)
    
    # Define test sequence
    def test_script(runner):
        # Navigate launcher to your app (example)
        runner.input.schedule_event(InputEvent.DOWN, at_frame=5)
        runner.input.schedule_event(InputEvent.DOWN, at_frame=10)
        runner.input.schedule_event(InputEvent.OK, at_frame=15)
        
        # Wait for app to load
        runner.run_for_frames(20)
        
        # Test app interaction
        runner.input.schedule_event(InputEvent.ACTION, at_frame=30)
        runner.run_for_frames(40)
    
    # Run test
    runner.run_test("apps.myapp.main", test_script)
    
    # Assertions
    runner.assert_render_count(expected=40, message="Should render every frame")
    
    # Check display state
    snapshot = runner.display.get_buffer_snapshot()
    # Verify something is drawn
    assert runner.display.count_pixels((0, 0, 0)) < 128 * 128
    
    print("✓ My app test passed")
```

## Benefits

1. **No Display Required** - Run tests on CI/CD servers
2. **Fast Execution** - No terminal I/O overhead
3. **Reproducible** - Exact input sequences every time
4. **Regression Testing** - Catch bugs before they ship
5. **Golden Screenshots** - Compare display output frame-by-frame
6. **Crash Detection** - Automatically catch exceptions

## Implementation Complexity

### Easy (1-2 hours)
- Headless display adapter
- Input simulator
- Basic test runner

### Medium (3-4 hours)
- Test assertions (pixel checks, text search)
- Golden screenshot comparisons
- Frame-by-frame debugging

### Hard (1-2 days)
- Full integration with pytest
- Visual diff tool for failed tests
- CI/CD pipeline integration
- Coverage reporting

## Alternative: Lightweight Version

If full framework is too much, start with a simpler approach:

```python
# tests/smoke_test.py
"""Just verify apps don't crash on launch."""

import sys
sys.stdout = open('/dev/null', 'w')  # Suppress output

from examples.platformer import main as platformer
from examples.space_invaders import main as invaders

# Mock minimal framework
class MockFramework:
    def __init__(self):
        self.apps = []
        self.matrix = MockMatrix()
    
    def register_app(self, app): 
        self.apps.append(app)
    
    def switch_to_app(self, app):
        app.on_activate()
    
    def run(self):
        # Run for a few frames
        for _ in range(10):
            for app in self.apps:
                app.render(self.matrix)

class MockMatrix:
    def __init__(self):
        self.width = 128
        self.height = 128
    
    def __getattr__(self, name):
        # All drawing methods do nothing
        return lambda *args, **kwargs: None

# Test
try:
    context = MockFramework()
    platformer.run(context)
    print("✓ Platformer doesn't crash")
except Exception as e:
    print(f"✗ Platformer crashed: {e}")
    raise

try:
    context = MockFramework()
    invaders.run(context)
    print("✓ Space Invaders doesn't crash")
except Exception as e:
    print(f"✗ Space Invaders crashed: {e}")
    raise
```

## Recommendation

**Start with the lightweight smoke tests** (30 minutes) to catch obvious crashes, then build out the full testing framework as needed.

The full framework is **not a huge job** - probably 4-6 hours total for a working system with basic assertions. The hard part is writing good tests, not building the infrastructure.

## Next Steps

1. Create `matrixos/testing/` directory
2. Implement `HeadlessDisplay` class
3. Implement `InputSimulator` class
4. Create simple smoke tests
5. Expand to full test suite as needed

Would you like me to implement the lightweight smoke test version now, or the full framework?
