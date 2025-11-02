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
from matrixos import network, layout


class WeatherApp(App):
    """Weather display with background updates."""

    def __init__(self):
        super().__init__("Weather")
        self.location = "Cardiff, UK"
        self.temperature = 20
        self.condition = "sunny"
        self.last_fetch = 0
        self.fetch_interval = 300  # Fetch every 5 minutes (was 5 seconds - too aggressive!)
        self.loading = True
        self.update_count = 0
        self.last_condition = None
        self.use_demo_mode = True  # Set to False to use real API

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
        """Fetch weather data using async network (non-blocking!).

        This method returns immediately. The actual fetch happens in
        a background thread, and the callback updates the weather data.
        """
        if self.loading:
            return  # Already fetching
        
        self.loading = True
        self.last_fetch = time.time()
        
        if self.use_demo_mode:
            # Demo mode: Simulate network fetch
            def fetch_in_background():
                """This runs in a background thread - doesn't block UI!"""
                time.sleep(0.5)  # Simulate network delay
                
                # Generate random weather (for demo)
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
            
            schedule_task(fetch_in_background, on_fetch_complete, self.name)
        else:
            # Real API mode (requires API key and setup)
            # Example: OpenWeatherMap API
            # url = f"https://api.openweathermap.org/data/2.5/weather?q={self.location}&appid=YOUR_KEY&units=metric"
            
            def on_weather_response(result: TaskResult):
                """Called when API response arrives."""
                self.loading = False
                
                if result.success:
                    data = result.value
                    # Parse API response (adjust for your API format)
                    self.temperature = int(data.get('main', {}).get('temp', 20))
                    weather_main = data.get('weather', [{}])[0].get('main', 'Clear').lower()
                    
                    # Map API weather to our conditions
                    if 'rain' in weather_main or 'drizzle' in weather_main:
                        self.condition = 'rainy'
                    elif 'cloud' in weather_main:
                        self.condition = 'cloudy'
                    elif 'thunder' in weather_main or 'storm' in weather_main:
                        self.condition = 'stormy'
                    else:
                        self.condition = 'sunny'
                    
                    self.update_count += 1
                    self.dirty = True
                else:
                    print(f"Weather API error: {result.error}")
            
            # Uncomment to use real API:
            # network.get_json(url, callback=on_weather_response, timeout=5.0)
            pass

    def on_event(self, event):
        """Handle input."""
        if event.key == 'r' or event.key == 'R':
            # Manual refresh
            self.fetch_weather()
            return True
        return False

    def render(self, matrix):
        """Draw weather UI - responsive to screen size!"""
        width = matrix.width
        height = matrix.height
        icon_size = layout.get_icon_size(matrix)  # 16px for 64×64, 32px for 128×128

        # Title with location
        matrix.text("WEATHER", 2, 2, (0, 255, 255))
        matrix.text(self.location.upper(), 2, 10, (100, 100, 100))

        if self.loading:
            layout.center_text(matrix, "LOADING...", color=(150, 150, 150))
            return

        # Weather icon (centered at top, size depends on resolution)
        icon_y = 20 if width < 100 else 30
        icon_color = next(c[1] for c in self.conditions if c[0] == self.condition)
        scale = icon_size / 16  # Scale factor for larger displays

        if self.condition == "sunny":
            # Sun
            radius = int(8 * scale)
            matrix.circle(width // 2, icon_y, radius, icon_color, fill=True)
            # Rays
            for angle in range(0, 360, 45):
                import math
                rad = math.radians(angle)
                x1 = int(width // 2 + (10 * scale) * math.cos(rad))
                y1 = int(icon_y + (10 * scale) * math.sin(rad))
                x2 = int(width // 2 + (14 * scale) * math.cos(rad))
                y2 = int(icon_y + (14 * scale) * math.sin(rad))
                matrix.line(x1, y1, x2, y2, icon_color)

        elif self.condition == "cloudy":
            # Cloud (scaled for resolution)
            r1, r2, r3 = int(4 * scale), int(5 * scale), int(4 * scale)
            matrix.circle(width // 2 - int(4 * scale), icon_y, r1, icon_color, fill=True)
            matrix.circle(width // 2, icon_y - int(2 * scale), r2, icon_color, fill=True)
            matrix.circle(width // 2 + int(4 * scale), icon_y, r3, icon_color, fill=True)
            matrix.rect(width // 2 - int(8 * scale), icon_y, int(16 * scale), int(4 * scale), icon_color, fill=True)

        elif self.condition == "rainy":
            # Cloud + rain (scaled)
            r1, r2, r3 = int(3 * scale), int(4 * scale), int(3 * scale)
            matrix.circle(width // 2 - int(3 * scale), icon_y - int(4 * scale), r1, (150, 150, 150), fill=True)
            matrix.circle(width // 2, icon_y - int(6 * scale), r2, (150, 150, 150), fill=True)
            matrix.circle(width // 2 + int(3 * scale), icon_y - int(4 * scale), r3, (150, 150, 150), fill=True)
            # Rain drops
            for i in range(int(3 * scale)):
                x = width // 2 - int(4 * scale) + i * int(4 * scale / 3)
                matrix.line(x, icon_y + int(2 * scale), x, icon_y + int(6 * scale), icon_color)

        elif self.condition == "stormy":
            # Cloud + lightning (scaled)
            r1, r2, r3 = int(3 * scale), int(4 * scale), int(3 * scale)
            matrix.circle(width // 2 - int(3 * scale), icon_y - int(4 * scale), r1, (100, 100, 100), fill=True)
            matrix.circle(width // 2, icon_y - int(6 * scale), r2, (100, 100, 100), fill=True)
            matrix.circle(width // 2 + int(3 * scale), icon_y - int(4 * scale), r3, (100, 100, 100), fill=True)
            # Lightning bolt
            cx = width // 2
            matrix.line(cx, icon_y, cx - int(2 * scale), icon_y + int(4 * scale), (255, 255, 0))
            matrix.line(cx - int(2 * scale), icon_y + int(4 * scale), cx + int(1 * scale), icon_y + int(4 * scale), (255, 255, 0))
            matrix.line(cx + int(1 * scale), icon_y + int(4 * scale), cx - int(1 * scale), icon_y + int(8 * scale), (255, 255, 0))

        # Temperature (large, centered)
        temp_text = f"{self.temperature}C"
        temp_y = height // 2 + int(8 * scale)
        layout.center_text(matrix, temp_text, temp_y, (255, 255, 255))

        # Condition text
        cond_y = temp_y + 10
        layout.center_text(matrix, self.condition.upper(), cond_y, icon_color)

        # Update info at bottom
        time_since = int(time.time() - self.last_fetch)
        mins = time_since // 60
        if mins > 0:
            status_text = f"{mins}m ago"
        else:
            status_text = f"{time_since}s ago"
        layout.center_text(matrix, status_text, height - 10, (80, 80, 80))


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
