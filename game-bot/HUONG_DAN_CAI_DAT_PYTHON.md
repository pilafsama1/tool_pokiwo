# 🐍 HƯỚNG DẪN CÀI ĐẶT PYTHON ĐỂ BUILD

## ⚠️ Vấn đề hiện tại

Bạn đang gặp lỗi: `Python tìm thấy` - đây là Windows Store stub, KHÔNG phải Python thật.

## ✅ GIẢI PHÁP: Cài đặt Python chính thức

### Cách 1: Tải từ Python.org (Khuyến nghị)

1. **Tải Python:**
   - Truy cập: https://www.python.org/downloads/
   - Tải phiên bản mới nhất (Python 3.11 hoặc 3.12)

2. **Cài đặt Python:**
   - ✅ **QUAN TRỌNG:** Tick vào "Add Python to PATH"
   - Chọn "Install Now"
   - Chờ cài đặt hoàn tất

3. **Kiểm tra lại:**
   Mở PowerShell MỚI và chạy:
   ```powershell
   python --version
   pip --version
   ```
   
   Nếu thấy version number (như `Python 3.12.0`) là OK!

### Cách 2: Vô hiệu hóa Windows Store Python

Nếu không muốn cài lại:

1. Mở **Settings** → **Apps** → **Apps & features**
2. Tìm "App execution aliases"
3. Tắt (OFF) cả:
   - ❌ App Installer python.exe
   - ❌ App Installer python3.exe

Sau đó cài Python từ python.org như Cách 1.

## 🚀 SAU KHI CÀI PYTHON

### Bước 1: Mở PowerShell MỚI (để load PATH mới)

### Bước 2: Cài đặt dependencies
```powershell
cd "d:\slim\Tool game\toolautopokiwo\game-bot"
pip install -r requirements.txt
pip install pyinstaller
```

### Bước 3: Chạy build
```powershell
.\build.bat
```

## 🎯 Kiểm tra Python đã đúng chưa

Chạy lệnh này:
```powershell
python -c "import sys; print(sys.executable)"
```

Kết quả ĐÚNG sẽ là:
```
C:\Users\[TenBan]\AppData\Local\Programs\Python\Python3xx\python.exe
```

Kết quả SAI (Windows Store stub):
```
C:\Users\[TenBan]\AppData\Local\Microsoft\WindowsApps\python.exe
```

## 📋 Checklist

- [ ] Tải Python từ python.org
- [ ] Tick "Add Python to PATH" khi cài
- [ ] Mở PowerShell MỚI
- [ ] Chạy `python --version` thấy version number
- [ ] Chạy `pip --version` thấy version number
- [ ] Cài dependencies: `pip install -r requirements.txt`
- [ ] Cài PyInstaller: `pip install pyinstaller`
- [ ] Chạy `.\build.bat`
- [ ] Kiểm tra file .exe trong thư mục `dist\`

## ❓ Vẫn gặp lỗi?

Nếu sau khi cài Python vẫn không chạy được:

1. Restart máy (để Windows load PATH mới)
2. Chạy PowerShell **AS ADMINISTRATOR**
3. Thử lại từ đầu

---

💡 **Lưu ý:** Sau khi build xong file .exe, máy KHÁC không cần cài Python nữa!
