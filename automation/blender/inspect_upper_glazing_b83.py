"""Inventário físico do fechamento e caixilhos; nenhuma mutação da cena."""
import bpy,json,runpy,os
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b83_encontro_superior_consolidado.blend'
data=json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))
inv=Matrix(data['measurement_frame']).inverted()
wm=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['world_matrix']
rows=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    mats=[m.name if m else None for m in o.data.materials]
    if not any(t in o.name.lower() for t in ('superior','passarela','caixilho')):continue
    p=[inv@wm(o)@v.co for v in o.data.vertices]
    if not p:continue
    lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
    if hi[0]<-10 or lo[0]>6 or hi[2]<69 or lo[2]>76:continue
    rows.append({'name':o.name,'bounds':[lo,hi],'materials':mats,'vertices':len(p),'collections':[c.name for c in o.users_collection],'properties':dict(o.items())})
report={'file':bpy.data.filepath,'scene':bpy.context.scene.name,'pid':os.getpid(),'objects':rows,'scene_changed':False}
out=ROOT/'docs/reports/blender/lacerda-consolidation-b83/upper_glazing_inventory.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf8')
print(json.dumps({'file':report['file'],'scene':report['scene'],'objects':[{'name':r['name'],'bounds':r['bounds'],'materials':r['materials']} for r in rows]},ensure_ascii=False))
