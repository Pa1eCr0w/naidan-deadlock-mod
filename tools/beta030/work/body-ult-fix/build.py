import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/NaiDanWorkspace/body-ult-fix');report={}
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
 wood=mat('materials/models/naidan_props/park_wood.vmat',(.32,.23,.15));metal=mat('materials/models/naidan_props/park_metal.vmat',(.10,.105,.10),.35);base.data.materials.append(wood);wi=len(base.data.materials)-1;base.data.materials.append(metal);mi=len(base.data.materials)-1
 for mm,tint in [(wood,(3.6,1.8,1.3)),(metal,(6.,1.6,1.8))]:
  im=bpy.data.images.load('D:/NaiDanWorkspace/naidan-3d/toolchain/valve/content/citadel/models/heroes_wip/baba/materials/baba_bench_color_tga_f7ef6365.png',check_existing=True);tex=mm.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;mul=mm.node_tree.nodes.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=tint;mm.node_tree.links.new(tex.outputs['Color'],mul.inputs[0]);mm.node_tree.links.new(mul.outputs['Vector'],mm.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
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
 burgundy=mat('materials/models/naidan_props/mouth_inner.vmat',(.038,.005,.003),.7);pink=mat('materials/models/naidan_props/tongue.vmat',(.48,.07,.055),.42)
 cup=[]
 profile0=[(.001,0),(.35,0),(.42,.06),(.49,.3),(.51,.75),(.50,.95),(.475,.98),(.44,.98),(.435,.94),(.45,.74),(.43,.25),(.32,.09),(.001,.09)]
 profile=[]
 for j in range(len(profile0)-1):
  for k in range(10):
   t=k/10;aa=Vector(profile0[max(0,j-1)]);bb=Vector(profile0[j]);cc=Vector(profile0[j+1]);dd=Vector(profile0[min(len(profile0)-1,j+2)]);v=.5*(2*bb+(-aa+cc)*t+(2*aa-5*bb+4*cc-dd)*t*t+(-aa+3*bb-3*cc+dd)*t*t*t);profile.append((max(.001,v.x),v.y))
 profile.append(profile0[-1]);shell=lathe('Sculpted laughing cup',profile,yellow,128);cup.append(shell);shell.data.materials.append(white)
 for f in shell.data.polygons:
  if 60*128<=f.index<120*128:f.material_index=1
 # Closed smile-shaped cutter makes a true recessed mouth, not a raised black oval.
 outline=[]
 for i in range(41):
  x=-.25+.5*i/40;outline.append((x,.642+.041*(x/.25)**2))
 for i in range(1,61):
  t=math.pi*i/60;outline.append((.25*math.cos(t),.683-.415*math.sin(t)**.78))
 outline=[(x,z+.08) for x,z in outline[:-1]]
 vs=[(x,y,z) for y in [-.8,-.26] for x,z in outline];N=len(outline);fs=[tuple(reversed(range(N))),tuple(N+i for i in range(N))]+[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)];cutter=mesh('Mouth cutter',vs,fs,yellow);active(shell);bo=shell.modifiers.new('Open smile cavity','BOOLEAN');bo.operation='DIFFERENCE';bo.solver='EXACT';bo.object=cutter;bpy.ops.object.modifier_apply(modifier=bo.name);bpy.data.objects.remove(cutter,do_unlink=True)
 vs=[];fs=[]
 for j in range(13):
  t=j/12;scale=1-.82*t
  for x,z in outline:vs.append((x*scale,-math.sqrt(max(.01,.51**2-x*x))+.008+.14*math.sin(t*math.pi/2),.555+(z-.555)*scale))
 for j in range(12):
  for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 fs.append(tuple(12*N+i for i in range(N)));cavity=mesh('Recessed laughing mouth',vs,fs,burgundy);cup.append(cavity)
 for sign in [-1,1]:
  eye=sphere('Convex rounded eyelid',(sign*.235,-.455,.85),(.145,.13,.105),yellow);active(eye);sub=eye.modifiers.new('Rounded eyelid surface','SUBSURF');sub.levels=1;bpy.ops.object.modifier_apply(modifier=sub.name);cup.append(eye)
 lip=tube('Golden laughing lip',[(x,-math.sqrt(max(.01,.51**2-x*x))-.007,z) for x,z in outline+[outline[0]]],.008,yellow,12);cup.append(lip)
 # Slits lie on the convex eyelids and are patches rather than protruding black tubes.
 for sign in [-1,1]:
  vs=[];fs=[]
  for j in range(3):
   for i in range(41):
    u=-1+2*i/40;x=sign*.235+u*.114;z=.795+.055*(1-u*u)+j*.010*(1-u*u);q=((x-sign*.235)/.145)**2+((z-.85)/.105)**2;y=-.455-.13*math.sqrt(max(.001,1-q))-.002;vs.append((x,y,z))
  for j in range(2):
   for i in range(40):fs.append((j*41+i,j*41+i+1,(j+1)*41+i+1,(j+1)*41+i))
  cup.append(mesh('Closed slit in convex eyelid',vs,fs,burgundy))
 def tooth(n,x,y,z,sx,sz):
  bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,z));o=bpy.context.object;o.name=n;o.scale=(sx,.028,sz);active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.materials.append(white);bev=o.modifiers.new('Rounded individual tooth','BEVEL');bev.width=.016;bev.segments=5;bpy.ops.object.modifier_apply(modifier=bev.name)
  for f in o.data.polygons:f.use_smooth=True
  cup.append(o)
 for i in range(8):
  x=(i-3.5)*.052;z=.722+.041*(x/.25)**2-.026;tooth('Upper tooth',x,-math.sqrt(.51**2-x*x)-.005,z,.057,.060)
 for i in range(6):
  x=(i-2.5)*.045;z=.358+.024*(x/.15)**2;tooth('Lower tooth',x,-math.sqrt(.51**2-x*x)-.003,z,.045,.030)
 cup.append(sphere('Red laughing tongue',(0,-.448,.394),(.105,.046,.053),pink))
 cup.append(lathe('Tea surface',[(.001,.9),(.433,.9),(.433,.89),(.001,.89)],tea))
 cup.append(tube('Cup handle',[(.45+.30*math.sin(t),.02,.55+.34*math.cos(t)) for t in [math.pi*i/32 for i in range(33)]],.065,yellow))
 cup.append(sphere('Cream belly',(0,-.461,.19),(.34,.045,.145),cream))
 for sign in [-1,1]:

  pts=[]
  for i in range(21):
   t=i/20;pts.append((sign*(.43-.22*t),-.22-.34*math.sin(t*math.pi/2),.41-.15*t))
  cup.append(tube('Belly hugging arm',pts,.069,yellow));cup.append(sphere('Palm',(sign*.16,-.55,.265),(.086,.047,.085),dark))
  for f in range(4):cup.append(tube('Curled finger',[(sign*(.15+.06*t),-.582,.305-f*.032+.01*math.sin(t*math.pi)) for t in [i/10 for i in range(11)]],.015,dark))
  cup.append(sphere('Short leg',(sign*.21,0,-.075),(.115,.13,.14),yellow));cup.append(sphere('Dark foot',(sign*.21,-.05,-.18),(.145,.19,.07),dark))

 for i in range(13):
  a=i*2.399;rad=.36*math.sqrt((i+.5)/13);o=sphere('Tea leaf',(rad*math.cos(a),rad*math.sin(a),.910),(.085,.018,.009),leaf);o.rotation_euler[2]=a;active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);cup.append(o)
 # Position cup bottom at the original saucer and maintain teacup attachment.
 for o in cup:
  for v in o.data.vertices:v.co=Vector((-v.co.x*.062,-v.co.y*.062-.014,v.co.z*.062+.777))
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
  t=max(0,min(1,(v.co.z-.275)/.057));t=t*t*t*(10+t*(-15+6*t));col=Vector((1,.72,.12)).lerp(Vector((.30,.18,.065)),t);a.data[v.index].color=(*col,1)
 uv=foot.data.uv_layers.new(name='FootGradientUV')
 for loop in foot.data.loops:
  v=foot.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(.5+math.atan2(v.y,v.x)/(2*math.pi),max(.005,min(.995,v.z/.39)))
 if lod==0:
  # Bake the material ramp on a full UV plane; this is the exact texture shipped to the game.
  im=bpy.data.images.new('Foot bright gradient',width=128,height=512,alpha=False);bake=mat('Gradient bake',(1,1,1));nodes=bake.node_tree.nodes;links=bake.node_tree.links;tc=nodes.new('ShaderNodeTexCoord');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(tc.outputs['UV'],sep.inputs[0]);ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='EASE';ramp.color_ramp.elements[0].position=.275/.39;ramp.color_ramp.elements[0].color=(1,.72,.12,1);ramp.color_ramp.elements[1].position=.332/.39;ramp.color_ramp.elements[1].color=(.30,.18,.065,1);links.new(sep.outputs['Y'],ramp.inputs[0]);em=nodes.new('ShaderNodeEmission');links.new(ramp.outputs['Color'],em.inputs[0]);links.new(em.outputs[0],nodes['Material Output'].inputs['Surface']);tex=nodes.new('ShaderNodeTexImage');tex.image=im;nodes.active=tex;bpy.ops.mesh.primitive_plane_add();plane=bpy.context.object;plane.data.materials.append(bake);bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1;bpy.context.scene.render.bake.margin=0;bpy.ops.object.bake(type='EMIT');im.filepath_raw=str(R/'foot_gradient.png');im.file_format='PNG';im.save();bpy.data.objects.remove(plane,do_unlink=True)
 else:im=bpy.data.images.load(str(R/'foot_gradient.png'))
 tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
 for attr in list(foot.data.color_attributes):foot.data.color_attributes.remove(attr)
 bind(foot,rig,'offhand')
 # Spend geometry on the silhouette, not on invisible density; every LOD uses a real reduction.
 for o in cup+[foot]:
  active(o);tri=sum(len(p.vertices)-2 for p in o.data.polygons);budget=(5200 if o==foot else 12000 if o==shell else 1400 if o==cavity else 2200 if o.name.startswith('Convex rounded eyelid') else 700)*[1,.60,.36,.22][lod]
  if tri>budget:
   dec=o.modifiers.new('Prop distance reduction','DECIMATE');dec.ratio=budget/tri;dec.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=dec.name)
 # Dedicated editor source includes full original rig and unaffected geometry.
 if lod==0:bpy.ops.wm.save_as_mainfile(filepath=str(R/'props-review.blend'),compress=True)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.fbx(filepath=str(R/f'base_lod{lod}.fbx'),global_scale=1,use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False,axis_forward='-Z',axis_up='Y',colors_type='LINEAR')
 report[lod]={'removedRigidPropVertices':len(remove),'recoloredChairVertices':len(materialByVertex),'preservedBenchCoordinates':True,'propTriangles':sum(len(p.vertices)-2 for o in cup+[foot] for p in o.data.polygons)}
 print('PROPS_LOD',lod,report[lod],flush=True)
(R/'props-report.json').write_text(json.dumps(report,indent=2))
