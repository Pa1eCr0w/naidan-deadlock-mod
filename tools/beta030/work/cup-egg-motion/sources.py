from pathlib import Path
import shutil,zipfile
from PIL import Image
r=Path('work/cup-egg-motion');c=r/'source';d=c/'models/heroes_wip/baba';d.mkdir(parents=True,exist_ok=True)
s=Path('work/bench-fix/source/models/heroes_wip/baba/baba.vmdl').read_text()
for lod in range(4):
 s=s.replace(f'models/heroes_wip/baba/naidan_base_lod{lod}.fbx',f'models/naidan_props/base_lod{lod}.fbx')
 for tag in ['folded','open']:s=s.replace(f'models/naige_bench_fix/bench_{tag}_lod{lod}.fbx',f'models/naidan_props/bench_{tag}_lod{lod}.fbx')
(d/'baba.vmdl').write_text(s)
colors={'park_wood':(.34,.105,.038),'park_metal':(.012,.016,.017),'yellow':(1,.56,.015),'cream':(.9,.78,.52),'dark':(.014,.011,.005),'white':(.95,.94,.87),'tea':(.115,.065,.018),'leaf':(.055,.07,.014),'foot':(1,1,1)}
for name,col in colors.items():
 s='"Layer0"\n{\n "shader" "pbr.vfx"\n "F_USE_NPR_LIGHTING" "1"\n "F_SOLID_COLOR_OUTLINE" "1"\n "F_USE_STATUS_EFFECTS_PROXY" "1"\n "g_vSolidOutlineTint" "[0.035 0.021 0.006 0]"\n "g_fSolidOutlineVertexColorTint" "0"\n "TextureNprOutlineMask1" "[0.927 0.927 0.927 1]"\n'
 s+=f' "F_VERTEX_COLOR" "{1 if name=="foot" else 0}"\n "g_fVertexColorStrength1" "{1 if name=="foot" else 0}"\n "g_vColorTint1" "[1 1 1 0]"\n "TextureColor1" "[{col[0]} {col[1]} {col[2]} 1]"\n "TextureNormal1" "materials/models/naidan/flat_normal.png"\n "TextureRoughness1" "[0.55 0.55 0.55 1]"\n "TextureMetalness1" "[0 0 0 1]"\n "TextureAmbientOcclusion1" "[1 1 1 1]"\n}}\n'
 p=c/f'materials/models/naidan_props/{name}.vmat';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
p=c/'panorama/images/items/spirit/goose_egg_psd.vtex';p.parent.mkdir(parents=True,exist_ok=True)
s=Path('work/bench-fix/source/panorama/images/hud/abilities/baba/strafing_run_psd.vtex').read_text().replace('panorama/images/hud/abilities/baba/strafing_run_psd.png','panorama/images/items/spirit/goose_egg_psd.png').replace('"int" "128"','"int" "256"').replace('"m_srcChannels" "string" "r"','"m_srcChannels" "string" "rgba"').replace('"m_dstChannels" "string" "a"','"m_dstChannels" "string" "rgba"').replace('"m_outputColorSpace" "string" "linear"','"m_outputColorSpace" "string" "srgb"');p.write_text(s);Image.open(r/'egg.png').convert('RGBA').save(p.with_suffix('.png'))
p=c/'models/naidan_props/picker.vmdl';p.parent.mkdir(parents=True,exist_ok=True);s=Path('work/naige-all/source/models/naige_all/picker.vmdl').read_text().replace('models/naige_all/picker.fbx','models/naidan_props/picker.fbx');p.write_text(s)
with zipfile.ZipFile(r/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in c.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(c))
