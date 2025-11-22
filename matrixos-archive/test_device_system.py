#!/usr/bin/env python3
"""
Test script for new device driver system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from matrixos.devices import DeviceManager
from matrixos.devices.display.terminal import TerminalDisplayDriver
from matrixos.devices.display.macos_window import MacOSWindowDriver
from matrixos.devices.input.terminal import TerminalInputDriver
try:
    from matrixos.devices.input.pygame_input import PygameInputDriver
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
from matrixos.boot import print_boot_banner, show_simple_boot_logo
import time


def test_device_manager():
    """Test the device manager"""
    print("\n🧪 Testing Device Manager...\n")
    
    # Print boot banner to console
    print_boot_banner()
    
    # Create device manager
    dm = DeviceManager()
    
    # Register drivers
    print("📝 Registering drivers...")
    dm.register_display_driver("terminal", TerminalDisplayDriver)
    dm.register_display_driver("macos_window", MacOSWindowDriver)
    dm.register_input_driver("terminal", TerminalInputDriver)
    if HAS_PYGAME:
        dm.register_input_driver("pygame", PygameInputDriver)
    
    # Detect platform
    print(f"🖥️  Platform: {dm.platform}")
    
    # Initialize display
    print("🎨 Initializing display...")
    if dm.initialize_display():
        print(f"✅ Display active: {dm.active_display.name}")
        print(f"   Resolution: {dm.active_display.width}×{dm.active_display.height}")
    else:
        print("❌ Display initialization failed!")
        return False
    
    # Show boot logo
    print("🚀 Showing boot logo...")
    show_simple_boot_logo(dm.active_display, duration=2.0)
    
    # Initialize input
    print("⌨️  Initializing input...")
    if dm.initialize_inputs():
        print(f"✅ {len(dm.active_inputs)} input device(s) active")
        for inp in dm.active_inputs:
            print(f"   - {inp.name}")
    else:
        print("❌ Input initialization failed!")
        return False
    
    # Test rendering
    print("\n🎨 Testing display rendering...")
    display = dm.active_display
    
    # Draw test pattern
    display.clear()
    
    # Cyan border
    for x in range(display.width):
        display.set_pixel(x, 0, (0, 255, 255))
        display.set_pixel(x, display.height - 1, (0, 255, 255))
    for y in range(display.height):
        display.set_pixel(0, y, (0, 255, 255))
        display.set_pixel(display.width - 1, y, (0, 255, 255))
    
    # Yellow square
    for y in range(80, 112):
        for x in range(112, 144):
            display.set_pixel(x, y, (255, 255, 0))
    
    # Show it
    display.show()
    
    print("\n✅ Test complete! You should see:")
    print("   - Cyan border around screen")
    print("   - Yellow square in center")
    print("\nPress any key to test input (or Ctrl+C to exit)...")
    
    # Test input
    try:
        while True:
            events = dm.poll_inputs()
            for event in events:
                print(f"   Input: {event.key}")
                if event.key == 'HOME':  # ESC to exit
                    print("\n👋 Exiting...")
                    dm.cleanup()
                    return True
            time.sleep(0.016)  # ~60 FPS
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
        dm.cleanup()
        return True


if __name__ == "__main__":
    try:
        success = test_device_manager()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
