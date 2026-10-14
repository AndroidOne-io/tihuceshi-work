from pathlib import Path
import json
b=Path(__file__).resolve().parent.parent
p=json.load(open(b/'工程.json'))
s=(b/'制作资料/预览模板.html').read_text().replace('__DATA__',json.dumps(p,ensure_ascii=False).replace('<','\\u003c'))
(b/'双轨预览.html').write_text(s)
