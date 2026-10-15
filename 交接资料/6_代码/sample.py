# v4 animated sample: opening hook -> title (output 0 ~ 46s)
import sys, json, subprocess
sys.path.insert(0, '/tmp/claude-0/mock'); sys.path.insert(0, '/tmp/claude-0/build')
import numpy as np, cv2
from PIL import Image, ImageDraw
import own as o, style3 as st
from mockups import calli, nick_token, crude, PEL
W, H, FPS = 1920, 1080, 30
R = o.R; P = o.P; CR = P + '/剪辑素材/'; SR = P + '/素材/'
PAUSE_AT, PAUSE_D = 42.8, 1.8
END = 49.0
def T(n): return n if n <= PAUSE_AT + 1e-9 else n + PAUSE_D
def N(t):
    if t < PAUSE_AT: return t
    if t < PAUSE_AT + PAUSE_D: return None
    return t - PAUSE_D
def ease(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
def back_out(u):
    u = min(max(u, 0.0), 1.0); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2
B = lambda im: im if isinstance(im, np.ndarray) else o.to_bgra(im)
def xform(img, s=1.0, ang=0.0):
    h, w = img.shape[:2]; M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, s)
    c, si = abs(M[0, 0]), abs(M[0, 1]); nw, nh = int(h * si + w * c), int(h * c + w * si)
    M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
    return cv2.warpAffine(img, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
def put(f, img, cx, cy, a=1.0): o.blit(f, img, cx - img.shape[1] // 2, cy - img.shape[0] // 2, a)

class Vid:
    def __init__(s, p): s.c = cv2.VideoCapture(p); s.fps = s.c.get(5) or 30; s.n = int(s.c.get(7)); s.i = -1; s.f = None
    def get(s, t):
        want = min(max(int(round(t * s.fps)), 0), s.n - 1)
        if want < s.i or want > s.i + 60: s.c.set(1, want); s.i = want - 1
        while s.i < want:
            ok, fr = s.c.read()
            if not ok: break
            s.i += 1; s.f = fr
        return s.f
host = Vid(R + '/口播粗剪.mp4')
def host_full(n, z=1.0):
    f = host.get(n); w, h = 1280 / z, 720 / z; x0 = 640 - w / 2; y0 = max(0, min(720 - h, 230 - h * 0.3))
    M = np.float32([[W / w, 0, -x0 * W / w], [0, H / h, -y0 * H / h]])
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# ---------------- assets
BG = o.bg(); BGW = o.bg(tint='warm')
import own2 as q
METAL = B(q.metal_title('世纪难题', 240, 0.08))
DEPTH = cv2.GaussianBlur(B(q.text_img('AI', q.F_TITLE, 760, (255, 120, 40, 255))), (0, 0), 30)
BRUSH = B(q.brush_title('鹈鹕测试', 330))
HALF = q.halftone_bg(o.grab(CR + '03_01_选用片段.mp4', 2.0), (255, 110, 40))
paper = o.paper_card(1000, 760, True, None); pa = B(paper)
pa[..., :3]  # draw question into paper
pim = Image.fromarray(cv2.cvtColor(pa, cv2.COLOR_BGRA2RGBA))
pim.paste(Image.fromarray(cv2.cvtColor(cv2.resize(crude[11], (430, 430), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)), (285, 165))
PAPER = o.to_bgra(pim)
SCORE = B(st.text('0分', st.F_BRUSH, 200, o.RED + (255,)))
TOK_OPUS = B(o.token(380, 'orange', 'Opus 5.5', ''))
sheet = Image.fromarray(cv2.cvtColor(B(o.paper_card(880, 700, True, None)), cv2.COLOR_BGRA2RGBA))
SHEET = o.to_bgra(sheet)
STAMP_BLANK = B(o.stamp('交白卷', size=180, angle=-12))
TITLE = B(st.metal('鹈鹕测试', 150, top='THE  PELICAN  TEST'))
MASCOT = B(nick_token(470, 'orange', PEL, '严', '父'))
UGLY = [B(st.photo_card(crude[k], 420, angle=a)) for k, a in [(2, -6), (3, 5), (6, 4), (10, -5)]]

def pen_circle(f, cx, cy, rx, ry, frac, w=10, ang=-8):
    if frac <= 0: return
    n = int(95 * min(frac, 1)) + 1; pts = []
    for i in range(n):
        t = np.radians(i * 4); j = 1 + 0.04 * np.sin(i * 4 / 23)
        pts.append((cx + rx * j * np.cos(t), cy + ry * j * np.sin(t) + i * 4 * 0.08))
    M = cv2.getRotationMatrix2D((cx, cy), ang, 1)
    pts = cv2.transform(np.array([pts], np.float32), M)[0].astype(np.int32)
    cv2.polylines(f, [pts], False, o.RED[::-1], w, cv2.LINE_AA)
def pen_x(f, cx, cy, s, frac, w=14):
    a = min(frac * 2, 1); b = max(0, min(frac * 2 - 1, 1))
    if a > 0: cv2.line(f, (int(cx - s), int(cy - s)), (int(cx - s + 2 * s * a), int(cy - s + 1.9 * s * a)), o.RED[::-1], w, cv2.LINE_AA)
    if b > 0: cv2.line(f, (int(cx + s * 0.95), int(cy - s * 1.05)), (int(cx + s * 0.95 - 1.85 * s * b), int(cy - s * 1.05 + 2.05 * s * b)), o.RED[::-1], w, cv2.LINE_AA)

SFX = []
def X(t, k): SFX.append((round(t, 3), k))

# ---------------- scenes (functions of output time t)
def sc_hook(t):
    if t < 1.05: return host_full(N(t), 1.0)
    tl = t - 1.05; f = q.tunnel(t)
    put(f, DEPTH, W // 2, 540, 0.4 * ease(tl / 0.5))
    u = ease(tl / 0.45); s = 1.25 - 0.25 * u + 0.03 * tl
    m = q.sweep(METAL, min(1.0, max(0.0, (tl - 0.35) / 1.1)))
    m = q.glow(m, (255, 170, 90), 20, 0.35)
    put(f, cv2.resize(m, None, fx=s, fy=s), W // 2, 520, min(1, tl / 0.15))
    return f
X(1.05, 'boom'); X(1.4, 'shine')
def sc_paper(t):
    tl = t - 3.9; f = BG.copy()
    u = back_out(tl / 0.45); s = 1.25 - 0.25 * u; ang = -12 + 8 * ease(tl / 0.45)
    img = xform(PAPER, s, ang); put(f, img, int(1080 + 500 * (1 - ease(tl / 0.35))), 520, min(1, tl / 0.12))
    if tl > 1.6:
        k = ease((tl - 1.6) / 0.35); w = max(1, int(SCORE.shape[1] * k))
        o.blit(f, SCORE[:, :w], 1480 - SCORE.shape[1] // 2, 300 - SCORE.shape[0] // 2)
        pen_circle(f, 1480, 300, 190, 130, (tl - 2.0) / 0.45)
    o.pip(f, cv2.resize(host.get(N(t)), (1280, 720))); return f
X(3.9, 'whoosh'); X(5.5, 'scribble'); X(5.9, 'scribble')
v03 = Vid(CR + '03_01_选用片段.mp4'); v04 = Vid(CR + '04_02_选用片段.mp4'); v05 = Vid(CR + '05_03_选用片段.mp4')
v06 = Vid(SR + '06_B站_19-24秒.mp4'); v07 = Vid(CR + '07_05_选用片段.mp4'); v09 = Vid(CR + '09_07_选用片段.mp4'); v20 = Vid(CR + '20_22_选用片段.mp4')
def full(v, src, kb=0.04, crop=None):
    def fn(t, t0, t1):
        fr = v.get(src + t - t0)
        if crop: x0, y0, x1, y1 = crop; fr = fr[y0:y1, x0:x1]
        z = 1 + kb * (t - t0) / (t1 - t0); return o.cover(fr, int(W * z), int(H * z))[int(H * (z - 1) / 2):int(H * (z - 1) / 2) + H, int(W * (z - 1) / 2):int(W * (z - 1) / 2) + W].copy()
    return fn
def slow09(t, t0, t1):
    fr = v09.get((t - t0) * 0.68); z = 1 + 0.08 * (t - t0) / (t1 - t0)
    return o.cover(fr, int(W * z), int(H * z))[int(H * (z - 1) / 2):int(H * (z - 1) / 2) + H, int(W * (z - 1) / 2):int(W * (z - 1) / 2) + W].copy()
def card_of(fr, w):
    h = int(fr.shape[0] * w / fr.shape[1]); im = cv2.resize(fr, (w, h), interpolation=cv2.INTER_CUBIC)
    return B(st.photo_card(im, w))
def sc_04(t, t0, t1):
    f = BG.copy(); fr = v04.get(t - t0)
    for crop, cx, d0 in [((58, 83, 600, 425), 495, 0.0), ((667, 100, 1205, 440), 1425, 0.3)]:
        if t - t0 < d0: continue
        x0, y0, x1, y1 = crop; c = card_of(fr[y0:y1, x0:x1], 820); u = back_out((t - t0 - d0) / 0.3)
        put(f, cv2.resize(c, None, fx=0.7 + 0.3 * u, fy=0.7 + 0.3 * u), cx, 520)
    return f
def sc_05(t, t0, t1):
    f = np.zeros((H, W, 3), np.uint8); fr = v05.get(t - t0); n = N(t)
    L = o.cover(fr[90:960, 20:970], 956, H); Rr = o.cover(fr[90:960, 1000:1953], 956, H)
    if 17.4 <= n < 20.0: L = (L * 0.45).astype(np.uint8)
    if 14.6 <= n < 17.4: Rr = (Rr * 0.45).astype(np.uint8)
    f[:, :956] = L; f[:, 964:] = Rr; return f
def sc_06(t, t0, t1):
    f = full(v06, 0.0, 0.03, (180, 40, 990, 496))(t, t0, t1); tl = t - t0
    pen_circle(f, 1250, 690, 260, 200, (tl - 1.2) / 0.5, 12, -5); pen_x(f, 1600, 280, 70, (tl - 2.0) / 0.3, 16); return f
X(T(21.12) + 1.2, 'scribble'); X(T(21.12) + 2.0, 'scribble')
def sc_ugly(t, t0, t1):
    f = BG.copy(); tl = t - t0
    for i, (cx, cy, d0) in enumerate([(470, 420, 0.05), (1450, 400, 0.9), (780, 700, 1.8), (1180, 690, 2.7)]):
        if tl < d0: continue
        u = back_out((tl - d0) / 0.28); c = UGLY[i]; put(f, cv2.resize(c, None, fx=0.6 + 0.4 * u, fy=0.6 + 0.4 * u), cx, cy)
        pen_x(f, cx + 120, cy - 110, 50, (tl - d0 - 0.35) / 0.25, 12)
    return f
for d0 in (0.05, 0.9, 1.8, 2.7): X(T(26.8) + d0, 'pop'); X(T(26.8) + d0 + 0.35, 'scribble')
def sc_opus(t, t0, t1):
    f = BG.copy(); tl = t - t0
    u = ease(tl / 0.4); put(f, TOK_OPUS, int(470 - 300 * (1 - u)), 480, u)
    if tl > 0.4:
        v = back_out((tl - 0.4) / 0.45); img = xform(SHEET, 1.2 - 0.2 * v, 8 - 5 * ease((tl - 0.4) / 0.45))
        put(f, img, int(1270 + 400 * (1 - ease((tl - 0.4) / 0.35))), 540, min(1, (tl - 0.4) / 0.12))
    ts = T(36.95) - t0
    if tl > ts:
        k = min((tl - ts) / 0.12, 1); s = 1.7 - 0.7 * k; st_ = cv2.resize(STAMP_BLANK, None, fx=s, fy=s)
        dx = int(np.sin(tl * 120) * 6 * max(0, 0.3 - (tl - ts)) / 0.3) if tl - ts > 0.12 else 0
        put(f, st_, 1290 + dx, 560, min(1, (tl - ts) / 0.05))
    o.pip(f, cv2.resize(host.get(N(t)), (1280, 720))); return f
X(T(31.05), 'whoosh'); X(T(31.45), 'whoosh'); X(T(36.95), 'stamp')
def sc_title(t, t0, t1):
    tl = t - t0; z = 1.06 - 0.06 * ease(tl / 0.4) + 0.02 * tl
    f = HALF.copy(); f = cv2.warpAffine(f, cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1 + 0.03 * tl), (W, H), borderMode=cv2.BORDER_REFLECT)
    put(f, cv2.resize(BRUSH, None, fx=z, fy=z), W // 2, 540, min(1, tl / 0.08))
    gl = max(0.0, 1 - tl / 0.35) * 0.9
    return q.glitch(f, gl, int(tl * 30))
X(T(42.8) - 1.4, 'riser'); X(T(42.8), 'boom')
def sc_host(z):
    return lambda t, t0, t1: host_full(N(t), z * (1 + 0.02 * (t - t0) / max(t1 - t0, .1)))

SC = [(0, 3.9, lambda t, a, b: sc_hook(t)), (3.9, 7.5, lambda t, a, b: sc_paper(t)),
      (7.5, 11.0, full(v03, 0.0)), (11.0, 14.45, sc_04), (14.45, 21.12, sc_05), (21.12, 24.95, sc_06),
      (24.95, 26.8, full(v07, 0.0, 0.03, (370, 230, 1130, 657))), (26.8, 31.05, sc_ugly), (31.05, 38.5, sc_opus),
      (38.5, 42.8, slow09)]
SC = [(T(a), T(b), fn) for a, b, fn in SC] + [(T(42.8), T(42.8) + PAUSE_D, sc_title), (T(42.8) + PAUSE_D, END + 1, sc_host(1.0))]
for a, b, fn in SC[2:]:
    if fn not in (sc_opus, sc_title, sc_ugly): pass
for k in (7.5, 11.0, 14.45, 24.95, 38.5): X(T(k), 'whoosh')

SUBS = json.load(open('/tmp/claude-0/build/subs_src.json'))
def wlen(s): return sum(0.55 if ord(c) < 128 else 1.0 for c in s)
SUB = []
for a, b, txt in SUBS:
    if a > 48: break
    parts = txt.split('|'); tot = sum(wlen(p) for p in parts); tt = a
    for i, p in enumerate(parts):
        dd = (b - a) * wlen(p) / tot; t1 = tt + dd if i < len(parts) - 1 else b
        SUB.append([T(tt), T(t1) + 0.12, p]); tt = t1
for i in range(len(SUB) - 1):
    if SUB[i][1] > SUB[i + 1][0] or 0 < SUB[i + 1][0] - SUB[i][1] < 0.35: SUB[i][1] = SUB[i + 1][0]
_sc = {}
def sub_img(t):
    if t not in _sc: _sc[t] = B(st.subtitle(t))
    return _sc[t]
WM = B(st.shadow(st.text('AI阿亮', st.F_MED, 30, (255, 255, 255), 0.12), 4, (0, 2), 160, 8))

def frame(t):
    for a, b, fn in SC:
        if a <= t < b: f = fn(t, a, b); break
    f = np.ascontiguousarray(f[..., :3])
    if not (T(42.8) <= t < T(42.8) + PAUSE_D):
        for a, b, s in SUB:
            if a <= t < b: im = sub_img(s); o.blit(f, im, (W - im.shape[1]) // 2, H - 56 - im.shape[0]); break
    o.blit(f, WM, W - WM.shape[1] - 44, 30, 0.5)
    return f

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        for t in map(float, sys.argv[2:]): cv2.imwrite(f'/tmp/claude-0/mock/s_{t:05.2f}.jpg', frame(t))
    elif sys.argv[1] == 'events':
        json.dump(dict(end=END, pause=[T(42.8), PAUSE_D], sfx=sorted(SFX)), open('/tmp/claude-0/mock/ev.json', 'w'))
    else:
        out = sys.argv[2]
        p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        a0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0; a1 = float(sys.argv[4]) if len(sys.argv) > 4 else END
        for i in range(int(round(a0 * FPS)), int(round(a1 * FPS))):
            p.stdin.write(frame(i / FPS).tobytes())
            if i % 150 == 0: print(i / FPS, flush=True)
        p.stdin.close(); p.wait()
