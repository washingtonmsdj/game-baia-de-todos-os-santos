"""Detectar regressão das fachadas e confirmar herança real das malhas viárias."""
import bpy,json,runpy,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];functions=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));signature=functions['signature'];inspect_file=functions['inspect_file']
catalog=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'));assert Path(bpy.data.filepath).resolve()==(root/catalog['authoring_source']['file']).resolve()
prior=json.loads((root/'docs/reports/blender/cidade_baixa_r30b31.json').read_text(encoding='utf8'));session=json.loads((root/'artifacts/blender-sessions/current-session.json').read_text(encoding='utf8'));scene=bpy.context.scene
ids={1263035779,1220650665,1220650857};bodies=[r['body'] for r in prior['buildings'] if r['osm_way_id'] in ids];parts=prior['archived_reference_objects'];roads=['MVP | terreno corrigido | colisão estática','R30A5 | COLLISION | terrain proxy'];names=roads+bodies+parts
current={n:signature(scene.objects[n]) for n in names}
production=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))['world_source'];baseline30=inspect_file(root/production['file'],roads)
same_roads={n:current[n]==baseline30[n] for n in roads}
assert all(same_roads.values()),'Malha/transforms/materiais não correspondem à B30; revisar antes de declarar herança'
b23='blender/salvador_lacerda_r30b23_fachada_praca.blend';baseline23=inspect_file(root/b23,names);snapshot=inspect_file(root/session['recovery_file'],names)
unsaved=[n for n in names if baseline23[n]!=snapshot[n]]
source=session['recovery_file'] if unsaved else b23
chosen=snapshot if unsaved else baseline23
part_diffs=[n for n in parts if current[n]!=chosen[n]]
report={'source_before':catalog['authoring_source'],'production_reference':production,'restore_osm_ids':sorted(ids),'restore_source':source,'restore_source_sha256':hashlib.file_digest((root/source).open('rb'),'sha256').hexdigest(),'body_names':bodies,'legacy_component_names':parts,'legacy_components_differing_from_source':part_diffs,'selected_b23_session_differences':unsaved,'unsaved_session_comparison_scope':'terreno/proxy e prédios/componentes selecionados; não a cena inteira','b31_roads_identical_to_b30':same_roads,'road_signatures':{n:current[n] for n in roads},'classification':'ERROR: regressão visual do passe novo sobre fachadas/toldo existentes, indicada pelo usuário','road_tests_inherited_not_rerun':['terrain_proxy_network_verify.json','terrain_real_boundary_verify.json','terrain_real_boundary_vehicle.json'],'known_road_limitations':['Conceição: conflito de nível ~36,6 m ainda não resolvido','larguras reais ausentes; circuito inteiro/ônibus não aprovado','replays cinemáticos, não suspensão/tráfego dinâmico']}
(root/'docs/reports/blender/facade_regression_b23_b31.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'b31_terrain_and_collision_equal_b30':same_roads,'recover_existing_components':len(parts),'selected_session_differences':unsaved,'restore_source':source},ensure_ascii=False))
