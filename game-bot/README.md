# Match-3 Game Bot (Vision-Based)

A Python-based automation tool for playing match-3 puzzle games using computer vision and mouse control.

## ⚠️ Important Notes

- This bot is designed for **educational purposes** and games that **explicitly allow automation**
- Uses **vision-based** interaction only (no memory hacking, file modification, or network tampering)
- Mimics human behavior with randomized delays and movements

## 🎯 Features

- **Screen Capture**: Captures game board using MSS
- **Gem Recognition**: Template matching with OpenCV
- **Match-3 Logic**: Detects valid moves and matches
- **Smart Evaluation**: Scores moves based on multiple criteria
- **Human-like Control**: Randomized mouse movements and delays
- **Animation Detection**: Waits for board stability before next move

## 📋 Requirements

- Python 3.10 or higher
- Windows/Linux/Mac OS
- Game window must be visible on screen

## 🚀 Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📁 Project Structure

```
game-bot/
├── assets/
│   └── templates/          # Template images for each gem type
├── capture.py              # Screen capture module
├── board_reader.py         # Gem recognition
├── logic.py                # Match-3 game logic
├── evaluator.py            # Move scoring system
├── controller.py           # Mouse control
├── main.py                 # Main bot loop
├── config.yaml             # Configuration file
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## ⚙️ Configuration

### 1. Prepare Template Images

Create template images for each gem type in your game:

1. Take screenshots of each unique gem
2. Crop them to show just the gem (consistent size)
3. Save in `assets/templates/` with names matching your config:
   - `RED_FIRE.png`
   - `BLUE_LIGHTNING.png`
   - `GREEN_HEART.png`
   - etc.

### 2. Configure Board Coordinates

Edit `config.yaml` to match your game:

```yaml
screen:
  top: 200      # Top pixel of game board
  left: 400     # Left pixel of game board
  width: 800    # Board width in pixels
  height: 800   # Board height in pixels

board:
  rows: 8       # Number of rows
  cols: 8       # Number of columns
```

**To find coordinates:**

Run the calibration helper:
```python
from controller import MouseCalibration
config = MouseCalibration.calibrate_board()
```

Or use Windows Snipping Tool / PowerToys to identify pixel coordinates.

### 3. Adjust Other Settings

- **Gem types**: List all gem types in your game
- **Scoring rules**: Adjust point values
- **Mouse settings**: Modify drag duration and delays
- **Animation detection**: Tune stability check parameters

## 🎮 Usage

### Test Components First

Before running the bot, test that everything works:

```bash
python main.py --test
```

This will:
- Capture the screen
- Try to read the board
- Find valid moves
- Show you the results

### Run the Bot

1. **Open your game and navigate to the puzzle board**

2. **Make sure the game window is visible**

3. **Run the bot:**
   ```bash
   python main.py
   ```

4. **Optional arguments:**
   ```bash
   # Run for specific number of iterations
   python main.py --iterations 10

   # Use custom config file
   python main.py --config my_config.yaml
   ```

### Stop the Bot

- Press `Ctrl+C` to stop gracefully
- Move mouse to top-left corner for emergency stop (PyAutoGUI failsafe)

## 🧪 Testing Individual Modules

Each module can be tested independently:

```bash
# Test screen capture
python capture.py

# Test board reader
python board_reader.py

# Test match-3 logic
python logic.py

# Test move evaluator
python evaluator.py

# Test mouse controller
python controller.py
```

## 🔧 Troubleshooting

### "No templates loaded"
- Make sure template images are in `assets/templates/`
- Check that filenames match gem types in config.yaml
- Verify image file extensions (.png, .jpg, etc.)

### "No valid moves found"
- Templates may not be matching correctly
- Adjust `threshold` in config.yaml (try 0.6 or 0.5)
- Check if template images match the actual game gems

### "Low confidence warnings"
- Board might not be fully captured
- Templates might be wrong size
- Adjust screen coordinates in config

### Mouse not clicking correctly
- Re-calibrate board coordinates
- Check that game window hasn't moved
- Verify cell dimensions are correct

## 🎨 Customization

### Scoring System

Modify scoring rules in `config.yaml`:

```yaml
scoring:
  gem_removed: 10      # Points per gem removed
  unlock_tile: 20      # Bonus for unlocking tiles
  combo_bonus: 30      # Bonus for multiple matches
  special_gem: 50      # Bonus for special gem creation
  match_4: 40          # Bonus for 4-gem match
  match_5: 100         # Bonus for 5+ gem match
```

### Adding New Gem Types

1. Add gem name to `gems` list in config.yaml
2. Create template image in `assets/templates/`
3. Restart the bot

### Custom Move Strategy

Edit `evaluator.py` to implement your own scoring logic in the `score_move()` method.

## 📊 Debug Mode

Enable debug features in `config.yaml`:

```yaml
debug:
  show_board: true          # Display recognized board
  show_matches: true        # Highlight matches
  save_screenshots: true    # Save board captures
  verbose: true            # Detailed console output
```

## 🚧 Future Enhancements

Potential improvements:

- [ ] Combo chain prediction
- [ ] Priority targeting (e.g., specific objectives)
- [ ] Boss battle recognition
- [ ] Reinforcement learning for optimal play
- [ ] Multi-game support
- [ ] Auto pause/resume
- [ ] Performance statistics tracking

## 📄 License

This project is for educational purposes. Use responsibly and only on games that permit automation.

## ⚖️ Legal & Ethical Considerations

- ✅ Vision-based automation (mimics human player)
- ✅ No game file modification
- ✅ No memory injection
- ✅ No network tampering
- ⚠️ Always check game's Terms of Service
- ⚠️ Use only on games that allow automation

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📞 Support

If you encounter issues:

1. Check the Troubleshooting section
2. Run `python main.py --test` to diagnose
3. Review configuration settings
4. Check that all dependencies are installed

---

**Happy automating! 🎮🤖**
