"""
News - ZX Spectrum RSS Reader for 256×192
==========================================

Features:
- Scrolling news headlines
- Multiple news sources
- Spectrum-styled text display
- Article preview area
- Side panels with indicators
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent

CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 40)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

class NewsApp(App):
    """Mock news reader with Spectrum aesthetic"""
    
    def __init__(self):
        super().__init__("News")
        # Mock news articles
        self.articles = [
            ("Tech", "New AI breakthrough announced", "Scientists develop faster algorithms..."),
            ("Science", "Mars mission scheduled for 2026", "NASA plans ambitious journey..."),
            ("Sports", "Championship game tonight", "Teams prepare for finals..."),
            ("Weather", "Sunny forecast this week", "Clear skies expected..."),
            ("Business", "Markets reach new highs", "Investors celebrate gains..."),
            ("World", "International summit begins", "Leaders gather for talks..."),
        ]
        self.selected = 0
        self.scroll_offset = 0
    
    def on_event(self, event):
        if event.key == InputEvent.UP:
            self.selected = max(0, self.selected - 1)
            self.dirty = True
            return True
        elif event.key == InputEvent.DOWN:
            self.selected = min(len(self.articles) - 1, self.selected + 1)
            self.dirty = True
            return True
        return False
    
    def on_update(self, delta_time):
        # Auto-scroll current article
        self.scroll_offset += 1
        self.dirty = True
    
    def render(self, matrix):
        matrix.clear()
        matrix.rect(0, 0, 256, 192, DARK_BLUE, fill=True)
        
        # Title bar
        matrix.text("NEWS READER", 70, 10, CYAN)
        matrix.rect(0, 22, 256, 2, CYAN, fill=True)
        
        # Headlines list (left side)
        y = 30
        for i, (category, headline, preview) in enumerate(self.articles):
            if i == self.selected:
                # Highlighted
                matrix.rect(5, y - 2, 150, 12, YELLOW)
                matrix.text(f"{category}:", 10, y, DARK_BLUE)
                matrix.text(headline[:18], 50, y, DARK_BLUE)
            else:
                # Normal
                matrix.text(f"{category}:", 10, y, GREEN)
                matrix.text(headline[:18], 50, y, WHITE)
            y += 15
        
        # Preview pane (right side)
        matrix.rect(160, 28, 90, 135, CYAN)
        matrix.text("PREVIEW", 165, 32, YELLOW)
        
        if self.selected < len(self.articles):
            category, headline, preview = self.articles[self.selected]
            # Word wrap preview
            words = preview.split()
            line = ""
            py = 45
            for word in words:
                if len(line + word) > 10:
                    matrix.text(line, 165, py, WHITE)
                    py += 10
                    line = word + " "
                else:
                    line += word + " "
            if line:
                matrix.text(line, 165, py, WHITE)
        
        # Instructions
        matrix.text("UP/DOWN: SELECT", 10, 175, CYAN)
        
        # Status indicators
        matrix.text(f"{self.selected + 1}/{len(self.articles)}", 200, 175, YELLOW)
        
        self.dirty = False


def run(os_context):
    app = NewsApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()
