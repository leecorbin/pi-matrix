#!/usr/bin/env python3
"""
Unit tests for MatrixOS Sprite Framework

Tests collision detection, sprite groups, movement, and rendering.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from matrixos.sprites import (
    Sprite, SpriteGroup, TileMap, EmojiSprite,
    rect_overlap, point_in_rect, distance
)


# ============================================================================
# Collision Utility Tests
# ============================================================================

def test_rect_overlap():
    """Test rectangle overlap detection."""
    print("TEST: Rectangle Overlap Detection")
    
    # Overlapping rectangles
    assert rect_overlap((0, 0, 10, 10), (5, 5, 10, 10)), "Should overlap"
    assert rect_overlap((5, 5, 10, 10), (0, 0, 10, 10)), "Should overlap (reversed)"
    
    # Touching edges (should not overlap)
    assert not rect_overlap((0, 0, 10, 10), (10, 0, 10, 10)), "Touching edges should not overlap"
    assert not rect_overlap((0, 0, 10, 10), (0, 10, 10, 10)), "Touching edges should not overlap"
    
    # Completely separate
    assert not rect_overlap((0, 0, 10, 10), (20, 20, 10, 10)), "Should not overlap"
    
    # One inside the other
    assert rect_overlap((0, 0, 20, 20), (5, 5, 5, 5)), "Small inside large"
    assert rect_overlap((5, 5, 5, 5), (0, 0, 20, 20)), "Small inside large (reversed)"
    
    print("✓ Rectangle overlap detection works correctly")


def test_point_in_rect():
    """Test point-in-rectangle detection."""
    print("\nTEST: Point in Rectangle")
    
    rect = (10, 10, 20, 20)  # x=10, y=10, w=20, h=20
    
    # Points inside
    assert point_in_rect(15, 15, rect), "Center point should be inside"
    assert point_in_rect(10, 10, rect), "Top-left corner should be inside"
    assert point_in_rect(29, 29, rect), "Just inside bottom-right"
    
    # Points outside
    assert not point_in_rect(5, 5, rect), "Before top-left"
    assert not point_in_rect(30, 30, rect), "After bottom-right"
    assert not point_in_rect(15, 5, rect), "Above rectangle"
    assert not point_in_rect(5, 15, rect), "Left of rectangle"
    
    print("✓ Point-in-rectangle detection works correctly")


def test_distance():
    """Test distance calculation."""
    print("\nTEST: Distance Calculation")
    
    # Horizontal/vertical
    assert distance(0, 0, 10, 0) == 10, "Horizontal distance"
    assert distance(0, 0, 0, 10) == 10, "Vertical distance"
    
    # Diagonal
    d = distance(0, 0, 3, 4)
    assert abs(d - 5.0) < 0.01, f"3-4-5 triangle, got {d}"
    
    # Same point
    assert distance(5, 5, 5, 5) == 0, "Same point should be 0"
    
    print("✓ Distance calculation works correctly")


# ============================================================================
# Sprite Tests
# ============================================================================

def test_sprite_creation():
    """Test sprite initialization."""
    print("\nTEST: Sprite Creation")
    
    sprite = Sprite(x=10, y=20, width=8, height=12, color=(255, 0, 0))
    
    assert sprite.x == 10, "X position"
    assert sprite.y == 20, "Y position"
    assert sprite.width == 8, "Width"
    assert sprite.height == 12, "Height"
    assert sprite.color == (255, 0, 0), "Color"
    assert sprite.velocity_x == 0, "Initial velocity X"
    assert sprite.velocity_y == 0, "Initial velocity Y"
    assert sprite.visible == True, "Initially visible"
    
    print("✓ Sprite creation works correctly")


def test_sprite_rect():
    """Test sprite bounding rectangle."""
    print("\nTEST: Sprite Rectangle")
    
    sprite = Sprite(x=10.5, y=20.5, width=8, height=12)
    rect = sprite.rect()
    
    assert rect == (10.5, 20.5, 8, 12), f"Expected (10.5, 20.5, 8, 12), got {rect}"
    
    print("✓ Sprite rectangle works correctly")


def test_sprite_center():
    """Test sprite center calculation."""
    print("\nTEST: Sprite Center")
    
    sprite = Sprite(x=10, y=20, width=8, height=12)
    cx, cy = sprite.center()
    
    assert cx == 14, f"Center X should be 14, got {cx}"
    assert cy == 26, f"Center Y should be 26, got {cy}"
    
    # Test set_center
    sprite.set_center(50, 60)
    assert sprite.x == 46, f"X should be 46, got {sprite.x}"
    assert sprite.y == 54, f"Y should be 54, got {sprite.y}"
    
    print("✓ Sprite center calculation works correctly")


def test_sprite_movement():
    """Test sprite movement with velocity."""
    print("\nTEST: Sprite Movement")
    
    sprite = Sprite(x=10, y=20, width=8, height=12)
    sprite.velocity_x = 50  # 50 pixels per second
    sprite.velocity_y = 100  # 100 pixels per second
    
    # Update for 0.5 seconds
    sprite.update(0.5)
    
    assert sprite.x == 35, f"X should be 35 (10 + 50*0.5), got {sprite.x}"
    assert sprite.y == 70, f"Y should be 70 (20 + 100*0.5), got {sprite.y}"
    
    # Update for another 0.1 seconds
    sprite.update(0.1)
    
    assert sprite.x == 40, f"X should be 40 (35 + 50*0.1), got {sprite.x}"
    assert sprite.y == 80, f"Y should be 80 (70 + 100*0.1), got {sprite.y}"
    
    print("✓ Sprite movement works correctly")


def test_sprite_collision():
    """Test sprite-to-sprite collision detection."""
    print("\nTEST: Sprite Collision")
    
    sprite1 = Sprite(x=10, y=10, width=10, height=10)
    sprite2 = Sprite(x=15, y=15, width=10, height=10)
    sprite3 = Sprite(x=30, y=30, width=10, height=10)
    
    # Overlapping sprites
    assert sprite1.collides_with(sprite2), "Sprites 1 and 2 should collide"
    assert sprite2.collides_with(sprite1), "Collision should be symmetric"
    
    # Non-overlapping sprites
    assert not sprite1.collides_with(sprite3), "Sprites 1 and 3 should not collide"
    assert not sprite2.collides_with(sprite3), "Sprites 2 and 3 should not collide"
    
    print("✓ Sprite collision detection works correctly")


def test_sprite_point_collision():
    """Test sprite-to-point collision."""
    print("\nTEST: Sprite Point Collision")
    
    sprite = Sprite(x=10, y=20, width=8, height=12)
    
    # Points inside
    assert sprite.collides_with_point(14, 26), "Center should collide"
    assert sprite.collides_with_point(10, 20), "Top-left corner should collide"
    
    # Points outside
    assert not sprite.collides_with_point(5, 5), "Outside point"
    assert not sprite.collides_with_point(20, 35), "Outside point"
    
    print("✓ Sprite point collision works correctly")


def test_sprite_distance():
    """Test distance calculation between sprites."""
    print("\nTEST: Sprite Distance")
    
    sprite1 = Sprite(x=0, y=0, width=10, height=10)  # Center at (5, 5)
    sprite2 = Sprite(x=30, y=40, width=10, height=10)  # Center at (35, 45)
    
    # Distance from (5,5) to (35,45) = sqrt(30^2 + 40^2) = 50
    d = sprite1.distance_to(sprite2)
    assert abs(d - 50.0) < 0.01, f"Distance should be 50, got {d}"
    
    print("✓ Sprite distance calculation works correctly")


def test_sprite_tags():
    """Test sprite tagging system."""
    print("\nTEST: Sprite Tags")
    
    sprite = Sprite(x=0, y=0, width=10, height=10)
    
    # Add tags
    sprite.add_tag("player")
    sprite.add_tag("movable")
    
    assert sprite.has_tag("player"), "Should have player tag"
    assert sprite.has_tag("movable"), "Should have movable tag"
    assert not sprite.has_tag("enemy"), "Should not have enemy tag"
    
    print("✓ Sprite tagging works correctly")


# ============================================================================
# Sprite Group Tests
# ============================================================================

def test_sprite_group_creation():
    """Test sprite group initialization."""
    print("\nTEST: Sprite Group Creation")
    
    # Empty group
    group1 = SpriteGroup()
    assert len(group1) == 0, "Empty group should have 0 sprites"
    
    # Group with initial sprites
    s1 = Sprite(0, 0, 10, 10)
    s2 = Sprite(20, 20, 10, 10)
    group2 = SpriteGroup(s1, s2)
    assert len(group2) == 2, "Group should have 2 sprites"
    
    print("✓ Sprite group creation works correctly")


def test_sprite_group_add_remove():
    """Test adding and removing sprites from group."""
    print("\nTEST: Sprite Group Add/Remove")
    
    group = SpriteGroup()
    s1 = Sprite(0, 0, 10, 10)
    s2 = Sprite(20, 20, 10, 10)
    
    # Add sprites
    group.add(s1)
    assert len(group) == 1, "Should have 1 sprite"
    
    group.add(s2)
    assert len(group) == 2, "Should have 2 sprites"
    
    # Adding same sprite again should not duplicate
    group.add(s1)
    assert len(group) == 2, "Should still have 2 sprites (no duplicates)"
    
    # Remove sprite
    group.remove(s1)
    assert len(group) == 1, "Should have 1 sprite after removal"
    
    # Clear all
    group.clear()
    assert len(group) == 0, "Should have 0 sprites after clear"
    
    print("✓ Sprite group add/remove works correctly")


def test_sprite_group_update():
    """Test batch updating sprites in group."""
    print("\nTEST: Sprite Group Update")
    
    s1 = Sprite(0, 0, 10, 10)
    s1.velocity_x = 50
    
    s2 = Sprite(0, 0, 10, 10)
    s2.velocity_y = 100
    
    group = SpriteGroup(s1, s2)
    group.update(0.5)
    
    assert s1.x == 25, f"S1 X should be 25, got {s1.x}"
    assert s2.y == 50, f"S2 Y should be 50, got {s2.y}"
    
    print("✓ Sprite group batch update works correctly")


def test_sprite_group_collisions():
    """Test collision detection in sprite groups."""
    print("\nTEST: Sprite Group Collisions")
    
    player = Sprite(x=10, y=10, width=10, height=10)
    
    enemy1 = Sprite(x=15, y=15, width=10, height=10)  # Overlaps player
    enemy2 = Sprite(x=50, y=50, width=10, height=10)  # Does not overlap
    
    enemies = SpriteGroup(enemy1, enemy2)
    
    # Check collisions
    collisions = enemies.check_collisions(player)
    
    assert len(collisions) == 1, f"Should have 1 collision, got {len(collisions)}"
    assert collisions[0] == enemy1, "Should collide with enemy1"
    
    print("✓ Sprite group collision detection works correctly")


def test_sprite_group_group_collisions():
    """Test collision detection between two groups."""
    print("\nTEST: Sprite Group-to-Group Collisions")
    
    # Players group
    player1 = Sprite(x=10, y=10, width=10, height=10)
    player2 = Sprite(x=50, y=50, width=10, height=10)
    players = SpriteGroup(player1, player2)
    
    # Enemies group
    enemy1 = Sprite(x=15, y=15, width=10, height=10)  # Overlaps player1
    enemy2 = Sprite(x=45, y=45, width=10, height=10)  # Overlaps player2
    enemy3 = Sprite(x=100, y=100, width=10, height=10)  # No overlap
    enemies = SpriteGroup(enemy1, enemy2, enemy3)
    
    # Check group collisions
    collisions = players.check_group_collisions(enemies)
    
    assert len(collisions) == 2, f"Should have 2 collisions, got {len(collisions)}"
    
    # Check collision pairs
    pairs = set(collisions)
    assert (player1, enemy1) in pairs, "Player1 should collide with enemy1"
    assert (player2, enemy2) in pairs, "Player2 should collide with enemy2"
    
    print("✓ Group-to-group collision detection works correctly")


def test_sprite_group_find_by_tag():
    """Test finding sprites by tag."""
    print("\nTEST: Find Sprites by Tag")
    
    s1 = Sprite(0, 0, 10, 10)
    s1.add_tag("enemy")
    s1.add_tag("red")
    
    s2 = Sprite(20, 20, 10, 10)
    s2.add_tag("enemy")
    s2.add_tag("blue")
    
    s3 = Sprite(40, 40, 10, 10)
    s3.add_tag("player")
    
    group = SpriteGroup(s1, s2, s3)
    
    # Find enemies
    enemies = group.find_by_tag("enemy")
    assert len(enemies) == 2, "Should find 2 enemies"
    assert s1 in enemies and s2 in enemies, "Should find both enemy sprites"
    
    # Find player
    players = group.find_by_tag("player")
    assert len(players) == 1, "Should find 1 player"
    assert players[0] == s3, "Should find player sprite"
    
    # Find red
    reds = group.find_by_tag("red")
    assert len(reds) == 1, "Should find 1 red sprite"
    assert reds[0] == s1, "Should find red sprite"
    
    print("✓ Find sprites by tag works correctly")


def test_sprite_group_find_by_color():
    """Test finding sprites by color."""
    print("\nTEST: Find Sprites by Color")
    
    s1 = Sprite(0, 0, 10, 10, color=(255, 0, 0))  # Red
    s2 = Sprite(20, 20, 10, 10, color=(255, 5, 0))  # Almost red
    s3 = Sprite(40, 40, 10, 10, color=(0, 255, 0))  # Green
    
    group = SpriteGroup(s1, s2, s3)
    
    # Find red sprites (with tolerance)
    reds = group.find_by_color((255, 0, 0), tolerance=10)
    assert len(reds) == 2, f"Should find 2 red sprites, got {len(reds)}"
    
    # Find green sprites (strict)
    greens = group.find_by_color((0, 255, 0), tolerance=0)
    assert len(greens) == 1, "Should find 1 green sprite"
    assert greens[0] == s3, "Should find green sprite"
    
    print("✓ Find sprites by color works correctly")


def test_sprite_group_iteration():
    """Test iterating over sprite group."""
    print("\nTEST: Sprite Group Iteration")
    
    sprites = [Sprite(i*10, 0, 10, 10) for i in range(5)]
    group = SpriteGroup(*sprites)
    
    # Test iteration
    count = 0
    for sprite in group:
        count += 1
        assert sprite in sprites, "Sprite should be in original list"
    
    assert count == 5, f"Should iterate over 5 sprites, got {count}"
    
    print("✓ Sprite group iteration works correctly")


# ============================================================================
# TileMap Tests
# ============================================================================

def test_tilemap_creation():
    """Test TileMap initialization."""
    print("\nTEST: TileMap Creation")
    
    tilemap = TileMap(width=10, height=8, tile_size=8)
    
    assert tilemap.width == 10, "Width should be 10"
    assert tilemap.height == 8, "Height should be 8"
    assert tilemap.tile_size == 8, "Tile size should be 8"
    assert len(tilemap.tiles) == 8, "Should have 8 rows"
    assert len(tilemap.tiles[0]) == 10, "Should have 10 columns"
    
    # All tiles should be 0 initially
    for row in range(8):
        for col in range(10):
            assert tilemap.tiles[row][col] == 0, f"Tile ({col}, {row}) should be 0"
    
    print("✓ TileMap creation works correctly")


def test_coordinate_conversion():
    """Test pixel ↔ grid coordinate conversion."""
    print("\nTEST: Coordinate Conversion")
    
    tilemap = TileMap(width=10, height=10, tile_size=8)
    
    # Pixel to grid
    assert tilemap.pixel_to_grid(0, 0) == (0, 0), "Top-left corner"
    assert tilemap.pixel_to_grid(8, 8) == (1, 1), "One tile over"
    assert tilemap.pixel_to_grid(16, 24) == (2, 3), "Multiple tiles"
    assert tilemap.pixel_to_grid(7, 7) == (0, 0), "Within first tile"
    
    # Grid to pixel (top-left)
    assert tilemap.grid_to_pixel(0, 0) == (0, 0), "Grid origin"
    assert tilemap.grid_to_pixel(1, 1) == (8, 8), "One tile over"
    assert tilemap.grid_to_pixel(2, 3) == (16, 24), "Multiple tiles"
    
    # Grid to pixel (center)
    assert tilemap.grid_to_pixel_center(0, 0) == (4, 4), "Center of first tile"
    assert tilemap.grid_to_pixel_center(1, 1) == (12, 12), "Center of (1,1)"
    
    print("✓ Coordinate conversion works correctly")


def test_tile_access():
    """Test setting and getting tiles."""
    print("\nTEST: Tile Access")
    
    tilemap = TileMap(width=5, height=5, tile_size=8)
    
    # Set tiles
    assert tilemap.set_tile(2, 3, 1), "Should set tile successfully"
    assert tilemap.set_tile(4, 4, 2), "Should set tile successfully"
    
    # Get tiles
    assert tilemap.get_tile(2, 3) == 1, "Should get tile 1"
    assert tilemap.get_tile(4, 4) == 2, "Should get tile 2"
    assert tilemap.get_tile(0, 0) == 0, "Unset tile should be 0"
    
    # Out of bounds
    assert tilemap.get_tile(10, 10) is None, "Out of bounds should return None"
    assert not tilemap.set_tile(10, 10, 1), "Out of bounds set should return False"
    
    # Get tile at pixel
    assert tilemap.get_tile_at_pixel(16, 24) == 1, "Pixel (16,24) is grid (2,3)"
    assert tilemap.get_tile_at_pixel(32, 32) == 2, "Pixel (32,32) is grid (4,4)"
    
    print("✓ Tile access works correctly")


def test_bounds_checking():
    """Test in_bounds checking."""
    print("\nTEST: Bounds Checking")
    
    tilemap = TileMap(width=5, height=5, tile_size=8)
    
    # Valid positions
    assert tilemap.in_bounds(0, 0), "Origin should be in bounds"
    assert tilemap.in_bounds(4, 4), "Max position should be in bounds"
    assert tilemap.in_bounds(2, 2), "Center should be in bounds"
    
    # Invalid positions
    assert not tilemap.in_bounds(-1, 0), "Negative col out of bounds"
    assert not tilemap.in_bounds(0, -1), "Negative row out of bounds"
    assert not tilemap.in_bounds(5, 0), "Col >= width out of bounds"
    assert not tilemap.in_bounds(0, 5), "Row >= height out of bounds"
    
    print("✓ Bounds checking works correctly")


def test_sprite_tile_overlap():
    """Test getting tiles that sprite overlaps."""
    print("\nTEST: Sprite Tile Overlap")
    
    tilemap = TileMap(width=10, height=10, tile_size=8)
    
    # Sprite exactly on one tile
    sprite1 = Sprite(x=16, y=16, width=8, height=8)
    tiles1 = tilemap.get_sprite_tiles(sprite1)
    assert len(tiles1) == 1, f"Should overlap 1 tile, got {len(tiles1)}"
    assert (2, 2) in tiles1, "Should overlap tile (2, 2)"
    
    # Sprite spanning 4 tiles
    sprite2 = Sprite(x=12, y=12, width=8, height=8)
    tiles2 = tilemap.get_sprite_tiles(sprite2)
    assert len(tiles2) == 4, f"Should overlap 4 tiles, got {len(tiles2)}"
    assert (1, 1) in tiles2, "Should overlap (1,1)"
    assert (2, 1) in tiles2, "Should overlap (2,1)"
    assert (1, 2) in tiles2, "Should overlap (1,2)"
    assert (2, 2) in tiles2, "Should overlap (2,2)"
    
    # Large sprite spanning many tiles
    sprite3 = Sprite(x=8, y=8, width=24, height=16)
    tiles3 = tilemap.get_sprite_tiles(sprite3)
    expected_count = 3 * 2  # 3 cols × 2 rows
    assert len(tiles3) == expected_count, f"Should overlap {expected_count} tiles, got {len(tiles3)}"
    
    print("✓ Sprite tile overlap detection works correctly")


def test_sprite_tile_collision():
    """Test sprite collision with tile types."""
    print("\nTEST: Sprite-Tile Collision")
    
    tilemap = TileMap(width=10, height=10, tile_size=8)
    
    # Set up walls
    tilemap.set_tile(5, 5, 1)  # Wall at (5, 5)
    tilemap.set_tile(6, 5, 1)  # Wall at (6, 5)
    
    # Sprite on wall
    sprite1 = Sprite(x=40, y=40, width=8, height=8)
    assert tilemap.sprite_collides_with_tile(sprite1, tile_id=1), "Should collide with wall"
    
    # Sprite not on wall
    sprite2 = Sprite(x=0, y=0, width=8, height=8)
    assert not tilemap.sprite_collides_with_tile(sprite2, tile_id=1), "Should not collide with wall"
    
    # Sprite partially on wall
    sprite3 = Sprite(x=36, y=36, width=12, height=12)
    assert tilemap.sprite_collides_with_tile(sprite3, tile_id=1), "Should collide (partially overlaps)"
    
    # Test collides_with_tiles (multiple tile types)
    tilemap.set_tile(0, 0, 2)  # Dot at (0, 0)
    sprite4 = Sprite(x=0, y=0, width=8, height=8)
    assert tilemap.sprite_collides_with_tiles(sprite4, [1, 2]), "Should collide with tile 2"
    assert not tilemap.sprite_collides_with_tiles(sprite4, [1]), "Should not collide with tile 1"
    
    print("✓ Sprite-tile collision detection works correctly")


def test_grid_spawn_helpers():
    """Test grid-aligned sprite spawning."""
    print("\nTEST: Grid Spawn Helpers")
    
    tilemap = TileMap(width=10, height=10, tile_size=8)
    
    # Spawn at grid (top-left aligned)
    sprite1 = tilemap.spawn_at_grid(col=5, row=3, width=8, height=8)
    assert sprite1.x == 40, f"X should be 40 (5*8), got {sprite1.x}"
    assert sprite1.y == 24, f"Y should be 24 (3*8), got {sprite1.y}"
    assert sprite1.width == 8, "Width should be 8"
    assert sprite1.height == 8, "Height should be 8"
    
    # Spawn at grid center
    sprite2 = tilemap.spawn_at_grid_center(col=4, row=2, width=12, height=12)
    cx, cy = sprite2.center()
    expected_cx = 4 * 8 + 4  # 36
    expected_cy = 2 * 8 + 4  # 20
    assert abs(cx - expected_cx) < 0.1, f"Center X should be {expected_cx}, got {cx}"
    assert abs(cy - expected_cy) < 0.1, f"Center Y should be {expected_cy}, got {cy}"
    
    print("✓ Grid spawn helpers work correctly")


def test_walkability():
    """Test walkability checking."""
    print("\nTEST: Walkability")
    
    tilemap = TileMap(width=10, height=10, tile_size=8)
    
    # Set up walls
    tilemap.set_tile(5, 5, 1)
    
    # Empty tile is walkable
    assert tilemap.is_walkable(0, 0), "Empty tile should be walkable"
    
    # Wall tile is not walkable
    assert not tilemap.is_walkable(5, 5), "Wall should not be walkable"
    
    # Out of bounds not walkable
    assert not tilemap.is_walkable(-1, 0), "Out of bounds not walkable"
    assert not tilemap.is_walkable(100, 100), "Out of bounds not walkable"
    
    # Custom blocked tiles
    tilemap.set_tile(3, 3, 2)
    assert tilemap.is_walkable(3, 3, blocked_tiles={1}), "Tile 2 walkable if only 1 blocks"
    assert not tilemap.is_walkable(3, 3, blocked_tiles={1, 2}), "Tile 2 not walkable if 2 blocks"
    
    print("✓ Walkability checking works correctly")


def test_walkable_neighbors():
    """Test getting walkable neighbor tiles."""
    print("\nTEST: Walkable Neighbors")
    
    tilemap = TileMap(width=5, height=5, tile_size=8)
    
    # Center tile with no walls
    neighbors1 = tilemap.get_walkable_neighbors(2, 2)
    assert len(neighbors1) == 4, f"Center should have 4 neighbors, got {len(neighbors1)}"
    assert (2, 1) in neighbors1, "Should have up neighbor"
    assert (2, 3) in neighbors1, "Should have down neighbor"
    assert (1, 2) in neighbors1, "Should have left neighbor"
    assert (3, 2) in neighbors1, "Should have right neighbor"
    
    # Corner tile
    neighbors2 = tilemap.get_walkable_neighbors(0, 0)
    assert len(neighbors2) == 2, f"Corner should have 2 neighbors, got {len(neighbors2)}"
    assert (0, 1) in neighbors2, "Should have down neighbor"
    assert (1, 0) in neighbors2, "Should have right neighbor"
    
    # Tile surrounded by walls
    tilemap.set_tile(1, 2, 1)  # Left
    tilemap.set_tile(3, 2, 1)  # Right
    tilemap.set_tile(2, 1, 1)  # Up
    tilemap.set_tile(2, 3, 1)  # Down
    neighbors3 = tilemap.get_walkable_neighbors(2, 2)
    assert len(neighbors3) == 0, f"Surrounded tile should have 0 neighbors, got {len(neighbors3)}"
    
    print("✓ Walkable neighbor detection works correctly")


def test_ascii_maze_loading():
    """Test loading maze from ASCII art."""
    print("\nTEST: ASCII Maze Loading")
    
    tilemap = TileMap(width=10, height=4, tile_size=8)
    
    maze = """
##########
#........#
#.##..##.#
##########
"""
    
    tilemap.load_from_ascii(maze, {'#': 1, '.': 0, ' ': 0})
    
    # Check corners (should be walls)
    assert tilemap.get_tile(0, 0) == 1, "Top-left should be wall"
    assert tilemap.get_tile(9, 0) == 1, "Top-right should be wall"
    assert tilemap.get_tile(0, 3) == 1, "Bottom-left should be wall"
    assert tilemap.get_tile(9, 3) == 1, "Bottom-right should be wall"
    
    # Check interior (should be empty)
    assert tilemap.get_tile(1, 1) == 0, "Interior should be empty"
    assert tilemap.get_tile(5, 1) == 0, "Interior should be empty"
    
    # Check interior walls
    assert tilemap.get_tile(2, 2) == 1, "Interior wall"
    assert tilemap.get_tile(3, 2) == 1, "Interior wall"
    
    print("✓ ASCII maze loading works correctly")


def test_list_maze_loading():
    """Test loading maze from 2D list."""
    print("\nTEST: List Maze Loading")
    
    tilemap = TileMap(width=4, height=4, tile_size=8)
    
    maze = [
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 2, 1],
        [1, 1, 1, 1],
    ]
    
    tilemap.load_from_list(maze)
    
    # Check walls
    assert tilemap.get_tile(0, 0) == 1, "Corner should be wall"
    assert tilemap.get_tile(3, 3) == 1, "Corner should be wall"
    
    # Check empty
    assert tilemap.get_tile(1, 1) == 0, "Interior should be empty"
    
    # Check special tile
    assert tilemap.get_tile(2, 2) == 2, "Should be tile type 2"
    
    print("✓ List maze loading works correctly")


def test_tile_utilities():
    """Test tile counting and finding."""
    print("\nTEST: Tile Utilities")
    
    tilemap = TileMap(width=5, height=5, tile_size=8)
    
    # Set some tiles
    tilemap.set_tile(0, 0, 1)
    tilemap.set_tile(1, 0, 1)
    tilemap.set_tile(2, 2, 2)
    
    # Count tiles
    assert tilemap.count_tiles(0) == 22, "Should have 22 empty tiles (25 - 3)"
    assert tilemap.count_tiles(1) == 2, "Should have 2 wall tiles"
    assert tilemap.count_tiles(2) == 1, "Should have 1 special tile"
    
    # Find tiles
    walls = tilemap.find_tiles(1)
    assert len(walls) == 2, "Should find 2 walls"
    assert (0, 0) in walls, "Wall at (0, 0)"
    assert (1, 0) in walls, "Wall at (1, 0)"
    
    special = tilemap.find_tiles(2)
    assert len(special) == 1, "Should find 1 special tile"
    assert (2, 2) in special, "Special at (2, 2)"
    
    print("✓ Tile utilities work correctly")


# ============================================================================
# EmojiSprite Tests
# ============================================================================

def test_emoji_sprite_creation():
    """Test EmojiSprite initialization."""
    print("\nTEST: EmojiSprite Creation")
    
    # Single emoji
    sprite1 = EmojiSprite(x=64, y=64, emoji="🟡", size=16)
    assert sprite1.x == 64, "X position"
    assert sprite1.y == 64, "Y position"
    assert sprite1.width == 16, "Width should match size"
    assert sprite1.height == 16, "Height should match size"
    assert not sprite1.animated, "Single emoji not animated"
    assert len(sprite1.emoji_frames) == 1, "Should have 1 frame"
    
    # Animated emoji
    sprite2 = EmojiSprite(x=50, y=50, emoji=["🚶", "🏃"], size=12, fps=10)
    assert sprite2.animated, "Multiple emoji should be animated"
    assert len(sprite2.emoji_frames) == 2, "Should have 2 frames"
    assert sprite2.animation_fps == 10, "FPS should be 10"
    
    print("✓ EmojiSprite creation works correctly")


def test_emoji_sprite_animation():
    """Test EmojiSprite animation."""
    print("\nTEST: EmojiSprite Animation")
    
    sprite = EmojiSprite(x=0, y=0, emoji=["😀", "😃", "😄"], size=16, fps=10)
    
    assert sprite.current_frame == 0, "Should start at frame 0"
    
    # Update for half a frame (1/10 second = 0.1s per frame)
    sprite.update(0.05)
    assert sprite.current_frame == 0, "Should still be frame 0"
    
    # Update to advance frame
    sprite.update(0.06)  # Total 0.11s, should advance
    assert sprite.current_frame == 1, f"Should advance to frame 1, got {sprite.current_frame}"
    
    # Continue animating
    sprite.update(0.1)
    assert sprite.current_frame == 2, "Should be frame 2"
    
    # Loop back to start
    sprite.update(0.1)
    assert sprite.current_frame == 0, "Should loop back to frame 0"
    
    print("✓ EmojiSprite animation works correctly")


def test_emoji_sprite_set_emoji():
    """Test changing emoji dynamically."""
    print("\nTEST: EmojiSprite Set Emoji")
    
    sprite = EmojiSprite(x=0, y=0, emoji="🐸", size=16)
    assert sprite.emoji_frames[0] == "🐸", "Initial emoji"
    
    # Change to different emoji
    sprite.set_emoji("🐢")
    assert sprite.emoji_frames[0] == "🐢", "Changed emoji"
    assert not sprite.animated, "Still not animated"
    
    # Change to animated sequence
    sprite.set_emoji(["🐢", "🐇"])
    assert len(sprite.emoji_frames) == 2, "Should have 2 frames"
    assert sprite.animated, "Should be animated"
    
    print("✓ EmojiSprite set_emoji works correctly")


def test_emoji_sprite_set_animation():
    """Test setting animation sequence."""
    print("\nTEST: EmojiSprite Set Animation")
    
    sprite = EmojiSprite(x=0, y=0, emoji="⏰", size=16)
    
    # Add animation
    sprite.set_animation(["⏰", "⏱️", "⏲️"], fps=5)
    assert len(sprite.emoji_frames) == 3, "Should have 3 frames"
    assert sprite.animation_fps == 5, "FPS should be 5"
    assert sprite.animated, "Should be animated"
    assert sprite.current_frame == 0, "Should reset to frame 0"
    
    print("✓ EmojiSprite set_animation works correctly")


def test_emoji_sprite_movement():
    """Test EmojiSprite with velocity."""
    print("\nTEST: EmojiSprite Movement")
    
    sprite = EmojiSprite(x=0, y=0, emoji="🚗", size=16)
    sprite.velocity_x = 50
    sprite.velocity_y = 25
    
    # Update for 1 second
    sprite.update(1.0)
    
    assert sprite.x == 50, f"X should be 50, got {sprite.x}"
    assert sprite.y == 25, f"Y should be 25, got {sprite.y}"
    
    print("✓ EmojiSprite movement works correctly")


def test_emoji_sprite_collision():
    """Test collision detection with EmojiSprite."""
    print("\nTEST: EmojiSprite Collision")
    
    sprite1 = EmojiSprite(x=10, y=10, emoji="⚽", size=12)
    sprite2 = EmojiSprite(x=15, y=15, emoji="🏀", size=12)
    sprite3 = EmojiSprite(x=50, y=50, emoji="🎾", size=12)
    
    # Overlapping
    assert sprite1.collides_with(sprite2), "Sprites 1 and 2 should collide"
    
    # Not overlapping
    assert not sprite1.collides_with(sprite3), "Sprites 1 and 3 should not collide"
    
    # Distance
    dist = sprite1.distance_to(sprite3)
    # Center of sprite1: (10 + 6, 10 + 6) = (16, 16)
    # Center of sprite3: (50 + 6, 50 + 6) = (56, 56)
    # Distance: sqrt((56-16)^2 + (56-16)^2) = sqrt(3200) ≈ 56.6
    expected = 56.6
    assert abs(dist - expected) < 2, f"Distance should be ~{expected:.1f}, got {dist:.1f}"
    
    print("✓ EmojiSprite collision works correctly")


# ============================================================================
# Run All Tests
# ============================================================================

def run_all_tests():
    """Run all sprite framework tests."""
    print("=" * 70)
    print("MATRIXOS SPRITE FRAMEWORK UNIT TESTS")
    print("=" * 70)
    
    tests = [
        # Collision utilities
        test_rect_overlap,
        test_point_in_rect,
        test_distance,
        
        # Sprite tests
        test_sprite_creation,
        test_sprite_rect,
        test_sprite_center,
        test_sprite_movement,
        test_sprite_collision,
        test_sprite_point_collision,
        test_sprite_distance,
        test_sprite_tags,
        
        # Sprite group tests
        test_sprite_group_creation,
        test_sprite_group_add_remove,
        test_sprite_group_update,
        test_sprite_group_collisions,
        test_sprite_group_group_collisions,
        test_sprite_group_find_by_tag,
        test_sprite_group_find_by_color,
        test_sprite_group_iteration,
        
        # TileMap tests
        test_tilemap_creation,
        test_coordinate_conversion,
        test_tile_access,
        test_bounds_checking,
        test_sprite_tile_overlap,
        test_sprite_tile_collision,
        test_grid_spawn_helpers,
        test_walkability,
        test_walkable_neighbors,
        test_ascii_maze_loading,
        test_list_maze_loading,
        test_tile_utilities,
        
        # EmojiSprite tests
        test_emoji_sprite_creation,
        test_emoji_sprite_animation,
        test_emoji_sprite_set_emoji,
        test_emoji_sprite_set_animation,
        test_emoji_sprite_movement,
        test_emoji_sprite_collision,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
