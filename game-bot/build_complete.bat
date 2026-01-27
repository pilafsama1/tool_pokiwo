@echo off
chcp 65001 >nul
echo ============================================================
echo 🎁 BUILD COMPLETE PACKAGE - MATCH-3 AUTO BOT
echo ============================================================
echo.
echo Tạo package hoàn chỉnh, KHÔNG CẦN cài thêm gì!
echo.

REM Bước 0: Tải file ngôn ngữ tiếng Việt
echo ============================================================
echo 📥 BƯỚC 0: TẢI FILE NGÔN NGỮ TIẾNG VIỆT
echo ============================================================
echo.

if not exist "bundle\tesseract\tessdata\vie.traineddata" (
    echo Đang tải file vie.traineddata...
    py download_vie_lang.py
    echo.
)

if exist "bundle\tesseract\tessdata\vie.traineddata" (
    echo ✓ File ngôn ngữ tiếng Việt đã sẵn sàng
) else (
    echo ⚠️  Không có file vie.traineddata - OCR có thể không hoạt động tốt
    timeout /t 3
)

echo.

REM Kiểm tra Tesseract đã được bundle chưa
if not exist "bundle\tesseract\tesseract.exe" (
    echo ⚠️  Chưa có Tesseract trong bundle!
    echo.
    echo Vui lòng chọn một trong hai cách:
    echo.
    echo [1] Bundle Tesseract (đầy đủ nhất - KHUYẾN NGHỊ)
    echo [2] Build không có Tesseract (tính năng auto-click nút sẽ không dùng được)
    echo.
    choice /C 12 /N /M "Chọn (1 hoặc 2): "
    
    if errorlevel 2 goto BUILD_WITHOUT_TESSERACT
    if errorlevel 1 goto BUNDLE_TESSERACT
)

:BUILD_WITH_TESSERACT
echo.
echo ✓ Đã có Tesseract trong bundle
goto BUILD

:BUNDLE_TESSERACT
echo.
echo ============================================================
echo 📦 BUNDLE TESSERACT OCR
echo ============================================================
echo.
echo Nhập đường dẫn Tesseract đã cài trên máy bạn:
echo (Ví dụ: C:\Program Files\Tesseract-OCR)
echo.
set /p TESS_PATH="Đường dẫn: "

if not exist "%TESS_PATH%\tesseract.exe" (
    echo.
    echo ❌ Không tìm thấy tesseract.exe tại: %TESS_PATH%
    echo.
    echo Hãy cài Tesseract trước:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    pause
    exit /b 1
)

echo.
echo 📋 Đang copy Tesseract files...
py setup_tesseract.py --copy-from "%TESS_PATH%"
echo.

if not exist "bundle\tesseract\tesseract.exe" (
    echo ❌ Copy thất bại!
    pause
    exit /b 1
)

goto BUILD

:BUILD_WITHOUT_TESSERACT
echo.
echo ⚠️  Build không có Tesseract - Tính năng auto-click nút sẽ BỊ TẮT
echo.
timeout /t 3

:BUILD
echo.
echo ============================================================
echo 🔨 BUILD EXECUTABLE
echo ============================================================
echo.

REM Xóa thư mục build/dist cũ
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"

REM Build với PyInstaller
py -m PyInstaller --name "Match3-AutoBot" ^
    --onefile ^
    --windowed ^
    --add-data "config.yaml;." ^
    --add-data "assets;assets" ^
    --add-data "bundle;bundle" ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    --hidden-import=mss ^
    --hidden-import=mss.windows ^
    --hidden-import=pyautogui ^
    --hidden-import=keyboard ^
    --hidden-import=PIL ^
    --hidden-import=pytesseract ^
    --hidden-import=yaml ^
    gui_main.py

if errorlevel 1 (
    echo.
    echo ❌ Build thất bại!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 📦 TẠO PACKAGE HOÀN CHỈNH
echo ============================================================
echo.

REM Tạo thư mục release
set RELEASE_DIR=Match3-AutoBot-Release
if exist "%RELEASE_DIR%" rd /s /q "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%"

REM Copy file .exe
copy "dist\Match3-AutoBot.exe" "%RELEASE_DIR%\"
echo ✓ Copied Match3-AutoBot.exe

REM Copy config mẫu
copy "config.yaml" "%RELEASE_DIR%\"
echo ✓ Copied config.yaml

REM Copy assets
if exist "assets" (
    xcopy /E /I /Q "assets" "%RELEASE_DIR%\assets"
    echo ✓ Copied assets\
)

REM Copy Tesseract nếu có
if exist "bundle\tesseract" (
    xcopy /E /I /Q "bundle\tesseract" "%RELEASE_DIR%\tesseract"
    echo ✓ Copied tesseract\
    
    REM Đảm bảo có file vie.traineddata
    if exist "bundle\tesseract\tessdata\vie.traineddata" (
        echo ✓ Bao gồm file ngôn ngữ tiếng Việt
    ) else (
        echo ⚠️ Thiếu file vie.traineddata
    )
)

REM Tạo README cho user
echo # 🎮 MATCH-3 AUTO BOT > "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo CACH SU DUNG: >> "%RELEASE_DIR%\README.txt"
echo 1. Double-click Match3-AutoBot.exe >> "%RELEASE_DIR%\README.txt"
echo 2. Lam theo huong dan tren giao dien >> "%RELEASE_DIR%\README.txt"
echo 3. Choi game! >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"
echo KHONG CAN CAI DAT THEM GI! >> "%RELEASE_DIR%\README.txt"
echo. >> "%RELEASE_DIR%\README.txt"

if exist "README_CHO_NGUOI_DUNG.md" (
    copy "README_CHO_NGUOI_DUNG.md" "%RELEASE_DIR%\HUONG_DAN.md"
    echo ✓ Copied HUONG_DAN.md
)

echo.
echo ============================================================
echo ✅ HOÀN THÀNH!
echo ============================================================
echo.
echo 📁 Package đã sẵn sàng tại: %RELEASE_DIR%\
echo.
echo 📋 Nội dung:
dir /B "%RELEASE_DIR%"
echo.
echo 🎁 Nén thư mục '%RELEASE_DIR%' thành .zip và gửi cho người khác!
echo.
echo 💡 Người dùng CHỈ CẦN:
echo    - Giải nén
echo    - Chạy Match3-AutoBot.exe
echo    - KHÔNG cần cài thêm gì!
echo.
pause
