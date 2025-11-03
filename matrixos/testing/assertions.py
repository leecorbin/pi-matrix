"""
Assertion helpers for testing MatrixOS apps.

Provides high-level assertions for common test scenarios.
"""

from typing import Tuple, Optional
from .display_adapter import HeadlessDisplay


class Assertions:
    """
    Collection of assertion helpers for display testing.
    
    Usage:
        assertions = Assertions(display)
        assertions.pixel_equals(64, 64, (255, 0, 0))
        assertions.text_was_drawn("GAME OVER")
    """
    
    def __init__(self, display: HeadlessDisplay):
        """
        Initialize assertions with a display adapter.
        
        Args:
            display: HeadlessDisplay instance to inspect
        """
        self.display = display
    
    def pixel_equals(self, x: int, y: int, color: Tuple[int, int, int], 
                     tolerance: int = 0, message: str = ""):
        """
        Assert pixel has expected color.
        
        Args:
            x, y: Pixel coordinates
            color: Expected RGB tuple
            tolerance: Allow color values to differ by this amount
            message: Custom error message
        """
        actual = self.display.get_pixel(x, y)
        if not self._color_match(actual, color, tolerance):
            msg = message or f"Pixel at ({x},{y}) is {actual}, expected {color}"
            raise AssertionError(msg)
    
    def pixel_not_equals(self, x: int, y: int, color: Tuple[int, int, int],
                        tolerance: int = 0, message: str = ""):
        """Assert pixel does NOT have a color."""
        actual = self.display.get_pixel(x, y)
        if self._color_match(actual, color, tolerance):
            msg = message or f"Pixel at ({x},{y}) should not be {color}"
            raise AssertionError(msg)
    
    def color_count(self, color: Tuple[int, int, int], 
                   expected: int, tolerance: int = 0, message: str = ""):
        """
        Assert exact number of pixels of a color.
        
        Args:
            color: RGB tuple to count
            expected: Expected pixel count
            tolerance: Color matching tolerance
            message: Custom error message
        """
        actual = self.display.count_color(color, tolerance)
        if actual != expected:
            msg = message or f"Expected {expected} pixels of {color}, found {actual}"
            raise AssertionError(msg)
    
    def color_count_min(self, color: Tuple[int, int, int],
                       min_count: int, tolerance: int = 0, message: str = ""):
        """Assert minimum number of pixels of a color."""
        actual = self.display.count_color(color, tolerance)
        if actual < min_count:
            msg = message or f"Expected at least {min_count} pixels of {color}, found {actual}"
            raise AssertionError(msg)
    
    def color_count_max(self, color: Tuple[int, int, int],
                       max_count: int, tolerance: int = 0, message: str = ""):
        """Assert maximum number of pixels of a color."""
        actual = self.display.count_color(color, tolerance)
        if actual > max_count:
            msg = message or f"Expected at most {max_count} pixels of {color}, found {actual}"
            raise AssertionError(msg)
    
    def text_was_drawn(self, text: str, message: str = ""):
        """
        Assert text was drawn to display.
        
        Note: This checks if text() was called with this string,
        not pixel-perfect rendering.
        """
        if not self.display.text_was_drawn(text):
            drawn_texts = self.display.get_text_calls()
            msg = message or f"Text '{text}' not found. Drawn texts: {drawn_texts}"
            raise AssertionError(msg)
    
    def text_not_drawn(self, text: str, message: str = ""):
        """Assert text was NOT drawn."""
        if self.display.text_was_drawn(text):
            msg = message or f"Text '{text}' should not be drawn"
            raise AssertionError(msg)
    
    def render_count(self, expected: int, message: str = ""):
        """Assert exact number of renders."""
        actual = self.display.render_count
        if actual != expected:
            msg = message or f"Expected {expected} renders, got {actual}"
            raise AssertionError(msg)
    
    def render_count_min(self, min_count: int, message: str = ""):
        """Assert minimum number of renders."""
        actual = self.display.render_count
        if actual < min_count:
            msg = message or f"Expected at least {min_count} renders, got {actual}"
            raise AssertionError(msg)
    
    def is_animating(self, expected: bool = True, message: str = ""):
        """Assert display is/isn't changing between frames."""
        actual = self.display.is_changing()
        if actual != expected:
            state = "animating" if actual else "static"
            expected_state = "animating" if expected else "static"
            msg = message or f"Display is {state}, expected {expected_state}"
            raise AssertionError(msg)
    
    def blob_count(self, color: Tuple[int, int, int], 
                  expected: int, min_size: int = 1, tolerance: int = 0,
                  message: str = ""):
        """
        Assert number of distinct blobs (connected regions) of a color.
        
        Useful for counting sprites/objects on screen.
        """
        blobs = self.display.find_blobs(color, min_size, tolerance)
        actual = len(blobs)
        if actual != expected:
            msg = message or f"Expected {expected} blobs of {color}, found {actual}"
            raise AssertionError(msg)
    
    def snapshot_matches(self, snapshot, similarity: float = 0.99, message: str = ""):
        """
        Assert current display matches a previous snapshot.
        
        Args:
            snapshot: numpy array from display.snapshot()
            similarity: Required similarity (0-1, 1=identical)
            message: Custom error message
        """
        actual_similarity = self.display.compare(snapshot)
        if actual_similarity < similarity:
            msg = message or (
                f"Display doesn't match snapshot "
                f"(similarity: {actual_similarity:.1%}, required: {similarity:.1%})"
            )
            raise AssertionError(msg)
    
    def _color_match(self, c1: Tuple[int, int, int], c2: Tuple[int, int, int],
                     tolerance: int) -> bool:
        """Check if two colors match within tolerance."""
        return all(abs(c1[i] - c2[i]) <= tolerance for i in range(3))
