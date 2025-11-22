#!/usr/bin/env python3
"""
Space Invaders - Enhanced for 256×192 ZX Spectrum Resolution!

Features:
- 12×5 alien formation (60 invaders!)
- Player ship with rapid-fire laser cannon
- Alien formations that move and descend
- Side panels with stats and shields
- Progressive difficulty with wave system
- Lives and high score tracking
- Beautiful retro ZX Spectrum aesthetic
"""

import sys
import os
import random

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent
from matrixos.logger import get_logger
from matrixos import storage

logger = get_logger("Invaders")


class SpaceInvadersGame(App):
    """Classic Space Invaders - ENHANCED!"""
    
    def __init__(self):
        super().__init__("Invaders")
        
        # Play area (center 192px)
        self.play_left = 32
        self.play_width = 192
        self.play_right = self.play_left + self.play_width
        
        # Player
        self.player_width = 16
        self.player_height = 10
        self.player_x = self.play_left + (self.play_width - self.player_width) // 2
        self.player_y = 170  # Near bottom
        self.player_speed = 4
        
        # Bullets
        self.bullets = []
        self.bullet_speed = 6
        self.max_bullets = 5  # Can have more bullets on screen
        
        # Aliens - 12×5 grid!
        self.aliens = []
        self.alien_width = 12
        self.alien_height = 10
        self.alien_direction = 1
        self.alien_speed = 1.0
        self.alien_descent = 6
        
        # Alien bullets
        self.alien_bullets = []
        self.alien_bullet_speed = 3
        
        # Game state
        self.score = 0
        self.high_score = storage.get('invaders.high_score', 0)
        self.lives = 3
        self.wave = 1
        self.game_over = False
        self.frame_count = 0
        
        # Initialize game immediately
        self.init_aliens()
        
    def on_activate(self):
        """Initialize game."""
        logger.info("Game starting - prepare for invasion!")
        self.player_x = self.play_left + (self.play_width - self.player_width) // 2
        self.bullets = []
        self.alien_bullets = []
        self.init_aliens()
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.game_over = False
        self.frame_count = 0
        self.dirty = True
    
    def init_aliens(self):
        """Initialize massive 12×5 alien formation!"""
        self.aliens = []
        rows = 5  # 5 rows (was 4)
        cols = 12  # 12 columns (was 8)
        spacing_x = 15
        spacing_y = 14
        start_x = self.play_left + 8
        start_y = 20
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                # Different alien types by row
                if row == 0:
                    alien_type = 'commander'  # Top row - special
                elif row <= 2:
                    alien_type = 'soldier'
                else:
                    alien_type = 'grunt'
                    
                self.aliens.append({
                    'x': x,
                    'y': y,
                    'alive': True,
                    'type': alien_type
                })
    
    def on_deactivate(self):
        """Cleanup when exiting."""
        pass
    
    def reset_game(self):
        """Reset for new game."""
        self.player_x = self.play_left + (self.play_width - self.player_width) // 2
        self.bullets = []
        self.alien_bullets = []
        self.init_aliens()
        self.lives = 3
        self.wave = 1
        self.game_over = False
        self.frame_count = 0
        self.alien_speed = 1.0
        self.dirty = True
    
    def next_wave(self):
        """Start next wave with faster aliens!"""
        self.wave += 1
        self.alien_speed += 0.3  # Speed increases each wave
        self.init_aliens()
        self.bullets = []
        self.alien_bullets = []
        logger.info(f"Wave {self.wave} - Speed: {self.alien_speed}")
        self.dirty = True
    
    def on_event(self, event):
        """Handle user input."""
        if self.game_over:
            if event.key in [InputEvent.OK, InputEvent.ACTION, 'A', ' ']:
                logger.info("Restarting game")
                self.reset_game()
                return True
            return False
        
        if event.key == InputEvent.LEFT:
            self.player_x = max(self.play_left, self.player_x - self.player_speed)
            self.dirty = True
            return True
            
        elif event.key == InputEvent.RIGHT:
            self.player_x = min(self.play_right - self.player_width, 
                              self.player_x + self.player_speed)
            self.dirty = True
            return True
            
        elif event.key in [InputEvent.OK, InputEvent.ACTION, 'A', ' ']:
            # Fire bullet - rapid fire capability!
            if len(self.bullets) < self.max_bullets:
                bullet_x = self.player_x + self.player_width // 2 - 1
                self.bullets.append({'x': bullet_x, 'y': self.player_y - 4})
                self.dirty = True
                logger.debug("Player fires!")
            return True
            
        return False
    
    def on_update(self, delta_time):
        """Update game state."""
        if self.game_over:
            return
        
        self.frame_count += 1
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet['y'] -= self.bullet_speed
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
        
        # Update alien bullets
        for bullet in self.alien_bullets[:]:
            bullet['y'] += self.alien_bullet_speed
            if bullet['y'] > 192:
                self.alien_bullets.remove(bullet)
        
        # Update aliens
        alive_aliens = [a for a in self.aliens if a['alive']]
        if not alive_aliens:
            # Wave complete - new wave!
            self.next_wave()
            return
        
        # Move aliens
        if self.frame_count % max(1, int(20 / self.alien_speed)) == 0:
            # Check if need to change direction
            leftmost = min(int(a['x']) for a in alive_aliens)
            rightmost = max(int(a['x']) + self.alien_width for a in alive_aliens)
            
            if (self.alien_direction > 0 and rightmost >= self.play_right) or \
               (self.alien_direction < 0 and leftmost <= self.play_left):
                self.alien_direction *= -1
                for alien in self.aliens:
                    alien['y'] = int(alien['y']) + self.alien_descent
            
            # Move all aliens
            for alien in self.aliens:
                if alien['alive']:
                    alien['x'] = int(alien['x']) + self.alien_direction * int(self.alien_speed)
        
        # Aliens shoot randomly (more bullets in later waves)
        shoot_frequency = max(30, 60 - self.wave * 5)
        if self.frame_count % shoot_frequency == 0 and alive_aliens:
            shooter = random.choice(alive_aliens)
            self.alien_bullets.append({
                'x': shooter['x'] + self.alien_width // 2 - 1,
                'y': shooter['y'] + self.alien_height
            })
        
        # Check collisions
        self.check_collisions()
        
        # Check if aliens reached bottom
        if any(a['y'] + self.alien_height >= self.player_y for a in alive_aliens):
            self.lives = 0
            self.game_over = True
            logger.info("Game Over - Aliens reached Earth!")
        
        self.dirty = True
    
    def check_collisions(self):
        """Check for bullet-alien and bullet-player collisions."""
        # Player bullets hitting aliens
        for bullet in self.bullets[:]:
            for alien in self.aliens:
                if not alien['alive']:
                    continue
                
                # Simple bounding box collision
                if (bullet['x'] >= alien['x'] and
                    bullet['x'] <= alien['x'] + self.alien_width and
                    bullet['y'] >= alien['y'] and
                    bullet['y'] <= alien['y'] + self.alien_height):
                    alien['alive'] = False
                    self.bullets.remove(bullet)
                    # Points based on alien type
                    if alien['type'] == 'commander':
                        self.score += 30
                    elif alien['type'] == 'soldier':
                        self.score += 20
                    else:
                        self.score += 10
                    
                    # Check high score
                    if self.score > self.high_score:
                        self.high_score = self.score
                        storage.set('invaders.high_score', self.high_score)
                    break
        
        # Alien bullets hitting player
        for bullet in self.alien_bullets[:]:
            if (bullet['x'] >= self.player_x and
                bullet['x'] <= self.player_x + self.player_width and
                bullet['y'] >= self.player_y and
                bullet['y'] <= self.player_y + self.player_height):
                self.alien_bullets.remove(bullet)
                self.lives -= 1
                logger.info(f"Player hit! Lives remaining: {self.lives}")
                if self.lives <= 0:
                    self.game_over = True
                    logger.info(f"Game Over! Final Score: {self.score}")
    
    def render(self, matrix):
        """Draw game state - Enhanced 256×192 with side panels!"""
        # Background
        matrix.fill((0, 0, 28))  # Dark blue space
        
        # Draw starfield
        random.seed(42)  # Consistent stars
        for _ in range(30):
            sx = random.randint(self.play_left, self.play_right)
            sy = random.randint(0, 192)
            brightness = random.randint(100, 255)
            matrix.set_pixel(sx, sy, (brightness, brightness, brightness))
        
        if self.game_over:
            # Epic game over screen
            matrix.centered_text("GAME OVER", 70, (255, 0, 0), scale=2)
            matrix.centered_text(f"Score: {self.score}", 100, (255, 255, 0))
            matrix.centered_text(f"High: {self.high_score}", 120, (0, 255, 255))
            matrix.centered_text("Press FIRE to restart", 145, (150, 150, 150))
            
            # Decorative border
            for i in range(0, 256, 8):
                matrix.set_pixel(i, 60, (255, 0, 255))
                matrix.set_pixel(i, 165, (255, 0, 255))
            
            self.dirty = False
            return
        
        # === LEFT PANEL (Lives Display) ===
        panel_color = (0, 255, 255)  # Cyan
        matrix.text("LIVES", 2, 10, panel_color)
        # Draw ship icons for lives
        for i in range(self.lives):
            y = 25 + i * 16
            # Mini ship icon
            matrix.rect(8, y, 12, 8, (0, 255, 0), fill=True)
            matrix.rect(11, y-2, 2, 2, (0, 255, 0), fill=True)  # Gun
        
        # Shields indicator (3 at 100%, 2 at 66%, 1 at 33%, 0 at dead)
        matrix.text("SHIELD", 2, 90, panel_color)
        shield_bars = self.lives
        for i in range(3):
            bar_color = (0, 255, 0) if i < shield_bars else (50, 0, 0)
            matrix.rect(4, 105 + i * 6, 24, 4, bar_color, fill=True)
        
        # === RIGHT PANEL (Score & Stats) ===
        matrix.text("SCORE", 232, 10, panel_color)
        score_str = str(self.score).zfill(5)
        matrix.text(score_str, 230, 25, (255, 255, 0))
        
        matrix.text("HI", 240, 45, panel_color)
        hi_str = str(self.high_score).zfill(5)
        matrix.text(hi_str, 230, 58, (255, 0, 255))
        
        matrix.text("WAVE", 232, 80, panel_color)
        matrix.text(str(self.wave).zfill(2), 238, 95, (255, 255, 255))
        
        # Alien count
        alive_count = sum(1 for a in self.aliens if a['alive'])
        matrix.text("ENEMY", 230, 115, panel_color)
        matrix.text(str(alive_count).zfill(2), 238, 130, (255, 0, 0))
        
        # === PLAY AREA BORDERS ===
        # Cyan/magenta decorative borders (ZX Spectrum style!)
        for y in range(0, 192, 4):
            matrix.set_pixel(self.play_left - 1, y, (0, 255, 255))
            matrix.set_pixel(self.play_right, y, (255, 0, 255))
        
        # Top border line
        matrix.line(self.play_left, 15, self.play_right, 15, (255, 0, 255))
        
        # === GAME OBJECTS ===
        
        # Draw player ship - Enhanced with details!
        # Main body
        matrix.rect(self.player_x, self.player_y, 
                   self.player_width, self.player_height, (0, 255, 0), fill=True)
        # Cockpit
        matrix.rect(self.player_x + 6, self.player_y + 2, 
                   4, 4, (0, 200, 0), fill=True)
        # Gun turret
        matrix.rect(self.player_x + self.player_width // 2 - 1, self.player_y - 4, 
                   2, 4, (0, 255, 0), fill=True)
        # Engine glow (pulsing)
        glow = 150 + int(50 * abs((self.frame_count % 20) / 10.0 - 1))
        matrix.rect(self.player_x + 2, self.player_y + self.player_height, 
                   4, 2, (glow, glow, 0), fill=True)
        matrix.rect(self.player_x + 10, self.player_y + self.player_height, 
                   4, 2, (glow, glow, 0), fill=True)
        
        # Draw aliens - Different sprites for different types!
        for alien in self.aliens:
            if not alien['alive']:
                continue
            
            # Ensure integer coordinates
            ax, ay = int(alien['x']), int(alien['y'])
            
            # Colors by type
            if alien['type'] == 'commander':
                color = (255, 0, 0)  # Red commanders
                eye_color = (255, 255, 0)
            elif alien['type'] == 'soldier':
                color = (255, 0, 255)  # Magenta soldiers
                eye_color = (255, 255, 0)
            else:
                color = (150, 0, 255)  # Purple grunts
                eye_color = (255, 200, 0)
            
            # Body
            matrix.rect(ax, ay, 
                       self.alien_width, self.alien_height, color, fill=True)
            
            # Eyes (animated blink)
            if self.frame_count % 40 != 0:  # Blink occasionally
                matrix.set_pixel(ax + 3, ay + 3, eye_color)
                matrix.set_pixel(ax + 8, ay + 3, eye_color)
            
            # Antennae (commanders only)
            if alien['type'] == 'commander':
                matrix.set_pixel(ax + 2, ay - 1, (255, 0, 0))
                matrix.set_pixel(ax + 9, ay - 1, (255, 0, 0))
        
        # Draw player bullets (bright yellow lasers)
        for bullet in self.bullets:
            matrix.rect(bullet['x'], bullet['y'], 
                       2, 6, (255, 255, 0), fill=True)
            # Bright tip
            matrix.set_pixel(bullet['x'], bullet['y'] - 1, (255, 255, 255))
        
        # Draw alien bullets (red plasma)
        for bullet in self.alien_bullets:
            matrix.rect(bullet['x'], bullet['y'], 
                       2, 6, (255, 0, 0), fill=True)
            # Dark trail
            matrix.set_pixel(bullet['x'], bullet['y'] + 6, (100, 0, 0))
        
        self.dirty = False


def run(os_context):
    """Run Space Invaders game within MatrixOS framework."""
    logger.info("run() function called")
    game = SpaceInvadersGame()
    logger.info("Game instance created")
    os_context.register_app(game)
    logger.info("App registered")
    os_context.switch_to_app(game)
    logger.info("Switched to app - entering event loop")
    os_context.run()
    logger.info("Event loop exited")


# App instance for launcher
app = SpaceInvadersGame()


def main():
    """Entry point for standalone mode."""
    import time
    from matrixos.led_api import create_matrix
    from matrixos.input import KeyboardInput
    
    print("\n" + "="*80)
    print("SPACE INVADERS - Enhanced for 256×192 ZX Spectrum Resolution!")
    print("="*80)
    print("\nControls:")
    print("  Arrow Keys - Move ship left/right")
    print("  Space/A    - Fire laser")
    print("  Backspace  - Quit")
    print("\nFeatures:")
    print("  • Massive 12×5 alien formation (60 invaders!)")
    print("  • Three alien types with different point values")
    print("  • Progressive difficulty - waves get faster!")
    print("  • Side panels with lives, score, and stats")
    print("  • Beautiful ZX Spectrum aesthetic")
    print("  • High score tracking")
    print("="*80 + "\n")
    
    # Create display
    matrix = create_matrix(width=256, height=192)
    input_handler = KeyboardInput()
    
    # Initialize game
    app.on_activate()
    
    print("Game started! Press Backspace to quit.\n")
    
    # Game loop
    last_update = time.time()
    running = True
    
    try:
        while running:
            # Handle input
            event = input_handler.get_key(timeout=0.01)
            if event:
                if event.key == InputEvent.BACK:
                    running = False
                else:
                    app.on_event(event)
            
            # Update at 60 FPS
            current_time = time.time()
            if current_time - last_update >= 1/60:
                app.on_update(current_time - last_update)
                if app.dirty:
                    app.render(matrix)
                    matrix.show()
                last_update = current_time
    
    except KeyboardInterrupt:
        print("\n\nGame interrupted.")
    
    print(f"\n{'='*64}")
    print(f"Final Score: {app.score}")
    print(f"High Score: {app.high_score}")
    print(f"{'='*64}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted.")
