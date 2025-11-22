#!/usr/bin/env python3
"""
Clock - ZX Spectrum Edition for 256×192
=========================================

Features:
- Giant digital time display with Spectrum colors
- Analog clock face with chunky hands
- Date and day display
- Side panels with mode indicators
- Pulsing seconds display
- Multiple display modes (toggle with OK)
"""

import sys
import os
import math
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent

# ZX Spectrum color palette
CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 40)
YELLOW = (255, 255, 0)
BRIGHT_YELLOW = (255, 255, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

class ClockApp(App):
    """ZX Spectrum clock with multiple display modes."""
    
    def __init__(self):
        super().__init__("Clock")
        self.mode = 0  # 0: digital, 1: analog, 2: both
        self.pulse_counter = 0
        self.panel_width = 32
        self.center_width = 192
        
    def on_activate(self):
        """Initialize app."""
        self.mode = 0
        self.pulse_counter = 0
        self.dirty = True
    
    def on_deactivate(self):
        """Cleanup when exiting."""
        pass
    
    def on_event(self, event):
        """Handle user input."""
        if event.key == InputEvent.OK:
            # Toggle mode
            self.mode = (self.mode + 1) % 3
            self.dirty = True
            return True
        return False
    
    def on_update(self, delta_time):
        """Update app state."""
        self.pulse_counter += 1
        # Redraw every frame for smooth pulsing
        self.dirty = True
    
    def draw_analog_clock(self, matrix, center_x, center_y, radius):
        """Draw Spectrum-style analog clock face."""
        now = datetime.now()
        
        # Draw double circle border (Spectrum style)
        matrix.circle(center_x, center_y, radius, CYAN)
        matrix.circle(center_x, center_y, radius - 2, CYAN)
        
        # Draw chunky hour markers
        for hour in range(12):
            angle = math.radians(hour * 30 - 90)
            outer_x = int(center_x + (radius - 4) * math.cos(angle))
            outer_y = int(center_y + (radius - 4) * math.sin(angle))
            inner_x = int(center_x + (radius - 10) * math.cos(angle))
            inner_y = int(center_y + (radius - 10) * math.sin(angle))
            
            color = YELLOW if hour % 3 == 0 else WHITE
            # Thicker lines
            for offset in range(-1, 2):
                if hour % 2 == 0:  # Vertical markers
                    matrix.line(outer_x + offset, outer_y, inner_x + offset, inner_y, color)
                else:  # Horizontal markers
                    matrix.line(outer_x, outer_y + offset, inner_x, inner_y + offset, color)
        
        # Calculate hand angles
        hours = now.hour % 12
        minutes = now.minute
        seconds = now.second
        
        hour_angle = math.radians((hours * 30 + minutes * 0.5) - 90)
        minute_angle = math.radians((minutes * 6) - 90)
        second_angle = math.radians((seconds * 6) - 90)
        
        # Draw hour hand (short, chunky)
        hour_length = radius * 0.5
        hour_x = int(center_x + hour_length * math.cos(hour_angle))
        hour_y = int(center_y + hour_length * math.sin(hour_angle))
        for offset in range(-2, 3):
            matrix.line(center_x, center_y + offset, hour_x, hour_y + offset, YELLOW)
        
        # Draw minute hand (longer, medium)
        minute_length = radius * 0.7
        minute_x = int(center_x + minute_length * math.cos(minute_angle))
        minute_y = int(center_y + minute_length * math.sin(minute_angle))
        for offset in range(-1, 2):
            matrix.line(center_x + offset, center_y, minute_x + offset, minute_y, GREEN)
        
        # Draw second hand (longest, thin, pulsing red)
        second_length = radius * 0.85
        second_x = int(center_x + second_length * math.cos(second_angle))
        second_y = int(center_y + second_length * math.sin(second_angle))
        pulse = 128 + int(127 * math.sin(self.pulse_counter * 0.1))
        second_color = (pulse, 0, 0)
        matrix.line(center_x, center_y, second_x, second_y, second_color)
        
        # Center dot (chunky)
        matrix.circle(center_x, center_y, 3, WHITE, fill=True)
    
    def render(self, matrix):
        """Draw app UI with Spectrum aesthetic."""
        matrix.clear()
        matrix.rect(0, 0, 256, 192, DARK_BLUE, fill=True)
        
        now = datetime.now()
        
        if self.mode == 0:
            # Digital only - GIANT display
            time_str = now.strftime("%H:%M")
            # Draw each digit large
            x = 40
            for char in time_str:
                if char == ':':
                    # Pulsing colon
                    if (self.pulse_counter // 30) % 2 == 0:
                        matrix.text(char, x, 70, BRIGHT_YELLOW)
                    x += 16
                else:
                    # Large cyan digits
                    matrix.text(char, x, 70, CYAN)
                    x += 32
            
            # Seconds below (pulsing)
            sec_str = now.strftime("%S")
            pulse = 128 + int(127 * math.sin(self.pulse_counter * 0.1))
            sec_color = (pulse, pulse // 2, 0)
            matrix.text(sec_str, 110, 110, sec_color)
            
            # Date
            date_str = now.strftime("%A, %B %d, %Y")
            matrix.text(date_str, 40, 30, YELLOW)
            
        elif self.mode == 1:
            # Analog only
            self.draw_analog_clock(matrix, 128, 96, 70)
            # Date above
            date_str = now.strftime("%a %b %d")
            matrix.text(date_str, 90, 10, YELLOW)
            # Time below
            time_str = now.strftime("%H:%M:%S")
            matrix.text(time_str, 90, 175, CYAN)
        
        else:
            # Both - split screen
            self.draw_analog_clock(matrix, 120, 96, 60)
            
            # Digital time on left
            time_str = now.strftime("%H:%M")
            matrix.text(time_str, 10, 80, CYAN)
            sec_str = now.strftime("%S")
            matrix.text(sec_str, 16, 100, RED)
            
            # Date at top
            date_str = now.strftime("%a, %b %d")
            matrix.text(date_str, 80, 10, YELLOW)
        
        # Left panel - mode indicator
        matrix.text("MODE", 2, 10, GREY)
        mode_text = ["DGTL", "ANLG", "BOTH"][self.mode]
        matrix.text(mode_text, 2, 22, CYAN)
        
        # Right panel - day
        matrix.text("DAY", 228, 10, GREY)
        day_num = now.strftime("%d")
        matrix.text(day_num, 228, 22, YELLOW)
        
        self.dirty = False


def run(os_context):
    """Run Clock app within MatrixOS framework."""
    app = ClockApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()
