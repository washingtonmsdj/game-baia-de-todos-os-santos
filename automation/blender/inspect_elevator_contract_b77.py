"""Inspecionar controles e dependências existentes; não criar elevador paralelo."""
import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-corridor'
scene=bpy.context.scene
rows=[]
for ob in scene.objects:
    if ob.get('elevator_id') not in (3,4):continue
    if not ob.name.startswith('FUNCIONAL'):continue
    drivers=[]
    if ob.animation_data:
        for f in ob.animation_data.drivers:
            drivers.append({'path':f.data_path,'index':f.array_index,'expression':f.driver.expression,'valid':f.driver.is_valid,'variables':[{'name':v.name,'targets':[{'id':t.id.name if t.id else None,'data_path':t.data_path} for t in v.targets]} for v in f.driver.variables]})
    rows.append({'name':ob.name,'drivers':drivers,'properties':{k:ob[k] for k in ob.keys() if isinstance(ob[k],(str,int,float,bool))}})
report={'scene_controls':{k:scene[k] for k in scene.keys() if isinstance(scene[k],(str,int,float,bool)) and any(v in k.casefold() for v in ('lift','elev','cabin','porta'))},'objects':rows,'scene_animation_actions':[(s.action.name if s.action else None) for s in scene.animation_data.nla_tracks[0].strips] if scene.animation_data and scene.animation_data.nla_tracks else []}
(out/'elevator_contract_before_b77.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'controls':report['scene_controls'],'functional_objects':len(rows),'driver_count':sum(len(o['drivers']) for o in rows)},ensure_ascii=False))
