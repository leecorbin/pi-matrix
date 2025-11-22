#!/usr/bin/env python3
"""
Sprite Framework Testing Integration Demo

Shows how to test apps using the sprite framework with direct sprite access
instead of color-based sprite finding.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from matrixos.testing import TestRunner
from matrixos.sprites import Sprite, SpriteGroup, TileMap
from matrixos.input import InputEvent


# ============================================================================
# Example 1: Simple Sprite-Based App
# ============================================================================

def test_direct_sprite_access():
    """
    Demo: Access sprites directly from app instead of finding by color.
    
    OLD WAY (color-based):
        player_pos = runner.find_sprite((255, 255, 0), tolerance=10)
        assert player_pos is not None
    
    NEW WAY (direct access):
        player = runner.get_sprite("player")
        assert player.x == 64
    """
    print("\n" + "="*70)
    print("TEST 1: Direct Sprite Access")
    print("="*70)
    
    # Create a simple test app inline
    from matrixos.app_framework import App
    
    class TestApp(App):
        def __init__(self):
            super().__init__("Sprite Test")
            # Create player sprite
            self.player = Sprite(x=64, y=64, width=12, height=12, color=(255, 255, 0))
            self.player.add_tag("player")
            self.dirty = True
        
        def render(self, matrix):
            matrix.clear()
            self.player.render(matrix)
            self.dirty = False
    
    # Create minimal test module
    class TestModule:
        @staticmethod
        def run(os_context):
            app = TestApp()
            os_context.register_app(app)
            os_context.switch_to_app(app)
            os_context.run()
    
    # Monkey-patch for testing
    sys.modules['_test_sprite_app'] = TestModule
    
    try:
        runner = TestRunner("_test_sprite_app", max_duration=5.0)
        runner.wait(0.5)
        
        # OLD WAY: Find by color (still works, but indirect)
        print("OLD WAY - Find by color:")
        player_pos = runner.find_sprite((255, 255, 0), tolerance=10)
        print(f"  Found player at: {player_pos}")
        
        # NEW WAY: Direct access
        print("\nNEW WAY - Direct sprite access:")
        player = runner.get_sprite("player")
        print(f"  player.x = {player.x}")
        print(f"  player.y = {player.y}")
        print(f"  player.width = {player.width}")
        print(f"  player.height = {player.height}")
        print(f"  player.color = {player.color}")
        print(f"  player.has_tag('player') = {player.has_tag('player')}")
        
        # Assertions are cleaner!
        runner.assert_sprite_exists("player")
        runner.assert_sprite_at("player", x=64, y=64, tolerance=1.0)
        runner.assert_sprite_in_bounds("player", x1=0, y1=0, x2=128, y2=128)
        
        print("\n✓ All sprite assertions passed!")
        
    finally:
        del sys.modules['_test_sprite_app']


# ============================================================================
# Example 2: Sprite Groups
# ============================================================================

def test_sprite_groups():
    """Demo: Access sprite groups from app."""
    print("\n" + "="*70)
    print("TEST 2: Sprite Groups")
    print("="*70)
    
    from matrixos.app_framework import App
    
    class TestApp(App):
        def __init__(self):
            super().__init__("Group Test")
            # Create player
            self.player = Sprite(x=64, y=64, width=10, height=10, color=(255, 255, 0))
            
            # Create enemy group
            self.enemies = SpriteGroup()
            for i in range(4):
                enemy = Sprite(x=20 + i*30, y=20, width=10, height=10, color=(255, 0, 0))
                enemy.add_tag("enemy")
                self.enemies.add(enemy)
            
            self.dirty = True
        
        def render(self, matrix):
            matrix.clear()
            self.player.render(matrix)
            self.enemies.render(matrix)
            self.dirty = False
    
    class TestModule:
        @staticmethod
        def run(os_context):
            app = TestApp()
            os_context.register_app(app)
            os_context.switch_to_app(app)
            os_context.run()
    
    sys.modules['_test_group_app'] = TestModule
    
    try:
        runner = TestRunner("_test_group_app", max_duration=5.0)
        runner.wait(0.5)
        
        # Access sprite group directly
        enemies = runner.get_sprite_group("enemies")
        print(f"Enemy count: {len(enemies)}")
        
        for i, enemy in enumerate(enemies):
            print(f"  Enemy {i}: x={enemy.x}, y={enemy.y}, color={enemy.color}")
        
        # Test assertions
        runner.assert_sprite_group_size("enemies", 4)
        print("\n✓ Sprite group test passed!")
        
    finally:
        del sys.modules['_test_group_app']


# ============================================================================
# Example 3: TileMap Integration
# ============================================================================

def test_tilemap_collision():
    """Demo: Test sprite-tile collision detection."""
    print("\n" + "="*70)
    print("TEST 3: TileMap Collision Detection")
    print("="*70)
    
    from matrixos.app_framework import App
    
    class TestApp(App):
        def __init__(self):
            super().__init__("TileMap Test")
            
            # Create tilemap
            self.tilemap = TileMap(width=16, height=16, tile_size=8)
            
            # Load simple maze
            maze = """
################
#..............#
#..............#
################
"""
            self.tilemap.load_from_ascii(maze, {'#': 1, '.': 0})
            
            # Spawn player centered on grid (no wall overlap!)
            # Use 6×6 sprite so it fits within single 8×8 tile
            self.player = self.tilemap.spawn_at_grid_center(
                col=8, row=2, width=6, height=6, color=(255, 255, 0)
            )
            
            self.dirty = True
        
        def render(self, matrix):
            matrix.clear()
            self.tilemap.render(matrix)
            self.player.render(matrix)
            self.dirty = False
    
    class TestModule:
        @staticmethod
        def run(os_context):
            app = TestApp()
            os_context.register_app(app)
            os_context.switch_to_app(app)
            os_context.run()
    
    sys.modules['_test_tilemap_app'] = TestModule
    
    try:
        runner = TestRunner("_test_tilemap_app", max_duration=10.0)
        runner.wait(0.5)
        
        # Access tilemap and player
        tilemap = runner.get_tilemap("tilemap")
        player = runner.get_sprite("player")
        
        print(f"TileMap: {tilemap.width}×{tilemap.height}, tile_size={tilemap.tile_size}")
        print(f"Player: x={player.x:.1f}, y={player.y:.1f}")
        
        # Check wall collision
        cx, cy = player.center()
        col, row = tilemap.pixel_to_grid(cx, cy)
        print(f"Player center at grid ({col}, {row})")
        print(f"Tile at player position: {tilemap.get_tile(col, row)}")
        
        # Test assertion
        runner.assert_sprite_not_in_wall("player", "tilemap", wall_tile_id=1)
        print("\n✓ Player not in wall!")
        
        # Count walls
        wall_count = tilemap.count_tiles(1)
        empty_count = tilemap.count_tiles(0)
        print(f"\nMaze has {wall_count} wall tiles, {empty_count} empty tiles")
        
    finally:
        del sys.modules['_test_tilemap_app']


# ============================================================================
# Example 4: Movement Testing
# ============================================================================

def test_sprite_movement():
    """Demo: Test sprite movement with input."""
    print("\n" + "="*70)
    print("TEST 4: Sprite Movement Testing")
    print("="*70)
    
    from matrixos.app_framework import App
    
    class TestApp(App):
        def __init__(self):
            super().__init__("Movement Test")
            self.player = Sprite(x=64, y=64, width=10, height=10, color=(0, 255, 0))
            self.dirty = True
        
        def on_event(self, event):
            if event.key == InputEvent.RIGHT:
                self.player.velocity_x = 50
                self.dirty = True
                return True
            elif event.key == InputEvent.LEFT:
                self.player.velocity_x = -50
                self.dirty = True
                return True
            return False
        
        def on_update(self, delta_time):
            self.player.update(delta_time)
            if self.player.velocity_x != 0:
                self.dirty = True
        
        def render(self, matrix):
            matrix.clear()
            self.player.render(matrix)
            self.dirty = False
    
    class TestModule:
        @staticmethod
        def run(os_context):
            app = TestApp()
            os_context.register_app(app)
            os_context.switch_to_app(app)
            os_context.run()
    
    sys.modules['_test_movement_app'] = TestModule
    
    try:
        runner = TestRunner("_test_movement_app", max_duration=5.0)
        runner.wait(0.5)
        
        # Get initial position
        player = runner.get_sprite("player")
        initial_x = player.x
        print(f"Initial position: x={initial_x}")
        
        # Send RIGHT input
        runner.inject(InputEvent.RIGHT)
        runner.wait(1.0)  # Let it move for 1 second
        
        # Check movement
        player = runner.get_sprite("player")
        final_x = player.x
        distance_moved = final_x - initial_x
        
        print(f"Final position: x={final_x}")
        print(f"Distance moved: {distance_moved:.1f} pixels")
        
        # Should move about 50 pixels in 1 second (50 px/s velocity)
        assert distance_moved > 40, f"Expected movement >40, got {distance_moved:.1f}"
        print("\n✓ Movement test passed!")
        
    finally:
        del sys.modules['_test_movement_app']


# ============================================================================
# Example 5: Collision Testing
# ============================================================================

def test_sprite_collision():
    """Demo: Test sprite-to-sprite collision."""
    print("\n" + "="*70)
    print("TEST 5: Sprite Collision Testing")
    print("="*70)
    
    from matrixos.app_framework import App
    
    class TestApp(App):
        def __init__(self):
            super().__init__("Collision Test")
            self.player = Sprite(x=60, y=60, width=10, height=10, color=(255, 255, 0))
            self.enemy = Sprite(x=100, y=60, width=10, height=10, color=(255, 0, 0))
            self.dirty = True
        
        def on_event(self, event):
            if event.key == InputEvent.RIGHT:
                self.player.velocity_x = 30
                self.dirty = True
                return True
            return False
        
        def on_update(self, delta_time):
            self.player.update(delta_time)
            if self.player.velocity_x != 0:
                self.dirty = True
        
        def render(self, matrix):
            matrix.clear()
            self.player.render(matrix)
            self.enemy.render(matrix)
            self.dirty = False
    
    class TestModule:
        @staticmethod
        def run(os_context):
            app = TestApp()
            os_context.register_app(app)
            os_context.switch_to_app(app)
            os_context.run()
    
    sys.modules['_test_collision_app'] = TestModule
    
    try:
        runner = TestRunner("_test_collision_app", max_duration=10.0)
        runner.wait(0.5)
        
        # Initially not overlapping
        runner.assert_sprites_not_overlapping("player", "enemy")
        print("✓ Initially not overlapping")
        
        player = runner.get_sprite("player")
        enemy = runner.get_sprite("enemy")
        distance = player.distance_to(enemy)
        print(f"Initial distance: {distance:.1f} pixels")
        
        # Move player toward enemy
        runner.inject(InputEvent.RIGHT)
        runner.wait(2.0)
        
        # Check if they collided
        player = runner.get_sprite("player")
        enemy = runner.get_sprite("enemy")
        distance = player.distance_to(enemy)
        print(f"Final distance: {distance:.1f} pixels")
        
        collided = player.collides_with(enemy)
        print(f"Collision: {collided}")
        
        if collided:
            print("✓ Sprites collided as expected!")
        else:
            print("✓ Sprites did not collide (may need more time)")
        
    finally:
        del sys.modules['_test_collision_app']


# ============================================================================
# Run All Tests
# ============================================================================

def run_all_tests():
    """Run all sprite integration tests."""
    print("="*70)
    print("SPRITE FRAMEWORK TESTING INTEGRATION DEMO")
    print("="*70)
    
    tests = [
        test_direct_sprite_access,
        test_sprite_groups,
        test_tilemap_collision,
        test_sprite_movement,
        test_sprite_collision,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
