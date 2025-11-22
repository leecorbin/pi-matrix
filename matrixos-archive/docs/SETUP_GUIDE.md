# MatrixOS Setup Guide

## Quick Start (Zero Dependencies)

For terminal-only mode, no dependencies needed:

```bash
git clone https://github.com/yourusername/matrixos.git
cd matrixos
./start.py --width 128 --height 64
```

This will use the built-in terminal display and keyboard drivers.

## Development Setup (with macOS Window)

For development with a nice macOS window interface:

### 1. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
# Optional: Install pygame for macOS window
pip install pygame
```

### 3. Run

```bash
python start.py --width 256 --height 192
```

The system will automatically:

- ✅ Detect pygame is available
- ✅ Create a macOS window (instead of terminal display)
- ✅ Capture keyboard input from the window (instead of terminal)

## Dependencies Explained

### Required (Always)

- **Pillow** - For emoji rendering and icon support

### Optional (Enhances Development)

- **pygame** - Enables macOS/Linux window display with keyboard input
  - Without it: Uses terminal display + terminal keyboard
  - With it: Nice resizable window + window keyboard capture

## Platform Support

| Platform | Terminal Mode | Window Mode   | Hardware Mode     |
| -------- | ------------- | ------------- | ----------------- |
| macOS    | ✅ (no deps)  | ✅ (+ pygame) | ❌                |
| Linux    | ✅ (no deps)  | ✅ (+ pygame) | ✅ (Raspberry Pi) |
| Windows  | ✅ (no deps)  | ⏳ TODO       | ❌                |

## Troubleshooting

### "No module named 'pygame'"

This is normal! MatrixOS works without pygame using terminal mode.

To enable window mode:

```bash
pip install pygame
```

### Window opens but keyboard doesn't work

The auto-detection should handle this now. If you still have issues:

1. Make sure pygame is installed
2. Click on the pygame window to focus it
3. Try pressing arrow keys, space, enter

### "externally-managed-environment" error

On macOS/Linux with system Python, use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pygame
```

## Configuration

The system auto-creates `settings/config/system_config.json` on first run.

You can manually configure drivers:

```json
{
  "display_devices": [
    {
      "driver": "macos_window",
      "enabled": true,
      "settings": {
        "width": 256,
        "height": 192,
        "scale": 2
      }
    }
  ],
  "input_devices": [
    {
      "driver": "pygame",
      "enabled": true
    }
  ]
}
```

**But you don't need to!** Auto-detection just works. ✨

## Development Workflow

```bash
# Activate venv once per terminal session
source .venv/bin/activate

# Run the system
python start.py

# Run tests
python test_device_system.py
```

## Next Steps

- See [DEVICE_DRIVER_ARCHITECTURE.md](DEVICE_DRIVER_ARCHITECTURE.md) for driver details
- See [API_REFERENCE.md](API_REFERENCE.md) for app development
- See [FRAMEWORK.md](FRAMEWORK.md) for architecture overview
