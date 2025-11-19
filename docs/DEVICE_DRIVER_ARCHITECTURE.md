# MatrixOS Device Driver Architecture

**Version:** 1.0  
**Date:** November 19, 2025  
**Philosophy:** "OS on an OS" - MatrixOS as a complete operating system with proper hardware abstraction

---

## 🎯 Vision

MatrixOS is designed to run on various platforms (Mac, Raspberry Pi, etc.) with different input and output devices. The device driver system provides a flexible, extensible architecture that:

- **Abstracts hardware** - Apps don't care about the underlying device
- **Auto-detects platform** - Chooses appropriate drivers for Mac vs Pi
- **Supports hot-plugging** - Devices can be added/removed at runtime
- **Graceful fallback** - Always has working defaults
- **Boot-time discovery** - Finds input devices when none configured

---

## 📁 Directory Structure

```
matrixos/
├── devices/                    # NEW: Device driver system
│   ├── __init__.py            # Device manager + registry
│   ├── base.py                # Base classes for all drivers
│   ├── display/               # Display output drivers
│   │   ├── __init__.py
│   │   ├── terminal.py        # ✅ Current default (cross-platform)
│   │   ├── hdmi_wayland.py    # 🔜 Raspberry Pi HDMI output
│   │   ├── led_matrix.py      # 🔜 RGB LED matrix (SPI)
│   │   └── macos_window.py    # 🔜 Native macOS window
│   ├── input/                 # Input device drivers
│   │   ├── __init__.py
│   │   ├── terminal.py        # ✅ Current default (keyboard via terminal)
│   │   ├── bluetooth_keyboard.py    # 🔜 Standard BT keyboard
│   │   ├── spectrum_keyboard.py     # 🔜 Recreated Spectrum keyboard
│   │   │                            #     (supports both modes!)
│   │   └── bluetooth_remote.py      # 🔜 IR/BT remote control
│   └── discovery.py           # Bluetooth device discovery + pairing
├── boot/                      # NEW: Boot sequence
│   ├── __init__.py
│   ├── logo.py                # MatrixOS boot logo
│   ├── device_setup.py        # First-boot device configuration
│   └── splash.py              # Boot splash screens
├── display.py                 # ✅ Current (will become thin wrapper)
├── input.py                   # ✅ Current (will become thin wrapper)
└── system_config.json         # ✅ OS-wide settings (extended)
```

---

## 🏗️ Base Driver Classes

### **DisplayDriver** (Abstract Base Class)

```python
from abc import ABC, abstractmethod

class DisplayDriver(ABC):
    """Base class for all display drivers"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.name = "Generic Display"
        self.platform = None  # "macos", "linux", "raspberry-pi", etc.

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize hardware/connection. Returns True if successful."""
        pass

    @abstractmethod
    def set_pixel(self, x: int, y: int, color: tuple):
        """Set a single pixel"""
        pass

    @abstractmethod
    def clear(self):
        """Clear the display"""
        pass

    @abstractmethod
    def show(self):
        """Push buffer to actual display"""
        pass

    @abstractmethod
    def cleanup(self):
        """Release resources"""
        pass

    @classmethod
    def is_available(cls) -> bool:
        """Check if this driver can run on current platform"""
        return True

    @classmethod
    def get_priority(cls) -> int:
        """Priority for auto-selection (higher = preferred)"""
        return 0
```

### **InputDriver** (Abstract Base Class)

```python
from abc import ABC, abstractmethod

class InputDriver(ABC):
    """Base class for all input drivers"""

    def __init__(self):
        self.name = "Generic Input"
        self.device_id = None
        self.connected = False

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize hardware/connection"""
        pass

    @abstractmethod
    def poll(self) -> list:
        """Poll for events. Returns list of InputEvent objects."""
        pass

    @abstractmethod
    def cleanup(self):
        """Release resources"""
        pass

    @classmethod
    def is_available(cls) -> bool:
        """Check if this driver can run on current platform"""
        return True

    @classmethod
    def requires_pairing(cls) -> bool:
        """Does this driver need Bluetooth pairing?"""
        return False

    @classmethod
    def get_device_class(cls) -> str:
        """Device class: 'keyboard', 'remote', 'gamepad', etc."""
        return "generic"
```

---

## 🎮 Device Manager

Central registry and lifecycle manager for all devices:

```python
class DeviceManager:
    """Manages device drivers throughout MatrixOS lifecycle"""

    def __init__(self):
        self.display_drivers = {}   # name -> class
        self.input_drivers = {}     # name -> class
        self.active_display = None
        self.active_inputs = []     # Can have multiple (keyboard + remote)
        self.config = self.load_config()

    def register_display_driver(self, name: str, driver_class):
        """Register a display driver"""
        self.display_drivers[name] = driver_class

    def register_input_driver(self, name: str, driver_class):
        """Register an input driver"""
        self.input_drivers[name] = driver_class

    def auto_detect_platform(self) -> str:
        """Detect current platform: 'macos', 'linux', 'raspberry-pi'"""
        import platform
        system = platform.system().lower()

        if system == "darwin":
            return "macos"
        elif system == "linux":
            # Check if Raspberry Pi
            try:
                with open("/proc/cpuinfo") as f:
                    if "Raspberry Pi" in f.read():
                        return "raspberry-pi"
            except:
                pass
            return "linux"
        return "unknown"

    def select_best_display(self) -> DisplayDriver:
        """Auto-select best display driver for current platform"""
        platform = self.auto_detect_platform()
        available = []

        for name, driver_class in self.display_drivers.items():
            if driver_class.is_available():
                priority = driver_class.get_priority()
                available.append((priority, name, driver_class))

        # Sort by priority (highest first)
        available.sort(reverse=True, key=lambda x: x[0])

        if available:
            priority, name, driver_class = available[0]
            return driver_class(width=256, height=192)

        raise RuntimeError("No display driver available!")

    def initialize_display(self, driver_name: str = None) -> bool:
        """Initialize display driver (from config or auto-detect)"""
        if driver_name and driver_name in self.display_drivers:
            # Use specified driver
            driver_class = self.display_drivers[driver_name]
            self.active_display = driver_class(width=256, height=192)
        else:
            # Auto-select
            self.active_display = self.select_best_display()

        return self.active_display.initialize()

    def initialize_inputs(self) -> bool:
        """Initialize input drivers (may trigger pairing UI)"""
        configured_inputs = self.config.get("input_devices", [])

        if not configured_inputs:
            # No inputs configured - trigger first-boot device setup
            return self.first_boot_input_setup()

        # Initialize configured inputs
        for input_config in configured_inputs:
            driver_name = input_config.get("driver")
            if driver_name in self.input_drivers:
                driver_class = self.input_drivers[driver_name]
                driver = driver_class()
                if driver.initialize():
                    self.active_inputs.append(driver)

        return len(self.active_inputs) > 0

    def first_boot_input_setup(self) -> bool:
        """First boot - discover and pair input devices"""
        from matrixos.boot.device_setup import InputDiscoveryScreen

        # Show animated discovery screen
        discovery = InputDiscoveryScreen(self.active_display)
        selected_devices = discovery.run()

        # Save to config
        if selected_devices:
            self.config["input_devices"] = selected_devices
            self.save_config()
            return True

        # Fallback to terminal input
        return self.initialize_terminal_input()
```

---

## 🔍 Bluetooth Device Discovery

### **Discovery Process:**

1. **Boot check** - If no input devices configured, trigger discovery
2. **Scan for devices** - Look for Bluetooth devices in pairing mode
3. **Classify devices** - Detect keyboard vs remote vs gamepad
4. **Animated UI** - Show "Searching..." with pulsing circle
5. **Device list** - Show found devices with icons
6. **Pairing** - Connect and save to config

### **Discovery Screen:**

```python
class InputDiscoveryScreen:
    """Animated Bluetooth device discovery during boot"""

    def __init__(self, display):
        self.display = display
        self.scanning = True
        self.found_devices = []

    def run(self) -> list:
        """Run discovery, return selected devices"""
        # Show animated "Searching for devices..." screen
        self.show_scanning_animation()

        # Scan for Bluetooth devices
        self.scan_bluetooth_devices()

        if not self.found_devices:
            # No devices found - use terminal input
            return self.fallback_to_terminal()

        # Show device list, let user select
        return self.show_device_selection()

    def show_scanning_animation(self):
        """Pulsing circles, "SEARCHING..." text"""
        # Animation loop with timeout
        pass

    def scan_bluetooth_devices(self):
        """Scan for BT devices in pairing mode"""
        # Use PyBluez or similar
        # Classify by device type (keyboard, remote, etc.)
        pass

    def classify_device(self, device_info) -> str:
        """Determine device class from BT info"""
        # Check device name, class, services
        if "keyboard" in device_info.name.lower():
            if "spectrum" in device_info.name.lower():
                return "spectrum_keyboard"
            return "bluetooth_keyboard"
        elif "remote" in device_info.name.lower():
            return "bluetooth_remote"
        return "unknown"

    def show_device_selection(self) -> list:
        """Show list of found devices, let user select"""
        # Display list with device icons
        # Use arrow keys to select (from terminal initially)
        # Return selected device configs
        pass
```

---

## 📱 Platform-Specific Drivers

### **Display Drivers:**

#### 1. **Terminal Display** (Default, Cross-Platform)

- **Status:** ✅ Currently implemented
- **Platform:** All (macOS, Linux, Raspberry Pi)
- **Priority:** 10 (low - fallback)
- **File:** `matrixos/devices/display/terminal.py`

#### 2. **macOS Native Window**

- **Status:** 🔜 Planned
- **Platform:** macOS only
- **Priority:** 50 (high on Mac)
- **Implementation:** PyQt5 or Pygame window
- **Features:** Resizable, smooth rendering, native feel

#### 3. **HDMI via Wayland** (Raspberry Pi)

- **Status:** 🔜 Planned
- **Platform:** Raspberry Pi (Wayland compositor)
- **Priority:** 50 (high on Pi)
- **Implementation:** Direct framebuffer or Wayland surface
- **Features:** Full-screen, hardware accelerated

#### 4. **RGB LED Matrix** (Raspberry Pi)

- **Status:** 🔜 Long-term goal
- **Platform:** Raspberry Pi (with LED matrix HAT)
- **Priority:** 60 (highest when available)
- **Implementation:** rpi-rgb-led-matrix library
- **Features:** Physical LED output

### **Input Drivers:**

#### 1. **Terminal Keyboard** (Default, Cross-Platform)

- **Status:** ✅ Currently implemented
- **Platform:** All
- **Priority:** 10 (fallback)
- **File:** `matrixos/devices/input/terminal.py`

#### 2. **Bluetooth Keyboard**

- **Status:** 🔜 Planned
- **Platform:** All (with Bluetooth)
- **Priority:** 40
- **Pairing:** Yes
- **Features:** Standard keyboard input

#### 3. **Recreated Spectrum Keyboard**

- **Status:** 🔜 Planned
- **Platform:** All (with Bluetooth)
- **Priority:** 50
- **Pairing:** Yes
- **Features:**
  - **Standard mode:** Regular keyboard layout
  - **Native mode:** Spectrum-specific keys (for emulator)
  - Mode switching via settings or key combo

#### 4. **Bluetooth Remote**

- **Status:** 🔜 Planned
- **Platform:** All (with Bluetooth)
- **Priority:** 30
- **Pairing:** Yes
- **Features:** Arrow keys, OK, Back, Home buttons

---

## ⚙️ Configuration File

Extended `matrixos/system_config.json`:

```json
{
  "display": {
    "width": 256,
    "height": 192,
    "driver": "auto",
    "driver_override": null,
    "terminal": {
      "emulator": "auto"
    },
    "hdmi": {
      "fullscreen": true,
      "vsync": true
    },
    "led_matrix": {
      "gpio_slowdown": 2,
      "brightness": 80
    }
  },
  "input_devices": [
    {
      "driver": "bluetooth_keyboard",
      "device_id": "AA:BB:CC:DD:EE:FF",
      "name": "Recreated ZX Spectrum",
      "mode": "standard",
      "enabled": true
    },
    {
      "driver": "bluetooth_remote",
      "device_id": "11:22:33:44:55:66",
      "name": "MatrixOS Remote",
      "enabled": true
    }
  ],
  "bluetooth": {
    "auto_discover_on_boot": true,
    "pairing_timeout": 30,
    "scan_interval": 5
  },
  "boot": {
    "show_logo": true,
    "logo_duration": 2.0,
    "skip_device_setup": false
  }
}
```

---

## 🚀 Boot Sequence

### **MatrixOS Boot Process:**

```
1. 🎨 Show Boot Logo (2 seconds)
   └─> Animated MatrixOS logo with version

2. 🔌 Initialize Display
   ├─> Check config for driver preference
   ├─> Auto-detect platform if needed
   ├─> Load and initialize driver
   └─> Fallback to terminal if failure

3. ⌨️  Initialize Input
   ├─> Check config for registered devices
   ├─> If none found:
   │   └─> Launch Bluetooth Discovery Screen
   │       ├─> Scan for devices (30s timeout)
   │       ├─> Show found devices
   │       ├─> Let user select (arrow keys + OK)
   │       └─> Save to config
   ├─> Connect to configured devices
   └─> Fallback to terminal if failure

4. 📱 Load OS
   ├─> Initialize app framework
   ├─> Load launcher
   └─> Show app grid
```

### **Boot Logo:**

```python
# matrixos/boot/logo.py

MATRIXOS_LOGO = """
┌─────────────────────────┐
│   ███╗   ███╗ ██████╗   │
│   ████╗ ████║██╔═══██╗  │
│   ██╔████╔██║██║   ██║  │
│   ██║╚██╔╝██║██║   ██║  │
│   ██║ ╚═╝ ██║╚██████╔╝  │
│   ╚═╝     ╚═╝ ╚═════╝   │
│                          │
│    M A T R I X  O S      │
│    v2.0 ZX SPECTRUM      │
└─────────────────────────┘
"""

def show_boot_logo(display, duration=2.0):
    """Display animated boot logo"""
    # Center logo on screen
    # Pulse cyan color
    # Show version
    # Wait for duration
    pass
```

---

## 🔧 Migration Path

### **Phase 1: Refactor Current Code** (Immediate)

1. Move `display.py` → `devices/display/terminal.py`
2. Move `input.py` → `devices/input/terminal.py`
3. Create `devices/base.py` with abstract classes
4. Create `devices/__init__.py` with DeviceManager
5. Update `start.py` to use DeviceManager

### **Phase 2: Boot System** (Next)

1. Create `boot/logo.py` with ASCII boot logo
2. Create `boot/device_setup.py` for first-boot discovery
3. Update config file with device settings
4. Add boot sequence to `start.py`

### **Phase 3: macOS Window Driver** (Near-term)

1. Implement `devices/display/macos_window.py`
2. Use PyQt5 or Pygame for native window
3. Add platform detection
4. Auto-select on macOS

### **Phase 4: Bluetooth Support** (Medium-term)

1. Add PyBluez dependency (optional)
2. Implement `devices/discovery.py`
3. Create discovery UI screens
4. Implement `devices/input/bluetooth_keyboard.py`
5. Add to Settings app

### **Phase 5: Raspberry Pi** (Long-term)

1. Test on actual Pi hardware
2. Implement `devices/display/hdmi_wayland.py`
3. Optimize performance
4. Test with LED matrix HAT

---

## 📝 Settings App Integration

### **New "Devices" Section:**

```
Settings App
├─> Display
│   ├─> Driver: [Auto] [Terminal] [macOS Window] [HDMI] [LED Matrix]
│   ├─> Resolution: 256×192 (locked)
│   └─> Brightness: [80%]
├─> Input Devices
│   ├─> [✓] Recreated Spectrum Keyboard (Standard Mode)
│   ├─> [✓] MatrixOS Remote
│   └─> [+ Add New Device] ← Triggers discovery screen
└─> Bluetooth
    ├─> Auto-discover on boot: [✓]
    ├─> Pairing timeout: 30s
    └─> Connected: [2 devices]
```

**"Add New Device" Flow:**

1. Show scanning animation (same as first-boot)
2. List found devices
3. User selects device(s)
4. Pair and save to config
5. Device immediately available

---

## 🎯 Benefits of This Architecture

1. **Clean Separation** - Display/input logic separated from apps
2. **Platform Agnostic** - Apps work everywhere without changes
3. **Easy Testing** - Mock drivers for unit tests
4. **Extensible** - New drivers = new file, register, done
5. **User Friendly** - Auto-detection "just works"
6. **Future-Proof** - Ready for LED matrices, projectors, whatever!

---

## 🚦 Implementation Checklist

- [ ] Create `matrixos/devices/` directory structure
- [ ] Implement `base.py` with abstract classes
- [ ] Implement `DeviceManager` in `__init__.py`
- [ ] Migrate terminal display to new structure
- [ ] Migrate terminal input to new structure
- [ ] Create boot logo and boot sequence
- [ ] Update `system_config.json` schema
- [ ] Add first-boot device discovery
- [ ] Update Settings app with Devices section
- [ ] Document driver development guide
- [ ] Test on macOS
- [ ] Test on Linux
- [ ] Test on Raspberry Pi (when available)

---

## 📚 Next Steps

1. **Review this architecture** - Does it meet your vision?
2. **Start Phase 1** - Refactor current code into new structure
3. **Create boot logo** - Design animated MatrixOS logo
4. **Plan macOS driver** - Decide on PyQt5 vs Pygame
5. **Research Bluetooth** - Investigate pairing libraries

---

**This architecture makes MatrixOS a true "OS on an OS"** - platform-independent, hardware-agnostic, and ready for anything from terminal emulators to physical LED matrices! 🚀

What do you think? Should we proceed with Phase 1? 🎮
