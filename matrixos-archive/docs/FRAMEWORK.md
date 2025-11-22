# MatrixOS App Framework

## Architecture Overview

MatrixOS uses **true OS-style app execution** with:

- **Event-driven architecture** - Apps don't run their own loops
- **Background processing** - Apps can run when inactive
- **Screen takeover** - Background apps can request attention
- **Cooperative multitasking** - OS manages all apps

> **Note**: ALL apps must use the framework. There is no subprocess/standalone mode.
> Apps are imported and run in-process by the OS.

## How It Works

### The Framework Model

MatrixOS uses an **event-driven, callback-based architecture**:
```python
from matrixos.app_framework import App

class MyApp(App):
    def on_update(self, delta_time):
        # Called every frame by OS (~60fps)
        pass

    def on_background_tick(self):
        # Called when app is in background (~1 second)
        pass

    def render(self, matrix):
        # Draw UI (don't call matrix.show()!)
        pass

def run(os_context):
    app = MyApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)
```

**Key Principles**:
- **Apps don't loop** - OS calls your methods
- **Apps don't manage exit** - ESC/Q handled by OS
- **Apps cooperate** - Share screen time
- **Apps can multitask** - Run in background

## App Lifecycle Methods

### `on_activate()`
Called when app becomes the foreground app.
- Initialize UI
- Resume animations
- Load saved state

### `on_deactivate()`
Called when app goes to background.
- Save state
- Pause animations
- Release resources

### `on_update(delta_time)`
Called every frame when active (~60fps).
- Update animations
- Game logic
- Active UI updates
- **Must return quickly!**

### `on_background_tick()`
Called periodically when inactive (~1 second).
- Check timers
- Fetch data
- Monitor for alerts
- **Must be VERY fast!**

### `on_event(event)`
Handle input events when active.
- Process keyboard input
- Return `True` if handled
- Return `False` to pass to OS

### `render(matrix)`
Draw the app's UI.
- Called after `on_update()`
- Draw to matrix
- **Don't call `matrix.show()`** - OS does this!

## Example: Timer App

Shows how background processing works:

```python
class TimerApp(App):
    def __init__(self):
        super().__init__("Timer")
        self.countdown = 10
        self.running = True

    def on_update(self, delta_time):
        """Smooth countdown when active"""
        if self.running:
            self.countdown -= delta_time
            if self.countdown <= 0:
                self.alarm_triggered = True

    def on_background_tick(self):
        """Timer runs even in background!"""
        if self.running:
            self.countdown -= 1
            if self.countdown <= 0:
                # Request OS to show us!
                self.request_attention(priority='high')

    def render(self, matrix):
        """Draw timer UI"""
        matrix.centered_text(f"{int(self.countdown)}s", 30, (255, 255, 0))
```

## Benefits

1. **Simpler apps** - No boilerplate event loops
2. **True multitasking** - Multiple apps can run
3. **Notifications** - Background apps can alert
4. **Better UX** - ESC always works (OS guarantees)
5. **Power efficient** - Single event loop
6. **Easy testing** - Apps can still run standalone

## Creating Framework Apps

### Required Structure

```
apps/myapp/
├── main.py       # App code with run(os_context)
├── config.json   # App metadata
└── icon.json     # 16x16 icon
```

### Minimal Example

```python
#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App

class MyApp(App):
    def render(self, matrix):
        matrix.centered_text("HELLO!", 30, (0, 255, 255))

def run(os_context):
    """Called by OS"""
    app = MyApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)

if __name__ == '__main__':
    # Standalone testing
    from matrixos.led_api import create_matrix
    from matrixos.input import KeyboardInput
    from matrixos.config import parse_matrix_args
    from matrixos.app_framework import OSContext

    args = parse_matrix_args("My App")
    matrix = create_matrix(args.width, args.height, args.color_mode)

    with KeyboardInput() as input_handler:
        os = OSContext(matrix, input_handler)
        app = MyApp()
        os.register_app(app)
        os.switch_to_app(app)
        os.run()
```

## System Events

Apps don't need to handle these - OS does:

- **ESC** - Return to launcher
- **Q** - Quit entire OS
- **Ctrl+C** - Emergency exit

## Layout System

MatrixOS provides simple layout helpers in `matrixos.layout` for clean, responsive UI code.

### Philosophy

**Keep it simple!** MatrixOS apps are straightforward - they don't need React-style reactivity. Our layout helpers provide 90% of the benefit with 10% of the complexity.

### Common Helpers

```python
from matrixos import layout

# Center text horizontally/vertically
layout.center_text(matrix, "HELLO", y=20, color=(255, 255, 0))
layout.center_text(matrix, "CENTERED!", color=(0, 255, 255))  # Both axes

# Draw scrollable menus
items = ["Option 1", "Option 2", "Option 3"]
layout.menu_list(matrix, items, selected_index=1)

# Progress bars
layout.draw_progress_bar(matrix, x=10, y=30, width=100, height=8, 
                        progress=0.75, fg_color=(0, 255, 0))

# Icon + text combos
layout.draw_icon_with_text(matrix, "☼", "Sunny", 10, 20,
                          icon_color=(255, 255, 0))

# Responsive icon sizing (16px for 64×64, 32px for 128×128)
icon_size = layout.get_icon_size(matrix)

# Multi-column layouts
cols = layout.split_columns(matrix, num_columns=2, padding=4)
x1, width1 = cols[0]
x2, width2 = cols[1]

# Grid positioning
cols, rows = layout.get_grid_dimensions(matrix, item_size=32, padding=4)
x, y = layout.grid_position(index=5, cols=cols, item_size=32)
```

### Responsive Design

Apps should adapt to different resolutions:

```python
def render(self, matrix):
    # Get appropriate sizes for this resolution
    icon_size = layout.get_icon_size(matrix)  # 16/32/48px
    scale = icon_size / 16  # Scale factor
    
    # Scale your drawings
    radius = int(8 * scale)
    matrix.circle(matrix.width // 2, 30, radius, (255, 0, 0), fill=True)
    
    # Use helpers for automatic centering
    layout.center_text(matrix, f"{self.count}", color=(255, 255, 255))
```

See `examples/layout_demo.py` for complete examples of all helpers.

## Network Module

MatrixOS provides async HTTP client in `matrixos.network` for non-blocking network I/O.

**Zero dependencies** - uses Python standard library (`urllib`) only.

### Basic Usage

```python
from matrixos import network

class WeatherApp(App):
    def __init__(self):
        super().__init__("Weather")
        self.temperature = None
        self.loading = True
    
    def on_activate(self):
        # Fetch weather when app opens
        self.fetch_weather()
    
    def fetch_weather(self):
        def on_response(result):
            """Called on main thread when fetch completes"""
            self.loading = False
            
            if result.success:
                data = result.value  # Parsed JSON
                self.temperature = data['temp']
                self.dirty = True  # Trigger redraw
            else:
                print(f"Error: {result.error}")
        
        # Non-blocking GET request with JSON parsing
        url = "https://api.weather.com/current?location=Cardiff"
        network.get_json(url, callback=on_response, timeout=5.0)
```

### API Reference

```python
# Simple convenience functions
network.get(url, callback, timeout=10.0)
network.get_json(url, callback, timeout=10.0)
network.post(url, data, callback, timeout=10.0)
network.post_json(url, data, callback, timeout=10.0)

# Or create a client with custom settings
client = network.NetworkClient(timeout=5.0, user_agent="MyApp/1.0")
client.get_json(url, callback=on_response)
```

### Error Handling

```python
def on_response(result):
    if result.success:
        data = result.value
        # Use data...
    else:
        error = result.error
        if isinstance(error, network.TimeoutError):
            print("Request timed out")
        elif isinstance(error, network.HTTPError):
            print(f"HTTP {error.code}")
        elif isinstance(error, network.ConnectionError):
            print("Connection failed")
```

**Important**: All callbacks run on the main thread, so UI updates are safe!

## Future Possibilities

With this architecture, we can add:

- **App switching** (Alt+Tab style)
- **System notifications**
- **Status bar**
- **App permissions**
- **Resource limiting**
- **App store/package manager**

The foundation is now in place for a true embedded OS!
