"""
UI Detector Module
Detects buttons and UI elements using OCR (pytesseract)
"""

import cv2
import numpy as np
import pytesseract
import sys
from typing import Optional, Dict, Tuple, List
from pathlib import Path
import re


class UIDetector:
    """Detects UI elements (buttons) in game window using OCR"""
    
    def __init__(self, config: dict):
        """
        Initialize UI detector
        
        Args:
            config: Configuration dictionary with OCR settings
        """
        self.config = config
        self.ocr_config = config.get('game_automation', {})
        
        # Configure tesseract path - tự động tìm trong bundle hoặc system
        tesseract_path = self._find_tesseract_path()
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Button keywords to detect
        self.button_keywords = {
            'nhan': ['Nhận', 'Nhan', 'NHẬN', 'NHAN'],
            'chien': ['Chiến', 'Chien', 'CHIẾN', 'CHIEN'],
            'batdau': ['Bắt đầu', 'Bat dau', 'BẮT ĐẦU', 'BAT DAU', 'Bắt Đầu']
        }
        
        # OCR confidence threshold
        self.confidence_threshold = self.ocr_config.get('ocr_confidence', 60)
    
    def _find_tesseract_path(self) -> Optional[str]:
        """
        Tự động tìm Tesseract OCR (bundle hoặc system)
        
        Returns:
            Đường dẫn đến tesseract.exe hoặc None
        """
        import os
        from pathlib import Path
        
        # 1. Kiểm tra trong config
        config_path = self.ocr_config.get('tesseract_path', '')
        if config_path and Path(config_path).exists():
            return config_path
        
        # 2. Kiểm tra trong thư mục bundle (cho .exe)
        if getattr(sys, 'frozen', False):
            # Running as .exe
            bundle_dir = Path(sys._MEIPASS)
        else:
            # Running as script
            bundle_dir = Path(__file__).parent
        
        bundle_tess = bundle_dir / "bundle" / "tesseract" / "tesseract.exe"
        if bundle_tess.exists():
            print(f"✓ Found bundled Tesseract: {bundle_tess}")
            return str(bundle_tess)
        
        # 3. Kiểm tra thư mục tesseract cùng cấp với .exe
        local_tess = bundle_dir / "tesseract" / "tesseract.exe"
        if local_tess.exists():
            print(f"✓ Found local Tesseract: {local_tess}")
            return str(local_tess)
        
        # 4. Kiểm tra PATH system (nếu user đã cài)
        system_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for path in system_paths:
            if Path(path).exists():
                print(f"✓ Found system Tesseract: {path}")
                return path
        
        # 5. Thử tìm trong PATH
        import shutil
        tess_in_path = shutil.which("tesseract")
        if tess_in_path:
            print(f"✓ Found Tesseract in PATH: {tess_in_path}")
            return tess_in_path
        
        print("⚠️ Tesseract not found - OCR features will be disabled")
        return None
    
    def get_search_region(self, button_type: str, img_shape: tuple) -> Optional[Tuple[int, int, int, int]]:
        """
        Lấy vùng tìm kiếm ưu tiên cho từng loại nút (để tìm nhanh hơn)
        
        Args:
            button_type: Loại nút ('nhan', 'chien', 'batdau')
            img_shape: Shape của ảnh (height, width, channels)
            
        Returns:
            (x1, y1, x2, y2) - tọa độ vùng tìm kiếm, hoặc None để tìm toàn màn hình
        """
        height, width = img_shape[:2]
        
        if button_type == 'nhan':
            # Nút "Nhận" - giữa dưới cùng màn hình
            # Vùng: 30-70% chiều ngang, 60-85% chiều dọc
            x1 = int(width * 0.30)
            x2 = int(width * 0.70)
            y1 = int(height * 0.60)
            y2 = int(height * 0.85)
            return (x1, y1, x2, y2)
            
        elif button_type == 'chien':
            # Nút "Chiến" - góc phải dưới cùng
            # Vùng: 60-95% chiều ngang, 70-95% chiều dọc
            x1 = int(width * 0.60)
            x2 = int(width * 0.95)
            y1 = int(height * 0.70)
            y2 = int(height * 0.95)
            return (x1, y1, x2, y2)
            
        elif button_type == 'batdau':
            # Nút "Bắt đầu" - góc phải dưới cùng (tương tự Chiến)
            # Vùng: 60-95% chiều ngang, 70-95% chiều dọc
            x1 = int(width * 0.60)
            x2 = int(width * 0.95)
            y1 = int(height * 0.70)
            y2 = int(height * 0.95)
            return (x1, y1, x2, y2)
            
        return None  # Tìm toàn màn hình nếu không xác định
    
    def preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: Input image (BGR)
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while keeping edges
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Apply adaptive threshold to get better text contrast
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Invert if background is dark
        if np.mean(gray) < 127:
            thresh = cv2.bitwise_not(thresh)
        
        return thresh
    
    def detect_text_regions(self, image: np.ndarray) -> List[Dict]:
        """
        Detect all text regions in image using OCR
        
        Args:
            image: Input image (BGR)
            
        Returns:
            List of detected text regions with positions
        """
        # Preprocess image
        processed = self.preprocess_for_ocr(image)
        
        # OCR with bounding boxes
        ocr_data = pytesseract.image_to_data(
            processed,
            lang='vie+eng',  # Vietnamese + English
            output_type=pytesseract.Output.DICT,
            config='--psm 11'  # Sparse text detection
        )
        
        text_regions = []
        
        for i in range(len(ocr_data['text'])):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            
            # Filter by confidence
            if conf < self.confidence_threshold or not text:
                continue
            
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            w = ocr_data['width'][i]
            h = ocr_data['height'][i]
            
            text_regions.append({
                'text': text,
                'confidence': conf,
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'center_x': x + w // 2,
                'center_y': y + h // 2
            })
        
        return text_regions
    
    def find_button_by_text(self, text_regions: List[Dict], 
                            button_type: str, screenshot_shape: tuple = None) -> Optional[Tuple[int, int]]:
        """
        Find button position by matching text
        
        Args:
            text_regions: List of detected text regions
            button_type: Type of button ('nhan', 'chien', 'batdau')
            screenshot_shape: Shape of screenshot (height, width) for position priority
            
        Returns:
            (x, y) center position of button or None
        """
        keywords = self.button_keywords.get(button_type, [])
        matched_regions = []
        
        # Find all matching regions
        for region in text_regions:
            text = region['text']
            
            # Check if any keyword matches
            for keyword in keywords:
                # Flexible matching (ignore case, accents)
                if self._fuzzy_match(text, keyword):
                    matched_regions.append(region)
                    break
        
        if not matched_regions:
            return None
        
        # Special handling for "Chiến" button - prefer bottom-right corner
        if button_type == 'chien' and screenshot_shape and len(matched_regions) > 1:
            height, width = screenshot_shape[:2]
            
            # Sort by distance from bottom-right corner (closest first)
            def distance_from_bottom_right(region):
                x = region['center_x']
                y = region['center_y']
                # Calculate distance from bottom-right corner
                dx = width - x
                dy = height - y
                return dx * dx + dy * dy
            
            matched_regions.sort(key=distance_from_bottom_right)
        
        # Return the first (or best) match
        best_match = matched_regions[0]
        return (best_match['center_x'], best_match['center_y'])
    
    def _fuzzy_match(self, text: str, keyword: str) -> bool:
        """
        Fuzzy text matching (ignore case and some accents)
        
        Args:
            text: Detected text
            keyword: Keyword to match
            
        Returns:
            True if matched
        """
        # Normalize both texts
        text_norm = text.lower().replace('đ', 'd').replace('ă', 'a').replace('â', 'a')
        keyword_norm = keyword.lower().replace('đ', 'd').replace('ă', 'a').replace('â', 'a')
        
        # Check if keyword is in text
        if keyword_norm in text_norm:
            return True
        
        # Check if text is in keyword (for partial matches)
        if text_norm in keyword_norm and len(text_norm) > 2:
            return True
        
        return False
    
    def detect_button_by_color_position(self, screenshot: np.ndarray, 
                                        button_type: str) -> Optional[Tuple[int, int]]:
        """
        Detect button by color and position (fallback method)
        
        Args:
            screenshot: Game window screenshot (BGR)
            button_type: Type of button to detect
            
        Returns:
            (x, y) position of button center or None
        """
        height, width = screenshot.shape[:2]
        
        # Convert to HSV for color detection
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # Define color ranges based on button type
        if button_type == 'batdau':
            # "Bắt đầu" button is ORANGE/YELLOW
            lower_orange = np.array([10, 100, 100])
            upper_orange = np.array([25, 255, 255])
            mask = cv2.inRange(hsv, lower_orange, upper_orange)
        else:
            # Other buttons (Nhận, Chiến) are typically BLUE/CYAN
            # Blue range in HSV
            lower_blue = np.array([100, 100, 100])
            upper_blue = np.array([130, 255, 255])
            
            # Cyan range (lighter blue)
            lower_cyan = np.array([80, 50, 50])
            upper_cyan = np.array([100, 255, 255])
            
            # Create masks
            mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
            mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
            mask = cv2.bitwise_or(mask_blue, mask_cyan)
        
        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Filter contours by size and position
        candidates = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by minimum size (button should be reasonably large)
            if area < 500:  # Minimum 500 pixels
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Calculate relative position
            rel_x = center_x / width
            rel_y = center_y / height
            
            # Filter by position based on button type
            if button_type == 'chien':
                # "Chiến" button: bottom-right corner
                # Right 40%, Bottom 40%
                if rel_x > 0.6 and rel_y > 0.6:
                    # Calculate distance from bottom-right
                    dist = ((1.0 - rel_x) ** 2 + (1.0 - rel_y) ** 2) ** 0.5
                    candidates.append((center_x, center_y, dist, area))
            
            elif button_type == 'batdau':
                # "Bắt đầu" button: search entire screen, prefer larger buttons
                # No position restriction - find anywhere in game window
                # Score based on area (larger = better)
                score = 1.0 / (area + 1)  # Inverse of area (smaller score = better)
                candidates.append((center_x, center_y, score, area))
            
            elif button_type == 'nhan':
                # "Nhận" button: center of screen
                # Center both horizontally and vertically
                if 0.3 < rel_x < 0.7 and 0.4 < rel_y < 0.7:
                    # Distance from center
                    dist = ((0.5 - rel_x) ** 2 + (0.55 - rel_y) ** 2) ** 0.5
                    candidates.append((center_x, center_y, dist, area))
        
        if not candidates:
            return None
        
        # Sort by score (lower is better) and area (larger is better)
        candidates.sort(key=lambda c: (c[2], -c[3]))
        
        # Return best candidate
        return (candidates[0][0], candidates[0][1])
    
    def detect_button(self, screenshot: np.ndarray, 
                     button_type: str, use_region_hint: bool = True) -> Optional[Tuple[int, int]]:
        """
        Detect a specific button in screenshot
        Uses COLOR+POSITION detection first (faster), falls back to OCR if needed
        
        Args:
            screenshot: Game window screenshot (BGR)
            button_type: Type of button to detect
            use_region_hint: If True, only search in optimal region for faster detection
            
        Returns:
            (x, y) position of button center or None
        """
        # Lấy vùng tìm kiếm ưu tiên (để tìm nhanh hơn)
        search_region = None
        region_offset = (0, 0)
        img_to_search = screenshot
        
        if use_region_hint:
            region = self.get_search_region(button_type, screenshot.shape)
            if region:
                x1, y1, x2, y2 = region
                img_to_search = screenshot[y1:y2, x1:x2].copy()
                region_offset = (x1, y1)
                search_region = region
        
        # Method 1: Try COLOR detection first (FASTER - 0.05-0.1s)
        color_result = self.detect_button_by_color_position(img_to_search, button_type)
        
        if color_result:
            # Điều chỉnh tọa độ về màn hình gốc nếu dùng region
            return (color_result[0] + region_offset[0], color_result[1] + region_offset[1])
        
        # Method 2: Fallback to OCR detection (SLOWER but more accurate - 0.1-0.3s)
        print(f"   ⚠️ Color detection không tìm thấy '{button_type}', thử OCR...")
        text_regions = self.detect_text_regions(img_to_search)
        ocr_result = self.find_button_by_text(text_regions, button_type, img_to_search.shape)
        
        if ocr_result:
            print(f"   ✅ Tìm thấy bằng OCR!")
            # Điều chỉnh tọa độ về màn hình gốc nếu dùng region
            return (ocr_result[0] + region_offset[0], ocr_result[1] + region_offset[1])
        
        return None
    
    def detect_all_buttons(self, screenshot: np.ndarray, use_fallback: bool = True, 
                          use_region_hints: bool = True) -> Dict[str, Tuple[int, int]]:
        """
        Detect all buttons in screenshot
        
        Args:
            screenshot: Game window screenshot (BGR)
            use_fallback: If True, use color detection as fallback
            use_region_hints: If True, search in optimal regions for faster detection
            
        Returns:
            Dictionary mapping button types to positions
        """
        buttons = {}
        
        # Tìm từng nút riêng biệt trong vùng ưu tiên của nó
        for button_type in self.button_keywords.keys():
            # Sử dụng detect_button với region hint để tìm nhanh
            pos = self.detect_button(screenshot, button_type, use_region_hint=use_region_hints)
            if pos:
                buttons[button_type] = pos
        
        return buttons
    
    def detect_reward_items(self, screenshot: np.ndarray) -> bool:
        """
        Phát hiện xem có màn thưởng (reward items) trên màn hình không
        
        Dấu hiệu của màn thưởng:
        - Có các icon/items phần thưởng (hình vuông/tròn màu sắc)
        - Có chữ "WIN" hoặc hiệu ứng
        - Có nút "Nhận" màu xanh ở dưới
        
        Args:
            screenshot: Game window screenshot (BGR)
            
        Returns:
            True nếu phát hiện màn thưởng, False nếu không
        """
        height, width = screenshot.shape[:2]
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # METHOD 1: Tìm nút "Nhận" màu xanh/cyan đặc trưng
        # Nút "Nhận" thường có màu xanh lam/cyan rất rõ
        lower_cyan = np.array([85, 100, 100])
        upper_cyan = np.array([105, 255, 255])
        mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
        
        # Tìm contours lớn (nút Nhận)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask_cyan = cv2.morphologyEx(mask_cyan, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask_cyan, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        large_cyan_buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 2000:  # Nút "Nhận" khá lớn
                x, y, w, h = cv2.boundingRect(contour)
                # Nút thường ở phần dưới giữa màn hình
                rel_y = y / height
                rel_x = x / width
                if rel_y > 0.6 and 0.3 < rel_x < 0.7:  # Bottom center
                    large_cyan_buttons.append((x, y, w, h, area))
        
        # Nếu có nút xanh lớn ở vị trí đúng → Có thể là màn thưởng
        if large_cyan_buttons:
            return True
        
        # METHOD 2: Tìm các reward items (hình vuông/icon màu sắc)
        # Reward items thường có nhiều màu sắc sặc sỡ
        # Tìm vùng có density màu sắc cao ở center màn hình
        center_region = screenshot[int(height*0.3):int(height*0.7), int(width*0.2):int(width*0.8)]
        center_hsv = cv2.cvtColor(center_region, cv2.COLOR_BGR2HSV)
        
        # Tính saturation trung bình (màu sắc sặc sỡ = saturation cao)
        saturation = center_hsv[:, :, 1]
        mean_saturation = np.mean(saturation)
        
        # Nếu saturation cao → Có nhiều màu sắc → Có thể là reward items
        if mean_saturation > 80:  # Threshold
            return True
        
        return False
    
    def debug_show_detections(self, screenshot: np.ndarray):
        """
        Show all detected text for debugging
        
        Args:
            screenshot: Game window screenshot
        """
        text_regions = self.detect_text_regions(screenshot)
        
        debug_img = screenshot.copy()
        
        for region in text_regions:
            x, y, w, h = region['x'], region['y'], region['width'], region['height']
            text = region['text']
            conf = region['confidence']
            
            # Draw rectangle
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw text
            label = f"{text} ({conf}%)"
            cv2.putText(debug_img, label, (x, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow("OCR Detection Debug", debug_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
