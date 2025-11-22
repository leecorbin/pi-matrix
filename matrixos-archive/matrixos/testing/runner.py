"""
Test runner for MatrixOS apps.

Provides high-level API for automated testing with headless display and input simulation.
"""

import time
import sys
import importlib
from pathlib import Path
from typing import Optional, Callable, List, Tuple, Any
from matrixos.input import InputEvent
from .display_adapter import HeadlessDisplay
from .input_simulator import InputSimulator
from .assertions import Assertions


class TestRunner:
    """
    High-level test automation for MatrixOS apps.
    
    Example:
        runner = TestRunner("examples.snake.main")
        runner.wait(0.5)
        runner.inject(InputEvent.RIGHT)
        runner.wait_until(lambda: runner.text_visible("GAME OVER"), timeout=5.0)
        assert runner.display.render_count > 60
    """
    
    def __init__(self, app_module: str, width: int = 128, height: int = 128,
                 max_duration: float = 30.0):
        """
        Initialize test runner.
        
        Args:
            app_module: Python import path to app (e.g., "examples.snake.main")
            width: Display width
            height: Display height
            max_duration: Maximum test duration in seconds (safety limit)
        """
        self.app_module = app_module
        self.display = HeadlessDisplay(width, height)
        self.input = InputSimulator()
        self.assertions = Assertions(self.display)
        
        self.max_duration = max_duration
        self.start_time = time.time()
        self.frame_count = 0
        self.fps = 60
        
        # Snapshots
        self.snapshots = {}
        
        # Logging integration
        self.log_dir = Path(__file__).parent.parent.parent / "settings" / "logs"
        self.app_log_file = None
        self._log_start_pos = {}  # Track log file positions at test start
        
        # Framework components (created when run() is called)
        self.framework = None
        self.app = None
        
        # Load app immediately so it's ready for testing
        self._load_app()
    
    def run(self, duration: Optional[float] = None):
        """
        Run the app for a specified duration.
        
        Args:
            duration: Seconds to run (None = run indefinitely or until max_duration)
        """
        if duration is None:
            duration = self.max_duration
        
        # Run for specified duration
        target_frames = int(duration * self.fps)
        for _ in range(target_frames):
            if not self._check_timeout():
                break
            self._tick()
    
    def _load_app(self):
        """Import and initialize the app."""
        # Record current log positions before loading app
        if self.log_dir.exists():
            for log_file in self.log_dir.glob("*.log"):
                try:
                    with open(log_file, 'r') as f:
                        f.seek(0, 2)  # Seek to end
                        self._log_start_pos[log_file] = f.tell()
                except:
                    pass
        
        # Suppress stdout during app initialization
        old_stdout = sys.stdout
        sys.stdout = open('/dev/null', 'w') if sys.platform != 'win32' else old_stdout
        
        try:
            # Import the app module
            module = importlib.import_module(self.app_module)
            
            # Create minimal framework context
            self.framework = MockOSContext(self.display, self.input)
            
            # Run the app's entry point
            module.run(self.framework)
            
            # Get reference to the app
            if self.framework.apps:
                self.app = self.framework.apps[0]
            
        finally:
            sys.stdout = old_stdout
        
        # Reset start time after loading (so max_duration only counts actual test time)
        self.start_time = time.time()
    
    def _tick(self):
        """Execute one frame of the event loop."""
        if not self.framework or not self.app:
            return
        
        # Handle input
        event = self.input.get_key()
        if event and self.app.active:
            self.app.on_event(event)
        
        # Update
        delta = 1.0 / self.fps
        if self.app.active:
            self.app.on_update(delta)
        
        # Render if dirty
        if self.app.active and self.app.dirty:
            self.display.clear()
            self.app.render(self.display)
            self.display.show()
        
        # Advance frame
        self.input.advance_frame()
        self.frame_count += 1
    
    def _check_timeout(self) -> bool:
        """Check if test has exceeded max duration."""
        # Calculate time since test runner was created
        elapsed = time.time() - self.start_time
        if elapsed > self.max_duration:
            raise TimeoutError(f"Test exceeded maximum duration of {self.max_duration}s")
        return True
    
    # === Input Injection ===
    
    def inject(self, key: str):
        """
        Inject an input event immediately.
        
        Args:
            key: InputEvent constant or raw character
        """
        self.input.inject(key)
        self._tick()  # Process immediately
    
    def inject_sequence(self, keys: List[str], delay: float = 0.1):
        """
        Inject a sequence of keys with delays.
        
        Args:
            keys: List of keys to inject
            delay: Seconds between each key
        """
        delay_frames = int(delay * self.fps)
        self.input.inject_sequence(keys, delay_frames)
    
    def inject_repeat(self, key: str, count: int, delay: float = 0.1):
        """Inject same key multiple times."""
        delay_frames = int(delay * self.fps)
        self.input.inject_repeat(key, count, delay_frames)
    
    # === Timing and Waiting ===
    
    def wait(self, seconds: float):
        """
        Run simulation for N seconds.
        
        Args:
            seconds: Duration to run
        """
        frames = int(seconds * self.fps)
        for _ in range(frames):
            if not self._check_timeout():
                break
            self._tick()
    
    def wait_frames(self, count: int):
        """Run for exact number of frames."""
        for _ in range(count):
            if not self._check_timeout():
                break
            self._tick()
    
    def wait_until(self, condition: Callable[[], bool], timeout: float = 5.0,
                   check_interval: float = 0.1):
        """
        Wait until a condition is true.
        
        Args:
            condition: Function that returns True when done waiting
            timeout: Maximum seconds to wait
            check_interval: How often to check condition (seconds)
            
        Raises:
            TimeoutError: If condition not met within timeout
        """
        start = time.time()
        check_frames = int(check_interval * self.fps)
        
        while time.time() - start < timeout:
            if condition():
                return
            self.wait_frames(check_frames)
        
        raise TimeoutError(f"Condition not met within {timeout}s")
    
    def wait_for_text(self, text: str, timeout: float = 5.0):
        """Wait until text appears on display."""
        self.wait_until(lambda: self.text_visible(text), timeout)
    
    def wait_for_animation(self, timeout: float = 5.0):
        """Wait until display starts changing."""
        self.wait_until(lambda: self.display.is_changing(), timeout)
    
    def wait_for_still(self, duration: float = 0.5):
        """Wait until display stops changing for specified duration."""
        still_frames = int(duration * self.fps)
        stable_count = 0
        
        while stable_count < still_frames:
            self._tick()
            if self.display.is_changing(frames=2):
                stable_count = 0
            else:
                stable_count += 1
    
    # === Display Inspection ===
    
    def text_visible(self, text: str) -> bool:
        """Check if text was drawn to display."""
        return self.display.text_was_drawn(text)
    
    def pixel_at(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get pixel color at coordinates."""
        return self.display.get_pixel(x, y)
    
    def count_color(self, color: Tuple[int, int, int], tolerance: int = 0) -> int:
        """Count pixels of a specific color."""
        return self.display.count_color(color, tolerance)
    
    def find_sprite(self, color: Tuple[int, int, int], 
                   tolerance: int = 0) -> Optional[Tuple[float, float]]:
        """
        Find centroid of largest blob of a color (useful for sprites).
        
        Returns:
            (x, y) centroid coordinates or None if not found
        """
        blobs = self.display.find_blobs(color, min_size=4, tolerance=tolerance)
        if not blobs:
            return None
        
        # Return centroid of largest blob
        largest = max(blobs, key=len)
        return self.display.get_centroid(largest)
    
    def snapshot(self, name: str):
        """Save current display state with a name."""
        self.snapshots[name] = self.display.snapshot()
    
    def assert_snapshot_matches(self, name: str, tolerance: float = 0.01):
        """Assert current display matches saved snapshot."""
        if name not in self.snapshots:
            raise ValueError(f"No snapshot named '{name}'")
        self.assertions.snapshot_matches(self.snapshots[name], 
                                        similarity=1.0 - tolerance)
    
    # === Assertion Helpers (delegates to Assertions) ===
    
    def assert_pixel(self, x: int, y: int, color: Tuple[int, int, int],
                    tolerance: int = 0):
        """Assert pixel has expected color."""
        self.assertions.pixel_equals(x, y, color, tolerance)
    
    def assert_text_visible(self, text: str):
        """Assert text was drawn."""
        self.assertions.text_was_drawn(text)
    
    def assert_animating(self, expected: bool = True):
        """Assert display is/isn't animating."""
        self.assertions.is_animating(expected)
    
    # === Sprite Framework Integration ===
    
    def get_app_attribute(self, attr_name: str) -> Any:
        """
        Get attribute from the running app.
        
        Useful for accessing sprites stored in app:
            player = runner.get_app_attribute("player")
            enemies = runner.get_app_attribute("enemies")
        
        Args:
            attr_name: Name of attribute to get
            
        Returns:
            Attribute value or None if not found
        """
        if not self.app:
            return None
        return getattr(self.app, attr_name, None)
    
    def get_sprite(self, attr_name: str):
        """
        Get a Sprite from the app by attribute name.
        
        Example:
            player = runner.get_sprite("player")
            assert player.x == 64
        
        Args:
            attr_name: Name of sprite attribute in app
            
        Returns:
            Sprite instance or None
        """
        sprite = self.get_app_attribute(attr_name)
        if sprite and hasattr(sprite, 'x') and hasattr(sprite, 'y'):
            return sprite
        return None
    
    def get_sprite_group(self, attr_name: str):
        """
        Get a SpriteGroup from the app by attribute name.
        
        Example:
            enemies = runner.get_sprite_group("enemies")
            assert len(enemies) == 4
        
        Args:
            attr_name: Name of sprite group attribute in app
            
        Returns:
            SpriteGroup instance or None
        """
        group = self.get_app_attribute(attr_name)
        if group and hasattr(group, 'sprites'):
            return group
        return None
    
    def get_tilemap(self, attr_name: str = "tilemap"):
        """
        Get a TileMap from the app by attribute name.
        
        Example:
            tilemap = runner.get_tilemap()
            assert tilemap.get_tile(5, 5) == 1
        
        Args:
            attr_name: Name of tilemap attribute in app (default: "tilemap")
            
        Returns:
            TileMap instance or None
        """
        tilemap = self.get_app_attribute(attr_name)
        if tilemap and hasattr(tilemap, 'tiles') and hasattr(tilemap, 'tile_size'):
            return tilemap
        return None
    
    def assert_sprite_exists(self, attr_name: str):
        """
        Assert that a sprite attribute exists in the app.
        
        Example:
            runner.assert_sprite_exists("player")
        """
        sprite = self.get_sprite(attr_name)
        assert sprite is not None, f"Sprite '{attr_name}' not found in app"
    
    def assert_sprite_at(self, attr_name: str, x: float, y: float, tolerance: float = 1.0):
        """
        Assert sprite is at expected position (within tolerance).
        
        Example:
            runner.assert_sprite_at("player", x=64, y=64, tolerance=2.0)
        
        Args:
            attr_name: Name of sprite attribute
            x: Expected x position
            y: Expected y position
            tolerance: Maximum allowed distance from expected position
        """
        sprite = self.get_sprite(attr_name)
        assert sprite is not None, f"Sprite '{attr_name}' not found"
        
        from matrixos.sprites import distance
        dist = distance(sprite.x, sprite.y, x, y)
        assert dist <= tolerance, \
            f"Sprite '{attr_name}' at ({sprite.x:.1f}, {sprite.y:.1f}), expected ({x}, {y}), distance={dist:.1f}"
    
    def assert_sprite_in_bounds(self, attr_name: str, 
                                x1: int = 0, y1: int = 0, 
                                x2: Optional[int] = None, y2: Optional[int] = None):
        """
        Assert sprite is within bounds.
        
        Example:
            runner.assert_sprite_in_bounds("player", x1=0, y1=0, x2=128, y2=128)
        
        Args:
            attr_name: Name of sprite attribute
            x1, y1: Top-left bounds
            x2, y2: Bottom-right bounds (defaults to display size)
        """
        sprite = self.get_sprite(attr_name)
        assert sprite is not None, f"Sprite '{attr_name}' not found"
        
        if x2 is None:
            x2 = self.display.width
        if y2 is None:
            y2 = self.display.height
        
        assert x1 <= sprite.x < x2, \
            f"Sprite '{attr_name}' x={sprite.x:.1f} out of bounds [{x1}, {x2})"
        assert y1 <= sprite.y < y2, \
            f"Sprite '{attr_name}' y={sprite.y:.1f} out of bounds [{y1}, {y2})"
    
    def assert_sprite_not_in_wall(self, sprite_attr: str, tilemap_attr: str = "tilemap",
                                  wall_tile_id: int = 1):
        """
        Assert sprite is not colliding with wall tiles.
        
        Example:
            runner.assert_sprite_not_in_wall("player", "tilemap", wall_tile_id=1)
        
        Args:
            sprite_attr: Name of sprite attribute
            tilemap_attr: Name of tilemap attribute
            wall_tile_id: Tile ID that represents walls
        """
        sprite = self.get_sprite(sprite_attr)
        assert sprite is not None, f"Sprite '{sprite_attr}' not found"
        
        tilemap = self.get_tilemap(tilemap_attr)
        assert tilemap is not None, f"TileMap '{tilemap_attr}' not found"
        
        collides = tilemap.sprite_collides_with_tile(sprite, wall_tile_id)
        assert not collides, \
            f"Sprite '{sprite_attr}' at ({sprite.x:.1f}, {sprite.y:.1f}) collides with wall tiles"
    
    def assert_sprites_not_overlapping(self, sprite1_attr: str, sprite2_attr: str):
        """
        Assert two sprites are not colliding.
        
        Example:
            runner.assert_sprites_not_overlapping("player", "enemy")
        
        Args:
            sprite1_attr: Name of first sprite attribute
            sprite2_attr: Name of second sprite attribute
        """
        sprite1 = self.get_sprite(sprite1_attr)
        sprite2 = self.get_sprite(sprite2_attr)
        
        assert sprite1 is not None, f"Sprite '{sprite1_attr}' not found"
        assert sprite2 is not None, f"Sprite '{sprite2_attr}' not found"
        
        collides = sprite1.collides_with(sprite2)
        assert not collides, \
            f"Sprites '{sprite1_attr}' and '{sprite2_attr}' are overlapping"
    
    def assert_sprite_group_size(self, attr_name: str, expected_size: int):
        """
        Assert sprite group has expected number of sprites.
        
        Example:
            runner.assert_sprite_group_size("enemies", 4)
        """
        group = self.get_sprite_group(attr_name)
        assert group is not None, f"SpriteGroup '{attr_name}' not found"
        
        actual = len(group)
        assert actual == expected_size, \
            f"SpriteGroup '{attr_name}' has {actual} sprites, expected {expected_size}"
    
    # === Logging Integration ===
    
    def assert_render_count_min(self, min_count: int):
        """Assert minimum number of renders."""
        self.assertions.render_count_min(min_count)
    
    # === Log Inspection ===
    
    def get_log_file(self, app_name: Optional[str] = None) -> Optional[Path]:
        """
        Get path to log file for an app.
        
        Args:
            app_name: App name (defaults to current app's name)
            
        Returns:
            Path to log file or None if not found
        """
        if app_name is None and self.app:
            app_name = self.app.name
        
        if not app_name:
            return None
        
        # Sanitize name same way logger does
        safe_name = "".join(c if c.isalnum() or c in '-_' else '_' 
                           for c in app_name.lower())
        log_file = self.log_dir / f"{safe_name}.log"
        
        if log_file.exists():
            return log_file
        return None
    
    def read_logs(self, app_name: Optional[str] = None, 
                  since_test_start: bool = False) -> str:
        """
        Read log file contents.
        
        Args:
            app_name: App name (defaults to current app)
            since_test_start: Only return logs written during this test (default: False, read all)
            
        Returns:
            Log file contents as string
        """
        log_file = self.get_log_file(app_name)
        if not log_file:
            return ""
        
        try:
            with open(log_file, 'r') as f:
                if since_test_start and log_file in self._log_start_pos:
                    # Seek to position at test start
                    f.seek(self._log_start_pos[log_file])
                return f.read()
        except:
            return ""
    
    def get_log_lines(self, app_name: Optional[str] = None,
                     since_test_start: bool = False) -> List[str]:
        """
        Get log file as list of lines.
        
        Args:
            app_name: App name (defaults to current app)
            since_test_start: Only return logs written during this test
            
        Returns:
            List of log lines
        """
        content = self.read_logs(app_name, since_test_start)
        if not content:
            return []
        return content.strip().split('\n')
    
    def log_contains(self, text: str, app_name: Optional[str] = None) -> bool:
        """
        Check if log contains specific text.
        
        Args:
            text: Text to search for
            app_name: App name (defaults to current app)
            
        Returns:
            True if text found in logs
        """
        logs = self.read_logs(app_name, since_test_start=False)
        return text in logs
    
    def count_log_occurrences(self, text: str, 
                             app_name: Optional[str] = None) -> int:
        """
        Count occurrences of text in logs.
        
        Args:
            text: Text to count
            app_name: App name (defaults to current app)
            
        Returns:
            Number of occurrences
        """
        logs = self.read_logs(app_name, since_test_start=False)
        return logs.count(text)
    
    def assert_log_contains(self, text: str, app_name: Optional[str] = None):
        """Assert that logs contain specific text."""
        if not self.log_contains(text, app_name):
            logs = self.read_logs(app_name, since_test_start=False)
            raise AssertionError(
                f"Log does not contain '{text}'\n"
                f"Recent logs:\n{logs[-500:]}"  # Show last 500 chars
            )
    
    def assert_no_errors_logged(self, app_name: Optional[str] = None):
        """Assert that no ERROR messages appear in logs."""
        logs = self.read_logs(app_name, since_test_start=False)
        error_lines = [line for line in logs.split('\n') if 'ERROR' in line]
        if error_lines:
            raise AssertionError(
                f"Found {len(error_lines)} error(s) in logs:\n" + 
                '\n'.join(error_lines)
            )
    
    def get_error_logs(self, app_name: Optional[str] = None) -> List[str]:
        """Get all ERROR log lines."""
        logs = self.read_logs(app_name, since_test_start=False)
        return [line for line in logs.split('\n') if 'ERROR' in line]
    
    def get_warning_logs(self, app_name: Optional[str] = None) -> List[str]:
        """Get all WARNING log lines."""
        logs = self.read_logs(app_name, since_test_start=False)
        return [line for line in logs.split('\n') if 'WARNING' in line]
    
    def clear_logs(self, app_name: Optional[str] = None):
        """
        Mark current log position (future reads will start from here).
        
        Useful for isolating logs from different test phases.
        """
        log_file = self.get_log_file(app_name)
        if log_file and log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    f.seek(0, 2)  # Seek to end
                    self._log_start_pos[log_file] = f.tell()
            except:
                pass
    
    def print_recent_logs(self, lines: int = 20, app_name: Optional[str] = None):
        """
        Print recent log lines (useful for debugging test failures).
        
        Args:
            lines: Number of recent lines to print
            app_name: App name (defaults to current app)
        """
        log_lines = self.get_log_lines(app_name, since_test_start=False)
        print(f"\n--- Recent logs ({len(log_lines)} lines) ---")
        for line in log_lines[-lines:]:
            print(line)
        print("--- End logs ---\n")
    
    # === Utilities ===
    
    def get_elapsed_time(self) -> float:
        """Get elapsed test time in seconds."""
        return time.time() - self.start_time
    
    def get_fps(self) -> float:
        """Calculate actual FPS achieved."""
        elapsed = self.get_elapsed_time()
        if elapsed > 0:
            return self.frame_count / elapsed
        return 0.0
    
    def __repr__(self):
        return f"TestRunner({self.app_module}, frame={self.frame_count})"


class MockOSContext:
    """
    Minimal mock of OSContext for testing.
    
    Provides just enough functionality to run apps in tests.
    """
    
    def __init__(self, matrix, input_handler):
        self.matrix = matrix
        self.input = input_handler
        self.apps = []
        self.active_app = None
        self.running = True
    
    def register_app(self, app):
        """Register an app."""
        self.apps.append(app)
        app.os = self
    
    def switch_to_app(self, app):
        """Make app active."""
        if self.active_app:
            self.active_app.active = False
            self.active_app.on_deactivate()
        
        self.active_app = app
        app.active = True
        app.on_activate()
        self.matrix.clear()
    
    def run(self):
        """
        Start event loop (no-op in testing - runner controls execution).
        
        This method is called by apps but doesn't actually loop.
        The TestRunner controls execution frame-by-frame.
        """
        pass  # TestRunner handles the loop
    
    def request_app_switch(self, app, priority='normal'):
        """Handle app requesting foreground (no-op in tests)."""
        pass
