#!/usr/bin/env python3
"""
Clock - Analog and Digital Clock Display

Features:
- Analog clock with hour, minute, and second hands
- Digital time display
- Date display
- Multiple clock faces (toggle with OK button)
"""

import sys
import os
import math
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent


class ClockApp(App):
    """Clock app with analog and digital displays."""
    
    def __init__(self):
        super().__init__("Clock")
        self.mode = 0  # 0: analog, 1: digital, 2: both
        self.show_date = True
        
    def on_activate(self):
        """Initialize app."""
        self.mode = 0
        self.show_date = True
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
        elif event.key == InputEvent.UP or event.key == InputEvent.DOWN:
            # Toggle date display
            self.show_date = not self.show_date
            self.dirty = True
        
        return True  # Event handled
    
    def on_update(self, delta_time):
        """Update app state."""
        # Redraw every second to update time
        self.dirty = True
    
    def draw_analog_clock(self, matrix, center_x, center_y, radius):
        """Draw analog clock face."""
        now = datetime.now()
        
        # Draw clock circle
        matrix.circle(center_x, center_y, radius, (100, 100, 100))
        matrix.circle(center_x, center_y, radius - 1, (100, 100, 100))
        
        # Draw hour markers
        for hour in range(12):
            angle = math.radians(hour * 30 - 90)
            outer_x = int(center_x + (radius - 3) * math.cos(angle))
            outer_y = int(center_y + (radius - 3) * math.sin(angle))
            inner_x = int(center_x + (radius - 7) * math.cos(angle))
            inner_y = int(center_y + (radius - 7) * math.sin(angle))
            
            color = (255, 255, 255) if hour % 3 == 0 else (150, 150, 150)
            matrix.line(outer_x, outer_y, inner_x, inner_y, color)
        
        # Calculate hand angles
        hours = now.hour % 12
        minutes = now.minute
        seconds = now.second
        
        hour_angle = math.radians((hours * 30 + minutes * 0.5) - 90)
        minute_angle = math.radians((minutes * 6) - 90)
        second_angle = math.radians((seconds * 6) - 90)
        
        # Draw hour hand (short, thick)
        hour_length = radius * 0.5
        hour_x = int(center_x + hour_length * math.cos(hour_angle))
        hour_y = int(center_y + hour_length * math.sin(hour_angle))
        matrix.line(center_x, center_y, hour_x, hour_y, (255, 200, 0))
        matrix.line(center_x, center_y + 1, hour_x, hour_y + 1, (255, 200, 0))
        
        # Draw minute hand (longer, medium)
        minute_length = radius * 0.7
        minute_x = int(center_x + minute_length * math.cos(minute_angle))
        minute_y = int(center_y + minute_length * math.sin(minute_angle))
        matrix.line(center_x, center_y, minute_x, minute_y, (0, 255, 0))
        
        # Draw second hand (longest, thin)
        second_length = radius * 0.8
        second_x = int(center_x + second_length * math.cos(second_angle))
        second_y = int(center_y + second_length * math.sin(second_angle))
        matrix.line(center_x, center_y, second_x, second_y, (255, 0, 0))
        
        # Center dot
        matrix.circle(center_x, center_y, 2, (255, 255, 255))
    
    def render(self, matrix):
        """Draw app UI."""
        matrix.clear()
        matrix.fill((0, 0, 0))
        
        now = datetime.now()
        
        if self.mode == 0:
            # Analog only
            self.draw_analog_clock(matrix, 64, 64, 50)
            if self.show_date:
                date_str = now.strftime("%a, %b %d")
                matrix.text(date_str, 25, 5, (255, 255, 0))
        
        elif self.mode == 1:
            # Digital only
            time_str = now.strftime("%H:%M:%S")
            
            # Large digital time
            matrix.text(time_str, 15, 50, (0, 255, 255))
            
            # Date
            if self.show_date:
                date_str = now.strftime("%A")
                matrix.text(date_str, 25, 20, (255, 255, 0))
                date_str2 = now.strftime("%B %d, %Y")
                matrix.text(date_str2, 10, 85, (255, 255, 0))
        
        else:
            # Both analog and digital
            self.draw_analog_clock(matrix, 64, 45, 35)
            
            time_str = now.strftime("%H:%M:%S")
            matrix.text(time_str, 30, 95, (0, 255, 255))
            
            if self.show_date:
                date_str = now.strftime("%a, %b %d")
                matrix.text(date_str, 25, 5, (255, 255, 0))
        
        # Draw mode indicator
        mode_text = ["ANALOG", "DIGITAL", "BOTH"][self.mode]
        matrix.text(mode_text, 2, 120, (100, 100, 100))
        
        self.dirty = False


def run(os_context):
    """Run Clock app within MatrixOS framework."""
    app = ClockApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()
