#!/usr/bin/env python3
"""
Bundle Popular Emoji Icons for MatrixOS

Downloads commonly-used emoji from Noto Emoji repository and converts them
to MatrixOS icon format. This creates a large cache of popular emojis that
work offline.

Sources for popularity:
- Unicode Consortium frequency data (2019)
- MatrixOS specific use cases (gaming, weather, UI)
"""

import os
import urllib.request
import json
from PIL import Image
import io


# Popular emojis to bundle (curated list)
# Format: (emoji, codepoint, category, description)
BUNDLED_EMOJIS = [
    # Top tier - most popular overall (Unicode data)
    ("😂", "1f602", "faces", "joy"),
    ("❤️", "2764", "symbols", "red heart"),
    ("😍", "1f60d", "faces", "heart eyes"),
    ("😊", "1f60a", "faces", "smiling"),
    ("🙏", "1f64f", "hands", "prayer"),
    ("💕", "1f495", "symbols", "two hearts"),
    ("😭", "1f62d", "faces", "crying"),
    ("😘", "1f618", "faces", "kiss"),
    ("👍", "1f44d", "hands", "thumbs up"),
    ("😅", "1f605", "faces", "sweat smile"),
    ("👏", "1f44f", "hands", "clap"),
    ("🔥", "1f525", "symbols", "fire"),
    ("💔", "1f494", "symbols", "broken heart"),
    ("💙", "1f499", "symbols", "blue heart"),
    ("😢", "1f622", "faces", "cry"),
    ("🤔", "1f914", "faces", "thinking"),
    ("😆", "1f606", "faces", "laugh"),
    ("💪", "1f4aa", "hands", "muscle"),
    ("😉", "1f609", "faces", "wink"),
    ("👌", "1f44c", "hands", "ok"),
    ("💜", "1f49c", "symbols", "purple heart"),
    ("😎", "1f60e", "faces", "cool"),
    ("🌹", "1f339", "nature", "rose"),
    ("🎉", "1f389", "activities", "party"),
    ("✨", "2728", "symbols", "sparkles"),
    ("😱", "1f631", "faces", "scream"),
    ("😌", "1f60c", "faces", "relieved"),
    ("🌸", "1f338", "nature", "flower"),
    ("🙌", "1f64c", "hands", "praise"),
    ("💗", "1f497", "symbols", "growing heart"),
    ("💚", "1f49a", "symbols", "green heart"),
    ("😏", "1f60f", "faces", "smirk"),
    ("💛", "1f49b", "symbols", "yellow heart"),
    ("😀", "1f600", "faces", "grin"),
    ("🙈", "1f648", "animals", "see no evil"),
    ("⭐", "2b50", "symbols", "star"),
    ("✅", "2705", "symbols", "check"),
    ("🌈", "1f308", "nature", "rainbow"),
    
    # Gaming (MatrixOS specific)
    ("🕹️", "1f579", "gaming", "joystick"),
    ("🎮", "1f3ae", "gaming", "gamepad"),
    ("👾", "1f47e", "gaming", "alien"),
    ("🎯", "1f3af", "gaming", "target"),
    ("🎲", "1f3b2", "gaming", "dice"),
    ("🏆", "1f3c6", "gaming", "trophy"),
    ("⚔️", "2694", "gaming", "swords"),
    ("🛡️", "1f6e1", "gaming", "shield"),
    ("🎰", "1f3b0", "gaming", "slot machine"),
    
    # Games we have
    ("🐍", "1f40d", "games", "snake"),
    ("🧱", "1f9f1", "games", "brick"),
    ("🏓", "1f3d3", "games", "ping pong"),
    ("🐸", "1f438", "games", "frog"),
    ("👻", "1f47b", "games", "ghost"),
    ("🍒", "1f352", "games", "cherries"),
    ("🍎", "1f34e", "games", "apple"),
    
    # Time & alarms
    ("⏰", "23f0", "time", "alarm"),
    ("⏲️", "23f2", "time", "timer"),
    ("⏱️", "23f1", "time", "stopwatch"),
    ("⌚", "231a", "time", "watch"),
    ("📅", "1f4c5", "time", "calendar"),
    ("🕐", "1f550", "time", "1 oclock"),
    ("🕑", "1f551", "time", "2 oclock"),
    ("🕒", "1f552", "time", "3 oclock"),
    
    # Weather
    ("☀️", "2600", "weather", "sun"),
    ("☁️", "2601", "weather", "cloud"),
    ("🌧️", "1f327", "weather", "rain"),
    ("⛈️", "26c8", "weather", "thunder"),
    ("❄️", "2744", "weather", "snow"),
    ("🌦️", "1f326", "weather", "sun behind rain"),
    ("🌤️", "1f324", "weather", "sun behind cloud"),
    ("⛅", "26c5", "weather", "partly sunny"),
    ("🌡️", "1f321", "weather", "thermometer"),
    ("💨", "1f4a8", "weather", "wind"),
    ("🌪️", "1f32a", "weather", "tornado"),
    ("🌈", "1f308", "weather", "rainbow"),
    
    # UI elements
    ("▶️", "25b6", "ui", "play"),
    ("⏸️", "23f8", "ui", "pause"),
    ("⏹️", "23f9", "ui", "stop"),
    ("⏭️", "23ed", "ui", "next"),
    ("⏮️", "23ee", "ui", "previous"),
    ("🔄", "1f504", "ui", "reload"),
    ("🔀", "1f500", "ui", "shuffle"),
    ("🔁", "1f501", "ui", "repeat"),
    ("ℹ️", "2139", "ui", "info"),
    ("❓", "2753", "ui", "question"),
    ("❗", "2757", "ui", "exclamation"),
    ("⚠️", "26a0", "ui", "warning"),
    ("🏠", "1f3e0", "ui", "home"),
    ("⚙️", "2699", "ui", "settings"),
    ("🔍", "1f50d", "ui", "search"),
    ("📊", "1f4ca", "ui", "chart"),
    ("📈", "1f4c8", "ui", "trending up"),
    ("📉", "1f4c9", "ui", "trending down"),
    ("🔔", "1f514", "ui", "bell"),
    ("🔕", "1f515", "ui", "bell slash"),
    ("💡", "1f4a1", "ui", "bulb"),
    ("🔋", "1f50b", "ui", "battery"),
    ("📶", "1f4f6", "ui", "signal"),
    
    # Art & media
    ("🎨", "1f3a8", "media", "art"),
    ("📷", "1f4f7", "media", "camera"),
    ("📸", "1f4f8", "media", "camera flash"),
    ("📺", "1f4fa", "media", "tv"),
    ("🎵", "1f3b5", "media", "music"),
    ("🎶", "1f3b6", "media", "notes"),
    ("🔊", "1f50a", "media", "speaker"),
    ("🔇", "1f507", "media", "mute"),
    
    # Numbers (useful for menus)
    ("0️⃣", "0030-20e3", "numbers", "0"),
    ("1️⃣", "0031-20e3", "numbers", "1"),
    ("2️⃣", "0032-20e3", "numbers", "2"),
    ("3️⃣", "0033-20e3", "numbers", "3"),
    ("4️⃣", "0034-20e3", "numbers", "4"),
    ("5️⃣", "0035-20e3", "numbers", "5"),
    ("6️⃣", "0036-20e3", "numbers", "6"),
    ("7️⃣", "0037-20e3", "numbers", "7"),
    ("8️⃣", "0038-20e3", "numbers", "8"),
    ("9️⃣", "0039-20e3", "numbers", "9"),
    ("🔟", "1f51f", "numbers", "10"),
    
    # Misc useful
    ("📝", "1f4dd", "misc", "memo"),
    ("📌", "1f4cc", "misc", "pin"),
    ("🎁", "1f381", "misc", "gift"),
    ("🎂", "1f382", "misc", "cake"),
    ("🌟", "1f31f", "misc", "glowing star"),
    ("💫", "1f4ab", "misc", "dizzy"),
    ("🚀", "1f680", "misc", "rocket"),
    ("🔗", "1f517", "misc", "link"),
]


def emoji_to_codepoint(emoji):
    """Convert emoji character to hex codepoint string."""
    codepoints = []
    for char in emoji:
        cp = ord(char)
        # Skip variation selectors in codepoint
        if cp == 0xFE0F:  # Emoji presentation selector
            continue
        codepoints.append(f"{cp:04x}")
    return "-".join(codepoints)


def download_noto_emoji(codepoint, size=32):
    """Download emoji PNG from Noto Emoji repository.
    
    Args:
        codepoint: Emoji codepoint (e.g., "1f579")
        size: Size (32 or 128)
    
    Returns:
        PIL Image or None if failed
    """
    url = f"https://raw.githubusercontent.com/googlefonts/noto-emoji/main/png/{size}/emoji_u{codepoint}.png"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            img_data = response.read()
            return Image.open(io.BytesIO(img_data))
    except Exception as e:
        print(f"  ❌ Failed to download {codepoint}: {e}")
        return None


def image_to_icon_json(img, size=32):
    """Convert PIL Image to MatrixOS icon JSON format."""
    # Ensure correct size
    if img.size != (size, size):
        img = img.resize((size, size), Image.LANCZOS)
    
    # Convert to RGBA
    img = img.convert('RGBA')
    
    # Extract pixels
    pixels = []
    for y in range(size):
        row = []
        for x in range(size):
            r, g, b, a = img.getpixel((x, y))
            # If mostly transparent, use None
            if a < 128:
                row.append(None)
            else:
                row.append([r, g, b])
        pixels.append(row)
    
    return {
        "format": "rgb",
        "pixels": pixels,
        "source": "Noto Color Emoji (Google) - Apache 2.0"
    }


def bundle_emojis(output_dir='matrixos/emoji_bundle', sizes=[32]):
    """Download and bundle all popular emojis."""
    os.makedirs(output_dir, exist_ok=True)
    
    print("="*60)
    print(f"Bundling {len(BUNDLED_EMOJIS)} Popular Emojis")
    print("="*60)
    
    success_count = 0
    fail_count = 0
    total_size = 0
    
    # Create manifest
    manifest = {}
    
    for emoji, codepoint, category, description in BUNDLED_EMOJIS:
        print(f"\n{emoji}  {description} ({codepoint})")
        
        emoji_success = True
        for size in sizes:
            # Download
            img = download_noto_emoji(codepoint, size)
            if img is None:
                emoji_success = False
                continue
            
            # Convert to icon JSON
            icon_data = image_to_icon_json(img, size)
            
            # Save
            filename = f"{codepoint}_{size}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(icon_data, f)
            
            file_size = os.path.getsize(filepath)
            total_size += file_size
            
            print(f"  ✅ {size}×{size}: {file_size:,} bytes")
        
        if emoji_success:
            success_count += 1
            # Add to manifest
            manifest[emoji] = {
                "codepoint": codepoint,
                "category": category,
                "description": description,
                "sizes": sizes
            }
        else:
            fail_count += 1
    
    # Save manifest
    manifest_path = os.path.join(output_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False, sort_keys=True)
    
    print("\n" + "="*60)
    print(f"✅ Successfully bundled: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📁 Total size: {total_size / 1024 / 1024:.2f} MB")
    print(f"📁 Saved to: {output_dir}/")
    print(f"📄 Manifest: {manifest_path}")
    print("="*60)


# Fallback emoji for when requested emoji doesn't exist
FALLBACK_EMOJI = ("❓", "2753", "ui", "question mark")


def create_fallback_icon(output_dir='matrixos/emoji_bundle'):
    """Create the fallback question mark icon."""
    print("\nCreating fallback icon...")
    
    emoji, codepoint, category, description = FALLBACK_EMOJI
    img = download_noto_emoji(codepoint, 32)
    
    if img:
        icon_data = image_to_icon_json(img, 32)
        filepath = os.path.join(output_dir, 'fallback_32.json')
        
        with open(filepath, 'w') as f:
            json.dump(icon_data, f)
        
        print(f"✅ Fallback icon saved: {filepath}")
        return True
    else:
        print("❌ Failed to create fallback icon")
        return False


if __name__ == '__main__':
    import sys
    
    # Check for PIL
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow (PIL) required!")
        print("Install with: sudo apt-get install python3-pil")
        sys.exit(1)
    
    # Bundle emojis
    bundle_emojis()
    
    # Create fallback
    create_fallback_icon()
    
    print("\n💡 Usage in launcher:")
    print('  1. Check matrixos/emoji_bundle/{codepoint}_32.json')
    print('  2. If not found, download from Noto Emoji')
    print('  3. If download fails, use fallback_32.json')
