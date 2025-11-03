#!/usr/bin/env python3
"""
Smoke Tests - Verify apps don't crash on launch.

Usage: python3 tests/smoke_test.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Suppress terminal output during tests
import io
_original_stdout = sys.stdout


class MockMatrix:
    """Mock LED matrix that captures calls without rendering."""
    
    def __init__(self, width=128, height=128):
        self.width = width
        self.height = height
        self.call_count = {}
    
    def _track_call(self, name):
        """Track method calls for debugging."""
        self.call_count[name] = self.call_count.get(name, 0) + 1
    
    def set_pixel(self, *args, **kwargs):
        self._track_call('set_pixel')
    
    def clear(self, *args, **kwargs):
        self._track_call('clear')
    
    def fill(self, *args, **kwargs):
        self._track_call('fill')
    
    def line(self, *args, **kwargs):
        self._track_call('line')
    
    def rect(self, *args, **kwargs):
        self._track_call('rect')
    
    def circle(self, *args, **kwargs):
        self._track_call('circle')
    
    def ellipse(self, *args, **kwargs):
        self._track_call('ellipse')
    
    def polygon(self, *args, **kwargs):
        self._track_call('polygon')
    
    def text(self, *args, **kwargs):
        self._track_call('text')
    
    def centered_text(self, *args, **kwargs):
        self._track_call('centered_text')
    
    def border(self, *args, **kwargs):
        self._track_call('border')
    
    def grid_lines(self, *args, **kwargs):
        self._track_call('grid_lines')
    
    def show(self, *args, **kwargs):
        self._track_call('show')
        # Don't render to terminal!


class MockInput:
    """Mock input that returns no events."""
    
    def get_key(self, timeout=0.0):
        return None


class MockFramework:
    """Minimal mock of AppFramework for smoke testing."""
    
    def __init__(self):
        self.apps = []
        self.active_app = None
        self.matrix = MockMatrix()
        self.input = MockInput()
        self.running = True
        self.frame_count = 0
        self.max_frames = 60  # Run for 1 second at 60fps
    
    def register_app(self, app):
        self.apps.append(app)
    
    def switch_to_app(self, app):
        self.active_app = app
        app.on_activate()
    
    def run(self):
        """Run event loop for a fixed number of frames."""
        import time
        
        while self.running and self.frame_count < self.max_frames:
            # Simulate frame timing
            start_time = time.time()
            
            # Update active app
            if self.active_app:
                delta = 1.0 / 60.0  # 60fps
                self.active_app.on_update(delta)
                
                # Render if dirty
                if self.active_app.dirty:
                    self.matrix.clear()
                    self.active_app.render(self.matrix)
                    self.matrix.show()
            
            self.frame_count += 1
            
            # Simulate frame rate limit
            elapsed = time.time() - start_time
            sleep_time = max(0, (1.0/60.0) - elapsed)
            time.sleep(sleep_time)


def run_smoke_test(app_name, import_path):
    """
    Test that an app can launch and render without crashing.
    
    Args:
        app_name: Display name for test output
        import_path: Python import path (e.g., "examples.platformer.main")
    """
    print(f"Testing {app_name}...", end=" ")
    
    # Suppress stdout during test
    sys.stdout = io.StringIO()
    
    try:
        # Import the app module
        module = __import__(import_path, fromlist=['run'])
        
        # Create mock framework
        framework = MockFramework()
        
        # Run the app
        module.run(framework)
        
        # Restore stdout
        sys.stdout = _original_stdout
        
        # Verify app did something
        if framework.frame_count == 0:
            print(f"✗ FAILED: No frames rendered")
            return False
        
        if not framework.matrix.call_count:
            print(f"✗ FAILED: No drawing operations")
            return False
        
        # Success!
        renders = framework.matrix.call_count.get('show', 0)
        print(f"✓ PASSED ({framework.frame_count} frames, {renders} renders)")
        return True
        
    except Exception as e:
        # Restore stdout
        sys.stdout = _original_stdout
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("MatrixOS Smoke Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Platformer", "examples.platformer.main"),
        ("Space Invaders", "examples.space_invaders.main"),
    ]
    
    results = []
    for app_name, import_path in tests:
        passed = run_smoke_test(app_name, import_path)
        results.append((app_name, passed))
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for app_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {app_name}")
    
    print()
    print(f"Result: {passed_count}/{total_count} tests passed")
    
    # Exit with error code if any failed
    if passed_count < total_count:
        sys.exit(1)
    else:
        print()
        print("All tests passed! 🎉")
        sys.exit(0)


if __name__ == "__main__":
    main()
