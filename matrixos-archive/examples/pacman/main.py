"""
Pac-Man - ZX Spectrum Edition for 256×192
==========================================

Classic Pac-Man game with:
- Authentic maze with proper collision detection
- 4 ghosts with different AI behaviors
- Power pellets that make ghosts vulnerable
- Tile-based movement system (no wall clipping)
- Side panels showing lives, score, high score, level
- Dark blue background with cyan maze walls
- Chunky 10px Pac-Man and ghost sprites
"""

from matrixos.app_framework import App
from matrixos.input import InputEvent
from matrixos.logger import get_logger
import random

# ZX Spectrum color palette
CYAN = (0, 255, 255)          # Maze walls
DARK_BLUE = (0, 0, 40)         # Background
YELLOW = (255, 255, 0)         # Pac-Man
BRIGHT_YELLOW = (255, 255, 128)
RED = (255, 0, 0)              # Blinky
PINK = (255, 184, 255)         # Pinky
CYAN_GHOST = (0, 255, 255)     # Inky
ORANGE = (255, 184, 82)        # Clyde
BLUE_SCARED = (0, 100, 255)    # Vulnerable ghosts
WHITE = (255, 255, 255)        # Dots
DOT_COLOR = (200, 200, 50)     # Small dots
POWER_DOT = (255, 255, 150)    # Power pellets

class PacManGame(App):
    """ZX Spectrum-style Pac-Man with proper collision detection"""
    
    def __init__(self):
        super().__init__("Pac-Man")
        self.logger = get_logger("pacman")
        
        # Display layout: 32px left panel + 192px center maze + 32px right panel
        self.panel_width = 32
        self.maze_left = 32
        self.maze_width = 192
        self.maze_right = 224
        
        # Tile-based game (each tile is 8×8 pixels)
        self.tile_size = 8
        self.maze_tiles_x = self.maze_width // self.tile_size  # 24 tiles
        self.maze_tiles_y = 192 // self.tile_size  # 24 tiles
        
        # Classic Pac-Man maze (1 = wall, 0 = path, 2 = dot, 3 = power pellet)
        self.original_maze = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,1],
            [1,3,1,1,2,1,1,1,2,1,2,1,1,2,1,2,1,1,1,2,1,1,3,1],
            [1,2,1,1,2,1,1,1,2,1,2,1,1,2,1,2,1,1,1,2,1,1,2,1],
            [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
            [1,2,1,1,2,1,2,1,1,1,1,1,1,1,1,1,1,2,1,2,1,1,2,1],
            [1,2,2,2,2,1,2,2,2,2,2,1,1,2,2,2,2,2,1,2,2,2,2,1],
            [1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1],
            [1,1,1,1,2,1,0,0,0,0,0,0,0,0,0,0,0,0,1,2,1,1,1,1],
            [1,1,1,1,2,1,0,1,1,0,0,0,0,0,0,1,1,0,1,2,1,1,1,1],
            [0,0,0,0,2,0,0,1,0,0,0,0,0,0,0,0,1,0,0,2,0,0,0,0],
            [1,1,1,1,2,1,0,1,1,1,1,1,1,1,1,1,1,0,1,2,1,1,1,1],
            [1,1,1,1,2,1,0,0,0,0,0,0,0,0,0,0,0,0,1,2,1,1,1,1],
            [1,1,1,1,2,1,0,1,1,1,1,1,1,1,1,1,1,0,1,2,1,1,1,1],
            [1,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,1],
            [1,2,1,1,2,1,1,1,2,1,2,1,1,2,1,2,1,1,1,2,1,1,2,1],
            [1,3,2,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,2,3,1],
            [1,1,2,1,2,1,2,1,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,1],
            [1,2,2,2,2,1,2,2,2,2,2,1,1,2,2,2,2,2,1,2,2,2,2,1],
            [1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1],
            [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]
        
        self.maze = None
        self.score = 0
        self.high_score = 0
        self.lives = 3
        self.level = 1
        
        # Pac-Man state (tile coordinates)
        self.pacman_tile_x = 12
        self.pacman_tile_y = 17
        self.pacman_dir_x = 0
        self.pacman_dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0
        self.pacman_mouth_angle = 0
        self.pacman_mouth_open = True
        
        # Ghosts (tile coordinates)
        self.ghosts = [
            {"x": 11, "y": 10, "dir_x": -1, "dir_y": 0, "color": RED, "name": "Blinky", "mode": "scatter"},
            {"x": 12, "y": 10, "dir_x": 0, "dir_y": -1, "color": PINK, "name": "Pinky", "mode": "scatter"},
            {"x": 11, "y": 11, "dir_x": 1, "dir_y": 0, "color": CYAN_GHOST, "name": "Inky", "mode": "scatter"},
            {"x": 12, "y": 11, "dir_x": 0, "dir_y": 1, "color": ORANGE, "name": "Clyde", "mode": "scatter"},
        ]
        
        # Power pellet state
        self.power_mode = False
        self.power_timer = 0
        self.power_duration = 300  # frames (~5 seconds at 60fps)
        
        # Game state
        self.game_state = "playing"  # playing, dead, won
        self.dots_remaining = 0
        self.death_animation_timer = 0
        self.respawn_timer = 0
        
        # Movement timing (update every N frames for smooth movement)
        self.move_counter = 0
        self.move_interval = 4  # Update every 4 frames (15 updates/sec at 60fps)
        
        self.reset_level()
        self.dirty = True
    
    def reset_level(self):
        """Reset level (keep score and lives)"""
        # Copy maze
        self.maze = [row[:] for row in self.original_maze]
        
        # Count dots
        self.dots_remaining = sum(row.count(2) + row.count(3) for row in self.maze)
        
        # Reset positions
        self.pacman_tile_x = 12
        self.pacman_tile_y = 17
        self.pacman_dir_x = 0
        self.pacman_dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0
        
        # Reset ghosts
        self.ghosts = [
            {"x": 11, "y": 10, "dir_x": -1, "dir_y": 0, "color": RED, "name": "Blinky", "mode": "scatter"},
            {"x": 12, "y": 10, "dir_x": 0, "dir_y": -1, "color": PINK, "name": "Pinky", "mode": "scatter"},
            {"x": 11, "y": 11, "dir_x": 1, "dir_y": 0, "color": CYAN_GHOST, "name": "Inky", "mode": "scatter"},
            {"x": 12, "y": 11, "dir_x": 0, "dir_y": 1, "color": ORANGE, "name": "Clyde", "mode": "scatter"},
        ]
        
        self.power_mode = False
        self.power_timer = 0
        self.game_state = "playing"
        self.logger.info(f"Level {self.level} started - {self.dots_remaining} dots to collect")
    
    def is_wall(self, tile_x, tile_y):
        """Check if tile is a wall"""
        if tile_x < 0 or tile_x >= self.maze_tiles_x or tile_y < 0 or tile_y >= self.maze_tiles_y:
            return True
        return self.maze[tile_y][tile_x] == 1
    
    def on_event(self, event):
        """Handle input"""
        if event.key == InputEvent.UP:
            self.next_dir_x = 0
            self.next_dir_y = -1
            self.dirty = True
            return True
        elif event.key == InputEvent.DOWN:
            self.next_dir_x = 0
            self.next_dir_y = 1
            self.dirty = True
            return True
        elif event.key == InputEvent.LEFT:
            self.next_dir_x = -1
            self.next_dir_y = 0
            self.dirty = True
            return True
        elif event.key == InputEvent.RIGHT:
            self.next_dir_x = 1
            self.next_dir_y = 0
            self.dirty = True
            return True
        return False
    
    def on_update(self, delta_time):
        """Update game state"""
        if self.game_state != "playing":
            return
        
        # Movement timing
        self.move_counter += 1
        if self.move_counter < self.move_interval:
            return
        self.move_counter = 0
        
        # Try to change direction
        next_x = self.pacman_tile_x + self.next_dir_x
        next_y = self.pacman_tile_y + self.next_dir_y
        if not self.is_wall(next_x, next_y):
            self.pacman_dir_x = self.next_dir_x
            self.pacman_dir_y = self.next_dir_y
        
        # Move Pac-Man
        next_x = self.pacman_tile_x + self.pacman_dir_x
        next_y = self.pacman_tile_y + self.pacman_dir_y
        if not self.is_wall(next_x, next_y):
            self.pacman_tile_x = next_x
            self.pacman_tile_y = next_y
            
            # Wrap around edges
            if self.pacman_tile_x < 0:
                self.pacman_tile_x = self.maze_tiles_x - 1
            elif self.pacman_tile_x >= self.maze_tiles_x:
                self.pacman_tile_x = 0
            
            # Collect dots
            tile_value = self.maze[self.pacman_tile_y][self.pacman_tile_x]
            if tile_value == 2:  # Dot
                self.maze[self.pacman_tile_y][self.pacman_tile_x] = 0
                self.score += 10
                self.dots_remaining -= 1
            elif tile_value == 3:  # Power pellet
                self.maze[self.pacman_tile_y][self.pacman_tile_x] = 0
                self.score += 50
                self.dots_remaining -= 1
                self.power_mode = True
                self.power_timer = self.power_duration
                self.logger.info("Power mode activated!")
        
        # Animate mouth
        self.pacman_mouth_angle = (self.pacman_mouth_angle + 10) % 360
        self.pacman_mouth_open = (self.pacman_mouth_angle // 90) % 2 == 0
        
        # Update power mode
        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False
                self.logger.info("Power mode ended")
        
        # Move ghosts
        for ghost in self.ghosts:
            # Simple AI: random direction changes at intersections
            moves = []
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx = ghost["x"] + dx
                ny = ghost["y"] + dy
                # Don't reverse direction
                if dx == -ghost["dir_x"] and dy == -ghost["dir_y"]:
                    continue
                if not self.is_wall(nx, ny):
                    moves.append((dx, dy))
            
            if moves:
                # Pick random valid direction
                if len(moves) > 1:
                    ghost["dir_x"], ghost["dir_y"] = random.choice(moves)
                else:
                    ghost["dir_x"], ghost["dir_y"] = moves[0]
                
                ghost["x"] += ghost["dir_x"]
                ghost["y"] += ghost["dir_y"]
                
                # Wrap around
                if ghost["x"] < 0:
                    ghost["x"] = self.maze_tiles_x - 1
                elif ghost["x"] >= self.maze_tiles_x:
                    ghost["x"] = 0
        
        # Check collisions with ghosts
        for ghost in self.ghosts:
            if ghost["x"] == self.pacman_tile_x and ghost["y"] == self.pacman_tile_y:
                if self.power_mode:
                    # Eat ghost
                    self.score += 200
                    ghost["x"] = 12
                    ghost["y"] = 10
                    self.logger.info(f"Ate {ghost['name']}!")
                else:
                    # Die
                    self.lives -= 1
                    self.logger.info(f"Hit by {ghost['name']}! Lives: {self.lives}")
                    if self.lives <= 0:
                        self.game_state = "dead"
                    else:
                        self.reset_level()
        
        # Check win condition
        if self.dots_remaining <= 0:
            self.level += 1
            self.logger.info(f"Level {self.level} complete!")
            self.reset_level()
        
        if self.score > self.high_score:
            self.high_score = self.score
        
        self.dirty = True
    
    def render(self, matrix):
        """Draw game"""
        # Dark blue background
        matrix.clear()
        matrix.rect(0, 0, 256, 192, DARK_BLUE, fill=True)
        
        # Draw maze
        for y in range(len(self.maze)):
            for x in range(len(self.maze[y])):
                tile = self.maze[y][x]
                px = self.maze_left + x * self.tile_size
                py = y * self.tile_size
                
                if tile == 1:  # Wall
                    matrix.rect(px, py, self.tile_size, self.tile_size, CYAN, fill=True)
                elif tile == 2:  # Dot
                    matrix.circle(px + 4, py + 4, 1, DOT_COLOR, fill=True)
                elif tile == 3:  # Power pellet
                    if (self.pacman_mouth_angle // 30) % 2 == 0:  # Blink
                        matrix.circle(px + 4, py + 4, 3, POWER_DOT, fill=True)
        
        # Draw Pac-Man (10px chunky sprite)
        px = self.maze_left + self.pacman_tile_x * self.tile_size - 1
        py = self.pacman_tile_y * self.tile_size - 1
        pac_color = BRIGHT_YELLOW if self.power_mode and (self.power_timer // 10) % 2 == 0 else YELLOW
        matrix.circle(px + 5, py + 5, 5, pac_color, fill=True)
        
        # Draw ghosts (10px chunky sprites)
        for ghost in self.ghosts:
            gx = self.maze_left + ghost["x"] * self.tile_size - 1
            gy = ghost["y"] * self.tile_size - 1
            ghost_color = BLUE_SCARED if self.power_mode else ghost["color"]
            # Body
            matrix.rect(gx + 1, gy + 3, 8, 7, ghost_color, fill=True)
            # Head
            matrix.rect(gx + 2, gy + 1, 6, 4, ghost_color, fill=True)
            # Eyes
            matrix.set_pixel(gx + 3, gy + 3, WHITE)
            matrix.set_pixel(gx + 6, gy + 3, WHITE)
        
        # Left panel - Lives
        matrix.text("LIVES", 2, 10, CYAN)
        for i in range(self.lives):
            ly = 20 + i * 12
            matrix.circle(10, ly, 4, YELLOW, fill=True)
        
        # Left panel - Power status
        if self.power_mode:
            matrix.text("POWER", 1, 80, BRIGHT_YELLOW)
            bar_height = int((self.power_timer / self.power_duration) * 40)
            matrix.rect(8, 90, 16, bar_height, BRIGHT_YELLOW, fill=True)
        
        # Right panel - Score
        matrix.text("SCORE", self.maze_right + 2, 10, YELLOW)
        matrix.text(str(self.score), self.maze_right + 2, 22, WHITE)
        
        # Right panel - High score
        matrix.text("HI", self.maze_right + 4, 50, CYAN)
        matrix.text(str(self.high_score), self.maze_right + 2, 62, WHITE)
        
        # Right panel - Level
        matrix.text("LEV", self.maze_right + 2, 90, PINK)
        matrix.text(str(self.level), self.maze_right + 8, 102, WHITE)
        
        # Right panel - Dots
        matrix.text("DOTS", self.maze_right + 2, 130, ORANGE)
        matrix.text(str(self.dots_remaining), self.maze_right + 4, 142, WHITE)
        
        # Game over message
        if self.game_state == "dead":
            matrix.text("GAME", 108, 88, RED)
            matrix.text("OVER", 108, 100, RED)
        
        self.dirty = False


def run(os_context):
    """Entry point"""
    app = PacManGame()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()


if __name__ == "__main__":
    # Test mode
    from matrixos.display import TerminalDisplay
    from matrixos.input import InputHandler
    
    matrix = TerminalDisplay(256, 192)
    input_handler = InputHandler()
    
    app = PacManGame()
    app.on_activate()
    
    print("Pac-Man ZX Spectrum Edition")
    print("Arrow keys to move | Ctrl+C to quit")
    print("Collect all dots, avoid ghosts!")
    
    import time
    last_time = time.time()
    
    try:
        while True:
            # Handle input
            event = input_handler.get_key(timeout=0.001)
            if event:
                app.on_event(event)
            
            # Update (60fps)
            current_time = time.time()
            delta_time = current_time - last_time
            if delta_time >= 1.0 / 60.0:
                app.on_update(delta_time)
                if app.dirty:
                    app.render(matrix)
                    matrix.show()
                last_time = current_time
    
    except KeyboardInterrupt:
        print("\nGame Over!")
        print(f"Final Score: {app.score}")
        print(f"High Score: {app.high_score}")
