"""Auditoria read-only dos encontros e malhas arquitetônicas B90."""
import bpy,bmesh,json,runpy,os
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b90_cotas_exteriores_consolidadas.blend'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
report=json.loads((root/'docs/reports/blender/lacerda-massing-b88/application.json').read_text())
names={r['object'] for r in report['changes']+report['added']}
names.update(['CALIBRADO | passarela piso 28.71 x 6.00m','LAC R30B07 | galeria | consolo inclinado'])
global_faces={};rows=[]
for name in sorted(names):
    o=bpy.context.scene.objects.get(name)
    if o is None or o.type!='MESH':continue
    tr=inv@wm(o);p=[tr@v.co for v in o.data.vertices]
    bounds=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
    bm=bmesh.new();bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table();bm.verts.ensure_lookup_table()
    face_map={}
    for f in bm.faces:
        key=tuple(sorted(tuple(round(float(x),6) for x in tr@v.co) for v in f.verts))
        face_map.setdefault(key,[]).append(f.index)
        if o.visible_get() and 'COLLISION' not in name and o.get('boas_physical_enabled') is not False:
            global_faces.setdefault(key,[]).append({'object':name,'face':f.index,'normal':list(f.normal)})
    pairs=[ids for ids in face_map.values() if len(ids)>1]
    seen=set();components=0
    for v in bm.verts:
        if v.index in seen:continue
        components+=1;queue=[v]
        while queue:
            a=queue.pop()
            if a.index in seen:continue
            seen.add(a.index);queue.extend(e.other_vert(a) for e in a.link_edges)
    rows.append({'object':name,'visible':o.visible_get(),'hide_render':o.hide_render,'collections':[c.name for c in o.users_collection],
      'properties':{k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))},'materials':[m.name if m else None for m in o.data.materials],
      'bounds':bounds,'vertices':len(bm.verts),'faces':len(bm.faces),'components':components,'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),
      'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'wire_edges':sum(e.is_wire for e in bm.edges),
      'signed_volume_local':bm.calc_volume(signed=True),'duplicate_face_groups':pairs,'signature':sig(o)})
    bm.free()
cross=[v for v in global_faces.values() if len({r['object'] for r in v})>1]
data={'revision':'B90','pid':os.getpid(),'file':Path(bpy.data.filepath).relative_to(root).as_posix(),'scene':bpy.context.scene.name,'rows':rows,'cross_object_coincident_faces':cross,
 'scope':'Apenas componentes arquitetônicos B88–B90 e duas fontes históricas explícitas; duplicidade não é classificação automática de erro.'}
out=root/'docs/reports/blender/lacerda-mesh-b91';out.mkdir(parents=True,exist_ok=True)
(out/'before.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects':len(rows),'visible':sum(r['visible'] for r in rows),'duplicates':[{'object':r['object'],'groups':len(r['duplicate_face_groups']),'components':r['components']} for r in rows if r['duplicate_face_groups']],
 'cross_object_groups':len(cross),'nonmanifold':[{'object':r['object'],'edges':r['nonmanifold_edges']} for r in rows if r['visible'] and r['nonmanifold_edges']],
 'targets':[{k:r[k] for k in ('object','visible','bounds','materials','properties')} for r in rows if r['object'] in ['SUPERIOR | cobertura corpo elevado','EDIFICIO | cobertura','LAC R30B07 | galeria | consolo inclinado','CASCA | parede lateral','TORRE | cornija galeria','CALIBRADO | passarela piso 28.71 x 6.00m']]},ensure_ascii=False))
