"""
Headless display adapter with rich inspection capabilities.

Provides a display that captures all drawing operations without rendering
to terminal, plus methods to inspect the display buffer for testing.

Uses pure Python (no numpy) to minimize dependencies.
"""

from typing import List, Tuple, Optional, Set
from collections import deque
import copy


class HeadlessDisplay:
    """
    Display adapter that captures drawing operations without rendering.
    
    Compatible with LEDMatrix API. Uses pure Python lists (no numpy).
    """
    
    def __init__(self, width: int = 128, height: int = 128):
        """
        Initialize headless display.
        
        Args:
            width: Display width in pixels
            height: Display height in pixels
        """
        self.width = width
        self.height = height
        
        # Pure Python buffer: list of lists of tuples (r, g, b)
        self.buffer = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]
        self.render_count = 0
        self.history = deque(maxlen=60)  # Keep last 60 frames (1 second at 60fps)
        self.call_log = []  # Track all drawing calls
    
    # === Core Display Methods (Compatible with LEDMatrix) ===
    
    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]):
        """Set a single pixel."""
        self._log_call('set_pixel', x=x, y=y, color=color)
        x, y = int(x), int(y)  # Ensure integers
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[y][x] = color
    
    def clear(self, color: Optional[Tuple[int, int, int]] = None):
        """Clear display to color (or black)."""
        self._log_call('clear', color=color)
        if color is None:
            color = (0, 0, 0)
        for y in range(self.height):
            for x in range(self.width):
                self.buffer[y][x] = color
    
    def fill(self, color: Tuple[int, int, int]):
        """Fill entire display with color."""
        self._log_call('fill', color=color)
        for y in range(self.height):
            for x in range(self.width):
                self.buffer[y][x] = color
    
    def line(self, x1: int, y1: int, x2: int, y2: int, color: Tuple[int, int, int]):
        """Draw a line."""
        self._log_call('line', x1=x1, y1=y1, x2=x2, y2=y2, color=color)
        # Bresenham's line algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            self.set_pixel(x, y, color)
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def rect(self, x: int, y: int, width: int, height: int, 
             color: Tuple[int, int, int], fill: bool = False):
        """Draw a rectangle."""
        self._log_call('rect', x=x, y=y, width=width, height=height, color=color, fill=fill)
        if fill:
            for dy in range(height):
                for dx in range(width):
                    self.set_pixel(x + dx, y + dy, color)
        else:
            # Draw outline
            for dx in range(width):
                self.set_pixel(x + dx, y, color)
                self.set_pixel(x + dx, y + height - 1, color)
            for dy in range(height):
                self.set_pixel(x, y + dy, color)
                self.set_pixel(x + width - 1, y + dy, color)
    
    def circle(self, cx: int, cy: int, radius: int, 
               color: Tuple[int, int, int], fill: bool = False):
        """Draw a circle."""
        self._log_call('circle', cx=cx, cy=cy, radius=radius, color=color, fill=fill)
        # Midpoint circle algorithm
        x = radius
        y = 0
        err = 0
        
        while x >= y:
            if fill:
                self.line(cx - x, cy + y, cx + x, cy + y, color)
                self.line(cx - x, cy - y, cx + x, cy - y, color)
                self.line(cx - y, cy + x, cx + y, cy + x, color)
                self.line(cx - y, cy - x, cx + y, cy - x, color)
            else:
                self.set_pixel(cx + x, cy + y, color)
                self.set_pixel(cx + y, cy + x, color)
                self.set_pixel(cx - y, cy + x, color)
                self.set_pixel(cx - x, cy + y, color)
                self.set_pixel(cx - x, cy - y, color)
                self.set_pixel(cx - y, cy - x, color)
                self.set_pixel(cx + y, cy - x, color)
                self.set_pixel(cx + x, cy - y, color)
            
            if err <= 0:
                y += 1
                err += 2 * y + 1
            if err > 0:
                x -= 1
                err -= 2 * x + 1
    
    def text(self, text: str, x: int, y: int, color: Tuple[int, int, int],
             bg_color: Optional[Tuple[int, int, int]] = None, scale: int = 1):
        """Draw text (simplified - just logs the call)."""
        self._log_call('text', text=text, x=x, y=y, color=color, bg_color=bg_color, scale=scale)
        # For testing, we track text calls but don't actually render
        # Real font rendering would need the Font class
    
    def show(self, renderer=None, clear_screen: bool = True):
        """
        Capture show() call without rendering to terminal.
        
        Saves current buffer to history for animation detection.
        """
        self._log_call('show')
        self.render_count += 1
        self.history.append(copy.deepcopy(self.buffer))
    
    # === Inspection Methods (Testing-specific) ===
    
    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get RGB value at coordinate."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.buffer[y][x]
        return (0, 0, 0)
    
    def find_color(self, color: Tuple[int, int, int], 
                   tolerance: int = 0) -> List[Tuple[int, int]]:
        """
        Find all pixels matching a color.
        
        Args:
            color: RGB tuple to search for
            tolerance: Allow color values to differ by this amount
            
        Returns:
            List of (x, y) coordinates
        """
        matches = []
        for y in range(self.height):
            for x in range(self.width):
                if self._color_match(self.buffer[y][x], color, tolerance):
                    matches.append((x, y))
        return matches
    
    def count_color(self, color: Tuple[int, int, int], tolerance: int = 0) -> int:
        """Count pixels of a specific color."""
        return len(self.find_color(color, tolerance))
    
    def find_blobs(self, color: Tuple[int, int, int], 
                   min_size: int = 1, tolerance: int = 0) -> List[List[Tuple[int, int]]]:
        """
        Find connected regions (blobs) of a color.
        
        Args:
            color: RGB tuple to search for
            min_size: Minimum pixels in blob
            tolerance: Color matching tolerance
            
        Returns:
            List of blobs, where each blob is a list of (x, y) coordinates
        """
        pixels = set(self.find_color(color, tolerance))
        blobs = []
        
        while pixels:
            # Flood fill to find connected component
            start = pixels.pop()
            blob = self._flood_fill(start, pixels)
            if len(blob) >= min_size:
                blobs.append(blob)
        
        return blobs
    
    def get_centroid(self, pixels: List[Tuple[int, int]]) -> Tuple[float, float]:
        """Calculate centroid of pixel list."""
        if not pixels:
            return (0.0, 0.0)
        x_avg = sum(p[0] for p in pixels) / len(pixels)
        y_avg = sum(p[1] for p in pixels) / len(pixels)
        return (x_avg, y_avg)
    
    def get_bounding_box(self, pixels: List[Tuple[int, int]]) -> Tuple[int, int, int, int]:
        """Get bounding box (x, y, width, height) of pixel list."""
        if not pixels:
            return (0, 0, 0, 0)
        xs = [p[0] for p in pixels]
        ys = [p[1] for p in pixels]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        return (x_min, y_min, x_max - x_min + 1, y_max - y_min + 1)
    
    def snapshot(self) -> List[List[Tuple[int, int, int]]]:
        """Get copy of current buffer."""
        return copy.deepcopy(self.buffer)
    
    def compare(self, snapshot: List[List[Tuple[int, int, int]]], tolerance: float = 0.01) -> float:
        """
        Compare current display to snapshot.
        
        Args:
            snapshot: Previous buffer state
            tolerance: Fraction of pixels that can differ
            
        Returns:
            Similarity score 0.0-1.0 (1.0 = identical)
        """
        if len(snapshot) != self.height or len(snapshot[0]) != self.width:
            return 0.0
        
        # Count differing pixels
        total_diff = 0
        max_possible = 255 * 3  # Max RGB difference per pixel
        
        for y in range(self.height):
            for x in range(self.width):
                for c in range(3):  # R, G, B
                    total_diff += abs(self.buffer[y][x][c] - snapshot[y][x][c])
        
        # Normalize to 0-1 range
        max_diff = max_possible * self.width * self.height
        similarity = 1.0 - (total_diff / max_diff)
        return similarity
    
    def is_changing(self, frames: int = 2) -> bool:
        """
        Check if display is animating (changing between frames).
        
        Args:
            frames: Number of recent frames to compare
            
        Returns:
            True if display changed in last N frames
        """
        if len(self.history) < frames:
            return False
        
        recent = list(self.history)[-frames:]
        for i in range(len(recent) - 1):
            if recent[i] != recent[i+1]:  # Compare buffers
                return True
        return False
    
    def text_was_drawn(self, text: str) -> bool:
        """
        Check if text() was called with this string.
        
        Note: This checks call log, not actual pixels (font rendering needed for that).
        """
        for call in self.call_log:
            if call['method'] == 'text' and call['kwargs'].get('text') == text:
                return True
        return False
    
    def get_text_calls(self) -> List[str]:
        """Get all text strings that were drawn."""
        texts = []
        for call in self.call_log:
            if call['method'] == 'text':
                texts.append(call['kwargs'].get('text', ''))
        return texts
    
    # === Helper Methods ===
    
    def _log_call(self, method: str, **kwargs):
        """Log a drawing method call."""
        self.call_log.append({
            'method': method,
            'kwargs': kwargs,
            'frame': self.render_count
        })
    
    def _color_match(self, c1: Tuple[int, int, int], c2: Tuple[int, int, int], 
                     tolerance: int) -> bool:
        """Check if two colors match within tolerance."""
        return all(abs(c1[i] - c2[i]) <= tolerance for i in range(3))
    
    def _flood_fill(self, start: Tuple[int, int], 
                    pixels: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Flood fill to find connected pixels."""
        blob = [start]
        queue = [start]
        
        while queue:
            x, y = queue.pop(0)
            
            # Check 4-connected neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor in pixels:
                    pixels.remove(neighbor)
                    blob.append(neighbor)
                    queue.append(neighbor)
        
        return blob
    
    def __repr__(self):
        return f"HeadlessDisplay({self.width}x{self.height}, {self.render_count} renders)"
