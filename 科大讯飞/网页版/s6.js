// 第 62–71 镜：回顾三张卡 → 不只是多懂知识 → 参与科研流程 → 1024 → 真实场景 → 五个场景 → 结尾
// 对应 代码/seg6_vis.py
'use strict';

// ------------------------------------------------------------------ 62 真人：身旁依次叠上三张回顾卡
VIS[62] = (ctx, t) => {
  host(1.0)(ctx, t);
  D.REV.forEach(([e, x, y, ang], j) => {
    const k = seg(t, EV[e] - 0.1, EV[e] + 0.25); if (k <= 0) return;
    const im = img('REV_C_' + j); if (!E.ready(im)) return; const [w, h] = E.sizeOf(im), ek = easeOut(k);
    E.persp(ctx, im, w, h, x + 60 * (1 - ek), y, { scale: 0.9 + 0.1 * ek, ry: -14, rz: ang, a: Math.min(1, k * 1.5), shadowK: 0.5, radius: 18 });
  });
};

// ------------------------------------------------------------------ 63–64 AI 徽章：书本飞进来 → 变灰；然后四步围成一个循环
function v6364(ctx, t) {
  bg(ctx, 'BG63'); const [cx, cy] = D.LC, LRX = D.LRX, LRY = D.LRY;
  const gray = ease(seg(t, lastVoice(63) - 0.7, lastVoice(63) - 0.2)) * (1 - ease(seg(t, EV.cut64, EV.cut64 + 0.4)));
  if (t < EV.cut64) {
    D.BOOK_P.forEach(([bx, by], j) => {
      const t0 = EV.more - 0.2 + 0.07 * j, u = seg(t, t0, t0 + 0.55); if (u <= 0 || u >= 1) return;
      const m = 1 - easeIn(u, 2);
      E.put(ctx, img('BOOKS_' + j), cx + bx * m, cy + by * m, Math.min(1, u * 4) * (1 - easeIn(u, 4)), 1 - 0.5 * u);
    });
    const kin = easeOut(seg(t, EV.cut63, EV.cut63 + 0.35)), pulse = Math.max(0, 1 - Math.abs(t - EV.more - 0.5) / 0.3);
    E.put(ctx, img('B_AI'), cx, cy, kin * (1 - gray), (0.85 + 0.15 * backOut(kin)) * (1 + 0.08 * pulse));
    E.put(ctx, img('B_AI_G'), cx, cy, kin * gray, 0.92);
  } else {
    const g = E.layer('loop');
    const pos = D.LOOP.map(([e, dx, dy]) => [cx + dx * LRX, cy + dy * LRY]), ts = D.LOOP.map(([e]) => EV[e] - 0.05);
    for (let k = 0; k < 4; k++) {                 // 弧线：亮了下一个才画到下一个
      const a0 = -Math.PI / 2 + k * Math.PI / 2 + 0.38, a1 = a0 + Math.PI / 2 - 0.76;
      const u = k < 3 ? ease(seg(t, ts[k + 1] - 0.25, ts[k + 1] + 0.1)) : ease(seg(t, ts[3] + 0.4, ts[3] + 0.9)); if (u <= 0) continue;
      const pts = []; for (let i = 0; i < 40; i++) { const a = a0 + (a1 - a0) * u * i / 39; pts.push([cx + LRX * Math.cos(a), cy + LRY * Math.sin(a)]); }
      E.line(g, pts, C.GOLD, 1, 4);
      if (u >= 1) {
        const tip = pts[39], p3 = pts[36]; let dx = tip[0] - p3[0], dy = tip[1] - p3[1]; const L = Math.hypot(dx, dy) + 1e-6; dx /= L; dy /= L; const nx = -dy, ny = dx;
        E.pathPoly(g, [[tip[0] + dx * 16, tip[1] + dy * 16], [tip[0] - dx * 14 + nx * 13, tip[1] - dy * 14 + ny * 13], [tip[0] - dx * 14 - nx * 13, tip[1] - dy * 14 - ny * 13]]);
        g.fillStyle = rgb(C.GOLD); g.fill();
      }
    }
    if (t > ts[3] + 0.9) for (let j = 0; j < 3; j++) {   // 循环转起来：金色光点绕圈
      const a = -Math.PI / 2 + (t - ts[3]) * 2.2 + j * 2 * Math.PI / 3; E.dot(g, cx + LRX * Math.cos(a), cy + LRY * Math.sin(a), 9, [255, 236, 190]);
    }
    E.addLayer(ctx, g, 1, [[6, 0.9]]);
    E.put(ctx, img('B_AI'), cx, cy, 1, 0.72 * (1 + 0.04 * Math.sin(t * 3)));
    pos.forEach(([x, y], j) => { const k = seg(t, ts[j], ts[j] + 0.3); E.put(ctx, img('LOOP_IM_' + j), x, y, 0.35 + 0.65 * easeOut(k), k > 0 ? 0.85 + 0.15 * backOut(k) : 0.85); });
  }
  pip2(ctx, t, easeOut(seg(t, EV.cut63, EV.cut63 + 0.4)), seg(t, lastVoice(64) - 0.35, lastVoice(64) - 0.05));
}
VIS[63] = v6364; VIS[64] = v6364;

// ------------------------------------------------------------------ 65 真人：「但它正在」处跳一次景别
VIS[65] = (ctx, t) => host(t < EV.but - 0.1 ? 1.0 : 1.12)(ctx, t);

// ------------------------------------------------------------------ 66 / 70 1024 活动页
VIS[66] = shot('IMG9', [40, 200, 1612, 730], [560, 250, 1080, 590], { rx: 4, ry: [-10, -6], maxk: 2.6, bgimg: 'BG9', rng_: () => [S[66].start, S[66].end] });
const F70 = shot('IMG9', [220, 350, 560, 530], [1090, 360, 1430, 520], { rx: 4, ry: [-8, -4], maxk: 2.4, bgimg: 'BG9', rng_: () => [S[70].start + 0.3, S[70].start + 5.6] });
VIS[70] = (ctx, t) => F70(ctx, clamp(t, S[70].start + 0.3, S[70].start + 5.6));

// ------------------------------------------------------------------ 67 真实场景：空镜 → 金属大字单独出现
const F67 = foot('v4', 60.0, 64.0, { speed: 0.9, dim: 0.95, sat: 0.6 });
VIS[67] = (ctx, t) => {
  const hit = EV.real;
  if (t < hit - 0.05) return F67(ctx, t, S[67].start, hit - S[67].start);
  const q = t - hit, u = seg(q, 0, 0.3); bg(ctx, 'BG67');
  E.put(ctx, E.sweep(img('T_REAL'), seg(q, 0.4, 1.4), 0.14, 1, 'sw_real'), W / 2, H / 2 - 20, easeOut(u, 2), (1.25 - 0.25 * easeOut(u, 4)) * (1 + 0.012 * q));
  E.flash(ctx, Math.max(0, 1 - q / 0.25) * 0.47);
  E.shake(ctx, Math.max(0, 1 - q / 0.35), Math.floor(t * 30));
};

// ------------------------------------------------------------------ 68 五个场景：随口播依次点亮，金线串起来，最后落到「生活」
VIS[68] = (ctx, t) => {
  E.zoomBegin(ctx, 1 + 0.03 * (t - S[68].start)); bg(ctx, 'BG67');
  const g = E.layer('scn'), P = D.SCN_P;
  for (let k = 0; k < 4; k++) {
    const u = ease(seg(t, EV.sc[k] + 0.1, EV.sc[k + 1])); if (u <= 0) continue;
    const [x0, y0] = P[k], [x1, y1] = P[k + 1], a = 0.36, b = 0.36 + 0.28 * u;
    E.line(g, [[x0 + (x1 - x0) * a, y0 + (y1 - y0) * a], [x0 + (x1 - x0) * b, y0 + (y1 - y0) * b]], C.GOLD, 1, 4);
  }
  E.addLayer(ctx, g, 1, [[6, 1]]);
  P.forEach(([x, y], k) => { const u = seg(t, EV.sc[k] - 0.05, EV.sc[k] + 0.25); if (u > 0) E.put(ctx, img('SCN_IM_' + k), x, y, easeOut(u), (0.8 + 0.2 * backOut(u)) * (k === 4 && u >= 1 ? 1.08 : 1)); });
  E.zoomEnd(ctx);
};

// ------------------------------------------------------------------ 69 使用它的人：人物空镜慢推；「着落」处一粒金光落下
const F69 = foot('v4', 70.5, 74.0, { speed: 0.8, push: 0.08, sat: 0.65 });
VIS[69] = (ctx, t) => {
  F69(ctx, t, S[69].start, S[69].dur);
  const u = seg(t, EV.land - 0.8, EV.land); if (u <= 0) return;
  const g = E.layer('land'), y = lerp(120, H / 2 + 40, easeOut(u, 2)), x = W / 2 + 120;
  if (u < 1) E.dot(g, x, y, 8, C.GOLD);
  else { const q = (t - EV.land) / 0.6; E.ring(g, x, y, 8 + 120 * easeOut(Math.min(1, q)), C.GOLD, Math.max(0, 1 - q), 3); }
  E.addLayer(ctx, g, 1, [[14, 1.2]]);
};

// ------------------------------------------------------------------ 71 真人 → 收尾画面（全程在动：光点上浮 + 片名扫光）
function endcard(ctx, t) {
  const q = t - EV.endcard; bg(ctx, 'BG67');
  const g = E.layer('end');
  for (const [x, y, s_, c] of D.END_DUST) {
    const px = x * W + 30 * Math.sin(q * 0.8 + c * 6), py = ((y * H - q * (25 + 60 * s_)) % H + H) % H;
    E.dot(g, px, py, 1 + Math.floor(3 * s_), c > 0.35 ? C.GOLD : C.ICE, 0.25 + 0.55 * s_);
  }
  E.addLayer(ctx, g, 1, [[5, 0.8]]);
  const u = easeOut(seg(q, 0, 0.6));
  E.put(ctx, E.sweep(img('T_AFS'), seg(q, 0.5, 1.8), 0.14, 1, 'sw_end'), W / 2, H / 2 - 10, u, (0.92 + 0.08 * u) * (1 + 0.02 * q));
}
VIS[71] = (ctx, t) => {
  host(t < EV.ordinary - 0.1 ? 1.06 : 1.0)(ctx, t);          // 说完即结束，不接收尾画面（endcard 保留备用）
};
