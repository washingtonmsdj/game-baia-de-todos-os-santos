"""Abre a composição explicitamente escolhida pelo usuário na janela MCP atual.

Não copia malhas das revisões experimentais R30C nem altera geometria.
"""
import bpy,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
relative='blender/salvador_lacerda_r30b23_fachada_praca.blend'
source=root/relative
if not source.is_file():raise RuntimeError('Fonte R30B23 ausente; não substituir')
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
cp=root/'world/areas/mvp-centro-lacerda/production.json'
contract=json.loads(cp.read_text(encoding='utf8'))
previous=contract['world_source'].copy()
digest=hashlib.file_digest(source.open('rb'),'sha256').hexdigest()
contract['world_source'].update(file=relative,sha256=digest,scene=scene.name,revision='R30B.23',selection_reason='Composição explicitamente escolhida pelo usuário em 01/10/2026: fachada da praça. Revisões experimentais R30C rejeitadas como base; terreno deve preservar limites XY da composição autoral.')
contract['export'].pop('urban_slice_collection',None)
contract['export']['visual_collection_ids']=[i for i in contract['export']['visual_collection_ids'] if i!='40']
contract['runtime']['road_widths_status']='not_verified_do_not_use_to_resize_source_geometry'
report={'source':contract['world_source'],'previous_candidate':previous,'geometry_changed':False,'runtime_reexported':False,'width_policy':'Preservar limites XY autorais; largura real não confirmada permanece null. Não usar envelopes por classe de rua para remodelar terreno.','scene':scene.name,'terrain_objects':[]}
for name in (contract['export']['road_object'],contract['export']['terrain_proxy']):
    o=scene.objects.get(name)
    report['terrain_objects'].append({'name':name,'present':bool(o),'vertices':len(o.data.vertices) if o and o.type=='MESH' else None,'materials':[m.name if m else None for m in o.data.materials] if o and o.type=='MESH' else []})
if not scene.objects.get(contract['export']['road_object']):raise RuntimeError('Binding de terreno ausente na composição selecionada; contrato não promovido')
cp.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
path=root/'docs/reports/blender/terrain_source_selection.json'
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
