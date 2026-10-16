# 第四段（第 37–50 镜）：讯飞化工大模型 3.0 Pro → 演示 → 400+ → 真人收束 → 「02 生物医药」章节卡
# 由 full.py exec 进来，共用 EV / S / VIS / CUTS / QUIET / SFX_MORE / 工具函数。
V6 = Vid(os.path.join(MAT, '6.演示录屏.mp4')); V7 = Vid(os.path.join(MAT, '7.400种.mp4')); V10 = Vid(os.path.join(MAT, '10.生物.mp4'))
IMG5 = img('5')

EV.update(
    link=wt(37, '合作'), cut38=S[38]['start'], cut39=S[39]['start'], cut40=S[40]['start'], req=wt(40, '流程设计'),
    cut41=S[41]['start'], cut46=S[46]['start'], cut47=S[47]['start'], n400=wt(47, '400'), cut48=S[48]['start'], cut49=S[49]['start'],
    digi=wt(49, '数字化'), early=wt(50, '更早发现'), labv=wt(50, '实验与工程'), ch2_in=last_voice(50), cut51=S[51]['start'],
)

def homog(w, h, cx, cy, scale=1.0, ry=0.0, rx=0.0, f=2200.0):
    pts = np.array([[-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], [w / 2, h / 2, 0], [-w / 2, h / 2, 0]], np.float32) * scale
    ay, ax = math.radians(ry), math.radians(rx)
    Ry = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
    p = pts @ (Ry @ Rx).T; z = p[:, 2] + f
    proj = np.stack([cx + p[:, 0] * f / z, cy + p[:, 1] * f / z], 1).astype(np.float32)
    return cv2.getPerspectiveTransform(np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32), proj)

def map_box(M, b):
    q = cv2.perspectiveTransform(np.array([[[b[0], b[1]], [b[2], b[1]], [b[2], b[3]], [b[0], b[3]]]], np.float32), M)[0]
    return q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max()

# ---------------------------------------------------------------- 37 合作：两枚徽章从两侧滑入，在「合作」处扣上
P_XF = make_card(440, 440, 'circle', 0, SAPPHIRE, 0.66, '科大讯飞', 'bulb', title_size=68, rim=0.6, rim_col=(190, 210, 255))
P_DL = make_card(440, 440, 'circle', 0, TEAL, 0.66, '中科院大连化物所', 'flask', title_size=44, rim=0.6, rim_col=(170, 235, 230))
BG37 = bg_gild(leak=(0.5, 0.25), leak_col=GOLD, k_leak=0.09, key='p37')
SP37 = np.random.default_rng(37).normal(0, 1, (70, 2))
def v37(t):
    f = BG37.copy(); s = S[37]['start']; tl = t - s
    u = ease_out(seg(tl, 0.0, 0.7)); lk = ease(seg(t, EV['link'] - 0.35, EV['link']))
    gap = lerp(1560, 760, u) - 60 * lk
    xl, xr = W / 2 - gap / 2, W / 2 + gap / 2; cy = H / 2 - 40
    if t >= EV['link'] - 0.3:                               # 金色连线 + 扣上时的光点
        lay = np.zeros((H, W, 3), np.float32); k = seg(t, EV['link'] - 0.3, EV['link'])
        xa, xb = xl + 225, xr - 225; xm = (xa + xb) / 2
        cv2.line(lay, (int(xm - (xm - xa) * k), int(cy)), (int(xm + (xb - xm) * k), int(cy)), GOLD, 5, cv2.LINE_AA)
        if t >= EV['link']:
            q = t - EV['link']
            cv2.circle(lay, (int(xm), int(cy)), int(20 + 260 * ease_out(min(1, q / 0.6))), (np.array(GOLD) * max(0, 1 - q / 0.6)).tolist(), 3, cv2.LINE_AA)
            for (a, b) in SP37:
                p = (int(xm + a * 180 * ease_out(min(1, q / 0.8))), int(cy + b * 120 * ease_out(min(1, q / 0.8))))
                cv2.circle(lay, p, 3, (np.array(GOLD) * max(0, 1 - q / 1.2)).tolist(), -1, cv2.LINE_AA)
        f += lay + cv2.GaussianBlur(lay, (0, 0), 5) + cv2.GaussianBlur(lay, (0, 0), 18) * 0.6
    put(f, P_XF, xl, cy, u, scale=0.9 + 0.1 * u)
    put(f, P_DL, xr, cy, u, scale=0.9 + 0.1 * u)
    return zoom(f, 1.0 + 0.03 * tl / S[37]['dur'], 0.5, 0.5)

# ---------------------------------------------------------------- 38–39 模型简介：整页 → 推到标题 → 四个模块依次亮起
BG5 = bg_gild(backdrop=cover(IMG5, W, H), dim=0.10, key='p5')
MODS = [(163, 210, 346, 298), (354, 210, 537, 298), (545, 210, 728, 298), (736, 210, 919, 298)]
EV['mods'] = [S[39]['start'] + 0.25 + 0.22 * k for k in range(4)]
def shot5(t, box, s0, dur, hl=None, mods=False, ry=-10):
    tl = t - s0; bw, bh = box[2] - box[0], box[3] - box[1]
    s = min(1560 / bw, 800 / bh, 2.3) * (0.94 + 0.06 * ease_out(min(1, tl / 0.8)))
    cd = card(IMG5, int(IMG5.shape[1] * s), radius=22)
    cxb, cyb = (box[0] + box[2]) / 2 * s, (box[1] + box[3]) / 2 * s
    f = BG5.copy()
    M = persp(f, cd, W / 2 + (cd.shape[1] / 2 - cxb), H / 2 - 30 + (cd.shape[0] / 2 - cyb), 1.0, ry=ry + 4 * ease(tl / dur), rx=5, shadow_k=0.6)
    dim_except(f, M, tuple(v * s for v in box), 0.6)
    if hl:
        x0, y0, x1, y1 = map_box(M, [v * s for v in hl]); hl_bar(f, x0, y0, x1, y1, seg(tl, 0.35, 0.9), GOLD, 0.40)
    if mods:                                                # 模块没亮之前压暗，亮起时恢复原亮度 + 金边
        lay = np.zeros((H, W, 3), np.float32); m = np.zeros((H, W), np.float32)
        for b, t0 in zip(MODS, EV['mods']):
            k = ease_out(seg(t, t0, t0 + 0.25))
            q = cv2.perspectiveTransform(np.array([[[b[0] * s, b[1] * s], [b[2] * s, b[1] * s], [b[2] * s, b[3] * s], [b[0] * s, b[3] * s]]], np.float32), M)[0].astype(np.int32)
            cv2.fillConvexPoly(m, q, 1.0 - k, cv2.LINE_AA)
            if k > 0: cv2.polylines(lay, [q], True, (np.array(GOLD) * k).tolist(), 6, cv2.LINE_AA)
        f *= 1 - 0.55 * m[..., None]
        f[:] = f * (1 - np.clip(lay.max(2, keepdims=True) / 255, 0, 1)) + lay
    return f
def v38(t):
    s = S[38]; u = ease(seg(t, s['start'] + 0.15, s['start'] + 1.3))
    box = [lerp(a, b, u) for a, b in zip((40, 60, 1040, 540), (375, 140, 705, 200))]
    return shot5(t, box, s['start'], s['dur'], hl=(445, 155, 700, 192) if u >= 1 else None)
def v39(t): return shot5(t, (150, 160, 935, 305), S[39]['start'], S[39]['dur'], mods=True, ry=-6)

# ---------------------------------------------------------------- 40–45 演示：录屏卡片 + 顶部五步流程徽章
BG6 = bg_gild(backdrop=cover(V6.get(1.5), W, H), dim=0.08, key='p6')
STEPS = [('拆解任务', 41, '拆解任务'), ('判断参数', 42, '判断出'), ('调用工具', 43, '调用'), ('分析核对', 44, '分析核对'), ('给出方案', 45, '给出')]
ST_T = [wt(i, w) - 0.08 for n, i, w in STEPS]
ST_OFF = [make_card(300, 100, 'rect', 22, INK, 0.55, n, title_size=46, rim=0.3) for n, i, w in STEPS]
ST_ON = [make_card(300, 100, 'rect', 22, (150, 112, 40), 0.72, n, title_size=46, rim=0.95, rim_col=GOLD) for n, i, w in STEPS]
ST_DONE = [make_card(300, 100, 'rect', 22, TEAL, 0.5, n, title_size=46, rim=0.4, rim_col=(170, 235, 230)) for n, i, w in STEPS]
ST_X = [W / 2 + (k - 2) * 352 for k in range(5)]; ST_Y = 128
REC = {40: (0.9, 2.3, (720, 540, 2380, 990), (745, 585, 2350, 800), (750, 598, 1100, 636)),
       41: (28.0, 34.0, (720, 570, 2380, 1040), None, None),
       42: (16.0, 22.0, (740, 70, 2240, 990), None, None),
       43: (36.0, 96.0, (720, 570, 2380, 1040), None, None),
       44: (100.0, 134.0, (720, 30, 2380, 520), None, (740, 240, 1700, 360)),
       45: (136.0, 145.5, (500, 20, 2634, 1080), None, (530, 795, 1160, 900))}
def steps_row(f, t):
    a = ease_out(seg(t, EV['cut41'] - 0.1, EV['cut41'] + 0.3)); dy = -160 * (1 - a)
    lay = np.zeros((H, W, 3), np.float32)
    for k in range(4):
        x0 = int(ST_X[k] + 150 + 6); x1 = int(ST_X[k + 1] - 150 - 6)
        cv2.line(lay, (x0, int(ST_Y + dy)), (x1, int(ST_Y + dy)), (np.array(GOLD if t >= ST_T[k + 1] else (120, 122, 132)) * a).tolist(), 3, cv2.LINE_AA)
    f += lay
    for k in range(5):
        on = t >= ST_T[k]; done = k + 1 < 5 and t >= ST_T[k + 1]
        im = ST_DONE[k] if done else ST_ON[k] if on else ST_OFF[k]
        pop = back_out(seg(t, ST_T[k], ST_T[k] + 0.3)) if on and not done else 1.0
        put(f, im, ST_X[k], ST_Y + dy, a * (1.0 if on else 0.6), scale=0.86 + 0.14 * pop if on and not done else 1.0)
    return f
def v_demo(t):
    s = next(x for x in shots if x['start'] <= t < x['end']); i = s['i']; tl = t - s['start']
    a, b, box, focus, hl = REC[i]; fr = V6.get(a + (b - a) * min(1.0, tl / s['dur']))
    sub = fr[box[1]:box[3], box[0]:box[2]]
    top = 220 if i >= 41 else 60
    sc = min(1760 / sub.shape[1], (H - top - 150) / sub.shape[0])
    cd = card(sub, int(sub.shape[1] * sc), radius=22)
    f = BG6.copy()
    M = persp(f, cd, W / 2, top + (H - top - 150) / 2 + 10, 0.96 + 0.05 * ease(tl / s['dur']), ry=-8 + 4 * ease(tl / s['dur']), rx=4, shadow_k=0.6)
    if focus: dim_except(f, M, [(focus[0] - box[0]) * sc, (focus[1] - box[1]) * sc, (focus[2] - box[0]) * sc, (focus[3] - box[1]) * sc], 0.5)
    if hl:
        t0 = EV['req'] if i == 40 else s['start'] + 0.35
        x0, y0, x1, y1 = map_box(M, [(hl[0] - box[0]) * sc, (hl[1] - box[1]) * sc, (hl[2] - box[0]) * sc, (hl[3] - box[1]) * sc])
        hl_bar(f, x0, y0, x1, y1, seg(t, t0, t0 + 0.5), GOLD, 0.38)
    if i >= 41: steps_row(f, t)
    return f

# ---------------------------------------------------------------- 46 技能商店 / 48 工具库
BG7 = bg_gild(backdrop=cover(V7.get(3.5), W, H), dim=0.08, key='p7')
def rec7(a, b, box, hl=None):
    def fn(t):
        s = next(x for x in shots if x['start'] <= t < x['end']); tl = t - s['start']
        sub = V7.get(a + (b - a) * min(1.0, tl / s['dur']))[box[1]:box[3], box[0]:box[2]]
        sc = min(1700 / sub.shape[1], 880 / sub.shape[0]); cd = card(sub, int(sub.shape[1] * sc), radius=22)
        f = BG7.copy(); M = persp(f, cd, W / 2, H / 2 - 20, 0.97 + 0.06 * ease(tl / s['dur']), ry=-12 + 5 * ease(tl / s['dur']), rx=6, shadow_k=0.6)
        if hl:
            x0, y0, x1, y1 = map_box(M, [(hl[0] - box[0]) * sc, (hl[1] - box[1]) * sc, (hl[2] - box[0]) * sc, (hl[3] - box[1]) * sc])
            hl_bar(f, x0, y0, x1, y1, seg(tl, 0.3, 0.9), GOLD, 0.35)
        return f
    return fn

# ---------------------------------------------------------------- 47 400+：工具墙一路拉远、一块块亮起 → 「400」砸下来
TILE_SRC = []
for tt in (14.0, 18.0):
    fr = V7.get(tt)
    for (x0, x1) in ((530, 1186), (1212, 1870), (1900, 2556)):
        for (y0, y1) in ((552, 790), (824, 1064)):
            TILE_SRC.append(fr[y0:y1, x0:x1].copy())
    TILE_SRC.append(fr[1098:1336, 530:1186].copy())
TW, TH, GX, GY, NC, NR = 320, 116, 340, 136, 22, 19
_rt = np.random.default_rng(400)
WALL_DIM = np.zeros((NR * GY, NC * GX, 3), np.float32); WALL_LIT = WALL_DIM.copy()
for r in range(NR):
    for c in range(NC):
        tile = cv2.resize(TILE_SRC[_rt.integers(len(TILE_SRC))], (TW, TH), interpolation=cv2.INTER_AREA).astype(np.float32)
        x, y = c * GX + 10, r * GY + 10
        WALL_DIM[y:y + TH, x:x + TW] = tile * 0.30 + np.array((20, 22, 28)) * 0.1
        lit = tile * 0.92; lit[:4] = GOLD; lit[-4:] = GOLD; lit[:, :4] = GOLD; lit[:, -4:] = GOLD
        WALL_LIT[y:y + TH, x:x + TW] = lit
_cc = np.array([[(c - NC / 2 + 0.5) ** 2 + 2.2 * (r - NR / 2 + 0.5) ** 2 for c in range(NC)] for r in range(NR)])
LIT_ORDER = np.argsort(np.argsort((_cc + _rt.uniform(0, 30, _cc.shape)).ravel())).reshape(NR, NC)   # 从中间往外亮
N400 = shadow(glow_rgba(text('400+', F_NUM, 400, GOLD, 0.02), GOLD, 34, 0.6), 18, (0, 10), 210)
BG47 = bg_gild(leak=(0.5, 0.5), leak_col=GOLD, k_leak=0.07, key='p47', bokeh=False)
def v47(t):
    s0 = EV['cut46']; hit = EV['n400']
    z = lerp(1.25, 0.26, ease(seg(t, s0, hit))) * (1 - 0.03 * max(0, t - hit))
    M = homog(NC * GX, NR * GY, W / 2, H / 2 + 30, z, ry=-6, rx=22)
    f = BG47.copy()
    dimw = cv2.warpPerspective(WALL_DIM, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    litw = cv2.warpPerspective(WALL_LIT, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    n_lit = NC * NR * ease_in(seg(t, s0 + 0.2, hit), 1.6)
    m_small = (LIT_ORDER < n_lit).astype(np.float32)
    SC8 = np.array([[GX / 8, 0, 0], [0, GY / 8, 0], [0, 0, 1]])
    m = cv2.warpPerspective(cv2.resize(m_small, (NC * 8, NR * 8), interpolation=cv2.INTER_NEAREST), M @ SC8, (W, H), flags=cv2.INTER_NEAREST, borderValue=0)[..., None]
    covm = cv2.warpPerspective(np.ones((NR * 8, NC * 8), np.float32), M @ SC8, (W, H), borderValue=0)[..., None]
    wall = dimw * (1 - m) + litw * m
    f = f * (1 - covm) + wall
    if t >= hit:
        q = t - hit
        f = f * (1 - 0.62 * ease_out(min(1, q / 0.25))) ; f = cv2.GaussianBlur(f, (0, 0), 1 + 5 * ease_out(min(1, q / 0.3)))
        lay = np.zeros((H, W, 3), np.float32)
        cv2.circle(lay, (W // 2, H // 2), int(80 + 1200 * ease_out(min(1, q / 0.7))), (np.array(GOLD) * max(0, 1 - q / 0.7)).tolist(), 5, cv2.LINE_AA)
        f += lay + cv2.GaussianBlur(lay, (0, 0), 10)
        u = seg(q, 0, 0.22)
        put(f, N400, W / 2, H / 2 - 20, ease_out(u, 2), scale=(1.45 - 0.45 * ease_out(u, 4)) * (1 + 0.015 * q))
        f += max(0.0, 1 - q / 0.18) * 120
        f = shake(f, max(0.0, 1 - q / 0.4), int(t * 30))
    return f

# ---------------------------------------------------------------- 49–50 真人：身旁依次换三张画面卡（数字工厂 → 方案表 → 实验）
def side_card(f, frame_rgb, cx, cy, a, w=640):
    if a <= 0: return f
    cd = card(cover(frame_rgb, w, int(w * 9 / 16)).astype(np.uint8), w, radius=20, border=3, bcol=(225, 228, 236))
    persp(f, cd, cx + 60 * (1 - ease_out(a)), cy, 0.92 + 0.08 * ease_out(a), ry=-14, rx=3, a=min(1, a * 1.5), shadow_k=0.55)
    return f
REC_TBL = V6.get(141.0)[20:740, 500:1840]
def v4950(t):
    f = host(1.0)(t)
    k1 = seg(t, EV['digi'] - 0.1, EV['digi'] + 0.25); k2 = seg(t, EV['early'] - 0.1, EV['early'] + 0.25); k3 = seg(t, EV['labv'] - 0.1, EV['labv'] + 0.25)
    if k1 > 0 and k2 < 1:
        side_card(f, np.clip(KJ.digital_factory(1.0 + (t - EV['digi']) * 0.8, 6.0, bgimg=BG_Z), 0, 255), 1490, 420, k1 * (1 - k2))
    if k2 > 0 and k3 < 1:
        side_card(f, REC_TBL, 1490, 420, k2 * (1 - k3))
    if k3 > 0:
        side_card(f, grade(V11.get(225.0 + (t - EV['labv']) * 0.8), 0.8), 1490, 420, k3)
    return f
CH2 = make_card(1040, 420, 'rect', 36, INK, 0.6, '生物医药', None, big=text('02', F_NUM, 170, GOLD), title_size=138, rim=0.45)
def v50(t):
    if t < EV['ch2_in']: return v4950(t)
    k = t - EV['ch2_in']
    f = grade(cover(V10.get(1.0 + k * 0.8), W, H), 0.6, dim=0.45)
    out = ease_in(seg(t, EV['cut51'] - 0.25, EV['cut51']), 2)
    put(f, CH2, W / 2, H / 2 - 20, ease_out(seg(k, 0, 0.3)) * (1 - out), scale=(0.85 + 0.15 * back_out(seg(k, 0, 0.4))) * (1 + 0.6 * out))
    return f

VIS.update({37: v37, 38: v38, 39: v39, 40: v_demo, 41: v_demo, 42: v_demo, 43: v_demo, 44: v_demo, 45: v_demo,
            46: v47, 47: v47, 48: rec7(10.0, 13.0, (510, 30, 2620, 1080), hl=(520, 205, 1640, 275)),
            49: v4950, 50: v50})
CUTS += ['cut38', 'cut40', 'cut46', 'cut48', 'cut51']; EV['cut47'] = EV['cut46']   # 46–47 是同一个工具墙镜头
SFX_MORE += [('徽章滑入', S[37]['start'] + 0.2, 'swish', 0.3), ('合作·扣上', EV['link'], 'thud', 0.3),
             ('标题高亮', S[38]['start'] + 1.35, 'thud', 0.14)] + [(f'模块{k + 1}', t0, 'thud', 0.10) for k, t0 in enumerate(EV['mods'])] + \
            [('流程条落下', EV['cut41'], 'swish', 0.28)] + [(f'步骤·{n}', t0 + 0.05, 'thud', 0.15) for (n, i, w), t0 in zip(STEPS, ST_T)] + \
            [('工具墙·蓄力', EV['n400'], 'rise', 0.55), ('400+', EV['n400'], 'dong', 1.0),
             ('数字工厂卡', EV['digi'], 'thud', 0.14), ('方案表卡', EV['early'], 'thud', 0.14), ('实验卡', EV['labv'], 'thud', 0.14),
             ('章节卡·生物', EV['ch2_in'], 'gate', 0.45), ('章节卡收', EV['cut51'], 'whoosh', 0.4)]
STILLS = [('37 合作', EV['link'] + 0.3), ('38 标题', S[38]['start'] + 1.8), ('39 模块', S[39]['start'] + 1.5), ('40 需求', S[40]['start'] + 2.5),
          ('41 拆解', S[41]['start'] + 1.0), ('42 参数', S[42]['start'] + 1.0), ('43 工具', S[43]['start'] + 1.2), ('45 方案', S[45]['start'] + 1.5),
          ('46 墙近', S[46]['start'] + 0.4), ('47 墙远', EV['n400'] - 0.3), ('47 400+', EV['n400'] + 0.6), ('48 工具库', S[48]['start'] + 1.5),
          ('49 数字工厂', EV['digi'] + 1.0), ('50 方案表', EV['early'] + 1.0), ('50 实验', EV['labv'] + 1.0), ('02 生物医药', EV['ch2_in'] + 0.6)]
