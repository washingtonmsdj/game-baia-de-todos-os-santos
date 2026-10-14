"""Levantamento read-only do corredor e suas superfícies na B76."""
import bpy,json,math,runpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-corridor';out.mkdir(parents=True,exist_ok=True)
source=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
assert source['revision']=='R30B.76' and Path(bpy.data.filepath).resolve()==(root/source['file']).resolve()
rows=[];surfaces=[]
def bounds(ob):
    p=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    return {'min':[min(v[i] for v in p) for i in range(3)],'max':[max(v[i] for v in p) for i in range(3)]}
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    bb=bounds(ob)
    if bb['max'][0]<-180 or bb['min'][0]>80 or bb['max'][1]<-70 or bb['min'][1]>245:continue
    cols=[c.name for c in ob.users_collection]
    if any(c.startswith(('SOURCE_GEOREF','QA |')) for c in cols):continue
    name=ob.name.casefold()
    interesting=any(k in name for k in ('piso','soleira','desembar','cabine','sagu','hall','passarela','passeio','rebaixo','térreo','terreo','chão','chao','porta','terreno corrigido','calçada','caminho osm','degrau','rampa'))
    if not interesting:continue
    row={'name':ob.name,'bounds':bb,'visible':ob.visible_get(),'render_visible':not ob.hide_render,'collections':cols,'parent':ob.parent.name if ob.parent else None,'location':list(ob.location),'dimensions':list(ob.dimensions),'matrix_world':[list(r) for r in ob.matrix_world],'properties':{k:ob[k] for k in ob.keys() if isinstance(ob[k],(str,int,float,bool))},'materials':[m.name if m else None for m in ob.data.materials]}
    rows.append(row)
    is_floor=any(k in name for k in ('piso','soleira','desembar','sagu','passeio','rebaixo','terreno corrigido','calçada','caminho osm','degrau','rampa','chão','chao')) and 'cobertura' not in name and 'entre pisos' not in name
    if is_floor and ob.visible_get():
        ob.data.calc_loop_triangles();points=[ob.matrix_world@v.co for v in ob.data.vertices]
        triangles=[]
        for t in ob.data.loop_triangles:
            p=[points[i] for i in t.vertices]
            if max(v.x for v in p)<-180 or min(v.x for v in p)>80 or max(v.y for v in p)<-70 or min(v.y for v in p)>245:continue
            triangles.append([list(v) for v in p])
        surfaces.append({'name':ob.name,'triangles':triangles,'matrix_world':row['matrix_world']})
report={'source':source,'frame':bpy.context.scene.frame_current,'objects':rows,'scope':'Inventário de superfícies e acessos; nomes somente para seleção de inspeção, não correspondência geográfica. Sem mutação.'}
(out/'inventory_before_b77.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
folder=root/'artifacts/lacerda-corridor';folder.mkdir(parents=True,exist_ok=True)
(folder/'surface_triangles_b76.json').write_text(json.dumps({'source':source,'surfaces':surfaces},ensure_ascii=False),encoding='utf8')
print(json.dumps({'inspected':len(rows),'visible_surfaces':len(surfaces),'surfaces':[{'name':s['name'],'triangles':len(s['triangles'])} for s in surfaces]},ensure_ascii=False))
