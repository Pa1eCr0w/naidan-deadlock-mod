from pathlib import Path
from PIL import Image
import numpy as np,zipfile,json
r=Path('work/yellow-complete');report={}
for n,stem in [('bench','baba_bench_color_tga_f7ef6365'),('accessories','baba_accessories_color_tga_36d14417')]:
 a=np.array(Image.open(r/f'source/models/heroes_wip/baba/materials/{stem}.png').convert('RGBA')).astype(float);b=np.array(Image.open(r/(n+'-roundtrip.png')).convert('RGBA')).astype(float);assert a.shape==b.shape
 err=abs(a-b);assert err.mean()<3 and np.quantile(err,.99)<12,(n,err.mean(),np.quantile(err,.99))
 report[n]={'shape':list(a.shape),'compressionMeanError':float(err.mean()),'errorP99':float(np.quantile(err,.99))}
 im=Image.fromarray(b.astype('uint8')).convert('RGB');im.thumbnail((900,900));im.save(r/(n+'-yellow-preview.png'))
with zipfile.ZipFile(r/'compiled.zip') as z:
 for n in z.namelist():
  if n.endswith(('/','\\')):continue
  p=r/'stage'/n.replace('\\','/');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
(r/'texture-roundtrip-report.json').write_text(json.dumps(report,indent=2));print(report)
