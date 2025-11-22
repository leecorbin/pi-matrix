# Pac-Man Bug Analysis Report

## Executive Summary
Pac-Man game appears frozen - neither Pac-Man nor ghosts move despite accepting input.

## Root Cause
**File:** `examples/pacman/main.py`  
**Lines:** 350-351  
**Issue:** Empty `on_activate()` method overrides base class behavior

```python
def on_activate(self):
    """App activated."""
    pass  # ❌ This breaks the dirty flag pattern!
```

## Technical Explanation

### The Dirty Flag Pattern
MatrixOS uses a "dirty flag" pattern for rendering:
1. When `self.dirty = True`, the framework calls `render()`
2. After rendering, app sets `self.dirty = False`
3. When state changes, app sets `self.dirty = True` again

### Base Class Behavior
The `App` base class (`matrixos/app_framework.py` line 54) sets the initial dirty flag:

```python
def on_activate(self):
    """Called when app becomes the foreground app."""
    self.dirty = True  # Always redraw on activation
```

### The Bug
Pac-Man **overrides** `on_activate()` with an empty method, which:
1. Prevents `self.dirty = True` from being set initially
2. Without dirty flag, `on_update()` never runs
3. Without `on_update()`, game logic doesn't execute
4. Result: Static screen, no movement

## Evidence from Testing

###Test Output:
```
[DEBUG] Pac-Man pos: (64, 112) dir: (0, 0)
[DEBUG] Ghost 0 pos: (64, 8) dir: (0, 0)
```

- Positions are logged (so `on_update()` runs at least once)
- Direction is always `(0, 0)` - not moving
- After pressing arrow keys, positions don't change

## The Fix

**Option 1:** Remove the empty override (recommended)
```python
# Delete lines 350-351
# Let base class handle activation
```

**Option 2:** Call parent class
```python
def on_activate(self):
    """App activated."""
    super().on_activate()  # ✓ Sets self.dirty = True
```

**Option 3:** Set dirty flag manually
```python
def on_activate(self):
    """App activated."""
    self.dirty = True  # ✓ Trigger initial render
```

## Why This Wasn't Caught Earlier

1. **No compile error** - Valid Python syntax
2. **Game renders once** - Initial `__init__` sets `self.dirty = True`
3. **Static screen looks correct** - Maze, Pac-Man, ghosts all visible
4. **Subtle behavioral bug** - Requires playing to notice

## Related Issues

The same pattern appears in `on_deactivate()`:
```python
def on_deactivate(self):
    """App deactivated."""
    pass  # This is OK - base class method is also empty
```

This one is harmless since the base class method is also empty.

## Prevention

This bug violates the documented pattern in AGENTS.md:

> ### 3. Dirty Flag Pattern
> - Set `dirty=True` after EVERY state change
> - Clear `dirty=False` at end of render()
> - **Set initial `dirty=True` in `__init__()` or `on_activate()`**

## Testing Validation

Our testing framework successfully identified this bug:
1. ✓ Game renders (static frame works)
2. ❌ Pac-Man doesn't move after input
3. ❌ Ghosts don't move over time
4. ❌ Direction vectors stay at (0, 0)

## Recommendation

**Apply Option 1** - Remove lines 350-351 entirely. The base class behavior is exactly what we need, and overriding it with `pass` serves no purpose.
