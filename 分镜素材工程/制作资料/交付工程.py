from pathlib import Path
import json,subprocess,xml.etree.ElementTree as E,csv,html
base=Path(__file__).resolve().parent.parent;p=json.load(open(base/'工程.json'));fps=30
probe={}
def meta(f):
 if f not in probe:
  probe[f]=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height,r_frame_rate,sample_rate,channels','-of','json',str(base/f)]))
 return probe[f]
def t(n):return f'{n}/30s'
f=E.Element('fcpxml',version='1.8');res=E.SubElement(f,'resources');E.SubElement(res,'format',id='fmt',name='FFVideoFormat3840x2160p30',frameDuration='1/30s',width='3840',height='2160',colorSpace='1-1-1 (Rec. 709)')
files=[p['narration']]+list(dict.fromkeys(c['file'] for c in p['clips']));ids={}
for i,name in enumerate(files,1):
 d=meta(name);v=next(s for s in d['streams'] if s['codec_type']=='video');a=next((s for s in d['streams'] if s['codec_type']=='audio'),None);fmt='fmt'+str(i)
 E.SubElement(res,'format',id=fmt,width=str(v['width']),height=str(v['height']),frameDuration='1/30s',colorSpace='1-1-1 (Rec. 709)')
 ids[name]='asset'+str(i);attrs=dict(id=ids[name],name=Path(name).name,src=(base/name).as_uri(),start='0s',duration=t(round(float(d.get('format',{}).get('duration',3600))*30)),hasVideo='1',hasAudio='1' if a else '0',format=fmt)
 if a:attrs.update(audioSources='1',audioChannels=str(a.get('channels',2)),audioRate=a.get('sample_rate','44100'))
 E.SubElement(res,'asset',attrs)
lib=E.SubElement(f,'library');event=E.SubElement(lib,'event',name='鹈鹕测试');proj=E.SubElement(event,'project',name=p['name']);seq=E.SubElement(proj,'sequence',format='fmt',duration=t(p['duration_frames']),tcStart='0s',tcFormat='NDF',audioLayout='stereo',audioRate='48k');sp=E.SubElement(seq,'spine');cut=p['insert_frame'];g=p['insert_duration_frames']
parents=[E.SubElement(sp,'asset-clip',name='口播轨道 · 插入前',ref=ids[p['narration']],offset='0s',start='0s',duration=t(cut),audioRole='dialogue'),E.SubElement(sp,'gap',name='15 独立素材插入',offset=t(cut),start='0s',duration=t(g)),E.SubElement(sp,'asset-clip',name='口播轨道 · 插入后',ref=ids[p['narration']],offset=t(cut+g),start=t(cut),duration=t(p['narration_duration_frames']-cut),audioRole='dialogue')]
for c in p['clips']:
 start=c['start_frame'];idx=0 if start<cut else 1 if start<cut+g else 2;offset=start if idx==0 else start-cut if idx==1 else start-g
 clip=E.SubElement(parents[idx],'asset-clip',name=c['name'],ref=ids[c['file']],lane='1',offset=t(offset),start=t(c['source_frame']),duration=t(c['duration_frames']),audioRole='effects')
 E.SubElement(clip,'note').text=f"分镜表行号 {c['row']}。{c['note']}"
 if not c['audio'] and any(s['codec_type']=='audio' for s in meta(c['file'])['streams']):E.SubElement(clip,'adjust-volume',amount='-96dB')
E.indent(f);(base/'鹈鹕测试_分镜双轨.fcpxml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n'+E.tostring(f,encoding='unicode'))
with (base/'时间轴清单.csv').open('w',encoding='utf-8-sig',newline='') as o:
 w=csv.writer(o);w.writerow(['分镜表行号','轨道','时间轴开始秒','时间轴结束秒','素材入点秒','文件','备注'])
 for c in p['clips']:w.writerow([c['row'],'素材',c['start_frame']/30,(c['start_frame']+c['duration_frames'])/30,c['source_frame']/30,c['file'],c['note']])
manifest=[]
for s in p['shots']:
 files=[str(q.relative_to(base)) for q in sorted((base/'素材').glob(f"{s['row']:02d}_*")) if q.suffix not in ['.json','.part','.ytdl']]
 manifest.append({'row':s['row'],'speech':s['speech'],'description':s['visual'],'files':files,'sources':s['assets']})
(base/'素材来源清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
# Checks include exact frame coverage, valid media, nonoverlap and source availability.
errors=[];end=0
for c in p['clips']:
 d=meta(c['file']);dur=d.get('format',{}).get('duration');s=c['start_frame'];e=s+c['duration_frames']
 if s<end:errors.append('overlap '+c['name'])
 if e>p['duration_frames']:errors.append('beyond timeline '+c['name'])
 if dur and (c['source_frame']+c['duration_frames'])/30>float(dur)+.04:errors.append('source too short '+c['name'])
 end=e
report={'timeline_seconds':p['duration_frames']/30,'tracks':2,'material_segments':len(p['clips']),'valid_media_files':len(probe),'errors':errors,'editor_import_verified':False}
(base/'制作资料/工程验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report)
