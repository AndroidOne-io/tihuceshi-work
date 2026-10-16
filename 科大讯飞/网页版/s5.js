// 第 51–61 镜：生物医药 → 蛋白质 → 讯飞蛋白质设计 → 指标提升 → 发表 → 品牌句
// 对应 代码/seg5_vis.py
'use strict';

// ------------------------------------------------------------------ 代码画的蛋白质（kongjing.protein）
const PROT = D.protein;
function protein(ctx, t, scale = 1.0, key = 'prot') {
  const ax = 12 * Math.PI / 180, ay = t * 22 * Math.PI / 180, az = 4 * Math.PI / 180;
  const cxA = Math.cos(ax), sxA = Math.sin(ax), cyA = Math.cos(ay), syA = Math.sin(ay), czA = Math.cos(az), szA = Math.sin(az);
  const n = PROT.P.length, U = new Array(n), Z = new Array(n);
  for (let i = 0; i < n; i++) {                   // R = Rz·Ry·Rx
    let [x, y, z] = PROT.P[i]; x *= scale; y *= scale; z *= scale;
    let y1 = y * cxA - z * sxA, z1 = y * sxA + z * cxA; y = y1; z = z1;
    let x1 = x * cyA + z * syA; z1 = -x * syA + z * cyA; x = x1; z = z1;
    x1 = x * czA - y * szA; y1 = x * szA + y * czA; x = x1; y = y1;
    const zz = z + 1350; Z[i] = zz; U[i] = [W / 2 + x * 1350 / zz, H / 2 + y * 1350 / zz];
  }
  const order = []; for (let i = 0; i < n - 1; i++) order.push(i);
  order.sort((a, b) => (Z[b] + Z[b + 1]) - (Z[a] + Z[a + 1]));   // 远的先画
  const g = E.layer(key); g.lineCap = 'round';
  for (const i of order) {
    const zz = (Z[i] + Z[i + 1]) / 2, k = clamp(1350 / zz, 0.4, 2.0), shade = clamp(1.25 - (zz - 950) / 900, 0.35, 1.15);
    const w = Math.max(2, Math.floor((PROT.K[i] === 'helix' ? 14 : PROT.K[i] === 'strand' ? 12 : 6) * k)), c = PROT.C[i];
    const seg_ = (col, lw) => { g.strokeStyle = rgb(col); g.lineWidth = lw; g.beginPath(); g.moveTo(U[i][0], U[i][1]); g.lineTo(U[i + 1][0], U[i + 1][1]); g.stroke(); };
    seg_(c.map(v => v * shade * 0.55), w + 4); seg_(c.map(v => v * shade), w); seg_(c.map(v => Math.min(v * shade + 90, 255)), Math.max(1, Math.floor(w / 4)));
  }
  E.addLayer(ctx, g, 1, [], 'source-over'); E.addLayer(ctx, g, 0, [[16, 0.35]]);
}

// ------------------------------------------------------------------ 51–53 生物空镜
VIS[51] = shotfn(51, foot('v10', 1.0, 14.7, { speed: 2.0 }));
VIS[52] = shotfn(52, foot('v10', 15.0, 31.9, { speed: 2.5 }));
VIS[53] = shotfn(53, foot('v10', 33.0, 59.7, { speed: 3.0 }));

// ------------------------------------------------------------------ 54 蛋白质结构
VIS[54] = (ctx, t) => { const tl = t - EV.cut54; E.zoomBegin(ctx, 1 + 0.05 * tl); bg(ctx, 'BGP'); protein(ctx, 1.0 + tl * 0.9, 1.05); E.zoomEnd(ctx); };

// ------------------------------------------------------------------ 55 大量实验：从中间一格（一直在动）拉远成一整面实验墙
VIS[55] = (ctx, t) => {
  const tl = t - EV.cut55, z = lerp(3.0, 0.62, ease(seg(tl, 0.15, 1.9))) * (1 + 0.01 * tl);
  const PW = D.PWg, PH = D.PHg, PG = D.PGg, gw = D.NCG * (PW + PG), gh = D.NRG * (PH + PG), cx0 = gw / 2, cy0 = gh / 2 - PG / 2;
  bg(ctx, 'BG');
  const gi = img('GRID_IM'); if (E.ready(gi)) ctx.drawImage(gi, W / 2 - cx0 * z, H / 2 - 20 - cy0 * z, gw * z, gh * z);
  const live = coverCanvas('live55', E.video('v10', 60.0 + tl * 1.2, 1.2), PW, PH, { sat: 0.75, warm: true });
  const ccx = 2 * (PW + PG) + PW / 2, ccy = 2 * (PH + PG) + PH / 2;
  ctx.drawImage(live, W / 2 + (ccx - cx0 - PW / 2) * z, H / 2 - 20 + (ccy - cy0 - PH / 2) * z, PW * z, PH * z);
};

// ------------------------------------------------------------------ 56–58 讯飞蛋白质设计截图
function shot8(ctx, t, box, s0, dur, o = {}) {
  const { ry = -9, flow = false, structs = false, badge = false } = o;
  const im = img('IMG8'); bg(ctx, 'BG8'); if (!E.ready(im)) return;
  const [iw, ih] = E.sizeOf(im), tl = t - s0, bw = box[2] - box[0], bh = box[3] - box[1];
  const s = Math.min(1600 / bw, 800 / bh, 2.6) * (0.94 + 0.06 * easeOut(Math.min(1, tl / 0.8)));
  const cw = iw * s, ch = ih * s, cxb = (box[0] + box[2]) / 2 * s, cyb = (box[1] + box[3]) / 2 * s;
  const M = E.persp(ctx, im, cw, ch, W / 2 + (cw / 2 - cxb), H / 2 - 30 + (ch / 2 - cyb), { ry: ry + 4 * ease(tl / dur), rx: 5, shadowK: 0.6 });
  E.dimExcept(ctx, M, cw, ch, box.map(v => v * s), 0.6);
  const g = E.layer('s8'); let any = false;
  if (flow) {                                     // 光点沿主线流过去，再分到三个可设计结构
    const segs = D.FLOW.map(([a, b]) => [a.map(v => v * s), b.map(v => v * s)]), on = easeOut(seg(tl, 0.3, 0.8));
    const L = ([a, b], u) => [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u];
    D.FL_PTS.forEach((u0, k) => {
      const u = (u0 + tl * 0.45) % 1; let p;
      if (u < 0.62) p = L(segs[0], u / 0.62);
      else {
        const br = k % 3, v = (u - 0.62) / 0.38;
        if (br === 1) p = L(segs[4], v);
        else { const s1 = segs[1 + (br === 0 ? 0 : 1)], s2 = segs[3 + (br === 0 ? 0 : 2)]; p = v < 0.5 ? L(s1, Math.min(1, v * 2)) : L(s2, (v - 0.5) * 2); }
      }
      const q = E.mapPt(M, p[0], p[1]); E.dot(g, q[0], q[1], 10, C.GOLD, on);
    });
    any = true;
  }
  if (structs) {                                  // 结构依次亮起：没亮之前压暗
    D.STRUCT.forEach((b, j) => {
      const t0 = EV.structs[j], k = easeOut(seg(t, t0, t0 + 0.25)), q = E.quadOf(M, b.map(v => v * s));
      if (k < 1) { ctx.save(); E.pathPoly(ctx, q); ctx.fillStyle = `rgba(0,0,0,${0.5 * (1 - k)})`; ctx.fill(); ctx.restore(); }
      if (k > 0) { E.pathPoly(g, q); g.strokeStyle = rgb(C.GOLD, k); g.lineWidth = 6; g.lineJoin = 'round'; g.stroke(); }
    });
    any = true;
  }
  if (any) { E.addLayer(ctx, g, 0.9, [], 'source-over'); E.addLayer(ctx, g, 0, [[6, 0.6]]); }
  if (badge) { const k = seg(t, s0 + 0.45, s0 + 0.8); E.put(ctx, img('P_XF'), lerp(-200, 300, easeOut(k)), H - 330, k, 0.72); }
}
const boxAt = (b0, b1, u) => b0.map((a, k) => lerp(a, b1[k], u));
VIS[56] = (ctx, t) => { const s = S[56], u = ease(seg(t, s.start, s.end)); shot8(ctx, t, boxAt([0, 0, 1010, 713], [20, 10, 1005, 420], u), s.start, s.dur, { badge: true }); };
VIS[57] = (ctx, t) => { const s = S[57], u = ease(seg(t, s.start, s.end)); shot8(ctx, t, boxAt([20, 10, 1005, 420], [40, 30, 790, 370], u), s.start, s.dur, { flow: true }); };
VIS[58] = (ctx, t) => { const s = S[58], u = ease(seg(t, s.start, s.start + 0.6)); shot8(ctx, t, boxAt([40, 30, 790, 370], [580, 50, 1008, 410], u), s.start, s.dur, { structs: true, ry: -6 }); };

// ------------------------------------------------------------------ 59 指标提升：三枚徽章 + 往上长的金箭头（不编具体数字）
const MET_E = ['m_acc', 'm_stab', 'm_act'];
VIS[59] = (ctx, t) => {
  const tl = t - EV.cut59;
  const pc = E.tmp('p59'), pg = pc.getContext('2d'); pg.setTransform(1, 0, 0, 1, 0, 0); pg.globalAlpha = 1; pg.globalCompositeOperation = 'source-over';
  bg(pg, 'BGP'); protein(pg, 3.0 + tl * 0.6, 1.15, 'prot59');
  bg(ctx, 'BGP'); E.blurDraw(ctx, pc, 3, 0, 0, W, H, 0.42);
  const g = E.layer('met');
  MET_E.forEach((e, j) => {
    const x = D.MET_X[j], t0 = EV[e] - 0.05, k = seg(t, t0, t0 + 0.3); if (k <= 0) return;
    E.put(ctx, img('MET_IM_' + j), x, H / 2 + 90, easeOut(k), 0.8 + 0.2 * backOut(k));
    const gr = easeOut(seg(t, t0 + 0.2, t0 + 0.8)) * (1 + 0.25 * easeOut(seg(t, EV.m_up, EV.m_up + 0.5)));
    const y0 = H / 2 - 110, y1 = y0 - 190 * gr;
    g.strokeStyle = rgb(C.GOLD); g.lineWidth = 10; g.lineCap = 'butt'; g.beginPath(); g.moveTo(x, y0); g.lineTo(x, y1); g.stroke();
    E.pathPoly(g, [[x - 34, y1 + 10], [x + 34, y1 + 10], [x, y1 - 40]]); g.fillStyle = rgb(C.GOLD); g.fill();
  });
  const pulse = Math.max(0, 1 - Math.abs(t - EV.m_up - 0.2) / 0.3);
  E.addLayer(ctx, g, 1, [], 'source-over'); E.addLayer(ctx, g, 0, [[12, 0.5 + 0.8 * pulse]]);
};

// ------------------------------------------------------------------ 60 发表：一页论文落下，金光扫过，盖章（不冒充具体期刊）
VIS[60] = (ctx, t) => {
  const tl = t - EV.cut60; E.zoomBegin(ctx, 1 + 0.03 * tl);
  bg(ctx, 'BG_PUB');
  for (let j = 0; j < 4; j++) E.put(ctx, img('PW_' + j), W / 2 - 40 + j * 26, H / 2 + 10 - j * 8, 0.55 * easeOut(seg(tl, 0, 0.3)), 1.6, -6 + j * 3);
  const u = seg(t, EV.pub - 0.45, EV.pub), y = u < 1 ? lerp(-500, H / 2 - 30, easeIn(u, 2)) : H / 2 - 30;
  if (u > 0) E.put(ctx, img('PAPER_BIG'), W / 2, y, 1, 1, lerp(-12, 2, u));
  const gk = ease(seg(t, EV.pub + 0.15, EV.pub + 0.6)); if (gk > 0) E.put(ctx, img('PAPER_G'), W / 2, H / 2 - 30, gk, 1, 2);
  const ks = seg(t, EV.pub + 0.25, EV.pub + 0.45); if (ks > 0) E.put(ctx, img('SEAL'), W / 2 + 210, H / 2 + 230, ks, 1.5 - 0.5 * easeOut(ks, 3), -12);
  E.zoomEnd(ctx);
  if (t >= EV.pub) {
    const q = t - EV.pub;
    if (q < 0.6) { const sx = lerp(W / 2 - 400, W / 2 + 400, q / 0.6), g = E.layer('sw60'); E.line(g, [[sx, 0], [sx - 200, H]], [255, 230, 170], 1, 50); E.addLayer(ctx, g, 0, [[30, 0.8]]); }
    E.shake(ctx, Math.max(0, 1 - q / 0.3) * 0.6, Math.floor(t * 30));
  }
};

// ------------------------------------------------------------------ 61 品牌句：真人，「自主可控」处跳一次景别
VIS[61] = (ctx, t) => host(t < EV.indep - 0.1 ? 1.0 : 1.13)(ctx, t);
