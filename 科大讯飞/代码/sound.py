# 整片配乐 + 音效规划（第五版声音）。由 full.py 在默认 MUSIC / sfx_plan 之后 exec，整体覆盖。
#
# 电平三档（相对人声响度，dB）：
#   gap   口播停顿 / 大字 / 纯画面：音乐抬上来，接近人声（小Lin 实测停顿抬 15–25 dB）
#   under 口播 + 全屏画面：能听见、不抢词
#   host  真人出镜口播：几乎退到背景，只留一点氛围
# 换曲只在段落交界；大字/数字重击前 0.25 秒音乐让开。

HOST_SHOTS = {6, 9, 12, 14, 16, 18, 25, 35, 49, 50, 61, 62, 65, 71}

NEW = os.path.join(REPO, '音乐素材') + '/'          # 你新找的曲子（tihuceshi-work/音乐素材）

def M(file, src, at, frm, to, fin=0.6, fout=1.2, dip=None, ref=None, gap=-4, under=-16, host=-30):
    return dict(file=file if file.startswith('/') else '音乐/' + file, src=src, at=at, frm=frm, to=to, fin=fin, fout=fout, dip=dip,
                ref=src if ref is None else ref, gap=gap, under=under, host=host)

MUSIC = [
    # 1 冷开（黑场蓄力 → 「攻克」炸开）：悬疑铺垫，炸开后在停顿里余响                         —— 旧库 Dance for me walls
    M('悬疑-Dance for me walls.mp3', 21.09, EV['boom'], EV['boom'] - 2.5, EV['cut2'] + 0.6, fin=0.4, fout=1.4, dip=EV['boom'], ref=21.0, gap=-3),
    # 2 A 讲解背景：OpenAI Math 新闻 → 知识向内/向外。跳过曲子开头太轻的 8 秒，后面慢慢起来；「参与创造知识」前整段断掉
    M(NEW + '53976329-tech-explainer-background-modern-digital-459114.mp3', 8.0, EV['cut2'] - 0.3, EV['cut2'] - 0.3, EV['create'] - 0.02,
      fin=0.8, fout=0.25, ref=30.0, gap=-5, under=-16),
    # 3 包袱「AI干的就是明珠」：滑稽小段，抖完就收                                              —— 旧库 Fluffing a Duck
    M('Fluffing a Duck - Kevin MacLeod.mp3', 0.0, EV['meme'], EV['meme'], S[16]['start'] + 1.2, fin=0.02, fout=1.2, ref=0.0, gap=-6, under=-12, host=-28),
    # 4 片名 AI for Science：史诗爆点对准片名，停顿里推满，转回国内时退下                         —— 旧库 Breath and Life
    M('Breath and Life - Audiomachine.mp3', 16.25, EV['afs'], EV['afs'] - 4.0, EV['bridge'] + 0.4, fin=1.5, fout=1.6, ref=17.0, gap=-3, under=-16),
    # 5 B 痛点悬念：国内科研 → 化工 → 死亡之谷。低频脉冲、几乎不占人声频段；曲线栽下去那一刻断掉
    M(NEW + 'leberch-documentary-suspense-375268.mp3', 0.0, EV['bridge'] - 0.2, EV['bridge'] - 0.2, EV['fall'] - 0.02, fin=0.8, fout=0.1, ref=5.0, gap=-5, under=-18),   # 脉冲感强，压低一点
    # 6 C1 解决方案：讯飞 3.0 Pro → 演示 → 400+。合作徽章下是安静前奏，曲子「起来」的那一下对准 3.0 Pro 截图出现
    M(NEW + 'sergepavkinmusic-futuristic-view-198436.mp3', 16.8, EV['cut38'], EV['cut37'] - 0.05, EV['ch2_in'] - 0.15, fin=0.3, fout=1.0,
      dip=[EV['n400']], ref=30.0, under=-18),
    # 7 C2 生物医药：换一首，开头的重拍对准「02 生物医药」章节卡
    M(NEW + 'the_mountain-inspiring-technology-179473.mp3', 1.9, EV['ch2_in'], EV['ch2_in'] - 0.4, EV['cut61'] + 0.2, fin=0.3, fout=1.0, ref=10.0, under=-18),
    # 8 D 温暖结尾：品牌句 → 总结 → 1024 → 结尾。曲中的安静段落在「AI 还不能替代科学家」，
    #   高潮起在 1024 活动页，回落对准最后一句真人口播，片尾渐黑
    M(NEW + 'echoes_of_lumen-hope-music-hopeful-piano-586991.mp3', 139.5, EV['cut71'], EV['cut61'] - 0.2, TOTAL + TAIL, fin=1.2, fout=2.5,
      dip=[EV['real']], ref=80.0, gap=-4, under=-17, host=-28),
]

SFX = {'rise': '上升-whoosh rise.mp3', 'whoosh': '转场-Whoosh.mp3', 'swish': '转场-Windy swish.mp3', 'gate': '重音-Gate Hit.mp3',
       'thud': '重音-Thud Hit C.mp3', 'dong': '重音-咚 重磅.mp3', 'rrise': '上声音-reverse rise.mp3'}

def sfx_plan():
    """一张表管全片音效：大重击只给大字/大数字；转场声只在换段落、换大画面；徽章轻点"""
    P = [
        # —— 开头
        ('蓄力→人声进', EV['voice_in'], 'rise', 0.55), ('冲进隧道', EV['voice_in'], 'thud', 0.40), ('攻克·问号炸开', EV['boom'], 'dong', 1.0),
        ('进新闻', EV['cut2'], 'whoosh', 0.35), ('截图换页', EV['split3'], 'swish', 0.22),
        ('进论文', EV['cut4'], 'swish', 0.25), ('719 停住', EV['land719'], 'gate', 0.45),
        ('未公开卡', EV['lock'] + 0.08, 'thud', 0.16), ('变金', EV['gold'] + 0.1, 'gate', 0.32),
        ('冲进论文', EV['dive'] + 0.3, 'swish', 0.38), ('ζ 出现', EV['dive'] + 0.35, 'thud', 0.32), ('黎曼卡', EV['rh'], 'thud', 0.11), ('霍奇卡', EV['hg'], 'thud', 0.11),
        ('数学研究卡', EV['neqA'] + 0.05, 'thud', 0.12), ('普通任务卡', EV['neqB'] + 0.05, 'thud', 0.12), ('≠', EV['neq'] + 0.05, 'gate', 0.18),
        ('进知识圈', EV['cut10'], 'whoosh', 0.3), ('写文章卡', EV['doc'] + 0.05, 'thud', 0.11), ('总结卡', EV['lst'] + 0.05, 'thud', 0.11),
        ('向内索取', EV['inward'] + 0.1, 'thud', 0.2), ('金光蓄力', EV['outward'] + 0.3, 'rise', 0.3), ('冲破边界', EV['outward'] + 0.3, 'gate', 0.38),
        ('新规律连线', EV['rule'], 'swish', 0.18),
        ('使用知识', EV['use'], 'thud', 0.15), ('创造·蓄力', EV['create'], 'rise', 0.5), ('参与创造知识', EV['create'], 'dong', 0.95),
        ('表情包', EV['meme'] + 0.08, 'gate', 0.45), ('片名·蓄力', EV['afs'], 'rise', 0.6), ('AI for Science', EV['afs'], 'dong', 1.0),
        ('转回国内', EV['bridge'], 'swish', 0.32),
    ]
    P += [(f'领域{j + 1}', t0 + 0.1, 'thud', 0.14) for j, t0 in enumerate(BADGE_T[:3])]
    P += [   # —— 国内 / 化工 / 死亡之谷
        ('研究院所', wt(22, '科研院所') + 0.05, 'thud', 0.14), ('高校', wt(22, '高校') + 0.05, 'thud', 0.14), ('科技企业', wt(22, '科技企业') + 0.05, 'thud', 0.14),
        ('章节卡·化工', EV['ch_in'], 'gate', 0.42), ('章节卡收', EV['cut26'], 'whoosh', 0.3),
        ('实验室→工厂', S[29]['start'] + 0.15, 'swish', 0.28), ('资源条', S[34]['start'], 'thud', 0.15),
        ('进山谷', EV['cut36'], 'swish', 0.22), ('曲线栽下去', EV['fall'], 'thud', 0.55), ('死亡之谷', EV['valley'], 'dong', 1.0),
    ]
    P += [   # —— 讯飞 3.0 Pro / 演示 / 400+
        ('徽章滑入', S[37]['start'] + 0.2, 'swish', 0.22), ('合作·扣上', EV['link'], 'thud', 0.28),
        ('进模型简介', EV['cut38'], 'whoosh', 0.3), ('标题高亮', S[38]['start'] + 1.35, 'thud', 0.1),
        ('进演示', EV['cut40'], 'swish', 0.2), ('流程条落下', EV['cut41'], 'swish', 0.2)] + \
         [(f'步骤·{n}', t0 + 0.05, 'thud', 0.12) for (n, i, w), t0 in zip(STEPS, ST_T)] + [
        ('进工具墙', EV['cut46'], 'whoosh', 0.28), ('工具墙·蓄力', EV['n400'], 'rise', 0.55), ('400+', EV['n400'], 'dong', 1.0),
        ('进工具库', EV['cut48'], 'swish', 0.15),
        ('数字工厂卡', EV['digi'], 'thud', 0.11), ('方案表卡', EV['early'], 'thud', 0.11), ('实验卡', EV['labv'], 'thud', 0.11),
        ('章节卡·生物', EV['ch2_in'], 'gate', 0.42), ('章节卡收', EV['cut51'], 'whoosh', 0.3),
    ]
    P += [   # —— 生物医药 / 蛋白质 / 发表
        ('进蛋白质', EV['cut54'], 'swish', 0.2), ('实验墙拉远', EV['cut55'] + 0.2, 'swish', 0.2),
        ('进讯飞项目', EV['cut56'], 'whoosh', 0.3), ('讯飞徽章', S[56]['start'] + 0.6, 'thud', 0.18),
        ('进指标', EV['cut59'], 'swish', 0.18), ('准确率', EV['m_acc'], 'thud', 0.14), ('稳定性', EV['m_stab'], 'thud', 0.14), ('活性', EV['m_act'], 'thud', 0.14),
        ('提升', EV['m_up'] + 0.15, 'gate', 0.26), ('论文落下', EV['pub'], 'thud', 0.28), ('盖章', EV['pub'] + 0.4, 'gate', 0.3),
        ('换曲·上扬', EV['cut61'], 'rrise', 0.3),
    ]
    P += [   # —— 总结 / 1024 / 结尾
        ('回顾卡1', EV['r_oai'], 'thud', 0.11), ('回顾卡2', EV['r_chem'], 'thud', 0.11), ('回顾卡3', EV['r_prot'], 'thud', 0.11),
        ('进总结', EV['cut63'], 'whoosh', 0.28), ('书飞进', EV['more'] - 0.1, 'swish', 0.22)] + \
         [(f'循环·{n}', EV[e], 'thud', 0.12) for n, ic, c, e, dx, dy in LOOP] + [
        ('循环接上', EV['s4'] + 0.9, 'gate', 0.2), ('进1024', EV['cut66'], 'whoosh', 0.3), ('真实场景', EV['real'], 'dong', 0.8),
        ('进场景', EV['cut68'], 'swish', 0.18)] + [(f'场景·{n}', t0, 'thud', 0.11) for (n, ic, c), t0 in zip(SCN, EV['sc'])] + [
        ('着落', EV['land'], 'thud', 0.14), ('回活动页', EV['cut70'], 'whoosh', 0.28),
    ]
    return P
