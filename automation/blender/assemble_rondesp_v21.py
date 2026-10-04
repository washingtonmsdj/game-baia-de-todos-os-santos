"""Remontagem V21 na única sessão visível, preservando a oficina V20."""
import ast,bpy,bmesh,hashlib,json,math,struct
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_chapa_v20.blend'
assert not s.get('boas_v21_assembly_applied')
body=s.objects['HILUX | CARROCERIA PRINCIPAL'];root=s.objects['RDP01_ROOT | viatura']
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
protected={ob.name:fingerprint(ob) for ob in s.objects if ob.type=='MESH' and (ob==body or ob.get('boas_role')=='moving_door_shell')}
assert len(protected)==5
checkpoint=r/'artifacts/vehicles/rondesp/v21-live-before.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
s.frame_set(1)
for ob in s.objects:
 if ob.type=='EMPTY' and 'abertura_graus' in ob:ob['abertura_graus']=0.
# Coleções e visibilidade individual são restauradas em conjunto.
stash=bpy.data.collections['RDP01 | PECAS RESERVADAS'];stash.hide_viewport=False;stash.hide_render=False
restored=[];withheld=[]
for col in list(stash.children):
 if col.name=='RDP01 | PORTAS':continue
 col.hide_viewport=False;col.hide_render=False
 for ob in col.objects:
  ob.hide_viewport=False;ob.hide_render=False;ob.hide_set(False);restored.append(ob.name)
for ob in s.objects:
 if any(t in ob.name for t in ['Vedação vidro dianteira','Vedação vidro traseira','Divisória vidro traseiro','HILUX11 | Joint cabine caçamba']):
  ob.hide_set(True);ob.hide_render=True;ob['boas_v21_role']='legacy_reserved; replaced by current structural assembly';withheld.append(ob.name)
bpy.context.view_layer.update()
def move(ob,col,parent):
 world=ob.matrix_world.copy()
 for old in list(ob.users_collection):old.objects.unlink(ob)
 col.objects.link(ob);ob.parent=parent;ob.matrix_world=world
 ob.hide_set(False);ob.hide_render=False;ob.hide_viewport=False
 ob['boas_v21_assembly']='reused and attached to moving assembly'
# Funções geométricas usadas apenas para o campo contínuo dos novos vidros.
for file,names in [('rebuild_hilux_reference_v06.py',{'interp','sidewidth'}),('rebuild_hilux_cab_v15.py',{'smooth','roof_width','roof_edge_z','cab_side','radius','rear_y','cab_x','rounded'}),('finish_hilux_cab_v15.py',{'regular_x'}),('model_hilux_doors_v18.py',{'field','area','inside','inset'})]:
 for fn in ast.parse((r/'automation/blender'/file).read_text(encoding='utf8')).body:
  if isinstance(fn,ast.FunctionDef) and fn.name in names:exec(compile(ast.Module(body=[fn],type_ignores=[]),file,'exec'),globals())
glass_changes=[]
for label in ['dianteira','traseira']:
 for side in [-1,1]:
  handed='esquerda' if side==-1 else 'direita'
  col=bpy.data.collections['HILUX | Porta '+label+' '+handed]
  pivot=s.objects[f'RDP01 | Pivô porta {label} {side:+}']
  channel=s.objects[f'HILUX18 | Canal vidro {label} {handed}']
  loop=[channel.matrix_world@Vector(p.co[:3]) for p in channel.data.splines[0].points]
  border=[Vector((p.y,p.z)) for p in loop]
  if area(border)<0:border.reverse()
  # A borda do vidro entra no canal, sem alargar ou deslocar a folha.
  border=inset(border,-.001)
  pts=list(border);edges=[(i,(i+1)%len(border)) for i in range(len(border))]
  ly,hy=min(p.x for p in border),max(p.x for p in border);lz,hz=min(p.y for p in border),max(p.y for p in border)
  ny,nz=math.ceil((hy-ly)/.045),math.ceil((hz-lz)/.045)
  for i in range(1,ny):
   for j in range(1,nz):
    p=Vector((ly+(hy-ly)*i/ny,lz+(hz-lz)*j/nz))
    if inside(p,border):pts.append(p)
  coords,_,faces,*_=delaunay_2d_cdt(pts,edges,[],1,1e-8)
  vs=[Vector((side*(field(p.x,p.y)-.0065),p.x,p.y)) for p in coords]
  faces=[tuple(f) if side==1 else tuple(reversed(f)) for f in faces if inside(sum((coords[i] for i in f),Vector((0,0)))/len(f),border)]
  ob=s.objects[f'RDP01 | HILUX06 | Vidro {label} {side}'];ob.modifiers.clear()
  me=bpy.data.meshes.new(ob.name+' | ajuste V21');me.from_pydata(vs,[],faces);me.materials.append(bpy.data.materials['RDP01 | Vidro fumê'])
  for p in me.polygons:p.use_smooth=True
  ob.data=me;ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4)
  mod=ob.modifiers.new('Lâmina do vidro para dentro','SOLIDIFY');mod.thickness=.003;mod.offset=-1;mod.use_quality_normals=True
  move(ob,col,pivot);glass_changes.append(ob.name)
  if label=='dianteira':
   for prefix in ['Base espelho','Espelho','Vidro espelho']:
    move(s.objects[f'RDP01 | HILUX06 | {prefix} {side}'],col,pivot)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def bvh_object(ob):
 ev=ob.evaluated_get(dg);me=ev.to_mesh()
 tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
 ev.to_mesh_clear();return tree
bodytree=bvh_object(body)
door_trees={(label,side):bvh_object(s.objects[f'RDP01 | HILUX06 | Porta {label} {side}']) for label in ['dianteira','traseira'] for side in [-1,1]}
def project(p,face,tree,offset):
 if face in [-1,1]:origin=Vector((face*2,p.y,p.z));direction=Vector((-face,0,0));normal=-direction
 elif face=='rear':origin=Vector((p.x,3.5,p.z));direction=Vector((0,-1,0));normal=-direction
 else:origin=Vector((p.x,p.y,3));direction=Vector((0,0,-1));normal=-direction
 hit,_,_,_=tree.ray_cast(origin,direction,5)
 if hit is None:return p,False
 return hit+normal*offset,True
# Letreiro dividido na junta real: cada metade acompanha sua porta.
textparts=[]
for side in [-1,1]:
 original=s.objects[f'RDP01 | HILUX10 | POLÍCIA MILITAR {side}']
 original_world=original.matrix_world.copy();original_mesh=original.data.copy()
 for label in ['dianteira','traseira']:
  ob=original if label=='dianteira' else bpy.data.objects.new(original.name+' | porta traseira',original_mesh.copy())
  if label=='traseira':
   for key in original.keys():ob[key]=original[key]
   bpy.data.collections['RDP01 | INSCRICOES'].objects.link(ob);ob.matrix_world=original_world
  bm=bmesh.new();bm.from_mesh(original_mesh)
  for v in bm.verts:v.co=original_world@v.co
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=Vector((0,.174,.516)),plane_no=Vector((0,1,-.012/1.234)),clear_outer=label=='dianteira',clear_inner=label=='traseira')
  me=bpy.data.meshes.new(ob.name+' | junta V21');bm.to_mesh(me);bm.free();me.materials.append(bpy.data.materials['RDP01 | Inscrição branca'])
  ob.data=me;ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4)
  ob['boas_v21_door_label']=label;ob['boas_v21_side']=side;textparts.append(ob)
# Reprojetar a identificação sobre as superfícies atuais; não alterar as chapas.
projected=[];misses=[]
for ob in list(bpy.data.collections['RDP01 | INSCRICOES'].objects):
 if ob.type not in ['MESH','CURVE']:continue
 world=ob.matrix_world.copy()
 points=list(ob.data.vertices) if ob.type=='MESH' else [p for spl in ob.data.splines for p in spl.points]
 if not points:continue
 coords=[world@Vector(p.co[:3]) for p in points];center=sum(coords,Vector((0,0,0)))/len(coords)
 if ob.name.endswith('Prefixo vidro'):continue # Capota e vidro traseiro preservados.
 if center.z>1.20 and abs(center.x)<.4 and center.y<-1.3:face='hood'
 elif center.y>2.7 and abs(center.x)<.8:face='rear'
 else:face=-1 if center.x<0 else 1
 label=ob.get('boas_v21_door_label')
 if face in [-1,1] and -.9<center.y<1.05:
  label=label or ('dianteira' if center.y<.174 else 'traseira')
  tree=door_trees[(label,face)]
 else:tree=bodytree
 offset=.002
 if ob.type=='CURVE':offset=ob.data.bevel_depth+.0012
 if 'Campo brasão' in ob.name:offset=.0013
 if 'Bordadura brasão' in ob.name:offset=ob.data.bevel_depth+.002
 if 'Armas cruzadas' in ob.name or 'Espada' in ob.name or 'Marca bordadura' in ob.name:offset=ob.data.bevel_depth+.003
 invmat=world.inverted();bad=0
 for v,p in zip(points,coords):
  q,hit=project(p,face,tree,offset)
  if not hit:bad+=1;continue
  q=invmat@q
  v.co=q if ob.type=='MESH' else (*q,v.co.w)
 if ob.type=='MESH':ob.data.update()
 projected.append(ob.name)
 if bad:misses.append({'object':ob.name,'points_without_support':bad})
 if face in [-1,1] and label:
  pivot=s.objects[f'RDP01 | Pivô porta {label} {face:+}'];handed='esquerda' if face==-1 else 'direita'
  move(ob,bpy.data.collections['HILUX | Porta '+label+' '+handed],pivot)
# Preservar as cores existentes, mas habilitar sua leitura no viewport.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.shading.use_scene_lights=False;sp.shading.use_scene_world=False;sp.shading.studiolight_rotate_z=.6
   sp.overlay.show_overlays=False
   sp.region_3d.view_rotation=(Vector((0,.15,1.05))-Vector((-7,-8,3.1))).to_track_quat('-Z','Y')
   sp.region_3d.view_location=(0,.15,1.05);sp.region_3d.view_distance=7.;sp.region_3d.view_perspective='PERSP'
for ob in s.objects:ob.select_set(False)
bpy.context.view_layer.objects.active=body
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
s.camera.location=(-7,-8,3.1);s.camera.rotation_euler=(Vector((0,.15,1.03))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=6.8
s['boas_v21_assembly_applied']=True;s['boas_authoring_mode']='assembled_review'
s['boas_next_scope']='Revisão visual do veículo completo com pintura; fidelidade fina ainda candidata.'
bpy.context.view_layer.update()
assert all(fingerprint(s.objects[n])==h for n,h in protected.items())
report={'asset_id':'vehicle-rondesp-pickup','status':'candidate','parent':'blender/assets/vehicles/rondesp-pickup/hilux_chapa_v20.blend','parent_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'authoring_mode':'assembled_review','base_body_and_doors_unchanged':True,'protected_mesh_hashes':protected,'restored_objects':restored,'withheld_legacy_objects':withheld,'refitted_glass':glass_changes,'projected_inscriptions':projected,'projection_misses':misses,'door_text_split': [o.name for o in textparts], 'source_reopened':False,'runtime_exported':False,'visual_review':'pending','texture_source':'Materiais preservados, pintura procedural candidata e inscrições geométricas; sem nova textura bitmap.'}
(r/'docs/reports/blender/rondesp_marrom_v21.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Primeira vista rápida para revisar encaixes antes de salvar a nova fonte.
s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.color_type='MATERIAL';sh.light='STUDIO';sh.studio_light='paint.sl';sh.show_cavity=False;sh.show_shadows=True
s.render.filepath=str(r/'artifacts/vehicles/rondesp/v21-montada-inicial.png');bpy.ops.render.render(write_still=True)
s.render.engine='CYCLES'
print(json.dumps({'restored':len(restored),'glass_refit':len(glass_changes),'projected':len(projected),'projection_misses':misses,'protected_body_and_doors':True}))
