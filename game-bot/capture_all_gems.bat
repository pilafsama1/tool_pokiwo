@echo off
chcp 65001 >nul
echo ============================================================
echo 🎯 CHỤP TẤT CẢ GEM TEMPLATES
echo ============================================================
echo.
echo Bạn sẽ chụp 6 loại gem theo thứ tự:
echo   1. BLUE_LIGHTNING (Tia chớp xanh)
echo   2. GREEN_HEART (Trái tim xanh lá)
echo   3. ORANGE_SUN (Mặt trời cam)
echo   4. PURPLE_MOON (Mặt trăng tím)
echo   5. RED_FIRE (Lửa đỏ)
echo   6. YELLOW_STAR (Ngôi sao vàng)
echo.
echo ⚠️  Đảm bảo game đã mở và bàn cờ hiện rõ!
echo.
pause

set PYTHON="C:\Users\tranv\AppData\Local\Programs\Python\Python314\python.exe"

echo.
echo ============================================================
%PYTHON% capture_gem.py BLUE_LIGHTNING
echo.

echo ============================================================
%PYTHON% capture_gem.py GREEN_HEART
echo.

echo ============================================================
%PYTHON% capture_gem.py ORANGE_SUN
echo.

echo ============================================================
%PYTHON% capture_gem.py PURPLE_MOON
echo.

echo ============================================================
%PYTHON% capture_gem.py RED_FIRE
echo.

echo ============================================================
%PYTHON% capture_gem.py YELLOW_STAR
echo.

echo ============================================================
echo ✅ HOÀN THÀNH! Đã chụp xong tất cả templates.
echo ============================================================
pause
