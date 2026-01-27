"""
Auto extract gem templates from game screenshot
This will try to remove borders and extract just the gem icons
"""

import cv2
import numpy as np
from pathlib import Path

def extract_gem_from_cell(cell_img):
    """Extract gem icon from cell (remove border)"""
    # Remove outer border (keep center 70%)
    h, w = cell_img.shape[:2]
    margin_x = int(w * 0.15)
    margin_y = int(h * 0.15)
    
    gem_img = cell_img[margin_y:h-margin_y, margin_x:w-margin_x]
    
    # Resize to standard size
    gem_img = cv2.resize(gem_img, (90, 60), interpolation=cv2.INTER_LANCZOS4)
    
    return gem_img

# Load game screenshot
print("Nhập tên file ảnh game (ví dụ: game_screenshot.png):")
screenshot_file = input().strip()

if not screenshot_file:
    print("❌ Cần nhập tên file!")
    exit()

img = cv2.imread(screenshot_file)
if img is None:
    print(f"❌ Không đọc được file: {screenshot_file}")
    exit()

print(f"✓ Đã load ảnh: {img.shape[1]}x{img.shape[0]}")

# Manual gem selection
gem_types = [
    "BLUE_LIGHTNING",
    "GREEN_HEART", 
    "ORANGE_SUN",
    "PURPLE_MOON",
    "RED_FIRE",
    "YELLOW_STAR"
]

templates_dir = Path("assets/templates")
templates_dir.mkdir(parents=True, exist_ok=True)

print("\n" + "="*60)
print("Hướng dẫn: Kéo chuột để chọn GEM (không lấy viền xung quanh)")
print("="*60)

class State:
    def __init__(self):
        self.selecting = False
        self.x_start = 0
        self.y_start = 0
        self.x_end = 0
        self.y_end = 0

for gem_name in gem_types:
    print(f"\n🎯 Chọn gem: {gem_name}")
    print("   Nhấn ENTER để tiếp tục...")
    input()
    
    state = State()
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            state.selecting = True
            state.x_start, state.y_start = x, y
            state.x_end, state.y_end = x, y
        elif event == cv2.EVENT_MOUSEMOVE and state.selecting:
            state.x_end, state.y_end = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            state.selecting = False
            state.x_end, state.y_end = x, y
    
    window_name = f"Chọn {gem_name} - ENTER để lưu, ESC để bỏ qua"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1200, 800)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    while True:
        display = img.copy()
        
        if state.x_start != state.x_end and state.y_start != state.y_end:
            cv2.rectangle(display, (state.x_start, state.y_start), (state.x_end, state.y_end), (0, 255, 0), 2)
        
        cv2.imshow(window_name, display)
        key = cv2.waitKey(1) & 0xFF
        
        if key == 13:  # ENTER
            if state.x_start != state.x_end and state.y_start != state.y_end:
                x1 = min(state.x_start, state.x_end)
                x2 = max(state.x_start, state.x_end)
                y1 = min(state.y_start, state.y_end)
                y2 = max(state.y_start, state.y_end)
                
                selected_img = img[y1:y2, x1:x2]
                
                # Extract gem (remove border)
                gem_img = extract_gem_from_cell(selected_img)
                
                # Save
                template_path = templates_dir / f"{gem_name}.png"
                cv2.imwrite(str(template_path), gem_img)
                
                print(f"   ✓ Đã lưu: {template_path.name} (90x60)")
                cv2.destroyWindow(window_name)
                break
        
        elif key == 27:  # ESC
            print("   ⚠️  Đã bỏ qua")
            cv2.destroyWindow(window_name)
            break

print("\n✅ Hoàn thành!")
