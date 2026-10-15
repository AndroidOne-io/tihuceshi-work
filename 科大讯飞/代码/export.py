# 导出工程附件：字幕 SRT、三条分轨（人声 / 配乐 / 音效）、音乐与音效 cue 表
# python3 export.py align.json 输出目录
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUTD = sys.argv[2]
HERE_ = os.path.dirname(os.path.abspath(__file__))
sys.argv = ['full.py', sys.argv[1], OUTD, 'none']
__file__ = os.path.join(HERE_, 'full.py')
exec(open(__file__, encoding='utf-8').read())

def ts(t):
    ms = int(round(t * 1000)); return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'

# 字幕：逐帧取画面上实际显示的那一行，和成片完全一致
rows, cur, t0 = [], None, 0.0
for n in range(int(DUR * FPS) + 1):
    tt = n / FPS; t = tt - PRE
    s = sub_now(t) if 0 <= t < TOTAL else ''
    if s != cur:
        if cur: rows.append((t0, tt, cur))
        cur, t0 = s, tt
if cur: rows.append((t0, DUR, cur))
with open(os.path.join(OUTD, '字幕.srt'), 'w', encoding='utf-8') as f:
    for k, (a, b, s) in enumerate(rows, 1): f.write(f'{k}\n{ts(a)} --> {ts(b)}\n{s}\n\n')

voice, music, sfx, rep, v_db, vmask = build_audio()
peak = max(np.abs(voice + music + sfx).max(), 1e-6)
for name, x in (('分轨_人声', voice), ('分轨_配乐', music), ('分轨_音效', sfx)):
    y = np.clip(x / peak * 0.98, -1, 1)
    with wave.open(os.path.join(OUTD, name + '.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())

cues = {'music': [dict(file=os.path.basename(m['file']), 曲内对齐点秒=m['src'], 片中开始=round(PRE + m['frm'], 2), 片中结束=round(PRE + m['to'], 2),
                       对齐到片中=round(PRE + m['at'], 2), 停顿电平dB=m.get('gap'), 画面口播电平dB=m.get('under'), 真人口播电平dB=m.get('host')) for m in MUSIC],
        'sfx': [dict(名称=n, 片中秒=round(te, 3), 音效=SFX[k]) for n, te, k in rep],
        'shots': [dict(镜号=s['i'], 开始=round(PRE + s['start'], 2), 结束=round(PRE + s['end'], 2), 台词=s['text'].strip()) for s in shots]}
json.dump(cues, open(os.path.join(OUTD, '时间线_cue表.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('export ok', len(rows), 'subs')
