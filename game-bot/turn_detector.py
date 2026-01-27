"""
Turn Detector Module
Detects when it's the player's turn and checks the turn timer
"""

import cv2
import numpy as np
import pytesseract
from typing import Optional, Tuple
import re


class TurnDetector:
    """Detects player turn and timer in PvP match-3 game"""
    
    def __init__(self, your_turn_region: dict, timer_region: dict, 
                 tesseract_cmd: Optional[str] = None):
        """
        Initialize turn detector
        
        Args:
            your_turn_region: Region to check for "Your Turn" text
                             {"top": y, "left": x, "width": w, "height": h}
            timer_region: Region to check for timer countdown
                         {"top": y, "left": x, "width": w, "height": h}
            tesseract_cmd: Path to tesseract executable (optional)
        """
        self.your_turn_region = your_turn_region
        self.timer_region = timer_region
        
        # Set tesseract path if provided
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def detect_your_turn_text(self, screen_img: np.ndarray) -> bool:
        """
        Detect "Your Turn" text on screen
        
        Args:
            screen_img: Full screen capture
            
        Returns:
            True if "Your Turn" is visible
        """
        try:
            # Extract the region
            region = self.your_turn_region
            roi = screen_img[
                region['top']:region['top'] + region['height'],
                region['left']:region['left'] + region['width']
            ]
            
            # Method 1: Template matching (fast, reliable)
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Detect yellow/orange text (Your Turn is typically yellow/orange)
            lower_yellow = np.array([15, 100, 100])
            upper_yellow = np.array([35, 255, 255])
            mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
            
            # Detect red text
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
            
            # Combine masks
            mask = cv2.bitwise_or(mask_yellow, cv2.bitwise_or(mask_red1, mask_red2))
            
            # Calculate text coverage
            text_coverage = np.sum(mask > 0) / mask.size
            
            # If significant text is present, it's likely "Your Turn"
            if text_coverage > 0.15:  # More than 15% of region has text
                return True
            
            # Method 2: OCR fallback (slower but more accurate)
            # Convert to grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Threshold
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # OCR
            text = pytesseract.image_to_string(thresh, config='--psm 7')
            text_clean = text.lower().replace(' ', '').replace('\n', '')
            
            # Check for "your turn" variations
            keywords = ['yourturn', 'your', 'turn', 'luot', 'cua', 'ban']
            for keyword in keywords:
                if keyword in text_clean:
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠ Error detecting 'Your Turn': {e}")
            return False
    
    def detect_timer_value(self, screen_img: np.ndarray) -> Optional[int]:
        """
        Detect the countdown timer value
        
        Args:
            screen_img: Full screen capture
            
        Returns:
            Timer value (0-10) or None if not detected
        """
        try:
            # Extract the timer region
            region = self.timer_region
            roi = screen_img[
                region['top']:region['top'] + region['height'],
                region['left']:region['left'] + region['width']
            ]
            
            # Method 1: Color-based detection (fast)
            # Convert to HSV
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Detect yellow/orange numbers (timer is typically yellow)
            lower_yellow = np.array([15, 100, 100])
            upper_yellow = np.array([35, 255, 255])
            mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            
            # If no significant yellow found, try white
            if np.sum(mask > 0) < 100:
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            
            # Apply morphology to clean up
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Method 2: OCR to read the number
            # Configure OCR for single digits/numbers
            text = pytesseract.image_to_string(
                mask, 
                config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
            )
            
            # Extract number
            numbers = re.findall(r'\d+', text)
            
            if numbers:
                timer_value = int(numbers[0])
                
                # Validate range (timer should be 0-10)
                if 0 <= timer_value <= 10:
                    return timer_value
            
            return None
            
        except Exception as e:
            print(f"⚠ Error detecting timer: {e}")
            return None
    
    def is_action_allowed(self, screen_img: np.ndarray, 
                         min_timer_value: int = 2) -> Tuple[bool, dict]:
        """
        Check if actions are allowed based on turn and timer
        
        Args:
            screen_img: Full screen capture
            min_timer_value: Minimum timer value to allow action (safety margin)
            
        Returns:
            Tuple of (allowed, info_dict)
            - allowed: True if actions are allowed
            - info_dict: {"is_my_turn": bool, "timer": int, "reason": str}
        """
        info = {
            "is_my_turn": False,
            "timer": None,
            "reason": ""
        }
        
        # Check if it's my turn
        is_my_turn = self.detect_your_turn_text(screen_img)
        info["is_my_turn"] = is_my_turn
        
        if not is_my_turn:
            info["reason"] = "Not your turn"
            return (False, info)
        
        # Check timer
        timer_value = self.detect_timer_value(screen_img)
        info["timer"] = timer_value
        
        if timer_value is None:
            info["reason"] = "Timer not detected"
            return (False, info)
        
        if timer_value < min_timer_value:
            info["reason"] = f"Timer too low ({timer_value}s)"
            return (False, info)
        
        # All conditions met
        info["reason"] = "Action allowed"
        return (True, info)
    
    def wait_for_my_turn(self, capture_func, max_wait_time: float = 30.0,
                        check_interval: float = 0.5) -> bool:
        """
        Wait until it's the player's turn
        
        Args:
            capture_func: Function to capture screen (returns numpy array)
            max_wait_time: Maximum time to wait (seconds)
            check_interval: Time between checks (seconds)
            
        Returns:
            True if turn detected, False if timeout
        """
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            # Capture screen
            screen_img = capture_func()
            
            # Check if it's my turn
            allowed, info = self.is_action_allowed(screen_img, min_timer_value=1)
            
            if allowed:
                print(f"✓ Your turn detected! Timer: {info['timer']}s")
                return True
            
            # Wait before next check
            time.sleep(check_interval)
        
        print(f"⏱ Timeout waiting for turn ({max_wait_time}s)")
        return False


class SimpleTurnDetector:
    """
    Simplified turn detector using color thresholds only
    (No OCR required - faster but less accurate)
    """
    
    def __init__(self, your_turn_region: dict, timer_region: dict):
        """
        Initialize simple turn detector
        
        Args:
            your_turn_region: Region to check for "Your Turn" text
            timer_region: Region to check for timer
        """
        self.your_turn_region = your_turn_region
        self.timer_region = timer_region
    
    def detect_your_turn_by_color(self, screen_img: np.ndarray) -> bool:
        """
        Detect "Your Turn" by checking for yellow/red text in region
        
        Args:
            screen_img: Full screen capture
            
        Returns:
            True if significant colored text is detected
        """
        try:
            region = self.your_turn_region
            roi = screen_img[
                region['top']:region['top'] + region['height'],
                region['left']:region['left'] + region['width']
            ]
            
            # Convert to HSV
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Yellow/Orange detection
            lower = np.array([10, 100, 100])
            upper = np.array([40, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
            
            # Calculate coverage
            coverage = np.sum(mask > 0) / mask.size
            
            return coverage > 0.12  # 12% threshold
            
        except Exception as e:
            return False
    
    def detect_timer_by_color(self, screen_img: np.ndarray) -> bool:
        """
        Detect timer presence by checking for yellow number
        
        Args:
            screen_img: Full screen capture
            
        Returns:
            True if timer is visible
        """
        try:
            region = self.timer_region
            roi = screen_img[
                region['top']:region['top'] + region['height'],
                region['left']:region['left'] + region['width']
            ]
            
            # Convert to HSV
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Yellow detection
            lower = np.array([15, 100, 150])
            upper = np.array([35, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
            
            # Calculate coverage
            coverage = np.sum(mask > 0) / mask.size
            
            return coverage > 0.05  # 5% threshold
            
        except Exception as e:
            return False
    
    def is_action_allowed(self, screen_img: np.ndarray) -> Tuple[bool, str]:
        """
        Simple check if action is allowed
        
        Returns:
            (allowed, reason)
        """
        has_turn_text = self.detect_your_turn_by_color(screen_img)
        has_timer = self.detect_timer_by_color(screen_img)
        
        if not has_turn_text:
            return (False, "No 'Your Turn' detected")
        
        if not has_timer:
            return (False, "No timer detected")
        
        return (True, "Action allowed")


if __name__ == "__main__":
    # Test turn detector
    print("Testing turn detector...")
    
    # Example configuration (adjust based on your game)
    your_turn_region = {
        "top": 100,
        "left": 400,
        "width": 600,
        "height": 150
    }
    
    timer_region = {
        "top": 150,
        "left": 350,
        "width": 80,
        "height": 100
    }
    
    # Use simple detector (no OCR)
    detector = SimpleTurnDetector(your_turn_region, timer_region)
    
    print("Simple turn detector initialized")
    print("Note: Adjust regions in config.yaml for your game")
