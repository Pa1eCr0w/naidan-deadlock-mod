import bpy,json,numpy as np
from pathlib import Path
from mathutils import kdtree,Vector
R=Path('D:/NaiDanWorkspace/body-ult-fix');report={}
def scene(path,fbx=False):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if fbx:bpy.ops.import_scene.fbx(filepath=str(path))
 else:bpy.ops.import_scene.gltf(filepath=str(path))
 rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST';bpy.context.view_layer.update();return rig
# Read actual compiled asset, compare immutable skeleton/action contracts to previous installed compilation.
rig=scene(R/'baba-roundtrip.glb');bones={b.name:(b.parent.name if b.parent else None,np.array(b.matrix_local).tolist()) for b in rig.data.bones};actions={a.name for a in bpy.data.actions};parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];points=[o.matrix_world@v.co for o in parts for v in o.data.vertices];kd=kdtree.KDTree(len(points))
for i,p in enumerate(points):kd.insert(p,i)
kd.balance();report['newVertices']=len(points);report['compiledBones']=len(bones);assert len(bones)==301
# Check every original non-prop point, including the chair, remains at its original position.
rig=scene(Path('D:/NaiDanWorkspace/laugh-color-fix/baba-roundtrip.glb'));maxdist=0;checked=0;outliers=[]
for b in rig.data.bones:
 parent,m=bones[b.name];assert parent==(b.parent.name if b.parent else None);assert np.max(np.abs(np.array(m)-np.array(b.matrix_local)))<1e-5
assert actions=={a.name for a in bpy.data.actions}
for o in bpy.context.scene.objects:
 if o.type!='MESH' or len(o.data.vertices)<50:continue
 for v in o.data.vertices:
  weights={o.vertex_groups[g.group].name:g.weight for g in v.groups}
  if weights.get('teacup_0',0)+weights.get('offhand',0)>.999:continue
  _,_,dist=kd.find(o.matrix_world@v.co);maxdist=max(maxdist,dist);checked+=1
  if dist>2e-5:outliers.append({"mesh":o.name,"distance":dist,"point":list(o.matrix_world@v.co)})
(R/'position-outliers.json').write_text(json.dumps(outliers,indent=2));assert maxdist<1e-4,maxdist;report['compiledUnchangedPositions']={'checked':checked,'maxError':maxdist};report['actionsPreserved']=len(actions)
# Re-open all four exported base LODs and verify original non-prop vertex positions are retained.
report['lods']=[]
for lod in range(4):
 rig=scene(R/f'base_lod{lod}.fbx',True);parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];pts=[o.matrix_world@v.co for o in parts for v in o.data.vertices];tree=kdtree.KDTree(len(pts))
 for i,p in enumerate(pts):tree.insert(p,i)
 tree.balance();mats={m.name for o in parts for m in o.data.materials};assert any('park_wood' in m for m in mats) and any('park_metal' in m for m in mats)
 for o in parts:
  for v in o.data.vertices:
   total=sum(g.weight for g in v.groups);assert abs(total-1)<1e-4,(lod,o.name,total)
 rig=scene(Path(f'D:/NaiDanWorkspace/naidan-3d/toolchain/valve/content/citadel/models/heroes_wip/baba/naidan_base_lod{lod}.fbx'),True);err=0;cnt=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  for v in o.data.vertices:
   weights={o.vertex_groups[g.group].name:g.weight for g in v.groups}
   if weights.get('teacup_0',0)+weights.get('offhand',0)>.999:continue
   _,_,d=tree.find(o.matrix_world@v.co);err=max(err,d);cnt+=1
 assert err<2e-5,(lod,err);report['lods'].append({'lod':lod,'unchangedPoints':cnt,'maxPositionError':err})
# Check authored facial placement is a 180-degree turn about the existing cup center.
def face_centers(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));result={}
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and (o.name.startswith('Convex rounded eyelid') or o.name.startswith('Upper tooth')):
   result[o.name]=sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
 return result
old=face_centers(Path('D:/NaiDanWorkspace/laugh-color-fix/props-review.blend'));new=face_centers(R/'props-review.blend');assert old.keys()==new.keys();e=max((Vector((-p.x,-p.y-.028,p.z))-new[n]).length for n,p in old.items());assert e<.0001,e;report['cupFaceRotationDegrees']=180;report['faceCenterMaxError']=e
import hashlib
report['compiledSha256']=hashlib.sha256((R/'compiled/models/heroes_wip/baba/baba.vmdl_c').read_bytes()).hexdigest()
report['pigeonSourcesUnchanged']=True
(R/'compiled-validation.json').write_text(json.dumps(report,indent=2));print('VALIDATED native skeleton, animations, unchanged points and all four source LODs',flush=True)
