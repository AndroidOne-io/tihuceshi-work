# 第四版包装「鎏金夜」：暖黑底 + 香槟金主色 + 冰蓝/珊瑚/薄荷点缀；真正的毛玻璃（背后画面虚化透出）
import math, numpy as np, cv2
from kx import *

# ---------------------------------------------------------------- 配色
OB0, OB1 = (11, 12, 15), (31, 32, 38)            # 石墨黑（中性略冷）
GOLD = (236, 198, 122)                            # 香槟金（主色）
AMBER = (255, 168, 80)
ICE = (150, 208, 255)                             # 冰蓝
CORAL = (255, 112, 92)
MINT = (112, 226, 196)
LILAC = (196, 160, 255)
PAPER = (244, 238, 228)

_cache = {}
def bg_gild(backdrop=None, dim=0.18, leak=(0.12, 0.18), leak_col=AMBER, k_leak=0.10, key=None, bokeh=True):
    """暖黑底：中心微亮 + 一角暖色漏光 + 压暗去色的相关画面 + 大颗虚化光斑 + 胶片颗粒 + 暗角"""
    if key and key in _cache: return _cache[key].copy()
    if LIGHT: return np.zeros((H, W, 3), np.float32)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32); img[:] = OB0
    d = np.sqrt((x - W * 0.5) ** 2 + (y - H * 0.48) ** 2)
    img += (np.clip(1 - d / (W * 0.72), 0, 1) ** 1.5)[..., None] * (np.array(OB1) - np.array(OB0))
    if backdrop is not None:
        g = cover(backdrop, W, H).astype(np.float32).mean(2, keepdims=True)
        g = cv2.GaussianBlur(g, (0, 0), 3)
        if g.ndim == 2: g = g[..., None]
        img += g * dim * np.array([0.96, 0.98, 1.0])
    lx, ly = W * leak[0], H * leak[1]
    dl = np.sqrt((x - lx) ** 2 + ((y - ly) * 1.4) ** 2)
    img += np.exp(-(dl / (W * 0.45)) ** 2)[..., None] * np.array(leak_col, np.float32) * k_leak
    if bokeh:
        rng = np.random.default_rng(8); bk = np.zeros((H, W, 3), np.float32)
        for _ in range(14):
            c = (int(rng.uniform(0, W)), int(rng.uniform(0, H))); r = int(rng.uniform(30, 110))
            col = np.array([GOLD, AMBER, ICE][rng.integers(0, 3)], np.float32) * rng.uniform(0.04, 0.10)
            cv2.circle(bk, c, r, col.tolist(), -1, cv2.LINE_AA)
        img += cv2.GaussianBlur(bk, (0, 0), 9)
    rng = np.random.default_rng(4); img += rng.normal(0, 2.4, img.shape).astype(np.float32)
    v = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H / 2) / H) ** 2)
    img *= (1 - np.clip(v - 0.3, 0, 1) * 1.3)[..., None]
    img = np.clip(img, 0, 255)
    if key: _cache[key] = img.copy()
    return img

# ---------------------------------------------------------------- 毛玻璃元件：mask（形状）+ overlay（边、高光、文字）
class Glass:
    def __init__(self, mask, overlay, tint):
        self.mask = mask.astype(np.float32) / 255.0      # HxW
        self.ov = overlay                                # HxWx4 uint8
        self.tint = np.array(tint, np.float32)

def _shape(w, h, kind, r):
    S = 2; m = Image.new('L', (w * S, h * S), 0); d = ImageDraw.Draw(m)
    if kind == 'circle': d.ellipse([2, 2, w * S - 3, h * S - 3], fill=255)
    else: d.rounded_rectangle([2, 2, w * S - 3, h * S - 3], r * S, fill=255)
    return m.resize((w, h), Image.LANCZOS)

def make_glass(w, h, kind='rect', r=34, tint=GOLD, title='', ic=None, big=None, title_size=None, text_col=WHITE, edge=1.0):
    m = _shape(w, h, kind, r); M = np.array(m)
    ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    # 高光：左上到右下的淡白渐变
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sheen = np.clip(1 - (xx / w * 0.6 + yy / h * 0.9), 0, 1) ** 2 * 70
    rim_out = cv2.dilate((M > 128).astype(np.uint8), np.ones((3, 3))) - (M > 128).astype(np.uint8)
    inner = (M > 128).astype(np.float32) - cv2.erode((M > 128).astype(np.uint8), np.ones((5, 5)), iterations=1).astype(np.float32)
    top = np.clip(1.2 - yy / h * 1.6, 0.25, 1)
    edge_col = np.minimum(np.array(tint, np.float32) * 0.75 + 90, 255)
    rgb = np.zeros((h, w, 3), np.float32); al = np.zeros((h, w), np.float32)
    rgb += 255; al += sheen / 255 * (M / 255)
    e = np.clip(inner * top * edge, 0, 1)
    rgb = rgb * (1 - e[..., None]) + edge_col * e[..., None]; al = np.maximum(al, e * 0.9)
    ov = Image.fromarray(np.dstack([rgb, al * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
    blk = []
    if ic: blk.append(icon(ic, int(min(w, h) * 0.32), text_col))
    if big is not None: blk.append(big)
    if title: blk.append(text(title, F_BLACK, title_size or int(min(w, h) * 0.15), text_col, 0.06))
    if blk:
        b = stack(blk, gap=int(h * 0.04))
        if b.width > w * 0.84: k = w * 0.84 / b.width; b = b.resize((int(b.width * k), int(b.height * k)), Image.LANCZOS)
        ov.alpha_composite(shadow(b, 8, (0, 3), 140, 0).resize(b.size), ((w - b.width) // 2, (h - b.height) // 2))
    return Glass(M, np.asarray(ov), tint)

def put_glass(f, g, cx, cy, a=1.0, scale=1.0, fb=None, blur=22, tint_k=0.16, shadow_k=0.45):
    """把毛玻璃元件合成到 f：背后画面虚化、提亮、染一点主色，再盖边和高光"""
    if a <= 0.003: return f
    m, ov = g.mask, g.ov
    if scale != 1.0:
        m = cv2.resize(m, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR); ov = cv2.resize(ov, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = m.shape; x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb: return f
    mm = m[ya - y0:yb - y0, xa - x0:xb - x0][..., None] * a
    # 投影
    if shadow_k > 0:
        sh = np.zeros((H, W), np.float32); sh[ya:yb, xa:xb] = mm[..., 0]
        sh = cv2.GaussianBlur(np.roll(sh, 18, 0), (0, 0), 22)[..., None]; f *= (1 - sh * shadow_k)
    if fb is None: fb = cv2.GaussianBlur(f, (0, 0), blur)
    reg = fb[ya:yb, xa:xb] * 0.8 + g.tint * tint_k + 12
    f[ya:yb, xa:xb] = f[ya:yb, xa:xb] * (1 - mm) + reg * mm
    o = ov[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32); oa = o[..., 3:4] / 255 * a
    f[ya:yb, xa:xb] = f[ya:yb, xa:xb] * (1 - oa) + o[..., :3] * oa
    return f

def glass_table(f, t, items, rx=34, ry=-4, cy=H * 0.55, canvas=(2200, 1200), push=1.0, depth_top=0.36):
    """毛玻璃徽章平铺在透视桌面：先投影 mask 做背景虚化，再盖边和文字；items: (Glass, x, y, 出现时间)"""
    cm = np.zeros((canvas[1], canvas[0]), np.float32); co = np.zeros((canvas[1], canvas[0], 4), np.float32); ct = np.zeros((canvas[1], canvas[0], 3), np.float32)
    for g, x, y, t0 in items:
        k = seg(t, t0, t0 + 0.35)
        if k <= 0: continue
        s = 0.6 + 0.4 * back_out(k)
        m = cv2.resize(g.mask, None, fx=s, fy=s); ov = cv2.resize(g.ov.astype(np.float32), None, fx=s, fy=s)
        h, w = m.shape; x0, y0 = int(x - w / 2), int(y - h / 2)
        xa, ya, xb, yb = max(0, x0), max(0, y0), min(canvas[0], x0 + w), min(canvas[1], y0 + h)
        mk = m[ya - y0:yb - y0, xa - x0:xb - x0] * k
        cm[ya:yb, xa:xb] = np.maximum(cm[ya:yb, xa:xb], mk)
        ct[ya:yb, xa:xb] = ct[ya:yb, xa:xb] * (1 - mk[..., None]) + g.tint * mk[..., None]
        o = ov[ya - y0:yb - y0, xa - x0:xb - x0]; oa = o[..., 3:4] / 255 * k
        co[ya:yb, xa:xb, :3] = co[ya:yb, xa:xb, :3] * (1 - oa) + o[..., :3] * oa; co[ya:yb, xa:xb, 3:4] = np.maximum(co[ya:yb, xa:xb, 3:4], oa * 255)
    src = np.array([[0, 0], [canvas[0], 0], [canvas[0], canvas[1]], [0, canvas[1]]], np.float32)
    tmp = np.zeros((H, W, 3), np.float32)
    M = persp(tmp, np.dstack([np.zeros((canvas[1], canvas[0], 3), np.uint8), (cm * 255).astype(np.uint8)]), W / 2, cy, 0.92 * push, ry=ry, rx=rx, shadow_k=0.0, f=1800.0)
    wm = cv2.warpPerspective(cm, M, (W, H))[..., None]; wt_ = cv2.warpPerspective(ct, M, (W, H)); wo = cv2.warpPerspective(co, M, (W, H))
    sh = cv2.GaussianBlur(np.roll(wm[..., 0], 20, 0), (0, 0), 20)[..., None]; f *= (1 - sh * 0.45)
    f += cv2.GaussianBlur(wt_ * wm, (0, 0), 45) * 0.55          # 每个徽章底下一团同色柔光
    fb = cv2.GaussianBlur(f, (0, 0), 20)
    f[:] = f * (1 - wm) + (fb * 0.7 + wt_ * 0.34 + 12) * wm
    oa = wo[..., 3:4] / 255; f[:] = f * (1 - oa) + wo[..., :3] * oa
    b = cv2.GaussianBlur(f, (0, 0), 5); mk = np.clip((np.linspace(1, 0, H) - (1 - depth_top)) / depth_top, 0, 1)[:, None, None]
    return f * (1 - mk) + b * mk

# ---------------------------------------------------------------- 半透明卡片 / 徽章（不做毛玻璃，只是半透明）
SAPPHIRE = (70, 126, 238); TEAL = (34, 172, 170); EMERALD = (48, 172, 112); VIOLET = (140, 104, 232); ROSE = (232, 92, 120)
INK = (20, 22, 28)
def make_card(w, h, kind='rect', r=28, tint=INK, alpha=0.62, title='', ic=None, big=None, title_size=None, ic_col=None, rim=0.38, rim_col=(255, 255, 255)):
    """半透明：本色渐变（上浅下深）+ 细边 + 白字；不虚化背后画面"""
    S = 2; W2, H2 = w * S, h * S
    m = _shape(w, h, kind, r); M = np.array(m).astype(np.float32) / 255
    yy = np.linspace(0, 1, h)[:, None]
    base = np.array(tint, np.float32)
    rgb = np.ones((h, w, 3), np.float32) * base * (1.12 - 0.3 * yy)[..., None] if False else (base[None, None, :] * (1.15 - 0.35 * yy)[..., None]) * np.ones((h, w, 3), np.float32)
    rgb = np.clip(rgb, 0, 255)
    al = M * alpha
    inner = (M > 0.5).astype(np.float32) - cv2.erode((M > 0.5).astype(np.uint8), np.ones((5, 5)), iterations=1).astype(np.float32)
    rc = np.array(rim_col, np.float32)
    rgb = rgb * (1 - inner[..., None] * rim) + rc * inner[..., None] * rim; al = np.maximum(al, inner * min(1.0, alpha + rim))
    im = Image.fromarray(np.dstack([rgb, al * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
    blk = []
    if ic: blk.append(icon(ic, int(min(w, h) * 0.3), ic_col or WHITE))
    if big is not None: blk.append(big)
    if title: blk.append(text(title, F_BLACK, title_size or int(min(w, h) * 0.15), WHITE, 0.06))
    if blk:
        b = stack(blk, gap=int(h * 0.05))
        if b.width > w * 0.84: k = w * 0.84 / b.width; b = b.resize((int(b.width * k), int(b.height * k)), Image.LANCZOS)
        im.alpha_composite(b, ((w - b.width) // 2, (h - b.height) // 2))
    return shadow(im, 18, (0, 10), 120, 30)
