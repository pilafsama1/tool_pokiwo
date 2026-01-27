"""
Tool to capture gem templates from game
Click on each gem type to capture it as a template
"""

import cv2
import mss
import numpy as np
from pathlib import Path

class TemplateCapturer:
    def __init__(self):
        self.templates_dir = Path("assets/templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Gem types to capture
        self.gem_types = [
            "BLUE_LIGHTNING",
            "GREEN_HEART",
            "ORANGE_SUN",
            "PURPLE_MOON",
            "RED_FIRE",
            "YELLOW_STAR",
            "RED_HEART",
            "GRAY_YINYANG"
        ]
        
        self.current_gem = 0
        self.screenshot = None
        self.click_pos = None
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.click_pos = (x, y)
    
    def capture_templates(self):
        """Interactive template capture"""
        print("="*60)
        print("🎯 CHỤP TEMPLATES")
        print("="*60)
        print("\nHướng dẫn:")
        print("1. Mở game và hiển thị bàn cờ")
        print("2. Nhấn ENTER để chụp màn hình")
        print("3. Click vào GIỮA gem bạn muốn chụp")
        print("4. Lặp lại cho tất cả loại gem")
        print("\n⚠️  Đảm bảo bàn cờ không bị che và hiện rõ ràng!")
        print("="*60)
        
        for i, gem_name in enumerate(self.gem_types):
            print(f"\n[{i+1}/{len(self.gem_types)}] Chụp: {gem_name}")
            print("   Nhấn ENTER để chụp màn hình...")
            input()
            
            # Capture screen
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                self.screenshot = np.array(screenshot)
                self.screenshot = cv2.cvtColor(self.screenshot, cv2.COLOR_BGRA2BGR)
            
            print(f"   ✓ Đã chụp màn hình: {self.screenshot.shape[1]}x{self.screenshot.shape[0]}")
            print(f"   📌 Click vào GIỮA gem {gem_name}...")
            
            # Show screenshot and wait for click
            window_name = f"Click on {gem_name}"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 1200, 800)
            cv2.setMouseCallback(window_name, self.mouse_callback)
            
            self.click_pos = None
            
            display_img = self.screenshot.copy()
            while True:
                cv2.imshow(window_name, display_img)
                key = cv2.waitKey(1)
                
                if self.click_pos:
                    # Extract gem area around click
                    x, y = self.click_pos
                    
                    # Use 120x70 template size
                    half_w = 60
                    half_h = 35
                    
                    x1 = max(0, x - half_w)
                    y1 = max(0, y - half_h)
                    x2 = min(self.screenshot.shape[1], x + half_w)
                    y2 = min(self.screenshot.shape[0], y + half_h)
                    
                    gem_img = self.screenshot[y1:y2, x1:x2]
                    
                    # Save template
                    template_path = self.templates_dir / f"{gem_name}.png"
                    cv2.imwrite(str(template_path), gem_img)
                    
                    print(f"   ✓ Đã lưu: {template_path.name} ({gem_img.shape[1]}x{gem_img.shape[0]})")
                    
                    cv2.destroyWindow(window_name)
                    break
                
                if key == 27:  # ESC
                    print("   ⚠️  Bỏ qua gem này")
                    cv2.destroyWindow(window_name)
                    break
        
        print("\n" + "="*60)
        print("✅ HOÀN THÀNH!")
        print(f"Đã chụp templates vào: {self.templates_dir}")
        print("="*60)

def main():
    capturer = TemplateCapturer()
    capturer.capture_templates()

if __name__ == "__main__":
    main()
