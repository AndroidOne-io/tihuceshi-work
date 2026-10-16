# 一条命令渲染成片：画面分 N 段并行渲染（按帧号切开）→ 整条混音 → 无损拼接 → 合成 成片.mp4
#
#   cd 科大讯飞/代码
#   python3 render_all.py                 # 默认进程数 = CPU 核数（最多 6）
#   python3 render_all.py 4               # 指定 4 个进程（每个进程约占 2.5 GB 内存）
#   python3 render_all.py 4 30 40         # 只渲染第 30–40 秒（试渲染用）
import os, sys, math, subprocess, time, wave, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
N = int(sys.argv[1]) if len(sys.argv) > 1 else min(os.cpu_count() or 2, 6)
OUT = os.environ.get('KX_RENDER_OUT', os.path.join(HERE, '..', '成片输出'))
os.makedirs(OUT, exist_ok=True)
FPS = 30

# 片长：从时间线算（和 full.py 完全一致）
dur = float(subprocess.run([sys.executable, '-c',
    "import sys; sys.argv=['full.py','align.json','.','none']; __file__='full.py'; exec(open('full.py',encoding='utf-8').read()); print(DUR)"],
    capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1])
a_all, b_all = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0.0, dur)
audio_source = os.environ.get('KX_AUDIO_SOURCE')
if audio_source:
    if (a_all, b_all) != (0.0, dur): sys.exit('复用预览音轨只支持完整导出')
    with wave.open(audio_source) as w:
        if abs(w.getnframes() / w.getframerate() - dur) > 0.5 / FPS:
            sys.exit('预览音轨与当前工程时长不一致')
f0, f1 = int(round(a_all * FPS)), int(round(b_all * FPS))
cuts = [f0 + (f1 - f0) * k // N for k in range(N + 1)]
print(f'片长 {dur:.2f} 秒；渲染 {a_all:.2f}–{b_all:.2f} 秒，共 {f1 - f0} 帧，{N} 个进程')

t0 = time.time(); procs = []
for k in range(N):
    d = os.path.join(OUT, f'_part{k}'); os.makedirs(d, exist_ok=True)
    procs.append(subprocess.Popen([sys.executable, 'full.py', 'align.json', d, 'video', f'{cuts[k] / FPS:.6f}', f'{cuts[k + 1] / FPS:.6f}'],
                                  stdout=open(os.path.join(d, 'log.txt'), 'w'), stderr=subprocess.STDOUT))
for k, p in enumerate(procs):
    if p.wait() != 0: sys.exit(f'第 {k} 段渲染失败（多半是内存不够，减少进程数再试），看 {OUT}/_part{k}/log.txt')
print(f'画面渲染完成，用时 {time.time() - t0:.0f} 秒；准备音轨')
aud = os.path.join(OUT, '_audio'); os.makedirs(aud, exist_ok=True)      # 画面全部渲完再混音，避免同时占内存
if audio_source:
    shutil.copy2(audio_source, os.path.join(aud, 'win_audio.wav'))
    print(f'使用当前预览音轨：{audio_source}')
else:
    subprocess.run([sys.executable, 'full.py', 'align.json', aud, 'audio', f'{a_all:.6f}', f'{b_all:.6f}'], check=True)

lst = os.path.join(OUT, '_list.txt')
with open(lst, 'w', encoding='utf-8') as f:
    for k in range(N): f.write(f"file '{os.path.join(OUT, f'_part{k}', 'win_video.mp4')}'\n")
name = '成片.mp4' if (a_all, b_all) == (0.0, dur) else f'试渲染_{a_all:g}-{b_all:g}.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', os.path.join(aud, 'win_audio.wav'),
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k',
                '-af', f'apad=whole_dur={(f1 - f0) / FPS:.9f}', '-t', f'{(f1 - f0) / FPS:.9f}', '-movflags', '+faststart',
                os.path.join(OUT, name)], check=True)
n = int(subprocess.run(['ffprobe', '-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_packets',
                        '-of', 'csv=p=0', os.path.join(OUT, name)], capture_output=True, text=True).stdout.strip() or 0)
print(f'完成：{os.path.join(OUT, name)}（{n} 帧，应为 {f1 - f0} 帧）')
if n != f1 - f0: sys.exit('成片帧数不匹配，请检查合成结果')
