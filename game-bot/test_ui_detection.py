"""
Test UI Detection - Kiểm tra xem OCR có hoạt động không
"""

print("="*60)
print("TESTING UI DETECTION")
print("="*60)

# Test 1: Check Tesseract installation
print("\n1. Kiểm tra Tesseract...")
try:
    import pytesseract
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    # Test with simple text
    import cv2
    import numpy as np
    
    # Create test image with text
    test_img = np.ones((100, 300, 3), dtype=np.uint8) * 255
    cv2.putText(test_img, "Test Text", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    text = pytesseract.image_to_string(test_img, lang='eng')
    if 'Test' in text or 'test' in text.lower():
        print("   ✓ Tesseract hoạt động!")
        print(f"   Detected: {text.strip()}")
    else:
        print("   ⚠ Tesseract không detect được text")
        print(f"   Result: {text}")
except Exception as e:
    print(f"   ✗ Tesseract ERROR: {e}")
    print("\n   💡 Hướng dẫn cài Tesseract:")
    print("   1. Download: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   2. Cài vào: C:\\Program Files\\Tesseract-OCR\\")
    print("   3. Thêm Vietnamese language pack khi cài")
    exit(1)

# Test 2: Load config and UI detector
print("\n2. Testing UI Detector...")
try:
    import yaml
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    from ui_detector import UIDetector
    detector = UIDetector(config)
    print("   ✓ UI Detector initialized")
    print(f"   OCR confidence: {detector.confidence_threshold}%")
except Exception as e:
    print(f"   ✗ UI Detector ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 3: Test button detection
print("\n3. Testing button detection...")
print("\n   📸 Bạn cần:")
print("   1. Mở game và đến màn WIN/LOSE (có nút Nhận)")
print("   2. Hoặc đến màn MAP (có nút Chiến)")
print("   3. Hoặc đến màn READY (có nút Bắt đầu)")
print("\n   ⏸️  Nhấn ENTER khi sẵn sàng...")
input()

try:
    from game_state_manager import GameStateManager, GameState
    
    game_window = config['game_window']
    board_region = config['screen']
    
    state_mgr = GameStateManager(config, game_window, board_region)
    
    print("\n   Capturing game window...")
    screenshot = state_mgr.capture_game_window()
    print(f"   ✓ Screenshot size: {screenshot.shape}")
    
    print("\n   Detecting buttons...")
    buttons = detector.detect_all_buttons(screenshot)
    
    if buttons:
        print(f"   ✓ Found {len(buttons)} button(s):")
        for btn_name, btn_pos in buttons.items():
            print(f"     - {btn_name}: position ({btn_pos[0]}, {btn_pos[1]})")
    else:
        print("   ✗ NO BUTTONS DETECTED!")
        print("\n   Possible reasons:")
        print("   1. OCR không nhận diện được chữ Việt")
        print("   2. Game window region sai")
        print("   3. Chữ trên button quá nhỏ/mờ")
        print("   4. Button không có trong màn hình hiện tại")
    
    # Test state detection
    print("\n   Detecting game state...")
    state = state_mgr.detect_current_state()
    print(f"   Current state: {state.value}")
    
    if state == GameState.PLAYING:
        print("   ℹ️  State is PLAYING - không có UI buttons")
    elif state == GameState.REWARD:
        print("   🎁 State is REWARD - nên có nút Nhận")
    elif state == GameState.MAP:
        print("   🗺️  State is MAP - nên có nút Chiến")
    elif state == GameState.READY:
        print("   ⚡ State is READY - nên có nút Bắt đầu")
    
except Exception as e:
    print(f"   ✗ Detection ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*60)
print("✅ TEST COMPLETED!")
print("="*60)

print("\n💡 Nếu không detect được buttons:")
print("1. Check Tesseract đã cài Vietnamese language pack")
print("2. Verify game_window region trong config.yaml")
print("3. Thử tắt game_automation nếu không cần:")
print("   game_automation:")
print("     enabled: false")
