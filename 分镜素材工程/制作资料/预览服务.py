from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import os,re
os.chdir(Path(__file__).resolve().parent.parent)
class Handler(SimpleHTTPRequestHandler):
 def send_head(self):
  path=self.translate_path(self.path)
  if not os.path.isfile(path):return super().send_head()
  f=open(path,'rb');size=os.fstat(f.fileno()).st_size;start=0;end=size-1;r=self.headers.get('Range');self.chunk=None
  if r:
   m=re.match(r'bytes=(\d+)-(\d*)',r)
   if m:start=int(m[1]);end=min(int(m[2]) if m[2] else end,end)
   if start>=size:self.send_error(416);f.close();return None
   self.send_response(206);self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.chunk=end-start+1
  else:self.send_response(200)
  self.send_header('Content-type',self.guess_type(path));self.send_header('Content-Length',str(end-start+1));self.send_header('Accept-Ranges','bytes');self.end_headers();f.seek(start);return f
 def copyfile(self,source,out):
  remaining=self.chunk
  try:
   while remaining is None or remaining>0:
    b=source.read(256*1024 if remaining is None else min(256*1024,remaining))
    if not b:break
    out.write(b)
    if remaining is not None:remaining-=len(b)
  except (BrokenPipeError,ConnectionResetError):pass
 def log_message(self,*args):pass
print('http://127.0.0.1:8876/双轨预览.html',flush=True)
ThreadingHTTPServer(('127.0.0.1',8876),Handler).serve_forever()
