"""Inventário localizado para modelagem junto ao acesso inferior do Lacerda."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Abrir fonte ativa em chamada separada')
bpy.context.view_layer.update();out=[]
for o in bpy.context.scene.objects:
    props={k:str(o[k]) for k in o.keys()}
    match=any(s in o.name.casefold() for s in ('cravo','cairu','cayru','cayr','vizinh','comerc','comérc','fachada baixa','rua da conceição','monumento'))
    big=False;bounds=None
    if o.type=='MESH':
        ps=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in ps) for i in range(3)];hi=[max(v[i] for v in ps) for i in range(3)];bounds=[lo,hi]
        big=hi[2]-lo[2]>6 and hi[0]-lo[0]>4 and hi[1]-lo[1]>4 and -280<o.matrix_world.translation.x<180 and -220<o.matrix_world.translation.y<280 and lo[2]<25 and hi[2]<70
    if not match and not big:continue
    row={'name':o.name,'type':o.type,'props':props,'collections':[x.name for x in o.users_collection],'location':list(o.matrix_world.translation),'matrix_world':[list(r) for r in o.matrix_world],'bounds':bounds,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport}
    if o.type=='MESH':
        row.update(vertices=len(o.data.vertices),materials=[m.name if m else None for m in o.data.materials])
        if len(o.data.vertices)<80:row['mesh_vertices_world']=[list(o.matrix_world@v.co) for v in o.data.vertices]
    if o.type=='CURVE':row['points']=[[list(o.matrix_world@Vector(v.co[:3])) for v in sp.points] for sp in o.data.splines]
    out.append(row)
(root/'docs/reports/blender/cidade_baixa_building_before.json').write_text(json.dumps({'source':c['world_source'],'objects':out},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'objects_catalogued':len(out),'report':'docs/reports/blender/cidade_baixa_building_before.json'}))
