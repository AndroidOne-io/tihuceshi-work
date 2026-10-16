# 第六段（第 62–71 镜）：回到开头 → 不只是多懂知识 → 参与科研流程 → 1024 → 真实场景 → 五个场景 → 结尾
# 由 full.py exec 进来（在 seg5_vis.py 之后）。
EV.update(cut62=S[62]['start'], cut63=S[63]['start'], cut64=S[64]['start'], cut65=S[65]['start'], cut66=S[66]['start'], cut67=S[67]['start'],
          cut68=S[68]['start'], cut69=S[69]['start'], cut70=S[70]['start'], cut71=S[71]['start'],
          r_oai=wt(62, 'OpenAI'), r_chem=wt(62, '化工研发'), r_prot=wt(62, '蛋白质设计'), more=wt(63, '多懂'),
          s1=wt(64, '提出方案'), s2=wt(64, '调用工具'), s3=wt(64, '模拟计算'), s4=wt(64, '辅助验证'),
          but=wt(65, '但它正在'), real=wt(67, '真实场景'), sc=[wt(68, w) for w in ('科研', '教育', '医疗', '工业', '生活')],
          land=wt(69, '着落'), ordinary=wt(71, '每个普通人'))

# ---------------------------------------------------------------- 62 真人：身旁依次叠上三张回顾卡
REV = [(img('1')[330:1150, 150:2874], 'r_oai', 1480, 300, -4), (REC_TBL, 'r_chem', 1520, 520, 3), (IMG8[30:380, 40:790], 'r_prot', 1480, 745, -2)]
REV_C = [card(cover(im, 540, 304).astype(np.uint8), 540, radius=18, border=3, bcol=(225, 228, 236)) for im, *_ in REV]
def v62(t):
    f = host(1.0)(t)
    for cd, (im, e, x, y, ang) in zip(REV_C, REV):
        k = seg(t, EV[e] - 0.1, EV[e] + 0.25)
        if k > 0: persp(f, cd, x + 60 * (1 - ease_out(k)), y, 0.9 + 0.1 * ease_out(k), ry=-14, rz=ang, a=min(1, k * 1.5), shadow_k=0.5)
    return f

# ---------------------------------------------------------------- 63–64 AI 徽章：书本飞进来 → 变灰；然后四步围成一个循环
B_AI = make_card(300, 300, 'circle', 0, VIOLET, 0.7, 'AI', None, title_size=120, rim=0.7, rim_col=(210, 190, 255))
B_AI_G = make_card(300, 300, 'circle', 0, (110, 110, 118), 0.55, 'AI', None, title_size=120, rim=0.35)
BOOKS = [make_card(180, 180, 'rect', 28, c, 0.65, None, 'book', rim=0.5) for c in (SAPPHIRE, TEAL, EMERALD, CORAL, ROSE, SAPPHIRE, TEAL, EMERALD)]
BOOK_P = [(math.cos(a) * 760, math.sin(a) * 400) for a in np.linspace(0, 2 * np.pi, 9)[:-1] + 0.3]
LOOP = [('提出方案', 'bulb', SAPPHIRE, 's1', 0, -1), ('调用工具', 'wrench', TEAL, 's2', 1, 0), ('模拟计算', 'chart', CORAL, 's3', 0, 1), ('辅助验证', 'check', EMERALD, 's4', -1, 0)]
LOOP_IM = [make_card(250, 250, 'circle', 0, c, 0.68, n, ic, title_size=44, rim=0.6, rim_col=tuple(min(255, int(v * 0.45 + 150)) for v in c)) for n, ic, c, e, dx, dy in LOOP]
LC = (W / 2 + 60, H / 2 - 40); LRX, LRY = 400, 280
BG63 = bg_gild(leak=(0.55, 0.25), leak_col=VIOLET, k_leak=0.07, key='p63')
def v6364(t):
    f = BG63.copy(); cx, cy = LC
    gray = ease(seg(t, last_voice(63) - 0.7, last_voice(63) - 0.2)) * (1 - ease(seg(t, EV['cut64'], EV['cut64'] + 0.4)))
    if t < EV['cut64']:
        for j, (bk, (bx, by)) in enumerate(zip(BOOKS, BOOK_P)):
            t0 = EV['more'] - 0.2 + 0.07 * j; u = seg(t, t0, t0 + 0.55)
            if u <= 0 or u >= 1: continue
            put(f, bk, cx + bx * (1 - ease_in(u, 2)), cy + by * (1 - ease_in(u, 2)), min(1, u * 4) * (1 - ease_in(u, 4)), scale=1.0 - 0.5 * u)
        k_in = ease_out(seg(t, EV['cut63'], EV['cut63'] + 0.35))
        pulse = max(0.0, 1 - abs(t - EV['more'] - 0.5) / 0.3)
        put(f, B_AI, cx, cy, k_in * (1 - gray), scale=(0.85 + 0.15 * back_out(k_in)) * (1 + 0.08 * pulse))
        put(f, B_AI_G, cx, cy, k_in * gray, scale=0.92)
    else:
        lay = np.zeros((H, W, 3), np.float32)
        pos = [(cx + dx * LRX, cy + dy * LRY) for n, ic, c, e, dx, dy in LOOP]
        ts = [EV[e] - 0.05 for n, ic, c, e, dx, dy in LOOP]
        for k in range(4):                                            # 弧线：亮了下一个才画到下一个
            a0 = -math.pi / 2 + k * math.pi / 2 + 0.38; a1 = a0 + math.pi / 2 - 0.76
            u = ease(seg(t, ts[(k + 1) % 4] - 0.25, ts[(k + 1) % 4] + 0.1)) if k < 3 else ease(seg(t, ts[3] + 0.4, ts[3] + 0.9))
            if u <= 0: continue
            aa = np.linspace(a0, a0 + (a1 - a0) * u, 40)
            pts = np.c_[cx + LRX * np.cos(aa), cy + LRY * np.sin(aa)].astype(np.int32)
            cv2.polylines(lay, [pts], False, GOLD, 4, cv2.LINE_AA)
            if u >= 1:
                tip = pts[-1]; d = pts[-1] - pts[-4]; d = d / (np.linalg.norm(d) + 1e-6); nrm = np.array([-d[1], d[0]])
                tri = np.array([tip + d * 16, tip - d * 14 + nrm * 13, tip - d * 14 - nrm * 13], np.int32); cv2.fillConvexPoly(lay, tri, GOLD, cv2.LINE_AA)
        if t > ts[3] + 0.9:                                           # 循环转起来：金色光点绕圈
            for j in range(3):
                a = -math.pi / 2 + (t - ts[3]) * 2.2 + j * 2 * math.pi / 3
                cv2.circle(lay, (int(cx + LRX * math.cos(a)), int(cy + LRY * math.sin(a))), 9, (255, 236, 190), -1, cv2.LINE_AA)
        f += lay + cv2.GaussianBlur(lay, (0, 0), 6) * 0.9
        put(f, B_AI, cx, cy, 1.0, scale=0.72 * (1 + 0.04 * math.sin(t * 3)))
        for im, (x, y), t0 in zip(LOOP_IM, pos, ts):
            k = seg(t, t0, t0 + 0.3)
            put(f, im, x, y, 0.35 + 0.65 * ease_out(k), scale=0.85 + 0.15 * back_out(k) if k > 0 else 0.85)
    out = seg(t, last_voice(64) - 0.35, last_voice(64) - 0.05)
    return pip2(f, t, u=ease_out(seg(t, EV['cut63'], EV['cut63'] + 0.4)), out=out)

# ---------------------------------------------------------------- 65 / 71 真人
def v65(t): return host(1.0 if t < EV['but'] - 0.1 else 1.12)(t)
def v71(t): return host(1.06 if t < EV['ordinary'] - 0.1 else 1.0)(t)

# ---------------------------------------------------------------- 66 / 70 活动页（横幅已补成 16:9）
IMG9 = img('9'); BG9 = bg_gild(backdrop=cover(IMG9, W, H), dim=0.12, key='p9')
F66 = shot(IMG9, (40, 200, 1612, 730), (560, 250, 1080, 590), rx=4, ry=(-10, -6), maxk=2.6, bgimg=BG9, rng_=(S[66]['start'], S[66]['end']))
def v70(t):
    s = S[70]; e = s['start'] + 0.4 + 5.2
    fn = shot(IMG9, (220, 350, 560, 530), (1090, 360, 1430, 520), rx=4, ry=(-8, -4), maxk=2.4, bgimg=BG9, rng_=(s['start'] + 0.3, e))
    return fn(min(max(t, s['start'] + 0.3), e))

# ---------------------------------------------------------------- 67 真实场景：空镜 → 金属大字单独出现
T_REAL = to_rgba_np(metal('真实场景', 230, 0.10))
BG67 = bg_gild(leak=(0.5, 0.3), leak_col=GOLD, k_leak=0.10, key='p67')
F67 = foot(V4b, 60.0, 64.0, speed=0.9, dim=0.95, sat=0.6)
def v67(t):
    hit = EV['real']
    if t < hit - 0.05: return F67(t, S[67]['start'], hit - S[67]['start'])
    q = t - hit; f = BG67.copy()
    u = seg(q, 0, 0.3)
    put(f, sweep(T_REAL, seg(q, 0.4, 1.4)), W / 2, H / 2 - 20, ease_out(u, 2), scale=(1.25 - 0.25 * ease_out(u, 4)) * (1 + 0.012 * q))
    f += max(0.0, 1 - q / 0.25) * 120
    return shake(f, max(0.0, 1 - q / 0.35), int(t * 30))

# ---------------------------------------------------------------- 68 五个场景：随口播依次点亮，金线把它们串起来，最后落到「生活」
SCN = [('科研', 'flask', SAPPHIRE), ('教育', 'book', TEAL), ('医疗', 'medical', ROSE), ('工业', 'factory', CORAL), ('生活', 'home', (176, 128, 44))]
SCN_IM = [make_card(250, 250, 'circle', 0, c, 0.68, n, ic, title_size=52, rim=0.6 if k < 4 else 0.95, rim_col=tuple(min(255, int(v * 0.45 + 150)) for v in c) if k < 4 else GOLD)
          for k, (n, ic, c) in enumerate(SCN)]
SCN_P = [(W / 2 + (k - 2) * 350, H / 2 - 40 + 60 * ((k - 2) / 2) ** 2 - 30) for k in range(5)]
def v68(t):
    f = BG67.copy(); lay = np.zeros((H, W, 3), np.float32)
    for k in range(4):
        t0, t1 = EV['sc'][k], EV['sc'][k + 1]; u = ease(seg(t, t0 + 0.1, t1))
        if u <= 0: continue
        p0, p1 = np.array(SCN_P[k]), np.array(SCN_P[k + 1]); a = p0 + (p1 - p0) * 0.36; b = p0 + (p1 - p0) * (0.36 + 0.28 * u)
        cv2.line(lay, tuple(a.astype(int)), tuple(b.astype(int)), GOLD, 4, cv2.LINE_AA)
    f += lay + cv2.GaussianBlur(lay, (0, 0), 6)
    for k, (im, (x, y)) in enumerate(zip(SCN_IM, SCN_P)):
        t0 = EV['sc'][k] - 0.05; u = seg(t, t0, t0 + 0.3)
        if u > 0: put(f, im, x, y, ease_out(u), scale=(0.8 + 0.2 * back_out(u)) * (1.08 if k == 4 and u >= 1 else 1.0))
    return zoom(f, 1.0 + 0.03 * (t - S[68]['start']), 0.5, 0.5)

# ---------------------------------------------------------------- 69 使用它的人：人物空镜，暖色慢推；「着落」处一粒金光落下
F69 = foot(V4b, 70.5, 74.0, speed=0.8, push=0.08, sat=0.65)
def v69(t):
    f = F69(t, S[69]['start'], S[69]['dur'])
    u = seg(t, EV['land'] - 0.8, EV['land'])
    if 0 < u:
        lay = np.zeros((H, W, 3), np.float32); y = lerp(120, H / 2 + 40, ease_out(u, 2)); x = W / 2 + 120
        r = 8 if u < 1 else int(8 + 120 * ease_out(min(1, (t - EV['land']) / 0.6)))
        col = np.array(GOLD) * (1.0 if u < 1 else max(0, 1 - (t - EV['land']) / 0.6))
        cv2.circle(lay, (int(x), int(y)), r, col.tolist(), -1 if u < 1 else 3, cv2.LINE_AA)
        f += lay + cv2.GaussianBlur(lay, (0, 0), 14) * 1.2
    return f

VIS.update({62: v62, 63: v6364, 64: v6364, 65: v65, 66: F66, 67: v67, 68: v68, 69: v69, 70: v70, 71: v71})
CUTS += ['cut63', 'cut65', 'cut66', 'cut67', 'cut68', 'cut69', 'cut70', 'cut71']
QUIET |= {'cut65', 'cut67', 'cut69', 'cut71'}
SFX_MORE += [(f'回顾卡{k + 1}', EV[e], 'thud', 0.13) for k, e in enumerate(('r_oai', 'r_chem', 'r_prot'))] + \
            [('书飞进', EV['more'] - 0.1, 'swish', 0.3)] + [(f'循环·{n}', EV[e], 'thud', 0.15) for n, ic, c, e, dx, dy in LOOP] + \
            [('循环接上', EV['s4'] + 0.9, 'gate', 0.25), ('真实场景', EV['real'], 'dong', 0.7)] + \
            [(f'场景·{n}', t0, 'thud', 0.12) for (n, ic, c), t0 in zip(SCN, EV['sc'])] + [('着落', EV['land'], 'thud', 0.18)]
STILLS = [('62 回顾', EV['r_prot'] + 0.6), ('63 书', EV['more'] + 0.3), ('63 变灰', last_voice(63) - 0.1), ('64 循环', EV['s3'] + 0.3),
          ('64 转圈', S[64]['end'] - 0.4), ('65', EV['but'] + 1.0), ('66 1024', S[66]['start'] + 3.0), ('67 空镜', EV['real'] - 1.0),
          ('67 真实场景', EV['real'] + 1.0), ('68 场景', EV['sc'][4] + 0.4), ('69 着落', EV['land'] + 0.2), ('70 左', S[70]['start'] + 1.0),
          ('70 右', S[70]['start'] + 6.5), ('71', EV['ordinary'] + 0.5), ('71 结束', TOTAL + PRE - 0.5 - PRE + 0.0)]
