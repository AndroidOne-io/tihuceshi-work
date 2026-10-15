# 第三版包装：照小Lin说重做——炭黑底 + 压暗的相关画面 + 段落主色；多色徽章、透视桌面、玻璃大卡、幽灵大数字
import math, numpy as np, cv2
from kx import *

# ---------------------------------------------------------------- 配色：中性炭黑 + 多种强调色（每个实体一个颜色）
CH0, CH1 = (17, 17, 21), (36, 35, 42)
VIOLET, VIOLET_D = (150, 98, 255), (78, 34, 150)
CRIMSON, GOLD, EMERALD, SKY, TEAL, ROSE, ORANGE = (232, 70, 78), (246, 196, 82), (58, 196, 132), (78, 162, 255), (52, 196, 196), (242, 112, 156), (255, 140, 60)

_cache = {}
def bg_char(backdrop=None, tint=VIOLET, k_tint=0.20, dim=0.22, halftone=False, grid=True, key=None, blob=(0.22, 0.25)):
    """炭黑底：中心微亮 + 段落主色的一团柔光 + 压暗去色的相关画面（可网点）+ 细网格 + 暗角"""
    if key and key in _cache: return _cache[key].copy()
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32); img[:] = CH0
    d = np.sqrt((x - W * 0.5) ** 2 + (y - H * 0.45) ** 2)
    img += (np.clip(1 - d / (W * 0.7), 0, 1) ** 1.6)[..., None] * (np.array(CH1) - np.array(CH0))
    if backdrop is not None:
        b = cover(backdrop, W, H).astype(np.float32); g = b.mean(2, keepdims=True)
        g = cv2.GaussianBlur(g, (0, 0), 2.5)[..., None] if g.ndim == 3 else g
        if g.ndim == 2: g = g[..., None]
        if halftone:
            cell = 7; small = cv2.resize(g[..., 0], (W // cell, H // cell), interpolation=cv2.INTER_AREA) / 255
            dt = np.zeros((H, W), np.float32)
            for (yy, xx), v in np.ndenumerate(small):
                if v > 0.04: cv2.circle(dt, (xx * cell + cell // 2, yy * cell + cell // 2), int(v * cell * 0.62), 1.0, -1, cv2.LINE_AA)
            g = g * (0.3 + 0.7 * dt[..., None])
        img = img + g * dim
    bx, by = W * blob[0], H * blob[1]
    db = np.sqrt((x - bx) ** 2 + (y - by) ** 2)
    img += (np.exp(-(db / (W * 0.42)) ** 2))[..., None] * np.array(tint, np.float32) * k_tint
    if grid:
        gm = ((x.astype(int) % 80 == 0) | (y.astype(int) % 80 == 0)).astype(np.float32) * np.clip(1.1 - d / (W * 0.6), 0, 1)
        img += gm[..., None] * 5
    rng = np.random.default_rng(3); img += rng.normal(0, 1.8, img.shape).astype(np.float32)
    v = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H / 2) / H) ** 2)
    img *= (1 - np.clip(v - 0.28, 0, 1) * 1.25)[..., None]
    img = np.clip(img, 0, 255)
    if key: _cache[key] = img.copy()
    return img

def ghost_number(txt, size=760, col=GOLD, a=0.10):
    t = text(txt, F_NUM, size, col, 0.02)
    return t, a

def glass_card(w, h, title='', ic=None, big=None, tint=VIOLET, active=1.0, title_size=None):
    """小Lin说「第一招/第二招」那种玻璃大卡：半透明、细亮边、大图标或大数字、一行大字"""
    S = 2; im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lt = np.array(tint) * (0.45 * active + 0.12) + 22
    for k in range(h * S):   # 竖向渐变
        u = k / (h * S); c = lt * (1 - 0.45 * u)
        d.line([(0, k), (w * S, k)], fill=tuple(int(v) for v in c) + (int(205 * (0.55 + 0.45 * active)),))
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w * S - 1, h * S - 1], 26 * S, fill=255)
    im.putalpha(Image.fromarray(np.minimum(np.array(im.split()[3]), np.array(m))))
    ImageDraw.Draw(im).rounded_rectangle([2, 2, w * S - 3, h * S - 3], 26 * S, outline=tuple(int(v) for v in (np.array(tint) * active + 150 * (1 - active)) * 0.5 + 110) + (int(230 * (0.5 + 0.5 * active)),), width=3 * S)
    im = im.resize((w, h), Image.LANCZOS)
    tc = tuple(int(v) for v in np.array(WHITE) * (0.5 + 0.5 * active))
    blk = []
    if ic: blk.append(icon(ic, int(h * 0.36), tc))
    if big: blk.append(big)
    if title: blk.append(text(title, F_BLACK, title_size or int(h * 0.15), tc, 0.06))
    if blk:
        b = stack(blk, gap=int(h * 0.05)); im.alpha_composite(b, ((w - b.width) // 2, (h - b.height) // 2))
    out = pad(im, 40)
    g = Image.new('RGBA', out.size, tuple(tint) + (0,)); g.putalpha(out.split()[3].filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.5 * active)))
    res = Image.new('RGBA', out.size, (0, 0, 0, 0)); res.alpha_composite(shadow(out, 22, (0, 16), 200, 0).resize(out.size)); res.alpha_composite(g); res.alpha_composite(out)
    return res

def depth_blur(f, top=0.0, bottom=1.0, r=7):
    """上方远处虚化（透视桌面用）"""
    b = cv2.GaussianBlur(f, (0, 0), r)
    m = np.clip((np.linspace(1, 0, H) - (1 - top)) / max(top, 1e-3), 0, 1)[:, None, None] if top > 0 else np.zeros((H, 1, 1))
    return f * (1 - m) + b * m

def badge_table(t, items, bgimg, push=(1.0, 1.08), rx=52, ry=-6, cy=H * 0.62, canvas=(2700, 1500), dur=4.0):
    """多色徽章平铺在透视桌面上，按时间依次弹起；items: (徽章RGBA, x, y, 出现时间)"""
    can = np.zeros((canvas[1], canvas[0], 4), np.uint8)
    cf = can.astype(np.float32)
    for im, x, y, t0 in items:
        k = seg(t, t0, t0 + 0.35)
        if k <= 0: continue
        arr = to_rgba_np(im).astype(np.float32); s = 0.6 + 0.4 * back_out(k)
        arr = cv2.resize(arr, None, fx=s, fy=s, interpolation=cv2.INTER_LINEAR)
        h, w = arr.shape[:2]; x0, y0 = int(x - w / 2), int(y - h / 2)
        xa, ya, xb, yb = max(0, x0), max(0, y0), min(canvas[0], x0 + w), min(canvas[1], y0 + h)
        sub = arr[ya - y0:yb - y0, xa - x0:xb - x0]; al = sub[..., 3:4] / 255 * k
        cf[ya:yb, xa:xb, :3] = cf[ya:yb, xa:xb, :3] * (1 - al) + sub[..., :3] * al
        cf[ya:yb, xa:xb, 3:4] = np.maximum(cf[ya:yb, xa:xb, 3:4], sub[..., 3:4] * k)
    f = bgimg.copy()
    z = lerp(push[0], push[1], ease(min(1, t / dur)))
    persp(f, cf.astype(np.uint8), W / 2, cy, z * 0.92, ry=ry, rx=rx, shadow_k=0.0, f=1800.0)
    return depth_blur(f, top=0.38, r=5)

def paper_img(w=250, h=330, seed=0):
    rng = np.random.default_rng(seed)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 10, fill=(238, 238, 242, 255))
    y = 40
    d.rectangle([24, 24, int(w * 0.62), 34], fill=(150, 150, 165, 255))
    while y < h - 30:
        ww = int((w - 48) * rng.uniform(0.6, 1.0)); d.rectangle([24, y, 24 + ww, y + 5], fill=(190, 190, 200, 255)); y += 16
    return shadow(im, 10, (0, 6), 150, 16)
PAPERS = [paper_img(seed=k) for k in range(6)]
