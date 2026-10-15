# 第五段（第 51–61 镜）：生物医药 → 蛋白质 → 讯飞蛋白质设计 → 指标提升 → 发表 → 品牌句
# 由 full.py exec 进来（在 seg4_vis.py 之后）。
IMG8 = img('8')
if IMG8.shape[2] == 4: IMG8 = IMG8[..., :3]
_a8 = imread(os.path.join(MAT, '8.蛋白质方案.png'))
if _a8.shape[2] == 4:                                   # 透明底垫白
    al = _a8[..., 3:4].astype(np.float32) / 255; IMG8 = (_a8[..., :3] * al + 255 * (1 - al)).astype(np.uint8)

EV.update(cut52=S[52]['start'], cut53=S[53]['start'], cut54=S[54]['start'], cut55=S[55]['start'], cut56=S[56]['start'], cut57=S[57]['start'],
          cut58=S[58]['start'], cut59=S[59]['start'], cut60=S[60]['start'], cut61=S[61]['start'],
          m_acc=wt(59, '功能预测'), m_stab=wt(59, '稳定性'), m_act=wt(59, '活性'), m_up=wt(59, '提升'), pub=wt(60, '发表'), indep=wt(61, '自主可控'))
EV['m3_end'] = EV['cut61']

# ---------------------------------------------------------------- 54 蛋白质结构：代码画的蛋白质，暖色底
BGP = bg_gild(leak=(0.7, 0.3), leak_col=ROSE, k_leak=0.08, key='prot')
def v54(t):
    tl = t - EV['cut54']
    return zoom(KJ.protein(1.0 + tl * 0.9, 6.0, bgimg=BGP, scale=1.05), 1.0 + 0.05 * tl, 0.5, 0.5)

# ---------------------------------------------------------------- 55 大量实验：从一个实验镜头拉远，变成一整面实验墙
_srcs = [(V10, x) for x in (62, 66, 70, 82, 86, 90, 4, 10, 20, 28, 40, 50)] + [(V11, x) for x in (5, 30, 45, 80, 95, 140, 160, 200, 215, 228)] + [(V4b, x) for x in (8, 26, 30, 62, 66)]
PW_, PH_, PG_ = 640, 360, 26; NCG, NRG = 5, 5
GRID_IM = np.zeros((NRG * (PH_ + PG_), NCG * (PW_ + PG_), 3), np.float32)
_rg = np.random.default_rng(55); _order = _rg.permutation(len(_srcs))
for k in range(NCG * NRG):
    r, c = divmod(k, NCG)
    if (r, c) == (2, 2): continue
    v, x = _srcs[_order[k % len(_srcs)]]
    GRID_IM[r * (PH_ + PG_):r * (PH_ + PG_) + PH_, c * (PW_ + PG_):c * (PW_ + PG_) + PW_] = grade(cover(v.get(x), PW_, PH_), 0.75)
def v55(t):
    tl = t - EV['cut55']
    z = lerp(3.0, 0.62, ease(seg(tl, 0.15, 1.9))) * (1 + 0.01 * tl)
    gw, gh = GRID_IM.shape[1], GRID_IM.shape[0]; cx0, cy0 = gw / 2, gh / 2 - PG_ / 2
    M = np.float32([[z, 0, W / 2 - cx0 * z], [0, z, H / 2 - 20 - cy0 * z]])
    f = BG.copy(); g = cv2.warpAffine(GRID_IM, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    cov = cv2.warpAffine(np.ones(GRID_IM.shape[:2], np.float32), M, (W, H), borderValue=0)[..., None]
    f = f * (1 - cov) + g
    live = grade(cover(V10.get(60.0 + tl * 1.2), PW_, PH_), 0.75)       # 中间这格一直在动
    lw, lh = int(PW_ * z), int(PH_ * z)
    if lw > 4: put(f, np.dstack([cv2.resize(live, (lw, lh)), np.full((lh, lw), 255, np.float32)]).astype(np.uint8), W / 2, H / 2 - 20 - PG_ / 2 * z + PG_ / 2 * z, 1.0)
    return f

# ---------------------------------------------------------------- 56–58 讯飞蛋白质设计截图（白底卡）
BG8 = bg_gild(backdrop=cover(IMG8, W, H), dim=0.08, key='p8')
STRUCT = [(615, 72, 770, 168), (615, 172, 770, 265), (615, 268, 770, 352), (842, 222, 1005, 308), (842, 312, 1005, 405)]
EV['structs'] = [EV['cut58'] + 0.2 + 0.36 * k for k in range(5)]
FLOW = [((190, 215), (575, 215))] + [((575, 215), (575, y)) for y in (125, 300)] + [((575, y), (618, y)) for y in (125, 215, 300)]
FL_PTS = np.random.default_rng(57).uniform(0, 1, 46)
def shot8(t, box, s0, dur, ry=-9, flow=False, structs=False, badge=False):
    tl = t - s0; bw, bh = box[2] - box[0], box[3] - box[1]
    s = min(1600 / bw, 800 / bh, 2.6) * (0.94 + 0.06 * ease_out(min(1, tl / 0.8)))
    cd = card(IMG8, int(IMG8.shape[1] * s), radius=22)
    cxb, cyb = (box[0] + box[2]) / 2 * s, (box[1] + box[3]) / 2 * s
    f = BG8.copy()
    M = persp(f, cd, W / 2 + (cd.shape[1] / 2 - cxb), H / 2 - 30 + (cd.shape[0] / 2 - cyb), 1.0, ry=ry + 4 * ease(tl / dur), rx=5, shadow_k=0.6)
    dim_except(f, M, tuple(v * s for v in box), 0.6)
    lay = np.zeros((H, W, 3), np.float32)
    if flow:                                            # 光点沿红色主线流过去，再分到三个可设计结构
        segs = [(np.array(a, np.float32) * s, np.array(b, np.float32) * s) for a, b in FLOW]
        on = ease_out(seg(tl, 0.3, 0.8))
        for k, u0 in enumerate(FL_PTS):
            u = (u0 + tl * 0.45) % 1.0
            if u < 0.62: a, b = segs[0]; p = a + (b - a) * (u / 0.62)
            else:
                br = k % 3; v = (u - 0.62) / 0.38
                if br == 1: a, b = segs[4]; p = a + (b - a) * v
                else:
                    a1, b1 = segs[1 + (0 if br == 0 else 1)]; a2, b2 = segs[3 + (0 if br == 0 else 2)]
                    p = a1 + (b1 - a1) * min(1, v * 2) if v < 0.5 else a2 + (b2 - a2) * (v - 0.5) * 2
            q = cv2.perspectiveTransform(p.reshape(1, 1, 2), M)[0, 0]
            cv2.circle(lay, (int(q[0]), int(q[1])), 10, (np.array(GOLD) * on).tolist(), -1, cv2.LINE_AA)
    if structs:                                         # 结构依次亮起：没亮之前压暗
        m = np.zeros((H, W), np.float32)
        for b, t0 in zip(STRUCT, EV['structs']):
            k = ease_out(seg(t, t0, t0 + 0.25))
            q = cv2.perspectiveTransform(np.array([[[b[0] * s, b[1] * s], [b[2] * s, b[1] * s], [b[2] * s, b[3] * s], [b[0] * s, b[3] * s]]], np.float32), M)[0].astype(np.int32)
            cv2.fillConvexPoly(m, q, 1.0 - k, cv2.LINE_AA)
            if k > 0: cv2.polylines(lay, [q], True, (np.array(GOLD) * k).tolist(), 6, cv2.LINE_AA)
        f *= 1 - 0.5 * m[..., None]
    f[:] = f * (1 - np.clip(lay.max(2, keepdims=True) / 255, 0, 1) * 0.9) + lay + cv2.GaussianBlur(lay, (0, 0), 6) * 0.6
    if badge:
        k = seg(t, s0 + 0.45, s0 + 0.8)
        put(f, P_XF, lerp(-200, 300, ease_out(k)), H - 330, k, scale=0.72)
    return f
def v56(t):
    s = S[56]; u = ease(seg(t, s['start'], s['end']))
    box = [lerp(a, b, u) for a, b in zip((0, 0, 1010, 713), (20, 10, 1005, 420))]
    return shot8(t, box, s['start'], s['dur'], badge=True)
def v57(t):
    s = S[57]; u = ease(seg(t, s['start'], s['end']))
    box = [lerp(a, b, u) for a, b in zip((20, 10, 1005, 420), (40, 30, 790, 370))]
    return shot8(t, box, s['start'], s['dur'], flow=True)
def v58(t):
    s = S[58]; u = ease(seg(t, s['start'], s['start'] + 0.6))
    box = [lerp(a, b, u) for a, b in zip((40, 30, 790, 370), (580, 50, 1008, 410))]
    return shot8(t, box, s['start'], s['dur'], structs=True, ry=-6)

# ---------------------------------------------------------------- 59 指标提升：三枚徽章 + 往上长的金箭头（不编具体数字）
MET = [('准确率', EMERALD, 'check', 'm_acc'), ('稳定性', SAPPHIRE, 'stack', 'm_stab'), ('活性', CORAL, 'gem', 'm_act')]
MET_IM = [make_card(330, 330, 'circle', 0, c, 0.66, n, ic, title_size=58, rim=0.6, rim_col=tuple(min(255, int(v * 0.45 + 150)) for v in c)) for n, c, ic, e in MET]
MET_X = [W / 2 - 480, W / 2, W / 2 + 480]
def v59(t):
    tl = t - EV['cut59']
    base = KJ.protein(3.0 + tl * 0.6, 6.0, bgimg=BGP, scale=1.15) * 0.42 + BGP * 0.58
    f = cv2.GaussianBlur(base, (0, 0), 3)
    lay = np.zeros((H, W, 3), np.float32)
    for (n, c, ic, e), im, x in zip(MET, MET_IM, MET_X):
        t0 = EV[e] - 0.05; k = seg(t, t0, t0 + 0.3)
        if k <= 0: continue
        put(f, im, x, H / 2 + 90, ease_out(k), scale=0.8 + 0.2 * back_out(k))
        g = ease_out(seg(t, t0 + 0.2, t0 + 0.8)) * (1 + 0.25 * ease_out(seg(t, EV['m_up'], EV['m_up'] + 0.5)))
        y0 = H / 2 - 110; y1 = y0 - 190 * g
        cv2.line(lay, (int(x), int(y0)), (int(x), int(y1)), GOLD, 10, cv2.LINE_AA)
        cv2.fillConvexPoly(lay, np.array([[x - 34, y1 + 10], [x + 34, y1 + 10], [x, y1 - 40]], np.int32), GOLD, cv2.LINE_AA)
    pulse = max(0.0, 1 - abs(t - EV['m_up'] - 0.2) / 0.3)
    a_ = np.clip(lay.max(2, keepdims=True) / 255, 0, 1); f = f * (1 - a_) + lay + cv2.GaussianBlur(lay, (0, 0), 12) * (0.5 + 0.8 * pulse)
    return f

# ---------------------------------------------------------------- 60 发表：一页论文落下，金光扫过（不冒充具体期刊）
SEAL = make_card(200, 200, 'circle', 0, (176, 128, 44), 0.85, None, 'check', rim=0.9, rim_col=GOLD)
PAPER_BIG = paper_img(520, 680, seed=3); PAPER_G = paper_img(520, 680, seed=3, tint=(250, 214, 130))
def v60(t):
    tl = t - EV['cut60']; f = bg_gild(key='pub', leak=(0.5, 0.2), leak_col=GOLD, k_leak=0.09).copy()
    for j in range(4):                                  # 背后一叠
        put(f, PW[j], W / 2 - 40 + j * 26, H / 2 + 10 - j * 8, 0.55 * ease_out(seg(tl, 0, 0.3)), scale=1.6, angle=-6 + j * 3)
    u = seg(t, EV['pub'] - 0.45, EV['pub'])
    y = lerp(-500, H / 2 - 30, ease_in(u, 2)) if u < 1 else H / 2 - 30
    put(f, PAPER_BIG, W / 2, y, 1.0 if u > 0 else 0, angle=lerp(-12, 2, u))
    g = ease(seg(t, EV['pub'] + 0.15, EV['pub'] + 0.6))
    if g > 0: put(f, PAPER_G, W / 2, H / 2 - 30, g, angle=2)
    ks = seg(t, EV['pub'] + 0.25, EV['pub'] + 0.45)
    if ks > 0: put(f, SEAL, W / 2 + 210, H / 2 + 230, ks, scale=1.5 - 0.5 * ease_out(ks, 3), angle=-12)
    if t >= EV['pub']:
        q = t - EV['pub']
        if q < 0.6:
            lay = np.zeros((H, W, 3), np.float32); sx = lerp(W / 2 - 400, W / 2 + 400, q / 0.6)
            cv2.line(lay, (int(sx), 0), (int(sx - 200), H), (255, 230, 170), 50); f += cv2.GaussianBlur(lay, (0, 0), 30) * 0.8
        f = shake(f, max(0.0, 1 - q / 0.3) * 0.6, int(t * 30))
    return zoom(f, 1.0 + 0.03 * tl, 0.5, 0.5)

# ---------------------------------------------------------------- 61 品牌句：真人，「自主可控」处跳一次景别
def v61(t): return host(1.0 if t < EV['indep'] - 0.1 else 1.13)(t)

VIS.update({51: shotfn(51, foot(V10, 1.0, 14.7, speed=2.0)), 52: shotfn(52, foot(V10, 15.0, 31.9, speed=2.5)),
            53: shotfn(53, foot(V10, 33.0, 59.7, speed=3.0)), 54: v54, 55: v55, 56: v56, 57: v57, 58: v58, 59: v59, 60: v60, 61: v61})
CUTS += ['cut54', 'cut55', 'cut56', 'cut59', 'cut52', 'cut53', 'cut60']
QUIET |= {'cut52', 'cut53', 'cut60'}
SFX_MORE += [('蛋白质推开', EV['cut55'] + 0.2, 'swish', 0.3), ('讯飞徽章', S[56]['start'] + 0.6, 'thud', 0.2)] + \
            [(f'结构{k + 1}', t0, 'thud', 0.10) for k, t0 in enumerate(EV['structs'])] + \
            [('准确率', EV['m_acc'], 'thud', 0.16), ('稳定性', EV['m_stab'], 'thud', 0.16), ('活性', EV['m_act'], 'thud', 0.16), ('提升', EV['m_up'] + 0.15, 'gate', 0.3),
             ('论文落下', EV['pub'], 'thud', 0.35), ('盖章', EV['pub'] + 0.4, 'gate', 0.35),
             ('换曲·上扬', EV['cut61'], 'rrise', 0.35)]
STILLS = [('51', S[51]['start'] + 1.0), ('52', S[52]['start'] + 1.0), ('53', S[53]['start'] + 1.0), ('54 蛋白质', S[54]['start'] + 1.0),
          ('55 起', S[55]['start'] + 0.3), ('55 墙', S[55]['start'] + 2.2), ('56', S[56]['start'] + 1.3), ('57 流', S[57]['start'] + 2.0),
          ('58 结构', S[58]['start'] + 2.4), ('59 指标', EV['m_up'] + 0.3), ('60 发表', EV['pub'] + 0.8), ('61 品牌', EV['indep'] + 0.5)]
