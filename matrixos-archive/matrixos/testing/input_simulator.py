"""
Input event simulator for automated testing.

Allows programmatic injection of keyboard events with precise timing control.
"""

from typing import Optional, List, Tuple
from matrixos.input import InputEvent


class InputSimulator:
    """
    Simulate keyboard input programmatically for testing.
    
    Replaces KeyboardInput during tests to provide deterministic input sequences.
    """
    
    def __init__(self):
        """Initialize input simulator."""
        self.event_queue = []  # List of (frame, key) tuples
        self.frame = 0
        self.event_history = []  # Track all events for debugging
    
    def inject(self, key: str):
        """
        Inject an input event immediately (next frame).
        
        Args:
            key: Key constant (e.g., InputEvent.UP) or raw character
        """
        self.schedule_event(key, at_frame=self.frame + 1)
    
    def schedule_event(self, key: str, at_frame: Optional[int] = None, 
                      at_time: Optional[float] = None):
        """
        Schedule an input event for a specific frame or time.
        
        Args:
            key: Key constant or raw character
            at_frame: Frame number to inject event
            at_time: Time in seconds (converted to frames at 60fps)
        """
        if at_frame is None:
            if at_time is not None:
                at_frame = int(at_time * 60)  # Convert to frames at 60fps
            else:
                at_frame = self.frame + 1
        
        self.event_queue.append((at_frame, key))
        self.event_queue.sort()  # Keep sorted by frame
    
    def inject_sequence(self, keys: List[str], delay_frames: int = 6):
        """
        Schedule a sequence of keys with delays.
        
        Args:
            keys: List of keys to inject
            delay_frames: Frames between each key (default 6 = 0.1s at 60fps)
        """
        for i, key in enumerate(keys):
            self.schedule_event(key, at_frame=self.frame + 1 + i * delay_frames)
    
    def inject_repeat(self, key: str, count: int, delay_frames: int = 6):
        """
        Inject the same key multiple times.
        
        Args:
            key: Key to inject
            count: Number of repetitions
            delay_frames: Frames between each injection
        """
        for i in range(count):
            self.schedule_event(key, at_frame=self.frame + 1 + i * delay_frames)
    
    def get_key(self, timeout: float = 0.0) -> Optional[InputEvent]:
        """
        Get next scheduled event if frame matches.
        
        Args:
            timeout: Ignored (for compatibility with KeyboardInput API)
            
        Returns:
            InputEvent if one is scheduled for current frame, else None
        """
        # Check if any events scheduled for current frame
        while self.event_queue and self.event_queue[0][0] <= self.frame:
            frame, key = self.event_queue.pop(0)
            event = InputEvent(key)
            self.event_history.append((self.frame, key))
            return event
        
        return None
    
    def advance_frame(self):
        """Move to next frame (called by test runner)."""
        self.frame += 1
    
    def clear_queue(self):
        """Clear all scheduled events."""
        self.event_queue.clear()
    
    def peek_next(self) -> Optional[Tuple[int, str]]:
        """
        Look at next scheduled event without consuming it.
        
        Returns:
            (frame, key) tuple or None if queue empty
        """
        if self.event_queue:
            return self.event_queue[0]
        return None
    
    def wait_for_key(self) -> InputEvent:
        """
        Wait for next event (blocks until one is available).
        
        For compatibility with KeyboardInput API.
        """
        while True:
            event = self.get_key()
            if event:
                return event
            self.advance_frame()
    
    def close(self):
        """Clean up (no-op for simulator)."""
        pass
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()
    
    def __repr__(self):
        return f"InputSimulator(frame={self.frame}, queued={len(self.event_queue)})"
