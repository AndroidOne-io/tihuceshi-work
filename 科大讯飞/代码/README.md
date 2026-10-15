# 科大讯飞 · AI for Science 成片工程

整条视频（约 4 分 18 秒）全部由这里的代码生成：画面逐帧渲染，口播、配乐、音效按同一张事件表对齐。
改任何一处（停顿、配乐、某个镜头的画面）后重新渲染即可，前后衔接自动跟着走。

## 一、目录

| 位置 | 内容 |
| --- | --- |
| `科大讯飞/素材/` | 画面素材 1–11 号、口播（`口播/非出镜美化.wav` 画外音、`1080-压缩版.mp4` 出镜、`科大讯飞1024结尾-声音克隆.mp3` 第 20 行） |
| `音乐素材/`（仓库根目录） | 新找的 Pixabay 配乐（讲解 / 悬念 / 解决方案 / 温暖结尾） |
| `aliang2052/Tempsucai` → `materials/audio/音乐素材/` | 旧库配乐 21 首 + 音效 7 个（冷开、包袱、片名和全部音效仍用这里的） |
| `交接资料/7_字体/` | 字体：优设标题黑、杨任东竹石体、得意黑、Bebas Neue |

## 二、代码文件

| 文件 | 作用 |
| --- | --- |
| `shots.py` | 分镜表：71 个镜头（原表行号、台词、画面类型、素材入出点、处理说明、声音、停顿） |
| `align.py` → `align.json` | 口播逐字对齐（sherpa-onnx SenseVoice）：每段录音选用哪一条、每个字在第几秒 |
| `timeline.py` | 按对齐结果排时间线（含停顿）、出字幕、出镜画面取帧（原片是镜像录的，已水平翻回） |
| `full.py` | **主程序**：事件表 `EV`、第 1–18 镜画面、混音、渲染。`PAUSE_OVR` 是全片停顿表 |
| `seg3_vis.py` | 第 19–36 镜：国内科研 → 01 化工研发 → 实验室到工厂 → 死亡之谷 |
| `seg4_vis.py` | 第 37–50 镜：合作徽章 → 3.0 Pro 简介 → 演示五步流程 → 400+ 工具墙 → 02 生物医药 |
| `seg5_vis.py` | 第 51–61 镜：生物医药 → 蛋白质 → 讯飞蛋白质设计 → 指标 → 发表 → 品牌句 |
| `seg6_vis.py` | 第 62–71 镜：回顾 → AI 循环 → 1024 → 真实场景 → 五个场景 → 结尾 |
| `sound.py` | **整片声音规划**：每段配乐（哪首、从曲子第几秒起、对齐到哪个画面事件、三档电平）+ 全片音效表 |
| `hook.py` / `kongjing.py` / `zeta.py` | 冷开问号隧道、代码空镜（数学宇宙、数字工厂、蛋白质）、ζ 函数 |
| `kx.py` / `v3.py` / `v4.py` | 包装库：背景、半透明卡片和徽章、金属字 / 毛笔字、透视截图、甩镜、字幕 |
| `export.py` | 导出字幕 SRT、三条分轨（人声 / 配乐 / 音效）、时间线 cue 表 |

## 三、在本地渲染（Mac）

```sh
# 1. 装工具（只需一次）
brew install ffmpeg git-lfs python
git lfs install
python3 -m pip install numpy opencv-python pillow matplotlib

# 2. 拉工程（视频素材在 Git LFS 里，必须 git lfs pull）
git clone -b xunfei-ai4s-edit https://github.com/AndroidOne-io/tihuceshi-work.git
cd tihuceshi-work && git lfs pull

# 3. 先试渲染 2 秒，确认环境没问题
cd 科大讯飞/代码
python3 render_all.py 4 45 47          # → 科大讯飞/成片输出/试渲染_45-47.mp4

# 4. 渲染整条
python3 render_all.py 4                # → 科大讯飞/成片输出/成片.mp4

# 5.（可选）导出字幕、分轨、cue 表
python3 export.py align.json ../成片输出
```

`render_all.py` 的第一个数字是并行进程数，每个进程约占 2.5 GB 内存：16 GB 内存用 4，32 GB 可以用 6–8。
画面按帧号切成几段并行渲染，再无损拼接，接缝处不丢帧、不重帧；最后会打印成片总帧数，应和「应为」一致。

单独调试：`python3 full.py align.json 输出目录 stills`（关键帧截图）、`check 起秒 止秒`（声画对位图 + 配乐电平）。

## 四、常改的地方

- **停顿长短**：`full.py` 第 11 行 `PAUSE_OVR = {镜号: 秒数}`，停顿加在该镜口播之后，后面所有画面、音乐、音效自动顺延。
- **换配乐**：改 `sound.py` 里对应那一行 `M(曲子, 曲内对齐点, 对齐到的事件, 起, 止, ...)`。
  `gap / under / host` 分别是停顿、画面口播、真人口播时配乐比人声低多少 dB。
- **音效**：`sound.py` 的 `sfx_plan()`，一行一个：名称、事件时间、音效、音量。音效按峰值对齐画面事件。
- **某个镜头的画面**：在对应的 `segN_vis.py` 里找 `VIS.update({...})`，镜号对应画面函数。

## 五、声音规划（当前版本）

| 段落 | 配乐 | 卡点 |
| --- | --- | --- |
| 冷开 | Dance for me walls | 「攻克」炸开 |
| OpenAI Math 新闻、讲解 | Tech Explainer (Modern Digital) | 「参与创造知识」前整段断掉 |
| 包袱 | Fluffing a Duck | 表情包出现 |
| 片名 | Breath and Life | 爆点对准片名 |
| 国内、化工、死亡之谷 | Documentary Suspense | 曲线栽下去那一刻断掉 |
| 讯飞 3.0 Pro、演示、400+ | Futuristic View | 曲子起来那一下对准 3.0 Pro 截图 |
| 生物医药 | Inspiring Technology | 开头重拍对准 02 章节卡 |
| 总结、1024、结尾 | Hope Music Hopeful Piano | 高潮起在 1024，回落对准最后一句 |

电平：真人口播约 −30 dB、画面口播约 −17 dB、停顿和大字约 −5 dB（相对人声）；整片 −14 LUFS。

## 六、待补

- 科大讯飞、中科院大连化物所 logo（现在是名字 + 图标的徽章）
- 蛋白质论文的期刊页截图（现在是通用论文落下 + 盖章）
- 徽章弹出、打勾、键盘、纸张、「叮」这几个音效
