#!/usr/bin/env python3
# 网页版 → 成片 mp4（逐帧精确导出：每一帧都等视频跳到位再截，和网页里看到的一模一样）
#
#   python3 科大讯飞/网页版/tools/export_mp4.py                 # 整条，默认 4 个并行，出 科大讯飞/成片输出/网页版成片.mp4
#   python3 科大讯飞/网页版/tools/export_mp4.py --jobs 6        # 并行数（每个占一个浏览器，内存 16G 的 Mac 建议 4–6）
#   python3 科大讯飞/网页版/tools/export_mp4.py --from 100 --to 130   # 只导一段试看（成片时间，秒）
#   python3 科大讯飞/网页版/tools/export_mp4.py --small         # 另外压一个 < 30MB 的交付版
#
# 第一次用要装：pip3 install playwright ；本机装了 Google Chrome 就行（脚本用系统 Chrome，因为它能解 H.264）。
# 没装 Chrome 的话：python3 -m playwright install chromium，并先跑 bash 科大讯飞/网页版/_proxy/make.sh 生成 webm 代理素材。
import sys, os, time, json, base64, argparse, subprocess, threading, http.server, urllib.parse, shutil

HERE = os.path.dirname(os.path.abspath(__file__)); WEB = os.path.dirname(HERE); ROOT = os.path.abspath(os.path.join(WEB, '..', '..'))
ap = argparse.ArgumentParser()
ap.add_argument('--jobs', type=int, default=4); ap.add_argument('--fps', type=float, default=0)
ap.add_argument('--from', dest='a', type=float, default=0.0); ap.add_argument('--to', dest='b', type=float, default=-1)
ap.add_argument('--out', default=''); ap.add_argument('--small', action='store_true'); ap.add_argument('--crf', type=int, default=18)
ap.add_argument('--part', nargs=3, help=argparse.SUPPRESS)          # 内部用：--part 起始帧 结束帧 输出文件
args = ap.parse_args()

def read_D():
    s = open(os.path.join(WEB, 'data.js'), encoding='utf-8').read(); return json.loads(s[s.index('{'):s.rindex('}') + 1])

# ---------------------------------------------------------------- 子进程：渲一段帧，直接喂给 ffmpeg
def render_part(f0, f1, out, fps):
    src = open(os.path.join(WEB, 'serve.py'), encoding='utf-8').read().split('H.extensions_map')[0]
    argv = sys.argv; sys.argv = ['serve.py']; ns = {'__file__': os.path.join(WEB, 'serve.py')}; exec(src, ns); sys.argv = argv
    Hh = ns['H']; Hh.extensions_map.update({'.js': 'text/javascript', '.mp4': 'video/mp4', '.webm': 'video/webm', '.m4a': 'audio/mp4', '.ttf': 'font/ttf'})
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Hh); threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{srv.server_address[1]}/' + urllib.parse.quote('科大讯飞/网页版/index.html')
    from playwright.sync_api import sync_playwright
    has_proxy = os.path.exists(os.path.join(WEB, '_proxy', 'cam.webm'))
    with sync_playwright() as p:
        A = ['--autoplay-policy=no-user-gesture-required']
        try: b = p.chromium.launch(channel='chrome', args=A)
        except Exception: b = p.chromium.launch(args=A)
        pg = b.new_page(viewport={'width': 1920, 'height': 1200})
        pg.goto(base); pg.wait_for_function('window.READY === true', timeout=300000)
        bad = pg.evaluate('E.probeVideos()')            # 这个浏览器能不能解原始 mp4（H.264）
        if bad:
            if not has_proxy:
                sys.exit(f'浏览器解不了这些视频：{bad}。请安装 Google Chrome（自带 H.264），或先跑 bash 科大讯飞/网页版/_proxy/make.sh 生成 webm 代理素材。')
            print(f'  浏览器解不了原始 mp4（{bad}），改用 _proxy 里的 webm', flush=True)
            pg.goto(base + '?proxy'); pg.wait_for_function('window.READY === true', timeout=300000)
            bad = pg.evaluate('E.probeVideos()')
            if bad: sys.exit(f'webm 代理也读不了：{bad}')
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', f'{fps}', '-c:v', 'mjpeg', '-i', '-',
                               '-c:v', 'libx264', '-preset', 'medium', '-crf', str(args.crf), '-pix_fmt', 'yuv420p', '-r', f'{fps}', out], stdin=subprocess.PIPE)
        t0 = time.time()
        for n in range(f0, f1):
            data = pg.evaluate(f"(async () => {{ await window.renderAt({n / fps}); return document.getElementById('c').toDataURL('image/jpeg', 0.95); }})()")
            ff.stdin.write(base64.b64decode(data.split(',', 1)[1]))
            k = n - f0 + 1
            if k % 60 == 0 or n == f1 - 1:
                el = time.time() - t0; print(f'  [{os.path.basename(out)}] {k}/{f1 - f0} 帧，还要约 {el / k * (f1 - f0 - k) / 60:.1f} 分钟', flush=True)
        ff.stdin.close(); ff.wait(); b.close()
    if ff.returncode != 0: sys.exit('ffmpeg 出错')

D = read_D(); FPS = args.fps or D['FPS']
if args.part:
    render_part(int(args.part[0]), int(args.part[1]), args.part[2], FPS); sys.exit(0)

# ---------------------------------------------------------------- 主进程：切段 → 并行 → 拼接 + 混好的音轨
a = max(0.0, args.a); b = D['DUR'] if args.b < 0 else min(args.b, D['DUR'])
f0, f1 = int(round(a * FPS)), int(round(b * FPS))
OUTD = os.path.join(ROOT, '科大讯飞', '成片输出'); os.makedirs(OUTD, exist_ok=True)
name = args.out or os.path.join(OUTD, '网页版成片.mp4' if (f0 == 0 and b >= D['DUR'] - 1e-6) else f'网页版试导_{a:g}-{b:g}.mp4')
tmp = os.path.join(OUTD, '_web_parts'); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
J = max(1, min(args.jobs, (f1 - f0) // 30 or 1)); cuts = [f0 + (f1 - f0) * k // J for k in range(J + 1)]
print(f'导出 {a:.2f}–{b:.2f} 秒，共 {f1 - f0} 帧，{J} 个并行')
t0 = time.time()
procs = [subprocess.Popen([sys.executable, __file__, '--fps', str(FPS), '--crf', str(args.crf), '--part', str(cuts[k]), str(cuts[k + 1]), os.path.join(tmp, f'p{k:02d}.mp4')])
         for k in range(J)]
for k, p in enumerate(procs):
    if p.wait() != 0: sys.exit(f'第 {k} 段失败（内存不够就减少 --jobs）')
lst = os.path.join(tmp, 'list.txt')
open(lst, 'w', encoding='utf-8').write(''.join(f"file '{os.path.join(tmp, f'p{k:02d}.mp4')}'\n" for k in range(J)))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-ss', f'{a}', '-t', f'{b - a}', '-i', os.path.join(WEB, 'mix.m4a'),
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', name], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print(f'完成：{name}（用时 {(time.time() - t0) / 60:.1f} 分钟）')

if args.small:                                   # 交付版：两遍编码压到 ~28MB
    dur = b - a; vk = max(300, int(28 * 8 * 1024 / dur - 128))
    small = name.replace('.mp4', '_交付版.mp4'); pl = os.path.join(OUTD, '_2pass')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', name, '-c:v', 'libx264', '-preset', 'slow', '-b:v', f'{vk}k', '-pass', '1', '-passlogfile', pl, '-an', '-f', 'mp4', os.devnull], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', name, '-c:v', 'libx264', '-preset', 'slow', '-b:v', f'{vk}k', '-pass', '2', '-passlogfile', pl,
                    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', small], check=True)
    for f in os.listdir(OUTD):
        if f.startswith('_2pass'): os.remove(os.path.join(OUTD, f))
    print(f'交付版：{small}（{os.path.getsize(small) / 1e6:.1f} MB）')
