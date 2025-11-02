"""
Audio system for MatrixOS.

Works in two modes:
1. Terminal mode (Mac/Linux/SSH): System beep + visual indicators
2. Hardware mode (Raspberry Pi): Real audio output via speaker

Example:
    from matrixos import audio
    
    # Play sounds
    audio.play('beep')      # System beep
    audio.play('success')   # Success sound
    audio.play('error')     # Error sound
    audio.play('alarm')     # Alarm sound
    
    # Play notes
    audio.note('C4', duration=0.5)
    audio.note('E4', duration=0.5)
    
    # Music
    audio.play_melody([
        ('C4', 0.25), ('E4', 0.25), ('G4', 0.5)
    ])
"""

import sys
import os
import time
from typing import Optional, List, Tuple


class AudioSystem:
    """Audio system with terminal and hardware modes."""
    
    # Note frequencies (Hz)
    NOTES = {
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
        'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46,
        'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
        'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61,
        'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
    }
    
    # Predefined sound effects (note sequences)
    SOUNDS = {
        'beep': [('A4', 0.1)],
        'success': [('C5', 0.1), ('E5', 0.1), ('G5', 0.2)],
        'error': [('E3', 0.15), ('C3', 0.25)],
        'alarm': [('G5', 0.2), ('G5', 0.2), ('G5', 0.2)],
        'coin': [('B5', 0.05), ('E5', 0.15)],
        'jump': [('C4', 0.05), ('G4', 0.1)],
        'hit': [('G3', 0.05), ('D3', 0.1)],
        'powerup': [('C4', 0.08), ('E4', 0.08), ('G4', 0.08), ('C5', 0.15)],
        'gameover': [('E4', 0.2), ('D4', 0.2), ('C4', 0.4)],
    }
    
    def __init__(self, mode: str = 'auto'):
        """
        Initialize audio system.
        
        Args:
            mode: 'terminal', 'hardware', or 'auto' (detect)
        """
        if mode == 'auto':
            # Auto-detect: Try hardware first, fall back to terminal
            self.mode = self._detect_mode()
        else:
            self.mode = mode
        
        self.enabled = True
        self.volume = 0.7  # 0.0 to 1.0
        
        # Initialize hardware if available
        if self.mode == 'hardware':
            self._init_hardware()
    
    def _detect_mode(self) -> str:
        """Detect available audio mode."""
        # Check if running on Raspberry Pi with audio hardware
        if os.path.exists('/dev/snd') and os.path.exists('/sys/class/gpio'):
            # Likely Raspberry Pi with audio
            return 'hardware'
        else:
            # Use terminal mode (works everywhere)
            return 'terminal'
    
    def _init_hardware(self):
        """Initialize hardware audio (Raspberry Pi)."""
        try:
            # Try to import pygame for audio (if available)
            import pygame.mixer
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.hardware_available = True
            print("Audio: Hardware mode (pygame)")
        except ImportError:
            # Fall back to terminal mode
            self.mode = 'terminal'
            self.hardware_available = False
            print("Audio: Terminal mode (pygame not available)")
    
    def play(self, sound_name: str):
        """
        Play a predefined sound effect.
        
        Args:
            sound_name: Name of sound ('beep', 'success', 'error', etc.)
        """
        if not self.enabled:
            return
        
        if sound_name in self.SOUNDS:
            melody = self.SOUNDS[sound_name]
            self.play_melody(melody)
        else:
            # Unknown sound, play generic beep
            self._terminal_beep()
    
    def note(self, note_name: str, duration: float = 0.2):
        """
        Play a musical note.
        
        Args:
            note_name: Note name ('C4', 'E5', etc.)
            duration: Duration in seconds
        """
        if not self.enabled:
            return
        
        if self.mode == 'terminal':
            self._terminal_beep()
            time.sleep(duration)
        elif self.mode == 'hardware':
            freq = self.NOTES.get(note_name, 440)
            self._hardware_play_tone(freq, duration)
    
    def play_melody(self, notes: List[Tuple[str, float]]):
        """
        Play a sequence of notes.
        
        Args:
            notes: List of (note_name, duration) tuples
        """
        if not self.enabled:
            return
        
        for note_name, duration in notes:
            self.note(note_name, duration)
    
    def _terminal_beep(self):
        """Play system beep in terminal."""
        # ASCII BEL character (makes terminal beep)
        sys.stdout.write('\a')
        sys.stdout.flush()
    
    def _hardware_play_tone(self, frequency: float, duration: float):
        """Play tone on hardware speaker (Raspberry Pi)."""
        if not hasattr(self, 'hardware_available') or not self.hardware_available:
            self._terminal_beep()
            return
        
        try:
            import pygame.sndarray
            import numpy as np
            
            # Generate sine wave
            sample_rate = 22050
            n_samples = int(sample_rate * duration)
            buf = np.sin(2 * np.pi * frequency * np.linspace(0, duration, n_samples))
            
            # Apply volume
            buf = (buf * self.volume * 32767).astype(np.int16)
            
            # Create stereo sound
            stereo_buf = np.zeros((n_samples, 2), dtype=np.int16)
            stereo_buf[:, 0] = buf
            stereo_buf[:, 1] = buf
            
            # Play sound
            sound = pygame.sndarray.make_sound(stereo_buf)
            sound.play()
            
            # Wait for sound to finish
            time.sleep(duration)
        
        except Exception as e:
            # Fall back to terminal beep
            self._terminal_beep()
            time.sleep(duration)
    
    def set_volume(self, volume: float):
        """
        Set audio volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
    
    def enable(self):
        """Enable audio."""
        self.enabled = True
    
    def disable(self):
        """Disable audio (mute)."""
        self.enabled = False
    
    def toggle(self) -> bool:
        """
        Toggle audio on/off.
        
        Returns:
            New enabled state
        """
        self.enabled = not self.enabled
        return self.enabled


# Global audio instance
_audio = None


def get_audio() -> AudioSystem:
    """Get the global audio system instance."""
    global _audio
    if _audio is None:
        _audio = AudioSystem()
    return _audio


# Convenience functions
def play(sound_name: str):
    """Play a sound effect."""
    get_audio().play(sound_name)


def note(note_name: str, duration: float = 0.2):
    """Play a musical note."""
    get_audio().note(note_name, duration)


def play_melody(notes: List[Tuple[str, float]]):
    """Play a melody."""
    get_audio().play_melody(notes)


def set_volume(volume: float):
    """Set audio volume (0.0 to 1.0)."""
    get_audio().set_volume(volume)


def enable():
    """Enable audio."""
    get_audio().enable()


def disable():
    """Disable audio."""
    get_audio().disable()


def toggle() -> bool:
    """Toggle audio on/off."""
    return get_audio().toggle()
