"""Leitura da B73 na janela atual: anchors, limites e amostras de terreno."""
import bpy,json,runpy,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
folder=root/'docs/reports/blender/centro-expansion';folder.mkdir(parents=True,exist_ok=True)
src=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
assert src['revision']=='R30B.73'
assert Path(bpy.data.filepath).resolve()==(root/src['file']).resolve()
def export(script,args):
    old=sys.argv[:]
    try:
        sys.argv=['blender','--',*args]
        runpy.run_path(str(root/script),run_name='__main__')
    finally:sys.argv=old
export('tools/blender/extract_georef_hints.py',['--output',str(folder/'georef_hints_live.json')])
hints=json.loads((folder/'georef_hints_live.json').read_text(encoding='utf8'))
hints['objects']=[o for o in hints['objects'] if not o.get('properties',{}).get('boas_reference_only') and not any(c.startswith('SOURCE_GEOREF') for c in o['collections'])]
(folder/'georef_hints_live.json').write_text(json.dumps(hints,ensure_ascii=False,indent=2),encoding='utf8')
export('tools/blender/export_terrain_samples.py',['--output',str(folder/'terrain_samples.json'),'--include-regex',r'^(MVP \| terreno corrigido \| colisão estática|B62 \| GAMEPLAY TERRAIN HQ \| pavimento e costura limpa)','--max-points-per-object','5000'])
rows=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not any(t in o.name.lower() for t in ['terreno','terrain','encosta','relevo','pier','cais','água','baía']):continue
    p=[o.matrix_world@Vector(c) for c in o.bound_box]
    rows.append({'name':o.name,'bounds':[min(v[i] for v in p) for i in range(3)]+[max(v[i] for v in p) for i in range(3)],'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'hidden':o.hide_get(),'collections':[c.name for c in o.users_collection]})
scene={'source':src,'objects':rows,'units':hints['units'],'instance_objects':[{'name':o.name,'collection':o.instance_collection.name if o.instance_collection else None,'location':list(o.matrix_world.translation),'rotation':list(o.rotation_euler)} for o in bpy.context.scene.objects if o.type=='EMPTY' and o.instance_collection]}
(folder/'scene_limits.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects':len(rows),'main_ground':[r for r in rows if r['name'] in ['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa']],'instances':scene['instance_objects']},ensure_ascii=False))
