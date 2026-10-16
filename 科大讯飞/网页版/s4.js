// 第 37–50 镜：讯飞 × 大连化物所 → 化工大模型 → 演示五步 → 400+ 工具 → 真人收束 → 「02 生物医药」
// 对应 代码/seg4_vis.py
'use strict';

// ------------------------------------------------------------------ 37 合作：两枚徽章从两侧滑入，在「合作」处扣上
VIS[37] = (ctx, t) => {
  const s = S[37], tl = t - s.start;
  E.zoomBegin(ctx, 1 + 0.03 * tl / s.dur);
  bg(ctx, 'BG37');
  const u = easeOut(seg(tl, 0, 0.7)), lk = ease(seg(t, EV.link - 0.35, EV.link));
  const gap = lerp(1560, 760, u) - 60 * lk, xl = W / 2 - gap / 2, xr = W / 2 + gap / 2, cy = H / 2 - 40;
  if (t >= EV.link - 0.3) {
    const g = E.layer('l37'), k = seg(t, EV.link - 0.3, EV.link), xa = xl + 225, xb = xr - 225, xm = (xa + xb) / 2;
    E.line(g, [[xm - (xm - xa) * k, cy], [xm + (xb - xm) * k, cy]], C.GOLD, 1, 5);
    if (t >= EV.link) {
      const q = t - EV.link;
      E.ring(g, xm, cy, 20 + 260 * easeOut(Math.min(1, q / 0.6)), C.GOLD, Math.max(0, 1 - q / 0.6), 3);
      const m = easeOut(Math.min(1, q / 0.8));
      for (const [a, b] of D.SP37) E.dot(g, xm + a * 180 * m, cy + b * 120 * m, 3, C.GOLD, Math.max(0, 1 - q / 1.2));
    }
    E.addLayer(ctx, g, 1, [[5, 1], [18, 0.6]]);
  }
  E.put(ctx, img('P_XF'), xl, cy, u, 0.9 + 0.1 * u);
  E.put(ctx, img('P_DL'), xr, cy, u, 0.9 + 0.1 * u);
  E.zoomEnd(ctx);
};

// ------------------------------------------------------------------ 38–39 模型简介：整页 → 推到标题 → 四个模块依次亮起
function shot5(ctx, t, box, s0, dur, o = {}) {
  const { hl = null, mods = false, ry = -10 } = o;
  const im = img('IMG5'); bg(ctx, 'BG5'); if (!E.ready(im)) return;
  const [iw, ih] = E.sizeOf(im), tl = t - s0, bw = box[2] - box[0], bh = box[3] - box[1];
  const s = Math.min(1560 / bw, 800 / bh, 2.3) * (0.94 + 0.06 * easeOut(Math.min(1, tl / 0.8)));
  const cw = iw * s, ch = ih * s, cxb = (box[0] + box[2]) / 2 * s, cyb = (box[1] + box[3]) / 2 * s;
  const M = E.persp(ctx, im, cw, ch, W / 2 + (cw / 2 - cxb), H / 2 - 30 + (ch / 2 - cyb), { ry: ry + 4 * ease(tl / dur), rx: 5, shadowK: 0.6 });
  E.dimExcept(ctx, M, cw, ch, box.map(v => v * s), 0.6);
  if (hl) { const [x0, y0, x1, y1] = E.bboxOf(E.quadOf(M, hl.map(v => v * s))); E.hlBar(ctx, x0, y0, x1, y1, seg(tl, 0.35, 0.9), C.GOLD, 0.40); }
  if (mods) {                                     // 模块没亮之前压暗，亮起时恢复原亮度 + 金边
    D.MODS.forEach((b, j) => {
      const t0 = EV.mods[j], k = easeOut(seg(t, t0, t0 + 0.25)), q = E.quadOf(M, b.map(v => v * s));
      ctx.save(); E.pathPoly(ctx, q);
      if (k < 1) { ctx.fillStyle = `rgba(0,0,0,${0.55 * (1 - k)})`; ctx.fill(); }
      if (k > 0) { ctx.strokeStyle = rgb(C.GOLD, 1, k); ctx.lineWidth = 6; ctx.lineJoin = 'round'; ctx.stroke(); }
      ctx.restore();
    });
  }
}
VIS[38] = (ctx, t) => {
  const s = S[38], u = ease(seg(t, s.start + 0.15, s.start + 1.3));
  const box = [40, 60, 1040, 540].map((a, k) => lerp(a, [375, 140, 705, 200][k], u));
  shot5(ctx, t, box, s.start, s.dur, { hl: u >= 1 ? [445, 155, 700, 192] : null });
};
VIS[39] = (ctx, t) => shot5(ctx, t, [150, 160, 935, 305], S[39].start, S[39].dur, { mods: true, ry: -6 });

// ------------------------------------------------------------------ 40–45 演示：录屏卡片 + 顶部五步流程徽章
// [录屏起, 录屏止, 裁切框, 只亮这块, 高亮条]（录屏原始像素 2634×1440）
const REC = {
  40: [0.9, 2.3, [720, 540, 2380, 990], [745, 585, 2350, 800], [750, 598, 1100, 636]],
  41: [28.0, 34.0, [720, 570, 2380, 1040], null, null],
  42: [16.0, 22.0, [740, 70, 2240, 990], null, null],
  43: [36.0, 96.0, [720, 570, 2380, 1040], null, null],
  44: [100.0, 134.0, [720, 30, 2380, 520], null, [740, 240, 1700, 360]],
  45: [136.0, 145.5, [500, 20, 2634, 1080], null, [530, 795, 1160, 900]],
};
function stepsRow(ctx, t) {
  const a = easeOut(seg(t, EV.cut41 - 0.1, EV.cut41 + 0.3)), dy = -160 * (1 - a), y = D.ST_Y + dy;
  const g = E.layer('steps');
  for (let k = 0; k < 4; k++) E.line(g, [[D.ST_X[k] + 156, y], [D.ST_X[k + 1] - 156, y]], t >= D.ST_T[k + 1] ? C.GOLD : [120, 122, 132], a, 3);
  E.addLayer(ctx, g, 1);
  for (let k = 0; k < 5; k++) {
    const on = t >= D.ST_T[k], done = k + 1 < 5 && t >= D.ST_T[k + 1];
    const name = (done ? 'ST_DONE_' : on ? 'ST_ON_' : 'ST_OFF_') + k;
    const pop = on && !done ? backOut(seg(t, D.ST_T[k], D.ST_T[k] + 0.3)) : 1;
    E.put(ctx, img(name), D.ST_X[k], y, a * (on ? 1 : 0.6), on && !done ? 0.86 + 0.14 * pop : 1);
  }
}
function vDemo(ctx, t) {
  const s = shotAt(t), i = s.i, tl = t - s.start; const [a, b, box, focus, hl] = REC[i];
  const bw = box[2] - box[0], bh = box[3] - box[1], top = i >= 41 ? 220 : 60;
  const sc = Math.min(1760 / bw, (H - top - 150) / bh), cw = bw * sc, ch = bh * sc, e = ease(tl / s.dur);
  bg(ctx, 'BG6');
  const v = E.video('v6', a + (b - a) * Math.min(1, tl / s.dur), (b - a) / s.dur);
  const M = E.persp(ctx, v, cw, ch, W / 2, top + (H - top - 150) / 2 + 10, { scale: 0.96 + 0.05 * e, ry: -8 + 4 * e, rx: 4, shadowK: 0.6, crop: [box[0], box[1], bw, bh] });
  const loc = r => [(r[0] - box[0]) * sc, (r[1] - box[1]) * sc, (r[2] - box[0]) * sc, (r[3] - box[1]) * sc];
  if (focus) E.dimExcept(ctx, M, cw, ch, loc(focus), 0.5);
  if (hl) { const t0 = i === 40 ? EV.req : s.start + 0.35; const [x0, y0, x1, y1] = E.bboxOf(E.quadOf(M, loc(hl))); E.hlBar(ctx, x0, y0, x1, y1, seg(t, t0, t0 + 0.5), C.GOLD, 0.38); }
  if (i >= 41) stepsRow(ctx, t);
}
for (let i = 40; i <= 45; i++) VIS[i] = vDemo;

// ------------------------------------------------------------------ 46–47 400+：工具墙一路拉远、一块块亮起 → 「400+」砸下来
// 墙的合成图（暗墙 + 已亮的格子）缓存在离屏画布上，只增量画新亮的格子；往回拖时整张重画
const WALL = { n: -1 };
function wallCanvas(nLit) {
  const dim = img('WALL_DIM'), lit = img('WALL_LIT'); if (!E.ready(dim) || !E.ready(lit)) return null;
  const ww = D.NC * D.GX, wh = D.NR * D.GY, c = E.tmp('wall', ww, wh), g = c.getContext('2d');
  if (nLit < WALL.n || WALL.n < 0) { g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.drawImage(dim, 0, 0, ww, wh); WALL.n = 0; }
  if (nLit > WALL.n) {
    const sx = lit.naturalWidth / ww, sy = lit.naturalHeight / wh;
    for (let r = 0; r < D.NR; r++) for (let cc = 0; cc < D.NC; cc++) {
      const o = D.LIT_ORDER[r][cc]; if (o < WALL.n || o >= nLit) continue;
      g.drawImage(lit, cc * D.GX * sx, r * D.GY * sy, D.GX * sx, D.GY * sy, cc * D.GX, r * D.GY, D.GX, D.GY);
    }
    WALL.n = nLit;
  }
  return c;
}
function v47(ctx, t) {
  const s0 = EV.cut46, hit = EV.n400;
  const z = lerp(1.25, 0.26, ease(seg(t, s0, hit))) * (1 - 0.03 * Math.max(0, t - hit));
  bg(ctx, 'BG47');
  const nLit = Math.floor(D.NC * D.NR * easeIn(seg(t, s0 + 0.2, hit), 1.6));
  const wc = wallCanvas(nLit);
  if (wc) {
    const ww = wc.width, wh = wc.height, q = E.projQuad(ww, wh, W / 2, H / 2 + 30, z, -6, 22);
    const M = E.solveH([[0, 0], [ww, 0], [ww, wh], [0, wh]], q);
    E.drawWarped(ctx, wc, [0, 0, ww, wh], ww, wh, M, 14, 0, 1);
  }
  if (t >= hit) {
    const q = t - hit;
    E.fill(ctx, '#000', 0.62 * easeOut(Math.min(1, q / 0.25)));
    const sn = E.tmp('snap47'), sg = sn.getContext('2d'); sg.setTransform(1, 0, 0, 1, 0, 0); sg.globalAlpha = 1; sg.globalCompositeOperation = 'copy'; sg.drawImage(ctx.canvas, 0, 0); sg.globalCompositeOperation = 'source-over';
    E.blurDraw(ctx, sn, 1 + 5 * easeOut(Math.min(1, q / 0.3)) * 1.6);
    const g = E.layer('r400'); E.ring(g, W / 2, H / 2, 80 + 1200 * easeOut(Math.min(1, q / 0.7)), C.GOLD, Math.max(0, 1 - q / 0.7), 5);
    E.addLayer(ctx, g, 1, [[10, 1]]);
    const u = seg(q, 0, 0.22);
    E.put(ctx, img('N400'), W / 2, H / 2 - 20, easeOut(u, 2), (1.45 - 0.45 * easeOut(u, 4)) * (1 + 0.015 * q));
    E.flash(ctx, Math.max(0, 1 - q / 0.18) * 0.47);
    E.shake(ctx, Math.max(0, 1 - q / 0.4), Math.floor(t * 30));
  }
}
VIS[46] = v47; VIS[47] = v47;

// ------------------------------------------------------------------ 48 工具库录屏
function rec7(a, b, box, hl) {
  return (ctx, t) => {
    const s = shotAt(t), tl = t - s.start, e = ease(tl / s.dur), bw = box[2] - box[0], bh = box[3] - box[1];
    const sc = Math.min(1700 / bw, 880 / bh), cw = bw * sc, ch = bh * sc;
    bg(ctx, 'BG7');
    const v = E.video('v7', a + (b - a) * Math.min(1, tl / s.dur), (b - a) / s.dur);
    const M = E.persp(ctx, v, cw, ch, W / 2, H / 2 - 20, { scale: 0.97 + 0.06 * e, ry: -12 + 5 * e, rx: 6, shadowK: 0.6, crop: [box[0], box[1], bw, bh] });
    if (hl) { const [x0, y0, x1, y1] = E.bboxOf(E.quadOf(M, [(hl[0] - box[0]) * sc, (hl[1] - box[1]) * sc, (hl[2] - box[0]) * sc, (hl[3] - box[1]) * sc])); E.hlBar(ctx, x0, y0, x1, y1, seg(tl, 0.3, 0.9), C.GOLD, 0.35); }
  };
}
VIS[48] = rec7(10.0, 13.0, [510, 30, 2620, 1080], [520, 205, 1640, 275]);

// ------------------------------------------------------------------ 49–50 真人：身旁依次换三张画面卡（数字工厂 → 方案表 → 实验）
function sideCard(ctx, src, cx, cy, a, w = 640) {
  if (a <= 0) return; const ea = easeOut(a);
  E.persp(ctx, src, w, w * 9 / 16, cx + 60 * (1 - ea), cy, { scale: 0.92 + 0.08 * ea, ry: -14, rx: 3, a: Math.min(1, a * 1.5), shadowK: 0.55, radius: 20, border: 3, borderCol: 'rgb(225,228,236)' });
}
function v4950(ctx, t) {
  host(1.0)(ctx, t);
  const k1 = seg(t, EV.digi - 0.1, EV.digi + 0.25), k2 = seg(t, EV.early - 0.1, EV.early + 0.25), k3 = seg(t, EV.labv - 0.1, EV.labv + 0.25);
  if (k1 > 0 && k2 < 1) sideCard(ctx, digitalFactory(1.0 + (t - EV.digi) * 0.8, 'fac49'), 1490, 420, k1 * (1 - k2));
  if (k2 > 0 && k3 < 1) sideCard(ctx, coverCanvas('rectbl', img('REC_TBL'), 640, 360), 1490, 420, k2 * (1 - k3));
  if (k3 > 0) sideCard(ctx, coverCanvas('lab49', E.video('v11', 225.0 + (t - EV.labv) * 0.8, 0.8), 640, 360, { sat: 0.8, warm: true }), 1490, 420, k3);
}
VIS[49] = v4950;
VIS[50] = (ctx, t) => t < EV.ch2_in ? v4950(ctx, t) : chapter(ctx, t, EV.ch2_in, EV.cut51, 'v10', 1.0, 'CH2');
