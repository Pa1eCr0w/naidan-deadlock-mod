from pathlib import Path
import zipfile
r=Path('work/naige-all');c=r/'source';d=c/'models/naige_all';d.mkdir(parents=True,exist_ok=True)
base=Path('work/naige-spirit-install/source/models/naige_spirit/baba_pigeon_pickscreen_a.vmdl').read_text()
for n in ['picker','effect']:(d/(n+'.vmdl')).write_text(base.replace('baba_pigeon_pickscreen_a',n).replace('models/naige_spirit/naige_spirit.fbx',f'models/naige_all/{n}.fbx'))
s=(r/'ghost_pigeon.vmdl').read_text().replace('models/particle/','models/naige_all/').replace('ghost_pigeon_ghost_pigeon.dmx','ghost.fbx');(d/'ghost.vmdl').write_text(s)
p=c/'particles/abilities/baba/baba_homing_pigeon_lock_debuff_pigeon_attack.vpcf';p.parent.mkdir(parents=True,exist_ok=True)
s=(r/'attack.vpcf').read_text().replace('models/particle/ghost_pigeon.vmdl','models/naige_all/ghost.vmdl');import re
s,n=re.subn(r'\s*m_hOverrideMaterial = resource:"models/npc_units/neutral_pigeon/materials/neutral_pigeon.vmat"','',s);assert n==1;p.write_text(s)
with zipfile.ZipFile(r/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in c.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(c))
