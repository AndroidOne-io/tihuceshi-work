# "AI阿亮" design system — derived from reference style 2 (dark charcoal + glass medallions + metallic titles + comic nicknames)
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import gfx
from gfx import W, H, font

F_LIGHT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc'
F_DEMI = '/usr/share/fonts/opentype/noto/NotoSansCJK-DemiLight.ttc'
F_MED = gfx.FONT_MED; F_BOLD = gfx.FONT_BOLD; F_BLACK = gfx.FONT_BLACK

# palette (RGB)
PAL = {
    'purple': ((150, 92, 255), (92, 44, 196), (46, 18, 104)),   # light, mid, dark
    'blue':   ((96, 168, 255), (40, 108, 214), (16, 52, 120)),
    'teal':   ((90, 214, 206), (34, 140, 140), (12, 70, 74)),
    'green':  ((140, 226, 110), (52, 160, 70), (18, 84, 34)),
    'gold':   ((255, 240, 170), (232, 200, 100), (150, 112, 36)),
    'red':    ((255, 120, 110), (206, 52, 58), (104, 16, 24)),
    'grey':   ((150, 150, 160), (82, 82, 92), (36, 36, 42)),
}
LAVENDER = (201, 168, 255)
GOLDTXT = (245, 214, 120)
INK = (12, 10, 16)

# ------------------------------------------------------------------ text primitives
def spaced(text, fpath, size, fill, spacing=0.12, stroke=0, stroke_fill=(0, 0, 0)):
    """render text with letter spacing -> RGBA"""
    f = font(fpath, size)
    if spacing == 0:
        bb = f.getbbox(text, stroke_width=stroke)
        im = Image.new('RGBA', (bb[2] - bb[0] + 8 + stroke * 2, int(size * 1.5) + stroke * 2), (0, 0, 0, 0))
        asc = f.getbbox('国'); y = (im.height - (asc[3] - asc[1])) // 2 - asc[1]
        ImageDraw.Draw(im).text((4 - bb[0] + stroke, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        return im.crop(im.getbbox()) if im.getbbox() else im
    chars = list(text); gap = int(size * spacing)
    ims = []
    for ch in chars:
        if ch == ' ':
            ims.append(Image.new('RGBA', (int(size * 0.35), 1), (0, 0, 0, 0))); continue
        bb = f.getbbox(ch, stroke_width=stroke)
        w = max(1, bb[2] - bb[0]) + stroke * 2
        im = Image.new('RGBA', (w + 4, int(size * 1.5) + stroke * 2), (0, 0, 0, 0))
        asc = f.getbbox('国')
        y = (im.height - (asc[3] - asc[1])) // 2 - asc[1]
        ImageDraw.Draw(im).text((2 - bb[0] + stroke, y), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        ims.append(im)
    hh = max(i.height for i in ims)
    tw = sum(i.width for i in ims) + gap * (len(ims) - 1)
    out = Image.new('RGBA', (tw, hh), (0, 0, 0, 0)); x = 0
    for i in ims:
        out.alpha_composite(i, (x, (hh - i.height) // 2)); x += i.width + gap
    return out.crop(out.getbbox()) if out.getbbox() else out

def grad_fill(mask_im, stops, vertical=True):
    """fill alpha of mask_im (RGBA) with a gradient; stops list of (pos, rgb)"""
    w, h = mask_im.size
    n = h if vertical else w
    pos = np.linspace(0, 1, n)
    cols = np.zeros((n, 3))
    ps = [s[0] for s in stops]
    for c in range(3):
        cols[:, c] = np.interp(pos, ps, [s[1][c] for s in stops])
    arr = np.zeros((h, w, 4), np.uint8)
    if vertical: arr[..., :3] = cols[:, None, :].astype(np.uint8)
    else: arr[..., :3] = cols[None, :, :].astype(np.uint8)
    arr[..., 3] = np.array(mask_im.split()[3])
    return Image.fromarray(arr, 'RGBA')

def pad_im(im, p):
    out = Image.new('RGBA', (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0)); out.alpha_composite(im, (p, p)); return out

def comic(text, size=120, tilt=-3):
    """style-2 nickname text: yellow->orange gradient, thick dark-red outline, extruded shadow"""
    lines = text.split('\n')
    def mk(fill, stroke, sf):
        ims = [spaced(l, F_BLACK, size, fill, 0, stroke, sf) for l in lines]
        return gfx.stack(ims, gap=-int(size * 0.12))
    sw = max(3, int(size * 0.065))
    outline = pad_im(mk((90, 10, 4), sw, (90, 10, 4)), 20)
    core = pad_im(mk((255, 255, 255), 0, (0, 0, 0)), 20)
    # align core inside outline
    core2 = Image.new('RGBA', outline.size, (0, 0, 0, 0))
    core2.alpha_composite(core, ((outline.width - core.width) // 2, (outline.height - core.height) // 2))
    fillg = grad_fill(core2, [(0.0, (255, 250, 150)), (0.45, (255, 214, 40)), (0.75, (255, 140, 20)), (1.0, (230, 70, 10))])
    # inner highlight stroke
    hi = core2.filter(ImageFilter.MinFilter(3))
    out = Image.new('RGBA', (outline.width + 16, outline.height + 16), (0, 0, 0, 0))
    ext = outline.copy(); ext = Image.composite(Image.new('RGBA', ext.size, (40, 4, 2, 255)), Image.new('RGBA', ext.size, (0, 0, 0, 0)), ext.split()[3])
    for k in range(1, 6):
        out.alpha_composite(ext, (k, k + 1))
    out.alpha_composite(outline, (0, 0))
    out.alpha_composite(fillg, (0, 0))
    out = out.rotate(tilt, resample=Image.BICUBIC, expand=True)
    return gfx.shadowed(out, 10, (0, 8), 150, 24)

def metal(text, size=150, spacing=0.10, tint=None):
    """chrome title text with letter spacing (style-2 '最大收购案')"""
    lines = text.split('\n')
    base = gfx.stack([spaced(l, F_BLACK, size, (255, 255, 255), spacing) for l in lines], gap=-int(size * 0.1))
    base = pad_im(base, 12)
    stops = [(0.0, (255, 255, 255)), (0.42, (236, 236, 244)), (0.52, (150, 150, 166)), (0.62, (206, 206, 218)), (1.0, (120, 120, 136))]
    if tint == 'gold':
        stops = [(0.0, (255, 248, 210)), (0.42, (250, 222, 140)), (0.52, (176, 130, 50)), (0.62, (236, 196, 110)), (1.0, (150, 104, 30))]
    if tint == 'lav':
        stops = [(0.0, (250, 244, 255)), (0.42, (226, 206, 255)), (0.52, (150, 110, 220)), (0.62, (206, 180, 255)), (1.0, (120, 80, 200))]
    g = grad_fill(base, stops)
    edge = Image.composite(Image.new('RGBA', base.size, (20, 18, 28, 255)), Image.new('RGBA', base.size, (0, 0, 0, 0)), base.split()[3].filter(ImageFilter.MaxFilter(5)))
    out = Image.new('RGBA', base.size, (0, 0, 0, 0)); out.alpha_composite(edge); out.alpha_composite(g)
    return gfx.shadowed(out, 16, (0, 10), 200, 30)

def caps(text, size=26, fill=(200, 200, 210), spacing=0.25):
    return spaced(text.upper(), F_DEMI, size, fill, spacing)

# ------------------------------------------------------------------ backgrounds
_bgcache = {}
def bg(tint='purple', backdrop=None, dim=0.22):
    key = (tint, id(backdrop) if backdrop is not None else None)
    if key in _bgcache: return _bgcache[key]
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = {'purple': (24, 14, 34), 'navy': (16, 20, 30), 'wine': (30, 12, 16), 'char': (16, 15, 19)}[tint]
    glow = {'purple': (120, 50, 190), 'navy': (40, 70, 130), 'wine': (150, 30, 40), 'char': (70, 60, 90)}[tint]
    img = np.zeros((H, W, 3), np.float32); img[:] = base[::-1]
    if backdrop is not None:
        b = gfx.fit_cover(backdrop, W, H).astype(np.float32)
        gray = b.mean(2, keepdims=True); b = gray * 0.6 + b * 0.4
        b = cv2.GaussianBlur(b, (0, 0), 3)
        img = img * (1 - dim) + b * dim
    d = np.sqrt(((x - W * 0.5) / W) ** 2 + ((y - H * 0.42) / H) ** 2)
    img += (np.clip(0.55 - d, 0, 1) ** 1.5 * 0.55)[..., None] * np.array(glow[::-1], np.float32)
    # dotted grid texture
    dots = ((x.astype(int) % 48 == 0) & (y.astype(int) % 48 == 0))
    img[dots] += 18
    rng = np.random.default_rng(3); img += rng.normal(0, 2.2, img.shape)
    v = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H / 2) / H) ** 2)
    img *= (1 - np.clip(v - 0.3, 0, 1) * 1.1)[..., None]
    out = np.clip(img, 0, 255).astype(np.uint8)
    _bgcache[key] = out
    return out

# ------------------------------------------------------------------ medallion (glass disc)
def medallion(d, color='purple', title='', sub='', icon=None, number=None, title_size=None, portrait=None, side_chars=None):
    S = 2  # supersample
    D = d * S
    lt, md, dk = PAL[color]
    yy, xx = np.mgrid[0:D, 0:D].astype(np.float32)
    cx = cy = D / 2; r = D / 2 - 2 * S
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    # radial gradient, lit from top-left
    lx = np.sqrt((xx - cx * 0.7) ** 2 + (yy - cy * 0.55) ** 2) / (r * 1.6)
    t = np.clip(lx, 0, 1)
    rgb = np.zeros((D, D, 3), np.float32)
    for c in range(3):
        rgb[..., c] = np.interp(t, [0, 0.45, 1.0], [lt[c], md[c], dk[c]])
    if portrait is not None:
        p = cv2.cvtColor(gfx.fit_cover(portrait, D, D), cv2.COLOR_BGR2RGB).astype(np.float32)
        tintc = np.array(md, np.float32)
        p = p * 0.82 + tintc * 0.18
        rgb = p
    # rim: bright edge band + inner dark line
    rim = np.clip(1 - np.abs(dist - 0.985) / 0.02, 0, 1)
    rgb = rgb * (1 - rim[..., None] * 0.7) + np.array(lt, np.float32) * rim[..., None] * 0.7 + 255 * rim[..., None] * 0.25
    inner = np.clip(1 - np.abs(dist - 0.90) / 0.006, 0, 1) * 0.35
    rgb = rgb * (1 - inner[..., None]) + 255 * inner[..., None]
    # specular arc top
    spec = np.clip(1 - ((xx - cx) ** 2 / (r * 0.75) ** 2 + (yy - cy * 0.45) ** 2 / (r * 0.38) ** 2), 0, 1) ** 2 * 0.15
    spec *= (yy < cy * 0.95)
    rgb = rgb + 255 * spec[..., None]
    # edge darkening (glass depth)
    rgb *= (1 - np.clip(dist - 0.75, 0, 1) * 0.6)[..., None]
    alpha = np.clip((1 - dist) * r / 1.2, 0, 1) * 255
    arr = np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8)
    im = Image.fromarray(arr, 'RGBA').resize((d, d), Image.LANCZOS)
    dr = ImageDraw.Draw(im)
    txtcol = (255, 255, 255) if color != 'gold' else (120, 84, 20)
    if portrait is None:
        # ornaments + dashed lines
        def dashed(y, half):
            x = d / 2 - half
            while x < d / 2 + half:
                dr.line([x, y, min(x + 4, d / 2 + half), y], fill=txtcol + (110,), width=1); x += 8
        cy2 = d * 0.5
        dr.polygon([(d / 2, d * 0.12), (d / 2 + 6, d * 0.12 + 6), (d / 2, d * 0.12 + 12), (d / 2 - 6, d * 0.12 + 6)], outline=txtcol + (150,))
        dr.line([d / 2 - 40, d * 0.12 + 6, d / 2 - 10, d * 0.12 + 6], fill=txtcol + (110,), width=1)
        dr.line([d / 2 + 10, d * 0.12 + 6, d / 2 + 40, d * 0.12 + 6], fill=txtcol + (110,), width=1)
        dr.polygon([(d / 2, d * 0.86), (d / 2 + 5, d * 0.86 + 5), (d / 2, d * 0.86 + 10), (d / 2 - 5, d * 0.86 + 5)], outline=txtcol + (150,))
        content = []
        if icon is not None: content.append(icon)
        if title:
            ts = title_size or int(d * (0.20 if len(title) <= 3 else 0.16))
            content.append(spaced(title, F_BLACK, ts, txtcol + (240,), 0.10))
        if sub: content.append(caps(sub, max(12, int(d * 0.055)), txtcol + (170,), 0.22))
        if content:
            blk = gfx.stack(content, gap=int(d * 0.03))
            if blk.width > d * 0.78:
                s = d * 0.78 / blk.width; blk = blk.resize((int(blk.width * s), int(blk.height * s)), Image.LANCZOS)
            y0 = int(cy2 - blk.height / 2)
            if icon is None and title:
                dashed(y0 - 10, d * 0.22)
            im.alpha_composite(blk, (int((d - blk.width) / 2), y0))
    if side_chars:
        a, b = side_chars
        ca = spaced(a, F_BLACK, int(d * 0.26), LAVENDER + (235,), 0, 3, (40, 10, 70))
        cb = spaced(b, F_BLACK, int(d * 0.26), LAVENDER + (235,), 0, 3, (40, 10, 70))
        im.alpha_composite(ca, (int(d * 0.04), int(d * 0.38)))
        im.alpha_composite(cb, (int(d * 0.96 - cb.width), int(d * 0.38)))
    out = pad_im(im, 30)
    if number is not None:
        nb = 44
        badge = Image.new('RGBA', (nb, nb), (0, 0, 0, 0)); bd = ImageDraw.Draw(badge)
        bd.ellipse([0, 0, nb - 1, nb - 1], fill=md + (255,), outline=(255, 255, 255, 200), width=2)
        n = spaced(str(number), F_BLACK, 26, (255, 255, 255), 0)
        badge.alpha_composite(n, ((nb - n.width) // 2, (nb - n.height) // 2))
        out.alpha_composite(badge, (30 + d // 2 - nb // 2, 6))
    # glow + shadow
    a = out.split()[3]
    glow = Image.new('RGBA', out.size, md + (0,)); glow.putalpha(a.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.55)))
    res = Image.new('RGBA', out.size, (0, 0, 0, 0)); res.alpha_composite(glow); res.alpha_composite(out)
    return gfx.shadowed(res, 16, (0, 14), 170, 24)

# ------------------------------------------------------------------ panels
def glass(w, h, radius=26, fill=(14, 12, 20, 205), border=(200, 170, 255, 70)):
    im = gfx.rounded((w, h), radius, fill, outline=border, width=2)
    d = ImageDraw.Draw(im)
    d.line([radius, 2, w - radius, 2], fill=(255, 255, 255, 60), width=1)
    return im

def name_card(en, role, nickname=None, cn_big=None):
    t1 = spaced(en, F_LIGHT, 64, (245, 245, 250), 0.06) if en else None
    parts = []
    if cn_big: parts.append(spaced(cn_big, F_MED, 62, (245, 245, 250), 0.18))
    if t1: parts.append(t1)
    head = gfx.stack(parts, 'l', 6)
    r = spaced(role, F_DEMI, 32, (215, 205, 235), 0.28)
    w = max(head.width, r.width) + 120; h = head.height + r.height + 80
    card = glass(w, h, 18, (8, 8, 12, 190), (255, 255, 255, 30))
    card.alpha_composite(head, (50, 26))
    ImageDraw.Draw(card).line([50, 26 + head.height + 16, w - 40, 26 + head.height + 16], fill=(255, 255, 255, 90), width=2)
    card.alpha_composite(r, (50, 26 + head.height + 30))
    out = pad_im(card, 40)
    if nickname:
        nk = comic(nickname, 92, -4)
        big = Image.new('RGBA', (max(out.width, out.width - 60 + nk.width // 2), out.height + nk.height - 70), (0, 0, 0, 0))
        big.alpha_composite(out, (0, 0))
        big.alpha_composite(nk, (big.width - nk.width, out.height - 70))
        out = big
    return gfx.shadowed(out, 14, (0, 8), 150, 10)

def section_tab(cn, en=''):
    t = spaced(cn, F_MED, 38, (240, 240, 250), 0.10)
    e = caps(en, 16, (150, 160, 190), 0.2) if en else None
    w = max(t.width, e.width if e else 0) + 90; h = 86 if e else 68
    im = Image.new('RGBA', (w + 30, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    poly = [(0, 0), (w + 26, 0), (w, h - 1), (0, h - 1)]
    d.polygon(poly, fill=(18, 24, 44, 225), outline=(120, 140, 200, 150))
    d.rectangle([0, 0, 8, h - 1], fill=LAVENDER + (255,))
    im.alpha_composite(t, (34, 10 if e else 14))
    if e: im.alpha_composite(e, (36, 14 + t.height + 2))
    return gfx.shadowed(im, 10, (0, 6), 140, 18)

def label(text):
    t = spaced(text, F_BOLD, 46, (255, 255, 255), 0.04)
    w, h = t.width + 74, t.height + 30
    im = glass(w, h, 14, (10, 8, 16, 200), (255, 255, 255, 40))
    ImageDraw.Draw(im).rounded_rectangle([12, 12, 19, h - 13], 3, fill=LAVENDER + (255,))
    im.alpha_composite(t, (40, 14))
    return gfx.shadowed(im, 10, (0, 6), 140, 18)

def stat(num, unit='', cap='', numcol=(255, 255, 255), size=150):
    n = spaced(num, F_BLACK, size, numcol, 0.0)
    n = n.resize((int(n.width * 0.84), n.height), Image.LANCZOS)  # condensed
    parts = [n]
    if unit:
        u = spaced(unit, F_BLACK, int(size * 0.34), GOLDTXT, 0.02)
        row = Image.new('RGBA', (n.width + u.width + 10, n.height), (0, 0, 0, 0))
        row.alpha_composite(n, (0, 0)); row.alpha_composite(u, (n.width + 10, n.height - u.height - int(size * 0.04)))
        parts = [row]
    blk = parts[0]
    if cap:
        c = spaced(cap, F_MED, int(size * 0.26), LAVENDER, 0.2)
        w = max(blk.width, c.width)
        out = Image.new('RGBA', (w, blk.height + c.height + 34), (0, 0, 0, 0))
        out.alpha_composite(blk, ((w - blk.width) // 2, 0))
        d = ImageDraw.Draw(out); x = 0
        while x < w:
            d.line([x, blk.height + 12, min(x + 6, w), blk.height + 12], fill=(255, 255, 255, 120), width=2); x += 12
        out.alpha_composite(c, ((w - c.width) // 2, blk.height + 28))
        blk = out
    return gfx.shadowed(blk, 12, (0, 8), 170, 20)

def subtitle(text):
    t = spaced(text, F_BOLD, 54, (255, 255, 255), 0.0, 3, (20, 16, 26))
    # slight italic like reference
    t = t.transform(t.size, Image.AFFINE, (1, 0.14, -0.14 * t.height * 0.5, 0, 1, 0), resample=Image.BICUBIC)
    t = pad_im(t, 6)
    return gfx.shadowed(t, 5, (0, 3), 190, 12)
