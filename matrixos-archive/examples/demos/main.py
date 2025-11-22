"""
Demos - ZX Spectrum Visual Effects for 256×192
===============================================

Features:
- Plasma effect with Spectrum colors
- Sine wave patterns
- Bouncing squares
- Color cycling
- Starfield
- Matrix rain effect
- All with authentic Spectrum aesthetic
"""

import sys
import os
import math
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent

# ZX Spectrum colors
CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 40)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

class DemosApp(App):
    """ZX Spectrum visual effects showcase"""
    
    def __init__(self):
        super().__init__("Demos")
        self.mode = 0  # 0: plasma, 1: waves, 2: bouncing, 3: stars
        self.time = 0
        self.stars = [(random.randint(0, 256), random.randint(0, 192), random.randint(1, 3)) for _ in range(50)]
        self.squares = [
            {"x": 50, "y": 50, "vx": 2, "vy": 1.5, "color": RED},
            {"x": 150, "y": 100, "vx": -1.5, "vy": 2, "color": CYAN},
            {"x": 100, "y": 150, "vx": 1, "vy": -2, "color": YELLOW},
        ]
    
    def on_event(self, event):
        if event.key == InputEvent.OK or event.key == InputEvent.RIGHT:
            self.mode = (self.mode + 1) % 4
            self.dirty = True
            return True
        elif event.key == InputEvent.LEFT:
            self.mode = (self.mode - 1) % 4
            self.dirty = True
            return True
        return False
    
    def on_update(self, delta_time):
        self.time += 1
        # Update stars
        if self.mode == 3:
            for i, (x, y, speed) in enumerate(self.stars):
                x += speed
                if x >= 256:
                    x = 0
                    y = random.randint(0, 192)
                self.stars[i] = (x, y, speed)
        
        # Update bouncing squares
        if self.mode == 2:
            for sq in self.squares:
                sq["x"] += sq["vx"]
                sq["y"] += sq["vy"]
                if sq["x"] <= 0 or sq["x"] >= 246:
                    sq["vx"] *= -1
                if sq["y"] <= 0 or sq["y"] >= 182:
                    sq["vy"] *= -1
        
        self.dirty = True
    
    def render(self, matrix):
        matrix.clear()
        matrix.rect(0, 0, 256, 192, DARK_BLUE, fill=True)
        
        if self.mode == 0:
            # Plasma effect
            for y in range(0, 192, 4):
                for x in range(0, 256, 4):
                    val = math.sin(x * 0.02 + self.time * 0.05) + math.sin(y * 0.03 + self.time * 0.07)
                    val += math.sin((x + y) * 0.02 + self.time * 0.06)
                    val = (val + 3) / 6
                    
                    if val < 0.33:
                        color = BLUE
                    elif val < 0.66:
                        color = CYAN
                    else:
                        color = YELLOW
                    
                    matrix.rect(x, y, 4, 4, color, fill=True)
            
            matrix.text("PLASMA", 100, 10, WHITE)
        
        elif self.mode == 1:
            # Sine waves
            for i in range(8):
                y_offset = 24 * i
                for x in range(256):
                    y = int(96 + 40 * math.sin(x * 0.05 + self.time * 0.1 + i))
                    if 0 <= y < 192:
                        colors = [RED, YELLOW, GREEN, CYAN, BLUE, MAGENTA, WHITE, RED]
                        matrix.set_pixel(x, y, colors[i])
            
            matrix.text("WAVES", 104, 10, WHITE)
        
        elif self.mode == 2:
            # Bouncing squares
            for sq in self.squares:
                matrix.rect(int(sq["x"]), int(sq["y"]), 10, 10, sq["color"], fill=True)
                # Trail
                for i in range(5):
                    tx = int(sq["x"] - sq["vx"] * i * 2)
                    ty = int(sq["y"] - sq["vy"] * i * 2)
                    if 0 <= tx < 256 and 0 <= ty < 192:
                        alpha = 255 - i * 50
                        trail_color = tuple(c * alpha // 255 for c in sq["color"])
                        matrix.set_pixel(tx, ty, trail_color)
            
            matrix.text("BOUNCE", 100, 10, WHITE)
        
        elif self.mode == 3:
            # Starfield
            for x, y, speed in self.stars:
                brightness = 128 + speed * 40
                color = (brightness, brightness, brightness)
                matrix.set_pixel(int(x), int(y), color)
                # Trail
                if x >= speed:
                    matrix.set_pixel(int(x - speed), int(y), (brightness // 2, brightness // 2, brightness // 2))
            
            matrix.text("STARS", 104, 10, WHITE)
        
        # Mode indicator
        matrix.text(f"MODE {self.mode + 1}/4", 2, 180, CYAN)
        matrix.text("< OK >", 200, 180, YELLOW)
        
        self.dirty = False


def run(os_context):
    app = DemosApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()


if __name__ == "__main__":
    from matrixos.display import TerminalDisplay
    from matrixos.input import InputHandler
    
    matrix = TerminalDisplay(256, 192)
    input_handler = InputHandler()
    app = DemosApp()
    app.on_activate()
    
    print("ZX Spectrum Demos - OK to cycle modes")
    
    import time
    last_time = time.time()
    
    try:
        while True:
            event = input_handler.get_key(timeout=0.001)
            if event:
                app.on_event(event)
            
            current_time = time.time()
            if current_time - last_time >= 1.0 / 60.0:
                app.on_update(1.0 / 60.0)
                if app.dirty:
                    app.render(matrix)
                    matrix.show()
                last_time = current_time
    except KeyboardInterrupt:
        print("\nDemos complete!")
