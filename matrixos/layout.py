"""
Layout utilities for resolution-agnostic display code.
Helps create displays that adapt to any matrix size.
"""


def scale_value(base_value, current_size, base_size=64):
    """
    Scale a value proportionally based on current vs base resolution.

    Args:
        base_value: The value at base resolution
        current_size: Current resolution dimension
        base_size: Base resolution (default 64)

    Returns:
        Scaled value (rounded to int)
    """
    return int(base_value * current_size / base_size)


def center_x(width, item_width):
    """Calculate X position to center an item."""
    return (width - item_width) // 2


def center_y(height, item_height):
    """Calculate Y position to center an item."""
    return (height - item_height) // 2


def grid_cols(width, char_width=8):
    """Calculate number of character columns available."""
    return width // char_width


def grid_rows(height, char_height=8):
    """Calculate number of character rows available."""
    return height // char_height


def grid_to_pixel_x(col, char_width=8):
    """Convert grid column to pixel X coordinate."""
    return col * char_width


def grid_to_pixel_y(row, char_height=8):
    """Convert grid row to pixel Y coordinate."""
    return row * char_height


def clamp(value, min_val, max_val):
    """Clamp value between min and max."""
    return max(min_val, min(value, max_val))


def safe_bounds(x, y, width, height, matrix_width, matrix_height):
    """
    Ensure coordinates and dimensions are within matrix bounds.

    Returns:
        Tuple of (clamped_x, clamped_y, safe_width, safe_height)
    """
    x = clamp(x, 0, matrix_width - 1)
    y = clamp(y, 0, matrix_height - 1)
    width = clamp(width, 1, matrix_width - x)
    height = clamp(height, 1, matrix_height - y)
    return x, y, width, height


class LayoutHelper:
    """
    Helper class for resolution-agnostic layouts.
    Stores matrix dimensions and provides scaling utilities.
    """

    def __init__(self, matrix_width, matrix_height, base_width=64, base_height=64):
        """
        Initialize layout helper.

        Args:
            matrix_width: Current matrix width
            matrix_height: Current matrix height
            base_width: Base width for scaling (default 64)
            base_height: Base height for scaling (default 64)
        """
        self.width = matrix_width
        self.height = matrix_height
        self.base_width = base_width
        self.base_height = base_height

        # Calculate scaling factors
        self.scale_x = matrix_width / base_width
        self.scale_y = matrix_height / base_height

        # Character grid info
        self.cols = grid_cols(matrix_width)
        self.rows = grid_rows(matrix_height)

    def scale_x_value(self, value):
        """Scale a horizontal value."""
        return int(value * self.scale_x)

    def scale_y_value(self, value):
        """Scale a vertical value."""
        return int(value * self.scale_y)

    def scale_size(self, width, height):
        """Scale width and height."""
        return self.scale_x_value(width), self.scale_y_value(height)

    def center_x(self, item_width):
        """Calculate centered X position."""
        return center_x(self.width, item_width)

    def center_y(self, item_height):
        """Calculate centered Y position."""
        return center_y(self.height, item_height)

    def center_point(self, item_width, item_height):
        """Calculate centered position (x, y)."""
        return self.center_x(item_width), self.center_y(item_height)

    def grid_center_x(self):
        """Get center column in character grid."""
        return self.cols // 2

    def grid_center_y(self):
        """Get center row in character grid."""
        return self.rows // 2

    def safe_bounds(self, x, y, width, height):
        """Ensure coordinates are within bounds."""
        return safe_bounds(x, y, width, height, self.width, self.height)


# ============================================================================
# High-level UI helpers for common patterns
# ============================================================================


def center_text(matrix, text, y=None, color=(255, 255, 255)):
    """Draw text centered horizontally.
    
    Args:
        matrix: Display matrix
        text: Text to draw
        y: Vertical position (None = center vertically too)
        color: Text color
    """
    char_width = 8
    text_width = len(text) * char_width
    x = (matrix.width - text_width) // 2
    
    if y is None:
        # Center vertically too
        y = (matrix.height - 8) // 2
    
    matrix.text(text, x, y, color)


def get_grid_dimensions(matrix, item_size, padding=2):
    """Calculate grid layout dimensions.
    
    Args:
        matrix: Display matrix
        item_size: Size of each grid item (square)
        padding: Space between items
        
    Returns:
        (columns, rows) that fit on screen
    """
    cols = (matrix.width + padding) // (item_size + padding)
    rows = (matrix.height + padding) // (item_size + padding)
    return (cols, rows)


def grid_position(index, cols, item_size, padding=2, offset_x=0, offset_y=0):
    """Calculate x,y position for grid item.
    
    Args:
        index: Item index (0-based)
        cols: Number of columns in grid
        item_size: Size of each grid item
        padding: Space between items
        offset_x: Left margin
        offset_y: Top margin
        
    Returns:
        (x, y) position for item
    """
    row = index // cols
    col = index % cols
    x = offset_x + col * (item_size + padding)
    y = offset_y + row * (item_size + padding)
    return (x, y)


def draw_progress_bar(matrix, x, y, width, height, progress, 
                      fg_color=(0, 255, 0), bg_color=(50, 50, 50)):
    """Draw a progress bar.
    
    Args:
        matrix: Display matrix
        x, y: Top-left position
        width, height: Bar dimensions
        progress: Progress value (0.0 to 1.0)
        fg_color: Foreground (filled) color
        bg_color: Background color
    """
    # Background
    matrix.rect(x, y, width, height, bg_color, fill=True)
    
    # Progress fill
    fill_width = int(width * max(0.0, min(1.0, progress)))
    if fill_width > 0:
        matrix.rect(x, y, fill_width, height, fg_color, fill=True)


def draw_icon_with_text(matrix, icon_char, text, x, y, 
                        icon_color=(255, 255, 0), text_color=(255, 255, 255)):
    """Draw an icon character followed by text.
    
    Args:
        matrix: Display matrix
        icon_char: Single character icon (use extended glyphs)
        text: Text to draw next to icon
        x, y: Top-left position
        icon_color: Icon color
        text_color: Text color
        
    Returns:
        Width of drawn content
    """
    matrix.text(icon_char, x, y, icon_color)
    matrix.text(text, x + 10, y, text_color)
    return 10 + len(text) * 8


def menu_list(matrix, items, selected_index, y_start=14, item_height=9, 
              highlight_color=(255, 200, 0), text_color=(150, 150, 150),
              max_visible=6):
    """Draw a scrollable menu list.
    
    Args:
        matrix: Display matrix
        items: List of menu item strings
        selected_index: Currently selected item index
        y_start: Starting Y position
        item_height: Height of each menu item
        highlight_color: Color for selected item
        text_color: Color for unselected items
        max_visible: Maximum visible items (for scrolling)
    """
    width = matrix.width
    visible_items = min(max_visible, len(items))
    
    # Calculate scroll offset
    if len(items) > visible_items:
        scroll_start = max(0, min(selected_index - 2, len(items) - visible_items))
        items_to_show = items[scroll_start:scroll_start + visible_items]
        selected_offset = selected_index - scroll_start
    else:
        items_to_show = items
        selected_offset = selected_index
    
    y = y_start
    for i, item in enumerate(items_to_show):
        is_selected = (i == selected_offset)
        
        if is_selected:
            # Highlight selected
            matrix.rect(2, y - 1, width - 4, 8, highlight_color, fill=True)
            matrix.text(">", 4, y, (0, 0, 0))
            matrix.text(item.upper(), 12, y, (0, 0, 0))
        else:
            matrix.text(item.upper(), 12, y, text_color)
        
        y += item_height


def get_icon_size(matrix):
    """Get appropriate icon size for display resolution.
    
    Args:
        matrix: Display matrix
        
    Returns:
        Icon size in pixels (16 for 64×64, 32 for 128×128, 48 for 256×192)
    """
    if matrix.width >= 256 or matrix.height >= 192:
        return 48
    elif matrix.width >= 128 or matrix.height >= 128:
        return 32
    else:
        return 16


def split_columns(matrix, num_columns=2, padding=4):
    """Calculate column positions for multi-column layout.
    
    Args:
        matrix: Display matrix
        num_columns: Number of columns
        padding: Space between columns
        
    Returns:
        List of (x, width) tuples for each column
    """
    total_padding = padding * (num_columns - 1)
    column_width = (matrix.width - total_padding) // num_columns
    
    columns = []
    x = 0
    for i in range(num_columns):
        columns.append((x, column_width))
        x += column_width + padding
    
    return columns
