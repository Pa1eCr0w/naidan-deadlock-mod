import bpy, math, json
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
O=Path('E:/HomeAgentAI/naidan-3d/animated-v2'); O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='D:/Mods/naidan-baba/build-ai/naidan-baba-rounder-eyes.blend')
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST'
for b in rig.pose.bones:b.matrix_basis.identity()
bpy.context.view_layer.update()
alias=json.loads((O/'control-bones.json').read_text()); controls=set(alias.values())
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and (o.name.startswith('Naidan_AI_') or 'base_model' in o.name)]
conflicts=[]
for o in meshes:
 if o.name.startswith('Naidan_AI_'):continue
 used={g.group for v in o.data.vertices for g in v.groups if g.weight>0.00001}
 for g in o.vertex_groups:
  if g.index in used and g.name in controls:conflicts.append((o.name,g.name))
if conflicts:raise RuntimeError('Controls already used: '+str(conflicts))
def weights(o,fn):
 o.vertex_groups.clear(); gs={n:o.vertex_groups.new(name=n) for n in controls}
 for v in o.data.vertices:
  for k,w in fn(v.co).items():
   if w>0.000001:gs[alias.get(k,k)].add([v.index],w,'REPLACE')
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def bodyw(p):
 if p.z<2.17:
  t=smooth((p.z-1.87)/.30);return {'low':1-t,'mid':t}
 t=smooth((p.z-2.17)/.24);return {'mid':1-t,'top':t}
for o in meshes:
 if not o.name.startswith('Naidan_AI_'):continue
 if o.name in ['Naidan_AI_Body','Naidan_AI_BodyOutline']:weights(o,bodyw)
 elif any(k in o.name for k in ['Eye','Pupil']):
  side='L' if o.name.endswith('-1') else 'R';kind='pupil' if 'Pupil' in o.name else 'eye'
  def ew(p,s=side,k=kind):
   t=max(0,min(1,.5+.5*(p.z-2.5094)/.05952));return {k+s+'U':t,k+s+'D':1-t}
  weights(o,ew)
 elif 'Smile' in o.name:
  weights(o,lambda p:{'mouthU':max(0,1-(p.x/.073)**2),'top':1-max(0,1-(p.x/.073)**2)})
 else:weights(o,lambda p:{'top':1})
body=bpy.data.objects['Naidan_AI_Body'];tree=BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices],[list(p.vertices) for p in body.data.polygons])
# A thin closed mouth becomes an oval opening; fixed corners preserve the smile.
vs=[];fs=[];N=64
for i in range(N+1):
 x=-.067+.134*i/N;z=2.418+.017*(x/.070)**2
 for edge in [0,1]:
  zz=z+(0.00045 if edge==0 else -0.00045);hit=tree.ray_cast(Vector((x,-3,zz)),Vector((0,1,0)))[0]
  if hit is None:raise RuntimeError('Mouth projection failed')
  hit.y-=.0012;vs.append(hit)
for i in range(N):fs.append((2*i,2*i+1,2*i+3,2*i+2))
m=bpy.data.meshes.new('Naidan_MouthCavity');m.from_pydata(vs,[],fs);m.materials.append(next(m for m in bpy.data.materials if m.name.startswith('naidan_mouth')));m.update()
o=bpy.data.objects.new('Naidan_AI_MouthCavity',m);bpy.context.collection.objects.link(o);o.parent=rig;mod=o.modifiers.new('Baba facial motion','ARMATURE');mod.object=rig
for poly in m.polygons:poly.use_smooth=True
o.vertex_groups.clear();groups={k:o.vertex_groups.new(name=alias[k]) for k in ['mouthU','mouthD','top']}
for v in m.vertices:
 w=math.sqrt(max(0,1-(v.co.x/.067)**2));groups['mouthU' if v.index%2==0 else 'mouthD'].add([v.index],w,'REPLACE');groups['top'].add([v.index],1-w,'REPLACE')
meshes.append(o)
for ob in meshes:
 for mod in ob.modifiers:
  if mod.type=='ARMATURE':mod.use_deform_preserve_volume=False
bpy.ops.wm.save_as_mainfile(filepath=str(O/'naidan-animated-v2.blend'),compress=True)
(O/'rig-build-report.json').write_text(json.dumps({'control_bones':alias,'unused_control_verified':True,'meshes':[{'name':o.name,'vertices':len(o.data.vertices)} for o in meshes]},indent=2))
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
print('ANIMATED_RIG_PREVIEWS_DONE')
