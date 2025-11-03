# MatrixOS Logging System

MatrixOS provides a simple but powerful logging system for apps and system components.

## Basic Usage

```python
from matrixos.logger import get_logger

# Create a logger for your app
logger = get_logger("MyApp")

# Log messages at different levels
logger.debug("Detailed debugging information")
logger.info("General information about app execution")
logger.warning("Something unexpected but not critical")
logger.error("An error occurred")
```

## Log Levels

- **DEBUG** - Detailed diagnostic information for troubleshooting
- **INFO** - General informational messages about app execution
- **WARNING** - Something unexpected happened but the app continues
- **ERROR** - An error occurred that prevented an operation

## Log Files

Logs are automatically written to `settings/logs/` with filenames based on your app name:
- `settings/logs/myapp.log` - Your app's log file
- `settings/logs/launcher.log` - Launcher system log
- `settings/logs/matrixos.log` - OS-level system log

Each log entry includes:
- **Timestamp** - Millisecond precision (e.g., `[22:15:43.142]`)
- **Level** - DEBUG, INFO, WARNING, ERROR
- **Message** - Your log message

Example log output:
```
============================================================
Session started: 2025-11-03 22:01:41
============================================================
[22:01:41.265] INFO: Starting app discovery
[22:01:41.266] DEBUG: Loading config for breakout
[22:01:41.316] INFO: Loaded: Breakout (breakout)
[22:01:41.785] INFO: Loaded: Platformer (platformer)
[22:01:41.817] INFO: Discovery complete: Found 13 apps
```

## Advanced Features

### Custom Log Levels

```python
logger.log("Custom message", level="CUSTOM")
```

### Session Markers

Each logger automatically writes a session start marker when created, making it easy to distinguish between different runs.

### Visual Separators

```python
logger.separator()  # Writes a visual separator line
```

## Best Practices

1. **Create logger once** - Create your logger at module level or in `__init__()`
2. **Use appropriate levels** - DEBUG for details, INFO for milestones, ERROR for failures
3. **Log key events** - App initialization, state changes, user actions, errors
4. **Don't log in tight loops** - Avoid logging every frame or rapid repeated events
5. **Include context** - Add relevant variables or state information to messages

## Example: Logging in Your App

```python
from matrixos.app_framework import App
from matrixos.input import InputEvent
from matrixos.logger import get_logger

logger = get_logger("MyGame")

class MyGame(App):
    def __init__(self):
        super().__init__("MyGame")
        logger.info("MyGame initialized")
        self.score = 0
    
    def on_activate(self):
        logger.info("Game activated - starting new game")
        self.score = 0
        self.dirty = True
    
    def on_event(self, event):
        if event.key == InputEvent.OK:
            self.score += 10
            logger.debug(f"Score increased to {self.score}")
            self.dirty = True
            return True
        return False
    
    def render(self, matrix):
        logger.debug(f"Rendering frame - score: {self.score}")
        matrix.clear()
        matrix.text(f"Score: {self.score}", 10, 50, (255, 255, 255))
        self.dirty = False


def run(os_context):
    logger.info("Launching MyGame")
    try:
        game = MyGame()
        os_context.register_app(game)
        os_context.switch_to_app(game)
        os_context.run()
        logger.info("MyGame completed normally")
    except Exception as e:
        logger.error(f"MyGame crashed: {e}")
        raise
```

## Log File Location

All logs are stored in the `settings/logs/` directory, which is gitignored so your logs never get committed to version control.

To view logs in real-time:
```bash
tail -f settings/logs/myapp.log
```

To clear old logs:
```bash
rm settings/logs/*.log
```

## System Logging

MatrixOS itself uses logging extensively. You can monitor system behavior by viewing:
- `settings/logs/launcher.log` - App discovery and launch events
- `settings/logs/matrixos.log` - OS-level events

This helps debug issues like slow app loading, discovery problems, or system errors.
