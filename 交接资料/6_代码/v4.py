# v4 full-film renderer (segments). Segment 1 scenes come from sample.py (valid until output 44.6).
import sys, json, subprocess
sys.path.insert(0, '/tmp/claude-0/mock'); sys.path.insert(0, '/tmp/claude-0/build')
import numpy as np, cv2
from PIL import Image, ImageDraw
import own as o, own2 as q, style3 as st
import sample as S1
from sample import ease, back_out, B, put, xform, Vid, host, host_full, pen_circle, pen_x, crude
W, H, FPS = 1920, 1080, 30
R = o.R; P = o.P; CR = P + '/剪辑素材/'; SR = P + '/素材/'
NARR_DUR = 207.4667
INSERTS = [(42.8, 1.8, 'title'), (72.25, 5.4, 'meme'), (83.72, 1.0, 'brush'), (121.1, 1.0, 'brush'), (176.93, 1.0, 'brush')]
def T(n): return n + sum(d for a, d, _ in INSERTS if a < n - 1e-9)
def PT(a):
    t0 = T(a) if a > INSERTS[0][0] else a
    t0 = a + sum(d for x, d, _ in INSERTS if x < a - 1e-9); d = [d for x, d, _ in INSERTS if abs(x - a) < 1e-6][0]; return t0, t0 + d
def N(t):
    off = 0
    for a, d, _ in INSERTS:
        if t < a + off: return t - off
        if t < a + off + d: return None
        off += d
    return t - off
TOTAL = T(NARR_DUR)
SFX = []
def X(t, kind, **kw): SFX.append(dict(at=round(t, 3), kind=kind, **kw))
SC = []
def S(n0, n1, fn, kind='other', out=False):
    SC.append(((n0 if out else T(n0)), (n1 if out else T(n1)), fn, kind))

BG = o.bg(); BGW = o.bg(tint='warm')
def host_sc(z=1.0, push=0.02):
    return lambda t, t0, t1: host_full(N(t), z * (1 + push * (t - t0) / max(t1 - t0, .1)))
def hf_small(t):
    n = N(t); return cv2.resize(host.get(n if n is not None else 72.0), (1280, 720))

# ======================= SEGMENT 2: narration 42.8 -> 72.25 (+ meme)
S(42.8 + 1e-6, 48.45, host_sc(1.0), 'host')
# SVG = drawing with code: a 2024 pelican drawn stroke-by-stroke with vector anchors/handles
SVG_IMG = crude[1]
def svg_scene(t, t0, t1):
    tl = t - t0; f = BG.copy()
    img = cv2.resize(SVG_IMG, (720, 720), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); ink = (gray < 200).astype(np.uint8)
    # reveal by angle sweep (like a pen drawing)
    yy, xx = np.mgrid[0:720, 0:720]; ang = (np.arctan2(yy - 360, xx - 360) + np.pi) / (2 * np.pi)
    frac = ease(tl / 1.9); m = (ang < frac).astype(np.float32)[..., None]
    paper = np.full((720, 720, 3), 248, np.uint8)
    drawn = (img * m + paper * (1 - m)).astype(np.uint8)
    card = B(st.photo_card(drawn, 720)); put(f, card, 960, 520)
    # anchor points + bezier handles along the drawn ink
    pts = np.argwhere(ink[::60, ::60] > 0) * 60
    ox, oy = 960 - 360, 520 - 360
    for k, (py, px) in enumerate(pts[:40]):
        if ang[py, px] > frac: continue
        x, y = ox + px, oy + py
        cv2.line(f, (x - 34, y - 12), (x + 34, y + 12), o.CYAN[::-1], 1, cv2.LINE_AA)
        cv2.circle(f, (x - 34, y - 12), 5, o.CYAN[::-1], 1, cv2.LINE_AA); cv2.circle(f, (x + 34, y + 12), 5, o.CYAN[::-1], 1, cv2.LINE_AA)
        cv2.rectangle(f, (x - 6, y - 6), (x + 6, y + 6), o.ORANGE[::-1], -1)
    o.pip(f, hf_small(t)); return f
S(48.45, 51.0, svg_scene, 'info'); X(T(48.45), 'whoosh')
# Simon: full-bleed portrait + name card + calligraphy nickname
PORT = o.imread(SR + '12_D01_参考图.png')
BIGP = cv2.resize(PORT, (1080, 1080), interpolation=cv2.INTER_CUBIC)
NAMECARD = B(o.name_card('Simon Willison', None))
NICK = q.glow(B(q.text_img('西蒙老哥', q.F_NICK, 130, (255, 214, 170, 255))), (255, 140, 60), 14, 0.6)
def simon_scene(t, t0, t1):
    tl = t - t0; f = BG.copy(); z = 1 + 0.05 * tl / (t1 - t0)
    b = o.cover(BIGP, int(1080 * z), int(1080 * z))[:1080, :1080]
    ramp = np.clip(np.linspace(-0.3, 1.3, 1080), 0, 1)[None, :, None]
    xs = int(840 + 120 * (1 - ease(tl / 0.5)))
    w = W - xs; f[:, xs:] = (f[:, xs:] * (1 - ramp[:, :w]) + b[:, :w] * ramp[:, :w]).astype(np.uint8)
    u = ease((tl - 0.25) / 0.35); put(f, NAMECARD, int(600 - 60 * (1 - u)), 470, u)
    if tl > 0.9:
        v = back_out((tl - 0.9) / 0.35); put(f, cv2.resize(NICK, None, fx=0.7 + 0.3 * v, fy=0.7 + 0.3 * v), 760, 640, min(1, (tl - 0.9) / 0.1))
    return f
S(51.0, 55.1, simon_scene, 'portrait'); X(T(51.0), 'whoosh'); X(T(51.0) + 0.9, 'pop')
# exam stage: Simon token on top, 16 seats pop in, later red X on all
import mockups2 as M2
TOK_SIMON = B(M2.tok_simon(250))
SEATS = [B(o.token(176, 'grey', portrait=crude[(k % 11) + 1], anchors=False)) for k in range(16)]
# 16 model medallions shown first (names inside medallion only), flipped to their drawings later
MODELS = [('Sonnet', 'orange'), ('o1', 'cyan'), ('4o mini', 'cyan'), ('Gemini', 'blue'), ('GPT-4o', 'cyan'), ('Flash', 'blue'), ('Opus 3', 'orange'), ('Llama', 'violet'),
          ('Mistral', 'red'), ('Haiku 3', 'orange'), ('o1 mini', 'cyan'), ('Flash 8B', 'blue'), ('Llama 3', 'violet'), ('Pixtral', 'red'), ('Grok 2', 'grey'), ('Qwen', 'violet')]
MTOK = [B(o.token(176, c, n, anchors=False, title_size=44 if len(n) <= 7 else 36)) for n, c in MODELS]
MTOK_HI = {3: B(o.token(300, 'blue', 'Gemini 1.5', anchors=True, title_size=58)), 4: B(o.token(300, 'cyan', 'GPT-4o', anchors=True, title_size=64))}
HI = [(3, 56.30, 57.20), (4, 57.20, 58.55)]  # Gemini 1.5 / GPT-4o spoken
FLIP0 = 63.3
SEAT_POS = [(300 + (k % 8) * 190, 620 + (k // 8) * 230) for k in range(16)]
def stage(t, t0, t1):
    tl = t - t0; f = BG.copy(); n = N(t)
    u = back_out(tl / 0.4); put(f, cv2.resize(TOK_SIMON, None, fx=0.6 + 0.4 * u, fy=0.6 + 0.4 * u), W // 2, 250, min(1, tl / 0.12))
    if tl > 0.4:
        a = ease((tl - 0.4) / 0.3); y1 = int(400 + 90 * a)
        for yy in range(400, y1, 22): cv2.line(f, (W // 2, yy), (W // 2, min(yy + 12, y1)), o.ORANGE[::-1], 4, cv2.LINE_AA)
    for k, (cx, cy) in enumerate(SEAT_POS):
        d0 = 0.7 + k * 0.08
        if tl < d0: continue
        s = 0.5 + 0.5 * back_out((tl - d0) / 0.3)
        nn = n if n is not None else 0
        fp = (nn - FLIP0 - k * 0.05) / 0.28  # flip progress 0..1
        if fp < 0.5:
            img = MTOK[k]; act = 1.0
            hk = [h for h in HI if h[1] <= nn < h[2]]
            if hk and hk[0][0] != k: act = 0.35
            if any(h[0] == k and h[1] - 0.05 <= nn < h[2] + 0.2 for h in HI): act = 0.0
            sx = s * max(0.02, np.cos(np.pi * max(0, fp)))
        else:
            img = SEATS[k]; act = 1.0; sx = s * max(0.02, -np.cos(np.pi * min(1, fp)))
        im2 = cv2.resize(img, (max(2, int(img.shape[1] * sx)), int(img.shape[0] * s)))
        if act > 0: put(f, im2, cx, cy, act)
        if n is not None and n > 66.0:
            pen_x(f, cx + 50, cy - 50, 26, (n - 66.0 - k * 0.09) / 0.2, 8)
    # spoken model pops up big above its seat
    for k, a0, a1 in HI:
        if n is not None and a0 - 0.05 <= n < a1 + 0.25:
            u = back_out((n - a0) / 0.3) if n < a1 else 1 - ease((n - a1) / 0.25)
            cx, cy = SEAT_POS[k]; put(f, cv2.resize(MTOK_HI[k], None, fx=0.6 + 0.4 * u, fy=0.6 + 0.4 * u), cx, int(cy - 40 * u), min(1, u * 3))
    # camera: slow push, then at 60.7 push toward seats
    zt = 1.0 + 0.03 * min(tl, 6) / 6
    if n is not None and n > 60.7: zt += 0.08 * ease((n - 60.7) / 0.8)
    M = cv2.getRotationMatrix2D((W / 2, 560), 0, zt)
    f = cv2.warpAffine(f, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    o.pip(f, hf_small(t), x=1660, y=830, d=200); return f
S(55.1, 68.7, stage, 'info'); X(T(55.1), 'whoosh')
for k in range(0, 16, 3): X(T(55.1) + 0.7 + k * 0.08, 'pop')
X(T(56.30), 'pop'); X(T(57.20), 'pop'); X(T(58.64), 'shine')
for k in range(0, 16, 4): X(T(FLIP0) + k * 0.05, 'whoosh')
X(T(66.0), 'scribble'); X(T(66.6), 'scribble'); X(T(67.2), 'scribble')
# host + stickers (pelican, bike, chicken, basketball)
PELSTK = B(st.sticker(Image.fromarray(cv2.cvtColor(M2.CUT_PEL, cv2.COLOR_BGRA2RGBA)), 300, 14, -8))
STK = [(PELSTK, 300, 330, 68.85), (B(st.sticker(st.emoji('🚲', 260), 260, 14, 6)), 320, 720, 69.4),
       (B(st.sticker(st.emoji('🐔', 260), 260, 14, 7)), 1620, 330, 70.45), (B(st.sticker(st.emoji('🏀', 240), 240, 14, -6)), 1600, 720, 70.95)]
def stickers(t, t0, t1):
    n = N(t); f = host_full(n, 1.06)
    for img, cx, cy, n0 in STK:
        if n < n0: continue
        u = back_out((n - n0) / 0.3); put(f, cv2.resize(img, None, fx=0.5 + 0.5 * u, fy=0.5 + 0.5 * u), cx, cy, min(1, (n - n0) / 0.08))
    return f
S(68.7, 72.25, stickers, 'host')
for _, _, _, n0 in STK: X(T(n0), 'pop')
vm = Vid(SR + '15_B站_11-20秒.mp4')
m0, m1 = PT(72.25)
def meme(t, t0, t1):
    fr = vm.get(t - t0)[0:360, 76:556]; z = 1 + 0.04 * (t - t0) / (t1 - t0)
    return o.cover(fr, int(W * z), int(H * z))[int(H * (z - 1) / 2):int(H * (z - 1) / 2) + H, int(W * (z - 1) / 2):int(W * (z - 1) / 2) + W].copy()
S(m0, m1, meme, 'meme', out=True); X(m0, 'whoosh')

# ======================= subtitles
SUBS = json.load(open('/tmp/claude-0/build/subs_src.json'))
def wlen(s): return sum(0.55 if ord(c) < 128 else 1.0 for c in s)
SUB = []
for a, b, txt in SUBS:
    parts = txt.split('|'); tot = sum(wlen(p) for p in parts); tt = a
    for i, p in enumerate(parts):
        dd = (b - a) * wlen(p) / tot; t1 = tt + dd if i < len(parts) - 1 else b
        SUB.append([T(tt), T(t1) + 0.12, p]); tt = t1
for i in range(len(SUB) - 1):
    if SUB[i][1] > SUB[i + 1][0] or 0 < SUB[i + 1][0] - SUB[i][1] < 0.35: SUB[i][1] = SUB[i + 1][0]
_sc = {}
def sub_img(s):
    if s not in _sc: _sc[s] = B(st.subtitle(s))
    return _sc[s]
WM = S1.WM
NOSUB = [(a + sum(d for x, d, _ in INSERTS if x < a - 1e-9), a + sum(d for x, d, _ in INSERTS if x < a - 1e-9) + d) for a, d, k in INSERTS]

def frame(t):
    if t < 44.6: return S1.frame(t)
    f = None
    for a, b, fn, kind in SC:
        if a <= t < b: f = fn(t, a, b); break
    if f is None: f = host_full(N(t) or 0)
    f = np.ascontiguousarray(f[..., :3])
    if not any(a <= t < b for a, b in NOSUB):
        for a, b, s in SUB:
            if a <= t < b: im = sub_img(s); o.blit(f, im, (W - im.shape[1]) // 2, H - 56 - im.shape[0]); break
    o.blit(f, WM, W - WM.shape[1] - 44, 30, 0.5)
    return f

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        for t in map(float, sys.argv[2:]): cv2.imwrite(f'/tmp/claude-0/mock/v_{t:06.2f}.jpg', frame(t))
    elif sys.argv[1] == 'events':
        json.dump(dict(total=TOTAL, sfx=SFX, inserts=INSERTS, T={str(k): T(k) for k in (42.8, 72.25, 83.72, 121.1, 176.93)}), open('/tmp/claude-0/mock/v4ev.json', 'w'))
    else:
        out, a0, a1 = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for i in range(int(round(a0 * FPS)), int(round(a1 * FPS))):
            p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait()
