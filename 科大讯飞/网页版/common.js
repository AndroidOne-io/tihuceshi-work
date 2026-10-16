// 本片共用：时间线查询、真人出镜、小窗、空镜镜头、截图镜头、整帧合成 frame(t)
'use strict';
const { W, H, seg, lerp, ease, easeOut, easeIn, backOut, clamp, rgb } = E;
const EV = D.EV, PRE = D.PRE;
const C = {                                     // 颜色（与 v4.py / kx.py 一致）
  GOLD: [236, 198, 122], AMBER: [255, 168, 80], ICE: [150, 208, 255], CORAL: [255, 112, 92], MINT: [112, 226, 196], LILAC: [196, 160, 255],
  SAPPHIRE: [70, 126, 238], TEAL: [34, 172, 170], EMERALD: [48, 172, 112], VIOLET: [140, 104, 232], ROSE: [232, 92, 120], INK: [20, 22, 28],
  CYAN: [46, 211, 255], BLUE: [64, 112, 255], WHITE: [242, 245, 250], SKY: [120, 190, 255], CRIMSON: [220, 60, 80],
};
const VIS = {};                                 // 镜号 → (ctx, t) 画面函数
const S = {}; D.shots.forEach(s => { s.dur = s.end - s.start; S[s.i] = s; });
const shotAt = t => D.shots.find(s => s.start <= t && t < s.end) || D.shots[D.shots.length - 1];
const lastVoice = i => S[i].chars[S[i].chars.length - 1] + 0.35;
const img = n => E.img(n);

E.setVideoSources(/[?&]proxy\b/.test(location.search)          // ?proxy：用 _proxy/ 里的 webm（测试用浏览器不支持 H.264 时）
  ? { v4: '_proxy/v4.webm', v6: '_proxy/v6.webm', v7: '_proxy/v7.webm', v10: '_proxy/v10.webm', v11: '_proxy/v11.webm', cam: '_proxy/cam.webm' }
  : { v4: '../素材/4.空镜.mp4', v6: '../素材/6.演示录屏.mp4', v7: '../素材/7.400种.mp4',
      v10: '../素材/10.生物.mp4', v11: '../素材/11.化学.mp4', cam: '../素材/口播/1080-压缩版.mp4' });

// ------------------------------------------------------------------ 真人出镜（原片镜像录的，水平翻回）
function srcAt(t) {                             // 成片时间线 → 出镜原片时间（含提速）
  let best = null;
  for (const [a0, a1, o, k] of D.cam) {
    const L = (a1 - a0) / k;
    if (o <= t && t <= o + L) return [a0 + (t - o) * k, k];
    const d = Math.min(Math.abs(t - o), Math.abs(t - o - L));
    if (!best || d < best[0]) best = [d, t < o ? a0 : a1];
  }
  return [best ? best[1] : 0, 0];
}
function camFrame(ctx, t, x, y, w, h, fx = 0.5, fy = 0.35, headShoulders = false) {   // 把出镜画面（翻转后）铺满 (x,y,w,h)
  const [ts, k] = srcAt(t); const v = E.video('cam', ts, k);
  if (!E.ready(v)) { ctx.fillStyle = '#222'; ctx.fillRect(x, y, w, h); return; }
  ctx.save(); ctx.translate(x + w, y); ctx.scale(-1, 1);
  if (headShoulders) {
    const side = Math.floor(Math.min(v.videoHeight * 0.66, v.videoWidth));
    const sx = Math.floor((v.videoWidth - side) / 2), sy = Math.floor(v.videoHeight * 0.035);
    ctx.drawImage(v, sx, sy, side, side, 0, 0, w, h);
  } else E.cover(ctx, v, 0, 0, w, h, 1 - fx, fy);
  ctx.restore();
}
function host(z0 = 1.0, cards = []) {
  return (ctx, t) => {
    const s = shotAt(t), tl = t - s.start;
    E.zoomBegin(ctx, z0 + 0.03 * tl / s.dur, 0.5, 0.35); camFrame(ctx, t, 0, 0, W, H); E.zoomEnd(ctx);
    for (const [im, t0, x, y] of cards) { const k = seg(t, t0, t0 + 0.3); if (k > 0) E.put(ctx, img(im), x + 40 * (1 - easeOut(k)), y, k); }
  };
}
function pip2(ctx, t, u = 1, out = 0, cx = 220, cy = H - 260, d = 240) {   // 左下角圆形小窗
  if (u <= 0 || out >= 1) return;
  const d2 = d * backOut(u) * (1 - easeIn(out, 2)); if (d2 < 8) return;
  ctx.save();
  ctx.shadowColor = 'rgba(0,0,0,0.65)'; ctx.shadowBlur = 32; ctx.shadowOffsetY = 8;
  ctx.beginPath(); ctx.arc(cx, cy, d2 / 2 + 4, 0, Math.PI * 2); ctx.fillStyle = 'rgba(255,255,255,0.86)'; ctx.fill();
  ctx.shadowColor = 'transparent';
  ctx.beginPath(); ctx.arc(cx, cy, d2 / 2, 0, Math.PI * 2); ctx.clip();
  camFrame(ctx, t, cx - d2 / 2, cy - d2 / 2, d2, d2, 0.5, 0.32, true);
  ctx.restore();
}

// ------------------------------------------------------------------ 空镜镜头（对应 seg3 的 foot / shotfn）
function foot(vkey, a, b, o = {}) {
  const { speed = 1.4, push = 0.06, dim = 1.0, sat = 0.75, slot = 0 } = o;
  return (ctx, t, t0, dur) => {
    const u = t - t0; const raw = a + u * speed; const st = Math.min(raw, b - 0.05);
    E.zoomBegin(ctx, 1 + push * u / Math.max(dur, 0.1), 0.5, 0.5);
    const v = E.video(vkey, st, raw < b - 0.05 ? speed : 0, slot); E.cover(ctx, v, 0, 0, W, H); E.grade(ctx, 0, 0, W, H, sat, dim);
    E.zoomEnd(ctx);
  };
}
function shotfn(i, ...clips) {                  // 一个镜头里平均切几段素材
  return (ctx, t) => { const s = S[i], n = clips.length; const k = Math.min(Math.floor((t - s.start) / s.dur * n), n - 1), d = s.dur / n; clips[k](ctx, t, s.start + k * d, d); };
}
// 把图片/视频等比裁切铺满成 w×h 的离屏画布（可调色），用来做透视卡片的源（对应 Python 的 card(cover(...))）
function coverCanvas(key, src, w, h, o = {}) {
  const { sat = 1, dim = 1, warm = false, fx = 0.5, fy = 0.5, crop = null } = o;
  const c = E.tmp(key, w, h), g = c.getContext('2d'); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
  if (!E.ready(src)) { g.fillStyle = '#1a1b20'; g.fillRect(0, 0, w, h); return c; }
  E.cover(g, src, 0, 0, w, h, fx, fy, crop); if (sat < 1 || dim < 1 || warm) E.grade(g, 0, 0, w, h, sat, dim, warm);
  return c;
}
function polyQuad(M, b) { return E.quadOf(M, b); }
const bg = (ctx, name) => { const im = img(name); if (E.ready(im)) ctx.drawImage(im, 0, 0, W, H); else { ctx.fillStyle = '#121318'; ctx.fillRect(0, 0, W, H); } };

// ------------------------------------------------------------------ 截图镜头（对应 full.py 的 shot：铺满、倾斜、其余压暗、高亮）
function shot(A, box0, box1, o = {}) {
  box1 = box1 || box0;
  const { hl = null, ry = [-16, -8], rx = 6, maxk = 2.4, bgimg = 'BG_PAGE', rng_ } = o;
  return (ctx, t) => {
    const im = img(A); if (!E.ready(im)) return; const [Aw, Ah] = E.sizeOf(im);
    const [a, b] = typeof rng_ === 'function' ? rng_() : rng_; const tl = t - a, dur = b - a, u = ease(tl / dur);
    const bx = box0.map((p, k) => lerp(p, box1[k], u)); const bw = bx[2] - bx[0], bh = bx[3] - bx[1];
    const s = Math.min(1500 / bw, 780 / bh, maxk) * (0.92 + 0.08 * easeOut(Math.min(1, tl / 0.9)));
    const mx = W / s * 0.8, my = H / s * 0.8;
    const x0 = Math.max(0, bx[0] - mx), y0 = Math.max(0, bx[1] - my), x1 = Math.min(Aw, bx[2] + mx), y1 = Math.min(Ah, bx[3] + my);
    const cw = (x1 - x0) * s, ch = (y1 - y0) * s; const cxb = ((bx[0] + bx[2]) / 2 - x0) * s, cyb = ((bx[1] + bx[3]) / 2 - y0) * s;
    bg(ctx, bgimg);
    const M = E.persp(ctx, im, cw, ch, W / 2 + (cw / 2 - cxb) + 60, H / 2 + (ch / 2 - cyb) - 30,
      { ry: lerp(ry[0], ry[1], u), rx, shadowK: 0.65, radius: 18, crop: [x0, y0, x1 - x0, y1 - y0] });
    E.dimExcept(ctx, M, cw, ch, [(bx[0] - x0) * s, (bx[1] - y0) * s, (bx[2] - x0) * s, (bx[3] - y0) * s], 0.62, 18);
    if (hl) {
      const p0 = E.mapPt(M, (hl[0] - x0) * s, (hl[1] - y0) * s), p1 = E.mapPt(M, (hl[2] - x0) * s, (hl[3] - y0) * s);
      E.hlBar(ctx, Math.max(0, p0[0]), Math.max(0, p0[1]), Math.min(W - 1, p1[0]), Math.min(H - 1, p1[1]), seg(tl, 0.3, 1.0), C.GOLD, 0.42);
    }
    return M;
  };
}

// ------------------------------------------------------------------ 整帧合成（对应 full.py 的 frame）
function subNow(t) {
  const s = D.shots.find(x => x.start <= t && t < x.end);
  if (!s || D.NO_SUB.includes(s.i) || t > s.chars[s.chars.length - 1] + 0.45) return '';
  for (const [a, txt, i, b] of D.subs) if (a <= t && t < b) return txt;
  return '';
}
function frame(ctx, tOut) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.shadowColor = 'transparent';
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const t = tOut - PRE;
  if (t < 0) { VIS.hookPre(ctx, t); }
  else {
    const s = shotAt(t); const fn = VIS[s.i];
    if (fn) fn(ctx, t); else { ctx.fillStyle = '#222'; ctx.fillRect(0, 0, W, H); }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    for (const c of [...D.CUTS, 'bridge']) {
      if (D.QUIET.includes(c)) continue; const t0 = EV[c]; if (t0 === undefined) continue;
      if (t - t0 >= 0 && t - t0 < 0.2) E.whip(ctx, 1 - (t - t0) / 0.2);
      if (t0 - t > 0 && t0 - t < 0.1) E.whip(ctx, (0.1 - (t0 - t)) / 0.1 * 0.8);
    }
    // 品牌句接回顾段：恢复原版短淡过背景，遮住出镜构图跳变。
    const cut = EV.cut62;
    if (cut - .12 < t && t < cut + .16) {
      const opacity = t < cut ? ease(seg(t, cut - .12, cut)) : 1 - ease(seg(t, cut, cut + .16));
      ctx.save(); ctx.globalAlpha = opacity; bg(ctx, 'BG'); ctx.restore();
    }
    E.subtitle(ctx, subNow(t));
  }
  const fade = clamp((PRE + D.TOTAL + D.TAIL - tOut) / 1.4, 0, 1);
  if (fade < 1) E.fill(ctx, '#000', 1 - fade);
}
