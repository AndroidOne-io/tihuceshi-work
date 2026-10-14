from pathlib import Path
import json,subprocess,shutil,math,xml.etree.ElementTree as E,csv
from PIL import Image,ImageDraw,ImageFont
base=Path(__file__).resolve().parent.parent;src=base/'素材';media=base/'剪辑素材';media.mkdir(exist_ok=True)
fontpath='/System/Library/Fonts/STHeiti Medium.ttc'
def card(name,title,lines,portrait=False,transparent=False):
 im=Image.new('RGBA',(1920,1080),(0,0,0,0) if transparent else (241,239,231,255));d=ImageDraw.Draw(im)
 if transparent:
  d.rounded_rectangle((180,730,1740,990),radius=22,fill=(15,25,32,235));x,y=240,755;color='white'
 else:x,y=150,150;color='#172c36'
 if portrait:
  p=Image.open(src/'12_D01_参考图.png').convert('RGBA');p.thumbnail((330,330));im.paste(p,(145,150));x=530
 d.text((x,y),title,font=ImageFont.truetype(fontpath,64),fill=color)
 yy=y+115
 for line in lines:
  d.text((x,yy),line,font=ImageFont.truetype(fontpath,43),fill=color);yy+=76
 im.save(media/name);return name
card('11_SVG名词解释.png','SVG · 可缩放矢量图形',['可以理解成：用代码画图'],transparent=True)
card('12_西蒙与测试起源.png','Simon Willison · 西蒙·威利森',['2024 年 10 月提出鹈鹕测试','让模型生成「鹈鹕骑自行车」的 SVG','最初测试了 16 个模型'],portrait=True)
card('16_选择鹈鹕的原因.png','为什么是鹈鹕骑自行车？',['西蒙的想法：','训练数据里很可能没有现成的同类 SVG。','让模型自己完成这个陌生的组合。','来源：Simon Willison，2024-10-25'])
card('25_发明者的提醒.png','Simon Willison 的提醒',['用一张鹈鹕图比较不同厂商的模型，','可能并没有多少意义。','同一家族、不同推理档位的对比，','仍然能提供一些观察。'],portrait=True)
card('08_最高档两次失败.png','Opus 5.5 · max',['两次测试未生成结果','持续推理，触及输出上限','来源：Simon Willison，2026-09-22'])
# Transparent caption for the sticker beat; no unrelated style-reference pictures in timeline.
card('14_抽象组合.png','鹈鹕 ＋ 自行车',['鸡 ＋ 篮球'],transparent=True)
# Source SVGs remain editable; Quick Look provides native raster representations for the edit.
for p in sorted(src.glob('12_网页原图_*.svg')):
 dest=media/(p.stem+'.png')
 if not dest.exists():
  subprocess.run(['qlmanage','-t','-s','1600','-o',str(media),str(p)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  q=media/(p.name+'.png')
  if q.exists():q.rename(dest)
# All offsets use the existing narration cut. A standalone 9s insert follows the chicken/basketball line.
insert=round(72.0*30);gap=270;duration=6224+gap
shots=json.load(open(base/'制作资料/分镜清单.json'))
bounds={2:0,3:7.1,4:10.9333,5:14.4,6:21.0667,7:24.9,8:31,9:38.4,10:42.7667,11:48.1333,12:50.6667,13:65.1333,14:68.6333,15:72,16:72,17:79.8,18:83.6667,19:94,20:104.1,21:112.4667,22:125.6333,23:129.1667,24:136,25:141.6,26:146.9667,27:155.8667,28:163.9,29:176.5667,30:189.4667,31:202.5333}
def fr(t):return round(t*30)
def timeline(t):return fr(t)+(gap if fr(t)>=insert else 0)
clips=[]
def add(row,start,end,filename,source=0,audio=False,note=''):
 p=media/filename if (media/filename).exists() else src/filename
 a=timeline(start);b=timeline(end)
 if fr(start)<insert and fr(end)==insert:b=insert
 if row==15:a=insert;b=insert+gap
 clips.append({'row':row,'name':f'{row:02d} '+filename.split('_',1)[-1].rsplit('.',1)[0],'file':str(p.relative_to(base)),'start_frame':a,'duration_frames':b-a,'source_frame':fr(source),'audio':audio,'note':note})
add(3,7.1,10.9333,'03_D01_链接素材_1.mp4',1)
add(4,10.9333,14.4,'04_D01_链接素材_1.mp4',6)
add(5,14.4,21.0667,'05_D01_链接素材_1.mp4',1)
add(6,21.0667,24.9,'06_B站_19-24秒.mp4',0,note='原视频19–24秒，时间轴使用前3.83秒')
add(7,24.9,31,'07_D01_链接素材_1.mp4',0)
add(8,31,38.4,'08_最高档两次失败.png')
add(9,38.4,41.4,'09_D01_附件.mp4')
add(11,48.1333,50.6667,'11_SVG名词解释.png')
add(12,50.6667,55,'12_西蒙与测试起源.png')
add(12,55,60.3,'12_C01_参考图.png')
add(12,60.3,62.7,'12_网页原图_01.png')
add(12,62.7,65.1333,'12_网页原图_04.png')
add(13,65.1333,66.3,'12_网页原图_05.png')
add(13,66.3,67.5,'12_网页原图_09.png')
add(13,67.5,68.6333,'12_网页原图_11.png')
add(14,68.6333,72,'14_抽象组合.png')
add(15,72,72,'15_B站_11-20秒.mp4',0,True,note='独立插入9秒，保留素材原声')
add(16,75.4,79.8,'16_选择鹈鹕的原因.png')
add(17,79.8,83.6667,'04_D01_链接素材_2.mp4',2)
add(18,87.1,94,'18_D01_链接素材_1.mp4',2)
add(19,97.2,104.1,'19_发布会原素材.mp4',50)
add(20,104.1,112.4667,'20_D01_链接素材_1.mp4',1)
add(22,125.6333,129.1667,'22_D01_附件.mp4',0.4)
add(23,129.1667,136,'23_D01_附件.mp4',4)
add(24,137.4,141.5333,'24_D01_链接素材_1.mp4')
add(25,141.6,146.9667,'25_发明者的提醒.png')
add(26,150.6,155.8667,'26_D01_附件.mp4',2)
add(27,158.6,163.9,'27_网页原图_02.webp')
add(28,168.3,176.5667,'28_B站_0-20秒.mp4',0)
add(29,181.4,184.3333,'12_网页原图_07.png')
add(29,184.3333,186.6667,'03_D01_链接素材_1.mp4',4)
add(29,186.6667,189.4667,'29_D01_链接素材_1.mp4',16)
add(30,194.0667,198.9333,'30_D01_链接素材_1.mp4',2)
add(30,198.9333,202.5333,'30_E01_链接素材_1.mp4',3)
# Trim long selected video sections to directly usable numbered files. Original downloads are retained.
for i,c in enumerate(clips):
 p=base/c['file']
 if p.suffix.lower()=='.webp':
  dest=media/f"{c['row']:02d}_模型对比.png";Image.open(p).convert('RGB').save(dest);c['file']=str(dest.relative_to(base));p=dest
 if p.suffix.lower()=='.mp4' and c['row'] not in [6,15]:
  dest=media/f"{c['row']:02d}_{i+1:02d}_选用片段.mp4"
  if not dest.exists():
   cmd=['ffmpeg','-v','error','-y','-ss',str(c['source_frame']/30),'-i',str(p),'-t',str(c['duration_frames']/30),'-map','0:v:0','-an','-vf','fps=30','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
   subprocess.run(cmd,check=True)
  c['original_file']=c['file'];c['original_source_frame']=c['source_frame'];c['file']=str(dest.relative_to(base));c['source_frame']=0
# Keep narration self-contained without duplicating the 845MB source recording.
narr=base/'口播粗剪.mp4'
if not narr.exists():
 try:narr.hardlink_to(base.parent/'口播粗剪.mp4')
 except:shutil.copy2(base.parent/'口播粗剪.mp4',narr)
project={'name':'鹈鹕测试_分镜双轨','fps':30,'width':3840,'height':2160,'duration_frames':duration,'insert_frame':insert,'insert_duration_frames':gap,'narration':'口播粗剪.mp4','narration_duration_frames':6224,'clips':clips,'shots':shots}
(base/'工程.json').write_text(json.dumps(project,ensure_ascii=False,indent=2))
print('Timeline ready',len(clips),duration/30,flush=True)
