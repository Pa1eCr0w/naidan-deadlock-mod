import bpy,json
from pathlib import Path
R=Path('D:/NaiDanWorkspace/bench-texture-fix');bpy.ops.wm.read_factory_settings(use_empty=True)
im=bpy.data.images.load('D:/NaiDanWorkspace/naidan-3d/toolchain/valve/content/citadel/models/heroes_wip/baba/materials/baba_bench_color_tga_f7ef6365.png');im.alpha_mode='NONE'
bpy.ops.mesh.primitive_plane_add();o=bpy.context.object;s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.render.bake.margin=0
for name,tint in [('wood',(3.6,1.8,1.3)),('metal',(6,1.6,1.8))]:
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;src=n.new('ShaderNodeTexImage');src.image=im;mul=n.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=tint;l.new(src.outputs['Color'],mul.inputs[0]);
 if name=='metal':
  bw=n.new('ShaderNodeRGBToBW');l.new(src.outputs['Color'],bw.inputs[0]);scale=n.new('ShaderNodeMath');scale.operation='MULTIPLY_ADD';scale.inputs[1].default_value=.7;scale.inputs[2].default_value=.035;l.new(bw.outputs[0],scale.inputs[0]);l.new(scale.outputs[0],mul.inputs[0]);mul.inputs[1].default_value=(1.05,1.03,1.0)
 em=n.new('ShaderNodeEmission');l.new(mul.outputs['Vector'],em.inputs[0]);l.new(em.outputs[0],n['Material Output'].inputs['Surface']);dest=bpy.data.images.new('park_'+name+'_recolor',width=4096,height=4096,alpha=False);tex=n.new('ShaderNodeTexImage');tex.image=dest;n.active=tex;o.data.materials.clear();o.data.materials.append(m);bpy.ops.object.bake(type='EMIT');dest.filepath_raw=str(R/('park_'+name+'_recolor.png'));dest.file_format='PNG';dest.save();print('BAKED',dest.filepath_raw,flush=True)
