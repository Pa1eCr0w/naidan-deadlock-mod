import bpy,bmesh,json,numpy as np,math
from pathlib import Path
from mathutils import Vector
SRC=Path('D:/NaiDanWorkspace/naige-successor/rebuild');OUT=SRC/'smooth-joints';OUT.mkdir(exist_ok=True)
report={}
def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
def blend(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def apply(o,m):active(o);bpy.ops.object.modifier_apply(modifier=m.name)
def join(obs,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
for kind in ['folded']:
 bpy.ops.wm.open_mainfile(filepath=str(SRC/f'naige-rebuilt-{kind}.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.data.pose_position='REST'
 for a in bpy.data.actions:a.use_fake_user=True
 parts=[o for o in s.objects if o.type=='MESH' and not o.name.startswith(('Green_eye','Low_pupil','Small_closed_beak','Subtle_beak_seam'))]
 for o in parts:
  if kind=='folded' and o.name.startswith(('Folded_covert_mantle','Folded_layer')):
   for v in o.data.vertices:
    x,y,z=v.co;v.co.x-=(1 if x>0 else -1)*.050*blend((z-.18)/.10)*blend((.085-y)/.15)
  for m in list(o.modifiers):o.modifiers.remove(m)
 donor=join(parts,'Joined_original_weight_donor');donor.hide_render=True
 shell=donor.copy();shell.data=donor.data.copy();s.collection.objects.link(shell);shell.hide_render=False;shell.name='Continuous_body_wings_tail_legs';shell.vertex_groups.clear()
 bridges=[];bones={b.name:rig.matrix_world@b.head_local for b in rig.data.bones}
 def sphere(name,center,scale):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=center);o=bpy.context.object;o.name=name;o.scale=scale;active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);bridges.append(o)
 for side,sign in [('L',1),('R',-1)]:
  if kind=='folded':pass
  else:
   root=bones['pigeon_wing_0_'+side];sphere('Shoulder transition',root+Vector((-sign*.012,0,-.008)),(.057,.050,.052))
 # Broad rump transition closes the previously intersecting tail base and torso surfaces.
 if kind=='folded':pass
 else:
  p=bones['pigeon_tail_0'];sphere('Rump transition',p+Vector((0,-.027,.015)),(.054,.072,.039))
 shell=join([shell]+bridges,'Continuous_body_wings_tail_legs');active(shell)
 m=shell.modifiers.new('Weld anatomy into one surface','REMESH');m.mode='VOXEL';m.voxel_size=.00115;m.use_smooth_shade=True;apply(shell,m)
 # Local shoulder/rump fairing is substantially broader than global surface fairing.
 g=shell.vertex_groups.new(name='Transition_fairing')
 for v in shell.data.vertices:
  p=v.co;f=0
  for side,sign in [('L',1),('R',-1)]:
   c=Vector((sign*.082,-.045,.252)) if kind=='folded' else bones['pigeon_wing_0_'+side]
   delta=p-c;dist=math.sqrt((delta.x/.085)**2+(delta.y/.12)**2+(delta.z/.085)**2);f=max(f,1-blend((dist-.20)/.80))
  c=Vector((0,.105,.15)) if kind=='folded' else bones['pigeon_tail_0'];delta=p-c;dist=math.sqrt((delta.x/.09)**2+(delta.y/.12)**2+(delta.z/.065)**2);f=max(f,1-blend((dist-.20)/.8))
  if f>1e-6:g.add([v.index],f,'REPLACE')
 m=shell.modifiers.new('Broad shoulder and rump curvature fairing','SMOOTH');m.factor=1.0;m.iterations=230;m.vertex_group=g.name;apply(shell,m)
 m=shell.modifiers.new('Continuous surface fairing','SMOOTH');m.factor=1.0;m.iterations=7;apply(shell,m)
 shell.vertex_groups.clear()
 for g in donor.vertex_groups:shell.vertex_groups.new(name=g.name)
 m=shell.modifiers.new('Transfer anatomical weights','DATA_TRANSFER');m.object=donor;m.use_vert_data=True;m.data_types_verts={'VGROUP_WEIGHTS'};m.vert_mapping='POLYINTERP_NEAREST';m.layers_vgroup_select_src='ALL';m.layers_vgroup_select_dst='NAME';apply(shell,m)
 names=[g.name for g in shell.vertex_groups];w=np.zeros((len(shell.data.vertices),len(names)),dtype=np.float32)
 for v in shell.data.vertices:
  for g in v.groups:w[v.index,g.group]=g.weight
 edges=np.array([list(e.vertices) for e in shell.data.edges]);aa=edges[:,0];bb=edges[:,1];degree=np.bincount(np.concatenate([aa,bb]),minlength=len(w));co=np.array([list(v.co) for v in shell.data.vertices]);head=names.index('pigeon_torso_2' if kind=='folded' else 'pigeon_torso_3');fixed=(co[:,2]>.335)&(np.abs(co[:,0])<.066)
 for _ in range(25):
  total=np.zeros_like(w);np.add.at(total,aa,w[bb]);np.add.at(total,bb,w[aa]);w=.55*w+.45*total/np.maximum(1,degree[:,None]);w[fixed]=0;w[fixed,head]=1
 shell.vertex_groups.clear();groups=[shell.vertex_groups.new(name=n) for n in names]
 for i,row in enumerate(w):
  ids=np.argsort(row)[-4:];total=sum(float(row[j]) for j in ids)
  if total<1e-8:groups[names.index('pigeon_pelvis')].add([i],1,'REPLACE');continue
  for j in ids:
   if row[j]>1e-7:groups[j].add([i],float(row[j])/total,'REPLACE')
 bpy.data.objects.remove(donor,do_unlink=True)
 # One color field across structural connections avoids a material seam masquerading as geometry.
 shell.data.materials.clear();mat=bpy.data.materials.new('Continuous yellow cream plumage');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.65;attr=shell.data.color_attributes.new(name='ContinuousColor',type='FLOAT_COLOR',domain='POINT')
 for v in shell.data.vertices:
  x,y,z=v.co;cream=(1-blend((y+.13)/.13))*(1-blend((z-.285)/.055))*blend((z-.065)/.045);col=Vector((1,.55,.009)).lerp(Vector((.9,.76,.46)),cream);pink=1-blend((z-.034)/.024);col=col.lerp(Vector((.47,.12,.095)),pink);attr.data[v.index].color=(*col,1)
 node=mat.node_tree.nodes.new('ShaderNodeVertexColor');node.layer_name=attr.name;mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);shell.data.materials.append(mat)
 for p in shell.data.polygons:p.use_smooth=True
 # Subdivision remains editable; no sharp boundary between body and its anatomical appendages.
 m=shell.modifiers.new('Native skeleton smooth deformation','ARMATURE');m.object=rig;m.use_deform_preserve_volume=True
 m=shell.modifiers.new('Continuous subdivision limit surface','SUBSURF');m.levels=1;m.render_levels=1
 bm=bmesh.new();bm.from_mesh(shell.data);seen=set();components=[]
 for v in bm.verts:
  if v in seen:continue
  seen.add(v);stack=[v];n=0
  while stack:
   u=stack.pop();n+=1
   for e in u.link_edges:
    q=e.other_vert(u)
    if q not in seen:seen.add(q);stack.append(q)
  components.append(n)
 report[kind]={'vertices':len(bm.verts),'components':sorted(components,reverse=True),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'native_bones':len(rig.data.bones),'C2_status':'Not mathematically certified. Continuous welded geometry, curvature fairing, editable subdivision; extraordinary vertices can lack C2 continuity.'};bm.free()
 (OUT/'surface-report.json').write_text(json.dumps(report,indent=2));print('SURFACE',kind,report[kind],flush=True)
 s.cycles.samples=24;s.render.resolution_percentage=100;s.render.resolution_x=900;s.render.resolution_y=900
 for view,d in [('front',(0,-1,.08)),('side',(1,0,.08)),('rear',(0,1,.08)),('threequarter',(.6,-1,.18))]:
  target=Vector((0,.015,.205));s.camera.location=target+Vector(d);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=.51 if kind=='folded' else 1.05;s.render.filepath=str(OUT/f'{kind}-{view}.png');bpy.ops.render.render(write_still=True)
 if kind=='flight':rig.data.pose_position='POSE';s.frame_set(0)
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'naige-continuous-{kind}.blend'),compress=True)
print('CONTINUOUS_SURFACES_DONE',flush=True)
