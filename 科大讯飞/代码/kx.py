# 科大讯飞 · AI for Science —— 包装库「科研观测台」
# 所有画面 RGB uint8 / float32，1920×1080
import os, subprocess, math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))        # 科大讯飞/
REPO = os.path.dirname(ROOT)
MAT = os.path.join(ROOT, '素材')
FD = os.path.join(REPO, '交接资料', '7_字体')
F_TITLE = os.path.join(FD, '优设标题黑.ttf')
F_BRUSH = os.path.join(FD, '杨任东竹石体-Heavy.ttf')
F_SUB = os.path.join(FD, 'SmileySans-Oblique.ttf')
F_NUM = os.path.join(FD, 'BebasNeue-Regular.ttf')
F_BLACK = os.path.join(FD, 'NotoSansCJK-Black.ttc')        # 思源黑体，已放进仓库字体目录
F_BOLD = os.path.join(FD, 'NotoSansCJK-Bold.ttc')        # 思源黑体，已放进仓库字体目录
F_MED = os.path.join(FD, 'NotoSansCJK-Medium.ttc')        # 思源黑体，已放进仓库字体目录

# ---------------------------------------------------------------- 配色（RGB）
BG0 = (11, 16, 27)        # 底
BG1 = (24, 40, 66)        # 中心光
CYAN = (46, 211, 255)     # 讯飞青：主色、取景框、线
BLUE = (64, 112, 255)     # 电蓝：辅色
AMBER = (255, 184, 76)    # 琥珀：高亮、数字、粒子
RED = (255, 78, 78)       # 警示：死亡之谷
WHITE = (242, 245, 250)

# ---------------------------------------------------------------- 基础
def ease(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
def ease_out(u, p=3): u = min(max(u, 0.0), 1.0); return 1 - (1 - u) ** p
def ease_in(u, p=3): u = min(max(u, 0.0), 1.0); return u ** p
def back_out(u, s=1.7):
    u = min(max(u, 0.0), 1.0) - 1; return u * u * ((s + 1) * u + s) + 1
def seg(t, a, b): return min(max((t - a) / max(b - a, 1e-6), 0.0), 1.0)
def lerp(a, b, u): return a + (b - a) * u

@functools.lru_cache(64)
def font(p, s):
    return ImageFont.truetype(p, s, index=0)

def text(t, fp, size, fill=WHITE, spacing=0.0, stroke=0, stroke_fill=(0, 0, 0)):
    """文字 → RGBA PIL（spacing 为字号比例的额外字距）"""
    f = font(fp, size)
    fill = tuple(fill) + ((255,) if len(fill) == 3 else ())
    if spacing == 0:
        bb = f.getbbox(t, stroke_width=stroke)
        im = Image.new('RGBA', (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((4 - bb[0], 4 - bb[1]), t, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        return im
    gap = size * spacing
    adv = [f.getlength(c) for c in t]
    tw = sum(adv) + gap * (len(t) - 1)
    asc, desc = f.getmetrics()
    im = Image.new('RGBA', (int(tw + 16 + 2 * stroke), asc + desc + 16 + 2 * stroke), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); x = 8 + stroke
    for c, a in zip(t, adv):
        d.text((x, 8 + stroke + asc), c, font=f, fill=fill, anchor='ls', stroke_width=stroke, stroke_fill=stroke_fill); x += a + gap
    return im.crop(im.getbbox()) if im.getbbox() else im

def pad(im, p):
    o = Image.new('RGBA', (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0)); o.alpha_composite(im, (p, p)); return o

def shadow(im, r=16, off=(0, 8), a=170, p=34, col=(0, 0, 0)):
    im = pad(im, p)
    s = Image.new('RGBA', im.size, col + (0,)); s.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(v * a / 255)))
    o = Image.new('RGBA', im.size, (0, 0, 0, 0)); o.alpha_composite(s, off); o.alpha_composite(im); return o

def glow_rgba(im, col=CYAN, r=18, k=0.8, p=40):
    im = pad(im, p)
    g = Image.new('RGBA', im.size, tuple(col) + (0,)); g.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(min(255, v * k))))
    o = Image.new('RGBA', im.size, (0, 0, 0, 0)); o.alpha_composite(g); o.alpha_composite(im); return o

def stack(ims, gap=0):
    w = max(i.width for i in ims); h = sum(i.height for i in ims) + gap * (len(ims) - 1)
    o = Image.new('RGBA', (w, h), (0, 0, 0, 0)); y = 0
    for i in ims: o.alpha_composite(i, ((w - i.width) // 2, y)); y += i.height + gap
    return o

def to_rgba_np(im): return np.asarray(im.convert('RGBA'))

def put(dst, im, cx, cy, a=1.0, scale=1.0, angle=0.0):
    """把 PIL RGBA 或 RGBA ndarray 以中心点 (cx,cy) 合成到 dst(float32 RGB) 上"""
    if a <= 0.003: return dst
    arr = to_rgba_np(im) if isinstance(im, Image.Image) else im
    if scale != 1.0 or angle != 0.0:
        h, w = arr.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, scale)
        c, s = abs(M[0, 0]), abs(M[0, 1]); nw, nh = int(h * s + w * c) + 2, int(h * c + w * s) + 2
        M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
        arr = cv2.warpAffine(arr, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    h, w = arr.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, dst.shape[1]), min(y0 + h, dst.shape[0])
    if xa >= xb or ya >= yb: return dst
    sub = arr[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    al = sub[..., 3:4] / 255.0 * a
    dst[ya:yb, xa:xb] = dst[ya:yb, xa:xb] * (1 - al) + sub[..., :3] * al
    return dst

def add(dst, layer, k=1.0):
    dst += layer * k; return dst

def cover(img, w, h, fx=0.5, fy=0.5):
    ih, iw = img.shape[:2]; s = max(w / iw, h / ih)
    r = cv2.resize(img, (int(math.ceil(iw * s)), int(math.ceil(ih * s))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    y0 = int((r.shape[0] - h) * fy); x0 = int((r.shape[1] - w) * fx)
    return r[y0:y0 + h, x0:x0 + w]

def imread(p):
    im = Image.open(p)
    if im.mode == 'RGBA':
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
    return np.asarray(im.convert('RGB'))

def grab(p, t):
    cap = cv2.VideoCapture(p); cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, f = cap.read(); cap.release()
    return cv2.cvtColor(f, cv2.COLOR_BGR2RGB) if ok else None

LIGHT = os.environ.get('KX_LIGHT') == '1'      # 轻量模式（export_web.py data/audio 用）：不读视频帧、不画背景，只为算时间线和混音
class Vid:
    """顺序读视频帧（按秒取，自动缓存当前帧）"""
    def __init__(self, p):
        self.p = p; self.cap = cv2.VideoCapture(p); self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30; self.i = -1; self.f = None
    def get(self, t):
        if LIGHT: return np.zeros((int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or H, int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or W, 3), np.uint8)
        n = int(round(t * self.fps))
        if n < self.i or n > self.i + 90:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, n); self.i = n - 1
        while self.i < n:
            ok, f = self.cap.read()
            if not ok: break
            self.f = f; self.i += 1
        return cv2.cvtColor(self.f, cv2.COLOR_BGR2RGB)

# ---------------------------------------------------------------- 背景：深蓝底 + 中心光 + 同心圆 + 点阵 + 布纹 + 暗角
_bg_cache = {}
def bg(kind='navy', backdrop=None, dim=0.22, halftone=False, dots=True, key=None):
    k = key or (kind, dim, halftone, dots, None if backdrop is None else backdrop.shape)
    if key and k in _bg_cache: return _bg_cache[k].copy()
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array({'navy': BG0, 'deep': (8, 12, 20), 'warm': (22, 14, 16)}[kind], np.float32)
    glow = np.array({'navy': BG1, 'deep': (18, 30, 52), 'warm': (70, 34, 26)}[kind], np.float32)
    img = np.zeros((H, W, 3), np.float32); img[:] = base
    if backdrop is not None:
        b = cover(backdrop, W, H).astype(np.float32)
        g = b.mean(2, keepdims=True)
        if halftone:
            cell = 8; small = cv2.resize(g[..., 0], (W // cell, H // cell), interpolation=cv2.INTER_AREA) / 255
            dt = np.zeros((H, W), np.float32)
            for (yy, xx), v in np.ndenumerate(small):
                if v > 0.05: cv2.circle(dt, (xx * cell + cell // 2, yy * cell + cell // 2), int(v * cell * 0.6), 1.0, -1, cv2.LINE_AA)
            g = g * (0.35 + 0.65 * dt[..., None])
        tint = np.array([0.55, 0.8, 1.0], np.float32)
        img = img * (1 - dim) + g * tint * dim
    cx, cy = W * 0.5, H * 0.46
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    img += (np.clip(1 - d / (W * 0.62), 0, 1) ** 2)[..., None] * (glow - base) * 0.9
    rings = np.clip(1 - np.abs((d % 140) - 70) / 1.4 + 1 - 50, 0, 1)
    rings = (np.abs((d % 140) - 70) > 68.6).astype(np.float32) * np.clip(1 - d / (W * 0.7), 0, 1)
    img += rings[..., None] * 9
    if dots:
        dm = ((x.astype(int) % 32 == 0) & (y.astype(int) % 32 == 0)).astype(np.float32)
        dm = cv2.dilate(dm, np.ones((2, 2), np.uint8)) * np.clip(1.15 - d / (W * 0.55), 0, 1)
        img += dm[..., None] * np.array(CYAN, np.float32) * 0.10
    rng = np.random.default_rng(7)
    n = rng.random((H, W)).astype(np.float32)
    fab = cv2.blur(n, (1, 41)) * 0.5 + cv2.blur(n, (41, 1)) * 0.5; fab = (fab - fab.mean()) / (fab.std() + 1e-6)
    img *= (1 + 0.025 * fab)[..., None]
    img += rng.normal(0, 1.6, img.shape).astype(np.float32)
    v = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H / 2) / H) ** 2)
    img *= (1 - np.clip(v - 0.32, 0, 1) * 1.1)[..., None]
    img = np.clip(img, 0, 255)
    if key: _bg_cache[k] = img.copy()
    return img

# ---------------------------------------------------------------- 大字三种
def _grad(mask_im, stops):
    w, h = mask_im.size; pos = np.linspace(0, 1, h); cols = np.zeros((h, 3))
    for c in range(3): cols[:, c] = np.interp(pos, [s[0] for s in stops], [s[1][c] for s in stops])
    arr = np.zeros((h, w, 4), np.uint8); arr[..., :3] = cols[:, None, :].astype(np.uint8); arr[..., 3] = np.array(mask_im.split()[3])
    return arr

def metal(t, size=190, spacing=0.10, top=None, bottom=None, fp=F_TITLE):
    """银色金属拉丝字，边缘带一点讯飞青"""
    base = pad(text(t, fp, size, (255, 255, 255), spacing), 16)
    stops = [(0, (252, 253, 255)), (0.44, (212, 220, 232)), (0.5, (118, 128, 146)), (0.6, (196, 206, 222)), (1, (120, 132, 152))]
    a = _grad(base, stops).astype(np.float32)
    rng = np.random.default_rng(3)
    s = cv2.blur(rng.random((base.height, base.width)).astype(np.float32), (91, 1)); s = (s - s.min()) / (s.max() - s.min() + 1e-6)
    a[..., :3] *= (0.84 + 0.28 * s)[..., None]
    scr = cv2.blur((rng.random((base.height, base.width)) > 0.996).astype(np.float32), (31, 1)) * 5
    a[..., :3] += (np.clip(scr, 0, 1) * 55)[..., None]
    face = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    edge = Image.new('RGBA', base.size, (10, 18, 30, 255)); edge.putalpha(base.split()[3].filter(ImageFilter.MaxFilter(7)))
    rim = Image.new('RGBA', base.size, CYAN + (255,)); rim.putalpha(base.split()[3].filter(ImageFilter.MaxFilter(3)).point(lambda v: int(v * 0.55)))
    o = Image.new('RGBA', base.size, (0, 0, 0, 0)); o.alpha_composite(edge); o.alpha_composite(rim, (0, 2)); o.alpha_composite(face)
    parts = []
    if top: parts.append(text(top, F_MED, int(size * 0.2), (220, 228, 240), 0.4))
    parts.append(o)
    if bottom: parts.append(text(bottom, F_NUM, int(size * 0.22), (170, 200, 225), 0.35))
    return shadow(stack(parts, gap=int(size * 0.06)), 20, (0, 12), 210, 40)

def sweep(arr_rgba, u, width=0.14, k=1.0):
    """金属字扫光：u 0→1 从左到右"""
    a = arr_rgba.astype(np.float32).copy(); h, w = a.shape[:2]
    x = np.arange(w, dtype=np.float32)[None, :] + np.arange(h, dtype=np.float32)[:, None] * 0.35
    c = lerp(-0.2, 1.3, u) * (w + h * 0.35)
    band = np.exp(-((x - c) / (width * w)) ** 2) * k
    a[..., :3] = a[..., :3] + (255 - a[..., :3]) * band[..., None] * (a[..., 3:4] / 255)
    return np.clip(a, 0, 255).astype(np.uint8)

def brush(t, size=320, col=(240, 240, 244)):
    """毛笔飞白字"""
    base = pad(text(t, F_BRUSH, size, (255, 255, 255), 0.02), 60)
    A = np.array(base.split()[3]).astype(np.float32) / 255
    h, w = A.shape; rng = np.random.default_rng(5)
    nx = cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 2) * 6 - 3
    ny = cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 2) * 6 - 3
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    A = cv2.remap(A, gx + nx * size / 60, gy + ny * size / 60, cv2.INTER_LINEAR)
    n = cv2.blur(rng.random((h * 2, w * 2)).astype(np.float32), (1, int(size * 0.8)))
    M = cv2.getRotationMatrix2D((w, h), -22, 1.0); n = cv2.warpAffine(n, M, (w * 2, h * 2))[h // 2:h // 2 + h, w // 2:w // 2 + w]
    n = (n - n.mean()) / (n.std() + 1e-6)
    dist = cv2.distanceTransform((A > 0.5).astype(np.uint8), cv2.DIST_L2, 3)
    band = np.clip(1 - dist / (size * 0.06), 0, 1)
    gaps = (n < -0.8).astype(np.float32) * (0.15 + 0.85 * band ** 1.5)
    A2 = cv2.GaussianBlur(np.clip(A * (1 - gaps), 0, 1), (3, 3), 0)
    colarr = np.zeros((h, w, 3), np.float32); colarr[:] = col
    colarr *= (1 - 0.18 * np.linspace(0, 1, h))[:, None, None]
    im = Image.fromarray(np.dstack([colarr, A2 * 255]).astype(np.uint8), 'RGBA'); im = im.crop(im.getbbox())
    return shadow(im, 22, (0, 10), 230, 44)

def number(num, unit='', size=260, col=AMBER, unit_col=WHITE):
    n = text(num, F_NUM, size, col, 0.02)
    if not unit: return shadow(glow_rgba(n, col, 26, 0.55), 16, (0, 10), 200)
    u = text(unit, F_BLACK, int(size * 0.42), unit_col)
    o = Image.new('RGBA', (n.width + u.width + 16, n.height), (0, 0, 0, 0)); o.alpha_composite(n, (0, 0)); o.alpha_composite(u, (n.width + 16, n.height - u.height - int(size * 0.08)))
    return shadow(glow_rgba(o, col, 26, 0.5), 16, (0, 10), 200)

# ---------------------------------------------------------------- 字幕：得意黑斜体白字细黑边
def subtitle(dst, t, y=H - 92):
    if not t: return dst
    im = text(t, F_SUB, 64, WHITE, 0.02, stroke=4, stroke_fill=(8, 10, 16))
    return put(dst, shadow(im, 6, (0, 3), 160, 12), W / 2, y)

# ---------------------------------------------------------------- 图标（代码画，白色线条）
def icon(name, s=220, col=(240, 246, 255), lw=None):
    S = s * 3; lw = lw or int(S * 0.055)
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = tuple(col) + (255,)
    def L(*pts): d.line([(x * S, y * S) for x, y in pts], fill=c, width=lw, joint='curve')
    def E(x0, y0, x1, y1, fill=False): d.ellipse([x0 * S, y0 * S, x1 * S, y1 * S], outline=c, width=lw, fill=c if fill else None)
    def R(x0, y0, x1, y1, r=0.04): d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, outline=c, width=lw)
    if name == 'flask':      # 科研
        L((0.38, 0.12), (0.62, 0.12)); L((0.42, 0.12), (0.42, 0.40), (0.20, 0.82), (0.80, 0.82), (0.58, 0.40), (0.58, 0.12))
        L((0.30, 0.62), (0.70, 0.62)); E(0.44, 0.68, 0.50, 0.74, True); E(0.56, 0.52, 0.61, 0.57, True)
    elif name == 'book':     # 教育
        L((0.5, 0.30), (0.5, 0.82)); L((0.5, 0.30), (0.14, 0.22), (0.14, 0.74), (0.5, 0.82), (0.86, 0.74), (0.86, 0.22), (0.5, 0.30))
        L((0.22, 0.38), (0.42, 0.42)); L((0.58, 0.42), (0.78, 0.38)); L((0.22, 0.52), (0.42, 0.56)); L((0.58, 0.56), (0.78, 0.52))
    elif name == 'medical':  # 医疗
        R(0.18, 0.18, 0.82, 0.82, 0.12)
        L((0.24, 0.52), (0.38, 0.52), (0.44, 0.36), (0.54, 0.68), (0.60, 0.52), (0.76, 0.52))
    elif name == 'gear':     # 工业
        cx = cy = 0.5
        for k in range(8):
            a = k * math.pi / 4
            L((cx + 0.26 * math.cos(a), cy + 0.26 * math.sin(a)), (cx + 0.38 * math.cos(a), cy + 0.38 * math.sin(a)))
        E(0.24, 0.24, 0.76, 0.76); E(0.40, 0.40, 0.60, 0.60)
    elif name == 'home':     # 生活
        L((0.14, 0.50), (0.5, 0.16), (0.86, 0.50)); L((0.24, 0.42), (0.24, 0.84), (0.76, 0.84), (0.76, 0.42))
        L((0.42, 0.84), (0.42, 0.62), (0.58, 0.62), (0.58, 0.84))
    elif name == 'bulb':     # 提出方案
        E(0.28, 0.12, 0.72, 0.56); L((0.40, 0.56), (0.40, 0.70), (0.60, 0.70), (0.60, 0.56)); L((0.42, 0.78), (0.58, 0.78))
        L((0.46, 0.36), (0.50, 0.44), (0.54, 0.36))
    elif name == 'wrench':   # 调用工具
        L((0.24, 0.80), (0.58, 0.46)); E(0.50, 0.14, 0.86, 0.50)
        d.rectangle([0.64 * S, 0.12 * S, 0.80 * S, 0.30 * S], fill=(0, 0, 0, 0))
        L((0.62, 0.20), (0.70, 0.28), (0.78, 0.20))
    elif name == 'chart':    # 模拟计算
        L((0.16, 0.16), (0.16, 0.84), (0.86, 0.84))
        d.line([(x * S, y * S) for x, y in [(0.22, 0.70), (0.36, 0.52), (0.50, 0.60), (0.64, 0.34), (0.82, 0.24)]], fill=c, width=lw, joint='curve')
        for p in [(0.36, 0.52), (0.64, 0.34)]: E(p[0] - 0.035, p[1] - 0.035, p[0] + 0.035, p[1] + 0.035, True)
    elif name == 'check':    # 辅助验证
        L((0.5, 0.12), (0.82, 0.24), (0.80, 0.54), (0.5, 0.86), (0.20, 0.54), (0.18, 0.24), (0.5, 0.12))
        L((0.34, 0.50), (0.46, 0.62), (0.68, 0.38))
    elif name == 'doc':      # 写文章
        R(0.22, 0.12, 0.78, 0.88, 0.05)
        for yy in (0.32, 0.46, 0.60): L((0.34, yy), (0.66, yy))
        L((0.34, 0.74), (0.52, 0.74))
    elif name == 'list':     # 总结资料
        for yy in (0.26, 0.50, 0.74):
            E(0.16, yy - 0.05, 0.26, yy + 0.05, True); L((0.36, yy), (0.84, yy))
    elif name == 'lock':
        R(0.22, 0.46, 0.78, 0.88, 0.06); d.arc([0.32 * S, 0.14 * S, 0.68 * S, 0.62 * S], 180, 360, fill=c, width=lw)
        L((0.32, 0.38), (0.32, 0.47)); L((0.68, 0.38), (0.68, 0.47)); E(0.46, 0.6, 0.54, 0.68, True); L((0.5, 0.66), (0.5, 0.76))
    elif name == 'stack':
        for k, yy in enumerate((0.62, 0.46, 0.30)):
            R(0.18 + k * 0.03, yy, 0.82 - k * 0.03, yy + 0.2, 0.03)
    elif name == 'gem':
        L((0.2, 0.38), (0.36, 0.18), (0.64, 0.18), (0.8, 0.38), (0.5, 0.86), (0.2, 0.38), (0.8, 0.38))
        L((0.36, 0.18), (0.42, 0.38), (0.5, 0.86)); L((0.64, 0.18), (0.58, 0.38), (0.5, 0.86))
    elif name == 'person':
        E(0.34, 0.12, 0.66, 0.44); d.arc([0.14 * S, 0.52 * S, 0.86 * S, 1.24 * S], 180, 360, fill=c, width=lw)
    elif name == 'factory':
        L((0.10, 0.86), (0.10, 0.46), (0.34, 0.60), (0.34, 0.46), (0.58, 0.60), (0.58, 0.20), (0.74, 0.20), (0.74, 0.86), (0.10, 0.86))
        L((0.82, 0.86), (0.90, 0.86))
    im = im.resize((s, s), Image.LANCZOS)
    return im

# ---------------------------------------------------------------- 玻璃徽章
def glass(d, title='', ic=None, tint=CYAN, active=1.0, title_size=None):
    S = 2; D = d * S
    yy, xx = np.mgrid[0:D, 0:D].astype(np.float32); c = D / 2; r = D / 2 - 3 * S
    dist = np.sqrt((xx - c) ** 2 + (yy - c) ** 2) / r
    lit = np.clip(np.sqrt((xx - c * 0.65) ** 2 + (yy - c * 0.45) ** 2) / (r * 1.7), 0, 1)
    lt = np.array(tint, np.float32) * 0.55 + 40; dk = np.array(BG0, np.float32) + 10
    rgb = lt[None, None, :] * (1 - lit[..., None]) + dk[None, None, :] * lit[..., None]
    if active < 1:
        g = rgb.mean(2, keepdims=True); rgb = rgb * active + (g * 0.6 + 14) * (1 - active)
    body = (0.40 + 0.25 * dist ** 3) * (0.5 + 0.5 * active)
    rim = np.clip(1 - np.abs(dist - 0.975) / 0.025, 0, 1)
    inner = np.clip(1 - np.abs(dist - 0.9) / 0.006, 0, 1)
    rimcol = np.array(tint, np.float32) * active + 200 * (1 - active)
    rgb = rgb * (1 - rim[..., None] * 0.8) + (rimcol * 0.5 + 127)[None, None, :] * rim[..., None] * 0.8
    rgb = rgb * (1 - inner[..., None] * 0.3) + 255 * inner[..., None] * 0.3
    alpha = np.clip(body + rim * 0.6 + inner * 0.25, 0, 0.95) * np.clip((1 - dist) * r / 1.5, 0, 1)
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8), 'RGBA').resize((d, d), Image.LANCZOS)
    tc = tuple(int(v) for v in (np.array(WHITE) * (0.55 + 0.45 * active))) + (int(255 * (0.6 + 0.4 * active)),)
    blk = []
    if ic: blk.append(icon(ic, int(d * (0.34 if title else 0.5)), tc[:3]))
    if title:
        ts = title_size or int(d * (0.17 if len(title) <= 3 else 0.13 if len(title) <= 5 else 0.1))
        blk.append(text(title, F_BOLD, ts, tc, 0.08))
    if blk:
        b = stack(blk, gap=int(d * 0.04))
        if b.width > d * 0.78: k = d * 0.78 / b.width; b = b.resize((int(b.width * k), int(b.height * k)), Image.LANCZOS)
        im.alpha_composite(b, ((d - b.width) // 2, (d - b.height) // 2))
    out = pad(im, 40)
    g = Image.new('RGBA', out.size, tuple(tint) + (0,)); g.putalpha(out.split()[3].filter(ImageFilter.GaussianBlur(20)).point(lambda v: int(v * 0.55 * active)))
    res = Image.new('RGBA', out.size, (0, 0, 0, 0)); res.alpha_composite(g); res.alpha_composite(out)
    return res

# ---------------------------------------------------------------- 招牌：青色取景框（四角括号 + 扫描线）
def finder(dst, x0, y0, x1, y1, u=1.0, col=CYAN, lw=5, scan=None):
    """u: 0→1 从放大状态收拢锁定；scan: 0→1 扫描线位置（None 不画）"""
    k = ease_out(u, 3); m = (1 - k) * 80
    a0, b0, a1, b1 = x0 - m, y0 - m, x1 + m, y1 + m
    L = min(x1 - x0, y1 - y0) * 0.16
    lay = np.zeros_like(dst)
    for (cx, cy, sx, sy) in [(a0, b0, 1, 1), (a1, b0, -1, 1), (a0, b1, 1, -1), (a1, b1, -1, -1)]:
        cv2.line(lay, (int(cx), int(cy)), (int(cx + sx * L), int(cy)), col, lw, cv2.LINE_AA)
        cv2.line(lay, (int(cx), int(cy)), (int(cx), int(cy + sy * L)), col, lw, cv2.LINE_AA)
    if scan is not None and 0 < scan < 1:
        yy = int(lerp(y0, y1, scan))
        cv2.line(lay, (int(x0), yy), (int(x1), yy), col, 2, cv2.LINE_AA)
        band = np.zeros_like(dst); cv2.rectangle(band, (int(x0), yy - 40), (int(x1), yy), col, -1)
        band = cv2.GaussianBlur(band, (1, 41), 0); lay += band * 0.25
    g = cv2.GaussianBlur(lay, (0, 0), 6)
    dst += (lay + g * 0.8) * min(1.0, u * 3)
    return dst

def hl_bar(dst, x0, y0, x1, y1, u, col=AMBER, a=0.42):
    """高亮条从左扫到右（叠加在截图上）"""
    xe = int(lerp(x0, x1, ease_out(u)))
    if xe <= x0: return dst
    sub = dst[int(y0):int(y1), int(x0):xe]
    dst[int(y0):int(y1), int(x0):xe] = sub * (1 - a) + np.array(col, np.float32) * a * (sub.mean(2, keepdims=True) / 255 * 0.4 + 0.75)
    return dst

# ---------------------------------------------------------------- 透视卡片（截图/录屏铺满、倾斜）
def card(img, w, radius=22, border=0, bcol=(255, 255, 255)):
    h = int(img.shape[0] * w / img.shape[1])
    r = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
    arr = np.dstack([r, np.array(m)])
    if border:
        o = Image.new('RGBA', (w + 2 * border, h + 2 * border), (0, 0, 0, 0)); ImageDraw.Draw(o).rounded_rectangle([0, 0, o.width - 1, o.height - 1], radius + border, fill=tuple(bcol) + (255,))
        o.alpha_composite(Image.fromarray(arr, 'RGBA'), (border, border)); arr = np.asarray(o)
    return arr

def persp(dst, rgba, cx, cy, scale=1.0, ry=0.0, rx=0.0, rz=0.0, a=1.0, shadow_k=0.6, f=2200.0):
    """把 RGBA 平面绕 Y/X/Z 轴旋转（度）后透视投影到 dst"""
    h, w = rgba.shape[:2]
    pts = np.array([[-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], [w / 2, h / 2, 0], [-w / 2, h / 2, 0]], np.float32) * scale
    ay, ax, az = map(math.radians, (ry, rx, rz))
    Ry = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
    Rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    p = pts @ (Rz @ Ry @ Rx).T
    z = p[:, 2] + f
    proj = np.stack([cx + p[:, 0] * f / z, cy + p[:, 1] * f / z], 1).astype(np.float32)
    src = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    M = cv2.getPerspectiveTransform(src, proj)
    warped = cv2.warpPerspective(rgba, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0)).astype(np.float32)
    al = warped[..., 3:4] / 255 * a
    if shadow_k > 0:
        sh = cv2.GaussianBlur(al, (0, 0), 28); sh = np.roll(sh, 26, axis=0)[..., None] if sh.ndim == 2 else np.roll(sh, 26, axis=0)
        if sh.ndim == 2: sh = sh[..., None]
        dst *= (1 - sh * shadow_k)
    dst[:] = dst * (1 - al) + warped[..., :3] * al
    return M

def dim_except(dst, M, keep_box, k=0.55):
    """透视后的截图：除了 keep_box（原图坐标）之外压暗"""
    x0, y0, x1, y1 = keep_box
    poly = cv2.perspectiveTransform(np.array([[[x0, y0], [x1, y0], [x1, y1], [x0, y1]]], np.float32), M)[0]
    m = np.zeros((H, W), np.float32); cv2.fillConvexPoly(m, poly.astype(np.int32), 1.0, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 6)[..., None]
    dst[:] = dst * (m + (1 - m) * (1 - k))
    return poly

# ---------------------------------------------------------------- 圆形小窗 / 白框贴纸
def pip(dst, frame, cx=250, cy=H - 250, d=330, u=1.0):
    if u <= 0: return dst
    d2 = int(d * back_out(u))
    if d2 < 8: return dst
    f = cover(frame, d2, d2, 0.5, 0.35)
    m = Image.new('L', (d2, d2), 0); ImageDraw.Draw(m).ellipse([2, 2, d2 - 3, d2 - 3], fill=255)
    im = Image.fromarray(np.dstack([f, np.array(m)]).astype(np.uint8), 'RGBA')
    ring = Image.new('RGBA', (d2 + 16, d2 + 16), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse([2, 2, d2 + 13, d2 + 13], outline=CYAN + (255,), width=5)
    ring.alpha_composite(im, (8, 8))
    return put(dst, shadow(glow_rgba(ring, CYAN, 16, 0.6), 18, (0, 10), 180), cx, cy)

def photo(img, w, border=12, angle=0):
    a = card(img, w, radius=10, border=border)
    return shadow(Image.fromarray(a, 'RGBA'), 18, (0, 12), 190).rotate(angle, resample=Image.BICUBIC, expand=True)

# ---------------------------------------------------------------- 转场 / 动效
def whip(frame, k, horiz=True):
    """甩镜模糊，k 0..1 强度"""
    if k <= 0.01: return frame
    n = int(5 + 120 * k) | 1
    ker = np.zeros((n, n), np.float32)
    if horiz: ker[n // 2, :] = 1.0 / n
    else: ker[:, n // 2] = 1.0 / n
    return cv2.filter2D(frame, -1, ker)

def glitch(frame, amt, seed=0):
    if amt <= 0.01: return frame
    rng = np.random.default_rng(seed); out = frame.copy()
    for _ in range(int(6 + 18 * amt)):
        y = rng.integers(0, H - 20); hh = rng.integers(4, 40); dx = int(rng.normal(0, 60 * amt))
        out[y:y + hh] = np.roll(out[y:y + hh], dx, axis=1)
    sh = int(10 * amt); out[..., 0] = np.roll(out[..., 0], sh, axis=1); out[..., 2] = np.roll(out[..., 2], -sh, axis=1)
    return out

def shake(frame, k, seed):
    if k <= 0.01: return frame
    rng = np.random.default_rng(seed); dx, dy = rng.normal(0, 14 * k, 2)
    M = np.float32([[1 + 0.02 * k, 0, dx - W * 0.01 * k], [0, 1 + 0.02 * k, dy - H * 0.01 * k]])
    return cv2.warpAffine(frame, M, (W, H), borderMode=cv2.BORDER_REFLECT)

def zoom(frame, z, fx=0.5, fy=0.5):
    if abs(z - 1) < 1e-3: return frame
    w, h = W / z, H / z; x0 = (W - w) * fx; y0 = (H - h) * fy
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    return cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def bloom(frame, k=0.35, r=18):
    b = cv2.GaussianBlur(np.clip(frame - 150, 0, 255), (0, 0), r)
    return frame + b * k

# ---------------------------------------------------------------- 输出
class Writer:
    def __init__(self, path, fps=FPS, crf=18):
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                                   '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf), '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    def write(self, f): self.p.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    def close(self): self.p.stdin.close(); self.p.wait()

def render(fn, dur, path, fps=FPS, stills=None, still_dir=None):
    """fn(t)->frame；stills: 需要导出静帧的时间点列表"""
    wr = Writer(path, fps); n = int(round(dur * fps))
    for i in range(n):
        t = i / fps; f = fn(t); wr.write(f)
        if stills and still_dir:
            for s in stills:
                if abs(t - s) < 0.5 / fps:
                    Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).save(os.path.join(still_dir, f'{os.path.splitext(os.path.basename(path))[0]}_{s:.1f}.jpg'), quality=90)
    wr.close()
