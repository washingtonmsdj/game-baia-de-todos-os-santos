"""Confronta curvas OSM existentes com eixos do grafo e relevo da fonte ativa."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Abrir a fonte em uma chamada separada antes da inspeção')
bpy.context.view_layer.update()
targets={421206045,48846625};out=[]
for o in bpy.context.scene.objects:
    props={k:str(o[k]) for k in o.keys()}
    explicit=any(str(id) in props.values() for id in targets)
    if not explicit and not any(s in o.name.casefold() for s in ('conceição','montanha')):continue
    row={'name':o.name,'type':o.type,'properties':props,'matrix_world':[list(r) for r in o.matrix_world]}
    if o.type=='CURVE':
        row['curves']=[[list(o.matrix_world@Vector(p.co[:3])) for p in sp.points] for sp in o.data.splines]
        row['bevel_depth']=o.data.bevel_depth
    out.append(row)
(root/'docs/reports/blender/terrain_real_roads_objects.json').write_text(json.dumps({'source':c['world_source'],'objects':out},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{'name':r['name'],'type':r['type'],'properties':r['properties'],'points':sum(len(s) for s in r.get('curves',[]))} for r in out],ensure_ascii=False))
