"""Mede o encontro atual contra baseline B77B/B78; nenhuma alteração."""
import bpy,json,runpy,os
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
assert scene.name=='SALVADOR | ESBOCO OFICIAL','Inspecionar a cena histórica que o usuário está vendo'
baseline=json.loads((ROOT/'docs/reports/blender/lacerda-corridor/junction_before_b78.json').read_text(encoding='utf8'))
inverse=Matrix(baseline['measurement_frame']).inverted()
utils=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'));wm=utils['world_matrix'];sig=utils['signature']
protected=json.loads((ROOT/'docs/reports/blender/lacerda-gameplay-proxy/protected_original_components.json').read_text(encoding='utf8'))
rows=[]
for old in baseline['objects']:
    name=old['name'];ob=scene.objects.get(name)
    if ob is None:rows.append({'name':name,'missing':True});continue
    world=wm(ob);pts=[inverse@world@v.co for v in ob.data.vertices] if ob.type=='MESH' else [inverse@world@Vector(v) for v in ob.bound_box]
    lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
    rows.append({'name':name,'local_min':lo,'local_max':hi,'baseline_local_min':old.get('mesh_min',old.get('local_min')),'baseline_local_max':old.get('mesh_max',old.get('local_max')),'visible':ob.visible_get(),'hidden':ob.hide_get(),'matches_protected_B82':sig(ob)==protected.get(name)})
report={'file':bpy.data.filepath,'scene':scene.name,'pid':os.getpid(),'frame':scene.frame_current,'baseline':'junction_before_b78.json','measurement_frame':'Baseline derivado do saguão; não novo SSOT','objects':rows,'geometry_changed':False,'historical_freeze_preserved':True}
OUT=ROOT/'docs/reports/blender/lacerda-live-diagnostic';OUT.mkdir(parents=True,exist_ok=True)
(OUT/'upper_wall_gap.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(ROOT/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'historical-upper-gap.png'})
print(json.dumps(report,ensure_ascii=False))
