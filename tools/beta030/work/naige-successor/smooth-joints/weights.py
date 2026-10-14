import bpy,numpy as np
from pathlib import Path
R=Path('D:/NaiDanWorkspace/naige-successor/rebuild/smooth-joints');bpy.ops.wm.open_mainfile(filepath=str(R/'naige-continuous-flight.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');o=bpy.data.objects['Continuous_body_wings_tail_legs'];names=[g.name for g in o.vertex_groups];co=np.array([list(v.co) for v in o.data.vertices]);w=np.zeros((len(co),len(names)),dtype=np.float32)
for v in o.data.vertices:
 for g in v.groups:w[v.index,g.group]=g.weight
def smooth(t):
 t=np.clip(t,0,1);return t*t*t*(10+t*(-15+6*t))
def projected_arc(points):
 best=np.full(len(co),1e9);arc=np.zeros(len(co));cumulative=0.;lengths=[]
 for a,b in zip(points,points[1:]):
  delta=b-a;length=np.linalg.norm(delta);t=np.clip((co-a)@delta/(length*length),0,1);distance=np.linalg.norm(co-a-t[:,None]*delta,axis=1);mask=distance<best;arc[mask]=cumulative+t[mask]*length;best[mask]=distance[mask];cumulative+=length;lengths.append(length)
 return arc,np.cumsum(lengths)
for side in ['L','R']:
 ids=[i for i,n in enumerate(names) if 'wing' in n and n.endswith('_'+side)];total=w[:,ids].sum(axis=1);w[:,ids]=0;ns=['pigeon_wing_'+str(i)+'_'+side for i in range(3)];points=np.array([list(rig.matrix_world@rig.data.bones[n].head_local) for n in ns+['pigeon_wing_end_'+side]]);x=np.abs(co[:,0]);j1=abs(points[1,0]);j2=abs(points[2,0]);q1=smooth((x-j1+.05)/.10);q2=smooth((x-j2+.05)/.10);print('WING_JOINTS',side,j1,j2,flush=True)
 for n,f in zip(ns,[1-q1,q1*(1-q2),q1*q2]):w[:,names.index(n)]=total*f
ids=[i for i,n in enumerate(names) if 'tail' in n];total=w[:,ids].sum(axis=1);w[:,ids]=0;ns=['pigeon_tail_'+str(i) for i in range(3)];points=np.array([list(rig.matrix_world@rig.data.bones[n].head_local) for n in ns]);y=co[:,1];j1=points[1,1];j2=points[2,1];q1=smooth((y-j1+.04)/.08);q2=smooth((y-j2+.04)/.08)
for n,f in zip(ns,[1-q1,q1*(1-q2),q1*q2]):w[:,names.index(n)]=total*f
o.vertex_groups.clear();groups=[o.vertex_groups.new(name=n) for n in names]
for i,row in enumerate(w):
 ids=np.argsort(row)[-4:];total=sum(float(row[j]) for j in ids);assert total>0
 for j in ids:
  if row[j]>1e-7:groups[j].add([i],float(row[j])/total,'REPLACE')
for m in o.modifiers:
 if m.type=='ARMATURE':m.use_deform_preserve_volume=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'naige-continuous-flight.blend'),compress=True);print('CONTINUOUS_WEIGHTS_DONE',flush=True)
