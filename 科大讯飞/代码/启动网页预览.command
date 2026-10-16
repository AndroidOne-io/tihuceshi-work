#!/bin/zsh
set -e
cd -- "$(dirname -- "$0")"
if curl --max-time 2 -fsS http://127.0.0.1:8776/metadata >/dev/null 2>&1; then
    open http://127.0.0.1:8776
    exit 0
fi
if [[ -n "${KX_PYTHON:-}" ]]; then
    preview_python="$KX_PYTHON"
elif [[ -x ../../.venv/bin/python ]]; then
    preview_python="../../.venv/bin/python"
elif [[ -x ../../../.venv-render/bin/python ]]; then
    preview_python="../../../.venv-render/bin/python"
else
    preview_python="python3"
fi
# 新机器第一次启动时，先生成必要的预览音轨。
if [[ ! -f ../成片输出/节奏声音调整/win_audio.wav ]]; then
    exec "$preview_python" preview_server.py --port 8776 --prepare-audio
else
    exec "$preview_python" preview_server.py --port 8776
fi
