import sys; sys.path.insert(0, '.')
from infographics import *
out, grp = sys.argv[1], sys.argv[2]
J = {'a': [('信息图1_向内索取向外延伸', knowledge, 8.0), ('大字1_参与创造知识', create_title, 4.2), ('大字2_AI_for_Science', afs_title, 4.5), ('信息图2_死亡之谷', valley, 5.2)],
     'b': [('信息图3_合作徽章', partners, 3.6), ('信息图4_四个环节', four_steps, 6.0), ('信息图5_五个场景', five_scenes, 4.6), ('数字_400', four_hundred, 3.6)]}
for name, fn, d in J[grp]:
    render(lambda t: fn(t, d), d, f'{out}/clips/{name}.mp4', stills=[d * 0.75], still_dir=f'{out}/stills'); print('done', name, flush=True)
