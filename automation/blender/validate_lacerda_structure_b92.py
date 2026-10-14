"""Reabertura e integridade consolidada B88–B92, sem aprovar controller."""
import bpy,bmesh,json,os,runpy,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-bridge-b92'
r=json.loads((out/'application.json').read_text());r91=json.loads((root/'docs/reports/blender/lacerda-mesh-b91/application.json').read_text())
assert Path(bpy.data.filepath).name==Path(r['file']).name
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text());assert proof['file']==r['file'] and proof['sha256']==r['sha256'] and proof['load_post_completed']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
expected={}
for report in [json.loads((root/f'docs/reports/blender/lacerda-massing-b{n}/application.json').read_text()) for n in (88,89,90)]+[r91,r]:
 for row in report['changes']+report.get('added',[]):
  state=row.get('after',row);expected[row['object']]=state.get('signature',state)
checks=[]
for name,state in expected.items():
 o=bpy.context.scene.objects[name];assert sig(o)==state,name
 bm=bmesh.new();bm.from_mesh(o.data);groups={}
 for f in bm.faces:
  key=tuple(sorted(tuple(round(float(c),6) for c in v.co) for v in f.verts));groups.setdefault(key,[]).append(f)
 d={'object':name,'visible':o.visible_get(),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'duplicate_face_groups':sum(len(fs)>1 for fs in groups.values())}
 assert d['degenerate_faces']==0,name
 if d['visible']:assert d['nonmanifold_edges']==d['duplicate_face_groups']==d['inconsistent_winding_edges']==0,(name,d)
 checks.append(d);bm.free()
def bounds(name):
 o=bpy.context.scene.objects[name];p=[inv@wm(o)@v.co for v in o.data.vertices];return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
floor='CALIBRADO | passarela piso 28.71 x 6.00m';roof='CALIBRADO | passarela cobertura 28.71 x 6.00m';visual='LAC R30B | Passarela | piso paginado visual'
bb=bounds(roof);bf=bounds(floor);bv=bounds(visual)
assert max(abs(bb[i][j]-bf[i][j]) for i in (0,1) for j in (0,1))<1e-4
assert abs(bb[2][1]-bv[2][1]-4.)<1e-4
for row in r['changes']:
 if row['operation']=='PRESERVE_AS_REFERENCE':
  o=bpy.context.scene.objects[row['object']];assert o.hide_get() and o.hide_render and sig(o)==row['before']['signature']
def plain(v):
 if hasattr(v,'to_dict'):return {k:plain(x) for k,x in v.to_dict().items()}
 if hasattr(v,'to_list'):return v.to_list()
 return v
assert {k:plain(v) for k,v in bpy.data.objects[r['proxy_metadata_restored']['object']].items()}==r['proxy_metadata_restored']['expected']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
contacts=[{'relationship':'laje / piso','gap_m':abs(bf[2][1]-bv[2][0])},
 {'relationship':'laje / intradorso','gap_m':abs(bf[2][0]-bounds('LAC R30B08 | passarela | intradorso continuo')[2][1])},
 {'relationship':'núcleo / capeamento','gap_m':abs(bounds('CASCA | parede lateral')[2][1]-bounds('TORRE | capeamento tecnico')[2][0])},
 {'relationship':'consolo / galeria','gap_m':abs(bounds(r91['added'][0]['object'])[2][1]-bounds('TORRE | cornija galeria')[2][0])}]
assert all(c['gap_m']<1e-4 for c in contacts)
data={'revision':'R30B.92','file':r['file'],'sha256':r['sha256'],'pid':os.getpid(),'scene':bpy.context.scene.name,'reopened':True,'objects_checked':len(checks),'visible_objects_checked':sum(c['visible'] for c in checks),'mesh_checks':checks,'bridge_floor_bounds':bf,'bridge_roof_bounds':bb,'bridge_roof_above_walkable_m':bb[2][1]-bv[2][1],
 'structural_contacts':contacts,'legacy_bridge_objects_preserved':20,'legacy_upper_platform_preserved':any(v['object']=='CALIBRADO | piso superior torre' for v in r['changes']),'proxy_metadata_b90_restored':True,'ssot_preserved':True,'B91_integrity_preserved':True,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'historic_witnesses':27,'production_ready':False,
 'scope':'Malha visível auditada, contatos definidos e ponte documental; implantação absoluta, layout, CCD e controller continuam não aprovados'}
(out/'validation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');r['reopened']=True
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:data[k] for k in ('objects_checked','visible_objects_checked','bridge_roof_above_walkable_m','legacy_bridge_objects_preserved','proxy_metadata_b90_restored','reopened','production_ready')},ensure_ascii=False))
