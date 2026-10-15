import sys; sys.path.insert(0, '.')
from kongjing import *
out, which = sys.argv[1], sys.argv[2]
D = 6.0
if which == 'math': render(lambda t: math_cosmos(t, D), D, f'{out}/clips/空镜1_数学宇宙.mp4', stills=[2.0, 5.0], still_dir=f'{out}/stills')
if which == 'factory': render(lambda t: digital_factory(t, D), D, f'{out}/clips/空镜2_数字化工厂.mp4', stills=[1.0, 4.5], still_dir=f'{out}/stills')
if which == 'protein': render(lambda t: protein(t, D, fold=(0.3, 3.8)), D, f'{out}/clips/空镜3_蛋白质折叠.mp4', stills=[1.5, 5.0], still_dir=f'{out}/stills')
print('done', which)
