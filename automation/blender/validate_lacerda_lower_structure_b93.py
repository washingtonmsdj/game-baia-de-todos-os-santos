"""Persistência, contornos e encontros B93; não aprova CCD/controller."""
import bpy,bmesh,json,os,runpy,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-lower-structure-b93'
r=json.loads((out/'application.json').read_text());cfg=json.loads((out/'controls.json').read_text());before=json.loads((out/'before.json').read_text())
assert Path(bpy.data.filepath).name==Path(r['file']).name and os.getpid()==r['pid']
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text());assert proof['file']==r['file'] and proof['sha256']==r['sha256'] and proof['load_post_completed']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted();scene=bpy.context.scene
expected={}
for n in (88,89,90):
    report=json.loads((root/f'docs/reports/blender/lacerda-massing-b{n}/application.json').read_text())
    for row in report['changes']+report.get('added',[]):expected[row['object']]=row.get('after',row).get('signature',row.get('after',row))
for folder in ('lacerda-mesh-b91','lacerda-bridge-b92','lacerda-lower-structure-b93'):
    report=json.loads((root/f'docs/reports/blender/{folder}/application.json').read_text())
    for row in report['changes']+report.get('added',[]):expected[row['object']]=row.get('after',row).get('signature',row.get('after',row))
checks=[]
for name,state in expected.items():
    o=scene.objects[name];assert sig(o)==state,name
    bm=bmesh.new();bm.from_mesh(o.data);groups={}
    for f in bm.faces:
        key=tuple(sorted(tuple(round(float(c),6) for c in v.co) for v in f.verts));groups.setdefault(key,[]).append(f)
    d={'object':name,'visible':o.visible_get(),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'duplicate_face_groups':sum(len(fs)>1 for fs in groups.values()),'signed_volume':bm.calc_volume(signed=True)}
    if d['visible']:assert d['degenerate_faces']==d['nonmanifold_edges']==d['inconsistent_winding_edges']==d['duplicate_face_groups']==0,(name,d)
    checks.append(d);bm.free()
changed={row['object'] for row in r['changes']};protected=0
for row in before['rows']:
    if row['object'] in changed:continue
    o=scene.objects[row['object']];assert sig(o)==row['signature'] and o.visible_get()==row['visible'],o.name;protected+=1
for row in r['changes']:
    if row['operation']=='PRESERVE_AS_REFERENCE':
        o=scene.objects[row['object']];assert sig(o)==row['before']['signature'] and o.hide_get() and o.hide_render,o.name
def bounds(name):
    o=scene.objects[name];p=[inv@wm(o)@v.co for v in o.data.vertices];return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
floor=bounds('INFERIOR | piso do saguão');roof=bounds('INFERIOR | cobertura do saguão');core=bounds('CASCA | parede lateral')
assert abs(roof[2][1]-cfg['levels']['roof_world'])<1e-4
assert abs(roof[2][1]-floor[2][1]-5.84)<1e-4
contacts=[{'relationship':'cobertura inferior / núcleo','gap_m':abs(roof[2][1]-core[2][0])}]
for name in ('INFERIOR | parede lateral','INFERIOR | parede lateral.001'):
    bb=bounds(name);contacts.extend([{'relationship':name+' / cobertura','gap_m':abs(bb[2][1]-roof[2][0])},{'relationship':name+' / piso','gap_m':abs(bb[2][0]-floor[2][1])}])
for row in r['added']:
    bb=bounds(row['object']);contacts.extend([{'relationship':row['object']+' / cobertura','gap_m':abs(bb[2][1]-roof[2][0])},{'relationship':row['object']+' / base laje','gap_m':abs(bb[2][0]-floor[2][0])}])
assert all(c['gap_m']<1e-4 for c in contacts)
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
def plain(v):
    if hasattr(v,'to_dict'):return {k:plain(x) for k,x in v.to_dict().items()}
    if hasattr(v,'to_list'):return v.to_list()
    return v
for n,state in r['proxy_before'].items():
    o=bpy.data.objects[n];assert sig(o)==state['signature'] and {k:plain(v) for k,v in o.items()}==state['properties'],n
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==r['terrain_signature']
# Comparação independente com a B92 preservada, na mesma janela, sem carregar
# outra cena como ativa. O import temporário é removido pelo helper.
names=list(r['proxy_before'])+['MVP | terreno corrigido | colisão estática']
parent=h['inspect_file'](root/r['parent_file'],names)
assert all(sig(bpy.data.objects[n])==parent[n] for n in names)
q={'revision':'R30B.93','file':r['file'],'sha256':r['sha256'],'pid':os.getpid(),'scene':scene.name,'reopened':True,'objects_checked':len(checks),'visible_objects_checked':sum(c['visible'] for c in checks),'protected_scoped_objects':protected,'mesh_checks':checks,'roof_delta_m':r['roof_delta_applied'],'roof_above_hall_floor_m':roof[2][1]-floor[2][1],'structural_contacts':contacts,'legacy_front_preserved':r['legacy_front_preserved'],'proxy_b82_matches_parent_b92':True,'terrain_matches_parent_b92':True,'ssot_preserved':True,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'historic_witnesses':27,'absolute_map_placement':'NEEDS_REVIEW','production_ready':False,'scope':'Malhas/contatos arquitetônicos relativos; não comprova implantação absoluta, interiores, CCD, controller ou acesso ao terreno.'}
(out/'validation.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8');r['reopened']=True;(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:q[k] for k in ('objects_checked','visible_objects_checked','roof_above_hall_floor_m','legacy_front_preserved','proxy_b82_matches_parent_b92','terrain_matches_parent_b92','reopened')},ensure_ascii=False))
