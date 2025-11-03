# MatrixOS Testing Framework - Design Document

## Vision

A **declarative, integrated testing framework** that makes it trivial to write comprehensive tests for MatrixOS apps. Tests should be:

1. **Declarative** - Define tests in YAML, not Python code
2. **Integrated** - Built into MatrixOS core, not external
3. **Powerful** - Support complex assertions (collision detection, sprite tracking, timing)
4. **Developer-friendly** - Easy to write, easy to debug
5. **Fast** - Run in CI/CD without display

## Architecture

### Layer 1: Core Testing Infrastructure (matrixos/testing/)

```
matrixos/testing/
├── __init__.py           # Public API
├── runner.py             # TestRunner class
├── display_adapter.py    # HeadlessDisplay with buffer inspection
├── input_simulator.py    # Programmatic input injection
├── assertions.py         # Rich assertion library
├── sprite_tracker.py     # Track objects on screen
└── yaml_loader.py        # Load test specs from YAML
```

### Layer 2: Test Specifications (YAML)

Tests defined in `tests/specs/*.yaml`:

```yaml
# tests/specs/snake_collision.yaml
name: "Snake - Collision Detection"
app: "examples.snake.main"
timeout: 10.0  # seconds

setup:
  # Wait for game to initialize
  - wait: 0.5

steps:
  - name: "Move snake right to hit wall"
    inputs:
      - { key: RIGHT, at: 0.0 }
    wait: 2.0
    
  - name: "Verify game over"
    assert:
      - type: text_visible
        text: "GAME OVER"
      - type: pixel_color
        x: 64
        y: 64
        color: [255, 0, 0]  # Red game over screen
```

### Layer 3: Python Test API (for complex tests)

```python
from matrixos.testing import TestRunner, Assertions

def test_snake_collision():
    runner = TestRunner("examples.snake.main")
    
    # Let game initialize
    runner.wait(0.5)
    
    # Track snake head position
    tracker = runner.track_sprite(color=(0, 255, 0))  # Green snake
    initial_pos = tracker.position
    
    # Move right until collision
    runner.inject(InputEvent.RIGHT)
    runner.wait_for_event("collision", timeout=5.0)
    
    # Verify game over state
    assert runner.text_visible("GAME OVER")
    assert not runner.is_animating()  # Game should stop
    
    runner.assert_passed()
```

## Key Features

### 1. Display Buffer Inspection

```python
class DisplayAdapter:
    def get_pixel(self, x, y) -> Tuple[int, int, int]:
        """Get RGB value at coordinate."""
    
    def find_color(self, color) -> List[Tuple[int, int]]:
        """Find all pixels matching color."""
    
    def find_rect(self, color, min_size=1) -> List[Rect]:
        """Find rectangular regions of color."""
    
    def get_region(self, x, y, w, h) -> np.ndarray:
        """Extract region as array."""
    
    def text_visible(self, text) -> bool:
        """Check if text appears on screen."""
    
    def count_objects(self, color, min_size=4) -> int:
        """Count distinct objects (blobs) of a color."""
```

### 2. Sprite Tracking

```python
class SpriteTracker:
    """Track a colored sprite across frames."""
    
    def __init__(self, display, color, tolerance=10):
        self.color = color
        self.positions = []  # History
    
    @property
    def position(self) -> Tuple[int, int]:
        """Current centroid position."""
    
    @property
    def velocity(self) -> Tuple[float, float]:
        """Movement speed (pixels/second)."""
    
    def moved(self, threshold=1) -> bool:
        """Has sprite moved since last check?"""
    
    def collides_with(self, other_tracker) -> bool:
        """Check collision with another sprite."""
```

### 3. Timing and Animation

```python
class TestRunner:
    def wait_for_movement(self, tracker, timeout=5.0):
        """Wait until sprite moves."""
    
    def wait_for_collision(self, tracker1, tracker2, timeout=5.0):
        """Wait until two sprites collide."""
    
    def wait_for_text(self, text, timeout=5.0):
        """Wait until text appears."""
    
    def wait_for_still(self, timeout=1.0):
        """Wait until display stops changing."""
    
    def is_animating(self) -> bool:
        """Is display changing between frames?"""
```

### 4. Input Sequencing

```python
# Simple
runner.inject(InputEvent.RIGHT)
runner.inject_sequence([InputEvent.RIGHT, InputEvent.UP], delay=0.5)

# Complex timing
runner.schedule_input(InputEvent.FIRE, at_frame=120)
runner.schedule_input(InputEvent.FIRE, at_time=2.0)

# Reactive
runner.inject_when(InputEvent.FIRE, condition=lambda: score > 100)
```

## YAML Test Format

### Basic Structure

```yaml
name: "Test name"
app: "import.path.to.main"
resolution: [128, 128]  # optional
timeout: 10.0  # seconds
tags: [collision, physics]  # for filtering

setup:
  - wait: 0.5
  - inject: OK  # Start game

steps:
  - name: "Step description"
    inputs:
      - { key: RIGHT, repeat: 10, delay: 0.1 }
    wait: 2.0
    assert:
      - type: text_visible
        text: "SCORE: 100"

teardown:
  - inject: HOME  # Exit to launcher
```

### Advanced Assertions

```yaml
assert:
  # Text checks
  - type: text_visible
    text: "GAME OVER"
  
  - type: text_not_visible
    text: "Loading..."
  
  # Pixel checks
  - type: pixel_color
    x: 64
    y: 64
    color: [255, 0, 0]
    tolerance: 10
  
  # Region checks
  - type: region_contains_color
    x: 0
    y: 0
    width: 128
    height: 64
    color: [0, 255, 0]
    min_pixels: 100
  
  # Object counting
  - type: object_count
    color: [255, 0, 0]  # Red enemies
    min: 5
    max: 10
  
  # Sprite position
  - type: sprite_at
    color: [0, 255, 0]  # Player
    x: 64
    y: 100
    tolerance: 5
  
  # Animation/movement
  - type: is_animating
    value: true
  
  - type: display_changed
    since: 1.0  # seconds ago
  
  # Collision detection
  - type: sprites_colliding
    color1: [0, 255, 0]  # Player
    color2: [255, 0, 0]  # Enemy
    value: false
  
  # Timing
  - type: render_count
    min: 60
    max: 120
  
  # Custom Python
  - type: custom
    function: "tests.helpers.check_score_valid"
```

### Example: Comprehensive Snake Test

```yaml
name: "Snake - Complete Gameplay Test"
app: "examples.snake.main"
timeout: 30.0
tags: [snake, collision, scoring]

setup:
  - wait: 0.5  # Game loads
  - snapshot: "initial"  # Save display state

steps:
  - name: "Collect first apple"
    actions:
      # Track snake and apple
      - track_sprite: 
          name: "snake"
          color: [0, 255, 0]
      - track_sprite:
          name: "apple"
          color: [255, 0, 0]
      
      # Navigate to apple
      - navigate_to:
          from_sprite: "snake"
          to_sprite: "apple"
          max_moves: 50
      
      # Wait for collision
      - wait_for_collision:
          sprite1: "snake"
          sprite2: "apple"
          timeout: 5.0
    
    assert:
      - type: text_contains
        text: "Score:"
        expect: "1"  # Score increased
      - type: sprite_grew
        name: "snake"
        min_growth: 1  # Snake got longer

  - name: "Hit wall to trigger game over"
    inputs:
      - { key: RIGHT, repeat: 20 }
    wait: 3.0
    
    assert:
      - type: text_visible
        text: "GAME OVER"
      - type: is_animating
        value: false
      - type: sprite_at_edge
        name: "snake"

  - name: "Restart game"
    inputs:
      - { key: OK }
    wait: 0.5
    
    assert:
      - type: display_matches
        snapshot: "initial"
        tolerance: 0.1
```

## Implementation Plan

### Phase 1: Core Infrastructure ⭐ START HERE

```python
# matrixos/testing/__init__.py
from .runner import TestRunner
from .assertions import Assertions
from .display_adapter import HeadlessDisplay

__all__ = ['TestRunner', 'Assertions', 'HeadlessDisplay']
```

```python
# matrixos/testing/display_adapter.py
import numpy as np
from typing import List, Tuple, Optional

class HeadlessDisplay:
    """Display adapter with rich inspection capabilities."""
    
    def __init__(self, width=128, height=128):
        self.width = width
        self.height = height
        self.buffer = np.zeros((height, width, 3), dtype=np.uint8)
        self.history = []  # Frame history for animations
        self.render_count = 0
    
    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get RGB at coordinate."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return tuple(self.buffer[y, x])
        return (0, 0, 0)
    
    def find_color(self, color: Tuple[int, int, int], 
                   tolerance: int = 0) -> List[Tuple[int, int]]:
        """Find all pixels matching color."""
        matches = []
        for y in range(self.height):
            for x in range(self.width):
                if self._color_match(self.buffer[y, x], color, tolerance):
                    matches.append((x, y))
        return matches
    
    def find_blobs(self, color: Tuple[int, int, int], 
                   min_size: int = 1) -> List[List[Tuple[int, int]]]:
        """Find connected regions (blobs) of a color."""
        # Connected component labeling
        pixels = set(self.find_color(color))
        blobs = []
        
        while pixels:
            # Flood fill to find blob
            start = pixels.pop()
            blob = self._flood_fill(start, pixels)
            if len(blob) >= min_size:
                blobs.append(blob)
        
        return blobs
    
    def get_centroid(self, pixels: List[Tuple[int, int]]) -> Tuple[float, float]:
        """Calculate centroid of pixel list."""
        if not pixels:
            return (0, 0)
        x_avg = sum(p[0] for p in pixels) / len(pixels)
        y_avg = sum(p[1] for p in pixels) / len(pixels)
        return (x_avg, y_avg)
    
    def text_visible(self, text: str) -> bool:
        """Check if text appears on display (using font matching)."""
        # Would need to render text and compare
        # For now, simplified check
        pass
    
    def snapshot(self) -> np.ndarray:
        """Get copy of current buffer."""
        return self.buffer.copy()
    
    def compare(self, snapshot: np.ndarray, tolerance: float = 0.1) -> float:
        """Compare current display to snapshot. Returns similarity 0-1."""
        diff = np.abs(self.buffer.astype(float) - snapshot.astype(float))
        max_diff = 255.0 * self.width * self.height * 3
        similarity = 1.0 - (diff.sum() / max_diff)
        return similarity
    
    def is_changing(self, frames: int = 2) -> bool:
        """Check if display is animating (changing between frames)."""
        if len(self.history) < frames:
            return False
        recent = self.history[-frames:]
        return any(not np.array_equal(recent[i], recent[i+1]) 
                   for i in range(len(recent)-1))
```

### Phase 2: Test Runner with Python API

```python
# matrixos/testing/runner.py
from typing import Optional, Callable, Any
import time
from matrixos.app_framework import AppFramework
from matrixos.input import InputEvent
from .display_adapter import HeadlessDisplay
from .input_simulator import InputSimulator
from .sprite_tracker import SpriteTracker

class TestRunner:
    """High-level test automation for MatrixOS apps."""
    
    def __init__(self, app_module: str, width: int = 128, height: int = 128):
        self.app_module = app_module
        self.display = HeadlessDisplay(width, height)
        self.input = InputSimulator()
        self.framework = self._create_framework()
        self.trackers = {}
        self.snapshots = {}
        self.start_time = time.time()
    
    def _create_framework(self) -> AppFramework:
        """Create headless framework."""
        # Would need to modify AppFramework to accept custom display/input
        pass
    
    def run(self, duration: float = None):
        """Run app for specified duration."""
        pass
    
    def inject(self, key: str):
        """Inject single input immediately."""
        self.input.inject(key)
    
    def inject_sequence(self, keys: List[str], delay: float = 0.1):
        """Inject sequence of inputs with delays."""
        for key in keys:
            self.inject(key)
            self.wait(delay)
    
    def wait(self, seconds: float):
        """Run simulation for N seconds."""
        frames = int(seconds * 60)  # 60fps
        for _ in range(frames):
            self.framework.tick()
    
    def track_sprite(self, name: str, color: Tuple[int, int, int]) -> SpriteTracker:
        """Create sprite tracker."""
        tracker = SpriteTracker(self.display, color)
        self.trackers[name] = tracker
        return tracker
    
    def snapshot(self, name: str):
        """Save current display state."""
        self.snapshots[name] = self.display.snapshot()
    
    def assert_snapshot_matches(self, name: str, tolerance: float = 0.1):
        """Assert current display matches snapshot."""
        if name not in self.snapshots:
            raise AssertionError(f"No snapshot named '{name}'")
        similarity = self.display.compare(self.snapshots[name])
        if similarity < (1.0 - tolerance):
            raise AssertionError(
                f"Display doesn't match snapshot '{name}' "
                f"(similarity: {similarity:.2%})"
            )
    
    def wait_for_collision(self, sprite1: str, sprite2: str, timeout: float = 5.0):
        """Wait until two sprites collide."""
        start = time.time()
        while time.time() - start < timeout:
            if self.trackers[sprite1].collides_with(self.trackers[sprite2]):
                return
            self.framework.tick()
        raise TimeoutError(f"Sprites didn't collide within {timeout}s")
    
    def text_visible(self, text: str) -> bool:
        """Check if text is on screen."""
        return self.display.text_visible(text)
    
    def is_animating(self) -> bool:
        """Check if display is changing."""
        return self.display.is_changing()
```

### Phase 3: YAML Test Loader

```python
# matrixos/testing/yaml_loader.py
import yaml
from typing import Dict, List, Any
from .runner import TestRunner

class YAMLTestLoader:
    """Load and execute tests from YAML specifications."""
    
    @staticmethod
    def load_test(yaml_path: str) -> Dict[str, Any]:
        """Parse YAML test specification."""
        with open(yaml_path) as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def run_test(spec: Dict[str, Any]) -> bool:
        """Execute test from specification."""
        runner = TestRunner(
            spec['app'],
            width=spec.get('resolution', [128, 128])[0],
            height=spec.get('resolution', [128, 128])[1]
        )
        
        # Setup
        for step in spec.get('setup', []):
            YAMLTestLoader._execute_step(runner, step)
        
        # Main steps
        for step in spec['steps']:
            print(f"  {step.get('name', 'Unnamed step')}...", end=" ")
            try:
                YAMLTestLoader._execute_step(runner, step)
                print("✓")
            except AssertionError as e:
                print(f"✗ {e}")
                return False
        
        # Teardown
        for step in spec.get('teardown', []):
            YAMLTestLoader._execute_step(runner, step)
        
        return True
    
    @staticmethod
    def _execute_step(runner: TestRunner, step: Dict[str, Any]):
        """Execute a single test step."""
        # Handle different step types
        if 'wait' in step:
            runner.wait(step['wait'])
        
        if 'inject' in step:
            runner.inject(step['inject'])
        
        if 'inputs' in step:
            for input_spec in step['inputs']:
                key = input_spec['key']
                repeat = input_spec.get('repeat', 1)
                delay = input_spec.get('delay', 0.0)
                for _ in range(repeat):
                    runner.inject(key)
                    if delay > 0:
                        runner.wait(delay)
        
        if 'assert' in step:
            for assertion in step['assert']:
                YAMLTestLoader._check_assertion(runner, assertion)
    
    @staticmethod
    def _check_assertion(runner: TestRunner, assertion: Dict[str, Any]):
        """Check a single assertion."""
        atype = assertion['type']
        
        if atype == 'text_visible':
            if not runner.text_visible(assertion['text']):
                raise AssertionError(f"Text not visible: {assertion['text']}")
        
        elif atype == 'pixel_color':
            actual = runner.display.get_pixel(assertion['x'], assertion['y'])
            expected = tuple(assertion['color'])
            tolerance = assertion.get('tolerance', 0)
            if not color_match(actual, expected, tolerance):
                raise AssertionError(
                    f"Pixel at ({assertion['x']},{assertion['y']}) "
                    f"is {actual}, expected {expected}"
                )
        
        elif atype == 'is_animating':
            expected = assertion['value']
            actual = runner.is_animating()
            if actual != expected:
                raise AssertionError(
                    f"Animation state is {actual}, expected {expected}"
                )
        
        # ... more assertion types
```

### Phase 4: CLI Test Runner

```bash
# Run all tests
python3 -m matrixos.testing

# Run specific test
python3 -m matrixos.testing tests/specs/snake_collision.yaml

# Run tests by tag
python3 -m matrixos.testing --tag collision

# Verbose mode
python3 -m matrixos.testing -v

# Save screenshots on failure
python3 -m matrixos.testing --save-screenshots
```

## Example Tests to Write

### 1. Snake Collision Detection
```yaml
name: "Snake - Wall Collision"
app: "examples.snake.main"
steps:
  - name: "Move right until crash"
    inputs:
      - { key: RIGHT, repeat: 30 }
    wait: 3.0
    assert:
      - type: text_visible
        text: "GAME OVER"
```

### 2. Clock Accuracy
```python
def test_clock_shows_correct_time():
    runner = TestRunner("apps.clock.main")
    runner.wait(1.0)
    
    # Get system time
    import datetime
    now = datetime.datetime.now()
    expected_text = now.strftime("%H:%M")
    
    # Verify clock displays it
    assert runner.text_visible(expected_text)
```

### 3. Platformer Physics
```yaml
name: "Platformer - Gravity and Jumping"
app: "examples.platformer.main"
steps:
  - name: "Player falls due to gravity"
    actions:
      - track_sprite:
          name: "player"
          color: [0, 150, 255]
      - wait: 1.0
    assert:
      - type: sprite_moved
        name: "player"
        direction: "down"
  
  - name: "Player can jump"
    inputs:
      - { key: ACTION }
    wait: 0.5
    assert:
      - type: sprite_moved
        name: "player"
        direction: "up"
```

## Next Steps

1. **Implement core infrastructure** (HeadlessDisplay, TestRunner base)
2. **Create SpriteTracker** for object tracking
3. **Build YAML loader** for declarative tests
4. **Write example tests** for existing apps
5. **Integrate with CI/CD**

This is about **6-8 hours of work** for a fully functional system, but we can start with Phase 1 (2-3 hours) and already have powerful testing capabilities.

Want me to start implementing?
