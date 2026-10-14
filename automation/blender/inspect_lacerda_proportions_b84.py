"""Medições do conjunto externo B84 na sessão visível, sem mutações."""
import bpy,json,runpy,os
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-proportions-b84';OUT.mkdir(parents=True,exist_ok=True)
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b84_fechamento_envidracado.blend'
M=Matrix(json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame']);inv=M.inverted()
wm=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['world_matrix'];rows=[]
prefixes=('LAC R30B08 | apoio oposto','OFICIAL | Terminal alto','CALIBRADO | passarela piso','EDIFICIO | parede posterior alta','SUPERIOR | piso saguão','SUPERIOR | lateral corpo elevado','FACHADA SUPERIOR | corpo elevado','CASCA | parede','TORRE |')
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not o.name.startswith(prefixes):continue
    pts=[inv@wm(o)@v.co for v in o.data.vertices]
    lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
    rows.append({'object':o.name,'bounds_local':[lo,hi],'dimensions':[b-a for a,b in zip(lo,hi)],'visible':o.visible_get(),'collections':[c.name for c in o.users_collection],'matrix':[list(r) for r in wm(o)],'properties':dict(o.items()),'vertices_local':[list(p) for p in pts] if len(pts)<60 else None})
r={'file':bpy.data.filepath,'scene':bpy.context.scene.name,'pid':os.getpid(),'units':bpy.context.scene.unit_settings.scale_length,'objects':rows,'scene_changed':False}
(OUT/'current_measurements.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf8')
print(json.dumps({'pid':r['pid'],'scene':r['scene'],'objects':[{'name':x['object'],'dimensions':x['dimensions'],'bounds':x['bounds_local'],'visible':x['visible']} for x in rows]},ensure_ascii=False))
