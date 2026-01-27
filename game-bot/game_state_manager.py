"""
Game State Manager Module
Manages game flow automation (Reward → Map → Ready → Playing)
"""

import time
import pyautogui
import mss
import numpy as np
import cv2
from enum import Enum
from typing import Optional, Tuple
from ui_detector import UIDetector


class GameState(Enum):
    """Game states"""
    PLAYING = "playing"      # Đang chơi match-3
    REWARD = "reward"        # Màn nhận thưởng (WIN/LOSE)
    MAP = "map"              # Màn map (chọn boss)
    READY = "ready"          # Màn sẵn sàng (chuẩn bị đánh boss)
    UNKNOWN = "unknown"      # Không xác định


class GameStateManager:
    """Manages game state detection and automation"""
    
    def __init__(self, config: dict, game_window_region: dict, board_region: dict):
        """
        Initialize game state manager
        
        Args:
            config: Configuration dictionary
            game_window_region: Game window coordinates
            board_region: Board region coordinates
        """
        self.config = config
        self.game_window = game_window_region
        self.board_region = board_region
        
        # Initialize UI detector
        self.ui_detector = UIDetector(config)
        
        # Automation settings
        self.automation_config = config.get('game_automation', {})
        self.enabled = self.automation_config.get('enabled', True)
        self.after_click_delay = self.automation_config.get('after_click_delay', 1.5)
        
        # State tracking
        self.current_state = GameState.UNKNOWN
        self.last_state_change = time.time()
        
    def capture_game_window(self) -> np.ndarray:
        """
        Capture game window screenshot
        
        Returns:
            Screenshot as numpy array (BGR)
        """
        with mss.mss() as sct:
            monitor = {
                'top': self.game_window['top'],
                'left': self.game_window['left'],
                'width': self.game_window['width'],
                'height': self.game_window['height']
            }
            
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return img
    
    def detect_current_state(self, silent: bool = False) -> GameState:
        """
        Detect current game state based on UI elements
        
        Args:
            silent: If True, don't print detection logs
        
        Returns:
            Current GameState
        """
        screenshot = self.capture_game_window()
        
        # Phương pháp 1: Thử detect tất cả buttons với OCR
        buttons = self.ui_detector.detect_all_buttons(screenshot, use_fallback=False)
        
        # Nếu không có button nào, thử fallback color detection cho từng button
        if not buttons:
            if not silent:
                print("  🔍 OCR không tìm thấy button, thử color detection...")
            
            # Thử detect từng button riêng biệt
            for btn_type in ['nhan', 'chien', 'batdau']:
                pos = self.ui_detector.detect_button_by_color_position(screenshot, btn_type)
                if pos:
                    buttons[btn_type] = pos
                    if not silent:
                        print(f"    ✓ Tìm thấy nút '{btn_type}' bằng color detection")
        
        # DEBUG: Log detected buttons (only if not silent and verbose enabled)
        if not silent and self.config.get('debug', {}).get('verbose', False):
            if buttons:
                print(f"🔍 Detected buttons: {list(buttons.keys())}")
            else:
                print(f"🔍 No buttons detected")
        
        # Determine state based on which buttons are present
        if 'nhan' in buttons:
            return GameState.REWARD
        elif 'chien' in buttons:
            return GameState.MAP
        elif 'batdau' in buttons:
            return GameState.READY
        else:
            # Assume PLAYING if no special buttons detected
            return GameState.PLAYING
    
    def click_at_position(self, x: int, y: int, relative: bool = True):
        """
        Click at position in game window
        
        Args:
            x: X coordinate
            y: Y coordinate
            relative: If True, x/y are relative to game window
        """
        if relative:
            # Convert relative position to absolute screen position
            abs_x = self.game_window['left'] + x
            abs_y = self.game_window['top'] + y
        else:
            abs_x = x
            abs_y = y
        
        # Move and click
        pyautogui.moveTo(abs_x, abs_y, duration=0.2)
        time.sleep(0.1)
        pyautogui.click()
        
        print(f"   🖱️  Clicked at ({abs_x}, {abs_y})")
    
    def handle_reward_screen(self) -> bool:
        """
        Handle reward screen - Click "Nhận" button, then wait and handle next
        
        Returns:
            True if handled successfully
        """
        print("\n🎁 Phát hiện màn REWARD - Đang tìm nút 'Nhận'...")
        
        start_time = time.time()
        screenshot = self.capture_game_window()
        button_pos = self.ui_detector.detect_button(screenshot, 'nhan', use_region_hint=True)
        elapsed = time.time() - start_time
        
        if button_pos:
            print(f"   ✓ Tìm thấy nút 'Nhận' tại ({button_pos[0]}, {button_pos[1]}) trong {elapsed:.2f}s")
            self.click_at_position(button_pos[0], button_pos[1])
            print("✅ Đã nhấn 'Nhận'!")
            
            # Wait 2 seconds then look for "Chiến"
            print("⏳ Đợi 2 giây...")
            time.sleep(2.0)
            
            return self.handle_map_screen()
        else:
            print(f"❌ KHÔNG TÌM THẤY nút 'Nhận' (đã tìm {elapsed:.2f}s)")
            print("💡 Kiểm tra: OCR có hoạt động không? Tesseract đã cài chưa?")
            return False
    
    def handle_map_screen(self) -> bool:
        """
        Handle map screen - Click "Chiến" button, then wait and handle next
        
        Returns:
            True if handled successfully
        """
        print("\n🗺️  Phát hiện màn MAP - Đang nhấn 'Chiến'...")
        
        start_time = time.time()
        screenshot = self.capture_game_window()
        button_pos = self.ui_detector.detect_button(screenshot, 'chien', use_region_hint=True)
        elapsed = time.time() - start_time
        
        if button_pos:
            print(f"   ✓ Tìm thấy nút 'Chiến' tại ({button_pos[0]}, {button_pos[1]}) trong {elapsed:.2f}s")
            self.click_at_position(button_pos[0], button_pos[1])
            print("✅ Đã nhấn 'Chiến'!")
            
            # Wait 2 seconds then look for "Bắt đầu"
            print("⏳ Đợi 2 giây...")
            time.sleep(2.0)
            
            return self.handle_ready_screen()
        else:
            print(f"⚠️ Không tìm thấy nút 'Chiến' (đã tìm {elapsed:.2f}s)")
            return False
    
    def handle_ready_screen(self) -> bool:
        """
        Handle ready screen - Click "Bắt đầu" button
        
        Returns:
            True if handled successfully
        """
        print("\n⚔️  Phát hiện màn READY - Đang nhấn 'Bắt đầu'...")
        
        start_time = time.time()
        screenshot = self.capture_game_window()
        button_pos = self.ui_detector.detect_button(screenshot, 'batdau', use_region_hint=True)
        elapsed = time.time() - start_time
        
        if button_pos:
            print(f"   ✓ Tìm thấy nút 'Bắt đầu' tại ({button_pos[0]}, {button_pos[1]}) trong {elapsed:.2f}s")
            self.click_at_position(button_pos[0], button_pos[1])
            print("✅ Đã nhấn 'Bắt đầu'!")
            print("🎮 Chuẩn bị chơi match-3...\n")
            time.sleep(2.0)  # Wait for game to start
            return True
        else:
            print(f"⚠️ Không tìm thấy nút 'Bắt đầu' (đã tìm {elapsed:.2f}s)")
            return False
    
    def update_and_handle_state(self, silent_check: bool = False) -> GameState:
        """
        Update current state and handle automation
        Sequential flow: Nhận → 2s → Chiến → 2s → Bắt đầu
        
        Args:
            silent_check: If True, don't print logs during initial state detection
        
        Returns:
            Current GameState after handling
        """
        if not self.enabled:
            return GameState.PLAYING
        
        # Detect current state
        new_state = self.detect_current_state(silent=silent_check)
        
        # Log state change
        if new_state != self.current_state:
            print(f"\n🔄 State changed: {self.current_state.value} → {new_state.value}")
            self.current_state = new_state
            self.last_state_change = time.time()
        
        # Handle state - Chain calls: REWARD → MAP → READY
        if new_state == GameState.REWARD:
            # This will handle REWARD → MAP → READY sequentially
            self.handle_reward_screen()
            # After handling, return current state (might not be PLAYING yet)
            return self.detect_current_state(silent=False)
        
        elif new_state == GameState.MAP:
            # This will handle MAP → READY sequentially
            self.handle_map_screen()
            # After handling, return current state
            return self.detect_current_state(silent=False)
        
        elif new_state == GameState.READY:
            self.handle_ready_screen()
            # After handling, should be in PLAYING state
            time.sleep(1)  # Give game time to transition
            return self.detect_current_state(silent=False)
        
        elif new_state == GameState.PLAYING:
            # Ready to play match-3
            return GameState.PLAYING
        
        return new_state
    
    def wait_for_playing_state(self, timeout: float = 30.0) -> bool:
        """
        Wait until game is in PLAYING state
        
        Args:
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if reached PLAYING state, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            state = self.update_and_handle_state()
            
            if state == GameState.PLAYING:
                return True
            
            time.sleep(0.5)
        
        print(f"⚠️ Timeout waiting for PLAYING state")
        return False
