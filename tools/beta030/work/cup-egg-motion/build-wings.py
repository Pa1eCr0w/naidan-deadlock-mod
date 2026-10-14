import bpy,bmesh,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('D:/NaiDanWorkspace/cup-egg-motion');report={}
def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
for stem,tag,ending in [('normal','bench_folded','baba_pidge_folded_model'),('transform','bench_open','baba_pidge_model')]:
 bpy.ops.wm.open_mainfile(filepath='D:/NaiDanWorkspace/naidan-3d/animated-v2/naidan-animated-v2.blend');rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST';bpy.context.view_layer.update()
 donor=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.endswith(ending))
 with bpy.data.libraries.load('D:/NaiDanWorkspace/naige-solid-install/'+stem+'.blend',link=False) as (src,dst):dst.objects=['NaiGe_'+stem]
 body=dst.objects[0];bpy.context.collection.objects.link(body);world=body.matrix_world.copy();body.parent=None;body.matrix_world=world;active(body);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 for m in list(body.modifiers):body.modifiers.remove(m)
 pts=[donor.matrix_world@v.co for v in donor.data.vertices];lo=Vector([min(p[k] for p in pts) for k in range(3)]);hi=Vector([max(p[k] for p in pts) for k in range(3)])
 pts=[v.co for v in body.data.vertices];bl=Vector([min(p[k] for p in pts) for k in range(3)]);bh=Vector([max(p[k] for p in pts) for k in range(3)])
 original_coords=[v.co.copy() for v in body.data.vertices]
 for v in body.data.vertices:v.co=Vector([lo[k]+(v.co[k]-bl[k])/(bh[k]-bl[k])*(hi[k]-lo[k]) for k in range(3)])
 # Preserve authored anatomical weights from the continuous source instead of nearest-surface transfer.
 oldweights=[{body.vertex_groups[g.group].name:g.weight for g in v.groups} for v in body.data.vertices]
 def target(n):
  side=n[-1]
  if n.startswith('pigeon_wing_'):
   idx=int(n.split('_')[2]);return (['pidgeClav_0_','pidgeWingFolded_0_','pidgeWingFolded_1_'] if stem=='normal' else ['pidgeClav_0_','pidgeWing_0_','pidgeWing_1_'])[idx]+side
  if n.startswith('wing_hlp_'):return 'pidgeWingHlp'+n.split('_')[2].upper()+'_0_'+side
  if n.startswith('toe'):return 'pidge_ball_'+side
  if n.startswith('tail'):return 'pidge_tail_1'
  if n=='pigeon_tail_2':return 'pidge_tail_1'
  if stem=='normal' and n=='pigeon_torso_2':return 'pidge_torso_3'
  return n.replace('pigeon_','pidge_')
 body.vertex_groups.clear()
 for weights in oldweights:
  for n in weights:
   mapped=target(n);assert mapped in rig.data.bones,mapped
   if mapped not in body.vertex_groups:body.vertex_groups.new(name=mapped)
 for i,weights in enumerate(oldweights):
  mapped={}
  for n,w in weights.items():mapped[target(n)]=mapped.get(target(n),0)+w
  for n,w in mapped.items():body.vertex_groups[n].add([i],w,'REPLACE')
 # Eyes, pupils and beak share exactly one rigid head transform, as does the surrounding head surface.
 head='pidge_torso_3';assert head in rig.data.bones and head in body.vertex_groups
 for v,co in zip(body.data.vertices,original_coords):
  t=1.0 if v.index<1952 else max(0,min(1,(co.z-.285)/(.325-.285)))*max(0,min(1,(.085-abs(co.x))/.025))*max(0,min(1,(-.02-co.y)/.05))
  t=t*t*t*(t*(t*6-15)+10)
  if not t:continue
  old={body.vertex_groups[g.group].name:g.weight for g in v.groups}
  for g in list(v.groups):body.vertex_groups[g.group].remove([v.index])
  weights={k:w*(1-t) for k,w in old.items()};weights[head]=weights.get(head,0)+t
  for k,w in weights.items():
   if w>1e-8:body.vertex_groups[k].add([v.index],w,'REPLACE')
 # Surface diffusion removes abrupt changes while preserving face, distal wings and feet.
 names=[g.name for g in body.vertex_groups];w=np.zeros((len(body.data.vertices),len(names)),np.float32)
 for v in body.data.vertices:
  for g in v.groups:w[v.index,g.group]=g.weight
 edges=np.array([e.vertices[:] for e in body.data.edges]);aa=edges[:,0];bb=edges[:,1];degree=np.maximum(1,np.bincount(np.r_[aa,bb],minlength=len(w)))
 co=np.array([list(v) for v in original_coords]);pin=(np.arange(len(w))<1952)|(co[:,2]<.03)|((co[:,2]>.34)&(np.abs(co[:,0])<.067))
 # Keep distal anatomy, diffuse only mixed binding zones. Head and facial rigid constraints are restored each iteration.
 original=w.copy()
 for it in range(300):
  accum=np.zeros_like(w);np.add.at(accum,aa,w[bb]);np.add.at(accum,bb,w[aa]);w=.35*w+.65*accum/degree[:,None];w[pin]=original[pin]
 body.vertex_groups.clear();groups=[body.vertex_groups.new(name=n) for n in names]
 for i,row in enumerate(w):
  ids=np.argsort(row)[-4:];total=sum(float(row[j]) for j in ids)
  for j in ids:
   if row[j]>1e-7:groups[j].add([i],float(row[j])/total,'REPLACE')
 mat=bpy.data.materials.new('materials/models/naige_bench_fix/'+stem+'.vmat');body.data.materials.clear();body.data.materials.append(mat)
 m=body.modifiers.new('Native hero rig','ARMATURE');m.object=rig;body.parent=rig;body.matrix_parent_inverse=rig.matrix_world.inverted()
 for o in list(bpy.context.scene.objects):
  if o not in [body,rig]:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(R/(tag+'.blend')),compress=True)
 report[tag]=[]
 for lod in range(4):
  active(body)
  bad=0
  if lod:
   base=body.data.copy()
   for ratio in [.48,.6,.72,.84,.92]:
    body.data=base.copy();m=body.modifiers.new('Distance LOD','DECIMATE');m.ratio=ratio;m.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=m.name)
    bm=bmesh.new();bm.from_mesh(body.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
    if not bad:break
   assert not bad,(tag,lod,bad)
  bpy.ops.object.vertex_group_limit_total(limit=4);bpy.ops.object.vertex_group_normalize_all(lock_active=False);err=max(abs(sum(g.weight for g in v.groups)-1) for v in body.data.vertices);assert err<1e-5
  report[tag].append({'lod':lod,'triangles':sum(len(p.vertices)-2 for p in body.data.polygons),'nonmanifold':bad,'weightError':err,'bounds':[list(lo),list(hi)]})
  assert all(len(v.groups)==1 and body.vertex_groups[v.groups[0].group].name==head for v in body.data.vertices[:1952]) if lod==0 else True
  rig.select_set(True);bpy.ops.export_scene.fbx(filepath=str(R/f'{tag}_lod{lod}.fbx'),global_scale=1/2.54,use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False,axis_forward='-Z',axis_up='Y')
 print('BENCH_READY',tag,flush=True)
(R/'bench-report.json').write_text(json.dumps(report,indent=2))
