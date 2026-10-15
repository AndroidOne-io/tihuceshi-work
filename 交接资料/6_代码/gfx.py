# Graphics helpers: text rendering, cards, compositing (BGRA numpy, cv2 space)
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FONT_BLACK = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
FONT_BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FONT_MED = '/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc'
FONT_REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONT_SYM = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
FONT_EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'

GOLD = (255, 210, 63)
RED = (255, 70, 70)
GREEN = (60, 220, 120)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        # SC face index 2 in Noto CJK ttc (JP=0, KR=1, SC=2, TC=3, HK=4)
        idx = 2 if path.endswith('.ttc') else 0
        _fc[k] = ImageFont.truetype(path, size, index=idx)
    return _fc[k]

def pil2bgra(im):
    a = np.array(im.convert('RGBA'))
    return cv2.cvtColor(a, cv2.COLOR_RGBA2BGRA)

def emoji_img(ch, size):
    f = ImageFont.truetype(FONT_EMOJI, 109)
    im = Image.new('RGBA', (140, 140), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4, 4), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    r = size / im.height
    return im.resize((max(1, int(im.width * r)), size), Image.LANCZOS)

def rich_line(segs, size, fill=WHITE, stroke=0, stroke_fill=BLACK, gap=0):
    """segs: list of (kind, text[, color]) kind in 't'(CJK black),'b'(bold),'s'(symbol),'m'(mono),'e'(emoji).
    returns RGBA PIL image (with stroke)."""
    pieces = []
    for sg in segs:
        kind, txt = sg[0], sg[1]
        col = sg[2] if len(sg) > 2 else fill
        if kind == 'e':
            pieces.append(emoji_img(txt, int(size * 1.0)))
            continue
        fp = {'t': FONT_BLACK, 'b': FONT_BOLD, 'm': FONT_MONO, 's': FONT_SYM, 'r': FONT_REG, 'M': FONT_MED}[kind]
        fsize = size if kind not in ('s', 'm') else int(size * 0.9)
        f = font(fp, fsize)
        d = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        bb = d.textbbox((0, 0), txt, font=f, stroke_width=stroke)
        w = bb[2] - bb[0] + 4
        hh = int(size * 1.45) + stroke * 2
        im = Image.new('RGBA', (w, hh), (0, 0, 0, 0))
        # vertical centre on cap height
        asc = f.getbbox('国')
        y = (hh - (asc[3] - asc[1])) // 2 - asc[1]
        if kind in ('s', 'm'):
            ab = f.getbbox('X'); y = (hh - (ab[3] - ab[1])) // 2 - ab[1]
        ImageDraw.Draw(im).text((-bb[0] + 2, y), txt, font=f, fill=col, stroke_width=stroke, stroke_fill=stroke_fill)
        pieces.append(im)
    hh = max(p.height for p in pieces)
    tw = sum(p.width for p in pieces) + gap * (len(pieces) - 1)
    out = Image.new('RGBA', (tw, hh), (0, 0, 0, 0))
    x = 0
    for p in pieces:
        out.alpha_composite(p, (x, (hh - p.height) // 2))
        x += p.width + gap
    return out

def stack(ims, align='c', gap=0):
    w = max(i.width for i in ims); h = sum(i.height for i in ims) + gap * (len(ims) - 1)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); y = 0
    for i in ims:
        x = {'c': (w - i.width) // 2, 'l': 0, 'r': w - i.width}[align]
        out.alpha_composite(i, (x, y)); y += i.height + gap
    return out

def shadowed(im, radius=14, offset=(0, 8), alpha=150, pad=30):
    W2, H2 = im.width + pad * 2, im.height + pad * 2
    sh = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: v * alpha // 255)
    blk = Image.new('RGBA', im.size, (0, 0, 0, 255)); blk.putalpha(a)
    sh.alpha_composite(blk, (pad + offset[0], pad + offset[1]))
    sh = sh.filter(ImageFilter.GaussianBlur(radius))
    sh.alpha_composite(im, (pad, pad))
    return sh

def pop_text(text, size=130, color=GOLD, stroke=10, sym=None):
    """Big variety-show style word: gold fill, thick black stroke, shadow. text may contain '\n'."""
    lines = []
    for ln in text.split('\n'):
        segs = []
        for part in split_syms(ln):
            segs.append(part)
        lines.append(rich_line([(k, t, color) for k, t in segs], size, stroke=stroke))
    return shadowed(stack(lines, gap=-int(size * 0.18)), radius=10, offset=(0, 10), alpha=170)

def split_syms(s):
    out = []; cur = ''; ck = None
    for ch in s:
        k = 's' if ch in '✔✘→×≈+' else 't'
        if ck is None or k == ck: cur += ch; ck = k
        else: out.append((ck, cur)); cur = ch; ck = k
    if cur: out.append((ck, cur))
    return out

def rounded(size, radius, fill, outline=None, width=0):
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius, fill=fill, outline=outline, width=width)
    return im

def tag(text, size=50, bg=GOLD, fg=BLACK, padx=26, pady=10, radius=14, prefix=None):
    t = rich_line(split_kind(text, fg), size)
    box = rounded((t.width + padx * 2, t.height + pady * 2 - 8), radius, bg + (255,))
    box.alpha_composite(t, (padx, pady - 4))
    return shadowed(box, radius=8, offset=(0, 6), alpha=120, pad=18)

def split_kind(s, col):
    return [(('s' if k == 's' else 't'), t, col) for k, t in split_syms(s)]

def glass_card(w, h, radius=36, fill=(18, 14, 38, 225), border=(255, 255, 255, 50)):
    return rounded((w, h), radius, fill, outline=border, width=2)

def purple_bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (x / W * 0.6 + y / H * 0.4)
    c0 = np.array([40, 14, 22], np.float32)   # BGR deep navy-purple
    c1 = np.array([92, 22, 66], np.float32)   # BGR purple
    img = c0[None, None] * (1 - t[..., None]) + c1[None, None] * t[..., None]
    # radial glow
    d = np.sqrt(((x - W * 0.7) / W) ** 2 + ((y - H * 0.3) / H) ** 2)
    img += (np.clip(0.5 - d, 0, 1) * 70)[..., None] * np.array([1.0, 0.3, 0.9], np.float32)
    # faint grid
    grid = ((x.astype(int) % 80 == 0) | (y.astype(int) % 80 == 0))
    img[grid] += 10
    # vignette
    v = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H / 2) / H) ** 2)
    img *= (1 - np.clip(v - 0.35, 0, 1) * 0.9)[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)

def blit(dst, src, x, y, alpha=1.0):
    """alpha-blend BGRA src onto BGR dst at (x,y) (top-left), clipped."""
    h, w = src.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    if x1 <= x0 or y1 <= y0 or alpha <= 0: return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    if s.shape[2] == 3:
        a = np.full(s.shape[:2] + (1,), alpha, np.float32)
        rgb = s.astype(np.float32)
    else:
        a = s[..., 3:4].astype(np.float32) / 255.0 * alpha
        rgb = s[..., :3].astype(np.float32)
    d = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = (rgb * a + d * (1 - a)).astype(np.uint8)

def scale_rgba(src, s):
    if abs(s - 1) < 1e-3: return src
    h, w = src.shape[:2]
    return cv2.resize(src, (max(1, int(w * s)), max(1, int(h * s))), interpolation=cv2.INTER_LINEAR)

def fit_cover(img, w, h):
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih)
    r = cv2.resize(img, (int(np.ceil(iw * s)), int(np.ceil(ih * s))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    y0 = (r.shape[0] - h) // 2; x0 = (r.shape[1] - w) // 2
    return r[y0:y0 + h, x0:x0 + w]

def fit_contain(img, w, h):
    ih, iw = img.shape[:2]
    s = min(w / iw, h / ih)
    return cv2.resize(img, (max(1, int(round(iw * s))), max(1, int(round(ih * s)))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)

def blur_fill(img):
    small = fit_cover(img, 192, 108)
    small = cv2.GaussianBlur(small, (0, 0), 6)
    big = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)
    return (big.astype(np.float32) * 0.45).astype(np.uint8)

def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)

def back_out(u):
    u = min(max(u, 0.0), 1.0); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2

def circle_mask(d):
    m = np.zeros((d, d), np.uint8)
    cv2.circle(m, (d // 2, d // 2), d // 2 - 1, 255, -1, lineType=cv2.LINE_AA)
    return m

def white_card_bgra(img_bgr, pad=0, radius=24):
    """put image into rounded white card with soft shadow -> BGRA"""
    h, w = img_bgr.shape[:2]
    card = np.zeros((h + pad * 2, w + pad * 2, 4), np.uint8)
    card[..., :3] = 255
    m = np.zeros(card.shape[:2], np.uint8)
    cv2.rectangle(m, (radius, 0), (m.shape[1] - radius, m.shape[0]), 255, -1)
    cv2.rectangle(m, (0, radius), (m.shape[1], m.shape[0] - radius), 255, -1)
    for cx, cy in [(radius, radius), (m.shape[1] - radius - 1, radius), (radius, m.shape[0] - radius - 1), (m.shape[1] - radius - 1, m.shape[0] - radius - 1)]:
        cv2.circle(m, (cx, cy), radius, 255, -1, lineType=cv2.LINE_AA)
    card[pad:pad + h, pad:pad + w, :3] = img_bgr
    card[..., 3] = m
    return card

def add_shadow_bgra(card, blur=22, off=10, alpha=0.55, pad=40):
    h, w = card.shape[:2]
    out = np.zeros((h + pad * 2, w + pad * 2, 4), np.uint8)
    sh = np.zeros(out.shape[:2], np.float32)
    sh[pad + off:pad + off + h, pad:pad + w] = card[..., 3].astype(np.float32) * alpha
    sh = cv2.GaussianBlur(sh, (0, 0), blur)
    out[..., 3] = np.clip(sh, 0, 255).astype(np.uint8)
    blit_rgba(out, card, pad, pad)
    return out

def blit_rgba(dst, src, x, y):
    """composite BGRA src over BGRA dst (same-size region assumed inside)."""
    h, w = src.shape[:2]
    sa = src[..., 3:4].astype(np.float32) / 255
    da = dst[y:y + h, x:x + w, 3:4].astype(np.float32) / 255
    oa = sa + da * (1 - sa)
    rgb = (src[..., :3] * sa + dst[y:y + h, x:x + w, :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    dst[y:y + h, x:x + w, :3] = rgb.astype(np.uint8)
    dst[y:y + h, x:x + w, 3:4] = (oa * 255).astype(np.uint8)
