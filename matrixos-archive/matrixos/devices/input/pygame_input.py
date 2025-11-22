"""
Pygame Input Driver

Captures keyboard input from Pygame window events.
Works seamlessly with MacOSWindowDriver.
"""

import pygame
from typing import List
from ..base import InputDriver
from ...input import InputEvent


class PygameInputDriver(InputDriver):
    """Pygame window keyboard input"""
    
    def __init__(self):
        self.name = "Pygame Keyboard"
        self.device_class = "keyboard"
        self.platform = "macos"
        self.events = []
        
        # Key mapping: Pygame key -> InputEvent key
        self.key_map = {
            pygame.K_UP: InputEvent.UP,
            pygame.K_DOWN: InputEvent.DOWN,
            pygame.K_LEFT: InputEvent.LEFT,
            pygame.K_RIGHT: InputEvent.RIGHT,
            pygame.K_RETURN: InputEvent.OK,
            pygame.K_SPACE: InputEvent.ACTION,
            pygame.K_BACKSPACE: InputEvent.BACK,
            pygame.K_ESCAPE: InputEvent.HOME,
            pygame.K_TAB: InputEvent.HELP,
        }
    
    def initialize(self) -> bool:
        """Initialize (pygame already initialized by display driver)"""
        return pygame.get_init()
    
    def poll(self) -> List[InputEvent]:
        """
        Poll for keyboard events from Pygame.
        Must be called frequently to keep window responsive.
        """
        events = []
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Window close button pressed
                events.append(InputEvent('HOME'))
            elif event.type == pygame.KEYDOWN:
                # Check mapped keys
                if event.key in self.key_map:
                    events.append(InputEvent(self.key_map[event.key]))
                else:
                    # Pass through other keys as characters
                    try:
                        char = event.unicode
                        if char and char.isprintable():
                            events.append(InputEvent(char))
                    except:
                        pass
        
        return events
    
    def cleanup(self):
        """Cleanup (handled by display driver)"""
        pass
    
    def requires_pairing(self) -> bool:
        """No pairing needed"""
        return False
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if Pygame is available and initialized"""
        try:
            import pygame
            return pygame.get_init()
        except ImportError:
            return False
    
    @classmethod
    def get_priority(cls) -> int:
        """
        Priority: 50 (higher than terminal)
        Should be used when Pygame window is active.
        """
        return 50
    
    @classmethod
    def get_platform_preference(cls) -> str:
        """This driver is preferred on macOS when using Pygame window"""
        return "macos"
