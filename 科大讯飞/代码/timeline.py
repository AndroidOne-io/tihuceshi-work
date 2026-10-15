# 第一版剪辑：按真实口播卡点，出镜位用占位画面
import sys, os, re, json, math
import numpy as np, cv2
from kx import *
from shots import SH
import infographics as IG
import kongjing as KJ

ALIGN = sys.argv[1] if len(sys.argv) > 1 else 'align.json'
VO_WAV = os.path.join(MAT, '口播', '非出镜美化.wav')
SUB_FIX = {'科研院所': '研究院所', '蛋白质设计项目': '蛋白质实验项目'}   # 按实际念的出字幕
ROW_GAP, LEAD, TAIL = 0.30, 0.10, 0.32

def nchars(s): return [m.group(0) for m in re.finditer(r'[一-鿿]|[A-Za-z]+|\d+(?:\.\d+)?', s)]

# ---------------------------------------------------------------- 1. 时间线：有录音的行按真实时间，没录音的按语速估
takes = json.load(open(ALIGN))
rate = sum(len(t['chars']) for t in takes) / sum(t['chars'][-1][3] - t['chars'][0][3] + 0.3 for t in takes)   # 字/秒
VO_ROWS = sorted({r for r, *_ in SH if r in (3, 9, 11, 13, 14, 15, 17)} | {18})
row_takes = {}
for tk in takes:
    for r in VO_ROWS:
        rowtxt = ''.join(s[1] for s in SH if s[0] == r)
        if ''.join(nchars(tk['use'])) in ''.join(nchars(rowtxt)) and len(nchars(tk['use'])) > 0:
            row_takes.setdefault(r, []).append(tk); break

shots, audio_pieces = [], []   # shots: dict(i,row,text,start,end,chars=[(char,t_out)])
t = 0.0
rows = sorted({s[0] for s in SH})
for r in rows:
    rs = [(i, s) for i, s in enumerate(SH, 1) if s[0] == r]
    has_vo = r in row_takes
    # 本行可用的录音字流（只对画外音镜头）
    stream = []
    if has_vo:
        for tk in row_takes[r]:
            a0 = tk['chars'][0][3] - LEAD; a1 = tk['chars'][-1][3] + TAIL
            out0 = t
            audio_pieces.append((a0, a1, out0))
            for c, _, _, ct in tk['chars']: stream.append((c, out0 + (ct - a0)))
            t = out0 + (a1 - a0) + 0.08
        row_end = t
        t_row0 = audio_pieces[-len(row_takes[r])][2]
    k = 0; tt = t_row0 if has_vo else t
    for j, (i, s) in enumerate(rs):
        txt = s[1].strip(); cs = nchars(txt)
        if has_vo and s[2] != '真人全屏' and k < len(stream):
            mine = stream[k:k + len(cs)]; k += len(cs)
            st = tt if j == 0 else max(tt, mine[0][1] - 0.06)
            shots.append(dict(i=i, row=r, text=txt, start=st, chars=mine, kind=s[2], vo=True, pause=s[8] or 0))
            tt = st
        else:
            d = len(cs) / rate + 0.25
            st = tt if not has_vo else row_end
            if has_vo: row_end += d
            ch = [(c, st + (q + 0.5) * (d - 0.25) / max(1, len(cs))) for q, c in enumerate(cs)]
            shots.append(dict(i=i, row=r, text=txt, start=st, chars=ch, kind=s[2], vo=False, pause=s[8] or 0, est=d))
            tt = st + d + (s[8] or 0)
            if has_vo: row_end = tt
    # 本行结束
    if has_vo:
        t = max(row_end, t)
    else:
        t = tt
    t += ROW_GAP
TOTAL = t + 0.6
for a, b in zip(shots, shots[1:]): a['end'] = b['start']
shots[-1]['end'] = TOTAL
for s in shots: s['dur'] = s['end'] - s['start']

# ---------------------------------------------------------------- 2. 字幕：每镜按标点切成 ≤15 字的条，按字时间出
PUN = '，。？！；：、'
PART = set('的了是在和地得把让被向对从到并而也都就还能会与及或')
def _w(tok):
    if tok in PUN or tok in '“”"': return 0.4
    return 0.55 * len(tok) if re.match(r'[A-Za-z0-9. ]+$', tok) else 1.0
def split_lines(txt, maxw=16.0):
    """逐字往行里放，放不下时往回找断点：标点 > 虚词后 > 当前位置；英文单词、数字不拆"""
    toks = re.findall(r'[A-Za-z][A-Za-z ]*[A-Za-z]|[A-Za-z]|\d+(?:\.\d+)?|.', txt.strip())
    lines, cur = [], []
    for tk in toks:
        if cur and sum(_w(x) for x in cur) + _w(tk) > maxw and tk not in PUN:
            cut = None
            for k in range(len(cur) - 1, -1, -1):
                L = sum(_w(x) for x in cur[:k + 1])
                if cur[k] in PUN and L >= 5: cut = k; break
            if cut is None:
                for k in range(len(cur) - 1, -1, -1):
                    L = sum(_w(x) for x in cur[:k + 1])
                    if cur[k] in PART and L >= 7 and k < len(cur) - 1: cut = k; break
            if cut is None: cut = len(cur) - 1
            lines.append(''.join(cur[:cut + 1])); cur = cur[cut + 1:]
        cur.append(tk)
        if tk in '。？！' and sum(_w(x) for x in cur) >= 6: lines.append(''.join(cur)); cur = []
    if cur: lines.append(''.join(cur))
    lines = [l.strip() for l in lines if l.strip(' ，。、')]
    # 最后一行太短（<4 字）：和上一行合起来重新均分，优先在虚词后断
    if len(lines) >= 2 and sum(_w(x) for x in re.findall(r'.', lines[-1].strip('，。、'))) < 4:
        tk = re.findall(r'[A-Za-z][A-Za-z ]*[A-Za-z]|[A-Za-z]|\d+(?:\.\d+)?|.', lines[-2] + lines[-1])
        ws = [_w(x) for x in tk]; tot = sum(ws); acc = np.cumsum(ws)
        k = min(range(len(tk) - 1), key=lambda k: abs(acc[k] - tot / 2) - (1.5 if tk[k] in PART or tk[k] in PUN else 0) + (9 if tk[k + 1] in PUN else 0))
        lines = lines[:-2] + [''.join(tk[:k + 1]), ''.join(tk[k + 1:])]
    return lines

SUBS = []
for s in shots:
    if s['i'] in (13, 17, 36): continue                 # 大字时刻不出字幕（不重复大字）
    txt = s['text']
    for a, b in SUB_FIX.items(): txt = txt.replace(a, b)
    lines = split_lines(txt.replace('\n', ''))
    q = 0; times = [c[1] for c in s['chars']]
    for ln in lines:
        n = len(nchars(ln)); t0 = times[min(q, len(times) - 1)] - 0.08; q += n
        SUBS.append([max(s['start'], t0), ln.rstrip('，。、；：'), s['i']])
for a, b in zip(SUBS, SUBS[1:]): a.append(b[0] if b[2] == a[2] else min(b[0], [s['end'] for s in shots if s['i'] == a[2]][0]))
SUBS[-1].append(TOTAL - 0.3)

def sub_at(t):
    for a, txt, i, b in SUBS:
        if a <= t < b: return txt
    return ''

# ---------------------------------------------------------------- 3. 画面
PH = np.zeros((600, 600, 3), np.uint8); PH[:] = (26, 36, 56)
ph_ic = to_rgba_np(icon('person', 360, (150, 175, 210)))
PHf = PH.astype(np.float32); put(PHf, ph_ic, 300, 330); PH = PHf.astype(np.uint8)
IG.HOST_PH = PH
B_HOST = glass(330, '真人出镜', 'person', title_size=44)

def grade(f):
    f = f.astype(np.float32) * np.array([0.94, 1.0, 1.05], np.float32)
    return f

VIDS = {}
def vid(k):
    if k not in VIDS: VIDS[k] = Vid(os.path.join(MAT, {'4': '4.空镜.mp4', '6': '6.演示录屏.mp4', '7': '7.400种.mp4', '10': '10.生物.mp4', '11': '11.化学.mp4'}[k]))
    return VIDS[k]

def v_video(clips, push=0.06):
    """clips: [(素材, 入, 出)]，镜头时长内平均分配，慢镜头自动提速"""
    def fn(tl, dur):
        n = len(clips); k = min(int(tl / dur * n), n - 1); d = dur / n; u = tl - k * d
        src, a, b = clips[k]
        sp = min(2.0, max(1.0, (b - a) / max(d, 0.1) if (b - a) < d * 1.0 else 1.5))
        st = min(a + u * sp, b - 0.05)
        fr = cover(vid(src).get(st), W, H)
        z = 1.0 + push * (u / max(d, 0.1))
        return grade(zoom(fr.astype(np.float32), z))
    return fn

IMGS = {}
def img(k):
    if k not in IMGS:
        p = {'1': '1.OpenAI Math.png', '2': '2.OpenAI Math.png', '3': '3.干的就是明珠.png', '5': '5.3.0Pro模型简介.png',
             '8': '8.蛋白质方案.png', '9': '9.科大讯飞活动页.png'}[k]
        a = imread(os.path.join(MAT, p))
        if k == '9':   # 横幅补成 16:9：上下用边缘拉伸+模糊补满
            h, w = a.shape[:2]; H2 = int(w * 9 / 16); top = (H2 - h) // 2
            ext = np.zeros((H2, w, 3), np.uint8); ext[top:top + h] = a
            ext[:top] = cv2.GaussianBlur(np.repeat(a[:1], top, 0), (0, 0), 25); ext[top + h:] = cv2.GaussianBlur(np.repeat(a[-1:], H2 - top - h, 0), (0, 0), 25)
            a = ext
        IMGS[k] = a
    return IMGS[k]

_BGN = bg('navy', key='navy')
def v_shot(k, box0, box1=None, hl=None, ry=(-8, -4), rx=4, maxk=2.6, white=False, finder_on=False):
    """截图：整张做卡片、倾斜，镜头对准 box，其余压暗，可选高亮条"""
    box1 = box1 or box0
    A = img(k)
    def fn(tl, dur):
        u = ease(tl / max(dur, 0.1))
        bx = [lerp(p, q, u) for p, q in zip(box0, box1)]
        bw, bh = bx[2] - bx[0], bx[3] - bx[1]
        s = min(1450 / bw, 760 / bh, maxk) * (0.93 + 0.07 * ease_out(min(1, tl / 0.8)))
        # 只截 box 周围一屏范围，省算力
        mx, my = W / s * 0.75, H / s * 0.75
        x0, y0 = int(max(0, bx[0] - mx)), int(max(0, bx[1] - my)); x1, y1 = int(min(A.shape[1], bx[2] + mx)), int(min(A.shape[0], bx[3] + my))
        sub = A[y0:y1, x0:x1]
        cw = max(8, int(sub.shape[1] * s))
        cd = card(sub, cw, radius=int(18 * s / 2 + 8))
        ch = cd.shape[0]
        cx_box = ((bx[0] + bx[2]) / 2 - x0) * s; cy_box = ((bx[1] + bx[3]) / 2 - y0) * s
        f = _BGN.copy()
        ryv = lerp(ry[0], ry[1], u)
        M = persp(f, cd, W / 2 + (cw / 2 - cx_box), H / 2 + (ch / 2 - cy_box) - 20, 1.0, ry=ryv, rx=rx, a=1.0, shadow_k=0.5)
        kb = ((bx[0] - x0) * s, (bx[1] - y0) * s, (bx[2] - x0) * s, (bx[3] - y0) * s)
        poly = dim_except(f, M, kb, 0.5 if not white else 0.35)
        if hl:
            hb = [(hl[0] - x0) * s, (hl[1] - y0) * s, (hl[2] - x0) * s, (hl[3] - y0) * s]
            hp = cv2.perspectiveTransform(np.array([[[hb[0], hb[1]], [hb[2], hb[3]]]], np.float32), M)[0]
            hl_bar(f, max(0, hp[0][0]), max(0, hp[0][1]), min(W - 1, hp[1][0]), min(H - 1, hp[1][1]), seg(tl, 0.35, 1.1), AMBER, 0.38)
        if finder_on:
            xs, ys = poly[:, 0], poly[:, 1]
            finder(f, xs.min() - 14, ys.min() - 14, xs.max() + 14, ys.max() + 14, seg(tl, 0.2, 0.6), scan=seg(tl, 0.6, 1.5))
        return f
    return fn

def v_rec(k, a, b, box, ry=(-10, -5)):
    """录屏：按 box 裁到有内容的部分，圆角卡片放深色底，透视；in→out 压缩到镜头时长"""
    def fn(tl, dur):
        u = tl / max(dur, 0.1)
        fr = vid(k).get(a + (b - a) * u)
        x0, y0, x1, y1 = box; sub = fr[y0:y1, x0:x1]
        s = min(1780 / sub.shape[1], 960 / sub.shape[0])
        cd = card(sub, int(sub.shape[1] * s), radius=24)
        f = _BGN.copy()
        persp(f, cd, W / 2, H / 2 - 10, 0.97 + 0.05 * ease(u), ry=lerp(ry[0], ry[1], ease(u)), rx=4, shadow_k=0.55)
        return f
    return fn

def v_host(stickers=()):
    """出镜占位：等出镜视频传上来替换"""
    def fn(tl, dur):
        f = _BGN.copy()
        put(f, B_HOST, W / 2, H / 2 - 40, 1.0, scale=1.0 + 0.02 * tl / max(dur, 0.1))
        for j, (im, t0, x, y, ang) in enumerate(stickers):
            k = seg(tl, t0, t0 + 0.35)
            if k > 0: put(f, im, x, y, k, scale=0.7 + 0.3 * back_out(k), angle=ang)
        return f
    return fn

def v_meme():
    A = img('3')[:420]
    card_im = photo(A, 860, border=14)
    def fn(tl, dur):
        f = cv2.GaussianBlur(cover(A, W, H).astype(np.float32), (0, 0), 30) * 0.35 + _BGN * 0.65
        k = seg(tl, 0, 0.25)
        put(f, card_im, W / 2, H / 2 - 30, k, scale=1.25 - 0.25 * back_out(k), angle=-4)
        return shake(f, max(0, 1 - tl / 0.4), int(tl * 30))
    return fn

def v_fn(fn, **kw):
    return lambda tl, dur: fn(tl, dur, **kw)

def v_protein(fold=None):
    return lambda tl, dur: KJ.protein(tl + 1.0, dur, fold=fold)

# 贴纸
ST_REC = photo(vid('6').get(140.0)[40:1000, 500:2634], 520, angle=0)
ST_LAB = photo(vid('11').get(225.0), 520)
ST_OAI = photo(img('1')[330:1150, 150:2874], 480)
ST_P8 = photo(img('8')[30:360, 40:780], 480)

def visual_for(s, shot_by_i):
    i = s['i']
    dur_of = lambda j: shot_by_i[j]['dur']
    V = {
     2: v_shot('1', (150, 330, 2874, 1150)),
     3: v_shot('1', (60, 1780, 2964, 2010), hl=(560, 1800, 2964, 1990)),
     4: v_shot('2', (300, 2540, 2060, 2740), hl=(330, 2555, 2060, 2610), finder_on=True),
     5: v_shot('2', (350, 3310, 1580, 3700), (350, 3760, 1580, 4150)),
     7: v_shot('2', (340, 4280, 2060, 4500), hl=(340, 4380, 2060, 4430)),
     8: v_shot('2', (340, 1990, 2060, 2170), hl=(340, 1995, 2060, 2050), finder_on=True),
     10: v_fn(IG.knowledge, split=dur_of(10)),
     13: v_fn(IG.create_title), 15: v_meme(), 17: v_fn(IG.afs_title), 36: v_fn(IG.valley),
     19: v_video([('4', 27.5, 30.7)]), 20: v_video([('4', 35.7, 39.5)]), 21: v_video([('4', 59.1, 63.0)]),
     22: v_video([('4', 12.7, 15.9)]), 23: v_video([('4', 0.0, 5.0)]), 24: v_video([('4', 18.7, 23.3)]),
     26: v_video([('11', 2.0, 25.6)]), 27: v_video([('11', 77.7, 83.5)]), 28: v_video([('11', 222.9, 232.3)]),
     29: v_fn(KJ.digital_factory), 30: v_video([('11', 133.3, 148.2)]),
     31: v_video([('11', 38.0, 50.5), ('11', 26.0, 37.7)]), 32: v_video([('11', 84.0, 102.4), ('11', 206.0, 222.9)]),
     33: v_video([('11', 193.0, 199.0)]), 34: v_video([('11', 149.0, 162.3)]),
     37: v_fn(IG.partners),
     38: v_shot('5', (370, 130, 710, 205), maxk=2.2), 39: v_shot('5', (150, 200, 960, 305), maxk=2.2),
     40: v_rec('6', 0.0, 3.0, (600, 250, 2500, 1080)), 41: v_rec('6', 28.0, 34.0, (650, 450, 2450, 1180)),
     42: v_rec('6', 16.0, 22.0, (600, 20, 2400, 1050)), 43: v_rec('6', 36.0, 96.0, (650, 250, 2450, 1180)),
     44: v_rec('6', 100.0, 134.0, (600, 20, 2400, 1000)), 45: v_rec('6', 136.0, 145.5, (450, 20, 2634, 1050)),
     46: v_rec('7', 2.0, 8.0, (250, 40, 2636, 1300)), 47: v_fn(IG.four_hundred), 48: v_rec('7', 12.0, 20.0, (250, 40, 2636, 1100)),
     49: v_host([(ST_REC, 0.4, 1530, 420, -3)]), 50: v_host([(ST_REC, 0.0, 1530, 420, -3), (ST_LAB, 0.3, 1500, 760, 3)]),
     51: v_video([('10', 1.0, 14.7)]), 52: v_video([('10', 15.0, 31.9)]), 53: v_video([('10', 33.0, 59.7)]),
     54: v_protein(), 55: v_video([('10', 60.0, 71.6), ('10', 81.0, 94.0)]),
     56: v_shot('8', (0, 0, 1010, 713), maxk=1.4, white=True), 57: v_shot('8', (40, 30, 780, 360), maxk=2.0, white=True),
     58: v_protein(fold=(0.0, 1.8)), 59: v_shot('8', (835, 50, 1005, 215), maxk=3.0, white=True),
     60: v_video([('10', 72.0, 80.9)]),
     62: v_host([(ST_OAI, 0.2, 1500, 300, -3), (ST_REC, 1.4, 1560, 560, 2), (ST_P8, 2.6, 1480, 820, -2)]),
     66: v_shot('9', (520, 120, 1120, 700), maxk=1.9), 68: v_fn(IG.five_scenes, step=max(0.5, (dur_of(68) - 1.0) / 5)),
     70: v_shot('9', (180, 280, 760, 600), (980, 280, 1480, 600), maxk=1.9),
    }
    if i == 11: return lambda tl, dur: IG.knowledge(tl + dur_of(10), dur_of(10) + dur, split=dur_of(10))
    if i == 63:
        d63 = dur_of(63); d64 = dur_of(64)
        txt = shot_by_i[64]['text']; L = len(txt)
        on = [d63 + d64 * txt.index(w) / L for w in ('提出方案', '调用工具', '模拟计算', '辅助验证')]
        return lambda tl, dur: IG.four_steps(tl, d63 + d64, on=[o - 0.1 for o in on])
    if i == 64:
        d63 = dur_of(63); d64 = dur_of(64); txt = s['text']; L = len(txt)
        on = [d63 + d64 * txt.index(w) / L for w in ('提出方案', '调用工具', '模拟计算', '辅助验证')]
        return lambda tl, dur: IG.four_steps(tl + d63, d63 + d64, on=[o - 0.1 for o in on])
    if i in V: return V[i]
    return v_host()

# ---------------------------------------------------------------- 4. 转场：截图/录屏/素材之间甩镜，大字和数字有重击
WHIP_IN = {2, 4, 7, 8, 19, 26, 38, 40, 46, 51, 56, 66, 70}
def frame_at(t, shot_by_i, vis):
    s = next(x for x in shots if x['start'] <= t < x['end']) if t < TOTAL else shots[-1]
    tl = t - s['start']
    f = vis[s['i']](tl, s['dur'])
    if s['i'] in WHIP_IN and tl < 0.22: f = whip(f, 1 - tl / 0.22)
    nxt = [x for x in shots if x['start'] >= s['end'] - 1e-6][:1]
    if nxt and nxt[0]['i'] in WHIP_IN and s['end'] - t < 0.12: f = whip(f, (0.12 - (s['end'] - t)) / 0.12 * 0.8)
    subtitle(f, sub_at(t))
    return f

def build_vis():
    shot_by_i = {s['i']: s for s in shots}
    return shot_by_i, {s['i']: visual_for(s, shot_by_i) for s in shots}

if __name__ == '__main__':
    print(f'语速 {rate:.2f} 字/秒；总长 {TOTAL:.1f} 秒；镜头 {len(shots)}；有录音 {sum(s["vo"] for s in shots)}')
    for s in shots: print(f"{s['i']:3d} {s['start']:7.2f} {s['dur']:5.2f} {'声' if s['vo'] else '估'} {s['text'][:20]}")
    json.dump(dict(shots=shots, audio=audio_pieces, total=TOTAL, subs=SUBS), open('timeline.json', 'w'), ensure_ascii=False, indent=1)
