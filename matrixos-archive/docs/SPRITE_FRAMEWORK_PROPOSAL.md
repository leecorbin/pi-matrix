# Sprite Framework Proposal for MatrixOS

## Overview
Add a lightweight sprite system to MatrixOS to simplify game development, improve testability, and enable optimizations.

## Current Pain Points

1. **Game Code Duplication**: Every game reimplements sprite logic
   - Position tracking
   - Velocity/direction
   - Collision detection
   - Bounding boxes
   - Animation state

2. **Testing Difficulty**: Hard to verify sprite behavior
   - No standard way to check if sprite is in valid position
   - Can't easily detect wall collisions
   - Manual color-based sprite finding is fragile

3. **Debugging Challenges**: When sprites overlap walls or each other
   - No built-in collision visualization
   - Hard to validate spawn points
   - Difficult to trace movement issues

## Proposed Architecture

### Core Sprite Class

```python
from matrixos.sprites import Sprite, SpriteGroup

class Sprite:
    """Base sprite class with position, velocity, and collision detection."""
    
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.velocity_x = 0
        self.velocity_y = 0
        self.visible = True
        self.collision_layer = 0  # For collision filtering
        
    def rect(self):
        """Return bounding rectangle (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)
    
    def center(self):
        """Return center point (cx, cy)."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def update(self, delta_time):
        """Update sprite state. Override in subclasses."""
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
    
    def render(self, matrix):
        """Draw sprite. Override for custom rendering."""
        if self.visible:
            matrix.rect(int(self.x), int(self.y), 
                       self.width, self.height, 
                       self.color, fill=True)
    
    def collides_with(self, other):
        """Check collision with another sprite."""
        return self._rect_overlap(self.rect(), other.rect())
    
    def collides_with_point(self, px, py):
        """Check if point is inside sprite."""
        return (self.x <= px < self.x + self.width and
                self.y <= py < self.y + self.height)
    
    @staticmethod
    def _rect_overlap(r1, r2):
        """Check if two rectangles overlap."""
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or
                   y1 + h1 <= y2 or y2 + h2 <= y1)
```

### Sprite Group for Management

```python
class SpriteGroup:
    """Collection of sprites with batch operations."""
    
    def __init__(self):
        self.sprites = []
    
    def add(self, sprite):
        """Add sprite to group."""
        self.sprites.append(sprite)
    
    def remove(self, sprite):
        """Remove sprite from group."""
        self.sprites.remove(sprite)
    
    def update(self, delta_time):
        """Update all sprites."""
        for sprite in self.sprites:
            sprite.update(delta_time)
    
    def render(self, matrix):
        """Render all sprites."""
        for sprite in self.sprites:
            sprite.render(matrix)
    
    def check_collisions(self, sprite):
        """Return list of sprites colliding with given sprite."""
        collisions = []
        for other in self.sprites:
            if other != sprite and sprite.collides_with(other):
                collisions.append(other)
        return collisions
    
    def find_by_color(self, color, tolerance=10):
        """Find sprites by color (for testing)."""
        matches = []
        for sprite in self.sprites:
            if self._color_match(sprite.color, color, tolerance):
                matches.append(sprite)
        return matches
    
    @staticmethod
    def _color_match(c1, c2, tolerance):
        """Check if colors match within tolerance."""
        return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))
```

### TileMap for Grid-Based Games

```python
class TileMap:
    """Grid-based tile map for maze games like Pac-Man."""
    
    def __init__(self, width, height, tile_size=8):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.grid_width = width // tile_size
        self.grid_height = height // tile_size
        self.tiles = [[0 for _ in range(self.grid_width)] 
                      for _ in range(self.grid_height)]
        self.tile_colors = {}  # tile_id -> color
    
    def set_tile(self, grid_x, grid_y, tile_id):
        """Set tile at grid position."""
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            self.tiles[grid_y][grid_x] = tile_id
    
    def get_tile(self, grid_x, grid_y):
        """Get tile at grid position."""
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            return self.tiles[grid_y][grid_x]
        return None
    
    def pixel_to_grid(self, x, y):
        """Convert pixel coordinates to grid coordinates."""
        return (x // self.tile_size, y // self.tile_size)
    
    def grid_to_pixel(self, grid_x, grid_y):
        """Convert grid coordinates to pixel coordinates (top-left)."""
        return (grid_x * self.tile_size, grid_y * self.tile_size)
    
    def is_walkable(self, x, y):
        """Check if pixel position is walkable (not a wall)."""
        gx, gy = self.pixel_to_grid(x, y)
        tile = self.get_tile(gx, gy)
        return tile != 1  # Assume 1 = wall
    
    def sprite_collides_with_tiles(self, sprite, tile_ids):
        """Check if sprite overlaps any tiles with given IDs."""
        # Check corners and center of sprite
        positions = [
            (sprite.x, sprite.y),  # Top-left
            (sprite.x + sprite.width, sprite.y),  # Top-right
            (sprite.x, sprite.y + sprite.height),  # Bottom-left
            (sprite.x + sprite.width, sprite.y + sprite.height),  # Bottom-right
            (sprite.x + sprite.width // 2, sprite.y + sprite.height // 2),  # Center
        ]
        
        for x, y in positions:
            gx, gy = self.pixel_to_grid(x, y)
            tile = self.get_tile(gx, gy)
            if tile in tile_ids:
                return True
        return False
    
    def render(self, matrix):
        """Render tilemap."""
        for gy in range(self.grid_height):
            for gx in range(self.grid_width):
                tile_id = self.tiles[gy][gx]
                if tile_id in self.tile_colors:
                    x, y = self.grid_to_pixel(gx, gy)
                    matrix.rect(x, y, self.tile_size, self.tile_size,
                              self.tile_colors[tile_id], fill=True)
```

## Usage Example: Pac-Man Refactored

```python
from matrixos.app_framework import App
from matrixos.sprites import Sprite, SpriteGroup, TileMap
from matrixos.input import InputEvent

class PacMan(Sprite):
    """Pac-Man sprite with game-specific behavior."""
    
    def __init__(self, x, y):
        super().__init__(x, y, 6, 6, (255, 255, 0))
        self.speed = 50  # pixels per second
        self.next_direction = (0, 0)
    
    def set_direction(self, dx, dy):
        """Queue direction change."""
        self.next_direction = (dx, dy)
    
    def update(self, delta_time, tilemap):
        """Update with wall collision checking."""
        # Try to apply queued direction
        if self.next_direction != (0, 0):
            test_x = self.x + self.next_direction[0] * self.speed * delta_time
            test_y = self.y + self.next_direction[1] * self.speed * delta_time
            
            # Check if new position is walkable
            if tilemap.is_walkable(test_x + self.width // 2, 
                                  test_y + self.height // 2):
                self.velocity_x = self.next_direction[0] * self.speed
                self.velocity_y = self.next_direction[1] * self.speed
                self.next_direction = (0, 0)
        
        # Move with current velocity
        new_x = self.x + self.velocity_x * delta_time
        new_y = self.y + self.velocity_y * delta_time
        
        # Check wall collision
        if tilemap.is_walkable(new_x + self.width // 2, 
                              new_y + self.height // 2):
            self.x = new_x
            self.y = new_y
        else:
            # Hit wall, stop moving
            self.velocity_x = 0
            self.velocity_y = 0

class PacManGame(App):
    def __init__(self):
        super().__init__("Pac-Man")
        
        # Create tilemap
        self.tilemap = TileMap(128, 128, tile_size=8)
        self.tilemap.tile_colors = {
            0: (0, 0, 0),      # Empty
            1: (0, 0, 255),    # Wall
            2: (255, 255, 255) # Dot
        }
        self._init_maze()
        
        # Create sprites
        self.pacman = PacMan(64, 64)
        self.ghosts = SpriteGroup()
        # Add ghosts...
        
        self.dirty = True
    
    def on_event(self, event):
        if event.key == InputEvent.UP:
            self.pacman.set_direction(0, -1)
        elif event.key == InputEvent.DOWN:
            self.pacman.set_direction(0, 1)
        elif event.key == InputEvent.LEFT:
            self.pacman.set_direction(-1, 0)
        elif event.key == InputEvent.RIGHT:
            self.pacman.set_direction(1, 0)
        self.dirty = True
        return True
    
    def on_update(self, delta_time):
        self.pacman.update(delta_time, self.tilemap)
        self.ghosts.update(delta_time)
        
        # Check collisions
        if self.ghosts.check_collisions(self.pacman):
            self.game_over = True
        
        self.dirty = True
    
    def render(self, matrix):
        matrix.clear()
        self.tilemap.render(matrix)
        self.pacman.render(matrix)
        self.ghosts.render(matrix)
        self.dirty = False
```

## Testing Benefits

```python
from matrixos.testing import TestRunner

def test_pacman_wall_collision():
    """Test that Pac-Man can't move through walls."""
    runner = TestRunner("examples.pacman.main", max_duration=10.0)
    runner.wait(1.0)
    
    # Access game instance
    game = runner.app
    
    # Check initial position is valid
    assert not game.tilemap.sprite_collides_with_tiles(game.pacman, [1]), \
        "Pac-Man spawns inside wall!"
    
    # Try to move into wall
    wall_tile = find_wall_tile(game.tilemap)
    game.pacman.x, game.pacman.y = game.tilemap.grid_to_pixel(*wall_tile)
    
    runner.wait(1.0)
    
    # Verify Pac-Man didn't move into wall
    assert not game.tilemap.sprite_collides_with_tiles(game.pacman, [1]), \
        "Pac-Man moved through wall!"

def test_ghost_positions():
    """Test that all ghosts spawn in valid positions."""
    runner = TestRunner("examples.pacman.main", max_duration=10.0)
    runner.wait(1.0)
    
    game = runner.app
    
    for ghost in game.ghosts.sprites:
        assert not game.tilemap.sprite_collides_with_tiles(ghost, [1]), \
            f"Ghost at ({ghost.x}, {ghost.y}) spawns inside wall!"
```

## Implementation Plan

### Phase 1: Core Sprites (Week 1)
- [ ] Create `matrixos/sprites.py` with Sprite and SpriteGroup
- [ ] Add unit tests for sprite collision detection
- [ ] Update docs/API_REFERENCE.md with sprite API

### Phase 2: TileMap System (Week 1)
- [ ] Add TileMap class to sprites.py
- [ ] Create maze loading utilities
- [ ] Add tilemap rendering tests

### Phase 3: Testing Integration (Week 2)
- [ ] Add sprite accessors to TestRunner
- [ ] Create collision detection helpers for tests
- [ ] Update docs/TESTING.md with sprite testing patterns

### Phase 4: Game Migration (Week 2-3)
- [ ] Refactor Pac-Man to use sprite system
- [ ] Refactor Snake to use sprite system
- [ ] Refactor Platformer to use sprite system
- [ ] Measure performance improvements

### Phase 5: Advanced Features (Week 4)
- [ ] Add sprite animation support
- [ ] Add sprite pooling for performance
- [ ] Add collision masks for complex shapes
- [ ] Add debug visualization mode

## Benefits

1. **Cleaner Game Code**: 50-70% less boilerplate
2. **Better Testing**: Direct access to sprite state and positions
3. **Easier Debugging**: Built-in collision visualization
4. **Performance**: Spatial partitioning for large sprite counts
5. **Consistency**: All games use same patterns
6. **Documentation**: Single place to document game development

## Open Questions

1. Should sprites auto-register with matrix for rendering?
2. Need physics simulation (gravity, acceleration)?
3. Support for sprite sheets / animations?
4. Collision layers vs collision groups?
5. Integration with existing emoji icon system?

## Conclusion

A sprite framework would significantly improve MatrixOS game development while maintaining the "pure Python" philosophy. It addresses real pain points discovered through testing and makes the testing framework even more powerful.

**Recommendation**: Start with Phase 1-2 to get core functionality, test with Pac-Man refactor, then expand based on learnings.
