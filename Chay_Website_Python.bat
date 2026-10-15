@echo off
title Green Corner - Kho Cây Cảnh Sinh Thái 2026
chcp 65001 > nul
echo =========================================================================
echo   🌿 GREEN CORNER - HỆ THỐNG WEBSITE CÂY CẢNH SINH THÁI CAO CẤP
echo   Backend: Python (Flask + SQLAlchemy)  ^|  Frontend: HTML5 + CSS3 + JS
echo =========================================================================
echo.
echo [*] Đang khởi động máy chủ tại: http://127.0.0.1:5000
echo [*] Tài khoản Quản trị: admin@greencorner.vn / admin123
echo [*] Tài khoản Khách:    customer@gmail.com / 123456
echo.
cd /d "%~dp0GreenCornerPython"
if exist "..\.venv\Scripts\python.exe" (
    "..\.venv\Scripts\python.exe" run.py
) else (
    python run.py
)
pause
