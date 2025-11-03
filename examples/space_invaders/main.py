#!/usr/bin/env python3
"""
Space Invaders - Classic arcade shooter

Features:
- Waves of alien invaders
- Player ship with laser cannon
- Alien formations that move and descend
- Progressive difficulty
- Lives and scoring system
"""

import sys
import os
import random

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent
from matrixos.logger import get_logger

logger = get_logger("Invaders")


class SpaceInvadersGame(App):
    """Classic Space Invaders arcade game."""
    
    def __init__(self):
        super().__init__("Invaders")
        # Player
        self.player_x = (128 - 12) // 2  # Center player initially
        self.player_y = 110
        self.player_width = 12
        self.player_height = 8
        self.player_speed = 3
        
        # Bullets
        self.bullets = []
        self.bullet_speed = 4
        
        # Aliens
        self.aliens = []
        self.alien_width = 10
        self.alien_height = 8
        self.alien_direction = 1
        self.alien_speed = 1
        self.alien_descent = 8
        
        # Alien bullets
        self.alien_bullets = []
        self.alien_bullet_speed = 2
        
        # Game state
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.game_over = False
        self.frame_count = 0
        
        # Initialize game immediately
        self.init_aliens()
        
    def on_activate(self):
        """Initialize game."""
        logger.info("on_activate() called")
        self.player_x = (128 - self.player_width) // 2
        self.bullets = []
        self.alien_bullets = []
        self.init_aliens()
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.game_over = False
        self.frame_count = 0
        self.dirty = True
        logger.info("on_activate() completed")
    
    def init_aliens(self):
        """Initialize alien formation."""
        self.aliens = []
        rows = 4
        cols = 8
        spacing_x = 14
        spacing_y = 12
        start_x = 10
        start_y = 10
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.aliens.append({
                    'x': x,
                    'y': y,
                    'alive': True
                })
    
    def on_deactivate(self):
        """Cleanup when exiting."""
        pass
    
    def on_event(self, event):
        """Handle user input."""
        if self.game_over:
            if event.key == InputEvent.OK:
                self.on_activate()  # Restart
            return True
        
        if event.key == InputEvent.LEFT:
            self.player_x = max(0, self.player_x - self.player_speed)
            self.dirty = True
        elif event.key == InputEvent.RIGHT:
            self.player_x = min(128 - self.player_width, self.player_x + self.player_speed)
            self.dirty = True
        elif event.key in [InputEvent.OK, InputEvent.ACTION, 'A', ' ']:
            # Fire bullet (Enter, Space, or A)
            if len(self.bullets) < 3:  # Limit bullets
                self.bullets.append({
                    'x': self.player_x + self.player_width // 2 - 1,
                    'y': self.player_y,
                    'width': 2,
                    'height': 6
                })
            self.dirty = True
        
        return True  # Event handled
    
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
            if bullet['y'] > 128:
                self.alien_bullets.remove(bullet)
        
        # Update aliens
        alive_aliens = [a for a in self.aliens if a['alive']]
        if not alive_aliens:
            # Wave complete - new wave
            self.wave += 1
            self.alien_speed = min(3, 1 + self.wave * 0.3)
            self.init_aliens()
            return
        
        # Move aliens
        if self.frame_count % max(1, int(20 / self.alien_speed)) == 0:
            # Check if need to change direction
            leftmost = min(a['x'] for a in alive_aliens)
            rightmost = max(a['x'] + self.alien_width for a in alive_aliens)
            
            if (self.alien_direction > 0 and rightmost >= 128) or \
               (self.alien_direction < 0 and leftmost <= 0):
                self.alien_direction *= -1
                for alien in self.aliens:
                    alien['y'] += self.alien_descent
            
            # Move all aliens
            for alien in self.aliens:
                if alien['alive']:
                    alien['x'] += self.alien_direction * self.alien_speed
        
        # Aliens shoot randomly
        if self.frame_count % 60 == 0 and alive_aliens:
            shooter = random.choice(alive_aliens)
            self.alien_bullets.append({
                'x': shooter['x'] + self.alien_width // 2 - 1,
                'y': shooter['y'] + self.alien_height,
                'width': 2,
                'height': 6
            })
        
        # Check collisions
        self.check_collisions()
        
        # Check if aliens reached bottom
        if any(a['y'] + self.alien_height >= self.player_y for a in alive_aliens):
            self.lives = 0
            self.game_over = True
        
        self.dirty = True
    
    def check_collisions(self):
        """Check for bullet-alien collisions."""
        # Player bullets hitting aliens
        for bullet in self.bullets[:]:
            for alien in self.aliens:
                if not alien['alive']:
                    continue
                
                if (bullet['x'] < alien['x'] + self.alien_width and
                    bullet['x'] + bullet['width'] > alien['x'] and
                    bullet['y'] < alien['y'] + self.alien_height and
                    bullet['y'] + bullet['height'] > alien['y']):
                    alien['alive'] = False
                    self.bullets.remove(bullet)
                    self.score += 10
                    break
        
        # Alien bullets hitting player
        for bullet in self.alien_bullets[:]:
            if (bullet['x'] < self.player_x + self.player_width and
                bullet['x'] + bullet['width'] > self.player_x and
                bullet['y'] < self.player_y + self.player_height and
                bullet['y'] + bullet['height'] > self.player_y):
                self.alien_bullets.remove(bullet)
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
    
    def render(self, matrix):
        """Draw game state."""
        matrix.clear()
        matrix.fill((0, 0, 0))
        
        if self.game_over:
            # Game over screen
            matrix.text("GAME OVER", 20, 50, (255, 0, 0))
            matrix.text(f"Score: {self.score}", 25, 70, (255, 255, 255))
            matrix.text("Press OK to restart", 10, 90, (150, 150, 150))
            self.dirty = False
            return
        
        # Draw player
        matrix.rect(self.player_x, self.player_y, 
                   self.player_width, self.player_height, (0, 255, 0), fill=True)
        # Player gun
        matrix.rect(self.player_x + 5, self.player_y - 3, 
                   2, 3, (0, 255, 0), fill=True)
        
        # Draw aliens
        for alien in self.aliens:
            if alien['alive']:
                color = (255, 0, 255)  # Magenta
                matrix.rect(alien['x'], alien['y'], 
                           self.alien_width, self.alien_height, color, fill=True)
                # Eyes
                matrix.set_pixel(alien['x'] + 2, alien['y'] + 2, (255, 255, 0))
                matrix.set_pixel(alien['x'] + 7, alien['y'] + 2, (255, 255, 0))
        
        # Draw player bullets
        for bullet in self.bullets:
            matrix.rect(bullet['x'], bullet['y'], 
                       bullet['width'], bullet['height'], (255, 255, 0), fill=True)
        
        # Draw alien bullets
        for bullet in self.alien_bullets:
            matrix.rect(bullet['x'], bullet['y'], 
                       bullet['width'], bullet['height'], (255, 0, 0), fill=True)
        
        # Draw HUD
        matrix.text(f"Score: {self.score}", 2, 2, (255, 255, 255))
        matrix.text(f"Lives: {self.lives}", 2, 122, (0, 255, 0))
        matrix.text(f"Wave: {self.wave}", 85, 122, (255, 255, 0))
        
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
