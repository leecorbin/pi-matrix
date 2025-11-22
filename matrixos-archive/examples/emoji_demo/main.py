"""
Emoji Demo - Showcase Emoji Rendering at 256×192
=================================================

Features:
- Grid of large emojis
- Cycling through different emoji sets
- Spectrum-colored borders and text
- Categories: Faces, Animals, Food, Objects, Symbols
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent

CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 40)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

class EmojiDemoApp(App):
    """Emoji showcase with Spectrum aesthetic"""
    
    def __init__(self):
        super().__init__("Emoji Demo")
        self.categories = [
            ("Faces", ["😀", "😎", "🤔", "😱", "🥳", "😴", "🤯", "😇", "😈", "🤖", "👽", "👻"]),
            ("Animals", ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁", "🐮"]),
            ("Food", ["🍎", "🍌", "🍇", "🍓", "🍕", "🍔", "🍟", "🍿", "🎂", "🍰", "🍪", "🍩"]),
            ("Objects", ["⚽", "🏀", "🎮", "🎸", "🎹", "🎺", "🎨", "🎭", "🎪", "🎬", "📱", "💻"]),
            ("Symbols", ["❤️", "💙", "💚", "💛", "⭐", "✨", "🌟", "💫", "🔥", "💧", "⚡", "🌈"]),
        ]
        self.category_index = 0
        self.scroll_offset = 0
    
    def on_event(self, event):
        if event.key == InputEvent.LEFT:
            self.category_index = (self.category_index - 1) % len(self.categories)
            self.scroll_offset = 0
            self.dirty = True
            return True
        elif event.key == InputEvent.RIGHT:
            self.category_index = (self.category_index + 1) % len(self.categories)
            self.scroll_offset = 0
            self.dirty = True
            return True
        elif event.key == InputEvent.UP:
            self.scroll_offset = max(0, self.scroll_offset - 1)
            self.dirty = True
            return True
        elif event.key == InputEvent.DOWN:
            self.scroll_offset += 1
            self.dirty = True
            return True
        return False
    
    def on_update(self, delta_time):
        # Optional: auto-cycle categories
        pass
    
    def render(self, matrix):
        matrix.clear()
        matrix.rect(0, 0, 256, 192, DARK_BLUE, fill=True)
        
        # Title
        category_name, emojis = self.categories[self.category_index]
        matrix.text(category_name.upper(), 80, 10, CYAN)
        
        # Draw emoji grid (4 columns × 3 rows)
        emoji_size = 48
        cols = 4
        start_x = 32
        start_y = 40
        
        for i, emoji in enumerate(emojis):
            if i >= self.scroll_offset and i < self.scroll_offset + 12:
                display_i = i - self.scroll_offset
                col = display_i % cols
                row = display_i // cols
                
                x = start_x + col * emoji_size
                y = start_y + row * emoji_size
                
                # Draw emoji (placeholder - actual emoji rendering would use PIL)
                matrix.text(emoji, x, y, WHITE)
        
        # Navigation
        matrix.text("<", 10, 90, YELLOW if self.category_index > 0 else WHITE)
        matrix.text(">", 240, 90, YELLOW if self.category_index < len(self.categories) - 1 else WHITE)
        
        # Instructions
        matrix.text("< PREV", 10, 175, CYAN)
        matrix.text("NEXT >", 190, 175, CYAN)
        
        self.dirty = False


def run(os_context):
    app = EmojiDemoApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()
