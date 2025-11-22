#!/usr/bin/env python3
"""
MatrixOS Sprite Framework

Provides sprite classes for game development with built-in collision detection,
animation support, and testing integration.

Philosophy:
- Pure Python (no numpy, pygame, etc.)
- Simple and fast for LED matrix games
- Built-in collision detection
- Easy testing integration
- Emoji sprite support

Usage:
    from matrixos.sprites import Sprite, SpriteGroup, TileMap
    
    # Create sprites
    player = Sprite(x=64, y=64, width=8, height=8, color=(255, 0, 0))
    
    # Organize in groups
    enemies = SpriteGroup()
    enemies.add(Sprite(x=100, y=50, width=8, height=8, color=(0, 255, 0)))
    
    # Check collisions
    if player.collides_with(enemy):
        game_over()
"""

import math
from matrixos.logger import get_logger

logger = get_logger("sprites")


# ============================================================================
# Collision Detection Utilities
# ============================================================================

def rect_overlap(r1, r2):
    """
    Check if two rectangles overlap.
    
    Args:
        r1: Tuple (x, y, width, height)
        r2: Tuple (x, y, width, height)
    
    Returns:
        bool: True if rectangles overlap
    
    Example:
        >>> rect_overlap((0, 0, 10, 10), (5, 5, 10, 10))
        True
        >>> rect_overlap((0, 0, 10, 10), (20, 20, 10, 10))
        False
    """
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    
    # Rectangles don't overlap if one is completely to the side of the other
    if x1 + w1 <= x2 or x2 + w2 <= x1:
        return False
    if y1 + h1 <= y2 or y2 + h2 <= y1:
        return False
    
    return True


def point_in_rect(px, py, rect):
    """
    Check if point is inside rectangle.
    
    Args:
        px: Point x coordinate
        py: Point y coordinate
        rect: Tuple (x, y, width, height)
    
    Returns:
        bool: True if point is inside rectangle
    
    Example:
        >>> point_in_rect(5, 5, (0, 0, 10, 10))
        True
        >>> point_in_rect(15, 15, (0, 0, 10, 10))
        False
    """
    x, y, w, h = rect
    return x <= px < x + w and y <= py < y + h


def distance(x1, y1, x2, y2):
    """
    Calculate distance between two points.
    
    Args:
        x1, y1: First point coordinates
        x2, y2: Second point coordinates
    
    Returns:
        float: Distance between points
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


# ============================================================================
# Base Sprite Class
# ============================================================================

class Sprite:
    """
    Base sprite class with position, velocity, and collision detection.
    
    Sprites are rectangular game objects that can move, render, and detect
    collisions with other sprites or tiles.
    
    Attributes:
        x (float): X position (top-left corner)
        y (float): Y position (top-left corner)
        width (int): Sprite width in pixels
        height (int): Sprite height in pixels
        color (tuple): RGB color (r, g, b) for default rendering
        velocity_x (float): Horizontal velocity (pixels per second)
        velocity_y (float): Vertical velocity (pixels per second)
        visible (bool): Whether sprite should be rendered
        collision_layer (int): Collision layer for filtering (default: 0)
        tags (set): Set of string tags for identification
    
    Example:
        # Create a simple sprite
        player = Sprite(x=64, y=64, width=12, height=12, color=(255, 255, 0))
        
        # Set velocity
        player.velocity_x = 50  # 50 pixels per second
        
        # Update (in game loop with delta_time)
        player.update(delta_time)
        
        # Render
        player.render(matrix)
        
        # Check collision
        if player.collides_with(enemy):
            print("Hit!")
    """
    
    def __init__(self, x, y, width, height, color=(255, 255, 255)):
        """
        Initialize sprite.
        
        Args:
            x: Initial x position (pixels)
            y: Initial y position (pixels)
            width: Sprite width (pixels)
            height: Sprite height (pixels)
            color: RGB color tuple (default: white)
        """
        self.x = float(x)
        self.y = float(y)
        self.width = int(width)
        self.height = int(height)
        self.color = color
        
        # Movement
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # State
        self.visible = True
        self.collision_layer = 0
        self.tags = set()
        
        # Optional name for debugging
        self.name = None
    
    def rect(self):
        """
        Get bounding rectangle.
        
        Returns:
            tuple: (x, y, width, height)
        """
        return (self.x, self.y, self.width, self.height)
    
    def center(self):
        """
        Get center point.
        
        Returns:
            tuple: (center_x, center_y)
        """
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    def set_center(self, cx, cy):
        """
        Set position by center point.
        
        Args:
            cx: Center x coordinate
            cy: Center y coordinate
        """
        self.x = cx - self.width / 2
        self.y = cy - self.height / 2
    
    def update(self, delta_time):
        """
        Update sprite state.
        
        Default behavior: Apply velocity to position.
        Override this in subclasses for custom logic.
        
        Args:
            delta_time: Time since last update in seconds
        """
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
    
    def render(self, matrix):
        """
        Render sprite to matrix.
        
        Default behavior: Draw filled rectangle.
        Override this in subclasses for custom rendering.
        
        Args:
            matrix: LED matrix to draw on
        """
        if self.visible:
            matrix.rect(
                int(self.x), int(self.y),
                self.width, self.height,
                self.color,
                fill=True
            )
    
    def collides_with(self, other):
        """
        Check collision with another sprite.
        
        Args:
            other: Another Sprite instance
        
        Returns:
            bool: True if sprites overlap
        """
        return rect_overlap(self.rect(), other.rect())
    
    def collides_with_point(self, px, py):
        """
        Check if point is inside sprite.
        
        Args:
            px: Point x coordinate
            py: Point y coordinate
        
        Returns:
            bool: True if point is inside sprite
        """
        return point_in_rect(px, py, self.rect())
    
    def distance_to(self, other):
        """
        Calculate distance to another sprite (center to center).
        
        Args:
            other: Another Sprite instance
        
        Returns:
            float: Distance in pixels
        """
        cx1, cy1 = self.center()
        cx2, cy2 = other.center()
        return distance(cx1, cy1, cx2, cy2)
    
    def add_tag(self, tag):
        """Add a tag for identification."""
        self.tags.add(tag)
    
    def has_tag(self, tag):
        """Check if sprite has tag."""
        return tag in self.tags
    
    def __repr__(self):
        """String representation for debugging."""
        name = self.name or self.__class__.__name__
        return f"{name}(x={self.x:.1f}, y={self.y:.1f}, {self.width}×{self.height})"


# ============================================================================
# Sprite Group
# ============================================================================

class SpriteGroup:
    """
    Collection of sprites with batch operations.
    
    Groups make it easy to manage multiple sprites, update them all at once,
    render them together, and check collisions.
    
    Example:
        enemies = SpriteGroup()
        enemies.add(Ghost(x=10, y=20))
        enemies.add(Ghost(x=30, y=40))
        
        # Update all enemies
        enemies.update(delta_time)
        
        # Render all enemies
        enemies.render(matrix)
        
        # Check player collision with any enemy
        for enemy in enemies.check_collisions(player):
            print(f"Hit {enemy}!")
    """
    
    def __init__(self, *sprites):
        """
        Initialize sprite group.
        
        Args:
            *sprites: Optional initial sprites to add
        """
        self.sprites = list(sprites)
    
    def add(self, sprite):
        """
        Add sprite to group.
        
        Args:
            sprite: Sprite instance to add
        """
        if sprite not in self.sprites:
            self.sprites.append(sprite)
    
    def remove(self, sprite):
        """
        Remove sprite from group.
        
        Args:
            sprite: Sprite instance to remove
        """
        if sprite in self.sprites:
            self.sprites.remove(sprite)
    
    def clear(self):
        """Remove all sprites from group."""
        self.sprites.clear()
    
    def update(self, delta_time):
        """
        Update all sprites in group.
        
        Args:
            delta_time: Time since last update in seconds
        """
        for sprite in self.sprites:
            sprite.update(delta_time)
    
    def render(self, matrix):
        """
        Render all sprites in group.
        
        Args:
            matrix: LED matrix to draw on
        """
        for sprite in self.sprites:
            sprite.render(matrix)
    
    def check_collisions(self, sprite):
        """
        Find all sprites in group that collide with given sprite.
        
        Args:
            sprite: Sprite to check against
        
        Returns:
            list: List of colliding sprites
        """
        collisions = []
        for other in self.sprites:
            if other != sprite and sprite.collides_with(other):
                collisions.append(other)
        return collisions
    
    def check_group_collisions(self, other_group):
        """
        Find all collision pairs between this group and another.
        
        Args:
            other_group: Another SpriteGroup
        
        Returns:
            list: List of (sprite1, sprite2) collision pairs
        """
        collisions = []
        for sprite1 in self.sprites:
            for sprite2 in other_group.sprites:
                if sprite1.collides_with(sprite2):
                    collisions.append((sprite1, sprite2))
        return collisions
    
    def find_by_tag(self, tag):
        """
        Find all sprites with given tag.
        
        Args:
            tag: Tag string to search for
        
        Returns:
            list: Sprites with matching tag
        """
        return [s for s in self.sprites if s.has_tag(tag)]
    
    def find_by_color(self, color, tolerance=10):
        """
        Find sprites by color (for testing).
        
        Args:
            color: RGB tuple to match
            tolerance: Max difference per channel
        
        Returns:
            list: Sprites with matching color
        """
        matches = []
        for sprite in self.sprites:
            if sprite.color and self._color_match(sprite.color, color, tolerance):
                matches.append(sprite)
        return matches
    
    @staticmethod
    def _color_match(c1, c2, tolerance):
        """Check if colors match within tolerance."""
        return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))
    
    def __len__(self):
        """Return number of sprites in group."""
        return len(self.sprites)
    
    def __iter__(self):
        """Iterate over sprites."""
        return iter(self.sprites)
    
    def __repr__(self):
        """String representation for debugging."""
        return f"SpriteGroup({len(self.sprites)} sprites)"


# ============================================================================
# TileMap System
# ============================================================================

class TileMap:
    """
    Grid-based tile system for maze-based games.
    
    TileMap manages a 2D grid of tiles, handles coordinate conversion between
    pixel space and grid space, and provides collision detection between
    sprites and tiles.
    
    Perfect for games like Pac-Man, Frogger, or any grid-based game.
    
    Attributes:
        width (int): Grid width in tiles
        height (int): Grid height in tiles
        tile_size (int): Size of each tile in pixels
        tiles (list): 2D list of tile IDs [row][col]
        tile_colors (dict): Mapping from tile ID to RGB color
    
    Example:
        # Create 10×10 tile map with 8×8 pixel tiles
        tilemap = TileMap(width=10, height=10, tile_size=8)
        
        # Set tiles (0=empty, 1=wall)
        tilemap.set_tile(5, 5, 1)  # Wall at grid (5, 5)
        
        # Check sprite collision with walls
        player = Sprite(x=40, y=40, width=8, height=8)
        if tilemap.sprite_collides_with_tile(player, tile_id=1):
            print("Hit wall!")
        
        # Load maze from ASCII
        maze = \"\"\"
        ##########
        #........#
        #.##..##.#
        ##########
        \"\"\"
        tilemap.load_from_ascii(maze, {'#': 1, '.': 0})
    """
    
    def __init__(self, width, height, tile_size=8):
        """
        Initialize tile map.
        
        Args:
            width: Grid width in tiles
            height: Grid height in tiles
            tile_size: Size of each tile in pixels (default: 8)
        """
        self.width = int(width)
        self.height = int(height)
        self.tile_size = int(tile_size)
        
        # Create empty grid (all zeros)
        self.tiles = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Tile rendering colors (tile_id -> RGB color)
        self.tile_colors = {
            0: (0, 0, 0),        # Empty/black
            1: (33, 33, 222),    # Wall/blue (Pac-Man style)
            2: (255, 200, 150),  # Dot/tan
        }
    
    # ------------------------------------------------------------------------
    # Coordinate Conversion
    # ------------------------------------------------------------------------
    
    def pixel_to_grid(self, x, y):
        """
        Convert pixel coordinates to grid coordinates.
        
        Args:
            x: Pixel x coordinate
            y: Pixel y coordinate
        
        Returns:
            tuple: (col, row) in grid space
        
        Example:
            >>> tilemap = TileMap(10, 10, tile_size=8)
            >>> tilemap.pixel_to_grid(20, 16)
            (2, 2)
        """
        col = int(x // self.tile_size)
        row = int(y // self.tile_size)
        return (col, row)
    
    def grid_to_pixel(self, col, row):
        """
        Convert grid coordinates to pixel coordinates (top-left of tile).
        
        Args:
            col: Grid column
            row: Grid row
        
        Returns:
            tuple: (x, y) in pixel space
        
        Example:
            >>> tilemap = TileMap(10, 10, tile_size=8)
            >>> tilemap.grid_to_pixel(2, 3)
            (16, 24)
        """
        x = col * self.tile_size
        y = row * self.tile_size
        return (x, y)
    
    def grid_to_pixel_center(self, col, row):
        """
        Convert grid coordinates to center of tile in pixel space.
        
        Args:
            col: Grid column
            row: Grid row
        
        Returns:
            tuple: (center_x, center_y) in pixel space
        
        Example:
            >>> tilemap = TileMap(10, 10, tile_size=8)
            >>> tilemap.grid_to_pixel_center(2, 3)
            (20, 28)  # Center of 8×8 tile at grid (2,3)
        """
        x = col * self.tile_size + self.tile_size // 2
        y = row * self.tile_size + self.tile_size // 2
        return (x, y)
    
    # ------------------------------------------------------------------------
    # Tile Access
    # ------------------------------------------------------------------------
    
    def in_bounds(self, col, row):
        """
        Check if grid coordinates are within bounds.
        
        Args:
            col: Grid column
            row: Grid row
        
        Returns:
            bool: True if in bounds
        """
        return 0 <= col < self.width and 0 <= row < self.height
    
    def get_tile(self, col, row):
        """
        Get tile ID at grid position.
        
        Args:
            col: Grid column
            row: Grid row
        
        Returns:
            int: Tile ID, or None if out of bounds
        """
        if self.in_bounds(col, row):
            return self.tiles[row][col]
        return None
    
    def set_tile(self, col, row, tile_id):
        """
        Set tile ID at grid position.
        
        Args:
            col: Grid column
            row: Grid row
            tile_id: Tile ID to set
        
        Returns:
            bool: True if set successfully, False if out of bounds
        """
        if self.in_bounds(col, row):
            self.tiles[row][col] = tile_id
            return True
        return False
    
    def get_tile_at_pixel(self, x, y):
        """
        Get tile ID at pixel coordinates.
        
        Args:
            x: Pixel x coordinate
            y: Pixel y coordinate
        
        Returns:
            int: Tile ID, or None if out of bounds
        """
        col, row = self.pixel_to_grid(x, y)
        return self.get_tile(col, row)
    
    # ------------------------------------------------------------------------
    # Sprite-Tile Collision
    # ------------------------------------------------------------------------
    
    def sprite_collides_with_tile(self, sprite, tile_id):
        """
        Check if sprite overlaps with any tiles of given type.
        
        Args:
            sprite: Sprite instance to check
            tile_id: Tile ID to check against (e.g., 1 for walls)
        
        Returns:
            bool: True if sprite overlaps with tile of given type
        
        Example:
            if tilemap.sprite_collides_with_tile(player, tile_id=1):
                print("Player hit wall!")
        """
        overlapping_tiles = self.get_sprite_tiles(sprite)
        for col, row in overlapping_tiles:
            if self.get_tile(col, row) == tile_id:
                return True
        return False
    
    def sprite_collides_with_tiles(self, sprite, tile_ids):
        """
        Check if sprite overlaps with any tiles in given set.
        
        Args:
            sprite: Sprite instance to check
            tile_ids: List/set of tile IDs to check against
        
        Returns:
            bool: True if sprite overlaps with any tile in set
        """
        overlapping_tiles = self.get_sprite_tiles(sprite)
        tile_set = set(tile_ids)
        for col, row in overlapping_tiles:
            if self.get_tile(col, row) in tile_set:
                return True
        return False
    
    def get_sprite_tiles(self, sprite):
        """
        Get all grid tiles that sprite overlaps.
        
        Args:
            sprite: Sprite instance
        
        Returns:
            list: List of (col, row) tuples for overlapping tiles
        
        Example:
            tiles = tilemap.get_sprite_tiles(player)
            for col, row in tiles:
                print(f"Player overlaps tile ({col}, {row})")
        """
        # Get sprite bounds in pixel space
        x1 = int(sprite.x)
        y1 = int(sprite.y)
        x2 = int(sprite.x + sprite.width - 1)
        y2 = int(sprite.y + sprite.height - 1)
        
        # Convert to grid space
        col1, row1 = self.pixel_to_grid(x1, y1)
        col2, row2 = self.pixel_to_grid(x2, y2)
        
        # Collect all overlapping tiles
        tiles = []
        for row in range(row1, row2 + 1):
            for col in range(col1, col2 + 1):
                if self.in_bounds(col, row):
                    tiles.append((col, row))
        
        return tiles
    
    # ------------------------------------------------------------------------
    # Grid-Aligned Spawn Helpers
    # ------------------------------------------------------------------------
    
    def spawn_at_grid(self, col, row, width, height, color=(255, 255, 255)):
        """
        Create sprite at grid position (top-left aligned).
        
        Args:
            col: Grid column
            row: Grid row
            width: Sprite width in pixels
            height: Sprite height in pixels
            color: RGB color tuple
        
        Returns:
            Sprite: New sprite at grid-aligned position
        
        Example:
            # Spawn player at grid (5, 5)
            player = tilemap.spawn_at_grid(5, 5, width=12, height=12)
        """
        x, y = self.grid_to_pixel(col, row)
        return Sprite(x, y, width, height, color)
    
    def spawn_at_grid_center(self, col, row, width, height, color=(255, 255, 255)):
        """
        Create sprite centered on grid tile.
        
        Args:
            col: Grid column
            row: Grid row
            width: Sprite width in pixels
            height: Sprite height in pixels
            color: RGB color tuple
        
        Returns:
            Sprite: New sprite centered on tile
        
        Example:
            # Spawn ghost centered on grid (10, 5)
            ghost = tilemap.spawn_at_grid_center(10, 5, width=12, height=12)
        """
        cx, cy = self.grid_to_pixel_center(col, row)
        sprite = Sprite(0, 0, width, height, color)
        sprite.set_center(cx, cy)
        return sprite
    
    # ------------------------------------------------------------------------
    # Walkability / Pathfinding Helpers
    # ------------------------------------------------------------------------
    
    def is_walkable(self, col, row, blocked_tiles=None):
        """
        Check if grid tile is walkable (not blocked).
        
        Args:
            col: Grid column
            row: Grid row
            blocked_tiles: Set of tile IDs that block movement (default: {1})
        
        Returns:
            bool: True if walkable
        
        Example:
            if tilemap.is_walkable(5, 5):
                ghost.move_to(5, 5)
        """
        if blocked_tiles is None:
            blocked_tiles = {1}  # Default: walls block
        
        if not self.in_bounds(col, row):
            return False
        
        tile_id = self.get_tile(col, row)
        return tile_id not in blocked_tiles
    
    def get_walkable_neighbors(self, col, row, blocked_tiles=None):
        """
        Get walkable neighboring tiles (4-way: up, down, left, right).
        
        Args:
            col: Grid column
            row: Grid row
            blocked_tiles: Set of tile IDs that block movement
        
        Returns:
            list: List of (col, row) tuples for walkable neighbors
        
        Example:
            neighbors = tilemap.get_walkable_neighbors(5, 5)
            for ncol, nrow in neighbors:
                print(f"Can move to ({ncol}, {nrow})")
        """
        neighbors = []
        directions = [
            (0, -1),  # Up
            (0, 1),   # Down
            (-1, 0),  # Left
            (1, 0),   # Right
        ]
        
        for dx, dy in directions:
            ncol = col + dx
            nrow = row + dy
            if self.is_walkable(ncol, nrow, blocked_tiles):
                neighbors.append((ncol, nrow))
        
        return neighbors
    
    # ------------------------------------------------------------------------
    # Maze Loading
    # ------------------------------------------------------------------------
    
    def load_from_ascii(self, ascii_str, char_to_tile):
        """
        Load maze from ASCII art string.
        
        Args:
            ascii_str: Multi-line string representing maze
            char_to_tile: Dictionary mapping characters to tile IDs
        
        Example:
            maze = \"\"\"
            ##########
            #........#
            #.##..##.#
            ##########
            \"\"\"
            tilemap.load_from_ascii(maze, {'#': 1, '.': 0, ' ': 0})
        """
        lines = [line for line in ascii_str.strip().split('\n') if line.strip()]
        
        # Validate dimensions
        if len(lines) > self.height:
            logger.warning(f"Maze has {len(lines)} rows but TileMap only has {self.height}")
        
        # Load tiles
        for row, line in enumerate(lines):
            if row >= self.height:
                break
            
            for col, char in enumerate(line):
                if col >= self.width:
                    break
                
                tile_id = char_to_tile.get(char, 0)
                self.set_tile(col, row, tile_id)
    
    def load_from_list(self, tile_list):
        """
        Load maze from 2D list of tile IDs.
        
        Args:
            tile_list: 2D list [row][col] of tile IDs
        
        Example:
            tiles = [
                [1, 1, 1, 1],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [1, 1, 1, 1],
            ]
            tilemap.load_from_list(tiles)
        """
        for row in range(min(len(tile_list), self.height)):
            for col in range(min(len(tile_list[row]), self.width)):
                self.set_tile(col, row, tile_list[row][col])
    
    # ------------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------------
    
    def render(self, matrix):
        """
        Render all tiles to matrix.
        
        Args:
            matrix: LED matrix to draw on
        """
        for row in range(self.height):
            for col in range(self.width):
                tile_id = self.tiles[row][col]
                if tile_id in self.tile_colors:
                    color = self.tile_colors[tile_id]
                    if color != (0, 0, 0):  # Skip black tiles (optimization)
                        x, y = self.grid_to_pixel(col, row)
                        matrix.rect(x, y, self.tile_size, self.tile_size, color, fill=True)
    
    def render_tile(self, matrix, col, row):
        """
        Render single tile to matrix.
        
        Args:
            matrix: LED matrix to draw on
            col: Grid column
            row: Grid row
        """
        if self.in_bounds(col, row):
            tile_id = self.tiles[row][col]
            if tile_id in self.tile_colors:
                color = self.tile_colors[tile_id]
                x, y = self.grid_to_pixel(col, row)
                matrix.rect(x, y, self.tile_size, self.tile_size, color, fill=True)
    
    # ------------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------------
    
    def count_tiles(self, tile_id):
        """
        Count number of tiles with given ID.
        
        Args:
            tile_id: Tile ID to count
        
        Returns:
            int: Number of matching tiles
        """
        count = 0
        for row in range(self.height):
            for col in range(self.width):
                if self.tiles[row][col] == tile_id:
                    count += 1
        return count
    
    def find_tiles(self, tile_id):
        """
        Find all tiles with given ID.
        
        Args:
            tile_id: Tile ID to find
        
        Returns:
            list: List of (col, row) tuples
        """
        positions = []
        for row in range(self.height):
            for col in range(self.width):
                if self.tiles[row][col] == tile_id:
                    positions.append((col, row))
        return positions
    
    def __repr__(self):
        """String representation for debugging."""
        return f"TileMap({self.width}×{self.height}, tile_size={self.tile_size})"


# ============================================================================
# Emoji Sprites
# ============================================================================

class EmojiSprite(Sprite):
    """
    Sprite rendered from emoji using the emoji_loader system.
    
    Perfect for quickly creating sprites with expressive graphics without
    designing pixel art. Uses existing emoji_loader.py for efficient loading
    and caching.
    
    Features:
    - Automatic emoji loading and caching
    - Size scaling (downscale from 32×32 to any size)
    - Animation support (sequence of emoji)
    - Transparent background
    
    Example:
        # Single emoji sprite
        player = EmojiSprite(x=64, y=64, emoji="🟡", size=12)
        
        # Animated emoji sprite
        runner = EmojiSprite(x=50, y=50, emoji=["🚶", "🏃"], size=16, fps=10)
        
        # In game loop
        runner.update(delta_time)  # Animates automatically
        runner.render(matrix)
    """
    
    def __init__(self, x, y, emoji, size=16, fps=10):
        """
        Initialize emoji sprite.
        
        Args:
            x: X position (pixels)
            y: Y position (pixels)
            emoji: Single emoji string or list of emoji for animation
                   Examples: "🟡", ["🚶", "🏃"], "🐸"
            size: Display size in pixels (will scale from 32×32 source)
            fps: Animation frame rate (frames per second, if animated)
        """
        # Initialize base sprite (color not used, but required by base class)
        super().__init__(x, y, size, size, color=(0, 0, 0))
        
        # Animation support
        if isinstance(emoji, list):
            self.emoji_frames = emoji
            self.animated = True
        else:
            self.emoji_frames = [emoji]
            self.animated = False
        
        self.current_frame = 0
        self.animation_fps = fps
        self.animation_timer = 0.0
        
        # Image cache (PIL Image objects)
        self._image_cache = {}
        self._preload_images()
    
    def _preload_images(self):
        """Pre-load and cache all emoji images."""
        from matrixos.emoji_loader import EmojiLoader
        
        loader = EmojiLoader()
        
        for emoji in self.emoji_frames:
            if emoji not in self._image_cache:
                # Get 32×32 emoji image
                img = loader.get_emoji_image(emoji)
                
                if img is None:
                    # Try download on-demand if available
                    img = loader.get_emoji_with_fallback(emoji, size=32)
                
                if img is not None:
                    # Scale to desired size
                    from PIL import Image
                    if self.width != 32 or self.height != 32:
                        # Use LANCZOS for older Pillow versions, Resampling.LANCZOS for newer
                        try:
                            resample = Image.Resampling.LANCZOS
                        except AttributeError:
                            resample = Image.LANCZOS
                        img = img.resize((self.width, self.height), resample)
                    
                    self._image_cache[emoji] = img
                else:
                    # Emoji not found - cache None to avoid repeated lookups
                    self._image_cache[emoji] = None
    
    def update(self, delta_time):
        """
        Update sprite (handles animation).
        
        Args:
            delta_time: Time since last update in seconds
        """
        # Call base update (handles velocity)
        super().update(delta_time)
        
        # Handle animation
        if self.animated and len(self.emoji_frames) > 1:
            self.animation_timer += delta_time
            
            # Advance frame
            frame_duration = 1.0 / self.animation_fps
            if self.animation_timer >= frame_duration:
                self.animation_timer -= frame_duration
                self.current_frame = (self.current_frame + 1) % len(self.emoji_frames)
    
    def render(self, matrix):
        """
        Render emoji sprite to matrix.
        
        Args:
            matrix: LED matrix to draw on
        """
        if not self.visible:
            return
        
        # Get current frame emoji
        emoji = self.emoji_frames[self.current_frame]
        img = self._image_cache.get(emoji)
        
        if img is None:
            # Emoji not available - draw placeholder (small rectangle)
            matrix.rect(int(self.x), int(self.y), self.width, self.height, 
                       (100, 100, 100), fill=False)
            return
        
        # Render emoji pixels
        for py in range(self.height):
            for px in range(self.width):
                try:
                    r, g, b, a = img.getpixel((px, py))
                    
                    # Skip transparent pixels (alpha < 128)
                    if a < 128:
                        continue
                    
                    # Draw pixel
                    screen_x = int(self.x + px)
                    screen_y = int(self.y + py)
                    matrix.set_pixel(screen_x, screen_y, (r, g, b))
                    
                except:
                    # Out of bounds or invalid pixel
                    pass
    
    def set_emoji(self, emoji):
        """
        Change the emoji (for single-frame sprites).
        
        Args:
            emoji: New emoji character
        """
        if isinstance(emoji, list):
            self.emoji_frames = emoji
            self.animated = True
        else:
            self.emoji_frames = [emoji]
            self.animated = False
        
        self.current_frame = 0
        self._preload_images()
    
    def set_animation(self, emoji_list, fps=10):
        """
        Set animation sequence.
        
        Args:
            emoji_list: List of emoji characters
            fps: Animation frame rate
        """
        self.emoji_frames = emoji_list
        self.animated = len(emoji_list) > 1
        self.animation_fps = fps
        self.current_frame = 0
        self.animation_timer = 0.0
        self._preload_images()
    
    def __repr__(self):
        """String representation for debugging."""
        emoji_str = self.emoji_frames[self.current_frame] if self.emoji_frames else "?"
        return f"EmojiSprite({emoji_str} at {self.x:.1f}, {self.y:.1f})"
