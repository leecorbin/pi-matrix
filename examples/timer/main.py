"""
Timer - ZX Spectrum Countdown Timer for 256×192
===============================================

Features:
- Giant countdown display
- Preset times (10s, 30s, 1m, 5m)
- Progress bar visualization
- Alarm animation when complete
- Spectrum colors and aesthetic
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent

CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 40)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

class TimerApp(App):
    """Simple countdown timer with Spectrum aesthetic"""
    
    def __init__(self):
        super().__init__("Timer")
        self.presets = [10, 30, 60, 300]  # seconds
        self.preset_names = ["10 SEC", "30 SEC", "1 MIN", "5 MIN"]
        self.selected = 0
        self.time_left = 0
        self.total_time = 0
        self.running = False
        self.alarm = False
        self.alarm_frame = 0
    
    def on_event(self, event):
        if self.alarm:
            # Any key stops alarm
            self.alarm = False
            self.running = False
            self.dirty = True
            return True
        
        if not self.running:
            if event.key == InputEvent.UP:
                self.selected = (self.selected - 1) % len(self.presets)
                self.dirty = True
                return True
            elif event.key == InputEvent.DOWN:
                self.selected = (self.selected + 1) % len(self.presets)
                self.dirty = True
                return True
            elif event.key == InputEvent.OK or event.key == InputEvent.ACTION:
                self.total_time = self.presets[self.selected]
                self.time_left = self.total_time
                self.running = True
                self.dirty = True
                return True
        else:
            if event.key == InputEvent.BACK:
                self.running = False
                self.time_left = 0
                self.dirty = True
                return True
        return False
    
    def on_update(self, delta_time):
        if self.running and not self.alarm:
            self.time_left -= delta_time
            if self.time_left <= 0:
                self.time_left = 0
                self.alarm = True
                self.alarm_frame = 0
        
        if self.alarm:
            self.alarm_frame += 1
        
        self.dirty = True
    
    def render(self, matrix):
        matrix.clear()
        matrix.rect(0, 0, 256, 192, DARK_BLUE, fill=True)
        
        if self.alarm:
            # Alarm animation
            if (self.alarm_frame // 10) % 2 == 0:
                matrix.rect(0, 0, 256, 192, RED, fill=True)
                matrix.text("TIME'S UP!", 70, 80, WHITE)
            else:
                matrix.text("TIME'S UP!", 70, 80, RED)
            
            matrix.text("PRESS ANY KEY", 60, 100, YELLOW)
        
        elif self.running:
            # Show countdown
            mins = int(self.time_left // 60)
            secs = int(self.time_left % 60)
            time_str = f"{mins:02d}:{secs:02d}"
            
            # Giant time display
            x = 60
            for char in time_str:
                matrix.text(char, x, 70, CYAN)
                x += 32
            
            # Progress bar
            bar_width = 200
            bar_x = 28
            bar_y = 130
            progress = self.time_left / self.total_time if self.total_time > 0 else 0
            filled = int(bar_width * progress)
            
            # Border
            matrix.rect(bar_x - 2, bar_y - 2, bar_width + 4, 24, CYAN)
            # Fill
            if filled > 0:
                color = GREEN if progress > 0.3 else YELLOW if progress > 0.1 else RED
                matrix.rect(bar_x, bar_y, filled, 20, color, fill=True)
            
            matrix.text("BACK TO CANCEL", 70, 160, YELLOW)
        
        else:
            # Selection menu
            matrix.text("SELECT TIME", 70, 30, CYAN)
            
            for i, name in enumerate(self.preset_names):
                y = 60 + i * 20
                if i == self.selected:
                    matrix.rect(50, y - 2, 156, 14, YELLOW)
                    matrix.text(name, 90, y, DARK_BLUE)
                else:
                    matrix.text(name, 90, y, WHITE)
            
            matrix.text("UP/DN  OK:START", 60, 160, CYAN)
        
        self.dirty = False


def run(os_context):
    app = TimerApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()
