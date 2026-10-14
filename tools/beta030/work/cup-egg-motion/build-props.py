import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/NaiDanWorkspace/cup-egg-motion');report={}
def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
def mat(n,c,rough=.55):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;return m
def mesh(n,vs,fs,m):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.data.materials.append(m)
 for p in me.polygons:p.use_smooth=True
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();return o
def sphere(n,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=p);o=bpy.context.object;o.name=n;o.scale=s;active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 return o
def tube(n,pts,r,m,sides=12):
 pts=[Vector(p) for p in pts];vs=[];fs=[];previous=None
 for i,p in enumerate(pts):
  tangent=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized();ref=Vector((0,1,0)) if abs(tangent.y)<.8 else Vector((1,0,0));a=(previous-tangent*previous.dot(tangent)).normalized() if previous is not None else tangent.cross(ref).normalized();b=tangent.cross(a).normalized();previous=a
  for k in range(sides):v=p+r*(math.cos(k*2*math.pi/sides)*a+math.sin(k*2*math.pi/sides)*b);vs.append(v)
 for j in range(len(pts)-1):
  for k in range(sides):fs.append((j*sides+k,j*sides+(k+1)%sides,(j+1)*sides+(k+1)%sides,(j+1)*sides+k))
 fs += [tuple(reversed(range(sides))),tuple((len(pts)-1)*sides+k for k in range(sides))];return mesh(n,vs,fs,m)
def lathe(n,profile,m,N=64):
 vs=[(r*math.cos(2*math.pi*i/N),r*math.sin(2*math.pi*i/N),z) for r,z in profile for i in range(N)];fs=[]
 for j in range(len(profile)-1):
  for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))

 if min(r for r,z in profile)>.01:
  j=len(profile)-1
  for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(i+1)%N,i))
 else:fs += [tuple(reversed(range(N))),tuple((len(profile)-1)*N+i for i in range(N))]
 return mesh(n,vs,fs,m)
def bind(o,rig,bone):
 active(o);o.vertex_groups.clear();o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE');o.parent=rig;o.matrix_parent_inverse=rig.matrix_world.inverted();mod=o.modifiers.new('Original prop attachment','ARMATURE');mod.object=rig
for lod in range(4):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=f'D:/NaiDanWorkspace/naidan-3d/toolchain/valve/content/citadel/models/heroes_wip/baba/naidan_base_lod{lod}.fbx');rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST';base=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.endswith('base_model') or o.type=='MESH' and '.base_model_lod' in o.name)
 # Recolor by connected native bench parts; no chair vertices or topology are changed.
 wood=mat('materials/models/naidan_props/park_wood.vmat',(.34,.105,.038));metal=mat('materials/models/naidan_props/park_metal.vmat',(.012,.016,.017),.35);base.data.materials.append(wood);wi=len(base.data.materials)-1;base.data.materials.append(metal);mi=len(base.data.materials)-1
 adj=[[] for v in base.data.vertices]
 for e in base.data.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
 seen=set();materialByVertex={};benchpoints=[]
 for v in base.data.vertices:
  if v.index in seen:continue
  todo=[v.index];seen.add(v.index);ids=[]
  while todo:
   i=todo.pop();ids.append(i)
   for j in adj[i]:
    if j not in seen:seen.add(j);todo.append(j)
  groups={base.vertex_groups[g.group].name for i in ids for g in base.data.vertices[i].groups if g.weight>.01}
  if not groups or not all(n.startswith(('bench','leg_','ankle','ball','toe')) or n=='pelvis' for n in groups):continue
  pts=[base.matrix_world@base.data.vertices[i].co for i in ids];lo=Vector([min(p[k] for p in pts) for k in range(3)]);hi=Vector([max(p[k] for p in pts) for k in range(3)]);d=hi-lo
  iswood=d.x>.4 and d.y<.075 and d.z<.09 and lo.z>.63
  for i in ids:materialByVertex[i]=wi if iswood else mi
  benchpoints.extend([tuple(p) for p in pts])
 for p in base.data.polygons:
  if all(i in materialByVertex for i in p.vertices):p.material_index=materialByVertex[p.vertices[0]]
 # Remove precisely the two rigid props being replaced, not chair or accessory geometry.
 remove=[]
 for v in base.data.vertices:
  weights={base.vertex_groups[g.group].name:g.weight for g in v.groups}
  if sum(weights.get(n,0) for n in ['teacup_0','offhand'])>.999:remove.append(v.index)
 bm=bmesh.new();bm.from_mesh(base.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in remove],context='VERTS');bm.to_mesh(base.data);bm.free();assert remove
 yellow=mat('materials/models/naidan_props/yellow.vmat',(1,.56,.015),.35);cream=mat('materials/models/naidan_props/cream.vmat',(.9,.78,.52),.42);dark=mat('materials/models/naidan_props/dark.vmat',(.014,.011,.005),.65);white=mat('materials/models/naidan_props/white.vmat',(.95,.94,.87),.35);tea=mat('materials/models/naidan_props/tea.vmat',(.115,.065,.018),.25);leaf=mat('materials/models/naidan_props/leaf.vmat',(.055,.07,.014),.65)
 # Author cup in normalized dimensions; the reference's arms actually wrap the belly.
 cup=[];cup.append(lathe('Laughing tea cup',[(.001,0),(.35,0),(.42,.06),(.49,.3),(.51,.75),(.50,.95),(.475,.98),(.44,.98),(.435,.94),(.45,.74),(.43,.25),(.32,.09),(.001,.09)],yellow))
 cup[0].data.materials.append(white)
 for f in cup[0].data.polygons:
  if 6*64<=f.index<12*64:f.material_index=1
 cup.append(lathe('Tea surface',[(.001,.9),(.433,.9),(.433,.89),(.001,.89)],tea))
 cup.append(tube('Cup handle',[(.45+.30*math.sin(t),.02,.55+.34*math.cos(t)) for t in [math.pi*i/32 for i in range(33)]],.065,yellow))
 cup.append(sphere('Cream belly',(0,-.461,.37),(.34,.045,.30),cream))
 for sign in [-1,1]:
  cup.append(tube('Closed laughing eye',[(sign*.205+.077*t,-.497,.755+.033*(1-t*t)) for t in [i/10 for i in range(-10,11)]],.018,dark))
  pts=[]
  for i in range(21):
   t=i/20;pts.append((sign*(.43-.22*t),-.22-.34*math.sin(t*math.pi/2),.51-.15*t))
  cup.append(tube('Belly hugging arm',pts,.069,yellow));cup.append(sphere('Palm',(sign*.16,-.55,.365),(.086,.047,.085),dark))
  for f in range(4):cup.append(tube('Curled finger',[(sign*(.15+.06*t),-.582,.405-f*.032+.01*math.sin(t*math.pi)) for t in [i/10 for i in range(11)]],.015,dark))
  cup.append(sphere('Short leg',(sign*.21,0,-.075),(.115,.13,.14),yellow));cup.append(sphere('Dark foot',(sign*.21,-.05,-.18),(.145,.19,.07),dark))
 cup.append(sphere('Open laughing mouth',(0,-.519,.61),(.19,.006,.14),dark));cup.append(sphere('Upper teeth',(0,-.528,.697),(.145,.008,.025),white));cup.append(sphere('Tongue',(0,-.528,.513),(.077,.008,.018),cream))
 for i in range(13):
  a=i*2.399;rad=.36*math.sqrt((i+.5)/13);o=sphere('Tea leaf',(rad*math.cos(a),rad*math.sin(a),.910),(.085,.018,.009),leaf);o.rotation_euler[2]=a;active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);cup.append(o)
 # Position cup bottom at the original saucer and maintain teacup attachment.
 for o in cup:
  for v in o.data.vertices:v.co=Vector((v.co.x*.062,v.co.y*.062-.014,v.co.z*.062+.777))
  bind(o,rig,'teacup_0')
 # Long yellow NaiLong leg with a continuous rounded ankle and three brown toes.
 profile=[(.001,0),(.024,.01),(.039,.03),(.043,.06),(.041,.09),(.036,.12),(.030,.15),(.023,.19),(.018,.23),(.017,.28),(.023,.305),(.030,.326),(.001,.347)]
 # Smooth cubic interpolation along the long leg avoids stacked-sphere seams.
 dense=[]
 for j in range(len(profile)-1):
  for k in range(8):
   t=k/8;a=Vector(profile[max(0,j-1)]);b=Vector(profile[j]);cc=Vector(profile[j+1]);d=Vector(profile[min(len(profile)-1,j+2)]);v=.5*((2*b)+(-a+cc)*t+(2*a-5*b+4*cc-d)*t*t+(-a+3*b-3*cc+d)*t*t*t);dense.append((max(.0005,v.x),v.y))
 dense.append(profile[-1]);foot=[lathe('Continuous long leg',dense,yellow),sphere('Foot palm',(0,-.014,.326),(.034,.024,.035),yellow)]
 for i,x in enumerate([-.026,0,.026]):foot.append(sphere('Toe',(x,-.024,.356 if i==1 else .352),(.014,.022,.032),yellow))
 active(foot[0])
 for o in foot:o.select_set(True)
 bpy.ops.object.join();foot=bpy.context.object;foot.name='NaiLong foot weapon';rem=foot.modifiers.new('Continuous leg ankle and toes','REMESH');rem.mode='VOXEL';rem.voxel_size=.0012;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name);sm=foot.modifiers.new('Smooth joined surface','SMOOTH');sm.factor=.65;sm.iterations=12;bpy.ops.object.modifier_apply(modifier=sm.name)
 m=mat('materials/models/naidan_props/foot.vmat',(1,1,1),.65);foot.data.materials.clear();foot.data.materials.append(m);a=foot.data.color_attributes.new(name='FootColor',type='FLOAT_COLOR',domain='POINT');foot.data.color_attributes.active_color=a;foot.data.color_attributes.render_color_index=0
 for v in foot.data.vertices:
  t=max(0,min(1,(v.co.z-.275)/.057));t=t*t*t*(10+t*(-15+6*t));col=Vector((1,.57,.015)).lerp(Vector((.13,.073,.015)),t);a.data[v.index].color=(*col,1)
 node=m.node_tree.nodes.new('ShaderNodeVertexColor');node.layer_name='FootColor';m.node_tree.links.new(node.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color']);bind(foot,rig,'offhand')
 # Spend geometry on the silhouette, not on invisible density; every LOD uses a real reduction.
 for o in cup+[foot]:
  active(o);tri=sum(len(p.vertices)-2 for p in o.data.polygons);budget=(5200 if o==foot else 700)*[1,.60,.36,.22][lod]
  if tri>budget:
   dec=o.modifiers.new('Prop distance reduction','DECIMATE');dec.ratio=budget/tri;dec.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=dec.name)
 # Dedicated editor source includes full original rig and unaffected geometry.
 if lod==0:bpy.ops.wm.save_as_mainfile(filepath=str(R/'props-review.blend'),compress=True)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.fbx(filepath=str(R/f'base_lod{lod}.fbx'),global_scale=1,use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False,axis_forward='-Z',axis_up='Y',colors_type='LINEAR')
 report[lod]={'removedRigidPropVertices':len(remove),'recoloredChairVertices':len(materialByVertex),'preservedBenchCoordinates':True,'propTriangles':sum(len(p.vertices)-2 for o in cup+[foot] for p in o.data.polygons)}
 print('PROPS_LOD',lod,report[lod],flush=True)
(R/'props-report.json').write_text(json.dumps(report,indent=2))
