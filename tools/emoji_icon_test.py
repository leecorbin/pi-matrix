#!/usr/bin/env python3
"""
Test script to render emoji as LED matrix icons.

Tests rendering emojis at 16x16 and 32x32 to see if this would work
as an alternative to hand-crafted icon.json files.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PIL import Image, ImageDraw, ImageFont
import json


def emoji_to_icon(emoji, size=32, font_size=None):
    """Render an emoji to a pixel array.
    
    Args:
        emoji: Single emoji character (e.g., "🕹️")
        size: Output size in pixels (16 or 32)
        font_size: Font size to use (defaults to size - 4)
    
    Returns:
        2D array of RGB tuples suitable for icon.json format
    """
    if font_size is None:
        font_size = size - 4
    
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to find a font that supports emojis
    fonts_to_try = [
        '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',  # Linux (installed!)
        '/usr/share/fonts/truetype/noto-color-emoji/NotoColorEmoji.ttf',  # Alt path
        '/System/Library/Fonts/Apple Color Emoji.ttc',        # macOS
        'seguiemj.ttf',                                        # Windows
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',    # Fallback with some symbols
    ]
    
    font = None
    font_path_used = None
    for font_path in fonts_to_try:
        try:
            font = ImageFont.truetype(font_path, font_size)
            font_path_used = font_path
            break
        except (OSError, IOError):
            continue
    
    if font is None:
        raise RuntimeError("No suitable emoji font found! Install fonts-noto-color-emoji")
    
    # Get text bounding box to center it
    try:
        bbox = draw.textbbox((0, 0), emoji, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        # Fallback for older Pillow versions
        text_width = size // 2
        text_height = size // 2
    
    # Center the emoji
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 2  # Slight upward adjustment
    
    # Draw the emoji
    try:
        draw.text((x, y), emoji, font=font, embedded_color=True)
    except Exception as e:
        # Fallback: try without embedded_color for simpler emojis
        try:
            draw.text((x, y), emoji, font=font, fill=(255, 255, 255))
        except Exception as e2:
            print(f"⚠️  Could not render emoji: {e}")
            # Draw a placeholder
            draw.rectangle([(2, 2), (size-2, size-2)], outline=(128, 128, 128), width=2)
    
    # Convert to RGB (flatten transparency)
    rgb_img = Image.new('RGB', (size, size), (0, 0, 0))
    rgb_img.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
    
    # Convert to 2D pixel array
    pixels = []
    for y in range(size):
        row = []
        for x in range(size):
            pixel = rgb_img.getpixel((x, y))
            row.append(list(pixel))
        pixels.append(row)
    
    return pixels


def save_icon_json(emoji, size, filename):
    """Save emoji icon as icon.json format."""
    pixels = emoji_to_icon(emoji, size)
    
    icon_data = {
        "format": "rgb",
        "pixels": pixels
    }
    
    with open(filename, 'w') as f:
        json.dump(icon_data, f, indent=2)
    
    print(f"✅ Saved {size}×{size} icon to {filename}")


def render_ascii_preview(emoji, size=32):
    """Show a rough ASCII preview of the emoji icon."""
    pixels = emoji_to_icon(emoji, size)
    
    print(f"\n{emoji} at {size}×{size} (ASCII preview):")
    print("┌" + "─" * size + "┐")
    
    for row in pixels:
        line = "│"
        for pixel in row:
            r, g, b = pixel
            # Convert to grayscale
            gray = (r + g + b) // 3
            # Pick ASCII character based on brightness
            if gray < 32:
                line += " "
            elif gray < 64:
                line += "."
            elif gray < 128:
                line += "o"
            elif gray < 192:
                line += "O"
            else:
                line += "█"
        line += "│"
        print(line)
    
    print("└" + "─" * size + "┘")


def test_emoji_gallery():
    """Test a variety of emojis to see how they look."""
    test_emojis = [
        ("🕹️", "joystick", "Gaming"),
        ("🎮", "gamepad", "Gaming"),
        ("👾", "alien", "Gaming"),
        ("🐍", "snake", "Snake game"),
        ("🧱", "brick", "Tetris/Breakout"),
        ("🏓", "paddle", "Breakout"),
        ("🐸", "frog", "Frogger"),
        ("👻", "ghost", "Pac-Man"),
        ("🌦️", "weather", "Weather app"),
        ("⏰", "clock", "Timer"),
        ("📊", "chart", "Dashboard"),
        ("🎨", "art", "Demos"),
    ]
    
    print("\n" + "="*60)
    print("EMOJI ICON GALLERY TEST")
    print("="*60)
    
    # Test at 32x32
    for emoji, name, description in test_emojis:
        print(f"\n{description}: {emoji} ({name})")
        render_ascii_preview(emoji, 32)
    
    # Save a few examples
    os.makedirs('/tmp/emoji_icons', exist_ok=True)
    
    print("\n" + "="*60)
    print("SAVING EXAMPLE ICON FILES")
    print("="*60)
    
    for emoji, name, description in test_emojis[:6]:
        save_icon_json(emoji, 32, f'/tmp/emoji_icons/{name}_32.json')
        save_icon_json(emoji, 16, f'/tmp/emoji_icons/{name}_16.json')
    
    print(f"\n📁 Example icons saved to: /tmp/emoji_icons/")


def test_specific_emoji(emoji, sizes=[16, 32]):
    """Test a specific emoji at different sizes."""
    print("\n" + "="*60)
    print(f"TESTING: {emoji}")
    print("="*60)
    
    for size in sizes:
        render_ascii_preview(emoji, size)
    
    # Save both sizes
    os.makedirs('/tmp/emoji_icons', exist_ok=True)
    for size in sizes:
        filename = f'/tmp/emoji_icons/test_{size}.json'
        save_icon_json(emoji, size, filename)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Test specific emoji from command line
        emoji = sys.argv[1]
        sizes = [int(s) for s in sys.argv[2:]] if len(sys.argv) > 2 else [16, 32]
        test_specific_emoji(emoji, sizes)
    else:
        # Run full gallery test
        test_emoji_gallery()
    
    print("\n" + "="*60)
    print("INTEGRATION FEASIBILITY")
    print("="*60)
    print("""
Feasibility: ✅ VERY DOABLE!

Pros:
  ✅ Much easier than hand-drawing icons
  ✅ Consistent style across all apps
  ✅ Huge variety of emojis available
  ✅ Zero artistic skill required
  ✅ Can be auto-generated on first run

Cons:
  ⚠️  Requires emoji font installed (NotoColorEmoji)
  ⚠️  Quality varies by emoji (some are too detailed)
  ⚠️  Black backgrounds (emojis designed for white)
  ⚠️  File size larger than palette format

Recommendation:
  Support BOTH formats:
    "icon": "🕹️"           → auto-render emoji
    "icon": "icon.json"    → load from file (custom art)
  
  Best of both worlds! 🎉
""")
