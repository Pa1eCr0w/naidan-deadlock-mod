from pathlib import Path
import json,struct
r=Path('/path/to/naidan-deadlock-mod/outputs/naige-yellow-spirit-preview');p=r/'naige-yellow-spirit-preview.glb';b=p.read_bytes();size=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+size]);tail=b[20+size:]
for m in j['materials']:
 color=m.pop('emissiveFactor');m['pbrMetallicRoughness']={'baseColorFactor':color+[1],'metallicFactor':0,'roughnessFactor':1};m['extensions']={'KHR_materials_unlit':{}};m['alphaMode']='OPAQUE';m['doubleSided']=False
j['extensionsUsed']=['KHR_materials_unlit'];j['extensionsRequired']=['KHR_materials_unlit'];data=json.dumps(j,separators=(',',':')).encode();data+=b' '*((-len(data))%4);p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
for mesh in j['meshes'][:2]:
 for k,a in mesh['primitives'][0]['attributes'].items():
  if not k.startswith('COLOR'):continue
  acc=j['accessors'][a];view=j['bufferViews'][acc['bufferView']];off=8+view.get('byteOffset',0)+acc.get('byteOffset',0);fmt={5126:'f',5123:'H',5121:'B'}[acc['componentType']];print(k,acc['componentType'],struct.unpack_from('<4'+fmt,tail,off))
(r/'glb-validation.json').write_text(json.dumps({'unlitMaterials':len(j['materials']),'opaqueMaterials':len(j['materials']),'backfaceCulled':True,'meshes':len(j['meshes']),'installed':False},indent=2))
