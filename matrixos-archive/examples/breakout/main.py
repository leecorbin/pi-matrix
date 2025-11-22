#!/usr/bin/env python3
"""
Breakout Game - Arkanoid-style brick-breaking arcade game for 256×192

Features:
- 15×8 brick grid (120 bricks!)
- Power-ups: Multi-ball, Expand paddle, Laser, Slow ball, Extra life
- Side panels: Lives/power-ups (left), Score/level (right)
- Ball physics with paddle spin
- Progressive difficulty levels
- High score tracking
- Beautiful ZX Spectrum aesthetic
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent
from matrixos import layout, storage, audio
import random
import time


class BreakoutGame(App):
    """Arkanoid-style Breakout game for 256×192."""
    
    def __init__(self):
        super().__init__("Breakout")
        # Screen layout - 256×192 with side panels
        self.width = 256
        self.height = 192
        self.play_left = 32
        self.play_width = 192
        self.play_right = 224
        
        # Paddle
        self.paddle_width = 30
        self.paddle_height = 6
        self.paddle_x = 0
        self.paddle_y = 0
        self.paddle_speed = 6
        self.paddle_normal_width = 30
        self.paddle_expanded_width = 50
        
        # Balls (support multi-ball power-up)
        self.balls = []
        self.ball_size = 5
        
        # Bricks - 15 cols × 8 rows = 120 bricks!
        self.bricks = []
        self.brick_width = 12
        self.brick_height = 8
        
        # Power-ups
        self.powerups = []
        self.powerup_size = 8
        self.active_powerups = set()
        self.powerup_timers = {}
        
        # Laser mode
        self.lasers = []
        self.laser_width = 3
        self.laser_height = 10
        self.laser_speed = 8
        
        # Game state
        self.score = 0
        self.lives = 3
        self.level = 1
        self.high_score = storage.get('breakout.high_score', 0)
        self.game_over = False
        self.won = False
        self.frame_count = 0
    
    def on_activate(self):
        """Initialize game."""
        # Paddle
        self.paddle_width = self.paddle_normal_width
        self.paddle_x = self.play_left + (self.play_width - self.paddle_width) // 2
        self.paddle_y = 170
        
        # Ball
        self.balls = [{
            'x': self.play_left + self.play_width // 2,
            'y': self.paddle_y - 15,
            'vx': 3,
            'vy': -3
        }]
        
        # Bricks
        self.init_bricks()
        
        # Power-ups
        self.powerups = []
        self.active_powerups = set()
        self.powerup_timers = {}
        self.lasers = []
        
        # Game state
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.won = False
        self.frame_count = 0
        self.dirty = True
    
    def init_bricks(self):
        """Initialize 15×8 brick grid (120 bricks!)."""
        colors = [
            (255, 0, 0),      # Red (top)
            (255, 64, 0),     # Orange-Red
            (255, 128, 0),    # Orange
            (255, 200, 0),    # Gold
            (255, 255, 0),    # Yellow
            (0, 255, 0),      # Green
            (0, 200, 255),    # Cyan
            (128, 0, 255),    # Purple (bottom)
        ]
        
        self.bricks = []
        rows = 8
        cols = 15
        spacing = 1
        
        # Center in play area
        total_width = cols * (self.brick_width + spacing) - spacing
        start_x = self.play_left + (self.play_width - total_width) // 2
        start_y = 15
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (self.brick_width + spacing)
                y = start_y + row * (self.brick_height + spacing)
                
                # Some bricks have power-ups
                has_powerup = random.random() < 0.15  # 15% chance
                powerup_type = random.choice([
                    'multi', 'expand', 'laser', 'slow', 'life'
                ]) if has_powerup else None
                
                self.bricks.append({
                    'x': x,
                    'y': y,
                    'color': colors[row],
                    'active': True,
                    'powerup': powerup_type
                })
    
    def restart(self):
        """Restart game."""
        self.on_activate()
        audio.play('beep')
    
    def fire_laser(self):
        """Fire laser from paddle."""
        # Fire from both sides of paddle
        self.lasers.append({
            'x': self.paddle_x + 5,
            'y': self.paddle_y - self.laser_height
        })
        self.lasers.append({
            'x': self.paddle_x + self.paddle_width - 5 - self.laser_width,
            'y': self.paddle_y - self.laser_height
        })
        audio.play('beep')
    
    def activate_powerup(self, powerup_type):
        """Activate a power-up."""
        if powerup_type == 'multi':
            # Add 2 more balls
            for ball in list(self.balls[:1]):  # Clone from first ball
                self.balls.append({
                    'x': ball['x'],
                    'y': ball['y'],
                    'vx': ball['vx'] + random.randint(-2, 2),
                    'vy': ball['vy']
                })
                self.balls.append({
                    'x': ball['x'],
                    'y': ball['y'],
                    'vx': ball['vx'] - random.randint(-2, 2),
                    'vy': ball['vy']
                })
        
        elif powerup_type == 'expand':
            self.paddle_width = self.paddle_expanded_width
            self.active_powerups.add('expand')
            self.powerup_timers['expand'] = time.time() + 10  # 10 seconds
        
        elif powerup_type == 'laser':
            self.active_powerups.add('laser')
            self.powerup_timers['laser'] = time.time() + 15  # 15 seconds
        
        elif powerup_type == 'slow':
            # Slow down all balls
            for ball in self.balls:
                ball['vx'] = max(1, ball['vx'] // 2)
                ball['vy'] = max(1, ball['vy'] // 2)
            self.active_powerups.add('slow')
            self.powerup_timers['slow'] = time.time() + 8  # 8 seconds
        
        elif powerup_type == 'life':
            self.lives = min(self.lives + 1, 5)
    
    def on_event(self, event):
        """Handle input."""
        if event.key == InputEvent.BACK or event.key == InputEvent.HOME:
            return False  # Exit app
        
        if self.game_over or self.won:
            if event.key == 'r' or event.key == InputEvent.OK:
                self.restart()
                return True
            return True
        
        if event.key == InputEvent.LEFT:
            self.paddle_x = max(self.play_left, self.paddle_x - self.paddle_speed)
            self.dirty = True
            return True
        elif event.key == InputEvent.RIGHT:
            self.paddle_x = min(self.play_right - self.paddle_width, self.paddle_x + self.paddle_speed)
            self.dirty = True
            return True
        elif event.key == InputEvent.ACTION or event.key == ' ':
            # Fire laser if active
            if 'laser' in self.active_powerups:
                self.fire_laser()
            self.dirty = True
            return True
        elif event.key == 'r':
            self.restart()
            return True
        
        return False
    
    def on_update(self, delta_time):
        """Update game logic."""
        if self.game_over or self.won:
            return
        
        self.dirty = True
        self.frame_count += 1
        
        # Update power-up timers
        current_time = time.time()
        expired = []
        for powerup, end_time in self.powerup_timers.items():
            if current_time >= end_time:
                expired.append(powerup)
        
        for powerup in expired:
            self.active_powerups.discard(powerup)
            del self.powerup_timers[powerup]
            if powerup == 'expand':
                self.paddle_width = self.paddle_normal_width
            if powerup == 'slow':
                # Speed up balls again
                for ball in self.balls:
                    ball['vx'] *= 2
                    ball['vy'] *= 2
        
        # Move balls
        balls_to_remove = []
        for i, ball in enumerate(self.balls):
            ball['x'] += ball['vx']
            ball['y'] += ball['vy']
            
            # Ball collision with walls
            if ball['x'] <= self.play_left or ball['x'] >= self.play_right - self.ball_size:
                ball['vx'] = -ball['vx']
                audio.play('tick')
            
            if ball['y'] <= 0:
                ball['vy'] = -ball['vy']
                audio.play('tick')
            
            # Ball collision with paddle
            if (ball['y'] + self.ball_size >= self.paddle_y and
                ball['y'] < self.paddle_y + self.paddle_height and
                ball['x'] + self.ball_size > self.paddle_x and
                ball['x'] < self.paddle_x + self.paddle_width):
                
                ball['vy'] = -abs(ball['vy'])  # Always bounce up
                # Add spin based on where ball hits paddle
                hit_pos = (ball['x'] - self.paddle_x) / self.paddle_width
                ball['vx'] = int((hit_pos - 0.5) * 8)
                audio.play('beep')
            
            # Ball collision with bricks
            for brick in self.bricks:
                if not brick['active']:
                    continue
                
                if (ball['x'] + self.ball_size > brick['x'] and
                    ball['x'] < brick['x'] + self.brick_width and
                    ball['y'] + self.ball_size > brick['y'] and
                    ball['y'] < brick['y'] + self.brick_height):
                    
                    brick['active'] = False
                    ball['vy'] = -ball['vy']
                    self.score += 10 * self.level
                    audio.play('collect')
                    
                    # Drop power-up
                    if brick['powerup']:
                        self.powerups.append({
                            'x': brick['x'] + self.brick_width // 2,
                            'y': brick['y'] + self.brick_height,
                            'type': brick['powerup']
                        })
                    break
            
            # Ball falls off bottom
            if ball['y'] >= self.height:
                balls_to_remove.append(i)
        
        # Remove fallen balls
        for i in reversed(balls_to_remove):
            self.balls.pop(i)
        
        # If no balls left, lose life
        if len(self.balls) == 0:
            self.lives -= 1
            audio.play('warning')
            if self.lives <= 0:
                self.game_over = True
                audio.play('gameover')
                if self.score > self.high_score:
                    self.high_score = self.score
                    storage.set('breakout.high_score', self.high_score)
            else:
                # Reset ball
                self.balls = [{
                    'x': self.play_left + self.play_width // 2,
                    'y': self.paddle_y - 15,
                    'vx': 3,
                    'vy': -3
                }]
        
        # Move power-ups
        powerups_to_remove = []
        for i, powerup in enumerate(self.powerups):
            powerup['y'] += 2
            
            # Check collision with paddle
            if (powerup['y'] + self.powerup_size >= self.paddle_y and
                powerup['y'] < self.paddle_y + self.paddle_height and
                powerup['x'] + self.powerup_size > self.paddle_x and
                powerup['x'] < self.paddle_x + self.paddle_width):
                
                self.activate_powerup(powerup['type'])
                powerups_to_remove.append(i)
                audio.play('success')
            
            # Remove if off screen
            elif powerup['y'] >= self.height:
                powerups_to_remove.append(i)
        
        for i in reversed(powerups_to_remove):
            self.powerups.pop(i)
        
        # Move lasers
        lasers_to_remove = []
        for i, laser in enumerate(self.lasers):
            laser['y'] -= self.laser_speed
            
            # Check collision with bricks
            hit = False
            for brick in self.bricks:
                if not brick['active']:
                    continue
                
                if (laser['x'] + self.laser_width > brick['x'] and
                    laser['x'] < brick['x'] + self.brick_width and
                    laser['y'] < brick['y'] + self.brick_height and
                    laser['y'] + self.laser_height > brick['y']):
                    
                    brick['active'] = False
                    self.score += 5 * self.level
                    audio.play('tick')
                    hit = True
                    break
            
            if hit or laser['y'] < 0:
                lasers_to_remove.append(i)
        
        for i in reversed(lasers_to_remove):
            self.lasers.pop(i)
        
        # Check win condition
        if all(not brick['active'] for brick in self.bricks):
            self.level += 1
            self.init_bricks()
            self.balls = [{
                'x': self.play_left + self.play_width // 2,
                'y': self.paddle_y - 15,
                'vx': 3 + self.level,
                'vy': -3 - self.level
            }]
            audio.play('success')
            if self.score > self.high_score:
                self.high_score = self.score
                storage.set('breakout.high_score', self.high_score)
    
    def render(self, matrix):
        """Render game at 256×192."""
        # Clear screen
        matrix.clear()
        
        # Fill with dark blue space background
        matrix.rect(0, 0, self.width, self.height, (0, 0, 40), fill=True)
        
        # Draw bricks with 3D effect
        for brick in self.bricks:
            if brick['active']:
                # Main brick
                matrix.rect(brick['x'], brick['y'],
                           self.brick_width, self.brick_height,
                           brick['color'], fill=True)
                # Highlight
                matrix.line(brick['x'], brick['y'], 
                           brick['x'] + self.brick_width - 1, brick['y'],
                           tuple(min(c + 80, 255) for c in brick['color']))
                # Shadow
                matrix.line(brick['x'], brick['y'] + self.brick_height - 1,
                           brick['x'] + self.brick_width - 1, brick['y'] + self.brick_height - 1,
                           tuple(max(c - 80, 0) for c in brick['color']))
                
                # Power-up indicator
                if brick['powerup']:
                    px = brick['x'] + self.brick_width // 2 - 1
                    py = brick['y'] + self.brick_height // 2 - 1
                    matrix.rect(px, py, 3, 3, (255, 255, 255), fill=True)
        
        # Draw paddle with gradient
        for i in range(self.paddle_height):
            gray = 150 + i * 15
            matrix.line(self.paddle_x, self.paddle_y + i,
                       self.paddle_x + self.paddle_width - 1, self.paddle_y + i,
                       (gray, gray, gray))
        
        # Laser mode - add gun turrets
        if 'laser' in self.active_powerups:
            matrix.rect(self.paddle_x + 3, self.paddle_y - 4, 4, 4, (255, 0, 0), fill=True)
            matrix.rect(self.paddle_x + self.paddle_width - 7, self.paddle_y - 4, 4, 4, (255, 0, 0), fill=True)
        
        # Draw balls with glow
        for ball in self.balls:
            bx, by = int(ball['x']), int(ball['y'])
            # Glow
            matrix.rect(bx - 1, by - 1, self.ball_size + 2, self.ball_size + 2, (255, 255, 100), fill=True)
            # Ball
            matrix.rect(bx, by, self.ball_size, self.ball_size, (255, 255, 255), fill=True)
        
        # Draw power-ups
        powerup_colors = {
            'multi': (255, 100, 255),  # Magenta
            'expand': (0, 255, 255),   # Cyan
            'laser': (255, 0, 0),      # Red
            'slow': (100, 100, 255),   # Blue
            'life': (0, 255, 0)        # Green
        }
        powerup_letters = {
            'multi': 'M',
            'expand': 'E',
            'laser': 'L',
            'slow': 'S',
            'life': '+'
        }
        for powerup in self.powerups:
            color = powerup_colors.get(powerup['type'], (255, 255, 255))
            px, py = int(powerup['x']), int(powerup['y'])
            matrix.rect(px, py, self.powerup_size, self.powerup_size, color, fill=True)
            matrix.text(powerup_letters[powerup['type']], px + 1, py + 1, (0, 0, 0))
        
        # Draw lasers
        for laser in self.lasers:
            lx, ly = int(laser['x']), int(laser['y'])
            # Bright red laser beam
            matrix.rect(lx, ly, self.laser_width, self.laser_height, (255, 50, 50), fill=True)
            matrix.line(lx + 1, ly, lx + 1, ly + self.laser_height - 1, (255, 255, 255))
        
        # Left panel - Lives & Active Power-ups
        matrix.line(self.play_left, 0, self.play_left, self.height - 1, (0, 255, 255))
        matrix.text("LIVES", 2, 10, (0, 255, 255))
        for i in range(self.lives):
            # Draw mini paddles
            matrix.rect(5, 25 + i * 15, 20, 4, (200, 200, 200), fill=True)
        
        # Active power-ups indicator
        matrix.text("POWER", 2, 100, (255, 255, 0))
        py = 115
        for powerup in sorted(self.active_powerups):
            time_left = int(self.powerup_timers.get(powerup, 0) - time.time())
            if time_left > 0:
                letter = powerup_letters.get(powerup, '?')
                color = powerup_colors.get(powerup, (255, 255, 255))
                matrix.rect(5, py, 8, 8, color, fill=True)
                matrix.text(letter, 6, py + 1, (0, 0, 0))
                matrix.text(f"{time_left}", 15, py + 1, (255, 255, 255))
                py += 12
        
        # Right panel - Score & Level
        matrix.line(self.play_right, 0, self.play_right, self.height - 1, (0, 255, 255))
        matrix.text("SCORE", self.play_right + 2, 10, (255, 255, 0))
        matrix.text(f"{self.score:05d}", self.play_right + 2, 22, (255, 255, 255))
        
        matrix.text("HI", self.play_right + 2, 45, (255, 200, 0))
        matrix.text(f"{self.high_score:05d}", self.play_right + 2, 57, (255, 255, 255))
        
        matrix.text("LEVEL", self.play_right + 2, 80, (0, 255, 0))
        matrix.text(f"{self.level}", self.play_right + 8, 92, (255, 255, 255))
        
        # Brick count
        active_bricks = sum(1 for b in self.bricks if b['active'])
        matrix.text("BRICKS", self.play_right + 2, 115, (255, 100, 255))
        matrix.text(f"{active_bricks}", self.play_right + 5, 127, (255, 255, 255))
        
        # Play area borders
        matrix.line(self.play_left, 0, self.play_left, self.height - 1, (0, 255, 255))
        matrix.line(self.play_right, 0, self.play_right, self.height - 1, (0, 255, 255))
        
        # Game over
        if self.game_over:
            # Dark overlay
            matrix.rect(self.play_left + 20, 60, 152, 70, (0, 0, 0), fill=True)
            matrix.rect(self.play_left + 20, 60, 152, 70, (255, 0, 0), fill=False)
            matrix.rect(self.play_left + 22, 62, 148, 66, (255, 0, 0), fill=False)
            
            matrix.text("GAME OVER", self.play_left + 35, 75, (255, 0, 0))
            matrix.text(f"Score: {self.score}", self.play_left + 50, 100, (255, 255, 255))
            matrix.text("Press R", self.play_left + 60, 115, (255, 255, 0))
        
        self.dirty = False


def run(os_context):
    """Run Breakout game within MatrixOS framework."""
    app = BreakoutGame()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()


# App instance for launcher
app = BreakoutGame()


def main():
    """Entry point for standalone mode."""
    from matrixos.led_api import create_matrix
    from matrixos.input import KeyboardInput
    
    print("\n" + "="*64)
    print("BREAKOUT - Arkanoid Edition (256×192)")
    print("="*64)
    print("\nControls:")
    print("  Arrow Keys - Move paddle")
    print("  Space      - Fire laser (when active)")
    print("  R          - Restart")
    print("  Backspace  - Quit")
    print("\nPower-ups:")
    print("  M - Multi-ball (3 balls!)")
    print("  E - Expand paddle")
    print("  L - Laser cannon")
    print("  S - Slow ball")
    print("  + - Extra life")
    print("\n" + "="*64 + "\n")
    
    matrix = create_matrix(256, 192, 'rgb')
    
    with KeyboardInput() as input_handler:
        app = BreakoutGame()
        app.on_activate()
        
        last_update = time.time()
        
        while True:
            # Handle input
            event = input_handler.get_key(timeout=0.01)
            if event:
                if not app.on_event(event):
                    break
            
            # Update at 60 FPS
            current_time = time.time()
            if current_time - last_update >= 1/60:
                app.on_update(current_time - last_update)
                if app.dirty:
                    app.render(matrix)
                    matrix.show()
                last_update = current_time
    
    print(f"\n{'='*64}")
    print(f"Final Score: {app.score}")
    print(f"High Score: {app.high_score}")
    print(f"{'='*64}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted.")
