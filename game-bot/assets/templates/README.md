# Template Images for Gem Recognition

This folder should contain template images for each gem type in your game.

## How to Create Templates

1. **Take a screenshot of your game board** when it's clearly visible
2. **Crop individual gems** - each should be the same size and show just the gem
3. **Save with consistent naming** matching your `config.yaml` gem types

## Example Structure

```
templates/
├── RED_FIRE.png
├── BLUE_LIGHTNING.png
├── GREEN_HEART.png
├── YELLOW_STAR.png
├── PURPLE_MOON.png
├── ORANGE_SUN.png
├── LOCKED.png
└── EMPTY.png
```

## Tips for Good Templates

- **Consistent size**: All templates should be the same dimensions
- **Clean images**: Remove any overlays, effects, or UI elements
- **Good contrast**: Clear, well-lit gems work best
- **Match actual game**: Templates should look exactly like in-game gems
- **Test different states**: Some gems may have idle animations - capture a neutral frame

## Template Image Size

The bot will automatically resize templates to match the cell size calculated from your board dimensions. However, starting with templates close to your actual cell size will improve matching accuracy.

### Recommended approach:

1. Calculate your cell size: `board_width / num_columns`
2. Create templates at approximately that size (±10 pixels is fine)
3. For an 8x8 board on 800x800 screen, templates should be around 100x100 pixels

## Testing Your Templates

After creating templates, run:

```bash
python board_reader.py
```

This will show which templates were loaded successfully.

## Adjusting Match Threshold

If templates aren't matching well:

1. Edit `config.yaml`
2. Change `matching.threshold` (default: 0.7)
   - Lower values (0.5-0.6) = more lenient matching
   - Higher values (0.8-0.9) = stricter matching
3. Test again

## File Formats

Supported formats: `.png`, `.jpg`, `.jpeg`, `.bmp`

PNG is recommended for best quality.
