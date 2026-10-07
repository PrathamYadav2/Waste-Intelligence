@echo off
echo =======================================================
echo   PUSHING TO GITHUB (Waste-Intelligence)
echo =======================================================
echo.
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo =======================================================
    echo   SUCCESS! Pura code GitHub par upload ho gaya hai.
    echo   Ab vercel.com par jakar 'Import' karein.
    echo =======================================================
) else (
    echo [NOTE] Agar GitHub login popup aaye toh browser me authorize karein.
)
pause
