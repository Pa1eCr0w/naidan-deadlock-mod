import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/NaiDanWorkspace/naige-all');report={}
def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
def bounds(objs):
 p=[o.matrix_world@v.co for o in objs for v in o.data.vertices];return Vector([min(v[k] for v in p) for k in range(3)]),Vector([max(v[k] for v in p) for k in range(3)])
def bake(o):
 world=o.matrix_world.copy();o.parent=None;o.matrix_world=world;active(o)
 for m in list(o.modifiers):o.modifiers.remove(m)
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
def fit(parts,lo,hi,uniform=False):
 bl,bh=bounds(parts);scale=(hi-lo)/(bh-bl) if False else Vector([(hi[k]-lo[k])/(bh[k]-bl[k]) for k in range(3)])
 if uniform:scale=Vector([min(scale)]*3)
 for o in parts:
  for v in o.data.vertices:v.co=Vector([(v.co[k]-(bl[k]+bh[k])/2)*scale[k]+(lo[k]+hi[k])/2 for k in range(3)])
def export(parts,stem,rig=None):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 if rig:rig.select_set(True)
 bpy.context.view_layer.objects.active=parts[0]
 bpy.ops.export_scene.fbx(filepath=str(R/(stem+'.fbx')),global_scale=1/2.54,use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False,axis_forward='-Z',axis_up='Y',colors_type='LINEAR')
 bpy.ops.wm.save_as_mainfile(filepath=str(R/(stem+'.blend')),compress=True)
 report[stem]={'bounds':[list(x) for x in bounds(parts)],'triangles':sum(len(p.vertices)-2 for o in parts for p in o.data.polygons),'bones':len(rig.data.bones) if rig else 0}
# Perched selection bird uses the approved solid model and original spatial bounds.
bpy.ops.wm.open_mainfile(filepath='D:/NaiDanWorkspace/naige-solid-install/normal.blend');o=next(o for o in bpy.context.scene.objects if o.type=='MESH');bake(o)
for x in list(bpy.context.scene.objects):
 if x!=o:bpy.data.objects.remove(x,do_unlink=True)
fit([o],Vector((-.160739481,-.183755189,-.010642301)),Vector((.160739481,.421312183,.431910843)));export([o],'picker')
for stem in ['effect','ghost']:
 bpy.ops.wm.open_mainfile(filepath='D:/NaiDanWorkspace/naige-feedback/naige-yellow-spirit-preview.blend');parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];mats={k:bpy.data.materials.new('materials/models/naige_spirit/'+k+'.vmat') for k in ['body','outline']}
 for o in parts:
  bake(o);key='outline' if o.name.startswith('Outline_') else 'body';o.data.materials.clear();o.data.materials.append(mats[key])
  for p in o.data.polygons:p.material_index=0
  if key=='body':o.data.color_attributes.active_color=o.data.color_attributes['SpiritColor'];o.data.color_attributes.render_color_index=o.data.color_attributes.find('SpiritColor')
  active(o);tri=sum(len(p.vertices)-2 for p in o.data.polygons);original=o.data.copy();budget=4500 if 'body_wings' in o.name else 180
  for factor in [1,1.4,2,3,6,1000]:
   o.data=original.copy();m=o.modifiers.new('Particle budget','DECIMATE');m.ratio=min(1,budget*factor/max(tri,1));m.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=m.name)
   bm=bmesh.new();bm.from_mesh(o.data);badedges=[e for e in bm.edges if not e.is_manifold]
   if badedges and len(badedges)<=12 and all(e.is_boundary for e in badedges):
    bmesh.ops.holes_fill(bm,edges=badedges,sides=6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data)
   bad=sum(not e.is_manifold for e in bm.edges);bm.free()
   if not bad:break
  assert not bad,(o.name,bad)

 # Generate each outline from the final reduced body topology so their surfaces stay paired.
 baseparts=[o for o in parts if not o.name.startswith('Outline_')]
 for o in parts:
  if o.name.startswith('Outline_'):bpy.data.objects.remove(o,do_unlink=True)
 parts=list(baseparts)
 for o in baseparts:
  h=o.copy();h.data=o.data.copy();bpy.context.collection.objects.link(h);h.name='Outline_'+o.name
  offset=.0008 if 'body_wings' in o.name else .00038
  for v in h.data.vertices:v.co+=v.normal*offset
  bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(h.data);bm.free();h.data.materials.clear();h.data.materials.append(mats['outline']);parts.append(h)
 if stem=='effect':
  rot=Matrix.Rotation(math.radians(70),4,'X')
  for o in parts:
   for v in o.data.vertices:v.co=rot@v.co
  fit(parts,Vector((-.31089345,-.14755303,-.094302885)),Vector((.3108865,.27976272,.097535409)),True);export(parts,stem)
 else:
  prev=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(R/'ghost_pigeon.glb'));imported=[o for o in bpy.context.scene.objects if o not in prev];rig=next(o for o in imported if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST';bpy.context.view_layer.update();donor=max([o for o in imported if o.type=='MESH'],key=lambda o:len(o.data.vertices));lo,hi=bounds([donor]);fit(parts,lo,hi)
  for o in parts:
   active(o);o.vertex_groups.clear()
   for b in rig.data.bones:o.vertex_groups.new(name=b.name)
   def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)));return t*t*t*(t*(t*6-15)+10)
   for v in o.data.vertices:
    x,y,z=v.co;ax=abs(x);side='L' if x>0 else 'R';w={};wing=smooth(.38,.62,ax)*smooth(.45,.68,z)
    # Keep the torso off the native hidden/folded wing bones. Continuous weight fields preserve the joined surface.
    head=smooth(.76,1.06,z)*(1-smooth(-.02,.18,y));tail=0.0
    w['head']=(1-wing)*head;w['tail_1']=(1-wing)*tail;w['chest']=(1-wing)*(1-head-tail)
    w[f'wing_out_0_{side}']=wing
    w={k:max(0,val) for k,val in w.items() if val>1e-7};total=sum(w.values())
    for k,val in w.items():o.vertex_groups[k].add([v.index],val/total,'REPLACE')
   bpy.ops.object.vertex_group_limit_total(limit=4);bpy.ops.object.vertex_group_normalize_all(lock_active=False)
   assert all(abs(sum(g.weight for g in v.groups)-1)<1e-5 for v in o.data.vertices)
   m=o.modifiers.new('Native ghost rig','ARMATURE');m.object=rig;o.parent=rig;o.matrix_parent_inverse=rig.matrix_world.inverted()
  for o in imported:
   if o!=rig:bpy.data.objects.remove(o,do_unlink=True)
  assert len(rig.data.bones)==23;export(parts,stem,rig)
 print('BUILT',stem,flush=True)
(R/'build-report.json').write_text(json.dumps(report,indent=2))
