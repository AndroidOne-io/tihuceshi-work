# 第四版样片：开头约 33 秒。画面和音效共用一张事件表 EV，保证声画对齐。
# python3 seg4.py align.json 输出目录 [stills|video|audio|check]
import sys, os, wave, subprocess, math
import numpy as np
mode = sys.argv[3]
sys.argv = ['timeline.py', sys.argv[1], sys.argv[2]]
OUT = sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
PAUSE_OVR = {1: 1.6, 8: 1.2}                     # 口播停顿：开场问题悬一下；最重的事实落地后、转入讲道理之前
exec(open(os.path.join(HERE, 'timeline.py'), encoding='utf-8').read().split("if __name__ == '__main__':")[0])
from v4 import *
from v3 import badge_table
import kongjing as KJ
from hook import hook

PRE = 1.6                                         # 开场黑场蓄力（人声之前）
S = {s['i']: s for s in shots}
T_END = S[10]['start']                            # 到第 9 镜结束
def wt(i, word):
    s = S[i]; txt = s['text']; k = len(nchars(txt[:txt.index(word)])); return s['chars'][k][1]

# ---------------------------------------------------------------- 事件表（时间线时间，秒）——画面和音效都从这里取
T0 = S[1]['chars'][0][1]
EV = dict(
    voice_in=T0, human=wt(1, '人类'), boom=wt(1, '攻克'),
    cut2=S[2]['start'], split3=wt(3, 'OpenAI展示了') + 1.2, cut4=S[4]['start'], land719=S[4]['start'] + 1.7,
    cut5=S[5]['start'], cut6=S[6]['start'], lock=wt(6, '还没公开') - 0.1, cut7=S[7]['start'],
    gold=wt(8, '含金量') - 0.05, dive=wt(8, '这里面') - 0.3, cut9=S[9]['start'],
)
BADGE_T = []                                      # 徽章弹出时间（下面填）

# ---------------------------------------------------------------- 底
IMG1, IMG2 = img('1'), img('2')
BG_PAGE = bg_gild(backdrop=cover(IMG1, W, H), dim=0.10, key='page')
BG = bg_gild(key='plain')
BG_Z = bg_gild(leak=(0.75, 0.3), leak_col=ICE, k_leak=0.10, key='z', bokeh=False)

# ---------------------------------------------------------------- 1 开场（不出人）
def v1(t):
    return hook(t - EV['voice_in'], dict(human=EV['human'] - EV['voice_in'], gongke=EV['boom'] - EV['voice_in']))

# ---------------------------------------------------------------- 2–3 截图
def shot(A, box0, box1=None, hl=None, ry=(-16, -8), rx=6, maxk=2.4, bgimg=None, rng_=None):
    box1 = box1 or box0
    def fn(t):
        a, b = rng_; tl = t - a; dur = b - a; u = ease(tl / dur)
        bx = [lerp(p, q, u) for p, q in zip(box0, box1)]; bw, bh = bx[2] - bx[0], bx[3] - bx[1]
        s = min(1500 / bw, 780 / bh, maxk) * (0.92 + 0.08 * ease_out(min(1, tl / 0.9)))
        mx, my = W / s * 0.8, H / s * 0.8
        x0, y0 = int(max(0, bx[0] - mx)), int(max(0, bx[1] - my)); x1, y1 = int(min(A.shape[1], bx[2] + mx)), int(min(A.shape[0], bx[3] + my))
        cd = card(A[y0:y1, x0:x1], max(8, int((x1 - x0) * s)), radius=18)
        cxb = ((bx[0] + bx[2]) / 2 - x0) * s; cyb = ((bx[1] + bx[3]) / 2 - y0) * s
        f = (bgimg if bgimg is not None else BG_PAGE).copy()
        M = persp(f, cd, W / 2 + (cd.shape[1] / 2 - cxb) + 60, H / 2 + (cd.shape[0] / 2 - cyb) - 30, 1.0, ry=lerp(ry[0], ry[1], u), rx=rx, shadow_k=0.65)
        dim_except(f, M, ((bx[0] - x0) * s, (bx[1] - y0) * s, (bx[2] - x0) * s, (bx[3] - y0) * s), 0.62)
        if hl:
            hb = [(hl[0] - x0) * s, (hl[1] - y0) * s, (hl[2] - x0) * s, (hl[3] - y0) * s]
            hp = cv2.perspectiveTransform(np.array([[[hb[0], hb[1]], [hb[2], hb[3]]]], np.float32), M)[0]
            hl_bar(f, max(0, hp[0][0]), max(0, hp[0][1]), min(W - 1, hp[1][0]), min(H - 1, hp[1][1]), seg(tl, 0.3, 1.0), GOLD, 0.42)
        return f
    return fn
F2 = shot(IMG1, (150, 330, 2874, 1150), rng_=(S[2]['start'], S[2]['end']))
F3a = shot(IMG1, (60, 1780, 2964, 2010), hl=(560, 1800, 2964, 1990), rng_=(S[3]['start'], EV['split3']))
F3b = shot(IMG2, (280, 360, 2120, 1000), (280, 700, 2120, 1560), ry=(10, 4), rng_=(EV['split3'], S[3]['end']))

# ---------------------------------------------------------------- 4 / 7 / 8 论文堆：落下 → 719 → 变金 → 冲进去
rng = np.random.default_rng(5)
DROPS = [(rng.uniform(-240, 240), rng.uniform(-14, 14), rng.uniform(0, 1.6), k % 6) for k in range(26)]
def paper_img(w=250, h=330, seed=0, tint=None):
    r = np.random.default_rng(seed)
    base = (244, 240, 232) if tint is None else tint
    line = (160, 160, 172) if tint is None else tuple(int(v * 0.7) for v in tint)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 10, fill=base + (255,)); d.rectangle([24, 24, int(w * 0.62), 34], fill=line + (255,)); y = 46
    while y < h - 30:
        ww = int((w - 48) * r.uniform(0.6, 1.0)); d.rectangle([24, y, 24 + ww, y + 5], fill=tuple(min(255, v + 30) for v in line) + (255,)); y += 16
    return to_rgba_np(shadow(im, 10, (0, 6), 150, 16))
PW = [paper_img(seed=k) for k in range(6)]
PG = [paper_img(seed=k, tint=(250, 214, 130)) for k in range(6)]
LBL = text('篇论文', F_BLACK, 70, WHITE, 0.08)
GHOST = text('719', F_NUM, 900, GOLD, 0.0)
SPARK = np.random.default_rng(9).uniform(0, 1, (90, 3))
PX, PY = W * 0.30, H * 0.60

def papers(t):
    tl = t - EV['cut4']
    f = BG.copy()
    put(f, GHOST, W * 0.62, H * 0.52, 0.08 * ease_out(seg(tl, 0, 0.6)), scale=1.0 + 0.015 * min(tl, 8))
    g = ease(seg(t, EV['gold'], EV['gold'] + 0.5))            # 变金
    sweep_x = lerp(PX - 400, PX + 400, seg(t, EV['gold'], EV['gold'] + 0.5))
    for n, (dx, ang, t0, k) in enumerate(DROPS):
        u = seg(tl, t0 * 0.9, t0 * 0.9 + 0.45)
        if u <= 0: continue
        yy = lerp(-300, PY - n * 6, ease_out(u, 2)); xx = PX + dx * (1 - u) * 0.6 + dx * 0.08
        put(f, PW[k], xx, yy, 1.0, scale=0.9, angle=ang * (1 - 0.6 * u))
        if g > 0: put(f, PG[k], xx, yy, g, scale=0.9, angle=ang * (1 - 0.6 * u))
    if 0 < seg(t, EV['gold'], EV['gold'] + 0.6) < 1:              # 金光扫过
        lay = np.zeros((H, W, 3), np.float32); cv2.line(lay, (int(sweep_x), 0), (int(sweep_x - 200), H), (255, 230, 170), 50)
        f += cv2.GaussianBlur(lay, (0, 0), 30) * 0.9
    if g > 0:
        lay = np.zeros((H, W, 3), np.float32)
        for (a, r, s) in SPARK:
            k = (t * 0.8 + s) % 1.0
            p = (int(PX + (a - 0.5) * 520), int(PY - 120 - k * 360 * (0.5 + r)))
            cv2.circle(lay, p, 2 + int(3 * r), (np.array(GOLD) * g * (1 - k)).tolist(), -1, cv2.LINE_AA)
        f += lay + cv2.GaussianBlur(lay, (0, 0), 6)
    cnt = 719 if t > EV['land719'] else int(719 * ease_out(seg(tl, 0.15, 1.7), 2))
    num = number(f'{cnt}', '', 300, GOLD)
    put(f, num, W * 0.66, H * 0.46, ease_out(seg(tl, 0.1, 0.4)), scale=1.0 + 0.08 * max(0, 1 - abs(t - EV['land719']) / 0.15))
    put(f, LBL, W * 0.66 + 10, H * 0.46 + 190, ease_out(seg(tl, 0.5, 0.8)))
    if t >= EV['cut7']:                                       # 第 7–8 镜：镜头慢慢推向论文堆
        f = zoom(f, 1.0 + 0.12 * ease(seg(t, EV['cut7'], EV['dive'])), 0.32, 0.55)
    return f

B_RH = make_card(560, 200, 'rect', 24, VIOLET, 0.6, '黎曼ζ函数', title_size=74, rim=0.5, rim_col=(210, 190, 255))
B_HG = make_card(520, 200, 'rect', 24, ROSE, 0.6, '霍奇猜想', title_size=74, rim=0.5, rim_col=(255, 190, 205))
def v78(t):
    if t < EV['dive']: return papers(t)
    k = t - EV['dive']
    if k < 0.35:                                              # 冲进最上面那张论文
        f = zoom(papers(EV['dive']), 1.12 + 6 * ease_in(k / 0.35, 3), 0.30, 0.50)
        return whip(f + (k / 0.35) ** 3 * 255, k / 0.35, horiz=False)
    tz = k - 0.35
    f = KJ.math_cosmos(2.5 + tz * 0.9, 6.0, bgimg=BG_Z)
    f += max(0, 1 - tz / 0.2) * 255
    put(f, B_RH, W * 0.24, H * 0.34, ease_out(seg(tz, 0.4, 0.7)), scale=0.85 + 0.15 * back_out(seg(tz, 0.4, 0.8)))
    put(f, B_HG, W * 0.27, H * 0.66, ease_out(seg(tz, 0.9, 1.2)), scale=0.85 + 0.15 * back_out(seg(tz, 0.9, 1.3)))
    return f
EV['rh'] = EV['dive'] + 0.35 + 0.45; EV['hg'] = EV['dive'] + 0.35 + 0.95

# ---------------------------------------------------------------- 5 方向徽章：半透明，平铺在透视桌面
FIELDS = [('数论', SAPPHIRE, 470, 96, 1100, 780, '数论'), ('代数几何', TEAL, 430, 74, 1600, 560, '代数几何'), ('理论计算机', CORAL, 430, 60, 600, 560, '理论计算机'),
          ('数学物理', EMERALD, 340, 56, 1880, 900, None), ('组合数学', VIOLET, 330, 56, 300, 900, None), ('偏微分方程', ROSE, 320, 46, 1100, 300, None), ('算子代数', ICE, 300, 50, 1900, 240, None)]
def _bimg(n, c, sz, ts): return make_card(sz, sz, 'circle', 0, c, 0.66, n, title_size=ts, rim=0.6, rim_col=tuple(min(255, int(v * 0.45 + 150)) for v in c))
FIMG = [_bimg(n, c, sz, ts) for n, c, sz, ts, x, y, w in FIELDS]
t_more = wt(5, '等多个方向')
for j, (n, c, sz, ts, x, y, w) in enumerate(FIELDS):
    BADGE_T.append((wt(5, w) - 0.05) if w else t_more + 0.1 * (j - 3))
def v5(t):
    items = [(im, x, y, t0 - EV['cut5']) for im, (n, c, sz, ts, x, y, w), t0 in zip(FIMG, FIELDS, BADGE_T)]
    return badge_table(t - EV['cut5'], items, BG, dur=S[5]['dur'], rx=34, ry=-4, cy=H * 0.55, canvas=(2200, 1200), push=(1.0, 1.08))

# ---------------------------------------------------------------- 6 / 9 出镜
LOCK = make_card(400, 300, 'rect', 26, INK, 0.58, '未公开模型', 'lock', title_size=52, ic_col=GOLD)
def host(z0=1.0, card=None):
    def fn(t):
        s = next(x for x in shots if x['start'] <= t < x['end']); tl = t - s['start']
        f = zoom(cover(cam_frame(t), W, H).astype(np.float32), z0 + 0.03 * tl / s['dur'], 0.5, 0.35)
        if card:
            im, t0, x, y = card; k = seg(t, t0, t0 + 0.3)
            if k > 0: put(f, im, x + 40 * (1 - ease_out(k)), y, k)
        return f
    return fn

VIS = {1: v1, 2: F2, 3: lambda t: F3a(t) if t < EV['split3'] else whip(F3b(t), max(0, 1 - (t - EV['split3']) / 0.2)),
       4: papers, 5: v5, 6: host(1.06, (LOCK, EV['lock'], 1520, 420)), 7: v78, 8: v78, 9: host(1.0)}
CUTS = ['cut2', 'cut4', 'cut5', 'cut7', 'cut9']                 # 甩镜转场（配 Whoosh）

def frame(t_out):
    t = t_out - PRE; CUR_T[0] = max(t, 0)
    if t < 0: return hook(t - EV['voice_in'] + 0.0, dict(human=EV['human'] - EV['voice_in'], gongke=EV['boom'] - EV['voice_in']))
    s = next(x for x in shots if x['start'] <= t < x['end'])
    f = VIS[s['i']](t)
    for c in CUTS:
        t0 = EV[c]
        if 0 <= t - t0 < 0.2: f = whip(f, 1 - (t - t0) / 0.2)
        if 0 < t0 - t < 0.1: f = whip(f, (0.1 - (t0 - t)) / 0.1 * 0.8)
    subtitle(f, sub_at(t))
    return f

DUR = PRE + T_END
if mode == 'stills':
    pts = [('黑场', -1.0), ('冲进', EV['voice_in'] + 0.3), ('问号', EV['boom'] - 0.4), ('炸开', EV['boom'] + 0.15), ('炸开后', EV['boom'] + 0.8),
           ('截图', EV['cut2'] + 1.5), ('719', EV['land719'] + 0.5), ('徽章', BADGE_T[-1] + 0.5), ('出镜卡', EV['lock'] + 0.6),
           ('数量', EV['cut7'] + 0.5), ('变金', EV['gold'] + 0.7), ('冲进去', EV['dive'] + 0.2), ('ζ', EV['hg'] + 0.6)]
    from PIL import Image as _I
    ims = []
    for name, tt in pts:
        im = _I.fromarray(np.clip(frame(tt + PRE), 0, 255).astype(np.uint8)).resize((640, 360)); ImageDraw.Draw(im).text((8, 6), name, fill=(255, 230, 0), font=font(F_MED, 22)); ims.append(im)
    g = _I.new('RGB', (640 * 3, 360 * ((len(ims) + 2) // 3)))
    for k, im in enumerate(ims): g.paste(im, ((k % 3) * 640, (k // 3) * 360))
    g.save(f'{OUT}/stills.jpg', quality=86); print('stills ok')

if mode == 'video':
    wr = Writer(f'{OUT}/seg4_video.mp4', FPS, crf=18)
    for n in range(int(DUR * FPS)): wr.write(frame(n / FPS))
    wr.close(); print('video ok', DUR)

# ---------------------------------------------------------------- 声音：人声 + 配乐（卡在「攻克」那一拍）+ 按峰值对齐的音效
SR = 44100
MUSD = '/home/claude/aliang2052/tempsucai/materials/audio/音乐素材/'
def load(p):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-vn', '-ac', '2', '-ar', str(SR), f'{OUT}/_t.wav'], check=True)
    with wave.open(f'{OUT}/_t.wav') as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
def peak_of(x):
    env = np.convolve(np.abs(x).mean(1), np.ones(441) / 441, 'same'); return env.argmax() / SR
def db(x): return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)

MUSIC = dict(file='音乐/悬疑-Dance for me walls.mp3', beat=21.09, pre=2.5)   # 曲子 21.09s 的重拍对准「攻克」
SFX = {'rise': '上升-whoosh rise.mp3', 'whoosh': '转场-Whoosh.mp3', 'swish': '转场-Windy swish.mp3', 'gate': '重音-Gate Hit.mp3', 'thud': '重音-Thud Hit C.mp3', 'dong': '重音-咚 重磅.mp3'}
# (事件名, 时间, 音效, 增益) —— 音效的峰值落在该时间
def sfx_plan():
    P = [('蓄力→人声进', EV['voice_in'], 'rise', 0.55), ('冲进隧道', EV['voice_in'], 'thud', 0.40), ('攻克·问号炸开', EV['boom'], 'dong', 1.0)]
    for c in CUTS: P.append((f'转场 {c}', EV[c], 'whoosh', 0.45))
    P += [('截图换页', EV['split3'], 'swish', 0.35), ('719 停住', EV['land719'], 'gate', 0.50)]
    for j, t0 in enumerate(BADGE_T): P.append((f'徽章{j + 1}', t0 + 0.1, 'thud', 0.20 if j < 3 else 0.12))
    P += [('未公开卡', EV['lock'] + 0.08, 'thud', 0.22), ('变金', EV['gold'] + 0.1, 'gate', 0.38), ('冲进论文', EV['dive'] + 0.3, 'swish', 0.45),
          ('ζ 出现', EV['dive'] + 0.35, 'thud', 0.40), ('黎曼卡', EV['rh'], 'thud', 0.16), ('霍奇卡', EV['hg'], 'thud', 0.16)]
    return P

if mode in ('audio', 'check'):
    RAW = {'vo': load(VO_WAV), 'cam': load(os.path.join(MAT, '口播', '1080-压缩版.mp4'))}
    def rms_src(src): return np.sqrt(np.mean(np.concatenate([RAW[src][int(a * SR):int(b * SR)] for a, b, o, sr in audio_pieces if sr == src]) ** 2))
    gcam = rms_src('vo') / rms_src('cam')
    N = int((DUR + 0.5) * SR)
    voice = np.zeros((N, 2), np.float32)
    for a0, a1, o, sr in audio_pieces:
        if o > T_END: continue
        x = RAW[sr][int(a0 * SR):int(a1 * SR)] * (gcam if sr == 'cam' else 1.0); i = int((o + PRE) * SR); n = min(len(x), N - i)
        fd = np.ones(n, np.float32); k = int(0.025 * SR); fd[:k] = np.linspace(0, 1, k); fd[-k:] = np.linspace(1, 0, k)
        voice[i:i + n] += x[:n] * fd[:, None]
    # 配乐：从 beat-pre 开始，让 beat 落在「攻克」
    mus = load(MUSD + MUSIC['file'])
    m_out0 = PRE + EV['boom'] - MUSIC['pre']; m_src0 = MUSIC['beat'] - MUSIC['pre']
    music = np.zeros((N, 2), np.float32); i0 = int(m_out0 * SR); seg_ = mus[int(m_src0 * SR):int(m_src0 * SR) + N - i0]
    music[i0:i0 + len(seg_)] = seg_
    fi = int(0.4 * SR); music[i0:i0 + fi] *= np.linspace(0, 1, fi)[:, None]
    gap0, gap1 = int((PRE + EV['boom'] - 0.25) * SR), int((PRE + EV['boom'] - 0.02) * SR)   # 重击前音乐先收住
    music[gap0:gap1] *= np.linspace(1, 0.05, gap1 - gap0)[:, None] ** 0.5
    fo = int(1.5 * SR); music[N - fo:] *= np.linspace(1, 0, fo)[:, None]
    # 音量：人声说话时配乐比人声低 12 dB；停顿处只低 5 dB（攻克之后的停顿再抬一点）
    vmask = np.abs(voice).mean(1) > 0
    v_db = db(voice[vmask]); m_db = db(mus[int(MUSIC['beat'] * SR):int((MUSIC['beat'] + 20) * SR)])
    g_under, g_gap = 10 ** ((v_db - 12 - m_db) / 20), 10 ** ((v_db - 5 - m_db) / 20)
    act = np.convolve(np.abs(voice).mean(1), np.ones(int(0.05 * SR)) / int(0.05 * SR), 'same') > 10 ** ((v_db - 25) / 20)
    act = act.astype(np.float32); env = np.zeros_like(act); a_up, a_dn = 1 / (0.06 * SR), 1 / (0.35 * SR); e = 0.0
    for k in range(len(act)):
        e = min(1.0, e + a_up) if act[k] > e else max(0.0, e - a_dn); env[k] = e
    mg = g_gap + (g_under - g_gap) * env
    music *= mg[:, None]
    sfx = np.zeros((N, 2), np.float32); report = []
    cache = {}
    for name, t_ev, key, gain in sfx_plan():
        if key not in cache:
            y = load(MUSD + '音效/' + SFX[key]); cache[key] = (y / (np.abs(y).max() + 1e-9), peak_of(y))
        y, pk = cache[key]
        st = PRE + t_ev - pk; i = int(st * SR); j0 = max(0, -i); i = max(0, i); n = min(len(y) - j0, N - i)
        sfx[i:i + n] += y[j0:j0 + n] * gain * 0.5
        report.append((name, PRE + t_ev, key, PRE + t_ev))
    mix = voice + music + sfx
    if mode == 'check':
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        matplotlib.rcParams['font.family'] = ['Noto Sans CJK JP']
        tt = np.arange(N) / SR; d = 441
        def envd(x): e = np.abs(x).mean(1); return 20 * np.log10(np.convolve(e, np.ones(d) / d, 'same')[::d] + 1e-5)
        fig, ax = plt.subplots(figsize=(26, 7))
        ax.plot(tt[::d], envd(voice), lw=0.6, color='#555', label='人声')
        ax.plot(tt[::d], envd(music), lw=0.9, color='#d4a017', label='配乐')
        ax.plot(tt[::d], envd(sfx), lw=0.7, color='#2a7fd4', label='音效')
        for name, te, key, _ in report:
            ax.axvline(te, color='#c0392b', lw=0.6, alpha=0.6); ax.text(te, -8, name, rotation=90, fontsize=7, va='top', color='#c0392b')
        for s in shots:
            if s['start'] < T_END: ax.axvline(s['start'] + PRE, color='#27ae60', lw=1.2, alpha=0.5, ls='--')
        ax.set_ylim(-75, 0); ax.set_xlim(0, DUR); ax.set_xticks(np.arange(0, DUR, 1)); ax.grid(alpha=0.2); ax.legend(loc='lower right')
        ax.set_title('声画对位：红线=画面事件（音效峰值对齐处）  绿虚线=镜头切换')
        fig.tight_layout(); fig.savefig(f'{OUT}/sync.png', dpi=80)
        um = vmask[:len(music)]
        print(f'人声 {db(voice[vmask]):.1f} dB；说话时配乐 {db(music[um & (np.abs(music).mean(1) > 0)]):.1f} dB；停顿时配乐 {db(music[~um & (np.arange(N) > (m_out0 + 1) * SR)]):.1f} dB')
        for name, te, key, _ in report: print(f'  {te:6.2f}s  {key:6s}  {name}')
    if mode == 'audio':
        with wave.open(f'{OUT}/seg4_raw.wav', 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/seg4_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', '44100', f'{OUT}/seg4_audio.wav'], check=True)
        print('audio ok')
