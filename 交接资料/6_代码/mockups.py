import sys; sys.path.insert(0, '/tmp/claude-0/mock')
import own as o, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
import style3 as st
W, H = 1920, 1080; P = o.P; CR = P + '/剪辑素材/'; SR = P + '/素材/'
OUT = '/home/claude/docfig2/'
import os; os.makedirs(OUT, exist_ok=True)

def calli(t, size, col=(255, 222, 186), glow=o.ORANGE):
    im = st.text(t, o.F_BRUSH if hasattr(o, 'F_BRUSH') else st.F_BRUSH, size, col + (245,), 0.02)
    im = o.pad(im, 30); a = im.split()[3]
    g = Image.new('RGBA', im.size, glow + (0,)); g.putalpha(a.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.6)))
    r = Image.new('RGBA', im.size, (0, 0, 0, 0)); r.alpha_composite(g); r.alpha_composite(im); return r
def nick_token(d, tint, img, a, b):
    t = o.token(d, tint, portrait=img)
    ca, cb = calli(a, int(d * 0.36)), calli(b, int(d * 0.36))
    w = t.width + ca.width * 2; out = Image.new('RGBA', (w, t.height), (0, 0, 0, 0)); out.alpha_composite(t, (ca.width, 0))
    cy = t.height // 2
    out.alpha_composite(ca, (int(w / 2 - d * 0.66 - ca.width / 2), cy - ca.height // 2))
    out.alpha_composite(cb, (int(w / 2 + d * 0.66 - cb.width / 2), cy - cb.height // 2))
    return out
def split_brush(f, left, right, size, col, glow, y=430, gapx=300):
    a = calli(left, size, col, glow); b = calli(right, size, col, glow)
    o.put(f, a, W // 2 - gapx - a.width // 2 + 60, y); o.put(f, b, W // 2 + gapx + b.width // 2 - 60, y)
crude = {i: o.imread(CR + '12_网页原图_%02d.png' % i) for i in range(1, 12)}
f03 = o.grab(CR + '03_01_选用片段.mp4', 2.0)
PEL = f03[40:500, 380:840]
PORT = o.imread(SR + '12_D01_参考图.png')
f33 = o.grab(CR + '30_33_选用片段.mp4', 2.0)
def save(name, f, sub=None):
    if sub: o.subtitle(f, sub)
    wm = o.to_bgra(st.shadow(st.text('AI阿亮', st.F_MED, 30, (255, 255, 255), 0.12), 4, (0, 2), 160, 8)); o.blit(f, wm, W - wm.shape[1] - 44, 30, 0.5)
    cv2.imwrite(OUT + name, f, [cv2.IMWRITE_JPEG_QUALITY, 88])

# M01 hook: brush behind cutout host
def m01():
    f = o.bg(); hf = o.host(2.2, 1.0)
    split_brush(f, '世纪', '难题', 300, (238, 238, 244), (90, 110, 160), 400, 200)
    cut = o.cutout(hf); o.blit(f, cut, 0, 0)
    save('m01.jpg', f, '连数学世纪难题都能轻松破解的AI')
# M02 exam paper with crude pelican and red zero
def m02():
    f = o.bg(); hf = o.host(5.0, 1.0)
    pc = o.paper_card(1000, 760, True, None)
    a = o.to_bgra(pc); c = cv2.resize(crude[11], (430, 430), interpolation=cv2.INTER_AREA)
    o.blit(a, c, 285, 165)
    im = Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGRA2RGBA))
    im = im.rotate(-4, resample=Image.BICUBIC, expand=True)
    o.put(f, im, 1080, 520)
    sc = st.text('0分', st.F_BRUSH, 200, o.RED + (255,)); o.put(f, sc, 1480, 300); o.red_circle(f, 1480, 300, 190, 130, 10)
    o.pip(f, cv2.resize(hf, (1280, 720)))
    save('m02.jpg', f, '却搞不懂一个小学生都能轻松答对的测试')
# M03 montage with red-pen grading marks (no text)
def m03():
    fr = o.grab(SR + '06_B站_19-24秒.mp4', 2.0); f = o.cover(fr[40:496, 180:990], W, H)
    o.red_circle(f, 1250, 690, 260, 200, 12, -5); o.red_x(f, 1600, 280, 70, 16)
    save('m03.jpg', f, '车轱辘像是鱼儿一样跃上跃下')
# M04 Opus blank answer sheet + token + stamp
def m04():
    f = o.bg(); hf = o.host(34.0, 1.0)
    o.put(f, o.token(380, 'orange', 'Opus 5.5', ''), 470, 480)
    pc = o.paper_card(880, 700, True, None); a = o.to_bgra(pc)
    im = Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGRA2RGBA)); d = ImageDraw.Draw(im)
    im = im.rotate(3, resample=Image.BICUBIC, expand=True); o.put(f, im, 1270, 540)
    o.put(f, o.stamp('交白卷', size=180, angle=-12), 1290, 560)
    o.pip(f, cv2.resize(hf, (1280, 720)))
    save('m04.jpg', f, '连试两次 跑了20分钟 硬是没跑出来')
# M05 title: pelican mascot token with nickname
def m05():
    f = o.bg(tint='warm')
    o.put(f, st.metal('鹈鹕测试', 150, top='THE  PELICAN  TEST'), W // 2, 180)
    o.put(f, nick_token(470, 'orange', PEL, '严', '父'), W // 2, 640)
    save('m05.jpg', f)
# M06 Simon intro: full-bleed halftone photo + name card w/ calli nickname
def m06():
    f = o.bg(); big = cv2.resize(PORT, (1080, 1080), interpolation=cv2.INTER_CUBIC)
    ramp = np.clip(np.linspace(-0.3, 1.3, 1080), 0, 1)[None, :, None]
    f[:, 840:] = (f[:, 840:] * (1 - ramp) + big * ramp).astype(np.uint8)
    nc = o.name_card('Simon Willison', None)
    o.put(f, nc, 600, 470)
    nk = calli('西蒙老哥', 150); o.put(f, nk, 860, 640)
    save('m06.jpg', f, '最早是由开发者西蒙·威利森')
# M07 exam hall stage: Simon -> 16 seats
def m07():
    f = o.bg(); hf = o.host(57.0, 1.0)
    o.put(f, nick_token(200, 'violet', PORT, '西', '蒙'), W // 2, 170)

    seats = []
    for k in range(16):
        img = crude[(k % 11) + 1]
        seats.append(o.token(190, 'grey', portrait=img, anchors=False))
    for k, s in enumerate(seats):
        col, row = k % 8, k // 8
        cx = 250 + col * 205; cy = 560 + row * 250
        o.put(f, s, cx, cy)
    o.arrow(f, (W // 2, 290), (W // 2, 400), dashed=True)
    o.pip(f, cv2.resize(hf, (1280, 720)), x=1660, y=830, d=200)
    save('m07.jpg', f, '当时最能打的16个模型')
# M08 host with big stickers (pelican+bike ≈ chicken+basketball)
def m08():
    f = o.host(70.5, 1.08)
    pel = Image.fromarray(cv2.cvtColor(PEL, cv2.COLOR_BGR2RGB)).convert('RGBA')
    o.put(f, st.sticker(pel, 300, 14, -8), 300, 330); o.put(f, st.sticker(st.emoji('🚲', 260), 260, 14, 6), 320, 720)
    o.put(f, st.sticker(st.emoji('🐔', 260), 260, 14, 7), 1620, 330); o.put(f, st.sticker(st.emoji('🏀', 240), 240, 14, -6), 1600, 720)
    save('m08.jpg', f, '颇有鸡和篮球的那味儿')
# M09 pause brush "没法作假" with cutout host in front
def m09():
    bgsrc = o.grab(CR + '17_19_选用片段.mp4', 2.0); f = o.bg(bgsrc, 0.25)
    split_brush(f, '没法', '作假', 280, (240, 240, 246), (120, 120, 140), 400, 200)
    hf = o.host(82.3, 1.0); cut = o.cutout(hf); o.blit(f, cut, 0, 0)
    save('m09.jpg', f)
# M10 bubble with SOTA tokens + pin
def m10():
    f = o.bg(); hf = o.host(96.0, 1.0)
    cx, cy, r = 980, 500, 400
    y, x = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
    rim = np.clip(1 - np.abs(d - 0.98) / 0.06, 0, 1) * 0.9 + np.clip(d - 0.6, 0, 0.4) * (d < 1) * 0.35 + np.clip(1 - d, 0, 1) ** 6 * 0
    irid = (np.sin(x / 40 + y / 60) * 0.5 + 0.5)
    col = np.stack([200 + 55 * irid, 230 - 30 * irid, 255 - 60 * irid], -1)
    f = (f * (1 - rim[..., None] * 0.7) + col * rim[..., None] * 0.7).astype(np.uint8)
    hl = np.clip(1 - (((x - (cx - r * 0.45)) / (r * 0.25)) ** 2 + ((y - (cy - r * 0.55)) / (r * 0.12)) ** 2), 0, 1) * 0.5
    f = (f * (1 - hl[..., None]) + 255 * hl[..., None]).astype(np.uint8)
    for t_, tint, px, py, dd in [('GPT', 'cyan', 800, 420, 290), ('Claude', 'orange', 1150, 380, 270), ('Gemini', 'blue', 990, 680, 280)]:
        o.put(f, o.token(dd, tint, t_, '', anchors=False, title_size=int(dd * 0.2)), px, py)
    pin = Image.new('RGBA', (300, 60), (0, 0, 0, 0)); dr = ImageDraw.Draw(pin); dr.line([0, 30, 250, 30], fill=(220, 220, 230, 255), width=6); dr.ellipse([240, 10, 290, 50], fill=o.RED + (255,))
    pin = pin.resize((600, 120)).rotate(-30, expand=True, resample=Image.BICUBIC); o.put(f, pin, 1520, 200)
    o.pip(f, cv2.resize(hf, (1280, 720)))
    save('m10.jpg', f, '而这也戳破了不少模型厂商营造的虚假泡泡')
# M11 big chat window + model tokens
def m11():
    f = o.bg(); hf = o.host(128.0, 1.0)
    ch = Image.new('RGBA', (1500, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(ch)
    d.rounded_rectangle([0, 0, 1499, 229], 60, fill=(26, 28, 42, 240), outline=o.ORANGE + (220,), width=4)
    d.text((80, 70), 'Generate an SVG of a pelican riding a bicycle', font=st.font(st.F_MED, 60), fill=(250, 250, 255))
    d.rectangle([1340, 72, 1346, 156], fill=o.ORANGE)
    d.ellipse([1370, 55, 1470, 175], fill=o.ORANGE); d.polygon([(1405, 90), (1445, 115), (1405, 140)], fill=(26, 28, 42))
    o.put(f, st.shadow(ch, 20, (0, 12), 180, 40), W // 2, 330)
    for k, (tn, sb, tint) in enumerate([('GPT', 'OpenAI', 'cyan'), ('Claude', 'Anthropic', 'orange'), ('DeepSeek', '深度求索', 'blue')]):
        o.put(f, o.token(280, tint, tn, '', num=k + 1), 620 + k * 340, 720)
    o.pip(f, cv2.resize(hf, (1280, 720)))
    save('m11.jpg', f, '不妨输入下面这句提示词')
# M12 bar chart: Opus 5.5 output tokens by effort
def m12():
    f = o.bg(); hf = o.host(158.0, 1.0)
    data = [('LOW', 1891, 'low'), ('MEDIUM', 2941, 'medium'), ('HIGH', 3366, 'high'), ('XHIGH', 11977, 'xhigh'), ('MAX', 128000, 'max')]
    x0, x1, yb, ytop = 420, 1640, 840, 250
    def ys(v): return yb - (np.log10(v) - 3) / (np.log10(140000) - 3) * (yb - ytop)
    for v in (1000, 10000, 100000):
        y = int(ys(v)); cv2.line(f, (x0 - 20, y), (x1, y), (90, 80, 70), 1, cv2.LINE_AA)
    yl = int(ys(128000))
    for xx in range(x0 - 20, x1, 24): cv2.line(f, (xx, yl), (xx + 12, yl), o.RED[::-1], 3, cv2.LINE_AA)
    bw = 150
    for k, (lab, v, key) in enumerate(data):
        cx = 560 + k * 250; top = int(ys(v))
        col = (o.RED if key == 'max' else o.ORANGE)[::-1]
        ov = f.copy(); cv2.rectangle(ov, (cx - bw // 2, top), (cx + bw // 2, yb), col, -1); f = cv2.addWeighted(ov, 0.85, f, 0.15, 0)
        o.put(f, st.text(f'{v:,}', st.F_BEBAS, 64, (255, 255, 255)), cx, top - 40 if key != 'max' else top + 80)
        img = crude[3] if key == 'max' else None
    o.put(f, o.stamp('交白卷', size=100, angle=-12), 560 + 4 * 250 + 40, int(ys(3000)))
    o.put(f, o.token(230, 'orange', 'Opus 5.5', ''), 230, 380)
    o.pip(f, cv2.resize(hf, (1280, 720)), x=1660, y=780, d=220)
    save('m12.jpg', f, '是达到了Token的输出上限')
# M13 pause "背题"
def m13():
    bgsrc = o.grab(CR + '28_29_选用片段.mp4', 5.5); f = o.bg(bgsrc, 0.3, tint='red')
    split_brush(f, '背', '题', 380, (240, 236, 236), (150, 40, 40), 420, 210)
    cut = o.cutout(o.host(176.0, 1.0)); o.blit(f, cut, 0, 0)
    save('m13.jpg', f)
# M14 evolution timeline
def m14():
    f = o.bg(); hf = o.host(183.0, 1.0)
    a3 = o.grab(CR + '29_32_选用片段.mp4', 1.0); a2 = o.grab(CR + '29_31_选用片段.mp4', 1.0)
    items = [(crude[7], 'grey', '2024', '一张图'), (a2[100:620, 300:980], 'orange', '2026', '动画'), (a3[60:660, 340:940], 'cyan', 'NEXT', '3D')]
    for k, (img, tint, yr, lab) in enumerate(items):
        cx = 420 + k * 560
        o.put(f, o.token(330, tint, portrait=img, num=k + 1), cx, 470)
        o.put(f, st.text(yr, st.F_BEBAS, 110, (255, 255, 255)), cx, 740)
        if k < 2: o.arrow(f, (cx + 200, 470), (cx + 360, 470), dashed=True)
    o.pip(f, cv2.resize(hf, (1280, 720)), x=60, y=60, d=200)
    save('m14.jpg', f, '现在主流的操作则是跑动画')
# M15 brain-hole characters
def m15():
    f = o.bg(tint='warm'); hf = o.host(196.0, 1.0)
    chars = [(f33[160:449, 23:423], 'cyan', '鹈', '鹕'), (f33[160:449, 440:840], 'orange', '大', '圣'), (f33[160:449, 856:1256], 'violet', '始', '皇')]
    for k, (img, tint, a, b) in enumerate(chars):
        o.put(f, nick_token(290 if k != 1 else 330, tint, img, a, b), 330 + k * 630, 500 if k != 1 else 440)
    o.pip(f, cv2.resize(hf, (1280, 720)))
    save('m15.jpg', f, '孙悟空开飞机和秦始皇骑北极熊')
# M16 ending: all tokens orbit the pelican mascot
def m16():
    f = o.bg(tint='warm')
    cx, cy = W // 2, 500
    ring = [('GPT', 'cyan'), ('Claude', 'orange'), ('Gemini', 'blue'), ('DeepSeek', 'blue'), ('Qwen', 'violet'), ('Llama', 'green'), ('Grok', 'grey'), ('GLM', 'cyan')]
    for k, (n_, t_) in enumerate(ring):
        a = np.radians(k * 360 / len(ring) - 90); x = cx + 640 * np.cos(a); y = cy + 340 * np.sin(a)
        o.arrow(f, (x, y), (cx + (x - cx) * 0.38, cy + (y - cy) * 0.38), col=(140, 120, 100), w=2, dashed=True)
        o.put(f, o.token(170, t_, n_, anchors=False), x, y)
    o.put(f, nick_token(330, 'orange', PEL, '考', '官'), cx, cy)
    save('m16.jpg', f)

for fn in (sys.argv[1:] or ['m%02d' % i for i in range(1, 17)]) if __name__ == '__main__' else []:
    globals()[fn](); print(fn, flush=True)
