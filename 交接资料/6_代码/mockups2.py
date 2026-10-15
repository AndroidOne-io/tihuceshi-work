import sys; sys.path.insert(0, '/tmp/claude-0/mock')
import numpy as np, cv2
import own as o, own2 as q, style3 as st
import mockups as M
W, H = 1920, 1080; P = o.P; CR = P + '/剪辑素材/'; SR = P + '/素材/'
fr03 = o.grab(CR + '03_01_选用片段.mp4', 2.0)
CUT_PEL = q.cut(fr03[60:640, 300:900])
CUT_SIMON = q.cut(o.imread(SR + '12_D01_参考图.png'))
f33 = o.grab(CR + '30_33_选用片段.mp4', 2.0)
CUT_MONK = q.cut(f33[160:449, 440:840]); CUT_QIN = q.cut(f33[160:449, 856:1256]); CUT_PEL2 = q.cut(f33[160:449, 23:423])
def tok_pel(d): return q.char_token(d, CUT_PEL, ('严', '父'), 'orange')
def tok_simon(d): return q.char_token(d, CUT_SIMON, ('西', '蒙'), 'violet')

def title_metal_frame(text, tt=1.5, depth='AI', sweep=0.45):
    f = q.tunnel(tt)
    if depth:
        dep = o.to_bgra(q.text_img(depth, q.F_TITLE, 760, (255, 120, 40, 255))); dep = cv2.GaussianBlur(dep, (0, 0), 30)
        o.blit(f, dep, 960 - dep.shape[1] // 2, 540 - dep.shape[0] // 2, 0.4)
    m = o.to_bgra(q.metal_title(text, 240, 0.08)); m = q.sweep(m, sweep); m = q.glow(m, (255, 170, 90), 20, 0.35)
    o.blit(f, m, 960 - m.shape[1] // 2, 520 - m.shape[0] // 2); return f
def brush_frame(text, backdrop, tint=(255, 110, 40), size=330, gl=0.0):
    g = q.halftone_bg(backdrop, tint)
    b = o.to_bgra(q.brush_title(text, size)); o.blit(g, b, 960 - b.shape[1] // 2, 540 - b.shape[0] // 2)
    return q.glitch(g, gl, 3)

def m01(): M.save('m01.jpg', title_metal_frame('世纪难题'))
def m05(): M.save('m05.jpg', brush_frame('鹈鹕测试', fr03))
def m06():
    f = o.bg(); big = cv2.resize(o.imread(SR + '12_D01_参考图.png'), (1080, 1080), interpolation=cv2.INTER_CUBIC)
    ramp = np.clip(np.linspace(-0.3, 1.3, 1080), 0, 1)[None, :, None]
    f[:, 840:] = (f[:, 840:] * (1 - ramp) + big * ramp).astype(np.uint8)
    nc = o.name_card('Simon Willison', None); o.put(f, nc, 600, 470)
    nk = o.to_bgra(q.text_img('西蒙老哥', q.F_NICK, 130, (255, 214, 170, 255)))
    o.put(f, q.glow(nk, (255, 140, 60), 14, 0.6), 760, 640)
    M.save('m06.jpg', f, '最早是由开发者西蒙·威利森')
def m07():
    f = o.bg(); hf = o.host(57.0, 1.0)
    o.put(f, tok_simon(250), W // 2, 190)
    for k in range(16):
        col, row = k % 8, k // 8; img = M.crude[(k % 11) + 1]
        o.put(f, o.token(190, 'grey', portrait=img, anchors=False), 250 + col * 205, 600 + row * 240)
    o.arrow(f, (W // 2, 340), (W // 2, 450), dashed=True)
    o.pip(f, cv2.resize(hf, (1280, 720)), x=1660, y=830, d=200)
    M.save('m07.jpg', f, '当时最能打的16个模型')
def m09(): M.save('m09.jpg', brush_frame('没法作假', o.grab(CR + '17_19_选用片段.mp4', 2.0), (90, 160, 255)))
def m13(): M.save('m13.jpg', brush_frame('背题', o.grab(CR + '28_29_选用片段.mp4', 5.5), (230, 50, 50), 420))
def m15():
    f = o.bg(tint='warm'); hf = o.host(196.0, 1.0)
    for k, (c, n, t) in enumerate([(CUT_PEL2, ('鹈', '鹕'), 'cyan'), (CUT_MONK, ('大', '圣'), 'orange'), (CUT_QIN, ('始', '皇'), 'violet')]):
        o.put(f, q.char_token(400 if k == 1 else 360, c, n, t), 380 + k * 580, 500 if k != 1 else 460)
    o.pip(f, cv2.resize(hf, (1280, 720)))
    M.save('m15.jpg', f, '孙悟空开飞机和秦始皇骑北极熊')
def m16():
    f = o.bg(tint='warm'); cx, cy = W // 2, 520
    ring = [('GPT', 'cyan'), ('Claude', 'orange'), ('Gemini', 'blue'), ('DeepSeek', 'blue'), ('Qwen', 'violet'), ('Llama', 'green'), ('Grok', 'grey'), ('GLM', 'cyan')]
    for k, (n_, t_) in enumerate(ring):
        a = np.radians(k * 360 / len(ring) - 90); x = cx + 660 * np.cos(a); y = cy + 360 * np.sin(a)
        o.arrow(f, (x, y), (cx + (x - cx) * 0.42, cy + (y - cy) * 0.42), col=(140, 120, 100), w=2, dashed=True)
        o.put(f, o.token(180, t_, n_, '', anchors=False), x, y)
    o.put(f, tok_pel(380), cx, cy)
    M.save('m16.jpg', f)
for fn in (sys.argv[1:] or ['m01', 'm05', 'm06', 'm07', 'm09', 'm13', 'm15', 'm16']) if __name__ == '__main__' else []:
    globals()[fn](); print(fn, flush=True)
