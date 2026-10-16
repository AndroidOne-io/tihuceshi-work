# 整片配乐 + 音效规划（第五版声音）。由 full.py 在默认 MUSIC / sfx_plan 之后 exec，整体覆盖。
#
# 电平三档（相对人声的听感响度 LUFS，dB；每首按实际用到的那一段测响度，各曲同档位一样响）：
#   gap   口播停顿 / 大字 / 纯画面：−8，抬上来但不冲
#   under 口播 + 全屏画面：−17，听得见、不抢词
#   host  真人出镜口播：−24，退到背景但不消失
# 三档之间的落差故意不拉太大，起落也放慢（压下 0.15 秒、抬起 0.6 秒），音乐不会一会儿没了一会儿冒出来。
# 换曲只在段落交界，并且一律交叉淡化；大字/数字重击前 0.25 秒音乐压低约 10 dB，之后 0.6 秒回来。

HOST_SHOTS = {6, 9, 12, 14, 16, 18, 25, 35, 49, 50, 61, 62, 65, 71}

NEW = os.path.join(REPO, '音乐素材') + '/'          # 你新找的曲子（tihuceshi-work/音乐素材）

def M(file, src, at, frm, to, fin=0.6, fout=1.2, dip=None, ref=None, gap=-8, under=-17, host=-24):
    return dict(file=file if file.startswith('/') else '音乐/' + file, src=src, at=at, frm=frm, to=to, fin=fin, fout=fout, dip=dip,
                ref=src if ref is None else ref, gap=gap, under=under, host=host)

MUSIC = [
    # 换曲一律 1–2 秒交叉淡化，不留没音乐的空档；大字重击处只压低一下（dip），不断掉。
    # 1 冷开（黑场蓄力 → 「攻克」炸开）：悬疑铺垫，炸开后在停顿里余响，淡进新闻段
    M('悬疑-Dance for me walls.mp3', 21.09, EV['boom'], EV['boom'] - 2.5, EV['cut2'] + 1.2, fin=0.4, fout=1.6, dip=EV['boom'], ref=21.0),
    # 2 A 讲解背景：OpenAI Math 新闻 → 知识向内/向外 → 参与创造知识（重击处压一下）→ 一直铺到表情包前淡出
    M(NEW + '53976329-tech-explainer-background-modern-digital-459114.mp3', 8.0, EV['cut2'] - 0.8, EV['cut2'] - 0.8, EV['meme'] + 0.4,
      fin=1.5, fout=1.2, dip=[EV['create']], ref=30.0),
    # 3 包袱「AI干的就是明珠」：滑稽小段，抖完淡出
    M('Fluffing a Duck - Kevin MacLeod.mp3', 0.0, EV['meme'], EV['meme'] - 0.05, S[16]['start'] + 1.4, fin=0.05, fout=1.4, ref=0.0, under=-14),
    # 4 片名 AI for Science：史诗爆点对准片名，转回国内时和下一首交叉淡化
    M('Breath and Life - Audiomachine.mp3', 16.25, EV['afs'], EV['afs'] - 4.0, EV['bridge'] + 1.4, fin=1.8, fout=2.0, ref=17.0),
    # 5 B 痛点悬念：国内科研 → 化工 → 死亡之谷。曲线栽下去时压一下，然后慢慢淡进讯飞段
    M(NEW + 'leberch-documentary-suspense-375268.mp3', 0.0, EV['bridge'] - 0.6, EV['bridge'] - 0.6, EV['cut37'] + 1.0, fin=1.6, fout=2.2,
      dip=[EV['fall'], EV['valley']], ref=5.0, under=-18),
    # 6 C1 解决方案：讯飞 3.0 Pro → 演示 → 400+。曲子「起来」的那一下对准 3.0 Pro 截图出现
    M(NEW + 'sergepavkinmusic-futuristic-view-198436.mp3', 16.8, EV['cut38'], EV['cut37'] - 1.2, EV['ch2_in'] + 0.8, fin=1.6, fout=1.5,
      dip=[EV['n400']], ref=30.0, under=-18),
    # 7 C2 生物医药：开头的重拍对准「02 生物医药」章节卡，和上一首交叉
    M(NEW + 'the_mountain-inspiring-technology-179473.mp3', 1.9, EV['ch2_in'], EV['ch2_in'] - 0.8, EV['cut61'] + 1.0, fin=0.8, fout=1.6, ref=10.0, under=-18),
    # 8 D 温暖结尾：品牌句 → 总结 → 1024 → 最后一句。高潮起在 1024，回落对准最后一句真人口播；片子说完即结束，所以在最后一句下面 2.5 秒淡出，和画面同时收（不硬切）
    M(NEW + 'echoes_of_lumen-hope-music-hopeful-piano-586991.mp3', 139.5, EV['cut71'], EV['cut61'] - 0.8, TOTAL, fin=1.6, fout=2.5,
      dip=[EV['real']], ref=80.0),
]

SFX = {'rise': '上升-whoosh rise.mp3', 'whoosh': '转场-Whoosh.mp3', 'swish': '转场-Windy swish.mp3', 'gate': '重音-Gate Hit.mp3',
       'thud': '重音-Thud Hit C.mp3', 'dong': '重音-咚 重磅.mp3', 'rrise': '上声音-reverse rise.mp3'}

def sfx_plan():
    """全片约 30 个音效（每分钟约 7 个）：大重击只给 6 个大字/大数字；转场声只在换段落、换大画面；
    徽章、卡片、步骤、模块亮起这些小动作不再配声（客户反馈：音效太多）"""
    return [
        # —— 开头
        ('蓄力→人声进', EV['voice_in'], 'rise', 0.5), ('冲进隧道', EV['voice_in'], 'thud', 0.32), ('攻克·问号炸开', EV['boom'], 'dong', 1.0),
        ('进新闻', EV['cut2'], 'whoosh', 0.28),
        ('719 停住', EV['land719'], 'gate', 0.4), ('变金', EV['gold'] + 0.1, 'gate', 0.3), ('冲进论文', EV['dive'] + 0.3, 'swish', 0.32),
        ('进知识圈', EV['cut10'], 'whoosh', 0.26), ('冲破边界', EV['outward'] + 0.3, 'gate', 0.32),
        ('创造·蓄力', EV['create'], 'rise', 0.45), ('参与创造知识', EV['create'], 'dong', 0.95),
        ('表情包', EV['meme'] + 0.08, 'gate', 0.4),
        ('片名·蓄力', EV['afs'], 'rise', 0.55), ('AI for Science', EV['afs'], 'dong', 1.0),
        ('转回国内', EV['bridge'], 'swish', 0.28),
        # —— 国内 / 化工 / 死亡之谷
        ('章节卡·化工', EV['ch_in'], 'gate', 0.38), ('章节卡收', EV['cut26'], 'whoosh', 0.26),
        ('实验室→工厂', S[29]['start'] + 0.15, 'swish', 0.24),
        ('曲线栽下去', EV['fall'], 'thud', 0.45), ('死亡之谷', EV['valley'], 'dong', 1.0),
        # —— 讯飞 3.0 Pro / 演示 / 400+
        ('进模型简介', EV['cut38'], 'whoosh', 0.26),
        ('工具墙·蓄力', EV['n400'], 'rise', 0.5), ('400+', EV['n400'], 'dong', 1.0),
        ('章节卡·生物', EV['ch2_in'], 'gate', 0.38), ('章节卡收', EV['cut51'], 'whoosh', 0.26),
        # —— 生物医药 / 发表
        ('进讯飞项目', EV['cut56'], 'whoosh', 0.26), ('盖章', EV['pub'] + 0.4, 'gate', 0.3),
        ('换曲·上扬', EV['cut61'], 'rrise', 0.25),
        # —— 总结 / 1024 / 结尾
        ('进总结', EV['cut63'], 'whoosh', 0.24), ('进1024', EV['cut66'], 'whoosh', 0.26), ('真实场景', EV['real'], 'dong', 0.8),
    ]
