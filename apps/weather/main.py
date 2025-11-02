#!/usr/bin/env python3
"""
Weather App - Displays weather with background updates

Demonstrates:
- Background data fetching (updates every 5 seconds in background)
- Notification system (alerts on weather changes)
- Async data loading
"""

import sys
import os
import time
import random

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent
from matrixos.async_tasks import schedule_task, TaskResult


class WeatherApp(App):
    """Weather display with background updates."""

    def __init__(self):
        super().__init__("Weather")
        self.location = "Cardiff, UK"
        self.temperature = 20
        self.condition = "sunny"
        self.last_fetch = 0
        self.fetch_interval = 5  # Fetch every 5 seconds
        self.loading = True
        self.update_count = 0
        self.last_condition = None

        # Weather conditions typical for Cardiff
        self.conditions = [
            ("sunny", (255, 255, 0)),
            ("cloudy", (150, 150, 150)),
            ("rainy", (100, 100, 255)),  # Very common in Cardiff!
            ("stormy", (128, 0, 128)),
        ]

    def get_help_text(self):
        """Return app-specific help."""
        return [("R", "Refresh")]

    def on_activate(self):
        """App becomes active."""
        # Trigger immediate fetch when activated
        self.fetch_weather()

    def on_background_tick(self):
        """Update in background."""
        current_time = time.time()

        # Fetch weather periodically
        if current_time - self.last_fetch >= self.fetch_interval:
            old_condition = self.condition
            self.fetch_weather()

            # Only request attention for severe weather (storms)
            # Rainy weather in Cardiff is too common to interrupt!
            if old_condition != self.condition and not self.active:
                if self.condition == "stormy":
                    self.request_attention(priority='normal')

    def fetch_weather(self):
        """Fetch weather data using async task (non-blocking!).

        This method returns immediately. The actual fetch happens in
        a background thread, and the callback updates the weather data.
        """
        if self.loading:
            return  # Already fetching
        
        self.loading = True
        self.last_fetch = time.time()
        
        def fetch_in_background():
            """This runs in a background thread - doesn't block UI!"""
            # Simulate network delay
            time.sleep(0.5)  # This is OK now - runs in background!
            
            # Generate random weather (for demo)
            # Cardiff typically has mild temperatures (8-18°C) and lots of rain!
            weather_choices = ["rainy"] * 4 + ["cloudy"] * 3 + ["sunny"] * 2 + ["stormy"] * 1
            condition = random.choice(weather_choices)
            temperature = random.randint(8, 18)
            
            return {
                'condition': condition,
                'temperature': temperature
            }
        
        def on_fetch_complete(result: TaskResult):
            """This runs on main thread when fetch completes."""
            self.loading = False
            
            if result.success:
                data = result.result
                old_condition = self.condition
                
                self.condition = data['condition']
                self.temperature = data['temperature']
                self.update_count += 1
                
                # Request attention for severe weather (storms)
                if old_condition != self.condition and not self.active:
                    if self.condition == "stormy":
                        self.request_attention(priority='normal')
            else:
                print(f"Weather fetch failed: {result.error}")
        
        # Schedule the task - returns immediately!
        schedule_task(fetch_in_background, on_fetch_complete, self.name)

    def on_event(self, event):
        """Handle input."""
        if event.key == 'r' or event.key == 'R':
            # Manual refresh
            self.fetch_weather()
            return True
        return False

    def render(self, matrix):
        """Draw weather UI."""
        width = matrix.width
        height = matrix.height

        # Title with location
        matrix.text("WEATHER", 2, 2, (0, 255, 255))
        matrix.text(self.location.upper(), 2, 10, (100, 100, 100))

        if self.loading:
            matrix.centered_text("LOADING...", height // 2, (150, 150, 150))
            return

        # Weather icon (centered at top)
        icon_y = 16
        icon_color = next(c[1] for c in self.conditions if c[0] == self.condition)

        if self.condition == "sunny":
            # Sun
            matrix.circle(width // 2, icon_y, 8, icon_color, fill=True)
            # Rays
            for angle in range(0, 360, 45):
                import math
                rad = math.radians(angle)
                x1 = int(width // 2 + 10 * math.cos(rad))
                y1 = int(icon_y + 10 * math.sin(rad))
                x2 = int(width // 2 + 14 * math.cos(rad))
                y2 = int(icon_y + 14 * math.sin(rad))
                matrix.line(x1, y1, x2, y2, icon_color)

        elif self.condition == "cloudy":
            # Cloud
            matrix.circle(width // 2 - 4, icon_y, 4, icon_color, fill=True)
            matrix.circle(width // 2, icon_y - 2, 5, icon_color, fill=True)
            matrix.circle(width // 2 + 4, icon_y, 4, icon_color, fill=True)
            matrix.rect(width // 2 - 8, icon_y, 16, 4, icon_color, fill=True)

        elif self.condition == "rainy":
            # Cloud + rain
            matrix.circle(width // 2 - 3, icon_y - 4, 3, (150, 150, 150), fill=True)
            matrix.circle(width // 2, icon_y - 6, 4, (150, 150, 150), fill=True)
            matrix.circle(width // 2 + 3, icon_y - 4, 3, (150, 150, 150), fill=True)
            # Rain drops
            for i in range(3):
                x = width // 2 - 4 + i * 4
                matrix.line(x, icon_y + 2, x, icon_y + 6, icon_color)

        elif self.condition == "stormy":
            # Cloud + lightning
            matrix.circle(width // 2 - 3, icon_y - 4, 3, (100, 100, 100), fill=True)
            matrix.circle(width // 2, icon_y - 6, 4, (100, 100, 100), fill=True)
            matrix.circle(width // 2 + 3, icon_y - 4, 3, (100, 100, 100), fill=True)
            # Lightning
            matrix.line(width // 2, icon_y, width // 2 - 2, icon_y + 4, (255, 255, 0))
            matrix.line(width // 2 - 2, icon_y + 4, width // 2 + 1, icon_y + 4, (255, 255, 0))
            matrix.line(width // 2 + 1, icon_y + 4, width // 2 - 1, icon_y + 8, (255, 255, 0))

        # Temperature (large)
        temp_text = f"{self.temperature}C"
        matrix.centered_text(temp_text, height // 2 + 8, (255, 255, 255))

        # Condition text
        matrix.centered_text(self.condition.upper(), height // 2 + 18, icon_color)

        # Update info (simple)
        time_since = int(time.time() - self.last_fetch)
        status_text = f"{time_since}s ago"
        matrix.centered_text(status_text, height - 10, (80, 80, 80))


def run(os_context):
    """Entry point called by OS."""
    app = WeatherApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()  # Start the OS event loop


def main():
    """Standalone testing mode."""
    from matrixos.led_api import create_matrix
    from matrixos.input import KeyboardInput
    from matrixos.config import parse_matrix_args
    from matrixos.app_framework import OSContext

    args = parse_matrix_args("Weather App")
    matrix = create_matrix(args.width, args.height, args.color_mode)

    print("\n" + "="*64)
    print("WEATHER APP - Standalone Mode")
    print("="*64)
    print("\nControls:")
    print("  R     - Refresh weather")
    print("  ESC   - Quit")
    print("\nNote: Weather updates automatically every 5 seconds,")
    print("      even when running in background!")
    print("\n" + "="*64 + "\n")

    with KeyboardInput() as input_handler:
        os = OSContext(matrix, input_handler)
        app = WeatherApp()
        os.register_app(app)
        os.switch_to_app(app)
        os.run()

    print("\nWeather app closed.")


if __name__ == '__main__':
    main()
