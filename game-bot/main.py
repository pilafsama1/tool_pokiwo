"""
Main Bot Loop
Orchestrates all components to automate match-3 gameplay
"""

import cv2
import numpy as np
import time
import yaml
from pathlib import Path
from typing import Optional, List
import glob
import os

from capture import ScreenCapture
from board_reader_color import BoardReaderColor
from logic import MatchThreeLogic, Move
from evaluator import MoveEvaluator
from controller import MouseController
from turn_detector import SimpleTurnDetector, TurnDetector
from calibrate import BoardCalibrator
from game_state_manager import GameStateManager, GameState


class GameBot:
    """Main bot controller"""
    
    def __init__(self, config_path: str = "config.yaml", auto_calibrate: bool = False):
        """
        Initialize the game bot
        
        Args:
            config_path: Path to configuration file
            auto_calibrate: If True, run calibration before starting
        """
        # Clean up old debug screenshots
        self._cleanup_old_screenshots()
        
        # Auto calibrate if requested
        if auto_calibrate:
            self._run_calibration(config_path)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize components
        self._initialize_components()
        
        # State tracking
        self.running = False
        self.move_count = 0
        self.total_score = 0
    
    def _cleanup_old_screenshots(self):
        """Remove old debug screenshots"""
        try:
            debug_files = glob.glob("debug_board_*.png")
            if debug_files:
                print(f"🧹 Cleaning up {len(debug_files)} old screenshots...")
                for file in debug_files:
                    try:
                        os.remove(file)
                    except:
                        pass
                print("✓ Cleanup complete")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")
    
    def _run_calibration(self, config_path: str):
        """Run interactive calibration"""
        print("\n" + "="*60)
        print("🎯 CHỌN VÙNG BÀN CỜ")
        print("="*60)
        print("\n⚠️  Đảm bảo:")
        print("   1. Game đã mở")
        print("   2. Bàn cờ 8x8 hiện trên màn hình")
        print("   3. Không có cửa sổ che game")
        print("\n📌 Nhấn ENTER để bắt đầu chọn vùng...")
        input()
        
        calibrator = BoardCalibrator()
        board_region = calibrator.select_region()
        
        if board_region:
            print("\n📊 Vùng đã chọn:")
            print(f"   Top: {board_region['top']}")
            print(f"   Left: {board_region['left']}")
            print(f"   Width: {board_region['width']}")
            print(f"   Height: {board_region['height']}")
            
            # Auto save
            calibrator.update_config(board_region, config_path)
            print("✓ Đã lưu cấu hình!\n")
        else:
            print("\n❌ Chưa chọn vùng! Sử dụng cấu hình hiện tại.\n")
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    
    def _initialize_components(self):
        """Initialize all bot components"""
        # Screen capture
        screen_config = self.config['screen']
        self.capture = ScreenCapture(
            top=screen_config['top'],
            left=screen_config['left'],
            width=screen_config['width'],
            height=screen_config['height']
        )
        
        # Board reader (using color detection)
        board_config = self.config['board']
        self.reader = BoardReaderColor(
            rows=board_config['rows'],
            cols=board_config['cols'],
            debug=self.config['debug']['verbose']
        )
        
        # Game logic
        self.logic = MatchThreeLogic(
            rows=board_config['rows'],
            cols=board_config['cols']
        )
        
        # Move evaluator
        self.evaluator = MoveEvaluator(
            scoring_rules=self.config['scoring']
        )
        
        # Mouse controller
        cell_width = screen_config['width'] // board_config['cols']
        cell_height = screen_config['height'] // board_config['rows']
        
        mouse_config = self.config['mouse']
        self.controller = MouseController(
            board_top=screen_config['top'],
            board_left=screen_config['left'],
            cell_width=cell_width,
            cell_height=cell_height,
            drag_duration=mouse_config['drag_duration'],
            random_delay_min=mouse_config['random_delay_min'],
            random_delay_max=mouse_config['random_delay_max']
        )
        
        # Turn detector (for PvP games with timer)
        if self.config.get('turn_detection', {}).get('enabled', False):
            turn_config = self.config['turn_detection']
            
            # Create a separate capture for full game window (for timer detection)
            game_window = self.config.get('game_window', screen_config)
            self.game_capture = ScreenCapture(
                top=game_window['top'],
                left=game_window['left'],
                width=game_window['width'],
                height=game_window['height']
            )
            
            # Initialize turn detector
            tesseract_cmd = self.config.get('game_automation', {}).get('tesseract_path')
            self.turn_detector = TurnDetector(
                your_turn_region=turn_config.get('your_turn_region', {'top': 0, 'left': 0, 'width': 100, 'height': 50}),
                timer_region=turn_config['timer_region'],
                tesseract_cmd=tesseract_cmd
            )
            self.min_timer_value = turn_config.get('min_timer_value', 2)
            print("✓ Turn detector initialized (timer-based)")
            print(f"  Timer region: {turn_config['timer_region']}")
            print(f"  Min timer value: {self.min_timer_value}s")
        else:
            self.turn_detector = None
            self.game_capture = None
            print("ℹ Turn detection disabled (bot sẽ chơi liên tục)")
        
        # Game state manager (for UI automation)
        if self.config.get('game_automation', {}).get('enabled', False):
            game_window_region = self.config.get('game_window', screen_config)
            
            # Store game window region for later use
            self.game_window_region = game_window_region
            
            self.state_manager = GameStateManager(
                config=self.config,
                game_window_region=game_window_region,
                board_region=screen_config
            )
            print("✓ Game automation enabled")
        else:
            self.state_manager = None
            self.game_window_region = None
            print("ℹ Game automation disabled")
        
        print("✓ All components initialized")
    
    def wait_for_stability(self) -> bool:
        """
        Wait for board animations to finish by checking frame stability
        
        Returns:
            True if board is stable, False if timeout
        """
        anim_config = self.config['animation']
        check_frames = anim_config['stability_check_frames']
        diff_threshold = anim_config['frame_diff_threshold']
        check_interval = anim_config['check_interval']
        max_wait = anim_config['max_wait_time']
        
        start_time = time.time()
        previous_frames = []
        
        while time.time() - start_time < max_wait:
            # Capture current frame
            current_frame = self.capture.capture_board()
            current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
            
            # Add to history
            previous_frames.append(current_gray)
            
            # Keep only required number of frames
            if len(previous_frames) > check_frames:
                previous_frames.pop(0)
            
            # Check if we have enough frames to compare
            if len(previous_frames) == check_frames:
                # Calculate differences between consecutive frames
                all_stable = True
                
                for i in range(len(previous_frames) - 1):
                    diff = cv2.absdiff(previous_frames[i], previous_frames[i + 1])
                    diff_percentage = np.sum(diff) / (diff.size * 255)
                    
                    if diff_percentage > diff_threshold:
                        all_stable = False
                        break
                
                if all_stable:
                    if self.config['debug']['verbose']:
                        print(f"✓ Board stable after {time.time() - start_time:.2f}s")
                    return True
            
            # Wait before next check
            time.sleep(check_interval)
        
        print(f"⚠ Stability timeout after {max_wait}s")
        return False
    
    def capture_and_read_board(self) -> Optional[List[List[str]]]:
        """
        Capture screen and read board state with multiple scans for better accuracy
        
        Returns:
            Board state as 2D list, or None if failed
        """
        try:
            # Số lần quét board (tối thiểu 3 lần)
            num_scans = 3
            scan_delay = 0.05  # Delay nhỏ giữa các lần quét (50ms)
            
            if self.config['debug']['verbose']:
                print(f"🔍 Quét board {num_scans} lần để tăng độ chính xác...")
            
            # Lưu kết quả từ các lần quét
            all_boards = []
            
            for scan_num in range(num_scans):
                # Capture board
                board_img = self.capture.capture_board()
                
                # Read board
                board = self.reader.read_board(board_img)
                
                if board:
                    all_boards.append(board)
                
                # Save screenshot từ lần quét đầu tiên
                if scan_num == 0 and self.config['debug']['save_screenshots']:
                    timestamp = int(time.time())
                    self.capture.save_screenshot(f"debug_board_{timestamp}.png")
                
                # Delay nhỏ giữa các lần quét (trừ lần cuối)
                if scan_num < num_scans - 1:
                    time.sleep(scan_delay)
            
            if not all_boards:
                print("✗ Tất cả các lần quét đều thất bại")
                return None
            
            # Merge kết quả từ các lần quét
            merged_board = self._merge_board_scans(all_boards)
            
            # Đếm số UNKNOWN còn lại
            unknown_count = sum(row.count('UNKNOWN') for row in merged_board)
            total_cells = len(merged_board) * len(merged_board[0])
            accuracy = ((total_cells - unknown_count) / total_cells) * 100
            
            if self.config['debug']['verbose']:
                print(f"✓ Độ chính xác sau {len(all_boards)} lần quét: {accuracy:.1f}% ({total_cells - unknown_count}/{total_cells} ô)")
            
            # Debug visualization
            if self.config['debug']['show_board']:
                board_img = self.capture.capture_board()
                self.reader.visualize_board(board_img, merged_board)
            
            return merged_board
            
        except Exception as e:
            print(f"✗ Error reading board: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _merge_board_scans(self, boards: List[List[List[str]]]) -> List[List[str]]:
        """
        Merge multiple board scans to get best result
        Ưu tiên gem được nhận diện nhiều nhất, bỏ qua UNKNOWN
        
        Args:
            boards: List of board states from multiple scans
            
        Returns:
            Merged board state
        """
        if not boards:
            return None
        
        rows = len(boards[0])
        cols = len(boards[0][0])
        merged = []
        
        for r in range(rows):
            row = []
            for c in range(cols):
                # Lấy tất cả giá trị từ các lần quét tại vị trí này
                values = [board[r][c] for board in boards]
                
                # Đếm số lần xuất hiện của mỗi giá trị (loại bỏ UNKNOWN)
                non_unknown = [v for v in values if v != 'UNKNOWN']
                
                if non_unknown:
                    # Chọn giá trị xuất hiện nhiều nhất
                    from collections import Counter
                    most_common = Counter(non_unknown).most_common(1)[0][0]
                    row.append(most_common)
                else:
                    # Nếu tất cả đều UNKNOWN, giữ UNKNOWN
                    row.append('UNKNOWN')
            
            merged.append(row)
        
        return merged
    
    def find_and_execute_best_move(self, board: List[List[str]]) -> bool:
        """
        Find and execute the best move
        
        Args:
            board: Current board state
            
        Returns:
            True if move was executed, False otherwise
        """
        try:
            # Find all valid moves
            moves = self.logic.find_valid_moves(board)
            
            if not moves:
                print("✗ No valid moves found")
                return False
            
            if self.config['debug']['verbose']:
                print(f"Found {len(moves)} valid moves")
            
            # Get calculation time limit from config
            calc_config = self.config.get('calculation', {})
            max_time = calc_config.get('max_calculation_time', 0.5)
            
            # Evaluate and get best move with time limit
            start_eval = time.time()
            best_move, score = self.evaluator.get_best_move(moves, board, self.logic, max_time=max_time)
            eval_time = time.time() - start_eval
            
            if best_move is None:
                print("✗ No best move determined")
                return False
            
            # Show move info
            if self.config['debug']['verbose']:
                print(f"\n🎯 Best move (score: {score}, eval time: {eval_time:.3f}s):")
                print(f"  From: {best_move.from_pos}")
                print(f"  To: {best_move.to_pos}")
                print(f"  Matches: {len(best_move.matches)}")
                
                # Show detailed breakdown
                breakdown = self.evaluator.explain_score(best_move, board, self.logic)
                print(f"  Score breakdown:")
                for key, value in breakdown.items():
                    if value > 0:
                        print(f"    {key}: {value}")
            
            # Execute move
            self.controller.execute_move(best_move)
            self.move_count += 1
            self.total_score += score
            
            if self.config['debug']['verbose']:
                print(f"✓ Move #{self.move_count} executed")
            
            return True
            
        except Exception as e:
            print(f"✗ Error in find_and_execute_best_move: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_single_iteration(self) -> bool:
        """
        Run a single bot iteration
        
        LUỒNG HOẠT ĐỘNG MỚI:
        1. Kiểm tra TIMER
           - Nếu có timer → Đánh gems (bước 2)
           - Nếu không có timer → Kiểm tra nút "Nhận" tại vị trí đã set (bước 1.1)
        
        1.1. Kiểm tra nút "Nhận" tại vị trí cố định
           - Nếu có nút "Nhận" (kiểm tra màu tại vị trí) → Click chuỗi: Nhận → Chiến → Bắt đầu
           - Nếu không có → Chờ lượt tiếp theo
        
        2. Đánh gems
           - Đợi board ổn định
           - Đọc board
           - Tính toán và thực hiện nước đi tối ưu
        
        Returns:
            True if move executed, False if waiting
        """
        try:
            # ============================================================
            # BƯỚC 1: KIỂM TRA TIMER (nếu turn detection được bật)
            # ============================================================
            if self.turn_detector:
                # Chụp game window để kiểm tra timer
                game_img = self.game_capture.capture_board()
                
                # Phát hiện giá trị timer
                timer_value = self.turn_detector.detect_timer_value(game_img)
                
                # --------------------------------------------------------
                # TRƯỜNG HỢP 1: KHÔNG CÓ TIMER
                # --------------------------------------------------------
                if timer_value is None:
                    if self.config['debug']['verbose']:
                        print("⏸ Không phát hiện timer - Kiểm tra nút Nhận trong vùng đã set...")
                    
                    # Kiểm tra xem có config vùng nút Nhận không
                    button_regions = self.config.get('button_regions', {})
                    
                    if not button_regions.get('nhan'):
                        if self.config['debug']['verbose']:
                            print("  ⚠️ Chưa config vùng nút Nhận. Chạy GUI để set vùng!")
                        return False
                    
                    # Lấy vị trí nút từ config
                    button_pos_config = self.config.get('button_positions', {})
                    if not button_pos_config.get('nhan') or not button_pos_config.get('chien') or not button_pos_config.get('batdau'):
                        if self.config['debug']['verbose']:
                            print("  ⚠️ Chưa config đủ vị trí 3 nút. Chạy GUI để set!")
                        return False
                    
                    # Chụp vùng nút Nhận
                    import mss
                    nhan_region = button_regions['nhan']
                    with mss.mss() as sct:
                        region_monitor = {
                            'top': nhan_region['top'],
                            'left': nhan_region['left'],
                            'width': nhan_region['width'],
                            'height': nhan_region['height']
                        }
                        screenshot = sct.grab(region_monitor)
                        nhan_region_img = np.array(screenshot)
                        nhan_region_img = cv2.cvtColor(nhan_region_img, cv2.COLOR_BGRA2BGR)
                    
                    # Dùng OCR đơn giản để tìm chữ "nhận" trong vùng
                    import pytesseract
                    
                    # OCR text trong vùng nút Nhận
                    tesseract_cmd = self.config.get('game_automation', {}).get('tesseract_path')
                    if tesseract_cmd:
                        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
                    
                    # Preprocess image cho background xanh dương + chữ trắng
                    gray = cv2.cvtColor(nhan_region_img, cv2.COLOR_BGR2GRAY)
                    
                    # Thử nhiều phương pháp threshold
                    # 1. Otsu's thresholding (tự động tìm ngưỡng tốt nhất)
                    _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    
                    # 2. Adaptive threshold (thích nghi với từng vùng)
                    thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                     cv2.THRESH_BINARY, 11, 2)
                    
                    # 3. Threshold cao cho chữ trắng trên nền xanh
                    _, thresh3 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
                    
                    # Lưu debug images (Đã tắt - debug xong rồi)
                    # cv2.imwrite('debug_nhan_original.png', nhan_region_img)
                    # cv2.imwrite('debug_nhan_gray.png', gray)
                    # cv2.imwrite('debug_nhan_otsu.png', thresh1)
                    # cv2.imwrite('debug_nhan_adaptive.png', thresh2)
                    # cv2.imwrite('debug_nhan_high.png', thresh3)
                    
                    # Thử OCR với cả 3 phương pháp
                    text1 = pytesseract.image_to_string(thresh1, lang='vie', config='--psm 6').lower()
                    text2 = pytesseract.image_to_string(thresh2, lang='vie', config='--psm 6').lower()
                    text3 = pytesseract.image_to_string(thresh3, lang='vie', config='--psm 6').lower()
                    
                    print(f"📝 OCR Debug:")
                    print(f"  Otsu: '{text1.strip()}'")
                    print(f"  Adaptive: '{text2.strip()}'")
                    print(f"  High(180): '{text3.strip()}'")
                    
                    # Kiểm tra có chữ "nhận" hoặc "nhan" trong bất kỳ kết quả nào
                    combined_text = text1 + ' ' + text2 + ' ' + text3
                    nhan_detected = 'nhận' in combined_text or 'nhan' in combined_text or 'nhân' in combined_text
                    
                    print(f"🔍 Kết quả phát hiện: {'✓ CÓ nút Nhận' if nhan_detected else '✗ KHÔNG có nút Nhận'}")
                    
                    if nhan_detected:
                        # ===============================================
                        # CÓ NÚT "NHẬN" → Nhấn chuỗi 3 nút theo vị trí đã set
                        # ===============================================
                        print("\n🎁 Phát hiện nút 'Nhận' trong vùng đã set - Bắt đầu chuỗi auto-click")
                        
                        # 1. Nhấn "Nhận"
                        nhan_pos = button_pos_config['nhan']
                        print(f"  1️⃣ Click 'Nhận' tại ({nhan_pos['x']}, {nhan_pos['y']})")
                        self.state_manager.click_at_position(nhan_pos['x'], nhan_pos['y'])
                        time.sleep(1.5)
                        
                        # 2. Nhấn "Chiến"
                        chien_pos = button_pos_config['chien']
                        print(f"  2️⃣ Click 'Chiến' tại ({chien_pos['x']}, {chien_pos['y']})")
                        self.state_manager.click_at_position(chien_pos['x'], chien_pos['y'])
                        time.sleep(1.5)
                        
                        # 3. Nhấn "Bắt đầu"
                        batdau_pos = button_pos_config['batdau']
                        print(f"  3️⃣ Click 'Bắt đầu' tại ({batdau_pos['x']}, {batdau_pos['y']})")
                        self.state_manager.click_at_position(batdau_pos['x'], batdau_pos['y'])
                        
                        print("✅ Hoàn thành chuỗi 3 nút → Tiếp tục màn chơi mới\n")
                        time.sleep(1.5)
                        return False
                    else:
                        # ===============================================
                        # KHÔNG CÓ NÚT "NHẬN" → Chờ lượt chơi
                        # ===============================================
                        if self.config['debug']['verbose']:
                            print("  → Không có nút 'Nhận' trong vùng - Chờ đến lượt chơi")
                        return False
                
                # --------------------------------------------------------
                # TRƯỜNG HỢP 2: CÓ TIMER NHƯNG QUÁ THẤP
                # --------------------------------------------------------
                if timer_value < self.min_timer_value:
                    if self.config['debug']['verbose']:
                        print(f"⏸ Timer {timer_value}s < {self.min_timer_value}s - Chờ lượt tiếp")
                    return False
                
                # --------------------------------------------------------
                # TRƯỜNG HỢP 3: CÓ TIMER ĐỦ → ĐẾN LƯỢT CHƠI!
                # --------------------------------------------------------
                if self.config['debug']['verbose']:
                    print(f"✓ Timer: {timer_value}s → Đến lượt chơi!")
                
                # Đợi 2 giây sau khi phát hiện timer
                print("⏳ Đợi 2 giây sau khi phát hiện timer...")
                time.sleep(2.0)
            
            # ============================================================
            # BƯỚC 2: ĐỢI BOARD ỔN ĐỊNH
            # ============================================================
            if not self.wait_for_stability():
                return False
            
            # ============================================================
            # BƯỚC 3: ĐỌC BOARD
            # ============================================================
            board = self.capture_and_read_board()
            if board is None:
                return False
            
            # ============================================================
            # BƯỚC 4: TÍNH TOÁN VÀ THỰC HIỆN NƯỚC ĐI TỐI ƯU
            # ============================================================
            return self.find_and_execute_best_move(board)
            
        except Exception as e:
            print(f"✗ Lỗi trong run_single_iteration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _verify_button_at_position(self, game_img: np.ndarray, button_pos: dict, button_type: str) -> bool:
        """
        Kiểm tra xem có nút tại vị trí đã set hay không (bằng color detection)
        
        Args:
            game_img: Ảnh game window
            button_pos: Dictionary với 'x' và 'y'
            button_type: Loại nút ('nhan', 'chien', 'batdau')
            
        Returns:
            True nếu có nút, False nếu không
        """
        try:
            import cv2
            
            x = button_pos['x']
            y = button_pos['y']
            
            # Lấy vùng nhỏ quanh vị trí nút (50x50 pixels)
            margin = 25
            y1 = max(0, y - margin)
            y2 = min(game_img.shape[0], y + margin)
            x1 = max(0, x - margin)
            x2 = min(game_img.shape[1], x + margin)
            
            roi = game_img[y1:y2, x1:x2]
            
            # Chuyển sang HSV
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Kiểm tra màu sắc theo loại nút
            if button_type == 'batdau':
                # Nút "Bắt đầu" màu CAM/VÀNG
                lower = np.array([10, 100, 100])
                upper = np.array([25, 255, 255])
            else:
                # Nút "Nhận", "Chiến" màu XANH
                lower = np.array([80, 50, 50])
                upper = np.array([130, 255, 255])
            
            mask = cv2.inRange(hsv, lower, upper)
            
            # Tính % pixel màu đúng
            color_ratio = np.sum(mask > 0) / mask.size
            
            # Nếu > 20% pixel là màu đúng → Có nút
            threshold = 0.20
            has_button = color_ratio > threshold
            
            if self.config['debug']['verbose'] and has_button:
                print(f"    ✓ Verify: {button_type} có màu đúng tại vị trí ({x}, {y}) - {color_ratio*100:.1f}%")
            
            return has_button
            
        except Exception as e:
            if self.config['debug']['verbose']:
                print(f"    ⚠ Lỗi verify button: {e}")
            return False
    
    def run(self, max_iterations: Optional[int] = None):
        """
        Run the bot main loop
        
        Args:
            max_iterations: Maximum number of iterations (None for infinite)
        """
        print("\n" + "="*50)
        print("🎮 MATCH-3 BOT STARTED")
        print("="*50)
        print(f"Press Ctrl+C to stop")
        print(f"Move mouse to top-left corner for emergency stop")
        print("="*50 + "\n")
        
        self.running = True
        self.move_count = 0
        self.total_score = 0
        iteration = 0
        
        try:
            while self.running:
                iteration += 1
                
                print(f"\n--- Iteration {iteration} ---")
                
                # Run single iteration
                success = self.run_single_iteration()
                
                if not success:
                    print("⚠ Iteration failed, retrying...")
                    time.sleep(1)
                    continue
                
                # Check max iterations
                if max_iterations and iteration >= max_iterations:
                    print(f"\n✓ Reached max iterations ({max_iterations})")
                    break
                
                # Delay between iterations (2-3 seconds)
                delay_min = self.config['scoring'].get('move_delay_min', 2.0)
                delay_max = self.config['scoring'].get('move_delay_max', 3.0)
                import random
                delay = random.uniform(delay_min, delay_max)
                time.sleep(delay)
        
        except KeyboardInterrupt:
            print("\n\n⏸ Bot stopped by user")
        
        except Exception as e:
            print(f"\n\n✗ Bot error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        
        print("\n" + "="*50)
        print("📊 SESSION SUMMARY")
        print("="*50)
        print(f"Total moves: {self.move_count}")
        print(f"Total score: {self.total_score}")
        if self.move_count > 0:
            print(f"Average score per move: {self.total_score / self.move_count:.1f}")
        print("="*50)
    
    def test_components(self):
        """Test all components individually"""
        print("\n" + "="*50)
        print("🧪 TESTING COMPONENTS")
        print("="*50)
        
        # Test capture
        print("\n1. Testing screen capture...")
        try:
            board_img = self.capture.capture_board()
            print(f"   ✓ Captured: {board_img.shape}")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
            return
        
        # Test board reader
        print("\n2. Testing board reader...")
        try:
            board = self.reader.read_board(board_img)
            print(f"   ✓ Read board: {len(board)}x{len(board[0])}")
            
            # Show board
            print("\n   Board state:")
            for row in board:
                print("   ", row)
        except Exception as e:
            print(f"   ✗ Failed: {e}")
            return
        
        # Test logic
        print("\n3. Testing match-3 logic...")
        try:
            moves = self.logic.find_valid_moves(board)
            print(f"   ✓ Found {len(moves)} valid moves")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
            return
        
        # Test evaluator
        print("\n4. Testing move evaluator...")
        try:
            if moves:
                best_move, score = self.evaluator.get_best_move(moves, board, self.logic)
                print(f"   ✓ Best move score: {score}")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
            return
        
        print("\n" + "="*50)
        print("Testing complete!")
        print("="*50 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Match-3 Game Bot")
    parser.add_argument('--config', default='config.yaml', help='Config file path')
    parser.add_argument('--test', action='store_true', help='Test components only')
    parser.add_argument('--iterations', type=int, help='Max iterations to run')
    parser.add_argument('--calibrate', action='store_true', help='Run calibration before starting')
    parser.add_argument('--no-calibrate', action='store_true', help='Skip calibration prompt')
    
    args = parser.parse_args()
    
    # Ask for calibration if not specified
    auto_calibrate = args.calibrate
    if not args.test and not args.no_calibrate and not args.calibrate:
        print("\n" + "="*60)
        print("🎮 MATCH-3 BOT")
        print("="*60)
        print("\n❓ Bạn có muốn chọn vùng bàn cờ không?")
        print("   (Khuyến nghị nếu chạy lần đầu hoặc game đã di chuyển)")
        print("\n   [Y] Có - Chọn vùng bằng chuột")
        print("   [N] Không - Dùng cấu hình hiện tại")
        print("\nLựa chọn (Y/n): ", end='')
        choice = input().strip().lower()
        auto_calibrate = (choice == 'y' or choice == 'yes' or choice == '')
    
    # Create bot
    bot = GameBot(config_path=args.config, auto_calibrate=auto_calibrate)
    
    # Test or run
    if args.test:
        bot.test_components()
    else:
        # Give user time to prepare
        print("\n⏱️  Starting in 3 seconds...")
        print("📌 Make sure the game window is visible!")
        time.sleep(3)
        
        bot.run(max_iterations=args.iterations)


if __name__ == "__main__":
    main()
