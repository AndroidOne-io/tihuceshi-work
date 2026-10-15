# 脚本里没有素材的信息图 / 大字时刻
import math, numpy as np, cv2
from kx import *
import kongjing as KJ

HOST = Vid(os.path.join(REPO, '口播粗剪.mp4'))       # 占位：上期口播，这期录好后替换
HOST_PH = None   # 设成图片后，小窗改用这张占位图
def host_frame(t, t0=50.0): return HOST_PH if HOST_PH is not None else HOST.get(t0 + t)

_BG = None
def BGN():
    global _BG
    if _BG is None: _BG = bg('navy', key='navy')
    return _BG.copy()

def _ring(lay, c, r, col, w=3, a0=0, a1=360):
    cv2.ellipse(lay, (int(c[0]), int(c[1])), (int(r), int(r)), 0, a0, a1, col, w, cv2.LINE_AA)

def _glow(l, k=0.8): return l + cv2.GaussianBlur(l, (0, 0), 4) * k + cv2.GaussianBlur(l, (0, 0), 18) * k * 0.7

def _word(t, size=120, col=WHITE, gcol=CYAN):
    return shadow(glow_rgba(text(t, F_BLACK, size, col, 0.08), gcol, 22, 0.7), 14, (0, 8), 200)

# ================================================================ R5b 知识圈：向内索取 → 向外延伸（带圆形小窗）
_rng = np.random.default_rng(2)
_KN_IN = _rng.uniform(0, 1, (160, 2))
_KN_OUT = np.c_[_rng.uniform(0, 2 * np.pi, 70), _rng.uniform(1.15, 1.9, 70), _rng.uniform(0, 1, 70)]
WORD_IN, WORD_OUT = _word('向内索取'), _word('向外延伸', col=(255, 236, 200), gcol=AMBER)
IC_DOC, IC_LIST = glass(150, '', 'doc'), glass(150, '', 'list')

def knowledge(t, dur=8.0, split=3.8):
    f = BGN(); c = (1120, 560); R = 290
    lay = np.zeros((H, W, 3), np.float32)
    out_u = ease(seg(t, split, split + 1.6))
    # 圈：出现
    u0 = ease_out(seg(t, 0, 0.6))
    _ring(lay, c, R * (0.85 + 0.15 * u0), (np.array(CYAN) * u0).tolist(), 4)
    _ring(lay, c, R * 0.62, (np.array(CYAN) * 0.25 * u0).tolist(), 2)
    # 圈内知识点：向内阶段往圆心收
    for (a, rr) in _KN_IN:
        ang = a * 2 * np.pi + t * 0.15; r0 = math.sqrt(rr) * R * 0.9
        pull = (t * 0.35 + rr) % 1.0 if t < split else 0
        r1 = r0 * (1 - 0.55 * pull) if t < split else r0
        p = (int(c[0] + r1 * math.cos(ang)), int(c[1] + r1 * math.sin(ang)))
        cv2.circle(lay, p, 3, (np.array(CYAN) * (0.5 + 0.5 * (1 - out_u * 0.5)) * u0).tolist(), -1, cv2.LINE_AA)
    # 向外：一束光从圆心冲出右上方，圈被冲开，圈外亮起新星
    if t >= split:
        ang = math.radians(-28); L = R * (0.2 + 1.7 * ease_out(seg(t, split, split + 1.0)))
        p0 = (int(c[0]), int(c[1])); p1 = (int(c[0] + L * math.cos(ang)), int(c[1] + L * math.sin(ang)))
        cv2.line(lay, p0, p1, AMBER, 6, cv2.LINE_AA)
        cv2.circle(lay, p1, 12, (255, 240, 210), -1, cv2.LINE_AA)
        hit = seg(t, split + 0.35, split + 0.7)
        if 0 < hit < 1:
            bp = (int(c[0] + R * math.cos(ang)), int(c[1] + R * math.sin(ang)))
            _ring(lay, bp, 20 + 120 * hit, (np.array(WHITE) * (1 - hit)).tolist(), 3)
        for (a, rr, ph) in _KN_OUT:
            if seg(t, split + 0.5 + ph * 1.8, split + 0.9 + ph * 1.8) > 0:
                k = seg(t, split + 0.5 + ph * 1.8, split + 0.9 + ph * 1.8)
                p = (int(c[0] + rr * R * math.cos(a)), int(c[1] + rr * R * math.sin(a) * 0.8))
                if 0 < p[0] < W and 0 < p[1] < H:
                    cv2.circle(lay, p, int(2 + 4 * k), (np.array(AMBER) * k).tolist(), -1, cv2.LINE_AA)
    f += _glow(lay)
    # 图标：写文章、总结资料，在圈里
    ia = ease_out(seg(t, 0.4, 1.0)) * (1 - 0.6 * out_u)
    put(f, IC_DOC, c[0] - 95, c[1] - 10 + 20 * (1 - ia), ia, scale=0.6 + 0.4 * back_out(seg(t, 0.4, 1.0)))
    put(f, IC_LIST, c[0] + 95, c[1] - 10 + 20 * (1 - ia), ia, scale=0.6 + 0.4 * back_out(seg(t, 0.6, 1.2)))
    # 花字（在图里，不压脸）
    a_in = ease_out(seg(t, 1.3, 1.7)) * (1 - ease(seg(t, split - 0.2, split + 0.2)))
    put(f, WORD_IN, c[0], c[1] - R - 110, a_in, scale=1.1 - 0.1 * ease_out(seg(t, 1.3, 1.7)))
    a_out = ease_out(seg(t, split + 0.9, split + 1.3))
    put(f, WORD_OUT, c[0] + 330, c[1] - R - 70, a_out, scale=1.1 - 0.1 * a_out)
    pip(f, host_frame(t), 250, H - 250, 330, ease_out(seg(t, 0, 0.5)))
    return f

# ================================================================ R6b 大字：使用知识 → 参与创造知识
T_USE = _word('使用知识', 120, (170, 178, 190), (90, 110, 140))
T_CREATE = metal('参与创造知识', 200, 0.08)
T_CREATE_A = to_rgba_np(T_CREATE)
_ZB = None
def create_title(t, dur=4.2):
    global _ZB
    if _ZB is None: _ZB = KJ.math_cosmos(5.5, 6.0)
    f = cv2.GaussianBlur(_ZB, (0, 0), 6) * 0.25 + BGN() * 0.75
    u1 = ease_out(seg(t, 0.0, 0.4)); back = ease_in(seg(t, 1.1, 1.5))
    put(f, T_USE, W / 2, H / 2, u1 * (1 - back), scale=1.0 - 0.35 * back)
    hit = 1.45
    if t >= hit:
        u = seg(t, hit, hit + 0.28)
        arr = sweep(T_CREATE_A, seg(t, hit + 0.4, hit + 1.4))
        put(f, arr, W / 2, H / 2, ease_out(u, 2), scale=1.35 - 0.35 * ease_out(u, 4))
        fl = max(0.0, 1 - (t - hit) / 0.25); f += fl * 120
        f = shake(f, max(0.0, 1 - (t - hit) / 0.35), int(t * 30))
    return f

# ================================================================ R8b 全片标题：AI for Science（素材4 全息转盘做景深）
V4 = Vid(os.path.join(MAT, '4.空镜.mp4'))
T_AFS = to_rgba_np(metal('AI for Science', 210, 0.03, fp=F_BLACK))
_PART = np.random.default_rng(9).uniform(0, 1, (260, 3))
def afs_title(t, dur=4.5):
    v = V4.get(50.0 + t * 0.8).astype(np.float32)
    v = cv2.GaussianBlur(cover(v, W, H), (0, 0), 7)
    f = BGN() * 0.55 + v * np.array([0.35, 0.5, 0.62]) * 0.75
    lay = np.zeros((H, W, 3), np.float32)
    conv = ease_in(seg(t, 0.0, 1.15), 2)
    for (a, r, s) in _PART:   # 粒子从四周汇聚到标题
        ang = a * 2 * np.pi; rr = (0.25 + r) * W * 0.7 * (1 - conv) + 40 * s
        p = (int(W / 2 + rr * math.cos(ang) * (0.6 + 0.4 * s)), int(H / 2 + rr * math.sin(ang) * 0.55))
        cv2.circle(lay, p, 2 + int(2 * s), (np.array(CYAN) * (0.5 + 0.5 * s) * (1 - seg(t, 1.1, 1.4))).tolist(), -1, cv2.LINE_AA)
    f += _glow(lay, 0.9)
    hit = 1.2
    if t >= hit:
        u = seg(t, hit, hit + 0.3)
        put(f, sweep(T_AFS, seg(t, hit + 0.5, hit + 1.6)), W / 2, H / 2, ease_out(u, 2), scale=1.25 - 0.25 * ease_out(u, 4) + 0.02 * (t - hit))
        f += max(0.0, 1 - (t - hit) / 0.3) * 150
        f = shake(f, max(0.0, 1 - (t - hit) / 0.4), int(t * 30))
    return bloom(f, 0.25)

# ================================================================ R12b 死亡之谷：曲线一头栽进谷底 → 毛笔大字
V11 = Vid(os.path.join(MAT, '11.化学.mp4'))
B_LAB, B_FAC = glass(170, '', 'flask'), glass(170, '', 'factory', tint=BLUE)
T_VALLEY = brush('死亡之谷', 300)
_HB = None
def valley(t, dur=5.2):
    global _HB
    if _HB is None: _HB = bg('navy', backdrop=V11.get(230.0), dim=0.38, halftone=True, key='valley')
    f = _HB.copy()
    xs = np.linspace(260, 1660, 600)
    def yfun(x):
        u = (x - 260) / 1400
        return 360 + 40 * u + 470 * np.exp(-((u - 0.52) / 0.11) ** 2) - 160 * np.clip((u - 0.7) / 0.3, 0, 1)
    ys = np.array([yfun(x) for x in xs])
    draw = ease(seg(t, 0.3, 2.5)); n = max(2, int(len(xs) * draw))
    lay = np.zeros((H, W, 3), np.float32)
    pts = np.c_[xs[:n], ys[:n]].astype(np.int32)
    for i in range(1, n):
        dip = max(0.0, (ys[i] - 420) / 400)
        col = np.array(CYAN) * (1 - dip) + np.array(RED) * dip
        cv2.line(lay, tuple(pts[i - 1]), tuple(pts[i]), col.tolist(), 6, cv2.LINE_AA)
    cv2.circle(lay, tuple(pts[-1]), 12, (255, 245, 230), -1, cv2.LINE_AA)
    # 谷底红光
    fall = seg(t, 1.25, 1.6)
    if fall > 0:
        gx, gy = int(xs[int(len(xs) * 0.52)]), int(ys.max())
        cv2.circle(lay, (gx, gy), int(30 + 60 * fall), (np.array(RED) * (1 - 0.5 * fall)).tolist(), 3, cv2.LINE_AA)
    f += _glow(lay)
    put(f, B_LAB, 240, 350, ease_out(seg(t, 0, 0.4)))
    put(f, B_FAC, 1690, ys[-1] - 10, ease_out(seg(t, 2.2, 2.6)) * 0.6)
    if 1.25 < t < 1.7: f = shake(f, 1 - seg(t, 1.25, 1.7), int(t * 30))
    # 大字单独出：图压暗 + 毛笔字砸下 + 故障闪
    hit = 2.8
    if t >= hit:
        dk = ease(seg(t, hit - 0.2, hit + 0.1)); f = f * (1 - 0.65 * dk)
        u = seg(t, hit, hit + 0.25)
        put(f, T_VALLEY, W / 2, H / 2, ease_out(u, 2), scale=1.3 - 0.3 * ease_out(u, 4))
        g = max(0.0, 1 - (t - hit) / 0.35)
        f = glitch(f, g, int(t * 30)); f = shake(f, g, int(t * 31))
    return f

# ================================================================ R13 合作徽章（logo 待提供，先用名字）
B_XF = glass(440, '科大讯飞', None, tint=CYAN, title_size=80)
B_DI = glass(440, '中科院大连化物所', None, tint=BLUE, title_size=50)
def partners(t, dur=3.6):
    f = BGN()
    u = ease_out(seg(t, 0, 0.7), 4)
    xl = lerp(-300, W / 2 - 300, u); xr = lerp(W + 300, W / 2 + 300, u)
    lay = np.zeros((H, W, 3), np.float32)
    if t > 0.7:
        k = ease_out(seg(t, 0.7, 1.0))
        cv2.line(lay, (int(W / 2 - 80), H // 2), (int(W / 2 - 80 + 160 * k), H // 2), AMBER, 4, cv2.LINE_AA)
        sp = seg(t, 0.95, 1.4)
        if 0 < sp < 1: _ring(lay, (W // 2, H // 2), 10 + 90 * sp, (np.array(WHITE) * (1 - sp)).tolist(), 3)
    f += _glow(lay)
    put(f, B_XF, xl, H / 2, 1.0, scale=1 + 0.03 * math.sin(t * 2))
    put(f, B_DI, xr, H / 2, 1.0, scale=1 + 0.03 * math.sin(t * 2 + 1))
    return f

# ================================================================ R19b 四个环节依次点亮（带小窗）
STEPS = [('提出方案', 'bulb'), ('调用工具', 'wrench'), ('模拟计算', 'chart'), ('辅助验证', 'check')]
B_ON = [glass(300, n, ic, active=1.0, title_size=52) for n, ic in STEPS]
B_OFF = [glass(300, n, ic, active=0.3, title_size=52) for n, ic in STEPS]
def four_steps(t, dur=6.0, on=None):
    f = BGN(); c = (1110, 540); R = 290
    pos = [(c[0], c[1] - R), (c[0] + R, c[1]), (c[0], c[1] + R), (c[0] - R, c[1])]
    on = on or [0.6 + 1.0 * i for i in range(4)]
    lay = np.zeros((H, W, 3), np.float32)
    _ring(lay, c, R, (np.array(CYAN) * 0.25).tolist(), 2)
    for i in range(4):          # 弧线随点亮依次接上
        k = ease(seg(t, on[i] + 0.3, on[i] + 0.9))
        if k > 0:
            a0 = -90 + i * 90 + 22; _ring(lay, c, R, CYAN, 4, a0, a0 + (90 - 44) * k)
    if t > on[3] + 0.9:         # 全亮后粒子沿环流动
        for k in range(10):
            a = math.radians(-90 + ((t - on[3]) * 60 + k * 36) % 360)
            cv2.circle(lay, (int(c[0] + R * math.cos(a)), int(c[1] + R * math.sin(a))), 6, AMBER, -1, cv2.LINE_AA)
    f += _glow(lay)
    for i, p in enumerate(pos):
        k = seg(t, on[i], on[i] + 0.25)
        put(f, B_OFF[i], p[0], p[1], ease_out(seg(t, 0, 0.4)) * (1 - k))
        if k > 0: put(f, B_ON[i], p[0], p[1], k, scale=1 + 0.15 * (1 - back_out(seg(t, on[i], on[i] + 0.5))))
    pip(f, host_frame(t, 80.0), 250, H - 250, 330, ease_out(seg(t, 0, 0.5)))
    return f

# ================================================================ R20c 五个场景（替代缺的教育、生活空镜）
SCN = [('科研', 'flask'), ('教育', 'book'), ('医疗', 'medical'), ('工业', 'gear'), ('生活', 'home')]
S_ON = [glass(285, n, ic, active=1.0, title_size=58) for n, ic in SCN]
S_OFF = [glass(285, n, ic, active=0.3, title_size=58) for n, ic in SCN]
def five_scenes(t, dur=4.6, step=0.85):
    f = BGN(); xs = [W / 2 + (i - 2) * 350 for i in range(5)]; y = H / 2 - 20
    lay = np.zeros((H, W, 3), np.float32)
    for i in range(4):
        k = ease(seg(t, 0.3 + step * (i + 1) - 0.4, 0.3 + step * (i + 1)))
        if k > 0: cv2.line(lay, (int(xs[i] + 145), int(y)), (int(xs[i] + 145 + 60 * k), int(y)), CYAN, 3, cv2.LINE_AA)
    f += _glow(lay)
    for i in range(5):
        t_on = 0.3 + step * i; k = seg(t, t_on, t_on + 0.2)
        cur = (t_on <= t < t_on + step) or (i == 4 and t >= t_on)
        put(f, S_OFF[i], xs[i], y, ease_out(seg(t, 0, 0.35)) * (1 - k))
        if k > 0: put(f, S_ON[i], xs[i], y, k * (1.0 if cur else 0.75), scale=(1.12 if cur else 1.0) + 0.12 * (1 - back_out(seg(t, t_on, t_on + 0.45))))
    if t > 0.3 + step * 4 + 0.4:   # 最后一个点亮后，全部一起亮
        k = ease(seg(t, 0.3 + step * 4 + 0.4, 0.3 + step * 4 + 0.8))
        for i in range(4): put(f, S_ON[i], xs[i], y, k * 0.3)
    return f

# ================================================================ R15 数字「400+」砸在智能体广场录屏上
V7 = Vid(os.path.join(MAT, '7.400种.mp4'))
N400 = number('400', '+', 300)
def four_hundred(t, dur=3.6):
    f = BGN()
    v = V7.get(3.0 + t * 1.4)
    rg = card(v[60:1380, 300:2600], 1500, 26)
    hit = 1.0
    dk = ease(seg(t, hit - 0.15, hit + 0.1))
    persp(f, rg, W / 2 + 40, H / 2 + 30, 1.0 + 0.03 * t, ry=-16 + 4 * t / dur, rx=6, a=1.0)
    f = f * (1 - 0.6 * dk)
    if t >= hit:
        u = seg(t, hit, hit + 0.25)
        put(f, N400, W / 2, H / 2, ease_out(u, 2), scale=1.3 - 0.3 * ease_out(u, 4))
        finder(f, W / 2 - 330, H / 2 - 200, W / 2 + 330, H / 2 + 200, seg(t, hit + 0.15, hit + 0.55), scan=seg(t, hit + 0.5, hit + 1.4))
        f = shake(f, max(0.0, 1 - (t - hit) / 0.35), int(t * 30))
    return f
