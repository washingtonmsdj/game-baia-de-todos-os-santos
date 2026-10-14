"""Encontros do corpo superior e comparação de backup, na janela B95."""
import bpy,json,runpy,os
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b95_limites_circulacoes_superiores.blend' and os.getpid()==16912
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
q=json.loads((root/'docs/reports/blender/lacerda-enclosure-b95/validation.json').read_text());names=[v['object'] for v in q['mesh_checks']]
expected={}
for folder in ('lacerda-massing-b88','lacerda-massing-b89','lacerda-massing-b90','lacerda-mesh-b91','lacerda-bridge-b92','lacerda-lower-structure-b93','lacerda-closure-b94','lacerda-enclosure-b95'):
    report=json.loads((root/f'docs/reports/blender/{folder}/application.json').read_text())
    for row in report['changes']+report.get('added',[]):expected[row['object']]=row.get('after',row).get('signature',row.get('after',row))
delta=[];rows=[]
for n in names:
    o=scene.objects[n];actual=sig(o)
    if actual!=expected[n]:delta.append({'object':n,'different_fields':[k for k in actual if actual[k]!=expected[n].get(k)]})
    p=[list(inv@wm(o)@v.co) for v in o.data.vertices]
    if any(t in n for t in ('corpo elevado','posterior alta','posterior','alas estruturais','apoio oposto','EDIFICIO | cobertura')):
        rows.append({'object':n,'visible':o.visible_get(),'signature':actual,'vertices_local':p,'faces':[list(f.vertices) for f in o.data.polygons],'bounds':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)],'properties':{k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))},'materials':[m.name if m else None for m in o.data.materials]})
out=root/'docs/reports/blender/lacerda-body-b96';out.mkdir(parents=True,exist_ok=True)
r={'file':Path(bpy.data.filepath).relative_to(root).as_posix(),'scene':scene.name,'pid':os.getpid(),'frame':scene.frame_current,'unsaved_changes':bpy.data.is_dirty,'session_recovery':json.loads((root/'artifacts/blender-sessions/current-session.json').read_text()),'validated_components_compared':len(names),'geometry_session_delta':delta,'rows':rows}
(out/'before.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Confirmar redundância geométrica antes de liberar somente um backup automático.
b92=json.loads((root/'docs/reports/blender/lacerda-bridge-b92/validation.json').read_text())
source=root/'blender/salvador_lacerda_r30b92_ponte_estrutural_consolidada.blend';backup=source.with_suffix('.blend1')
if backup.exists():
    bn=[v['object'] for v in b92['mesh_checks']];final=h['inspect_file'](source,bn);old=h['inspect_file'](backup,bn)
    comparison={'source':source.relative_to(root).as_posix(),'backup':backup.relative_to(root).as_posix(),'objects_compared':len(bn),'geometry_differences':[n for n in bn if final[n]!=old[n]],'official_source_validated':b92['reopened'],'scope':'Assinaturas de geometria/transform/material; backup automático anterior ao checkpoint final, não revisão oficial.'}
    (out/'backup-comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
else:comparison=None
print(json.dumps({'session_geometry_delta':delta,'backup_comparison':comparison,'targets':[{'object':r['object'],'bounds':r['bounds']} for r in rows if not any(r['object'].endswith(f'.{i:03}') for i in range(100))]},ensure_ascii=False))
