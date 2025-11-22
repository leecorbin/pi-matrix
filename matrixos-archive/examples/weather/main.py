"""
Weather - ZX Spectrum Style Weather Display for 256×192
=======================================================

Features:
- Large temperature display
- Weather icons (ASCII art style)
- Forecast display
- Spectrum color scheme
- Beautiful side panels
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
WHITE = (255, 255, 255)
BLUE = (100, 150, 255)
GREEN = (0, 255, 0)

class WeatherApp(App):
    """Mock weather display with Spectrum aesthetic"""
    
    def __init__(self):
        super().__init__("Weather")
        # Mock weather data
        self.conditions = [
            ("Sunny", "☀️", 72, YELLOW),
            ("Cloudy", "☁️", 65, WHITE),
            ("Rainy", "🌧️", 58, BLUE),
            ("Stormy", "⛈️", 55, CYAN),
            ("Snowy", "❄️", 32, WHITE),
        ]
        self.current = 0
        self.forecast = [
            ("MON", "☀️", 75, 60),
            ("TUE", "☁️", 68, 55),
            ("WED", "🌧️", 62, 52),
            ("THU", "☀️", 70, 58),
            ("FRI", "☁️", 67, 54),
        ]
    
    def on_event(self, event):
        if event.key == InputEvent.LEFT:
            self.current = (self.current - 1) % len(self.conditions)
            self.dirty = True
            return True
        elif event.key == InputEvent.RIGHT:
            self.current = (self.current + 1) % len(self.conditions)
            self.dirty = True
            return True
        return False
    
    def on_update(self, delta_time):
        # Could update from real API
        pass
    
    def render(self, matrix):
        matrix.clear()
        matrix.rect(0, 0, 256, 192, DARK_BLUE, fill=True)
        
        # Current conditions
        condition, icon, temp, color = self.conditions[self.current]
        
        # Top: Location
        matrix.text("SAN FRANCISCO", 60, 10, CYAN)
        
        # Center: Big temperature
        temp_str = f"{temp}°F"
        matrix.text(temp_str, 80, 60, color)
        
        # Condition
        matrix.text(condition.upper(), 90, 90, YELLOW)
        
        # Weather icon (large)
        matrix.text(icon, 20, 50, color)
        
        # Forecast bar at bottom
        matrix.text("5-DAY FORECAST", 70, 115, WHITE)
        
        x = 10
        for day, day_icon, high, low in self.forecast:
            matrix.text(day, x, 135, CYAN)
            matrix.text(day_icon, x, 145, YELLOW)
            matrix.text(f"{high}", x, 160, RED)
            matrix.text(f"{low}", x, 170, BLUE)
            x += 50
        
        # Navigation
        matrix.text("< >", 110, 180, GREEN)
        
        self.dirty = False


def run(os_context):
    app = WeatherApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()
