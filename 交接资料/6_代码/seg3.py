# ======================= SEGMENT 3: narration 72.25 -> 112.85  (exec'd inside v4.py: uses S, X, T, N, put, B, ...)
def persp(img, w, yaw=0.0, radius=18, border=8):
    """card with white rim, perspective-turned by yaw (deg, + = right edge farther). returns BGRA"""
    h = int(img.shape[0] * w / img.shape[1])
    c = B(st.photo_card(img, w, border=border, radius=radius))
    ch, cw = c.shape[:2]; k = np.tan(np.radians(abs(yaw))) * 0.55
    src = np.float32([[0, 0], [cw, 0], [cw, ch], [0, ch]])
    if yaw >= 0: dst = np.float32([[0, 0], [cw * (1 - k * 0.25), ch * k * 0.5], [cw * (1 - k * 0.25), ch * (1 - k * 0.5)], [0, ch]])
    else: dst = np.float32([[cw * k * 0.25, ch * k * 0.5], [cw, 0], [cw, ch], [cw * k * 0.25, ch * (1 - k * 0.5)]])
    return cv2.warpPerspective(c, cv2.getPerspectiveTransform(src, dst), (cw, ch), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
def ring_sel(f, cx, cy, r, frac=1.0, col=None, w=3):
    """orange vector selection ring with 4 anchor squares (our signature)"""
    col = col or o.ORANGE[::-1]
    if frac <= 0: return
    cv2.ellipse(f, (int(cx), int(cy)), (int(r), int(r)), -90, 0, 360 * min(1, frac), col, w, cv2.LINE_AA)
    if frac >= 1:
        for a in (0, 90, 180, 270):
            x = int(cx + r * np.cos(np.radians(a))); y = int(cy + r * np.sin(np.radians(a)))
            cv2.rectangle(f, (x - 8, y - 8), (x + 8, y + 8), (28, 20, 20), -1); cv2.rectangle(f, (x - 8, y - 8), (x + 8, y + 8), col, 2)
def disc(d, tint, inner):
    """glass disc with an image (BGRA) inside"""
    t = B(o.token(d, tint, '', anchors=False)); s = d * 0.72 / max(inner.shape[:2])
    im = cv2.resize(inner, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    o.blit(t, im, t.shape[1] // 2 - im.shape[1] // 2, t.shape[0] // 2 - im.shape[0] // 2); return t
def flash(f, a):
    if a > 0: f[:] = (f.astype(np.float32) * (1 - a) + 255 * a).astype(np.uint8)
    return f

# --- A: host + Simon token slides in beside him
TOK_SIMON3 = B(M2.tok_simon(330))
def sA(t, t0, t1):
    n = N(t); f = host_full(n, 1.04 + 0.03 * (t - t0) / (t1 - t0))
    if n > 73.25:
        u = back_out((n - 73.25) / 0.4); put(f, cv2.resize(TOK_SIMON3, None, fx=0.6 + 0.4 * u, fy=0.6 + 0.4 * u), int(1560 + 200 * (1 - ease((n - 73.25) / 0.3))), 420, min(1, (n - 73.25) / 0.1))
    return f
S(72.25 + 1e-6, 75.9, sA, 'host'); X(T(73.25), 'pop')

# --- B: pelican + bicycle never seen together: scrolling data wall, two discs meet, empty overlap
PEL_IMG = o.grab(CR + '18_20_选用片段.mp4', 1.0)[55:205, 845:1085]
BIKE = B(st.emoji('🚲', 300))
D_PEL = B(o.token(440, 'cyan', portrait=PEL_IMG, anchors=False)); D_BIKE = disc(440, 'orange', BIKE)
EM = ['🐦', '🚲', '🦩', '🛵', '🐧', '🚗', '🦆', '🛴', '🐟', '🏍️', '🦅', '🚌']
EMI = [B(st.emoji(e, 70)) for e in EM]
WALL = np.zeros((H * 2, W, 4), np.uint8)
rng3 = np.random.default_rng(7)
for r in range(0, H * 2, 130):
    for c in range(0, W, 130):
        x0, y0 = c + 12, r + 12
        cv2.rectangle(WALL, (x0, y0), (x0 + 106, y0 + 106), (90, 70, 60, 120), 2, cv2.LINE_AA)
        e = EMI[rng3.integers(len(EMI))]; ex, ey = x0 + 53 - e.shape[1] // 2, y0 + 53 - e.shape[0] // 2
        if ey + e.shape[0] > H * 2 or ex + e.shape[1] > W: continue
        reg = WALL[ey:ey + e.shape[0], ex:ex + e.shape[1]]; a_ = e[..., 3:] / 255.0
        reg[..., :3] = (e[..., :3] * a_ + reg[..., :3] * (1 - a_)).astype(np.uint8); reg[..., 3] = np.maximum(reg[..., 3], (e[..., 3] * 0.5).astype(np.uint8))
def sB(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy()
    # data wall (training data) scrolling, dims after "没有任何"
    off = int((tl * 140) % H); dimw = 0.9 if n < 77.58 else 0.9 - 0.6 * ease((n - 77.58) / 0.6)
    o.blit(f, WALL[off:off + H], 0, 0, 0.5 * dimw * ease(tl / 0.3))
    # scan beam
    bx = int((tl * 900) % (W + 400)) - 200
    beam = np.zeros((H, 260, 4), np.uint8); beam[..., :3] = (232, 214, 78); beam[..., 3] = (np.exp(-((np.arange(260) - 130) / 60.0) ** 2) * 70).astype(np.uint8)[None, :]
    if n < 78.6: o.blit(f, beam, bx, 0, 1.0)
    # discs slide in, then move to overlap
    a = ease((n - 75.96) / 0.4); b = ease((n - 76.3) / 0.4); m = ease((n - 77.58) / 0.5)
    lx = int(-300 + (560 + 300) * a - 60 * m); rx = int(W + 300 - (W + 300 - 1360) * b + 60 * m)
    if n > 75.9: put(f, D_PEL, lx, 520, min(1, a * 3))
    if n > 76.25: put(f, D_BIKE, rx, 520, min(1, b * 3))
    # the overlap is empty: dashed ring + pulsing glow, then red pen circle
    if n > 78.0:
        cx = W // 2; r = (150 + 6 * np.sin(tl * 8)) * ease((n - 78.0) / 0.3)
        cv2.line(f, (lx + 230, 520), (cx - int(r) - 10, 520), o.CYAN[::-1], 3, cv2.LINE_AA); cv2.line(f, (cx + int(r) + 10, 520), (rx - 230, 520), o.ORANGE[::-1], 3, cv2.LINE_AA)
        for k in range(0, 360, 20): cv2.ellipse(f, (cx, 520), (int(r), int(r)), 0, k, k + 11, o.ORANGE[::-1], 4, cv2.LINE_AA)
    if n > 78.54: pen_circle(f, W // 2, 520, 200, 190, (n - 78.54) / 0.45, 10)
    o.pip(f, hf_small(t), x=60, y=60, d=200); return f
S(75.9, 80.25, sB, 'info'); X(T(75.96), 'whoosh'); X(T(76.3), 'whoosh'); X(T(77.58), 'pop'); X(T(78.54), 'scribble')

# --- C: four model animations fanned in perspective (labels cropped)
v17 = Vid(CR + '17_19_选用片段.mp4')
C17 = [(80, 78, 470, 295), (760, 68, 1166, 295), (70, 440, 466, 672), (752, 435, 1166, 672)]
def sC(t, t0, t1):
    tl = t - t0; n = N(t); f = BGW.copy(); fr = v17.get(min(tl, 3.8))
    pos = [(560, 330, 12), (1360, 330, -12), (560, 760, 12), (1360, 760, -12)]
    for k, ((x0, y0, x1, y1), (cx, cy, yaw)) in enumerate(zip(C17, pos)):
        d0 = k * 0.12; u = ease((tl - d0) / 0.35)
        if u <= 0: continue
        card = persp(fr[y0:y1, x0:x1], 700, yaw * (1 - 0.4 * ease((n - 81.6) / 0.8)))
        sx = cx + (1 if cx > W / 2 else -1) * 500 * (1 - u)
        put(f, card, int(sx), cy, u)
    z = 1 + 0.06 * ease((n - 81.64) / 1.2)
    f = cv2.warpAffine(f, cv2.getRotationMatrix2D((W / 2, H / 2), 0, z), (W, H), borderMode=cv2.BORDER_REFLECT)
    return f
S(80.25, 83.72, sC, 'info')
for k in range(4): X(T(80.25) + k * 0.12, 'whoosh') if k % 2 == 0 else None

# --- pause 83.72 (+1.0s): brush title 没法作假 on halftone of the clip
HALF3 = q.halftone_bg(o.grab(CR + '17_19_选用片段.mp4', 2.0), (90, 160, 255))
BR3 = B(q.brush_title('没法作假', 330))
b0, b1 = PT(83.72)
def sBrush(t, t0, t1):
    tl = t - t0; f = HALF3.copy()
    s = 1.18 - 0.18 * ease(tl / 0.18) + 0.04 * tl
    put(f, cv2.resize(BR3, None, fx=s, fy=s), W // 2, 540, min(1, tl / 0.06))
    return q.glitch(f, max(0, 1 - tl / 0.25) * 0.9, int(tl * 30))
S(b0, b1, sBrush, 'title', out=True)

# --- D/E: one good animation; first frozen (drawing it right), then it moves: seat, then pedals
v18 = Vid(CR + '18_20_选用片段.mp4')
Q18 = (0, 0, 638, 296)
def sD(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy()
    play = max(0.0, n - 90.74) if n is not None else 0.0
    fr = v18.get(0.2 + play)[Q18[1]:Q18[3], Q18[0]:Q18[2]]
    big = cv2.resize(fr, (1500, int(1500 * fr.shape[0] / fr.shape[1])), interpolation=cv2.INTER_CUBIC)  # 1500x696
    u = ease(tl / 0.4); yaw = 10 * (1 - u) + (0 if n < 90.74 else 0)
    card = persp(big, 1500, yaw)
    # zoom targets in card coords (card has 8px border): bird body ~ (0.42,0.45), pedal ~ (0.40,0.80)
    zt, fx, fy = 1.0, 0.5, 0.5
    if n > 91.6: k = ease((n - 91.6) / 0.5); zt += 0.55 * k; fx, fy = 0.5 + (0.40 - 0.5) * k, 0.5 + (0.42 - 0.5) * k
    if n > 92.7: k = ease((n - 92.7) / 0.5); fx, fy = 0.40 + (0.40 - 0.40) * k, 0.42 + (0.78 - 0.42) * k; zt += 0.25 * k
    ch, cw = card.shape[:2]
    cx, cy = W // 2 + int((0.5 - fx) * cw * zt), 540 + int((0.5 - fy) * ch * zt)
    cz = cv2.resize(card, None, fx=zt, fy=zt, interpolation=cv2.INTER_LINEAR)
    put(f, cz, cx, cy, u if tl < 0.4 else 1)
    def at(px, py): return cx + (px - 0.5) * cw * zt, cy + (py - 0.5) * ch * zt
    # "drawn right": selection rings on pelican & bike while frozen
    if 87.3 < n < 90.7:
        x, y = at(0.42, 0.42); ring_sel(f, x, y, 160 * zt, (n - 87.3) / 0.35)
        x, y = at(0.42, 0.75); ring_sel(f, x, y, 190 * zt, (n - 88.1) / 0.35, o.CYAN[::-1])
    if n > 91.7:
        x, y = at(0.42, 0.45); ring_sel(f, x, y, 170 * zt * (1 if n < 92.7 else 0.0), (n - 91.7) / 0.3)
    if n > 92.78:
        x, y = at(0.39, 0.80); r = 120 * zt
        for k in range(0, 360, 24):
            a0 = k + (n - 92.78) * 360
            cv2.ellipse(f, (int(x), int(y)), (int(r), int(r)), 0, a0, a0 + 13, o.ORANGE[::-1], 6, cv2.LINE_AA)
    o.pip(f, hf_small(t), x=1660, y=60, d=200); return f
S(83.88, 94.2, sD, 'info'); X(T(83.88), 'whoosh'); X(T(87.3), 'pop'); X(T(88.1), 'pop'); X(T(90.74), 'whoosh'); X(T(91.6), 'pop'); X(T(92.78), 'pop')

# --- F: the false bubble — model tokens floating inside, pelican beak pops it
BUB_TOK = [B(o.token(170, c, n_, anchors=False, title_size=40)) for n_, c in [('GPT', 'cyan'), ('Claude', 'orange'), ('Gemini', 'blue'), ('Llama', 'violet'), ('Mistral', 'red'), ('Grok', 'grey')]]
PEL_FLY = B(st.sticker(Image.fromarray(cv2.cvtColor(M2.CUT_PEL, cv2.COLOR_BGRA2RGBA)), 320, 12, -18))
def bubble(R):
    D = 2 * R + 8; yy, xx = np.mgrid[0:D, 0:D].astype(np.float32); d = np.sqrt((xx - D / 2) ** 2 + (yy - D / 2) ** 2) / R
    ang = np.arctan2(yy - D / 2, xx - D / 2)
    rim = np.clip((d - 0.82) / 0.18, 0, 1) ** 2 * (d <= 1.0)
    hue = (ang / np.pi * 90 + 90 + d * 60) % 180
    hsv = np.dstack([hue, np.full_like(d, 140), np.full_like(d, 255)]).astype(np.uint8)
    col = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).astype(np.float32)
    spec = np.exp(-(((xx - D * 0.33) / (R * 0.22)) ** 2 + ((yy - D * 0.3) / (R * 0.12)) ** 2)) * 0.9
    a = np.clip(0.07 + rim * 0.7 + spec, 0, 1) * (d <= 1.0)
    col = col * (1 - spec[..., None]) + 255 * spec[..., None]
    return np.dstack([col, a * 255]).astype(np.uint8)
BUBS = {}
def sF(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy(); cx, cy = W // 2, 520
    pop = 96.96
    if n < pop:
        R = int(260 + 140 * ease((n - 94.2) / 2.6) + 6 * np.sin(tl * 5)); R -= R % 4
        if R not in BUBS: BUBS[R] = bubble(R)
        for k, tk in enumerate(BUB_TOK):
            a = tl * 0.6 + k * np.pi / 3; rr = R * 0.5
            put(f, tk, int(cx + rr * np.cos(a)), int(cy + rr * 0.7 * np.sin(a)))
        put(f, BUBS[R], cx, cy)
        # pelican flies in, beak first
        if n > 95.9:
            u = ease((n - 95.9) / (pop - 95.9)); put(f, PEL_FLY, int(-200 + (cx - R - 40 + 200) * u), int(cy - 60 + 30 * np.sin(u * 3)))
    else:
        k = n - pop; R = 400
        for i, tk in enumerate(BUB_TOK):  # tokens tumble down
            a = i * np.pi / 3; vx = 260 * np.cos(a); vy = -200 + 60 * np.sin(a)
            x = cx + R * 0.5 * np.cos(a) + vx * k; y = cy + R * 0.35 * np.sin(a) + vy * k + 900 * k * k
            put(f, xform(tk, 1.0, k * 200 * (1 if i % 2 else -1)), int(x), int(y))
        for i in range(36):  # droplets
            a = i * np.pi / 18; rr = R * (1 + 1.6 * ease(k / 0.35))
            al = max(0, 1 - k / 0.4)
            if al > 0: cv2.circle(f, (int(cx + rr * np.cos(a)), int(cy + rr * np.sin(a))), 7, (250, 240, 220), -1, cv2.LINE_AA)
        put(f, PEL_FLY, int(cx - R - 40 + 160 * k), int(cy - 60))
        flash(f, 0.6 * max(0, 1 - k / 0.12))
    o.pip(f, hf_small(t), x=60, y=H - 260, d=200); return f
S(94.2, 97.5, sF, 'info'); X(T(94.2), 'whoosh'); X(T(95.9), 'whoosh'); X(T(96.96), 'hit')

# --- G: launch event — spotlit stage screen, giant number, SOTA trophies; then host deadpan
v19 = Vid(CR + '19_21_选用片段.mp4')
BEAM = np.zeros((H * 2, 400, 4), np.uint8)
pts = np.array([[190, 0], [210, 0], [400, H * 2], [0, H * 2]], np.int32)
cv2.fillPoly(BEAM, [pts], (255, 230, 200, 60)); BEAM = cv2.GaussianBlur(BEAM, (0, 0), 25)
NUM = q.glow(B(q.metal_title('+37%', 300, 0.08)), (255, 170, 90), 22, 0.45)
SOTA = B(o.token(250, 'orange', 'SOTA', anchors=True, title_size=64))
def stage_bg(tl):
    f = (BG.astype(np.float32) * 0.8).astype(np.uint8)
    for k, (bx, ph) in enumerate([(300, 0), (W - 300, 1.7), (W // 2, 3.1)]):
        ang = 22 * np.sin(tl * 0.9 + ph)
        bm = cv2.warpAffine(BEAM, cv2.getRotationMatrix2D((200, 0), ang, 1), (400, H * 2), borderValue=(0, 0, 0, 0))
        o.blit(f, bm[:H], bx - 200, -20, 1.0)
    return f
def sG(t, t0, t1):
    tl = t - t0; n = N(t); f = stage_bg(tl)
    if n < 100.14:
        fr = v19.get(2.6 + tl); fr = fr[20:340, 40:600]
        u = ease(tl / 0.35); card = persp(cv2.resize(fr, (1400, 800)), 1400, 8 * (1 - u) + 4)
        # glow behind the screen
        g = np.zeros((card.shape[0] + 160, card.shape[1] + 160, 4), np.uint8); g[80:-80, 80:-80, 3] = card[..., 3]; g[..., :3] = (60, 150, 255)
        g = cv2.GaussianBlur(g, (0, 0), 40); put(f, g, W // 2, 520, 0.8 * u)
        put(f, cv2.resize(card, None, fx=0.9 + 0.1 * u + 0.02 * tl, fy=0.9 + 0.1 * u + 0.02 * tl), W // 2, 520, u)
        if n > 98.88:  # 大吹特吹: confetti
            k = n - 98.88; rr = np.random.default_rng(3)
            for i in range(90):
                x = int(rr.uniform(0, W) + 40 * np.sin(k * 3 + i)); y = int(-40 + (rr.uniform(300, 700)) * k + rr.uniform(-200, 0))
                c = [(42, 138, 255), (232, 214, 78), (52, 64, 232), (255, 255, 255)][i % 4]
                if 0 < y < H: cv2.rectangle(f, (x, y), (x + 10, y + 18), c, -1)
    elif n < 100.92:
        k = n - 100.14
        heights = [180, 240, 300, 380, 640]
        for i, hgt in enumerate(heights):
            hh = int(hgt * ease((k - i * 0.05) / 0.35)); x = 520 + i * 200
            col = o.ORANGE[::-1] if i == 4 else (120, 100, 90)
            cv2.rectangle(f, (x, 900 - hh), (x + 140, 900), col, -1)
        u = back_out((k - 0.25) / 0.3)
        if k > 0.25: put(f, cv2.resize(NUM, None, fx=0.6 + 0.4 * u, fy=0.6 + 0.4 * u), 1420, 230, min(1, (k - 0.25) / 0.08))
    else:
        k = n - 100.92
        for i in range(4):
            d0 = i * 0.18
            if k < d0: continue
            u = back_out((k - d0) / 0.25); s = 1.6 - 0.6 * u
            put(f, xform(SOTA, s, (-1) ** i * 8), 420 + i * 360, 520, min(1, (k - d0) / 0.06))
    return f
S(97.5, 102.1, sG, 'info'); X(T(97.5), 'whoosh'); X(T(100.14), 'whoosh'); X(T(100.45), 'thud')
for i in range(4): X(T(100.92) + i * 0.18, 'hit' if i == 3 else 'pop')
S(102.1, 103.45, host_sc(1.08, 0.0), 'host')

# --- H: six pelicans slam down, the bad one is obvious at a glance
v20 = Vid(CR + '20_22_选用片段.mp4')
C20 = [(10, 6, 770, 380), (806, 6, 1446, 380), (1480, 6, 2170, 380), (10, 552, 750, 960), (800, 552, 1440, 952), (1490, 552, 2170, 948)]
POS20 = [(400 + (k % 3) * 560, 330 + (k // 3) * 400) for k in range(6)]
def sH(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy(); fr = v20.get(max(0, n - 105.0))
    for k, ((x0, y0, x1, y1), (cx, cy)) in enumerate(zip(C20, POS20)):
        d0 = 104.25 + k * 0.1 + (0.0 if k < 3 else 0.5)
        if n < d0: continue
        u = ease((n - d0) / 0.25); s = 1.5 - 0.5 * u
        card = B(st.photo_card(fr[y0:y1, x0:x1], 500, border=6))
        bad = k == 1
        dx = int(10 * np.sin((n - 107.0) * 60) * max(0, 1 - (n - 107.0) / 0.5)) if bad and n > 107.0 else 0
        act = 1.0 if (n < 107.54 or bad or k in (2, 3)) else 0.55
        put(f, cv2.resize(card, None, fx=s, fy=s), cx + dx, cy, min(1, u * 2) * act)
    if n > 107.54: pen_x(f, POS20[1][0], POS20[1][1], 120, (n - 107.54) / 0.3, 16)
    if n > 107.9: pen_circle(f, POS20[2][0], POS20[2][1], 290, 200, (n - 107.9) / 0.4, 10)
    o.pip(f, hf_small(t), x=W - 260, y=H - 260, d=200)
    return f
S(103.45, 108.9, sH, 'info'); X(T(104.25), 'whoosh'); X(T(104.75), 'whoosh'); X(T(105.68), 'thud'); X(T(107.0), 'pop'); X(T(107.54), 'scribble'); X(T(107.9), 'scribble')

# --- I: host, new model gift -> pelican test sticker
GIFT = B(st.sticker(st.emoji('🎁', 260), 260, 14, -8))
STK3 = [(GIFT, 330, 420, 109.86), (PELSTK, 1600, 420, 111.84)]
def sI(t, t0, t1):
    n = N(t); f = host_full(n, 1.06)
    for img, cx, cy, n0 in STK3:
        if n < n0: continue
        u = back_out((n - n0) / 0.3); put(f, cv2.resize(img, None, fx=0.5 + 0.5 * u, fy=0.5 + 0.5 * u), cx, cy, min(1, (n - n0) / 0.08))
    return f
S(108.9, 112.85, sI, 'host'); X(T(109.86), 'pop'); X(T(111.84), 'pop')
