#!/usr/bin/env python3
"""
Test emoji icon loading in the launcher
"""

import sys
import os
sys.path.insert(0, '/home/lee/led-matrix-project')

from matrixos.builtin_apps.launcher import App

print("="*70)
print("Testing Emoji Icon Loading")
print("="*70)

test_apps = [
    '/home/lee/led-matrix-project/apps/snake',
    '/home/lee/led-matrix-project/apps/tetris',
    '/home/lee/led-matrix-project/apps/breakout',
    '/home/lee/led-matrix-project/apps/weather',
    '/home/lee/led-matrix-project/apps/timer',
    '/home/lee/led-matrix-project/apps/demos',
]

for app_path in test_apps:
    if not os.path.exists(app_path):
        print(f"❌ {app_path} not found")
        continue
    
    app = App(app_path)
    
    print(f"\n{app.name}:")
    print(f"  Emoji: {app.emoji_icon if app.emoji_icon else 'None'}")
    print(f"  Icon loaded: {'✅' if app.icon_pixels else '❌'}")
    
    if app.icon_pixels:
        print(f"  Format: {app.icon_format}")
        print(f"  Size: {app.icon_native_size}×{app.icon_native_size}")
        
        # Count non-transparent pixels
        pixel_count = 0
        for row in app.icon_pixels:
            for pixel in row:
                if pixel is not None:
                    pixel_count += 1
        
        print(f"  Non-transparent pixels: {pixel_count}")

print("\n" + "="*70)
print("✨ Test complete!")
