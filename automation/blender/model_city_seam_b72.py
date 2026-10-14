"""B72: junção viária compartilhada e pavimento contínuo nas superfícies atuais."""
import bpy,bmesh,json,hashlib,runpy,shutil,numpy as np
from pathlib import Path
from array import array

def coordinate_hash(me):
 a=array('f',[0])*(len(me.vertices)*3);me.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
def topology_hash(me):
 h=hashlib.sha256()
 for table,key in [(me.loops,'vertex_index'),(me.polygons,'loop_start'),(me.polygons,'loop_total')]:
  a=array('i',[0])*len(table);table.foreach_get(key,a);h.update(a.tobytes())
 return h.hexdigest()
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf8'));src=cat['validation_source']
assert src['revision']=='R30B.71' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
out=r/'blender/salvador_lacerda_r30b72_costura_viaria_continua.blend';assert not out.exists()
assert shutil.disk_usage(r).free>(r/src['file']).stat().st_size*2+300*1024**2
candidate=json.loads((r/'docs/reports/blender/manoel_transition_b72_candidate.json').read_text(encoding='utf8'));assert candidate['source']['sha256']==src['sha256'] and candidate['finite']
for p in candidate['profiles']:
 assert p['missing_supports']==0
 if p['osm_way_id']==456471269:assert p['max_crossfall_after']<.04 and p['max_grade_after']<.17
 if p['osm_way_id']==154743329:assert p['max_crossfall_after']<.04 and p['max_grade_after']<.17
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
names=['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B63 | VISUAL | piso contínuo até o cais']
objects=[s.objects[n] for n in names];modified=set(names)
for o in objects:
 if o.get('boas_collision_partner'):modified.add(o['boas_collision_partner'])
oldreport=json.loads((r/'docs/reports/blender/north_junction_r30b71.json').read_text(encoding='utf8'))
protected_names=(set(oldreport['protected_signatures'])|{'CAIS | contenção costeira alinhada à linha de costa','B64 | COLLISION | cais e borda marítima'})-modified
protected={n:sig(s.objects[n]) for n in sorted(protected_names)}
contract=json.loads((r/'world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json').read_text(encoding='utf8'));roads=[x for x in contract['roads'] if x['role']=='road_driveable']
ref=json.loads((r/'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json').read_text(encoding='utf8'));byid={f['osm_id']:f for f in ref['features'] if f['layer']=='roads'}
segments=[]
for rec in roads:
 assert rec['blender_xy']==byid[rec['osm_way_id']]['blender_xy']
 for a,b in zip(rec['blender_xy'],rec['blender_xy'][1:]):
  a=np.array(a);d=np.array(b)-a;ll=float(d@d)
  if ll>1e-8:segments.append((a,d,ll,float(rec['gameplay_width_m'])/2,rec))
data=np.load(r/'artifacts/waterfront/manoel_transition_b72.npz');prepared=[];qa=[];rows=[];before={o.name:sig(o) for o in objects}
baseline={x['object']:x for x in json.loads((r/'docs/reports/blender/city_seam_b72_baseline.json').read_text(encoding='utf8'))['rows']}
coordinate_before={o.name:coordinate_hash(o.data) for o in objects};topology_before={o.name:topology_hash(o.data) for o in objects}
for ob in objects:
 old=ob.data;me=old.copy();xyz=np.array([list(v.co) for v in old.vertices],float)
 if ob.name.startswith('B62'):
  assert np.array_equal(xyz,data['xyz'])
  coords=xyz.copy();coords[:,2]=data['z'];me.vertices.foreach_set('co',coords.astype(np.float32).ravel());me.update()
  assert np.array_equal(coords[data['locked']],xyz[data['locked']])
 centers=np.array([list(ob.matrix_world@p.center) for p in me.polygons],float)
 best=np.full(len(centers),np.inf);which=np.full(len(centers),-1,dtype=int)
 for k,(a,d,ll,half,rec) in enumerate(segments):
  sel=np.where((centers[:,0]>=min(a[0],a[0]+d[0])-half)&(centers[:,0]<=max(a[0],a[0]+d[0])+half)&(centers[:,1]>=min(a[1],a[1]+d[1])-half)&(centers[:,1]<=max(a[1],a[1]+d[1])+half))[0]
  if not len(sel):continue
  t=np.clip(((centers[sel,:2]-a)@d)/ll,0,1);dist=np.linalg.norm(centers[sel,:2]-a-t[:,None]*d,axis=1);good=(dist<=half)&(dist/half<best[sel]);ids=sel[good];best[ids]=dist[good]/half;which[ids]=k
 roles=me.attributes.get('boas_surface_role') or me.attributes.new(name='boas_surface_role',type='INT',domain='FACE')
 ids=me.attributes.get('boas_osm_way_id') or me.attributes.new(name='boas_osm_way_id',type='INT',domain='FACE')
 slots={}
 for matname in ['MVP | asfalto da ladeira','VIAS | pavimento de pedra Rua Chile']:
  mat=bpy.data.materials[matname];index=next((i for i,m in enumerate(me.materials) if m==mat),None)
  if index is None:me.materials.append(mat);index=len(me.materials)-1
  slots[matname]=index
 changes=0;counts={}
 for fi in np.where(which>=0)[0]:
  p=me.polygons[int(fi)];rec=segments[int(which[fi])][4]
  # Não converter passeios/praças existentes automaticamente em pista.
  if ob.name.startswith('MVP') and p.material_index not in (0,2,5):continue
  if roles.data[p.index].value==2:continue
  matname='VIAS | pavimento de pedra Rua Chile' if rec.get('surface')=='sett' else 'MVP | asfalto da ladeira'
  target=slots[matname];changes+=int(p.material_index!=target);p.material_index=target
  roles.data[p.index].value=1;ids.data[p.index].value=int(rec['osm_way_id']);p.use_smooth=True
  key=str(rec['osm_way_id']);counts[key]=counts.get(key,0)+1
 me.update();me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
 row={'object':ob.name,'degenerate_triangles':sum(t.area<1e-9 for t in me.loop_triangles),'edges_more_than_two_faces':sum(len(e.link_faces)>2 for e in bm.edges),'finite':bool(np.isfinite(np.array([v.co for v in me.vertices])).all()),'vertices':len(me.vertices),'polygons':len(me.polygons)}
 bm.free();row['degenerate_triangles_before']=baseline[ob.name]['degenerate_triangles'];assert row['degenerate_triangles']==row['degenerate_triangles_before'] and row['edges_more_than_two_faces']==0 and row['finite']
 assert topology_hash(me)==topology_before[ob.name]
 if not ob.name.startswith('B62'):assert coordinate_hash(me)==coordinate_before[ob.name]
 assert len(me.vertices)==len(old.vertices) and len(me.polygons)==len(old.polygons)
 partner=s.objects.get(ob.get('boas_collision_partner',''))
 prepared.append((ob,partner,me));qa.append(row);rows.append({'object':ob.name,'pavement_material_changed_faces':changes,'source_osm_face_counts':counts,'xy_topology_changed':False,'coordinates_changed':ob.name.startswith('B62')})
for ob,partner,me in prepared:
 ob.data=me
 if partner:partner.data=me.copy()
 for o in [ob]+([partner] if partner else []):
  o['boas_revision']='R30B.72';o['boas_source_report']='docs/reports/blender/city_seam_r30b72.json';o['boas_gameplay_approved']=False;o['boas_road_width_status']='ADAPT_GAMEPLAY_NOT_SURVEYED';o['boas_road_binding_status']='OSM_IDS_SHARED_REFERENCE_CANDIDATE'
changes=[n for n,old in protected.items() if sig(s.objects[n])!=old];assert not changes
s['boas_validation_revision']='R30B.72'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={'schema':'boas/city-seam-r30b72-v1','source_before':src,'source_after':{'file':out.relative_to(r).as_posix(),'revision':'R30B.72','sha256':sha},'classification':'ADAPT_LOCAL','missing_pavement_classification':'ERROR','candidate':candidate,'pavement':rows,'mesh_qa':qa,'coordinate_hash_before':coordinate_before,'coordinate_hash_after':{o.name:coordinate_hash(o.data) for o in objects},'topology_hash_before':topology_before,'topology_hash_after':{o.name:topology_hash(o.data) for o in objects},'modified_before':before,'modified_after':{o.name:sig(o) for o in objects},'protected_signatures':protected,'protected_changes':changes,'source_reopened':False,'core_coordinates_changed':False,'floor_coordinates_changed':False,'xy_changed':False,'topology_changed':False,'road_widths_changed':False,'source_dem_changed':False,'real_dimensions_verified':False,'geographic_fit_verified':False,'approved':False,'runtime_exported':False,'pending':['94 triângulos degenerados preexistentes no terreno antigo, sem reparo nesta passagem','Georreferenciamento ainda candidato; não certifica toda a cidade','Vias fora dos oito corredores e domínio sem terreno não foram reconstruídos','Encosta/altimetria absoluta e fonte original Aleph','Larguras reais e acesso público/ônibus pendentes','Travessia física na engine não realizada']}
rp=r/'docs/reports/blender/city_seam_r30b72.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(r/'artifacts/waterfront/blender_revisions_before_b72.json').write_bytes(cp.read_bytes())
entry={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(r).as_posix(),'notes':'Junção compartilhada Manoel/Conceição e pavimento de oito corredores nas três superfícies, mesmos IDs/XY e larguras candidatas; fidelidade global pendente.'}
for e in cat['revisions']:
 if e['file']==src['file']:e['status']='superseded_validation'
cat['revisions'].append(entry);cat['validation_source']=entry.copy();cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source':report['source_after'],'pavement':rows,'qa':qa}))
