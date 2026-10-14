"""Fecha pesquisa B80 sem alterar seus contratos/relatórios canônicos ou cena."""
import hashlib
import json
from pathlib import Path

from elevator_controller import crossing_allowed, find_path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'docs/reports/world/cairu-market-pedestrian'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    baseline = json.loads((ROOT/'docs/reports/research/lacerda-issue22/reconciliation.json').read_text(encoding='utf-8'))
    protected = []
    for row in baseline['protected_revisions']+baseline['canonical_local_reports']:
        expected = row.get('expected_sha256', row.get('sha256'))
        actual = digest(ROOT/row['file'])
        assert actual == expected, f"Baseline protegido mudou: {row['file']}"
        protected.append({'file': row['file'], 'sha256': actual, 'preserved': True})
    ssot = digest(ROOT/'world/geographic-reference.json')
    assert ssot == baseline['ssot_sha256']
    contract = json.loads((ROOT/'world/areas/mvp-centro-lacerda/corridor-slice.json').read_text(encoding='utf-8'))
    extension = {
        'schema': 'boas/corridor-external-validation-v1',
        'extends': 'world/areas/mvp-centro-lacerda/corridor-slice.json',
        'geographic_ssot': 'world/geographic-reference.json',
        'baseline': 'B80', 'scene_revision_applied': None,
        'LACERDA_VERTICAL': 'BLOCKED_EXTERNAL_EVIDENCE',
        'investigation_conclusion': 'STILL_UNRESOLVED',
        'movement_enabled': False,
        'CAIRU_MARKET_PEDESTRIAN': 'CANDIDATE_VALIDATION_NOT_APPLIED',
        'EXPANDED_MAP': 'GREYBOX',
        'external_block': {
            'process': 'SEMOB 151228/2023', 'contract': '008/2023',
            'inexigibility': '013/2023',
            'required': ['Projeto Básico', 'proposta comercial', 'desenhos de instalação/montagem',
                         'levantamento físico equivalente do conjunto executado'],
            'must_resolve': ['W/D/H cabine', 'abertura e posição de portas', 'soleiras/gap',
                             'seção útil e folgas do poço', 'níveis de parada e datum/offsets'],
            'maintenance_contract_is_not_installation': '004/2023 / 20952/2023',
            'generic_searches_this_round': 0,
            'witness_count': 27, 'witness_classification': 'UNRESOLVED',
            'reopen_only_on': 'nova evidência independente aplicável à instalação atual'
        },
        'crossing_binding': {
            'source': 'source:osm-centro-20261005', 'way_id': 395865976,
            'evidence': 'docs/reports/world/cairu-market-pedestrian/osm_crossing_binding.json',
            'road_intersections': [
                {'road': 1004133497, 'shared_node': 3178050253, 'traffic_type': 'uncontrolled'},
                {'road': 978525930, 'shared_node': 5917201014, 'traffic_type': 'traffic_signals'},
                {'road': 46348179, 'shared_node': 592378620, 'traffic_type': 'traffic_signals'}],
            'approach_ways': [312006925, 1423065746],
            'topology_confirmed': True, 'final_pavement_alignment_verified': False,
            'OSM_does_not_prove': ['largura livre', 'rampa/degrau', 'cota', 'fase semafórica',
                                  'entrada atual do Mercado', 'estado atual de obras']
        },
        'controller': {
            'implementation': 'tools/world/elevator_controller.py',
            'reuse_edges_from': 'corridor-slice.json#/controller/edges',
            'default_permissions': {
                **contract['controller']['default_permissions'],
                'source_crossing': True, 'traffic_permission': None,
                'lower_capsule_clear': False, 'mercado_capsule_clear': False,
                'lower_boarding': False, 'upper_boarding': False
            },
            'traffic_rule': 'Todos os três conflitos precisam de permissão atual explícita. Tag traffic_signals não significa sinal verde; uncontrolled exige avaliação de veículos.',
            'ground_following_candidate': 'docs/reports/world/cairu-market-pedestrian/ground_following_candidates.json',
            'engine_adapter_required': ['gravity/slide/step solver', 'support gap <= 0.03',
                                        'capsule CCD and closed-shaft guard', 'traffic/vehicle sensing',
                                        'visual-ground vs simplified collider equivalence'],
            'no_teleport_or_elevator_bypass': True
        },
        'collider_plan': {
            'applied': False,
            'collision_role_evidence': 'docs/reports/world/cairu-market-pedestrian/collision_role_evidence.json',
            'render_only_candidate': ['LAC R30B06 | fundo verde travessia 3178050253'],
            'curbs_remain_physical': True,
            'layers': ['walkable_ground', 'curb_step_or_obstacle', 'wall_obstacle', 'shaft_forbidden', 'dynamic_door'],
            'rule': 'Derivar superfícies caminháveis e obstáculos necessários de faces visuais existentes; manter source object/hash, SSOT e provenance. Não copiar toda arquitetura nem transformar referência OSM em collider final.',
            'requires_live_B80_inspection': True,
            'disable_old_binding_only_after_equivalence_validation': True
        },
        'production_ready': False, 'production_exported': False
    }
    out_contract = ROOT/'world/areas/mvp-centro-lacerda/cairu-market-pedestrian.json'
    out_contract.write_text(json.dumps(extension, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    permissions = extension['controller']['default_permissions']
    assert find_path(contract['controller']['edges'], 'upper_foyer', 'mercado', permissions) is None
    assert find_path(contract['controller']['edges'], 'lower_foyer', 'mercado', permissions) is None
    assert not crossing_allowed(source_crossing_confirmed=True, traffic_permission=None, capsule_clear=True)
    assert not crossing_allowed(source_crossing_confirmed=True, traffic_permission=True, capsule_clear=False)
    proof = {'protected': protected, 'ssot_sha256': ssot,
             'upper_to_market_path': None, 'lower_to_market_path': None,
             'unknown_traffic_blocks': True, 'unverified_collision_blocks': True,
             'movement_enabled': False, 'engine_physics_verified': False,
             'cabin_CCD_repeated': False, 'B81_created': False, 'scene_changed': False}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'closure_and_controller_gate.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'protected_files': len(protected), 'status': 'BLOCKED_EXTERNAL_EVIDENCE', 'movement_enabled': False}))


if __name__ == '__main__':
    main()
