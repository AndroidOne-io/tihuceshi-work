# 科大讯飞 · AI for Science 剪辑代码

| 文件 | 内容 |
| --- | --- |
| `kx.py` | 包装库「科研观测台」：深蓝分层背景、讯飞青/琥珀配色、金属字/毛笔字（杨任东竹石体）/数字字、玻璃徽章与代码画图标、青色取景框、高亮条、透视卡片、圆形小窗、甩镜/故障/震动、视频输出 |
| `kongjing.py` | 代码空镜：数学宇宙（素数螺旋 + ζ 函数临界线轨迹）、数字化工厂（线框装置 + 管道粒子 + 扫描面）、蛋白质折叠 |
| `zeta.py` | ζ 函数（Borwein 算法，不依赖 mpmath） |
| `infographics.py` | 信息图与大字：向内索取/向外延伸、参与创造知识、AI for Science、死亡之谷、合作徽章、四个环节、五个场景、400+ |
| `shots.py` | 分镜表（71 个镜头：原表行、台词、画面类型、素材入出点/裁切框、处理、声音、停顿） |
| `align.py` → `align.json` | 口播逐字对齐：选用的录音片段 + 每个字的时间（sherpa-onnx SenseVoice） |
| `timeline.py` | 按对齐结果排时间线、出字幕、每个镜头的画面函数；出镜位目前是占位 |
| `render_v1.py` | 渲染第一版：`audio` 混音（口播拼接 + 合成音效，-14 LUFS），`video 段号 段数` 分段渲染画面 |

## 运行

```sh
cd 科大讯飞/代码
python3 render_v1.py align.json 输出目录 audio
python3 render_v1.py align.json 输出目录 video 0 2 &   # 两个进程并行
python3 render_v1.py align.json 输出目录 video 1 2 &
# 合并：ffmpeg concat 两段画面，再和 v1_mix.wav 合成
```

依赖：Python 3 + numpy + opencv + Pillow + ffmpeg；字体在 `交接资料/7_字体`。
重新对齐口播需要 sherpa-onnx v1.13.8 静态版、`sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17`、`silero_vad.onnx`（GitHub k2-fsa/sherpa-onnx releases），放在 `/home/claude/asr`。

## 进度（第一版）

- 画外音段落按真实口播卡点；出镜位和短画外音（不只是数量多 / 向内索取 / AI for Science / 死亡之谷 / 第 20、21 行）等出镜视频。
- 待补：两家 logo、蛋白质论文期刊截图、配乐。
- 字幕按实际念的出：「研究院所」「蛋白质实验项目」。
