"""Acabamentos de remontagem e primeira vista com materiais reais."""
import ast,bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_chapa_v20.blend' and s.get('boas_v21_assembly_applied')
assert not s.get('boas_v21_glazing_finish')
root=s.objects['RDP01_ROOT | viatura'];body=s.objects['HILUX | CARROCERIA PRINCIPAL']
def tree(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear();return t
# Recortar o adesivo na junta; os poucos pontos sobre o vão não ficam suspensos.
clipped=[];misses=[]
for ob in [o for o in s.objects if o.get('boas_v21_door_label')]:
 label=ob['boas_v21_door_label'];side=ob['boas_v21_side'];mw=ob.matrix_world.copy();inv=mw.inverted();bm=bmesh.new();bm.from_mesh(ob.data)
 for v in bm.verts:v.co=mw@v.co
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=Vector((0,.174+(-.003 if label=='dianteira' else .003),.516)),plane_no=Vector((0,1,-.012/1.234)),clear_outer=label=='dianteira',clear_inner=label=='traseira')
 t=tree(s.objects[f'RDP01 | HILUX06 | Porta {label} {side}']);bad=0
 for v in bm.verts:
  hit,*_=t.ray_cast(Vector((side*2,v.co.y,v.co.z)),Vector((-side,0,0)),5)
  if hit is None:bad+=1
  else:v.co=hit+Vector((side*.002,0,0))
  v.co=inv@v.co
 bm.to_mesh(ob.data);bm.free();ob.data.update();clipped.append(ob.name)
 if bad:misses.append({'object':ob.name,'points_without_support':bad})
# Vidro posterior da cabine: completa o vão da oficina V15, sob a capota.
for file,names in [('rebuild_hilux_reference_v06.py',{'interp','sidewidth'}),('rebuild_hilux_cab_v15.py',{'smooth','roof_width','roof_edge_z','cab_side','radius','rear_y','wall_width','wall_y'}),('model_hilux_doors_v18.py',{'area','inside'})]:
 for fn in ast.parse((r/'automation/blender'/file).read_text(encoding='utf8')).body:
  if isinstance(fn,ast.FunctionDef) and fn.name in names:exec(compile(ast.Module(body=[fn],type_ignores=[]),file,'exec'),globals())
col=bpy.data.collections['RDP01 | VIDROS'];border=[]
for i in range(128):
 a=i*math.tau/128;c,si=math.cos(a),math.sin(a)
 border.append(Vector((.660*math.copysign(abs(c)**(1/3),c),1.528+.190*math.copysign(abs(si)**(1/3),si))))
pts=list(border);edges=[(i,(i+1)%len(border)) for i in range(len(border))]
for i in range(1,33):
 for j in range(1,13):
  p=Vector((-.660+1.320*i/33,1.338+.380*j/13))
  if inside(p,border):pts.append(p)
coords,_,faces,*_=delaunay_2d_cdt(pts,edges,[],1,1e-8)
me=bpy.data.meshes.new('HILUX21 | Vidro posterior cabine');me.from_pydata([(p.x,wall_y(abs(p.x),p.y)-.004,p.y) for p in coords],[],[tuple(reversed(f)) for f in faces if inside(sum((coords[i] for i in f),Vector((0,0)))/len(f),border)])
me.materials.append(bpy.data.materials['RDP01 | Vidro fumê'])
for p in me.polygons:p.use_smooth=True
ob=bpy.data.objects.new(me.name,me);col.objects.link(ob);ob.parent=root;ob['boas_component']='cab_rear_glass';ob['boas_asset_id']='vehicle-rondesp-pickup';ob['boas_shape_status']='candidate; follows authored V15 aperture'
mod=ob.modifiers.new('Espessura interna vidro','SOLIDIFY');mod.thickness=.003;mod.offset=-1;mod.use_quality_normals=True
cu=bpy.data.curves.new('HILUX21 | Vedação vidro posterior cabine','CURVE');cu.dimensions='3D';cu.bevel_depth=.003;cu.bevel_resolution=3
spl=cu.splines.new('POLY');spl.points.add(len(border)-1);spl.use_cyclic_u=True
for v,p in zip(spl.points,border):v.co=(p.x,wall_y(abs(p.x),p.y)-.001,p.y,1)
cu.materials.append(bpy.data.materials['RDP01 | Polímero preto']);seal=bpy.data.objects.new(cu.name,cu);col.objects.link(seal);seal.parent=root;seal['boas_component']='cab_rear_glass_seal';seal['boas_asset_id']='vehicle-rondesp-pickup'
# Reassentar sapatas e pés do rack na superfície atual do teto.
bpy.context.view_layer.update();bt=tree(body);supports=[]
for side in [-1,1]:
 for y in [-.1,.49]:
  hit,*_=bt.ray_cast(Vector((side*.56,y,3)),Vector((0,0,-1)),3);assert hit is not None
  for prefix,zlo,zhi in [('Sapata teto',hit.z-.001,hit.z+.023),('Pé rack',hit.z+.020,1.862)]:
   ob=s.objects[f'RDP01 | HILUX11 | {prefix} {str((side,y))}'];mw=ob.matrix_world.copy();im=mw.inverted()
   vs=[mw@v.co for v in ob.data.vertices];lo,hi=min(p.z for p in vs),max(p.z for p in vs)
   assert zhi>zlo
   for v,p in zip(ob.data.vertices,vs):p.z=zlo+(p.z-lo)/(hi-lo)*(zhi-zlo);v.co=im@p
   ob.data.update();supports.append(ob.name)
s['boas_v21_glazing_finish']=True
rp=r/'docs/reports/blender/rondesp_marrom_v21.json';report=json.loads(rp.read_text(encoding='utf8'));report['projection_misses_after_finish']=misses;report['door_decals_trimmed_at_gap']=clipped;report['new_cab_glazing']=[ob.name for ob in [s.objects['HILUX21 | Vidro posterior cabine'],seal]];report['roof_supports_refitted']=supports
report['material_settings']={mat.name:{sock.name:list(sock.default_value) if hasattr(sock.default_value,'__len__') else sock.default_value for sock in mat.node_tree.nodes.get('Principled BSDF').inputs if sock.name in ['Base Color','Roughness','Metallic','Transmission Weight','Alpha']} for mat in bpy.data.materials if mat.use_nodes and mat.node_tree.nodes.get('Principled BSDF')}
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Cycles para exibir pintura, lentes e reflexos com as luzes do estúdio.
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.cycles.device='CPU'
s.render.resolution_x=1280;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX';s.view_settings.exposure=.4
s.camera.location=(-7,-8,3.1);s.camera.rotation_euler=(Vector((0,.15,1.03))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=6.8
s.render.filepath=str(r/'artifacts/vehicles/rondesp/v21-frente-materiais.png');bpy.ops.render.render(write_still=True)
print(json.dumps({'material_view':s.render.filepath,'clipped_decals':len(clipped),'remaining_projection_misses':misses,'cab_rear_glass_added':True}))
