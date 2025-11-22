"""
MatrixOS Boot Logo

Displays the epic ZX Spectrum-style boot logo on startup.
"""

import time
import math


# ASCII Art Boot Logo
MATRIXOS_LOGO_ASCII = """
█▀▄▀█ ▄▀█ ▀█▀ █▀█ █ ▀▄▀   █▀█ █▀
█ ▀ █ █▀█  █  █▀▄ █ █ █   █▄█ ▄█
""".strip()

# Centered ZX Spectrum style logo
MATRIXOS_LOGO = [
    "███╗   ███╗ ██████╗",
    "████╗ ████║██╔═══██╗",
    "██╔████╔██║██║   ██║",
    "██║╚██╔╝██║██║   ██║",
    "██║ ╚═╝ ██║╚██████╔╝",
    "╚═╝     ╚═╝ ╚═════╝",
]

SUBTITLE = "Z X   S P E C T R U M"
VERSION = "v2.0"

# ZX Spectrum colors
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
DARK_BLUE = (0, 0, 40)
BLACK = (0, 0, 0)


def show_boot_logo(display, duration: float = 2.0):
    """
    Display animated MatrixOS boot logo.
    
    Args:
        display: Display driver instance
        duration: How long to show logo (seconds)
    """
    width = display.width
    height = display.height
    
    start_time = time.time()
    frame = 0
    
    while time.time() - start_time < duration:
        display.clear()
        
        # Background
        for y in range(height):
            for x in range(width):
                display.set_pixel(x, y, DARK_BLUE)
        
        # Pulsing border effect
        pulse = abs(math.sin(frame * 0.1))
        border_color = (
            int(CYAN[0] * pulse),
            int(CYAN[1] * pulse),
            int(CYAN[2] * pulse)
        )
        
        # Draw border
        for x in range(width):
            display.set_pixel(x, 0, border_color)
            display.set_pixel(x, height - 1, border_color)
        for y in range(height):
            display.set_pixel(0, y, border_color)
            display.set_pixel(width - 1, y, border_color)
        
        # Center text
        logo_y = height // 2 - 20
        
        # Draw "MATRIX OS" as simple pixel blocks (no text rendering needed)
        # Just show the colored border - text will be added later with proper font support
        # For now, we can draw a filled rectangle in the center as a placeholder
        center_x = width // 2
        center_y = height // 2
        
        # Draw a centered filled rectangle (placeholder for logo)
        logo_width = 80
        logo_height = 20
        logo_x = center_x - logo_width // 2
        logo_y_pos = center_y - logo_height // 2
        
        for y in range(logo_y_pos, logo_y_pos + logo_height):
            for x in range(logo_x, logo_x + logo_width):
                # Create gradient effect
                intensity = int(255 * pulse)
                display.set_pixel(x, y, (0, intensity, intensity))  # Cyan
        
        # Draw version text at bottom
        version_y = height - 20
        version_width = 40
        version_x = center_x - version_width // 2
        
        for y in range(version_y, version_y + 10):
            for x in range(version_x, version_x + version_width):
                intensity = int(200 * pulse)
                display.set_pixel(x, y, (intensity, intensity, 0))  # Yellow
        
        # Show for one frame
        display.show()
        
        frame += 1
        time.sleep(1/30)  # 30 FPS animation


def show_simple_boot_logo(display, duration: float = 2.0):
    """
    Show a simple boot logo for terminals without full graphics support.
    
    Args:
        display: Display driver instance  
        duration: How long to show logo (seconds)
    """
    width = display.width
    height = display.height
    
    # Clear and fill with dark blue background
    display.clear()
    for y in range(height):
        for x in range(width):
            display.set_pixel(x, y, DARK_BLUE)
    
    # Draw cyan border
    for x in range(width):
        display.set_pixel(x, 0, CYAN)
        display.set_pixel(x, height - 1, CYAN)
    for y in range(height):
        display.set_pixel(0, y, CYAN)
        display.set_pixel(width - 1, y, CYAN)
    
    # Draw centered colored blocks for logo (no text rendering needed)
    center_x = width // 2
    center_y = height // 2
    
    # Draw "MATRIX OS" placeholder as cyan rectangle
    logo_width = 100
    logo_height = 30
    logo_x = center_x - logo_width // 2
    logo_y = center_y - logo_height // 2 - 10
    
    for y in range(logo_y, logo_y + logo_height):
        for x in range(logo_x, logo_x + logo_width):
            display.set_pixel(x, y, CYAN)
    
    # Draw "ZX SPECTRUM" subtitle as yellow rectangle
    sub_width = 80
    sub_height = 10
    sub_x = center_x - sub_width // 2
    sub_y = center_y + 20
    
    for y in range(sub_y, sub_y + sub_height):
        for x in range(sub_x, sub_x + sub_width):
            display.set_pixel(x, y, YELLOW)
    
    # Draw version as white small rectangle
    ver_width = 30
    ver_height = 8
    ver_x = center_x - ver_width // 2
    ver_y = center_y + 40
    
    for y in range(ver_y, ver_y + ver_height):
        for x in range(ver_x, ver_x + ver_width):
            display.set_pixel(x, y, WHITE)
    
    display.show()
    time.sleep(duration)


def print_boot_banner():
    """Print ASCII boot banner to console"""
    print("\n" + "=" * 60)
    print(MATRIXOS_LOGO_ASCII)
    print("")
    print(f"                    {SUBTITLE}")
    print(f"                      {VERSION}")
    print("=" * 60 + "\n")
