import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
O=Path('E:/HomeAgentAI/naidan-3d/animated-v2')
bpy.ops.wm.open_mainfile(filepath=str(O/'naidan-animated-v2.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');body=bpy.data.objects['Naidan_AI_Body']
# Preview the exact per-clip transforms that are written into game resources.
anims=json.loads((O/'preview-animation.json').read_text());rig.data.pose_position='POSE'
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.resolution_x=640;scene.render.resolution_y=700;scene.render.resolution_percentage=100
for ob in scene.objects:
 if ob.type=='MESH':ob.hide_render=not ob.name.startswith('Naidan_AI_') or 'BodyOutline' in ob.name
cam=scene.camera;cam.data.type='ORTHO';cam.data.ortho_scale=1.25
pre=O/'previews';pre.mkdir(exist_ok=True)
def setpose(name,phase):
 rig.animation_data_clear()
 for b in rig.pose.bones:b.matrix_basis.identity()
 a=next((a for a in bpy.data.actions if a.name=='models/heroes_wip/baba/clips/'+name),None)
 if a:
  rig.animation_data_create();rig.animation_data.action=a
  if a.slots:rig.animation_data.action_slot=a.slots[0]
  scene.frame_set(round(a.frame_range[0]+phase*(a.frame_range[1]-a.frame_range[0])))
 bpy.context.view_layer.update()
 saved={b.name:b.matrix.copy() for b in rig.pose.bones};rig.animation_data_clear()
 for b in rig.pose.bones:b.matrix=saved[b.name]
 bpy.context.view_layer.update()
 samples=anims[name]['samples'];sample=samples[round(phase*(len(samples)-1))]
 for bone in rig.data.bones:
  if bone.name in sample['deforms']:
   vals=sample['deforms'][bone.name];D=Matrix([vals[i:i+4] for i in range(0,16,4)]).transposed();rig.pose.bones[bone.name].matrix=D@bone.matrix_local;bpy.context.view_layer.update()
 return sample
for label,name,phase,d in [('idle','ui_main_menu',0,(0,-5,0)),('idle_side','ui_main_menu',0,(4,-4,0)),('blink','ui_main_menu',.66,(0,-5,0)),('jump','jump_ground',.4,(0,-5,0)),('cast','ability_hex_casting',.5,(1,-5,0)),('landing','landing_impact',.3,(0,-5,0)),('run','out_of_combat_run_n',.3,(1,-5,0))]:
 s=setpose(name,phase);deps=bpy.context.evaluated_depsgraph_get();bo=body.evaluated_get(deps);coords=[bo.matrix_world@v.co for v in bo.data.vertices];target=sum(coords,Vector())/len(coords);target.z+=.06
 cam.location=target+Vector(d);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(pre/(label+'.png'));bpy.ops.render.render(write_still=True)
movie=O/'motion-preview';movie.mkdir(exist_ok=True)
scene.render.resolution_x=480;scene.render.resolution_y=520;scene.cycles.samples=12
for name in ['ui_main_menu','out_of_combat_run_n','ability_hex_casting']:
 for f in range(18):
  setpose(name,f/17);deps=bpy.context.evaluated_depsgraph_get();bo=body.evaluated_get(deps);coords=[bo.matrix_world@v.co for v in bo.data.vertices];target=sum(coords,Vector())/len(coords);target.z+=.06
  cam.location=target+Vector((0,-5,0));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(movie/(name+'_%02d.png'%f));bpy.ops.render.render(write_still=True)
print('ANIMATED_PREVIEWS_DONE')
