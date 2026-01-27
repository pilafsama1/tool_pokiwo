"""
Test detect nút "Nhận" - Kiểm tra nhanh
"""

import yaml
import cv2
import numpy as np
from game_state_manager import GameStateManager, GameState
from ui_detector import UIDetector

print("="*60)
print("TEST DETECT NÚT 'NHẬN'")
print("="*60)

# Load config
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Initialize
game_window = config['game_window']
board_region = config['screen']

state_mgr = GameStateManager(config, game_window, board_region)
detector = UIDetector(config)

print("\n📸 Mở game và đến màn NHẬN QUÀ (có nút Nhận)")
print("⏸️  Nhấn ENTER khi sẵn sàng...")
input()

print("\n1. Chụp màn hình game...")
screenshot = state_mgr.capture_game_window()
print(f"   ✓ Screenshot size: {screenshot.shape}")

print("\n2. Detect state (với fallback color detection)...")
state = state_mgr.detect_current_state(silent=False)
print(f"   Kết quả: {state.value}")

if state == GameState.REWARD:
    print("\n   ✅ THÀNH CÔNG - Phát hiện màn REWARD!")
else:
    print(f"\n   ❌ THẤT BẠI - State là: {state.value}")
    print("\n   Thử detect trực tiếp nút 'Nhận'...")
    
    # Try OCR
    print("\n3. Thử OCR detection...")
    text_regions = detector.detect_text_regions(screenshot)
    print(f"   Tìm thấy {len(text_regions)} text regions:")
    for region in text_regions[:10]:  # Show first 10
        print(f"     - '{region['text']}' (confidence: {region['confidence']}%)")
    
    ocr_pos = detector.find_button_by_text(text_regions, 'nhan', screenshot.shape)
    if ocr_pos:
        print(f"   ✅ OCR tìm thấy nút 'Nhận' tại: {ocr_pos}")
    else:
        print("   ❌ OCR không tìm thấy nút 'Nhận'")
    
    # Try color detection
    print("\n4. Thử Color detection...")
    color_pos = detector.detect_button_by_color_position(screenshot, 'nhan')
    if color_pos:
        print(f"   ✅ Color detection tìm thấy nút 'Nhận' tại: {color_pos}")
    else:
        print("   ❌ Color detection không tìm thấy nút 'Nhận'")

print("\n5. Lưu screenshot để kiểm tra...")
cv2.imwrite("debug_screenshot.png", screenshot)
print("   ✓ Đã lưu: debug_screenshot.png")

print("\n" + "="*60)
print("HOÀN TẤT")
print("="*60)
