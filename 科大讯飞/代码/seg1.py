# 第三版样片：开头 0–30 秒（第 1–9 镜）。python3 seg1.py align.json 输出目录 [stills|video|audio]
import sys, os, wave, subprocess
import numpy as np
mode = sys.argv[3]
sys.argv = ['timeline.py', sys.argv[1], sys.argv[2]]
OUT = sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'timeline.py'), encoding='utf-8').read().split("if __name__ == '__main__':")[0])
from v3 import *
import kongjing as KJ

S = {s['i']: s for s in shots}
T_END = S[10]['start']
def wt(i, word):
    """某镜里某个词开始的输出时间"""
    s = S[i]; txt = s['text']; k = len(nchars(txt[:txt.index(word)])); return s['chars'][k][1]

# ---------------------------------------------------------------- 背景
IMG1, IMG2 = img('1'), img('2')
BG_MATH = bg_char(backdrop=cover(IMG1, W, H), tint=VIOLET, dim=0.10, key='math')
BG_DARK = bg_char(tint=VIOLET, k_tint=0.24, key='dark', blob=(0.5, 0.35))

# ---------------------------------------------------------------- 出镜
def host(i, z0=1.0, punch=None, card=None):
    def fn(t):
        tl = t - S[i]['start']; dur = S[i]['dur']
        fr = cover(cam_frame(t), W, H).astype(np.float32)
        z = z0 + 0.03 * tl / dur
        if punch and t >= punch: z += 0.09
        f = zoom(fr, z, 0.5, 0.35)
        if card:
            im, t0, x, y = card; k = seg(t, t0, t0 + 0.35)
            if k > 0: put(f, im, x, y, k, scale=0.75 + 0.25 * back_out(k), angle=-3)
        return f
    return fn

LOCK = glass_card(400, 400, '未公开模型', 'lock', tint=VIOLET, title_size=62)

# ---------------------------------------------------------------- 截图（新底色、金色高亮、更明显的透视）
def shot(i, A, box0, box1=None, hl=None, ry=(-16, -8), rx=6, maxk=2.4, bgimg=None, t_rng=None):
    box1 = box1 or box0
    def fn(t):
        a, b = t_rng if t_rng else (S[i]['start'], S[i]['end'])
        tl = t - a; dur = b - a; u = ease(tl / dur)
        bx = [lerp(p, q, u) for p, q in zip(box0, box1)]; bw, bh = bx[2] - bx[0], bx[3] - bx[1]
        s = min(1500 / bw, 780 / bh, maxk) * (0.92 + 0.08 * ease_out(min(1, tl / 0.9)))
        mx, my = W / s * 0.8, H / s * 0.8
        x0, y0 = int(max(0, bx[0] - mx)), int(max(0, bx[1] - my)); x1, y1 = int(min(A.shape[1], bx[2] + mx)), int(min(A.shape[0], bx[3] + my))
        cd = card(A[y0:y1, x0:x1], max(8, int((x1 - x0) * s)), radius=18)
        cxb = ((bx[0] + bx[2]) / 2 - x0) * s; cyb = ((bx[1] + bx[3]) / 2 - y0) * s
        f = (bgimg if bgimg is not None else BG_MATH).copy()
        M = persp(f, cd, W / 2 + (cd.shape[1] / 2 - cxb) + 60, H / 2 + (cd.shape[0] / 2 - cyb) - 30, 1.0, ry=lerp(ry[0], ry[1], u), rx=rx, shadow_k=0.65)
        dim_except(f, M, ((bx[0] - x0) * s, (bx[1] - y0) * s, (bx[2] - x0) * s, (bx[3] - y0) * s), 0.62)
        if hl:
            hb = [(hl[0] - x0) * s, (hl[1] - y0) * s, (hl[2] - x0) * s, (hl[3] - y0) * s]
            hp = cv2.perspectiveTransform(np.array([[[hb[0], hb[1]], [hb[2], hb[3]]]], np.float32), M)[0]
            hl_bar(f, max(0, hp[0][0]), max(0, hp[0][1]), min(W - 1, hp[1][0]), min(H - 1, hp[1][1]), seg(tl, 0.3, 1.0), GOLD, 0.42)
        return f
    return fn

# ---------------------------------------------------------------- 第 4 镜：论文纸片落下堆成一摞 + 719 跳数
rng = np.random.default_rng(5)
DROPS = [(rng.uniform(-260, 260), rng.uniform(-14, 14), rng.uniform(0, 1.6), k % 6) for k in range(26)]
NUM_LBL = text('篇论文', F_BLACK, 70, WHITE, 0.08)
GHOST = text('719', F_NUM, 900, GOLD, 0.0)
def papers(t):
    s = S[4]; tl = t - s['start']; dur = S[4]['dur'] + S[5]['dur'] * 0
    f = BG_DARK.copy()
    put(f, GHOST, W * 0.62, H * 0.52, 0.09 * ease_out(seg(tl, 0, 0.6)), scale=1.0 + 0.04 * tl)
    px, py = W * 0.30, H * 0.60
    for n, (dx, ang, t0, k) in enumerate(DROPS):
        u = seg(tl, t0 * 0.9, t0 * 0.9 + 0.45)
        if u <= 0: continue
        yy = lerp(-300, py - n * 6, ease_out(u, 2)); xx = px + dx * (1 - u) * 0.6 + dx * 0.08
        put(f, PAPERS[k], xx, yy, 1.0, scale=0.9, angle=ang * (1 - 0.6 * u))
    cnt = int(719 * ease_out(seg(tl, 0.15, 1.7), 2))
    num = number(f'{cnt}', '', 300, GOLD)
    put(f, num, W * 0.66, H * 0.46, ease_out(seg(tl, 0.1, 0.4)))
    put(f, NUM_LBL, W * 0.66 + 10, H * 0.46 + 190, ease_out(seg(tl, 0.5, 0.8)))
    return f

# ---------------------------------------------------------------- 第 5 镜：多色徽章平铺在透视桌面上
FIELDS = [('数论', VIOLET, 470, 1100, 760, '数论'), ('代数几何', TEAL, 430, 1560, 560, '代数几何'), ('理论计算机', SKY, 430, 640, 560, '理论计算机'),
          ('数学物理', EMERALD, 340, 1820, 880, None), ('组合数学', GOLD, 330, 300, 880, None), ('偏微分方程', ROSE, 320, 1100, 280, None), ('算子代数', ORANGE, 300, 1740, 250, None)]
FIELD_IMG = [glass(sz, n, None, tint=c, title_size=int(sz * (0.2 if len(n) <= 2 else 0.15 if len(n) <= 4 else 0.12))) for n, c, sz, x, y, w in FIELDS]
def fields(t):
    items = []
    t_more = wt(5, '等多个方向')
    for (n, c, sz, x, y, w), im in zip(FIELDS, FIELD_IMG):
        t0 = (wt(5, w) - 0.05) if w else t_more + 0.08 * len(items)
        items.append((im, x, y, t0 - S[5]['start']))
    return badge_table(t - S[5]['start'], items, BG_DARK, dur=S[5]['dur'], rx=34, ry=-4, cy=H * 0.55, canvas=(2200, 1200), push=(1.0, 1.1))

# ---------------------------------------------------------------- 第 7–8 镜：数量 vs 含金量 → 尚未解决的问题
C_NUM_ON = glass_card(540, 620, '数量', 'stack', tint=SKY, active=1.0, title_size=74)
C_NUM_OFF = glass_card(540, 620, '数量', 'stack', tint=SKY, active=0.3, title_size=74)
C_GOLD_ON = glass_card(540, 620, '含金量', 'gem', tint=GOLD, active=1.0, title_size=74)
C_GOLD_OFF = glass_card(540, 620, '含金量', 'gem', tint=GOLD, active=0.3, title_size=74)
B_RH = glass(330, '黎曼ζ函数', None, tint=VIOLET, title_size=52)
B_HG = glass(300, '霍奇猜想', None, tint=ROSE, title_size=52)
BG_Z = bg_char(tint=VIOLET, k_tint=0.3, key='z', blob=(0.6, 0.45))
def cards(t):
    t_gold = wt(8, '含金量'); t_q = wt(8, '这里面')
    if t < t_q - 0.1:
        f = BG_DARK.copy(); t0 = S[7]['start']
        a = ease_out(seg(t, t0, t0 + 0.3)); g = seg(t, t_gold - 0.05, t_gold + 0.25)
        put(f, C_NUM_OFF if g > 0.5 else C_NUM_ON, W / 2 - 340, H / 2 - 40, a, scale=(0.85 + 0.15 * back_out(seg(t, t0, t0 + 0.4))) * (1 - 0.06 * g))
        put(f, C_GOLD_OFF, W / 2 + 340, H / 2 - 40, a * (1 - g), scale=0.85 + 0.15 * back_out(seg(t, t0 + 0.1, t0 + 0.5)))
        if g > 0: put(f, C_GOLD_ON, W / 2 + 340, H / 2 - 40, g, scale=1.0 + 0.1 * (1 - back_out(g)))
        return f
    tl = t - t_q
    f = KJ.math_cosmos(3.0 + tl * 0.9, 6.0, bgimg=BG_Z)
    put(f, B_RH, W * 0.24, H * 0.36, ease_out(seg(tl, 0.5, 0.85)), scale=0.7 + 0.3 * back_out(seg(tl, 0.5, 0.95)))
    put(f, B_HG, W * 0.32, H * 0.70, ease_out(seg(tl, 1.1, 1.45)), scale=0.7 + 0.3 * back_out(seg(tl, 1.1, 1.55)))
    return whip(f, max(0, 1 - tl / 0.2))

# ---------------------------------------------------------------- 组装
t_split3 = wt(3, 'OpenAI展示了') + 1.2
VIS = {
 1: host(1, 1.0, punch=wt(1, '全让AI')),
 2: shot(2, IMG1, (150, 330, 2874, 1150)),
 3: None,
 4: papers, 5: fields,
 6: host(6, 1.06, card=(LOCK, wt(6, '还没公开') - 0.1, 1540, 470)),
 7: cards, 8: cards,
 9: host(9, 1.0),
}
F3a = shot(3, IMG1, (60, 1780, 2964, 2010), hl=(560, 1800, 2964, 1990), t_rng=(S[3]['start'], t_split3))
F3b = shot(3, IMG2, (280, 360, 2120, 1000), (280, 700, 2120, 1560), ry=(10, 4), t_rng=(t_split3, S[3]['end']))
VIS[3] = lambda t: F3a(t) if t < t_split3 else whip(F3b(t), max(0, 1 - (t - t_split3) / 0.2))
WHIP = {2: S[2]['start'], 4: S[4]['start'], 5: S[5]['start'], 7: S[7]['start']}

def frame(t):
    s = next(x for x in shots if x['start'] <= t < x['end']); CUR_T[0] = t
    f = VIS[s['i']](t)
    for i, t0 in WHIP.items():
        if 0 <= t - t0 < 0.2: f = whip(f, 1 - (t - t0) / 0.2)
        if 0 < t0 - t < 0.1: f = whip(f, (0.1 - (t0 - t)) / 0.1 * 0.8)
    subtitle(f, sub_at(t))
    return f

if mode == 'stills':
    for i in range(1, 10):
        for q in (0.35, 0.85):
            tt = S[i]['start'] + S[i]['dur'] * q
            Image.fromarray(np.clip(frame(tt), 0, 255).astype(np.uint8)).save(f'{OUT}/s{i}_{int(q*100)}.jpg', quality=88)
    print('stills ok')

if mode == 'video':
    wr = Writer(f'{OUT}/seg1_video.mp4', FPS, crf=18)
    for n in range(int(T_END * FPS)): wr.write(frame(n / FPS))
    wr.close(); print('video ok', T_END)

if mode == 'audio':
    SR = 44100
    def load(p, gain=1.0):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-vn', '-ac', '2', '-ar', str(SR), f'{OUT}/_t.wav'], check=True)
        with wave.open(f'{OUT}/_t.wav') as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768 * gain
    MUS = '/home/claude/aliang2052/tempsucai/materials/audio/音乐素材/'
    RAW = {'vo': load(VO_WAV), 'cam': load(os.path.join(MAT, '口播', '1080-压缩版.mp4'))}
    def rms(src): x = np.concatenate([RAW[src][int(a * SR):int(b * SR)] for a, b, o, sr in audio_pieces if sr == src]); return np.sqrt((x ** 2).mean())
    gcam = rms('vo') / rms('cam')
    N = int((T_END + 1.5) * SR); voice = np.zeros((N, 2), np.float32)
    for a0, a1, o, sr in audio_pieces:
        if o > T_END: continue
        x = RAW[sr][int(a0 * SR):int(a1 * SR)] * (gcam if sr == 'cam' else 1.0); n = min(len(x), N - int(o * SR))
        fd = np.ones(n, np.float32); k = int(0.025 * SR); fd[:k] = np.linspace(0, 1, k); fd[-k:] = np.linspace(1, 0, k)
        voice[int(o * SR):int(o * SR) + n] += x[:n] * fd[:, None]
    music = load(MUS + '音乐/Mind Heist - Zack Hemsey.m4a')[:N]
    music = np.pad(music, ((0, max(0, N - len(music))), (0, 0)))
    env = np.abs(voice).mean(1); env = np.convolve(env, np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
    duck = np.clip(env / (env.max() * 0.15), 0, 1)
    duck = np.convolve(duck, np.ones(int(0.3 * SR)) / int(0.3 * SR), 'same')
    mg = 10 ** (lerp(-6, -17, duck) / 20)                    # 有人声时音乐压到 -17 dB，停顿处抬到 -6 dB
    fade = np.ones(N); fe = int(1.2 * SR); fade[-fe:] = np.linspace(1, 0, fe)
    mix = voice + music * (mg * fade)[:, None]
    fx = {k: load(MUS + '音效/' + v) for k, v in {'whoosh': '转场-Whoosh.mp3', 'swish': '转场-Windy swish.mp3', 'hit': '重音-Gate Hit.mp3',
                                                 'thud': '重音-Thud Hit C.mp3', 'rise': '上升-whoosh rise.mp3'}.items()}
    def add(t0, y, g):
        i = int(t0 * SR); j = min(N, i + len(y)); mix[i:j] += y[:j - i] * g
    for i, t0 in WHIP.items(): add(t0 - 0.15, fx['whoosh'], 0.35)
    add(t_split3 - 0.15, fx['swish'], 0.3)
    add(S[4]['start'] + 1.65, fx['hit'], 0.45)                 # 719 跳到头
    for (n, c, sz, x, y, w) in FIELDS[:3]: add(wt(5, w) - 0.05, fx['thud'], 0.22)
    add(wt(6, '还没公开') - 0.1, fx['thud'], 0.3)
    add(wt(8, '含金量') - 0.05, fx['hit'], 0.35)
    add(wt(8, '这里面') - 1.0, fx['rise'], 0.35)
    mix = np.clip(mix, -1, 1)
    with wave.open(f'{OUT}/seg1_raw.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/seg1_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', '44100', f'{OUT}/seg1_audio.wav'], check=True)
    print('audio ok')
