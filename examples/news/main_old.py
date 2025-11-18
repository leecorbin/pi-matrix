#!/usr/bin/env python3
"""
News Headlines - Live news from RSS feeds

Features:
- Scrolling news headlines
- Multiple news sources
- Auto-refresh
- Category selection
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent


class NewsApp(App):
    """News headlines app with scrolling text."""
    
    def __init__(self):
        super().__init__("News")
        self.headlines = []
        self.current_index = 0
        self.scroll_x = 128
        self.last_update = 0
        self.update_interval = 300  # 5 minutes
        self.scroll_speed = 1
        self.loading = True
        
    def on_activate(self):
        """Initialize app."""
        self.current_index = 0
        self.scroll_x = 128
        self.loading = True
        self.load_headlines()
        self.dirty = True
    
    def load_headlines(self):
        """Load news headlines from RSS/API."""
        # Simulated headlines (in production, would fetch from RSS feeds or NewsAPI)
        self.headlines = [
            "🌍 Breaking: New climate agreement signed by 50 nations",
            "💻 Tech: AI breakthrough in quantum computing announced",
            "🏀 Sports: Championship finals begin this weekend",
            "🎬 Entertainment: New blockbuster breaks box office records",
            "📈 Markets: Stock indices reach all-time highs",
            "🔬 Science: Researchers discover new exoplanet in habitable zone",
            "🏥 Health: Vaccine development progresses for emerging virus",
            "🚀 Space: Mars mission prepares for launch next month",
            "🌦️ Weather: Tropical storm warning issued for coastal regions",
            "🎓 Education: Universities announce new online programs",
        ]
        self.loading = False
        self.last_update = time.time()
    
    def on_deactivate(self):
        """Cleanup when exiting."""
        pass
    
    def on_event(self, event):
        """Handle user input."""
        if event.key == InputEvent.UP:
            # Previous headline
            self.current_index = (self.current_index - 1) % len(self.headlines)
            self.scroll_x = 128
            self.dirty = True
        elif event.key == InputEvent.DOWN:
            # Next headline
            self.current_index = (self.current_index + 1) % len(self.headlines)
            self.scroll_x = 128
            self.dirty = True
        elif event.key == InputEvent.OK:
            # Refresh
            self.loading = True
            self.load_headlines()
            self.dirty = True
        
        return True  # Event handled
    
    def on_update(self, delta_time):
        """Update app state."""
        if self.loading:
            return
        
        # Scroll headline
        self.scroll_x -= self.scroll_speed
        
        # Calculate text width (approximate)
        current_text = self.headlines[self.current_index]
        text_width = len(current_text) * 6  # Approximate character width
        
        # Reset scroll when text is off screen
        if self.scroll_x < -text_width:
            self.scroll_x = 128
            # Auto-advance to next headline
            self.current_index = (self.current_index + 1) % len(self.headlines)
        
        # Check if need to refresh headlines
        if time.time() - self.last_update > self.update_interval:
            self.load_headlines()
        
        self.dirty = True
    
    def render(self, matrix):
        """Draw app UI."""
        matrix.clear()
        matrix.fill((0, 0, 0))
        
        if self.loading:
            matrix.text("Loading news...", 15, 60, (255, 255, 255))
            self.dirty = False
            return
        
        # Draw header
        matrix.rect(0, 0, 128, 20, (200, 0, 0), fill=True)
        matrix.text("LIVE NEWS", 25, 5, (255, 255, 255))
        
        # Draw headline count
        headline_info = f"{self.current_index + 1}/{len(self.headlines)}"
        matrix.text(headline_info, 85, 5, (255, 255, 0))
        
        # Draw scrolling headline
        if self.headlines:
            current_text = self.headlines[self.current_index]
            matrix.text(current_text, self.scroll_x, 40, (255, 255, 255))
        
        # Draw divider
        matrix.line(0, 60, 128, 60, (100, 100, 100))
        
        # Draw instructions
        matrix.text("UP/DOWN: Navigate", 10, 70, (150, 150, 150))
        matrix.text("OK: Refresh", 10, 85, (150, 150, 150))
        
        # Draw last update time
        minutes_ago = int((time.time() - self.last_update) / 60)
        update_text = f"Updated {minutes_ago}m ago"
        matrix.text(update_text, 10, 105, (100, 100, 100))
        
        self.dirty = False


def run(os_context):
    """Run News app within MatrixOS framework."""
    app = NewsApp()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()
