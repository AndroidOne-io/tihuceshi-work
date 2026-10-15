# Whole-film cue sheet (grows segment by segment). python3 cues.py -> cues_all.json
import json, sys
sys.path.insert(0, '/tmp/claude-0/mock')
ev = json.load(open('/tmp/claude-0/mock/v4ev.json')); INS = ev['inserts']
def T(n): return n + sum(d for a, d, _ in INS if a < n - 1e-9)
def PT(a):
    t0 = a + sum(d for x, d, _ in INS if x < a - 1e-9); d = [d for x, d, _ in INS if abs(x - a) < 1e-6][0]; return t0, t0 + d
V = '/home/claude/aliang2052/tihuceshi/口播粗剪.mp4'; MEME = '/home/claude/aliang2052/tihuceshi/分镜素材工程/素材/15_B站_11-20秒.mp4'
END = float(sys.argv[1]) if len(sys.argv) > 1 else ev['total']
voice = []; cur = 0.0
for a, d, k in INS + [[207.4667, 0, 'end']]:
    voice.append(dict(src=V, ss=cur, dur=a - cur, at=cur + sum(d for x, d, _ in INS if x <= cur + 1e-9))); cur = a
m0, m1 = PT(72.25); voice.append(dict(src=MEME, ss=0, dur=m1 - m0 - 0.05, at=m0, lufs=-17))
WH = '转场-Whoosh.mp3'
music = [
    # --- seg 1
    dict(file='In Motion - Trent Reznor & Atticus Ross.m4a', src=0.0, at=1.05, until=7.6, fade_in=0.02, fade_out=0.25, level=-19),
    dict(file='Sneaky Snitch - Kevin MacLeod.mp3', src=0.0, at=7.45, until=31.2, fade_in=0.05, fade_out=0.3, level=-20),
    dict(file='In Motion - Trent Reznor & Atticus Ross.m4a', src=8.0, at=31.0, until=38.7, fade_in=0.1, fade_out=0.3, level=-20),
    dict(file='Mind Heist - Zack Hemsey.m4a', src=52.0 - (42.8 - 38.5), ref_ss=52.0, at=38.5, until=45.1, fade_in=0.4, fade_out=0.6, level=-17),
    # --- seg 2
    dict(file='Monkeys Spinning Monkeys - Kevin MacLeod.m4a', src=1.0, ref_ss=4.0, at=44.75, until=T(66.0), fade_in=0.3, fade_out=0.25, level=-22),
    dict(file='Fluffing a Duck - Kevin MacLeod.mp3', src=0.0, at=T(66.0) - 0.05, until=m0 + 0.1, fade_in=0.05, fade_out=0.3, level=-20),
]
sfx = [dict(file='重音-咚 重磅.mp3', at=1.05, gain_db=-16, align='peak'), dict(file=WH, at=3.9, gain_db=-24, align='peak')]
sfx += [dict(file=WH, at=t, gain_db=-26, align='peak') for t in (7.5, 11.0, 14.45, 21.12, 24.95, 38.5)]
sfx += [dict(file='转场-Windy swish.mp3', at=17.4, gain_db=-28, align='peak'), dict(file=WH, at=31.05, gain_db=-24, align='peak'),
        dict(file='重音-Gate Hit.mp3', at=36.95, gain_db=-17, align='peak'), dict(file='上升-whoosh rise.mp3', at=42.8, gain_db=-22, align='end'),
        dict(file='重音-Thud Hit C.mp3', at=42.8, gain_db=-15, align='peak')]
synth = [dict(kind='shine', at=1.4)] + [dict(kind='scribble', at=t) for t in (5.5, 5.9, 22.32, 23.12)]
synth += [dict(kind='pop', at=26.8 + d) for d in (0.05, 0.9, 1.8, 2.7)] + [dict(kind='scribble', at=26.8 + d + 0.35) for d in (0.05, 0.9, 1.8, 2.7)]
# seg 2 events from renderer
for e in ev['sfx']:
    k = e['kind']; t = e['at']
    if t < 44.6: continue
    if k == 'whoosh': sfx.append(dict(file=WH, at=t, gain_db=-26, align='peak'))
    else: synth.append(dict(kind=k, at=t))
swell = [[1.05, 3.9, 1.0], [42.75, 44.6, 1.0]]
json.dump(dict(end=END, duck_db=-11, voice=voice, music=[m for m in music if m['at'] < END], sfx=[s for s in sfx if s['at'] < END],
               synth=[s for s in synth if s['at'] < END], swell=swell), open('/tmp/claude-0/mock/cues_all.json', 'w'), ensure_ascii=False, indent=1)
print('ok', END)
