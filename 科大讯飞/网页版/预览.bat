@echo off
REM Windows：双击预览（关掉这个窗口就停止）
cd /d "%~dp0"
python serve.py
pause
