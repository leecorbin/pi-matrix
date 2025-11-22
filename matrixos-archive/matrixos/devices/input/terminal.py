"""
Terminal Input Driver

Cross-platform input driver that reads from terminal/keyboard.
Uses the existing KeyboardInput class.
"""

from typing import List
from ..base import InputDriver
from ...input import KeyboardInput, InputEvent as MatrixInputEvent


class TerminalInputDriver(InputDriver):
    """Input driver for terminal keyboard input"""
    
    def __init__(self):
        super().__init__()
        self.name = "Terminal Keyboard"
        self.keyboard = None
    
    def initialize(self) -> bool:
        """Initialize keyboard input"""
        try:
            self.keyboard = KeyboardInput()
            self.connected = True
            return True
        except Exception as e:
            print(f"[TerminalInput] Initialization failed: {e}")
            return False
    
    def poll(self) -> List:
        """Poll for keyboard events"""
        if not self.keyboard:
            return []
        
        events = []
        # Non-blocking poll
        event = self.keyboard.get_key(timeout=0.0)
        if event:
            events.append(event)
        
        return events
    
    def cleanup(self):
        """Restore terminal settings"""
        if self.keyboard:
            self.keyboard._restore_terminal()
    
    @classmethod
    def is_available(cls) -> bool:
        """Terminal input always available"""
        return True
    
    @classmethod
    def requires_pairing(cls) -> bool:
        """No pairing needed"""
        return False
    
    @classmethod
    def get_device_class(cls) -> str:
        """This is a keyboard"""
        return "keyboard"
    
    @classmethod
    def get_priority(cls) -> int:
        """Low priority - used as fallback"""
        return 10
