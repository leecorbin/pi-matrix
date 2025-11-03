#!/usr/bin/env python3
"""
Platformer - Side-scrolling platform game

Features:
- Jump and run mechanics
- Multiple platforms
- Coins to collect
- Obstacles and enemies
- Simple physics
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent


class PlatformerGame(App):
    """Side-scrolling platformer game."""
    
    def __init__(self):
        super().__init__("Platformer")
        # Player
        self.player_x = 20
        self.player_y = 0
        self.player_width = 8
        self.player_height = 10
        self.player_vy = 0
        self.on_ground = False
        
        # Physics
        self.gravity = 0.5
        self.jump_strength = -8
        self.move_speed = 2
        
        # Camera
        self.camera_x = 0
        
        # Level
        self.platforms = []
        self.coins = []
        self.enemies = []
        
        # Game state
        self.score = 0
        self.game_over = False
        self.won = False
        
    def on_activate(self):
        """Initialize game."""
        self.player_x = 20
        self.player_y = 50
        self.player_vy = 0
        self.camera_x = 0
        self.on_ground = False
        self.init_level()
        self.score = 0
        self.game_over = False
        self.won = False
        self.dirty = True
    
    def init_level(self):
        """Initialize level with platforms and collectibles."""
        self.platforms = []
        self.coins = []
        self.enemies = []
        
        # Ground
        self.platforms.append({'x': 0, 'y': 108, 'width': 600, 'height': 10})
        
        # Platforms
        platforms_data = [
            (60, 90, 40), (120, 75, 35), (180, 60, 40), (240, 75, 35),
            (300, 85, 40), (360, 70, 35), (420, 55, 40), (480, 70, 35),
        ]
        
        for x, y, width in platforms_data:
            self.platforms.append({'x': x, 'y': y, 'width': width, 'height': 8})
        
        # Coins
        coin_positions = [
            (80, 70), (140, 55), (200, 40), (260, 55),
            (320, 65), (380, 50), (440, 35), (500, 50)
        ]
        
        for x, y in coin_positions:
            self.coins.append({'x': x, 'y': y, 'size': 6, 'collected': False})
        
        # Enemies (moving obstacles)
        enemy_positions = [(150, 65), (350, 75), (470, 60)]
        
        for x, y in enemy_positions:
            self.enemies.append({
                'x': x, 'y': y, 'width': 8, 'height': 8,
                'vx': 1, 'range': 30, 'start_x': x
            })
    
    def on_deactivate(self):
        """Cleanup when exiting."""
        pass
    
    def on_event(self, event):
        """Handle user input."""
        if self.game_over or self.won:
            if event.key == InputEvent.OK:
                self.on_activate()  # Restart
            return True
        
        if event.key == InputEvent.LEFT:
            self.player_x = max(0, self.player_x - self.move_speed)
            self.dirty = True
        elif event.key == InputEvent.RIGHT:
            self.player_x = min(550, self.player_x + self.move_speed)
            self.dirty = True
        elif event.key == InputEvent.OK or event.key == 'A':
            # Jump
            if self.on_ground:
                self.player_vy = self.jump_strength
                self.on_ground = False
            self.dirty = True
        
        return True  # Event handled
    
    def on_update(self, delta_time):
        """Update game state."""
        if self.game_over or self.won:
            return
        
        # Apply gravity
        self.player_vy += self.gravity
        self.player_y += self.player_vy
        
        # Check platform collisions
        self.on_ground = False
        player_bottom = self.player_y + self.player_height
        
        for platform in self.platforms:
            # Check if player is above platform
            if (self.player_x + self.player_width > platform['x'] and
                self.player_x < platform['x'] + platform['width']):
                
                # Landing on top
                if (self.player_vy >= 0 and
                    player_bottom >= platform['y'] and
                    player_bottom <= platform['y'] + platform['height']):
                    self.player_y = platform['y'] - self.player_height
                    self.player_vy = 0
                    self.on_ground = True
        
        # Check if fell off screen
        if self.player_y > 128:
            self.game_over = True
        
        # Update enemies
        for enemy in self.enemies:
            enemy['x'] += enemy['vx']
            if abs(enemy['x'] - enemy['start_x']) > enemy['range']:
                enemy['vx'] *= -1
        
        # Check enemy collisions
        for enemy in self.enemies:
            if (self.player_x + self.player_width > enemy['x'] and
                self.player_x < enemy['x'] + enemy['width'] and
                self.player_y + self.player_height > enemy['y'] and
                self.player_y < enemy['y'] + enemy['height']):
                self.game_over = True
        
        # Check coin collection
        for coin in self.coins:
            if not coin['collected']:
                coin_center_x = coin['x'] + coin['size'] // 2
                coin_center_y = coin['y'] + coin['size'] // 2
                player_center_x = self.player_x + self.player_width // 2
                player_center_y = self.player_y + self.player_height // 2
                
                distance = ((coin_center_x - player_center_x) ** 2 + 
                           (coin_center_y - player_center_y) ** 2) ** 0.5
                
                if distance < 10:
                    coin['collected'] = True
                    self.score += 10
        
        # Check win condition
        if all(coin['collected'] for coin in self.coins):
            self.won = True
        
        # Update camera to follow player
        target_camera = self.player_x - 40
        self.camera_x = max(0, min(target_camera, 600 - 128))
        
        self.dirty = True
    
    def render(self, matrix):
        """Draw game state."""
        matrix.clear()
        
        if self.game_over:
            matrix.fill((0, 0, 0))
            matrix.text("GAME OVER", 20, 50, (255, 0, 0))
            matrix.text(f"Score: {self.score}", 25, 70, (255, 255, 255))
            matrix.text("Press OK to restart", 10, 90, (150, 150, 150))
            self.dirty = False
            return
        
        if self.won:
            matrix.fill((0, 0, 0))
            matrix.text("YOU WIN!", 25, 50, (0, 255, 0))
            matrix.text(f"Score: {self.score}", 25, 70, (255, 255, 255))
            matrix.text("Press OK to restart", 10, 90, (150, 150, 150))
            self.dirty = False
            return
        
        # Draw background (sky)
        matrix.fill((135, 206, 235))
        
        # Draw platforms
        for platform in self.platforms:
            screen_x = platform['x'] - self.camera_x
            if -platform['width'] < screen_x < 128:
                matrix.rect(screen_x, platform['y'], 
                           platform['width'], platform['height'], 
                           (150, 75, 0), fill=True)
        
        # Draw coins
        for coin in self.coins:
            if not coin['collected']:
                screen_x = coin['x'] - self.camera_x
                if 0 <= screen_x < 128:
                    matrix.circle(screen_x + coin['size']//2, 
                                coin['y'] + coin['size']//2, 
                                coin['size']//2, (255, 215, 0))
        
        # Draw enemies
        for enemy in self.enemies:
            screen_x = enemy['x'] - self.camera_x
            if 0 <= screen_x < 128:
                matrix.rect(screen_x, enemy['y'], 
                           enemy['width'], enemy['height'], 
                           (255, 0, 0), fill=True)
                # Evil eyes
                matrix.pixel(screen_x + 2, enemy['y'] + 2, (255, 255, 0))
                matrix.pixel(screen_x + 5, enemy['y'] + 2, (255, 255, 0))
        
        # Draw player
        player_screen_x = self.player_x - self.camera_x
        matrix.rect(player_screen_x, self.player_y, 
                   self.player_width, self.player_height, 
                   (0, 150, 255), fill=True)
        # Face
        matrix.pixel(player_screen_x + 2, self.player_y + 2, (255, 255, 255))
        matrix.pixel(player_screen_x + 5, self.player_y + 2, (255, 255, 255))
        matrix.pixel(player_screen_x + 3, self.player_y + 6, (255, 255, 255))
        matrix.pixel(player_screen_x + 4, self.player_y + 6, (255, 255, 255))
        
        # Draw HUD
        matrix.text(f"Score: {self.score}", 2, 2, (255, 255, 255))
        coins_left = sum(1 for c in self.coins if not c['collected'])
        matrix.text(f"Coins: {coins_left}", 70, 2, (255, 215, 0))
        
        self.dirty = False


def run(os_context):
    """Run Platformer game within MatrixOS framework."""
    game = PlatformerGame()
    os_context.register_app(game)
    os_context.switch_to_app(game)
    os_context.run()
