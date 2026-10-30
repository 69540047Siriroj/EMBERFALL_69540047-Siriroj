@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    py -3 -X utf8 launch.py desktop
) else (
    python -X utf8 launch.py desktop
)
echo.
echo If Python was not found, install Python first.
echo Keep this window open while playing the website.
pause
