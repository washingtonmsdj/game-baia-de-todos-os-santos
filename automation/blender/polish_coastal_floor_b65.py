"""B65: limpa resíduos da superfície nova; preserva costa, pistas e píeres."""
import bpy,bmesh,json,hashlib,runpy,shutil
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];sc=bpy.context.scene;cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf8'));src=cat['validation_source'];assert src['revision']=='R30B.64'
assert Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
out=r/'blender/salvador_lacerda_r30b65_piso_orla_sem_residuos.blend';assert not out.exists()
assert shutil.disk_usage(r).free>400*1024**2,'Espaço insuficiente para revisão segura'
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
fill=sc.objects['B63 | VISUAL | piso contínuo até o cais'];quay=sc.objects['CAIS | contenção costeira alinhada à linha de costa'];water=sc.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro']
protected={o.name:sig(o) for o in [water,sc.objects['MVP | terreno corrigido | colisão estática'],sc.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa']]+[o for o in sc.objects if o.name.startswith(('B56 | COLLISION | PIER |','B57 | PIER VISUAL |'))]}
water.data.calc_loop_triangles();wv=[water.matrix_world@v.co for v in water.data.vertices];wt=BVHTree.FromPolygons(wv,[list(t.vertices) for t in water.data.loop_triangles],all_triangles=True)
def wet(p):
 h=wt.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),300)[0]
 return h is not None and abs(h.z-.35)<.001
rows=[]
for ob in (fill,quay):
 bm=bmesh.new();bm.from_mesh(ob.data);before={'vertices':len(bm.verts),'faces':len(bm.faces)}
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
 if ob==fill:bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
 bad=[f for f in bm.faces if f.calc_area()<1e-8 or (ob==fill and wet(ob.matrix_world@f.calc_center_median()))]
 removed=len(bad)
 if bad:bmesh.ops.delete(bm,geom=bad,context='FACES')
 if ob==fill:bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 me=ob.data.copy();bm.to_mesh(me);bm.free();me.update();me.calc_loop_triangles();assert not any(t.area<1e-9 for t in me.loop_triangles)
 ob.data=me;ob['boas_revision']='R30B.65';partner=sc.objects[ob['boas_collision_partner']];partner.data=me.copy();partner['boas_revision']='R30B.65'
 rows.append({'object':ob.name,'before':before,'after':{'vertices':len(me.vertices),'faces':len(me.polygons)},'removed_residual_faces':removed,'weld_distance_blender_units':1e-5,'degenerate_after':0,'collision_synchronized':True,'open_surface_intentional':True})
assert all(sig(sc.objects[n])==h for n,h in protected.items())
sc['boas_validation_revision']='R30B.65';sc['boas_waterfront_status']='coastline_and_floor_corrected_reference_detail_pending'
for ob in bpy.context.selected_objects:ob.select_set(False)
quay.select_set(True);bpy.context.view_layer.objects.active=quay
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
rep={'schema':'boas/coastal-floor-b65-v1','source_before':src,'source_after':{'file':out.relative_to(r).as_posix(),'revision':'R30B.65','sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()},'corrections':rows,'protected_changes':[],'road_geometry_preserved':True,'water_and_piers_preserved':True,'real_wall_thickness_m':None,'real_foundation_depth_m':None,'pier_bridge_width_m':None,'real_fidelity_approved':False,'runtime_exported':False,'pending':['Passarela OSM 1426173327: largura/footprint real ainda sem evidência suficiente; 11 apoios ausentes na B64.','Dimensões do cais e conferência vertical absoluta','Detalhamento do terminal e época de representação','Rede e percursos completos na engine']}
rp=r/'docs/reports/blender/coastal_floor_r30b65.json';tmp=rp.with_suffix('.tmp');tmp.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(rp)
entry={**rep['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(r).as_posix(),'notes':'Limpa somente piso novo e solda a face visível do cais; costa/terreno/pistas/píeres preservados. Fidelidade e passarela pendentes.'}
for x in cat['revisions']:
 if x['file']==src['file']:x['status']='superseded_validation'
cat['revisions'].append(entry);cat['validation_source']=entry.copy();tmp=cp.with_suffix('.tmp');payload=json.dumps(cat,ensure_ascii=False,indent=2)+'\n';tmp.write_text(payload,encoding='utf8')
try:tmp.replace(cp)
except PermissionError:
 backup=r/'artifacts/waterfront/blender_revisions_before_registration.json';backup.write_bytes(cp.read_bytes());cp.write_text(payload,encoding='utf8');assert json.loads(cp.read_text(encoding='utf8'))['validation_source']['sha256']==entry['sha256'];tmp.unlink()
print(json.dumps(rep,ensure_ascii=False))
