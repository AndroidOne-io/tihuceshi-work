import json,pathlib,subprocess,concurrent.futures,re
base=pathlib.Path(__file__).resolve().parent.parent
rows=json.load(open(base/'制作资料/分镜表原始.json'))['data']['valueRange']['values']
tasks=[];shots=[]
def scan(v):
 if isinstance(v,list):
  for q in v:yield from scan(q)
 elif isinstance(v,dict):yield v
for n,row in enumerate(rows,1):
 if n==1 or not any(x is not None for x in row):continue
 shot={'row':n,'visual':row[0] or '', 'speech':row[1] or '', 'notes':[x for x in row[2:] if isinstance(x,str)],'assets':[]}
 for col,v in enumerate(row):
  for i,x in enumerate(scan(v),1):
   typ=x.get('type'); prefix=f'{n:02d}_{chr(65+col)}{i:02d}'
   if typ in ['attachment','embed-image']:
    ext=pathlib.Path(x.get('text','')).suffix if typ=='attachment' else '.png'
    name=prefix+('_附件' if typ=='attachment' else '_参考图')+(ext or '.bin')
    dest=base/'素材'/name
    cmd=['lark-cli','api','GET',f"/open-apis/drive/v1/medias/{x['fileToken']}/download",'--output',str(dest.relative_to(pathlib.Path.cwd()))]
    task={'row':n,'type':typ,'name':name,'cmd':cmd,'token':x['fileToken']}
   elif typ=='url':
    url=x['link'];name=prefix+'_链接素材'
    task={'row':n,'type':'url','url':url,'name':name}
    if 'simonwillison.net' not in url:
     task['cmd']=['yt-dlp','--no-update','--socket-timeout','25','--retries','2','--write-info-json','--merge-output-format','mp4','-f','bv*[height<=1080]+ba/b[height<=1080]/best','-o',str(base/'素材'/f'{name}_%(playlist_index|1)s.%(ext)s'),url]
     if n==6:task['cmd']+=['--download-sections','*19-24','--force-keyframes-at-cuts']
     if n==15:task['cmd']+=['--download-sections','*11-20','--force-keyframes-at-cuts']
     if n==19:task['cmd']+=['--download-sections','*60-90','--force-keyframes-at-cuts']
     if n==28:task['cmd']+=['--download-sections','*0-20','--force-keyframes-at-cuts']
   else:continue
   shot['assets'].append(task);tasks.append(task)
 shots.append(shot)
(base/'制作资料/分镜清单.json').write_text(json.dumps(shots,ensure_ascii=False,indent=2))
def run(t):
 if 'cmd' not in t:return {'name':t['name'],'status':'webpage','url':t.get('url')}
 log=base/'制作资料'/(t['name']+'.log')
 try:
  with log.open('w') as f:r=subprocess.run(t['cmd'],stdout=f,stderr=f,timeout=500)
  result={'name':t['name'],'code':r.returncode}
 except Exception as e:result={'name':t['name'],'error':str(e)}
 print(json.dumps(result,ensure_ascii=False),flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 results=list(pool.map(run,tasks))
(base/'制作资料/下载结果.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
