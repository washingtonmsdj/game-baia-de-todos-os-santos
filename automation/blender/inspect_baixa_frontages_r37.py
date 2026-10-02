"""Controles dos três edifícios existentes, sem pesquisa ou alteração de cena."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];cat=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'));source=cat['authoring_source'];assert source['revision']=='R30B.36' and Path(bpy.data.filepath).resolve()==(root/source['file']).resolve()
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm,sig=h['world_matrix'],h['signature'];rows=[];scene=bpy.context.scene
old=json.loads((root/'docs/reports/blender/cidade_baixa_r30b33.json').read_text(encoding='utf8'))
for b in old['buildings']:
    o=scene.objects[b['body']];controls=json.loads(o['boas_footprint_controls']);points=[wm(o)@v.co for v in o.data.vertices];components=[n for n in old['created_objects'] if str(b['osm_way_id']) in n]
    rows.append({'osm_way_id':b['osm_way_id'],'body':o.name,'controls_xy':controls,'base_z':min(p.z for p in points),'top_z':max(p.z for p in points),'candidate_floors':b['candidate_floors'],'candidate_bays':b['facade_bays_candidate'],'components':components,'materials':[m.name for m in o.data.materials],'before':sig(o)})
out=root/'artifacts/cidade-baixa/frontage_controls_r37.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({'source':source,'buildings':rows},ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(rows,ensure_ascii=False))
