# 完整时间线（第四版起）：画面和音效共用事件表 EV；可只渲染某一段。
# python3 full.py align.json 输出目录 [stills|video|audio|check] [起秒 止秒]
import sys, os, wave, subprocess, math
import numpy as np
mode = sys.argv[3]
WIN = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else None
sys.argv = ['timeline.py', sys.argv[1], sys.argv[2]]
OUT = sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
# 口播停顿（只停在全屏画面上）：开场问题、最重的事实、向内/向外对比、论点大字、包袱、片名、转国内
PAUSE_OVR = {1: 0.8, 8: 0.45, 11: 0.35, 13: 0.35, 15: 0.4, 17: 0.9, 18: 0.65,
             25: 0.75, 36: 0.4, 47: 0.5, 50: 0.75, 60: 0.3, 70: 0.25, 71: 0.0}
# 只轻提较慢的长口播；保留技术名词段和此前修好的英文、化工词头。
ROW_SPEED = {6: 1.04, 16: 1.06, 19: 1.04}
ROW_GAP_OVR = 0.16
END_PAD = 0.0
exec(open(os.path.join(HERE, 'timeline.py'), encoding='utf-8').read().split("if __name__ == '__main__':")[0])
from v4 import *
from v3 import badge_table
import kongjing as KJ
from hook import hook

PRE = 0.9
S = {s['i']: s for s in shots}
def wt(i, word):
    s = S[i]; txt = s['text']; k = len(nchars(txt[:txt.index(word)])); return s['chars'][k][1]
def last_voice(i): return S[i]['chars'][-1][1] + 0.35

# ================================================================ 事件表
T0 = S[1]['chars'][0][1]
EV = dict(
    voice_in=T0, human=wt(1, '人类'), boom=wt(1, '攻克'),
    cut2=S[2]['start'], split3=wt(3, 'OpenAI展示了') + 1.2, cut4=S[4]['start'], land719=S[4]['start'] + 1.7,
    cut5=S[5]['start'], cut6=S[6]['start'], lock=wt(6, '还没公开') - 0.1, cut7=S[7]['start'],
    gold=wt(8, '含金量') - 0.05, dive=wt(8, '这里面') - 0.3, cut9=S[9]['start'],
    # 第 9–18 镜
    neqA=wt(9, '数学研究'), neqB=wt(9, '普通任务'), neq=wt(9, '两码事'),
    cut10=S[10]['start'], doc=wt(10, '写文章'), lst=wt(10, '总结资料'), inward=wt(10, '向内索取'), tidy=wt(10, '整理'),
    outward=wt(11, '向外延伸'), rule=wt(11, '新的规律'),
    use=wt(13, '使用知识'), create=wt(13, '参与创造知识'),
    meme=S[15]['start'], afs=wt(17, 'AI for Science'), bridge=last_voice(18), cut19=S[19]['start'],
    cut22=S[22]['start'], ch_in=last_voice(25), cut26=S[26]['start'], cut28=S[28]['start'], cut30=S[30]['start'], cut32=S[32]['start'], cut33=S[33]['start'],
    cut35=S[35]['start'], cut36=S[36]['start'], fall=wt(36, '中试') + 0.15, valley=wt(36, '死亡之谷'), cut37=S[37]['start'],
)
EV['rh'] = EV['dive'] + 0.8; EV['hg'] = EV['dive'] + 1.3
BADGE_T = []

IMG1, IMG2 = img('1'), img('2')
BG_PAGE = bg_gild(backdrop=cover(IMG1, W, H), dim=0.10, key='page')
BG = bg_gild(key='plain')
BG_Z = bg_gild(leak=(0.75, 0.3), leak_col=ICE, k_leak=0.10, key='z', bokeh=False)

# ================================================================ 1–9（第四版开头）
def v1(t): return hook(t - EV['voice_in'], dict(human=EV['human'] - EV['voice_in'], gongke=EV['boom'] - EV['voice_in']))

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
    tl = t - EV['cut4']; f = BG.copy()
    put(f, GHOST, W * 0.62, H * 0.52, 0.08 * ease_out(seg(tl, 0, 0.6)), scale=1.0 + 0.015 * min(tl, 8))
    g = ease(seg(t, EV['gold'], EV['gold'] + 0.5)); sweep_x = lerp(PX - 400, PX + 400, seg(t, EV['gold'], EV['gold'] + 0.5))
    for n, (dx, ang, t0, k) in enumerate(DROPS):
        u = seg(tl, t0 * 0.9, t0 * 0.9 + 0.45)
        if u <= 0: continue
        yy = lerp(-300, PY - n * 6, ease_out(u, 2)); xx = PX + dx * (1 - u) * 0.6 + dx * 0.08
        put(f, PW[k], xx, yy, 1.0, scale=0.9, angle=ang * (1 - 0.6 * u))
        if g > 0: put(f, PG[k], xx, yy, g, scale=0.9, angle=ang * (1 - 0.6 * u))
    if 0 < seg(t, EV['gold'], EV['gold'] + 0.6) < 1:
        lay = np.zeros((H, W, 3), np.float32); cv2.line(lay, (int(sweep_x), 0), (int(sweep_x - 200), H), (255, 230, 170), 50)
        f += cv2.GaussianBlur(lay, (0, 0), 30) * 0.9
    if g > 0:
        lay = np.zeros((H, W, 3), np.float32)
        for (a, r, s_) in SPARK:
            k = (t * 0.8 + s_) % 1.0; p = (int(PX + (a - 0.5) * 520), int(PY - 120 - k * 360 * (0.5 + r)))
            cv2.circle(lay, p, 2 + int(3 * r), (np.array(GOLD) * g * (1 - k)).tolist(), -1, cv2.LINE_AA)
        f += lay + cv2.GaussianBlur(lay, (0, 0), 6)
    cnt = 719 if t > EV['land719'] else int(719 * ease_out(seg(tl, 0.15, 1.7), 2))
    put(f, number(f'{cnt}', '', 300, GOLD), W * 0.66, H * 0.46, ease_out(seg(tl, 0.1, 0.4)), scale=1.0 + 0.08 * max(0, 1 - abs(t - EV['land719']) / 0.15))
    put(f, LBL, W * 0.66 + 10, H * 0.46 + 190, ease_out(seg(tl, 0.5, 0.8)))
    if t >= EV['cut7']: f = zoom(f, 1.0 + 0.12 * ease(seg(t, EV['cut7'], EV['dive'])), 0.32, 0.55)
    return f
B_RH = make_card(560, 200, 'rect', 24, VIOLET, 0.6, '黎曼ζ函数', title_size=74, rim=0.5, rim_col=(210, 190, 255))
B_HG = make_card(520, 200, 'rect', 24, ROSE, 0.6, '霍奇猜想', title_size=74, rim=0.5, rim_col=(255, 190, 205))
def v78(t):
    if t < EV['dive']: return papers(t)
    k = t - EV['dive']
    if k < 0.35:
        f = zoom(papers(EV['dive']), 1.12 + 6 * ease_in(k / 0.35, 3), 0.30, 0.50); return whip(f + (k / 0.35) ** 3 * 255, k / 0.35, horiz=False)
    tz = k - 0.35; f = KJ.math_cosmos(2.5 + tz * 0.9, 6.0, bgimg=BG_Z); f += max(0, 1 - tz / 0.2) * 255
    put(f, B_RH, W * 0.24, H * 0.34, ease_out(seg(tz, 0.4, 0.7)), scale=0.85 + 0.15 * back_out(seg(tz, 0.4, 0.8)))
    put(f, B_HG, W * 0.27, H * 0.66, ease_out(seg(tz, 0.9, 1.2)), scale=0.85 + 0.15 * back_out(seg(tz, 0.9, 1.3)))
    return f
FIELDS = [('数论', SAPPHIRE, 470, 96, 1100, 780, '数论'), ('代数几何', TEAL, 430, 74, 1600, 560, '代数几何'), ('理论计算机', CORAL, 430, 60, 600, 560, '理论计算机'),
          ('数学物理', EMERALD, 340, 56, 1880, 900, None), ('组合数学', VIOLET, 330, 56, 300, 900, None), ('偏微分方程', ROSE, 320, 46, 1100, 300, None), ('算子代数', ICE, 300, 50, 1900, 240, None)]
FIMG = [make_card(sz, sz, 'circle', 0, c, 0.66, n, title_size=ts, rim=0.6, rim_col=tuple(min(255, int(v * 0.45 + 150)) for v in c)) for n, c, sz, ts, x, y, w in FIELDS]
t_more = wt(5, '等多个方向')
for j, (n, c, sz, ts, x, y, w) in enumerate(FIELDS): BADGE_T.append((wt(5, w) - 0.05) if w else t_more + 0.1 * (j - 3))
def v5(t):
    items = [(im, x, y, t0 - EV['cut5']) for im, (n, c, sz, ts, x, y, w), t0 in zip(FIMG, FIELDS, BADGE_T)]
    return badge_table(t - EV['cut5'], items, BG, dur=S[5]['dur'], rx=34, ry=-4, cy=H * 0.55, canvas=(2200, 1200), push=(1.0, 1.08))

LOCK = make_card(400, 300, 'rect', 26, INK, 0.58, '未公开模型', 'lock', title_size=52, ic_col=GOLD)
NEQ_A = make_card(330, 150, 'rect', 22, INK, 0.58, '数学研究', title_size=56, rim_col=GOLD, rim=0.7)
NEQ_B = make_card(330, 150, 'rect', 22, INK, 0.45, '普通任务', title_size=56)
NEQ = shadow(text('≠', F_BLACK, 110, GOLD), 8, (0, 3), 160)
def host(z0=1.0, cards=()):
    def fn(t):
        s = next((x for x in shots if x['start'] <= t < x['end']), shots[-1]); tl = t - s['start']
        f = zoom(cover(cam_frame(t), W, H).astype(np.float32), z0 + 0.03 * tl / s['dur'], 0.5, 0.35)
        for im, t0, x, y in cards:
            k = seg(t, t0, t0 + 0.3)
            if k > 0: put(f, im, x + 40 * (1 - ease_out(k)), y, k)
        return f
    return fn

# ================================================================ 10–11 向内索取 / 向外延伸（带小窗）
KC = (1180, 545); KR = 300
_r = np.random.default_rng(12)
KN = _r.uniform(0, 1, (150, 2))                            # 圈内知识点
GRID = np.array([(KC[0] + (i % 15 - 7) * 26, KC[1] + (i // 15 - 4.5) * 26) for i in range(150)], np.float32)   # 整理后的网格
STARS = []                                                  # 圈外新星：一条平滑、等距的「规律」弧线
for k in range(15):
    a = math.radians(-62 + k * 9.0); rr = KR * 1.42 + 18 * math.sin(k * 1.2566)
    STARS.append((KC[0] + rr * math.cos(a), KC[1] + rr * math.sin(a)))
C_DOC = make_card(150, 150, 'rect', 24, SAPPHIRE, 0.62, None, 'doc', rim=0.5)
C_LST = make_card(150, 150, 'rect', 24, TEAL, 0.62, None, 'list', rim=0.5)
W_IN = shadow(text('向内索取', F_BLACK, 104, WHITE, 0.08), 10, (0, 4), 180)
W_OUT = shadow(glow_rgba(text('向外延伸', F_BLACK, 104, GOLD, 0.08), GOLD, 18, 0.4), 10, (0, 4), 180)

def pip2(f, t, cx=220, cy=H - 260, d=240, u=1.0, out=0.0):
    if u <= 0 or out >= 1: return f
    d2 = int(d * back_out(u) * (1 - ease_in(out, 2)))
    if d2 < 8: return f
    # 圆窗只保留头肩，缩小外圈后仍能看清表情；全片共用这一构图。
    src = cam_frame(t)
    ih, iw = src.shape[:2]; side = int(min(ih * 0.66, iw))
    x0 = (iw - side) // 2; y0 = int(ih * 0.035)
    fr = cover(src[y0:y0 + side, x0:x0 + side], d2, d2)
    m = Image.new('L', (d2, d2), 0); ImageDraw.Draw(m).ellipse([2, 2, d2 - 3, d2 - 3], fill=255)
    im = Image.fromarray(np.dstack([fr, np.array(m)]).astype(np.uint8), 'RGBA')
    ring = Image.new('RGBA', (d2 + 10, d2 + 10), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse([1, 1, d2 + 8, d2 + 8], outline=(255, 255, 255, 220), width=3)
    ring.alpha_composite(im, (5, 5))
    return put(f, shadow(ring, 16, (0, 8), 170), cx, cy)

def v1011(t):
    f = BG.copy(); lay = np.zeros((H, W, 3), np.float32)
    u0 = ease_out(seg(t, EV['cut10'], EV['cut10'] + 0.5))
    outk = ease(seg(t, EV['outward'], EV['outward'] + 0.6))
    cv2.circle(lay, KC, int(KR * (0.9 + 0.1 * u0)), (np.array((230, 236, 245)) * u0 * (1 - 0.45 * outk)).tolist(), 3, cv2.LINE_AA)
    # 圈内知识点：向内索取 → 收拢、整理成网格
    tidy = ease(seg(t, EV['inward'], EV['tidy'] + 0.6))
    for n, (a, rr) in enumerate(KN):
        ang = a * 2 * np.pi + t * 0.12 * (1 - tidy); r0 = math.sqrt(rr) * KR * 0.85
        p0 = np.array([KC[0] + r0 * math.cos(ang), KC[1] + r0 * math.sin(ang)])
        p = p0 * (1 - tidy) + GRID[n] * tidy
        cv2.circle(lay, (int(p[0]), int(p[1])), 4, (np.array(ICE) * u0 * (0.55 + 0.45 * tidy) * (1 - 0.4 * outk)).tolist(), -1, cv2.LINE_AA)
    if t >= EV['outward']:                                    # 金光冲出边界
        k = seg(t, EV['outward'], EV['outward'] + 0.5); a = math.radians(-35); L = KR * (0.1 + 1.6 * ease_out(k))
        p1 = (int(KC[0] + L * math.cos(a)), int(KC[1] + L * math.sin(a)))
        cv2.line(lay, KC, p1, GOLD, 6, cv2.LINE_AA); cv2.circle(lay, p1, 11, (255, 245, 220), -1, cv2.LINE_AA)
        hit = seg(t, EV['outward'] + 0.25, EV['outward'] + 0.7)
        if 0 < hit < 1:
            bp = (int(KC[0] + KR * math.cos(a)), int(KC[1] + KR * math.sin(a))); cv2.circle(lay, bp, int(20 + 120 * hit), (np.array(WHITE) * (1 - hit)).tolist(), 3, cv2.LINE_AA)
    if t >= EV['rule'] - 0.3:                                 # 新的规律：圈外星点依次亮起并连成线
        k = seg(t, EV['rule'] - 0.3, EV['rule'] + 1.2); n_on = int(len(STARS) * k)
        for j in range(n_on):
            p = tuple(int(v) for v in STARS[j]); cv2.circle(lay, p, 7, GOLD, -1, cv2.LINE_AA)
            if j > 0: cv2.line(lay, tuple(int(v) for v in STARS[j - 1]), p, (np.array(GOLD) * 0.8).tolist(), 2, cv2.LINE_AA)
    f += lay + cv2.GaussianBlur(lay, (0, 0), 4) * 0.8 + cv2.GaussianBlur(lay, (0, 0), 18) * 0.6
    ia = 1 - 0.7 * tidy
    put(f, C_DOC, KC[0] - 90, KC[1], ease_out(seg(t, EV['doc'] - 0.1, EV['doc'] + 0.2)) * ia, scale=0.8 + 0.2 * back_out(seg(t, EV['doc'] - 0.1, EV['doc'] + 0.3)))
    put(f, C_LST, KC[0] + 90, KC[1], ease_out(seg(t, EV['lst'] - 0.1, EV['lst'] + 0.2)) * ia, scale=0.8 + 0.2 * back_out(seg(t, EV['lst'] - 0.1, EV['lst'] + 0.3)))
    put(f, W_IN, KC[0] - 250, KC[1] - KR - 70, ease_out(seg(t, EV['inward'], EV['inward'] + 0.3)) * (1 - 0.75 * outk))
    put(f, W_OUT, KC[0] + 420, KC[1] - KR - 70, ease_out(seg(t, EV['outward'] + 0.3, EV['outward'] + 0.6)))
    out = seg(t, last_voice(11) - 0.35, last_voice(11) - 0.05)            # 口播一停（画面定住）小窗就收掉
    return pip2(f, t, u=ease_out(seg(t, EV['cut10'], EV['cut10'] + 0.4)), out=out)

# ================================================================ 13 大字：使用知识 → 参与创造知识
T_USE = shadow(text('使用知识', F_BLACK, 130, (150, 155, 166), 0.08), 10, (0, 4), 160)
T_CREATE = to_rgba_np(metal('参与创造知识', 210, 0.08))
DUST = np.random.default_rng(31).uniform(0, 1, (120, 3))
def v13(t):
    f = BG.copy(); lay = np.zeros((H, W, 3), np.float32)
    for (x, y, s_) in DUST:
        p = (int(x * W), int((y * H - t * 18 * (0.3 + s_)) % H)); cv2.circle(lay, p, 1 + int(2 * s_), (np.array(GOLD) * 0.35 * s_).tolist(), -1, cv2.LINE_AA)
    f += lay + cv2.GaussianBlur(lay, (0, 0), 3)
    u1 = ease_out(seg(t, EV['use'] - 0.05, EV['use'] + 0.25)); back = ease_in(seg(t, EV['create'] - 0.35, EV['create'] - 0.05))
    put(f, T_USE, W / 2, H / 2, u1 * (1 - back), scale=1.0 - 0.3 * back)
    hit = EV['create']
    if t >= hit:
        u = seg(t, hit, hit + 0.25)
        put(f, sweep(T_CREATE, seg(t, hit + 0.4, hit + 1.5)), W / 2, H / 2, ease_out(u, 2), scale=(1.3 - 0.3 * ease_out(u, 4)) * (1 + 0.015 * (t - hit)))
        f += max(0.0, 1 - (t - hit) / 0.22) * 140
        f = shake(f, max(0.0, 1 - (t - hit) / 0.35), int(t * 30))
    return f

# ================================================================ 15 表情包
MEME = img('3')[:420]
MEME_CARD = photo(MEME, 900, border=14)
def v15(t):
    tl = t - EV['meme']
    f = cv2.GaussianBlur(cover(MEME, W, H).astype(np.float32), (0, 0), 30) * 0.3 + BG * 0.7
    k = seg(tl, 0, 0.22)
    put(f, MEME_CARD, W / 2, H / 2 - 30, k, scale=(1.3 - 0.3 * back_out(k)) * (1 + 0.02 * tl), angle=-4)
    return shake(f, max(0, 1 - tl / 0.4), int(tl * 30))

# ================================================================ 17 片名：AI for Science（素材4 全息转盘做景深，去冷调）
V4 = Vid(os.path.join(MAT, '4.空镜.mp4'))
T_AFS = to_rgba_np(metal('AI for Science', 220, 0.03, fp=F_BLACK))
PART = np.random.default_rng(9).uniform(0, 1, (260, 3))
def v17(t):
    tl = t - S[17]['start']
    v = cover(V4.get(50.0 + tl * 0.6), W, H).astype(np.float32); g = v.mean(2, keepdims=True)
    v = (v * 0.35 + g * 0.65) * np.array([1.08, 1.0, 0.9])                  # 去饱和、偏暖
    f = BG * 0.55 + cv2.GaussianBlur(v, (0, 0), 8) * 0.55
    lay = np.zeros((H, W, 3), np.float32); hit = EV['afs']
    conv = ease_in(seg(t, hit - 1.2, hit), 2)
    for (a, r, s_) in PART:
        ang = a * 2 * np.pi; rr = (0.25 + r) * W * 0.7 * (1 - conv) + 40 * s_
        p = (int(W / 2 + rr * math.cos(ang) * (0.6 + 0.4 * s_)), int(H / 2 + rr * math.sin(ang) * 0.55))
        cv2.circle(lay, p, 2 + int(2 * s_), (np.array(GOLD if s_ > 0.4 else ICE) * (0.5 + 0.5 * s_) * (1 - seg(t, hit - 0.05, hit + 0.25))).tolist(), -1, cv2.LINE_AA)
    f += lay + cv2.GaussianBlur(lay, (0, 0), 4) + cv2.GaussianBlur(lay, (0, 0), 16) * 0.6
    if t >= hit:
        u = seg(t, hit, hit + 0.3)
        put(f, sweep(T_AFS, seg(t, hit + 0.5, hit + 1.7)), W / 2, H / 2, ease_out(u, 2), scale=(1.25 - 0.25 * ease_out(u, 4)) * (1 + 0.012 * (t - hit)))
        f += max(0.0, 1 - (t - hit) / 0.3) * 160
        f = shake(f, max(0.0, 1 - (t - hit) / 0.4), int(t * 30))
    return bloom(f, 0.2)

# ================================================================ 18 → 过渡：话题转回国内（停顿落在画面上）
def v18(t):
    if t < EV['bridge']: return host(1.06)(t)
    k = t - EV['bridge']
    v = cover(V4.get(0.5 + k * 0.8), W, H).astype(np.float32); g = v.mean(2, keepdims=True)
    f = (v * 0.5 + g * 0.5) * np.array([1.06, 1.0, 0.9])
    return zoom(f, 1.0 + 0.05 * k, 0.5, 0.5)

VIS = {1: v1, 2: F2, 3: lambda t: F3a(t) if t < EV['split3'] else whip(F3b(t), max(0, 1 - (t - EV['split3']) / 0.2)),
       4: papers, 5: v5, 6: host(1.06, [(LOCK, EV['lock'], 1520, 420)]), 7: v78, 8: v78,
       9: host(1.0, [(NEQ_A, EV['neqA'] - 0.05, 1540, 330), (NEQ, EV['neq'] - 0.05, 1540, 488), (NEQ_B, EV['neqB'] - 0.05, 1540, 640)]),
       10: v1011, 11: v1011, 12: host(1.08), 13: v13, 14: host(1.0), 15: v15, 16: host(1.08), 17: v17, 18: v18}
CUTS = ['cut2', 'cut4', 'cut5', 'cut7', 'cut9', 'cut10', 'cut19']
QUIET = {'cut22', 'cut26', 'cut30', 'cut32', 'cut33', 'cut35'}   # 同一段落里素材换素材：硬切，不甩镜、不加转场声（避免音效泛滥）
SFX_MORE = []; STILLS = []
for _f in ('seg3_vis.py', 'seg4_vis.py', 'seg5_vis.py', 'seg6_vis.py'):
    if os.path.exists(os.path.join(HERE, _f)): exec(open(os.path.join(HERE, _f), encoding='utf-8').read())
_old = None
def vis_of(i):
    global _old
    if i in VIS: return VIS[i]
    if _old is None: _old = build_vis()
    sbi, vv = _old
    return lambda t: vv[i](t - sbi[i]['start'], sbi[i]['dur'])

NO_SUB = {13, 17, 36}
def sub_now(t):
    s = next((x for x in shots if x['start'] <= t < x['end']), None)
    if s is None or s['i'] in NO_SUB or t > s['chars'][-1][1] + 0.45: return ''      # 说完就收字幕
    return sub_at(t)

TAIL = 0.05  # 最后一句后仅留 0.21 秒；源视频仍有真实动作，不定格延长
END_FADE = 0.45
def frame(t_out):
    fade = ease(seg(PRE + TOTAL + TAIL - t_out, 0, END_FADE))
    return frame_(t_out) * fade
def frame_(t_out):
    t = t_out - PRE; CUR_T[0] = max(t, 0)
    if t < 0: return hook(t - EV['voice_in'], dict(human=EV['human'] - EV['voice_in'], gongke=EV['boom'] - EV['voice_in']))
    s = next((x for x in shots if x['start'] <= t < x['end']), shots[-1])
    f = vis_of(s['i'])(t)
    for c in CUTS + ['bridge']:
        if c in QUIET: continue
        t0 = EV[c]
        if 0 <= t - t0 < 0.2: f = whip(f, 1 - (t - t0) / 0.2)
        if 0 < t0 - t < 0.1: f = whip(f, (0.1 - (t0 - t)) / 0.1 * 0.8)
    # 品牌句 → 回顾段：两段出镜取景不同，用短暂淡过背景遮住跳切。
    cut = EV['cut62']
    if cut - 0.12 < t < cut + 0.16:
        opacity = ease(seg(t, cut - 0.12, cut)) if t < cut else 1 - ease(seg(t, cut, cut + 0.16))
        f = f * (1 - opacity) + BG * opacity
    subtitle(f, sub_now(t))
    return f

DUR = PRE + TOTAL + TAIL
A_OUT, B_OUT = WIN if WIN else (0.0, DUR)

# ================================================================ 声音
SR = 44100
MUSD = os.path.join(REPO, '音乐素材', '旧库') + '/'      # 旧库里用到的曲子和 7 个音效（原在 aliang2052/Tempsucai）
def load(p):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-vn', '-ac', '2', '-ar', str(SR), f'{OUT}/_t.wav'], check=True)
    with wave.open(f'{OUT}/_t.wav') as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
def smooth_audio(x, width):
    width = max(1, int(width))
    padded = np.pad(x, (width // 2, (width - 1) // 2))
    cumulative = np.concatenate(([0.0], np.cumsum(padded, dtype=np.float64)))
    return ((cumulative[width:] - cumulative[:-width]) / width).astype(np.float32)

def peak_of(x): return smooth_audio(np.abs(x).mean(1), 441).argmax() / SR
def db(x): return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)

def filter_audio(x, filters):
    """保留浮点余量，滤波过程不先压成 16bit 或削波。"""
    if not filters: return x
    r = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2',
                        '-i', 'pipe:0', '-af', filters, '-f', 'f32le', 'pipe:1'],
                       input=x.astype('<f4').tobytes(), capture_output=True, check=True)
    y = np.frombuffer(r.stdout, '<f4').reshape(-1, 2)
    if len(y) != len(x): raise ValueError('音频滤波改变了样本长度')
    return y.copy()

# 配乐段落：(曲子, 曲内对齐点, 时间线对齐点, 从, 到)
MUSIC = [dict(file='音乐/悬疑-Dance for me walls.mp3', src=21.09, at=EV['boom'], frm=EV['boom'] - 2.5, to=EV['bridge'] + 0.9, fin=0.4, fout=1.1, dip=EV['boom']),
         dict(file='音乐/Time - Hans Zimmer.mp3', src=30.0, at=EV['bridge'], frm=EV['bridge'] - 0.3, to=EV['fall'] - 0.02, fin=1.0, fout=0.12, dip=None),   # 死亡之谷：曲线栽下去那一刻配乐断掉
         dict(file='音乐/In Motion - Trent Reznor & Atticus Ross.m4a', src=0.14, at=EV['cut37'], frm=EV['cut37'] - 0.05, to=EV.get('m3_end', EV['cut37'] + 40), fin=0.05, fout=1.2, dip=[EV['n400']]),
         dict(file='音乐/大气史诗-破晓曙光.mp3', src=233.45, at=last_voice(71) + 1.0, frm=EV['cut61'] - 0.1, to=TOTAL + TAIL, fin=0.5, fout=2.5, dip=None, ref=190.0)]   # 尾音落在最后一句说完 1 秒后
SFX = {'rise': '上升-whoosh rise.mp3', 'whoosh': '转场-Whoosh.mp3', 'swish': '转场-Windy swish.mp3', 'gate': '重音-Gate Hit.mp3', 'thud': '重音-Thud Hit C.mp3', 'dong': '重音-咚 重磅.mp3', 'rrise': '上声音-reverse rise.mp3'}
def sfx_plan():
    P = [('蓄力→人声进', EV['voice_in'], 'rise', 0.55), ('冲进隧道', EV['voice_in'], 'thud', 0.40), ('攻克·问号炸开', EV['boom'], 'dong', 1.0)]
    for c in CUTS:
        if c not in QUIET: P.append((f'转场 {c}', EV[c], 'whoosh', 0.45))
    P += [('截图换页', EV['split3'], 'swish', 0.35), ('719 停住', EV['land719'], 'gate', 0.50)]
    for j, t0 in enumerate(BADGE_T): P.append((f'徽章{j + 1}', t0 + 0.1, 'thud', 0.20 if j < 3 else 0.12))
    P += [('未公开卡', EV['lock'] + 0.08, 'thud', 0.22), ('变金', EV['gold'] + 0.1, 'gate', 0.38), ('冲进论文', EV['dive'] + 0.3, 'swish', 0.45),
          ('ζ 出现', EV['dive'] + 0.35, 'thud', 0.40), ('黎曼卡', EV['rh'], 'thud', 0.16), ('霍奇卡', EV['hg'], 'thud', 0.16),
          ('数学研究卡', EV['neqA'] + 0.05, 'thud', 0.16), ('普通任务卡', EV['neqB'] + 0.05, 'thud', 0.16), ('≠', EV['neq'] + 0.05, 'gate', 0.22),
          ('写文章卡', EV['doc'] + 0.05, 'thud', 0.15), ('总结卡', EV['lst'] + 0.05, 'thud', 0.15), ('向内索取', EV['inward'] + 0.1, 'thud', 0.25),
          ('金光蓄力', EV['outward'] + 0.3, 'rise', 0.35), ('冲破边界', EV['outward'] + 0.3, 'gate', 0.45), ('新规律连线', EV['rule'], 'swish', 0.25),
          ('使用知识', EV['use'], 'thud', 0.18), ('创造·蓄力', EV['create'], 'rise', 0.5), ('参与创造知识', EV['create'], 'dong', 0.9),
          ('表情包', EV['meme'] + 0.08, 'gate', 0.55), ('片名·蓄力', EV['afs'], 'rise', 0.6), ('AI for Science', EV['afs'], 'dong', 1.0),
          ('转回国内', EV['bridge'], 'swish', 0.4),
          ('研究院所', wt(22, '科研院所') + 0.05, 'thud', 0.18), ('高校', wt(22, '高校') + 0.05, 'thud', 0.18), ('科技企业', wt(22, '科技企业') + 0.05, 'thud', 0.18),
          ('章节卡·化工', EV['ch_in'], 'gate', 0.45), ('章节卡收', EV['cut26'], 'whoosh', 0.4),
          ('实验室→工厂', S[29]['start'] + 0.15, 'swish', 0.4), ('资源条', S[34]['start'], 'thud', 0.2),
          ('曲线栽下去', EV['fall'], 'thud', 0.55), ('死亡之谷', EV['valley'], 'dong', 1.0)]
    return P + SFX_MORE

if os.path.exists(os.path.join(HERE, 'sound.py')): exec(open(os.path.join(HERE, 'sound.py'), encoding='utf-8').read())   # 整片声音规划覆盖上面的默认值

def build_audio():
    RAW = {'vo': load(VO_WAV), 'cam': load(os.path.join(MAT, '口播', '1080-压缩版.mp4')), 'r20': load(os.path.join(MAT, '口播', '科大讯飞1024结尾-声音克隆.mp3'))}
    for start, end, speed in globals().get('VOICE_TIGHTEN', []):
        # 只重定时指定词尾，保留音高；腾出的源区间由 SOURCE_SKIPS 统一移除。
        a, b = round(start * SR), round(end * SR)
        count = round((end - start) * SR / speed)
        result = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR),
                                 '-ac', '2', '-i', 'pipe:0', '-af', f'atempo={speed},apad=whole_len={count},atrim=end_sample={count}',
                                 '-f', 'f32le', 'pipe:1'], input=RAW['vo'][a:b].astype('<f4').tobytes(),
                                capture_output=True, check=True)
        tightened = np.frombuffer(result.stdout, '<f4').reshape(-1, 2)
        assert len(tightened) == count
        RAW['vo'][a:b] = 0
        RAW['vo'][a:a + count] = tightened
    phrase = globals().get('VOICE_PHRASE_TIGHTEN')
    if phrase:
        # 先保留此前的词内压缩与去空白，再整句保音高加速；画面使用同一时间映射。
        spans, cursor = [], phrase['start']
        for left, right in phrase['gaps'] + [(phrase['end'], phrase['end'])]:
            part = RAW['vo'][round(cursor * SR):round(left * SR)].copy()
            if len(part):
                fade = min(round(.003 * SR), len(part) // 2)
                if cursor != phrase['start']: part[:fade] *= np.linspace(0, 1, fade)[:, None]
                if left != phrase['end']: part[-fade:] *= np.linspace(1, 0, fade)[:, None]
                spans.append(part)
            cursor = right
        count = round(phrase['duration'] * SR)
        result = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2',
                                 '-i', 'pipe:0', '-af', f"atempo={phrase['speed']},apad=whole_len={count},atrim=end_sample={count}",
                                 '-f', 'f32le', 'pipe:1'], input=np.concatenate(spans).astype('<f4').tobytes(),
                                capture_output=True, check=True)
        tightened = np.frombuffer(result.stdout, '<f4').reshape(-1, 2)
        assert len(tightened) == count
        a, b = round(phrase['start'] * SR), round(phrase['end'] * SR)
        RAW['vo'][a:b] = 0
        RAW['vo'][a:a + count] = tightened
    def rms_src(src): return np.sqrt(np.mean(np.concatenate([RAW[src][int(a * SR):int(b * SR)] for a, b, o, sr in audio_pieces if sr == src]) ** 2))
    GN = {k: rms_src('vo') / rms_src(k) for k in ('vo', 'cam', 'r20')}       # 三种录音响度对齐
    N = int((DUR + 0.5) * SR); voice = np.zeros((N, 2), np.float32)
    for piece_index, (a0, a1, o, sr) in enumerate(audio_pieces):
        x = RAW[sr][round(a0 * SR):round(a1 * SR)] * GN[sr]
        speed = audio_speeds.get(o, 1.0)
        count = round((a1 - a0) * SR / speed)
        if speed != 1.0:
            result = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2',
                                     '-i', 'pipe:0', '-af', f'atempo={speed},apad=whole_len={count},atrim=end_sample={count}',
                                     '-f', 'f32le', 'pipe:1'], input=x.astype('<f4').tobytes(), capture_output=True, check=True)
            x = np.frombuffer(result.stdout, '<f4').reshape(-1, 2)
        i = round((o + PRE) * SR); n = min(len(x), N - i)
        joined_in = piece_index > 0 and abs(audio_pieces[piece_index - 1][2] + (audio_pieces[piece_index - 1][1] - audio_pieces[piece_index - 1][0]) / audio_speeds.get(audio_pieces[piece_index - 1][2], 1.0) - o) < 1 / SR
        joined_out = piece_index + 1 < len(audio_pieces) and abs(o + (a1 - a0) / speed - audio_pieces[piece_index + 1][2]) < 1 / SR
        ki, ko = int((0.003 if joined_in else 0.025) * SR), int((0.003 if joined_out else 0.025) * SR)
        fd = np.ones(n, np.float32); fd[:ki] = np.linspace(0, 1, ki); fd[-ko:] = np.linspace(1, 0, ko)
        voice[i:i + n] += x[:n] * fd[:, None]
    voice = filter_audio(voice, globals().get('VOICE_FILTER'))
    vmask = np.abs(voice).mean(1) > 1e-7; v_db = db(voice[vmask])
    act = smooth_audio(np.abs(voice).mean(1), .05 * SR) > 10 ** ((v_db - 25) / 20)
    env = np.zeros(N, np.float32); e = 0.0; up, dn = 1 / (0.12 * SR), 1 / (0.8 * SR); hold = int(0.6 * SR); last = -10 ** 9
    for k in range(N):                               # 说话间换气（<0.6 秒）不抬音乐，避免一呼一吸地起伏
        if act[k]: last = k
        e = min(1.0, e + up) if k - last < hold else max(0.0, e - dn); env[k] = e
    hostm = np.zeros(N, np.float32)                     # 真人出镜时段（音乐再压低一档）
    for s_ in shots:
        if s_['i'] in globals().get('HOST_SHOTS', set()):
            # 真人后的章节卡 / 国内转场不再沿用真人的低配乐档。
            end = min(s_['end'], last_voice(s_['i'])) if s_['i'] in (18, 25, 50) else s_['end']
            hostm[int((PRE + s_['start']) * SR):int((PRE + end) * SR)] = 1.0
    hostm = smooth_audio(hostm, .6 * SR)
    music = np.zeros((N, 2), np.float32)
    for m in MUSIC:
        tr = load(m['file'] if m['file'].startswith('/') else MUSD + m['file'])
        o0 = PRE + m['frm']; s0 = m['src'] - (m['at'] - m['frm']); n = round((m['to'] - m['frm']) * SR)
        source_start = round(s0 * SR)
        if source_start < 0 or source_start + n > len(tr):
            raise ValueError(f"配乐素材长度不足：{m['file']} {s0:.2f}s + {n / SR:.2f}s")
        x = filter_audio(tr[source_start:source_start + n].copy(), globals().get('MUSIC_DYNAMICS'))
        m_db = db(x)  # 用实际播放段归一，避免不相关的参考段带来换曲电平跳变
        i0 = round(o0 * SR)
        fi, fo = min(len(x), round(m['fin'] * SR)), min(len(x), round(m['fout'] * SR))
        # 相邻段同长交叉淡化：sin/cos 等功率，交接处不出现音量坑。
        x[:fi] *= np.sin(np.linspace(0, np.pi / 2, fi))[:, None]
        x[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo))[:, None]
        gg = 10 ** ((v_db + m.get('gap', -5) - m_db) / 20); gu = 10 ** ((v_db + m.get('under', -12) - m_db) / 20); gh = 10 ** ((v_db + m.get('host', -12) - m_db) / 20)
        e_ = env[i0:i0 + len(x)]; h_ = hostm[i0:i0 + len(x)]
        gain = (gg + (gu - gg) * e_) * (1 - h_) + gh * h_          # 真人出镜整段压低，不随换气起伏
        music[i0:i0 + len(x)] += x * gain[:len(x), None]
    music = filter_audio(music, globals().get('MUSIC_FILTER'))
    sfx = np.zeros((N, 2), np.float32); cache = {}; rep = []
    for name, te, key, gain in sfx_plan():
        if key not in cache:
            y = load(MUSD + '音效/' + SFX[key])
            pk = peak_of(y)
            # 活跃部分 RMS 归一；转场比重击再低 4 dB，限制尖峰。
            active = np.abs(y).mean(1) > np.abs(y).max() * .04
            target = v_db - (12 if key in ('whoosh', 'swish', 'rise') else 8)
            scale = min(10 ** ((target - db(y[active])) / 20), .35 / (np.abs(y).max() + 1e-9))
            y *= scale
            fade = min(round(.02 * SR), len(y) // 2)
            y[:fade] *= np.linspace(0, 1, fade)[:, None]
            y[-fade:] *= np.linspace(1, 0, fade)[:, None]
            cache[key] = (y, pk)
        y, pk = cache[key]; st = PRE + te - pk; i = round(st * SR); j0 = max(0, -i); i = max(0, i); n = min(len(y) - j0, N - i)
        sfx[i:i + n] += y[j0:j0 + n] * gain; rep.append((name, PRE + te, key))
    return voice, music, sfx, rep, v_db, vmask

if mode == 'stills':
    pts = [(n_, PRE + t_) for n_, t_ in STILLS] if STILLS else [(n_, PRE + t_) for n_, t_ in [('苦·周期长', S[19]['start'] + 0.5), ('三类机构', wt(22, '科技企业') + 0.4), ('探索', S[23]['start'] + 0.6),
           ('章节卡', EV['ch_in'] + 0.5), ('化工', S[26]['start'] + 0.5), ('头痛', S[27]['start'] + 1.2), ('实验室', S[28]['start'] + 1.0), ('→工厂', S[29]['start'] + 1.5),
           ('冷凝管', S[30]['start'] + 0.7), ('调参数', S[32]['start'] + 1.2), ('每多试一次', S[34]['start'] + 1.5), ('曲线', EV['fall'] - 0.2), ('栽下去', EV['fall'] + 0.3), ('死亡之谷', EV['valley'] + 0.8)]]
    ims = []
    for name, tt in pts:
        im = Image.fromarray(np.clip(frame(tt), 0, 255).astype(np.uint8)).resize((640, 360)); ImageDraw.Draw(im).text((8, 6), name, fill=(255, 230, 0), font=font(F_MED, 22)); ims.append(im)
    g = Image.new('RGB', (640 * 3, 360 * ((len(ims) + 2) // 3)))
    for k, im in enumerate(ims): g.paste(im, ((k % 3) * 640, (k // 3) * 360))
    g.save(f'{OUT}/stills.jpg', quality=86); print('stills ok')

if mode == 'video':
    wr = Writer(f'{OUT}/win_video.mp4', FPS, crf=18)
    for n in range(int(round(A_OUT * FPS)), int(round(B_OUT * FPS))): wr.write(frame(n / FPS))   # 按帧号切，分段拼接不丢帧不重帧
    wr.close(); print('video ok', A_OUT, B_OUT)

if mode in ('audio', 'check'):
    voice, music, sfx, rep, v_db, vmask = build_audio()
    a, b = int(A_OUT * SR), int(B_OUT * SR)
    if mode == 'check':
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        matplotlib.rcParams['font.family'] = ['Noto Sans CJK JP']
        d = 441; tt = np.arange(a, b, d) / SR
        def envd(x): e = np.abs(x[a:b]).mean(1); return 20 * np.log10(np.convolve(e, np.ones(d) / d, 'same')[::d] + 1e-5)
        fig, ax = plt.subplots(figsize=(26, 7))
        ax.plot(tt, envd(voice)[:len(tt)], lw=0.6, color='#555', label='人声'); ax.plot(tt, envd(music)[:len(tt)], lw=0.9, color='#d4a017', label='配乐'); ax.plot(tt, envd(sfx)[:len(tt)], lw=0.7, color='#2a7fd4', label='音效')
        for name, te, key in rep:
            if A_OUT <= te <= B_OUT: ax.axvline(te, color='#c0392b', lw=0.6, alpha=0.6); ax.text(te, -8, name, rotation=90, fontsize=7, va='top', color='#c0392b')
        for s in shots:
            if A_OUT <= s['start'] + PRE <= B_OUT: ax.axvline(s['start'] + PRE, color='#27ae60', lw=1.2, alpha=0.5, ls='--')
        ax.set_ylim(-75, 0); ax.set_xlim(A_OUT, B_OUT); ax.set_xticks(np.arange(int(A_OUT), B_OUT, 1)); ax.grid(alpha=0.2); ax.legend(loc='lower right')
        ax.set_title('声画对位：红线=画面事件（音效峰值对齐处）  绿虚线=镜头切换'); fig.tight_layout(); fig.savefig(f'{OUT}/sync.png', dpi=80)
        wv = vmask[a:b]; mm = music[a:b]; mv = np.abs(mm).mean(1) > 0
        print(f'人声 {v_db:.1f} dB；说话时配乐 {db(mm[wv & mv]):.1f} dB；停顿时配乐 {db(mm[~wv & mv]):.1f} dB')
    if mode == 'audio':
        mix = voice + music + sfx
        # 先留余量，再做响度归一；不能先 clip 再归一，否则失真已写入。
        peak = float(np.abs(mix).max())
        mix *= min(1.0, 0.90 / max(peak, 1e-9))
        with wave.open(f'{OUT}/full_raw.wav', 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
        first = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', f'{OUT}/full_raw.wav',
                                '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                               capture_output=True, text=True, check=True)
        measured, _ = json.JSONDecoder().raw_decode(first.stderr[first.stderr.rfind('{'):])
        af = ('loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:'
              f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
              f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
              f"offset={measured['target_offset']}")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/full_raw.wav', '-af', af, '-ar', '44100', f'{OUT}/full_audio.wav'], check=True)
        with open(f'{OUT}/响度测量.json', 'w') as f:
            json.dump(dict(pre_normalization=measured, float_mix_peak=peak,
                           voice_db=float(v_db), music_under_voice_db=float(db(music[vmask])),
                           music_sections=len(MUSIC), sfx_events=rep,
                           music_handoffs=[dict(time=PRE + (left['to'] + right['frm']) / 2,
                               overlap=left['to'] - right['frm'],
                               rms_before=float(db(music[round((PRE + right['frm'] - .5) * SR):round((PRE + right['frm']) * SR)])),
                               rms_mid=float(db(music[round((PRE + (left['to'] + right['frm']) / 2 - .25) * SR):round((PRE + (left['to'] + right['frm']) / 2 + .25) * SR)])),
                               rms_after=float(db(music[round((PRE + left['to']) * SR):round((PRE + left['to'] + .5) * SR)])))
                               for left, right in zip(MUSIC, MUSIC[1:])],
                           sfx_peak=float(np.abs(sfx).max()),
                           voice_peak=float(np.abs(voice).max())), f, ensure_ascii=False, indent=2)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{A_OUT}', '-to', f'{B_OUT}', '-i', f'{OUT}/full_audio.wav', f'{OUT}/win_audio.wav'], check=True)
        print('audio ok')
