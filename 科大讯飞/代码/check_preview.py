"""检查当前工程的同步映射、字幕、换曲及片尾，不生成视频。"""
import os
from pathlib import Path
import runpy
import sys

import numpy as np

here = Path(__file__).resolve().parent
os.chdir(here)
sys.argv = ['full.py', 'align.json', '.', 'none']
g = runpy.run_path(str(here / 'full.py'))

pieces = g['audio_pieces']
for a, b, out, source in pieces:
    speed = g['audio_speeds'][out]
    assert b > a and speed > 0
    for delta in (.02, (b - a) / speed - .02):
        assert abs(g['src_at'](out + delta, source) - (a + delta * speed)) < 1e-5
for left, right in zip(pieces, pieces[1:]):
    end = left[2] + (left[1] - left[0]) / g['audio_speeds'][left[2]]
    assert end <= right[2] + 1e-6, '人声片段重叠'
assert len(g['SUBS']) == 120
assert all(start < end for start, text, shot, end in g['SUBS'])
for left, right in zip(g['MUSIC'], g['MUSIC'][1:]):
    overlap = left['to'] - right['frm']
    assert overlap >= 1.3
    assert abs(overlap - left['fout']) < 1e-5 and abs(overlap - right['fin']) < 1e-5
assert len(g['sfx_plan']()) == 21

# 最后 0.6 秒真实画面持续更新；原素材取帧不越界，最终亮度收低。
source_end = g['CAMV'].cap.get(g['cv2'].CAP_PROP_FRAME_COUNT) / g['CAMV'].fps
previous = None
for t in np.arange(g['DUR'] - .6, g['DUR'] - .02, 1 / 30):
    assert g['src_at'](t - g['PRE'], 'cam') < source_end
    frame = g['frame'](float(t))
    assert frame.shape == (1080, 1920, 3) and np.isfinite(frame).all()
    sampled = frame[::8, ::8]
    if previous is not None:
        assert np.abs(sampled - previous).mean() > .001, '片尾出现重复定格'
    previous = sampled.copy()
assert previous.mean() < 5
print(f"通过：声画映射、120 条字幕、6 处换曲、21 个音效及片尾；总长 {g['DUR']:.3f} 秒")
