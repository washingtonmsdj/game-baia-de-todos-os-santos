"""Controles locais dos encontros; leitura da mesma cena, sem alteração."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2]
r=json.loads((root/'docs/reports/blender/terracos_palacio_r30b36.json').read_text(encoding='utf8'))
r34=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'))
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
SI=Matrix(r['layout']['frame_world']).inverted();rows=[]
for n in r34['galleries']['created_objects']+r['created_objects']:
    if not any(s in n for s in ('alvenaria','Laje','Escad','Bastião','Parede','Piso','Passeio')):continue
    o=bpy.context.scene.objects[n];M=SI@wm(o);pts=[M@Vector(v) for v in o.bound_box]
    rows.append({'name':n,'bounds_local':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]})
segments=[]
for s in r34['galleries']['segments']:
    p=SI@Vector(s['origin_world']);u=SI.to_3x3()@Vector(s['along_world']);n=SI.to_3x3()@Vector(s['outward_world'])
    segments.append({'name':s['name'],'origin_local':list(p),'end_local':list(p+u*s['length_from_existing_controls_m']),'along_local':list(u),'outward_local':list(n),'height':s['height_candidate_m']})
out={'file':bpy.data.filepath,'bounds':rows,'gallery_segments':segments}
(root/'artifacts/palacio-rio-branco/terrace_connections_r36.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
