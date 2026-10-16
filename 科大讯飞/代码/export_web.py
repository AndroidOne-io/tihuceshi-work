# 网页版导出：把时间线、事件表、场景参数、静态图、混好的音轨导出到 科大讯飞/网页版/
#   python3 export_web.py            # 全部（时间线 + 图片 + 音轨）
#   python3 export_web.py data       # 只导时间线和参数（改了停顿/口播/事件后跑这个，再跑一次 audio）
#   python3 export_web.py audio      # 只重混音轨
# 画面本身在网页里实时画（网页版/scenes.js），这里只导出它需要的数据和重效果图片。
import sys, os, json, subprocess
HERE_ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE_); os.chdir(HERE_)
WHAT = sys.argv[1] if len(sys.argv) > 1 else 'all'
WEB = os.path.join(HERE_, '..', '网页版'); AS = os.path.join(WEB, 'assets'); os.makedirs(AS, exist_ok=True)
TMP = os.path.join(WEB, '_tmp'); os.makedirs(TMP, exist_ok=True)
sys.argv = ['full.py', 'align.json', TMP, 'none']
__file__ = os.path.join(HERE_, 'full.py')
exec(open(__file__, encoding='utf-8').read())
from PIL import Image as _PILImage

def r3(x):
    if isinstance(x, dict): return {str(k): r3(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [r3(v) for v in x]
    if isinstance(x, np.ndarray): return r3(x.tolist())
    if isinstance(x, (np.floating, float)): return round(float(x), 4)
    if isinstance(x, (np.integer,)): return int(x)
    return x

# ---------------------------------------------------------------- 1. 时间线与参数
if WHAT in ('all', 'data'):
    import hook as _hook, kongjing as _kj
    D = dict(
        W=W, H=H, FPS=FPS, PRE=PRE, TOTAL=TOTAL, TAIL=TAIL, DUR=DUR,
        shots=[dict(i=s['i'], row=s['row'], start=s['start'], end=s['end'], chars=[c[1] for c in s['chars']], text=s['text']) for s in shots],
        EV=EV, subs=[[a, txt, i, b] for a, txt, i, b in SUBS], NO_SUB=sorted(NO_SUB), CUTS=CUTS, QUIET=sorted(QUIET),
        HOST_SHOTS=sorted(HOST_SHOTS), SPEED=SPEED,
        cam=[[a0, a1, o, SPEED[sr]] for a0, a1, o, sr in audio_pieces if sr in ('cam', 'cam_slow')],
        BADGE_T=BADGE_T, FIELDS=[[x, y] for n, c, sz, ts, x, y, w in FIELDS],
        DROPS=DROPS, PX=PX, PY=PY, SPARK=SPARK, KC=KC, KR=KR, KN=KN, GRID=GRID, STARS=STARS, DUST=DUST, PART=PART,
        PFLOW=PFLOW, SP37=SP37, MODS=MODS, ST_X=ST_X, ST_Y=ST_Y, ST_T=ST_T,
        TW=TW, TH=TH, GX=GX, GY=GY, NC=NC, NR=NR, LIT_ORDER=LIT_ORDER, PWg=PW_, PHg=PH_, PGg=PG_, NCG=NCG, NRG=NRG,
        STRUCT=STRUCT, FLOW=FLOW, FL_PTS=FL_PTS, MET_X=MET_X, BOOK_P=BOOK_P, LC=LC, LRX=LRX, LRY=LRY,
        LOOP=[[e, dx, dy] for n, ic, c, e, dx, dy in LOOP], SCN_P=SCN_P, REV=[[e, x, y, ang] for im, e, x, y, ang in REV], END_DUST=END_DUST,
        hook=dict(TU_A=_hook.TU_A, TU_R=_hook.TU_R, TU_Z=_hook.TU_Z, TU_C=_hook.TU_C, QP=_hook.QP, QS=_hook.QS, QV=_hook.QV),
        cosmos=dict(P=_kj._UL[_kj._PR] * 9.0, R=np.hypot(_kj._UL[_kj._PR][:, 0], _kj._UL[_kj._PR][:, 1]),
                    Z=np.c_[_kj._ZT, _kj._ZV.real, _kj._ZV.imag], ZEROS=_kj._ZEROS),
        factory=dict(L=[ln for ln in _kj._FL], PIPES=_kj._PIPES),
        protein=dict(P=_kj._PROT, K=_kj._PK, C=_kj._chain_colors(len(_kj._PROT)), S=_kj._STRAIGHT),
    )
    with open(os.path.join(WEB, 'data.js'), 'w', encoding='utf-8') as f:
        f.write('// 由 代码/export_web.py 生成，不要手改\nwindow.D = ' + json.dumps(r3(D), ensure_ascii=False, separators=(',', ':')) + ';\n')
    print('data.js ok')

# ---------------------------------------------------------------- 2. 静态图（卡片、徽章、大字、背景、截图、工具墙…）
def save(name, v, jpg=False, q=88):
    p = os.path.join(AS, name + ('.jpg' if jpg else '.png'))
    if isinstance(v, _PILImage.Image): im = v
    else:
        a = np.clip(np.asarray(v, np.float32), 0, 255).astype(np.uint8)
        im = _PILImage.fromarray(a, 'RGBA' if a.shape[2] == 4 else 'RGB')
    if jpg: im.convert('RGB').save(p, quality=q)
    else: im.save(p, optimize=True)

if WHAT in ('all', 'img'):
    G = globals()
    single = ['B_AI', 'B_AI_G', 'B_FAC', 'B_HG', 'B_LAB', 'B_RH', 'CH', 'CH2', 'C_DOC', 'C_LST', 'FAC_TAG', 'GHOST', 'LAB_TAG', 'LBL', 'LOCK',
              'MEME_CARD', 'N400', 'NEQ', 'NEQ_A', 'NEQ_B', 'PAPER_BIG', 'PAPER_G', 'P_DL', 'P_XF', 'SEAL', 'TRY', 'TRY2',
              'T_AFS', 'T_CREATE', 'T_REAL', 'T_USE', 'T_VALLEY', 'W_IN', 'W_OUT']
    lists = ['BOOKS', 'ENT_IMG', 'FIMG', 'LOOP_IM', 'MET_IM', 'PG', 'PW', 'RES_IC', 'RES_T', 'REV_C', 'SCN_IM', 'ST_DONE', 'ST_OFF', 'ST_ON']
    for k in single: save(k, G[k])
    for k in lists:
        for j, v in enumerate(G[k]): save(f'{k}_{j}', v)
    for k in ['BG', 'BG37', 'BG47', 'BG5', 'BG6', 'BG63', 'BG67', 'BG7', 'BG8', 'BG9', 'BGP', 'BG_PAGE', 'BG_Z']: save(k, G[k], jpg=True, q=90)
    save('BG_VALLEY', bg_gild(backdrop=V11.get(230.0), dim=0.30, key='valley', leak_col=CORAL, k_leak=0.08), jpg=True, q=90)
    for k in ['IMG1', 'IMG2', 'IMG5', 'IMG8', 'IMG9', 'REC_TBL', 'MEME']: save(k, G[k], jpg=True, q=90)
    save('GRID_IM', GRID_IM, jpg=True, q=85)
    save('WALL_DIM', WALL_DIM, jpg=True, q=82); save('WALL_LIT', WALL_LIT, jpg=True, q=82)
    save('BG_PUB', bg_gild(key='pub', leak=(0.5, 0.2), leak_col=GOLD, k_leak=0.09), jpg=True, q=90)
    L = sorted(os.listdir(AS))
    open(os.path.join(WEB, 'assets.js'), 'w', encoding='utf-8').write('// 由 export_web.py 生成\nwindow.ASSETS = ' + json.dumps(L) + ';\n')
    print('assets ok', len(L))

# ---------------------------------------------------------------- 3. 混好的音轨（人声 + 配乐 + 音效，-14 LUFS）
if WHAT in ('all', 'audio'):
    voice, music, sfx, rep, v_db, vmask = build_audio()
    mix = voice + music + sfx
    # 恢复旧版防削波处理，先留峰值余量，再做响度归一。
    peak = float(np.abs(mix).max())
    mix *= min(1.0, .90 / max(peak, 1e-9))
    with wave.open(os.path.join(TMP, 'raw.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(TMP, 'raw.wav'), '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', '44100',
                    '-c:a', 'aac', '-b:a', '192k', os.path.join(WEB, 'mix.m4a')], check=True)
    json.dump(r3([[n, t, k] for n, t, k in rep]), open(os.path.join(WEB, 'sfx_cues.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('mix.m4a ok')
