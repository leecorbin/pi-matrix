"""
MatrixOS Launcher
Displays app icons in a grid and allows navigation/launching

All apps use the framework - no subprocess execution.
"""

import json
import importlib.util
from pathlib import Path


# Color palette for icons
COLOR_PALETTE = {
    0: (0, 0, 0),         # Black/Transparent
    1: (255, 255, 255),   # White
    2: (255, 0, 0),       # Red
    3: (0, 255, 0),       # Green
    4: (0, 0, 255),       # Blue
    5: (255, 255, 0),     # Yellow
    6: (0, 255, 255),     # Cyan
    7: (255, 0, 255),     # Magenta
}


class App:
    """Represents a MatrixOS app."""

    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
        self.name = "Unknown"
        self.author = "Unknown"
        self.version = "1.0.0"
        self.description = ""
        self.icon_pixels = None

        self._load_config()
        self._load_icon()

    def _load_config(self):
        """Load app config from config.json."""
        config_path = self.folder_path / "config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.name = config.get("name", self.folder_path.name)
                self.author = config.get("author", "Unknown")
                self.version = config.get("version", "1.0.0")
                self.description = config.get("description", "")

    def _load_icon(self):
        """Load app icon from icon.json."""
        icon_path = self.folder_path / "icon.json"
        if icon_path.exists():
            with open(icon_path, 'r') as f:
                icon_data = json.load(f)
                self.icon_pixels = icon_data.get("pixels", [])

    def draw_icon(self, matrix, x, y):
        """Draw the app icon at the given position."""
        if not self.icon_pixels:
            # Draw default icon if no icon file
            matrix.rect(x, y, 16, 16, (100, 100, 100), fill=True)
            return

        for row_idx, row in enumerate(self.icon_pixels):
            for col_idx, color_code in enumerate(row):
                if color_code != 0:  # Skip transparent pixels
                    color = COLOR_PALETTE.get(color_code, (255, 255, 255))
                    matrix.set_pixel(x + col_idx, y + row_idx, color)

    def launch(self, os_context):
        """Launch the app using the framework.

        Args:
            os_context: OSContext for app execution

        Returns:
            True if app was launched successfully
        """
        main_py = self.folder_path / "main.py"
        if not main_py.exists():
            return False

        print(f"\n{'='*64}")
        print(f"Launching: {self.name}")
        print(f"{'='*64}\n")

        try:
            # Import app module
            spec = importlib.util.spec_from_file_location(
                f"app_{self.folder_path.name}",
                main_py
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Call the app's run() function
            if hasattr(module, 'run'):
                module.run(os_context)
            else:
                print(f"Error: App '{self.name}' missing run(os_context) function!")
                return False

            print(f"\n{'='*64}")
            print(f"{self.name} exited.")
            print(f"{'='*64}\n")
            return True

        except Exception as e:
            print(f"Error loading app: {e}")
            import traceback
            traceback.print_exc()
            return False


class Launcher:
    """MatrixOS app launcher with icon grid."""

    def __init__(self, matrix, input_handler, os_context=None, apps_base_dir=None):
        self.matrix = matrix
        self.input_handler = input_handler
        self.os_context = os_context
        self.apps_base_dir = Path(apps_base_dir) if apps_base_dir else Path(__file__).parent.parent.parent
        self.apps = []
        self.selected_index = 0
        self.icon_size = 16
        self.padding = 2

        # Calculate grid layout
        self.grid_width = (matrix.width + self.padding) // (self.icon_size + self.padding)
        self.grid_height = (matrix.height - 10 + self.padding) // (self.icon_size + self.padding)  # Reserve 10px for text at bottom

        self._discover_apps()

    def _discover_apps(self):
        """Discover all valid apps in the apps/ directory and root."""
        # Check apps/ directory
        apps_dir = self.apps_base_dir / "apps"
        if apps_dir.exists():
            for folder in sorted(apps_dir.iterdir()):
                if folder.is_dir() and self._is_valid_app(folder):
                    self.apps.append(App(folder))

        # Also check root directory for app folders
        for folder in sorted(self.apps_base_dir.iterdir()):
            if folder.is_dir() and folder.name not in ['apps', 'matrixos', 'examples', 'tests', 'venv', '.git', 'docs']:
                if self._is_valid_app(folder):
                    self.apps.append(App(folder))

    def _is_valid_app(self, folder_path):
        """Check if a folder is a valid app."""
        main_py = folder_path / "main.py"
        config_json = folder_path / "config.json"
        return main_py.exists() and config_json.exists()

    def draw(self):
        """Draw the launcher UI."""
        self.matrix.clear()
        self.matrix.fill((0, 0, 0))

        # Draw app icons in grid
        for idx, app in enumerate(self.apps):
            if idx >= self.grid_width * self.grid_height:
                break  # Don't draw more than can fit

            row = idx // self.grid_width
            col = idx % self.grid_width

            x = col * (self.icon_size + self.padding) + self.padding
            y = row * (self.icon_size + self.padding) + self.padding

            # Draw selection box
            if idx == self.selected_index:
                self.matrix.rect(x - 1, y - 1, self.icon_size + 2, self.icon_size + 2, (255, 255, 0), fill=False)

            # Draw icon
            app.draw_icon(self.matrix, x, y)

        # Draw selected app name at bottom
        if 0 <= self.selected_index < len(self.apps):
            selected_app = self.apps[self.selected_index]
            text_y = self.matrix.height - 8
            self.matrix.centered_text(selected_app.name.upper(), text_y, (255, 255, 255))

        self.matrix.show()

    def run(self):
        """Run the launcher main loop."""
        running = True
        needs_redraw = True  # Initial draw

        while running:
            # Only draw when needed (not every frame)
            if needs_redraw:
                self.draw()
                needs_redraw = False

            # Handle input
            event = self.input_handler.get_key(timeout=0.1)

            if event:
                if event.key == 'UP':
                    new_row = (self.selected_index // self.grid_width) - 1
                    if new_row >= 0:
                        self.selected_index -= self.grid_width
                        needs_redraw = True

                elif event.key == 'DOWN':
                    new_row = (self.selected_index // self.grid_width) + 1
                    if new_row * self.grid_width < len(self.apps):
                        self.selected_index = min(self.selected_index + self.grid_width, len(self.apps) - 1)
                        needs_redraw = True

                elif event.key == 'LEFT':
                    if self.selected_index % self.grid_width > 0:
                        self.selected_index -= 1
                        needs_redraw = True

                elif event.key == 'RIGHT':
                    if self.selected_index % self.grid_width < self.grid_width - 1 and self.selected_index < len(self.apps) - 1:
                        self.selected_index += 1
                        needs_redraw = True

                elif event.key == 'OK':  # Enter key maps to OK
                    if 0 <= self.selected_index < len(self.apps):
                        selected_app = self.apps[self.selected_index]
                        selected_app.launch(self.os_context)
                        # Redraw after returning from app
                        needs_redraw = True

                elif event.key == 'BACK' or event.key == 'QUIT':  # ESC or Q
                    running = False
