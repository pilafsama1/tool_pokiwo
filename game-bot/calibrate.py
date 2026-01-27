"""
Board Calibration Tool
Allows user to select game board region by dragging mouse
"""

import cv2
import numpy as np
import mss
import yaml
from pathlib import Path
import os
from datetime import datetime


class BoardCalibrator:
    """Interactive board calibration tool"""
    
    def __init__(self, calibration_file: str = "calibration_settings.yaml"):
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.image = None
        self.image_copy = None
        self.calibration_file = calibration_file
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for region selection"""
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Start drawing
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            # Update rectangle while dragging
            if self.drawing:
                self.end_point = (x, y)
                
        elif event == cv2.EVENT_LBUTTONUP:
            # Finish drawing
            self.drawing = False
            self.end_point = (x, y)
    
    def capture_screenshot(self) -> np.ndarray:
        """Capture full screen"""
        with mss.mss() as sct:
            # Capture primary monitor
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            
            # Convert to numpy array
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
        return img
    
    def select_button_position(self, button_name: str = "NÚT", screenshot: np.ndarray = None) -> dict:
        """
        Let user select a button position by clicking
        
        Args:
            button_name: Name of button being selected
            screenshot: Pre-captured screenshot (if None, will capture new one)
        
        Returns:
            Dictionary with x, y coordinates
        """
        print("\n" + "="*60)
        print(f"🖱️  CHỌN VỊ TRÍ {button_name}")
        print("="*60)
        
        # Use provided screenshot or capture new one
        if screenshot is not None:
            image = screenshot.copy()
        else:
            print("\n📸 Đang chụp màn hình...")
            image = self.capture_screenshot()
        
        # Resize for display if too large
        display_height = 800
        height, width = image.shape[:2]
        if height > display_height:
            scale = display_height / height
            display_width = int(width * scale)
            display_img = cv2.resize(image, (display_width, display_height))
        else:
            display_img = image.copy()
            scale = 1.0
        
        print("\n📌 HƯỚNG DẪN:")
        print(f"1. CLICK vào giữa nút {button_name}")
        print("2. Nhấn SPACE hoặc ENTER để xác nhận")
        print("3. Nhấn ESC để chọn lại")
        print("4. Nhấn Q để bỏ qua\n")
        
        # Create window
        window_name = f"Chọn vị trí {button_name} - Click vào nút"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        selected_pos = None
        confirmed = False
        
        def click_callback(event, x, y, flags, param):
            nonlocal selected_pos
            if event == cv2.EVENT_LBUTTONDOWN:
                selected_pos = (x, y)
        
        cv2.setMouseCallback(window_name, click_callback)
        
        while True:
            display_copy = display_img.copy()
            
            if selected_pos:
                # Draw crosshair at selected position
                cv2.circle(display_copy, selected_pos, 10, (0, 255, 0), 2)
                cv2.line(display_copy, (selected_pos[0]-20, selected_pos[1]), 
                        (selected_pos[0]+20, selected_pos[1]), (0, 255, 0), 2)
                cv2.line(display_copy, (selected_pos[0], selected_pos[1]-20), 
                        (selected_pos[0], selected_pos[1]+20), (0, 255, 0), 2)
                
                text = f"Vi tri da chon: ({int(selected_pos[0]/scale)}, {int(selected_pos[1]/scale)})"
                cv2.putText(display_copy, text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                text2 = "Nhan SPACE de xac nhan, ESC de chon lai"
                cv2.putText(display_copy, text2, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                text = f"Click vao giua nut {button_name}"
                cv2.putText(display_copy, text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.imshow(window_name, display_copy)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' ') or key == 13:  # SPACE or ENTER
                if selected_pos:
                    confirmed = True
                    break
            elif key == 27:  # ESC
                selected_pos = None
            elif key == ord('q') or key == ord('Q'):
                cv2.destroyAllWindows()
                return None
        
        cv2.destroyAllWindows()
        
        if confirmed and selected_pos:
            return {
                'x': int(selected_pos[0] / scale),
                'y': int(selected_pos[1] / scale)
            }
        
        return None
    
    def select_region(self, region_name: str = "BÀN CỜ", screenshot: np.ndarray = None) -> dict:
        """
        Let user select a region interactively
        
        Args:
            region_name: Name of the region being selected
            screenshot: Pre-captured screenshot (if None, will capture new one)
        
        Returns:
            Dictionary with top, left, width, height
        """
        print("\n" + "="*60)
        print(f"🎯 CHỌN VÙNG {region_name}")
        print("="*60)
        
        # Reset selection
        self.start_point = None
        self.end_point = None
        self.drawing = False
        
        # Use provided screenshot or capture new one
        if screenshot is not None:
            self.image = screenshot.copy()
        else:
            print("\n📸 Đang chụp màn hình...")
            self.image = self.capture_screenshot()
        self.image_copy = self.image.copy()
        
        # Resize for display if too large
        display_height = 800
        height, width = self.image.shape[:2]
        if height > display_height:
            scale = display_height / height
            display_width = int(width * scale)
            display_img = cv2.resize(self.image, (display_width, display_height))
        else:
            display_img = self.image.copy()
            scale = 1.0
        
        print("\n📌 HƯỚNG DẪN:")
        print(f"1. Kéo chuột để chọn vùng {region_name}")
        print("2. Chọn từ GÓC TRÊN TRÁI đến GÓC DƯỚI PHẢI")
        print("3. Nhấn SPACE hoặc ENTER để xác nhận")
        print("4. Nhấn ESC để chọn lại")
        print("5. Nhấn Q để thoát\n")
        
        # Create window
        window_name = f"Chọn vùng {region_name} - Kéo chuột để chọn"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        confirmed = False
        
        while True:
            # Draw rectangle
            display_copy = display_img.copy()
            
            if self.start_point and self.end_point:
                # Draw rectangle
                cv2.rectangle(display_copy, self.start_point, self.end_point, (0, 255, 0), 2)
                
                # Draw info text
                width = abs(self.end_point[0] - self.start_point[0])
                height = abs(self.end_point[1] - self.start_point[1])
                
                text = f"Vung chon: {int(width/scale)}x{int(height/scale)} pixels"
                cv2.putText(display_copy, text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                text2 = "Nhan SPACE de xac nhan, ESC de chon lai"
                cv2.putText(display_copy, text2, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                text = f"Keo chuot de chon vung {region_name}"
                cv2.putText(display_copy, text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.imshow(window_name, display_copy)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' ') or key == 13:  # SPACE or ENTER
                if self.start_point and self.end_point:
                    confirmed = True
                    break
                    
            elif key == 27:  # ESC
                self.start_point = None
                self.end_point = None
                
            elif key == ord('q') or key == ord('Q'):
                cv2.destroyAllWindows()
                return None
        
        cv2.destroyAllWindows()
        
        if confirmed and self.start_point and self.end_point:
            # Calculate coordinates (account for scale)
            x1 = int(min(self.start_point[0], self.end_point[0]) / scale)
            y1 = int(min(self.start_point[1], self.end_point[1]) / scale)
            x2 = int(max(self.start_point[0], self.end_point[0]) / scale)
            y2 = int(max(self.start_point[1], self.end_point[1]) / scale)
            
            return {
                'top': y1,
                'left': x1,
                'width': x2 - x1,
                'height': y2 - y1
            }
        
        return None
    
    def select_regions(self, interactive: bool = True) -> dict:
        """
        Let user select both game window and board regions
        
        Args:
            interactive: If True, wait for user input between steps
        
        Returns:
            Dictionary with 'game_window' and 'board' regions
        """
        print("\n" + "="*60)
        print("🎮 CHỌN 2 VÙNG: CỬA SỔ GAME & BÀN CỜ")
        print("="*60)
        print("\n📸 Đang chụp màn hình (chỉ 1 lần)...")
        
        # Capture screenshot ONCE for both regions
        screenshot = self.capture_screenshot()
        print("✅ Đã chụp màn hình!\n")
        
        # Select game window first
        print("🖼️  BƯỚC 1: Chọn toàn bộ cửa sổ game")
        print("   (Từ góc trên trái đến góc dưới phải của cửa sổ game)")
        if interactive:
            print()
            input("   Nhấn ENTER để tiếp tục...")
        
        game_region = self.select_region("CỬA SỔ GAME", screenshot=screenshot)
        
        if not game_region:
            print("\n❌ Đã hủy chọn vùng game.")
            return None
        
        print("\n✅ Đã chọn vùng game:")
        print(f"   {game_region['width']}x{game_region['height']} tại ({game_region['left']}, {game_region['top']})")
        
        # Select board region
        print("\n♟️  BƯỚC 2: Chọn vùng bàn cờ 8x8")
        print("   (Chỉ chọn phần bàn cờ, không bao gồm khung và UI)")
        if interactive:
            print()
            input("   Nhấn ENTER để tiếp tục...")
        
        board_region = self.select_region("BÀN CỜ 8x8", screenshot=screenshot)
        
        if not board_region:
            print("\n❌ Đã hủy chọn vùng bàn cờ.")
            return None
        
        print("\n✅ Đã chọn vùng bàn cờ:")
        print(f"   {board_region['width']}x{board_region['height']} tại ({board_region['left']}, {board_region['top']})")
        print(f"   Kích thước mỗi ô: ~{board_region['width']//8}x{board_region['height']//8}")
        
        return {
            'game_window': game_region,
            'board': board_region
        }
    
    def select_full_calibration(self, interactive: bool = True) -> dict:
        """
        Chọn đầy đủ: 3 vùng (Game + Board + Timer) + 3 nút (Nhận + Chiến + Bắt đầu)
        
        Args:
            interactive: If True, wait for user input between steps
        
        Returns:
            Dictionary with all regions and button positions
        """
        print("\n" + "="*60)
        print("🎮 CALIBRATION HOÀN CHỈNH")
        print("="*60)
        print("\n📋 Bạn sẽ chọn:")
        print("   📍 3 VÙNG: Game Window + Board + Timer")
        print("   🖱️  3 NÚT: Nhận + Chiến + Bắt đầu")
        print("\n📸 Đang chụp màn hình (chỉ 1 lần)...")
        
        # Capture screenshot ONCE for all selections
        screenshot = self.capture_screenshot()
        print("✅ Đã chụp màn hình!\n")
        
        # ============== PHẦN 1: CHỌN 3 VÙNG ==============
        
        # 1. Game window
        print("🖼️  BƯỚC 1/6: Chọn toàn bộ cửa sổ game")
        print("   (Từ góc trên trái đến góc dưới phải)")
        if interactive:
            input("   Nhấn ENTER để tiếp tục...")
        
        game_region = self.select_region("CỬA SỔ GAME", screenshot=screenshot)
        if not game_region:
            print("\n❌ Đã hủy.")
            return None
        print(f"   ✅ {game_region['width']}x{game_region['height']}")
        
        # 2. Board region
        print("\n♟️  BƯỚC 2/6: Chọn vùng bàn cờ 8x8")
        print("   (Chỉ chọn phần gems, không bao gồm khung)")
        if interactive:
            input("   Nhấn ENTER để tiếp tục...")
        
        board_region = self.select_region("BÀN CỜ 8x8", screenshot=screenshot)
        if not board_region:
            print("\n❌ Đã hủy.")
            return None
        print(f"   ✅ {board_region['width']}x{board_region['height']}")
        
        # 3. Timer region
        print("\n⏱️  BƯỚC 3/6: Chọn vùng timer (đếm ngược)")
        if interactive:
            input("   Nhấn ENTER để tiếp tục...")
        
        timer_region = self.select_region("TIMER", screenshot=screenshot)
        if not timer_region:
            print("   ⚠️  Bỏ qua timer")
        else:
            print(f"   ✅ {timer_region['width']}x{timer_region['height']}")
        
        # ============== PHẦN 2: CHỌN 3 NÚT ==============
        
        print("\n" + "="*60)
        print("🖱️  PHẦN 2: CHỌN VỊ TRÍ CÁC NÚT")
        print("="*60)
        print("\n💡 Mở game đến màn hình tương ứng để chọn nút")
        
        # 4. Nút Nhận
        print("\n🎁 BƯỚC 4/6: Chọn nút NHẬN (màn reward)")
        print("   Hãy mở game đến màn nhận thưởng sau khi thắng boss")
        if interactive:
            input("   Nhấn ENTER khi đã sẵn sàng...")
        
        # Chụp màn hình mới cho nút Nhận
        print("   📸 Đang chụp...")
        screenshot_nhan = self.capture_screenshot()
        nhan_button = self.select_button_position("NÚT NHẬN", screenshot=screenshot_nhan)
        if not nhan_button:
            print("   ⚠️  Bỏ qua nút Nhận")
        else:
            print(f"   ✅ Vị trí: ({nhan_button['x']}, {nhan_button['y']})")
        
        # 5. Nút Chiến
        print("\n🗺️  BƯỚC 5/6: Chọn nút CHIẾN (màn map)")
        print("   Hãy mở game đến màn chọn ải (map screen)")
        if interactive:
            input("   Nhấn ENTER khi đã sẵn sàng...")
        
        print("   📸 Đang chụp...")
        screenshot_chien = self.capture_screenshot()
        chien_button = self.select_button_position("NÚT CHIẾN", screenshot=screenshot_chien)
        if not chien_button:
            print("   ⚠️  Bỏ qua nút Chiến")
        else:
            print(f"   ✅ Vị trí: ({chien_button['x']}, {chien_button['y']})")
        
        # 6. Nút Bắt đầu
        print("\n⚔️  BƯỚC 6/6: Chọn nút BẮT ĐẦU (màn ready)")
        print("   Hãy mở game đến màn chuẩn bị đánh boss")
        if interactive:
            input("   Nhấn ENTER khi đã sẵn sàng...")
        
        print("   📸 Đang chụp...")
        screenshot_batdau = self.capture_screenshot()
        batdau_button = self.select_button_position("NÚT BẮT ĐẦU", screenshot=screenshot_batdau)
        if not batdau_button:
            print("   ⚠️  Bỏ qua nút Bắt đầu")
        else:
            print(f"   ✅ Vị trí: ({batdau_button['x']}, {batdau_button['y']})")
        
        # Trả về tất cả dữ liệu
        return {
            'game_window': game_region,
            'board': board_region,
            'timer': timer_region,
            'buttons': {
                'nhan': nhan_button,
                'chien': chien_button,
                'batdau': batdau_button
            }
        }
    
    def update_config(self, data: dict, config_path: str = "config.yaml"):
        """
        Update config.yaml with new regions and button positions
        
        Args:
            data: Dictionary with 'game_window', 'board', 'timer', and 'buttons'
            config_path: Path to config file
        """
        # Load existing config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Update game window coordinates
        if 'game_window' not in config:
            config['game_window'] = {}
        
        config['game_window']['top'] = data['game_window']['top']
        config['game_window']['left'] = data['game_window']['left']
        config['game_window']['width'] = data['game_window']['width']
        config['game_window']['height'] = data['game_window']['height']
        
        # Update board coordinates
        config['screen']['top'] = data['board']['top']
        config['screen']['left'] = data['board']['left']
        config['screen']['width'] = data['board']['width']
        config['screen']['height'] = data['board']['height']
        
        # Update timer region if provided
        if 'timer' in data and data['timer'] is not None:
            if 'turn_detection' not in config:
                config['turn_detection'] = {}
            
            config['turn_detection']['enabled'] = True
            config['turn_detection']['detection_method'] = 'ocr'
            config['turn_detection']['timer_region'] = {
                'top': data['timer']['top'],
                'left': data['timer']['left'],
                'width': data['timer']['width'],
                'height': data['timer']['height']
            }
            config['turn_detection']['min_timer_value'] = 2
            config['turn_detection']['max_wait_time'] = 30
        
        # Update button positions
        if 'buttons' in data:
            if 'button_positions' not in config:
                config['button_positions'] = {}
            
            if data['buttons'].get('nhan'):
                config['button_positions']['nhan'] = {
                    'x': data['buttons']['nhan']['x'],
                    'y': data['buttons']['nhan']['y']
                }
            
            if data['buttons'].get('chien'):
                config['button_positions']['chien'] = {
                    'x': data['buttons']['chien']['x'],
                    'y': data['buttons']['chien']['y']
                }
            
            if data['buttons'].get('batdau'):
                config['button_positions']['batdau'] = {
                    'x': data['buttons']['batdau']['x'],
                    'y': data['buttons']['batdau']['y']
                }
        
        # Save config
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print("\n✅ Đã cập nhật config.yaml:")
        print("\n   🖼️  Vùng game window:")
        print(f"      {data['game_window']['width']}x{data['game_window']['height']} tại ({data['game_window']['left']}, {data['game_window']['top']})")
        print("\n   ♟️  Vùng bàn cờ:")
        print(f"      {data['board']['width']}x{data['board']['height']} tại ({data['board']['left']}, {data['board']['top']})")
        
        if 'timer' in data and data['timer'] is not None:
            print("\n   ⏱️  Vùng timer:")
            print(f"      {data['timer']['width']}x{data['timer']['height']} tại ({data['timer']['left']}, {data['timer']['top']})")
            print("      ✅ Turn detection: ENABLED")
        
        if 'buttons' in data:
            print("\n   🖱️  Vị trí các nút:")
            if data['buttons'].get('nhan'):
                print(f"      🎁 Nút Nhận: ({data['buttons']['nhan']['x']}, {data['buttons']['nhan']['y']})")
            if data['buttons'].get('chien'):
                print(f"      🗺️  Nút Chiến: ({data['buttons']['chien']['x']}, {data['buttons']['chien']['y']})")
            if data['buttons'].get('batdau'):
                print(f"      ⚔️  Nút Bắt đầu: ({data['buttons']['batdau']['x']}, {data['buttons']['batdau']['y']})")
    
    def save_calibration_settings(self, data: dict):
        """
        Lưu cấu hình calibration vào file riêng để dùng lại sau
        
        Args:
            data: Dictionary with 'game_window', 'board', 'timer', and 'buttons'
        """
        # Thêm metadata
        settings = {
            'saved_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'game_window': data['game_window'],
            'board': data['board']
        }
        
        if 'timer' in data and data['timer'] is not None:
            settings['timer'] = data['timer']
        
        if 'buttons' in data:
            settings['buttons'] = data['buttons']
        
        # Lưu vào file
        with open(self.calibration_file, 'w', encoding='utf-8') as f:
            yaml.dump(settings, f, default_flow_style=False, allow_unicode=True)
        
        print(f"\n💾 Đã lưu cấu hình vào: {self.calibration_file}")
    
    def load_calibration_settings(self) -> dict:
        """
        Load cấu hình calibration đã lưu trước đó
        
        Returns:
            Dictionary với các cấu hình đã lưu hoặc None nếu không tồn tại
        """
        if not os.path.exists(self.calibration_file):
            return None
        
        try:
            with open(self.calibration_file, 'r', encoding='utf-8') as f:
                settings = yaml.safe_load(f)
            
            # Validate các trường bắt buộc
            if 'game_window' not in settings or 'board' not in settings:
                print("⚠️  File cấu hình không hợp lệ")
                return None
            
            return settings
        except Exception as e:
            print(f"⚠️  Lỗi khi đọc file cấu hình: {e}")
            return None
    
    def display_saved_settings(self, settings: dict):
        """
        Hiển thị thông tin cấu hình đã lưu
        
        Args:
            settings: Dictionary với các cấu hình đã lưu
        """
        print("\n" + "="*60)
        print("📋 CẤU HÌNH ĐÃ LƯU TRƯỚC ĐÓ")
        print("="*60)
        
        if 'saved_at' in settings:
            print(f"\n⏰ Lưu lúc: {settings['saved_at']}")
        
        print("\n🖼️  Vùng Game Window:")
        gw = settings['game_window']
        print(f"   Position: ({gw['left']}, {gw['top']})")
        print(f"   Size: {gw['width']}x{gw['height']}")
        
        print("\n♟️  Vùng Bàn Cờ:")
        bd = settings['board']
        print(f"   Position: ({bd['left']}, {bd['top']})")
        print(f"   Size: {bd['width']}x{bd['height']}")
        print(f"   Cell size: ~{bd['width']//8}x{bd['height']//8}")
        
        if 'timer' in settings and settings['timer'] is not None:
            print("\n⏱️  Vùng Timer:")
            tm = settings['timer']
            print(f"   Position: ({tm['left']}, {tm['top']})")
            print(f"   Size: {tm['width']}x{tm['height']}")
        
        if 'buttons' in settings:
            print("\n🖱️  Vị trí các nút:")
            buttons = settings['buttons']
            if buttons.get('nhan'):
                print(f"   🎁 Nút Nhận: ({buttons['nhan']['x']}, {buttons['nhan']['y']})")
            if buttons.get('chien'):
                print(f"   🗺️  Nút Chiến: ({buttons['chien']['x']}, {buttons['chien']['y']})")
            if buttons.get('batdau'):
                print(f"   ⚔️  Nút Bắt đầu: ({buttons['batdau']['x']}, {buttons['batdau']['y']})")


def main():
    """Main calibration process"""
    print("\n" + "="*60)
    print("🎮 CÔNG CỤ CALIBRATION")
    print("="*60)
    
    # Create calibrator
    calibrator = BoardCalibrator()
    
    # Kiểm tra xem có cấu hình đã lưu không
    saved_settings = calibrator.load_calibration_settings()
    
    if saved_settings:
        calibrator.display_saved_settings(saved_settings)
        print("\n" + "="*60)
        print("❓ BẠN MUỐN:")
        print("="*60)
        print("   1. Sử dụng cấu hình đã lưu (nhanh)")
        print("   2. Set lại toàn bộ (chọn vùng mới)")
        print("   3. Thoát")
        print("\n👉 Chọn (1/2/3): ", end='')
        
        choice = input().strip()
        
        if choice == '1':
            # Sử dụng cấu hình đã lưu
            print("\n✅ Sử dụng cấu hình đã lưu...")
            
            # Cập nhật vào config.yaml
            print("\n❓ Cập nhật vào config.yaml? (y/n): ", end='')
            confirm = input().lower()
            
            if confirm == 'y' or confirm == 'yes':
                calibrator.update_config(saved_settings)
                print("\n" + "="*60)
                print("✅ HOÀN THÀNH!")
                print("="*60)
                print("\n🚀 Bây giờ bạn có thể chạy bot:")
                print("   python main.py")
            else:
                print("\n❌ Đã hủy. Không cập nhật config.yaml")
            return
            
        elif choice == '3':
            print("\n👋 Tạm biệt!")
            return
        elif choice != '2':
            print("\n⚠️  Lựa chọn không hợp lệ. Thoát.")
            return
    
    # Set lại từ đầu
    print("\n⚠️  QUAN TRỌNG:")
    print("   1. Mở game lên trước")
    print("   2. Đảm bảo bàn cờ 8x8 hiện trên màn hình")
    print("   3. Không che game bởi cửa sổ khác")
    print("\n📌 Bạn sẽ chọn 2 vùng:")
    print("   🖼️  Vùng 1: TOÀN BỘ CỬA SỔ GAME (để đọc thông tin)")
    print("   ♟️  Vùng 2: BÀN CỜ 8x8 (để phát hiện gem)")
    print("\n📌 Nhấn ENTER để bắt đầu...")
    input()
    
    # Let user select both regions
    regions = calibrator.select_regions()
    
    if regions:
        print("\n" + "="*60)
        print("📊 THÔNG TIN CÁC VÙNG ĐÃ CHỌN")
        print("="*60)
        
        print("\n🖼️  Vùng Game Window:")
        print(f"   Position: ({regions['game_window']['left']}, {regions['game_window']['top']})")
        print(f"   Size: {regions['game_window']['width']}x{regions['game_window']['height']}")
        
        print("\n♟️  Vùng Bàn Cờ:")
        print(f"   Position: ({regions['board']['left']}, {regions['board']['top']})")
        print(f"   Size: {regions['board']['width']}x{regions['board']['height']}")
        print(f"   Cell size: ~{regions['board']['width']//8}x{regions['board']['height']//8}")
        
        # Confirm
        print("\n❓ Lưu cấu hình? (y/n): ", end='')
        confirm = input().lower()
        
        if confirm == 'y' or confirm == 'yes':
            # Lưu vào file riêng
            calibrator.save_calibration_settings(regions)
            
            # Cập nhật vào config.yaml
            calibrator.update_config(regions)
            
            print("\n" + "="*60)
            print("✅ HOÀN THÀNH!")
            print("="*60)
            print("\n🚀 Bây giờ bạn có thể chạy bot:")
            print("   python main.py")
            print("\n💡 Hoặc test trước:")
            print("   python main.py --test")
            print("\n💾 Lần sau chạy calibrate.py, bạn có thể chọn dùng lại cấu hình này!")
        else:
            print("\n❌ Đã hủy. Không lưu thay đổi.")
    else:
        print("\n❌ Đã hủy calibration.")


if __name__ == "__main__":
    main()
