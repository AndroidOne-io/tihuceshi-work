# ======================= SEGMENT 4: narration 112.85 -> 136.6  (exec'd inside v4.py after seg3)
# --- A: pelicans getting better over the years: rising vector curve of medallions, newest one ringed
v17b = Vid(CR + '17_19_选用片段.mp4')
EVO_IMG = [crude[2], crude[7], crude[1], o.grab(CR + '17_19_选用片段.mp4', 1.0)[78:295, 80:470], o.grab(CR + '18_20_选用片段.mp4', 1.0)[0:296, 0:638]]
EVO = [B(o.token(d, 'grey', portrait=im, anchors=False)) for im, d in zip(EVO_IMG, (200, 220, 240, 270, 330))]
EVO_POS = [(330, 800), (640, 690), (950, 560), (1270, 420), (1600, 300)]
EVO_T = [113.31, 113.7, 114.1, 114.5, 114.9]
def sA4(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy()
    # dashed bezier through the medallions (vector-drawing look)
    pts = np.array(EVO_POS, np.float32); prog = ease((n - 113.2) / 2.0)
    curve = []
    for i in range(len(pts) - 1):
        a_, b_ = pts[i], pts[i + 1]; c_ = (a_ + b_) / 2 + np.array([0, 60])
        for s in np.linspace(0, 1, 20): curve.append((1 - s) ** 2 * a_ + 2 * (1 - s) * s * c_ + s * s * b_)
    curve = np.array(curve); m = int(len(curve) * prog)
    for i in range(0, m - 1, 2): cv2.line(f, tuple(curve[i].astype(int)), tuple(curve[i + 1].astype(int)), o.ORANGE[::-1], 4, cv2.LINE_AA)
    for k, (img, (cx, cy), tk) in enumerate(zip(EVO, EVO_POS, EVO_T)):
        if n < tk: continue
        u = back_out((n - tk) / 0.35); put(f, cv2.resize(img, None, fx=0.5 + 0.5 * u, fy=0.5 + 0.5 * u), cx, cy, min(1, (n - tk) / 0.08))
    if n > 116.4:  # 新的用途: newest pelican gets the selection ring, pulsing
        r = 210 + 10 * np.sin((n - 116.4) * 9); ring_sel(f, EVO_POS[4][0], EVO_POS[4][1], r, (n - 116.4) / 0.3)
    z = 1 + 0.05 * ease((n - 116.4) / 1.0)
    f = cv2.warpAffine(f, cv2.getRotationMatrix2D((1500, 330), 0, z), (W, H), borderMode=cv2.BORDER_REFLECT)
    o.pip(f, hf_small(t), x=60, y=60, d=200); return f
S(112.85, 117.5, sA4, 'info'); X(T(112.85), 'whoosh')
for tk in EVO_T: X(T(tk), 'pop')
X(T(116.4), 'shine')
S(117.5, 121.1, host_sc(1.0, 0.04), 'host')

# --- pause 121.1 (+1.0s): brush title 降智, halftone of the good result, red
RES = o.grab(CR + '23_24_选用片段.mp4', 3.0)[530:1330, 600:2136]
HALF4 = q.halftone_bg(cv2.resize(RES, (1920, 1000)), (230, 50, 50))
BR4 = B(q.brush_title('降智', 420))
c0, c1 = PT(121.1)
def sBrush4(t, t0, t1):
    tl = t - t0; f = HALF4.copy()
    s = 1.2 - 0.2 * ease(tl / 0.18) + 0.04 * tl
    put(f, cv2.resize(BR4, None, fx=s, fy=s), W // 2, 540, min(1, tl / 0.06))
    return q.glitch(f, max(0, 1 - tl / 0.25) * 0.9, int(tl * 30) + 5)
S(c0, c1, sBrush4, 'title', out=True)
S(121.1 + 1e-6, 123.0, host_sc(1.04, 0.05), 'host')

# --- D: GPT, Claude ... and the rest (no Chinese models on screen)
TK_GPT = B(o.token(330, 'cyan', 'GPT', anchors=True, title_size=90)); TK_CL = B(o.token(330, 'orange', 'Claude', anchors=True, title_size=74))
TK_ETC = [B(o.token(190, c, n_, anchors=False, title_size=44)) for n_, c in [('Gemini', 'blue'), ('Grok', 'grey'), ('Llama', 'violet'), ('Mistral', 'red')]]
def sD4(t, t0, t1):
    n = N(t); f = BG.copy()
    for img, cx, tk in ((TK_GPT, 640, 123.49), (TK_CL, 1280, 123.97)):
        if n < tk: continue
        u = back_out((n - tk) / 0.35); put(f, cv2.resize(img, None, fx=0.5 + 0.5 * u, fy=0.5 + 0.5 * u), cx, 420, min(1, (n - tk) / 0.08))
    for k, img in enumerate(TK_ETC):
        tk = 124.78 + k * 0.08
        if n < tk: continue
        u = back_out((n - tk) / 0.3); put(f, cv2.resize(img, None, fx=0.5 + 0.5 * u, fy=0.5 + 0.5 * u), 480 + k * 320, 790, 0.85 * min(1, (n - tk) / 0.08))
    o.pip(f, hf_small(t), x=W - 260, y=60, d=200); return f
S(123.0, 125.75, sD4, 'info'); X(T(123.0), 'whoosh'); X(T(123.49), 'pop'); X(T(123.97), 'pop'); X(T(124.78), 'pop')

# --- E: "model feels dumb" -> the prompt, typed into a big glass input bar
DIZZY = B(st.sticker(st.emoji('🥴', 280), 280, 14, 8))
def sE1(t, t0, t1):
    n = N(t); f = host_full(n, 1.05 + 0.03 * (t - t0) / (t1 - t0))
    if n > 126.95:
        u = back_out((n - 126.95) / 0.3); put(f, cv2.resize(DIZZY, None, fx=0.5 + 0.5 * u, fy=0.5 + 0.5 * u), 1580, 380, min(1, (n - 126.95) / 0.08))
    return f
S(125.75, 127.55, sE1, 'host'); X(T(126.95), 'pop')
PROMPT = '创建一个html，绘制一个|鹈鹕骑自行车的2D SVG动画'
from PIL import ImageFont
F_P = ImageFont.truetype(st.F_MED, 92)
def prompt_bar(nchar, caret, press):
    bw, bh = 1720, 380
    im = Image.new('RGBA', (bw + 80, bh + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 40, 40 + bw, 40 + bh], 48, fill=(24, 30, 44, 235), outline=(255, 138, 42, 255), width=4)
    lines = PROMPT.split('|'); left = nchar; y = 80
    for ln in lines:
        s = ln[:max(0, left)]; left -= len(ln)
        d.text((100, y), s, font=F_P, fill=(245, 245, 250, 255))
        if 0 <= left + len(ln) - len(s) and len(s) < len(ln) or (left <= 0 and ln is lines[-1]):
            pass
        y += 130
    # caret after the last typed char
    if caret:
        k = nchar; li = 0
        if k > len(lines[0]): li = 1; k -= len(lines[0])
        x = 100 + d.textlength(lines[li][:k], font=F_P); yy = 80 + li * 130
        d.rectangle([x + 6, yy + 8, x + 13, yy + 106], fill=(255, 138, 42, 255))
    # send button
    r = 52 * (1 - 0.15 * press); cx, cy = 40 + bw - 90, 40 + bh - 80
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 138, 42, 255))
    d.polygon([(cx - 18, cy + 6), (cx, cy - 20), (cx + 18, cy + 6)], fill=(20, 20, 28, 255)); d.rectangle([cx - 5, cy - 6, cx + 5, cy + 22], fill=(20, 20, 28, 255))
    return o.to_bgra(im)
NCH = len(PROMPT.replace('|', ''))
def sE2(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy()
    nc = int(NCH * min(1, max(0, (n - 127.8) / 1.25)))
    press = max(0, 1 - abs(n - 129.25) / 0.12) if n > 129.1 else 0
    bar = prompt_bar(nc, int(tl * 4) % 2 == 0 or nc < NCH, press)
    u = ease(tl / 0.3); put(f, bar, W // 2, int(540 + 300 * (1 - u)), u)
    if n > 129.25: flash(f, 0.35 * max(0, 1 - (n - 129.25) / 0.15))
    o.pip(f, hf_small(t), x=60, y=60, d=200); return f
S(127.55, 129.45, sE2, 'info'); X(T(127.55), 'whoosh'); X(T(129.25), 'pop')
for i in range(0, NCH, 2): X(T(127.8) + 1.25 * i / NCH, 'type')

# --- F: pass (good result + stamp) / riddled with bugs (crude + red pen) -> congrats -> 降智 stamp
v23 = Vid(CR + '23_24_选用片段.mp4')
ST_PASS = B(o.stamp('通过', size=200, angle=-10)); ST_DUMB = B(o.stamp('降智', size=260, angle=-12))
BAD = crude[6]
PARTY = B(st.sticker(st.emoji('🎉', 260), 260, 14, -10))
def sF4(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy()
    if n < 131.6:
        fr = v23.get(1.0 + tl)[530:1330, 600:2136]
        u = ease(tl / 0.35); card = persp(cv2.resize(fr, (1300, 677)), 1300, 8 * (1 - u) + 3)
        put(f, card, int(W // 2 + 400 * (1 - u)), 520, u)
        if n > 130.72:
            v = ease((n - 130.72) / 0.15); s = 1.8 - 0.8 * v; put(f, cv2.resize(ST_PASS, None, fx=s, fy=s), 1500, 260, v)
    else:
        k = n - 131.6; u = ease(k / 0.25)
        shake = int(14 * np.sin(k * 70) * max(0, 1 - (k - 0.3) / 0.6)) if k > 0.3 else 0
        card = B(st.photo_card(BAD, 760, border=10, angle=-3))
        put(f, card, W // 2 + shake - int(500 * (1 - u)), 520, u)
        for j, (dx, dy) in enumerate([(-200, -150), (160, -40), (-60, 180)]):
            pen_x(f, W // 2 + dx + shake, 520 + dy, 50, (n - (131.95 + j * 0.2)) / 0.22, 12)
        if n > 132.88:  # congrats: confetti + party sticker
            kk = n - 132.88; rr = np.random.default_rng(11)
            for i in range(80):
                x = int(rr.uniform(0, W) + 40 * np.sin(kk * 3 + i)); y = int(-60 + rr.uniform(400, 800) * kk + rr.uniform(-250, 0))
                c = [(42, 138, 255), (232, 214, 78), (52, 64, 232), (255, 255, 255)][i % 4]
                if 0 < y < H: cv2.rectangle(f, (x, y), (x + 10, y + 18), c, -1)
            v = back_out(kk / 0.3); put(f, cv2.resize(PARTY, None, fx=0.5 + 0.5 * v, fy=0.5 + 0.5 * v), 1560, 300, min(1, kk / 0.08))
        if n > 135.1:
            v = ease((n - 135.1) / 0.15); s = 2.0 - 1.0 * v; put(f, cv2.resize(ST_DUMB, None, fx=s, fy=s), W // 2 + 40, 560, v)
            flash(f, 0.25 * max(0, 1 - (n - 135.25) / 0.12) if n > 135.25 else 0)
        if 131.6 < n < 131.75: f = q.glitch(f, 0.8, int(k * 60))
    o.pip(f, hf_small(t), x=60, y=H - 260, d=200); return f
S(129.45, 136.6, sF4, 'info'); X(T(129.45), 'whoosh'); X(T(130.72), 'hit'); X(T(131.6), 'whoosh')
for j in range(3): X(T(131.95 + j * 0.2), 'scribble')
X(T(132.88), 'pop'); X(T(135.25), 'thud')
