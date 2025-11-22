#!/usr/bin/env python3
"""
Frogger Game - Enhanced for 256×192 ZX Spectrum Resolution!

Help the frog cross the road and river to reach home safely.

Controls:
- Arrow Keys: Move frog  
- R: Restart level
- ESC: Exit to launcher

Features:
- 5 lanes of traffic (was 3!)
- 5 river lanes with logs and turtles
- Lives displayed with frog icons
- Level indicator and timer
- Score tracking with multipliers
- Beautiful ZX Spectrum aesthetic
- Larger, more detailed sprites
"""

import sys
import os
import time
import random

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent
from matrixos import layout, storage, audio


class Frog:
    """The player's frog."""
    
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.size = 8  # Larger for 256×192
        self.alive = True
        self.on_log = False
        self.log_speed = 0
    
    def move(self, dx, dy, grid_size=12):
        """Move frog by grid units."""
        if self.alive:
            self.x += dx * grid_size
            self.y += dy * grid_size
    
    def reset(self, start_x, start_y):
        """Reset frog position."""
        self.x = start_x
        self.y = start_y
        self.alive = True
        self.on_log = False
        self.log_speed = 0


class Vehicle:
    """Road vehicle (car, truck, van, etc)."""
    
    def __init__(self, x, y, width, speed, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = 8  # Larger for 256×192
        self.speed = speed
        self.color = color
    
    def update(self, dt, play_left, play_width):
        """Update vehicle position within play area."""
        self.x += self.speed * dt
        
        # Wrap around within play area
        play_right = play_left + play_width
        if self.speed > 0 and self.x > play_right + self.width:
            self.x = play_left - self.width
        elif self.speed < 0 and self.x < play_left - self.width:
            self.x = play_right + self.width


class Log:
    """Floating log in river."""
    
    def __init__(self, x, y, width, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = 8  # Larger for 256×192
        self.speed = speed
    
    def update(self, dt, play_left, play_width):
        """Update log position within play area."""
        self.x += self.speed * dt
        
        # Wrap around within play area
        play_right = play_left + play_width
        if self.speed > 0 and self.x > play_right + self.width:
            self.x = play_left - self.width
        elif self.speed < 0 and self.x < play_left - self.width:
            self.x = play_right + self.width


class FroggerGame(App):
    """Frogger game app."""
    
    def __init__(self):
        super().__init__("Frogger")
        
        self.score = 0
        self.high_score = storage.get('frogger.high_score', default=0)
        self.lives = 3
        self.level = 1
        
        self.grid_size = 8  # Pixels per grid unit
        self.start_y = None  # Set in reset()
        
        self.frog = None
        self.vehicles = []
        self.logs = []
        
        self.game_over = False
        self.win = False
        
    def get_help_text(self):
        """Return app-specific help."""
        return [("Arrows", "Move"), ("R", "Restart")]
    
    def on_activate(self):
        """App becomes active."""
        self.reset_game()
    
    def reset_game(self):
        """Reset game to start."""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.win = False
        # Initialize with default dimensions (128x128 for LED matrix)
        self.reset_level(128, 128)
    
    def reset_level(self, width, height):
        """Reset level with screen dimensions - Enhanced for 256×192!"""
        self.grid_size = 12  # Grid movement size
        self.width = width
        self.height = height
        
        # Play area is center 192px wide (leaving 32px on each side for UI)
        self.play_left = 32
        self.play_width = 192
        self.play_right = self.play_left + self.play_width
        
        # Frog starts at bottom center (safe zone)
        self.start_x = self.play_left + self.play_width // 2
        self.start_y = height - 18  # Above bottom edge
        
        if self.frog is None:
            self.frog = Frog(self.start_x, self.start_y)
        else:
            self.frog.reset(self.start_x, self.start_y)
        
        # Clear obstacles
        self.vehicles = []
        self.logs = []
        
        # Layout for 256×192:
        # Goal homes: y=8-20 (12px)
        # River: y=30-110 (5 lanes × 16px each)
        # Safe middle: y=110-122 (12px)
        # Road: y=122-178 (5 lanes × ~11px each, actually adjusted)
        # Safe start: y=178-192 (14px)
        
        lane_height = 14
        
        # === ROAD LANES (5 lanes moving bottom-up) ===
        road_start_y = height - 70  # ~122 for 192
        
        # Lane 1: Mini cars moving right (fast)
        road_y = road_start_y
        for i in range(5):
            x = self.play_left + i * (self.play_width // 5) + random.randint(0, 15)
            speed = 18 + self.level * 3
            self.vehicles.append(Vehicle(x, road_y, 14, speed, (255, 255, 0)))  # Yellow
        
        # Lane 2: Trucks moving left (slow)
        road_y += lane_height
        for i in range(3):
            x = self.play_left + i * (self.play_width // 3) + random.randint(0, 25)
            speed = -(12 + self.level * 2)
            self.vehicles.append(Vehicle(x, road_y, 28, speed, (0, 150, 255)))  # Blue trucks
        
        # Lane 3: Race cars moving right (very fast!)
        road_y += lane_height
        for i in range(6):
            x = self.play_left + i * (self.play_width // 6) + random.randint(0, 10)
            speed = 25 + self.level * 4
            self.vehicles.append(Vehicle(x, road_y, 16, speed, (255, 0, 0)))  # Red
        
        # Lane 4: Vans moving left (medium)
        road_y += lane_height
        for i in range(4):
            x = self.play_left + i * (self.play_width // 4) + random.randint(0, 20)
            speed = -(15 + self.level * 3)
            self.vehicles.append(Vehicle(x, road_y, 20, speed, (255, 128, 0)))  # Orange
        
        # Lane 5: Sports cars moving right (fast)
        road_y += lane_height
        for i in range(5):
            x = self.play_left + i * (self.play_width // 5) + random.randint(0, 12)
            speed = 20 + self.level * 3
            self.vehicles.append(Vehicle(x, road_y, 18, speed, (255, 0, 255)))  # Magenta
        
        # === RIVER LANES (5 lanes) ===
        river_start_y = 30
        self.river_top = river_start_y
        self.river_bottom = river_start_y + (5 * 16)  # 5 lanes × 16px = 110
        
        # River Lane 1: Short logs moving right
        river_y = river_start_y
        for i in range(4):
            x = self.play_left + i * (self.play_width // 4) + random.randint(0, 20)
            speed = 10 + self.level
            self.logs.append(Log(x, river_y, 32, speed))
        
        # River Lane 2: Long logs moving left
        river_y += 16
        for i in range(3):
            x = self.play_left + i * (self.play_width // 3) + random.randint(0, 30)
            speed = -(12 + self.level)
            self.logs.append(Log(x, river_y, 48, speed))
        
        # River Lane 3: Medium logs moving right (faster)
        river_y += 16
        for i in range(4):
            x = self.play_left + i * (self.play_width // 4) + random.randint(0, 25)
            speed = 14 + self.level * 2
            self.logs.append(Log(x, river_y, 36, speed))
        
        # River Lane 4: Turtles moving left (dive pattern would be cool!)
        river_y += 16
        for i in range(5):
            x = self.play_left + i * (self.play_width // 5) + random.randint(0, 15)
            speed = -(10 + self.level)
            self.logs.append(Log(x, river_y, 24, speed))  # Shorter "turtle rafts"
        
        # River Lane 5: Fast logs moving right
        river_y += 16
        for i in range(3):
            x = self.play_left + i * (self.play_width // 3) + random.randint(0, 35)
            speed = 16 + self.level * 2
            self.logs.append(Log(x, river_y, 40, speed))
    
    def on_event(self, event):
        """Handle input."""
        if self.game_over or self.win:
            if event.key == InputEvent.OK or event.key == 'r' or event.key == 'R':
                self.reset_game()
                audio.play('jump')
                self.dirty = True
                return True
            return False
        
        if event.key == InputEvent.UP:
            self.frog.move(0, -1, self.grid_size)
            self.score += 10
            audio.play('jump')
            self.dirty = True
            return True
        elif event.key == InputEvent.DOWN:
            self.frog.move(0, 1, self.grid_size)
            audio.play('jump')
            self.dirty = True
            return True
        elif event.key == InputEvent.LEFT:
            self.frog.move(-1, 0, self.grid_size)
            audio.play('jump')
            self.dirty = True
            return True
        elif event.key == InputEvent.RIGHT:
            self.frog.move(1, 0, self.grid_size)
            audio.play('jump')
            self.dirty = True
            return True
        elif event.key == 'r' or event.key == 'R':
            self.reset_game()
            audio.play('jump')
            self.dirty = True
            return True
        
        return False
    
    def on_update(self, delta_time):
        """Update game state."""
        if self.game_over or self.win:
            return
        
        # Update vehicles with play area bounds
        play_left = getattr(self, 'play_left', 32)
        play_width = getattr(self, 'play_width', 192)
        
        for vehicle in self.vehicles:
            vehicle.update(delta_time, play_left, play_width)
        
        # Update logs with play area bounds
        for log in self.logs:
            log.update(delta_time, play_left, play_width)
        
        # Check collisions
        self.check_collisions()
        
        # Always mark dirty for animation
        self.dirty = True
        
        # Check win condition (reached goal homes at top)
        if self.frog.y < 22:  # In goal zone
            self.win = True
            self.score += 1000 * self.level  # Level multiplier!
            if self.score > self.high_score:
                self.high_score = self.score
                storage.set('frogger.high_score', self.high_score)
            audio.play('success')
        
        self.dirty = True
    
    def check_collisions(self):
        """Check for collisions with vehicles and water."""
        if not self.frog.alive:
            return
        
        play_left = getattr(self, 'play_left', 32)
        play_right = getattr(self, 'play_right', 224)
        
        # Check vehicle collisions
        for vehicle in self.vehicles:
            if self.check_overlap(
                self.frog.x, self.frog.y, self.frog.size, self.frog.size,
                vehicle.x, vehicle.y, vehicle.width, vehicle.height
            ):
                self.die()
                return
        
        # Check if in river area
        if hasattr(self, 'river_top') and hasattr(self, 'river_bottom'):
            if self.river_top < self.frog.y < self.river_bottom:
                # In river - must be on a log
                on_log = False
                for log in self.logs:
                    if self.check_overlap(
                        self.frog.x, self.frog.y, self.frog.size, self.frog.size,
                        log.x, log.y, log.width, log.height
                    ):
                        on_log = True
                        self.frog.on_log = True
                        self.frog.log_speed = log.speed
                        # Move frog with log
                        self.frog.x += log.speed * 0.016  # Approximate dt
                        break
                
                if not on_log:
                    self.frog.on_log = False
                    self.die()
                    return
            else:
                self.frog.on_log = False
        
        # Check if frog went off play area sides
        if self.frog.x < play_left or self.frog.x + self.frog.size > play_right:
            self.die()
    
    def check_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2):
        """Check if two rectangles overlap."""
        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + h2 and y1 + h1 > y2)
    
    def die(self):
        """Frog dies."""
        self.frog.alive = False
        self.lives -= 1
        audio.play('hit')
        
        if self.lives <= 0:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                storage.set('frogger.high_score', self.high_score)
            audio.play('gameover')
        else:
            # Reset frog position
            self.frog.reset(self.start_x, self.start_y)
    
    def render(self, matrix):
        """Draw game with beautiful ZX Spectrum aesthetic and side panels!"""
        width = matrix.width
        height = matrix.height
        
        # === BACKGROUND (dark blue) ===
        matrix.rect(0, 0, width, height, (0, 0, 40), fill=True)
        
        # === SIDE PANELS (32px each side) ===
        # Left panel - Lives display
        matrix.rect(0, 0, 32, height, (0, 0, 60), fill=True)
        matrix.rect(0, 0, 32, height, (0, 255, 255), fill=False)
        matrix.text("LIVES", 4, 10, (255, 255, 0))
        
        # Draw frog icons for lives
        for i in range(self.lives):
            fy = 24 + i * 16
            # Mini frog icon
            matrix.circle(16, fy, 4, (50, 255, 50), fill=True)
            matrix.set_pixel(14, fy - 2, (0, 0, 0))  # Left eye
            matrix.set_pixel(18, fy - 2, (0, 0, 0))  # Right eye
        
        # Right panel - Score & Level
        matrix.rect(224, 0, 32, height, (0, 0, 60), fill=True)
        matrix.rect(224, 0, 32, height, (0, 255, 255), fill=False)
        
        matrix.text("LVL", 228, 10, (255, 255, 0))
        matrix.text(f"{self.level}", 234, 22, (255, 255, 255))
        
        matrix.text("SCORE", 226, 50, (0, 255, 255))
        # Score display (truncate if too long)
        score_str = str(self.score)
        if len(score_str) > 5:
            score_str = score_str[-5:]
        matrix.text(score_str, 228, 62, (255, 255, 255))
        
        matrix.text("HIGH", 228, 90, (255, 200, 0))
        hi_str = str(self.high_score)
        if len(hi_str) > 5:
            hi_str = hi_str[-5:]
        matrix.text(hi_str, 228, 102, (255, 255, 0))
        
        # === PLAY AREA (192px center) ===
        play_left = 32
        play_width = 192
        
        # Goal zone with homes (y=8-22)
        matrix.rect(play_left, 8, play_width, 14, (100, 220, 100), fill=True)
        matrix.rect(play_left, 8, play_width, 14, (0, 200, 0), fill=False)
        
        # Draw 5 home slots
        for i in range(5):
            home_x = play_left + 8 + i * 36
            matrix.rect(home_x, 10, 24, 10, (50, 150, 50), fill=True)
            matrix.text("H", home_x + 8, 12, (255, 255, 0))
        
        # Sky strip above river
        matrix.rect(play_left, 22, play_width, 8, (100, 150, 255), fill=True)
        
        # River zone (5 lanes: y=30-110)
        river_h = self.river_bottom - self.river_top
        matrix.rect(play_left, self.river_top, play_width, river_h, 
                   (50, 120, 255), fill=True)
        
        # River waves decoration
        for i in range(0, play_width, 16):
            wave_x = play_left + i
            matrix.set_pixel(wave_x, self.river_top + 2, (100, 180, 255))
            matrix.set_pixel(wave_x + 8, self.river_top + 6, (100, 180, 255))
        
        # Draw logs with wood texture
        for log in self.logs:
            # Brown log
            matrix.rect(int(log.x), int(log.y), log.width, log.height, 
                       (139, 69, 19), fill=True)
            # Wood rings
            for i in range(0, log.width, 10):
                if int(log.x + i) < play_left + play_width:
                    matrix.circle(int(log.x + i + 4), int(log.y + 4), 3, 
                                (160, 82, 45), fill=False)
        
        # Safe middle zone
        matrix.rect(play_left, 110, play_width, 12, (150, 220, 150), fill=True)
        matrix.rect(play_left, 110, play_width, 12, (100, 200, 100), fill=False)
        
        # Road zone (5 lanes: y=122-178)
        matrix.rect(play_left, 122, play_width, 56, (60, 60, 60), fill=True)
        
        # Road lane markings
        for i in range(4):
            lane_y = 136 + i * 14
            for x in range(play_left, play_left + play_width, 12):
                matrix.rect(x, lane_y, 6, 2, (255, 255, 255), fill=True)
        
        # Draw vehicles with details
        for vehicle in self.vehicles:
            # Vehicle body
            matrix.rect(int(vehicle.x), int(vehicle.y), vehicle.width, vehicle.height,
                       vehicle.color, fill=True)
            # Windshield
            window_color = (180, 220, 255)
            window_w = max(4, vehicle.width - 8)
            matrix.rect(int(vehicle.x + 4), int(vehicle.y + 2), 
                       window_w, 4, window_color, fill=True)
            # Headlights/taillights
            if vehicle.speed > 0:  # Moving right - headlights
                matrix.set_pixel(int(vehicle.x + vehicle.width - 2), int(vehicle.y + 1), (255, 255, 200))
                matrix.set_pixel(int(vehicle.x + vehicle.width - 2), int(vehicle.y + 6), (255, 255, 200))
            else:  # Moving left - taillights
                matrix.set_pixel(int(vehicle.x + 1), int(vehicle.y + 1), (255, 0, 0))
                matrix.set_pixel(int(vehicle.x + 1), int(vehicle.y + 6), (255, 0, 0))
        
        # Safe starting zone
        matrix.rect(play_left, 178, play_width, 14, (100, 220, 100), fill=True)
        matrix.rect(play_left, 178, play_width, 14, (0, 200, 0), fill=False)
        
        # Draw the heroic frog!
        if self.frog.alive:
            frog_color = (100, 255, 100)
            if self.frog.on_log:
                frog_color = (150, 255, 150)  # Brighter on log
            
            fx = int(self.frog.x)
            fy = int(self.frog.y)
            
            # Frog body (larger and more detailed)
            matrix.circle(fx + 4, fy + 4, 4, frog_color, fill=True)
            
            # Eyes (big round eyes)
            matrix.circle(fx + 2, fy + 2, 1, (255, 255, 255), fill=True)
            matrix.circle(fx + 6, fy + 2, 1, (255, 255, 255), fill=True)
            matrix.set_pixel(fx + 2, fy + 2, (0, 0, 0))  # Pupils
            matrix.set_pixel(fx + 6, fy + 2, (0, 0, 0))
            
            # Legs (simple lines)
            leg_color = (80, 200, 80)
            matrix.set_pixel(fx, fy + 6, leg_color)
            matrix.set_pixel(fx + 7, fy + 6, leg_color)
        
        # === GAME OVER / WIN OVERLAYS ===
        if self.game_over:
            # Semi-transparent overlay
            overlay_x = 64
            overlay_y = 70
            overlay_w = 128
            overlay_h = 52
            matrix.rect(overlay_x, overlay_y, overlay_w, overlay_h, (0, 0, 0), fill=True)
            matrix.rect(overlay_x, overlay_y, overlay_w, overlay_h, (255, 0, 0), fill=False)
            matrix.rect(overlay_x + 1, overlay_y + 1, overlay_w - 2, overlay_h - 2, (255, 0, 0), fill=False)
            
            matrix.text("GAME OVER!", 80, 80, (255, 0, 0))
            matrix.text(f"Score: {self.score}", 85, 94, (255, 255, 255))
            matrix.text("Press R", 95, 108, (200, 200, 200))
        
        elif self.win:
            # Victory overlay
            overlay_x = 64
            overlay_y = 70
            overlay_w = 128
            overlay_h = 52
            matrix.rect(overlay_x, overlay_y, overlay_w, overlay_h, (0, 0, 0), fill=True)
            matrix.rect(overlay_x, overlay_y, overlay_w, overlay_h, (255, 255, 0), fill=False)
            matrix.rect(overlay_x + 1, overlay_y + 1, overlay_w - 2, overlay_h - 2, (255, 255, 0), fill=False)
            
            matrix.text("SAFE HOME!", 82, 80, (255, 255, 0))
            matrix.text(f"Score: {self.score}", 85, 94, (0, 255, 255))
            matrix.text("Press R", 95, 108, (200, 200, 200))
        
        self.dirty = False


def run(os_context):
    """Entry point called by OS."""
    app = FroggerGame()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()


def main():
    """Standalone testing mode."""
    from matrixos.led_api import create_matrix
    from matrixos.input import KeyboardInput
    from matrixos.config import parse_matrix_args
    from matrixos.app_framework import OSContext

    args = parse_matrix_args("Frogger Game")
    matrix = create_matrix(args.width, args.height, args.color_mode)

    print("\n" + "="*64)
    print("FROGGER - Classic Arcade Game!")
    print("="*64)
    print("\nControls:")
    print("  Arrow Keys - Move frog")
    print("  R          - Restart")
    print("  ESC        - Exit")
    print("\n" + "="*64 + "\n")

    with KeyboardInput() as input_handler:
        os = OSContext(matrix, input_handler)
        app = FroggerGame()
        os.register_app(app)
        os.switch_to_app(app)
        os.run()

    print("\nFrogger closed.")


# App instance for launcher
app = FroggerGame()


if __name__ == '__main__':
    main()
