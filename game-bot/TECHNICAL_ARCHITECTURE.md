# 🏗️ KIẾN TRÚC KỸ THUẬT - MATCH-3 AUTO BOT

## 📋 MỤC LỤC

1. [Tổng Quan Kiến Trúc](#1-tổng-quan-kiến-trúc)
2. [Luồng Hoạt Động Chính](#2-luồng-hoạt-động-chính)
3. [Chi Tiết Từng Module](#3-chi-tiết-từng-module)
4. [Thuật Toán Core](#4-thuật-toán-core)
5. [State Management](#5-state-management)
6. [Computer Vision Pipeline](#6-computer-vision-pipeline)
7. [AI Decision Making](#7-ai-decision-making)
8. [Automation Controller](#8-automation-controller)
9. [Best Practices](#9-best-practices)
10. [Áp Dụng Cho Dự Án Khác](#10-áp-dụng-cho-dự-án-khác)

---

## 1. TỔNG QUAN KIẾN TRÚC

### 1.1. Kiến Trúc Tầng (Layered Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                      (GUI - Tkinter)                         │
│  - User Interface                                            │
│  - Event Handlers                                            │
│  - Display Updates                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓↑
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│                  (Main Bot Controller)                       │
│  - Game Loop Management                                      │
│  - State Orchestration                                       │
│  - Error Handling                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓↑
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Game Logic  │  │  Evaluator   │  │ State Manager│      │
│  │              │  │              │  │              │      │
│  │ - Match Det. │  │ - Scoring    │  │ - UI States  │      │
│  │ - Valid Moves│  │ - Cascade    │  │ - Auto Click │      │
│  │ - Simulation │  │ - Priority   │  │ - Transitions│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓↑
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Board Reader  │  │Turn Detector │  │ Controller   │      │
│  │              │  │              │  │              │      │
│  │ - CV2        │  │ - OCR        │  │ - PyAutoGUI  │      │
│  │ - Template   │  │ - Color Det. │  │ - Mouse Move │      │
│  │ - Color Det. │  │ - Timer      │  │ - Drag/Drop  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓↑
┌─────────────────────────────────────────────────────────────┐
│                      SYSTEM LAYER                            │
│  - Screen Capture (MSS)                                      │
│  - OS API (Windows/Linux/Mac)                                │
│  - Hardware Interface (Mouse, Keyboard)                      │
└─────────────────────────────────────────────────────────────┘
```

### 1.2. Module Dependency Graph

```
gui_main.py
    ↓
main.py (GameBot)
    ├── capture.py (ScreenCapture)
    ├── board_reader_color.py (BoardReaderColor)
    ├── logic.py (MatchThreeLogic)
    ├── evaluator.py (MoveEvaluator)
    ├── controller.py (MouseController)
    ├── turn_detector.py (TurnDetector)
    └── game_state_manager.py (GameStateManager)
            └── ui_detector.py (UIDetector)
```

### 1.3. Data Flow Architecture

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Screen  │────>│  Board  │────>│  Game   │────>│  Move   │
│ Capture │     │ Reader  │     │  Logic  │     │Evaluator│
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     │           Board[8][8]     List[Move]     Best Move
     │           (Gem Types)     (Validated)    (Score)
     │
     ↓
┌─────────┐     ┌─────────┐     ┌─────────┐
│  Timer  │────>│Decision │────>│  Mouse  │
│Detector │     │ Engine  │     │Controller│
└─────────┘     └─────────┘     └─────────┘
     │               │               │
Timer Value     Execute?        Screen Click
```

---

## 2. LUỒNG HOẠT ĐỘNG CHÍNH

### 2.1. Main Loop Flow

```python
# PSEUDOCODE: Main Game Loop
def main_loop():
    initialize_all_components()
    
    WHILE bot_is_running:
        iteration += 1
        
        # ═══════════════════════════════════════════════
        # PHASE 1: PRE-GAME STATE HANDLING
        # ═══════════════════════════════════════════════
        IF game_automation_enabled:
            current_state = detect_game_state()
            
            IF current_state == REWARD_SCREEN:
                click_receive_button()
                wait(2 seconds)
                CONTINUE to next state
            
            ELIF current_state == MAP_SCREEN:
                click_battle_button()
                wait(2 seconds)
                CONTINUE to next state
            
            ELIF current_state == READY_SCREEN:
                click_start_button()
                wait(2 seconds)
                # Now in PLAYING state
        
        # ═══════════════════════════════════════════════
        # PHASE 2: TURN VALIDATION
        # ═══════════════════════════════════════════════
        IF turn_detection_enabled:
            timer_value = detect_timer_on_screen()
            
            IF timer_value == NULL:
                # No timer = not in game or waiting
                handle_pre_game_states()
                CONTINUE
            
            IF timer_value < MIN_TIMER_THRESHOLD:
                # Not enough time to make move
                wait_for_next_turn()
                CONTINUE
            
            # Timer OK → Continue to gameplay
        
        # ═══════════════════════════════════════════════
        # PHASE 3: BOARD STABILITY CHECK
        # ═══════════════════════════════════════════════
        is_stable = wait_for_board_stability()
        
        IF NOT is_stable:
            log("Board unstable - animations running")
            CONTINUE
        
        # ═══════════════════════════════════════════════
        # PHASE 4: BOARD RECOGNITION
        # ═══════════════════════════════════════════════
        screenshot = capture_screen(board_region)
        board_matrix = recognize_gems(screenshot)
        # board_matrix[8][8] = 2D array of gem types
        
        IF board_matrix == NULL:
            log("Failed to read board")
            CONTINUE
        
        # ═══════════════════════════════════════════════
        # PHASE 5: MOVE GENERATION
        # ═══════════════════════════════════════════════
        valid_moves = find_all_valid_moves(board_matrix)
        # Scan all 64 cells × 4 directions = 256 attempts
        
        IF valid_moves.is_empty():
            log("No valid moves found")
            CONTINUE
        
        # ═══════════════════════════════════════════════
        # PHASE 6: MOVE EVALUATION
        # ═══════════════════════════════════════════════
        best_move = evaluate_and_select_best(valid_moves, board_matrix)
        # Score based on: gems removed, cascades, special gems
        
        # ═══════════════════════════════════════════════
        # PHASE 7: MOVE EXECUTION
        # ═══════════════════════════════════════════════
        execute_move_on_screen(best_move)
        # Convert grid coordinates to screen coordinates
        # Perform mouse drag and drop
        
        # ═══════════════════════════════════════════════
        # PHASE 8: POST-MOVE DELAY
        # ═══════════════════════════════════════════════
        update_statistics(best_move)
        random_delay(2.0 to 3.0 seconds)
        # Human-like delay between moves
    
    cleanup_and_exit()
```

### 2.2. Detailed Flow Diagram

```
START
  │
  ├─► [1] Initialize Components
  │      ├─ Load config.yaml
  │      ├─ Create ScreenCapture
  │      ├─ Create BoardReader
  │      ├─ Create Logic Engine
  │      ├─ Create Evaluator
  │      ├─ Create Controller
  │      └─ Create State Manager
  │
  ├─► [2] Start Main Loop
  │      │
  │      └─► Check: Game State
  │             │
  │             ├─ REWARD? ──► Click "Nhận" ──► Wait 2s ──┐
  │             ├─ MAP? ─────► Click "Chiến" ──► Wait 2s ─┤
  │             ├─ READY? ───► Click "Bắt đầu" ─► Wait 2s ┤
  │             │                                          │
  │             └─ PLAYING ◄──────────────────────────────┘
  │                  │
  │                  ├─► Check: Timer
  │                  │      ├─ No Timer? ──► Go back to State Check
  │                  │      ├─ Timer < 2s? ─► Wait for next turn
  │                  │      └─ Timer ≥ 2s? ──► Continue ✓
  │                  │
  │                  ├─► Wait: Board Stability
  │                  │      ├─ Capture Frame 1 ──► Gray Convert
  │                  │      ├─ Wait 100ms
  │                  │      ├─ Capture Frame 2 ──► Gray Convert
  │                  │      ├─ Wait 100ms
  │                  │      ├─ Capture Frame 3 ──► Gray Convert
  │                  │      ├─ Calculate Diff(F1, F2)
  │                  │      ├─ Calculate Diff(F2, F3)
  │                  │      └─ All Diffs < 0.02? ──► Stable ✓
  │                  │
  │                  ├─► Capture & Read Board
  │                  │      ├─ Screenshot board region
  │                  │      ├─ Split into 64 cells
  │                  │      ├─ FOR each cell:
  │                  │      │    ├─ Extract HSV colors
  │                  │      │    ├─ Match color patterns
  │                  │      │    └─ Identify gem type
  │                  │      └─ Build board[8][8] matrix
  │                  │
  │                  ├─► Find Valid Moves
  │                  │      ├─ FOR row = 0 to 7:
  │                  │      │    FOR col = 0 to 7:
  │                  │      │       FOR direction in [UP,DOWN,LEFT,RIGHT]:
  │                  │      │          ├─ Create board_copy
  │                  │      │          ├─ Swap(current, neighbor)
  │                  │      │          ├─ Check matches at both positions
  │                  │      │          └─ IF matches exist: Add to valid_moves[]
  │                  │      └─ Return List[Move]
  │                  │
  │                  ├─► Evaluate Moves
  │                  │      ├─ FOR each move in valid_moves:
  │                  │      │    ├─ Score base gems removed
  │                  │      │    ├─ Detect special matches (4, 5)
  │                  │      │    ├─ Simulate cascade:
  │                  │      │    │    WHILE new matches found:
  │                  │      │    │       ├─ Remove matched gems
  │                  │      │    │       ├─ Apply gravity
  │                  │      │    │       ├─ Gems fall down
  │                  │      │    │       ├─ Find new matches
  │                  │      │    │       └─ cascade_depth++
  │                  │      │    ├─ Calculate position bonus
  │                  │      │    ├─ Calculate priority bonus
  │                  │      │    └─ Total score = SUM(all bonuses)
  │                  │      └─ Return move with MAX(score)
  │                  │
  │                  ├─► Execute Move
  │                  │      ├─ from_pos → screen_coords(x1, y1)
  │                  │      ├─ to_pos → screen_coords(x2, y2)
  │                  │      ├─ Add random offset (±5px)
  │                  │      ├─ moveTo(x1, y1, duration=0.3s)
  │                  │      ├─ Wait 0.1s
  │                  │      ├─ drag(x2-x1, y2-y1, duration=0.3s)
  │                  │      └─ Wait 0.15s
  │                  │
  │                  ├─► Update Stats
  │                  │      ├─ move_count++
  │                  │      ├─ total_score += move_score
  │                  │      └─ Log to console/GUI
  │                  │
  │                  └─► Random Delay
  │                         └─ Wait 2.0 - 3.0 seconds
  │
  └─► Loop Back to [2]
```

---

## 3. CHI TIẾT TỪNG MODULE

### 3.1. Screen Capture Module

**File:** `capture.py`

**Chức năng:** Chụp màn hình game với hiệu suất cao

**Technical Details:**

```python
class ScreenCapture:
    """
    Sử dụng MSS (Multiple Screen Shots) library
    - Nhanh hơn PIL.ImageGrab 30-50%
    - Không block main thread
    - Cross-platform (Windows, Linux, Mac)
    """
    
    def __init__(self, top, left, width, height):
        self.monitor = {
            'top': top,      # Y coordinate
            'left': left,    # X coordinate
            'width': width,  # Region width
            'height': height # Region height
        }
    
    def capture_board(self):
        """
        Capture và convert về BGR format (OpenCV compatible)
        
        Performance: ~15-20ms per capture
        """
        with mss.mss() as sct:
            # Grab screenshot as PIL Image
            screenshot = sct.grab(self.monitor)
            
            # Convert BGRA → BGR
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
        return img  # numpy.ndarray, shape=(H,W,3), dtype=uint8
```

**Key Optimizations:**
- Context manager (`with`) để tự động cleanup
- Direct numpy array conversion (zero-copy)
- BGR format để tương thích với OpenCV

**Performance Metrics:**
- Capture time: 15-20ms
- Memory: ~1-2 MB per screenshot (800×600 region)
- CPU: 2-3% on modern processors

---

### 3.2. Board Reader Module

**File:** `board_reader_color.py`

**Chức năng:** Nhận diện loại gem từ màu sắc

**Computer Vision Pipeline:**

```python
class BoardReaderColor:
    def read_board(self, board_img):
        """
        INPUT: board_img (H×W×3 BGR image)
        OUTPUT: board[8][8] (2D list of gem types)
        
        Pipeline:
        1. Split image into 64 cells
        2. For each cell:
           a. Convert BGR → HSV
           b. Extract dominant colors
           c. Match color patterns
           d. Identify gem type
        """
        
        # ──────────────────────────────────────────
        # STEP 1: Cell Extraction
        # ──────────────────────────────────────────
        cells = self.split_into_cells(board_img)
        # cells[row][col] = cell_image (cell_h × cell_w × 3)
        
        board = []
        for row in range(8):
            row_gems = []
            for col in range(8):
                cell_img = cells[row][col]
                
                # ──────────────────────────────────────────
                # STEP 2: Color Space Conversion
                # ──────────────────────────────────────────
                hsv = cv2.cvtColor(cell_img, cv2.COLOR_BGR2HSV)
                
                # ──────────────────────────────────────────
                # STEP 3: Color Detection
                # ──────────────────────────────────────────
                gem_type = self.detect_gem_by_color(hsv)
                row_gems.append(gem_type)
            
            board.append(row_gems)
        
        return board
    
    def detect_gem_by_color(self, hsv_img):
        """
        Color Matching Algorithm
        
        Uses HSV color ranges for robustness against lighting
        """
        # Define color ranges (H: 0-180, S: 0-255, V: 0-255)
        color_ranges = {
            'RED': ([0, 100, 100], [10, 255, 255]),      # Red hue
            'BLUE': ([100, 100, 100], [130, 255, 255]),  # Blue hue
            'GREEN': ([40, 50, 50], [80, 255, 255]),     # Green hue
            'YELLOW': ([20, 100, 100], [30, 255, 255]),  # Yellow hue
            'PURPLE': ([130, 50, 50], [160, 255, 255]),  # Purple hue
            'ORANGE': ([10, 100, 100], [20, 255, 255]),  # Orange hue
        }
        
        best_match = "UNKNOWN"
        max_coverage = 0
        
        for gem_type, (lower, upper) in color_ranges.items():
            # Create color mask
            mask = cv2.inRange(hsv_img, 
                              np.array(lower), 
                              np.array(upper))
            
            # Calculate coverage percentage
            coverage = np.sum(mask > 0) / mask.size
            
            if coverage > max_coverage and coverage > 0.15:
                max_coverage = coverage
                best_match = gem_type
        
        return best_match
```

**Algorithm Explanation:**

```
HSV Color Space:
- H (Hue): Color type (0-180°)
- S (Saturation): Color intensity (0-255)
- V (Value): Brightness (0-255)

Why HSV?
- More robust than RGB for color detection
- Less affected by lighting variations
- Easier to define color ranges

Example: RED gem detection
- Hue: 0-10° (red in color wheel)
- Saturation: 100-255 (vivid color)
- Value: 100-255 (not too dark)

Mask Operation:
- cv2.inRange() creates binary mask
- White pixels = color match
- Black pixels = no match
- Coverage = white_pixels / total_pixels
```

**Performance:**
- Time per cell: ~1-2ms
- Total board read: 64 cells × 2ms = ~128ms
- Accuracy: 95-98% under normal lighting

---

### 3.3. Game Logic Module

**File:** `logic.py`

**Chức năng:** Xử lý game logic (match detection, move finding)

#### 3.3.1. Match Detection Algorithm

```python
def find_matches_at_position(board, pos):
    """
    Two-directional scan algorithm
    
    Time Complexity: O(1) - constant time per position
    Space Complexity: O(1) - constant space
    """
    gem_type = board[pos.row][pos.col]
    matches = []
    
    # ═══════════════════════════════════════════════════
    # HORIZONTAL SCAN (Left ← → Right)
    # ═══════════════════════════════════════════════════
    h_positions = [pos]
    
    # Scan LEFT ←
    col = pos.col - 1
    WHILE col >= 0 AND board[pos.row][col] == gem_type:
        h_positions.append(Position(pos.row, col))
        col -= 1
    
    # Scan RIGHT →
    col = pos.col + 1
    WHILE col < 8 AND board[pos.row][col] == gem_type:
        h_positions.append(Position(pos.row, col))
        col += 1
    
    # Check if match (≥3)
    IF len(h_positions) >= 3:
        matches.append(Match(
            positions=h_positions,
            gem_type=gem_type,
            length=len(h_positions),
            direction="horizontal"
        ))
    
    # ═══════════════════════════════════════════════════
    # VERTICAL SCAN (Up ↑ ↓ Down)
    # ═══════════════════════════════════════════════════
    v_positions = [pos]
    
    # Scan UP ↑
    row = pos.row - 1
    WHILE row >= 0 AND board[row][pos.col] == gem_type:
        v_positions.append(Position(row, pos.col))
        row -= 1
    
    # Scan DOWN ↓
    row = pos.row + 1
    WHILE row < 8 AND board[row][pos.col] == gem_type:
        v_positions.append(Position(row, pos.col))
        row += 1
    
    # Check if match (≥3)
    IF len(v_positions) >= 3:
        matches.append(Match(
            positions=v_positions,
            gem_type=gem_type,
            length=len(v_positions),
            direction="vertical"
        ))
    
    RETURN matches
```

**Visual Example:**

```
Board:
  0 1 2 3 4 5 6 7
0 R B G Y P O R B
1 B R B G R G B R
2 G G R B G R G B
3 R R R R B G R B  ← Check position (3,2)
4 B G B G R G B R
5 G R G R B R G B
6 R B R B G B R B
7 B G B G R G B R

Horizontal Scan at (3,2):
- Current: (3,2) = R
- Left:  (3,1) = R ✓
        (3,0) = R ✓
        (3,-1) = out of bounds
- Right: (3,3) = R ✓
        (3,4) = B ✗

h_positions = [(3,0), (3,1), (3,2), (3,3)]
length = 4 ≥ 3 → MATCH! (Match-4)

Vertical Scan at (3,2):
- Current: (3,2) = R
- Up:    (2,2) = R ✓
        (1,2) = B ✗
- Down:  (4,2) = B ✗

v_positions = [(2,2), (3,2)]
length = 2 < 3 → No match

Result: 1 horizontal match of length 4
```

#### 3.3.2. Valid Move Finding Algorithm

```python
def find_valid_moves(board):
    """
    Brute-force search with optimization
    
    Time Complexity: O(N×M×D) where:
    - N = rows (8)
    - M = cols (8)
    - D = directions (4)
    Total: 8×8×4 = 256 swap checks
    
    Optimization: Early termination when match found
    """
    valid_moves = []
    
    FOR row = 0 TO 7:
        FOR col = 0 TO 7:
            current_pos = Position(row, col)
            current_gem = board[row][col]
            
            # Skip invalid cells
            IF current_gem IN ["EMPTY", "LOCKED", "UNKNOWN"]:
                CONTINUE
            
            # Try 4 directions
            FOR direction IN [UP, DOWN, LEFT, RIGHT]:
                neighbor_pos = calculate_neighbor(current_pos, direction)
                
                # Bounds check
                IF NOT is_valid_position(neighbor_pos):
                    CONTINUE
                
                neighbor_gem = board[neighbor_pos.row][neighbor_pos.col]
                
                # Skip invalid neighbors
                IF neighbor_gem IN ["EMPTY", "LOCKED", "UNKNOWN"]:
                    CONTINUE
                
                # ═══════════════════════════════════════════
                # SWAP SIMULATION
                # ═══════════════════════════════════════════
                board_copy = deep_copy(board)
                swap_gems(board_copy, current_pos, neighbor_pos)
                
                # ═══════════════════════════════════════════
                # MATCH DETECTION
                # ═══════════════════════════════════════════
                matches_at_current = find_matches_at_position(
                    board_copy, current_pos
                )
                matches_at_neighbor = find_matches_at_position(
                    board_copy, neighbor_pos
                )
                
                all_matches = matches_at_current + matches_at_neighbor
                
                # Remove duplicates
                unique_matches = remove_duplicate_matches(all_matches)
                
                # ═══════════════════════════════════════════
                # VALID MOVE CHECK
                # ═══════════════════════════════════════════
                IF unique_matches.is_not_empty():
                    move = Move(
                        from_pos=current_pos,
                        to_pos=neighbor_pos,
                        direction=direction,
                        matches=unique_matches
                    )
                    valid_moves.append(move)
    
    RETURN valid_moves
```

**Optimization Strategies:**

1. **Early Termination:**
   - Nếu swap không tạo match → Skip ngay
   - Không cần simulate cascade ở bước này

2. **Duplicate Avoidance:**
   - Move (A→B) và (B→A) là giống nhau
   - Chỉ lưu một trong hai

3. **Cache Board Copy:**
   - Reuse board copy structure
   - Reduce memory allocation overhead

#### 3.3.3. Cascade Simulation

```python
def simulate_cascade(board_after_move, initial_matches):
    """
    Recursive cascade simulation
    
    Models real game physics:
    1. Remove matched gems
    2. Apply gravity (gems fall)
    3. Check for new matches
    4. Repeat until stable
    """
    
    current_board = deep_copy(board_after_move)
    current_matches = initial_matches
    
    cascade_depth = 0
    total_gems_removed = 0
    all_cascade_chains = []
    
    MAX_CASCADE_DEPTH = 5  # Prevent infinite loop
    
    FOR iteration = 0 TO MAX_CASCADE_DEPTH:
        IF current_matches.is_empty():
            BREAK  # No more matches → Stable
        
        cascade_depth += 1
        
        # ═══════════════════════════════════════════════
        # STEP 1: COLLECT MATCHED POSITIONS
        # ═══════════════════════════════════════════════
        removed_positions = SET()
        FOR match IN current_matches:
            FOR pos IN match.positions:
                removed_positions.add(pos)
        
        total_gems_removed += len(removed_positions)
        all_cascade_chains.append(current_matches)
        
        # ═══════════════════════════════════════════════
        # STEP 2: REMOVE GEMS (Set to EMPTY)
        # ═══════════════════════════════════════════════
        FOR pos IN removed_positions:
            current_board[pos.row][pos.col] = "EMPTY"
        
        # ═══════════════════════════════════════════════
        # STEP 3: APPLY GRAVITY
        # ═══════════════════════════════════════════════
        current_board = apply_gravity(current_board)
        
        # ═══════════════════════════════════════════════
        # STEP 4: FIND NEW MATCHES
        # ═══════════════════════════════════════════════
        current_matches = find_all_matches(current_board)
        
        # Filter out EMPTY gems (simulation artifact)
        current_matches = filter_valid_matches(current_matches)
        
        IF current_matches.is_empty():
            BREAK  # Cascade ended
    
    RETURN {
        'cascade_depth': cascade_depth,
        'total_gems_removed': total_gems_removed,
        'cascade_chains': all_cascade_chains
    }


def apply_gravity(board):
    """
    Column-by-column gravity simulation
    
    Algorithm:
    1. For each column
    2. Collect non-EMPTY gems from bottom to top
    3. Place them back from bottom
    4. Fill top with EMPTY
    """
    new_board = create_empty_board(8, 8)
    
    FOR col = 0 TO 7:
        # ═══════════════════════════════════════════════
        # Collect gems (bottom → top)
        # ═══════════════════════════════════════════════
        gems = []
        FOR row = 7 DOWN_TO 0:  # Bottom to top
            gem = board[row][col]
            IF gem NOT IN ["EMPTY", "LOCKED"]:
                gems.append(gem)
        
        # ═══════════════════════════════════════════════
        # Place gems back (bottom → top)
        # ═══════════════════════════════════════════════
        row = 7  # Start from bottom
        FOR gem IN gems:
            new_board[row][col] = gem
            row -= 1
        
        # ═══════════════════════════════════════════════
        # Fill remaining with EMPTY
        # ═══════════════════════════════════════════════
        WHILE row >= 0:
            new_board[row][col] = "EMPTY"
            row -= 1
    
    RETURN new_board
```

**Cascade Example:**

```
Initial Board After Move:
R _ _ B    (Match: Row 0, cols 0-2 removed)
G B G R
B G B G
R B R B

Apply Gravity (Column 1):
_ B G R
G _ B R
B G B G
R B R B

↓ Collect: [B, G, B, B] (bottom to top)
↓ Place back from bottom:

_ _ _ R
G B G R
B G B G
R B R B

Find New Matches:
- Check all positions
- Column 1: B-G-B-B → B B B (rows 4-5-6-7) → Match!

Cascade continues...
```

---

### 3.4. Move Evaluator Module

**File:** `evaluator.py`

**Chức năng:** AI decision making - chọn nước đi tối ưu

#### 3.4.1. Scoring Function

```python
def score_move(move, board, logic):
    """
    Multi-criteria scoring function
    
    Weights:
    - Immediate gems: 40%
    - Cascade effect: 35%
    - Special gems: 15%
    - Position: 10%
    """
    
    total_score = 0
    
    # ═══════════════════════════════════════════════════
    # CRITERION 1: BASE GEMS REMOVED (40%)
    # ═══════════════════════════════════════════════════
    immediate_gems = count_matched_gems(move.matches)
    base_score = immediate_gems * POINTS_PER_GEM  # 10 points each
    total_score += base_score
    
    # ═══════════════════════════════════════════════════
    # CRITERION 2: COMBO MULTIPLIER
    # ═══════════════════════════════════════════════════
    IF len(move.matches) > 1:  # Multiple matches at once
        combo_bonus = base_score * 0.5 * len(move.matches)
        total_score += combo_bonus
    
    # ═══════════════════════════════════════════════════
    # CRITERION 3: SPECIAL GEM BONUS (15%)
    # ═══════════════════════════════════════════════════
    FOR match IN move.matches:
        IF match.length == 4:
            total_score += MATCH_4_BONUS  # 100 points
        ELIF match.length >= 5:
            total_score += MATCH_5_BONUS  # 300 points
    
    # ═══════════════════════════════════════════════════
    # CRITERION 4: CASCADE SIMULATION (35%)
    # ═══════════════════════════════════════════════════
    board_after_move = apply_move_to_board(board, move)
    cascade_result = simulate_cascade(board_after_move, move.matches)
    
    cascade_score = 0
    cascade_score += (cascade_result.depth - 1) * 80
    cascade_score += cascade_result.extra_gems * 25
    cascade_score += cascade_result.extra_matches * 60
    
    total_score += cascade_score
    
    # ═══════════════════════════════════════════════════
    # CRITERION 5: POSITION BONUS (10%)
    # ═══════════════════════════════════════════════════
    position_score = calculate_position_bonus(move.from_pos)
    total_score += position_score
    
    # ═══════════════════════════════════════════════════
    # CRITERION 6: GEM TYPE PRIORITY
    # ═══════════════════════════════════════════════════
    # Prioritize rare gems or objective gems
    priority_score = calculate_gem_priority(move, board)
    total_score += priority_score
    
    # ═══════════════════════════════════════════════════
    # CRITERION 7: FUTURE SETUP BONUS
    # ═══════════════════════════════════════════════════
    # Moves that create opportunities for future big matches
    setup_score = evaluate_future_potential(board_after_move)
    total_score += setup_score
    
    RETURN total_score


def calculate_position_bonus(position):
    """
    Position-based scoring heuristics
    
    Strategy:
    - Bottom rows: Higher score (more likely to cascade)
    - Edges: Medium score (stable)
    - Center: Lower score (volatile)
    """
    
    row = position.row
    col = position.col
    bonus = 0
    
    # Bottom rows bonus (easier to create cascades)
    IF row >= 5:  # Rows 5,6,7
        bonus += 50
    ELIF row >= 3:  # Rows 3,4
        bonus += 20
    
    # Edge bonus (less affected by cascades)
    IF col == 0 OR col == 7:
        bonus += 20
    
    # Corner bonus
    IF (row == 0 OR row == 7) AND (col == 0 OR col == 7):
        bonus += 30
    
    RETURN bonus


def calculate_gem_priority(move, board):
    """
    Dynamic gem prioritization
    
    Strategy:
    - Count gem distribution on board
    - Rare gems get higher priority
    - Aligns with game objectives
    """
    
    gem_counts = count_all_gems(board)
    priority_score = 0
    
    FOR match IN move.matches:
        gem_type = match.gem_type
        count = gem_counts[gem_type]
        
        # Inverse priority: fewer gems = higher score
        IF count <= 5:
            priority_score += 50  # Very rare
        ELIF count <= 10:
            priority_score += 30  # Rare
        ELIF count <= 15:
            priority_score += 15  # Medium
        # Common gems get no bonus
    
    RETURN priority_score
```

#### 3.4.2. Best Move Selection

```python
def get_best_move(valid_moves, board, logic, max_time=0.5):
    """
    Evaluate all moves and select best
    
    Time Constraint: max_time seconds
    - If too many moves, use sampling
    - If within time, evaluate all
    """
    
    IF valid_moves.is_empty():
        RETURN None, 0
    
    start_time = current_time()
    evaluated_moves = []
    
    # ═══════════════════════════════════════════════════
    # SAMPLING STRATEGY (if too many moves)
    # ═══════════════════════════════════════════════════
    IF len(valid_moves) > 30:
        # Quick pre-filter: sort by immediate match count
        valid_moves = sort_by_match_count(valid_moves)
        # Keep top 30 candidates
        valid_moves = valid_moves[:30]
    
    # ═══════════════════════════════════════════════════
    # EVALUATION LOOP
    # ═══════════════════════════════════════════════════
    FOR move IN valid_moves:
        # Time check
        elapsed = current_time() - start_time
        IF elapsed > max_time:
            BREAK  # Time limit exceeded
        
        # Score the move
        score = score_move(move, board, logic)
        
        evaluated_moves.append((move, score))
    
    # ═══════════════════════════════════════════════════
    # SELECT BEST
    # ═══════════════════════════════════════════════════
    IF evaluated_moves.is_empty():
        RETURN valid_moves[0], 0  # Fallback to first move
    
    # Sort by score (descending)
    evaluated_moves.sort(key=lambda x: x[1], reverse=True)
    
    best_move, best_score = evaluated_moves[0]
    
    RETURN best_move, best_score
```

**Performance Optimization:**

```
Scenario 1: Few moves (<20)
- Evaluate all moves completely
- Time: ~100-200ms

Scenario 2: Many moves (20-50)
- Evaluate all with time check
- Time: ~300-500ms

Scenario 3: Too many moves (>50)
- Pre-filter to top 30
- Evaluate top candidates
- Time: ~400-500ms (capped)

Trade-off:
- Accuracy vs Speed
- In practice: Top 30 moves contain optimal ~95% of time
```

---

### 3.5. Mouse Controller Module

**File:** `controller.py`

**Chức năng:** Thực hiện move trên màn hình

#### 3.5.1. Coordinate Transformation

```python
def grid_to_screen(grid_pos):
    """
    Convert grid coordinates to screen coordinates
    
    Transformation:
    Grid (row, col) → Screen (x, y pixels)
    """
    
    row, col = grid_pos.row, grid_pos.col
    
    # Calculate cell center
    screen_x = board_left + (col * cell_width) + (cell_width // 2)
    screen_y = board_top + (row * cell_height) + (cell_height // 2)
    
    RETURN (screen_x, screen_y)


# Example:
# Board region: top=200, left=300, width=800, height=800
# Cell size: 800/8 = 100px
#
# Grid position: (3, 5)
# screen_x = 300 + (5 * 100) + 50 = 850
# screen_y = 200 + (3 * 100) + 50 = 550
# → Screen: (850, 550)
```

#### 3.5.2. Human-like Movement

```python
def execute_move(move):
    """
    Execute move with human-like behavior
    
    Features:
    - Random offset (±5px)
    - Smooth easing
    - Variable timing
    - Natural pauses
    """
    
    # ═══════════════════════════════════════════════════
    # STEP 1: COORDINATE CALCULATION
    # ═══════════════════════════════════════════════════
    from_x, from_y = grid_to_screen(move.from_pos)
    to_x, to_y = grid_to_screen(move.to_pos)
    
    # ═══════════════════════════════════════════════════
    # STEP 2: HUMANIZATION - Random Offset
    # ═══════════════════════════════════════════════════
    # Add ±5 pixel random offset to avoid perfect clicks
    from_x += random.randint(-5, 5)
    from_y += random.randint(-5, 5)
    to_x += random.randint(-5, 5)
    to_y += random.randint(-5, 5)
    
    # ═══════════════════════════════════════════════════
    # STEP 3: MOUSE MOVEMENT (with easing)
    # ═══════════════════════════════════════════════════
    pyautogui.moveTo(
        from_x, from_y,
        duration=random.uniform(0.25, 0.35),  # Variable speed
        tween=pyautogui.easeInOutQuad        # Smooth acceleration
    )
    
    # ═══════════════════════════════════════════════════
    # STEP 4: PAUSE (Human reaction time)
    # ═══════════════════════════════════════════════════
    time.sleep(random.uniform(0.08, 0.12))  # 80-120ms
    
    # ═══════════════════════════════════════════════════
    # STEP 5: DRAG & DROP
    # ═══════════════════════════════════════════════════
    pyautogui.mouseDown()  # Press
    time.sleep(0.05)       # Hold for 50ms
    
    pyautogui.moveTo(
        to_x, to_y,
        duration=random.uniform(0.25, 0.35),
        tween=pyautogui.easeInOutQuad
    )
    
    time.sleep(0.05)       # Hold at destination
    pyautogui.mouseUp()    # Release
    
    # ═══════════════════════════════════════════════════
    # STEP 6: POST-MOVE DELAY
    # ═══════════════════════════════════════════════════
    time.sleep(random.uniform(0.12, 0.18))  # 120-180ms
```

**Easing Functions:**

```
Linear:          ————————————— (Robotic)
                 Constant speed

EaseInOutQuad:   ——————————    (Natural)
                ╱          ╲   
               ╱            ╲  
              ╱              ╲ 
             ╱                ╲
            ╱                  ╲

- Slow start (acceleration)
- Fast middle (constant speed)
- Slow end (deceleration)
- Mimics human hand movement
```

**Anti-Detection Features:**

1. **Random Offset:**
   - Prevents pixel-perfect clicks
   - ±5px variation

2. **Variable Timing:**
   - Duration: 0.25-0.35s (not constant)
   - Delays: 0.08-0.18s (random)

3. **Smooth Easing:**
   - Natural acceleration/deceleration
   - Not linear robot movement

4. **Micro-pauses:**
   - Reaction time: 80-120ms
   - Hold time: 50ms

---

### 3.6. Turn Detector Module

**File:** `turn_detector.py`

**Chức năng:** Phát hiện lượt chơi và timer

#### 3.6.1. Timer Detection

```python
def detect_timer_value(screen_img):
    """
    Multi-method timer detection
    
    Method 1: Color detection (fast)
    Method 2: OCR (accurate)
    """
    
    # ═══════════════════════════════════════════════════
    # EXTRACT TIMER REGION
    # ═══════════════════════════════════════════════════
    region = timer_region  # From config
    roi = screen_img[
        region['top']:region['top'] + region['height'],
        region['left']:region['left'] + region['width']
    ]
    
    # ═══════════════════════════════════════════════════
    # METHOD 1: COLOR-BASED DETECTION
    # ═══════════════════════════════════════════════════
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Detect yellow/white numbers (typical timer colors)
    lower_yellow = np.array([15, 100, 100])
    upper_yellow = np.array([35, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # If insufficient yellow, try white
    IF np.sum(mask > 0) < 100:
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # Clean up mask
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # ═══════════════════════════════════════════════════
    # METHOD 2: OCR
    # ═══════════════════════════════════════════════════
    text = pytesseract.image_to_string(
        mask,
        config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
    )
    # psm 7 = single text line
    # oem 3 = default OCR engine
    # whitelist = only digits
    
    # Extract number
    numbers = re.findall(r'\d+', text)
    
    IF numbers:
        timer_value = int(numbers[0])
        
        # Validate range
        IF 0 <= timer_value <= 10:
            RETURN timer_value
    
    RETURN None  # Detection failed
```

**OCR Configuration Explained:**

```
Tesseract Config:
--psm 7 : Page Segmentation Mode 7 (single text line)
    - Best for timer numbers (single line)
    - Faster than auto-detection

--oem 3 : OCR Engine Mode 3 (default)
    - Legacy + LSTM
    - Best accuracy/speed balance

-c tessedit_char_whitelist=0123456789
    - Only recognize digits 0-9
    - Prevents false detection of letters
    - Improves accuracy from ~80% to ~95%
```

#### 3.6.2. Turn Detection

```python
def is_action_allowed(screen_img, min_timer_value=2):
    """
    Decision logic: Can we make a move?
    
    Conditions:
    1. Is it my turn?
    2. Is timer visible?
    3. Is timer above threshold?
    """
    
    result = {
        "allowed": False,
        "reason": "",
        "timer": None,
        "is_my_turn": False
    }
    
    # ═══════════════════════════════════════════════════
    # CHECK 1: TURN INDICATOR
    # ═══════════════════════════════════════════════════
    is_my_turn = detect_your_turn_text(screen_img)
    result["is_my_turn"] = is_my_turn
    
    IF NOT is_my_turn:
        result["reason"] = "Not your turn"
        RETURN result
    
    # ═══════════════════════════════════════════════════
    # CHECK 2: TIMER VALUE
    # ═══════════════════════════════════════════════════
    timer = detect_timer_value(screen_img)
    result["timer"] = timer
    
    IF timer == None:
        result["reason"] = "Timer not detected"
        RETURN result
    
    # ═══════════════════════════════════════════════════
    # CHECK 3: TIME THRESHOLD
    # ═══════════════════════════════════════════════════
    IF timer < min_timer_value:
        result["reason"] = f"Timer too low ({timer}s)"
        RETURN result
    
    # ═══════════════════════════════════════════════════
    # ALL CHECKS PASSED
    # ═══════════════════════════════════════════════════
    result["allowed"] = True
    result["reason"] = "Action allowed"
    RETURN result
```

**Safety Margin Explanation:**

```
Why min_timer_value = 2?

Timeline:
t=2.0s  Start processing
t=2.5s  Board stable
t=2.7s  Board read complete
t=3.2s  Moves found & evaluated
t=3.8s  Move executed
────────────────────────────
Total: ~1.8 seconds

Safety margin:
- Processing: ~1.5s
- Network lag: ~0.3s
- Buffer: ~0.2s
────────────────────────────
Minimum safe: 2.0s

If timer < 2s:
- Risk of timeout during execution
- Better to skip and wait for next turn
```

---

### 3.7. Game State Manager Module

**File:** `game_state_manager.py`

**Chức năng:** Quản lý state transitions và automation

#### 3.7.1. State Detection

```python
class GameState(Enum):
    PLAYING = "playing"    # Match-3 gameplay
    REWARD = "reward"      # Reward screen (WIN/LOSE)
    MAP = "map"            # Map selection
    READY = "ready"        # Pre-battle ready screen
    UNKNOWN = "unknown"    # Cannot determine


def detect_current_state(screenshot):
    """
    State detection via UI button recognition
    
    Logic:
    - Detect which buttons are visible
    - Infer game state from button presence
    """
    
    # ═══════════════════════════════════════════════════
    # BUTTON DETECTION
    # ═══════════════════════════════════════════════════
    buttons = detect_all_buttons(screenshot)
    # Returns: {"nhan": pos, "chien": pos, ...}
    
    # ═══════════════════════════════════════════════════
    # STATE INFERENCE
    # ═══════════════════════════════════════════════════
    IF "nhan" IN buttons:
        # "Nhận" button → Reward screen
        RETURN GameState.REWARD
    
    ELIF "chien" IN buttons:
        # "Chiến" button → Map screen
        RETURN GameState.MAP
    
    ELIF "batdau" IN buttons:
        # "Bắt đầu" button → Ready screen
        RETURN GameState.READY
    
    ELSE:
        # No special buttons → Assume playing
        RETURN GameState.PLAYING
```

#### 3.7.2. Automated State Transitions

```python
def handle_state_transitions():
    """
    Automatic navigation through game screens
    
    Flow: REWARD → MAP → READY → PLAYING
    """
    
    state = detect_current_state()
    
    SWITCH state:
        CASE REWARD:
            # ═══════════════════════════════════════════
            # REWARD SCREEN HANDLER
            # ═══════════════════════════════════════════
            print("🎁 Reward screen detected")
            
            # Find "Nhận" button
            button_pos = find_button("nhan")
            
            IF button_pos:
                click_at_position(button_pos)
                wait(2 seconds)
                
                # Chain to next state
                RETURN handle_map_screen()
            
            ELSE:
                log("Button not found")
                RETURN False
        
        CASE MAP:
            # ═══════════════════════════════════════════
            # MAP SCREEN HANDLER
            # ═══════════════════════════════════════════
            print("🗺️ Map screen detected")
            
            button_pos = find_button("chien")
            
            IF button_pos:
                click_at_position(button_pos)
                wait(2 seconds)
                
                # Chain to next state
                RETURN handle_ready_screen()
        
        CASE READY:
            # ═══════════════════════════════════════════
            # READY SCREEN HANDLER
            # ═══════════════════════════════════════════
            print("⚔️ Ready screen detected")
            
            button_pos = find_button("batdau")
            
            IF button_pos:
                click_at_position(button_pos)
                wait(2 seconds)
                
                # Now in PLAYING state
                RETURN True
        
        CASE PLAYING:
            # ═══════════════════════════════════════════
            # PLAYING STATE
            # ═══════════════════════════════════════════
            # Ready for match-3 gameplay
            RETURN True
```

**State Transition Diagram:**

```
     ┌─────────┐
     │ PLAYING │◄────────────────────┐
     └─────────┘                     │
          │                          │
          │ Game ends                │
          ↓                          │
     ┌─────────┐                     │
     │ REWARD  │                     │
     └─────────┘                     │
          │                          │
          │ Click "Nhận"             │
          │ Wait 2s                  │
          ↓                          │
     ┌─────────┐                     │
     │   MAP   │                     │
     └─────────┘                     │
          │                          │
          │ Click "Chiến"            │
          │ Wait 2s                  │
          ↓                          │
     ┌─────────┐                     │
     │  READY  │                     │
     └─────────┘                     │
          │                          │
          │ Click "Bắt đầu"          │
          │ Wait 2s                  │
          └──────────────────────────┘
```

---

## 4. THUẬT TOÁN CORE

### 4.1. Board Stability Detection

**Problem:** Game có animation khi gems rơi/xóa. Cần đợi animation xong mới đọc board.

**Solution:** Frame difference algorithm

```python
def wait_for_stability():
    """
    Algorithm: Consecutive Frame Comparison
    
    Stability Criteria:
    - Capture N consecutive frames
    - Calculate differences between frames
    - If all differences < threshold → Stable
    """
    
    CONFIG:
        N = 3                    # Number of frames to check
        THRESHOLD = 0.02         # 2% difference allowed
        CHECK_INTERVAL = 0.1s    # 100ms between captures
        MAX_WAIT = 5.0s          # Timeout
    
    previous_frames = []
    start_time = now()
    
    WHILE (now() - start_time) < MAX_WAIT:
        # ═══════════════════════════════════════════════
        # CAPTURE FRAME
        # ═══════════════════════════════════════════════
        frame = capture_board()
        gray_frame = convert_to_grayscale(frame)
        
        previous_frames.append(gray_frame)
        
        # Keep only N frames
        IF len(previous_frames) > N:
            previous_frames.pop(0)  # Remove oldest
        
        # ═══════════════════════════════════════════════
        # CHECK STABILITY
        # ═══════════════════════════════════════════════
        IF len(previous_frames) == N:
            all_stable = True
            
            FOR i = 0 TO N-2:
                # Calculate absolute difference
                diff = abs(previous_frames[i] - previous_frames[i+1])
                
                # Normalize by image size
                diff_percentage = sum(diff) / (pixels * 255)
                
                IF diff_percentage > THRESHOLD:
                    all_stable = False
                    BREAK
            
            IF all_stable:
                RETURN True  # Board is stable
        
        # ═══════════════════════════════════════════════
        # WAIT BEFORE NEXT CHECK
        # ═══════════════════════════════════════════════
        wait(CHECK_INTERVAL)
    
    RETURN False  # Timeout
```

**Mathematical Analysis:**

```
Frame Difference:
D = Σ|pixel_i - pixel_j| / (W × H × 255)

Where:
- pixel_i, pixel_j = pixel values in frames i, j
- W × H = image dimensions
- 255 = max pixel value (normalize to 0-1)

Example:
- Board size: 800×800 = 640,000 pixels
- Threshold: 0.02 = 2%
- Max allowed diff: 640,000 × 0.02 = 12,800 pixels

If more than 12,800 pixels differ → Animation still running
```

---

### 4.2. Color Detection Algorithm

**Problem:** Nhận diện gem type từ màu sắc

**Solution:** HSV color space masking

```python
def detect_gem_by_color(cell_img):
    """
    Algorithm: HSV Color Range Matching
    
    Steps:
    1. Convert BGR → HSV
    2. Define color ranges for each gem type
    3. Create binary masks
    4. Calculate coverage percentage
    5. Select gem with highest coverage
    """
    
    # ═══════════════════════════════════════════════════
    # STEP 1: COLOR SPACE CONVERSION
    # ═══════════════════════════════════════════════════
    hsv = cv2.cvtColor(cell_img, cv2.COLOR_BGR2HSV)
    
    # ═══════════════════════════════════════════════════
    # STEP 2: COLOR RANGE DEFINITIONS
    # ═══════════════════════════════════════════════════
    color_ranges = {
        # Hue range optimized for each gem
        'RED': {
            'lower': [0, 100, 100],    # H:0°, S:100, V:100
            'upper': [10, 255, 255],   # H:10°, S:max, V:max
            'coverage_threshold': 0.15  # 15% minimum
        },
        'BLUE': {
            'lower': [100, 100, 100],  # H:100° (blue)
            'upper': [130, 255, 255],
            'coverage_threshold': 0.15
        },
        'GREEN': {
            'lower': [40, 50, 50],     # H:40-80° (green)
            'upper': [80, 255, 255],
            'coverage_threshold': 0.15
        },
        # ... more colors
    }
    
    # ═══════════════════════════════════════════════════
    # STEP 3: MASK CREATION & EVALUATION
    # ═══════════════════════════════════════════════════
    best_gem = "UNKNOWN"
    max_coverage = 0
    
    FOR gem_type, params IN color_ranges:
        # Create binary mask
        mask = cv2.inRange(
            hsv,
            np.array(params['lower']),
            np.array(params['upper'])
        )
        
        # Calculate coverage
        white_pixels = np.sum(mask == 255)
        total_pixels = mask.size
        coverage = white_pixels / total_pixels
        
        # Update best match
        IF coverage > max_coverage AND coverage > params['coverage_threshold']:
            max_coverage = coverage
            best_gem = gem_type
    
    RETURN best_gem
```

**HSV Color Space Advantages:**

```
RGB vs HSV:

RGB (Red, Green, Blue):
- Device-dependent
- Lighting-sensitive
- Hard to define color ranges
Example: Red = (255, 0, 0) but dark red = (128, 0, 0)

HSV (Hue, Saturation, Value):
- Perceptually uniform
- Separates color from brightness
- Easy to define ranges
Example: All reds have H ≈ 0°, regardless of brightness

HSV Channels:
┌────────────────────────────────────┐
│ H (Hue): Color type (0-180°)      │
│   0° = Red                         │
│   60° = Yellow                     │
│   120° = Green                     │
│   180° = Cyan                      │
├────────────────────────────────────┤
│ S (Saturation): Color intensity    │
│   0 = Grayscale                    │
│   255 = Vivid color                │
├────────────────────────────────────┤
│ V (Value): Brightness              │
│   0 = Black                        │
│   255 = Bright                     │
└────────────────────────────────────┘

Why better for gem detection?
- Gems have consistent hue regardless of lighting
- S and V filters can ignore dark/light variations
- Single H range captures all shades of a color
```

---

### 4.3. Cascade Depth Prediction

**Problem:** Mô phỏng cascade để đánh giá move

**Solution:** Iterative gravity simulation

```python
def predict_cascade_depth(board, initial_matches):
    """
    Algorithm: Iterative Physics Simulation
    
    Complexity:
    - Time: O(N × M × D) where D = cascade depth
    - Space: O(N × M) for board copy
    - Typical D: 1-3, max 5
    """
    
    current_board = copy(board)
    matches = initial_matches
    depth = 0
    
    WHILE depth < MAX_DEPTH AND matches.not_empty():
        depth += 1
        
        # ═══════════════════════════════════════════════
        # PHASE 1: REMOVE GEMS
        # ═══════════════════════════════════════════════
        FOR match IN matches:
            FOR pos IN match.positions:
                current_board[pos.row][pos.col] = EMPTY
        
        # ═══════════════════════════════════════════════
        # PHASE 2: APPLY GRAVITY (Column by column)
        # ═══════════════════════════════════════════════
        FOR col = 0 TO N-1:
            # Collect non-empty gems
            gems = []
            FOR row = N-1 DOWN_TO 0:  # Bottom to top
                IF current_board[row][col] != EMPTY:
                    gems.append(current_board[row][col])
                    current_board[row][col] = EMPTY
            
            # Place gems back from bottom
            row = N - 1
            FOR gem IN gems:
                current_board[row][col] = gem
                row -= 1
        
        # ═══════════════════════════════════════════════
        # PHASE 3: DETECT NEW MATCHES
        # ═══════════════════════════════════════════════
        matches = find_all_matches(current_board)
        
        # Filter out EMPTY matches (shouldn't happen but safety check)
        matches = filter(lambda m: is_valid_match(m, current_board), matches)
    
    RETURN depth
```

**Gravity Physics:**

```
Example Column Gravity:

Before:           After Gravity:
Row 0:  R         Row 0:  _
Row 1:  _         Row 1:  _
Row 2:  B         Row 2:  R
Row 3:  _         Row 3:  B
Row 4:  G         Row 4:  G
Row 5:  _         Row 5:  R
Row 6:  R         Row 6:  B
Row 7:  B         Row 7:  G

Algorithm:
1. Scan bottom → top: Collect [B, G, R, B, G]
2. Place bottom → top:
   Row 7 ← G
   Row 6 ← B
   Row 5 ← R
   Row 4 ← G
   Row 3 ← B
3. Fill rest with EMPTY

Time: O(N) per column, O(N×M) total
```

---

## 5. STATE MANAGEMENT

### 5.1. Game State Machine

```
┌──────────────────────────────────────────────────────────┐
│                    GAME STATE MACHINE                     │
└──────────────────────────────────────────────────────────┘

States:
- PLAYING: Active match-3 gameplay
- REWARD: Post-game reward collection
- MAP: Boss/level selection
- READY: Pre-battle preparation
- UNKNOWN: Cannot determine state

Transitions:
PLAYING ──[game ends]──> REWARD
REWARD ──[click "Nhận"]──> MAP
MAP ──[click "Chiến"]──> READY
READY ──[click "Bắt đầu"]──> PLAYING

State Persistence:
- Current state stored in GameStateManager
- Last state change timestamp tracked
- Prevents rapid state flipping
```

### 5.2. Turn State Machine (PvP Mode)

```
┌──────────────────────────────────────────────────────────┐
│                    TURN STATE MACHINE                     │
└──────────────────────────────────────────────────────────┘

States:
- OPPONENT_TURN: Waiting for opponent
- MY_TURN: Can make moves
- NO_TIMER: Between rounds or loading

Transitions:
NO_TIMER ──[timer appears]──> OPPONENT_TURN / MY_TURN
OPPONENT_TURN ──[timer & "Your Turn"]──> MY_TURN
MY_TURN ──[timer expires]──> OPPONENT_TURN
MY_TURN ──[no timer]──> NO_TIMER

Decision Logic:
IF timer == None:
    state = NO_TIMER
    action = check_for_buttons (reward/map/ready)
ELIF timer < 2:
    state = MY_TURN (but too late)
    action = wait
ELIF timer >= 2 AND is_my_turn:
    state = MY_TURN
    action = execute_move
ELSE:
    state = OPPONENT_TURN
    action = wait
```

---

## 6. COMPUTER VISION PIPELINE

### 6.1. Image Processing Flow

```
RAW SCREENSHOT
      ↓
┌─────────────────────┐
│ 1. CAPTURE          │
│    - MSS library    │
│    - BGRA format    │
│    - 800×800 pixels │
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 2. COLOR CONVERT    │
│    - BGRA → BGR     │
│    - OpenCV compat  │
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 3. CELL EXTRACTION  │
│    - Split 8×8      │
│    - 100×100 each   │
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 4. COLOR SPACE      │
│    - BGR → HSV      │
│    - Per cell       │
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 5. COLOR DETECTION  │
│    - Range masking  │
│    - Coverage calc  │
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 6. GEM RECOGNITION  │
│    - Type selection │
│    - Confidence     │
└─────────────────────┘
      ↓
BOARD MATRIX [8][8]
```

### 6.2. OCR Pipeline (Timer Detection)

```
SCREEN REGION
      ↓
┌─────────────────────┐
│ 1. ROI EXTRACT      │
│    - Timer region   │
│    - 80×100 pixels  │
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 2. COLOR FILTER     │
│    - HSV yellow     │
│    - Isolate text   │
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 3. BINARIZATION     │
│    - Threshold      │
│    - Black/white    │
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 4. MORPHOLOGY       │
│    - Close gaps     │
│    - Clean noise    │
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 5. TESSERACT OCR    │
│    - PSM 7          │
│    - Digits only    │
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 6. POST-PROCESS     │
│    - Regex extract  │
│    - Validate 0-10  │
└─────────────────────┘
      ↓
TIMER VALUE (int)
```

---

## 7. AI DECISION MAKING

### 7.1. Decision Tree

```
┌────────────────────────────────────────────────────────┐
│             MOVE SELECTION DECISION TREE               │
└────────────────────────────────────────────────────────┘

1. Find All Valid Moves (256 swap attempts)
   │
   ├─> No moves? → Wait / Report
   │
   └─> Has moves → Continue
       │
2. Pre-filter (if >30 moves)
   │
   ├─> Sort by immediate gem count
   ├─> Keep top 30 candidates
   │
3. Evaluate Each Move
   │
   ├─> Calculate base score (gems removed)
   ├─> Detect special matches (4, 5)
   ├─> Simulate cascade
   │   ├─> Apply gravity
   │   ├─> Find new matches
   │   ├─> Repeat until stable
   │   └─> Count cascade depth & gems
   ├─> Add position bonus
   ├─> Add priority bonus
   └─> Total score
       │
4. Select Best Move
   │
   └─> Max(score) → Execute
```

### 7.2. Scoring Weights

```python
SCORING_WEIGHTS = {
    # Base scoring
    'points_per_gem': 10,           # Each gem removed
    
    # Special matches
    'match_4_bonus': 100,           # Match-4 bonus
    'match_5_bonus': 300,           # Match-5 bonus
    
    # Cascade bonuses
    'cascade_depth_multiplier': 80, # Per cascade level
    'cascade_gem_bonus': 25,        # Per extra gem
    'cascade_match_bonus': 60,      # Per extra match
    
    # Position bonuses
    'bottom_row_bonus': 50,         # Rows 5-7
    'mid_row_bonus': 20,            # Rows 3-4
    'edge_bonus': 20,               # Columns 0,7
    'corner_bonus': 30,             # Corners
    
    # Strategic bonuses
    'rare_gem_bonus': 50,           # Rare gems (<5)
    'common_gem_bonus': 15,         # Common gems (5-10)
    'setup_bonus': 20,              # Future potential
}
```

### 7.3. Evaluation Examples

```
Example 1: Simple Match-3
┌─────────────────────────────┐
│ R R R B G Y P O             │
│ ...                         │
└─────────────────────────────┘

Score Breakdown:
- Base: 3 gems × 10 = 30
- Special: 0 (no match-4/5)
- Cascade: 0 (no cascade)
- Position: 20 (top row)
- Priority: 0 (common gem)
──────────────────────────────
Total: 50 points

Example 2: Match-4 with Cascade
┌─────────────────────────────┐
│ R R R R B                   │
│ G B G R G  ← After fall     │
│ B G B G B  ← New match!     │
└─────────────────────────────┘

Score Breakdown:
- Base: 4 gems × 10 = 40
- Special: 100 (match-4)
- Cascade:
  - Depth 2: (2-1) × 80 = 80
  - Extra gems: 3 × 25 = 75
  - Extra match: 1 × 60 = 60
  → Cascade total: 215
- Position: 50 (bottom)
- Priority: 15 (common)
──────────────────────────────
Total: 420 points

Example 3: Match-5 with Deep Cascade
┌─────────────────────────────┐
│ R R R R R                   │
│ ...cascade depth 3...       │
└─────────────────────────────┘

Score Breakdown:
- Base: 5 gems × 10 = 50
- Special: 300 (match-5)
- Cascade:
  - Depth 3: (3-1) × 80 = 160
  - Extra gems: 8 × 25 = 200
  - Extra match: 2 × 60 = 120
  → Cascade total: 480
- Position: 50
- Priority: 50 (rare gem)
──────────────────────────────
Total: 930 points (BEST MOVE!)
```

---

## 8. AUTOMATION CONTROLLER

### 8.1. Human Behavior Simulation

```python
class HumanBehaviorSimulator:
    """
    Simulate human-like patterns to avoid detection
    """
    
    def randomize_timing(base_duration):
        """
        Add variability to timing
        Human reaction time: 200-400ms
        """
        variance = random.uniform(0.8, 1.2)  # ±20%
        return base_duration * variance
    
    def randomize_position(x, y, offset=5):
        """
        Add pixel offset to avoid perfect clicks
        Human accuracy: ±5 pixels
        """
        x += random.randint(-offset, offset)
        y += random.randint(-offset, offset)
        return (x, y)
    
    def easing_function(t):
        """
        Smooth acceleration/deceleration
        Mimics human hand movement
        
        t: 0 to 1 (progress)
        returns: eased value 0 to 1
        """
        # EaseInOutQuad
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - (-2 * t + 2) ** 2 / 2
    
    def add_micro_pauses():
        """
        Random micro-pauses between actions
        Human "thinking time"
        """
        pause = random.uniform(0.05, 0.15)  # 50-150ms
        time.sleep(pause)
```

### 8.2. Anti-Detection Features

```
Feature List:

1. RANDOMIZED TIMING
   - Move duration: 0.25-0.35s (not constant)
   - Inter-move delay: 2.0-3.0s (variable)
   - Reaction time: 0.08-0.12s (human-like)

2. RANDOMIZED POSITIONING
   - Click offset: ±5 pixels
   - Path variance: Bezier curves (future)
   - No pixel-perfect clicks

3. SMOOTH MOVEMENT
   - EaseInOutQuad easing
   - Natural acceleration/deceleration
   - Not linear robotic motion

4. MICRO-PAUSES
   - 50-150ms random pauses
   - Between mouse actions
   - Simulates "thinking"

5. BEHAVIORAL PATTERNS
   - No 24/7 operation
   - Session limits (optional)
   - Break times (optional)

6. ERROR INJECTION (Optional)
   - Occasional "misclicks"
   - Skip moves randomly
   - More human-like patterns
```

---

## 9. BEST PRACTICES

### 9.1. Performance Optimization

```python
# ✓ GOOD: Efficient board copying
def copy_board(board):
    return [row[:] for row in board]  # List comprehension

# ✗ BAD: Inefficient deep copy
def copy_board(board):
    return copy.deepcopy(board)  # Overkill, slow


# ✓ GOOD: Early termination
def find_valid_moves(board):
    for row in range(8):
        for col in range(8):
            if board[row][col] == "EMPTY":
                continue  # Skip immediately
            # ... rest of logic

# ✗ BAD: No early termination
def find_valid_moves(board):
    for row in range(8):
        for col in range(8):
            if board[row][col] != "EMPTY":
                # ... logic inside if


# ✓ GOOD: Batch processing
masks = {gem: create_mask(gem) for gem in gem_types}

# ✗ BAD: Repeated processing
for cell in cells:
    for gem in gem_types:
        mask = create_mask(gem)  # Recreated every time!
```

### 9.2. Error Handling

```python
# ✓ GOOD: Graceful degradation
def capture_and_read_board():
    try:
        img = capture_screen()
        board = read_board(img)
        return board
    except ScreenCaptureError:
        log("Screen capture failed, retrying...")
        return None
    except Exception as e:
        log(f"Unexpected error: {e}")
        return None

# Usage
board = capture_and_read_board()
if board is None:
    # Skip this iteration, continue loop
    continue


# ✓ GOOD: Timeout protection
def find_best_move(moves, max_time=0.5):
    start = time.time()
    for move in moves:
        if time.time() - start > max_time:
            break  # Time limit
        score = evaluate(move)
    return best


# ✗ BAD: No timeout
def find_best_move(moves):
    for move in moves:
        score = evaluate(move)  # Could take forever
```

### 9.3. Logging & Debugging

```python
# ✓ GOOD: Structured logging
def execute_move(move):
    logger.info(f"Executing move {move.from_pos} → {move.to_pos}")
    logger.debug(f"  Matches: {len(move.matches)}")
    logger.debug(f"  Score: {move.score}")
    
    try:
        controller.execute(move)
        logger.info("Move executed successfully")
    except Exception as e:
        logger.error(f"Move execution failed: {e}")
        raise

# ✗ BAD: No logging
def execute_move(move):
    controller.execute(move)  # Silent failure possible


# ✓ GOOD: Debug visualization
if config['debug']['show_board']:
    visualize_board(board_img, board)
if config['debug']['save_screenshots']:
    save_debug_screenshot(board_img, f"debug_{timestamp}.png")
```

---

## 10. ÁP DỤNG CHO DỰ ÁN KHÁC

### 10.1. Các Game Tương Tự

**Candy Crush, Bejeweled, etc.**

```python
# Cần thay đổi:
1. Board size: rows, cols
2. Gem types: màu sắc, hình dạng
3. Color ranges: HSV values
4. Special gems: Striped, Wrapped, etc.

# Giữ nguyên:
- Match detection logic
- Cascade simulation
- Move evaluation
- Mouse controller
```

**Adaptation Template:**

```python
class CandyCrushBot(GameBot):
    def __init__(self):
        super().__init__()
        
        # ═══════════════════════════════════════════════
        # CUSTOMIZE: Board configuration
        # ═══════════════════════════════════════════════
        self.rows = 9  # Candy Crush: 9×9
        self.cols = 9
        
        # ═══════════════════════════════════════════════
        # CUSTOMIZE: Gem types
        # ═══════════════════════════════════════════════
        self.gem_types = [
            "RED_JELLY",
            "ORANGE_LOZENGE",
            "YELLOW_LEMON",
            "GREEN_LIME",
            "BLUE_DROP",
            "PURPLE_GRAPE"
        ]
        
        # ═══════════════════════════════════════════════
        # CUSTOMIZE: Special gems
        # ═══════════════════════════════════════════════
        self.special_gems = {
            "STRIPED": detect_striped_candy,
            "WRAPPED": detect_wrapped_candy,
            "COLOR_BOMB": detect_color_bomb
        }
        
        # ═══════════════════════════════════════════════
        # KEEP: Core logic (unchanged)
        # ═══════════════════════════════════════════════
        self.logic = MatchThreeLogic(self.rows, self.cols)
        self.evaluator = MoveEvaluator(scoring_rules)
```

### 10.2. Các Loại Game Khác

#### A. Puzzle Games (Tetris, 2048)

```python
# Áp dụng:
1. Board reader: Grid detection
2. State management: Game state tracking
3. Evaluator: Score optimization

# Thay đổi:
- Piece shapes (Tetris)
- Merge logic (2048)
- Move generation (rotation, placement)
```

#### B. Strategy Games (Chess, Go)

```python
# Áp dụng:
1. Move generation: Valid move finding
2. Evaluation: Position scoring
3. Lookahead: Minimax, Alpha-beta pruning

# Thay đổi:
- Game rules
- Evaluation function
- Search depth
```

#### C. Card Games (Solitaire, Hearthstone)

```python
# Áp dụng:
1. OCR: Card text recognition
2. State detection: Game phases
3. Controller: Click automation

# Thay đổi:
- Card recognition (CV or OCR)
- Deck strategy
- Timing (turn-based)
```

### 10.3. Generalized Architecture

```python
class GameBotFramework:
    """
    Generic game bot architecture
    Applicable to any game with visual interface
    """
    
    # ═══════════════════════════════════════════════════
    # CORE COMPONENTS (Always needed)
    # ═══════════════════════════════════════════════════
    def __init__(self):
        self.capture = ScreenCapture()     # Screen reading
        self.vision = VisionModule()       # CV/OCR
        self.logic = GameLogic()           # Game rules
        self.ai = DecisionEngine()         # AI/Strategy
        self.controller = InputController() # Mouse/Keyboard
    
    # ═══════════════════════════════════════════════════
    # MAIN LOOP (Template Method Pattern)
    # ═══════════════════════════════════════════════════
    def run(self):
        while self.running:
            # 1. Perception
            state = self.perceive_game_state()
            
            # 2. Decision
            action = self.decide_action(state)
            
            # 3. Execution
            self.execute_action(action)
            
            # 4. Wait
            self.delay()
    
    # ═══════════════════════════════════════════════════
    # CUSTOMIZATION POINTS (Override in subclass)
    # ═══════════════════════════════════════════════════
    def perceive_game_state(self):
        """Override: Implement game-specific perception"""
        raise NotImplementedError
    
    def decide_action(self, state):
        """Override: Implement game-specific AI"""
        raise NotImplementedError
    
    def execute_action(self, action):
        """Override: Implement game-specific controls"""
        raise NotImplementedError
```

### 10.4. Ví dụ Áp Dụng: 2048 Game

```python
class Bot2048(GameBotFramework):
    """
    2048 game bot using the framework
    """
    
    def __init__(self):
        super().__init__()
        self.board_size = 4  # 4×4 grid
    
    # ═══════════════════════════════════════════════════
    # PERCEPTION: Read 4×4 grid numbers
    # ═══════════════════════════════════════════════════
    def perceive_game_state(self):
        screenshot = self.capture.capture()
        cells = self.vision.split_grid(screenshot, 4, 4)
        
        board = []
        for cell in cells:
            number = self.vision.ocr_number(cell)
            board.append(number)
        
        return np.array(board).reshape(4, 4)
    
    # ═══════════════════════════════════════════════════
    # DECISION: Expectimax algorithm
    # ═══════════════════════════════════════════════════
    def decide_action(self, board):
        best_move = None
        best_score = -inf
        
        for direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            # Simulate move
            new_board = self.logic.simulate_move(board, direction)
            
            if not self.logic.is_same(board, new_board):
                # Evaluate using Expectimax
                score = self.ai.expectimax(new_board, depth=3)
                
                if score > best_score:
                    best_score = score
                    best_move = direction
        
        return best_move
    
    # ═══════════════════════════════════════════════════
    # EXECUTION: Keyboard arrow keys
    # ═══════════════════════════════════════════════════
    def execute_action(self, direction):
        key_map = {
            'UP': 'up',
            'DOWN': 'down',
            'LEFT': 'left',
            'RIGHT': 'right'
        }
        
        self.controller.press_key(key_map[direction])
        time.sleep(0.3)  # Wait for animation


# Usage
bot = Bot2048()
bot.run()
```

### 10.5. Module Reusability Matrix

```
┌────────────────────┬─────────┬─────────┬─────────┬─────────┐
│ Module             │ Match-3 │ Tetris  │  Chess  │  2048   │
├────────────────────┼─────────┼─────────┼─────────┼─────────┤
│ ScreenCapture      │   ✓✓    │   ✓✓    │   ✓✓    │   ✓✓    │
│ BoardReader (CV)   │   ✓✓    │   ✓✓    │   ✓     │   ✓     │
│ OCR Module         │   ✓     │   ✗     │   ✓     │   ✓✓    │
│ GameLogic          │   ✓✗    │   ✗✗    │   ✗✗    │   ✗✗    │
│ MoveEvaluator      │   ✓     │   ✗     │   ✗     │   ✗     │
│ MouseController    │   ✓✓    │   ✗     │   ✓✓    │   ✗     │
│ KeyboardController │   ✗     │   ✓✓    │   ✗     │   ✓✓    │
│ StateManager       │   ✓     │   ✓     │   ✓     │   ✓     │
└────────────────────┴─────────┴─────────┴─────────┴─────────┘

Legend:
✓✓ = Reuse as-is (100%)
✓  = Minor modifications (<20%)
✓✗ = Major modifications (50%)
✗✗ = Completely different
✗  = Not applicable
```

### 10.6. Checklist: Adapting to New Game

```
☐ 1. GAME ANALYSIS
   ☐ Identify game type (puzzle/strategy/card)
   ☐ Understand game rules
   ☐ Identify win conditions
   ☐ Map game state structure

☐ 2. VISION SETUP
   ☐ Locate game window
   ☐ Define important regions (board, UI, score)
   ☐ Choose detection method (CV vs OCR)
   ☐ Calibrate color ranges / templates
   ☐ Test recognition accuracy

☐ 3. GAME LOGIC
   ☐ Implement state representation
   ☐ Implement move generation
   ☐ Implement move validation
   ☐ Implement game physics / rules
   ☐ Test logic correctness

☐ 4. AI STRATEGY
   ☐ Define evaluation criteria
   ☐ Implement scoring function
   ☐ Choose search algorithm (brute-force/minimax/etc)
   ☐ Optimize for speed
   ☐ Test strategy effectiveness

☐ 5. AUTOMATION
   ☐ Implement input controller (mouse/keyboard)
   ☐ Add humanization features
   ☐ Implement error recovery
   ☐ Add safety checks (pause on focus loss)

☐ 6. TESTING & TUNING
   ☐ Unit test each module
   ☐ Integration test full loop
   ☐ Performance profiling
   ☐ Parameter tuning
   ☐ Anti-detection measures

☐ 7. DEPLOYMENT
   ☐ Config file setup
   ☐ GUI (optional)
   ☐ Logging system
   ☐ Documentation
   ☐ Error handling
```

---

## TÓM TẮT

### Core Concepts

1. **Layered Architecture**: Separation of concerns (UI → Logic → Infrastructure)
2. **Computer Vision**: HSV color detection for robust gem recognition
3. **Game Logic**: Brute-force move generation + cascade simulation
4. **AI Decision**: Multi-criteria scoring with look-ahead
5. **Automation**: Human-like mouse control with anti-detection
6. **State Management**: Automatic navigation through game screens

### Key Algorithms

1. **Frame Stability**: Consecutive frame difference
2. **Color Detection**: HSV range masking
3. **Match Detection**: Bidirectional scan (horizontal/vertical)
4. **Cascade Simulation**: Iterative gravity + match detection
5. **Move Evaluation**: Weighted multi-criteria scoring
6. **Human Simulation**: Random timing + easing functions

### Reusable Components

- Screen Capture (MSS)
- Computer Vision (OpenCV)
- OCR (Tesseract)
- Mouse/Keyboard Control (PyAutoGUI)
- State Machine Pattern
- Evaluation Framework

### Applicable To

- Match-3 games (Candy Crush, Bejeweled)
- Puzzle games (Tetris, 2048)
- Board games (Chess, Go)
- Card games (Hearthstone, Solitaire)
- Any game with visual interface

---

**Tài liệu này cung cấp blueprint hoàn chỉnh để xây dựng game bot tự động với AI decision making và computer vision. Bạn có thể áp dụng kiến trúc và thuật toán này cho bất kỳ dự án game automation nào!**
