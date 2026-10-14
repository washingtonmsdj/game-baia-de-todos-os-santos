"""Inventário estrutural da B82; não modifica cenas, geometria ou controller."""
import bpy,json,runpy,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'docs/reports/world/centro-structural-triage';out.mkdir(parents=True,exist_ok=True)
wm=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['world_matrix']
scene=bpy.data.scenes['SALVADOR | ESBOCO OFICIAL'];rows=[]
keys=('boas_osm_way_id','boas_osm_id','osm_id','osm_way_id','osm_relation_id','boas_location_id','boas_role','boas_reference_only','status','accuracy','replacement_required')
for ob in scene.objects:
    props={k:ob[k] for k in keys if k in ob and isinstance(ob[k],(str,int,float,bool))}
    try:matrix=wm(ob)
    except RuntimeError:continue
    corners=[matrix@Vector(v) for v in ob.bound_box] if ob.type in {'MESH','CURVE'} else []
    row={'name':ob.name,'type':ob.type,'properties':props,'collections':[c.name for c in ob.users_collection],
         'matrix_world':[list(r) for r in matrix],'data':ob.data.name if ob.data else None,
         'bounds':{'min':[min(v[i] for v in corners) for i in range(3)],'max':[max(v[i] for v in corners) for i in range(3)]} if corners else None}
    if ob.type=='CURVE' and 'boas_osm_way_id' in props:
        row['splines']=[[list(matrix@Vector(p.co[:3])) for p in sp.points] for sp in ob.data.splines]
    rows.append(row)
result={'source_file':Path(bpy.data.filepath).relative_to(ROOT).as_posix(),'scene':scene.name,'pid':os.getpid(),'scene_changed':False,'objects':rows}
(out/'scene_b82.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects':len(rows),'explicit_bindings':sum('boas_osm_way_id' in r['properties'] for r in rows),'scene_changed':False}))
