"""
Script để tải và setup Tesseract OCR cho bundle
"""
import urllib.request
import zipfile
import os
import shutil
from pathlib import Path

TESSERACT_URL = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
TESSERACT_PORTABLE_URL = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3/tesseract-ocr-w64-setup-5.3.3.20231005.exe"

def setup_tesseract_bundle():
    """
    Tạo thư mục tesseract portable để bundle vào package
    """
    print("📦 Đang chuẩn bị Tesseract OCR để bundle...")
    
    bundle_dir = Path("bundle")
    tesseract_dir = bundle_dir / "tesseract"
    
    # Tạo thư mục
    tesseract_dir.mkdir(parents=True, exist_ok=True)
    
    print("""
    ⚠️ HƯỚNG DẪN THỦ CÔNG:
    
    Để bundle Tesseract OCR hoàn chỉnh:
    
    1. Tải Tesseract tại:
       https://github.com/UB-Mannheim/tesseract/wiki
       
    2. Cài đặt Tesseract vào máy (ví dụ: C:\\Program Files\\Tesseract-OCR)
    
    3. Copy các file sau vào thư mục bundle/tesseract/:
       - tesseract.exe
       - Thư mục tessdata/ (chứa file vie.traineddata)
       - Các file .dll cần thiết
    
    4. Chạy lại build.bat
    
    Hoặc nếu đã cài Tesseract, chạy lệnh:
    python setup_tesseract.py --copy-from "C:\\Program Files\\Tesseract-OCR"
    """)
    
    return tesseract_dir

def copy_tesseract_files(source_path: str):
    """
    Copy Tesseract files từ system installation
    """
    source = Path(source_path)
    if not source.exists():
        print(f"❌ Không tìm thấy Tesseract tại: {source}")
        return False
    
    bundle_dir = Path("bundle/tesseract")
    bundle_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📋 Copy từ: {source}")
    print(f"📋 Đến: {bundle_dir}")
    
    # Copy tesseract.exe
    if (source / "tesseract.exe").exists():
        shutil.copy2(source / "tesseract.exe", bundle_dir / "tesseract.exe")
        print("✓ Copied tesseract.exe")
    
    # Copy tessdata
    if (source / "tessdata").exists():
        if (bundle_dir / "tessdata").exists():
            shutil.rmtree(bundle_dir / "tessdata")
        shutil.copytree(source / "tessdata", bundle_dir / "tessdata")
        print("✓ Copied tessdata/")
    
    # Copy DLLs
    dll_files = list(source.glob("*.dll"))
    for dll in dll_files:
        shutil.copy2(dll, bundle_dir / dll.name)
        print(f"✓ Copied {dll.name}")
    
    print("\n✅ Tesseract đã được bundle thành công!")
    print(f"📁 Thư mục: {bundle_dir.absolute()}")
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2 and sys.argv[1] == "--copy-from":
        copy_tesseract_files(sys.argv[2])
    else:
        setup_tesseract_bundle()
