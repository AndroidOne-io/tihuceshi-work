from PIL import Image,ImageDraw,ImageFont
import pathlib,subprocess,json
base=pathlib.Path(__file__).resolve().parent.parent;out=base/'制作资料/抽帧';out.mkdir(exist_ok=True)
files=sorted(base.glob('素材/*.mp4'));font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',17)
for chunk in range(0,len(files),8):
 board=Image.new('RGB',(960,200*min(8,len(files)-chunk)),(225,225,225));draw=ImageDraw.Draw(board)
 for row,p in enumerate(files[chunk:chunk+8]):
  dur=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(p)]))['format']['duration'])
  for col,t in enumerate([min(0.7,dur*.1),dur*.45,dur*.8]):
   f=out/f'{p.stem}_{col}.jpg';subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=310:160:force_original_aspect_ratio=decrease','-y',str(f)],check=True)
   im=Image.open(f);board.paste(im,(col*320,row*200+30));draw.text((col*320,row*200+10),f'{p.name[:21]} {t:.1f}s',fill='black',font=font)
 board.save(out/f'contact_{chunk//8}.jpg')
