# ======================= SEGMENT 5: narration 136.6 -> 164.15  (exec'd inside v4.py after seg4)
S(136.6, 140.2, host_sc(1.0, 0.04), 'host')
# --- A2: just for fun — pelican on a motorbike, blurred fill + card, laughing sticker
v24 = Vid(CR + '24_25_选用片段.mp4')
LOL = B(st.sticker(st.emoji('😂', 260), 260, 14, 10))
def sA5(t, t0, t1):
    tl = t - t0; n = N(t); fr = v24.get(tl)
    f = cv2.GaussianBlur(o.cover(fr, W, H), (0, 0), 30); f = (f.astype(np.float32) * 0.45 + BG.astype(np.float32) * 0.35).astype(np.uint8)
    u = back_out(tl / 0.35); card = B(st.photo_card(fr, 640, border=10, angle=-4))
    put(f, cv2.resize(card, None, fx=0.7 + 0.3 * u, fy=0.7 + 0.3 * u), W // 2, 520, min(1, tl / 0.1))
    if n > 141.0:
        v = back_out((n - 141.0) / 0.3); put(f, cv2.resize(LOL, None, fx=0.5 + 0.5 * v, fy=0.5 + 0.5 * v), 1430, 330, min(1, (n - 141.0) / 0.08))
    return f
S(140.2, 141.95, sA5, 'info'); X(T(140.2), 'whoosh'); X(T(141.0), 'pop')

# --- B: the inventor says: don't rank every model — podium gets crossed out
TOK_SIMON5 = B(M2.tok_simon(250))
POD = [('Claude', 'orange', 960, 300), ('GPT', 'cyan', 640, 220), ('Gemini', 'blue', 1280, 150)]
POD_TK = [B(o.token(210, c, n_, anchors=False, title_size=50)) for n_, c, _, _ in POD]
DIG = [B(q.text_img(s_, q.F_TITLE, 120, (255, 214, 170, 255))) for s_ in ('1', '2', '3')]
def sB5(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy()
    u = back_out(tl / 0.4); put(f, cv2.resize(TOK_SIMON5, None, fx=0.6 + 0.4 * u, fy=0.6 + 0.4 * u), W // 2, 200, min(1, tl / 0.1))
    if n > 143.39:  # 呼吁: dashed line down
        a = ease((n - 143.39) / 0.3); y1 = int(340 + 120 * a)
        for yy in range(340, y1, 22): cv2.line(f, (W // 2, yy), (W // 2, min(yy + 12, y1)), o.ORANGE[::-1], 4, cv2.LINE_AA)
    fall = max(0, n - 146.5)
    for k, ((n_, c, cx, hgt), tk, dg) in enumerate(zip(POD, POD_TK, DIG)):
        st0 = 143.8 + k * 0.12
        if n < st0: continue
        g = ease((n - st0) / 0.3); h_ = int(hgt * g); x0 = cx - 150
        ov = f.copy(); cv2.rectangle(ov, (x0, 960 - h_), (x0 + 300, 960), (70, 54, 44), -1); f[:] = cv2.addWeighted(ov, 0.75, f, 0.25, 0)
        cv2.rectangle(f, (x0, 960 - h_), (x0 + 300, 960), o.ORANGE[::-1] if k == 0 else (150, 130, 120), 3, cv2.LINE_AA)
        if g > 0.9: put(f, dg, cx, 960 - h_ // 2, 0.9)
        t2 = 144.35 + k * 0.15
        if n > t2:
            v = back_out((n - t2) / 0.3); y = 960 - h_ - 115 + int(1400 * fall * fall) ; ang = fall * 160 * (1 if k % 2 else -1)
            put(f, xform(cv2.resize(tk, None, fx=0.5 + 0.5 * v, fy=0.5 + 0.5 * v), 1.0, ang), cx, y, min(1, (n - t2) / 0.08))
    if n > 146.09: pen_x(f, W // 2, 760, 330, (n - 146.09) / 0.35, 22)
    o.pip(f, hf_small(t), x=60, y=60, d=200); return f
S(141.95, 147.1, sB5, 'info'); X(T(141.95), 'whoosh'); X(T(143.8), 'pop'); X(T(144.35), 'pop'); X(T(144.65), 'pop'); X(T(146.09), 'scribble'); X(T(146.5), 'thud')
S(147.1, 148.25, host_sc(1.05, 0.03), 'host')

# --- D1: one test measures one slice: ability ring around a model, only the pelican slice lights
TK_AI = B(o.token(300, 'blue', 'AI', anchors=False, title_size=110))
PEL_ICON = B(o.token(170, 'orange', portrait=PEL_IMG, anchors=False))
def sD5(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy(); cx, cy = W // 2, 520
    put(f, TK_AI, cx, cy, min(1, tl / 0.15))
    ov = f.copy()
    for k in range(8):
        a0 = -90 + k * 45 + 4; a1 = a0 + 37; g = ease((tl - 0.1 - k * 0.05) / 0.25)
        if g <= 0: continue
        lit = (k == 1 and n > 148.79)
        pulse = n > 149.9 and k != 1 and abs((n - 149.9) * 8 - k) < 1
        col = o.ORANGE[::-1] if lit else ((232, 214, 78) if pulse else (80, 66, 58))
        cv2.ellipse(ov, (cx, cy), (int(400 * g), int(400 * g)), 0, a0, a1, col, 90, cv2.LINE_AA)
    f[:] = cv2.addWeighted(ov, 0.8, f, 0.2, 0)
    if n > 148.79:  # pelican icon inside the lit slice
        a = np.radians(-90 + 45 + 22.5); x, y = int(cx + 400 * np.cos(a)), int(cy + 400 * np.sin(a))
        o.blit(f, PEL_ICON, x - PEL_ICON.shape[1] // 2, y - PEL_ICON.shape[0] // 2, min(1, (n - 148.79) / 0.15))
    o.pip(f, hf_small(t), x=60, y=60, d=200); return f
S(148.25, 150.8, sD5, 'info'); X(T(148.25), 'whoosh'); X(T(148.79), 'pop'); X(T(149.99), 'shine')

# --- D2: gacha — three reels of pelicans spin and stop on random good/bad results
REEL = [cv2.resize(im, (400, 400), interpolation=cv2.INTER_AREA) for im in
        [crude[2], o.grab(CR + '18_20_选用片段.mp4', 1.0)[0:296, 100:500], crude[6], RES[:, 300:1100], crude[9], o.grab(CR + '18_20_选用片段.mp4', 1.0)[362:655, 742:1180], crude[3], EVO_IMG[3]]]
STRIP = np.vstack(REEL)  # 3200 x 400
STOP_T = [154.55, 154.85, 155.15]; STOP_I = [1, 2, 3]
def sE5(t, t0, t1):
    tl = t - t0; n = N(t); f = BGW.copy()
    frame_w, gap = 400, 60; x_start = W // 2 - (3 * frame_w + 2 * gap) // 2; y0 = 300
    cv2.rectangle(f, (x_start - 40, y0 - 40), (x_start + 3 * frame_w + 2 * gap + 40, y0 + 440), (40, 30, 26), -1)
    cv2.rectangle(f, (x_start - 40, y0 - 40), (x_start + 3 * frame_w + 2 * gap + 40, y0 + 440), o.ORANGE[::-1], 4, cv2.LINE_AA)
    for r in range(3):
        if n < STOP_T[r]:
            pos = (tl * (2600 + r * 300)) % 3200; blur = True
        else:
            k = n - STOP_T[r]; pos = STOP_I[r] * 400 - 40 * np.exp(-k * 12) * np.cos(k * 40); blur = False
        p = int(pos) % 3200; win = np.vstack([STRIP, STRIP])[p:p + 400]
        if blur: win = cv2.blur(win, (1, 61))
        f[y0:y0 + 400, x_start + r * (frame_w + gap):x_start + r * (frame_w + gap) + 400] = win
    if n > 155.15:
        for r, good in enumerate((True, False, True)):
            xc = x_start + r * (frame_w + gap) + 200
            if good: ring_sel(f, xc, y0 + 200, 240, (n - 155.2 - r * 0.05) / 0.3, o.CYAN[::-1])
            else: pen_x(f, xc, y0 + 200, 120, (n - 155.25) / 0.25, 16)
    o.pip(f, hf_small(t), x=60, y=H - 260, d=200); return f
S(150.8, 156.15, sE5, 'info'); X(T(150.8), 'whoosh')
for i in range(int((154.55 - 150.9) / 0.12)): X(T(150.9) + i * 0.12, 'type')
for st_ in STOP_T: X(T(st_), 'pop')
X(T(155.25), 'hit')

# --- F1: Opus 5.5's two failures were the output limit — gauge slams into the red end
SHEET5 = cv2.resize(S1.SHEET, None, fx=0.38, fy=0.38)
NUM5 = q.glow(B(q.metal_title('128K', 220, 0.08)), (255, 120, 90), 20, 0.45)
def sF5(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy()
    u = back_out(tl / 0.4); put(f, cv2.resize(S1.TOK_OPUS, None, fx=0.6 + 0.4 * u, fy=0.6 + 0.4 * u), 480, 400, min(1, tl / 0.1))
    for j in range(2):  # two blank answer sheets with red X
        tj = 157.11 + j * 0.25
        if n < tj: continue
        v = ease((n - tj) / 0.3); put(f, xform(SHEET5, 1.0, -6 + 12 * j), int(1150 + j * 400 + 300 * (1 - v)), 400, v)
        pen_x(f, 1150 + j * 400, 400, 90, (n - tj - 0.3) / 0.25, 14)
    if n > 158.85:  # output gauge
        g = ease((n - 158.85) / 0.4); x0, x1, y = 260, 1660, 840
        cv2.rectangle(f, (x0, y - 34), (x1, y + 34), (60, 46, 40), -1); cv2.rectangle(f, (x0, y - 34), (x1, y + 34), (200, 190, 180), 3, cv2.LINE_AA)
        fill = min(1.0, max(0.0, (n - 159.2) / 0.9))
        xe = int(x0 + (x1 - x0) * fill)
        for xx in range(x0 + 4, xe - 4, 6):
            c = (xx - x0) / (x1 - x0); col = (int(42 + 10 * c), int(138 - 100 * c), int(255 - 20 * c))
            cv2.line(f, (xx, y - 28), (xx, y + 28), (col[0], col[1], 232) if c > 0.8 else (42, 138, 255), 4)
        cv2.rectangle(f, (x1 - 8, y - 60), (x1 + 8, y + 60), o.RED[::-1], -1)
        if n > 160.1:
            v = back_out((n - 160.1) / 0.3); put(f, cv2.resize(NUM5, None, fx=0.6 + 0.4 * v, fy=0.6 + 0.4 * v), 1440, 690, min(1, (n - 160.1) / 0.08))
            if n < 160.5: f = cv2.warpAffine(f, np.float32([[1, 0, 10 * np.sin(n * 90)], [0, 1, 0]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    o.pip(f, hf_small(t), x=W - 260, y=60, d=200); return f
S(156.15, 160.65, sF5, 'info'); X(T(156.15), 'whoosh'); X(T(157.11), 'whoosh'); X(T(157.36), 'whoosh'); X(T(157.45), 'scribble'); X(T(157.7), 'scribble'); X(T(159.2), 'shine'); X(T(160.1), 'thud')

# --- F2: every other effort level drew it fine — four Opus 5.5 pelicans, each ringed
T27 = o.imread(CR + '27_模型对比.png')
OK4 = [T27[y0:y1, 405:665] for y0, y1 in ((330, 516), (610, 800), (900, 1090), (1194, 1380))]
OK4C = [B(st.photo_card(im, 380, border=8)) for im in OK4]
def sG5(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy()
    for k, card in enumerate(OK4C):
        tk = 160.75 + k * 0.15
        if n < tk: continue
        v = back_out((n - tk) / 0.3); cx = 330 + k * 420
        put(f, cv2.resize(card, None, fx=0.6 + 0.4 * v, fy=0.6 + 0.4 * v), cx, 500, min(1, (n - tk) / 0.08))
        if n > 162.2 + k * 0.12: ring_sel(f, cx, 500, 215, (n - 162.2 - k * 0.12) / 0.3, o.CYAN[::-1])
    z = 1 + 0.03 * tl / (t1 - t0); f = cv2.warpAffine(f, cv2.getRotationMatrix2D((W / 2, 500), 0, z), (W, H), borderMode=cv2.BORDER_REFLECT)
    o.pip(f, hf_small(t), x=W - 260, y=H - 260, d=200); return f
S(160.65, 164.15, sG5, 'info'); X(T(160.65), 'whoosh')
for k in range(4): X(T(160.75 + k * 0.15), 'pop'); X(T(162.2 + k * 0.12), 'shine') if k == 0 else None
