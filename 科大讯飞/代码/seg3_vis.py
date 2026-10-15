# 第三段（第 19–36 镜）：国内科研 → 化工研发 → 死亡之谷。由 full.py exec 进来，共用 EV / S / 工具函数。
V11 = Vid(os.path.join(MAT, '11.化学.mp4')); V4b = Vid(os.path.join(MAT, '4.空镜.mp4'))
def grade(v, sat=0.75, warm=(1.04, 1.0, 0.93), dim=1.0):
    v = v.astype(np.float32); g = v.mean(2, keepdims=True); v = (v * sat + g * (1 - sat)) * np.array(warm)
    return np.clip((v - 128) * 1.06 + 128, 0, 255) * dim
def foot(vid, a, b, speed=1.4, push=0.06, dim=1.0, sat=0.75):
    def fn(t, t0, dur):
        u = t - t0; st = min(a + u * speed, b - 0.05)
        return zoom(grade(cover(vid.get(st), W, H), sat, dim=dim), 1.0 + push * u / max(dur, 0.1), 0.5, 0.5)
    return fn
def shotfn(i, *clips):
    """一个镜头里平均切几段素材"""
    def fn(t):
        s = S[i]; n = len(clips); k = min(int((t - s['start']) / s['dur'] * n), n - 1); d = s['dur'] / n
        return clips[k](t, s['start'] + k * d, d)
    return fn

# ---- 22 研究院所 / 高校 / 科技企业：徽章依次弹出
ENT = [('研究院所', 'flask', SAPPHIRE, '科研院所', 640), ('高校', 'book', TEAL, '高校', 960), ('科技企业', 'gear', CORAL, '科技企业', 1280)]
ENT_IMG = [make_card(300, 300, 'circle', 0, c, 0.68, n, ic, title_size=50, rim=0.6, rim_col=tuple(min(255, int(v * 0.45 + 150)) for v in c)) for n, ic, c, w, x in ENT]
F22 = foot(V4b, 12.7, 15.9, dim=0.55)
def v22(t):
    f = F22(t, S[22]['start'], S[22]['dur'])
    for im, (n, ic, c, w, x) in zip(ENT_IMG, ENT):
        t0 = wt(22, w) - 0.05; k = seg(t, t0, t0 + 0.3)
        if k > 0: put(f, im, x, H / 2 - 30, k, scale=0.7 + 0.3 * back_out(k))
    return f

# ---- 25 问句 → 停顿落在章节卡上
CH = make_card(1040, 420, 'rect', 36, INK, 0.6, '化工研发', None, big=text('01', F_NUM, 170, GOLD), title_size=138, rim=0.45)
def v25(t):
    if t < EV['ch_in']: return host(1.06)(t)
    k = t - EV['ch_in']
    f = grade(cover(V11.get(3.0 + k * 0.8), W, H), 0.6, dim=0.45)
    out = ease_in(seg(t, EV['cut26'] - 0.25, EV['cut26']), 2)
    put(f, CH, W / 2, H / 2 - 20, ease_out(seg(k, 0, 0.3)) * (1 - out), scale=(0.85 + 0.15 * back_out(seg(k, 0, 0.4))) * (1 + 0.6 * out))
    return f

# ---- 28–29 实验室 → 工厂：左右两块画面，金色粒子从实验室流向工厂
LAB_TAG = make_card(220, 86, 'rect', 18, INK, 0.6, '实验室', title_size=44); FAC_TAG = make_card(200, 86, 'rect', 18, INK, 0.6, '工厂', title_size=44, rim_col=GOLD, rim=0.7)
PFLOW = np.random.default_rng(4).uniform(0, 1, (40, 2))
def panel(img, w, h):
    return card(img, w, radius=22, border=0)
def v2829(t):
    f = BG.copy(); s28 = S[28]['start']; s29 = S[29]['start']
    split = ease(seg(t, s29 - 0.15, s29 + 0.45))
    lab = grade(cover(V11.get(222.9 + (t - s28) * 1.2), 1600, 900))
    wl = int(lerp(1680, 780, split)); hl = int(wl * 9 / 16)
    persp(f, panel(cover(lab, wl, hl), wl, hl), lerp(W / 2, W * 0.25, split), H / 2 - 20, 1.0, ry=lerp(0, 8, split), shadow_k=0.5)
    if split > 0:
        fac = KJ.digital_factory(2.0 + (t - s29), 6.0, bgimg=BG_Z)
        fw = 780; fh = int(fw * 9 / 16)
        persp(f, panel(cv2.resize(fac, (fw, fh)).astype(np.uint8), fw, fh), lerp(W + 500, W * 0.75, split), H / 2 - 20, 1.0, ry=-8, a=split, shadow_k=0.5)
        lay = np.zeros((H, W, 3), np.float32)
        x0, x1 = W * 0.25 + 395, W * 0.75 - 395
        cv2.arrowedLine(lay, (int(x0), H // 2 - 20), (int(lerp(x0, x1, split)), H // 2 - 20), (np.array(GOLD) * 0.8).tolist(), 4, cv2.LINE_AA, tipLength=0.25)
        for (a, r) in PFLOW:
            u = (t * 0.6 + a) % 1.0; p = (int(lerp(x0, x1, u)), int(H / 2 - 20 + (r - 0.5) * 60))
            cv2.circle(lay, p, 4, (np.array(GOLD) * split).tolist(), -1, cv2.LINE_AA)
        f += lay + cv2.GaussianBlur(lay, (0, 0), 6)
        put(f, FAC_TAG, W * 0.75, H / 2 + 240, ease_out(seg(t, s29 + 0.3, s29 + 0.6)))
    put(f, LAB_TAG, W * 0.25, H / 2 + 240, ease_out(seg(t, s29 + 0.2, s29 + 0.5)))   # 标签只在分屏后出现，避开字幕
    return f

# ---- 32 调参数：实验镜头 + 右侧一组半透明滑杆
F32 = foot(V11, 84.0, 102.4, dim=0.8)
def v32(t):
    f = F32(t, S[32]['start'], S[32]['dur']); tl = t - S[32]['start']
    px, py, pw, ph = 1220, 200, 560, 600
    ov = np.zeros((H, W, 3), np.float32); al = np.zeros((H, W), np.float32)
    cv2.rectangle(al, (px, py), (px + pw, py + ph), 0.55, -1); f[:] = f * (1 - al[..., None]) + np.array(INK, np.float32) * al[..., None]
    lay = np.zeros((H, W, 3), np.float32); cv2.rectangle(lay, (px, py), (px + pw, py + ph), (120, 120, 130), 2, cv2.LINE_AA)
    a_in = ease_out(seg(tl, 0, 0.3))
    for k, col in enumerate((GOLD, ICE, CORAL, MINT)):
        y = py + 105 + k * 130; cv2.line(lay, (px + 50, y), (px + pw - 50, y), (90, 92, 100), 9, cv2.LINE_AA)
        v = 0.5 + 0.35 * math.sin(tl * (2.2 + k * 0.7) + k * 1.3)
        x = int(px + 50 + (pw - 100) * v); cv2.line(lay, (px + 50, y), (x, y), col, 9, cv2.LINE_AA); cv2.circle(lay, (x, y), 19, (245, 245, 250), -1, cv2.LINE_AA)
    f += (lay + cv2.GaussianBlur(lay, (0, 0), 4) * 0.4) * a_in
    return f

# ---- 33–34 每多试一次：次数往上跳，三根资源条往下掉
RES = [('时间', 'clock', GOLD), ('材料', 'flask', ICE), ('设备', 'gear', CORAL)]
RES_IC = [make_card(150, 150, 'circle', 0, c, 0.6, None, ic if ic != 'clock' else 'chart', rim=0.55) for n, ic, c in RES]
RES_T = [shadow(text(n, F_BLACK, 52, WHITE), 6, (0, 2), 150) for n, ic, c in RES]
TRY = shadow(text('第', F_BLACK, 70, WHITE), 6, (0, 2), 150); TRY2 = shadow(text('次', F_BLACK, 70, WHITE), 6, (0, 2), 150)
F3334 = foot(V11, 149.0, 162.3, dim=0.4)
def v3334(t):
    s33 = S[33]['start']; f = F3334(t, s33, S[33]['dur'] + S[34]['dur'])
    tl = t - s33; n = 1 + int(max(0, tl) / 0.55); n = min(n, 9)
    put(f, TRY, 420, 330, 1.0); put(f, number(str(n), '', 230, GOLD), 560, 320, 1.0, scale=1.0 + 0.12 * max(0, 1 - ((tl % 0.55) / 0.12))); put(f, TRY2, 700, 330, 1.0)
    lay = np.zeros((H, W, 3), np.float32)
    for k, ((nm, ic, c), im, tx) in enumerate(zip(RES, RES_IC, RES_T)):
        y = 560 + k * 150; t0 = S[34]['start'] - 0.1 + k * 0.25
        a = ease_out(seg(t, t0, t0 + 0.3))
        put(f, im, 330, y, a, scale=0.8); put(f, tx, 470, y, a)
        lvl = max(0.08, 1 - 0.1 * (n - 1) - 0.05 * k)
        cv2.rectangle(lay, (570, y - 20), (1500, y + 20), (60, 62, 70), -1, cv2.LINE_AA)
        cv2.rectangle(lay, (570, y - 20), (int(570 + 930 * lvl), y + 20), (np.array(c) * a).tolist(), -1, cv2.LINE_AA)
    f += lay * 1.0
    return f

# ---- 36 死亡之谷：曲线一头栽进谷底 → 毛笔大字
B_LAB = make_card(170, 170, 'circle', 0, SAPPHIRE, 0.65, None, 'flask', rim=0.6)
B_FAC = make_card(170, 170, 'circle', 0, (110, 112, 125), 0.55, None, 'factory', rim=0.4)
T_VALLEY = brush('死亡之谷', 300)
_HB = [None]
def v36(t):
    if _HB[0] is None: _HB[0] = bg_gild(backdrop=V11.get(230.0), dim=0.30, key='valley', leak_col=CORAL, k_leak=0.08)
    f = _HB[0].copy(); s = S[36]['start']
    xs = np.linspace(260, 1660, 600); u = (xs - 260) / 1400
    ys = 360 + 40 * u + 470 * np.exp(-((u - 0.52) / 0.11) ** 2) - 160 * np.clip((u - 0.7) / 0.3, 0, 1)
    draw = ease(seg(t, s + 0.2, EV['fall'] + 0.35)); n = max(2, int(len(xs) * draw))
    lay = np.zeros((H, W, 3), np.float32); pts = np.c_[xs[:n], ys[:n]].astype(np.int32)
    for i in range(1, n):
        dip = max(0.0, (ys[i] - 420) / 400); col = np.array(ICE) * (1 - dip) + np.array(CORAL) * dip
        cv2.line(lay, tuple(pts[i - 1]), tuple(pts[i]), col.tolist(), 6, cv2.LINE_AA)
    cv2.circle(lay, tuple(pts[-1]), 12, (255, 245, 230), -1, cv2.LINE_AA)
    if t > EV['fall']:
        k = seg(t, EV['fall'], EV['fall'] + 0.4); cv2.circle(lay, (int(xs[int(600 * 0.52)]), int(ys.max())), int(30 + 70 * k), (np.array(CORAL) * (1 - 0.5 * k)).tolist(), 3, cv2.LINE_AA)
    f += lay + cv2.GaussianBlur(lay, (0, 0), 4) * 0.8 + cv2.GaussianBlur(lay, (0, 0), 16) * 0.5
    put(f, B_LAB, 240, 350, ease_out(seg(t, s, s + 0.3)))
    put(f, B_FAC, 1690, ys[-1] - 10, ease_out(seg(t, s + 2.0, s + 2.3)) * 0.7)
    if EV['fall'] < t < EV['fall'] + 0.45: f = shake(f, 1 - seg(t, EV['fall'], EV['fall'] + 0.45), int(t * 30))
    hit = EV['valley']
    if t >= hit:
        f = f * (1 - 0.65 * ease(seg(t, hit - 0.15, hit + 0.1)))
        u2 = seg(t, hit, hit + 0.25)
        put(f, T_VALLEY, W / 2, H / 2, ease_out(u2, 2), scale=(1.3 - 0.3 * ease_out(u2, 4)) * (1 + 0.012 * (t - hit)))
        g = max(0.0, 1 - (t - hit) / 0.35); f = glitch(f, g, int(t * 30)); f = shake(f, g, int(t * 31))
    return f

VIS.update({
    19: shotfn(19, foot(V4b, 27.5, 30.7)), 20: shotfn(20, foot(V4b, 35.7, 39.5)), 21: shotfn(21, foot(V4b, 59.1, 63.0)),
    22: v22, 23: shotfn(23, foot(V4b, 0.0, 5.0, speed=1.0, push=0.1)), 24: shotfn(24, foot(V4b, 18.7, 23.3)),
    25: v25, 26: shotfn(26, foot(V11, 2.0, 25.6, speed=2.0)), 27: shotfn(27, foot(V11, 77.7, 83.5)),
    28: v2829, 29: v2829, 30: shotfn(30, foot(V11, 133.3, 148.2, speed=2.0)),
    31: shotfn(31, foot(V11, 38.0, 50.5, speed=2.0), foot(V11, 26.0, 37.7, speed=2.0)),
    32: v32, 33: v3334, 34: v3334, 35: host(1.0), 36: v36,
})
CUTS += ['cut22', 'cut26', 'cut28', 'cut30', 'cut32', 'cut33', 'cut35', 'cut36']
