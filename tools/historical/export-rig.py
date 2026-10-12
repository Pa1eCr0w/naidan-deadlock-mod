import bpy,json,math
from pathlib import Path
from mathutils import Matrix
O=Path('E:/HomeAgentAI/naidan-3d/animated-v2');B=O/'build';B.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'naidan-animated-v2.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST'
for b in rig.pose.bones:b.matrix_basis.identity()
bpy.context.view_layer.update()
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and (o.name.startswith('Naidan_AI_') or 'base_model' in o.name)]
used={m for o in meshes for m in o.data.materials if m}
for mat in bpy.data.materials:
 if mat not in used:mat.name='unused_'+mat.name
for mat in used:
 if mat.name.startswith('naidan_'):mat.name='materials/models/naidan/'+mat.name.split('.')[0]+'.vmat'
 elif mat.name.startswith('baba_'):mat.name='models/heroes_wip/baba/materials/'+mat.name+'.vmat'
info=[]
for lod in range(4):
 if lod:
  for o in meshes:
   if len(o.data.polygons)>200 and not o.name.startswith('Naidan_AI_'):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    mod=o.modifiers.new('LOD reduction','DECIMATE');mod.ratio=.5;mod.delimit={'MATERIAL'};bpy.ops.object.modifier_apply(modifier=mod.name)
 for o in meshes:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.vertex_group_limit_total(limit=4);bpy.ops.object.vertex_group_normalize_all(lock_active=False)
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(B/f'naidan_base_lod{lod}.fbx'),global_scale=1/2.54,use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False,axis_forward='-Z',axis_up='Y')
 info.append({'lod':lod,'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)})
# Bake the six legacy animations too; menu and alternate renderers can still use them.
rig.data.pose_position='POSE';scene=bpy.context.scene;scene.render.fps=30
anims=json.loads((O/'preview-animation.json').read_text());alias=json.loads((O/'control-bones.json').read_text());controls=set(alias.values())
for name in ['ui_main_menu','ui_shop','ability_bench_run_n','outofcombat_stand_idle','out_of_combat_run_n','respawn_countdown_idle']:
 source=next((a for a in bpy.data.actions if a.name=='models/heroes_wip/baba/clips/'+name),None) or bpy.data.actions.get(name)
 clip=anims.get(name);samples=clip['samples'] if clip else [None];count=len(samples);frames=[]
 for f,sample in enumerate(samples):
  rig.animation_data_clear()
  for b in rig.pose.bones:b.matrix_basis.identity()
  if source:
   rig.animation_data_create();rig.animation_data.action=source
   if source.slots:rig.animation_data.action_slot=source.slots[0]
   scene.frame_set(round(source.frame_range[0]+f/max(1,count-1)*(source.frame_range[1]-source.frame_range[0])))
  bpy.context.view_layer.update();saved={b.name:b.matrix.copy() for b in rig.pose.bones};rig.animation_data_clear()
  for b in rig.pose.bones:b.matrix=saved[b.name]
  bpy.context.view_layer.update()
  for bone in rig.data.bones:
   if bone.name not in controls:continue
   if sample:
    v=sample['deforms'][bone.name];D=Matrix([v[i:i+4] for i in range(0,16,4)]).transposed()
   else:D=saved['bench_pitch']@rig.data.bones['bench_pitch'].matrix_local.inverted()
   rig.pose.bones[bone.name].matrix=D@bone.matrix_local;bpy.context.view_layer.update()
  frames.append({b.name:b.matrix_basis.copy() for b in rig.pose.bones})
 new=bpy.data.actions.new('Naidan_'+name);new.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=new
 for f,pose in enumerate(frames):
  for b in rig.pose.bones:
   b.rotation_mode='QUATERNION';b.matrix_basis=pose[b.name]
   for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(data_path=prop,frame=f+1,group=b.name)
 scene.frame_start=1;scene.frame_end=max(1,count);scene.frame_set(1)
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(B/('naidan_'+name+'.fbx')),global_scale=1/2.54,use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_simplify_factor=0,axis_forward='-Z',axis_up='Y')
 print('BAKED',name,count,flush=True)
rig.animation_data_clear();rig.data.pose_position='REST'
(O/'lod-report.json').write_text(json.dumps(info,indent=2))
# Save animation library without replacing the full-detail editable mesh.
bpy.ops.wm.save_as_mainfile(filepath=str(O/'naidan-animation-library.blend'),compress=True)
print('ANIMATED_EXPORT_DONE')
