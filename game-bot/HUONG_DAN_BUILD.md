# 📦 HƯỚNG DẪN BUILD PHẦN MỀM MATCH-3 AUTO BOT

## 🎯 Các bước build file .exe

### Bước 1: Cài đặt PyInstaller (nếu chưa có)
```bash
pip install -r requirements_build.txt
```

### Bước 2: Chạy file build
Chỉ cần double-click vào file:
```
build.bat
```

Hoặc chạy trong terminal:
```bash
build.bat
```

### Bước 3: Lấy file .exe
Sau khi build xong, file .exe sẽ nằm trong thư mục:
```
dist\Match3-AutoBot.exe
```

## 📋 Các file cần đi kèm khi phân phối

Khi chia sẻ phần mềm cho người khác, cần đóng gói các file sau:

```
📁 Match3-AutoBot/
  ├── 📄 Match3-AutoBot.exe       (File chính - từ thư mục dist)
  ├── 📄 config.yaml              (File cấu hình)
  └── 📁 assets/                  (Thư mục assets nếu có icon/templates)
```

## ⚠️ LỖI THƯỜNG GẶP VÀ CÁCH SỬA

### 1. Thiếu DLL khi chạy trên máy khác
**Triệu chứng:** Lỗi "VCRUNTIME140.dll was not found"

**Giải pháp:** 
- Cài đặt Microsoft Visual C++ Redistributable
- Link tải: https://aka.ms/vs/17/release/vc_redist.x64.exe

### 2. Lỗi Tesseract OCR
**Triệu chứng:** Bot không thể đọc text từ game

**Giải pháp:**
1. Tải và cài Tesseract-OCR: https://github.com/UB-Mannheim/tesseract/wiki
2. Thêm đường dẫn Tesseract vào `config.yaml`:
```yaml
game_automation:
  tesseract_path: "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

### 3. File .exe quá lớn
**Giải pháp:** Đã dùng `--onefile` để gộp tất cả vào 1 file, nhưng vẫn có thể giảm size bằng:
- Xóa các module không dùng trong code
- Dùng `upx=True` để nén (đã bật sẵn)

### 4. Antivirus báo virus
**Lý do:** PyInstaller exe thường bị false positive

**Giải pháp:**
- Thêm exception trong antivirus
- Hoặc ký (code signing) file .exe

## 🚀 CHẠY TRÊN MÁY KHÁC

Người dùng chỉ cần:
1. Giải nén folder Match3-AutoBot
2. Double-click `Match3-AutoBot.exe`
3. Làm theo hướng dẫn trong GUI để calibrate vùng game

**KHÔNG CẦN** cài đặt:
- ❌ Python
- ❌ pip packages
- ❌ Visual Studio Code

**CẦN CÓ** (thường đã có sẵn trên Windows):
- ✅ Windows 10/11
- ✅ Microsoft Visual C++ Redistributable (nếu thiếu thì tải)
- ✅ Tesseract OCR (nếu dùng tính năng auto-click nút)

## 📝 Ghi chú

- File build.bat đã tự động kiểm tra và cài PyInstaller nếu thiếu
- Config.yaml được nhúng vào .exe, khi chạy lần đầu sẽ tạo file config.yaml riêng
- Debug mode đã tắt trong build để giảm kích thước và tăng tốc độ
