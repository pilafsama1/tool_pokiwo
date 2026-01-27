"""
Simple tool to capture one gem template at a time
Just click on a gem when prompted
"""

import cv2
import mss
import numpy as np
from pathlib import Path
import sys

def capture_single_gem(gem_name):
    """Capture a single gem template"""
    templates_dir = Path("assets/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🎯 Chụp: {gem_name}")
    print("   Nhấn ENTER để chụp màn hình...")
    input()
    
    # Capture screen
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    print(f"   ✓ Đã chụp: {img.shape[1]}x{img.shape[0]}")
    
    # Variables
    selecting = False
    x_start, y_start = 0, 0
    x_end, y_end = 0, 0
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal selecting, x_start, y_start, x_end, y_end
        
        if event == cv2.EVENT_LBUTTONDOWN:
            selecting = True
            x_start, y_start = x, y
            x_end, y_end = x, y
        
        elif event == cv2.EVENT_MOUSEMOVE and selecting:
            x_end, y_end = x, y
        
        elif event == cv2.EVENT_LBUTTONUP:
            selecting = False
            x_end, y_end = x, y
    
    # Setup window
    window_name = f"Kéo chuột để chọn gem {gem_name} - Nhấn ENTER để lưu, ESC để bỏ qua"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1200, 800)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    print(f"   📌 Kéo chuột để chọn vùng gem {gem_name}")
    print("      Nhấn ENTER để lưu, ESC để bỏ qua")
    
    while True:
        display = img.copy()
        
        # Draw selection rectangle
        if x_start != x_end and y_start != y_end:
            cv2.rectangle(display, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
        
        cv2.imshow(window_name, display)
        key = cv2.waitKey(1) & 0xFF
        
        if key == 13:  # ENTER
            if x_start != x_end and y_start != y_end:
                # Get selected region
                x1 = min(x_start, x_end)
                x2 = max(x_start, x_end)
                y1 = min(y_start, y_end)
                y2 = max(y_start, y_end)
                
                gem_img = img[y1:y2, x1:x2]
                
                # Resize to standard size
                gem_img = cv2.resize(gem_img, (120, 70), interpolation=cv2.INTER_LANCZOS4)
                
                # Save
                template_path = templates_dir / f"{gem_name}.png"
                cv2.imwrite(str(template_path), gem_img)
                
                print(f"   ✓ Đã lưu: {template_path.name} (120x70)")
                cv2.destroyWindow(window_name)
                return True
            else:
                print("   ⚠️  Chưa chọn vùng!")
        
        elif key == 27:  # ESC
            print("   ⚠️  Đã bỏ qua")
            cv2.destroyWindow(window_name)
            return False
    
    cv2.destroyWindow(window_name)

def main():
    if len(sys.argv) < 2:
        print("Cách dùng:")
        print("  python capture_gem.py BLUE_LIGHTNING")
        print("  python capture_gem.py GREEN_HEART")
        print("  python capture_gem.py ORANGE_SUN")
        print("  python capture_gem.py PURPLE_MOON")
        print("  python capture_gem.py RED_FIRE")
        print("  python capture_gem.py YELLOW_STAR")
        print("  python capture_gem.py RED_HEART")
        print("  python capture_gem.py GRAY_YINYANG")
        return
    
    gem_name = sys.argv[1]
    print("="*60)
    print(f"🎯 CHỤP TEMPLATE: {gem_name}")
    print("="*60)
    print("\n⚠️  Đảm bảo:")
    print("   1. Game đã mở")
    print("   2. Gem cần chụp hiện rõ trên màn hình")
    print("="*60)
    
    capture_single_gem(gem_name)
    
    print("\n✅ Xong!")

if __name__ == "__main__":
    main()
