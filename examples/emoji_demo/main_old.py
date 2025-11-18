#!/usr/bin/env python3
"""
EmojiSprite Demo

Shows emoji sprites with movement, animation, and collision detection.
Run with: python3 examples/emoji_demo/main.py
"""

from matrixos.app_framework import App
from matrixos.sprites import EmojiSprite, SpriteGroup
from matrixos.input import InputEvent


class EmojiDemo(App):
    """Demo app showing EmojiSprite features."""
    
    def __init__(self):
        super().__init__("Emoji Demo")
        
        # Player (animated runner)
        self.player = EmojiSprite(
            x=64, y=64,
            emoji=["🚶", "🏃"],
            size=20,
            fps=5
        )
        self.player.add_tag("player")
        
        # Collectibles (coins)
        self.coins = SpriteGroup()
        for i in range(5):
            coin = EmojiSprite(
                x=20 + i * 25,
                y=20,
                emoji="🪙",
                size=12
            )
            coin.add_tag("coin")
            self.coins.add(coin)
        
        # Obstacles (rocks)
        self.obstacles = SpriteGroup()
        for i in range(3):
            rock = EmojiSprite(
                x=30 + i * 35,
                y=100,
                emoji="🪨",
                size=16
            )
            rock.add_tag("obstacle")
            self.obstacles.add(rock)
        
        # Animated background element
        self.star = EmojiSprite(
            x=10, y=100,
            emoji=["⭐", "✨", "💫"],
            size=14,
            fps=3
        )
        
        # Score
        self.score = 0
        
        self.dirty = True
    
    def on_event(self, event):
        """Handle input."""
        speed = 60  # pixels per second
        
        if event.key == InputEvent.UP:
            self.player.velocity_y = -speed
            self.player.velocity_x = 0
            self.dirty = True
            return True
        elif event.key == InputEvent.DOWN:
            self.player.velocity_y = speed
            self.player.velocity_x = 0
            self.dirty = True
            return True
        elif event.key == InputEvent.LEFT:
            self.player.velocity_x = -speed
            self.player.velocity_y = 0
            self.dirty = True
            return True
        elif event.key == InputEvent.RIGHT:
            self.player.velocity_x = speed
            self.player.velocity_y = 0
            self.dirty = True
            return True
        elif event.key == InputEvent.ACTION:
            # Stop
            self.player.velocity_x = 0
            self.player.velocity_y = 0
            self.dirty = True
            return True
        
        return False
    
    def on_update(self, delta_time):
        """Update game state."""
        # Update all sprites
        self.player.update(delta_time)
        self.coins.update(delta_time)
        self.obstacles.update(delta_time)
        self.star.update(delta_time)
        
        # Keep player in bounds
        if self.player.x < 0:
            self.player.x = 0
            self.player.velocity_x = 0
        elif self.player.x + self.player.width > 128:
            self.player.x = 128 - self.player.width
            self.player.velocity_x = 0
        
        if self.player.y < 0:
            self.player.y = 0
            self.player.velocity_y = 0
        elif self.player.y + self.player.height > 128:
            self.player.y = 128 - self.player.height
            self.player.velocity_y = 0
        
        # Check coin collection
        for coin in list(self.coins):
            if self.player.collides_with(coin):
                self.coins.remove(coin)
                self.score += 10
                self.logger.info(f"Collected coin! Score: {self.score}")
                self.dirty = True
        
        # Check obstacle collision
        for obstacle in self.obstacles:
            if self.player.collides_with(obstacle):
                # Bounce back
                self.player.velocity_x *= -0.5
                self.player.velocity_y *= -0.5
                self.logger.info("Hit obstacle!")
                self.dirty = True
        
        if self.player.velocity_x != 0 or self.player.velocity_y != 0:
            self.dirty = True
    
    def render(self, matrix):
        """Draw everything."""
        matrix.clear()
        
        # Draw all sprites
        self.star.render(matrix)
        self.coins.render(matrix)
        self.obstacles.render(matrix)
        self.player.render(matrix)
        
        # Draw score
        matrix.text(f"Score: {self.score}", 2, 2, (255, 255, 255))
        
        # Draw instructions at bottom
        if len(self.coins) > 0:
            matrix.text("Arrows=Move", 2, 115, (150, 150, 150))
        else:
            matrix.centered_text("YOU WIN!", y=64, color=(0, 255, 0))
        
        self.dirty = False


def run(os_context):
    """Entry point."""
    app = EmojiDemo()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()


if __name__ == "__main__":
    # For standalone testing
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    from matrixos.display import Display
    from matrixos.input import KeyboardInput
    from matrixos.app_framework import OSContext
    
    matrix = Display(width=128, height=128)
    input_handler = KeyboardInput()
    os_context = OSContext(matrix, input_handler)
    
    run(os_context)
