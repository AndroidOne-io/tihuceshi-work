# 代码生成的空镜（全屏、无文字）
import math, numpy as np, cv2
from kx import *
from zeta import zeta

def _glow(layer, r1=3, r2=14, k1=0.9, k2=0.6):
    return layer + cv2.GaussianBlur(layer, (0, 0), r1) * k1 + cv2.GaussianBlur(layer, (0, 0), r2) * k2

def _proj(P, cam_d, f=1300, cx=W / 2, cy=H / 2):
    z = P[:, 2] + cam_d
    return np.stack([cx + P[:, 0] * f / z, cy + P[:, 1] * f / z], 1), z

def _rot(ax, ay, az=0.0):
    cx_, sx = math.cos(ax), math.sin(ax); cy_, sy = math.cos(ay), math.sin(ay); cz, sz = math.cos(az), math.sin(az)
    Rx = np.array([[1, 0, 0], [0, cx_, -sx], [0, sx, cx_]]); Ry = np.array([[cy_, 0, sy], [0, 1, 0], [-sy, 0, cy_]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

# ================================================================ 1. 数学宇宙：素数螺旋 + ζ 函数临界线轨迹
def _ulam(n):
    pts = np.zeros((n + 1, 2)); x = y = 0; dx, dy = 1, 0; step, cnt, turn = 1, 0, 0
    for i in range(2, n + 1):
        x += dx; y += dy; pts[i] = (x, y); cnt += 1
        if cnt == step:
            cnt = 0; dx, dy = -dy, dx; turn += 1
            if turn % 2 == 0: step += 1
    return pts
_N = 30000
_sieve = np.ones(_N + 1, bool); _sieve[:2] = False
for p in range(2, int(_N ** 0.5) + 1):
    if _sieve[p]: _sieve[p * p::p] = False
_UL = _ulam(_N)
_PR = np.nonzero(_sieve)[0]
_ZT = np.linspace(0.0, 48.0, 2400); _ZV = zeta(0.5 + 1j * _ZT)
_ZEROS = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062, 37.586178, 40.918719, 43.327073, 48.005151]

def math_cosmos(t, dur=6.0, bgimg=None):
    base = bgimg.copy() if bgimg is not None else bg('deep', key='deep')
    lay = np.zeros((H, W, 3), np.float32)
    # 素数螺旋：倾斜平面缓慢旋转，波从中心向外点亮
    P = np.c_[_UL[_PR] * 9.0, np.zeros(len(_PR))]
    R = _rot(math.radians(58), 0, math.radians(8 + t * 3.0))
    Q = P @ R.T; Q[:, 1] += 140
    uv, z = _proj(Q, 1500 - t * 40)
    r = np.hypot(_UL[_PR][:, 0], _UL[_PR][:, 1])
    wave = np.clip((t * 22 + 10 - r) / 12, 0, 1)
    vis = (z > 50) & (uv[:, 0] > -10) & (uv[:, 0] < W + 10) & (uv[:, 1] > -10) & (uv[:, 1] < H + 10)
    for (x, y), zz, wv in zip(uv[vis].astype(int), z[vis], wave[vis]):
        k = np.clip(1600 / zz, 0.3, 2.2)
        col = np.array(CYAN) * (0.18 + 0.82 * wv) * min(1.0, k)
        cv2.circle(lay, (x, y), max(1, int(1.6 * k)), col.tolist(), -1, cv2.LINE_AA)
    lay = _glow(lay, 2, 10, 0.6, 0.5)
    # ζ(1/2+it) 轨迹：琥珀色，逐段描出，穿过原点时闪一下
    tz = 6 + t / dur * 40
    m = _ZT <= tz
    sc, ox, oy = 175.0, W * 0.56, H * 0.50
    pts = np.c_[ox + _ZV.real[m] * sc, oy - _ZV.imag[m] * sc].astype(np.int32)
    zl = np.zeros((H, W, 3), np.float32)
    if len(pts) > 1:
        cv2.polylines(zl, [pts], False, AMBER, 3, cv2.LINE_AA)
        cv2.circle(zl, tuple(pts[-1]), 9, (255, 240, 210), -1, cv2.LINE_AA)
    for z0 in _ZEROS:
        if z0 <= tz:
            age = tz - z0; k = math.exp(-age * 0.25)
            cv2.circle(zl, (int(ox), int(oy)), int(10 + 60 * (1 - k)), (np.array(WHITE) * k).tolist(), 2, cv2.LINE_AA)
    cv2.line(zl, (int(ox - 380), int(oy)), (int(ox + 520), int(oy)), (60, 90, 130), 1, cv2.LINE_AA)
    cv2.line(zl, (int(ox), int(oy - 420)), (int(ox), int(oy + 420)), (60, 90, 130), 1, cv2.LINE_AA)
    zl = _glow(zl, 3, 16, 0.8, 0.7)
    f = base + lay + zl
    return zoom(f, 1.0 + 0.04 * t / dur, 0.55, 0.5)

# ================================================================ 2. 数字化工厂：等距线框装置 + 管道流动粒子 + 扫描面
def _cyl(cx, cz, r, y0, y1, n=40, rings=6):
    L = []
    a = np.linspace(0, 2 * np.pi, n)
    for y in np.linspace(y0, y1, rings): L.append(np.c_[cx + r * np.cos(a), np.full(n, y), cz + r * np.sin(a)])
    for k in range(8):
        aa = k * np.pi / 4; L.append(np.array([[cx + r * math.cos(aa), y0, cz + r * math.sin(aa)], [cx + r * math.cos(aa), y1, cz + r * math.sin(aa)]]))
    return L

def _sphere(cx, cy, cz, r, n=36):
    L = []; a = np.linspace(0, 2 * np.pi, n)
    for lat in np.linspace(-0.75, 0.75, 5) * np.pi / 2:
        L.append(np.c_[cx + r * math.cos(lat) * np.cos(a), np.full(n, cy - r * math.sin(lat)), cz + r * math.cos(lat) * np.sin(a)])
    for lon in np.linspace(0, np.pi, 5, endpoint=False):
        L.append(np.c_[cx + r * np.cos(a) * math.cos(lon), cy - r * np.sin(a), cz + r * np.cos(a) * math.sin(lon)])
    return L

def _build_factory():
    L = []
    for i in range(-6, 7):  # 地面网格（y 向下为正，地面 y=0）
        L.append(np.array([[i * 100, 0, -600], [i * 100, 0, 600]])); L.append(np.array([[-600, 0, i * 100], [600, 0, i * 100]]))
    eq = []
    L += _cyl(-330, -180, 55, 0, -520, rings=12); eq.append((-330, -520, -180))     # 精馏塔
    L += _cyl(-170, -260, 40, 0, -400, rings=10); eq.append((-170, -400, -260))
    L += _cyl(80, -140, 90, 0, -230, rings=6); L += _sphere(80, -230, -140, 90); eq.append((80, -320, -140))   # 反应釜
    L += _sphere(300, -150, 120, 140); eq.append((300, -290, 120))                  # 球罐
    L += [np.array(p) for p in ([[260, -60, -320], [460, -60, -320]],)]
    L += _cyl(-60, 220, 70, 0, -160, rings=5); eq.append((-60, -160, 220))
    pipes = [
        np.array([[-330, -480, -180], [-330, -560, -180], [-170, -560, -180], [-170, -560, -260], [-170, -380, -260]], float),
        np.array([[-170, -60, -260], [-170, -60, -140], [-10, -60, -140]], float),
        np.array([[80, -330, -140], [80, -420, -140], [300, -420, -140], [300, -300, 120]], float),
        np.array([[160, -40, -140], [240, -40, -140], [240, -40, 120], [180, -40, 120]], float),
        np.array([[-60, -150, 220], [-60, -300, 220], [-330, -300, 220], [-330, -300, -180]], float),
        np.array([[420, -40, 120], [520, -40, 120], [520, -40, -320], [-330, -40, -320], [-330, -40, -230]], float),
    ]
    return L, pipes

_FL, _PIPES = _build_factory()

def _along(path, u):
    seg = np.linalg.norm(np.diff(path, axis=0), axis=1); cum = np.r_[0, np.cumsum(seg)]; d = (u % 1.0) * cum[-1]
    i = min(np.searchsorted(cum, d) - 1, len(seg) - 1); i = max(i, 0); k = (d - cum[i]) / max(seg[i], 1e-6)
    return path[i] + (path[i + 1] - path[i]) * k

def digital_factory(t, dur=6.0, bgimg=None):
    base = bgimg.copy() if bgimg is not None else bg('deep', key='deep')
    R = _rot(math.radians(30), math.radians(35 + t * 4.5))
    cam = 1380 - t * 30
    lay = np.zeros((H, W, 3), np.float32)
    def P(arr):
        Q = (arr - np.array([95.0, 0.0, -50.0])) @ R.T; Q[:, 1] += 40
        return _proj(Q, cam, 1250, W / 2, H * 0.60)
    scan_y = lerp(20, -540, (t % 3.0) / 3.0)   # 扫描面从下往上
    for ln in _FL:
        uv, z = P(ln)
        if (z < 50).any(): continue
        depth = np.clip((z.mean() - cam + 700) / 1400, 0, 1)
        col = np.array(CYAN) * (1.0 - 0.65 * depth)
        if ln.shape[0] == 2 and ln[0, 1] == 0 and ln[1, 1] == 0: col = np.array((40, 90, 140)) * (1 - 0.5 * depth)
        near = np.exp(-((ln[:, 1].mean() - scan_y) / 40) ** 2)
        col = col + (np.array(WHITE) - col) * near * 0.6
        cv2.polylines(lay, [uv.astype(np.int32)], False, col.tolist(), 2, cv2.LINE_AA)
    pl = np.zeros((H, W, 3), np.float32)
    for pi, path in enumerate(_PIPES):
        uv, z = P(path)
        cv2.polylines(lay, [uv.astype(np.int32)], False, (70, 150, 210), 3, cv2.LINE_AA)
        for k in range(7):
            p = _along(path, t * 0.22 + k / 7 + pi * 0.13)
            q, zz = P(p[None, :])
            cv2.circle(pl, tuple(q[0].astype(int)), 5, AMBER, -1, cv2.LINE_AA)
    # 扫描面：一块半透明的水平光面
    sq = np.array([[-420, scan_y, -400], [580, scan_y, -400], [580, scan_y, 300], [-420, scan_y, 300]], float)
    uv, _ = P(sq); scan = np.zeros((H, W, 3), np.float32)
    cv2.fillConvexPoly(scan, uv.astype(np.int32), (np.array(CYAN) * 0.10).tolist(), cv2.LINE_AA)
    cv2.polylines(scan, [uv.astype(np.int32)], True, (np.array(CYAN) * 0.7).tolist(), 2, cv2.LINE_AA)
    f = base + _glow(lay, 2, 12, 0.7, 0.55) + _glow(pl, 3, 12, 1.0, 0.8) + cv2.GaussianBlur(scan, (0, 0), 2)
    return f

# ================================================================ 3. 蛋白质：3D 螺旋链（α 螺旋 + 折叠片 + 环），可从伸展态折叠
def _build_protein(seed=11, k=12):
    rng = np.random.default_rng(seed)
    # 二级结构单元：中心在球内，方向大致成束（相邻单元反平行）
    centers = []
    while len(centers) < k:
        c = rng.uniform(-1, 1, 3)
        if np.linalg.norm(c) < 1 and all(np.linalg.norm(c - q) > 0.55 for q in centers): centers.append(c)
    axis = rng.normal(0, 1, 3); axis /= np.linalg.norm(axis)
    pts, kinds = [], []
    prev_end, prev_dir = None, None
    for i, c in enumerate(centers):
        kind = 'helix' if rng.random() < 0.65 else 'strand'
        d = axis * (1 if i % 2 == 0 else -1) + rng.normal(0, 0.35, 3); d /= np.linalg.norm(d)
        a = np.cross(d, [0.3, 0.2, 0.9]); a /= np.linalg.norm(a); b = np.cross(d, a)
        if kind == 'helix':
            n = rng.integers(16, 24); L = n * 0.045
            seg_pts = [c + d * (j * 0.045 - L / 2) + (a * np.cos(j * 2 * np.pi / 3.6) + b * np.sin(j * 2 * np.pi / 3.6)) * 0.095 for j in range(n)]
        else:
            n = rng.integers(7, 10); L = n * 0.1
            seg_pts = [c + d * (j * 0.1 - L / 2) + a * (0.025 if j % 2 else -0.025) for j in range(n)]
        if prev_end is not None:   # 环：三次贝塞尔连接
            p0, p3 = prev_end, seg_pts[0]
            p1 = p0 + prev_dir * 0.22 + rng.normal(0, 0.1, 3); p2 = p3 - d * 0.22 + rng.normal(0, 0.1, 3)
            m = max(5, int(np.linalg.norm(p3 - p0) / 0.07))
            for u in np.linspace(0, 1, m + 2)[1:-1]:
                pts.append((1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1 + 3 * (1 - u) * u ** 2 * p2 + u ** 3 * p3); kinds.append('loop')
        pts += seg_pts; kinds += [kind] * len(seg_pts)
        prev_end, prev_dir = seg_pts[-1], d
    P = np.array(pts); P -= P.mean(0)
    return P / np.abs(P).max() * 430, kinds

_PROT, _PK = _build_protein()
_STRAIGHT = np.c_[np.linspace(-900, 900, len(_PROT)), 60 * np.sin(np.linspace(0, 9, len(_PROT))), np.zeros(len(_PROT))]
_PCOL = None

def _chain_colors(n):
    stops = [(0, BLUE), (0.4, CYAN), (0.75, (150, 230, 200)), (1.0, AMBER)]
    u = np.linspace(0, 1, n); c = np.zeros((n, 3))
    for k in range(3): c[:, k] = np.interp(u, [s[0] for s in stops], [s[1][k] for s in stops])
    return c

def protein(t, dur=6.0, fold=None, bgimg=None, cx=W / 2, cy=H / 2, scale=1.0, base=None):
    """fold: None=已折叠；(t0,t1)=在这段时间内从伸展态折叠"""
    f = base if base is not None else (bgimg.copy() if bgimg is not None else bg('deep', key='deep'))
    P = _PROT
    if fold:
        u = ease(seg(t, *fold)); P = _STRAIGHT * (1 - u) + _PROT * u
    R = _rot(math.radians(12), math.radians(t * 22), math.radians(4))
    Q = (P * scale) @ R.T
    uv, z = _proj(Q, 1350, 1350, cx, cy)
    cols = _chain_colors(len(P))
    order = np.argsort(-(z[:-1] + z[1:]))
    lay = np.zeros((H, W, 3), np.float32)
    for i in order:
        zz = (z[i] + z[i + 1]) / 2; k = np.clip(1350 / zz, 0.4, 2.0)
        shade = np.clip(1.25 - (zz - 950) / 900, 0.35, 1.15)
        w = max(2, int((14 if _PK[i] == 'helix' else 12 if _PK[i] == 'strand' else 6) * k))
        p0, p1 = tuple(uv[i].astype(int)), tuple(uv[i + 1].astype(int))
        cv2.line(lay, p0, p1, (cols[i] * shade * 0.55).tolist(), w + 4, cv2.LINE_AA)
        cv2.line(lay, p0, p1, (cols[i] * shade).tolist(), w, cv2.LINE_AA)
        cv2.line(lay, p0, p1, (np.minimum(cols[i] * shade + 90, 255)).tolist(), max(1, w // 4), cv2.LINE_AA)
    m = (lay.max(2, keepdims=True) > 0).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 1.2)[..., None]
    out = f * (1 - m * 0.92) + lay
    return out + cv2.GaussianBlur(lay, (0, 0), 16) * 0.35
