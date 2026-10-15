# 渲染（第二版起：出镜视频已接入）：python3 render_v1.py align.json 输出目录 [video 段号 段数 | audio | mux]
import sys, os, json, wave, subprocess
import numpy as np
mode = sys.argv[3]
sys.argv = ['timeline.py', sys.argv[1], sys.argv[2]] + sys.argv[4:]
OUT = sys.argv[2]
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timeline.py'), encoding='utf-8').read().split("if __name__ == '__main__':")[0])

if mode == 'video':
    part, nparts = int(sys.argv[3]), int(sys.argv[4])
    shot_by_i, vis = build_vis()
    N = int(round(TOTAL * FPS)); a = N * part // nparts; b = N * (part + 1) // nparts
    wr = Writer(f'{OUT}/v2_part{part}.mp4', FPS, crf=19)
    for n in range(a, b):
        wr.write(frame_at(n / FPS, shot_by_i, vis))
        if (n - a) % 300 == 0: print(f'part{part} {n - a}/{b - a}', flush=True)
    wr.close(); print('done video', part)

if mode == 'audio':
    SR = 44100
    def load(p):
        tmp = f'{OUT}/_src.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-vn', '-ac', '2', '-ar', str(SR), tmp], check=True)
        with wave.open(tmp) as w:
            return np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    RAW = {'vo': load(VO_WAV), 'cam': load(os.path.join(MAT, '口播', '1080-压缩版.mp4'))}
    def speech_rms(src):
        x = np.concatenate([RAW[src][int(a0 * SR):int(a1 * SR)] for a0, a1, o, sr in audio_pieces if sr == src])
        return float(np.sqrt((x ** 2).mean()))
    GAIN = {'vo': 1.0, 'cam': speech_rms('vo') / max(speech_rms('cam'), 1e-6)}     # 出镜声音对齐画外音响度
    print('cam gain', round(GAIN['cam'], 2))
    mix = np.zeros((int((TOTAL + 1) * SR), 2), np.float32)
    for a0, a1, o, sr in audio_pieces:
        seg_ = RAW[sr][int(a0 * SR):int(a1 * SR)].copy() * GAIN[sr]; n = len(seg_)
        fade = np.ones(n, np.float32); k = int(0.03 * SR); fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.linspace(1, 0, k)
        mix[int(o * SR):int(o * SR) + n] += seg_ * fade[:, None]
    rng = np.random.default_rng(1)
    def whoosh(d=0.38):
        n = int(d * SR); x = rng.normal(0, 1, n)
        X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
        X *= np.exp(-((np.log(f + 1) - np.log(1400)) / 0.9) ** 2); y = np.fft.irfft(X, n)
        env = np.sin(np.linspace(0, np.pi, n)) ** 2; y = y * env; return y / (np.abs(y).max() + 1e-9) * 0.22
    def boom(d=1.4):
        n = int(d * SR); tt = np.arange(n) / SR
        fr = 42 + 40 * np.exp(-tt * 8); ph = 2 * np.pi * np.cumsum(fr) / SR
        y = np.sin(ph) * np.exp(-tt * 3.2) + rng.normal(0, 1, n) * np.exp(-tt * 40) * 0.35
        return y / np.abs(y).max() * 0.55
    def tick(d=0.12, f0=1900):
        n = int(d * SR); tt = np.arange(n) / SR; y = np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 45); return y * 0.16
    def add(t0, y):
        i = int(t0 * SR); j = min(len(mix), i + len(y)); mix[i:j] += y[:j - i, None]
    S = {s['i']: s for s in shots}
    for i in WHIP_IN: add(S[i]['start'] - 0.12, whoosh())
    add(S[13]['start'] + 1.45, boom()); add(S[17]['start'] + 1.2, boom()); add(S[36]['start'] + 2.8, boom())
    add(S[36]['start'] + 1.25, boom(0.8) * 0.5); add(S[47]['start'] + 1.0, boom(1.0) * 0.8); add(S[15]['start'], boom(0.9) * 0.7)
    add(S[11]['start'] + 0.35, whoosh(0.5)); add(S[37]['start'] + 0.7, tick(0.2, 1500))
    txt = S[64]['text']
    for w_ in ('提出方案', '调用工具', '模拟计算', '辅助验证'): add(S[64]['chars'][len(nchars(txt[:txt.index(w_)]))][1] - 0.05, tick())
    if 68 in S:
        st = max(0.5, (S[68]['dur'] - 1.0) / 5)
        for k in range(5): add(S[68]['start'] + 0.3 + st * k, tick(0.12, 1700 + 120 * k))
    for i in (49, 50, 62): add(S[i]['start'] + 0.3, tick(0.1, 1200))
    mix = np.clip(mix, -1, 1)
    with wave.open(f'{OUT}/v2_mix_raw.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/v2_mix_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100', f'{OUT}/v2_mix.wav'], check=True)
    print('done audio', TOTAL)
