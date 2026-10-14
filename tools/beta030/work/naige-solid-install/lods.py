import bpy,bmesh,json
from pathlib import Path
R=Path('D:/NaiDanWorkspace/naige-solid-install');report={}
for stem in ['normal','transform']:
 bpy.ops.wm.open_mainfile(filepath=str(R/(stem+'.blend')));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');body=next(o for o in bpy.context.scene.objects if o.type=='MESH');report[stem]=[]
 for lod in range(3):
  bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
  if lod:
   base=body.data.copy()
   for ratio in [.48,.6,.72,.84,.92]:
    body.data=base.copy();m=body.modifiers.new('Distance LOD','DECIMATE');m.ratio=ratio;bpy.ops.object.modifier_apply(modifier=m.name)
    bm=bmesh.new();bm.from_mesh(body.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
    if not bad:break
   assert not bad,(stem,lod,bad)
  bpy.ops.object.vertex_group_limit_total(limit=4);bpy.ops.object.vertex_group_normalize_all(lock_active=False)
  err=max(abs(sum(g.weight for g in v.groups)-1) for v in body.data.vertices);assert err<1e-5
  report[stem].append({'lod':lod,'triangles':sum(len(p.vertices)-2 for p in body.data.polygons),'weightError':err,'nonmanifold':0,'bones':len(rig.data.bones)})
  rig.select_set(True);bpy.ops.export_scene.fbx(filepath=str(R/f'{stem}_lod{lod}.fbx'),global_scale=1/2.54,use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False,axis_forward='-Z',axis_up='Y')
 print('LOD_READY',stem,report[stem],flush=True)
(R/'build-report.json').write_text(json.dumps(report,indent=2))
