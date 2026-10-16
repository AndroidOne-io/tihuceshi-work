// 第 1–18 镜：冷开 → OpenAI Math → 719 篇 → 领域 → 含金量/ζ → 向内向外 → 参与创造知识 → 明珠 → 片名 → 转回国内
'use strict';

// ------------------------------------------------------------------ 冷开（hook.py）
const HK = D.hook;
function tunnel(g, t, speed, kCol = 1, streak = 1) {
  const fx = 900, n = HK.TU_A.length;
  for (let i = 0; i < n; i++) {
    let z = ((HK.TU_Z[i] - t * speed) % 6000 + 6000) % 6000 + 60;
    const zp = z + speed / 30 * 2.5 * streak; const a = HK.TU_A[i] + t * 0.15, r = HK.TU_R[i];
    const b = clamp(1.6 - z / 4000, 0, 1) * kCol; if (b <= 0.03) continue;
    const ca = Math.cos(a), sa = Math.sin(a);
    g.strokeStyle = rgb(HK.TU_C[i], b); g.lineWidth = z > 1500 ? 1 : z > 600 ? 2 : 3;
    g.beginPath(); g.moveTo(W / 2 + r * ca * fx / zp, H / 2 + r * sa * fx / zp); g.lineTo(W / 2 + r * ca * fx / z, H / 2 + r * sa * fx / z); g.stroke();
  }
}
function hook(ctx, t) {                          // t：以人声开始为 0；负数是黑场蓄力
  const hq = EV.human - EV.voice_in, ge = EV.boom - EV.voice_in;
  ctx.fillStyle = 'rgb(10,9,14)'; ctx.fillRect(0, 0, W, H);
  const g = E.layer('hook');
  if (t < 0) {
    const u = seg(t, -1.6, 0), L = 40 + 900 * easeIn(u, 3);
    E.line(g, [[W / 2 - L, H / 2], [W / 2 + L, H / 2]], [220, 200, 255], 0.3 + 0.7 * u, 2 + 3 * u);
    E.dot(g, W / 2, H / 2, 4 + 10 * u, [255, 255, 255]);
    tunnel(g, -t * 1.0, -900 * u, 0.35 * u, 0.5);
    E.addLayer(ctx, g, 1, [[3, 1.0], [16, 1.2]]); return;
  }
  if (t < hq + 0.2) {
    const sp = 5200 * (1 - 0.65 * ease(seg(t, hq - 0.5, hq + 0.2)));
    tunnel(g, t, sp, 1, 1);
    E.zoomBegin(ctx, 1 + 0.05 * Math.sin(t * 2)); E.addLayer(ctx, g, 1, [[3, 0.9], [16, 0.7]]); E.zoomEnd(ctx);
    E.flash(ctx, Math.max(0, 1 - t / 0.22)); return;
  }
  tunnel(g, t, 900, 0.45, 0.6);
  const u = ease(seg(t, hq, hq + 1.3)); let col = [150 * (0.6 + 0.4 * u), 150 * (0.6 + 0.4 * u), 170 * (0.6 + 0.4 * u)];
  const k = t - ge, boom = t >= ge;
  if (boom) {
    col = C.GOLD.map(v => v * (1.25 - 0.2 * Math.min(1, k)));
    E.ring(g, W / 2, H / 2, 60 + 1600 * easeOut(Math.min(1, k / 0.7)), C.GOLD, Math.max(0, 1 - k / 0.7), 6);
  }
  g.fillStyle = rgb(col);
  const ex = boom ? (1 - Math.exp(-k * 2.2)) * 0.9 : 0;
  for (let i = 0; i < HK.QP.length; i++) {
    let x, y;
    if (boom) { x = HK.QP[i][0] + HK.QV[i][0] * ex; y = HK.QP[i][1] + HK.QV[i][1] * ex + 160 * k * k; }
    else { x = HK.QS[i][0] * (1 - u) + HK.QP[i][0] * u; y = HK.QS[i][1] * (1 - u) + HK.QP[i][1] * u; }
    g.fillRect(W / 2 + x - 3, H / 2 + y - 3, 6, 6);
  }
  E.addLayer(ctx, g, 1, [[3, 0.8], [16, 0.9]]);
  if (boom) { E.flash(ctx, Math.max(0, 1 - k / 0.18) * 0.9); E.shake(ctx, Math.max(0, 1 - k / 0.6), Math.floor(t * 30)); E.glitch(ctx, Math.max(0, 0.8 - k / 0.4), Math.floor(t * 30)); }
}
VIS.hookPre = (ctx, t) => hook(ctx, t - EV.voice_in);
VIS[1] = (ctx, t) => hook(ctx, t - EV.voice_in);

// ------------------------------------------------------------------ 2–3 OpenAI Math 截图
const F2 = shot('IMG1', [150, 330, 2874, 1150], null, { rng_: [S[2].start, S[2].end] });
const F3a = shot('IMG1', [60, 1780, 2964, 2010], null, { hl: [560, 1800, 2964, 1990], rng_: [S[3].start, EV.split3] });
const F3b = shot('IMG2', [280, 360, 2120, 1000], [280, 700, 2120, 1560], { ry: [10, 4], rng_: [EV.split3, S[3].end] });
VIS[2] = F2;
VIS[3] = (ctx, t) => { if (t < EV.split3) F3a(ctx, t); else { F3b(ctx, t); E.whip(ctx, Math.max(0, 1 - (t - EV.split3) / 0.2)); } };

// ------------------------------------------------------------------ 4 / 7–8 719 篇论文 → 变金 → 冲进 ζ 函数
function papers(ctx, t) {
  const tl = t - EV.cut4;
  if (t >= EV.cut7) E.zoomBegin(ctx, 1 + 0.12 * ease(seg(t, EV.cut7, EV.dive)), 0.32, 0.55);
  bg(ctx, 'BG');
  E.put(ctx, img('GHOST'), W * 0.62, H * 0.52, 0.08 * easeOut(seg(tl, 0, 0.6)), 1 + 0.015 * Math.min(tl, 8));
  const gk = ease(seg(t, EV.gold, EV.gold + 0.5)), sweepX = lerp(D.PX - 400, D.PX + 400, seg(t, EV.gold, EV.gold + 0.5));
  D.DROPS.forEach(([dx, ang, t0, k], n) => {
    const u = seg(tl, t0 * 0.9, t0 * 0.9 + 0.45); if (u <= 0) return;
    const yy = lerp(-300, D.PY - n * 6, easeOut(u, 2)), xx = D.PX + dx * (1 - u) * 0.6 + dx * 0.08;
    E.put(ctx, img('PW_' + k), xx, yy, 1, 0.9, ang * (1 - 0.6 * u));
    if (gk > 0) E.put(ctx, img('PG_' + k), xx, yy, gk, 0.9, ang * (1 - 0.6 * u));
  });
  const sw = seg(t, EV.gold, EV.gold + 0.6);
  if (sw > 0 && sw < 1) { const g = E.layer('sw'); E.line(g, [[sweepX, 0], [sweepX - 200, H]], [255, 230, 170], 1, 50); E.addLayer(ctx, g, 0, [[30, 0.9]]); }
  if (gk > 0) {
    const g = E.layer('sp');
    for (const [a, r, s_] of D.SPARK) { const k = (t * 0.8 + s_) % 1; E.dot(g, D.PX + (a - 0.5) * 520, D.PY - 120 - k * 360 * (0.5 + r), 2 + 3 * r, C.GOLD, gk * (1 - k)); }
    E.addLayer(ctx, g, 1, [[6, 1]]);
  }
  const cnt = t > EV.land719 ? 719 : Math.floor(719 * easeOut(seg(tl, 0.15, 1.7), 2));
  E.number(ctx, String(cnt), W * 0.66, H * 0.46, 300, C.GOLD, easeOut(seg(tl, 0.1, 0.4)), 1 + 0.08 * Math.max(0, 1 - Math.abs(t - EV.land719) / 0.15));
  E.put(ctx, img('LBL'), W * 0.66 + 10, H * 0.46 + 190, easeOut(seg(tl, 0.5, 0.8)));
  if (t >= EV.cut7) E.zoomEnd(ctx);
}
VIS[4] = papers;

const ZETA = D.cosmos;
function mathCosmos(ctx, t, dur = 6) {
  const z = 1 + 0.04 * t / dur; E.zoomBegin(ctx, z, 0.55, 0.5);
  bg(ctx, 'BG_Z');
  const g = E.layer('cos');
  const ax = 58 * Math.PI / 180, az = (8 + t * 3) * Math.PI / 180, cx = Math.cos(ax), sx = Math.sin(ax), cz = Math.cos(az), sz = Math.sin(az), cam = 1500 - t * 40;
  for (let i = 0; i < ZETA.P.length; i++) {
    const X = ZETA.P[i][0], Y = ZETA.P[i][1];
    // R = Rz·Ry·Rx（ay=0）作用在 (X, Y, 0)
    const y1 = Y * cx, z1 = Y * sx; const x2 = X * cz - y1 * sz, y2 = X * sz + y1 * cz + 140;
    const zz = z1 + cam; if (zz <= 50) continue;
    const u = W / 2 + x2 * 1300 / zz, v = H / 2 + y2 * 1300 / zz; if (u < -10 || u > W + 10 || v < -10 || v > H + 10) continue;
    const k = clamp(1600 / zz, 0.3, 2.2), wave = clamp((t * 22 + 10 - ZETA.R[i]) / 12, 0, 1);
    E.dot(g, u, v, Math.max(1, 1.6 * k), C.CYAN, (0.18 + 0.82 * wave) * Math.min(1, k));
  }
  E.addLayer(ctx, g, 1, [[2, 0.6], [10, 0.5]]);
  const zl = E.layer('zeta'); const tz = 6 + t / dur * 40, sc = 175, ox = W * 0.56, oy = H * 0.5;
  E.line(zl, [[ox - 380, oy], [ox + 520, oy]], [60, 90, 130], 1, 1); E.line(zl, [[ox, oy - 420], [ox, oy + 420]], [60, 90, 130], 1, 1);
  const pts = []; for (const [zt, re, im] of ZETA.Z) { if (zt > tz) break; pts.push([ox + re * sc, oy - im * sc]); }
  if (pts.length > 1) { E.line(zl, pts, C.AMBER, 1, 3); const [hx, hy] = pts[pts.length - 1]; E.dot(zl, hx, hy, 9, [255, 240, 210]); }
  for (const z0 of ZETA.ZEROS) if (z0 <= tz) { const k = Math.exp(-(tz - z0) * 0.25); E.ring(zl, ox, oy, 10 + 60 * (1 - k), C.WHITE, k, 2); }
  E.addLayer(ctx, zl, 1, [[3, 0.8], [16, 0.7]]);
  E.zoomEnd(ctx);
}
function v78(ctx, t) {
  if (t < EV.dive) return papers(ctx, t);
  const k = t - EV.dive;
  if (k < 0.35) {
    E.zoomBegin(ctx, 1.12 + 6 * easeIn(k / 0.35, 3), 0.30, 0.50); papers(ctx, EV.dive); E.zoomEnd(ctx);
    E.flash(ctx, Math.pow(k / 0.35, 3)); E.whip(ctx, k / 0.35, false); return;
  }
  const tz = k - 0.35; mathCosmos(ctx, 2.5 + tz * 0.9, 6); E.flash(ctx, Math.max(0, 1 - tz / 0.2));
  E.put(ctx, img('B_RH'), W * 0.24, H * 0.34, easeOut(seg(tz, 0.4, 0.7)), 0.85 + 0.15 * backOut(seg(tz, 0.4, 0.8)));
  E.put(ctx, img('B_HG'), W * 0.27, H * 0.66, easeOut(seg(tz, 0.9, 1.2)), 0.85 + 0.15 * backOut(seg(tz, 0.9, 1.3)));
}
VIS[7] = v78; VIS[8] = v78;

// ------------------------------------------------------------------ 5 领域徽章摆在透视桌面上
function v5(ctx, t) {
  const tl = t - EV.cut5; const cw = 2200, chh = 1200; const c = E.tmp('table', cw, chh), g = c.getContext('2d');
  g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, cw, chh);
  D.FIELDS.forEach(([x, y], j) => {
    const k = seg(tl, D.BADGE_T[j] - EV.cut5, D.BADGE_T[j] - EV.cut5 + 0.35); if (k <= 0) return;
    E.put(g, img('FIMG_' + j), x, y, k, 0.6 + 0.4 * backOut(k));
  });
  bg(ctx, 'BG');
  const z = lerp(1.0, 1.08, ease(Math.min(1, tl / S[5].dur)));
  E.persp(ctx, c, cw, chh, W / 2, H * 0.55, { scale: z * 0.92, ry: -4, rx: 34, f: 1800, shadowK: 0, radius: 0, n: 8 });
}
VIS[5] = v5;

// ------------------------------------------------------------------ 真人 + 卡片
VIS[6] = host(1.06, [['LOCK', EV.lock, 1520, 420]]);
VIS[9] = host(1.0, [['NEQ_A', EV.neqA - 0.05, 1540, 330], ['NEQ', EV.neq - 0.05, 1540, 488], ['NEQ_B', EV.neqB - 0.05, 1540, 640]]);
VIS[12] = host(1.08); VIS[14] = host(1.0); VIS[16] = host(1.08);

// ------------------------------------------------------------------ 10–11 向内索取 / 向外延伸（知识圈 + 小窗）
function v1011(ctx, t) {
  bg(ctx, 'BG');
  const [KCx, KCy] = D.KC, KR = D.KR; const g = E.layer('kn');
  const u0 = easeOut(seg(t, EV.cut10, EV.cut10 + 0.5)), outk = ease(seg(t, EV.outward, EV.outward + 0.6));
  E.ring(g, KCx, KCy, KR * (0.9 + 0.1 * u0), [230, 236, 245], u0 * (1 - 0.45 * outk), 3);
  const tidy = ease(seg(t, EV.inward, EV.tidy + 0.6));
  D.KN.forEach(([a, rr], n) => {
    const ang = a * 2 * Math.PI + t * 0.12 * (1 - tidy), r0 = Math.sqrt(rr) * KR * 0.85;
    const x = (KCx + r0 * Math.cos(ang)) * (1 - tidy) + D.GRID[n][0] * tidy, y = (KCy + r0 * Math.sin(ang)) * (1 - tidy) + D.GRID[n][1] * tidy;
    E.dot(g, x, y, 4, C.ICE, u0 * (0.55 + 0.45 * tidy) * (1 - 0.4 * outk));
  });
  if (t >= EV.outward) {
    const k = seg(t, EV.outward, EV.outward + 0.5), a = -35 * Math.PI / 180, L = KR * (0.1 + 1.6 * easeOut(k));
    const p1 = [KCx + L * Math.cos(a), KCy + L * Math.sin(a)];
    E.line(g, [[KCx, KCy], p1], C.GOLD, 1, 6); E.dot(g, p1[0], p1[1], 11, [255, 245, 220]);
    const hit = seg(t, EV.outward + 0.25, EV.outward + 0.7);
    if (hit > 0 && hit < 1) E.ring(g, KCx + KR * Math.cos(a), KCy + KR * Math.sin(a), 20 + 120 * hit, C.WHITE, 1 - hit, 3);
  }
  if (t >= EV.rule - 0.3) {
    const k = seg(t, EV.rule - 0.3, EV.rule + 1.2), on = Math.floor(D.STARS.length * k);
    for (let j = 0; j < on; j++) { const [x, y] = D.STARS[j]; E.dot(g, x, y, 7, C.GOLD); if (j > 0) E.line(g, [D.STARS[j - 1], [x, y]], C.GOLD, 0.8, 2); }
  }
  E.addLayer(ctx, g, 1, [[4, 0.8], [18, 0.6]]);
  const ia = 1 - 0.7 * tidy;
  E.put(ctx, img('C_DOC'), KCx - 90, KCy, easeOut(seg(t, EV.doc - 0.1, EV.doc + 0.2)) * ia, 0.8 + 0.2 * backOut(seg(t, EV.doc - 0.1, EV.doc + 0.3)));
  E.put(ctx, img('C_LST'), KCx + 90, KCy, easeOut(seg(t, EV.lst - 0.1, EV.lst + 0.2)) * ia, 0.8 + 0.2 * backOut(seg(t, EV.lst - 0.1, EV.lst + 0.3)));
  E.put(ctx, img('W_IN'), KCx - 250, KCy - KR - 70, easeOut(seg(t, EV.inward, EV.inward + 0.3)) * (1 - 0.75 * outk));
  E.put(ctx, img('W_OUT'), KCx + 420, KCy - KR - 70, easeOut(seg(t, EV.outward + 0.3, EV.outward + 0.6)));
  pip2(ctx, t, easeOut(seg(t, EV.cut10, EV.cut10 + 0.4)), seg(t, lastVoice(11) - 0.35, lastVoice(11) - 0.05));
}
VIS[10] = v1011; VIS[11] = v1011;

// ------------------------------------------------------------------ 13 大字：使用知识 → 参与创造知识
function v13(ctx, t) {
  const hit = EV.create, sk = t >= hit ? Math.max(0, 1 - (t - hit) / 0.35) : 0;
  bg(ctx, 'BG'); const g = E.layer('dust');
  for (const [x, y, s_] of D.DUST) E.dot(g, x * W, ((y * H - t * 18 * (0.3 + s_)) % H + H) % H, 1 + 2 * s_, C.GOLD, 0.35 * s_);
  E.addLayer(ctx, g, 1, [[3, 1]]);
  const u1 = easeOut(seg(t, EV.use - 0.05, EV.use + 0.25)), back = easeIn(seg(t, hit - 0.35, hit - 0.05));
  E.put(ctx, img('T_USE'), W / 2, H / 2, u1 * (1 - back), 1 - 0.3 * back);
  if (t >= hit) {
    const u = seg(t, hit, hit + 0.25);
    E.put(ctx, E.sweep(img('T_CREATE'), seg(t, hit + 0.4, hit + 1.5)), W / 2, H / 2, easeOut(u, 2), (1.3 - 0.3 * easeOut(u, 4)) * (1 + 0.015 * (t - hit)));
    E.flash(ctx, Math.max(0, 1 - (t - hit) / 0.22) * 0.55); E.shake(ctx, sk, Math.floor(t * 30));
  }
}
VIS[13] = v13;

// ------------------------------------------------------------------ 15 表情包
VIS[15] = (ctx, t) => {
  const tl = t - EV.meme; bg(ctx, 'BG');
  const m = img('MEME'); if (E.ready(m)) { const c = E.tmp('meme'); const gg = c.getContext('2d'); gg.clearRect(0, 0, W, H); E.cover(gg, m, 0, 0, W, H); E.blurDraw(ctx, c, 30, 0, 0, W, H, 0.3); }
  const k = seg(tl, 0, 0.22);
  E.put(ctx, img('MEME_CARD'), W / 2, H / 2 - 30, k, (1.3 - 0.3 * backOut(k)) * (1 + 0.02 * tl), -4);
  E.shake(ctx, Math.max(0, 1 - tl / 0.4), Math.floor(tl * 30));
};

// ------------------------------------------------------------------ 17 片名 AI for Science（全息转盘空镜做景深）
VIS[17] = (ctx, t) => {
  const tl = t - S[17].start, hit = EV.afs;
  bg(ctx, 'BG'); E.fill(ctx, '#000', 0.45);
  const v = E.video('v4', 50 + tl * 0.6, 0.6);
  if (E.ready(v)) { const c = E.tmp('v17'); const gg = c.getContext('2d'); gg.globalCompositeOperation = 'source-over'; gg.globalAlpha = 1; E.cover(gg, v, 0, 0, W, H); E.grade(gg, 0, 0, W, H, 0.35, 1); E.blurDraw(ctx, c, 8, 0, 0, W, H, 0.55, 'lighter'); }
  const g = E.layer('afs'); const conv = easeIn(seg(t, hit - 1.2, hit), 2), fade = 1 - seg(t, hit - 0.05, hit + 0.25);
  for (const [a, r, s_] of D.PART) {
    const ang = a * 2 * Math.PI, rr = (0.25 + r) * W * 0.7 * (1 - conv) + 40 * s_;
    E.dot(g, W / 2 + rr * Math.cos(ang) * (0.6 + 0.4 * s_), H / 2 + rr * Math.sin(ang) * 0.55, 2 + 2 * s_, s_ > 0.4 ? C.GOLD : C.ICE, (0.5 + 0.5 * s_) * fade);
  }
  E.addLayer(ctx, g, 1, [[4, 1], [16, 0.6]]);
  if (t >= hit) {
    const u = seg(t, hit, hit + 0.3);
    E.put(ctx, E.sweep(img('T_AFS'), seg(t, hit + 0.5, hit + 1.7)), W / 2, H / 2, easeOut(u, 2), (1.25 - 0.25 * easeOut(u, 4)) * (1 + 0.012 * (t - hit)));
    E.flash(ctx, Math.max(0, 1 - (t - hit) / 0.3) * 0.63); E.shake(ctx, Math.max(0, 1 - (t - hit) / 0.4), Math.floor(t * 30));
  }
};

// ------------------------------------------------------------------ 18 真人 → 走廊空镜（停顿落在画面上）
VIS[18] = (ctx, t) => {
  if (t < EV.bridge) return host(1.06)(ctx, t);
  const k = t - EV.bridge; E.zoomBegin(ctx, 1 + 0.05 * k);
  E.cover(ctx, E.video('v4', 0.5 + k * 0.8, 0.8), 0, 0, W, H); E.grade(ctx, 0, 0, W, H, 0.5, 1); E.zoomEnd(ctx);
};
