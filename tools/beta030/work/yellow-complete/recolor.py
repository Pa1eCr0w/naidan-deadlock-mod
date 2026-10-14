from pathlib import Path
from PIL import Image
import numpy as np,json,zipfile
r=Path('work/yellow-complete');d=r/'source/models/heroes_wip/baba/materials';d.mkdir(parents=True,exist_ok=True);report={}
for name,stem in [('bench','baba_bench_color_tga_f7ef6365'),('accessories','baba_accessories_color_tga_36d14417')]:
 im=Image.open(r/(name+'.png')).convert('RGBA');a=np.array(im);h=np.array(im.convert('RGB').convert('HSV')); mask=((h[:,:,0]>=170)&(h[:,:,0]<=254)&(h[:,:,1]>=15))
 if name=='bench':mask |= (h[:,:,0]<15)&(h[:,:,1]>=15)&(h[:,:,1]<130)
 # Preserve original value and saturation; recolor the purple/pink family to warm yellow.
 h[:,:,0][mask]=36
 rgb=np.array(Image.fromarray(h,'HSV').convert('RGB'));out=a.copy();out[:,:,:3][mask]=rgb[mask]
 assert np.array_equal(out[~mask],a[~mask]) and np.array_equal(out[:,:,3],a[:,:,3]);assert mask.sum()>1000
 Image.fromarray(out).save(d/(stem+'.png'));preview=Image.fromarray(out);preview.thumbnail((900,900));preview.save(r/(name+'-yellow-preview.png'))
 template=Path('work/final-brand/ui-source/panorama/images/heroes/baba_mm_psd.vtex').read_text().replace('panorama/images/heroes/baba_mm_psd.png',f'models/heroes_wip/baba/materials/{stem}.png').replace('"128"','"4096"').replace('"RGBA8888"','"DXT5"').replace('"m_bNoLod" "bool" "1"','"m_bNoLod" "bool" "0"')
 # Box mip generation is the native Source 2 default for color maps.
 pos=template.index('"m_mipAlgorithm"');template=template[:pos]+template[pos:].replace('"None"','"Box"',1)
 (d/(stem+'.vtex')).write_text(template);report[name]={'pixelsChanged':int(mask.sum()),'total':int(mask.size),'untouchedExact':True,'alphaExact':True}
(r/'texture-report.json').write_text(json.dumps(report,indent=2))
with zipfile.ZipFile(r/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in (r/'source').rglob('*'):
  if p.is_file():z.write(p,p.relative_to(r/'source'))

print(report)
