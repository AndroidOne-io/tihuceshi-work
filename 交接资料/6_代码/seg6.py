# ======================= SEGMENT 6: narration 164.15 -> end (+ outro)  (exec'd inside v4.py after seg5)
S(164.15, 165.1, host_sc(1.04, 0.03), 'host')
# --- B: public question bank — the exam paper is copied everywhere, a sneaky vendor "optimizes" it
PAPER6 = cv2.resize(S1.PAPER, None, fx=0.62, fy=0.62)
SPY = B(st.sticker(st.emoji('🕵️', 300), 300, 14, -6))
def sB6(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy()
    if n > 166.12:  # copies fly out
        for k, (dx, dy, a) in enumerate([(-560, -60, -10), (560, -40, 9), (-420, 260, 6), (430, 280, -7)]):
            u = ease((n - 166.12 - k * 0.08) / 0.45)
            if u > 0: put(f, xform(PAPER6, 0.7, a * u), int(W // 2 + dx * u), int(520 + dy * u), 0.75 * u)
    u = back_out(tl / 0.4); put(f, xform(PAPER6, 0.8 + 0.2 * u, -3), W // 2, 520, min(1, tl / 0.1))
    if n > 168.64:
        v = ease((n - 168.64) / 0.4); put(f, SPY, int(W + 200 - 560 * v), 640, v)
    if n > 169.6:  # targeted "optimization": marker sweeps across the answer area
        k = min(1, (n - 169.6) / 0.6); ov = f.copy()
        cv2.rectangle(ov, (W // 2 - 230, 430), (int(W // 2 - 230 + 460 * k), 700), (40, 160, 255), -1); f[:] = cv2.addWeighted(ov, 0.35, f, 0.65, 0)
    o.pip(f, hf_small(t), x=60, y=60, d=200); return f
S(165.1, 170.9, sB6, 'info'); X(T(165.1), 'whoosh'); X(T(166.12), 'whoosh'); X(T(168.64), 'whoosh'); X(T(169.6), 'scribble')

# --- C: memorizing the answers to score well: grainy footage on a tilted card -> score counter shoots to 99.9
v28 = Vid(CR + '28_29_选用片段.mp4')
def sC6(t, t0, t1):
    tl = t - t0; n = N(t); f = BGW.copy()
    if n < 173.36:
        fr = v28.get(tl); u = ease(tl / 0.35)
        card = persp(cv2.resize(fr, (1280, 720)), 1280, 10 * (1 - u) + 4)
        put(f, card, W // 2 + int(300 * (1 - u)), 520, u)
    else:
        k = n - 173.36; val = 60 + 39.9 * ease(k / 1.0)
        num = q.glow(B(q.metal_title(f'{val:.1f}', 300, 0.08)), (255, 170, 90), 22, 0.45)
        put(f, num, W // 2, 500)
        if n > 175.88: f = q.glitch(f, 0.6 * max(0, 1 - (n - 175.88) / 0.4), int(k * 40))
    o.pip(f, hf_small(t), x=W - 260, y=60, d=200); return f
S(170.9, 176.93, sC6, 'info'); X(T(170.9), 'whoosh'); X(T(173.36), 'whoosh'); X(T(174.36), 'pop'); X(T(175.88), 'pop')
# --- pause 176.93: brush 背题
HALF6 = q.halftone_bg(cv2.resize(o.grab(CR + '28_29_选用片段.mp4', 5.5), (1920, 1080)), (230, 50, 50))
BR6 = B(q.brush_title('背题', 420))
e0, e1 = PT(176.93)
def sBrush6(t, t0, t1):
    tl = t - t0; f = HALF6.copy(); s = 1.2 - 0.2 * ease(tl / 0.18) + 0.04 * tl
    put(f, cv2.resize(BR6, None, fx=s, fy=s), W // 2, 540, min(1, tl / 0.06))
    return q.glitch(f, max(0, 1 - tl / 0.25) * 0.9, int(tl * 30) + 9)
S(e0, e1, sBrush6, 'title', out=True)

# --- D: progress is so fast the exam goes stale: year flips, paper yellows and falls away
def sepia(img, a):
    b = img.copy(); rgb = b[..., :3].astype(np.float32); g = rgb.mean(2, keepdims=True)
    sp = np.concatenate([g * 0.55, g * 0.8, g * 1.0], 2)
    b[..., :3] = np.clip(rgb * (1 - a) + sp * a, 0, 255).astype(np.uint8); return b
YEARS = [q.glow(B(q.metal_title(y, 200, 0.08)), (255, 170, 90), 18, 0.4) for y in ('2024', '2025', '2026')]
def sD6(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy()
    yi = 0 if n < 178.3 else (1 if n < 179.0 else 2)
    put(f, YEARS[yi], W // 2, 180, min(1, tl / 0.15))
    age = ease((n - 178.3) / 2.0); fall = max(0, n - 180.64)
    p = sepia(PAPER6, age); p = xform(p, 1.0, -3 + 25 * fall * 2)
    put(f, p, W // 2 + int(200 * fall), 600 + int(1600 * fall * fall), min(1, tl / 0.1) * max(0, 1 - fall * 1.2))
    o.pip(f, hf_small(t), x=60, y=H - 260, d=200); return f
S(176.93 + 1e-6, 181.8, sD6, 'info'); X(T(178.3), 'pop'); X(T(179.0), 'pop'); X(T(180.64), 'whoosh')

# --- E: one image -> animation -> 3D: three cards, the active one big
v31 = Vid(CR + '29_31_选用片段.mp4'); v32 = Vid(CR + '29_32_选用片段.mp4')
STILL = cv2.copyMakeBorder(cv2.resize(crude[5], (340, 340)), 10, 10, 150, 150, cv2.BORDER_CONSTANT, value=(255, 255, 255))
def sE6(t, t0, t1):
    tl = t - t0; n = N(t); f = BG.copy()
    act = 0 if n < 184.62 else (1 if n < 187.56 else 2)
    imgs = [STILL, v31.get(max(0, n - 184.62) % 2.3), v32.get(max(0, n - 187.56) % 2.8)]
    starts = [181.9, 184.62, 187.56]
    order = [k for k in range(3) if k != act] + [act]
    for k in order:
        if n < starts[k]: continue
        u = back_out((n - starts[k]) / 0.35)
        w = 680 if k == act else 440
        card = B(st.photo_card(cv2.resize(imgs[k], (640, 360)), w, border=8, angle=(-3, 2, -2)[k]))
        cx = [int(960 - 600 * ease((n - 184.62) / 0.4)), 960, 1560][k]; a = 1.0 if k == act else 0.45
        put(f, cv2.resize(card, None, fx=0.7 + 0.3 * u, fy=0.7 + 0.3 * u), cx, 520, a * min(1, (n - starts[k]) / 0.1))
    o.pip(f, hf_small(t), x=W - 260, y=H - 260, d=200); return f
S(181.8, 189.5, sE6, 'info')
for s_ in (181.9, 184.62, 187.56): X(T(s_), 'whoosh')

# --- F: host — just the beginning of brain-melting tests
BRAIN = B(st.sticker(st.emoji('🧠', 260), 260, 14, -8)); BULB = B(st.sticker(st.emoji('💡', 240), 240, 14, 8))
def stk_host(items):
    def fn(t, t0, t1):
        n = N(t); f = host_full(n, 1.05 + 0.03 * (t - t0) / max(t1 - t0, 0.1))
        for img, cx, cy, n0 in items:
            if n < n0: continue
            u = back_out((n - n0) / 0.3); put(f, cv2.resize(img, None, fx=0.5 + 0.5 * u, fy=0.5 + 0.5 * u), cx, cy, min(1, (n - n0) / 0.08))
        return f
    return fn
S(189.5, 194.3, stk_host([(BRAIN, 330, 400, 192.42), (BULB, 1600, 380, 193.74)]), 'host'); X(T(192.42), 'pop'); X(T(193.74), 'pop')

# --- G: new cast of absurd tests — character medallions with nicknames, then the combined artwork
TK_MONK = B(q.char_token(380, M2.CUT_MONK, ('大', '圣'), 'orange')); TK_QIN = B(q.char_token(380, M2.CUT_QIN, ('始', '皇'), 'violet'))
TK_PEL6 = B(q.char_token(340, M2.CUT_PEL2, ('鹈', '鹕'), 'cyan'))
def sG6(t, t0, t1):
    tl = t - t0; n = N(t); f = BGW.copy()
    for img, cx, cy, n0 in ((TK_MONK, 960 - 520, 470, 194.46), (TK_QIN, 960 + 520, 470, 195.54), (TK_PEL6, 960, 500, 196.8)):
        if n < n0: continue
        u = back_out((n - n0) / 0.35); put(f, cv2.resize(img, None, fx=0.5 + 0.5 * u, fy=0.5 + 0.5 * u), cx, cy, min(1, (n - n0) / 0.08))
    o.pip(f, hf_small(t), x=60, y=H - 260, d=200); return f
S(194.3, 197.9, sG6, 'info'); X(T(194.3), 'whoosh'); X(T(194.46), 'pop'); X(T(195.54), 'pop'); X(T(196.8), 'shine')
v34 = Vid(CR + '30_34_选用片段.mp4')
CALM = B(st.sticker(st.emoji('😌', 260), 260, 14, 8))
def sH6(t, t0, t1):
    tl = t - t0; n = N(t); fr = v34.get(min(tl, 3.5))[130:610, 110:900]
    f = cv2.GaussianBlur(o.cover(fr, W, H), (0, 0), 28); f = (f.astype(np.float32) * 0.5 + BG.astype(np.float32) * 0.3).astype(np.uint8)
    u = ease(tl / 0.35); z = 1 + 0.05 * tl / (t1 - t0)
    card = B(st.photo_card(fr, int(1300 * z), border=10, angle=-2))
    put(f, card, W // 2, 520, u)
    if n > 201.64:
        v = back_out((n - 201.64) / 0.3); put(f, cv2.resize(CALM, None, fx=0.5 + 0.5 * v, fy=0.5 + 0.5 * v), 1640, 820, min(1, (n - 201.64) / 0.08))
    return f
S(197.9, 202.6, sH6, 'info'); X(T(197.9), 'whoosh'); X(T(201.64), 'pop')

# --- I: host call-to-action, comment sticker
CHAT = B(st.sticker(st.emoji('💬', 260), 260, 14, -8)); PELS = B(st.sticker(Image.fromarray(cv2.cvtColor(M2.CUT_PEL, cv2.COLOR_BGRA2RGBA)), 300, 14, 8))
S(202.6, NARR_DUR, stk_host([(PELS, 1600, 380, 204.21), (CHAT, 330, 420, 205.77)]), 'host'); X(T(204.21), 'pop'); X(T(205.77), 'pop')

# --- outro (1.6s after the last word): the 严父 mascot medallion on the tunnel
OUT0 = T(NARR_DUR); OUT1 = OUT0 + 1.6
def sOut(t, t0, t1):
    tl = t - t0; f = q.tunnel(t)
    u = back_out(tl / 0.4); put(f, cv2.resize(S1.MASCOT, None, fx=0.6 + 0.4 * u, fy=0.6 + 0.4 * u), W // 2, 540, min(1, tl / 0.1))
    f = (f.astype(np.float32) * (1 - ease((tl - 1.1) / 0.5))).astype(np.uint8)
    return f
S(OUT0, OUT1, sOut, 'title', out=True); X(OUT0, 'whoosh'); X(OUT0 + 0.15, 'boom')
TOTAL = OUT1
