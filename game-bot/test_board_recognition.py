"""
Test Board Recognition với các ảnh debug đã lưu
"""

import cv2
import yaml
import numpy as np
from pathlib import Path
from board_reader_color import BoardReaderColor

def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def test_single_image(image_path: str, config: dict):
    """Test nhận diện 1 ảnh với multiple scans"""
    print("\n" + "="*80)
    print(f"📸 Test file: {Path(image_path).name}")
    print("="*80)
    
    # Load ảnh
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Không đọc được file {image_path}")
        return
    
    print(f"✓ Đã load ảnh: {img.shape[1]}x{img.shape[0]} pixels")
    
    # Khởi tạo board reader
    board_config = config['board']
    reader = BoardReaderColor(
        rows=board_config['rows'],
        cols=board_config['cols'],
        debug=True
    )
    
    # Nhận diện board NHIỀU LẦN (3 lần)
    num_scans = 3
    print(f"\n🔍 Bắt đầu nhận diện board ({num_scans} lần quét)...")
    
    all_boards = []
    for scan_num in range(num_scans):
        board = reader.read_board(img)
        if board:
            all_boards.append(board)
            print(f"   ✓ Lần quét {scan_num + 1}: OK")
    
    if not all_boards:
        print("❌ Không nhận diện được board")
        return
    
    # Merge kết quả từ các lần quét
    print(f"\n🔄 Merge kết quả từ {len(all_boards)} lần quét...")
    merged_board = merge_board_scans(all_boards)
    
    print(f"\n✓ Đã nhận diện board {len(merged_board)}x{len(merged_board[0])}")
    
    # Hiển thị board
    print("\n📊 BOARD SAU KHI MERGE:")
    print("-" * 80)
    
    # Đếm từng loại gem
    gem_count = {}
    unknown_count = 0
    
    for row_idx, row in enumerate(merged_board):
        row_display = []
        for col_idx, gem in enumerate(row):
            if gem == 'UNKNOWN':
                unknown_count += 1
                row_display.append('???')
            else:
                # Viết tắt tên gem
                short_name = gem.replace('_', ' ')[:3].upper()
                row_display.append(short_name)
                gem_count[gem] = gem_count.get(gem, 0) + 1
        
        print(f"Row {row_idx}: [{', '.join(row_display)}]")
    
    print("-" * 80)
    
    # Thống kê
    print("\n📈 THỐNG KÊ:")
    total_cells = len(merged_board) * len(merged_board[0])
    recognized = total_cells - unknown_count
    accuracy = (recognized / total_cells) * 100
    
    print(f"   Tổng số ô: {total_cells}")
    print(f"   Đã nhận diện: {recognized} ({accuracy:.1f}%)")
    print(f"   Chưa nhận diện (UNKNOWN): {unknown_count}")
    
    if gem_count:
        print("\n   Chi tiết các gem đã nhận diện:")
        for gem_type, count in sorted(gem_count.items()):
            print(f"      • {gem_type}: {count} viên")
    
    # Đánh giá
    print("\n🎯 ĐÁNH GIÁ:")
    if accuracy == 100:
        print("   🎉 HOÀN HẢO - Nhận diện 100%!")
    elif accuracy >= 95:
        print("   ✅ XUẤT SẮC - Nhận diện gần như hoàn hảo!")
    elif accuracy >= 90:
        print("   ✅ RẤT TỐT - Nhận diện rất tốt!")
    elif accuracy >= 75:
        print("   ✓ TỐT - Nhận diện chấp nhận được")
    elif accuracy >= 50:
        print("   ⚠️ TRUNG BÌNH - Cần cải thiện")
    else:
        print("   ❌ KÉM - Cần điều chỉnh lại detection")
    
    if unknown_count > 0:
        print(f"\n💡 GỢI Ý:")
        print(f"   - Còn {unknown_count} ô chưa nhận diện được")
        print(f"   - Kiểm tra template images trong assets/templates/")
        print(f"   - Xem xét điều chỉnh threshold trong config.yaml")
        print(f"   - Chạy capture_templates.py để lấy template mới")

def merge_board_scans(boards):
    """Merge multiple board scans"""
    from collections import Counter
    
    if not boards:
        return None
    
    rows = len(boards[0])
    cols = len(boards[0][0])
    merged = []
    
    for r in range(rows):
        row = []
        for c in range(cols):
            # Lấy tất cả giá trị từ các lần quét
            values = [board[r][c] for board in boards]
            
            # Đếm số lần xuất hiện (loại bỏ UNKNOWN)
            non_unknown = [v for v in values if v != 'UNKNOWN']
            
            if non_unknown:
                # Chọn giá trị xuất hiện nhiều nhất
                most_common = Counter(non_unknown).most_common(1)[0][0]
                row.append(most_common)
            else:
                row.append('UNKNOWN')
        
        merged.append(row)
    
    return merged

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("🧪 TEST BOARD RECOGNITION - Kiểm tra nhận diện kim cương")
    print("="*80)
    
    # Load config
    config = load_config()
    
    # Tìm tất cả file debug_board
    debug_files = sorted(Path('.').glob('debug_board_*.png'))
    
    if not debug_files:
        print("\n❌ Không tìm thấy file debug_board_*.png")
        print("💡 Chạy bot để tạo các file debug trước")
        return
    
    print(f"\n✓ Tìm thấy {len(debug_files)} file debug")
    
    # Test file mới nhất
    latest_file = debug_files[-1]
    test_single_image(str(latest_file), config)
    
    # Hỏi có muốn test thêm không
    if len(debug_files) > 1:
        print("\n" + "="*80)
        print(f"📋 Còn {len(debug_files)-1} file khác. Test tất cả? (y/n): ", end='')
        choice = input().lower()
        
        if choice == 'y':
            for debug_file in debug_files[:-1]:
                test_single_image(str(debug_file), config)
    
    print("\n" + "="*80)
    print("✅ HOÀN THÀNH TEST")
    print("="*80)

if __name__ == "__main__":
    main()
