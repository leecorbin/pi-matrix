# Sprite Framework Implementation Plan

## Phase 1: Core Sprite Class (Day 1-2)

### Day 1 Tasks ✅ COMPLETED

- [x] Create `matrixos/sprites.py` with base Sprite class
- [x] Implement rectangle collision utilities (pure functions)
- [x] Implement Sprite class:
  - Position (x, y) and dimensions (width, height)
  - Velocity (velocity_x, velocity_y)
  - Color for default rendering
  - `update(delta_time)` method
  - `render(matrix)` method
  - `collides_with(other)` method
  - `collides_with_point(x, y)` method
  - `rect()` - return bounding rectangle
  - `center()` - return center point
  - `set_center(x, y)` - set position by center
- [x] Create unit tests in `tests/test_sprites.py`
- [x] Test collision detection thoroughly
- [x] Test movement with velocity
- [x] **BONUS**: Added tagging system for sprite identification
- [x] **BONUS**: Added distance calculation between sprites
- [x] **ALL TESTS PASS**: 19/19 unit tests passing

---

## Phase 2: TileMap System (Day 2-3) ✅ COMPLETED

### Implementation Summary ✅

**Completed:** TileMap class with 450+ lines in `matrixos/sprites.py`

**Features Delivered:**
- [x] Grid-based tile storage (2D array)
- [x] Pixel ↔ Grid coordinate conversion (all 3 variants)
- [x] Sprite-tile collision detection (`sprite_collides_with_tile`)
- [x] Grid-aligned spawn helpers (`spawn_at_grid`, `spawn_at_grid_center`)
- [x] Walkability checking (`is_walkable`, `get_walkable_neighbors`)
- [x] ASCII maze loading (`load_from_ascii`)
- [x] List maze loading (`load_from_list`)
- [x] Tile rendering (`render`, `render_tile`)
- [x] Tile utilities (`count_tiles`, `find_tiles`)
- [x] **12 comprehensive unit tests** in `tests/test_sprites.py`
- [x] **ALL TESTS PASS**: 31/31 (19 Sprite + 12 TileMap) ✅

**Key Methods:**
```python
# Coordinate conversion
tilemap.pixel_to_grid(x, y) → (col, row)
tilemap.grid_to_pixel(col, row) → (x, y)
tilemap.grid_to_pixel_center(col, row) → (center_x, center_y)

# Sprite-tile collision (solves Pac-Man wall overlaps!)
tilemap.sprite_collides_with_tile(sprite, tile_id=1)
tilemap.get_sprite_tiles(sprite) → [(col, row), ...]

# Grid-aligned spawning (prevents wall overlaps)
player = tilemap.spawn_at_grid_center(col, row, width, height, color)

# Pathfinding helpers
tilemap.is_walkable(col, row)
tilemap.get_walkable_neighbors(col, row) → [(col, row), ...]

# Maze loading
tilemap.load_from_ascii(maze_string, {'#': 1, '.': 0})
tilemap.load_from_list(tile_array)
```

---

## Phase 3: Testing Integration (Day 3-4)

### 3.1 TestRunner Sprite Support
**File**: `matrixos/testing/runner.py`

Add methods:
```python
def get_sprites(self, color=None, tolerance=10):
    """Get sprite objects directly from app."""
    
def assert_sprite_in_bounds(self, sprite, bounds):
    """Assert sprite within bounds."""
    
def assert_sprite_not_in_wall(self, sprite, tilemap, wall_tile_id=1):
    """Assert sprite not colliding with wall tiles."""
    
def assert_sprites_not_overlapping(self, sprite1, sprite2):
    """Assert two sprites don't collide."""
```

### 3.2 Sprite Test Helpers
**File**: `matrixos/testing/sprite_helpers.py`

Utilities for common test patterns:
- Grid alignment validation
- Movement tracking
- Collision visualization
- Sprite state assertions

### 3.3 Documentation
**File**: `docs/TESTING.md`

Add section on sprite testing patterns.

---

## Phase 4: Emoji Sprite Support (Day 4)

### 4.1 Emoji to Sprite Converter
**File**: `matrixos/sprites.py` (add EmojiSprite class)

```python
class EmojiSprite(Sprite):
    """Sprite rendered from emoji."""
    
    def __init__(self, x, y, emoji, size=16):
        # Use existing emoji_loader system
        from matrixos.emoji_loader import load_emoji
        
        self.emoji = emoji
        self.size = size
        self.image = load_emoji(emoji, size)  # Returns PIL Image
        
        super().__init__(x, y, size, size, color=None)
    
    def render(self, matrix):
        """Render emoji to matrix."""
        if self.visible and self.image:
            # Convert PIL image to pixel array
            pixels = self.image.load()
            for dy in range(self.size):
                for dx in range(self.size):
                    if 0 <= dx < self.image.width and 0 <= dy < self.image.height:
                        r, g, b, a = pixels[dx, dy]
                        if a > 128:  # Non-transparent
                            matrix.set_pixel(
                                int(self.x + dx), 
                                int(self.y + dy), 
                                (r, g, b)
                            )
```

### 4.2 Sprite Sheet Support
**File**: `matrixos/sprite_sheet.py`

For animation frames:
```python
class SpriteSheet:
    """Load multiple sprites from emoji or image."""
    
    def __init__(self, emoji_list, size=16):
        """
        Args:
            emoji_list: ["🐸", "🐸", "🐸"] or ["walk1.png", "walk2.png"]
            size: Sprite size in pixels
        """
        self.frames = []
        for emoji in emoji_list:
            frame = load_emoji(emoji, size)
            self.frames.append(frame)
    
    def get_frame(self, index):
        """Get frame by index."""
        return self.frames[index % len(self.frames)]
```

### 4.3 Example Usage
```python
# Simple emoji sprite
pacman = EmojiSprite(64, 64, "🟡", size=12)

# Animated sprite
class AnimatedPacman(EmojiSprite):
    def __init__(self, x, y):
        super().__init__(x, y, "🟡", size=12)
        self.frames = SpriteSheet(["🟡", "🟠", "🔴"], size=12)
        self.frame_index = 0
        self.frame_timer = 0
    
    def update(self, delta_time):
        super().update(delta_time)
        self.frame_timer += delta_time
        if self.frame_timer >= 0.1:  # 10fps animation
            self.frame_index += 1
            self.frame_timer = 0
```

---

## Phase 5: Pac-Man Refactor (Day 5-6)

### 5.1 Create New Pac-Man with Sprites
**File**: `examples/pacman_v2/main.py`

**Changes:**
1. Use `TileMap` for maze
2. `PacMan` extends `Sprite`
3. `Ghost` extends `Sprite`
4. Use sprite collision detection
5. Grid-aligned spawn positions
6. Cleaner movement logic

**Estimated lines reduced:** 150-200 lines (30-40% smaller)

### 5.2 Comprehensive Tests
**File**: `tests/test_pacman_v2.py`

Tests using sprite framework:
```python
def test_pacman_spawn_position():
    """Test Pac-Man spawns in valid position."""
    runner = TestRunner("examples.pacman_v2.main", max_duration=10.0)
    game = runner.app
    
    # Direct sprite access
    assert game.pacman.x == 64, "Pac-Man x position"
    assert game.pacman.y == 112, "Pac-Man y position"
    
    # Check not in wall
    runner.assert_sprite_not_in_wall(game.pacman, game.tilemap)
    
def test_ghost_spawn_positions():
    """Test all ghosts spawn in valid positions."""
    runner = TestRunner("examples.pacman_v2.main", max_duration=10.0)
    game = runner.app
    
    for ghost in game.ghosts.sprites:
        runner.assert_sprite_not_in_wall(ghost, game.tilemap)
        
def test_pacman_movement():
    """Test Pac-Man moves correctly."""
    runner = TestRunner("examples.pacman_v2.main", max_duration=10.0)
    game = runner.app
    
    initial_x = game.pacman.x
    
    runner.inject(InputEvent.RIGHT)
    runner.wait(1.0)
    
    assert game.pacman.x > initial_x, "Pac-Man should move right"
    runner.assert_sprite_not_in_wall(game.pacman, game.tilemap)
    
def test_ghost_movement():
    """Test ghosts move over time."""
    runner = TestRunner("examples.pacman_v2.main", max_duration=10.0)
    game = runner.app
    
    initial_positions = [(g.x, g.y) for g in game.ghosts.sprites]
    
    runner.wait(3.0)
    
    moved_count = 0
    for i, ghost in enumerate(game.ghosts.sprites):
        if (ghost.x, ghost.y) != initial_positions[i]:
            moved_count += 1
    
    assert moved_count >= 2, f"At least 2 ghosts should move, {moved_count} moved"
```

### 5.3 Side-by-side comparison
Keep old `examples/pacman/` for reference, new one in `examples/pacman_v2/`

---

## Phase 6: Other Games (Day 6-7)

### 6.1 Snake Refactor
**File**: `examples/snake_v2/main.py`

**Benefits:**
- Snake segments as sprite list
- Food as sprite
- Simple collision: `snake.head.collides_with(food)`
- Grid-aligned automatically

### 6.2 Platformer Refactor
**File**: `examples/platformer_v2/main.py`

**Benefits:**
- Player as sprite with gravity
- Platforms as tilemap
- Enemies as sprite group
- Collision detection built-in

### 6.3 Frogger Refactor
**File**: `examples/frogger_v2/main.py`

**Benefits:**
- Frog as sprite
- Cars/logs as sprite groups
- Lane-based positioning easier
- Collision detection simpler

---

## Implementation Schedule

### Day 1 (Monday)
- [ ] Morning: Implement base Sprite class
- [ ] Afternoon: Implement SpriteGroup
- [ ] Evening: Write unit tests

### Day 2 (Tuesday)  
- [ ] Morning: Implement TileMap
- [ ] Afternoon: Maze loading utilities
- [ ] Evening: TileMap tests

### Day 3 (Wednesday)
- [ ] Morning: TestRunner sprite integration
- [ ] Afternoon: Sprite test helpers
- [ ] Evening: Documentation updates

### Day 4 (Thursday)
- [ ] Morning: EmojiSprite implementation
- [ ] Afternoon: SpriteSheet support
- [ ] Evening: Emoji sprite tests

### Day 5 (Friday)
- [ ] Morning: Start Pac-Man refactor
- [ ] Afternoon: Complete Pac-Man refactor
- [ ] Evening: Pac-Man tests

### Day 6 (Saturday)
- [ ] Morning: Snake refactor
- [ ] Afternoon: Platformer refactor
- [ ] Evening: Test all refactored games

### Day 7 (Sunday)
- [ ] Morning: Frogger refactor
- [ ] Afternoon: Documentation polish
- [ ] Evening: Update AGENTS.md with sprite patterns

---

## Emoji System Integration

Yes! The emoji system is perfect for sprites:

### Current System
```python
# matrixos/emoji_loader.py already has:
def load_emoji(emoji_char, size=16):
    """Load emoji as PIL Image at given size."""
    # Uses Noto Emoji font
    # Returns RGBA image
```

### How We'll Use It

**Simple static sprite:**
```python
class Coin(EmojiSprite):
    def __init__(self, x, y):
        super().__init__(x, y, "🪙", size=8)
```

**Animated sprite:**
```python
class Player(AnimatedSprite):
    def __init__(self, x, y):
        animations = {
            'idle': ["🧍"],
            'walk': ["🚶", "🚶‍♂️", "🚶"],
            'jump': ["🤸"]
        }
        super().__init__(x, y, animations, size=16)
```

**Custom game sprites:**
```python
# Pac-Man can use actual emoji
pacman = EmojiSprite(64, 64, "🟡", size=12)

# Or mix with custom rendering
class PacMan(Sprite):
    def render(self, matrix):
        # Custom yellow circle with mouth
        matrix.circle(self.x, self.y, 6, (255, 255, 0), fill=True)
        # ... mouth animation
```

### Benefits

1. **Rapid prototyping**: Drop in emoji, instant sprite
2. **Consistent style**: Emoji pack gives cohesive look
3. **Easy animation**: Multiple emoji = animation frames
4. **Fallback**: Can still do custom rendering when needed
5. **Icon reuse**: Same emoji in icon.json and as sprite

---

## File Structure After Implementation

```
matrixos/
├── sprites.py              # NEW: Core sprite system
├── sprite_sheet.py         # NEW: Animation frames
├── maze_loader.py          # NEW: Maze utilities
├── emoji_loader.py         # EXISTING: Already have this!
└── testing/
    ├── runner.py           # MODIFIED: Add sprite helpers
    └── sprite_helpers.py   # NEW: Sprite test utilities

examples/
├── pacman/                 # Original (keep for reference)
├── pacman_v2/              # NEW: Sprite-based version
├── snake_v2/               # NEW: Sprite-based version
└── platformer_v2/          # NEW: Sprite-based version

tests/
├── test_sprites.py         # NEW: Unit tests
├── test_tilemap.py         # NEW: TileMap tests
├── test_pacman_v2.py       # NEW: Sprite-based game tests
└── test_sprite_emoji.py    # NEW: Emoji sprite tests

docs/
├── SPRITES.md              # NEW: Sprite framework guide
└── API_REFERENCE.md        # MODIFIED: Add sprite API
```

---

## Success Criteria

**Phase 1 Complete when:**
- [ ] All unit tests pass (collision, movement, groups)
- [ ] Can create and render basic sprites
- [ ] SpriteGroup works correctly

**Phase 2 Complete when:**
- [ ] TileMap can load and render mazes
- [ ] Sprite-tile collision detection works
- [ ] Grid alignment utilities work

**Phase 3 Complete when:**
- [ ] TestRunner can access sprites directly
- [ ] Can assert on sprite positions/collisions
- [ ] Sprite test helpers documented

**Phase 4 Complete when:**
- [ ] EmojiSprite renders correctly
- [ ] SpriteSheet animations work
- [ ] Can use emoji for game sprites

**Phase 5 Complete when:**
- [ ] Pac-Man v2 is playable
- [ ] All tests pass
- [ ] No sprites overlap walls
- [ ] Movement works correctly

**Phase 6 Complete when:**
- [ ] All games refactored
- [ ] All tests pass
- [ ] Code reduction verified
- [ ] Documentation complete

---

## Risk Mitigation

**Risk: Performance issues**
- Mitigation: Profile early, use spatial hashing if needed
- Target: 60fps on 128×128 with 100+ sprites

**Risk: Breaking existing games**
- Mitigation: Keep old versions, create v2 variants
- No deletion until v2 proven

**Risk: Emoji rendering slow**
- Mitigation: Cache rendered emoji, use sprite sheets
- Pre-render common sprites at startup

**Risk: Testing framework changes break tests**
- Mitigation: Make sprite features additive
- Old tests continue working

---

## Next Immediate Steps

1. **Start now**: Create `matrixos/sprites.py` with base Sprite class
2. **Test early**: Write collision tests as we go
3. **Document continuously**: Update docs with each phase
4. **Get feedback**: Show working sprites ASAP for validation

Ready to begin implementation! 🚀
