"""工程内按需预览，不编码视频。运行：python preview_server.py"""
import argparse
from collections import OrderedDict
import gc
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import runpy
import sys
import subprocess
import threading
from urllib.parse import parse_qs, urlparse
import wave

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / '成片输出' / '网页预览'
AUDIO = HERE.parent / '成片输出' / '节奏声音调整' / 'win_audio.wav'
LOCK = threading.RLock()
CACHE = OrderedDict()
ENGINE = None
REVISION = 0
PREVIEW_FPS = 24


def load_engine():
    global ENGINE, REVISION
    with LOCK:
        # 工程模块重新读取，字幕、构图和动画改动无需导出即可加载。
        ENGINE = None
        for name, module in list(sys.modules.items()):
            filename = getattr(module, '__file__', None)
            if filename and Path(filename).resolve().parent == HERE and name != '__main__':
                del sys.modules[name]
        gc.collect()
        argv = sys.argv[:]
        try:
            sys.argv = ['full.py', 'align.json', str(OUT), 'none']
            ENGINE = runpy.run_path(str(HERE / 'full.py'), run_name='preview_engine')
        finally:
            sys.argv = argv
        CACHE.clear()
        REVISION += 1


def metadata():
    with LOCK:
        duration = ENGINE['DUR']
        ready = False
        if AUDIO.exists():
            try:
                with wave.open(str(AUDIO)) as w:
                    ready = abs(w.getnframes() / w.getframerate() - duration) < .05
            except (EOFError, wave.Error):
                pass
        return dict(duration=duration, fps=PREVIEW_FPS, source_fps=ENGINE['FPS'], audio_ready=ready,
                    revision=REVISION, audio_stamp=AUDIO.stat().st_mtime_ns if ready else 0,
                    markers=[dict(label=label, time=max(0, time + ENGINE['PRE'])) for label, time in [
                        ('开场节奏', 0), ('OpenAI 词头', ENGINE['S'][2]['start']),
                        ('研究成果', ENGINE['wt'](3, '研究成果') - .6),
                        ('片名与换曲', ENGINE['EV']['afs'] - 3.5),
                        ('化工章节', ENGINE['EV']['ch_in'] - .8),
                        ('死亡之谷换曲', ENGINE['EV']['valley'] - .8),
                        ('复杂化工', ENGINE['S'][48]['start']),
                        ('生物章节换曲', ENGINE['EV']['ch2_in'] - 1),
                        ('总结换曲', ENGINE['EV']['cut61'] - 1),
                        ('结尾收束', ENGINE['DUR'] - ENGINE['PRE'] - 4)]])


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_data(self, data, content_type, status=200):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        # 只允许当前本地页面发起重新加载。
        if self.headers.get('Origin') not in (None, f'http://{self.headers.get("Host")}'):
            self.send_error(403)
            return
        if self.path != '/reload':
            self.send_error(404)
            return
        try:
            load_engine()
            self.send_data(json.dumps(metadata()).encode(), 'application/json')
        except Exception as exc:
            self.send_data(str(exc).encode(), 'text/plain; charset=utf-8', 500)

    def do_GET(self):
        url = urlparse(self.path)
        try:
            if url.path == '/':
                self.send_data((HERE / 'preview.html').read_bytes(), 'text/html; charset=utf-8')
            elif url.path == '/metadata':
                self.send_data(json.dumps(metadata()).encode(), 'application/json')
            elif url.path == '/frame':
                params = parse_qs(url.query)
                t = float(params.get('t', ['0'])[0])
                if not np.isfinite(t):
                    raise ValueError('时间必须是有限数字')
                still = params.get('still', ['0'])[0] == '1'
                with LOCK:
                    n = max(0, min(round(t * PREVIEW_FPS), round(ENGINE['DUR'] * PREVIEW_FPS) - 1))
                    key = (n, still)
                    if key not in CACHE:
                        frame = ENGINE['frame'](n / PREVIEW_FPS)
                        im = Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8))
                        if not still:
                            im = im.resize((960, 540), Image.Resampling.LANCZOS)
                        buf = io.BytesIO()
                        im.save(buf, format='PNG' if still else 'JPEG', **({} if still else {'quality': 88}))
                        CACHE[key] = buf.getvalue()
                        if len(CACHE) > 24:
                            CACHE.popitem(last=False)
                    data = CACHE[key]
                    CACHE.move_to_end(key)
                self.send_data(data, 'image/png' if still else 'image/jpeg')
            elif url.path == '/audio':
                self.serve_audio()
            else:
                self.send_error(404)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as exc:
            self.send_data(str(exc).encode(), 'text/plain; charset=utf-8', 500)

    def serve_audio(self):
        if not metadata()['audio_ready']:
            self.send_error(503, 'Audio is not ready')
            return
        size = AUDIO.stat().st_size
        start, end = 0, size - 1
        range_header = self.headers.get('Range')
        if range_header:
            try:
                unit, interval = range_header.split('=', 1)
                left, right = interval.split('-', 1)
                if unit != 'bytes' or ',' in interval:
                    raise ValueError()
                if left:
                    start = int(left)
                    end = min(int(right), size - 1) if right else size - 1
                else:
                    start = max(0, size - int(right))
                if not 0 <= start <= end < size:
                    raise ValueError()
            except ValueError:
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{size}')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
        self.send_response(206 if range_header else 200)
        self.send_header('Content-Type', 'audio/wav')
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1))
        if range_header:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        with AUDIO.open('rb') as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining:
                chunk = f.read(min(65536, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8776)
    parser.add_argument('--prepare-audio', action='store_true', help='启动时重新生成工程预览混音，不导出视频')
    args = parser.parse_args()
    os.chdir(HERE)
    OUT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print('正在载入工程…', flush=True)
    load_engine()
    if args.prepare_audio:
        AUDIO.parent.mkdir(parents=True, exist_ok=True)
        print('正在更新预览混音…', flush=True)
        subprocess.run([sys.executable, str(HERE / 'full.py'), str(HERE / 'align.json'), str(AUDIO.parent), 'audio'], check=True)
        for name in ('_t.wav', 'full_raw.wav', 'full_audio.wav'):
            (AUDIO.parent / name).unlink(missing_ok=True)
    print(f'网页预览：http://127.0.0.1:{args.port}', flush=True)
    server.serve_forever()
