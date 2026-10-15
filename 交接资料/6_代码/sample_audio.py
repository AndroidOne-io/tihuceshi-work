import json, subprocess, numpy as np
from scipy import signal
SR = 48000; rng = np.random.default_rng(4)
EV = json.load(open('/tmp/claude-0/mock/ev.json')); END = EV['end']; P0, PD = EV['pause']
N = int(END * SR) + SR
def load(p, ss=0, t=None):
    cmd = ['ffmpeg', '-loglevel', 'error', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', p, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
def lufs(x):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'ebur128', '-f', 'null', '-'], input=x.astype(np.float32).tobytes(), capture_output=True)
    for ln in p.stderr.decode().splitlines()[::-1]:
        if ln.strip().startswith('I:'): return float(ln.split()[1])
def tt(d): return np.arange(int(d * SR)) / SR
def bp(x, lo, hi): b, a = signal.butter(2, [lo / (SR / 2), min(hi / (SR / 2), .99)], 'band'); return signal.lfilter(b, a, x)
def lp(x, f): b, a = signal.butter(2, f / (SR / 2)); return signal.lfilter(b, a, x)
def hp(x, f): b, a = signal.butter(2, f / (SR / 2), 'high'); return signal.lfilter(b, a, x)
narr = load('/home/claude/aliang2052/tihuceshi/口播粗剪.mp4', 0, END); narr *= 10 ** ((-16 - lufs(narr)) / 20)
voice = np.zeros((N, 2), np.float32); c = int(P0 * SR)
voice[:c] = narr[:c]; rest = narr[c:]; o_ = int((P0 + PD) * SR); voice[o_:o_ + len(rest)] = rest[:N - o_]
def boom():
    t = tt(2.4); sub = np.sin(2 * np.pi * np.cumsum(60 * np.exp(-t * 2) + 30) / SR) * np.exp(-t * 1.8)
    body = lp(rng.standard_normal(len(t)), 800) * np.exp(-t * 6); crack = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 45) * 0.6
    tail = bp(rng.standard_normal(len(t)), 150, 1500) * np.exp(-t * 1.3) * 0.15
    y = np.tanh(1.8 * (sub + body + crack + tail)); return np.stack([y, np.roll(y, 300)], 1)
def whoosh(d=0.5, s=1.0):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros(len(t))
    for i in range(0, len(t), 512): fc = 300 + 5000 * (i / len(t)) ** 1.5; out[i:i + 512] = bp(n[i:i + 512], fc * .5, fc * 1.6)
    y = out * np.sin(np.pi * t / d) ** 3 * .6 * s; pan = np.linspace(-.7, .7, len(t))
    return np.stack([y * (1 - np.clip(pan, 0, 1)), y * (1 + np.clip(pan, -1, 0))], 1)
def shine():
    t = tt(1.2); y = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 3) for f in (2093, 2637, 3136, 4186)) * .08
    y += hp(rng.standard_normal(len(t)), 6000) * np.exp(-((t - .25) / .2) ** 2) * .15; return np.stack([y, y], 1)
def scribble():
    t = tt(.35); y = bp(rng.standard_normal(len(t)), 1500, 6000) * (0.5 + 0.5 * np.sin(2 * np.pi * 18 * t)) * np.exp(-t * 4) * .5; return np.stack([y, y], 1)
def pop():
    t = tt(.16); y = np.sin(2 * np.pi * np.cumsum(900 * np.exp(-t * 25) + 350) / SR) * np.exp(-t * 30) * .45; return np.stack([y, y], 1)
def stamp():
    t = tt(.6); y = np.tanh(2 * (np.sin(2 * np.pi * np.cumsum(140 * np.exp(-t * 12) + 50) / SR) * np.exp(-t * 14) + bp(rng.standard_normal(len(t)), 800, 6000) * np.exp(-t * 35) * .7)) * .8
    return np.stack([y, y], 1)
def riser():
    d = 1.6; t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros(len(t))
    for i in range(0, len(t), 512): fc = 200 + 6000 * (i / len(t)) ** 2; out[i:i + 512] = bp(n[i:i + 512], fc * .7, fc * 1.4)
    y = (out * .5 + np.sin(2 * np.pi * np.cumsum(120 + 500 * (t / d) ** 2) / SR) * .25) * (t / d) ** 2.2; return np.stack([y, y], 1)
LIB = dict(boom=boom, whoosh=whoosh, shine=shine, scribble=scribble, pop=pop, stamp=stamp, riser=riser)
G = dict(boom=.9, whoosh=.45, shine=.6, scribble=.5, pop=.35, stamp=.8, riser=.5)
sfx = np.zeros((N, 2), np.float32)
for t0, k in EV['sfx']:
    cl = LIB[k](); off = -.15 if k == 'whoosh' else (-len(cl) / SR if k == 'riser' else 0)
    i = int(max(0, t0 + off) * SR); j = min(N, i + len(cl)); sfx[i:j] += cl[:j - i] * G[k]
sfx *= 10 ** ((-26 - lufs(sfx)) / 20)
# placeholder bed: tension pulse, swells in pause, drop before hits
BPM = 100; beat = 60 / BPM; L = int(beat * 16 * SR); loop = np.zeros(L)
def add(b, y, t): i = int(t * SR); j = min(len(b), i + len(y)); b[i:j] += y[:j - i]
for k in range(32):
    t_ = tt(beat / 2 * .95); add(loop, lp(signal.sawtooth(2 * np.pi * 55 * (1 if (k // 8) % 2 == 0 else 0.89) * t_) * np.exp(-t_ * 6) * .1, 600), k * beat / 2)
for k in range(0, 16, 2):
    t_ = tt(.35); add(loop, np.sin(2 * np.pi * np.cumsum(120 * np.exp(-t_ * 28) + 42) / SR) * np.exp(-t_ * 9) * .32, k * beat)
bed = np.tile(loop, N // L + 2)[:N]; bed = np.stack([bed, np.roll(bed, 220)], 1).astype(np.float32); bed *= 10 ** ((-34 - lufs(bed[:SR * 20])) / 20)
env = np.convolve(np.abs(voice).mean(1), np.ones(4800) / 4800, 'same'); g = 1 - .45 * np.clip(env / (np.percentile(env, 95) * .25), 0, 1)
g = np.convolve(g, np.ones(12000) / 12000, 'same')
for a, b in [(1.05, 3.9), (P0, P0 + PD)]: g[int(a * SR):int(b * SR)] = np.maximum(g[int(a * SR):int(b * SR)], 2.2)
for hit in (1.05, P0): i = int(hit * SR); g[i - int(.35 * SR):i] *= .1
g[:int(.4 * SR)] *= np.linspace(0, 1, int(.4 * SR)); e = int(END * SR); g[e - SR:e] *= np.linspace(1, 0, SR)
bed *= g[:, None]
x = (voice + sfx + bed)[:int(END * SR)].astype(np.float32).tobytes()
base = ['ffmpeg', '-hide_banner', '-nostats', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-']
p = subprocess.run(base + ['-af', 'loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json', '-f', 'null', '-'], input=x, capture_output=True)
js = p.stderr.decode(); m = json.loads(js[js.rindex('{'):js.rindex('}') + 1])
af = 'loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true'.format(**m)
subprocess.run(base + ['-af', af, '-c:a', 'pcm_s16le', '-y', '/tmp/claude-0/mock/sample.wav'], input=x, check=True, capture_output=True)
print('ok')
