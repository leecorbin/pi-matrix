# MatrixOS API Reference

## LEDMatrix Drawing API

The `matrix` object passed to your `render()` method provides these drawing methods:

### Basic Drawing

#### `set_pixel(x, y, color)`
Set a single pixel.
```python
matrix.set_pixel(10, 20, (255, 0, 0))  # Red pixel at (10, 20)
```

#### `clear(color=None)`
Clear the entire display.
```python
matrix.clear()  # Clear to black
matrix.clear((50, 50, 50))  # Clear to gray
```

#### `fill(color)`
Fill entire display with a color.
```python
matrix.fill((0, 0, 255))  # Fill with blue
```

### Lines and Shapes

#### `line(x1, y1, x2, y2, color)`
Draw a line between two points.
```python
matrix.line(0, 0, 127, 127, (255, 255, 255))  # White diagonal
```

#### `rect(x, y, width, height, color, fill=False)`
Draw a rectangle.
```python
# Outline
matrix.rect(10, 10, 50, 30, (255, 0, 0), fill=False)

# Filled
matrix.rect(10, 10, 50, 30, (255, 0, 0), fill=True)
```

#### `circle(x, y, radius, color, fill=False)`
Draw a circle.
```python
matrix.circle(64, 64, 30, (0, 255, 0), fill=False)  # Green circle outline
matrix.circle(64, 64, 30, (0, 255, 0), fill=True)   # Filled green circle
```

#### `ellipse(x, y, rx, ry, color, fill=False)`
Draw an ellipse.
```python
matrix.ellipse(64, 64, 40, 20, (255, 255, 0), fill=True)
```

#### `polygon(points, color, fill=False)`
Draw a polygon from list of (x, y) points.
```python
points = [(64, 10), (90, 50), (64, 70), (38, 50)]
matrix.polygon(points, (255, 0, 255), fill=True)  # Filled diamond
```

### Text

#### `text(text, x, y, color, bg_color=None, scale=1)`
Draw text using the ZX Spectrum 8×8 font.
```python
matrix.text("HELLO", 10, 20, (255, 255, 255))  # White text
matrix.text("WORLD", 10, 30, (255, 0, 0), (0, 0, 0))  # Red on black
matrix.text("BIG", 10, 40, (0, 255, 0), scale=2)  # 16×16 text
```

#### `centered_text(text, y, color, bg_color=None)`
Draw text centered horizontally.
```python
matrix.centered_text("GAME OVER", 50, (255, 0, 0))
```

### Convenience Methods

#### `border(color=(255,255,255), thickness=1)`
Draw a border around the display.
```python
matrix.border((255, 255, 255), thickness=2)
```

#### `grid_lines(spacing=8, color=(50,50,50))`
Draw a grid (useful for debugging positioning).
```python
matrix.grid_lines(spacing=16, color=(80, 80, 80))
```

### Color Format

Colors are RGB tuples with values 0-255:
```python
(255, 0, 0)     # Red
(0, 255, 0)     # Green
(0, 0, 255)     # Blue
(255, 255, 0)   # Yellow
(255, 0, 255)   # Magenta
(0, 255, 255)   # Cyan
(255, 255, 255) # White
(128, 128, 128) # Gray
(0, 0, 0)       # Black
```

For monochrome displays, use `True` for on, `False` for off:
```python
matrix.set_pixel(10, 20, True)  # Turn pixel on
```

### Important Notes

- **Never call `matrix.show()`** in your app - the framework does this automatically
- All coordinates use (x, y) where (0, 0) is top-left
- Drawing outside the display bounds is safe (automatically clipped)
- The `dirty` flag tells the framework when to re-render (set `self.dirty = True` after changes)

---

## InputEvent API

The `event` object passed to your `on_event()` method:

### Standard Events

```python
from matrixos.input import InputEvent

def on_event(self, event):
    if event.key == InputEvent.UP:
        # Arrow up pressed
        pass
    elif event.key == InputEvent.DOWN:
        # Arrow down pressed
        pass
    elif event.key == InputEvent.LEFT:
        # Arrow left pressed
        pass
    elif event.key == InputEvent.RIGHT:
        # Arrow right pressed
        pass
    elif event.key == InputEvent.OK:
        # Enter key pressed
        pass
    elif event.key == InputEvent.ACTION:
        # Space bar pressed (for jump/fire/action in games)
        pass
    elif event.key == InputEvent.BACK:
        # Backspace pressed
        pass
    elif event.key == InputEvent.HOME:
        # ESC pressed (usually handled by framework)
        pass
    elif event.key == InputEvent.HELP:
        # Tab pressed
        pass
    elif event.key == InputEvent.L1:
        # Page Up pressed (left shoulder button)
        pass
    elif event.key == InputEvent.R1:
        # Page Down pressed (right shoulder button)
        pass
```

### Raw Character Input

You can also check for raw characters:
```python
def on_event(self, event):
    if event.key == 'A' or event.key == 'a':
        # 'A' key pressed
        pass
    elif event.key == ' ':
        # Space bar (also available as InputEvent.ACTION)
        pass
    elif event.key.isdigit():
        # Any number key
        number = int(event.key)
```

### Event Handling Best Practices

1. **Return `True` if handled:** Tells framework you processed the event
2. **Return `False` if not handled:** Framework may handle it (e.g., help overlay)
3. **Set `self.dirty = True`:** Mark display as needing redraw after changes

```python
def on_event(self, event):
    if event.key == InputEvent.OK:
        self.score += 1
        self.dirty = True  # Tell framework to re-render
        return True        # Event was handled
    return False  # Let framework handle it
```

---

## App Class

Your app inherits from `matrixos.app_framework.App`:

### Constructor

```python
class MyApp(App):
    def __init__(self):
        super().__init__("My App Name")
        self.dirty = True  # Request initial render
        # Your initialization here
```

### Properties

- `self.name` - App name (shown in launcher)
- `self.dirty` - Set to `True` when display needs redraw
- `self.active` - `True` when app is in foreground

### Lifecycle Methods

#### `on_activate()`
Called when app becomes active (switches to foreground).
```python
def on_activate(self):
    """Initialize or resume the app."""
    self.score = 0
    self.dirty = True
```

#### `on_deactivate()`
Called when app goes to background.
```python
def on_deactivate(self):
    """Save state, pause animations."""
    self.save_score()
```

#### `on_update(delta_time)`
Called every frame (~60fps) when active.
```python
def on_update(self, delta_time):
    """Update game logic."""
    self.player_x += self.velocity * delta_time
    self.dirty = True  # Mark for re-render
```

#### `on_background_tick()`
Called ~1/second when inactive.
```python
def on_background_tick(self):
    """Check for events while in background."""
    if self.timer_expired():
        self.request_foreground()
```

#### `on_event(event)` 
Handle input events.
```python
def on_event(self, event):
    """Process user input."""
    if event.key == InputEvent.OK:
        self.fire_weapon()
        self.dirty = True
        return True
    return False
```

#### `render(matrix)`
Draw your UI.
```python
def render(self, matrix):
    """Draw the game."""
    matrix.clear()
    matrix.text(f"Score: {self.score}", 10, 10, (255, 255, 255))
    self.dirty = False  # Clear dirty flag after rendering
```

### Special Methods

#### `request_foreground()`
Ask to become the active app (for timers, alerts).
```python
def on_background_tick(self):
    if self.alarm_triggered:
        self.request_foreground()
```

---

## Entry Point

Every app needs a `run()` function:

```python
def run(os_context):
    """Called by MatrixOS to start your app."""
    app = MyApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()  # Start the event loop
```

The OS context provides:
- `register_app(app)` - Add app to system
- `switch_to_app(app)` - Make app active
- `run()` - Start the event loop (blocks until app exits)

---

## Complete Example: Simple Game

```python
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent

class SimpleGame(App):
    def __init__(self):
        super().__init__("Simple Game")
        self.player_x = 64
        self.player_y = 64
        self.score = 0
        self.dirty = True
    
    def on_activate(self):
        """Reset game on start."""
        self.player_x = 64
        self.player_y = 64
        self.score = 0
        self.dirty = True
    
    def on_event(self, event):
        """Move player with arrow keys."""
        if event.key == InputEvent.LEFT:
            self.player_x = max(0, self.player_x - 5)
            self.dirty = True
            return True
        elif event.key == InputEvent.RIGHT:
            self.player_x = min(123, self.player_x + 5)
            self.dirty = True
            return True
        elif event.key == InputEvent.ACTION:
            # Space bar for action
            self.score += 1
            self.dirty = True
            return True
        return False
    
    def on_update(self, delta_time):
        """Smooth animations here if needed."""
        pass
    
    def render(self, matrix):
        """Draw the game."""
        matrix.clear()
        
        # Draw player
        matrix.rect(self.player_x, self.player_y, 5, 5, (0, 255, 0), fill=True)
        
        # Draw score
        matrix.text(f"Score: {self.score}", 5, 5, (255, 255, 255))
        
        self.dirty = False

def run(os_context):
    """Entry point."""
    game = SimpleGame()
    os_context.register_app(game)
    os_context.switch_to_app(game)
    os_context.run()
```

---

## Common Patterns

### Dirty Flag Management

```python
def on_event(self, event):
    if event.key == InputEvent.LEFT:
        self.x -= 1
        self.dirty = True  # Mark for re-render
        return True
    return False

def render(self, matrix):
    matrix.clear()
    # ... draw everything ...
    self.dirty = False  # Clear flag after render
```

### Animation Loop

```python
def on_update(self, delta_time):
    """Smooth 60fps animation."""
    self.angle += 90 * delta_time  # 90 degrees per second
    self.dirty = True

def render(self, matrix):
    # Draw based on self.angle
    pass
```

### Background Tasks

```python
def on_background_tick(self):
    """Check every second while inactive."""
    self.check_for_updates()
    if self.has_alert:
        self.request_foreground()
```

### Game State Machine

```python
class MyGame(App):
    def __init__(self):
        super().__init__("My Game")
        self.state = "MENU"  # MENU, PLAYING, GAME_OVER
    
    def render(self, matrix):
        if self.state == "MENU":
            self.render_menu(matrix)
        elif self.state == "PLAYING":
            self.render_game(matrix)
        elif self.state == "GAME_OVER":
            self.render_game_over(matrix)
        self.dirty = False
```

---

## Debugging Tips

1. **Check `/tmp/matrixos_debug.log`** for framework errors
2. **Use the logging system:**
   ```python
   from matrixos.logger import get_logger
   logger = get_logger("MyApp")
   logger.info("Debug message")
   # Check settings/logs/myapp.log
   ```
3. **In tests, inspect logs programmatically:**
   ```python
   runner = TestRunner("examples.myapp.main")
   runner.wait(1.0)
   
   # Read all logs from this test
   logs = runner.read_logs()
   print(logs)
   
   # Check for errors
   runner.assert_no_errors_logged()
   
   # Search for specific text
   if runner.log_contains("player moved"):
       print("Movement logged correctly")
   
   # Debug test failures
   runner.print_recent_logs(lines=20)
   ```
4. **Render errors crash silently** - check the debug log
5. **Test with terminal emulator** before deploying to hardware
6. **Use `matrix.grid_lines()` to verify positioning**

---

## Testing API

### TestRunner

The testing framework provides log inspection alongside display testing:

```python
from matrixos.testing import TestRunner

runner = TestRunner("examples.myapp.main")
runner.wait(1.0)

# Display inspection
assert runner.text_visible("GAME OVER")
player_pos = runner.find_sprite((0, 255, 0))

# Log inspection
logs = runner.read_logs()
runner.assert_no_errors_logged()
runner.assert_log_contains("Game started")

# Count errors
error_count = len(runner.get_error_logs())
warning_count = len(runner.get_warning_logs())

# Debug failures
if test_failed:
    runner.print_recent_logs(lines=30)
```

### Log Inspection Methods

#### `read_logs(app_name=None, since_test_start=True)`
Read log file contents as string.

#### `get_log_lines(app_name=None, since_test_start=True)`
Get logs as list of lines.

#### `log_contains(text, app_name=None)`
Check if logs contain specific text.

#### `count_log_occurrences(text, app_name=None)`
Count how many times text appears in logs.

#### `assert_log_contains(text, app_name=None)`
Assert logs contain text (throws with helpful message if not).

#### `assert_no_errors_logged(app_name=None)`
Assert no ERROR messages in logs.

#### `get_error_logs(app_name=None)`
Get all ERROR log lines as list.

#### `get_warning_logs(app_name=None)`
Get all WARNING log lines as list.

#### `clear_logs(app_name=None)`
Mark current position (future reads start from here). Useful for test phases.

#### `print_recent_logs(lines=20, app_name=None)`
Print recent log lines to console (debugging).

### Example: Debugging with Logs

```python
def test_complex_interaction():
    runner = TestRunner("examples.game.main")
    
    # Phase 1: Setup
    runner.wait(0.5)
    runner.assert_log_contains("Game initialized")
    runner.clear_logs()  # Start fresh for next phase
    
    # Phase 2: Play
    runner.inject(InputEvent.ACTION)
    runner.wait(1.0)
    
    # If something goes wrong, logs show what happened
    if not runner.text_visible("SCORE"):
        print("Test failed! Checking logs...")
        runner.print_recent_logs(lines=30)
        
        # Get specific error details
        errors = runner.get_error_logs()
        if errors:
            print(f"Found {len(errors)} errors:")
            for error in errors:
                print(f"  {error}")
    
    # Assert no errors occurred
    runner.assert_no_errors_logged()
```

---

## Complete Testing Guide

For comprehensive testing documentation including:
- Advanced techniques (sprite tracking, visual regression)
- Common test patterns (movement, collision, animation)
- Best practices and troubleshooting
- Performance testing
- Log inspection strategies

See **[TESTING.md](TESTING.md)** - Complete MatrixOS Testing Guide

---

## See Also

- [TESTING.md](TESTING.md) - Complete testing framework guide
- [TESTING_FRAMEWORK_SUMMARY.md](TESTING_FRAMEWORK_SUMMARY.md) - Testing overview
- [FRAMEWORK.md](FRAMEWORK.md) - App architecture and design
- [APP_STRUCTURE.md](APP_STRUCTURE.md) - App file organization
- [LOGGING.md](LOGGING.md) - Logging system guide
- [ICON_FORMATS.md](ICON_FORMATS.md) - Creating app icons
