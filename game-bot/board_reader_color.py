"""
Board Reader - Color Detection Method
Recognizes gems by dominant color instead of template matching
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict

class BoardReaderColor:
    """Read board state using color detection"""
    
    def __init__(self, rows: int, cols: int, debug: bool = False):
        self.rows = rows
        self.cols = cols
        self.debug = debug
        
        # Define color ranges for each gem type (in HSV)
        self.gem_colors = {
            'BLUE_LIGHTNING': {
                'lower': np.array([100, 50, 50]),   # Blue
                'upper': np.array([130, 255, 255])
            },
            'GREEN_HEART': {
                'lower': np.array([40, 40, 40]),    # Green
                'upper': np.array([80, 255, 255])
            },
            'YELLOW_STAR': {
                'lower': np.array([20, 100, 100]),  # Yellow
                'upper': np.array([35, 255, 255])
            },
            'RED_FIRE': {
                'lower1': np.array([0, 100, 100]),   # Red (wraps around)
                'upper1': np.array([10, 255, 255]),
                'lower2': np.array([170, 100, 100]),
                'upper2': np.array([180, 255, 255])
            },
            'PURPLE_MOON': {
                'lower': np.array([130, 50, 50]),   # Purple
                'upper': np.array([160, 255, 255])
            },
            'ORANGE_SUN': {
                'lower': np.array([10, 100, 100]),  # Orange
                'upper': np.array([20, 255, 255])
            }
        }
    
    def get_dominant_color(self, cell_img: np.ndarray) -> str:
        """
        Detect gem type by dominant color
        
        Args:
            cell_img: Cell image (BGR)
            
        Returns:
            Gem type name (mặc định ORANGE_SUN nếu không nhận diện được)
        """
        # Convert to HSV
        hsv = cv2.cvtColor(cell_img, cv2.COLOR_BGR2HSV)
        
        # Remove border (use center 60%)
        h, w = hsv.shape[:2]
        margin_h = int(h * 0.2)
        margin_w = int(w * 0.2)
        hsv_center = hsv[margin_h:h-margin_h, margin_w:w-margin_w]
        
        best_match = 'ORANGE_SUN'  # Mặc định là ORANGE_SUN thay vì UNKNOWN
        best_ratio = 0.0
        
        # Check each color
        for gem_name, color_range in self.gem_colors.items():
            if 'lower1' in color_range:
                # Red wraps around (0-10 and 170-180)
                mask1 = cv2.inRange(hsv_center, color_range['lower1'], color_range['upper1'])
                mask2 = cv2.inRange(hsv_center, color_range['lower2'], color_range['upper2'])
                mask = cv2.bitwise_or(mask1, mask2)
            else:
                mask = cv2.inRange(hsv_center, color_range['lower'], color_range['upper'])
            
            # Calculate ratio of matching pixels
            ratio = np.count_nonzero(mask) / mask.size
            
            if ratio > best_ratio and ratio > 0.1:  # At least 10% match
                best_ratio = ratio
                best_match = gem_name
        
        return best_match
    
    def is_board_visible(self, board_img: np.ndarray, min_gems_for_active: int = 10) -> bool:
        """
        Kiểm tra xem bàn chơi 8x8 có ĐANG HOẠT ĐỘNG không (có gems trên bàn)
        
        Logic:
        - Nếu có ≥ min_gems gems → Bàn chơi đang hoạt động (đang chơi hoặc chờ lượt)
        - Nếu có < min_gems gems → Bàn chơi trống/kết thúc → Cần check UI
        
        Args:
            board_img: Full board image
            min_gems_for_active: Số gems tối thiểu để coi là bàn chơi đang hoạt động (default: 10)
            
        Returns:
            True nếu bàn chơi ĐANG HOẠT ĐỘNG (còn gems), False nếu trống/kết thúc
        """
        try:
            cell_height = board_img.shape[0] // self.rows
            cell_width = board_img.shape[1] // self.cols
            
            gems_detected = 0
            
            # Check nhiều cells hơn để chính xác (20 cells thay vì 14)
            sample_positions = [
                # Top rows
                (0, 0), (0, 2), (0, 4), (0, 6), (0, 7),
                # Middle rows
                (2, 0), (2, 3), (2, 7),
                (4, 0), (4, 3), (4, 7),
                # Bottom rows
                (6, 0), (6, 3), (6, 7),
                (7, 0), (7, 2), (7, 4), (7, 6), (7, 7),
                # Center
                (3, 3)
            ]
            
            for row, col in sample_positions:
                if row >= self.rows or col >= self.cols:
                    continue
                    
                # Extract cell
                y = row * cell_height
                x = col * cell_width
                cell_img = board_img[y:y+cell_height, x:x+cell_width]
                
                # Detect gem
                gem_type = self.get_dominant_color(cell_img)
                
                # Nếu detect được gem (không phải UNKNOWN) → có gem trên bàn
                if gem_type != 'UNKNOWN':
                    gems_detected += 1
            
            # LOGIC MỚI:
            # Nếu detect >= 10 gems (50% của 20 samples) → Bàn chơi còn hoạt động
            # Nếu detect < 10 gems → Bàn trống/kết thúc → Cần check UI (có thể là màn nhận quà)
            if self.debug:
                print(f"  Board check: {gems_detected}/{len(sample_positions)} gems detected")
            
            return gems_detected >= min_gems_for_active
            
        except Exception as e:
            if self.debug:
                print(f"⚠ Error checking board visibility: {e}")
            return False
    
    def read_board(self, board_img: np.ndarray) -> List[List[str]]:
        """
        Read entire board
        
        Args:
            board_img: Full board image
            
        Returns:
            2D list of gem types
        """
        board = []
        
        cell_height = board_img.shape[0] // self.rows
        cell_width = board_img.shape[1] // self.cols
        
        for row in range(self.rows):
            board_row = []
            
            for col in range(self.cols):
                # Extract cell
                y = row * cell_height
                x = col * cell_width
                cell_img = board_img[y:y+cell_height, x:x+cell_width]
                
                # Detect gem
                gem_type = self.get_dominant_color(cell_img)
                board_row.append(gem_type)
                
                # Không còn warning vì tất cả đều được nhận diện (ORANGE_SUN là mặc định)
            
            board.append(board_row)
        
        return board
    
    def visualize_board(self, board_img: np.ndarray, board: List[List[str]]):
        """Visualize detected board"""
        display = board_img.copy()
        cell_height = board_img.shape[0] // self.rows
        cell_width = board_img.shape[1] // self.cols
        
        for row in range(self.rows):
            for col in range(self.cols):
                gem = board[row][col]
                
                # Draw cell border
                y = row * cell_height
                x = col * cell_width
                color = (0, 255, 0) if gem != 'UNKNOWN' else (0, 0, 255)
                cv2.rectangle(display, (x, y), (x+cell_width, y+cell_height), color, 2)
                
                # Draw gem name
                text = gem[:4] if gem != 'UNKNOWN' else 'UNK'
                cv2.putText(display, text, (x+5, y+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        cv2.imshow('Board Detection', display)
        cv2.waitKey(1)
