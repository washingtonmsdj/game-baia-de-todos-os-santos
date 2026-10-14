"""B70: corrigir contato HQ/piso/cais, sem mover XY, vias, água ou cais."""
import bpy,bmesh,json,hashlib,math,runpy,shutil,numpy as np
from pathlib import Path
from mathutils import Vector,Euler
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf8'));src=cat['validation_source']
assert src['revision']=='R30B.69' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
out=r/'blender/salvador_lacerda_r30b70_juncao_terreno_cais.blend';assert not out.exists()
assert shutil.disk_usage(r).free>(r/src['file']).stat().st_size*2+160*1024**2
probe=json.loads((r/'docs/reports/blender/coastal_junction_b70_probe.json').read_text(encoding='utf8'));data=np.load(r/'artifacts/waterfront/coastal_junction_b70.npz')
assert probe['source']['sha256']==src['sha256'] and probe['finite'] and probe['road_locked_max_change_m']==0
assert probe['floor_below_water_after']==0 and probe['floor_after']['grade_over_200percent']<=2 and probe['floor_after']['grade_p95']<.25
assert probe['hq_after']['grade_max']<=probe['hq_before']['grade_max'] and probe['hq_after']['grade_over_200percent']==0
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
hq=s.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'];fill=s.objects['B63 | VISUAL | piso contínuo até o cais']
hqc=s.objects[hq['boas_collision_partner']];fc=s.objects[fill['boas_collision_partner']]
assert sig(hq)==sig(hqc) and sig(fill)==sig(fc)
names=['MVP | terreno corrigido | colisão estática','BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro','CAIS | contenção costeira alinhada à linha de costa']
names += [o.name for o in s.objects if o.name.startswith(('B56 | COLLISION | PIER |','B57 | PIER VISUAL |','B67 |','B68 |','B63 | VISUAL | canteiro','B63 | VISUAL | meios-fios','B63 | NAV |'))]
protected={n:sig(s.objects[n]) for n in names};before={o.name:sig(o) for o in (hq,fill)}
prepared=[];qa=[]
for ob,key,col in ((hq,'hq',hqc),(fill,'fill',fc)):
 xyz=np.array([list(v.co) for v in ob.data.vertices],dtype=float);assert np.array_equal(xyz,data[key+'_xyz'])
 me=ob.data.copy();coords=xyz.copy();coords[:,2]=data[key+'_z'];me.vertices.foreach_set('co',np.asarray(coords,dtype=np.float32).ravel());me.update()
 me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
 row={'object':ob.name,'vertices':len(me.vertices),'polygons':len(me.polygons),'degenerate_triangles':sum(t.area<1e-9 for t in me.loop_triangles),'finite':all(math.isfinite(c) for v in me.vertices for c in v.co),'boundary_edges':sum(e.is_boundary for e in bm.edges),'edges_with_more_than_two_faces':sum(len(e.link_faces)>2 for e in bm.edges)}
 bm.free();assert row['finite'] and row['degenerate_triangles']==0 and row['edges_with_more_than_two_faces']==0,row
 if key=='fill':
  for p in me.polygons:p.use_smooth=True
 assert np.array_equal(coords[:,:2],xyz[:,:2]);prepared.append((ob,me,col,key));qa.append(row)
for ob,me,col,key in prepared:
 ob.data=me;col.data=me.copy()
 for item in (ob,col):
  item['boas_revision']='R30B.70';item['boas_gameplay_approved']=False;item['boas_height_status']='ADAPT_LOCAL_CURRENT_QUAY_CONTROL_NOT_SURVEYED';item['boas_source_report']='docs/reports/blender/coastal_junction_r30b70.json'
 ob['boas_b70_method']='Contato por arestas explícitas; faixa local 2m e transição até 30m para o cais existente; vias/passeios fixos.'
changed=[n for n,old in protected.items() if sig(s.objects[n])!=old];assert not changed,changed
for ob,me,col,key in prepared:assert sig(ob)==sig(col)
s['boas_validation_revision']='R30B.70';s['boas_coastal_contact_status']='HQ_floor_junction_improved_north_corner_pending'
for win in bpy.context.window_manager.windows:
 for ar in win.screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.overlay.show_extras=False
   sp.region_3d.view_location=Vector((-335,-35,7));sp.region_3d.view_distance=240;sp.region_3d.view_rotation=Euler((math.radians(48),0,math.radians(38)),'XYZ').to_quaternion();sp.region_3d.view_perspective='ORTHO'
for ob in bpy.context.selected_objects:ob.select_set(False)
fill.select_set(True);bpy.context.view_layer.objects.active=fill
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={'schema':'boas/coastal-junction-r30b70-v1','source_before':src,'source_after':{'file':out.relative_to(r).as_posix(),'revision':'R30B.70','sha256':sha},'classification':'ADAPT_LOCAL','binding_error_classification':'ERROR','basis':'mesmas arestas físicas de HQ e mesmos controles XYZ do cais existente; borda XY preservada','design_contact_band_m':2,'design_transition_limit_m':30,'real_transition_width_m':None,'real_height_verified':False,'probe_evidence':'docs/reports/blender/coastal_junction_b70_probe.json','probe':probe,'protected_signatures':protected,'protected_changes':changed,'modified_before':before,'modified_after':{ob.name:sig(ob) for ob,me,col,key in prepared},'mesh_qa':qa,'source_reopened':False,'road_locked_vertices':len(data['locked']),'road_vertices_changed':0,'xy_changed':False,'terrain_topology_changed':False,'floor_topology_changed':False,'road_width_changed':False,'source_dem_modified':False,'quay_changed':False,'water_changed':False,'visual_collision_identical':True,'runtime_exported':False,'approved':False,'pending':['Dois triângulos no encontro norte do piso/cais/núcleo; alturas 7,2557 versus ~9,0563 requerem revisão','Altimetria absoluta cais/água e fonte Aleph original ausente no caminho registrado','Inclinações do terreno adjacente e travessia real de personagem/carro não aprovadas','Acabamento e conexões viárias do restante da região']}
rp=r/'docs/reports/blender/coastal_junction_r30b70.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(r/'artifacts/waterfront/blender_revisions_before_b70.json').write_bytes(cp.read_bytes())
entry={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(r).as_posix(),'notes':'Junção HQ/piso/cais recomposta por controles locais. Vias/XY/água/cais preservados; dois triângulos no extremo norte e datum real pendentes.'}
for old in cat['revisions']:
 if old['file']==src['file']:old['status']='superseded_validation'
cat['revisions'].append(entry);cat['validation_source']=entry.copy();cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source':report['source_after'],'protected_changes':changed,'qa':qa}))
