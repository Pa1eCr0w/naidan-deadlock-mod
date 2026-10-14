from pathlib import Path
import zipfile
r=Path('work/naige-solid-install');c=r/'source';models=c/'models/heroes_wip/baba';mats=c/'materials/models/naige_continuous';models.mkdir(parents=True,exist_ok=True);mats.mkdir(parents=True,exist_ok=True)
for name,stem in [('baba_pigeon','normal'),('baba_pigeon_transform','transform')]:
 s=Path('work/naige-install/source/models/heroes_wip/baba',name+'.vmdl').read_text()
 for i in range(3):s=s.replace(f'models/heroes_wip/baba/naige_{stem}_lod{i}.fbx',f'models/naige_continuous/{stem}_lod{i}.fbx')
 (models/(name+'.vmdl')).write_text(s)
 s=Path('work/naige-install/source/materials/models/naige/naige_solid.vmat').read_text().replace('materials/models/naige/naige_albedo.png',f'materials/models/naige_continuous/{stem}_albedo.png')
 (mats/(stem+'.vmat')).write_text(s)
s=Path('work/naige-install/source/models/heroes_wip/baba/baba.vmdl').read_text()
for tag in ['folded','open']:
 for i in range(4):s=s.replace(f'models/heroes_wip/baba/naige_bench_{tag}_lod{i}.fbx',f'models/naige_continuous/bench_{tag}_lod{i}.fbx')
(models/'baba.vmdl').write_text(s)
with zipfile.ZipFile(r/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in c.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(c))
