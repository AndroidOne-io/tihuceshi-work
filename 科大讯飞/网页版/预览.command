#!/bin/bash
# Mac：双击这个文件就能预览（会自动用浏览器打开；关掉这个终端窗口就停止）
cd "$(dirname "$0")"
python3 serve.py
