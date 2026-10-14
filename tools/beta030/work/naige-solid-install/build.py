import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/NaiDanWorkspace/naige-solid-install'); report={}
def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
for kind,stem in [('folded','normal'),('flight','transform')]:
 bpy.ops.wm.open_mainfile(filepath=f'D:/NaiDanWorkspace/naige-successor/rebuild/smooth-joints/naige-continuous-{kind}.blend');s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST';meshes=[o for o in s.objects if o.type=='MESH']
 for o in meshes:
  active(o)
  for m in list(o.modifiers):
   if m.type!='ARMATURE':o.modifiers.remove(m)
  tri=sum(len(p.vertices)-2 for p in o.data.polygons);m=o.modifiers.new('Game budget','DECIMATE');m.use_collapse_triangulate=True;m.ratio=min(1,(24000 if o.name.startswith('Continuous') else 700)/tri);bpy.ops.object.modifier_apply(modifier=m.name)
  bpy.ops.object.vertex_group_limit_total(limit=4);bpy.ops.object.vertex_group_normalize_all(lock_active=False)
 active(meshes[0])
 for o in meshes:o.select_set(True)
 bpy.ops.object.join();body=bpy.context.object;body.name='NaiGe_'+stem
 # Bake the approved vertex colors and material colors into one shared atlas.
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.005);bpy.ops.object.mode_set(mode='OBJECT')
 im=bpy.data.images.new(stem+'_albedo',width=1024,height=1024,alpha=False)
 for mat in body.data.materials:
  n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');out=next(x for x in n if x.type=='OUTPUT_MATERIAL');em=n.new('ShaderNodeEmission')
  if bs.inputs['Base Color'].is_linked:l.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs[0])
  else:em.inputs[0].default_value=bs.inputs['Base Color'].default_value
  l.new(em.outputs[0],out.inputs['Surface']);tex=n.new('ShaderNodeTexImage');tex.image=im;n.active=tex
 s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.device='CPU';s.render.bake.margin=8;bpy.ops.object.bake(type='EMIT');im.filepath_raw=str(R/(stem+'_albedo.png'));im.file_format='PNG';im.save()
 mat=bpy.data.materials.new('materials/models/naige_continuous/'+stem+'.vmat');mat.use_nodes=True;tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;mat.node_tree.links.new(tex.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color']);body.data.materials.clear();body.data.materials.append(mat)
 for f in body.data.polygons:f.material_index=0;f.use_smooth=True
 for a in list(body.data.color_attributes):body.data.color_attributes.remove(a)
 # Keep native rig and animation contract; bake_anim is false, native clips remain in ModelDoc.
 for o in list(s.objects):
  if o not in [rig,body]:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(R/(stem+'.blend')),compress=True)
 print('SOURCE_READY',stem,flush=True)
