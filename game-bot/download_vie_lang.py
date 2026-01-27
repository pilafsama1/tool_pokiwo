"""
Script tải file ngôn ngữ tiếng Việt cho Tesseract OCR
"""
import urllib.request
import os
from pathlib import Path

VIE_TRAINEDDATA_URL = "https://github.com/tesseract-ocr/tessdata/raw/main/vie.traineddata"

def download_vie_traineddata():
    """
    Tải file vie.traineddata từ GitHub
    """
    print("📥 Đang tải file ngôn ngữ tiếng Việt cho Tesseract...")
    
    # Tạo thư mục tessdata trong bundle
    tessdata_dir = Path("bundle/tesseract/tessdata")
    tessdata_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = tessdata_dir / "vie.traineddata"
    
    # Kiểm tra đã có chưa
    if output_file.exists():
        print(f"✓ File đã tồn tại: {output_file}")
        return True
    
    try:
        print(f"   URL: {VIE_TRAINEDDATA_URL}")
        print(f"   Đích: {output_file}")
        
        # Tải file
        urllib.request.urlretrieve(VIE_TRAINEDDATA_URL, output_file)
        
        # Kiểm tra file size
        file_size = output_file.stat().st_size / (1024 * 1024)  # MB
        print(f"✓ Tải thành công! Size: {file_size:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi tải: {e}")
        print("\n⚠️ Giải pháp thay thế:")
        print("1. Tải thủ công tại:")
        print(f"   {VIE_TRAINEDDATA_URL}")
        print("2. Lưu vào:")
        print(f"   {output_file.absolute()}")
        return False

if __name__ == "__main__":
    success = download_vie_traineddata()
    
    if success:
        print("\n✅ Hoàn tất! Bạn có thể chạy build_complete.bat để build package.")
    else:
        print("\n❌ Không thể tải tự động. Vui lòng tải thủ công.")
    
    input("\nNhấn ENTER để đóng...")
