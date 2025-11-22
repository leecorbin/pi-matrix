# MatrixOS Documentation Index

Welcome to the MatrixOS documentation! This index helps you find what you need.

## 🚀 Getting Started

Start here if you're new to MatrixOS:

- **[../README.md](../README.md)** - Main project README with quick start
- **[VISION.md](VISION.md)** - Project philosophy and long-term goals
- **[FRAMEWORK.md](FRAMEWORK.md)** - How MatrixOS works (architecture overview)

## 📖 Core Documentation

### For App Developers

- **[API_REFERENCE.md](API_REFERENCE.md)** ⭐ - Complete API documentation
  - Display drawing methods (set_pixel, line, rect, circle, text, etc.)
  - Input handling (InputEvent constants)
  - App lifecycle (on_activate, render, on_event, etc.)
  - Testing API (TestRunner, assertions, log inspection)
  
- **[APP_STRUCTURE.md](APP_STRUCTURE.md)** - App folder structure and files
  - config.json format
  - icon.json format
  - main.py requirements
  
- **[ICON_FORMATS.md](ICON_FORMATS.md)** - Creating app icons
  - 16×16 and 32×32 formats
  - Color encoding
  - Design guidelines

- **[LOGGING.md](LOGGING.md)** - Logging system
  - How to add logging to your app
  - Log levels and formatting
  - Viewing logs

### For Testing

- **[TESTING.md](TESTING.md)** ⭐ - Complete testing guide
  - Quick start examples
  - Display buffer inspection
  - Input simulation
  - Sprite tracking
  - Log inspection
  - Common patterns
  - Best practices
  
- **[TESTING_FRAMEWORK_SUMMARY.md](TESTING_FRAMEWORK_SUMMARY.md)** - Testing overview
  - Architecture summary
  - Key features
  - Real-world examples
  - Test results (17/17 passing!)

- **[TESTING_FRAMEWORK_DESIGN.md](TESTING_FRAMEWORK_DESIGN.md)** - Original design
  - YAML test specifications (future enhancement)
  - Design decisions
  - Implementation roadmap

### For Hardware Builders

- **[HARDWARE.md](HARDWARE.md)** - Complete hardware guide
  - Parts list
  - Raspberry Pi setup
  - LED matrix wiring
  - Power requirements
  - Assembly instructions
  
- **[SPECTRUM_EMULATOR.md](SPECTRUM_EMULATOR.md)** - ZX Spectrum emulator plan
  - 256×192 multi-panel setup
  - Emulation approach
  - Ultimate vision

## 📝 Reference Documents

- **[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)** - Historical development notes
- **[RETRO_EMULATORS.md](RETRO_EMULATORS.md)** - Retro computing context
- **[AUTOMATED_TESTING.md](AUTOMATED_TESTING.md)** - Original testing concepts (superseded by TESTING.md)

## 🗺️ Navigation Tips

### I want to...

**...create my first app**
1. Read [FRAMEWORK.md](FRAMEWORK.md) - understand architecture
2. Read [API_REFERENCE.md](API_REFERENCE.md) - learn the APIs
3. Look at `../apps/demos/main.py` - see examples
4. Copy an existing app folder and modify it

**...test my app**
1. Read [TESTING.md](TESTING.md) - learn testing framework
2. Look at `../tests/advanced_test.py` - see examples
3. Write tests for your app
4. Run with `python3 tests/your_test.py`

**...build the hardware**
1. Read [HARDWARE.md](HARDWARE.md) - complete build guide
2. Order parts from the list
3. Follow wiring diagrams
4. Deploy MatrixOS to Raspberry Pi

**...understand the vision**
1. Read [VISION.md](VISION.md) - philosophy and goals
2. Read [SPECTRUM_EMULATOR.md](SPECTRUM_EMULATOR.md) - ultimate goal
3. Check [../README.md](../README.md) roadmap section

**...add logging to my app**
1. Read [LOGGING.md](LOGGING.md) - logging system
2. Import logger in your app
3. Use logger.info(), logger.debug(), etc.
4. Check `settings/logs/` folder

**...create an icon**
1. Read [ICON_FORMATS.md](ICON_FORMATS.md) - format specs
2. Design 16×16 or 32×32 pixel art
3. Create icon.json with pixel grid
4. Add to your app folder

## 📚 Document Status

| Document | Status | Last Updated | Notes |
|----------|--------|--------------|-------|
| README.md (main) | ✅ Current | Nov 2025 | Includes testing section |
| API_REFERENCE.md | ✅ Current | Nov 2025 | Complete with testing APIs |
| TESTING.md | ✅ Current | Nov 2025 | Comprehensive guide |
| TESTING_FRAMEWORK_SUMMARY.md | ✅ Current | Nov 2025 | Updated with results |
| FRAMEWORK.md | ✅ Current | Oct 2025 | Core architecture |
| APP_STRUCTURE.md | ✅ Current | Oct 2025 | App organization |
| LOGGING.md | ✅ Current | Oct 2025 | Logging system |
| HARDWARE.md | ✅ Current | Oct 2025 | Build guide |
| VISION.md | ✅ Current | Oct 2025 | Project goals |
| ICON_FORMATS.md | ✅ Current | Oct 2025 | Icon creation |
| SPECTRUM_EMULATOR.md | ✅ Current | Oct 2025 | Future vision |
| TESTING_FRAMEWORK_DESIGN.md | ⏳ Design | Oct 2025 | YAML specs (future) |
| AUTOMATED_TESTING.md | ⚠️ Superseded | Oct 2025 | See TESTING.md instead |
| DEVELOPMENT_LOG.md | 📝 Archive | Oct 2025 | Historical notes |
| RETRO_EMULATORS.md | 📝 Reference | Oct 2025 | Background info |

## 🆕 Recent Updates (November 2025)

**Testing Framework Complete:**
- ✅ Created comprehensive TESTING.md guide
- ✅ Updated API_REFERENCE.md with testing APIs
- ✅ Updated TESTING_FRAMEWORK_SUMMARY.md with real results
- ✅ Added testing section to main README.md
- ✅ All 17 tests passing (smoke, advanced, log integration)
- ✅ Pure Python implementation (no numpy)

**Documentation Cleanup:**
- ✅ Removed duplicate content from README.md
- ✅ Updated project structure in README.md
- ✅ Added testing to roadmap (marked complete)
- ✅ Created this documentation index

## 💡 Tips

- **Start simple**: Don't try to read everything at once
- **Use examples**: Check `../apps/` and `../tests/` for working code
- **API first**: [API_REFERENCE.md](API_REFERENCE.md) is your friend
- **Test early**: Write tests as you build (catches bugs faster)
- **Retro style, modern practices**: That's the MatrixOS way! 🎮✨

---

**Questions?** Open an issue on GitHub or check the examples in `../apps/` and `../tests/`.

**Contributing?** Read [FRAMEWORK.md](FRAMEWORK.md) and [API_REFERENCE.md](API_REFERENCE.md), then dive in!

Built with ❤️ for LED matrices and retro computing!
