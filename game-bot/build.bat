@echo off
chcp 65001 >nul
echo ============================================================
echo 🔨 BUILD MATCH-3 AUTO BOT
echo ============================================================
echo.

REM Check if PyInstaller is installed
py -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 📦 Đang cài đặt PyInstaller...
    py -m pip install pyinstaller keyboard
    echo.
)

echo 🔨 Đang build phần mềm...
echo.

REM Build executable
py -m PyInstaller --name "Match3-AutoBot" ^
    --onefile ^
    --windowed ^
    --add-data "config.yaml;." ^
    --add-data "assets;assets" ^
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

echo.
echo ============================================================
echo ✅ BUILD HOÀN THÀNH!
echo ============================================================
echo.
echo 📁 File .exe nằm trong thư mục: dist\Match3-AutoBot.exe
echo.
pause
