// 第 19–36 镜：国内科研 → 01 化工研发 → 实验室到工厂 → 调参数 → 每多试一次 → 死亡之谷
'use strict';

// ------------------------------------------------------------------ 代码画的数字工厂（kongjing.digital_factory）
const FAC = D.factory;
function rotXY(ax, ay) { const cx = Math.cos(ax), sx = Math.sin(ax), cy = Math.cos(ay), sy = Math.sin(ay); return p => { const y1 = p[1] * cx - p[2] * sx, z1 = p[1] * sx + p[2] * cx; return [p[0] * cy + z1 * sy, y1, -p[0] * sy + z1 * cy]; }; }
function digitalFactory(t, key = 'fac') {        // 画到离屏画布并返回（1920×1080）
  const c = E.tmp(key); const ctx = c.getContext('2d'); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  bg(ctx, 'BG_Z');
  const R = rotXY(30 * Math.PI / 180, (35 + t * 4.5) * Math.PI / 180), cam = 1380 - t * 30;
  const P = p => { const q = R([p[0] - 95, p[1], p[2] + 50]); q[1] += 40; const z = q[2] + cam; return [W / 2 + q[0] * 1250 / z, H * 0.6 + q[1] * 1250 / z, z]; };
  const scanY = lerp(20, -540, (t % 3) / 3);
  const g = E.layer('fac1'), pl = E.layer('fac2'), sc = E.layer('fac3');
  for (const ln of FAC.L) {
    const pr = ln.map(P); if (pr.some(p => p[2] < 50)) continue;
    const zm = pr.reduce((a, p) => a + p[2], 0) / pr.length, depth = clamp((zm - cam + 700) / 1400, 0, 1);
    let col = C.CYAN.map(v => v * (1 - 0.65 * depth));
    if (ln.length === 2 && ln[0][1] === 0 && ln[1][1] === 0) col = [40, 90, 140].map(v => v * (1 - 0.5 * depth));
    const ym = ln.reduce((a, p) => a + p[1], 0) / ln.length, near = Math.exp(-Math.pow((ym - scanY) / 40, 2));
    col = col.map((v, i) => v + (C.WHITE[i] - v) * near * 0.6);
    E.line(g, pr, col, 1, 2);
  }
  FAC.PIPES.forEach((path, pi) => {
    E.line(g, path.map(P), [70, 150, 210], 1, 3);
    const segs = []; let tot = 0; for (let i = 0; i < path.length - 1; i++) { const d = Math.hypot(...[0, 1, 2].map(k => path[i + 1][k] - path[i][k])); segs.push(d); tot += d; }
    for (let k = 0; k < 7; k++) {
      let d = (((t * 0.22 + k / 7 + pi * 0.13) % 1) + 1) % 1 * tot, i = 0; while (i < segs.length - 1 && d > segs[i]) { d -= segs[i]; i++; }
      const u = d / Math.max(segs[i], 1e-6), p = [0, 1, 2].map(j => path[i][j] + (path[i + 1][j] - path[i][j]) * u), q = P(p);
      E.dot(pl, q[0], q[1], 5, C.AMBER);
    }
  });
  const sq = [[-420, scanY, -400], [580, scanY, -400], [580, scanY, 300], [-420, scanY, 300]].map(P);
  E.pathPoly(sc, sq); sc.fillStyle = rgb(C.CYAN, 0.1); sc.fill(); sc.strokeStyle = rgb(C.CYAN, 0.7); sc.lineWidth = 2; sc.stroke();
  E.addLayer(ctx, g, 1, [[2, 0.7], [12, 0.55]]); E.addLayer(ctx, pl, 1, [[3, 1.0], [12, 0.8]]); E.addLayer(ctx, sc, 0, [[2, 1]]);
  return c;
}

// ------------------------------------------------------------------ 19–24 国内科研：空镜 + 三类机构徽章
VIS[19] = shotfn(19, foot('v4', 27.5, 30.7)); VIS[20] = shotfn(20, foot('v4', 35.7, 39.5)); VIS[21] = shotfn(21, foot('v4', 59.1, 63.0));
const F22 = foot('v4', 12.7, 15.9, { dim: 0.55 });
const ENT = [['科研院所', 640], ['高校', 960], ['科技企业', 1280]];
const wtT = (i, k) => S[i].chars[k];               // 第 i 镜第 k 个字的时间
const ENT_T = (() => { const s = S[22]; const txt = s.text; const idx = w => { const pre = txt.slice(0, txt.indexOf(w)); return (pre.match(/[一-鿿]|[A-Za-z]+|\d+(?:\.\d+)?/g) || []).length; }; return ENT.map(([w]) => s.chars[idx(w)]); })();
VIS[22] = (ctx, t) => {
  F22(ctx, t, S[22].start, S[22].dur);
  ENT.forEach(([w, x], j) => { const t0 = ENT_T[j] - 0.05, k = seg(t, t0, t0 + 0.3); if (k > 0) E.put(ctx, img('ENT_IMG_' + j), x, H / 2 - 30, k, 0.7 + 0.3 * backOut(k)); });
};
VIS[23] = shotfn(23, foot('v4', 0.0, 5.0, { speed: 1.0, push: 0.1 })); VIS[24] = shotfn(24, foot('v4', 18.7, 23.3));

// ------------------------------------------------------------------ 25 问句 → 停顿落在「01 化工研发」章节卡
function chapter(ctx, t, tin, tout, vkey, vstart, card) {
  const k = t - tin;
  E.cover(ctx, E.video(vkey, vstart + k * 0.8, 0.8), 0, 0, W, H); E.grade(ctx, 0, 0, W, H, 0.6, 0.45);
  const out = easeIn(seg(t, tout - 0.25, tout), 2);
  E.put(ctx, img(card), W / 2, H / 2 - 20, easeOut(seg(k, 0, 0.3)) * (1 - out), (0.85 + 0.15 * backOut(seg(k, 0, 0.4))) * (1 + 0.6 * out));
}
VIS[25] = (ctx, t) => t < EV.ch_in ? host(1.06)(ctx, t) : chapter(ctx, t, EV.ch_in, EV.cut26, 'v11', 3.0, 'CH');
VIS[26] = shotfn(26, foot('v11', 2.0, 25.6, { speed: 2.0 })); VIS[27] = shotfn(27, foot('v11', 77.7, 83.5));

// ------------------------------------------------------------------ 28–29 实验室 → 工厂：分屏 + 金色粒子流
function v2829(ctx, t) {
  bg(ctx, 'BG'); const s28 = S[28].start, s29 = S[29].start; const split = ease(seg(t, s29 - 0.15, s29 + 0.45));
  const wl = lerp(1680, 780, split), hl = wl * 9 / 16;
  const lab = E.video('v11', 222.9 + (t - s28) * 1.2, 1.2);
  if (E.ready(lab)) {                          // 先把视频按 16:9 裁好、调色，再做成卡片
    const c = E.tmp('lab', 1600, 900), g = c.getContext('2d'); E.cover(g, lab, 0, 0, 1600, 900); E.grade(g, 0, 0, 1600, 900, 0.75, 1);
    E.persp(ctx, c, wl, hl, lerp(W / 2, W * 0.25, split), H / 2 - 20, { ry: lerp(0, 8, split), shadowK: 0.5 });
  }
  if (split > 0) {
    const fac = digitalFactory(2.0 + (t - s29));
    E.persp(ctx, fac, 780, 780 * 9 / 16, lerp(W + 500, W * 0.75, split), H / 2 - 20, { ry: -8, a: split, shadowK: 0.5 });
    const g = E.layer('flow'); const x0 = W * 0.25 + 395, x1 = W * 0.75 - 395, y = H / 2 - 20, xe = lerp(x0, x1, split);
    E.line(g, [[x0, y], [xe, y]], C.GOLD, 0.8, 4); const L = (xe - x0) * 0.25;
    E.line(g, [[xe - L * 0.7, y - L * 0.45], [xe, y], [xe - L * 0.7, y + L * 0.45]], C.GOLD, 0.8, 4);
    for (const [a, r] of D.PFLOW) { const u = (t * 0.6 + a) % 1; E.dot(g, lerp(x0, x1, u), y + (r - 0.5) * 60, 4, C.GOLD, split); }
    E.addLayer(ctx, g, 1, [[6, 1]]);
    E.put(ctx, img('FAC_TAG'), W * 0.75, H / 2 + 240, easeOut(seg(t, s29 + 0.3, s29 + 0.6)));
  }
  E.put(ctx, img('LAB_TAG'), W * 0.25, H / 2 + 240, easeOut(seg(t, s29 + 0.2, s29 + 0.5)));
}
VIS[28] = v2829; VIS[29] = v2829;
VIS[30] = shotfn(30, foot('v11', 133.3, 148.2, { speed: 2.0 }));
VIS[31] = shotfn(31, foot('v11', 38.0, 50.5, { speed: 2.0 }), foot('v11', 26.0, 37.7, { speed: 2.0 }));

// ------------------------------------------------------------------ 32 调参数：半透明滑杆
const F32 = foot('v11', 84.0, 102.4, { dim: 0.8 });
VIS[32] = (ctx, t) => {
  F32(ctx, t, S[32].start, S[32].dur); const tl = t - S[32].start; const px = 1220, py = 200, pw = 560, ph = 600;
  ctx.fillStyle = rgb(C.INK, 1, 0.55); ctx.fillRect(px, py, pw, ph);
  const g = E.layer('sl'); g.strokeStyle = 'rgb(120,120,130)'; g.lineWidth = 2; g.strokeRect(px, py, pw, ph);
  [C.GOLD, C.ICE, C.CORAL, C.MINT].forEach((col, k) => {
    const y = py + 105 + k * 130; E.line(g, [[px + 50, y], [px + pw - 50, y]], [90, 92, 100], 1, 9);
    const v = 0.5 + 0.35 * Math.sin(tl * (2.2 + k * 0.7) + k * 1.3), x = px + 50 + (pw - 100) * v;
    E.line(g, [[px + 50, y], [x, y]], col, 1, 9); E.dot(g, x, y, 19, [245, 245, 250]);
  });
  E.addLayer(ctx, g, easeOut(seg(tl, 0, 0.3)), [[4, 0.4 * easeOut(seg(tl, 0, 0.3))]]);
};

// ------------------------------------------------------------------ 33–34 每多试一次：次数往上跳，资源条往下掉
const F3334 = foot('v11', 149.0, 162.3, { dim: 0.4 });
const RES = [C.GOLD, C.ICE, C.CORAL];
function v3334(ctx, t) {
  const s33 = S[33].start; F3334(ctx, t, s33, S[33].dur + S[34].dur);
  const tl = t - s33, n = Math.min(9, 1 + Math.floor(Math.max(0, tl) / 0.55));
  E.put(ctx, img('TRY'), 420, 330); E.number(ctx, String(n), 560, 320, 230, C.GOLD, 1, 1 + 0.12 * Math.max(0, 1 - ((tl % 0.55) / 0.12))); E.put(ctx, img('TRY2'), 700, 330);
  RES.forEach((c, k) => {
    const y = 560 + k * 150, t0 = S[34].start - 0.1 + k * 0.25, a = easeOut(seg(t, t0, t0 + 0.3));
    E.put(ctx, img('RES_IC_' + k), 330, y, a, 0.8); E.put(ctx, img('RES_T_' + k), 470, y, a);
    const lvl = Math.max(0.08, 1 - 0.1 * (n - 1) - 0.05 * k);
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = 'rgb(60,62,70)'; ctx.fillRect(570, y - 20, 930, 40);
    ctx.fillStyle = rgb(c, a); ctx.fillRect(570, y - 20, 930 * lvl, 40); ctx.restore();
  });
}
VIS[33] = v3334; VIS[34] = v3334; VIS[35] = host(1.0);

// ------------------------------------------------------------------ 36 死亡之谷：曲线栽进谷底 → 毛笔大字
const VX = [], VY = []; for (let i = 0; i < 600; i++) { const x = 260 + 1400 * i / 599, u = (x - 260) / 1400; VX.push(x); VY.push(360 + 40 * u + 470 * Math.exp(-Math.pow((u - 0.52) / 0.11, 2)) - 160 * clamp((u - 0.7) / 0.3, 0, 1)); }
const VYMAX = Math.max(...VY);
VIS[36] = (ctx, t) => {
  const s = S[36].start, hit = EV.valley;
  bg(ctx, 'BG_VALLEY');
  const draw = ease(seg(t, s + 0.2, EV.fall + 0.35)), n = Math.max(2, Math.floor(600 * draw));
  const g = E.layer('vy'); g.lineWidth = 6; g.lineCap = 'round';
  for (let i = 1; i < n; i++) { const dip = Math.max(0, (VY[i] - 420) / 400); g.strokeStyle = rgb(C.ICE.map((v, k) => v * (1 - dip) + C.CORAL[k] * dip)); g.beginPath(); g.moveTo(VX[i - 1], VY[i - 1]); g.lineTo(VX[i], VY[i]); g.stroke(); }
  E.dot(g, VX[n - 1], VY[n - 1], 12, [255, 245, 230]);
  if (t > EV.fall) { const k = seg(t, EV.fall, EV.fall + 0.4); E.ring(g, VX[Math.floor(600 * 0.52)], VYMAX, 30 + 70 * k, C.CORAL, 1 - 0.5 * k, 3); }
  E.addLayer(ctx, g, 1, [[4, 0.8], [16, 0.5]]);
  E.put(ctx, img('B_LAB'), 240, 350, easeOut(seg(t, s, s + 0.3)));
  E.put(ctx, img('B_FAC'), 1690, VY[599] - 10, easeOut(seg(t, s + 2.0, s + 2.3)) * 0.7);
  if (t > EV.fall && t < EV.fall + 0.45) E.shake(ctx, 1 - seg(t, EV.fall, EV.fall + 0.45), Math.floor(t * 30));
  if (t >= hit) {
    E.fill(ctx, '#000', 0.65 * ease(seg(t, hit - 0.15, hit + 0.1)));
    const u2 = seg(t, hit, hit + 0.25);
    E.put(ctx, img('T_VALLEY'), W / 2, H / 2, easeOut(u2, 2), (1.3 - 0.3 * easeOut(u2, 4)) * (1 + 0.012 * (t - hit)));
    const gk = Math.max(0, 1 - (t - hit) / 0.35); E.glitch(ctx, gk, Math.floor(t * 30)); E.shake(ctx, gk, Math.floor(t * 31));
  }
};
