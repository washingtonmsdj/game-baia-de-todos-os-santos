"""Persistência, fechamento e encontros físicos do exterior B91; sem CCD."""
import bpy,bmesh,json,runpy,os,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-mesh-b91'
r=json.loads((out/'application.json').read_text());assert Path(bpy.data.filepath).name==Path(r['file']).name
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text());assert proof['file']==r['file'] and proof['sha256']==r['sha256'] and proof['load_post_completed']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
expected={}
for n in (88,89,90):
 prior=json.loads((root/f'docs/reports/blender/lacerda-massing-b{n}/application.json').read_text())
 for row in prior['changes']+prior.get('added',[]):
  state=row.get('after',row);expected[row['object']]=state.get('signature',state)
for row in r['changes']+r['added']:expected[row['object']]=row.get('after',row)['signature']
checks=[];by_name={}
for name,state in expected.items():
 o=bpy.context.scene.objects[name];assert sig(o)==state,name
 bm=bmesh.new();bm.from_mesh(o.data);groups={}
 for f in bm.faces:
  key=tuple(sorted(tuple(round(float(c),6) for c in v.co) for v in f.verts));groups.setdefault(key,[]).append(f)
 d={'object':name,'visible':o.visible_get(),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'duplicate_face_groups':sum(len(fs)>1 for fs in groups.values()),'signed_volume':bm.calc_volume(signed=True)}
 assert d['degenerate_faces']==0,name
 if d['visible']:assert d['nonmanifold_edges']==0 and d['duplicate_face_groups']==0,(name,d)
 checks.append(d);by_name[name]=d;bm.free()
def bounds(name):
 o=bpy.context.scene.objects[name];p=[inv@wm(o)@v.co for v in o.data.vertices];return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());dim=[]
for name,key in [('SUPERIOR | piso saguão','upper_floor'),('TORRE | cornija galeria','new_gallery'),('LAC R30B | Passarela | piso paginado visual','bridge'),('CALIBRADO | passarela piso 28.71 x 6.00m','bridge'),('INFERIOR | piso do saguão','lower_floor'),('CASCA | parede lateral','new_core')]:
 bb=bounds(name);p=cfg['polygons'][key]['points_local'];desired=[[min(v[i] for v in p),max(v[i] for v in p)] for i in (0,1)]
 err=max(abs(bb[i][j]-desired[i][j]) for i in (0,1) for j in (0,1));assert err<1e-4,(name,err)
 dim.append({'object':name,'polygon':key,'bounds':bb,'cad_bounds_residual_m':err})
slab='CALIBRADO | passarela piso 28.71 x 6.00m';support=r['added'][0]['object']
contacts=[{'relationship':'laje estrutural → piso da ponte','gap_m':abs(bounds(slab)[2][1]-bounds('LAC R30B | Passarela | piso paginado visual')[2][0])},
 {'relationship':'intradorso → laje estrutural','gap_m':abs(bounds(slab)[2][0]-bounds('LAC R30B08 | passarela | intradorso continuo')[2][1])},
 {'relationship':'núcleo contínuo → capeamento superior','gap_m':abs(bounds('CASCA | parede lateral')[2][1]-bounds('TORRE | capeamento tecnico')[2][0])},
 {'relationship':'consolo → fundo da laje da galeria','gap_m':abs(bounds(support)[2][1]-bounds('TORRE | cornija galeria')[2][0])}]
assert all(c['gap_m']<1e-4 for c in contacts)
# Verificação independente de que a operação foi local: carregar componentes
# B90 somente como datablocks temporários nesta instância, nunca nova cena.
names=[o.name for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects]+['MVP | terreno corrigido | colisão estática']
prior=h['inspect_file'](root/r['parent_file'],names)
assert all(sig(bpy.data.objects[n])==s for n,s in prior.items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
for row in r['changes']:
 if row['operation']=='PRESERVE_AS_REFERENCE':
  o=bpy.context.scene.objects[row['object']];assert o.hide_get() and o.hide_render and sig(o)==row['before']['signature']
upper=bounds('SUPERIOR | piso saguão')[2][1];lower=bounds('INFERIOR | piso do saguão')[2][1]
assert abs(upper-lower-59.01)<1e-4
data={'revision':'R30B.91','file':r['file'],'sha256':r['sha256'],'pid':os.getpid(),'scene':bpy.context.scene.name,'reopened':True,'objects_checked':len(checks),'visible_objects_checked':sum(c['visible'] for c in checks),'checks':checks,'document_contours':dim,'structural_contacts':contacts,
 'architectural_access_difference_m':upper-lower,'ssot_preserved':True,'terrain_and_proxy_signatures_preserved':True,'removed_internal_faces':sum(c['removed_internal_faces'] for c in r['cleanup']),
 'scope':'Fechamento/topologia de malha e contatos estruturais explícitos; não constitui varredura integral de auto-interseções de todos os acabamentos, CCD ou validação do personagem',
 'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'movement_enabled':False,'absolute_ssot_fit':'NOT_ACCEPTED','interior_layout':'NOT_VALIDATED','production_ready':False}
(out/'validation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');r['reopened']=True;r['mesh_and_structure_checked']=True
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:data[k] for k in ('objects_checked','visible_objects_checked','removed_internal_faces','structural_contacts','reopened','production_ready')},ensure_ascii=False))
