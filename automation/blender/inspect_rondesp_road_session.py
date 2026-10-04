"""Inventário local para preparar auditoria veicular; sem alterar a cena."""
import bpy, json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2]
s=bpy.context.scene
catalog=json.loads((r/'world/vehicles/catalog.json').read_text(encoding='utf8'))
vehicle=next(v for v in catalog['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')['authoring_base']
with bpy.data.libraries.load(str(r/vehicle['file']),link=True) as (src,dst):
    names=list(src.objects);collections=list(src.collections)
roads=[]
for o in s.objects:
    if o.name.startswith('R30A7 | ROAD |'):
        roads.append({'name':o.name,'properties':dict(o.items()),'points':[[list(o.matrix_world@Vector(p.co[:3])) for p in sp.points] for sp in o.data.splines]})
report={'file':bpy.data.filepath,'vehicle':vehicle,'vehicle_objects':names,'vehicle_collections':collections,'roads':roads,
        'test_collections':[c.name for c in bpy.data.collections if any(k in c.name for k in ['TESTE','Conceicao','GAMEPLAY'])],
        'obstacle_candidates':[{'name':o.name,'visible':o.visible_get(),'collections':[c.name for c in o.users_collection]} for o in s.objects if o.type=='MESH' and any(k in o.name.casefold() for k in ['colis','collision'])]}
p=r/'artifacts/roads/rondesp';p.mkdir(parents=True,exist_ok=True)
(p/'session_inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'roads':len(roads),'vehicle_objects':len(names),'wheel_names':[n for n in names if 'Eixo giro roda' in n],
                  'interior_names':[n for n in names if any(k in n.casefold() for k in ['volante','banco','painel','pneu'])],
                  'obstacles':report['obstacle_candidates'][:20]},ensure_ascii=False))
