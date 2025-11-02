# Icon Format Guide

MatrixOS supports multiple icon formats to give developers flexibility in how they create icons.

## Supported Formats

### 1. RGB Format (Recommended for gradients)

Direct RGB color values per pixel. Perfect for gradient icons with millions of colors.

```json
{
  "format": "rgb",
  "pixels": [
    [[255, 0, 0], [255, 100, 0], null],
    [[255, 200, 0], [255, 255, 0], [200, 255, 100]],
    [null, [100, 255, 100], [0, 255, 0]]
  ]
}
```

- Each pixel is `[r, g, b]` where values are 0-255
- Use `null` for transparent pixels
- Supports 16.7 million colors (24-bit RGB)

### 2. Hex Format (Web-style colors)

Hex color strings like web CSS colors.

```json
{
  "format": "hex",
  "pixels": [
    ["#FF0000", "#FF6400", null],
    ["#FFC800", "#FFFF00", "#C8FF64"],
    [null, "#64FF64", "#00FF00"]
  ]
}
```

- Each pixel is a hex color string `"#RRGGBB"`
- Use `null` for transparent pixels
- Automatically converted to RGB internally

### 3. Palette Format (Retro 8-color)

Classic 8-color palette for retro aesthetic.

```json
{
  "format": "palette",
  "pixels": [
    [0, 1, 2, 3],
    [4, 5, 6, 7],
    [1, 2, 3, 4],
    [0, 0, 0, 0]
  ]
}
```

- Each pixel is an index 0-7
- 0 = transparent
- 1-7 = predefined palette colors (red, green, blue, yellow, cyan, magenta, white)
- Backward compatible with original MatrixOS icons

### 4. PNG Format (Design tool friendly!)

Load icons directly from PNG image files.

**Option A: Convert PNG to JSON** (recommended for deployment)
```bash
# Using the icon_utils tool
python matrixos/icon_utils.py myicon.png icon32.json 32
```

**Option B: Load PNG directly in launcher** (if Pillow installed)
```python
from matrixos.icon_utils import png_to_rgb

# Load PNG and get RGB data
rgb_data = png_to_rgb('myicon.png', size=32)

# Use in icon system
icon_data = {'format': 'rgb', 'pixels': rgb_data}
```

PNG Requirements:
- Any size (will be resized to 16×16 or 32×32)
- Alpha channel for transparency (or specify transparent_color)
- Nearest-neighbor scaling preserves pixel art
- Requires Pillow library: `pip install Pillow`

## Icon Sizes

- **16×16**: Small icons for 64×64 displays
- **32×32**: Standard icons for 128×128 displays (recommended)
- **48×48**: Large icons for 256×192 displays

Launcher automatically chooses:
- Tries `icon32.json` first for 128×128
- Falls back to `icon.json` (16×16)
- Scales up/down as needed

## Creating Icons

### Method 1: Design in Image Editor (Easiest!)

1. Create 32×32 PNG in Photoshop/GIMP/Aseprite
2. Use transparency for empty pixels
3. Convert to JSON:
   ```bash
   python matrixos/icon_utils.py myicon.png apps/myapp/icon32.json 32
   ```

### Method 2: Hand-code RGB (Full control)

```json
{
  "format": "rgb",
  "pixels": [
    [null, null, [255,0,0], [255,0,0], null, null],
    [null, [255,100,0], [255,200,0], [255,200,0], [255,100,0], null],
    [[255,0,0], [255,150,0], [255,255,0], [255,255,0], [255,150,0], [255,0,0]]
  ]
}
```

### Method 3: Use Hex Colors (Web designer friendly)

```json
{
  "format": "hex",
  "pixels": [
    [null, null, "#FF0000", "#FF0000", null, null],
    [null, "#FF6400", "#FFC800", "#FFC800", "#FF6400", null],
    ["#FF0000", "#FF9600", "#FFFF00", "#FFFF00", "#FF9600", "#FF0000"]
  ]
}
```

## Example Icons

### Gradient Clock (Timer)
```json
{
  "format": "rgb",
  "pixels": [
    [null, [255,220,100], [255,220,100], null],
    [[255,200,80], [255,255,255], [255,255,255], [255,200,80]],
    [[255,180,60], [255,255,255], [255,255,255], [255,180,60]],
    [null, [255,160,40], [255,160,40], null]
  ]
}
```

### Simple 8-Color Icon (Palette)
```json
{
  "format": "palette",
  "pixels": [
    [0, 1, 1, 0],
    [1, 7, 7, 1],
    [1, 7, 7, 1],
    [0, 1, 1, 0]
  ]
}
```

## Format Auto-Detection

Launcher automatically detects format:
- Checks `"format"` field if present
- Otherwise infers from pixel data structure:
  - `[[[r,g,b], ...]]` → RGB
  - `[["#RRGGBB", ...]]` → Hex  
  - `[[0-7, ...]]` → Palette

## Best Practices

1. **Use PNG workflow** for complex icons (gradients, anti-aliasing)
2. **Use RGB/Hex** for simple hand-coded icons
3. **Use Palette** for retro 8-color aesthetic
4. **Always provide 32×32** for 128×128 displays
5. **Test icons** at target resolution
6. **Use null** for transparency (not [0,0,0])

## Tools

- **icon_utils.py**: PNG ↔ JSON converter
- **Aseprite**: Excellent pixel art editor
- **GIMP**: Free image editor
- **Photoshop**: Professional option
- **Online**: Piskel, PixilArt (web-based)

## Example Workflow

```bash
# 1. Design icon in image editor (32×32 PNG)
# Save as: my_cool_icon.png

# 2. Convert to JSON format
python matrixos/icon_utils.py my_cool_icon.png apps/myapp/icon32.json 32

# 3. App config.json
{
  "name": "My App",
  "version": "1.0.0"
}

# 4. App structure:
apps/myapp/
├── config.json
├── icon.json      # 16×16 fallback
├── icon32.json    # 32×32 main icon (from PNG)
└── main.py

# Done! Launcher will display your beautiful icon.
```

## Color Palettes

**Retro 8-Color Palette** (palette format):
- 0: Transparent
- 1: Red (255, 0, 0)
- 2: Green (0, 255, 0)
- 3: Blue (0, 0, 255)
- 4: Yellow (255, 255, 0)
- 5: Cyan (0, 255, 255)
- 6: Magenta (255, 0, 255)
- 7: White (255, 255, 255)

**RGB Gradients** (recommended for modern look):
```json
// Orange to red gradient
[255, 220, 100] // Bright orange
[255, 200, 80]  // Orange
[255, 180, 60]  // Deep orange
[255, 160, 40]  // Orange-red
[255, 100, 20]  // Red-orange
[200, 50, 10]   // Dark red
[100, 20, 5]    // Very dark red
```

## FAQ

**Q: Can I use 24×24 icons?**
A: Yes, but 16/32/48 are recommended. The launcher will scale any size.

**Q: Do I need Pillow for PNG support?**
A: Only if loading PNG directly. Pre-converted JSON works without Pillow.

**Q: Can icons be animated?**
A: Not yet, but planned for future release!

**Q: What's the file size limit?**
A: No hard limit, but keep icons under 100KB. 32×32 RGB is ~10-15KB.

**Q: Can I use gradients with palette format?**
A: No, palette is limited to 8 colors. Use RGB or hex for gradients.

**Q: How do I make icons crisp and pixelated?**
A: Use nearest-neighbor scaling (automatic in icon_utils.py).
