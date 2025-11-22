#!/usr/bin/env python3
"""
Tetris Game - ZX Spectrum style for 256×192

Upgraded for 256×192 resolution with proper Spectrum aesthetic!

Features:
- Classic 7 tetromino shapes in authentic Spectrum colors
- 10×20 playfield with chunky 8px blocks (Spectrum style!)
- Next 3 pieces preview (plan ahead!)
- Hold piece mechanic (strategy!)
- Side panels with cyan borders (Spectrum aesthetic)
- Left panel: Next 3 pieces, Hold piece, Controls
- Right panel: Score, High score, Lines, Level, Speed
- Line clearing with progressive scoring (1/2/3/4 lines)
- Progressive speed increase with levels
- Proper Spectrum color palette
- Dark blue background (#000028)

Layout:
- Left panel: 32px (next pieces, hold, help)
- Center: 192px (perfect for 10-wide × 8px blocks + borders = 88px playfield)
- Right panel: 32px (stats)

Controls:
- LEFT/RIGHT: Move piece
- UP: Rotate clockwise
- DOWN: Soft drop
- SPACE: Hard drop
- C: Hold piece
- R: Restart
- P: Pause

ZX Spectrum forever! 🎮
"""

import sys
import os
import random

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent
from matrixos import layout, storage
from matrixos.logger import get_logger


# Tetromino shapes (as 4x4 grids)
SHAPES = {
    'I': [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
    'O': [[0,0,0,0], [0,1,1,0], [0,1,1,0], [0,0,0,0]],
    'T': [[0,0,0,0], [0,1,0,0], [1,1,1,0], [0,0,0,0]],
    'S': [[0,0,0,0], [0,1,1,0], [1,1,0,0], [0,0,0,0]],
    'Z': [[0,0,0,0], [1,1,0,0], [0,1,1,0], [0,0,0,0]],
    'J': [[0,0,0,0], [1,0,0,0], [1,1,1,0], [0,0,0,0]],
    'L': [[0,0,0,0], [0,0,1,0], [1,1,1,0], [0,0,0,0]],
}

# ZX Spectrum authentic colors!
COLORS = {
    'I': (0, 255, 255),      # Cyan (classic Spectrum cyan)
    'O': (255, 255, 0),      # Yellow (bright yellow)
    'T': (255, 0, 255),      # Magenta (Spectrum magenta)
    'S': (0, 255, 0),        # Green (bright green)
    'Z': (255, 0, 0),        # Red (bright red)
    'J': (0, 0, 255),        # Blue (bright blue)
    'L': (255, 128, 0),      # Orange (for variety)
}


class TetrisGame(App):
    """ZX Spectrum-style Tetris for 256×192."""
    
    def __init__(self):
        super().__init__("Tetris")
        self.logger = get_logger("tetris")
        
        # Display dimensions (256×192)
        self.width = 256
        self.height = 192
        self.panel_width = 32
        self.play_area_x = self.panel_width
        self.play_area_width = self.width - (2 * self.panel_width)  # 192px
        
        # Playfield (10 wide × 20 tall with 8px blocks - Spectrum chunky!)
        self.field_width = 10
        self.field_height = 20
        self.block_size = 8  # Chunky Spectrum blocks!
        
        # Center the playfield in the play area
        playfield_pixel_width = self.field_width * self.block_size  # 80px
        self.field_x = self.play_area_x + (self.play_area_width - playfield_pixel_width) // 2
        self.field_y = 10
        
        self.field = []
        
        # Current piece
        self.current_shape = None
        self.current_type = None
        self.current_x = 0
        self.current_y = 0
        
        # Next 3 pieces (strategic planning!)
        self.next_queue = []
        
        # Hold piece mechanic
        self.hold_piece = None
        self.can_hold = True
        
        # Game state
        self.score = 0
        self.lines = 0
        self.level = 1
        self.high_score = storage.get('tetris.high_score', 0)
        self.game_over = False
        self.paused = False
        self.update_timer = 0
        self.update_speed = 30  # Frames between drops (decreases with level)
        self.fast_fall = False
        
        self.logger.info("Tetris initialized for 256×192 with Spectrum aesthetic!")
    
    def get_speed_for_level(self):
        """Calculate drop speed based on level (faster = lower number)"""
        return max(5, 30 - (self.level - 1) * 2)
        
    def on_activate(self):
        """Initialize game."""
        self.field = [[None for _ in range(self.field_width)]
                      for _ in range(self.field_height)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.update_timer = 0
        self.update_speed = self.get_speed_for_level()
        self.fast_fall = False
        self.hold_piece = None
        self.can_hold = True
        
        # Fill next queue with 3 pieces
        self.next_queue = [random.choice(list(SHAPES.keys())) for _ in range(3)]
        
        self.spawn_piece()
        self.dirty = True
        self.logger.info("Game started!")
    
    def rotate_shape(self, shape):
        """Rotate shape 90 degrees clockwise."""
        return [[shape[3-j][i] for j in range(4)] for i in range(4)]
    
    def spawn_piece(self):
        """Spawn a new piece from queue."""
        # Get next from queue
        self.current_type = self.next_queue.pop(0)
        self.current_shape = [row[:] for row in SHAPES[self.current_type]]
        self.current_x = self.field_width // 2 - 2
        self.current_y = 0
        
        # Add new piece to end of queue
        self.next_queue.append(random.choice(list(SHAPES.keys())))
        
        # Can hold again after spawning new piece
        self.can_hold = True
        
        # Check if can spawn
        if not self.can_place(self.current_x, self.current_y, self.current_shape):
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                storage.set('tetris.high_score', self.high_score)
            self.logger.info(f"Game over! Final score: {self.score}, Lines: {self.lines}")
    
    def hold_current_piece(self):
        """Hold current piece for later use."""
        if not self.can_hold:
            return
        
        if self.hold_piece is None:
            # First hold - store and spawn new
            self.hold_piece = self.current_type
            self.spawn_piece()
        else:
            # Swap with held piece
            temp = self.hold_piece
            self.hold_piece = self.current_type
            self.current_type = temp
            self.current_shape = [row[:] for row in SHAPES[self.current_type]]
            self.current_x = self.field_width // 2 - 2
            self.current_y = 0
        
        self.can_hold = False
        self.logger.debug(f"Piece held: {self.hold_piece}")
    
    def can_place(self, x, y, shape):
        """Check if piece can be placed at position."""
        for sy in range(4):
            for sx in range(4):
                if shape[sy][sx]:
                    fx = x + sx
                    fy = y + sy
                    
                    # Check bounds
                    if fx < 0 or fx >= self.field_width or fy >= self.field_height:
                        return False
                    
                    # Check collision (but allow negative y for spawning)
                    if fy >= 0 and self.field[fy][fx] is not None:
                        return False
        
        return True
    
    def place_piece(self):
        """Place current piece into field."""
        for sy in range(4):
            for sx in range(4):
                if self.current_shape[sy][sx]:
                    fx = self.current_x + sx
                    fy = self.current_y + sy
                    if 0 <= fy < self.field_height:
                        self.field[fy][fx] = self.current_type
        
        # Check for completed lines
        self.check_lines()
        
        # Spawn next piece
        self.spawn_piece()
    
    def check_lines(self):
        """Check and clear completed lines."""
        lines_cleared = 0
        
        y = self.field_height - 1
        while y >= 0:
            if all(self.field[y][x] is not None for x in range(self.field_width)):
                # Remove line
                del self.field[y]
                # Add empty line at top
                self.field.insert(0, [None for _ in range(self.field_width)])
                lines_cleared += 1
                # Don't decrement y, check same line again
            else:
                y -= 1
        
        if lines_cleared > 0:
            self.lines += lines_cleared
            # Tetris scoring: Single=100, Double=300, Triple=500, Tetris=800
            scores = [0, 100, 300, 500, 800]
            points = scores[min(lines_cleared, 4)] * self.level
            self.score += points
            
            # Level up every 10 lines
            new_level = (self.lines // 10) + 1
            if new_level > self.level:
                self.level = new_level
                self.update_speed = self.get_speed_for_level()
                self.logger.info(f"Level up! Now level {self.level}, speed {self.update_speed}")
            
            self.logger.info(f"Cleared {lines_cleared} line(s), +{points} points")
    
    def restart(self):
        """Restart game."""
        self.on_activate()
    
    def hard_drop(self):
        """Drop piece instantly to bottom."""
        drop_distance = 0
        while self.can_place(self.current_x, self.current_y + 1, self.current_shape):
            self.current_y += 1
            drop_distance += 1
        
        # Bonus points for hard drop
        self.score += drop_distance * 2
        
        # Place piece immediately
        self.place_piece()
        self.dirty = True
        self.logger.debug(f"Hard drop: {drop_distance} cells, +{drop_distance * 2} points")
    
    def on_event(self, event):
        """Handle input."""
        if self.game_over:
            if event.key == 'r' or event.key == 'R' or event.key == InputEvent.OK:
                self.restart()
                self.dirty = True
                return True
            return True
        
        if event.key == 'p' or event.key == 'P':
            self.paused = not self.paused
            self.dirty = True
            return True
        
        if self.paused:
            return True
        
        if event.key == InputEvent.LEFT:
            if self.can_place(self.current_x - 1, self.current_y, self.current_shape):
                self.current_x -= 1
                self.dirty = True
            return True
        
        elif event.key == InputEvent.RIGHT:
            if self.can_place(self.current_x + 1, self.current_y, self.current_shape):
                self.current_x += 1
                self.dirty = True
            return True
        
        elif event.key == InputEvent.DOWN:
            # Soft drop
            self.fast_fall = True
            return True
        
        elif event.key == InputEvent.UP:
            # Rotate clockwise
            rotated = self.rotate_shape(self.current_shape)
            if self.can_place(self.current_x, self.current_y, rotated):
                self.current_shape = rotated
                self.dirty = True
            return True
        
        elif event.key == ' ' or event.key == InputEvent.ACTION:
            # Hard drop
            self.hard_drop()
            return True
        
        elif event.key == 'c' or event.key == 'C':
            # Hold piece
            self.hold_current_piece()
            self.dirty = True
            return True
        
        elif event.key == 'r' or event.key == 'R':
            self.restart()
            return True
        
        return False
    
    def on_update(self, delta_time):
        """Update game logic."""
        if self.game_over or self.paused:
            return
        
        self.update_timer += 1
        
        # Fast fall speed (soft drop)
        fall_speed = 2 if self.fast_fall else self.update_speed
        
        if self.update_timer >= fall_speed:
            self.update_timer = 0
            self.fast_fall = False
            
            # Try to move piece down
            if self.can_place(self.current_x, self.current_y + 1, self.current_shape):
                self.current_y += 1
                self.dirty = True
            else:
                # Piece landed
                self.place_piece()
                self.dirty = True
    
    def draw_mini_tetromino(self, matrix, piece_type, x, y, size=5):
        """Draw a small tetromino for preview/hold."""
        shape = SHAPES[piece_type]
        color = COLORS[piece_type]
        
        for sy in range(4):
            for sx in range(4):
                if shape[sy][sx]:
                    px = x + sx * size
                    py = y + sy * size
                    matrix.rect(px, py, size - 1, size - 1, color, fill=True)
    
    def render(self, matrix):
        """Render game at 256×192 with ZX Spectrum aesthetic."""
        # Clear screen
        matrix.clear()
        
        # Dark blue Spectrum background
        matrix.rect(0, 0, self.width, self.height, (0, 0, 40), fill=True)
        
        # === LEFT PANEL (32px) ===
        # Cyan border (Spectrum style!)
        matrix.line(self.panel_width - 1, 0, self.panel_width - 1, self.height - 1, (0, 255, 255))
        
        y_pos = 5
        
        # Next 3 pieces
        matrix.text("NXT", 3, y_pos, (255, 255, 255))
        y_pos += 10
        
        for i, piece_type in enumerate(self.next_queue[:3]):
            self.draw_mini_tetromino(matrix, piece_type, 4, y_pos, size=5)
            y_pos += 25
        
        y_pos += 5
        
        # Hold piece
        matrix.text("HLD", 3, y_pos, (255, 255, 255))
        y_pos += 10
        
        if self.hold_piece:
            self.draw_mini_tetromino(matrix, self.hold_piece, 4, y_pos, size=5)
        else:
            matrix.text("---", 6, y_pos + 8, (100, 100, 100))
        
        y_pos += 30
        
        # Controls (compact)
        matrix.text("C:HLD", 2, y_pos, (200, 200, 0))
        y_pos += 8
        matrix.text("SPC:", 2, y_pos, (200, 200, 0))
        y_pos += 8
        matrix.text("DROP", 2, y_pos, (200, 200, 0))
        
        # === RIGHT PANEL (32px) ===
        panel_x = self.width - self.panel_width
        
        # Cyan border
        matrix.line(panel_x, 0, panel_x, self.height - 1, (0, 255, 255))
        
        y_pos = 10
        
        # Score
        matrix.text("SCR", panel_x + 2, y_pos, (255, 255, 255))
        y_pos += 8
        score_str = str(self.score)
        if len(score_str) > 5:
            score_str = score_str[:5]
        matrix.text(score_str, panel_x + 2, y_pos, (255, 255, 0))
        y_pos += 15
        
        # High score
        matrix.text("HI", panel_x + 2, y_pos, (255, 255, 255))
        y_pos += 8
        hi_str = str(self.high_score)
        if len(hi_str) > 5:
            hi_str = hi_str[:5]
        matrix.text(hi_str, panel_x + 2, y_pos, (255, 100, 100))
        y_pos += 15
        
        # Lines
        matrix.text("LNS", panel_x + 2, y_pos, (255, 255, 255))
        y_pos += 8
        matrix.text(str(self.lines), panel_x + 2, y_pos, (0, 255, 255))
        y_pos += 15
        
        # Level
        matrix.text("LVL", panel_x + 2, y_pos, (255, 255, 255))
        y_pos += 8
        matrix.text(str(self.level), panel_x + 2, y_pos, (0, 255, 0))
        y_pos += 15
        
        # Speed indicator
        matrix.text("SPD", panel_x + 2, y_pos, (255, 255, 255))
        y_pos += 8
        speed_val = 31 - self.update_speed  # Higher number = faster
        matrix.text(str(speed_val), panel_x + 2, y_pos, (255, 127, 0))
        
        # === CENTER PLAY AREA (192px) ===
        
        # Draw playfield border (thick Spectrum style)
        border_x = self.field_x - 2
        border_y = self.field_y - 2
        border_w = self.field_width * self.block_size + 4
        border_h = self.field_height * self.block_size + 4
        
        # Double border (Spectrum aesthetic)
        matrix.rect(border_x, border_y, border_w, border_h, (0, 255, 255), fill=False)
        matrix.rect(border_x - 1, border_y - 1, border_w + 2, border_h + 2, (0, 255, 255), fill=False)
        
        # Draw placed blocks
        for y in range(self.field_height):
            for x in range(self.field_width):
                if self.field[y][x] is not None:
                    color = COLORS[self.field[y][x]]
                    px = self.field_x + x * self.block_size
                    py = self.field_y + y * self.block_size
                    
                    # Draw block with highlight (3D effect)
                    matrix.rect(px, py, self.block_size - 1, self.block_size - 1, color, fill=True)
                    
                    # Top-left highlight
                    lighter = tuple(min(c + 50, 255) for c in color)
                    matrix.line(px, py, px + self.block_size - 2, py, lighter)
                    matrix.line(px, py, px, py + self.block_size - 2, lighter)
        
        # Draw current piece
        if self.current_shape:
            color = COLORS[self.current_type]
            for sy in range(4):
                for sx in range(4):
                    if self.current_shape[sy][sx]:
                        px = self.field_x + (self.current_x + sx) * self.block_size
                        py = self.field_y + (self.current_y + sy) * self.block_size
                        
                        # Only draw if in visible area
                        if py >= self.field_y:
                            matrix.rect(px, py, self.block_size - 1, self.block_size - 1, color, fill=True)
                            
                            # Top-left highlight
                            lighter = tuple(min(c + 50, 255) for c in color)
                            matrix.line(px, py, px + self.block_size - 2, py, lighter)
                            matrix.line(px, py, px, py + self.block_size - 2, lighter)
        
        # Game over overlay
        if self.game_over:
            # Dark overlay
            overlay_x = self.play_area_x + 30
            overlay_y = 70
            overlay_w = 132
            overlay_h = 52
            
            matrix.rect(overlay_x, overlay_y, overlay_w, overlay_h, (0, 0, 0), fill=True)
            matrix.rect(overlay_x, overlay_y, overlay_w, overlay_h, (255, 0, 0), fill=False)
            matrix.rect(overlay_x + 1, overlay_y + 1, overlay_w - 2, overlay_h - 2, (255, 0, 0), fill=False)
            
            matrix.text("GAME OVER", overlay_x + 20, overlay_y + 10, (255, 0, 0))
            matrix.text(f"Score: {self.score}", overlay_x + 20, overlay_y + 22, (255, 255, 255))
            matrix.text(f"Lines: {self.lines}", overlay_x + 20, overlay_y + 32, (0, 255, 255))
            matrix.text("Press R", overlay_x + 30, overlay_y + 44, (255, 255, 0))
        
        # Pause indicator
        if self.paused:
            matrix.text("PAUSED", self.play_area_x + 70, 90, (255, 255, 0))
        
        self.dirty = False


def run(os_context):
    """Run Tetris game within MatrixOS framework."""
    app = TetrisGame()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()


if __name__ == '__main__':
    """Standalone test mode"""
    from matrixos.led_api import create_matrix
    from matrixos.input import KeyboardInput
    import time
    
    print("\n" + "="*64)
    print("TETRIS - ZX SPECTRUM EDITION (256×192)")
    print("="*64)
    print("\nControls:")
    print("  LEFT/RIGHT - Move piece")
    print("  UP         - Rotate")
    print("  DOWN       - Soft drop")
    print("  SPACE      - Hard drop (instant)")
    print("  C          - Hold piece")
    print("  P          - Pause")
    print("  R          - Restart")
    print("\nFeatures:")
    print("  • Next 3 pieces preview")
    print("  • Hold piece mechanic")
    print("  • Progressive levels & speed")
    print("  • ZX Spectrum aesthetic!")
    print("\n" + "="*64 + "\n")
    
    # Create 256×192 display
    matrix = create_matrix(256, 192, 'rgb')
    
    app = TetrisGame()
    app.on_activate()
    
    with KeyboardInput() as input_handler:
        last_update = time.time()
        frame_count = 0
        
        while True:
            # Handle input
            event = input_handler.get_key(timeout=0.001)
            if event:
                if not app.on_event(event):
                    break
            
            # Update at 60 FPS
            current_time = time.time()
            if current_time - last_update >= 1/60:
                frame_count += 1
                app.on_update(current_time - last_update)
                
                if app.dirty:
                    app.render(matrix)
                    matrix.show()
                
                last_update = current_time
    
    print(f"\n{'='*64}")
    print(f"Final Score: {app.score}")
    print(f"Lines Cleared: {app.lines}")
    print(f"Level Reached: {app.level}")
    print(f"High Score: {app.high_score}")
    print(f"{'='*64}\n")
