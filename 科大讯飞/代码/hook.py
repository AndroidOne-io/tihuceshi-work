# 开场冷开：黑场蓄力 → 冲进数学隧道 → 粒子聚成问号 → 「攻克」时问号炸成金色
import math, numpy as np, cv2
from kx import *
from v3 import VIOLET, GOLD, SKY, CRIMSON

rng = np.random.default_rng(21)
NP = 2600
# 隧道粒子：圆柱面上随机分布，沿 z 向镜头飞
TU_A = rng.uniform(0, 2 * np.pi, NP); TU_R = rng.uniform(260, 1300, NP); TU_Z = rng.uniform(80, 6000, NP)
TU_C = np.array([VIOLET, SKY, (200, 160, 255), GOLD])[rng.choice(4, NP, p=[0.42, 0.33, 0.2, 0.05])]

def _qmask(n=2200):
    im = Image.new('L', (900, 1100), 0); d = ImageDraw.Draw(im)
    f = font(F_BLACK, 1000); d.text((450, 560), '?', font=f, fill=255, anchor='mm')
    a = np.array(im); ys, xs = np.nonzero(a > 128); k = rng.choice(len(xs), n, replace=False)
    return np.c_[xs[k] - 450, ys[k] - 560].astype(np.float32) * 0.62
QP = _qmask()
QS = np.c_[rng.uniform(-W, W, len(QP)), rng.uniform(-H, H, len(QP))].astype(np.float32)          # 起始散开位置
QV = rng.normal(0, 1, (len(QP), 2)).astype(np.float32); QV /= np.linalg.norm(QV, axis=1, keepdims=True) + 1e-6
QV *= rng.uniform(600, 2200, (len(QP), 1)).astype(np.float32)

def _bg():
    f = np.zeros((H, W, 3), np.float32); f[:] = (10, 9, 14); return f

def tunnel(t, speed, lay, k_col=1.0, streak=1.0):
    z = (TU_Z - t * speed) % 6000 + 60
    z_prev = z + speed * (1 / FPS) * 2.5 * streak
    fx = 900.0
    x = W / 2 + TU_R * np.cos(TU_A + t * 0.15) * fx / z; y = H / 2 + TU_R * np.sin(TU_A + t * 0.15) * fx / z
    xp = W / 2 + TU_R * np.cos(TU_A + t * 0.15) * fx / z_prev; yp = H / 2 + TU_R * np.sin(TU_A + t * 0.15) * fx / z_prev
    b = np.clip(1.6 - z / 4000, 0, 1) * k_col
    for i in np.nonzero(b > 0.03)[0]:
        c = (TU_C[i] * b[i]).tolist(); w = 1 if z[i] > 1500 else 2 if z[i] > 600 else 3
        cv2.line(lay, (int(xp[i]), int(yp[i])), (int(x[i]), int(y[i])), c, w, cv2.LINE_AA)
    return lay

def glow(l, a=0.9, b=0.7): return l + cv2.GaussianBlur(l, (0, 0), 3) * a + cv2.GaussianBlur(l, (0, 0), 16) * b

def hook(t, T):
    """t: 以人声开始为 0（负数是黑场蓄力）；T: dict 里放关键时刻 human, quan, gongke, end"""
    f = _bg(); lay = np.zeros((H, W, 3), np.float32)
    if t < 0:                                    # 黑场蓄力：光点拉成一道横光，粒子向中心收
        u = seg(t, -1.6, 0)
        L = int(40 + 900 * ease_in(u, 3))
        cv2.line(lay, (W // 2 - L, H // 2), (W // 2 + L, H // 2), (np.array((220, 200, 255)) * (0.3 + 0.7 * u)).tolist(), 2 + int(3 * u), cv2.LINE_AA)
        cv2.circle(lay, (W // 2, H // 2), int(4 + 10 * u), (255, 255, 255), -1, cv2.LINE_AA)
        tunnel(-t * 1.0, -900 * u, lay, k_col=0.35 * u, streak=0.5)
        return f + glow(lay, 1.0, 1.2)
    hq, ge = T['human'], T['gongke']
    if t < hq + 0.2:                             # 高速冲进隧道
        sp = 5200 * (1 - 0.65 * ease(seg(t, hq - 0.5, hq + 0.2)))
        tunnel(t, sp, lay, 1.0, 1.0)
        f += glow(lay)
        f += max(0.0, 1 - t / 0.22) * 255        # 闪白
        return zoom(f, 1.0 + 0.05 * math.sin(t * 2), 0.5, 0.5)
    # 隧道慢下来，粒子聚成问号
    tunnel(t, 900, lay, 0.45, 0.6)
    u = ease(seg(t, hq, hq + 1.3))
    P = QS * (1 - u) + QP * u
    col = np.array((150, 150, 170), np.float32)
    if t >= ge:                                  # 「攻克」：问号炸开成金色
        k = t - ge
        P = QP + QV * (1 - math.exp(-k * 2.2)) * 0.9 + np.array([0, 160 * k * k])
        col = np.array(GOLD, np.float32) * (1.25 - 0.2 * min(1, k))
        r = int(60 + 1600 * ease_out(min(1, k / 0.7)))
        cv2.circle(lay, (W // 2, H // 2), r, (np.array(GOLD) * max(0, 1 - k / 0.7)).tolist(), 6, cv2.LINE_AA)
    else:
        col = col * (0.6 + 0.4 * u)
    for (x, y) in P:
        cv2.circle(lay, (int(W / 2 + x), int(H / 2 + y)), 3, col.tolist(), -1, cv2.LINE_AA)
    f += glow(lay, 0.8, 0.9)
    if t >= ge:
        k = t - ge
        f += max(0.0, 1 - k / 0.18) * 230
        f = shake(f, max(0.0, 1 - k / 0.6), int(t * 30))
        f = glitch(f, max(0.0, 0.8 - k / 0.4), int(t * 30))
    return f
