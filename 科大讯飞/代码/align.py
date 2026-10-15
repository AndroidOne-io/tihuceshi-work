# 口播逐字对齐：选定的录音片段 → 每个字的时间
import os, re, json, subprocess, difflib, sys
ASR = '/home/claude/asr'
BIN = f'{ASR}/sherpa-onnx-v1.13.8-linux-x64-static/bin/sherpa-onnx-offline'
MD = f'{ASR}/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17'
SRC16 = f'{ASR}/vo16.wav'

# 选用的录音：(片段起, 片段止, 这段里实际念的脚本原文, 要用的那部分)
TAKES = [
 (8.95, 17.05, 'OpenAI突然公开了一个叫 OpenAI Math 的项目。在这个项目里，OpenAI展示了由AI模型探索得到的大量数据研究成果。', 'OpenAI突然公开了一个叫 OpenAI Math 的项目。在这个项目里，'),
 (18.50, 22.95, 'OpenAI展示了由AI模型探索得到的大量数学研究成果。', None),
 (23.20, 27.30, '公开内容包括数百项数学成果，覆盖数论带和。', '公开内容包括数百项数学成果，'),
 (28.00, 31.35, '覆盖数论、代数几何、理论计算机等多个方向。', None),
 (46.25, 53.00, '我国的科研院所、高校和科技企业一直在积极探索，并已将AI应用于真实的科研流程之中。', None),
 (87.00, 106.50, '先看化工研发，有个让所有研发人员都头痛的环节。就是把实验室里做成功的方案，变成工厂里真正能稳定运行的工艺。哪怕只是一个催化反应，都要经历实验室多个严苛的试验环节。工程师需要不断调整参数、优化流程。而每多试一次，都要投大量的时间、材料和设备资源。', None),
 (125.40, 132.75, '科大讯飞与中科院大连化物所等单位合作研发的智能化工大模型3.0 Pro，解决的就是这些专业问题。', None),
 (135.10, 147.10, '以流程设计或工艺优化为例，工程师提出需求后，3.0 Pro可以拆解任务，判断出需要计算的参数、调用专业工具和模拟软件，最后再分析核对结果，给出可行的方案和建议。', None),
 (148.45, 154.45, '目前，这套系统已经集成超过400个化工智能体和工具，支持复杂化工任务的执行。', None),
 (158.60, 170.60, '而生物医药领域，也有类似的难题。如何设计出一个满足特定功能的蛋白质，一直是生物医药领域非常复杂的问题。因为蛋白质结构高度复杂，同样需要通过大量实验不断验证。', None),
 (183.45, 189.05, '科大讯飞参与的AI蛋白质设计项目，AI模型可以辅助科学家进行蛋白质结构和序列设计，', None),
 (190.90, 193.60, '帮助科研人员探索更优的蛋白质方案。', None),
 (197.40, 202.90, '相关成果已经在功能预测准确率、稳定性、活性等指标上取得提升，', None),
 (202.95, 204.95, '并发表于国际学术期刊。', None),
]
# 第9行前半句「面对科研周期长、实验成本高、专业门槛高等难题，」只在 37.6 那一遍里完整
TAKES.insert(4, (37.55, 42.75, '面对科研周期长、实验成本高、专业门槛高等难题，我国的研究院所。', '面对科研周期长、实验成本高、专业门槛高等难题，'))

def norm_chars(s):
    """把脚本拆成「可对齐字符」列表：汉字、数字、字母串各算一个"""
    out = []
    for m in re.finditer(r'[一-鿿]|[A-Za-z]+|\d+(?:\.\d+)?', s):
        out.append((m.group(0).lower(), m.start(), m.end()))
    return out

NUM = {'三点零': '3.0', '四百': '400'}
def asr(a, b, tag):
    wav = f'{ASR}/take_{tag}.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a}', '-to', f'{b}', '-i', SRC16, wav], check=True)
    r = subprocess.run([BIN, f'--sense-voice-model={MD}/model.int8.onnx', '--sense-voice-use-itn=1', f'--tokens={MD}/tokens.txt', '--num-threads=2', wav],
                       capture_output=True, text=True)
    js = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith('{')][-1]
    d = json.loads(js)
    toks = []
    for tk, ts in zip(d['tokens'], d['timestamps']):
        tk = tk.strip().lower()
        if tk: toks.append((tk, a + ts))
    return d['text'], toks

def align_take(i, take):
    a, b, said, use = take
    text, toks = asr(a, b, i)
    sc = norm_chars(said)
    S = [c for c, _, _ in sc]; T = [t for t, _ in toks]
    sm = difflib.SequenceMatcher(None, S, T, autojunk=False)
    times = [None] * len(S)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): times[blk.a + k] = toks[blk.b + k][1]
    # 没对上的字：前后插值
    known = [(k, v) for k, v in enumerate(times) if v is not None]
    for k in range(len(times)):
        if times[k] is None:
            prev = max([kv for kv in known if kv[0] < k], default=None, key=lambda x: x[0])
            nxt = min([kv for kv in known if kv[0] > k], default=None, key=lambda x: x[0])
            if prev and nxt: times[k] = prev[1] + (nxt[1] - prev[1]) * (k - prev[0]) / (nxt[0] - prev[0])
            elif prev: times[k] = prev[1] + 0.2 * (k - prev[0])
            elif nxt: times[k] = nxt[1] - 0.2 * (nxt[0] - k)
    matched = sum(1 for blk in sm.get_matching_blocks() for _ in range(blk.size))
    # 要用的部分
    lo, hi = 0, len(said)
    if use:
        lo = said.index(use); hi = lo + len(use)
    chars = [(c, s0, e0, t) for (c, s0, e0), t in zip(sc, times) if s0 >= lo and e0 <= hi]
    return {'a': a, 'b': b, 'asr': text, 'said': said, 'use': said[lo:hi], 'chars': chars, 'match': matched / max(1, len(S))}

if __name__ == '__main__':
    out = [align_take(i, tk) for i, tk in enumerate(TAKES)]
    for o in out:
        print(f"{o['a']:7.2f} 对上 {o['match']:.0%}  {o['use'][:24]}…  首字 {o['chars'][0][3]:.2f}  末字 {o['chars'][-1][3]:.2f}")
    json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
