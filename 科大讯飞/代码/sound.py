# 节奏与声音修订：七段配乐连续交接，音效只保留结构性落点。
VOICE_FILTER = 'highpass=f=70'
MUSIC_FILTER = 'equalizer=f=2600:t=q:w=0.8:g=-2.5'
MUSIC_DYNAMICS = 'acompressor=threshold=0.08:ratio=2:attack=30:release=350:makeup=1'
HOST_SHOTS = {6, 9, 12, 14, 16, 18, 25, 35, 49, 50, 61, 62, 65, 71}
NEW = os.path.join(REPO, '音乐素材') + '/'


def M(file, src, at, frm, to, fin, fout):
    # 真人和全屏讲解仅差 1 dB；停顿只抬 3 dB，避免反复忽大忽小。
    return dict(file=file if file.startswith('/') else '音乐/' + file,
                src=src, at=at, frm=frm, to=to, fin=fin, fout=fout,
                gap=-18, under=-21, host=-22, dip=None)


MUSIC = [
    M('悬疑-Dance for me walls.mp3', 21.09, EV['boom'], EV['boom'] - 2.5,
      EV['cut2'] + .7, .4, 1.4),
    M(NEW + '53976329-tech-explainer-background-modern-digital-459114.mp3', 8.0, EV['cut2'] - .7,
      EV['cut2'] - .7, EV['afs'] - 1.5, 1.4, 1.5),
    # 包袱沿用讲解音乐，不再突然切入滑稽小曲；片名保留一次自然铺垫。
    M('Breath and Life - Audiomachine.mp3', 16.25, EV['afs'], EV['afs'] - 3.0,
      EV['bridge'] + .8, 1.5, 1.6),
    M(NEW + 'leberch-documentary-suspense-375268.mp3', 0.0, EV['bridge'] - .8,
      EV['bridge'] - .8, EV['cut37'] + .8, 1.6, 1.6),
    # 死亡之谷不断音乐，以完整交叉淡化接到解决方案。
    M(NEW + 'sergepavkinmusic-futuristic-view-198436.mp3', 16.8, EV['cut38'], EV['cut37'] - .8,
      EV['ch2_in'] + .7, 1.6, 1.4),
    M(NEW + 'the_mountain-inspiring-technology-179473.mp3', 1.9, EV['ch2_in'], EV['ch2_in'] - .7,
      EV['cut61'] + .9, 1.4, 1.8),
    M(NEW + 'echoes_of_lumen-hope-music-hopeful-piano-586991.mp3', 139.5, EV['cut71'], EV['cut61'] - .9,
      TOTAL + TAIL, 1.8, 1.2),
]

SFX = {'rise': '上升-whoosh rise.mp3', 'whoosh': '转场-Whoosh.mp3', 'swish': '转场-Windy swish.mp3',
       'gate': '重音-Gate Hit.mp3', 'thud': '重音-Thud Hit C.mp3', 'dong': '重音-咚 重磅.mp3'}


def sfx_plan():
    # 删除逐卡、逐步、逐指标轻击和同点叠加；数字、章节、关键转折各留一声。
    return [
        ('攻克·问号炸开', EV['boom'], 'dong', .8),
        ('进新闻', EV['cut2'], 'whoosh', .7),
        ('719 停住', EV['land719'], 'gate', .7),
        ('冲进论文', EV['dive'] + .3, 'swish', .65),
        ('冲破边界', EV['outward'] + .3, 'gate', .65),
        ('参与创造知识', EV['create'], 'dong', .75),
        ('表情包', EV['meme'] + .08, 'thud', .55),
        ('AI for Science', EV['afs'], 'dong', .8),
        ('章节卡·化工', EV['ch_in'], 'gate', .7),
        ('实验室→工厂', S[29]['start'] + .15, 'swish', .6),
        ('死亡之谷', EV['valley'], 'dong', .75),
        ('合作·扣上', EV['link'], 'thud', .6),
        ('进演示', EV['cut40'], 'swish', .65),
        ('400+', EV['n400'], 'dong', .8),
        ('章节卡·生物', EV['ch2_in'], 'gate', .7),
        ('进讯飞项目', EV['cut56'], 'whoosh', .65),
        ('盖章', EV['pub'] + .4, 'gate', .6),
        ('循环接上', EV['s4'] + .9, 'thud', .55),
        ('进1024', EV['cut66'], 'whoosh', .65),
        ('真实场景', EV['real'], 'dong', .7),
        ('回活动页', EV['cut70'], 'swish', .6),
    ]
