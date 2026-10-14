import bpy
from pathlib import Path
R=Path('D:/NaiDanWorkspace/naige-successor/rebuild/smooth-joints');bpy.ops.wm.open_mainfile(filepath=str(R/'naige-continuous-flight.blend'));o=bpy.data.objects['Continuous_body_wings_tail_legs'];bpy.context.view_layer.objects.active=o;o.select_set(True)
m=o.modifiers.new('Preserve smooth joint curvature during motion','CORRECTIVE_SMOOTH');m.factor=.8;m.iterations=20;m.smooth_type='LENGTH_WEIGHTED'
bpy.ops.object.modifier_move_up(modifier=m.name)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'naige-continuous-flight.blend'),compress=True)
