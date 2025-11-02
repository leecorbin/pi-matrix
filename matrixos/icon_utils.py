"""
Icon utilities for MatrixOS.

Supports multiple icon formats:
- RGB: [[[r,g,b], ...], ...] arrays
- Hex: [["#RRGGBB", ...], ...] strings
- Palette: [[0-7, ...], ...] indices
- PNG: Load from PNG image files

Example:
    from matrixos.icon_utils import load_icon, png_to_rgb
    
    # Convert PNG to RGB format
    rgb_data = png_to_rgb('icon.png', size=32)
    
    # Save as JSON
    import json
    with open('icon32.json', 'w') as f:
        json.dump({'format': 'rgb', 'pixels': rgb_data}, f, indent=2)
"""

import json
from typing import Optional, List, Tuple
from pathlib import Path


def png_to_rgb(png_path: str, size: int = 32, 
               transparent_color: Optional[Tuple[int, int, int]] = None) -> List:
    """
    Convert PNG image to RGB icon format.
    
    Args:
        png_path: Path to PNG file
        size: Target size (will be resized to size×size)
        transparent_color: RGB color to treat as transparent (default: None = alpha channel)
        
    Returns:
        RGB pixel array: [[[r,g,b], ...], ...] with null for transparent pixels
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("PIL/Pillow required for PNG support. Install with: pip install Pillow")
    
    # Load and resize image
    img = Image.open(png_path)
    img = img.resize((size, size), Image.Resampling.NEAREST)  # Use nearest for pixel art
    
    # Convert to RGBA
    img = img.convert('RGBA')
    
    # Extract pixels
    pixels = []
    for y in range(size):
        row = []
        for x in range(size):
            r, g, b, a = img.getpixel((x, y))
            
            # Check transparency
            if a < 128:  # Alpha threshold
                row.append(None)
            elif transparent_color and (r, g, b) == transparent_color:
                row.append(None)
            else:
                row.append([r, g, b])
        
        pixels.append(row)
    
    return pixels


def rgb_to_png(rgb_data: List, output_path: str):
    """
    Convert RGB icon data to PNG file.
    
    Args:
        rgb_data: RGB pixel array [[[r,g,b], ...], ...] with null for transparent
        output_path: Path to save PNG file
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("PIL/Pillow required for PNG support. Install with: pip install Pillow")
    
    size = len(rgb_data)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    for y in range(size):
        for x in range(size):
            pixel = rgb_data[y][x]
            if pixel is None:
                # Transparent
                img.putpixel((x, y), (0, 0, 0, 0))
            else:
                # Opaque with RGB color
                r, g, b = pixel
                img.putpixel((x, y), (r, g, b, 255))
    
    img.save(output_path)


def create_icon_from_png(png_path: str, output_json: str, size: int = 32):
    """
    Convert PNG to JSON icon file.
    
    Args:
        png_path: Input PNG file
        output_json: Output JSON file path
        size: Icon size (default: 32)
    """
    rgb_data = png_to_rgb(png_path, size)
    
    icon_data = {
        'format': 'rgb',
        'pixels': rgb_data
    }
    
    with open(output_json, 'w') as f:
        json.dump(icon_data, f, indent=2)
    
    print(f"Created {output_json} from {png_path} ({size}×{size})")


def load_icon_with_png_fallback(icon_path: str, png_fallback: Optional[str] = None) -> dict:
    """
    Load icon from JSON, with optional PNG fallback.
    
    Args:
        icon_path: Path to icon JSON file
        png_fallback: Optional PNG file to try if JSON doesn't exist
        
    Returns:
        Icon data dict with 'format' and 'pixels'
    """
    # Try JSON first
    if Path(icon_path).exists():
        with open(icon_path, 'r') as f:
            return json.load(f)
    
    # Try PNG fallback
    if png_fallback and Path(png_fallback).exists():
        size = 32 if '32' in icon_path else 16
        rgb_data = png_to_rgb(png_fallback, size)
        return {'format': 'rgb', 'pixels': rgb_data}
    
    # Not found
    raise FileNotFoundError(f"Icon not found: {icon_path}")


# Command-line tool
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python icon_utils.py <input.png> <output.json> [size]")
        print("Example: python icon_utils.py myicon.png icon32.json 32")
        sys.exit(1)
    
    input_png = sys.argv[1]
    output_json = sys.argv[2]
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 32
    
    create_icon_from_png(input_png, output_json, size)
