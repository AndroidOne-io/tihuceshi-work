import pathlib,json,subprocess,concurrent.futures,os
base=pathlib.Path(__file__).resolve().parent.parent
def run(a):
 row,b,start,end=a;d=json.load(open(base/'制作资料'/f'{b}.json'))['data'];url=d['durl'][0]['url'];out=base/'素材'/f'{row:02d}_B站_{start}-{end}秒.mp4';env=os.environ.copy()
 for k in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy']:env.pop(k,None)
 with (base/'制作资料'/f'{row:02d}_B站截取.log').open('w') as f:
  r=subprocess.run(['ffmpeg','-hide_banner','-y','-ss',str(start),'-headers','Referer: https://www.bilibili.com/\r\nUser-Agent: Mozilla/5.0\r\n','-i',url,'-t',str(end-start),'-c:v','libx264','-preset','fast','-crf','18','-c:a','aac',str(out)],stdout=f,stderr=f,env=env,timeout=180)
 print(row,r.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:list(p.map(run,[(6,'BV1dKbz6kEkw',19,24),(15,'BV16d4y1g7dB',11,20),(28,'BV12a4y1G7Hp',0,20)]))
